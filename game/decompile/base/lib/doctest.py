# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\doctest.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 107188 bytes
__docformat__ = 'reStructuredText en'
__all__ = [
 "'register_optionflag'", 
 "'DONT_ACCEPT_TRUE_FOR_1'", 
 "'DONT_ACCEPT_BLANKLINE'", 
 "'NORMALIZE_WHITESPACE'", 
 "'ELLIPSIS'", 
 "'SKIP'", 
 "'IGNORE_EXCEPTION_DETAIL'", 
 "'COMPARISON_FLAGS'", 
 "'REPORT_UDIFF'", 
 "'REPORT_CDIFF'", 
 "'REPORT_NDIFF'", 
 "'REPORT_ONLY_FIRST_FAILURE'", 
 "'REPORTING_FLAGS'", 
 "'FAIL_FAST'", 
 "'Example'", 
 "'DocTest'", 
 "'DocTestParser'", 
 "'DocTestFinder'", 
 "'DocTestRunner'", 
 "'OutputChecker'", 
 "'DocTestFailure'", 
 "'UnexpectedException'", 
 "'DebugRunner'", 
 "'testmod'", 
 "'testfile'", 
 "'run_docstring_examples'", 
 "'DocTestSuite'", 
 "'DocFileSuite'", 
 "'set_unittest_reportflags'", 
 "'script_from_examples'", 
 "'testsource'", 
 "'debug_src'", 
 "'debug'"]
import __future__, difflib, inspect, linecache, os, pdb, re, sys, traceback, unittest
from io import StringIO
from collections import namedtuple
TestResults = namedtuple('TestResults', 'failed attempted')
OPTIONFLAGS_BY_NAME = {}

def register_optionflag(name):
    return OPTIONFLAGS_BY_NAME.setdefault(name, 1 << len(OPTIONFLAGS_BY_NAME))


DONT_ACCEPT_TRUE_FOR_1 = register_optionflag('DONT_ACCEPT_TRUE_FOR_1')
DONT_ACCEPT_BLANKLINE = register_optionflag('DONT_ACCEPT_BLANKLINE')
NORMALIZE_WHITESPACE = register_optionflag('NORMALIZE_WHITESPACE')
ELLIPSIS = register_optionflag('ELLIPSIS')
SKIP = register_optionflag('SKIP')
IGNORE_EXCEPTION_DETAIL = register_optionflag('IGNORE_EXCEPTION_DETAIL')
COMPARISON_FLAGS = DONT_ACCEPT_TRUE_FOR_1 | DONT_ACCEPT_BLANKLINE | NORMALIZE_WHITESPACE | ELLIPSIS | SKIP | IGNORE_EXCEPTION_DETAIL
REPORT_UDIFF = register_optionflag('REPORT_UDIFF')
REPORT_CDIFF = register_optionflag('REPORT_CDIFF')
REPORT_NDIFF = register_optionflag('REPORT_NDIFF')
REPORT_ONLY_FIRST_FAILURE = register_optionflag('REPORT_ONLY_FIRST_FAILURE')
FAIL_FAST = register_optionflag('FAIL_FAST')
REPORTING_FLAGS = REPORT_UDIFF | REPORT_CDIFF | REPORT_NDIFF | REPORT_ONLY_FIRST_FAILURE | FAIL_FAST
BLANKLINE_MARKER = '<BLANKLINE>'
ELLIPSIS_MARKER = '...'

def _extract_future_flags(globs):
    flags = 0
    for fname in __future__.all_feature_names:
        feature = globs.get(fname, None)
        if feature is getattr(__future__, fname):
            flags |= feature.compiler_flag

    return flags


def _normalize_module(module, depth=2):
    if inspect.ismodule(module):
        return module
    if isinstance(module, str):
        return __import__(module, globals(), locals(), ['*'])
    if module is None:
        return sys.modules[sys._getframe(depth).f_globals['__name__']]
    raise TypeError('Expected a module, string, or None')


def _load_testfile(filename, package, module_relative, encoding):
    if module_relative:
        package = _normalize_module(package, 3)
        filename = _module_relative_path(package, filename)
        if getattr(package, '__loader__', None) is not None:
            if hasattr(package.__loader__, 'get_data'):
                file_contents = package.__loader__.get_data(filename)
                file_contents = file_contents.decode(encoding)
                return (
                 file_contents.replace(os.linesep, '\n'), filename)
    with open(filename, encoding=encoding) as (f):
        return (
         f.read(), filename)


def _indent(s, indent=4):
    return re.sub('(?m)^(?!$)', indent * ' ', s)


def _exception_traceback(exc_info):
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    return excout.getvalue()


class _SpoofOut(StringIO):

    def getvalue(self):
        result = StringIO.getvalue(self)
        if result:
            if not result.endswith('\n'):
                result += '\n'
        return result

    def truncate(self, size=None):
        self.seek(size)
        StringIO.truncate(self)


def _ellipsis_match(want, got):
    if ELLIPSIS_MARKER not in want:
        return want == got
    ws = want.split(ELLIPSIS_MARKER)
    startpos, endpos = 0, len(got)
    w = ws[0]
    if w:
        if got.startswith(w):
            startpos = len(w)
            del ws[0]
        else:
            return False
    w = ws[-1]
    if w:
        if got.endswith(w):
            endpos -= len(w)
            del ws[-1]
        else:
            return False
    if startpos > endpos:
        return False
    for w in ws:
        startpos = got.find(w, startpos, endpos)
        if startpos < 0:
            return False
        startpos += len(w)

    return True


def _comment_line(line):
    line = line.rstrip()
    if line:
        return '# ' + line
    return '#'


def _strip_exception_details(msg):
    start, end = 0, len(msg)
    i = msg.find('\n')
    if i >= 0:
        end = i
    i = msg.find(':', 0, end)
    if i >= 0:
        end = i
    i = msg.rfind('.', 0, end)
    if i >= 0:
        start = i + 1
    return msg[start:end]


class _OutputRedirectingPdb(pdb.Pdb):

    def __init__(self, out):
        self._OutputRedirectingPdb__out = out
        self._OutputRedirectingPdb__debugger_used = False
        pdb.Pdb.__init__(self, stdout=out, nosigint=True)
        self.use_rawinput = 1

    def set_trace(self, frame=None):
        self._OutputRedirectingPdb__debugger_used = True
        if frame is None:
            frame = sys._getframe().f_back
        pdb.Pdb.set_trace(self, frame)

    def set_continue(self):
        if self._OutputRedirectingPdb__debugger_used:
            pdb.Pdb.set_continue(self)

    def trace_dispatch(self, *args):
        save_stdout = sys.stdout
        sys.stdout = self._OutputRedirectingPdb__out
        try:
            return (pdb.Pdb.trace_dispatch)(self, *args)
        finally:
            sys.stdout = save_stdout


