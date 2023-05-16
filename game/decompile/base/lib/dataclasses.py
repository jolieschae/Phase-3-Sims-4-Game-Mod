# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\dataclasses.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 46615 bytes
import re, sys, copy, types, inspect, keyword
__all__ = [
 "'dataclass'", 
 "'field'", 
 "'Field'", 
 "'FrozenInstanceError'", 
 "'InitVar'", 
 "'MISSING'", 
 "'fields'", 
 "'asdict'", 
 "'astuple'", 
 "'make_dataclass'", 
 "'replace'", 
 "'is_dataclass'"]

class FrozenInstanceError(AttributeError):
    pass


class _HAS_DEFAULT_FACTORY_CLASS:

    def __repr__(self):
        return '<factory>'


_HAS_DEFAULT_FACTORY = _HAS_DEFAULT_FACTORY_CLASS()

class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()
_EMPTY_METADATA = types.MappingProxyType({})

class _FIELD_BASE:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


_FIELD = _FIELD_BASE('_FIELD')
_FIELD_CLASSVAR = _FIELD_BASE('_FIELD_CLASSVAR')
_FIELD_INITVAR = _FIELD_BASE('_FIELD_INITVAR')
_FIELDS = '__dataclass_fields__'
_PARAMS = '__dataclass_params__'
_POST_INIT_NAME = '__post_init__'
_MODULE_IDENTIFIER_RE = re.compile('^(?:\\s*(\\w+)\\s*\\.)?\\s*(\\w+)')

class _InitVarMeta(type):

    def __getitem__(self, params):
        return self


class InitVar(metaclass=_InitVarMeta):
    pass


class Field:
    __slots__ = ('name', 'type', 'default', 'default_factory', 'repr', 'hash', 'init',
                 'compare', 'metadata', '_field_type')

    def __init__(self, default, default_factory, init, repr, hash, compare, metadata):
        self.name = None
        self.type = None
        self.default = default
        self.default_factory = default_factory
        self.init = init
        self.repr = repr
        self.hash = hash
        self.compare = compare
        self.metadata = _EMPTY_METADATA if (metadata is None or len(metadata) == 0) else (types.MappingProxyType(metadata))
        self._field_type = None

    def __repr__(self):
        return f"Field(name={self.name!r},type={self.type!r},default={self.default!r},default_factory={self.default_factory!r},init={self.init!r},repr={self.repr!r},hash={self.hash!r},compare={self.compare!r},metadata={self.metadata!r},_field_type={self._field_type})"

    def __set_name__(self, owner, name):
        func = getattr(type(self.default), '__set_name__', None)
        if func:
            func(self.default, owner, name)


class _DataclassParams:
    __slots__ = ('init', 'repr', 'eq', 'order', 'unsafe_hash', 'frozen')

    def __init__(self, init, repr, eq, order, unsafe_hash, frozen):
        self.init = init
        self.repr = repr
        self.eq = eq
        self.order = order
        self.unsafe_hash = unsafe_hash
        self.frozen = frozen

    def __repr__(self):
        return f"_DataclassParams(init={self.init!r},repr={self.repr!r},eq={self.eq!r},order={self.order!r},unsafe_hash={self.unsafe_hash!r},frozen={self.frozen!r})"


def field(*, default=MISSING, default_factory=MISSING, init=True, repr=True, hash=None, compare=True, metadata=None):
    if default is not MISSING:
        if default_factory is not MISSING:
            raise ValueError('cannot specify both default and default_factory')
    return Field(default, default_factory, init, repr, hash, compare, metadata)


def _tuple_str(obj_name, fields):
    if not fields:
        return '()'
    return f"({','.join([{obj_name}.{f.name} for f in fields])},)"


def _create_fn(name, args, body, *, globals=None, locals=None, return_type=MISSING):
    if locals is None:
        locals = {}
    return_annotation = ''
    if return_type is not MISSING:
        locals['_return_type'] = return_type
        return_annotation = '->_return_type'
    args = ','.join(args)
    body = '\n'.join((f" {b}" for b in body))
    txt = f"def {name}({args}){return_annotation}:\n{body}"
    exec(txt, globals, locals)
    return locals[name]


def _field_assign(frozen, name, value, self_name):
    if frozen:
        return f"object.__setattr__({self_name},{name!r},{value})"
    return f"{self_name}.{name}={value}"


