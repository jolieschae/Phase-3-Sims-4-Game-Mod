# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\body_type_level_tracker.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 8199 bytes
import alarms, services, sims4
from cas.cas import change_bodytype_level
from date_and_time import create_time_span
from sims.body_type_level.body_type_level_commodity import BODY_TYPE_TO_LEVEL_COMMODITY
from sims.body_type_level.hair_growth_flags import HairGrowthFlags, HAIR_GROWTH_TO_BODY_TYPE
from sims.outfits.outfit_enums import BodyType
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.common import Pack
from sims4.tuning.tunable import Tunable
from sims4.utils import classproperty
from statistics.statistic_enums import StatisticLockAction
logger = sims4.log.Logger('BodyTypeLevelTracker', default_owner='skorman')

class BodyTypeLevelTracker(SimInfoTracker):
    COLLECT_REQUESTS_MINUTES = Tunable(description='\n        The number of in-game minutes to wait before sending pending body type \n        level change requests after receiving the first one. This is a \n        performance optimization so client can process multiple requests at the \n        same time.\n        ',
      tunable_type=float,
      default=0.5)

    def __init__(self, sim_info):
        self._sim_info = sim_info
        self._pending_requests = None
        self._send_pending_requests_alarm_handle = None

    @classproperty
    def required_packs(cls):
        return (Pack.EP12,)

    def request_client_level_change(self, body_type, new_level):
        request = {body_type: new_level}
        if self._pending_requests is None:
            self._pending_requests = request
            self._send_pending_requests_alarm_handle = alarms.add_alarm(self, create_time_span(minutes=(self.COLLECT_REQUESTS_MINUTES)),
              (lambda _: self._send_body_type_level_update()),
              cross_zone=True)
        else:
            self._pending_requests.update(request)

    def _send_body_type_level_update(self):
        change_bodytype_level(self._sim_info._base, self._pending_requests)
        self._sim_info.resend_current_occult_types()
        self._sim_info.resend_physical_attributes()
        self._pending_requests = None
        self._send_pending_requests_alarm_handle = None

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.ACTIVE

    def on_lod_update--- This code section failed: ---

 L.  89         0  LOAD_FAST                'new_lod'
                2  LOAD_FAST                'self'
                4  LOAD_ATTR                _tracker_lod_threshold
                6  COMPARE_OP               <
                8  POP_JUMP_IF_FALSE    68  'to 68'

 L.  92        10  SETUP_LOOP          152  'to 152'
               12  LOAD_GLOBAL              BODY_TYPE_TO_LEVEL_COMMODITY
               14  LOAD_METHOD              items
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  GET_ITER         
               20  FOR_ITER             64  'to 64'
               22  UNPACK_SEQUENCE_2     2 
               24  STORE_FAST               'body_type'
               26  STORE_FAST               'level_commodity_type'

 L.  93        28  LOAD_STR                 'locked in body_type_level_tracker.py:on_lod_update at {}'
               30  LOAD_METHOD              format
               32  LOAD_GLOBAL              services
               34  LOAD_METHOD              time_service
               36  CALL_METHOD_0         0  '0 positional arguments'
               38  LOAD_ATTR                sim_now
               40  CALL_METHOD_1         1  '1 positional argument'
               42  STORE_FAST               'reason'

 L.  94        44  LOAD_FAST                'self'
               46  LOAD_ATTR                _sim_info
               48  LOAD_METHOD              lock_statistic
               50  LOAD_FAST                'level_commodity_type'

 L.  95        52  LOAD_GLOBAL              StatisticLockAction
               54  LOAD_ATTR                DO_NOT_CHANGE_VALUE

 L.  96        56  LOAD_FAST                'reason'
               58  CALL_METHOD_3         3  '3 positional arguments'
               60  POP_TOP          
               62  JUMP_BACK            20  'to 20'
               64  POP_BLOCK        
               66  JUMP_FORWARD        152  'to 152'
             68_0  COME_FROM             8  '8'

 L.  98        68  LOAD_FAST                'old_lod'
               70  LOAD_FAST                'self'
               72  LOAD_ATTR                _tracker_lod_threshold
               74  COMPARE_OP               <
               76  POP_JUMP_IF_FALSE   152  'to 152'

 L. 101        78  LOAD_GLOBAL              BODY_TYPE_TO_LEVEL_COMMODITY
               80  LOAD_METHOD              get
               82  LOAD_GLOBAL              BodyType
               84  LOAD_ATTR                SKINDETAIL_ACNE_PUBERTY
               86  CALL_METHOD_1         1  '1 positional argument'
               88  STORE_FAST               'acne_stat_type'

 L. 102        90  LOAD_FAST                'self'
               92  LOAD_ATTR                _sim_info
               94  LOAD_METHOD              get_statistic
               96  LOAD_FAST                'acne_stat_type'
               98  CALL_METHOD_1         1  '1 positional argument'
              100  STORE_FAST               'acne_stat'

 L. 103       102  LOAD_FAST                'self'
              104  LOAD_ATTR                _sim_info
              106  LOAD_METHOD              is_in_locked_commodities
              108  LOAD_FAST                'acne_stat'
              110  CALL_METHOD_1         1  '1 positional argument'
              112  POP_JUMP_IF_FALSE   144  'to 144'

 L. 104       114  LOAD_STR                 'unlocked in body_type_level_tracker.py:on_lod_update at {}'
              116  LOAD_METHOD              format
              118  LOAD_GLOBAL              services
              120  LOAD_METHOD              time_service
              122  CALL_METHOD_0         0  '0 positional arguments'
              124  LOAD_ATTR                sim_now
              126  CALL_METHOD_1         1  '1 positional argument'
              128  STORE_FAST               'reason'

 L. 105       130  LOAD_FAST                'self'
              132  LOAD_ATTR                _sim_info
              134  LOAD_METHOD              unlock_statistic
              136  LOAD_FAST                'acne_stat_type'
              138  LOAD_FAST                'reason'
              140  CALL_METHOD_2         2  '2 positional arguments'
              142  POP_TOP          
            144_0  COME_FROM           112  '112'

 L. 106       144  LOAD_FAST                'self'
              146  LOAD_METHOD              refresh_hair_growth_commodities
              148  CALL_METHOD_0         0  '0 positional arguments'
              150  POP_TOP          
            152_0  COME_FROM            76  '76'
            152_1  COME_FROM            66  '66'
            152_2  COME_FROM_LOOP       10  '10'

