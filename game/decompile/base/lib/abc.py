# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\abc.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5750 bytes


def abstractmethod(funcobj):
    funcobj.__isabstractmethod__ = True
    return funcobj


class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super().__init__(callable)


class abstractstaticmethod(staticmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super().__init__(callable)


class abstractproperty(property):
    __isabstractmethod__ = True


try:
    from _abc import get_cache_token, _abc_init, _abc_register, _abc_instancecheck, _abc_subclasscheck, _get_dump, _reset_registry, _reset_caches
except ImportError:
    from _py_abc import ABCMeta, get_cache_token
    ABCMeta.__module__ = 'abc'
else:

    class ABCMeta(type):

        def __new__(mcls, name, bases, namespace, **kwargs):
            cls = (super().__new__)(mcls, name, bases, namespace, **kwargs)
            _abc_init(cls)
            return cls

        def register(cls, subclass):
            return _abc_register(cls, subclass)

        def __instancecheck__(cls, instance):
            return _abc_instancecheck(cls, instance)

        def __subclasscheck__(cls, subclass):
            return _abc_subclasscheck(cls, subclass)

        def _dump_registry(cls, file=None):
            print(f"Class: {cls.__module__}.{cls.__qualname__}", file=file)
            print(f"Inv. counter: {get_cache_token()}", file=file)
            _abc_registry, _abc_cache, _abc_negative_cache, _abc_negative_cache_version = _get_dump(cls)
            print(f"_abc_registry: {_abc_registry!r}", file=file)
            print(f"_abc_cache: {_abc_cache!r}", file=file)
            print(f"_abc_negative_cache: {_abc_negative_cache!r}", file=file)
            print(f"_abc_negative_cache_version: {_abc_negative_cache_version!r}", file=file)

        def _abc_registry_clear(cls):
            _reset_registry(cls)

        def _abc_caches_clear(cls):
            _reset_caches(cls)


class ABC(metaclass=ABCMeta):
    __slots__ = ()