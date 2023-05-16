# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\enum_lib.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 35462 bytes
import sys
from types import MappingProxyType, DynamicClassAttribute
try:
    from _collections import OrderedDict
except ImportError:
    from collections import OrderedDict

__all__ = ["'EnumMeta'", 
 "'Enum'", "'IntEnum'", "'Flag'", "'IntFlag'", 
 "'auto'", 
 "'unique'"]

def _is_descriptor(obj):
    return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')


def _is_dunder(name):
    return name[:2] == name[-2:] == '__' and name[2:3] != '_' and name[-3:-2] != '_' and len(name) > 4


def _is_sunder(name):
    return name[0] == name[-1] == '_' and name[1:2] != '_' and name[-2:-1] != '_' and len(name) > 2


def _make_class_unpicklable(cls):

    def _break_on_call_reduce(self, proto):
        raise TypeError('%r cannot be pickled' % self)

    cls.__reduce_ex__ = _break_on_call_reduce
    cls.__module__ = '<unknown>'


_auto_null = object()

class auto:
    value = _auto_null


class _EnumDict(dict):

    def __init__(self):
        super().__init__()
        self._member_names = []
        self._last_values = []
        self._ignore = []

    def __setitem__(self, key, value):
        if _is_sunder(key):
            if key not in ('_order_', '_create_pseudo_member_', '_generate_next_value_',
                           '_missing_', '_ignore_'):
                raise ValueError('_names_ are reserved for future Enum use')
            if key == '_generate_next_value_':
                setattr(self, '_generate_next_value', value)
            else:
                if key == '_ignore_':
                    if isinstance(value, str):
                        value = value.replace(',', ' ').split()
                    else:
                        value = list(value)
                    self._ignore = value
                    already = set(value) & set(self._member_names)
                    if already:
                        raise ValueError('_ignore_ cannot specify already set names: %r' % (already,))
        else:
            if _is_dunder(key):
                if key == '__order__':
                    key = '_order_'
            else:
                if key in self._member_names:
                    raise TypeError('Attempted to reuse key: %r' % key)
                else:
                    if key in self._ignore:
                        pass
                    else:
                        if not _is_descriptor(value):
                            if key in self:
                                raise TypeError('%r already defined as: %r' % (key, self[key]))
                            if isinstance(value, auto):
                                if value.value == _auto_null:
                                    value.value = self._generate_next_value(key, 1, len(self._member_names), self._last_values[:])
                                value = value.value
                            self._member_names.append(key)
                            self._last_values.append(value)
                        super().__setitem__(key, value)


Enum = None

