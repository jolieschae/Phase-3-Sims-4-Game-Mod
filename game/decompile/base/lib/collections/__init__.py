# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\collections\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 48919 bytes
__all__ = [
 "'deque'", "'defaultdict'", "'namedtuple'", "'UserDict'", "'UserList'", 
 "'UserString'", 
 "'Counter'", "'OrderedDict'", "'ChainMap'"]
import _collections_abc
from operator import itemgetter as _itemgetter, eq as _eq
from keyword import iskeyword as _iskeyword
import sys as _sys, heapq as _heapq
from _weakref import proxy as _proxy
from itertools import repeat as _repeat, chain as _chain, starmap as _starmap
from reprlib import recursive_repr as _recursive_repr
try:
    from _collections import deque
except ImportError:
    pass
else:
    _collections_abc.MutableSequence.register(deque)
try:
    from _collections import defaultdict
except ImportError:
    pass

def __getattr__(name):
    if name in _collections_abc.__all__:
        obj = getattr(_collections_abc, name)
        import warnings
        warnings.warn("Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated, and in 3.8 it will stop working", DeprecationWarning,
          stacklevel=2)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class _OrderedDictKeysView(_collections_abc.KeysView):

    def __reversed__(self):
        yield from reversed(self._mapping)
        if False:
            yield None


class _OrderedDictItemsView(_collections_abc.ItemsView):

    def __reversed__(self):
        for key in reversed(self._mapping):
            yield (
             key, self._mapping[key])


class _OrderedDictValuesView(_collections_abc.ValuesView):

    def __reversed__(self):
        for key in reversed(self._mapping):
            yield self._mapping[key]


class _Link(object):
    __slots__ = ('prev', 'next', 'key', '__weakref__')


class OrderedDict(dict):

    def __init__(*args, **kwds):
        if not args:
            raise TypeError("descriptor '__init__' of 'OrderedDict' object needs an argument")
        else:
            self, *args = args
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            try:
                self._OrderedDict__root
            except AttributeError:
                self._OrderedDict__hardroot = _Link()
                self._OrderedDict__root = root = _proxy(self._OrderedDict__hardroot)
                root.prev = root.next = root
                self._OrderedDict__map = {}

        (self._OrderedDict__update)(*args, **kwds)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__, proxy=_proxy, Link=_Link):
        if key not in self:
            self._OrderedDict__map[key] = link = Link()
            root = self._OrderedDict__root
            last = root.prev
            link.prev, link.next, link.key = last, root, key
            last.next = link
            root.prev = proxy(link)
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        dict_delitem(self, key)
        link = self._OrderedDict__map.pop(key)
        link_prev = link.prev
        link_next = link.next
        link_prev.next = link_next
        link_next.prev = link_prev
        link.prev = None
        link.next = None

    def __iter__(self):
        root = self._OrderedDict__root
        curr = root.next
        while curr is not root:
            yield curr.key
            curr = curr.next

    def __reversed__(self):
        root = self._OrderedDict__root
        curr = root.prev
        while curr is not root:
            yield curr.key
            curr = curr.prev

    def clear(self):
        root = self._OrderedDict__root
        root.prev = root.next = root
        self._OrderedDict__map.clear()
        dict.clear(self)

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        else:
            root = self._OrderedDict__root
            if last:
                link = root.prev
                link_prev = link.prev
                link_prev.next = root
                root.prev = link_prev
            else:
                link = root.next
            link_next = link.next
            root.next = link_next
            link_next.prev = root
        key = link.key
        del self._OrderedDict__map[key]
        value = dict.pop(self, key)
        return (key, value)

    def move_to_end(self, key, last=True):
        link = self._OrderedDict__map[key]
        link_prev = link.prev
        link_next = link.next
        soft_link = link_next.prev
        link_prev.next = link_next
        link_next.prev = link_prev
        root = self._OrderedDict__root
        if last:
            last = root.prev
            link.prev = last
            link.next = root
            root.prev = soft_link
            last.next = link
        else:
            first = root.next
            link.prev = root
            link.next = first
            first.prev = soft_link
            root.next = link

    def __sizeof__(self):
        sizeof = _sys.getsizeof
        n = len(self) + 1
        size = sizeof(self.__dict__)
        size += sizeof(self._OrderedDict__map) * 2
        size += sizeof(self._OrderedDict__hardroot) * n
        size += sizeof(self._OrderedDict__root) * n
        return size

    update = _OrderedDict__update = _collections_abc.MutableMapping.update

    def keys(self):
        return _OrderedDictKeysView(self)

    def items(self):
        return _OrderedDictItemsView(self)

    def values(self):
        return _OrderedDictValuesView(self)

    __ne__ = _collections_abc.MutableMapping.__ne__
    _OrderedDict__marker = object()

    def pop(self, key, default=_OrderedDict__marker):
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is self._OrderedDict__marker:
            raise KeyError(key)
        return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    @_recursive_repr()
    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def __reduce__(self):
        inst_dict = vars(self).copy()
        for k in vars(OrderedDict()):
            inst_dict.pop(k, None)

        return (
         self.__class__, (), inst_dict or None, None, iter(self.items()))

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        self = cls()
        for key in iterable:
            self[key] = value

        return self

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return dict.__eq__(self, other) and all(map(_eq, self, other))
        return dict.__eq__(self, other)


try:
    from _collections import OrderedDict
except ImportError:
    pass

_nt_itemgetters = {}