def _module_relative_path(module, test_path):
    if not inspect.ismodule(module):
        raise TypeError('Expected a module: %r' % module)
    else:
        if test_path.startswith('/'):
            raise ValueError('Module-relative files may not have absolute paths')
        test_path = (os.path.join)(*test_path.split('/'))
        if hasattr(module, '__file__'):
            basedir = os.path.split(module.__file__)[0]
        else:
            if module.__name__ == '__main__':
                if len(sys.argv) > 0 and sys.argv[0] != '':
                    basedir = os.path.split(sys.argv[0])[0]
                else:
                    basedir = os.curdir
            else:
                if hasattr(module, '__path__'):
                    for directory in module.__path__:
                        fullpath = os.path.join(directory, test_path)
                        if os.path.exists(fullpath):
                            return fullpath

                raise ValueError("Can't resolve paths relative to the module %r (it has no __file__)" % module.__name__)
    return os.path.join(basedir, test_path)


class Example:

    def __init__(self, source, want, exc_msg=None, lineno=0, indent=0, options=None):
        if not source.endswith('\n'):
            source += '\n'
        else:
            if want:
                if not want.endswith('\n'):
                    want += '\n'
            if exc_msg is not None:
                exc_msg.endswith('\n') or exc_msg += '\n'
        self.source = source
        self.want = want
        self.lineno = lineno
        self.indent = indent
        if options is None:
            options = {}
        self.options = options
        self.exc_msg = exc_msg

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.source == other.source and self.want == other.want and self.lineno == other.lineno and self.indent == other.indent and self.options == other.options and self.exc_msg == other.exc_msg

    def __hash__(self):
        return hash((self.source, self.want, self.lineno, self.indent,
         self.exc_msg))


class DocTest:

    def __init__(self, examples, globs, name, filename, lineno, docstring):
        self.examples = examples
        self.docstring = docstring
        self.globs = globs.copy()
        self.name = name
        self.filename = filename
        self.lineno = lineno

    def __repr__(self):
        if len(self.examples) == 0:
            examples = 'no examples'
        else:
            if len(self.examples) == 1:
                examples = '1 example'
            else:
                examples = '%d examples' % len(self.examples)
        return '<%s %s from %s:%s (%s)>' % (
         self.__class__.__name__,
         self.name, self.filename, self.lineno, examples)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.examples == other.examples and self.docstring == other.docstring and self.globs == other.globs and self.name == other.name and self.filename == other.filename and self.lineno == other.lineno

    def __hash__(self):
        return hash((self.docstring, self.name, self.filename, self.lineno))

    def __lt__(self, other):
        if not isinstance(other, DocTest):
            return NotImplemented
        return (
         self.name, self.filename, self.lineno, id(self)) < (
         other.name, other.filename, other.lineno, id(other))


class DocTestParser:
    _EXAMPLE_RE = re.compile('\n        # Source consists of a PS1 line followed by zero or more PS2 lines.\n        (?P<source>\n            (?:^(?P<indent> [ ]*) >>>    .*)    # PS1 line\n            (?:\\n           [ ]*  \\.\\.\\. .*)*)  # PS2 lines\n        \\n?\n        # Want consists of any non-blank lines that do not start with PS1.\n        (?P<want> (?:(?![ ]*$)    # Not a blank line\n                     (?![ ]*>>>)  # Not a line starting with PS1\n                     .+$\\n?       # But any other line\n                  )*)\n        ', re.MULTILINE | re.VERBOSE)
    _EXCEPTION_RE = re.compile("\n        # Grab the traceback header.  Different versions of Python have\n        # said different things on the first traceback line.\n        ^(?P<hdr> Traceback\\ \\(\n            (?: most\\ recent\\ call\\ last\n            |   innermost\\ last\n            ) \\) :\n        )\n        \\s* $                # toss trailing whitespace on the header.\n        (?P<stack> .*?)      # don't blink: absorb stuff until...\n        ^ (?P<msg> \\w+ .*)   #     a line *starts* with alphanum.\n        ", re.VERBOSE | re.MULTILINE | re.DOTALL)
    _IS_BLANK_OR_COMMENT = re.compile('^[ ]*(#.*)?$').match

    def parse(self, string, name='<string>'):
        string = string.expandtabs()
        min_indent = self._min_indent(string)
        if min_indent > 0:
            string = '\n'.join([l[min_indent:] for l in string.split('\n')])
        output = []
        charno, lineno = (0, 0)
        for m in self._EXAMPLE_RE.finditer(string):
            output.append(string[charno:m.start()])
            lineno += string.count('\n', charno, m.start())
            source, options, want, exc_msg = self._parse_example(m, name, lineno)
            if not self._IS_BLANK_OR_COMMENT(source):
                output.append(Example(source, want, exc_msg, lineno=lineno,
                  indent=(min_indent + len(m.group('indent'))),
                  options=options))
            lineno += string.count('\n', m.start(), m.end())
            charno = m.end()

        output.append(string[charno:])
        return output

    def get_doctest(self, string, globs, name, filename, lineno):
        return DocTest(self.get_examples(string, name), globs, name, filename, lineno, string)

    def get_examples(self, string, name='<string>'):
        return [x for x in self.parse(string, name) if isinstance(x, Example)]

    def _parse_example(self, m, name, lineno):
        indent = len(m.group('indent'))
        source_lines = m.group('source').split('\n')
        self._check_prompt_blank(source_lines, indent, name, lineno)
        self._check_prefix(source_lines[1:], ' ' * indent + '.', name, lineno)
        source = '\n'.join([sl[indent + 4:] for sl in source_lines])
        want = m.group('want')
        want_lines = want.split('\n')
        if len(want_lines) > 1:
            if re.match(' *$', want_lines[-1]):
                del want_lines[-1]
        else:
            self._check_prefix(want_lines, ' ' * indent, name, lineno + len(source_lines))
            want = '\n'.join([wl[indent:] for wl in want_lines])
            m = self._EXCEPTION_RE.match(want)
            if m:
                exc_msg = m.group('msg')
            else:
                exc_msg = None
        options = self._find_options(source, name, lineno)
        return (
         source, options, want, exc_msg)

    _OPTION_DIRECTIVE_RE = re.compile('#\\s*doctest:\\s*([^\\n\\\'"]*)$', re.MULTILINE)

    def _find_options(self, source, name, lineno):
        options = {}
        for m in self._OPTION_DIRECTIVE_RE.finditer(source):
            option_strings = m.group(1).replace(',', ' ').split()
            for option in option_strings:
                if not option[0] not in '+-':
                    if option[1:] not in OPTIONFLAGS_BY_NAME:
                        raise ValueError('line %r of the doctest for %s has an invalid option: %r' % (
                         lineno + 1, name, option))
                    flag = OPTIONFLAGS_BY_NAME[option[1:]]
                    options[flag] = option[0] == '+'

        if options:
            if self._IS_BLANK_OR_COMMENT(source):
                raise ValueError('line %r of the doctest for %s has an option directive on a line with no example: %r' % (
                 lineno, name, source))
        return options

    _INDENT_RE = re.compile('^([ ]*)(?=\\S)', re.MULTILINE)

    def _min_indent(self, s):
        indents = [len(indent) for indent in self._INDENT_RE.findall(s)]
        if len(indents) > 0:
            return min(indents)
        return 0

    def _check_prompt_blank(self, lines, indent, name, lineno):
        for i, line in enumerate(lines):
            if len(line) >= indent + 4 and line[indent + 3] != ' ':
                raise ValueError('line %r of the docstring for %s lacks blank after %s: %r' % (
                 lineno + i + 1, name,
                 line[indent:indent + 3], line))

    def _check_prefix(self, lines, prefix, name, lineno):
        for i, line in enumerate(lines):
            if line and not line.startswith(prefix):
                raise ValueError('line %r of the docstring for %s has inconsistent leading whitespace: %r' % (
                 lineno + i + 1, name, line))