def _field_init(f, frozen, globals, self_name):
    default_name = f"_dflt_{f.name}"
    if f.default_factory is not MISSING:
        if f.init:
            globals[default_name] = f.default_factory
            value = f"{default_name}() if {f.name} is _HAS_DEFAULT_FACTORY else {f.name}"
        else:
            globals[default_name] = f.default_factory
            value = f"{default_name}()"
    elif f.init:
        if f.default is MISSING:
            value = f.name
        elif f.default is not MISSING:
            globals[default_name] = f.default
            value = f.name
    else:
        return
    if f._field_type is _FIELD_INITVAR:
        return
    return _field_assign(frozen, f.name, value, self_name)


def _init_param(f):
    if f.default is MISSING and f.default_factory is MISSING:
        default = ''
    else:
        if f.default is not MISSING:
            default = f"=_dflt_{f.name}"
        else:
            if f.default_factory is not MISSING:
                default = '=_HAS_DEFAULT_FACTORY'
    return f"{f.name}:_type_{f.name}{default}"


def _init_fn(fields, frozen, has_post_init, self_name):
    seen_default = False
    for f in fields:
        if f.init:
            if f.default is MISSING:
                seen_default = f.default_factory is MISSING or True
            elif seen_default:
                raise TypeError(f"non-default argument {f.name!r} follows default argument")

    globals = {'MISSING':MISSING, 
     '_HAS_DEFAULT_FACTORY':_HAS_DEFAULT_FACTORY}
    body_lines = []
    for f in fields:
        line = _field_init(f, frozen, globals, self_name)
        if line:
            body_lines.append(line)

    if has_post_init:
        params_str = ','.join((f.name for f in fields if f._field_type is _FIELD_INITVAR))
        body_lines.append(f"{self_name}.{_POST_INIT_NAME}({params_str})")
    if not body_lines:
        body_lines = [
         'pass']
    locals = {f"_type_{f.name}": f.type for f in fields}
    return _create_fn('__init__', ([
     self_name] + [_init_param(f) for f in fields if f.init]),
      body_lines,
      locals=locals,
      globals=globals,
      return_type=None)


def _repr_fn(fields):
    return _create_fn('__repr__', ('self', ), [
     'return self.__class__.__qualname__ + f"(' + ', '.join([f"{f.name}={{self.{f.name}!r}}" for f in fields]) + ')"'])


def _frozen_get_del_attr(cls, fields):
    globals = {'cls':cls, 
     'FrozenInstanceError':FrozenInstanceError}
    if fields:
        fields_str = '(' + ','.join((repr(f.name) for f in fields)) + ',)'
    else:
        fields_str = '()'
    return (
     _create_fn('__setattr__', ('self', 'name', 'value'),
       (
      f"if type(self) is cls or name in {fields_str}:",
      ' raise FrozenInstanceError(f"cannot assign to field {name!r}")',
      'super(cls, self).__setattr__(name, value)'),
       globals=globals),
     _create_fn('__delattr__', ('self', 'name'),
       (
      f"if type(self) is cls or name in {fields_str}:",
      ' raise FrozenInstanceError(f"cannot delete field {name!r}")',
      'super(cls, self).__delattr__(name)'),
       globals=globals))


def _cmp_fn(name, op, self_tuple, other_tuple):
    return _create_fn(name, ('self', 'other'), [
     'if other.__class__ is self.__class__:',
     f" return {self_tuple}{op}{other_tuple}",
     'return NotImplemented'])


def _hash_fn(fields):
    self_tuple = _tuple_str('self', fields)
    return _create_fn('__hash__', ('self', ), [
     f"return hash({self_tuple})"])


def _is_classvar(a_type, typing):
    return a_type is typing.ClassVar or type(a_type) is typing._GenericAlias and a_type.__origin__ is typing.ClassVar


def _is_initvar(a_type, dataclasses):
    return a_type is dataclasses.InitVar


def _is_type(annotation, cls, a_module, a_type, is_type_predicate):
    match = _MODULE_IDENTIFIER_RE.match(annotation)
    if match:
        ns = None
        module_name = match.group(1)
        if not module_name:
            ns = sys.modules.get(cls.__module__).__dict__
        else:
            module = sys.modules.get(cls.__module__)
            if module:
                if module.__dict__.get(module_name) is a_module:
                    ns = sys.modules.get(a_type.__module__).__dict__
            elif ns and is_type_predicate(ns.get(match.group(2)), a_module):
                return True
    return False