Parse error at or near `COME_FROM' instruction at offset 152_1

    def set_acne_enabled(self, is_enabled):
        acne_stat_type = BODY_TYPE_TO_LEVEL_COMMODITY.get(BodyType.SKINDETAIL_ACNE_PUBERTY)
        if acne_stat_type is None:
            logger.error('Failed to set acne enabled. No matching BodyTypeLevelCommodity found.')
        else:
            acne_stat = self._sim_info.get_statistic(acne_stat_type)
            if is_enabled:
                if self._sim_info.is_in_locked_commodities(acne_stat):
                    reason = f"unlocked in body_type_level_tracker.py:set_acne_enabled at {services.time_service().sim_now}"
                    self._sim_info.unlock_statisticacne_stat_typereason
            else:
                reason = f"locked in body_type_level_tracker.py:set_acne_enabled at {services.time_service().sim_now}"
                self._sim_info.lock_statisticacne_stat_typeStatisticLockAction.USE_MIN_VALUE_TUNINGreason

    def refresh_hair_growth_commodities(self):
        active_growth_flags = HairGrowthFlags.ALL & self._sim_info.flags
        growth_enabled_body_types = [body_type for growth_flag, body_type in HAIR_GROWTH_TO_BODY_TYPE.items() if active_growth_flags & growth_flag]
        potential_hair_growth_body_types = HAIR_GROWTH_TO_BODY_TYPE.values()
        for body_type, level_commodity_type in BODY_TYPE_TO_LEVEL_COMMODITY.items():
            if body_type not in potential_hair_growth_body_types:
                continue
            else:
                stat = self._sim_info.get_statistic(level_commodity_type)
                if body_type in growth_enabled_body_types:
                    if self._sim_info.is_in_locked_commodities(stat):
                        reason = f"unlocked by body_type_level_tracker.py: refresh_hair_growth_commodities at {services.time_service().sim_now}"
                        self._sim_info.unlock_statisticlevel_commodity_typereason
                else:
                    reason = f"locked by body_type_level_tracker.py: refresh_hair_growth_commodities at {services.time_service().sim_now}"
                    self._sim_info.lock_statisticlevel_commodity_typeStatisticLockAction.DO_NOT_CHANGE_VALUEreason
            level = self._sim_info._base.get_current_growth_level(body_type)
            stat.set_level(level)

    def on_zone_load(self):
        self.refresh_hair_growth_commodities()

    def on_zone_unload(self):
        if self._pending_requests is not None:
            self._send_body_type_level_update()