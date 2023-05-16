# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\zone_director_venue_proxy.py
# Compiled at: 2019-09-05 16:33:14
# Size of source mod 2**32: 1084 bytes
from zone_director import ZoneDirectorBase
import services

class ZoneDirectorVenueProxy(ZoneDirectorBase):

    def __new__--- This code section failed: ---

 L.  14         0  LOAD_FAST                'proxy'
                2  POP_JUMP_IF_TRUE     38  'to 38'

 L.  15         4  LOAD_GLOBAL              super
                6  CALL_FUNCTION_0       0  '0 positional arguments'
                8  LOAD_ATTR                __new__
               10  STORE_FAST               'new'

 L.  16        12  LOAD_FAST                'new'
               14  LOAD_GLOBAL              object
               16  LOAD_ATTR                __new__
               18  COMPARE_OP               is
               20  POP_JUMP_IF_FALSE    30  'to 30'

 L.  17        22  LOAD_FAST                'new'
               24  LOAD_FAST                'cls'
               26  CALL_FUNCTION_1       1  '1 positional argument'
               28  RETURN_VALUE     
             30_0  COME_FROM            20  '20'

 L.  18        30  LOAD_GLOBAL              TypeError
               32  LOAD_STR                 'super() of _ZoneDirectorVenueProxy cannot override __new__'
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  RAISE_VARARGS_1       1  'exception instance'
             38_0  COME_FROM             2  '2'

 L.  19        38  LOAD_GLOBAL              services
               40  LOAD_METHOD              venue_service
               42  CALL_METHOD_0         0  '0 positional arguments'
               44  LOAD_ATTR                active_venue
               46  LOAD_METHOD              zone_director
               48  CALL_METHOD_0         0  '0 positional arguments'
               50  STORE_FAST               'venue_zone_director'

 L.  20        52  LOAD_BUILD_CLASS 
               54  LOAD_CODE                <code_object _ZoneDirectorVenueProxy>
               56  LOAD_STR                 '_ZoneDirectorVenueProxy'
               58  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               60  LOAD_STR                 '_ZoneDirectorVenueProxy'
               62  LOAD_FAST                'cls'
               64  LOAD_GLOBAL              type
               66  LOAD_FAST                'venue_zone_director'
               68  CALL_FUNCTION_1       1  '1 positional argument'
               70  CALL_FUNCTION_4       4  '4 positional arguments'
               72  STORE_FAST               '_ZoneDirectorVenueProxy'

 L.  25        74  LOAD_FAST                '_ZoneDirectorVenueProxy'
               76  LOAD_FAST                'args'
               78  LOAD_STR                 'proxy'
               80  LOAD_CONST               False
               82  BUILD_MAP_1           1 
               84  LOAD_FAST                'kwargs'
               86  BUILD_MAP_UNPACK_WITH_CALL_2     2 
               88  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               90  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `CALL_FUNCTION_4' instruction at offset 70

    INSTANCE_SUBCLASSES_ONLY = True