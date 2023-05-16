# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_threading_local.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 7456 bytes
from weakref import ref
from contextlib import contextmanager
__all__ = [
 'local']

class _localimpl:
    __slots__ = ('key', 'dicts', 'localargs', 'locallock', '__weakref__')

    def __init__(self):
        self.key = '_threading_local._localimpl.' + str(id(self))
        self.dicts = {}

    def get_dict(self):
        thread = current_thread()
        return self.dicts[id(thread)][1]

    def create_dict(self):
        localdict = {}
        key = self.key
        thread = current_thread()
        idt = id(thread)

        def local_deleted(_, key=key):
            thread = wrthread()
            if thread is not None:
                del thread.__dict__[key]

        def thread_deleted(_, idt=idt):
            local = wrlocal()
            if local is not None:
                dct = local.dicts.pop(idt)

        wrlocal = ref(self, local_deleted)
        wrthread = ref(thread, thread_deleted)
        thread.__dict__[key] = wrlocal
        self.dicts[idt] = (wrthread, localdict)
        return localdict


@contextmanager
def _patch(self):
    impl = object.__getattribute__(self, '_local__impl')
    try:
        dct = impl.get_dict()
    except KeyError:
        dct = impl.create_dict()
        args, kw = impl.localargs
        (self.__init__)(*args, **kw)

    with impl.locallock:
        object.__setattr__(self, '__dict__', dct)
        yield


class local:
    __slots__ = ('_local__impl', '__dict__')

    def __new__(cls, *args, **kw):
        if args or kw:
            if cls.__init__ is object.__init__:
                raise TypeError('Initialization arguments are not supported')
        self = object.__new__(cls)
        impl = _localimpl()
        impl.localargs = (args, kw)
        impl.locallock = RLock()
        object.__setattr__(self, '_local__impl', impl)
        impl.create_dict()
        return self

    def __getattribute__(self, name):
        with _patch(self):
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name == '__dict__':
            raise AttributeError("%r object attribute '__dict__' is read-only" % self.__class__.__name__)
        with _patch(self):
            return object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name == '__dict__':
            raise AttributeError("%r object attribute '__dict__' is read-only" % self.__class__.__name__)
        with _patch(self):
            return object.__delattr__(self, name)


from threading import current_thread, RLock