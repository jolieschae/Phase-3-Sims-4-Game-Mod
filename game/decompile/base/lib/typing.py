# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\typing.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 56148 bytes
import abc
from abc import abstractmethod, abstractproperty
import collections, collections.abc, contextlib, functools, operator, re as stdlib_re, sys, types
from types import WrapperDescriptorType, MethodWrapperType, MethodDescriptorType
__all__ = [
 "'Any'", 
 "'Callable'", 
 "'ClassVar'", 
 "'Generic'", 
 "'Optional'", 
 "'Tuple'", 
 "'Type'", 
 "'TypeVar'", 
 "'Union'", 
 "'AbstractSet'", 
 "'ByteString'", 
 "'Container'", 
 "'ContextManager'", 
 "'Hashable'", 
 "'ItemsView'", 
 "'Iterable'", 
 "'Iterator'", 
 "'KeysView'", 
 "'Mapping'", 
 "'MappingView'", 
 "'MutableMapping'", 
 "'MutableSequence'", 
 "'MutableSet'", 
 "'Sequence'", 
 "'Sized'", 
 "'ValuesView'", 
 "'Awaitable'", 
 "'AsyncIterator'", 
 "'AsyncIterable'", 
 "'Coroutine'", 
 "'Collection'", 
 "'AsyncGenerator'", 
 "'AsyncContextManager'", 
 "'Reversible'", 
 "'SupportsAbs'", 
 "'SupportsBytes'", 
 "'SupportsComplex'", 
 "'SupportsFloat'", 
 "'SupportsInt'", 
 "'SupportsRound'", 
 "'Counter'", 
 "'Deque'", 
 "'Dict'", 
 "'DefaultDict'", 
 "'List'", 
 "'Set'", 
 "'FrozenSet'", 
 "'NamedTuple'", 
 "'Generator'", 
 "'AnyStr'", 
 "'cast'", 
 "'get_type_hints'", 
 "'NewType'", 
 "'no_type_check'", 
 "'no_type_check_decorator'", 
 "'NoReturn'", 
 "'overload'", 
 "'Text'", 
 "'TYPE_CHECKING'"]

def _type_check(arg, msg, is_argument=True):
    invalid_generic_forms = (
     Generic, _Protocol)
    if is_argument:
        invalid_generic_forms = invalid_generic_forms + (ClassVar,)
    if arg is None:
        return type(None)
    if isinstance(arg, str):
        return ForwardRef(arg)
    if isinstance(arg, _GenericAlias):
        if arg.__origin__ in invalid_generic_forms:
            raise TypeError(f"{arg} is not valid as type argument")
    if not (isinstance(arg, _SpecialForm) and arg is not Any):
        if arg in (Generic, _Protocol):
            raise TypeError(f"Plain {arg} is not valid as type argument")
        if isinstance(arg, (type, TypeVar, ForwardRef)):
            return arg
    if not callable(arg):
        raise TypeError(f"{msg} Got {arg!r:.100}.")
    return arg


def _type_repr(obj):
    if isinstance(obj, type):
        if obj.__module__ == 'builtins':
            return obj.__qualname__
        return f"{obj.__module__}.{obj.__qualname__}"
    if obj is ...:
        return '...'
    if isinstance(obj, types.FunctionType):
        return obj.__name__
    return repr(obj)


def _collect_type_vars(types):
    tvars = []
    for t in types:
        if isinstance(t, TypeVar):
            if t not in tvars:
                tvars.append(t)
        if isinstance(t, _GenericAlias):
            t._special or tvars.extend([t for t in t.__parameters__ if t not in tvars])

    return tuple(tvars)


def _subs_tvars(tp, tvars, subs):
    if not isinstance(tp, _GenericAlias):
        return tp
    new_args = list(tp.__args__)
    for a, arg in enumerate(tp.__args__):
        if isinstance(arg, TypeVar):
            for i, tvar in enumerate(tvars):
                if arg == tvar:
                    new_args[a] = subs[i]

        else:
            new_args[a] = _subs_tvars(arg, tvars, subs)

    if tp.__origin__ is Union:
        return Union[tuple(new_args)]
    return tp.copy_with(tuple(new_args))


def _check_generic(cls, parameters):
    if not cls.__parameters__:
        raise TypeError(f"{cls} is not a generic class")
    alen = len(parameters)
    elen = len(cls.__parameters__)
    if alen != elen:
        raise TypeError(f"Too {'many' if alen > elen else 'few'} parameters for {cls}; actual {alen}, expected {elen}")


