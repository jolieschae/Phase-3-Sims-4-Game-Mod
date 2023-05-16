# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\loader.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 23168 bytes
import os, re, sys, traceback, types, functools, warnings
from fnmatch import fnmatch, fnmatchcase
from . import case, suite, util
__unittest = True
VALID_MODULE_NAME = re.compile('[_a-z]\\w*\\.py$', re.IGNORECASE)

class _FailedTest(case.TestCase):
    _testMethodName = None

    def __init__(self, method_name, exception):
        self._exception = exception
        super(_FailedTest, self).__init__(method_name)

    def __getattr__(self, name):
        if name != self._testMethodName:
            return super(_FailedTest, self).__getattr__(name)

        def testFailure():
            raise self._exception

        return testFailure


def _make_failed_import_test(name, suiteClass):
    message = 'Failed to import test module: %s\n%s' % (
     name, traceback.format_exc())
    return _make_failed_test(name, ImportError(message), suiteClass, message)


def _make_failed_load_tests(name, exception, suiteClass):
    message = 'Failed to call load_tests:\n%s' % (traceback.format_exc(),)
    return _make_failed_test(name, exception, suiteClass, message)


def _make_failed_test(methodname, exception, suiteClass, message):
    test = _FailedTest(methodname, exception)
    return (suiteClass((test,)), message)


def _make_skipped_test(methodname, exception, suiteClass):

    @case.skip(str(exception))
    def testSkipped(self):
        pass

    attrs = {methodname: testSkipped}
    TestClass = type('ModuleSkipped', (case.TestCase,), attrs)
    return suiteClass((TestClass(methodname),))


def _jython_aware_splitext(path):
    if path.lower().endswith('$py.class'):
        return path[:-9]
    return os.path.splitext(path)[0]