class EnumMeta(type):

    @classmethod
    def __prepare__(metacls, cls, bases):
        enum_dict = _EnumDict()
        member_type, first_enum = metacls._get_mixins_(bases)
        if first_enum is not None:
            enum_dict['_generate_next_value_'] = getattr(first_enum, '_generate_next_value_', None)
        return enum_dict

    def __new__--- This code section failed: ---

 L. 141         0  LOAD_DEREF               'classdict'
                2  LOAD_METHOD              setdefault
                4  LOAD_STR                 '_ignore_'
                6  BUILD_LIST_0          0 
                8  CALL_METHOD_2         2  '2 positional arguments'
               10  LOAD_METHOD              append
               12  LOAD_STR                 '_ignore_'
               14  CALL_METHOD_1         1  '1 positional argument'
               16  POP_TOP          

 L. 142        18  LOAD_DEREF               'classdict'
               20  LOAD_STR                 '_ignore_'
               22  BINARY_SUBSCR    
               24  STORE_FAST               'ignore'

 L. 143        26  SETUP_LOOP           52  'to 52'
               28  LOAD_FAST                'ignore'
               30  GET_ITER         
               32  FOR_ITER             50  'to 50'
               34  STORE_FAST               'key'

 L. 144        36  LOAD_DEREF               'classdict'
               38  LOAD_METHOD              pop
               40  LOAD_FAST                'key'
               42  LOAD_CONST               None
               44  CALL_METHOD_2         2  '2 positional arguments'
               46  POP_TOP          
               48  JUMP_BACK            32  'to 32'
               50  POP_BLOCK        
             52_0  COME_FROM_LOOP       26  '26'

 L. 145        52  LOAD_FAST                'metacls'
               54  LOAD_METHOD              _get_mixins_
               56  LOAD_FAST                'bases'
               58  CALL_METHOD_1         1  '1 positional argument'
               60  UNPACK_SEQUENCE_2     2 
               62  STORE_DEREF              'member_type'
               64  STORE_FAST               'first_enum'

 L. 146        66  LOAD_FAST                'metacls'
               68  LOAD_METHOD              _find_new_
               70  LOAD_DEREF               'classdict'
               72  LOAD_DEREF               'member_type'

 L. 147        74  LOAD_FAST                'first_enum'
               76  CALL_METHOD_3         3  '3 positional arguments'
               78  UNPACK_SEQUENCE_3     3 
               80  STORE_FAST               '__new__'
               82  STORE_FAST               'save_new'
               84  STORE_FAST               'use_args'

 L. 151        86  LOAD_CLOSURE             'classdict'
               88  BUILD_TUPLE_1         1 
               90  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               92  LOAD_STR                 'EnumMeta.__new__.<locals>.<dictcomp>'
               94  MAKE_FUNCTION_8          'closure'
               96  LOAD_DEREF               'classdict'
               98  LOAD_ATTR                _member_names
              100  GET_ITER         
              102  CALL_FUNCTION_1       1  '1 positional argument'
              104  STORE_FAST               'enum_members'

 L. 152       106  SETUP_LOOP          128  'to 128'
              108  LOAD_DEREF               'classdict'
              110  LOAD_ATTR                _member_names
              112  GET_ITER         
              114  FOR_ITER            126  'to 126'
              116  STORE_FAST               'name'

 L. 153       118  LOAD_DEREF               'classdict'
              120  LOAD_FAST                'name'
              122  DELETE_SUBSCR    
              124  JUMP_BACK           114  'to 114'
              126  POP_BLOCK        
            128_0  COME_FROM_LOOP      106  '106'

 L. 156       128  LOAD_DEREF               'classdict'
              130  LOAD_METHOD              pop
              132  LOAD_STR                 '_order_'
              134  LOAD_CONST               None
              136  CALL_METHOD_2         2  '2 positional arguments'
              138  STORE_FAST               '_order_'

 L. 159       140  LOAD_GLOBAL              set
              142  LOAD_FAST                'enum_members'
              144  CALL_FUNCTION_1       1  '1 positional argument'
              146  LOAD_STR                 'mro'
              148  BUILD_SET_1           1 
              150  BINARY_AND       
              152  STORE_FAST               'invalid_names'

 L. 160       154  LOAD_FAST                'invalid_names'
              156  POP_JUMP_IF_FALSE   178  'to 178'

 L. 161       158  LOAD_GLOBAL              ValueError
              160  LOAD_STR                 'Invalid enum member name: {0}'
              162  LOAD_METHOD              format

 L. 162       164  LOAD_STR                 ','
              166  LOAD_METHOD              join
              168  LOAD_FAST                'invalid_names'
              170  CALL_METHOD_1         1  '1 positional argument'
              172  CALL_METHOD_1         1  '1 positional argument'
              174  CALL_FUNCTION_1       1  '1 positional argument'
              176  RAISE_VARARGS_1       1  'exception instance'
            178_0  COME_FROM           156  '156'

 L. 165       178  LOAD_STR                 '__doc__'
              180  LOAD_DEREF               'classdict'
              182  COMPARE_OP               not-in
              184  POP_JUMP_IF_FALSE   194  'to 194'

 L. 166       186  LOAD_STR                 'An enumeration.'
              188  LOAD_DEREF               'classdict'
              190  LOAD_STR                 '__doc__'
              192  STORE_SUBSCR     
            194_0  COME_FROM           184  '184'

 L. 169       194  LOAD_GLOBAL              super
              196  CALL_FUNCTION_0       0  '0 positional arguments'
              198  LOAD_METHOD              __new__
              200  LOAD_FAST                'metacls'
              202  LOAD_FAST                'cls'
              204  LOAD_FAST                'bases'
              206  LOAD_DEREF               'classdict'
              208  CALL_METHOD_4         4  '4 positional arguments'
              210  STORE_FAST               'enum_class'

 L. 170       212  BUILD_LIST_0          0 
              214  LOAD_FAST                'enum_class'
              216  STORE_ATTR               _member_names_

 L. 171       218  LOAD_GLOBAL              OrderedDict
              220  CALL_FUNCTION_0       0  '0 positional arguments'
              222  LOAD_FAST                'enum_class'
              224  STORE_ATTR               _member_map_

 L. 172       226  LOAD_DEREF               'member_type'
              228  LOAD_FAST                'enum_class'
              230  STORE_ATTR               _member_type_

 L. 176       232  LOAD_SETCOMP             '<code_object <setcomp>>'
              234  LOAD_STR                 'EnumMeta.__new__.<locals>.<setcomp>'
              236  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              238  LOAD_FAST                'enum_class'
              240  LOAD_METHOD              mro
              242  CALL_METHOD_0         0  '0 positional arguments'
              244  GET_ITER         
              246  CALL_FUNCTION_1       1  '1 positional argument'
              248  STORE_FAST               'base_attributes'

 L. 179       250  BUILD_MAP_0           0 
              252  LOAD_FAST                'enum_class'
              254  STORE_ATTR               _value2member_map_

 L. 191       256  LOAD_STR                 '__reduce_ex__'
              258  LOAD_DEREF               'classdict'
              260  COMPARE_OP               not-in
          262_264  POP_JUMP_IF_FALSE   312  'to 312'

 L. 192       266  LOAD_DEREF               'member_type'
              268  LOAD_GLOBAL              object
              270  COMPARE_OP               is-not
          272_274  POP_JUMP_IF_FALSE   312  'to 312'

 L. 193       276  LOAD_CONST               ('__getnewargs_ex__', '__getnewargs__', '__reduce_ex__', '__reduce__')
              278  STORE_FAST               'methods'

 L. 195       280  LOAD_GLOBAL              any
              282  LOAD_CLOSURE             'member_type'
              284  BUILD_TUPLE_1         1 
              286  LOAD_GENEXPR             '<code_object <genexpr>>'
              288  LOAD_STR                 'EnumMeta.__new__.<locals>.<genexpr>'
              290  MAKE_FUNCTION_8          'closure'
              292  LOAD_FAST                'methods'
              294  GET_ITER         
              296  CALL_FUNCTION_1       1  '1 positional argument'
              298  CALL_FUNCTION_1       1  '1 positional argument'
          300_302  POP_JUMP_IF_TRUE    312  'to 312'

 L. 196       304  LOAD_GLOBAL              _make_class_unpicklable
              306  LOAD_FAST                'enum_class'
              308  CALL_FUNCTION_1       1  '1 positional argument'
              310  POP_TOP          
            312_0  COME_FROM           300  '300'
            312_1  COME_FROM           272  '272'
            312_2  COME_FROM           262  '262'

 L. 202   312_314  SETUP_LOOP          626  'to 626'
              316  LOAD_DEREF               'classdict'
              318  LOAD_ATTR                _member_names
              320  GET_ITER         
          322_324  FOR_ITER            624  'to 624'
              326  STORE_FAST               'member_name'

 L. 203       328  LOAD_FAST                'enum_members'
              330  LOAD_FAST                'member_name'
              332  BINARY_SUBSCR    
              334  STORE_FAST               'value'

 L. 204       336  LOAD_GLOBAL              isinstance
              338  LOAD_FAST                'value'
              340  LOAD_GLOBAL              tuple
              342  CALL_FUNCTION_2       2  '2 positional arguments'
          344_346  POP_JUMP_IF_TRUE    356  'to 356'

 L. 205       348  LOAD_FAST                'value'
              350  BUILD_TUPLE_1         1 
              352  STORE_FAST               'args'
              354  JUMP_FORWARD        360  'to 360'
            356_0  COME_FROM           344  '344'

 L. 207       356  LOAD_FAST                'value'
              358  STORE_FAST               'args'
            360_0  COME_FROM           354  '354'

 L. 208       360  LOAD_DEREF               'member_type'
              362  LOAD_GLOBAL              tuple
              364  COMPARE_OP               is
          366_368  POP_JUMP_IF_FALSE   376  'to 376'

 L. 209       370  LOAD_FAST                'args'
              372  BUILD_TUPLE_1         1 
              374  STORE_FAST               'args'
            376_0  COME_FROM           366  '366'

 L. 210       376  LOAD_FAST                'use_args'
          378_380  POP_JUMP_IF_TRUE    410  'to 410'

 L. 211       382  LOAD_FAST                '__new__'
              384  LOAD_FAST                'enum_class'
              386  CALL_FUNCTION_1       1  '1 positional argument'
              388  STORE_FAST               'enum_member'

 L. 212       390  LOAD_GLOBAL              hasattr
              392  LOAD_FAST                'enum_member'
              394  LOAD_STR                 '_value_'
              396  CALL_FUNCTION_2       2  '2 positional arguments'
          398_400  POP_JUMP_IF_TRUE    464  'to 464'

 L. 213       402  LOAD_FAST                'value'
              404  LOAD_FAST                'enum_member'
              406  STORE_ATTR               _value_
              408  JUMP_FORWARD        464  'to 464'
            410_0  COME_FROM           378  '378'

 L. 215       410  LOAD_FAST                '__new__'
              412  LOAD_FAST                'enum_class'
              414  BUILD_TUPLE_1         1 
              416  LOAD_FAST                'args'
              418  BUILD_TUPLE_UNPACK_WITH_CALL_2     2 
              420  CALL_FUNCTION_EX      0  'positional arguments only'
              422  STORE_FAST               'enum_member'

 L. 216       424  LOAD_GLOBAL              hasattr
              426  LOAD_FAST                'enum_member'
              428  LOAD_STR                 '_value_'
              430  CALL_FUNCTION_2       2  '2 positional arguments'
          432_434  POP_JUMP_IF_TRUE    464  'to 464'

 L. 217       436  LOAD_DEREF               'member_type'
              438  LOAD_GLOBAL              object
              440  COMPARE_OP               is
          442_444  POP_JUMP_IF_FALSE   454  'to 454'

 L. 218       446  LOAD_FAST                'value'
              448  LOAD_FAST                'enum_member'
              450  STORE_ATTR               _value_
              452  JUMP_FORWARD        464  'to 464'
            454_0  COME_FROM           442  '442'

 L. 220       454  LOAD_DEREF               'member_type'
              456  LOAD_FAST                'args'
              458  CALL_FUNCTION_EX      0  'positional arguments only'
              460  LOAD_FAST                'enum_member'
              462  STORE_ATTR               _value_
            464_0  COME_FROM           452  '452'
            464_1  COME_FROM           432  '432'
            464_2  COME_FROM           408  '408'
            464_3  COME_FROM           398  '398'

 L. 221       464  LOAD_FAST                'enum_member'
              466  LOAD_ATTR                _value_
              468  STORE_FAST               'value'

 L. 222       470  LOAD_FAST                'member_name'
              472  LOAD_FAST                'enum_member'
              474  STORE_ATTR               _name_

 L. 223       476  LOAD_FAST                'enum_class'
              478  LOAD_FAST                'enum_member'
              480  STORE_ATTR               __objclass__

 L. 224       482  LOAD_FAST                'enum_member'
              484  LOAD_ATTR                __init__
              486  LOAD_FAST                'args'
              488  CALL_FUNCTION_EX      0  'positional arguments only'
              490  POP_TOP          

 L. 227       492  SETUP_LOOP          550  'to 550'
              494  LOAD_FAST                'enum_class'
              496  LOAD_ATTR                _member_map_
              498  LOAD_METHOD              items
              500  CALL_METHOD_0         0  '0 positional arguments'
              502  GET_ITER         
            504_0  COME_FROM           522  '522'
              504  FOR_ITER            536  'to 536'
              506  UNPACK_SEQUENCE_2     2 
              508  STORE_FAST               'name'
              510  STORE_FAST               'canonical_member'

 L. 228       512  LOAD_FAST                'canonical_member'
              514  LOAD_ATTR                _value_
              516  LOAD_FAST                'enum_member'
              518  LOAD_ATTR                _value_
              520  COMPARE_OP               ==
          522_524  POP_JUMP_IF_FALSE   504  'to 504'

 L. 229       526  LOAD_FAST                'canonical_member'
              528  STORE_FAST               'enum_member'

 L. 230       530  BREAK_LOOP       
          532_534  JUMP_BACK           504  'to 504'
              536  POP_BLOCK        

 L. 233       538  LOAD_FAST                'enum_class'
              540  LOAD_ATTR                _member_names_
              542  LOAD_METHOD              append
              544  LOAD_FAST                'member_name'
              546  CALL_METHOD_1         1  '1 positional argument'
              548  POP_TOP          
            550_0  COME_FROM_LOOP      492  '492'

 L. 236       550  LOAD_FAST                'member_name'
              552  LOAD_FAST                'base_attributes'
              554  COMPARE_OP               not-in
          556_558  POP_JUMP_IF_FALSE   572  'to 572'

 L. 237       560  LOAD_GLOBAL              setattr
              562  LOAD_FAST                'enum_class'
              564  LOAD_FAST                'member_name'
              566  LOAD_FAST                'enum_member'
              568  CALL_FUNCTION_3       3  '3 positional arguments'
              570  POP_TOP          
            572_0  COME_FROM           556  '556'

 L. 239       572  LOAD_FAST                'enum_member'
              574  LOAD_FAST                'enum_class'
              576  LOAD_ATTR                _member_map_
              578  LOAD_FAST                'member_name'
              580  STORE_SUBSCR     

 L. 240       582  SETUP_EXCEPT        598  'to 598'

 L. 244       584  LOAD_FAST                'enum_member'
              586  LOAD_FAST                'enum_class'
              588  LOAD_ATTR                _value2member_map_
              590  LOAD_FAST                'value'
              592  STORE_SUBSCR     
              594  POP_BLOCK        
              596  JUMP_BACK           322  'to 322'
            598_0  COME_FROM_EXCEPT    582  '582'

 L. 245       598  DUP_TOP          
              600  LOAD_GLOBAL              TypeError
              602  COMPARE_OP               exception-match
          604_606  POP_JUMP_IF_FALSE   618  'to 618'
              608  POP_TOP          
              610  POP_TOP          
              612  POP_TOP          

 L. 246       614  POP_EXCEPT       
              616  JUMP_BACK           322  'to 322'
            618_0  COME_FROM           604  '604'
              618  END_FINALLY      
          620_622  JUMP_BACK           322  'to 322'
              624  POP_BLOCK        
            626_0  COME_FROM_LOOP      312  '312'

 L. 250       626  SETUP_LOOP          708  'to 708'
              628  LOAD_CONST               ('__repr__', '__str__', '__format__', '__reduce_ex__')
              630  GET_ITER         
            632_0  COME_FROM           686  '686'
            632_1  COME_FROM           676  '676'
              632  FOR_ITER            706  'to 706'
              634  STORE_FAST               'name'

 L. 251       636  LOAD_GLOBAL              getattr
              638  LOAD_FAST                'enum_class'
              640  LOAD_FAST                'name'
              642  CALL_FUNCTION_2       2  '2 positional arguments'
              644  STORE_FAST               'class_method'

 L. 252       646  LOAD_GLOBAL              getattr
              648  LOAD_DEREF               'member_type'
              650  LOAD_FAST                'name'
              652  LOAD_CONST               None
              654  CALL_FUNCTION_3       3  '3 positional arguments'
              656  STORE_FAST               'obj_method'

 L. 253       658  LOAD_GLOBAL              getattr
              660  LOAD_FAST                'first_enum'
              662  LOAD_FAST                'name'
              664  LOAD_CONST               None
              666  CALL_FUNCTION_3       3  '3 positional arguments'
              668  STORE_FAST               'enum_method'

 L. 254       670  LOAD_FAST                'obj_method'
              672  LOAD_CONST               None
              674  COMPARE_OP               is-not
          676_678  POP_JUMP_IF_FALSE   632  'to 632'
              680  LOAD_FAST                'obj_method'
              682  LOAD_FAST                'class_method'
              684  COMPARE_OP               is
          686_688  POP_JUMP_IF_FALSE   632  'to 632'

 L. 255       690  LOAD_GLOBAL              setattr
              692  LOAD_FAST                'enum_class'
              694  LOAD_FAST                'name'
              696  LOAD_FAST                'enum_method'
              698  CALL_FUNCTION_3       3  '3 positional arguments'
              700  POP_TOP          
          702_704  JUMP_BACK           632  'to 632'
              706  POP_BLOCK        
            708_0  COME_FROM_LOOP      626  '626'

 L. 259       708  LOAD_GLOBAL              Enum
              710  LOAD_CONST               None
              712  COMPARE_OP               is-not
          714_716  POP_JUMP_IF_FALSE   738  'to 738'

 L. 262       718  LOAD_FAST                'save_new'
          720_722  POP_JUMP_IF_FALSE   730  'to 730'

 L. 263       724  LOAD_FAST                '__new__'
              726  LOAD_FAST                'enum_class'
              728  STORE_ATTR               __new_member__
            730_0  COME_FROM           720  '720'

 L. 264       730  LOAD_GLOBAL              Enum
              732  LOAD_ATTR                __new__
              734  LOAD_FAST                'enum_class'
              736  STORE_ATTR               __new__
            738_0  COME_FROM           714  '714'

 L. 267       738  LOAD_FAST                '_order_'
              740  LOAD_CONST               None
              742  COMPARE_OP               is-not
          744_746  POP_JUMP_IF_FALSE   796  'to 796'

 L. 268       748  LOAD_GLOBAL              isinstance
              750  LOAD_FAST                '_order_'
              752  LOAD_GLOBAL              str
              754  CALL_FUNCTION_2       2  '2 positional arguments'
          756_758  POP_JUMP_IF_FALSE   776  'to 776'

 L. 269       760  LOAD_FAST                '_order_'
              762  LOAD_METHOD              replace
              764  LOAD_STR                 ','
              766  LOAD_STR                 ' '
              768  CALL_METHOD_2         2  '2 positional arguments'
              770  LOAD_METHOD              split
              772  CALL_METHOD_0         0  '0 positional arguments'
              774  STORE_FAST               '_order_'
            776_0  COME_FROM           756  '756'

 L. 270       776  LOAD_FAST                '_order_'
              778  LOAD_FAST                'enum_class'
              780  LOAD_ATTR                _member_names_
              782  COMPARE_OP               !=
          784_786  POP_JUMP_IF_FALSE   796  'to 796'

 L. 271       788  LOAD_GLOBAL              TypeError
              790  LOAD_STR                 'member order does not match _order_'
              792  CALL_FUNCTION_1       1  '1 positional argument'
              794  RAISE_VARARGS_1       1  'exception instance'
            796_0  COME_FROM           784  '784'
            796_1  COME_FROM           744  '744'

 L. 273       796  LOAD_FAST                'enum_class'
              798  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 90

    def __bool__(self):
        return True

    def __call__(cls, value, names=None, *, module=None, qualname=None, type=None, start=1):
        if names is None:
            return cls.__new__(cls, value)
        return cls._create_(value, names, module=module, qualname=qualname, type=type, start=start)

    def __contains__(cls, member):
        if not isinstance(member, Enum):
            import warnings
            warnings.warn'using non-Enums in containment checks will raise TypeError in Python 3.8'DeprecationWarning2
        return isinstance(member, cls) and member._name_ in cls._member_map_

    def __delattr__(cls, attr):
        if attr in cls._member_map_:
            raise AttributeError('%s: cannot delete Enum member.' % cls.__name__)
        super().__delattr__(attr)

    def __dir__(self):
        return [
         '__class__', '__doc__', '__members__', '__module__'] + self._member_names_

    def __getattr__(cls, name):
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            return cls._member_map_[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        return (cls._member_map_[name] for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)

    @property
    def __members__(cls):
        return MappingProxyType(cls._member_map_)

    def __repr__(cls):
        return '<enum %r>' % cls.__name__

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        member_map = cls.__dict__.get('_member_map_', {})
        if name in member_map:
            raise AttributeError('Cannot reassign members.')
        super().__setattr__(name, value)

    def _create_(cls, class_name, names, *, module=None, qualname=None, type=None, start=1):
        metacls = cls.__class__
        bases = (cls,) if type is None else (type, cls)
        _, first_enum = cls._get_mixins_(bases)
        classdict = metacls.__prepare__(class_name, bases)
        if isinstance(names, str):
            names = names.replace(',', ' ').split()
        elif isinstance(names, (tuple, list)):
            if names:
                if isinstance(names[0], str):
                    original_names, names = names, []
                    last_values = []
                    for count, name in enumerate(original_names):
                        value = first_enum._generate_next_value_(name, start, count, last_values[:])
                        last_values.append(value)
                        names.append((name, value))

            else:
                for item in names:
                    if isinstance(item, str):
                        member_name, member_value = item, names[item]
                    else:
                        member_name, member_value = item
                    classdict[member_name] = member_value

                enum_class = metacls.__new__(metacls, class_name, bases, classdict)
                if module is None:
                    try:
                        module = sys._getframe(2).f_globals['__name__']
                    except (AttributeError, ValueError) as exc:
                        try:
                            pass
                        finally:
                            exc = None
                            del exc

            if module is None:
                _make_class_unpicklable(enum_class)
        else:
            enum_class.__module__ = module
        if qualname is not None:
            enum_class.__qualname__ = qualname
        return enum_class

    @staticmethod
    def _get_mixins_(bases):
        if not bases:
            return (
             object, Enum)
        else:
            member_type = first_enum = None
            for base in bases:
                if base is not Enum and issubclass(base, Enum) and base._member_names_:
                    raise TypeError('Cannot extend enumerations')

            if not issubclass(base, Enum):
                raise TypeError('new enumerations must be created as `ClassName([mixin_type,] enum_type)`')
            if not issubclass(bases[0], Enum):
                member_type = bases[0]
                first_enum = bases[-1]
            else:
                for base in bases[0].__mro__:
                    if issubclass(base, Enum):
                        if first_enum is None:
                            first_enum = base
                        elif member_type is None:
                            member_type = base

        return (
         member_type, first_enum)

    @staticmethod
    def _find_new_(classdict, member_type, first_enum):
        __new__ = classdict.get('__new__', None)
        save_new = __new__ is not None
        if __new__ is None:
            for method in ('__new_member__', '__new__'):
                for possible in (member_type, first_enum):
                    target = getattr(possible, method, None)
                    if target not in {
                     None,
                     (None).__new__,
                     object.__new__,
                     Enum.__new__}:
                        __new__ = target
                        break

                if __new__ is not None:
                    break
            else:
                __new__ = object.__new__

        elif __new__ is object.__new__:
            use_args = False
        else:
            use_args = True
        return (__new__, save_new, use_args)


class Enum(metaclass=EnumMeta):

    def __new__(cls, value):
        if type(value) is cls:
            return value
        try:
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        except TypeError:
            for member in cls._member_map_.values():
                if member._value_ == value:
                    return member

        return cls._missing_(value)

    def _generate_next_value_(name, start, count, last_values):
        for last_value in reversed(last_values):
            try:
                return last_value + 1
            except TypeError:
                pass

        else:
            return start

    @classmethod
    def _missing_(cls, value):
        raise ValueError('%r is not a valid %s' % (value, cls.__name__))

    def __repr__(self):
        return '<%s.%s: %r>' % (
         self.__class__.__name__, self._name_, self._value_)

    def __str__(self):
        return '%s.%s' % (self.__class__.__name__, self._name_)

    def __dir__(self):
        added_behavior = [m for cls in self.__class__.mro() if m[0] != '_' if m not in self._member_map_ for m in iter((cls.__dict__)) if m not in self._member_map_]
        return [
         '__class__', '__doc__', '__module__'] + added_behavior

    def __format__(self, format_spec):
        if self._member_type_ is object:
            cls = str
            val = str(self)
        else:
            cls = self._member_type_
            val = self._value_
        return cls.__format__(val, format_spec)

    def __hash__(self):
        return hash(self._name_)

    def __reduce_ex__(self, proto):
        return (
         self.__class__, (self._value_,))

    @DynamicClassAttribute
    def name(self):
        return self._name_

    @DynamicClassAttribute
    def value(self):
        return self._value_

    @classmethod
    def _convert(cls, name, module, filter, source=None):
        module_globals = vars(sys.modules[module])
        if source:
            source = vars(source)
        else:
            source = module_globals
        members = [(name, source[name]) for name in source.keys() if filter(name)]
        try:
            members.sort(key=(lambda t: (t[1], t[0])))
        except TypeError:
            members.sort(key=(lambda t: t[0]))

        cls = cls(name, members, module=module)
        cls.__reduce_ex__ = _reduce_ex_by_name
        module_globals.update(cls.__members__)
        module_globals[name] = cls
        return cls


class IntEnum(int, Enum):
    pass


def _reduce_ex_by_name(self, proto):
    return self.name


class Flag(Enum):

    def _generate_next_value_(name, start, count, last_values):
        if not count:
            if start is not None:
                return start
            return 1
        for last_value in reversed(last_values):
            try:
                high_bit = _high_bit(last_value)
                break
            except Exception:
                raise TypeError('Invalid Flag value: %r' % last_value) from None

        return 2 ** (high_bit + 1)

    @classmethod
    def _missing_(cls, value):
        original_value = value
        if value < 0:
            value = ~value
        possible_member = cls._create_pseudo_member_(value)
        if original_value < 0:
            possible_member = ~possible_member
        return possible_member

    @classmethod
    def _create_pseudo_member_(cls, value):
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            _, extra_flags = _decompose(cls, value)
            if extra_flags:
                raise ValueError('%r is not a valid %s' % (value, cls.__name__))
            pseudo_member = object.__new__(cls)
            pseudo_member._name_ = None
            pseudo_member._value_ = value
            pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)
        return pseudo_member

    def __contains__(self, other):
        if not isinstance(other, self.__class__):
            import warnings
            warnings.warn'using non-Flags in containment checks will raise TypeError in Python 3.8'DeprecationWarning2
            return False
        return other._value_ & self._value_ == other._value_

    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return '<%s.%s: %r>' % (cls.__name__, self._name_, self._value_)
        members, uncovered = _decompose(cls, self._value_)
        return '<%s.%s: %r>' % (
         cls.__name__,
         '|'.join([str(m._name_ or m._value_) for m in members]),
         self._value_)

    def __str__(self):
        cls = self.__class__
        if self._name_ is not None:
            return '%s.%s' % (cls.__name__, self._name_)
        members, uncovered = _decompose(cls, self._value_)
        if len(members) == 1:
            if members[0]._name_ is None:
                return '%s.%r' % (cls.__name__, members[0]._value_)
        return '%s.%s' % (
         cls.__name__,
         '|'.join([str(m._name_ or m._value_) for m in members]))

    def __bool__(self):
        return bool(self._value_)

    def __or__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ | other._value_)

    def __and__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ & other._value_)

    def __xor__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(self._value_ ^ other._value_)

    def __invert__(self):
        members, uncovered = _decompose(self.__class__, self._value_)
        inverted = self.__class__(0)
        for m in self.__class__:
            if m not in members:
                inverted = m._value_ & self._value_ or inverted | m

        return self.__class__(inverted)