def _remove_dups_flatten(parameters):
    params = []
    for p in parameters:
        if isinstance(p, _GenericAlias) and p.__origin__ is Union:
            params.extend(p.__args__)
        elif isinstance(p, tuple) and len(p) > 0 and p[0] is Union:
            params.extend(p[1:])
        else:
            params.append(p)

    all_params = set(params)
    if len(all_params) < len(params):
        new_params = []
        for t in params:
            if t in all_params:
                new_params.append(t)
                all_params.remove(t)

        params = new_params
    return tuple(params)


_cleanups = []

def _tp_cache(func):
    cached = functools.lru_cache()(func)
    _cleanups.append(cached.cache_clear)

    @functools.wraps(func)
    def inner(*args, **kwds):
        try:
            return cached(*args, **kwds)
        except TypeError:
            pass

        return func(*args, **kwds)

    return inner


def _eval_type(t, globalns, localns):
    if isinstance(t, ForwardRef):
        return t._evaluate(globalns, localns)
    if isinstance(t, _GenericAlias):
        ev_args = tuple((_eval_type(a, globalns, localns) for a in t.__args__))
        if ev_args == t.__args__:
            return t
        res = t.copy_with(ev_args)
        res._special = t._special
        return res
    return t


class _Final:
    __slots__ = ('__weakref__', )

    def __init_subclass__(self, *args, **kwds):
        if '_root' not in kwds:
            raise TypeError('Cannot subclass special typing classes')


class _Immutable:

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


class _SpecialForm(_Final, _Immutable, _root=True):
    __slots__ = ('_name', '_doc')

    def __new__(cls, *args, **kwds):
        if len(args) == 3:
            if isinstance(args[0], str):
                if isinstance(args[1], tuple):
                    raise TypeError(f"Cannot subclass {cls!r}")
        return super().__new__(cls)

    def __init__(self, name, doc):
        self._name = name
        self._doc = doc

    def __eq__(self, other):
        if not isinstance(other, _SpecialForm):
            return NotImplemented
        return self._name == other._name

    def __hash__(self):
        return hash((self._name,))

    def __repr__(self):
        return 'typing.' + self._name

    def __reduce__(self):
        return self._name

    def __call__(self, *args, **kwds):
        raise TypeError(f"Cannot instantiate {self!r}")

    def __instancecheck__(self, obj):
        raise TypeError(f"{self} cannot be used with isinstance()")

    def __subclasscheck__(self, cls):
        raise TypeError(f"{self} cannot be used with issubclass()")

    @_tp_cache
    def __getitem__(self, parameters):
        if self._name == 'ClassVar':
            item = _type_check(parameters, 'ClassVar accepts only single type.')
            return _GenericAlias(self, (item,))
        if self._name == 'Union':
            if parameters == ():
                raise TypeError('Cannot take a Union of no types.')
            if not isinstance(parameters, tuple):
                parameters = (
                 parameters,)
            msg = 'Union[arg, ...]: each arg must be a type.'
            parameters = tuple((_type_check(p, msg) for p in parameters))
            parameters = _remove_dups_flatten(parameters)
            if len(parameters) == 1:
                return parameters[0]
            return _GenericAlias(self, parameters)
        if self._name == 'Optional':
            arg = _type_check(parameters, 'Optional[t] requires a single type.')
            return Union[(arg, type(None))]
        raise TypeError(f"{self} is not subscriptable")


Any = _SpecialForm('Any', doc='Special type indicating an unconstrained type.\n\n    - Any is compatible with every type.\n    - Any assumed to have all methods.\n    - All values assumed to be instances of Any.\n\n    Note that all the above statements are true from the point of view of\n    static type checkers. At runtime, Any should not be used with instance\n    or class checks.\n    ')
NoReturn = _SpecialForm('NoReturn', doc="Special type indicating functions that never return.\n    Example::\n\n      from typing import NoReturn\n\n      def stop() -> NoReturn:\n          raise Exception('no way')\n\n    This type is invalid in other positions, e.g., ``List[NoReturn]``\n    will fail in static type checkers.\n    ")
ClassVar = _SpecialForm('ClassVar', doc='Special type construct to mark class variables.\n\n    An annotation wrapped in ClassVar indicates that a given\n    attribute is intended to be used as a class variable and\n    should not be set on instances of that class. Usage::\n\n      class Starship:\n          stats: ClassVar[Dict[str, int]] = {} # class variable\n          damage: int = 10                     # instance variable\n\n    ClassVar accepts only types and cannot be further subscribed.\n\n    Note that ClassVar is not a class itself, and should not\n    be used with isinstance() or issubclass().\n    ')
Union = _SpecialForm('Union', doc='Union type; Union[X, Y] means either X or Y.\n\n    To define a union, use e.g. Union[int, str].  Details:\n    - The arguments must be types and there must be at least one.\n    - None as an argument is a special case and is replaced by\n      type(None).\n    - Unions of unions are flattened, e.g.::\n\n        Union[Union[int, str], float] == Union[int, str, float]\n\n    - Unions of a single argument vanish, e.g.::\n\n        Union[int] == int  # The constructor actually returns int\n\n    - Redundant arguments are skipped, e.g.::\n\n        Union[int, str, int] == Union[int, str]\n\n    - When comparing unions, the argument order is ignored, e.g.::\n\n        Union[int, str] == Union[str, int]\n\n    - You cannot subclass or instantiate a union.\n    - You can use Optional[X] as a shorthand for Union[X, None].\n    ')
Optional = _SpecialForm('Optional', doc='Optional type.\n\n    Optional[X] is equivalent to Union[X, None].\n    ')