class DocTestFinder:

    def __init__(self, verbose=False, parser=DocTestParser(), recurse=True, exclude_empty=True):
        self._parser = parser
        self._verbose = verbose
        self._recurse = recurse
        self._exclude_empty = exclude_empty

    def find(self, obj, name=None, module=None, globs=None, extraglobs=None):
        if name is None:
            name = getattr(obj, '__name__', None)
            if name is None:
                raise ValueError("DocTestFinder.find: name must be given when obj.__name__ doesn't exist: %r" % (
                 type(obj),))
            elif module is False:
                module = None
            else:
                if module is None:
                    module = inspect.getmodule(obj)
            try:
                file = inspect.getsourcefile(obj)
            except TypeError:
                source_lines = None
            else:
                if not file:
                    file = inspect.getfile(obj)
                    if not file[0] + file[-2:] == '<]>':
                        file = None
                if file is None:
                    source_lines = None
        else:
            if module is not None:
                source_lines = linecache.getlines(file, module.__dict__)
            else:
                source_lines = linecache.getlines(file)
            if not source_lines:
                source_lines = None
            elif globs is None:
                if module is None:
                    globs = {}
                else:
                    globs = module.__dict__.copy()
            else:
                globs = globs.copy()
            if extraglobs is not None:
                globs.update(extraglobs)
            if '__name__' not in globs:
                globs['__name__'] = '__main__'
            tests = []
            self._find(tests, obj, name, module, source_lines, globs, {})
            tests.sort()
            return tests

    def _from_module(self, module, object):
        if module is None:
            return True
        else:
            if inspect.getmodule(object) is not None:
                return module is inspect.getmodule(object)
            elif inspect.isfunction(object):
                return module.__dict__ is object.__globals__
                if inspect.ismethoddescriptor(object):
                    if hasattr(object, '__objclass__'):
                        obj_mod = object.__objclass__.__module__
            elif hasattr(object, '__module__'):
                obj_mod = object.__module__
            else:
                return True
            return module.__name__ == obj_mod
        if inspect.isclass(object):
            return module.__name__ == object.__module__
        if hasattr(object, '__module__'):
            return module.__name__ == object.__module__
        if isinstance(object, property):
            return True
        raise ValueError('object must be a class or function')

    def _find(self, tests, obj, name, module, source_lines, globs, seen):
        if self._verbose:
            print('Finding tests in %s' % name)
        else:
            if id(obj) in seen:
                return
                seen[id(obj)] = 1
                test = self._get_test(obj, name, module, globs, source_lines)
                if test is not None:
                    tests.append(test)
            else:
                if inspect.ismodule(obj):
                    if self._recurse:
                        for valname, val in obj.__dict__.items():
                            valname = '%s.%s' % (name, valname)
                            if inspect.isroutine(inspect.unwrap(val)) or inspect.isclass(val):
                                if self._from_module(module, val):
                                    self._find(tests, val, valname, module, source_lines, globs, seen)

                if inspect.ismodule(obj) and self._recurse:
                    for valname, val in getattr(obj, '__test__', {}).items():
                        if not isinstance(valname, str):
                            raise ValueError('DocTestFinder.find: __test__ keys must be strings: %r' % (
                             type(valname),))
                        if not inspect.isroutine(val) or inspect.isclass(val) or inspect.ismodule(val):
                            if not isinstance(val, str):
                                raise ValueError('DocTestFinder.find: __test__ values must be strings, functions, methods, classes, or modules: %r' % (
                                 type(val),))
                            valname = '%s.__test__.%s' % (name, valname)
                            self._find(tests, val, valname, module, source_lines, globs, seen)

            if inspect.isclass(obj) and self._recurse:
                for valname, val in obj.__dict__.items():
                    if isinstance(val, staticmethod):
                        val = getattr(obj, valname)
                    if isinstance(val, classmethod):
                        val = getattr(obj, valname).__func__
                    if not (inspect.isroutine(val) or inspect.isclass(val)):
                        if isinstance(val, property):
                            pass
                        if self._from_module(module, val):
                            valname = '%s.%s' % (name, valname)
                            self._find(tests, val, valname, module, source_lines, globs, seen)

    def _get_test(self, obj, name, module, globs, source_lines):
        if isinstance(obj, str):
            docstring = obj
        else:
            try:
                if obj.__doc__ is None:
                    docstring = ''
                else:
                    docstring = obj.__doc__
                    if not isinstance(docstring, str):
                        docstring = str(docstring)
            except (TypeError, AttributeError):
                docstring = ''

            lineno = self._find_lineno(obj, source_lines)
            if self._exclude_empty:
                if not docstring:
                    return
            elif module is None:
                filename = None
            else:
                filename = getattr(module, '__file__', module.__name__)
                if filename[-4:] == '.pyc':
                    filename = filename[:-1]
            return self._parser.get_doctest(docstring, globs, name, filename, lineno)

    def _find_lineno(self, obj, source_lines):
        lineno = None
        if inspect.ismodule(obj):
            lineno = 0
        if inspect.isclass(obj):
            if source_lines is None:
                return
            pat = re.compile('^\\s*class\\s*%s\\b' % getattr(obj, '__name__', '-'))
            for i, line in enumerate(source_lines):
                if pat.match(line):
                    lineno = i
                    break

        if inspect.ismethod(obj):
            obj = obj.__func__
        if inspect.isfunction(obj):
            obj = obj.__code__
        if inspect.istraceback(obj):
            obj = obj.tb_frame
        if inspect.isframe(obj):
            obj = obj.f_code
        if inspect.iscode(obj):
            lineno = getattr(obj, 'co_firstlineno', None) - 1
        if lineno is not None:
            if source_lines is None:
                return lineno + 1
            pat = re.compile('(^|.*:)\\s*\\w*("|\\\')')
            for lineno in range(lineno, len(source_lines)):
                if pat.match(source_lines[lineno]):
                    return lineno