def namedtuple--- This code section failed: ---

 L. 342         0  LOAD_GLOBAL              isinstance
                2  LOAD_DEREF               'field_names'
                4  LOAD_GLOBAL              str
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_FALSE    26  'to 26'

 L. 343        10  LOAD_DEREF               'field_names'
               12  LOAD_METHOD              replace
               14  LOAD_STR                 ','
               16  LOAD_STR                 ' '
               18  CALL_METHOD_2         2  '2 positional arguments'
               20  LOAD_METHOD              split
               22  CALL_METHOD_0         0  '0 positional arguments'
               24  STORE_DEREF              'field_names'
             26_0  COME_FROM             8  '8'

 L. 344        26  LOAD_GLOBAL              list
               28  LOAD_GLOBAL              map
               30  LOAD_GLOBAL              str
               32  LOAD_DEREF               'field_names'
               34  CALL_FUNCTION_2       2  '2 positional arguments'
               36  CALL_FUNCTION_1       1  '1 positional argument'
               38  STORE_DEREF              'field_names'

 L. 345        40  LOAD_GLOBAL              _sys
               42  LOAD_METHOD              intern
               44  LOAD_GLOBAL              str
               46  LOAD_FAST                'typename'
               48  CALL_FUNCTION_1       1  '1 positional argument'
               50  CALL_METHOD_1         1  '1 positional argument'
               52  STORE_FAST               'typename'

 L. 347        54  LOAD_FAST                'rename'
               56  POP_JUMP_IF_FALSE   144  'to 144'

 L. 348        58  LOAD_GLOBAL              set
               60  CALL_FUNCTION_0       0  '0 positional arguments'
               62  STORE_FAST               'seen'

 L. 349        64  SETUP_LOOP          144  'to 144'
               66  LOAD_GLOBAL              enumerate
               68  LOAD_DEREF               'field_names'
               70  CALL_FUNCTION_1       1  '1 positional argument'
               72  GET_ITER         
               74  FOR_ITER            142  'to 142'
               76  UNPACK_SEQUENCE_2     2 
               78  STORE_FAST               'index'
               80  STORE_FAST               'name'

 L. 350        82  LOAD_FAST                'name'
               84  LOAD_METHOD              isidentifier
               86  CALL_METHOD_0         0  '0 positional arguments'
               88  POP_JUMP_IF_FALSE   116  'to 116'

 L. 351        90  LOAD_GLOBAL              _iskeyword
               92  LOAD_FAST                'name'
               94  CALL_FUNCTION_1       1  '1 positional argument'
               96  POP_JUMP_IF_TRUE    116  'to 116'

 L. 352        98  LOAD_FAST                'name'
              100  LOAD_METHOD              startswith
              102  LOAD_STR                 '_'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_JUMP_IF_TRUE    116  'to 116'

 L. 353       108  LOAD_FAST                'name'
              110  LOAD_FAST                'seen'
              112  COMPARE_OP               in
              114  POP_JUMP_IF_FALSE   130  'to 130'
            116_0  COME_FROM           106  '106'
            116_1  COME_FROM            96  '96'
            116_2  COME_FROM            88  '88'

 L. 354       116  LOAD_STR                 '_'
              118  LOAD_FAST                'index'
              120  FORMAT_VALUE          0  ''
              122  BUILD_STRING_2        2 
              124  LOAD_DEREF               'field_names'
              126  LOAD_FAST                'index'
              128  STORE_SUBSCR     
            130_0  COME_FROM           114  '114'

 L. 355       130  LOAD_FAST                'seen'
              132  LOAD_METHOD              add
              134  LOAD_FAST                'name'
              136  CALL_METHOD_1         1  '1 positional argument'
              138  POP_TOP          
              140  JUMP_BACK            74  'to 74'
              142  POP_BLOCK        
            144_0  COME_FROM_LOOP       64  '64'
            144_1  COME_FROM            56  '56'

 L. 357       144  SETUP_LOOP          228  'to 228'
              146  LOAD_FAST                'typename'
              148  BUILD_LIST_1          1 
              150  LOAD_DEREF               'field_names'
              152  BINARY_ADD       
              154  GET_ITER         
            156_0  COME_FROM           208  '208'
              156  FOR_ITER            226  'to 226'
              158  STORE_FAST               'name'

 L. 358       160  LOAD_GLOBAL              type
              162  LOAD_FAST                'name'
              164  CALL_FUNCTION_1       1  '1 positional argument'
              166  LOAD_GLOBAL              str
              168  COMPARE_OP               is-not
              170  POP_JUMP_IF_FALSE   180  'to 180'

 L. 359       172  LOAD_GLOBAL              TypeError
              174  LOAD_STR                 'Type names and field names must be strings'
              176  CALL_FUNCTION_1       1  '1 positional argument'
              178  RAISE_VARARGS_1       1  'exception instance'
            180_0  COME_FROM           170  '170'

 L. 360       180  LOAD_FAST                'name'
              182  LOAD_METHOD              isidentifier
              184  CALL_METHOD_0         0  '0 positional arguments'
              186  POP_JUMP_IF_TRUE    202  'to 202'

 L. 361       188  LOAD_GLOBAL              ValueError
              190  LOAD_STR                 'Type names and field names must be valid identifiers: '
              192  LOAD_FAST                'name'
              194  FORMAT_VALUE          2  '!r'
              196  BUILD_STRING_2        2 
              198  CALL_FUNCTION_1       1  '1 positional argument'
              200  RAISE_VARARGS_1       1  'exception instance'
            202_0  COME_FROM           186  '186'

 L. 363       202  LOAD_GLOBAL              _iskeyword
              204  LOAD_FAST                'name'
              206  CALL_FUNCTION_1       1  '1 positional argument'
              208  POP_JUMP_IF_FALSE   156  'to 156'

 L. 364       210  LOAD_GLOBAL              ValueError
              212  LOAD_STR                 'Type names and field names cannot be a keyword: '
              214  LOAD_FAST                'name'
              216  FORMAT_VALUE          2  '!r'
              218  BUILD_STRING_2        2 
              220  CALL_FUNCTION_1       1  '1 positional argument'
              222  RAISE_VARARGS_1       1  'exception instance'
              224  JUMP_BACK           156  'to 156'
              226  POP_BLOCK        
            228_0  COME_FROM_LOOP      144  '144'

 L. 367       228  LOAD_GLOBAL              set
              230  CALL_FUNCTION_0       0  '0 positional arguments'
              232  STORE_FAST               'seen'

 L. 368       234  SETUP_LOOP          314  'to 314'
              236  LOAD_DEREF               'field_names'
              238  GET_ITER         
              240  FOR_ITER            312  'to 312'
              242  STORE_FAST               'name'

 L. 369       244  LOAD_FAST                'name'
              246  LOAD_METHOD              startswith
              248  LOAD_STR                 '_'
              250  CALL_METHOD_1         1  '1 positional argument'
          252_254  POP_JUMP_IF_FALSE   276  'to 276'
              256  LOAD_FAST                'rename'
          258_260  POP_JUMP_IF_TRUE    276  'to 276'

 L. 370       262  LOAD_GLOBAL              ValueError
              264  LOAD_STR                 'Field names cannot start with an underscore: '
              266  LOAD_FAST                'name'
              268  FORMAT_VALUE          2  '!r'
              270  BUILD_STRING_2        2 
              272  CALL_FUNCTION_1       1  '1 positional argument'
              274  RAISE_VARARGS_1       1  'exception instance'
            276_0  COME_FROM           258  '258'
            276_1  COME_FROM           252  '252'

 L. 372       276  LOAD_FAST                'name'
              278  LOAD_FAST                'seen'
              280  COMPARE_OP               in
          282_284  POP_JUMP_IF_FALSE   300  'to 300'

 L. 373       286  LOAD_GLOBAL              ValueError
              288  LOAD_STR                 'Encountered duplicate field name: '
              290  LOAD_FAST                'name'
              292  FORMAT_VALUE          2  '!r'
              294  BUILD_STRING_2        2 
              296  CALL_FUNCTION_1       1  '1 positional argument'
              298  RAISE_VARARGS_1       1  'exception instance'
            300_0  COME_FROM           282  '282'

 L. 374       300  LOAD_FAST                'seen'
              302  LOAD_METHOD              add
              304  LOAD_FAST                'name'
              306  CALL_METHOD_1         1  '1 positional argument'
              308  POP_TOP          
              310  JUMP_BACK           240  'to 240'
              312  POP_BLOCK        
            314_0  COME_FROM_LOOP      234  '234'

 L. 376       314  BUILD_MAP_0           0 
              316  STORE_FAST               'field_defaults'

 L. 377       318  LOAD_FAST                'defaults'
              320  LOAD_CONST               None
              322  COMPARE_OP               is-not
          324_326  POP_JUMP_IF_FALSE   392  'to 392'

 L. 378       328  LOAD_GLOBAL              tuple
              330  LOAD_FAST                'defaults'
              332  CALL_FUNCTION_1       1  '1 positional argument'
              334  STORE_FAST               'defaults'

 L. 379       336  LOAD_GLOBAL              len
              338  LOAD_FAST                'defaults'
              340  CALL_FUNCTION_1       1  '1 positional argument'
              342  LOAD_GLOBAL              len
              344  LOAD_DEREF               'field_names'
              346  CALL_FUNCTION_1       1  '1 positional argument'
              348  COMPARE_OP               >
          350_352  POP_JUMP_IF_FALSE   362  'to 362'

 L. 380       354  LOAD_GLOBAL              TypeError
              356  LOAD_STR                 'Got more default values than field names'
              358  CALL_FUNCTION_1       1  '1 positional argument'
              360  RAISE_VARARGS_1       1  'exception instance'
            362_0  COME_FROM           350  '350'

 L. 381       362  LOAD_GLOBAL              dict
              364  LOAD_GLOBAL              reversed
              366  LOAD_GLOBAL              list
              368  LOAD_GLOBAL              zip
              370  LOAD_GLOBAL              reversed
              372  LOAD_DEREF               'field_names'
              374  CALL_FUNCTION_1       1  '1 positional argument'

 L. 382       376  LOAD_GLOBAL              reversed
              378  LOAD_FAST                'defaults'
              380  CALL_FUNCTION_1       1  '1 positional argument'
              382  CALL_FUNCTION_2       2  '2 positional arguments'
              384  CALL_FUNCTION_1       1  '1 positional argument'
              386  CALL_FUNCTION_1       1  '1 positional argument'
              388  CALL_FUNCTION_1       1  '1 positional argument'
              390  STORE_FAST               'field_defaults'
            392_0  COME_FROM           324  '324'

 L. 385       392  LOAD_GLOBAL              tuple
              394  LOAD_GLOBAL              map
              396  LOAD_GLOBAL              _sys
              398  LOAD_ATTR                intern
              400  LOAD_DEREF               'field_names'
              402  CALL_FUNCTION_2       2  '2 positional arguments'
              404  CALL_FUNCTION_1       1  '1 positional argument'
              406  STORE_DEREF              'field_names'

 L. 386       408  LOAD_GLOBAL              len
              410  LOAD_DEREF               'field_names'
              412  CALL_FUNCTION_1       1  '1 positional argument'
              414  STORE_DEREF              'num_fields'

 L. 387       416  LOAD_GLOBAL              repr
              418  LOAD_DEREF               'field_names'
              420  CALL_FUNCTION_1       1  '1 positional argument'
              422  LOAD_METHOD              replace
              424  LOAD_STR                 "'"
              426  LOAD_STR                 ''
              428  CALL_METHOD_2         2  '2 positional arguments'
              430  LOAD_CONST               1
              432  LOAD_CONST               -1
              434  BUILD_SLICE_2         2 
              436  BINARY_SUBSCR    
              438  STORE_FAST               'arg_list'

 L. 388       440  LOAD_STR                 '('
              442  LOAD_STR                 ', '
              444  LOAD_METHOD              join
              446  LOAD_GENEXPR             '<code_object <genexpr>>'
              448  LOAD_STR                 'namedtuple.<locals>.<genexpr>'
              450  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              452  LOAD_DEREF               'field_names'
              454  GET_ITER         
              456  CALL_FUNCTION_1       1  '1 positional argument'
              458  CALL_METHOD_1         1  '1 positional argument'
              460  BINARY_ADD       
              462  LOAD_STR                 ')'
              464  BINARY_ADD       
              466  STORE_DEREF              'repr_fmt'

 L. 389       468  LOAD_GLOBAL              tuple
              470  LOAD_ATTR                __new__
              472  STORE_DEREF              'tuple_new'

 L. 390       474  LOAD_GLOBAL              len
              476  STORE_DEREF              '_len'

 L. 394       478  LOAD_STR                 'def __new__(_cls, '
              480  LOAD_FAST                'arg_list'
              482  FORMAT_VALUE          0  ''
              484  LOAD_STR                 '): return _tuple_new(_cls, ('
              486  LOAD_FAST                'arg_list'
              488  FORMAT_VALUE          0  ''
              490  LOAD_STR                 '))'
              492  BUILD_STRING_5        5 
              494  STORE_FAST               's'

 L. 395       496  LOAD_DEREF               'tuple_new'
              498  LOAD_STR                 'namedtuple_'
              500  LOAD_FAST                'typename'
              502  FORMAT_VALUE          0  ''
              504  BUILD_STRING_2        2 
              506  LOAD_CONST               ('_tuple_new', '__name__')
              508  BUILD_CONST_KEY_MAP_2     2 
              510  STORE_FAST               'namespace'

 L. 397       512  LOAD_GLOBAL              exec
              514  LOAD_FAST                's'
              516  LOAD_FAST                'namespace'
              518  CALL_FUNCTION_2       2  '2 positional arguments'
              520  POP_TOP          

 L. 398       522  LOAD_FAST                'namespace'
              524  LOAD_STR                 '__new__'
              526  BINARY_SUBSCR    
              528  STORE_FAST               '__new__'

 L. 399       530  LOAD_STR                 'Create new instance of '
              532  LOAD_FAST                'typename'
              534  FORMAT_VALUE          0  ''
              536  LOAD_STR                 '('
              538  LOAD_FAST                'arg_list'
              540  FORMAT_VALUE          0  ''
              542  LOAD_STR                 ')'
              544  BUILD_STRING_5        5 
              546  LOAD_FAST                '__new__'
              548  STORE_ATTR               __doc__

 L. 400       550  LOAD_FAST                'defaults'
              552  LOAD_CONST               None
              554  COMPARE_OP               is-not
          556_558  POP_JUMP_IF_FALSE   566  'to 566'

 L. 401       560  LOAD_FAST                'defaults'
              562  LOAD_FAST                '__new__'
              564  STORE_ATTR               __defaults__
            566_0  COME_FROM           556  '556'

 L. 403       566  LOAD_GLOBAL              classmethod
              568  LOAD_CLOSURE             '_len'
              570  LOAD_CLOSURE             'num_fields'
              572  LOAD_CLOSURE             'tuple_new'
              574  BUILD_TUPLE_3         3 
              576  LOAD_CODE                <code_object _make>
              578  LOAD_STR                 'namedtuple.<locals>._make'
              580  MAKE_FUNCTION_8          'closure'
              582  CALL_FUNCTION_1       1  '1 positional argument'
              584  STORE_FAST               '_make'

 L. 410       586  LOAD_STR                 'Make a new '
              588  LOAD_FAST                'typename'
              590  FORMAT_VALUE          0  ''
              592  LOAD_STR                 ' object from a sequence or iterable'
              594  BUILD_STRING_3        3 
              596  LOAD_FAST                '_make'
              598  LOAD_ATTR                __func__
              600  STORE_ATTR               __doc__

 L. 413       602  LOAD_CLOSURE             'field_names'
              604  BUILD_TUPLE_1         1 
              606  LOAD_CODE                <code_object _replace>
              608  LOAD_STR                 'namedtuple.<locals>._replace'
              610  MAKE_FUNCTION_8          'closure'
              612  STORE_FAST               '_replace'

 L. 419       614  LOAD_STR                 'Return a new '
              616  LOAD_FAST                'typename'
              618  FORMAT_VALUE          0  ''
              620  LOAD_STR                 ' object replacing specified fields with new values'
              622  BUILD_STRING_3        3 
              624  LOAD_FAST                '_replace'
              626  STORE_ATTR               __doc__

 L. 422       628  LOAD_CLOSURE             'repr_fmt'
              630  BUILD_TUPLE_1         1 
              632  LOAD_CODE                <code_object __repr__>
              634  LOAD_STR                 'namedtuple.<locals>.__repr__'
              636  MAKE_FUNCTION_8          'closure'
              638  STORE_FAST               '__repr__'

 L. 426       640  LOAD_CODE                <code_object _asdict>
              642  LOAD_STR                 'namedtuple.<locals>._asdict'
              644  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              646  STORE_FAST               '_asdict'

 L. 430       648  LOAD_CODE                <code_object __getnewargs__>
              650  LOAD_STR                 'namedtuple.<locals>.__getnewargs__'
              652  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              654  STORE_FAST               '__getnewargs__'

 L. 436       656  SETUP_LOOP          704  'to 704'
              658  LOAD_FAST                '__new__'
              660  LOAD_FAST                '_make'
              662  LOAD_ATTR                __func__
              664  LOAD_FAST                '_replace'

 L. 437       666  LOAD_FAST                '__repr__'
              668  LOAD_FAST                '_asdict'
              670  LOAD_FAST                '__getnewargs__'
              672  BUILD_TUPLE_6         6 
              674  GET_ITER         
              676  FOR_ITER            702  'to 702'
              678  STORE_FAST               'method'

 L. 438       680  LOAD_FAST                'typename'
              682  FORMAT_VALUE          0  ''
              684  LOAD_STR                 '.'
              686  LOAD_FAST                'method'
              688  LOAD_ATTR                __name__
              690  FORMAT_VALUE          0  ''
              692  BUILD_STRING_3        3 
              694  LOAD_FAST                'method'
              696  STORE_ATTR               __qualname__
          698_700  JUMP_BACK           676  'to 676'
              702  POP_BLOCK        
            704_0  COME_FROM_LOOP      656  '656'

 L. 443       704  LOAD_FAST                'typename'
              706  FORMAT_VALUE          0  ''
              708  LOAD_STR                 '('
              710  LOAD_FAST                'arg_list'
              712  FORMAT_VALUE          0  ''
              714  LOAD_STR                 ')'
              716  BUILD_STRING_4        4 

 L. 444       718  LOAD_CONST               ()

 L. 445       720  LOAD_DEREF               'field_names'

 L. 446       722  LOAD_FAST                'field_defaults'

 L. 447       724  LOAD_FAST                '__new__'

 L. 448       726  LOAD_FAST                '_make'

 L. 449       728  LOAD_FAST                '_replace'

 L. 450       730  LOAD_FAST                '__repr__'

 L. 451       732  LOAD_FAST                '_asdict'

 L. 452       734  LOAD_FAST                '__getnewargs__'
              736  LOAD_CONST               ('__doc__', '__slots__', '_fields', '_fields_defaults', '__new__', '_make', '_replace', '__repr__', '_asdict', '__getnewargs__')
              738  BUILD_CONST_KEY_MAP_10    10 
              740  STORE_FAST               'class_namespace'

 L. 454       742  LOAD_GLOBAL              _nt_itemgetters
              744  STORE_FAST               'cache'

 L. 455       746  SETUP_LOOP          856  'to 856'
              748  LOAD_GLOBAL              enumerate
              750  LOAD_DEREF               'field_names'
              752  CALL_FUNCTION_1       1  '1 positional argument'
              754  GET_ITER         
              756  FOR_ITER            854  'to 854'
              758  UNPACK_SEQUENCE_2     2 
              760  STORE_FAST               'index'
              762  STORE_FAST               'name'

 L. 456       764  SETUP_EXCEPT        782  'to 782'

 L. 457       766  LOAD_FAST                'cache'
              768  LOAD_FAST                'index'
              770  BINARY_SUBSCR    
              772  UNPACK_SEQUENCE_2     2 
              774  STORE_FAST               'itemgetter_object'
              776  STORE_FAST               'doc'
              778  POP_BLOCK        
              780  JUMP_FORWARD        834  'to 834'
            782_0  COME_FROM_EXCEPT    764  '764'

 L. 458       782  DUP_TOP          
              784  LOAD_GLOBAL              KeyError
              786  COMPARE_OP               exception-match
          788_790  POP_JUMP_IF_FALSE   832  'to 832'
              792  POP_TOP          
              794  POP_TOP          
              796  POP_TOP          

 L. 459       798  LOAD_GLOBAL              _itemgetter
              800  LOAD_FAST                'index'
              802  CALL_FUNCTION_1       1  '1 positional argument'
              804  STORE_FAST               'itemgetter_object'

 L. 460       806  LOAD_STR                 'Alias for field number '
              808  LOAD_FAST                'index'
              810  FORMAT_VALUE          0  ''
              812  BUILD_STRING_2        2 
              814  STORE_FAST               'doc'

 L. 461       816  LOAD_FAST                'itemgetter_object'
              818  LOAD_FAST                'doc'
              820  BUILD_TUPLE_2         2 
              822  LOAD_FAST                'cache'
              824  LOAD_FAST                'index'
              826  STORE_SUBSCR     
              828  POP_EXCEPT       
              830  JUMP_FORWARD        834  'to 834'
            832_0  COME_FROM           788  '788'
              832  END_FINALLY      
            834_0  COME_FROM           830  '830'
            834_1  COME_FROM           780  '780'

 L. 462       834  LOAD_GLOBAL              property
              836  LOAD_FAST                'itemgetter_object'
              838  LOAD_FAST                'doc'
              840  LOAD_CONST               ('doc',)
              842  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              844  LOAD_FAST                'class_namespace'
              846  LOAD_FAST                'name'
              848  STORE_SUBSCR     
          850_852  JUMP_BACK           756  'to 756'
              854  POP_BLOCK        
            856_0  COME_FROM_LOOP      746  '746'

 L. 464       856  LOAD_GLOBAL              type
              858  LOAD_FAST                'typename'
              860  LOAD_GLOBAL              tuple
              862  BUILD_TUPLE_1         1 
              864  LOAD_FAST                'class_namespace'
              866  CALL_FUNCTION_3       3  '3 positional arguments'
              868  STORE_FAST               'result'

 L. 471       870  LOAD_FAST                'module'
              872  LOAD_CONST               None
              874  COMPARE_OP               is
          876_878  POP_JUMP_IF_FALSE   932  'to 932'

 L. 472       880  SETUP_EXCEPT        906  'to 906'

 L. 473       882  LOAD_GLOBAL              _sys
              884  LOAD_METHOD              _getframe
              886  LOAD_CONST               1
              888  CALL_METHOD_1         1  '1 positional argument'
              890  LOAD_ATTR                f_globals
              892  LOAD_METHOD              get
              894  LOAD_STR                 '__name__'
              896  LOAD_STR                 '__main__'
              898  CALL_METHOD_2         2  '2 positional arguments'
              900  STORE_FAST               'module'
              902  POP_BLOCK        
              904  JUMP_FORWARD        932  'to 932'
            906_0  COME_FROM_EXCEPT    880  '880'

 L. 474       906  DUP_TOP          
              908  LOAD_GLOBAL              AttributeError
              910  LOAD_GLOBAL              ValueError
              912  BUILD_TUPLE_2         2 
              914  COMPARE_OP               exception-match
          916_918  POP_JUMP_IF_FALSE   930  'to 930'
              920  POP_TOP          
              922  POP_TOP          
              924  POP_TOP          

 L. 475       926  POP_EXCEPT       
              928  JUMP_FORWARD        932  'to 932'
            930_0  COME_FROM           916  '916'
              930  END_FINALLY      
            932_0  COME_FROM           928  '928'
            932_1  COME_FROM           904  '904'
            932_2  COME_FROM           876  '876'

 L. 476       932  LOAD_FAST                'module'
              934  LOAD_CONST               None
              936  COMPARE_OP               is-not
          938_940  POP_JUMP_IF_FALSE   948  'to 948'

 L. 477       942  LOAD_FAST                'module'
              944  LOAD_FAST                'result'
              946  STORE_ATTR               __module__
            948_0  COME_FROM           938  '938'

 L. 479       948  LOAD_FAST                'result'
              950  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 130_0