class ForwardRef(_Final, _root=True):
    __slots__ = ('__forward_arg__', '__forward_code__', '__forward_evaluated__', '__forward_value__',
                 '__forward_is_argument__')

    def __init__(self, arg, is_argument=True):
        if not isinstance(arg, str):
            raise TypeError(f"Forward reference must be a string -- got {arg!r}")
        try:
            code = compile(arg, '<string>', 'eval')
        except SyntaxError:
            raise SyntaxError(f"Forward reference must be an expression -- got {arg!r}")

        self.__forward_arg__ = arg
        self.__forward_code__ = code
        self.__forward_evaluated__ = False
        self.__forward_value__ = None
        self.__forward_is_argument__ = is_argument

    def _evaluate(self, globalns, localns):
        if not self.__forward_evaluated__ or localns is not globalns:
            if globalns is None and localns is None:
                globalns = localns = {}
            else:
                if globalns is None:
                    globalns = localns
                else:
                    if localns is None:
                        localns = globalns
            self.__forward_value__ = _type_check((eval(self.__forward_code__, globalns, localns)),
              'Forward references must evaluate to types.',
              is_argument=(self.__forward_is_argument__))
            self.__forward_evaluated__ = True
        return self.__forward_value__

    def __eq__(self, other):
        if not isinstance(other, ForwardRef):
            return NotImplemented
        return self.__forward_arg__ == other.__forward_arg__ and self.__forward_value__ == other.__forward_value__

    def __hash__(self):
        return hash((self.__forward_arg__, self.__forward_value__))

    def __repr__(self):
        return f"ForwardRef({self.__forward_arg__!r})"


class TypeVar(_Final, _Immutable, _root=True):
    __slots__ = ('__name__', '__bound__', '__constraints__', '__covariant__', '__contravariant__')

    def __init__(self, name, *constraints, bound=None, covariant=False, contravariant=False):
        self.__name__ = name
        if covariant:
            if contravariant:
                raise ValueError('Bivariant types are not supported.')
        self.__covariant__ = bool(covariant)
        self.__contravariant__ = bool(contravariant)
        if constraints:
            if bound is not None:
                raise TypeError('Constraints cannot be combined with bound=...')
        if constraints:
            if len(constraints) == 1:
                raise TypeError('A single constraint is not allowed')
        else:
            msg = 'TypeVar(name, constraint, ...): constraints must be types.'
            self.__constraints__ = tuple((_type_check(t, msg) for t in constraints))
            if bound:
                self.__bound__ = _type_check(bound, 'Bound must be a type.')
            else:
                self.__bound__ = None
        def_mod = sys._getframe(1).f_globals['__name__']
        if def_mod != 'typing':
            self.__module__ = def_mod

    def __repr__(self):
        if self.__covariant__:
            prefix = '+'
        else:
            if self.__contravariant__:
                prefix = '-'
            else:
                prefix = '~'
        return prefix + self.__name__

    def __reduce__(self):
        return self.__name__


_normalize_alias = {
 'list': "'List'", 
 'tuple': "'Tuple'", 
 'dict': "'Dict'", 
 'set': "'Set'", 
 'frozenset': "'FrozenSet'", 
 'deque': "'Deque'", 
 'defaultdict': "'DefaultDict'", 
 'type': "'Type'", 
 'Set': "'AbstractSet'"}

def _is_dunder(attr):
    return attr.startswith('__') and attr.endswith('__')


