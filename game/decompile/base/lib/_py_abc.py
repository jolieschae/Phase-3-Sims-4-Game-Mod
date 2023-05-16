# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_py_abc.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 6333 bytes
from _weakrefset import WeakSet

def get_cache_token():
    return ABCMeta._abc_invalidation_counter


class ABCMeta(type):
    _abc_invalidation_counter = 0

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = (super().__new__)(mcls, name, bases, namespace, **kwargs)
        abstracts = {name for name, value in namespace.items() if getattr(value, '__isabstractmethod__', False)}
        for base in bases:
            for name in getattr(base, '__abstractmethods__', set()):
                value = getattr(cls, name, None)
                if getattr(value, '__isabstractmethod__', False):
                    abstracts.add(name)

        cls.__abstractmethods__ = frozenset(abstracts)
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        return cls

    def register(cls, subclass):
        if not isinstance(subclass, type):
            raise TypeError('Can only register classes')
        if issubclass(subclass, cls):
            return subclass
        if issubclass(cls, subclass):
            raise RuntimeError('Refusing to create an inheritance cycle')
        cls._abc_registry.add(subclass)
        ABCMeta._abc_invalidation_counter += 1
        return subclass

    def _dump_registry(cls, file=None):
        print(f"Class: {cls.__module__}.{cls.__qualname__}", file=file)
        print(f"Inv. counter: {get_cache_token()}", file=file)
        for name in cls.__dict__:
            if name.startswith('_abc_'):
                value = getattr(cls, name)
                if isinstance(value, WeakSet):
                    value = set(value)
                print(f"{name}: {value!r}", file=file)

    def _abc_registry_clear(cls):
        cls._abc_registry.clear()

    def _abc_caches_clear(cls):
        cls._abc_cache.clear()
        cls._abc_negative_cache.clear()

    def __instancecheck__(cls, instance):
        subclass = instance.__class__
        if subclass in cls._abc_cache:
            return True
        subtype = type(instance)
        if subtype is subclass:
            if cls._abc_negative_cache_version == ABCMeta._abc_invalidation_counter:
                if subclass in cls._abc_negative_cache:
                    return False
            return cls.__subclasscheck__(subclass)
        return any((cls.__subclasscheck__(c) for c in (subclass, subtype)))

    def __subclasscheck__(cls, subclass):
        if not isinstance(subclass, type):
            raise TypeError('issubclass() arg 1 must be a class')
        else:
            if subclass in cls._abc_cache:
                return True
                if cls._abc_negative_cache_version < ABCMeta._abc_invalidation_counter:
                    cls._abc_negative_cache = WeakSet()
                    cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
                else:
                    if subclass in cls._abc_negative_cache:
                        return False
                ok = cls.__subclasshook__(subclass)
                if ok is not NotImplemented:
                    if ok:
                        cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        if cls in getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            return True
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True

        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True

        cls._abc_negative_cache.add(subclass)
        return False