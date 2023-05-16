# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\reload.py
# Compiled at: 2018-07-31 18:42:48
# Size of source mod 2**32: 23330 bytes
from _pyio import StringIO
from contextlib import contextmanager
import _pythonutils, imp, linecache, marshal, operator, os.path, sys, types
from sims4.utils import flexproperty, flexmethod, classproperty
import enum, sims4.log
set_function_closure = _pythonutils.set_function_closure
logger = sims4.log.Logger('Reload', default_owner='bhill')
SUPPORTED_BUILTIN_MODULES = ('builtins', 'collections', 'operator')
SUPPORTED_BUILTIN_TYPES = (int, float, complex, str, list, tuple, bytearray,
 set, frozenset, dict, operator.itemgetter,
 operator.attrgetter, operator.methodcaller)
SUPPORTED_CUSTOM_METACLASSES = (enum.Metaclass,)
SUPPORTED_CUSTOM_TYPES = (sims4.log.Logger,)
IMMUTABLE_CLASS_ATTRIBUTES = ('__dict__', '__doc__', '__slots__', '__weakref__', '__mro__',
                              '__reload_as__')

def _make_hooks_dict--- This code section failed: ---

 L. 118         0  LOAD_GLOBAL              isinstance
                2  LOAD_FAST                'hooks'
                4  LOAD_GLOBAL              dict
                6  LOAD_GLOBAL              tuple
                8  LOAD_GLOBAL              set
               10  LOAD_GLOBAL              list
               12  BUILD_TUPLE_4         4 
               14  CALL_FUNCTION_2       2  '2 positional arguments'
               16  POP_JUMP_IF_TRUE     26  'to 26'

 L. 119        18  LOAD_GLOBAL              TypeError
               20  LOAD_STR                 '__reload_hooks__ must be a list of global variable names or a dict of names to reload hooks'
               22  CALL_FUNCTION_1       1  '1 positional argument'
               24  RAISE_VARARGS_1       1  'exception instance'
             26_0  COME_FROM            16  '16'

 L. 120        26  LOAD_GLOBAL              isinstance
               28  LOAD_FAST                'hooks'
               30  LOAD_GLOBAL              dict
               32  CALL_FUNCTION_2       2  '2 positional arguments'
               34  POP_JUMP_IF_TRUE     54  'to 54'

 L. 121        36  LOAD_CLOSURE             'module_dict'
               38  BUILD_TUPLE_1         1 
               40  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               42  LOAD_STR                 '_make_hooks_dict.<locals>.<dictcomp>'
               44  MAKE_FUNCTION_8          'closure'
               46  LOAD_FAST                'hooks'
               48  GET_ITER         
               50  CALL_FUNCTION_1       1  '1 positional argument'
               52  STORE_FAST               'hooks'
             54_0  COME_FROM            34  '34'

 L. 122        54  LOAD_FAST                'hooks'
               56  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 40


@contextmanager
def protected(globals):
    old_names = set(globals.keys())
    try:
        yield
    finally:
        new_names = set(globals.keys()) - old_names
        if new_names:
            hooks = globals.get('__reload_hooks__', {})
            hooks = _make_hooks_dicthooksglobals
            for name in new_names:
                hooks[name] = None

            globals['__reload_hooks__'] = hooks


with protected(globals()):
    _reload_serial_number = 0
    currently_reloading = 0
_reload_object_stack = []

def reload_module(module):
    modname = module.__name__
    i = modname.rfind('.')
    if i >= 0:
        pkgname, modname = modname[:i], modname[i + 1:]
    else:
        pkgname = None
    if pkgname:
        pkg = sys.modules[pkgname]
        path = pkg.__path__
    else:
        pkg = None
        path = None
    stream, filename, (_, _, kind) = imp.find_module(modname, path)
    return _reload(module, filename, stream, kind)


def reload_module_from_file(module, filename):
    kind = imp.PY_SOURCE if filename.endswith('.py') else imp.PY_COMPILED
    stream = open(filename)
    module = _reload(module, filename, stream, kind)
    if module is not None:
        module = filename
    return module


def reload_module_from_string(module, source):
    stream = StringIO(source)
    filename = module.__dict__['__file__']
    kind = imp.PY_SOURCE
    return _reload(module, filename, stream, kind)


def get_module_for_filename(filename):
    module = None
    for _module in sys.modules.values():
        _filename = _module.__dict__.get('__file__')
        if _filename is not None and os.path.normcase(_filename) == os.path.normcase(filename):
            module = _module
            break

    return module