class _GenericAlias(_Final, _root=True):

    def __init__(self, origin, params, *, inst=True, special=False, name=None):
        self._inst = inst
        self._special = special
        if special:
            if name is None:
                orig_name = origin.__name__
                name = _normalize_alias.get(orig_name, orig_name)
        self._name = name
        if not isinstance(params, tuple):
            params = (
             params,)
        self.__origin__ = origin
        self.__args__ = tuple((... if a is _TypingEllipsis else () if a is _TypingEmpty else a for a in params))
        self.__parameters__ = _collect_type_vars(params)
        self.__slots__ = None
        if not name:
            self.__module__ = origin.__module__

    @_tp_cache
    def __getitem__(self, params):
        if self.__origin__ in (Generic, _Protocol):
            raise TypeError(f"Cannot subscript already-subscripted {self}")
        if not isinstance(params, tuple):
            params = (
             params,)
        msg = 'Parameters to generic types must be types.'
        params = tuple((_type_check(p, msg) for p in params))
        _check_generic(self, params)
        return _subs_tvars(self, self.__parameters__, params)

    def copy_with(self, params):
        return _GenericAlias((self.__origin__), params, name=(self._name), inst=(self._inst))

    def __repr__(self):
        if (self._name != 'Callable' or len(self.__args__)) == 2:
            if self.__args__[0] is Ellipsis:
                if self._name:
                    name = 'typing.' + self._name
                else:
                    name = _type_repr(self.__origin__)
                if not self._special:
                    args = f"[{', '.join([_type_repr(a) for a in self.__args__])}]"
                else:
                    args = ''
                return f"{name}{args}"
        if self._special:
            return 'typing.Callable'
        return f"typing.Callable[[{', '.join([_type_repr(a) for a in self.__args__[:-1]])}], {_type_repr(self.__args__[-1])}]"

    def __eq__(self, other):
        if not isinstance(other, _GenericAlias):
            return NotImplemented
        else:
            if self.__origin__ != other.__origin__:
                return False
            if self.__origin__ is Union and other.__origin__ is Union:
                return frozenset(self.__args__) == frozenset(other.__args__)
        return self.__args__ == other.__args__

    def __hash__(self):
        if self.__origin__ is Union:
            return hash((Union, frozenset(self.__args__)))
        return hash((self.__origin__, self.__args__))

    def __call__(self, *args, **kwargs):
        if not self._inst:
            raise TypeError(f"Type {self._name} cannot be instantiated; use {self._name.lower()}() instead")
        result = (self.__origin__)(*args, **kwargs)
        try:
            result.__orig_class__ = self
        except AttributeError:
            pass

        return result

    def __mro_entries__(self, bases):
        if self._name:
            res = []
            if self.__origin__ not in bases:
                res.append(self.__origin__)
            i = bases.index(self)
            if not any((isinstance(b, _GenericAlias) or issubclass(b, Generic) for b in bases[i + 1:])):
                res.append(Generic)
            return tuple(res)
        if self.__origin__ is Generic:
            i = bases.index(self)
            for b in bases[i + 1:]:
                if isinstance(b, _GenericAlias) and b is not self:
                    return ()

        return (
         self.__origin__,)

    def __getattr__(self, attr):
        if '__origin__' in self.__dict__:
            if not _is_dunder(attr):
                return getattr(self.__origin__, attr)
        raise AttributeError(attr)

    def __setattr__(self, attr, val):
        if _is_dunder(attr) or attr in ('_name', '_inst', '_special'):
            super().__setattr__(attr, val)
        else:
            setattr(self.__origin__, attr, val)

    def __instancecheck__(self, obj):
        return self.__subclasscheck__(type(obj))

    def __subclasscheck__(self, cls):
        if self._special:
            if not isinstance(cls, _GenericAlias):
                return issubclass(cls, self.__origin__)
            if cls._special:
                return issubclass(cls.__origin__, self.__origin__)
        raise TypeError('Subscripted generics cannot be used with class and instance checks')

    def __reduce__(self):
        if self._special:
            return self._name
        elif self._name:
            origin = globals()[self._name]
        else:
            origin = self.__origin__
        if origin is Callable:
            args = len(self.__args__) == 2 and self.__args__[0] is Ellipsis or (
             list(self.__args__[:-1]), self.__args__[-1])
        else:
            args = tuple(self.__args__)
            if len(args) == 1:
                if not isinstance(args[0], tuple):
                    args, = args
        return (
         operator.getitem, (origin, args))