class DocTestRunner:
    DIVIDER = '**********************************************************************'

    def __init__(self, checker=None, verbose=None, optionflags=0):
        self._checker = checker or OutputChecker()
        if verbose is None:
            verbose = '-v' in sys.argv
        self._verbose = verbose
        self.optionflags = optionflags
        self.original_optionflags = optionflags
        self.tries = 0
        self.failures = 0
        self._name2ft = {}
        self._fakeout = _SpoofOut()

    def report_start(self, out, test, example):
        if self._verbose:
            if example.want:
                out('Trying:\n' + _indent(example.source) + 'Expecting:\n' + _indent(example.want))
            else:
                out('Trying:\n' + _indent(example.source) + 'Expecting nothing\n')

    def report_success(self, out, test, example, got):
        if self._verbose:
            out('ok\n')

    def report_failure(self, out, test, example, got):
        out(self._failure_header(test, example) + self._checker.output_difference(example, got, self.optionflags))

    def report_unexpected_exception(self, out, test, example, exc_info):
        out(self._failure_header(test, example) + 'Exception raised:\n' + _indent(_exception_traceback(exc_info)))

    def _failure_header(self, test, example):
        out = [
         self.DIVIDER]
        if test.filename:
            if test.lineno is not None and example.lineno is not None:
                lineno = test.lineno + example.lineno + 1
            else:
                lineno = '?'
            out.append('File "%s", line %s, in %s' % (
             test.filename, lineno, test.name))
        else:
            out.append('Line %s, in %s' % (example.lineno + 1, test.name))
        out.append('Failed example:')
        source = example.source
        out.append(_indent(source))
        return '\n'.join(out)

    def __run--- This code section failed: ---

 L.1282         0  LOAD_CONST               0
                2  DUP_TOP          
                4  STORE_FAST               'failures'
                6  STORE_FAST               'tries'

 L.1286         8  LOAD_FAST                'self'
               10  LOAD_ATTR                optionflags
               12  STORE_FAST               'original_optionflags'

 L.1288        14  LOAD_GLOBAL              range
               16  LOAD_CONST               3
               18  CALL_FUNCTION_1       1  '1 positional argument'
               20  UNPACK_SEQUENCE_3     3 
               22  STORE_FAST               'SUCCESS'
               24  STORE_FAST               'FAILURE'
               26  STORE_FAST               'BOOM'

 L.1290        28  LOAD_FAST                'self'
               30  LOAD_ATTR                _checker
               32  LOAD_ATTR                check_output
               34  STORE_FAST               'check'

 L.1293     36_38  SETUP_LOOP          622  'to 622'
               40  LOAD_GLOBAL              enumerate
               42  LOAD_FAST                'test'
               44  LOAD_ATTR                examples
               46  CALL_FUNCTION_1       1  '1 positional argument'
               48  GET_ITER         
             50_0  COME_FROM           614  '614'
             50_1  COME_FROM           604  '604'
            50_52  FOR_ITER            620  'to 620'
               54  UNPACK_SEQUENCE_2     2 
               56  STORE_FAST               'examplenum'
               58  STORE_FAST               'example'

 L.1297        60  LOAD_FAST                'self'
               62  LOAD_ATTR                optionflags
               64  LOAD_GLOBAL              REPORT_ONLY_FIRST_FAILURE
               66  BINARY_AND       
               68  JUMP_IF_FALSE_OR_POP    76  'to 76'

 L.1298        70  LOAD_FAST                'failures'
               72  LOAD_CONST               0
               74  COMPARE_OP               >
             76_0  COME_FROM            68  '68'
               76  STORE_FAST               'quiet'

 L.1301        78  LOAD_FAST                'original_optionflags'
               80  LOAD_FAST                'self'
               82  STORE_ATTR               optionflags

 L.1302        84  LOAD_FAST                'example'
               86  LOAD_ATTR                options
               88  POP_JUMP_IF_FALSE   150  'to 150'

 L.1303        90  SETUP_LOOP          150  'to 150'
               92  LOAD_FAST                'example'
               94  LOAD_ATTR                options
               96  LOAD_METHOD              items
               98  CALL_METHOD_0         0  '0 positional arguments'
              100  GET_ITER         
              102  FOR_ITER            148  'to 148'
              104  UNPACK_SEQUENCE_2     2 
              106  STORE_FAST               'optionflag'
              108  STORE_FAST               'val'

 L.1304       110  LOAD_FAST                'val'
              112  POP_JUMP_IF_FALSE   130  'to 130'

 L.1305       114  LOAD_FAST                'self'
              116  DUP_TOP          
              118  LOAD_ATTR                optionflags
              120  LOAD_FAST                'optionflag'
              122  INPLACE_OR       
              124  ROT_TWO          
              126  STORE_ATTR               optionflags
              128  JUMP_BACK           102  'to 102'
            130_0  COME_FROM           112  '112'

 L.1307       130  LOAD_FAST                'self'
              132  DUP_TOP          
              134  LOAD_ATTR                optionflags
              136  LOAD_FAST                'optionflag'
              138  UNARY_INVERT     
              140  INPLACE_AND      
              142  ROT_TWO          
              144  STORE_ATTR               optionflags
              146  JUMP_BACK           102  'to 102'
              148  POP_BLOCK        
            150_0  COME_FROM_LOOP       90  '90'
            150_1  COME_FROM            88  '88'

 L.1310       150  LOAD_FAST                'self'
              152  LOAD_ATTR                optionflags
              154  LOAD_GLOBAL              SKIP
              156  BINARY_AND       
              158  POP_JUMP_IF_FALSE   162  'to 162'

 L.1311       160  CONTINUE             50  'to 50'
            162_0  COME_FROM           158  '158'

 L.1314       162  LOAD_FAST                'tries'
              164  LOAD_CONST               1
              166  INPLACE_ADD      
              168  STORE_FAST               'tries'

 L.1315       170  LOAD_FAST                'quiet'
              172  POP_JUMP_IF_TRUE    188  'to 188'

 L.1316       174  LOAD_FAST                'self'
              176  LOAD_METHOD              report_start
              178  LOAD_FAST                'out'
              180  LOAD_FAST                'test'
              182  LOAD_FAST                'example'
              184  CALL_METHOD_3         3  '3 positional arguments'
              186  POP_TOP          
            188_0  COME_FROM           172  '172'

 L.1321       188  LOAD_STR                 '<doctest %s[%d]>'
              190  LOAD_FAST                'test'
              192  LOAD_ATTR                name
              194  LOAD_FAST                'examplenum'
              196  BUILD_TUPLE_2         2 
              198  BINARY_MODULO    
              200  STORE_FAST               'filename'

 L.1326       202  SETUP_EXCEPT        248  'to 248'

 L.1328       204  LOAD_GLOBAL              exec
              206  LOAD_GLOBAL              compile
              208  LOAD_FAST                'example'
              210  LOAD_ATTR                source
              212  LOAD_FAST                'filename'
              214  LOAD_STR                 'single'

 L.1329       216  LOAD_FAST                'compileflags'
              218  LOAD_CONST               1
              220  CALL_FUNCTION_5       5  '5 positional arguments'
              222  LOAD_FAST                'test'
              224  LOAD_ATTR                globs
              226  CALL_FUNCTION_2       2  '2 positional arguments'
              228  POP_TOP          

 L.1330       230  LOAD_FAST                'self'
              232  LOAD_ATTR                debugger
              234  LOAD_METHOD              set_continue
              236  CALL_METHOD_0         0  '0 positional arguments'
              238  POP_TOP          

 L.1331       240  LOAD_CONST               None
              242  STORE_FAST               'exception'
              244  POP_BLOCK        
              246  JUMP_FORWARD        300  'to 300'
            248_0  COME_FROM_EXCEPT    202  '202'

 L.1332       248  DUP_TOP          
              250  LOAD_GLOBAL              KeyboardInterrupt
              252  COMPARE_OP               exception-match
          254_256  POP_JUMP_IF_FALSE   270  'to 270'
              258  POP_TOP          
              260  POP_TOP          
              262  POP_TOP          

 L.1333       264  RAISE_VARARGS_0       0  'reraise'
              266  POP_EXCEPT       
              268  JUMP_FORWARD        300  'to 300'
            270_0  COME_FROM           254  '254'

 L.1334       270  POP_TOP          
              272  POP_TOP          
              274  POP_TOP          

 L.1335       276  LOAD_GLOBAL              sys
              278  LOAD_METHOD              exc_info
              280  CALL_METHOD_0         0  '0 positional arguments'
              282  STORE_FAST               'exception'

 L.1336       284  LOAD_FAST                'self'
              286  LOAD_ATTR                debugger
              288  LOAD_METHOD              set_continue
              290  CALL_METHOD_0         0  '0 positional arguments'
              292  POP_TOP          
              294  POP_EXCEPT       
              296  JUMP_FORWARD        300  'to 300'
              298  END_FINALLY      
            300_0  COME_FROM           296  '296'
            300_1  COME_FROM           268  '268'
            300_2  COME_FROM           246  '246'

 L.1338       300  LOAD_FAST                'self'
              302  LOAD_ATTR                _fakeout
              304  LOAD_METHOD              getvalue
              306  CALL_METHOD_0         0  '0 positional arguments'
              308  STORE_FAST               'got'

 L.1339       310  LOAD_FAST                'self'
              312  LOAD_ATTR                _fakeout
              314  LOAD_METHOD              truncate
              316  LOAD_CONST               0
              318  CALL_METHOD_1         1  '1 positional argument'
              320  POP_TOP          

 L.1340       322  LOAD_FAST                'FAILURE'
              324  STORE_FAST               'outcome'

 L.1344       326  LOAD_FAST                'exception'
              328  LOAD_CONST               None
              330  COMPARE_OP               is
          332_334  POP_JUMP_IF_FALSE   360  'to 360'

 L.1345       336  LOAD_FAST                'check'
              338  LOAD_FAST                'example'
              340  LOAD_ATTR                want
              342  LOAD_FAST                'got'
              344  LOAD_FAST                'self'
              346  LOAD_ATTR                optionflags
              348  CALL_FUNCTION_3       3  '3 positional arguments'
          350_352  POP_JUMP_IF_FALSE   484  'to 484'

 L.1346       354  LOAD_FAST                'SUCCESS'
              356  STORE_FAST               'outcome'
              358  JUMP_FORWARD        484  'to 484'
            360_0  COME_FROM           332  '332'

 L.1350       360  LOAD_GLOBAL              traceback
              362  LOAD_ATTR                format_exception_only
              364  LOAD_FAST                'exception'
              366  LOAD_CONST               None
              368  LOAD_CONST               2
              370  BUILD_SLICE_2         2 
              372  BINARY_SUBSCR    
              374  CALL_FUNCTION_EX      0  'positional arguments only'
              376  LOAD_CONST               -1
              378  BINARY_SUBSCR    
              380  STORE_FAST               'exc_msg'

 L.1351       382  LOAD_FAST                'quiet'
          384_386  POP_JUMP_IF_TRUE    400  'to 400'

 L.1352       388  LOAD_FAST                'got'
              390  LOAD_GLOBAL              _exception_traceback
              392  LOAD_FAST                'exception'
              394  CALL_FUNCTION_1       1  '1 positional argument'
              396  INPLACE_ADD      
              398  STORE_FAST               'got'
            400_0  COME_FROM           384  '384'

 L.1356       400  LOAD_FAST                'example'
              402  LOAD_ATTR                exc_msg
              404  LOAD_CONST               None
              406  COMPARE_OP               is
          408_410  POP_JUMP_IF_FALSE   418  'to 418'

 L.1357       412  LOAD_FAST                'BOOM'
              414  STORE_FAST               'outcome'
              416  JUMP_FORWARD        484  'to 484'
            418_0  COME_FROM           408  '408'

 L.1360       418  LOAD_FAST                'check'
              420  LOAD_FAST                'example'
              422  LOAD_ATTR                exc_msg
              424  LOAD_FAST                'exc_msg'
              426  LOAD_FAST                'self'
              428  LOAD_ATTR                optionflags
              430  CALL_FUNCTION_3       3  '3 positional arguments'
          432_434  POP_JUMP_IF_FALSE   442  'to 442'

 L.1361       436  LOAD_FAST                'SUCCESS'
              438  STORE_FAST               'outcome'
              440  JUMP_FORWARD        484  'to 484'
            442_0  COME_FROM           432  '432'

 L.1364       442  LOAD_FAST                'self'
              444  LOAD_ATTR                optionflags
              446  LOAD_GLOBAL              IGNORE_EXCEPTION_DETAIL
              448  BINARY_AND       
          450_452  POP_JUMP_IF_FALSE   484  'to 484'

 L.1365       454  LOAD_FAST                'check'
              456  LOAD_GLOBAL              _strip_exception_details
              458  LOAD_FAST                'example'
              460  LOAD_ATTR                exc_msg
              462  CALL_FUNCTION_1       1  '1 positional argument'

 L.1366       464  LOAD_GLOBAL              _strip_exception_details
              466  LOAD_FAST                'exc_msg'
              468  CALL_FUNCTION_1       1  '1 positional argument'

 L.1367       470  LOAD_FAST                'self'
              472  LOAD_ATTR                optionflags
              474  CALL_FUNCTION_3       3  '3 positional arguments'
          476_478  POP_JUMP_IF_FALSE   484  'to 484'

 L.1368       480  LOAD_FAST                'SUCCESS'
              482  STORE_FAST               'outcome'
            484_0  COME_FROM           476  '476'
            484_1  COME_FROM           450  '450'
            484_2  COME_FROM           440  '440'
            484_3  COME_FROM           416  '416'
            484_4  COME_FROM           358  '358'
            484_5  COME_FROM           350  '350'

 L.1371       484  LOAD_FAST                'outcome'
              486  LOAD_FAST                'SUCCESS'
              488  COMPARE_OP               is
          490_492  POP_JUMP_IF_FALSE   518  'to 518'

 L.1372       494  LOAD_FAST                'quiet'
          496_498  POP_JUMP_IF_TRUE    602  'to 602'

 L.1373       500  LOAD_FAST                'self'
              502  LOAD_METHOD              report_success
              504  LOAD_FAST                'out'
              506  LOAD_FAST                'test'
              508  LOAD_FAST                'example'
              510  LOAD_FAST                'got'
              512  CALL_METHOD_4         4  '4 positional arguments'
              514  POP_TOP          
              516  JUMP_FORWARD        602  'to 602'
            518_0  COME_FROM           490  '490'

 L.1374       518  LOAD_FAST                'outcome'
              520  LOAD_FAST                'FAILURE'
              522  COMPARE_OP               is
          524_526  POP_JUMP_IF_FALSE   560  'to 560'

 L.1375       528  LOAD_FAST                'quiet'
          530_532  POP_JUMP_IF_TRUE    550  'to 550'

 L.1376       534  LOAD_FAST                'self'
              536  LOAD_METHOD              report_failure
              538  LOAD_FAST                'out'
              540  LOAD_FAST                'test'
              542  LOAD_FAST                'example'
              544  LOAD_FAST                'got'
              546  CALL_METHOD_4         4  '4 positional arguments'
              548  POP_TOP          
            550_0  COME_FROM           530  '530'

 L.1377       550  LOAD_FAST                'failures'
              552  LOAD_CONST               1
              554  INPLACE_ADD      
              556  STORE_FAST               'failures'
              558  JUMP_FORWARD        602  'to 602'
            560_0  COME_FROM           524  '524'

 L.1378       560  LOAD_FAST                'outcome'
              562  LOAD_FAST                'BOOM'
              564  COMPARE_OP               is
          566_568  POP_JUMP_IF_FALSE   602  'to 602'

 L.1379       570  LOAD_FAST                'quiet'
          572_574  POP_JUMP_IF_TRUE    592  'to 592'

 L.1380       576  LOAD_FAST                'self'
              578  LOAD_METHOD              report_unexpected_exception
              580  LOAD_FAST                'out'
              582  LOAD_FAST                'test'
              584  LOAD_FAST                'example'

 L.1381       586  LOAD_FAST                'exception'
              588  CALL_METHOD_4         4  '4 positional arguments'
              590  POP_TOP          
            592_0  COME_FROM           572  '572'

 L.1382       592  LOAD_FAST                'failures'
              594  LOAD_CONST               1
              596  INPLACE_ADD      
              598  STORE_FAST               'failures'
              600  JUMP_FORWARD        602  'to 602'
            602_0  COME_FROM           600  '600'
            602_1  COME_FROM           566  '566'
            602_2  COME_FROM           558  '558'
            602_3  COME_FROM           516  '516'
            602_4  COME_FROM           496  '496'

 L.1386       602  LOAD_FAST                'failures'
              604  POP_JUMP_IF_FALSE    50  'to 50'
              606  LOAD_FAST                'self'
              608  LOAD_ATTR                optionflags
              610  LOAD_GLOBAL              FAIL_FAST
              612  BINARY_AND       
              614  POP_JUMP_IF_FALSE    50  'to 50'

 L.1387       616  BREAK_LOOP       
              618  JUMP_BACK            50  'to 50'
              620  POP_BLOCK        
            622_0  COME_FROM_LOOP       36  '36'

 L.1390       622  LOAD_FAST                'original_optionflags'
              624  LOAD_FAST                'self'
              626  STORE_ATTR               optionflags

 L.1393       628  LOAD_FAST                'self'
              630  LOAD_METHOD              _DocTestRunner__record_outcome
              632  LOAD_FAST                'test'
              634  LOAD_FAST                'failures'
              636  LOAD_FAST                'tries'
              638  CALL_METHOD_3         3  '3 positional arguments'
              640  POP_TOP          

 L.1394       642  LOAD_GLOBAL              TestResults
              644  LOAD_FAST                'failures'
              646  LOAD_FAST                'tries'
              648  CALL_FUNCTION_2       2  '2 positional arguments'
              650  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 622_0

    def __record_outcome(self, test, f, t):
        f2, t2 = self._name2ft.get(test.name, (0, 0))
        self._name2ft[test.name] = (f + f2, t + t2)
        self.failures += f
        self.tries += t

    _DocTestRunner__LINECACHE_FILENAME_RE = re.compile('<doctest (?P<name>.+)\\[(?P<examplenum>\\d+)\\]>$')

    def __patched_linecache_getlines(self, filename, module_globals=None):
        m = self._DocTestRunner__LINECACHE_FILENAME_RE.match(filename)
        if m:
            if m.group('name') == self.test.name:
                example = self.test.examples[int(m.group('examplenum'))]
                return example.source.splitlines(keepends=True)
        return self.save_linecache_getlines(filename, module_globals)

    def run(self, test, compileflags=None, out=None, clear_globs=True):
        self.test = test
        if compileflags is None:
            compileflags = _extract_future_flags(test.globs)
        else:
            save_stdout = sys.stdout
            if out is None:
                encoding = save_stdout.encoding
                if encoding is None or encoding.lower() == 'utf-8':
                    out = save_stdout.write
                else:

                    def out(s):
                        s = str(s.encode(encoding, 'backslashreplace'), encoding)
                        save_stdout.write(s)

        sys.stdout = self._fakeout
        save_trace = sys.gettrace()
        save_set_trace = pdb.set_trace
        self.debugger = _OutputRedirectingPdb(save_stdout)
        self.debugger.reset()
        pdb.set_trace = self.debugger.set_trace
        self.save_linecache_getlines = linecache.getlines
        linecache.getlines = self._DocTestRunner__patched_linecache_getlines
        save_displayhook = sys.displayhook
        sys.displayhook = sys.__displayhook__
        try:
            return self._DocTestRunner__run(test, compileflags, out)
        finally:
            sys.stdout = save_stdout
            pdb.set_trace = save_set_trace
            sys.settrace(save_trace)
            linecache.getlines = self.save_linecache_getlines
            sys.displayhook = save_displayhook
            if clear_globs:
                test.globs.clear()
                import builtins
                builtins._ = None

    def summarize(self, verbose=None):
        if verbose is None:
            verbose = self._verbose
        notests = []
        passed = []
        failed = []
        totalt = totalf = 0
        for x in self._name2ft.items():
            name, (f, t) = x
            totalt += t
            totalf += f
            if t == 0:
                notests.append(name)
            elif f == 0:
                passed.append((name, t))
            else:
                failed.append(x)

        if verbose:
            if notests:
                print(len(notests), 'items had no tests:')
                notests.sort()
                for thing in notests:
                    print('   ', thing)

            if passed:
                print(len(passed), 'items passed all tests:')
                passed.sort()
                for thing, count in passed:
                    print(' %3d tests in %s' % (count, thing))

        if failed:
            print(self.DIVIDER)
            print(len(failed), 'items had failures:')
            failed.sort()
            for thing, (f, t) in failed:
                print(' %3d of %3d in %s' % (f, t, thing))

        if verbose:
            print(totalt, 'tests in', len(self._name2ft), 'items.')
            print(totalt - totalf, 'passed and', totalf, 'failed.')
        if totalf:
            print('***Test Failed***', totalf, 'failures.')
        else:
            if verbose:
                print('Test passed.')
            return TestResults(totalf, totalt)

    def merge(self, other):
        d = self._name2ft
        for name, (f, t) in other._name2ft.items():
            if name in d:
                f2, t2 = d[name]
                f = f + f2
                t = t + t2
            d[name] = (
             f, t)