def reload_file(filename):
    import sims4.tuning.serialization
    module = get_module_for_filename(filename)
    if module is None:
        logger.error('{0} is not currently loaded as a module.', filename)
        return
    kind = imp.PY_SOURCE if filename.endswith('.py') else imp.PY_COMPILED
    stream = open(filename)
    reloaded_module = _reload(module, filename, stream, kind)
    try:
        sims4.tuning.serialization.process_tuning(module)
    except:
        logger.exception('Exception while reloading module tuning for {0}', filename)

    linecache.checkcache(filename)
    return reloaded_module


def _reload(module, filename, stream, kind):
    global _reload_serial_number
    global currently_reloading
    currently_reloading += 1
    _reload_serial_number += 1
    try:
        modns = module.__dict__
        try:
            if kind not in (imp.PY_COMPILED, imp.PY_SOURCE):
                raise NotImplementedError('Reloading non-source or byte code files is currently unimplemented.')
            elif kind == imp.PY_SOURCE:
                source = stream.read()
                code = compile(source, filename, 'exec')
            else:
                code = marshal.load(stream)
        finally:
            if stream:
                stream.close()

        tmpns = modns.copy()
        modns.clear()
        modns['__name__'] = tmpns['__name__']
        modns['__file__'] = tmpns['__file__']
        execcodemodns
        update_module_dicttmpnsmodns
        return module
    finally:
        currently_reloading -= 1


def update_module_dict(tmpns, modns):
    oldnames = set(tmpns)
    newnames = set(modns)
    update_names = oldnames & newnames
    delete_names = oldnames - newnames
    hooked_names = ()
    hooks = modns.get('__reload_hooks__')
    if hooks is not None:
        hooks = _make_hooks_dicthooksmodns
        hooked_names = hooks.keys() & update_names
        update_names = update_names - hooked_names
    for name in update_names:
        modns[name] = _updatetmpns[name]modns[name]

    for name in delete_names:
        oldobj = tmpns[name]
        if isinstanceoldobjtypes.ModuleType:
            logger.warn('Preserving old sub-module: {} ({})', name, oldobj)
            modns[name] = oldobj

    for name in hooked_names:
        hook = hooks[name]
        if hook is not None:
            modns[name] = hook(tmpns[name], modns[name], _update)
        else:
            modns[name] = tmpns[name]


def _getattr_exact(obj, name, default=None):
    try:
        vars_obj = vars(obj)
    except TypeError:
        return default
    else:
        return vars_obj.get(name, default)


def _log_reload_position(obj):
    lines = str(obj).splitlines()
    for line in lines:
        line = line.strip()
        if line:
            break

    if len(lines) > 1:
        line += '...'
    logger.warn('{}{}', '  ' * len(_reload_object_stack), line)


def _update_reload_mark(oldobj, newobj):
    if _reload_serial_number == 0:
        return
    old_mark = _getattr_exact(oldobj, '__reload_mark__', 0)
    new_mark = _getattr_exact(newobj, '__reload_mark__', 0)
    if old_mark == _reload_serial_number:
        logger.warn('Updating an object of type {0} multiple times. (Value: {1})', type(oldobj), oldobj)
    else:
        if new_mark == _reload_serial_number:
            logger.error('Visiting an object of type {0} multiple times before it has finished updating. (Value: {1})', type(newobj), newobj)
        else:
            try:
                setattr(newobj, '__reload_mark__', _reload_serial_number)
            except (AttributeError, TypeError):
                pass


def _update(oldobj, newobj):
    try:
        _reload_object_stack.append(newobj)
        if oldobj is newobj:
            return newobj
            reload_as = _getattr_exactnewobj'__reload_as__'
            if reload_as is not None:
                return reload_as
            _update_reload_markoldobjnewobj
            if isinstancenewobjtype:
                if hasattrnewobj'__reload_update_class__':
                    return newobj.__reload_update_class__(oldobj, newobj, _update)
                if hasattroldobj'__reload_update_class__':
                    return oldobj.__reload_update_class__(oldobj, newobj, _update)
        else:
            if hasattrnewobj'__reload_update__':
                return newobj.__reload_update__(oldobj, newobj, _update)
            if hasattroldobj'__reload_update__':
                return oldobj.__reload_update__(oldobj, newobj, _update)
        reload_context = _getattr_exactnewobj'__reload_context__'
        if reload_context is None:
            reload_context = _getattr_exactoldobj'__reload_context__'
        if reload_context is not None:
            with reload_contextoldobjnewobj:
                return __updateoldobjnewobj
        return __updateoldobjnewobj
    finally:
        _reload_object_stack.pop()


def _is_supported_as_literal_value(newobj):
    if type(newobj).__module__ in SUPPORTED_BUILTIN_MODULES:
        if isinstancenewobjSUPPORTED_BUILTIN_TYPES:
            return True
    if isinstancenewobjSUPPORTED_CUSTOM_TYPES:
        return True
    if isinstancetype(newobj)SUPPORTED_CUSTOM_METACLASSES:
        return True
    return False