class _VariadicGenericAlias(_GenericAlias, _root=True):

    def __getitem__(self, params):
        return self._name != 'Callable' or self._special or self.__getitem_inner__(params)
        if not isinstance(params, tuple) or len(params) != 2:
            raise TypeError('Callable must be used as Callable[[arg, ...], result].')
        args, result = params
        if args is Ellipsis:
            params = (
             Ellipsis, result)
        else:
            if not isinstance(args, list):
                raise TypeError(f"Callable[args, result]: args must be a list. Got {args}")
            params = (tuple(args), result)
        return self.__getitem_inner__(params)

    @_tp_cache
    def __getitem_inner__(self, params):
        if self.__origin__ is tuple:
            if self._special:
                if params == ():
                    return self.copy_with((_TypingEmpty,))
                else:
                    if not isinstance(params, tuple):
                        params = (
                         params,)
                    if len(params) == 2 and params[1] is ...:
                        msg = 'Tuple[t, ...]: t must be a type.'
                        p = _type_check(params[0], msg)
                        return self.copy_with((p, _TypingEllipsis))
                msg = 'Tuple[t0, t1, ...]: each t must be a type.'
                params = tuple((_type_check(p, msg) for p in params))
                return self.copy_with(params)
        if self.__origin__ is collections.abc.Callable:
            if self._special:
                args, result = params
                msg = 'Callable[args, result]: result must be a type.'
                result = _type_check(result, msg)
                if args is Ellipsis:
                    return self.copy_with((_TypingEllipsis, result))
                msg = 'Callable[[arg, ...], result]: each arg must be a type.'
                args = tuple((_type_check(arg, msg) for arg in args))
                params = args + (result,)
                return self.copy_with(params)
        return super().__getitem__(params)


class Generic:
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        if cls is Generic:
            raise TypeError('Type Generic cannot be instantiated; it can be used only as a base class')
        if super().__new__ is object.__new__ and cls.__init__ is not object.__init__:
            obj = super().__new__(cls)
        else:
            obj = (super().__new__)(cls, *args, **kwds)
        return obj

    @_tp_cache
    def __class_getitem__(cls, params):
        if not isinstance(params, tuple):
            params = (
             params,)
        elif not params:
            if cls is not Tuple:
                raise TypeError(f"Parameter list to {cls.__qualname__}[...] cannot be empty")
        else:
            msg = 'Parameters to generic types must be types.'
            params = tuple((_type_check(p, msg) for p in params))
            if cls is Generic:
                if not all((isinstance(p, TypeVar) for p in params)):
                    raise TypeError('Parameters to Generic[...] must all be type variables')
                if len(set(params)) != len(params):
                    raise TypeError('Parameters to Generic[...] must all be unique')
            elif cls is _Protocol:
                pass
            else:
                _check_generic(cls, params)
        return _GenericAlias(cls, params)

    def __init_subclass__(cls, *args, **kwargs):
        (super().__init_subclass__)(*args, **kwargs)
        tvars = []
        if '__orig_bases__' in cls.__dict__:
            error = Generic in cls.__orig_bases__
        else:
            error = Generic in cls.__bases__ and cls.__name__ != '_Protocol'
        if error:
            raise TypeError('Cannot inherit from plain Generic')
        elif '__orig_bases__' in cls.__dict__:
            tvars = _collect_type_vars(cls.__orig_bases__)
            gvars = None
            for base in cls.__orig_bases__:
                if isinstance(base, _GenericAlias):
                    if base.__origin__ is Generic:
                        if gvars is not None:
                            raise TypeError('Cannot inherit from Generic[...] multiple types.')
                    gvars = base.__parameters__

            if gvars is None:
                gvars = tvars
            else:
                tvarset = set(tvars)
                gvarset = set(gvars)
                if not tvarset <= gvarset:
                    s_vars = ', '.join((str(t) for t in tvars if t not in gvarset))
                    s_args = ', '.join((str(g) for g in gvars))
                    raise TypeError(f"Some type variables ({s_vars}) are not listed in Generic[{s_args}]")
            tvars = gvars
        cls.__parameters__ = tuple(tvars)


class _TypingEmpty:
    pass


class _TypingEllipsis:
    pass


def cast(typ, val):
    return val


def _get_defaults(func):
    try:
        code = func.__code__
    except AttributeError:
        return {}
    else:
        pos_count = code.co_argcount
        arg_names = code.co_varnames
        arg_names = arg_names[:pos_count]
        defaults = func.__defaults__ or ()
        kwdefaults = func.__kwdefaults__
        res = dict(kwdefaults) if kwdefaults else {}
        pos_offset = pos_count - len(defaults)
        for name, value in zip(arg_names[pos_offset:], defaults):
            res[name] = value

        return res


_allowed_types = (
 types.FunctionType, types.BuiltinFunctionType,
 types.MethodType, types.ModuleType,
 WrapperDescriptorType, MethodWrapperType, MethodDescriptorType)