def _get_field(cls, a_name, a_type):
    default = getattr(cls, a_name, MISSING)
    if isinstance(default, Field):
        f = default
    else:
        if isinstance(default, types.MemberDescriptorType):
            default = MISSING
        f = field(default=default)
    f.name = a_name
    f.type = a_type
    f._field_type = _FIELD
    typing = sys.modules.get('typing')
    if typing:
        if (_is_classvar(a_type, typing) or isinstance)(f.type, str):
            if _is_type(f.type, cls, typing, typing.ClassVar, _is_classvar):
                f._field_type = _FIELD_CLASSVAR
    if f._field_type is _FIELD:
        dataclasses = sys.modules[__name__]
        if (_is_initvar(a_type, dataclasses) or isinstance)(f.type, str):
            if _is_type(f.type, cls, dataclasses, dataclasses.InitVar, _is_initvar):
                f._field_type = _FIELD_INITVAR
    if f._field_type in (_FIELD_CLASSVAR, _FIELD_INITVAR):
        if f.default_factory is not MISSING:
            raise TypeError(f"field {f.name} cannot have a default factory")
    if f._field_type is _FIELD:
        if isinstance(f.default, (list, dict, set)):
            raise ValueError(f"mutable default {type(f.default)} for field {f.name} is not allowed: use default_factory")
    return f


def _set_new_attribute(cls, name, value):
    if name in cls.__dict__:
        return True
    setattr(cls, name, value)
    return False


def _hash_set_none(cls, fields):
    pass


def _hash_add(cls, fields):
    flds = [f for f in fields if (f.compare if f.hash is None else f.hash)]
    return _hash_fn(flds)


def _hash_exception(cls, fields):
    raise TypeError(f"Cannot overwrite attribute __hash__ in class {cls.__name__}")


_hash_action = {
 (False, False, False, False): None, 
 (False, False, False, True): None, 
 (False, False, True, False): None, 
 (False, False, True, True): None, 
 (False, True, False, False): '_hash_set_none', 
 (False, True, False, True): None, 
 (False, True, True, False): '_hash_add', 
 (False, True, True, True): None, 
 (True, False, False, False): '_hash_add', 
 (True, False, False, True): '_hash_exception', 
 (True, False, True, False): '_hash_add', 
 (True, False, True, True): '_hash_exception', 
 (True, True, False, False): '_hash_add', 
 (True, True, False, True): '_hash_exception', 
 (True, True, True, False): '_hash_add', 
 (True, True, True, True): '_hash_exception'}