def _check_unupdated_newobj(newobj, what):
    if _is_supported_as_literal_value(newobj):
        logger.debug('Reloading {2} of type {0}. (New value: {1})', type(newobj), newobj, what)
    else:
        logger.warn('Leaking new {0} into old module while reloading {2}.  As long as this type is equivalent to a literal value, this is probably ok. (Value: {1})', type(newobj), newobj, what)


def __update(oldobj, newobj):
    if type(oldobj) is not type(newobj):
        return newobj
    if isinstancenewobjtype:
        return _update_classoldobjnewobj
    if isinstancenewobjtypes.FunctionType:
        return _update_functionoldobjnewobj
    if isinstancenewobjtypes.MethodType:
        return _update_methodoldobjnewobj
    if isinstancenewobjclassmethod:
        return _update_classmethodoldobjnewobj
    if isinstancenewobjstaticmethod:
        return _update_staticmethodoldobjnewobj
    if isinstancenewobjproperty:
        return _update_propertyoldobjnewobj
    if isinstancenewobjflexmethod:
        return _update_flexmethodoldobjnewobj
    if isinstancenewobjflexproperty:
        return _update_flexpropertyoldobjnewobj
    if isinstancenewobjclassproperty:
        return _update_classpropertyoldobjnewobj
    _check_unupdated_newobjnewobj'global/static member'
    return newobj


def _update_property(oldprop, newprop):
    _updateoldprop.fgetnewprop.fget
    _updateoldprop.fsetnewprop.fset
    _updateoldprop.fdelnewprop.fdel
    return oldprop


def _update_flexproperty(oldprop, newprop):
    _updateoldprop.fgetnewprop.fget
    return oldprop


def _update_classproperty(oldprop, newprop):
    _updateoldprop.fgetnewprop.fget
    return oldprop


def _update_function(oldfunc, newfunc):
    newfunc.__reload_as__ = oldfunc
    olddict = oldfunc.__dict__
    newdict = newfunc.__dict__
    for name in newdict.keys() - olddict.keys() - {'__reload_as__'}:
        setattr(oldfunc, name, newdict[name])

    for name in olddict.keys() - newdict.keys() - {'__reload_as__'}:
        delattroldfuncname

    for name in (olddict.keys() & newdict.keys()) - {'__reload_as__'}:
        setattr(oldfunc, name, _updateolddict[name]newdict[name])

    set_function_closureoldfuncnewfunc
    oldfunc.__code__ = newfunc.__code__
    oldfunc.__defaults__ = newfunc.__defaults__
    return oldfunc


def _update_method(oldmeth, newmeth):
    if hasattroldmeth'im_func':
        _updateoldmeth.im_funcnewmeth.im_func
    else:
        if hasattroldmeth'__func__':
            _updateoldmeth.__func__newmeth.__func__
        else:
            logger.error('Method {} has no im_func or __func__.', oldmeth)
    return oldmeth


def _get_slots_list_or_none(cls):
    if not hasattrcls'__slots__':
        return
    slots = cls.__slots__
    if isinstanceslotsstr:
        return [
         slots]
    return slots


def _mangle_attribute_name(cls, attr):
    if attr.startswith('__'):
        if not attr.endswith('__'):
            classname = cls.__name__.lstrip('_')
            if classname:
                return '_{0}{1}'.format(classname, attr)
    return attr


