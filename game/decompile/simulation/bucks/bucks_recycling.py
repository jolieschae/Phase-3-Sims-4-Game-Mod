# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_recycling.py
# Compiled at: 2020-02-06 17:26:04
# Size of source mod 2**32: 2359 bytes
from sims4.tuning.geometric import TunableCurve
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableRange, TunableTuple
from bucks.bucks_enums import BucksType

class BucksRecycling:
    RECYCLING_VALUE = TunableMapping(description='\n        Maps a buck type the parameters controlling object recycling value.\n        Recycling Formula:\n        Total = Base Value * Price Response Curve (Object Current Simoleon Value) * \n            Object Recycle Value (Buck Type)\n        ',
      key_type=TunableEnumEntry(tunable_type=BucksType,
      default=(BucksType.INVALID),
      invalid_enums=(BucksType.INVALID),
      pack_safe=True),
      key_name='Bucks Type',
      value_type=TunableTuple(description='\n            Recycling parameters for this buck type.\n            ',
      base_value=TunableRange(description='\n                Base multiplier for this buck type\n                ',
      tunable_type=float,
      default=1.0,
      minimum=0.0),
      price_response_curve=TunableCurve(description='\n                Modulate the base value by the objects Simoleon value.\n                ',
      x_axis_name='Object Price',
      y_axis_name='Base Multiplier')),
      value_name='Recycled Value')

    @classmethod
    def get_recycling_value_for_object--- This code section failed: ---

 L.  53         0  LOAD_FAST                'obj'
                2  LOAD_CONST               None
                4  COMPARE_OP               is
                6  POP_JUMP_IF_TRUE     36  'to 36'
                8  LOAD_FAST                'obj'
               10  LOAD_ATTR                is_sim
               12  POP_JUMP_IF_TRUE     36  'to 36'
               14  LOAD_FAST                'bucks'
               16  LOAD_FAST                'obj'
               18  LOAD_ATTR                recycling_data
               20  LOAD_ATTR                recycling_values
               22  COMPARE_OP               not-in
               24  POP_JUMP_IF_TRUE     36  'to 36'

 L.  54        26  LOAD_FAST                'bucks'
               28  LOAD_GLOBAL              BucksRecycling
               30  LOAD_ATTR                RECYCLING_VALUE
               32  COMPARE_OP               not-in
               34  POP_JUMP_IF_FALSE    40  'to 40'
             36_0  COME_FROM            24  '24'
             36_1  COME_FROM            12  '12'
             36_2  COME_FROM             6  '6'

 L.  55        36  LOAD_CONST               0
               38  RETURN_VALUE     
             40_0  COME_FROM            34  '34'

 L.  56        40  LOAD_FAST                'obj'
               42  LOAD_ATTR                recycling_data
               44  LOAD_ATTR                recycling_values
               46  LOAD_FAST                'bucks'
               48  BINARY_SUBSCR    
               50  STORE_FAST               'object_recycle_value'

 L.  57        52  LOAD_FAST                'obj'
               54  LOAD_ATTR                current_value
               56  STORE_FAST               'object_value'

 L.  58        58  LOAD_GLOBAL              BucksRecycling
               60  LOAD_ATTR                RECYCLING_VALUE
               62  LOAD_FAST                'bucks'
               64  BINARY_SUBSCR    
               66  STORE_FAST               'params'

 L.  59        68  LOAD_FAST                'params'
               70  LOAD_ATTR                price_response_curve
               72  LOAD_METHOD              get
               74  LOAD_FAST                'object_value'
               76  CALL_METHOD_1         1  '1 positional argument'
               78  STORE_FAST               'recycle_curve_value'

 L.  60        80  LOAD_GLOBAL              int
               82  LOAD_FAST                'params'
               84  LOAD_ATTR                base_value
               86  LOAD_FAST                'recycle_curve_value'
               88  BINARY_MULTIPLY  
               90  LOAD_FAST                'object_recycle_value'
               92  BINARY_MULTIPLY  
               94  LOAD_FAST                'object_value'
               96  BINARY_MULTIPLY  
               98  CALL_FUNCTION_1       1  '1 positional argument'
              100  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 100