class IntFlag(int, Flag):

    @classmethod
    def _missing_(cls, value):
        if not isinstance(value, int):
            raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        new_member = cls._create_pseudo_member_(value)
        return new_member

    @classmethod
    def _create_pseudo_member_(cls, value):
        pseudo_member = cls._value2member_map_.get(value, None)
        if pseudo_member is None:
            need_to_create = [
             value]
            _, extra_flags = _decompose(cls, value)
            while extra_flags:
                bit = _high_bit(extra_flags)
                flag_value = 2 ** bit
                if flag_value not in cls._value2member_map_:
                    if flag_value not in need_to_create:
                        need_to_create.append(flag_value)
                if extra_flags == -flag_value:
                    extra_flags = 0
                else:
                    extra_flags ^= flag_value

            for value in reversed(need_to_create):
                pseudo_member = int.__new__(cls, value)
                pseudo_member._name_ = None
                pseudo_member._value_ = value
                pseudo_member = cls._value2member_map_.setdefault(value, pseudo_member)

        return pseudo_member

    def __or__(self, other):
        if not isinstance(other, (self.__class__, int)):
            return NotImplemented
        result = self.__class__(self._value_ | self.__class__(other)._value_)
        return result

    def __and__(self, other):
        if not isinstance(other, (self.__class__, int)):
            return NotImplemented
        return self.__class__(self._value_ & self.__class__(other)._value_)

    def __xor__(self, other):
        if not isinstance(other, (self.__class__, int)):
            return NotImplemented
        return self.__class__(self._value_ ^ self.__class__(other)._value_)

    __ror__ = __or__
    __rand__ = __and__
    __rxor__ = __xor__

    def __invert__(self):
        result = self.__class__(~self._value_)
        return result


