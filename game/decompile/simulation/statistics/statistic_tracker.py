# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_tracker.py
# Compiled at: 2020-10-24 18:33:02
# Size of source mod 2**32: 6681 bytes
from protocolbuffers import SimObjectAttributes_pb2 as protocols
import services, sims, sims4.log, statistics.base_statistic_tracker
from sims.sim_info_lod import SimInfoLODLevel
logger = sims4.log.Logger('Statistic')

class StatisticTracker(statistics.base_statistic_tracker.BaseStatisticTracker):
    __slots__ = '_monetary_value_statistics'

    def __init__(self, owner=None):
        super().__init__(owner)
        self._monetary_value_statistics = []

    def save(self):
        self.check_for_unneeded_initial_statistics()
        save_list = []
        if self._statistics is not None:
            for stat_type, stat in self._statistics.items():
                if stat_type.persisted:
                    try:
                        statistic_data = protocols.Statistic()
                        statistic_data.name_hash = stat_type.guid64
                        if stat is not None:
                            statistic_data.value = stat.get_saved_value()
                        else:
                            statistic_data.ClearField('value')
                        save_list.append(statistic_data)
                    except Exception as e:
                        try:
                            logger.exception('Exception {} thrown while trying to save stat {}', e, stat, owner='rez')
                        finally:
                            e = None
                            del e

        return save_list

    def load--- This code section failed: ---

 L.  60       0_2  SETUP_FINALLY       286  'to 286'

 L.  61         4  LOAD_GLOBAL              services
                6  LOAD_METHOD              get_instance_manager
                8  LOAD_GLOBAL              sims4
               10  LOAD_ATTR                resources
               12  LOAD_ATTR                Types
               14  LOAD_ATTR                STATISTIC
               16  CALL_METHOD_1         1  '1 positional argument'
               18  STORE_FAST               'statistics_manager'

 L.  62        20  LOAD_GLOBAL              isinstance
               22  LOAD_FAST                'self'
               24  LOAD_ATTR                _owner
               26  LOAD_GLOBAL              sims
               28  LOAD_ATTR                sim_info
               30  LOAD_ATTR                SimInfo
               32  CALL_FUNCTION_2       2  '2 positional arguments'
               34  POP_JUMP_IF_FALSE    44  'to 44'
               36  LOAD_FAST                'self'
               38  LOAD_ATTR                _owner
               40  LOAD_ATTR                lod
               42  JUMP_FORWARD         46  'to 46'
             44_0  COME_FROM            34  '34'
               44  LOAD_CONST               None
             46_0  COME_FROM            42  '42'
               46  STORE_FAST               'owner_lod'

 L.  63        48  SETUP_LOOP          282  'to 282'
               50  LOAD_FAST                'statistics'
               52  GET_ITER         
             54_0  COME_FROM           152  '152'
               54  FOR_ITER            280  'to 280'
               56  STORE_FAST               'statistics_data'

 L.  66        58  LOAD_FAST                'statistics_manager'
               60  LOAD_METHOD              get
               62  LOAD_FAST                'statistics_data'
               64  LOAD_ATTR                name_hash
               66  CALL_METHOD_1         1  '1 positional argument'
               68  STORE_FAST               'stat_cls'

 L.  68        70  LOAD_FAST                'stat_cls'
               72  LOAD_CONST               None
               74  COMPARE_OP               is-not
            76_78  POP_JUMP_IF_FALSE   264  'to 264'

 L.  69        80  LOAD_FAST                'self'
               82  LOAD_METHOD              _should_add_commodity_from_gallery
               84  LOAD_FAST                'stat_cls'
               86  LOAD_FAST                'skip_load'
               88  CALL_METHOD_2         2  '2 positional arguments'
               90  POP_JUMP_IF_TRUE     94  'to 94'

 L.  72        92  CONTINUE             54  'to 54'
             94_0  COME_FROM            90  '90'

 L.  74        94  LOAD_FAST                'stat_cls'
               96  LOAD_ATTR                persisted
               98  POP_JUMP_IF_TRUE    102  'to 102'

 L.  75       100  CONTINUE             54  'to 54'
            102_0  COME_FROM            98  '98'

 L.  77       102  LOAD_FAST                'self'
              104  LOAD_ATTR                statistics_to_skip_load
              106  LOAD_CONST               None
              108  COMPARE_OP               is-not
              110  POP_JUMP_IF_FALSE   124  'to 124'

 L.  78       112  LOAD_FAST                'stat_cls'
              114  LOAD_FAST                'self'
              116  LOAD_ATTR                statistics_to_skip_load
              118  COMPARE_OP               in
              120  POP_JUMP_IF_FALSE   124  'to 124'

 L.  79       122  CONTINUE             54  'to 54'
            124_0  COME_FROM           120  '120'
            124_1  COME_FROM           110  '110'

 L.  83       124  LOAD_FAST                'owner_lod'
              126  LOAD_CONST               None
              128  COMPARE_OP               is-not
              130  POP_JUMP_IF_FALSE   194  'to 194'
              132  LOAD_FAST                'owner_lod'
              134  LOAD_FAST                'stat_cls'
              136  LOAD_ATTR                min_lod_value
              138  COMPARE_OP               <
              140  POP_JUMP_IF_FALSE   194  'to 194'

 L.  84       142  LOAD_FAST                'stat_cls'
              144  LOAD_ATTR                min_lod_value
              146  LOAD_GLOBAL              SimInfoLODLevel
              148  LOAD_ATTR                ACTIVE
              150  COMPARE_OP               ==
              152  POP_JUMP_IF_FALSE    54  'to 54'

 L.  85       154  LOAD_FAST                'self'
              156  LOAD_ATTR                _delayed_active_lod_statistics
              158  LOAD_CONST               None
              160  COMPARE_OP               is
              162  POP_JUMP_IF_FALSE   172  'to 172'

 L.  86       164  LOAD_GLOBAL              list
              166  CALL_FUNCTION_0       0  '0 positional arguments'
              168  LOAD_FAST                'self'
              170  STORE_ATTR               _delayed_active_lod_statistics
            172_0  COME_FROM           162  '162'

 L.  87       172  LOAD_FAST                'self'
              174  LOAD_ATTR                _delayed_active_lod_statistics
              176  LOAD_METHOD              append
              178  LOAD_FAST                'statistics_data'
              180  LOAD_ATTR                name_hash
              182  LOAD_FAST                'statistics_data'
              184  LOAD_ATTR                value
              186  BUILD_TUPLE_2         2 
              188  CALL_METHOD_1         1  '1 positional argument'
              190  POP_TOP          

 L.  88       192  CONTINUE             54  'to 54'
            194_0  COME_FROM           140  '140'
            194_1  COME_FROM           130  '130'

 L.  91       194  LOAD_FAST                'statistics_data'
              196  LOAD_METHOD              HasField
              198  LOAD_STR                 'value'
              200  CALL_METHOD_1         1  '1 positional argument'
              202  POP_JUMP_IF_FALSE   224  'to 224'

 L.  92       204  LOAD_FAST                'self'
              206  LOAD_ATTR                set_value
              208  LOAD_FAST                'stat_cls'
              210  LOAD_FAST                'statistics_data'
              212  LOAD_ATTR                value
              214  LOAD_CONST               True
              216  LOAD_CONST               ('from_load',)
              218  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              220  POP_TOP          
              222  JUMP_FORWARD        262  'to 262'
            224_0  COME_FROM           202  '202'

 L.  96       224  LOAD_FAST                'self'
              226  LOAD_ATTR                _statistics
              228  LOAD_CONST               None
              230  COMPARE_OP               is
              232  POP_JUMP_IF_FALSE   240  'to 240'

 L.  97       234  BUILD_MAP_0           0 
              236  LOAD_FAST                'self'
              238  STORE_ATTR               _statistics
            240_0  COME_FROM           232  '232'

 L. 101       240  LOAD_FAST                'stat_cls'
              242  LOAD_FAST                'self'
              244  LOAD_ATTR                _statistics
              246  COMPARE_OP               not-in
          248_250  POP_JUMP_IF_FALSE   278  'to 278'

 L. 102       252  LOAD_CONST               None
              254  LOAD_FAST                'self'
              256  LOAD_ATTR                _statistics
              258  LOAD_FAST                'stat_cls'
              260  STORE_SUBSCR     
            262_0  COME_FROM           222  '222'
              262  JUMP_BACK            54  'to 54'
            264_0  COME_FROM            76  '76'

 L. 104       264  LOAD_GLOBAL              logger
              266  LOAD_METHOD              info
              268  LOAD_STR                 'Trying to load unavailable STATISTIC resource: {}'
              270  LOAD_FAST                'statistics_data'
              272  LOAD_ATTR                name_hash
              274  CALL_METHOD_2         2  '2 positional arguments'
              276  POP_TOP          
            278_0  COME_FROM           248  '248'
              278  JUMP_BACK            54  'to 54'
              280  POP_BLOCK        
            282_0  COME_FROM_LOOP       48  '48'
              282  POP_BLOCK        
              284  LOAD_CONST               None
            286_0  COME_FROM_FINALLY     0  '0'

 L. 106       286  LOAD_CONST               None
              288  LOAD_FAST                'self'
              290  STORE_ATTR               statistics_to_skip_load
              292  END_FINALLY      

 L. 107       294  LOAD_FAST                'self'
              296  LOAD_METHOD              check_for_unneeded_initial_statistics
              298  CALL_METHOD_0         0  '0 positional arguments'
              300  POP_TOP          

Parse error at or near `POP_BLOCK' instruction at offset 280

    def add_statistic(self, stat_type, **kwargs):
        stat = (super().add_statistic)(stat_type, **kwargs)
        if stat is not None:
            if stat.apply_value_to_object_cost:
                if stat not in self._monetary_value_statistics:
                    self._monetary_value_statistics.append(stat)
        return stat

    def remove_statistic(self, stat_type, on_destroy=False):
        if self.has_statistic(stat_type):
            stat = self._statistics[stat_type]
            if stat is not None:
                if stat.apply_value_to_object_cost:
                    if stat in self._monetary_value_statistics:
                        self._monetary_value_statistics.remove(stat)
        super().remove_statisticstat_typeon_destroy

    def get_monetary_value_statistics(self):
        return self._monetary_value_statistics