class OutputChecker:

    def _toAscii(self, s):
        return str(s.encode('ASCII', 'backslashreplace'), 'ASCII')

    def check_output(self, want, got, optionflags):
        got = self._toAscii(got)
        want = self._toAscii(want)
        if got == want:
            return True
        if not optionflags & DONT_ACCEPT_TRUE_FOR_1:
            if (
             got, want) == ('True\n', '1\n'):
                return True
            if (
             got, want) == ('False\n', '0\n'):
                return True
        if not optionflags & DONT_ACCEPT_BLANKLINE:
            want = re.sub('(?m)^%s\\s*?$' % re.escape(BLANKLINE_MARKER), '', want)
            got = re.sub('(?m)^[^\\S\\n]+$', '', got)
            if got == want:
                return True
        if optionflags & NORMALIZE_WHITESPACE:
            got = ' '.join(got.split())
            want = ' '.join(want.split())
            if got == want:
                return True
        if optionflags & ELLIPSIS:
            if _ellipsis_match(want, got):
                return True
        return False

    def _do_a_fancy_diff(self, want, got, optionflags):
        if not optionflags & (REPORT_UDIFF | REPORT_CDIFF | REPORT_NDIFF):
            return False
        if optionflags & REPORT_NDIFF:
            return True
        return want.count('\n') > 2 and got.count('\n') > 2

    def output_difference(self, example, got, optionflags):
        want = example.want
        if not optionflags & DONT_ACCEPT_BLANKLINE:
            got = re.sub('(?m)^[ ]*(?=\n)', BLANKLINE_MARKER, got)
        if self._do_a_fancy_diff(want, got, optionflags):
            want_lines = want.splitlines(keepends=True)
            got_lines = got.splitlines(keepends=True)
            if optionflags & REPORT_UDIFF:
                diff = difflib.unified_diff(want_lines, got_lines, n=2)
                diff = list(diff)[2:]
                kind = 'unified diff with -expected +actual'
            else:
                if optionflags & REPORT_CDIFF:
                    diff = difflib.context_diff(want_lines, got_lines, n=2)
                    diff = list(diff)[2:]
                    kind = 'context diff with expected followed by actual'
                else:
                    if optionflags & REPORT_NDIFF:
                        engine = difflib.Differ(charjunk=(difflib.IS_CHARACTER_JUNK))
                        diff = list(engine.compare(want_lines, got_lines))
                        kind = 'ndiff with -expected +actual'
                    else:
                        diff = [line.rstrip() + '\n' for line in diff]
                        return 'Differences (%s):\n' % kind + _indent(''.join(diff))
        if want:
            if got:
                return 'Expected:\n%sGot:\n%s' % (_indent(want), _indent(got))
        if want:
            return 'Expected:\n%sGot nothing\n' % _indent(want)
        if got:
            return 'Expected nothing\nGot:\n%s' % _indent(got)
        return 'Expected nothing\nGot nothing\n'