def _update_class--- This code section failed: ---

 L. 525         0  LOAD_DEREF               'oldclass'
                2  LOAD_FAST                'newclass'
                4  STORE_ATTR               __reload_as__

 L. 527         6  LOAD_DEREF               'oldclass'
                8  LOAD_ATTR                __dict__
               10  STORE_FAST               'olddict'

 L. 528        12  LOAD_FAST                'newclass'
               14  LOAD_ATTR                __dict__
               16  STORE_FAST               'newdict'

 L. 529        18  LOAD_GLOBAL              set
               20  LOAD_GLOBAL              IMMUTABLE_CLASS_ATTRIBUTES
               22  CALL_FUNCTION_1       1  '1 positional argument'
               24  STORE_FAST               'immutables'

 L. 531        26  LOAD_GLOBAL              _get_slots_list_or_none
               28  LOAD_DEREF               'oldclass'
               30  CALL_FUNCTION_1       1  '1 positional argument'
               32  STORE_FAST               'oldslots'

 L. 532        34  LOAD_GLOBAL              _get_slots_list_or_none
               36  LOAD_FAST                'newclass'
               38  CALL_FUNCTION_1       1  '1 positional argument'
               40  STORE_FAST               'newslots'

 L. 535        42  LOAD_FAST                'oldslots'
               44  LOAD_CONST               None
               46  COMPARE_OP               is-not
               48  POP_JUMP_IF_FALSE    76  'to 76'

 L. 538        50  LOAD_CLOSURE             'oldclass'
               52  BUILD_TUPLE_1         1 
               54  LOAD_SETCOMP             '<code_object <setcomp>>'
               56  LOAD_STR                 '_update_class.<locals>.<setcomp>'
               58  MAKE_FUNCTION_8          'closure'
               60  LOAD_FAST                'oldslots'
               62  GET_ITER         
               64  CALL_FUNCTION_1       1  '1 positional argument'
               66  STORE_FAST               'slots'

 L. 539        68  LOAD_FAST                'immutables'
               70  LOAD_FAST                'slots'
               72  INPLACE_OR       
               74  STORE_FAST               'immutables'
             76_0  COME_FROM            48  '48'

 L. 541        76  LOAD_GLOBAL              set
               78  LOAD_FAST                'olddict'
               80  CALL_FUNCTION_1       1  '1 positional argument'
               82  LOAD_FAST                'immutables'
               84  BINARY_SUBTRACT  
               86  STORE_FAST               'oldnames'

 L. 542        88  LOAD_GLOBAL              set
               90  LOAD_FAST                'newdict'
               92  CALL_FUNCTION_1       1  '1 positional argument'
               94  LOAD_FAST                'immutables'
               96  BINARY_SUBTRACT  
               98  STORE_FAST               'newnames'

 L. 543       100  SETUP_LOOP          134  'to 134'
              102  LOAD_FAST                'newnames'
              104  LOAD_FAST                'oldnames'
              106  BINARY_SUBTRACT  
              108  GET_ITER         
              110  FOR_ITER            132  'to 132'
              112  STORE_FAST               'name'

 L. 544       114  LOAD_GLOBAL              setattr
              116  LOAD_DEREF               'oldclass'
              118  LOAD_FAST                'name'
              120  LOAD_FAST                'newdict'
              122  LOAD_FAST                'name'
              124  BINARY_SUBSCR    
              126  CALL_FUNCTION_3       3  '3 positional arguments'
              128  POP_TOP          
              130  JUMP_BACK           110  'to 110'
              132  POP_BLOCK        
            134_0  COME_FROM_LOOP      100  '100'

 L. 545       134  SETUP_LOOP          162  'to 162'
              136  LOAD_FAST                'oldnames'
              138  LOAD_FAST                'newnames'
              140  BINARY_SUBTRACT  
              142  GET_ITER         
              144  FOR_ITER            160  'to 160'
              146  STORE_FAST               'name'

 L. 546       148  LOAD_GLOBAL              delattr
              150  LOAD_DEREF               'oldclass'
              152  LOAD_FAST                'name'
              154  CALL_FUNCTION_2       2  '2 positional arguments'
              156  POP_TOP          
              158  JUMP_BACK           144  'to 144'
              160  POP_BLOCK        
            162_0  COME_FROM_LOOP      134  '134'

 L. 547       162  SETUP_LOOP          206  'to 206'
              164  LOAD_FAST                'oldnames'
              166  LOAD_FAST                'newnames'
              168  BINARY_AND       
              170  GET_ITER         
              172  FOR_ITER            204  'to 204'
              174  STORE_FAST               'name'

 L. 548       176  LOAD_GLOBAL              setattr
              178  LOAD_DEREF               'oldclass'
              180  LOAD_FAST                'name'
              182  LOAD_GLOBAL              _update
              184  LOAD_FAST                'olddict'
              186  LOAD_FAST                'name'
              188  BINARY_SUBSCR    
              190  LOAD_FAST                'newdict'
              192  LOAD_FAST                'name'
              194  BINARY_SUBSCR    
              196  CALL_FUNCTION_2       2  '2 positional arguments'
              198  CALL_FUNCTION_3       3  '3 positional arguments'
              200  POP_TOP          
              202  JUMP_BACK           172  'to 172'
              204  POP_BLOCK        
            206_0  COME_FROM_LOOP      162  '162'

 L. 549       206  LOAD_DEREF               'oldclass'
              208  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_SETCOMP' instruction at offset 54


def _update_classmethod(oldcm, newcm):
    _updateoldcm.__get__(0)newcm.__get__(0)
    return oldcm


def _update_staticmethod(oldsm, newsm):
    _updateoldsm.__get__(0)newsm.__get__(0)
    return oldsm


def _update_flexmethod(oldfm, newfm):
    oldfm.__wrapped_method__ = _updateoldfm.__wrapped_method__newfm.__wrapped_method__
    return oldfm