def _count_elements(mapping, iterable):
    mapping_get = mapping.get
    for elem in iterable:
        mapping[elem] = mapping_get(elem, 0) + 1


try:
    from _collections import _count_elements
except ImportError:
    pass

class Counter(dict):

    def __init__(*args, **kwds):
        if not args:
            raise TypeError("descriptor '__init__' of 'Counter' object needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        super(Counter, self).__init__()
        (self.update)(*args, **kwds)

    def __missing__(self, key):
        return 0

    def most_common(self, n=None):
        if n is None:
            return sorted((self.items()), key=(_itemgetter(1)), reverse=True)
        return _heapq.nlargest(n, (self.items()), key=(_itemgetter(1)))

    def elements(self):
        return _chain.from_iterable(_starmap(_repeat, self.items()))

    @classmethod
    def fromkeys(cls, iterable, v=None):
        raise NotImplementedError('Counter.fromkeys() is undefined.  Use Counter(iterable) instead.')

    def update--- This code section failed: ---

 L. 637         0  LOAD_FAST                'args'
                2  POP_JUMP_IF_TRUE     12  'to 12'

 L. 638         4  LOAD_GLOBAL              TypeError
                6  LOAD_STR                 "descriptor 'update' of 'Counter' object needs an argument"
                8  CALL_FUNCTION_1       1  '1 positional argument'
               10  RAISE_VARARGS_1       1  'exception instance'
             12_0  COME_FROM             2  '2'

 L. 640        12  LOAD_FAST                'args'
               14  UNPACK_EX_1+0           
               16  STORE_FAST               'self'
               18  STORE_FAST               'args'

 L. 641        20  LOAD_GLOBAL              len
               22  LOAD_FAST                'args'
               24  CALL_FUNCTION_1       1  '1 positional argument'
               26  LOAD_CONST               1
               28  COMPARE_OP               >
               30  POP_JUMP_IF_FALSE    48  'to 48'

 L. 642        32  LOAD_GLOBAL              TypeError
               34  LOAD_STR                 'expected at most 1 arguments, got %d'
               36  LOAD_GLOBAL              len
               38  LOAD_FAST                'args'
               40  CALL_FUNCTION_1       1  '1 positional argument'
               42  BINARY_MODULO    
               44  CALL_FUNCTION_1       1  '1 positional argument'
               46  RAISE_VARARGS_1       1  'exception instance'
             48_0  COME_FROM            30  '30'

 L. 643        48  LOAD_FAST                'args'
               50  POP_JUMP_IF_FALSE    60  'to 60'
               52  LOAD_FAST                'args'
               54  LOAD_CONST               0
               56  BINARY_SUBSCR    
               58  JUMP_FORWARD         62  'to 62'
             60_0  COME_FROM            50  '50'
               60  LOAD_CONST               None
             62_0  COME_FROM            58  '58'
               62  STORE_FAST               'iterable'

 L. 644        64  LOAD_FAST                'iterable'
               66  LOAD_CONST               None
               68  COMPARE_OP               is-not
               70  POP_JUMP_IF_FALSE   164  'to 164'

 L. 645        72  LOAD_GLOBAL              isinstance
               74  LOAD_FAST                'iterable'
               76  LOAD_GLOBAL              _collections_abc
               78  LOAD_ATTR                Mapping
               80  CALL_FUNCTION_2       2  '2 positional arguments'
               82  POP_JUMP_IF_FALSE   154  'to 154'

 L. 646        84  LOAD_FAST                'self'
               86  POP_JUMP_IF_FALSE   136  'to 136'

 L. 647        88  LOAD_FAST                'self'
               90  LOAD_ATTR                get
               92  STORE_FAST               'self_get'

 L. 648        94  SETUP_LOOP          152  'to 152'
               96  LOAD_FAST                'iterable'
               98  LOAD_METHOD              items
              100  CALL_METHOD_0         0  '0 positional arguments'
              102  GET_ITER         
              104  FOR_ITER            132  'to 132'
              106  UNPACK_SEQUENCE_2     2 
              108  STORE_FAST               'elem'
              110  STORE_FAST               'count'

 L. 649       112  LOAD_FAST                'count'
              114  LOAD_FAST                'self_get'
              116  LOAD_FAST                'elem'
              118  LOAD_CONST               0
              120  CALL_FUNCTION_2       2  '2 positional arguments'
              122  BINARY_ADD       
              124  LOAD_FAST                'self'
              126  LOAD_FAST                'elem'
              128  STORE_SUBSCR     
              130  JUMP_BACK           104  'to 104'
              132  POP_BLOCK        
              134  JUMP_ABSOLUTE       164  'to 164'
            136_0  COME_FROM            86  '86'

 L. 651       136  LOAD_GLOBAL              super
              138  LOAD_GLOBAL              Counter
              140  LOAD_FAST                'self'
              142  CALL_FUNCTION_2       2  '2 positional arguments'
              144  LOAD_METHOD              update
              146  LOAD_FAST                'iterable'
              148  CALL_METHOD_1         1  '1 positional argument'
              150  POP_TOP          
            152_0  COME_FROM_LOOP       94  '94'
              152  JUMP_FORWARD        164  'to 164'
            154_0  COME_FROM            82  '82'

 L. 653       154  LOAD_GLOBAL              _count_elements
              156  LOAD_FAST                'self'
              158  LOAD_FAST                'iterable'
              160  CALL_FUNCTION_2       2  '2 positional arguments'
              162  POP_TOP          
            164_0  COME_FROM           152  '152'
            164_1  COME_FROM            70  '70'

 L. 654       164  LOAD_FAST                'kwds'
              166  POP_JUMP_IF_FALSE   178  'to 178'

 L. 655       168  LOAD_FAST                'self'
              170  LOAD_METHOD              update
              172  LOAD_FAST                'kwds'
              174  CALL_METHOD_1         1  '1 positional argument'
              176  POP_TOP          
            178_0  COME_FROM           166  '166'

Parse error at or near `COME_FROM_LOOP' instruction at offset 152_0

    def subtract(*args, **kwds):
        if not args:
            raise TypeError("descriptor 'subtract' of 'Counter' object needs an argument")
        else:
            self, *args = args
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            iterable = args[0] if args else None
            if iterable is not None:
                self_get = self.get
                if isinstance(iterable, _collections_abc.Mapping):
                    for elem, count in iterable.items():
                        self[elem] = self_get(elem, 0) - count

            else:
                for elem in iterable:
                    self[elem] = self_get(elem, 0) - 1

        if kwds:
            self.subtract(kwds)

    def copy(self):
        return self.__class__(self)

    def __reduce__(self):
        return (
         self.__class__, (dict(self),))

    def __delitem__(self, elem):
        if elem in self:
            super().__delitem__(elem)

    def __repr__(self):
        if not self:
            return '%s()' % self.__class__.__name__
        try:
            items = ', '.join(map('%r: %r'.__mod__, self.most_common()))
            return '%s({%s})' % (self.__class__.__name__, items)
        except TypeError:
            return '{0}({1!r})'.format(self.__class__.__name__, dict(self))

    def __add__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        result = Counter()
        for elem, count in self.items():
            newcount = count + other[elem]
            if newcount > 0:
                result[elem] = newcount

        for elem, count in other.items():
            if elem not in self and count > 0:
                result[elem] = count

        return result

    def __sub__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        result = Counter()
        for elem, count in self.items():
            newcount = count - other[elem]
            if newcount > 0:
                result[elem] = newcount

        for elem, count in other.items():
            if elem not in self and count < 0:
                result[elem] = 0 - count

        return result

    def __or__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        result = Counter()
        for elem, count in self.items():
            other_count = other[elem]
            newcount = other_count if count < other_count else count
            if newcount > 0:
                result[elem] = newcount

        for elem, count in other.items():
            if elem not in self and count > 0:
                result[elem] = count

        return result

    def __and__(self, other):
        if not isinstance(other, Counter):
            return NotImplemented
        result = Counter()
        for elem, count in self.items():
            other_count = other[elem]
            newcount = count if count < other_count else other_count
            if newcount > 0:
                result[elem] = newcount

        return result

    def __pos__(self):
        result = Counter()
        for elem, count in self.items():
            if count > 0:
                result[elem] = count

        return result

    def __neg__(self):
        result = Counter()
        for elem, count in self.items():
            if count < 0:
                result[elem] = 0 - count

        return result

    def _keep_positive(self):
        nonpositive = [elem for elem, count in self.items() if not count > 0]
        for elem in nonpositive:
            del self[elem]

        return self

    def __iadd__(self, other):
        for elem, count in other.items():
            self[elem] += count

        return self._keep_positive()

    def __isub__(self, other):
        for elem, count in other.items():
            self[elem] -= count

        return self._keep_positive()

    def __ior__(self, other):
        for elem, other_count in other.items():
            count = self[elem]
            if other_count > count:
                self[elem] = other_count

        return self._keep_positive()

    def __iand__(self, other):
        for elem, count in self.items():
            other_count = other[elem]
            if other_count < count:
                self[elem] = other_count

        return self._keep_positive()


class ChainMap(_collections_abc.MutableMapping):

    def __init__(self, *maps):
        self.maps = list(maps) or [{}]

    def __missing__(self, key):
        raise KeyError(key)

    def __getitem__(self, key):
        for mapping in self.maps:
            try:
                return mapping[key]
            except KeyError:
                pass

        return self.__missing__(key)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def __len__(self):
        return len((set().union)(*self.maps))

    def __iter__(self):
        d = {}
        for mapping in reversed(self.maps):
            d.update(mapping)

        return iter(d)

    def __contains__(self, key):
        return any((key in m for m in self.maps))

    def __bool__(self):
        return any(self.maps)

    @_recursive_repr()
    def __repr__(self):
        return '{0.__class__.__name__}({1})'.format(self, ', '.join(map(repr, self.maps)))

    @classmethod
    def fromkeys(cls, iterable, *args):
        return cls((dict.fromkeys)(iterable, *args))

    def copy(self):
        return (self.__class__)(self.maps[0].copy(), *self.maps[1:])

    __copy__ = copy

    def new_child(self, m=None):
        if m is None:
            m = {}
        return (self.__class__)(m, *self.maps)

    @property
    def parents(self):
        return (self.__class__)(*self.maps[1:])

    def __setitem__(self, key, value):
        self.maps[0][key] = value

    def __delitem__(self, key):
        try:
            del self.maps[0][key]
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    def popitem(self):
        try:
            return self.maps[0].popitem()
        except KeyError:
            raise KeyError('No keys found in the first mapping.')

    def pop(self, key, *args):
        try:
            return (self.maps[0].pop)(key, *args)
        except KeyError:
            raise KeyError('Key not found in the first mapping: {!r}'.format(key))

    def clear(self):
        self.maps[0].clear()


class UserDict(_collections_abc.MutableMapping):

    def __init__(*args, **kwargs):
        if not args:
            raise TypeError("descriptor '__init__' of 'UserDict' object needs an argument")
        else:
            self, *args = args
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            elif args:
                dict = args[0]
            else:
                if 'dict' in kwargs:
                    dict = kwargs.pop('dict')
                    import warnings
                    warnings.warn("Passing 'dict' as keyword argument is deprecated", DeprecationWarning,
                      stacklevel=2)
                else:
                    dict = None
        self.data = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, '__missing__'):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return repr(self.data)

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data

        c.update(self)
        return c

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value

        return d


class UserList(_collections_abc.MutableSequence):

    def __init__(self, initlist=None):
        self.data = []
        if initlist is not None:
            if type(initlist) == type(self.data):
                self.data[:] = initlist
            else:
                if isinstance(initlist, UserList):
                    self.data[:] = initlist.data[:]
                else:
                    self.data = list(initlist)

    def __repr__(self):
        return repr(self.data)

    def __lt__(self, other):
        return self.data < self._UserList__cast(other)

    def __le__(self, other):
        return self.data <= self._UserList__cast(other)

    def __eq__(self, other):
        return self.data == self._UserList__cast(other)

    def __gt__(self, other):
        return self.data > self._UserList__cast(other)

    def __ge__(self, other):
        return self.data >= self._UserList__cast(other)

    def __cast(self, other):
        if isinstance(other, UserList):
            return other.data
        return other

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, item):
        self.data[i] = item

    def __delitem__(self, i):
        del self.data[i]

    def __add__(self, other):
        if isinstance(other, UserList):
            return self.__class__(self.data + other.data)
        if isinstance(other, type(self.data)):
            return self.__class__(self.data + other)
        return self.__class__(self.data + list(other))

    def __radd__(self, other):
        if isinstance(other, UserList):
            return self.__class__(other.data + self.data)
        if isinstance(other, type(self.data)):
            return self.__class__(other + self.data)
        return self.__class__(list(other) + self.data)

    def __iadd__(self, other):
        if isinstance(other, UserList):
            self.data += other.data
        else:
            if isinstance(other, type(self.data)):
                self.data += other
            else:
                self.data += list(other)
        return self

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __imul__(self, n):
        self.data *= n
        return self

    def append(self, item):
        self.data.append(item)

    def insert(self, i, item):
        self.data.insert(i, item)

    def pop(self, i=-1):
        return self.data.pop(i)

    def remove(self, item):
        self.data.remove(item)

    def clear(self):
        self.data.clear()

    def copy(self):
        return self.__class__(self)

    def count(self, item):
        return self.data.count(item)

    def index(self, item, *args):
        return (self.data.index)(item, *args)

    def reverse(self):
        self.data.reverse()

    def sort(self, *args, **kwds):
        (self.data.sort)(*args, **kwds)

    def extend(self, other):
        if isinstance(other, UserList):
            self.data.extend(other.data)
        else:
            self.data.extend(other)


class UserString(_collections_abc.Sequence):

    def __init__(self, seq):
        if isinstance(seq, str):
            self.data = seq
        else:
            if isinstance(seq, UserString):
                self.data = seq.data[:]
            else:
                self.data = str(seq)

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data)

    def __float__(self):
        return float(self.data)

    def __complex__(self):
        return complex(self.data)

    def __hash__(self):
        return hash(self.data)

    def __getnewargs__(self):
        return (self.data[:],)

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        return self.data == string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        return self.data < string

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        return self.data <= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        return self.data > string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        return self.data >= string

    def __contains__(self, char):
        if isinstance(char, UserString):
            char = char.data
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        if isinstance(other, str):
            return self.__class__(self.data + other)
        return self.__class__(self.data + str(other))

    def __radd__(self, other):
        if isinstance(other, str):
            return self.__class__(other + self.data)
        return self.__class__(str(other) + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    def __rmod__(self, format):
        return self.__class__(format % args)

    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def casefold(self):
        return self.__class__(self.data.casefold())

    def center(self, width, *args):
        return self.__class__((self.data.center)(width, *args))

    def count(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, UserString):
            sub = sub.data
        return self.data.count(sub, start, end)

    def encode(self, encoding=None, errors=None):
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            return self.__class__(self.data.encode(encoding))
        return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=_sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, UserString):
            sub = sub.data
        return self.data.find(sub, start, end)

    def format(self, *args, **kwds):
        return (self.data.format)(*args, **kwds)

    def format_map(self, mapping):
        return self.data.format_map(mapping)

    def index(self, sub, start=0, end=_sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isascii(self):
        return self.data.isascii()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def isidentifier(self):
        return self.data.isidentifier()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isprintable(self):
        return self.data.isprintable()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__((self.data.ljust)(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    maketrans = str.maketrans

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        if isinstance(old, UserString):
            old = old.data
        if isinstance(new, UserString):
            new = new.data
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=_sys.maxsize):
        if isinstance(sub, UserString):
            sub = sub.data
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=_sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__((self.data.rjust)(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=False):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=_sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__((self.data.translate)(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))