def get_type_hints(obj, globalns=None, localns=None):
    if getattr(obj, '__no_type_check__', None):
        return {}
        if isinstance(obj, type):
            hints = {}
            for base in reversed(obj.__mro__):
                if globalns is None:
                    base_globals = sys.modules[base.__module__].__dict__
                else:
                    base_globals = globalns
                ann = base.__dict__.get('__annotations__', {})
                for name, value in ann.items():
                    if value is None:
                        value = type(None)
                    if isinstance(value, str):
                        value = ForwardRef(value, is_argument=False)
                    value = _eval_type(value, base_globals, localns)
                    hints[name] = value

            return hints
        if globalns is None:
            if isinstance(obj, types.ModuleType):
                globalns = obj.__dict__
            else:
                globalns = getattr(obj, '__globals__', {})
            if localns is None:
                localns = globalns
    elif localns is None:
        localns = globalns
    hints = getattr(obj, '__annotations__', None)
    if hints is None:
        if isinstance(obj, _allowed_types):
            return {}
        raise TypeError('{!r} is not a module, class, method, or function.'.format(obj))
    defaults = _get_defaults(obj)
    hints = dict(hints)
    for name, value in hints.items():
        if value is None:
            value = type(None)
        if isinstance(value, str):
            value = ForwardRef(value)
        value = _eval_type(value, globalns, localns)
        if name in defaults:
            if defaults[name] is None:
                value = Optional[value]
        hints[name] = value

    return hints


def no_type_check(arg):
    if isinstance(arg, type):
        arg_attrs = arg.__dict__.copy()
        for attr, val in arg.__dict__.items():
            if val in arg.__bases__ + (arg,):
                arg_attrs.pop(attr)

        for obj in arg_attrs.values():
            if isinstance(obj, types.FunctionType):
                obj.__no_type_check__ = True
            if isinstance(obj, type):
                no_type_check(obj)

    try:
        arg.__no_type_check__ = True
    except TypeError:
        pass

    return arg


def no_type_check_decorator(decorator):

    @functools.wraps(decorator)
    def wrapped_decorator(*args, **kwds):
        func = decorator(*args, **kwds)
        func = no_type_check(func)
        return func

    return wrapped_decorator


def _overload_dummy(*args, **kwds):
    raise NotImplementedError('You should not call an overloaded function. A series of @overload-decorated functions outside a stub module should always be followed by an implementation that is not @overload-ed.')


def overload(func):
    return _overload_dummy


class _ProtocolMeta(type):

    def __instancecheck__(self, obj):
        if _Protocol not in self.__bases__:
            return super().__instancecheck__(obj)
        raise TypeError('Protocols cannot be used with isinstance().')

    def __subclasscheck__(self, cls):
        if not self._is_protocol:
            return NotImplemented
        if self is _Protocol:
            return True
        attrs = self._get_protocol_attrs()
        for attr in attrs:
            if not any((attr in d.__dict__ for d in cls.__mro__)):
                return False

        return True

    def _get_protocol_attrs(self):
        protocol_bases = []
        for c in self.__mro__:
            if getattr(c, '_is_protocol', False) and c.__name__ != '_Protocol':
                protocol_bases.append(c)

        attrs = set()
        for base in protocol_bases:
            for attr in base.__dict__.keys():
                for c in self.__mro__:
                    if c is not base:
                        if attr in c.__dict__ and not getattr(c, '_is_protocol', False):
                            break
                else:
                    if attr.startswith('_abc_') or attr != '__abstractmethods__' and attr != '__annotations__' and attr != '__weakref__' and attr != '_is_protocol' and attr != '_gorg' and attr != '__dict__' and attr != '__args__' and attr != '__slots__' and attr != '_get_protocol_attrs' and attr != '__next_in_mro__' and attr != '__parameters__' and attr != '__origin__' and attr != '__orig_bases__' and attr != '__extra__' and attr != '__tree_hash__' and attr != '__module__':
                        attrs.add(attr)

        return attrs


class _Protocol(Generic, metaclass=_ProtocolMeta):
    __slots__ = ()
    _is_protocol = True

    def __class_getitem__(cls, params):
        return super().__class_getitem__(params)


T = TypeVar('T')
KT = TypeVar('KT')
VT = TypeVar('VT')
T_co = TypeVar('T_co', covariant=True)
V_co = TypeVar('V_co', covariant=True)
VT_co = TypeVar('VT_co', covariant=True)
T_contra = TypeVar('T_contra', contravariant=True)
CT_co = TypeVar('CT_co', covariant=True, bound=type)
AnyStr = TypeVar('AnyStr', bytes, str)

def _alias(origin, params, inst=True):
    return _GenericAlias(origin, params, special=True, inst=inst)


