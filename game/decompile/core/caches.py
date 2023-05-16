# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\caches.py
# Compiled at: 2020-11-20 14:21:35
# Size of source mod 2**32: 13844 bytes
from itertools import count
import collections, functools, weakref
from sims4.callback_utils import add_callbacks, CallbackEvent
from sims4.utils import decorator
import enum, sims4.log, sims4.reload
logger = sims4.log.Logger('Caches', default_owner='bhill')
MAX_CACHE_SIZE = 18446744073709551616

class AccBccUsage(enum.IntFlags, export=False):
    NONE = 0
    ACC = 1
    BCC = 2


with sims4.reload.protected(globals()):
    _KEYWORD_MARKER = object()
    USE_ACC_AND_BCC = AccBccUsage.ACC | AccBccUsage.BCC
    use_asm_cache = True
    use_constraints_cache = True
    skip_cache = False
    skip_cache_once = False
    all_cached_functions = weakref.WeakSet()
    clearable_barebone_caches = weakref.WeakSet()
    global_cache_version = 0
    cache_clear_misses = None
CacheInfo = collections.namedtuple('CacheInfo', ('hits', 'misses', 'maxsize', 'currsize'))

def clear_all_caches(force=False):
    global global_cache_version
    global_cache_version += 1
    if force or global_cache_version % 1000 == 0:
        for fn in all_cached_functions:
            fn.cache.clear()

    for c in clearable_barebone_caches:
        c.clear()


if not sims4.reload.currently_reloading:
    add_callbacks(CallbackEvent.TUNING_CODE_RELOAD, (lambda: clear_all_caches(force=True)))

@decorator
def cached(fn, maxsize=100, key=None, debug_cache=False):
    key_fn = key
    del key

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if skip_cache:
            return fn(*args, **kwargs)
            cache = wrapper.cache
            if global_cache_version != wrapper.cache_version:
                cache.clear()
                wrapper.cache_version = global_cache_version
        else:
            try:
                if key_fn is None:
                    key = (args, _KEYWORD_MARKER, frozenset(kwargs.items())) if kwargs else args
                else:
                    key = key_fn(*args, **kwargs)
                result = cache[key]
            except TypeError as exc:
                try:
                    if len(exc.args) == 1:
                        if exc.args[0].startswith('unhashable type'):
                            logger.callstack('Cache failed on {} in function argument(s):\nargs={} kwargs={}\nTry one of the following: use hashable types as arguments to the function (e.g. tuple instead of list) or implement __hash__() on the unhashable object.', (exc.args[0]),
                              args, kwargs, level=(sims4.log.LEVEL_ERROR), owner='bhill')
                    raise exc
                finally:
                    exc = None
                    del exc

            except KeyError:
                cache[key] = result = fn(*args, **kwargs)

        if maxsize is not None:
            if len(cache) > maxsize:
                cache.popitem(last=False)
        return result

    def cache_info():
        raise AttributeError('Cache statistics not tracked in optimized Python.')

    wrapper.cache = {} if maxsize is None else collections.OrderedDict()
    wrapper.cache_version = global_cache_version
    wrapper.uncached_function = fn
    wrapper.cache_info = cache_info
    all_cached_functions.add(wrapper)
    return wrapper


@decorator
def cached_generator(fn, cache_decorator=cached, **cache_kwargs):

    @cache_decorator(**cache_kwargs)
    @functools.wraps(fn)
    def _wrapper(*args, **kwargs):
        return ([], fn(*args, **kwargs))

    @functools.wraps(_wrapper)
    def yielder(*args, **kwargs):
        computed_values, gen = _wrapper(*args, **kwargs)
        try:
            for i in count():
                if i >= len(computed_values):
                    computed_values.append(next(gen))
                yield computed_values[i]

        except StopIteration:
            pass

    return yielder


@decorator
def cached_test(fn):

    @functools.wraps(fn)
    def wrapper(test, **kwargs):
        global skip_cache_once
        if skip_cache:
            return fn(test, **kwargs)
            cache = wrapper.cache
            if not skip_cache_once:
                if global_cache_version != wrapper.cache_version:
                    if test.qualifies_for_cache_clear():
                        skip_cache_once = False
                        cache.clear()
                        wrapper.cache_version = global_cache_version
        else:
            key = (
             test, frozenset(kwargs.items()))
            try:
                result = cache[key]
            except KeyError:
                cache[key] = result = fn(test, **kwargs)

        return result

    wrapper.cache = {}
    wrapper.cache_version = global_cache_version
    all_cached_functions.add(wrapper)
    return wrapper


def uncached(wrapper):
    return wrapper.uncached_function


class BarebonesCache(dict):
    __slots__ = ('uncached_function', '__weakref__')

    def __init__(self, uncached_function, clear=False):
        self.uncached_function = uncached_function

    def __repr__(self):
        return '{}({})'.format(type(self).__qualname__, self.uncached_function)

    __call__ = dict.__getitem__

    def __missing__(self, key):
        self[key] = ret = self.uncached_function(key)
        return ret

    def __hash__(self):
        return id(self.uncached_function)


@decorator
def clearable_barebones_cache(fn):
    wrapper = BarebonesCache(fn)
    clearable_barebone_caches.add(wrapper)
    return wrapper