class DocTestFailure(Exception):

    def __init__(self, test, example, got):
        self.test = test
        self.example = example
        self.got = got

    def __str__(self):
        return str(self.test)


class UnexpectedException(Exception):

    def __init__(self, test, example, exc_info):
        self.test = test
        self.example = example
        self.exc_info = exc_info

    def __str__(self):
        return str(self.test)


class DebugRunner(DocTestRunner):

    def run(self, test, compileflags=None, out=None, clear_globs=True):
        r = DocTestRunner.run(self, test, compileflags, out, False)
        if clear_globs:
            test.globs.clear()
        return r

    def report_unexpected_exception(self, out, test, example, exc_info):
        raise UnexpectedException(test, example, exc_info)

    def report_failure(self, out, test, example, got):
        raise DocTestFailure(test, example, got)


master = None

def testmod(m=None, name=None, globs=None, verbose=None, report=True, optionflags=0, extraglobs=None, raise_on_error=False, exclude_empty=False):
    global master
    if m is None:
        m = sys.modules.get('__main__')
    else:
        if not inspect.ismodule(m):
            raise TypeError('testmod: module required; %r' % (m,))
        else:
            if name is None:
                name = m.__name__
            finder = DocTestFinder(exclude_empty=exclude_empty)
            if raise_on_error:
                runner = DebugRunner(verbose=verbose, optionflags=optionflags)
            else:
                runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
        for test in finder.find(m, name, globs=globs, extraglobs=extraglobs):
            runner.run(test)

        if report:
            runner.summarize()
        if master is None:
            master = runner
        else:
            master.merge(runner)
    return TestResults(runner.failures, runner.tries)