Hashable = _alias(collections.abc.Hashable, ())
Awaitable = _alias(collections.abc.Awaitable, T_co)
Coroutine = _alias(collections.abc.Coroutine, (T_co, T_contra, V_co))
AsyncIterable = _alias(collections.abc.AsyncIterable, T_co)
AsyncIterator = _alias(collections.abc.AsyncIterator, T_co)
Iterable = _alias(collections.abc.Iterable, T_co)
Iterator = _alias(collections.abc.Iterator, T_co)
Reversible = _alias(collections.abc.Reversible, T_co)
Sized = _alias(collections.abc.Sized, ())
Container = _alias(collections.abc.Container, T_co)
Collection = _alias(collections.abc.Collection, T_co)
Callable = _VariadicGenericAlias((collections.abc.Callable), (), special=True)
Callable.__doc__ = 'Callable type; Callable[[int], str] is a function of (int) -> str.\n\n    The subscription syntax must always be used with exactly two\n    values: the argument list and the return type.  The argument list\n    must be a list of types or ellipsis; the return type must be a single type.\n\n    There is no syntax to indicate optional or keyword arguments,\n    such function types are rarely used as callback types.\n    '
AbstractSet = _alias(collections.abc.Set, T_co)
MutableSet = _alias(collections.abc.MutableSet, T)
Mapping = _alias(collections.abc.Mapping, (KT, VT_co))
MutableMapping = _alias(collections.abc.MutableMapping, (KT, VT))
Sequence = _alias(collections.abc.Sequence, T_co)
MutableSequence = _alias(collections.abc.MutableSequence, T)
ByteString = _alias(collections.abc.ByteString, ())
Tuple = _VariadicGenericAlias(tuple, (), inst=False, special=True)
Tuple.__doc__ = 'Tuple type; Tuple[X, Y] is the cross-product type of X and Y.\n\n    Example: Tuple[T1, T2] is a tuple of two elements corresponding\n    to type variables T1 and T2.  Tuple[int, float, str] is a tuple\n    of an int, a float and a string.\n\n    To specify a variable-length tuple of homogeneous type, use Tuple[T, ...].\n    '
List = _alias(list, T, inst=False)
Deque = _alias(collections.deque, T)
Set = _alias(set, T, inst=False)
FrozenSet = _alias(frozenset, T_co, inst=False)
MappingView = _alias(collections.abc.MappingView, T_co)
KeysView = _alias(collections.abc.KeysView, KT)
ItemsView = _alias(collections.abc.ItemsView, (KT, VT_co))
ValuesView = _alias(collections.abc.ValuesView, VT_co)
ContextManager = _alias(contextlib.AbstractContextManager, T_co)
AsyncContextManager = _alias(contextlib.AbstractAsyncContextManager, T_co)
Dict = _alias(dict, (KT, VT), inst=False)
DefaultDict = _alias(collections.defaultdict, (KT, VT))
Counter = _alias(collections.Counter, T)
ChainMap = _alias(collections.ChainMap, (KT, VT))
Generator = _alias(collections.abc.Generator, (T_co, T_contra, V_co))
AsyncGenerator = _alias(collections.abc.AsyncGenerator, (T_co, T_contra))
Type = _alias(type, CT_co, inst=False)
Type.__doc__ = "A special construct usable to annotate class objects.\n\n    For example, suppose we have the following classes::\n\n      class User: ...  # Abstract base for User classes\n      class BasicUser(User): ...\n      class ProUser(User): ...\n      class TeamUser(User): ...\n\n    And a function that takes a class argument that's a subclass of\n    User and returns an instance of the corresponding class::\n\n      U = TypeVar('U', bound=User)\n      def new_user(user_class: Type[U]) -> U:\n          user = user_class()\n          # (Here we could write the user object to a database)\n          return user\n\n      joe = new_user(BasicUser)\n\n    At this point the type checker knows that joe has type BasicUser.\n    "

