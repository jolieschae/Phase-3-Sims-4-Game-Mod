# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\proxy.py
# Compiled at: 2018-03-08 18:47:47
# Size of source mod 2**32: 8735 bytes
import _weakrefutils
from sims4.repr_utils import standard_repr
import sims4.log, weakref
logger = sims4.log.Logger('Proxy')

class ProxyObject:
    _unproxied_attributes = {
     '__dict__', '__weakref__', '__module__', '_proxied_obj'}

    def __new__(cls, proxied_obj, *args, **kwargs):
        try:
            cache = cls._class_proxy_cache
        except AttributeError:
            cache = cls._class_proxy_cache = {}

        proxied_type = type(proxied_obj)
        if proxied_type in cache:
            return object.__new__(cache[proxied_type])
        class_dict = {'__doc__': 'This is a class for proxying instances of {}.'.format(proxied_type) + ('\n\n' + cls.__doc__ if cls.__doc__ else '')}
        proxy_type = type('{}({})'.format(cls.__qualname__, proxied_type.__qualname__), (
         cls, proxied_type), class_dict)
        cache[proxied_type] = proxy_type
        for attr, value in proxy_type.__dict__.items():
            if isinstance(value, property):
                proxy_type._unproxied_attributes.add(attr)

        return object.__new__(proxy_type)

    def __init__(self, proxied_obj):
        self._proxied_obj = proxied_obj

    def on_proxied_object_removed(self):
        _weakrefutils.clear_weak_refs(self)
        self._proxied_obj = None

    def __getattr__(self, name):
        if name in self._unproxied_attributes:
            raise AttributeError('unproxied attribute not initialized: ' + name)
        if self._proxied_obj is None:
            return
        return getattr(self._proxied_obj, name)

    def __delattr__(self, name):
        if name in self._unproxied_attributes:
            return object.__delattr__(self, name)
        return delattr(self._proxied_obj, name)

    def __setattr__(self, name, value):
        if name in self._unproxied_attributes:
            return object.__setattr__(self, name, value)
        return setattr(self._proxied_obj, name, value)

    def __repr__(self):
        return standard_repr(self, self._proxied_obj)

    def ref(self, callback=None):
        return _ProxyWeakRef(self, callback)

    @property
    def client_objects_gen(self):
        if self._proxied_obj is not None:
            yield self._proxied_obj

    @property
    def proxied_obj(self):
        return self._proxied_obj


class _ProxyWeakRef(weakref.ref):
    __slots__ = ('_proxy', '_proxy_callback')

    def __new__(cls, proxy, callback=None):
        return super().__new__(cls, proxy._proxied_obj, _ProxyWeakRef._wrapped_callback)

    def __init__(self, proxy, callback=None):
        super().__init__(proxy._proxied_obj, _ProxyWeakRef._wrapped_callback)
        self._proxy = proxy
        self._proxy_callback = callback

    @staticmethod
    def _wrapped_callback(proxy_weakref):
        if proxy_weakref._proxy_callback is not None:
            proxy_weakref._proxy_callback(proxy_weakref)
            proxy_weakref._proxy_callback = None
        proxy_weakref._proxy = None

    def __call__(self):
        return self._proxy

    def __hash__(self):
        return hash((self.__class__, self._proxy))

    def __eq__(self, other):
        return other.__class__ == self.__class__ and self._proxy is other._proxy