def testfile(filename, module_relative=True, name=None, package=None, globs=None, verbose=None, report=True, optionflags=0, extraglobs=None, raise_on_error=False, parser=DocTestParser(), encoding=None):
    global master
    if package:
        if not module_relative:
            raise ValueError('Package may only be specified for module-relative paths.')
    else:
        text, filename = _load_testfile(filename, package, module_relative, encoding or 'utf-8')
        if name is None:
            name = os.path.basename(filename)
        else:
            if globs is None:
                globs = {}
            else:
                globs = globs.copy()
            if extraglobs is not None:
                globs.update(extraglobs)
            if '__name__' not in globs:
                globs['__name__'] = '__main__'
            if raise_on_error:
                runner = DebugRunner(verbose=verbose, optionflags=optionflags)
            else:
                runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
        test = parser.get_doctest(text, globs, name, filename, 0)
        runner.run(test)
        if report:
            runner.summarize()
        if master is None:
            master = runner
        else:
            master.merge(runner)
    return TestResults(runner.failures, runner.tries)


def run_docstring_examples(f, globs, verbose=False, name='NoName', compileflags=None, optionflags=0):
    finder = DocTestFinder(verbose=verbose, recurse=False)
    runner = DocTestRunner(verbose=verbose, optionflags=optionflags)
    for test in finder.find(f, name, globs=globs):
        runner.run(test, compileflags=compileflags)


_unittest_reportflags = 0

def set_unittest_reportflags(flags):
    global _unittest_reportflags
    if flags & REPORTING_FLAGS != flags:
        raise ValueError('Only reporting flags allowed', flags)
    old = _unittest_reportflags
    _unittest_reportflags = flags
    return old


class DocTestCase(unittest.TestCase):

    def __init__(self, test, optionflags=0, setUp=None, tearDown=None, checker=None):
        unittest.TestCase.__init__(self)
        self._dt_optionflags = optionflags
        self._dt_checker = checker
        self._dt_test = test
        self._dt_setUp = setUp
        self._dt_tearDown = tearDown

    def setUp(self):
        test = self._dt_test
        if self._dt_setUp is not None:
            self._dt_setUp(test)

    def tearDown(self):
        test = self._dt_test
        if self._dt_tearDown is not None:
            self._dt_tearDown(test)
        test.globs.clear()

    def runTest(self):
        test = self._dt_test
        old = sys.stdout
        new = StringIO()
        optionflags = self._dt_optionflags
        if not optionflags & REPORTING_FLAGS:
            optionflags |= _unittest_reportflags
        runner = DocTestRunner(optionflags=optionflags, checker=(self._dt_checker),
          verbose=False)
        try:
            runner.DIVIDER = '----------------------------------------------------------------------'
            failures, tries = runner.run(test,
              out=(new.write), clear_globs=False)
        finally:
            sys.stdout = old

        if failures:
            raise self.failureException(self.format_failure(new.getvalue()))

    def format_failure(self, err):
        test = self._dt_test
        if test.lineno is None:
            lineno = 'unknown line number'
        else:
            lineno = '%s' % test.lineno
        lname = '.'.join(test.name.split('.')[-1:])
        return 'Failed doctest test for %s\n  File "%s", line %s, in %s\n\n%s' % (
         test.name, test.filename, lineno, lname, err)

    def debug(self):
        self.setUp()
        runner = DebugRunner(optionflags=(self._dt_optionflags), checker=(self._dt_checker),
          verbose=False)
        runner.run((self._dt_test), clear_globs=False)
        self.tearDown()

    def id(self):
        return self._dt_test.name

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self._dt_test == other._dt_test and self._dt_optionflags == other._dt_optionflags and self._dt_setUp == other._dt_setUp and self._dt_tearDown == other._dt_tearDown and self._dt_checker == other._dt_checker

    def __hash__(self):
        return hash((self._dt_optionflags, self._dt_setUp, self._dt_tearDown,
         self._dt_checker))

    def __repr__(self):
        name = self._dt_test.name.split('.')
        return '%s (%s)' % (name[-1], '.'.join(name[:-1]))

    __str__ = __repr__

    def shortDescription(self):
        return 'Doctest: ' + self._dt_test.name


