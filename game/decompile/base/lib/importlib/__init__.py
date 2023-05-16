# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\importlib\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 6213 bytes
__all__ = ['__import__', 'import_module', 'invalidate_caches', 'reload']
import _imp, sys
try:
    import _frozen_importlib as _bootstrap
except ImportError:
    from . import _bootstrap
    _bootstrap._setup(sys, _imp)
else:
    _bootstrap.__name__ = 'importlib._bootstrap'
    _bootstrap.__package__ = 'importlib'
    try:
        _bootstrap.__file__ = __file__.replace('__init__.py', '_bootstrap.py')
    except NameError:
        pass

    sys.modules['importlib._bootstrap'] = _bootstrap
try:
    import _frozen_importlib_external as _bootstrap_external
except ImportError:
    from . import _bootstrap_external
    _bootstrap_external._setup(_bootstrap)
    _bootstrap._bootstrap_external = _bootstrap_external
else:
    _bootstrap_external.__name__ = 'importlib._bootstrap_external'
    _bootstrap_external.__package__ = 'importlib'
    try:
        _bootstrap_external.__file__ = __file__.replace('__init__.py', '_bootstrap_external.py')
    except NameError:
        pass

    sys.modules['importlib._bootstrap_external'] = _bootstrap_external
_w_long = _bootstrap_external._w_long
_r_long = _bootstrap_external._r_long
import types, warnings
from ._bootstrap import __import__

def invalidate_caches():
    for finder in sys.meta_path:
        if hasattr(finder, 'invalidate_caches'):
            finder.invalidate_caches()


def find_loader(name, path=None):
    warnings.warn('Deprecated since Python 3.4. Use importlib.util.find_spec() instead.', DeprecationWarning,
      stacklevel=2)
    try:
        loader = sys.modules[name].__loader__
        if loader is None:
            raise ValueError('{}.__loader__ is None'.format(name))
        else:
            return loader
    except KeyError:
        pass
    except AttributeError:
        raise ValueError('{}.__loader__ is not set'.format(name)) from None

    spec = _bootstrap._find_spec(name, path)
    if spec is None:
        return
    if spec.loader is None:
        if spec.submodule_search_locations is None:
            raise ImportError(('spec for {} missing loader'.format(name)), name=name)
        raise ImportError('namespace packages do not have loaders', name=name)
    return spec.loader


def import_module(name, package=None):
    level = 0
    if name.startswith('.'):
        if not package:
            msg = "the 'package' argument is required to perform a relative import for {!r}"
            raise TypeError(msg.format(name))
        for character in name:
            if character != '.':
                break
            level += 1

    return _bootstrap._gcd_import(name[level:], package, level)


_RELOADING = {}

def reload(module):
    if not (module and isinstance(module, types.ModuleType)):
        raise TypeError('reload() argument must be a module')
    try:
        name = module.__spec__.name
    except AttributeError:
        name = module.__name__

    if sys.modules.get(name) is not module:
        msg = 'module {} not in sys.modules'
        raise ImportError((msg.format(name)), name=name)
    if name in _RELOADING:
        return _RELOADING[name]
    _RELOADING[name] = module
    try:
        parent_name = name.rpartition('.')[0]
        if parent_name:
            try:
                parent = sys.modules[parent_name]
            except KeyError:
                msg = 'parent {!r} not in sys.modules'
                raise ImportError((msg.format(parent_name)), name=parent_name) from None
            else:
                pkgpath = parent.__path__
        else:
            pkgpath = None
        target = module
        spec = module.__spec__ = _bootstrap._find_spec(name, pkgpath, target)
        if spec is None:
            raise ModuleNotFoundError(f"spec not found for the module {name!r}", name=name)
        _bootstrap._exec(spec, module)
        return sys.modules[name]
    finally:
        try:
            del _RELOADING[name]
        except KeyError:
            pass