def _high_bit(value):
    return value.bit_length() - 1


def unique(enumeration):
    duplicates = []
    for name, member in enumeration.__members__.items():
        if name != member.name:
            duplicates.append((name, member.name))

    if duplicates:
        alias_details = ', '.join(['%s -> %s' % (alias, name) for alias, name in duplicates])
        raise ValueError('duplicate values found in %r: %s' % (
         enumeration, alias_details))
    return enumeration


def _decompose(flag, value):
    not_covered = value
    negative = value < 0
    if negative:
        flags_to_check = [(m, v) for v, m in list(flag._value2member_map_.items()) if m.name is not None]
    else:
        flags_to_check = [(m, v) for v, m in list(flag._value2member_map_.items()) if not m.name is not None if _power_of_two(v)]
    members = []
    for member, member_value in flags_to_check:
        if member_value and member_value & value == member_value:
            members.append(member)
            not_covered &= ~member_value

    if not members:
        if value in flag._value2member_map_:
            members.append(flag._value2member_map_[value])
    members.sort(key=(lambda m: m._value_), reverse=True)
    if len(members) > 1:
        if members[0].value == value:
            members.pop(0)
    return (
     members, not_covered)


def _power_of_two(value):
    if value < 1:
        return False
    return value == 2 ** _high_bit(value)