class SkipDocTestCase(DocTestCase):

    def __init__(self, module):
        self.module = module
        DocTestCase.__init__(self, None)

    def setUp(self):
        self.skipTest('DocTestSuite will not work with -O2 and above')

    def test_skip(self):
        pass

    def shortDescription(self):
        return 'Skipping tests from %s' % self.module.__name__

    __str__ = shortDescription


class _DocTestSuite(unittest.TestSuite):

    def _removeTestAtIndex(self, index):
        pass


def DocTestSuite(module=None, globs=None, extraglobs=None, test_finder=None, **options):
    if test_finder is None:
        test_finder = DocTestFinder()
    module = _normalize_module(module)
    tests = test_finder.find(module, globs=globs, extraglobs=extraglobs)
    if not tests:
        if sys.flags.optimize >= 2:
            suite = _DocTestSuite()
            suite.addTest(SkipDocTestCase(module))
            return suite
    tests.sort()
    suite = _DocTestSuite()
    for test in tests:
        if len(test.examples) == 0:
            continue
        if not test.filename:
            filename = module.__file__
            if filename[-4:] == '.pyc':
                filename = filename[:-1]
            test.filename = filename
        suite.addTest(DocTestCase(test, **options))

    return suite


class DocFileCase(DocTestCase):

    def id(self):
        return '_'.join(self._dt_test.name.split('.'))

    def __repr__(self):
        return self._dt_test.filename

    __str__ = __repr__

    def format_failure(self, err):
        return 'Failed doctest test for %s\n  File "%s", line 0\n\n%s' % (
         self._dt_test.name, self._dt_test.filename, err)


def DocFileTest(path, module_relative=True, package=None, globs=None, parser=DocTestParser(), encoding=None, **options):
    if globs is None:
        globs = {}
    else:
        globs = globs.copy()
    if package:
        if not module_relative:
            raise ValueError('Package may only be specified for module-relative paths.')
    doc, path = _load_testfile(path, package, module_relative, encoding or 'utf-8')
    if '__file__' not in globs:
        globs['__file__'] = path
    name = os.path.basename(path)
    test = parser.get_doctest(doc, globs, name, path, 0)
    return DocFileCase(test, **options)


def DocFileSuite(*paths, **kw):
    suite = _DocTestSuite()
    if kw.get('module_relative', True):
        kw['package'] = _normalize_module(kw.get('package'))
    for path in paths:
        suite.addTest(DocFileTest(path, **kw))

    return suite


def script_from_examples(s):
    output = []
    for piece in DocTestParser().parse(s):
        if isinstance(piece, Example):
            output.append(piece.source[:-1])
            want = piece.want
            if want:
                output.append('# Expected:')
                output += ['## ' + l for l in want.split('\n')[:-1]]
        else:
            output += [_comment_line(l) for l in piece.split('\n')[:-1]]

    while output and output[-1] == '#':
        output.pop()

    while output and output[0] == '#':
        output.pop(0)

    return '\n'.join(output) + '\n'


def testsource(module, name):
    module = _normalize_module(module)
    tests = DocTestFinder().find(module)
    test = [t for t in tests if t.name == name]
    if not test:
        raise ValueError(name, 'not found in tests')
    test = test[0]
    testsrc = script_from_examples(test.docstring)
    return testsrc


def debug_src(src, pm=False, globs=None):
    testsrc = script_from_examples(src)
    debug_script(testsrc, pm, globs)


def debug_script(src, pm=False, globs=None):
    import pdb
    if globs:
        globs = globs.copy()
    else:
        globs = {}
    if pm:
        try:
            exec(src, globs, globs)
        except:
            print(sys.exc_info()[1])
            p = pdb.Pdb(nosigint=True)
            p.reset()
            p.interaction(None, sys.exc_info()[2])

    else:
        pdb.Pdb(nosigint=True).run('exec(%r)' % src, globs, globs)


def debug(module, name, pm=False):
    module = _normalize_module(module)
    testsrc = testsource(module, name)
    debug_script(testsrc, pm, module.__dict__)


class _TestClass:

    def __init__(self, val):
        self.val = val

    def square(self):
        self.val = self.val ** 2
        return self

    def get(self):
        return self.val


__test__ = {
 '_TestClass': '_TestClass', 
 'string': "'\\n                      Example of a string object, searched as-is.\\n                      >>> x = 1; y = 2\\n                      >>> x + y, x * y\\n                      (3, 2)\\n                      '", 
 'bool-int equivalence': "'\\n                                    In 2.2, boolean expressions displayed\\n                                    0 or 1.  By default, we still accept\\n                                    them.  This can be disabled by passing\\n                                    DONT_ACCEPT_TRUE_FOR_1 to the new\\n                                    optionflags argument.\\n                                    >>> 4 == 4\\n                                    1\\n                                    >>> 4 == 4\\n                                    True\\n                                    >>> 4 > 4\\n                                    0\\n                                    >>> 4 > 4\\n                                    False\\n                                    '", 
 'blank lines': '"\\n                Blank lines can be marked with <BLANKLINE>:\\n                    >>> print(\'foo\\\\n\\\\nbar\\\\n\')\\n                    foo\\n                    <BLANKLINE>\\n                    bar\\n                    <BLANKLINE>\\n            "', 
 'ellipsis': '"\\n                If the ellipsis flag is used, then \'...\' can be used to\\n                elide substrings in the desired output:\\n                    >>> print(list(range(1000))) #doctest: +ELLIPSIS\\n                    [0, 1, 2, ..., 999]\\n            "', 
 'whitespace normalization': "'\\n                If the whitespace normalization flag is used, then\\n                differences in whitespace are ignored.\\n                    >>> print(list(range(30))) #doctest: +NORMALIZE_WHITESPACE\\n                    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,\\n                     15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,\\n                     27, 28, 29]\\n            '"}

def _test():
    import argparse
    parser = argparse.ArgumentParser(description='doctest runner')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print very verbose output for all tests')
    parser.add_argument('-o', '--option', action='append', choices=(OPTIONFLAGS_BY_NAME.keys()),
      default=[],
      help='specify a doctest option flag to apply to the test run; may be specified more than once to apply multiple options')
    parser.add_argument('-f', '--fail-fast', action='store_true', help='stop running tests after first failure (this is a shorthand for -o FAIL_FAST, and is in addition to any other -o options)')
    parser.add_argument('file', nargs='+', help='file containing the tests to run')
    args = parser.parse_args()
    testfiles = args.file
    verbose = args.verbose
    options = 0
    for option in args.option:
        options |= OPTIONFLAGS_BY_NAME[option]

    if args.fail_fast:
        options |= FAIL_FAST
    for filename in testfiles:
        if filename.endswith('.py'):
            dirname, filename = os.path.split(filename)
            sys.path.insert(0, dirname)
            m = __import__(filename[:-3])
            del sys.path[0]
            failures, _ = testmod(m, verbose=verbose, optionflags=options)
        else:
            failures, _ = testfile(filename, module_relative=False, verbose=verbose,
              optionflags=options)
        if failures:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(_test())