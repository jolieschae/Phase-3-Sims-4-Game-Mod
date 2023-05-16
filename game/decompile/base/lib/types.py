# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\types.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 10213 bytes
import sys

def _f():
    pass


FunctionType = type(_f)
LambdaType = type((lambda: None))
CodeType = type(_f.__code__)
MappingProxyType = type(type.__dict__)
SimpleNamespace = type(sys.implementation)

def _g():
    yield 1


GeneratorType = type(_g())

async def _c():
    pass


_c = _c()
CoroutineType = type(_c)
_c.close()

async def _ag():
    yield


_ag = _ag()
AsyncGeneratorType = type(_ag)

class _C:

    def _m(self):
        pass


MethodType = type(_C()._m)
BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)
WrapperDescriptorType = type(object.__init__)
MethodWrapperType = type(object().__str__)
MethodDescriptorType = type(str.join)
ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])
ModuleType = type(sys)
try:
    raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    tb = None
    del tb

GetSetDescriptorType = type(FunctionType.__code__)
MemberDescriptorType = type(FunctionType.__globals__)
del sys
del _f
del _g
del _C
del _c

def new_class(name, bases=(), kwds=None, exec_body=None):
    resolved_bases = resolve_bases(bases)
    meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
    if exec_body is not None:
        exec_body(ns)
    if resolved_bases is not bases:
        ns['__orig_bases__'] = bases
    return meta(name, resolved_bases, ns, **kwds)


def resolve_bases(bases):
    new_bases = list(bases)
    updated = False
    shift = 0
    for i, base in enumerate(bases):
        if isinstance(base, type):
            continue
        if not hasattr(base, '__mro_entries__'):
            continue
        new_base = base.__mro_entries__(bases)
        updated = True
        if not isinstance(new_base, tuple):
            raise TypeError('__mro_entries__ must return a tuple')
        else:
            new_bases[i + shift:i + shift + 1] = new_base
            shift += len(new_base) - 1

    if not updated:
        return bases
    return tuple(new_bases)


def prepare_class(name, bases=(), kwds=None):
    if kwds is None:
        kwds = {}
    else:
        kwds = dict(kwds)
    if 'metaclass' in kwds:
        meta = kwds.pop('metaclass')
    else:
        if bases:
            meta = type(bases[0])
        else:
            meta = type
    if isinstance(meta, type):
        meta = _calculate_meta(meta, bases)
    elif hasattr(meta, '__prepare__'):
        ns = (meta.__prepare__)(name, bases, **kwds)
    else:
        ns = {}
    return (
     meta, ns, kwds)


def _calculate_meta(meta, bases):
    winner = meta
    for base in bases:
        base_meta = type(base)
        if issubclass(winner, base_meta):
            continue
        if issubclass(base_meta, winner):
            winner = base_meta
            continue
        raise TypeError('metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases')

    return winner


class DynamicClassAttribute:

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or fget.__doc__
        self.overwrite_doc = doc is None
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', False))

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            if self.__isabstractmethod__:
                return self
            raise AttributeError()
        else:
            if self.fget is None:
                raise AttributeError('unreadable attribute')
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        fdoc = fget.__doc__ if self.overwrite_doc else None
        result = type(self)(fget, self.fset, self.fdel, fdoc or self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def setter(self, fset):
        result = type(self)(self.fget, fset, self.fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def deleter(self, fdel):
        result = type(self)(self.fget, self.fset, fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result


class _GeneratorWrapper:

    def __init__(self, gen):
        self._GeneratorWrapper__wrapped = gen
        self._GeneratorWrapper__isgen = gen.__class__ is GeneratorType
        self.__name__ = getattr(gen, '__name__', None)
        self.__qualname__ = getattr(gen, '__qualname__', None)

    def send(self, val):
        return self._GeneratorWrapper__wrapped.send(val)

    def throw(self, tp, *rest):
        return (self._GeneratorWrapper__wrapped.throw)(tp, *rest)

    def close(self):
        return self._GeneratorWrapper__wrapped.close()

    @property
    def gi_code(self):
        return self._GeneratorWrapper__wrapped.gi_code

    @property
    def gi_frame(self):
        return self._GeneratorWrapper__wrapped.gi_frame

    @property
    def gi_running(self):
        return self._GeneratorWrapper__wrapped.gi_running

    @property
    def gi_yieldfrom(self):
        return self._GeneratorWrapper__wrapped.gi_yieldfrom

    cr_code = gi_code
    cr_frame = gi_frame
    cr_running = gi_running
    cr_await = gi_yieldfrom

    def __next__(self):
        return next(self._GeneratorWrapper__wrapped)

    def __iter__(self):
        if self._GeneratorWrapper__isgen:
            return self._GeneratorWrapper__wrapped
        return self

    __await__ = __iter__


def coroutine(func):
    if not callable(func):
        raise TypeError('types.coroutine() expects a callable')
    elif func.__class__ is FunctionType:
        if getattr(func, '__code__', None).__class__ is CodeType:
            co_flags = func.__code__.co_flags
            if co_flags & 384:
                return func
            if co_flags & 32:
                co = func.__code__
                func.__code__ = CodeType(co.co_argcount, co.co_kwonlyargcount, co.co_nlocals, co.co_stacksize, co.co_flags | 256, co.co_code, co.co_consts, co.co_names, co.co_varnames, co.co_filename, co.co_name, co.co_firstlineno, co.co_lnotab, co.co_freevars, co.co_cellvars)
                return func
    import functools, _collections_abc

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        if (coro.__class__ is CoroutineType or coro.__class__) is GeneratorType:
            if coro.gi_code.co_flags & 256:
                return coro
        if isinstance(coro, _collections_abc.Generator):
            if not isinstance(coro, _collections_abc.Coroutine):
                return _GeneratorWrapper(coro)
        return coro

    return wrapped


__all__ = [n for n in globals() if n[:1] != '_']