def _process_class(cls, init, repr, eq, order, unsafe_hash, frozen):
    fields = {}
    setattr(cls, _PARAMS, _DataclassParams(init, repr, eq, order, unsafe_hash, frozen))
    any_frozen_base = False
    has_dataclass_bases = False
    for b in cls.__mro__[-1:0:-1]:
        base_fields = getattr(b, _FIELDS, None)
        if base_fields:
            has_dataclass_bases = True
            for f in base_fields.values():
                fields[f.name] = f

            if getattr(b, _PARAMS).frozen:
                any_frozen_base = True

    cls_annotations = cls.__dict__.get('__annotations__', {})
    cls_fields = [_get_field(cls, name, type) for name, type in cls_annotations.items()]
    for f in cls_fields:
        fields[f.name] = f
        if isinstance(getattr(cls, f.name, None), Field):
            if f.default is MISSING:
                delattr(cls, f.name)
            else:
                setattr(cls, f.name, f.default)

    for name, value in cls.__dict__.items():
        if isinstance(value, Field) and name not in cls_annotations:
            raise TypeError(f"{name!r} is a field but has no type annotation")

    if has_dataclass_bases:
        if any_frozen_base and not frozen:
            raise TypeError('cannot inherit non-frozen dataclass from a frozen one')
        if not any_frozen_base:
            if frozen:
                raise TypeError('cannot inherit frozen dataclass from a non-frozen one')
    setattr(cls, _FIELDS, fields)
    class_hash = cls.__dict__.get('__hash__', MISSING)
    has_explicit_hash = not (class_hash is MISSING or class_hash is None and '__eq__' in cls.__dict__)
    if order and not eq:
        raise ValueError('eq must be true if order is true')
    if init:
        has_post_init = hasattr(cls, _POST_INIT_NAME)
        flds = [f for f in fields.values() if f._field_type in (_FIELD, _FIELD_INITVAR)]
        _set_new_attribute(cls, '__init__', _init_fn(flds, frozen, has_post_init, '__dataclass_self__' if 'self' in fields else 'self'))
    field_list = [f for f in fields.values() if f._field_type is _FIELD]
    if repr:
        flds = [f for f in field_list if f.repr]
        _set_new_attribute(cls, '__repr__', _repr_fn(flds))
    if eq:
        flds = [f for f in field_list if f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
        _set_new_attribute(cls, '__eq__', _cmp_fn('__eq__', '==', self_tuple, other_tuple))
    if order:
        flds = [f for f in field_list if f.compare]
        self_tuple = _tuple_str('self', flds)
        other_tuple = _tuple_str('other', flds)
        for name, op in (('__lt__', '<'), ('__le__', '<='), ('__gt__', '>'), ('__ge__', '>=')):
            if _set_new_attribute(cls, name, _cmp_fn(name, op, self_tuple, other_tuple)):
                raise TypeError(f"Cannot overwrite attribute {name} in class {cls.__name__}. Consider using functools.total_ordering")

    if frozen:
        for fn in _frozen_get_del_attr(cls, field_list):
            if _set_new_attribute(cls, fn.__name__, fn):
                raise TypeError(f"Cannot overwrite attribute {fn.__name__} in class {cls.__name__}")

    hash_action = _hash_action[(bool(unsafe_hash),
     bool(eq),
     bool(frozen),
     has_explicit_hash)]
    if hash_action:
        cls.__hash__ = hash_action(cls, field_list)
    if not getattr(cls, '__doc__'):
        cls.__doc__ = cls.__name__ + str(inspect.signature(cls)).replace(' -> None', '')
    return cls


def dataclass(_cls=None, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False):

    def wrap(cls):
        return _process_class(cls, init, repr, eq, order, unsafe_hash, frozen)

    if _cls is None:
        return wrap
    return wrap(_cls)


def fields(class_or_instance):
    try:
        fields = getattr(class_or_instance, _FIELDS)
    except AttributeError:
        raise TypeError('must be called with a dataclass type or instance')

    return tuple((f for f in fields.values() if f._field_type is _FIELD))


def _is_dataclass_instance(obj):
    return not isinstance(obj, type) and hasattr(obj, _FIELDS)


def is_dataclass(obj):
    return hasattr(obj, _FIELDS)


def asdict(obj, *, dict_factory=dict):
    if not _is_dataclass_instance(obj):
        raise TypeError('asdict() should be called on dataclass instances')
    return _asdict_inner(obj, dict_factory)


def _asdict_inner(obj, dict_factory):
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_inner(getattr(obj, f.name), dict_factory)
            result.append((f.name, value))

        return dict_factory(result)
    if isinstance(obj, (list, tuple)):
        return type(obj)((_asdict_inner(v, dict_factory) for v in obj))
    if isinstance(obj, dict):
        return type(obj)(((_asdict_inner(k, dict_factory), _asdict_inner(v, dict_factory)) for k, v in obj.items()))
    return copy.deepcopy(obj)


def astuple(obj, *, tuple_factory=tuple):
    if not _is_dataclass_instance(obj):
        raise TypeError('astuple() should be called on dataclass instances')
    return _astuple_inner(obj, tuple_factory)


def _astuple_inner(obj, tuple_factory):
    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _astuple_inner(getattr(obj, f.name), tuple_factory)
            result.append(value)

        return tuple_factory(result)
    if isinstance(obj, (list, tuple)):
        return type(obj)((_astuple_inner(v, tuple_factory) for v in obj))
    if isinstance(obj, dict):
        return type(obj)(((_astuple_inner(k, tuple_factory), _astuple_inner(v, tuple_factory)) for k, v in obj.items()))
    return copy.deepcopy(obj)


def make_dataclass(cls_name, fields, *, bases=(), namespace=None, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False):
    if namespace is None:
        namespace = {}
    else:
        namespace = namespace.copy()
    seen = set()
    anns = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        else:
            if len(item) == 2:
                name, tp = item
            else:
                if len(item) == 3:
                    name, tp, spec = item
                    namespace[name] = spec
                else:
                    raise TypeError(f"Invalid field: {item!r}")
        if not (isinstance(name, str) and name.isidentifier()):
            raise TypeError(f"Field names must be valid identifers: {name!r}")
        if keyword.iskeyword(name):
            raise TypeError(f"Field names must not be keywords: {name!r}")
        if name in seen:
            raise TypeError(f"Field name duplicated: {name!r}")
        seen.add(name)
        anns[name] = tp

    namespace['__annotations__'] = anns
    cls = types.new_class(cls_name, bases, {}, lambda ns: ns.update(namespace))
    return dataclass(cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
      frozen=frozen)


def replace(obj, **changes):
    if not _is_dataclass_instance(obj):
        raise TypeError('replace() should be called on dataclass instances')
    for f in getattr(obj, _FIELDS).values():
        if f._field_type is _FIELD_CLASSVAR:
            continue
        if not f.init:
            if f.name in changes:
                raise ValueError(f"field {f.name} is declared with init=False, it cannot be specified with replace()")
                continue
            if f.name not in changes:
                changes[f.name] = getattr(obj, f.name)

    return (obj.__class__)(**changes)