class SupportsInt(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __int__(self) -> int:
        pass


class SupportsFloat(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __float__(self) -> float:
        pass


class SupportsComplex(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __complex__(self) -> complex:
        pass


class SupportsBytes(_Protocol):
    __slots__ = ()

    @abstractmethod
    def __bytes__(self) -> bytes:
        pass


class SupportsAbs(_Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __abs__(self) -> T_co:
        pass


class SupportsRound(_Protocol[T_co]):
    __slots__ = ()

    @abstractmethod
    def __round__(self, ndigits: int=0) -> T_co:
        pass


def _make_nmtuple(name, types):
    msg = "NamedTuple('Name', [(f0, t0), (f1, t1), ...]); each t must be a type"
    types = [(n, _type_check(t, msg)) for n, t in types]
    nm_tpl = collections.namedtuple(name, [n for n, t in types])
    nm_tpl.__annotations__ = nm_tpl._field_types = collections.OrderedDict(types)
    try:
        nm_tpl.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return nm_tpl


_prohibited = ('__new__', '__init__', '__slots__', '__getnewargs__', '_fields', '_field_defaults',
               '_field_types', '_make', '_replace', '_asdict', '_source')
_special = ('__module__', '__name__', '__qualname__', '__annotations__')

class NamedTupleMeta(type):

    def __new__(cls, typename, bases, ns):
        if ns.get('_root', False):
            return super().__new__(cls, typename, bases, ns)
        types = ns.get('__annotations__', {})
        nm_tpl = _make_nmtuple(typename, types.items())
        defaults = []
        defaults_dict = {}
        for field_name in types:
            if field_name in ns:
                default_value = ns[field_name]
                defaults.append(default_value)
                defaults_dict[field_name] = default_value

        nm_tpl.__new__.__annotations__ = collections.OrderedDict(types)
        nm_tpl.__new__.__defaults__ = tuple(defaults)
        nm_tpl._field_defaults = defaults_dict
        for key in ns:
            if key in _prohibited:
                raise AttributeError('Cannot overwrite NamedTuple attribute ' + key)

        return nm_tpl


class NamedTuple(metaclass=NamedTupleMeta):
    _root = True

    def __new__(self, typename, fields=None, **kwargs):
        if fields is None:
            fields = kwargs.items()
        else:
            if kwargs:
                raise TypeError('Either list of fields or keywords can be provided to NamedTuple, not both')
        return _make_nmtuple(typename, fields)


def NewType(name, tp):

    def new_type(x):
        return x

    new_type.__name__ = name
    new_type.__supertype__ = tp
    return new_type


Text = str
TYPE_CHECKING = False

class IO(Generic[AnyStr]):
    __slots__ = ()

    @abstractproperty
    def mode(self) -> str:
        pass

    @abstractproperty
    def name(self) -> str:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def closed(self) -> bool:
        pass

    @abstractmethod
    def fileno(self) -> int:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def isatty(self) -> bool:
        pass

    @abstractmethod
    def read(self, n: int=-1) -> AnyStr:
        pass

    @abstractmethod
    def readable(self) -> bool:
        pass

    @abstractmethod
    def readline(self, limit: int=-1) -> AnyStr:
        pass

    @abstractmethod
    def readlines(self, hint: int=-1) -> List[AnyStr]:
        pass

    @abstractmethod
    def seek(self, offset: int, whence: int=0) -> int:
        pass

    @abstractmethod
    def seekable(self) -> bool:
        pass

    @abstractmethod
    def tell(self) -> int:
        pass

    @abstractmethod
    def truncate(self, size: int=None) -> int:
        pass

    @abstractmethod
    def writable(self) -> bool:
        pass

    @abstractmethod
    def write(self, s: AnyStr) -> int:
        pass

    @abstractmethod
    def writelines(self, lines: List[AnyStr]) -> None:
        pass

    @abstractmethod
    def __enter__(self) -> 'IO[AnyStr]':
        pass

    @abstractmethod
    def __exit__(self, type, value, traceback) -> None:
        pass


class BinaryIO(IO[bytes]):
    __slots__ = ()

    @abstractmethod
    def write(self, s: Union[(bytes, bytearray)]) -> int:
        pass

    @abstractmethod
    def __enter__(self) -> 'BinaryIO':
        pass


class TextIO(IO[str]):
    __slots__ = ()

    @abstractproperty
    def buffer(self) -> BinaryIO:
        pass

    @abstractproperty
    def encoding(self) -> str:
        pass

    @abstractproperty
    def errors(self) -> Optional[str]:
        pass

    @abstractproperty
    def line_buffering(self) -> bool:
        pass

    @abstractproperty
    def newlines(self) -> Any:
        pass

    @abstractmethod
    def __enter__(self) -> 'TextIO':
        pass


class io:
    __all__ = [
     'IO', 'TextIO', 'BinaryIO']
    IO = IO
    TextIO = TextIO
    BinaryIO = BinaryIO


io.__name__ = __name__ + '.io'
sys.modules[io.__name__] = io
Pattern = _alias(stdlib_re.Pattern, AnyStr)
Match = _alias(stdlib_re.Match, AnyStr)

class re:
    __all__ = [
     'Pattern', 'Match']
    Pattern = Pattern
    Match = Match


re.__name__ = __name__ + '.re'
sys.modules[re.__name__] = re