class TestLoader(object):
    testMethodPrefix = 'test'
    sortTestMethodsUsing = staticmethod(util.three_way_cmp)
    testNamePatterns = None
    suiteClass = suite.TestSuite
    _top_level_dir = None

    def __init__(self):
        super(TestLoader, self).__init__()
        self.errors = []
        self._loading_packages = set()

    def loadTestsFromTestCase(self, testCaseClass):
        if issubclass(testCaseClass, suite.TestSuite):
            raise TypeError('Test cases should not be derived from TestSuite. Maybe you meant to derive from TestCase?')
        testCaseNames = self.getTestCaseNames(testCaseClass)
        if not testCaseNames:
            if hasattr(testCaseClass, 'runTest'):
                testCaseNames = [
                 'runTest']
        loaded_suite = self.suiteClass(map(testCaseClass, testCaseNames))
        return loaded_suite

    def loadTestsFromModule(self, module, *args, pattern=None, **kws):
        if len(args) > 0 or 'use_load_tests' in kws:
            warnings.warn('use_load_tests is deprecated and ignored', DeprecationWarning)
            kws.pop('use_load_tests', None)
        else:
            if len(args) > 1:
                complaint = len(args) + 1
                raise TypeError('loadTestsFromModule() takes 1 positional argument but {} were given'.format(complaint))
            if len(kws) != 0:
                complaint = sorted(kws)[0]
                raise TypeError("loadTestsFromModule() got an unexpected keyword argument '{}'".format(complaint))
            tests = []
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, case.TestCase):
                    tests.append(self.loadTestsFromTestCase(obj))

            load_tests = getattr(module, 'load_tests', None)
            tests = self.suiteClass(tests)
            if load_tests is not None:
                try:
                    return load_tests(self, tests, pattern)
                except Exception as e:
                    try:
                        error_case, error_message = _make_failed_load_tests(module.__name__, e, self.suiteClass)
                        self.errors.append(error_message)
                        return error_case
                    finally:
                        e = None
                        del e

        return tests

    def loadTestsFromName(self, name, module=None):
        parts = name.split('.')
        error_case, error_message = (None, None)
        if module is None:
            parts_copy = parts[:]
            while parts_copy:
                try:
                    module_name = '.'.join(parts_copy)
                    module = __import__(module_name)
                    break
                except ImportError:
                    next_attribute = parts_copy.pop()
                    error_case, error_message = _make_failed_import_test(next_attribute, self.suiteClass)
                    if not parts_copy:
                        self.errors.append(error_message)
                        return error_case

            parts = parts[1:]
        else:
            obj = module
            for part in parts:
                try:
                    parent, obj = obj, getattr(obj, part)
                except AttributeError as e:
                    try:
                        if getattr(obj, '__path__', None) is not None:
                            if error_case is not None:
                                self.errors.append(error_message)
                                return error_case
                        error_case, error_message = _make_failed_test(part, e, self.suiteClass, 'Failed to access attribute:\n%s' % (
                         traceback.format_exc(),))
                        self.errors.append(error_message)
                        return error_case
                    finally:
                        e = None
                        del e

            if isinstance(obj, types.ModuleType):
                return self.loadTestsFromModule(obj)
            if isinstance(obj, type):
                if issubclass(obj, case.TestCase):
                    return self.loadTestsFromTestCase(obj)
            if isinstance(obj, types.FunctionType) and isinstance(parent, type) and issubclass(parent, case.TestCase):
                name = parts[-1]
                inst = parent(name)
                return isinstance(getattr(inst, name), types.FunctionType) or self.suiteClass([inst])
            else:
                if isinstance(obj, suite.TestSuite):
                    return obj
                if callable(obj):
                    test = obj()
                    if isinstance(test, suite.TestSuite):
                        return test
                        if isinstance(test, case.TestCase):
                            return self.suiteClass([test])
                        raise TypeError('calling %s returned %s, not a test' % (
                         obj, test))
                    else:
                        pass
            raise TypeError("don't know how to make test from: %s" % obj)

    def loadTestsFromNames(self, names, module=None):
        suites = [self.loadTestsFromName(name, module) for name in names]
        return self.suiteClass(suites)

    def getTestCaseNames(self, testCaseClass):

        def shouldIncludeMethod(attrname):
            if not attrname.startswith(self.testMethodPrefix):
                return False
            else:
                testFunc = getattr(testCaseClass, attrname)
                return callable(testFunc) or False
            fullName = '%s.%s' % (testCaseClass.__module__, testFunc.__qualname__)
            return self.testNamePatterns is None or any((fnmatchcase(fullName, pattern) for pattern in self.testNamePatterns))

        testFnNames = list(filter(shouldIncludeMethod, dir(testCaseClass)))
        if self.sortTestMethodsUsing:
            testFnNames.sort(key=(functools.cmp_to_key(self.sortTestMethodsUsing)))
        return testFnNames

    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        set_implicit_top = False
        if top_level_dir is None and self._top_level_dir is not None:
            top_level_dir = self._top_level_dir
        else:
            if top_level_dir is None:
                set_implicit_top = True
                top_level_dir = start_dir
        top_level_dir = os.path.abspath(top_level_dir)
        if top_level_dir not in sys.path:
            sys.path.insert(0, top_level_dir)
        self._top_level_dir = top_level_dir
        is_not_importable = False
        is_namespace = False
        tests = []
        if os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            if start_dir != top_level_dir:
                is_not_importable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            try:
                __import__(start_dir)
            except ImportError:
                is_not_importable = True
            else:
                the_module = sys.modules[start_dir]
                top_part = start_dir.split('.')[0]
                try:
                    start_dir = os.path.abspath(os.path.dirname(the_module.__file__))
                except AttributeError:
                    try:
                        spec = the_module.__spec__
                    except AttributeError:
                        spec = None

                    if spec and spec.loader is None:
                        if spec.submodule_search_locations is not None:
                            is_namespace = True
                            for path in the_module.__path__:
                                if not set_implicit_top:
                                    if not path.startswith(top_level_dir):
                                        continue
                                    self._top_level_dir = path.split(the_module.__name__.replace('.', os.path.sep))[0]
                                    tests.extend(self._find_tests(path, pattern,
                                      namespace=True))

                    elif the_module.__name__ in sys.builtin_module_names:
                        raise TypeError('Can not use builtin modules as dotted module names') from None
                    else:
                        raise TypeError("don't know how to discover from {!r}".format(the_module)) from None

                if set_implicit_top:
                    if not is_namespace:
                        self._top_level_dir = self._get_directory_containing_module(top_part)
                        sys.path.remove(top_level_dir)
                    else:
                        sys.path.remove(top_level_dir)
                if is_not_importable:
                    raise ImportError('Start directory is not importable: %r' % start_dir)
                if not is_namespace:
                    tests = list(self._find_tests(start_dir, pattern))
                return self.suiteClass(tests)

    def _get_directory_containing_module(self, module_name):
        module = sys.modules[module_name]
        full_path = os.path.abspath(module.__file__)
        if os.path.basename(full_path).lower().startswith('__init__.py'):
            return os.path.dirname(os.path.dirname(full_path))
        return os.path.dirname(full_path)

    def _get_name_from_path(self, path):
        if path == self._top_level_dir:
            return '.'
        path = _jython_aware_splitext(os.path.normpath(path))
        _relpath = os.path.relpath(path, self._top_level_dir)
        name = _relpath.replace(os.path.sep, '.')
        return name

    def _get_module_from_name(self, name):
        __import__(name)
        return sys.modules[name]

    def _match_path(self, path, full_path, pattern):
        return fnmatch(path, pattern)

    def _find_tests(self, start_dir, pattern, namespace=False):
        name = self._get_name_from_path(start_dir)
        if name != '.':
            if name not in self._loading_packages:
                tests, should_recurse = self._find_test_path(start_dir, pattern, namespace)
                if tests is not None:
                    yield tests
                if not should_recurse:
                    return
        paths = sorted(os.listdir(start_dir))
        for path in paths:
            full_path = os.path.join(start_dir, path)
            tests, should_recurse = self._find_test_path(full_path, pattern, namespace)
            if tests is not None:
                yield tests
            if should_recurse:
                name = self._get_name_from_path(full_path)
                self._loading_packages.add(name)
                try:
                    yield from self._find_tests(full_path, pattern, namespace)
                finally:
                    self._loading_packages.discard(name)

    def _find_test_path--- This code section failed: ---

 L. 424         0  LOAD_GLOBAL              os
                2  LOAD_ATTR                path
                4  LOAD_METHOD              basename
                6  LOAD_FAST                'full_path'
                8  CALL_METHOD_1         1  '1 positional argument'
               10  STORE_FAST               'basename'

 L. 425        12  LOAD_GLOBAL              os
               14  LOAD_ATTR                path
               16  LOAD_METHOD              isfile
               18  LOAD_FAST                'full_path'
               20  CALL_METHOD_1         1  '1 positional argument'
            22_24  POP_JUMP_IF_FALSE   328  'to 328'

 L. 426        26  LOAD_GLOBAL              VALID_MODULE_NAME
               28  LOAD_METHOD              match
               30  LOAD_FAST                'basename'
               32  CALL_METHOD_1         1  '1 positional argument'
               34  POP_JUMP_IF_TRUE     40  'to 40'

 L. 428        36  LOAD_CONST               (None, False)
               38  RETURN_VALUE     
             40_0  COME_FROM            34  '34'

 L. 429        40  LOAD_FAST                'self'
               42  LOAD_METHOD              _match_path
               44  LOAD_FAST                'basename'
               46  LOAD_FAST                'full_path'
               48  LOAD_FAST                'pattern'
               50  CALL_METHOD_3         3  '3 positional arguments'
               52  POP_JUMP_IF_TRUE     58  'to 58'

 L. 430        54  LOAD_CONST               (None, False)
               56  RETURN_VALUE     
             58_0  COME_FROM            52  '52'

 L. 432        58  LOAD_FAST                'self'
               60  LOAD_METHOD              _get_name_from_path
               62  LOAD_FAST                'full_path'
               64  CALL_METHOD_1         1  '1 positional argument'
               66  STORE_FAST               'name'

 L. 433        68  SETUP_EXCEPT         84  'to 84'

 L. 434        70  LOAD_FAST                'self'
               72  LOAD_METHOD              _get_module_from_name
               74  LOAD_FAST                'name'
               76  CALL_METHOD_1         1  '1 positional argument'
               78  STORE_FAST               'module'
               80  POP_BLOCK        
               82  JUMP_FORWARD        174  'to 174'
             84_0  COME_FROM_EXCEPT     68  '68'

 L. 435        84  DUP_TOP          
               86  LOAD_GLOBAL              case
               88  LOAD_ATTR                SkipTest
               90  COMPARE_OP               exception-match
               92  POP_JUMP_IF_FALSE   132  'to 132'
               94  POP_TOP          
               96  STORE_FAST               'e'
               98  POP_TOP          
              100  SETUP_FINALLY       120  'to 120'

 L. 436       102  LOAD_GLOBAL              _make_skipped_test
              104  LOAD_FAST                'name'
              106  LOAD_FAST                'e'
              108  LOAD_FAST                'self'
              110  LOAD_ATTR                suiteClass
              112  CALL_FUNCTION_3       3  '3 positional arguments'
              114  LOAD_CONST               False
              116  BUILD_TUPLE_2         2 
              118  RETURN_VALUE     
            120_0  COME_FROM_FINALLY   100  '100'
              120  LOAD_CONST               None
              122  STORE_FAST               'e'
              124  DELETE_FAST              'e'
              126  END_FINALLY      
              128  POP_EXCEPT       
              130  JUMP_FORWARD        588  'to 588'
            132_0  COME_FROM            92  '92'

 L. 437       132  POP_TOP          
              134  POP_TOP          
              136  POP_TOP          

 L. 439       138  LOAD_GLOBAL              _make_failed_import_test
              140  LOAD_FAST                'name'
              142  LOAD_FAST                'self'
              144  LOAD_ATTR                suiteClass
              146  CALL_FUNCTION_2       2  '2 positional arguments'
              148  UNPACK_SEQUENCE_2     2 
              150  STORE_FAST               'error_case'
              152  STORE_FAST               'error_message'

 L. 440       154  LOAD_FAST                'self'
              156  LOAD_ATTR                errors
              158  LOAD_METHOD              append
              160  LOAD_FAST                'error_message'
              162  CALL_METHOD_1         1  '1 positional argument'
              164  POP_TOP          

 L. 441       166  LOAD_FAST                'error_case'
              168  LOAD_CONST               False
              170  BUILD_TUPLE_2         2 
              172  RETURN_VALUE     
            174_0  COME_FROM            82  '82'

 L. 443       174  LOAD_GLOBAL              os
              176  LOAD_ATTR                path
              178  LOAD_METHOD              abspath

 L. 444       180  LOAD_GLOBAL              getattr
              182  LOAD_FAST                'module'
              184  LOAD_STR                 '__file__'
              186  LOAD_FAST                'full_path'
              188  CALL_FUNCTION_3       3  '3 positional arguments'
              190  CALL_METHOD_1         1  '1 positional argument'
              192  STORE_FAST               'mod_file'

 L. 445       194  LOAD_GLOBAL              _jython_aware_splitext

 L. 446       196  LOAD_GLOBAL              os
              198  LOAD_ATTR                path
              200  LOAD_METHOD              realpath
              202  LOAD_FAST                'mod_file'
              204  CALL_METHOD_1         1  '1 positional argument'
              206  CALL_FUNCTION_1       1  '1 positional argument'
              208  STORE_FAST               'realpath'

 L. 447       210  LOAD_GLOBAL              _jython_aware_splitext

 L. 448       212  LOAD_GLOBAL              os
              214  LOAD_ATTR                path
              216  LOAD_METHOD              realpath
              218  LOAD_FAST                'full_path'
              220  CALL_METHOD_1         1  '1 positional argument'
              222  CALL_FUNCTION_1       1  '1 positional argument'
              224  STORE_FAST               'fullpath_noext'

 L. 449       226  LOAD_FAST                'realpath'
              228  LOAD_METHOD              lower
              230  CALL_METHOD_0         0  '0 positional arguments'
              232  LOAD_FAST                'fullpath_noext'
              234  LOAD_METHOD              lower
              236  CALL_METHOD_0         0  '0 positional arguments'
              238  COMPARE_OP               !=
          240_242  POP_JUMP_IF_FALSE   306  'to 306'

 L. 450       244  LOAD_GLOBAL              os
              246  LOAD_ATTR                path
              248  LOAD_METHOD              dirname
              250  LOAD_FAST                'realpath'
              252  CALL_METHOD_1         1  '1 positional argument'
              254  STORE_FAST               'module_dir'

 L. 451       256  LOAD_GLOBAL              _jython_aware_splitext

 L. 452       258  LOAD_GLOBAL              os
              260  LOAD_ATTR                path
              262  LOAD_METHOD              basename
              264  LOAD_FAST                'full_path'
              266  CALL_METHOD_1         1  '1 positional argument'
              268  CALL_FUNCTION_1       1  '1 positional argument'
              270  STORE_FAST               'mod_name'

 L. 453       272  LOAD_GLOBAL              os
              274  LOAD_ATTR                path
              276  LOAD_METHOD              dirname
              278  LOAD_FAST                'full_path'
              280  CALL_METHOD_1         1  '1 positional argument'
              282  STORE_FAST               'expected_dir'

 L. 454       284  LOAD_STR                 '%r module incorrectly imported from %r. Expected %r. Is this module globally installed?'
              286  STORE_FAST               'msg'

 L. 456       288  LOAD_GLOBAL              ImportError

 L. 457       290  LOAD_FAST                'msg'
              292  LOAD_FAST                'mod_name'
              294  LOAD_FAST                'module_dir'
              296  LOAD_FAST                'expected_dir'
              298  BUILD_TUPLE_3         3 
              300  BINARY_MODULO    
              302  CALL_FUNCTION_1       1  '1 positional argument'
              304  RAISE_VARARGS_1       1  'exception instance'
            306_0  COME_FROM           240  '240'

 L. 458       306  LOAD_FAST                'self'
              308  LOAD_ATTR                loadTestsFromModule
              310  LOAD_FAST                'module'
              312  LOAD_FAST                'pattern'
              314  LOAD_CONST               ('pattern',)
              316  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              318  LOAD_CONST               False
              320  BUILD_TUPLE_2         2 
              322  RETURN_VALUE     
          324_326  JUMP_FORWARD        588  'to 588'
            328_0  COME_FROM            22  '22'

 L. 459       328  LOAD_GLOBAL              os
              330  LOAD_ATTR                path
              332  LOAD_METHOD              isdir
              334  LOAD_FAST                'full_path'
              336  CALL_METHOD_1         1  '1 positional argument'
          338_340  POP_JUMP_IF_FALSE   584  'to 584'

 L. 460       342  LOAD_FAST                'namespace'
          344_346  POP_JUMP_IF_TRUE    376  'to 376'

 L. 461       348  LOAD_GLOBAL              os
              350  LOAD_ATTR                path
              352  LOAD_METHOD              isfile
              354  LOAD_GLOBAL              os
              356  LOAD_ATTR                path
              358  LOAD_METHOD              join
              360  LOAD_FAST                'full_path'
              362  LOAD_STR                 '__init__.py'
              364  CALL_METHOD_2         2  '2 positional arguments'
              366  CALL_METHOD_1         1  '1 positional argument'
          368_370  POP_JUMP_IF_TRUE    376  'to 376'

 L. 462       372  LOAD_CONST               (None, False)
              374  RETURN_VALUE     
            376_0  COME_FROM           368  '368'
            376_1  COME_FROM           344  '344'

 L. 464       376  LOAD_CONST               None
              378  STORE_FAST               'load_tests'

 L. 465       380  LOAD_CONST               None
              382  STORE_FAST               'tests'

 L. 466       384  LOAD_FAST                'self'
              386  LOAD_METHOD              _get_name_from_path
              388  LOAD_FAST                'full_path'
              390  CALL_METHOD_1         1  '1 positional argument'
            392_0  COME_FROM           130  '130'
              392  STORE_FAST               'name'

 L. 467       394  SETUP_EXCEPT        410  'to 410'

 L. 468       396  LOAD_FAST                'self'
              398  LOAD_METHOD              _get_module_from_name
              400  LOAD_FAST                'name'
              402  CALL_METHOD_1         1  '1 positional argument'
              404  STORE_FAST               'package'
              406  POP_BLOCK        
              408  JUMP_FORWARD        502  'to 502'
            410_0  COME_FROM_EXCEPT    394  '394'

 L. 469       410  DUP_TOP          
              412  LOAD_GLOBAL              case
              414  LOAD_ATTR                SkipTest
              416  COMPARE_OP               exception-match
          418_420  POP_JUMP_IF_FALSE   460  'to 460'
              422  POP_TOP          
              424  STORE_FAST               'e'
              426  POP_TOP          
              428  SETUP_FINALLY       448  'to 448'

 L. 470       430  LOAD_GLOBAL              _make_skipped_test
              432  LOAD_FAST                'name'
              434  LOAD_FAST                'e'
              436  LOAD_FAST                'self'
              438  LOAD_ATTR                suiteClass
              440  CALL_FUNCTION_3       3  '3 positional arguments'
              442  LOAD_CONST               False
              444  BUILD_TUPLE_2         2 
              446  RETURN_VALUE     
            448_0  COME_FROM_FINALLY   428  '428'
              448  LOAD_CONST               None
              450  STORE_FAST               'e'
              452  DELETE_FAST              'e'
              454  END_FINALLY      
              456  POP_EXCEPT       
              458  JUMP_FORWARD        582  'to 582'
            460_0  COME_FROM           418  '418'

 L. 471       460  POP_TOP          
              462  POP_TOP          
              464  POP_TOP          

 L. 473       466  LOAD_GLOBAL              _make_failed_import_test
              468  LOAD_FAST                'name'
              470  LOAD_FAST                'self'
              472  LOAD_ATTR                suiteClass
              474  CALL_FUNCTION_2       2  '2 positional arguments'
              476  UNPACK_SEQUENCE_2     2 
              478  STORE_FAST               'error_case'
              480  STORE_FAST               'error_message'

 L. 474       482  LOAD_FAST                'self'
              484  LOAD_ATTR                errors
              486  LOAD_METHOD              append
              488  LOAD_FAST                'error_message'
              490  CALL_METHOD_1         1  '1 positional argument'
              492  POP_TOP          

 L. 475       494  LOAD_FAST                'error_case'
              496  LOAD_CONST               False
              498  BUILD_TUPLE_2         2 
              500  RETURN_VALUE     
            502_0  COME_FROM           408  '408'

 L. 477       502  LOAD_GLOBAL              getattr
              504  LOAD_FAST                'package'
              506  LOAD_STR                 'load_tests'
              508  LOAD_CONST               None
              510  CALL_FUNCTION_3       3  '3 positional arguments'
              512  STORE_FAST               'load_tests'

 L. 479       514  LOAD_FAST                'self'
              516  LOAD_ATTR                _loading_packages
              518  LOAD_METHOD              add
              520  LOAD_FAST                'name'
              522  CALL_METHOD_1         1  '1 positional argument'
              524  POP_TOP          

 L. 480       526  SETUP_FINALLY       568  'to 568'

 L. 481       528  LOAD_FAST                'self'
              530  LOAD_ATTR                loadTestsFromModule
              532  LOAD_FAST                'package'
              534  LOAD_FAST                'pattern'
              536  LOAD_CONST               ('pattern',)
              538  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              540  STORE_FAST               'tests'

 L. 482       542  LOAD_FAST                'load_tests'
              544  LOAD_CONST               None
              546  COMPARE_OP               is-not
          548_550  POP_JUMP_IF_FALSE   560  'to 560'

 L. 484       552  LOAD_FAST                'tests'
              554  LOAD_CONST               False
              556  BUILD_TUPLE_2         2 
              558  RETURN_VALUE     
            560_0  COME_FROM           548  '548'

 L. 485       560  LOAD_FAST                'tests'
              562  LOAD_CONST               True
              564  BUILD_TUPLE_2         2 
              566  RETURN_VALUE     
            568_0  COME_FROM_FINALLY   526  '526'

 L. 487       568  LOAD_FAST                'self'
              570  LOAD_ATTR                _loading_packages
              572  LOAD_METHOD              discard
              574  LOAD_FAST                'name'
              576  CALL_METHOD_1         1  '1 positional argument'
              578  POP_TOP          
              580  END_FINALLY      
            582_0  COME_FROM           458  '458'
              582  JUMP_FORWARD        588  'to 588'
            584_0  COME_FROM           338  '338'

 L. 489       584  LOAD_CONST               (None, False)
              586  RETURN_VALUE     
            588_0  COME_FROM           582  '582'
            588_1  COME_FROM           324  '324'

Parse error at or near `COME_FROM' instruction at offset 392_0


defaultTestLoader = TestLoader()

def _makeLoader(prefix, sortUsing, suiteClass=None, testNamePatterns=None):
    loader = TestLoader()
    loader.sortTestMethodsUsing = sortUsing
    loader.testMethodPrefix = prefix
    loader.testNamePatterns = testNamePatterns
    if suiteClass:
        loader.suiteClass = suiteClass
    return loader


def getTestCaseNames(testCaseClass, prefix, sortUsing=util.three_way_cmp, testNamePatterns=None):
    return _makeLoader(prefix, sortUsing, testNamePatterns=testNamePatterns).getTestCaseNames(testCaseClass)


def makeSuite(testCaseClass, prefix='test', sortUsing=util.three_way_cmp, suiteClass=suite.TestSuite):
    return _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromTestCase(testCaseClass)


def findTestCases(module, prefix='test', sortUsing=util.three_way_cmp, suiteClass=suite.TestSuite):
    return _makeLoader(prefix, sortUsing, suiteClass).loadTestsFromModule(module)