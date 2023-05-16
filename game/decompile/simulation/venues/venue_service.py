# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\venue_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 52345 bytes
from protocolbuffers import GameplaySaveData_pb2 as gameplay_serialization, Consts_pb2, Venue_pb2
import alarms, build_buy, clock, persistence_error_types, random, services, sims4.log, sims4.resources, telemetry_helper
from build_buy import get_current_venue
from date_and_time import TimeSpan
from distributor.ops import OwnedUniversityHousingLoad
from distributor.system import Distributor
from objects.components.types import FOOTPRINT_COMPONENT
from open_street_director.open_street_director_request import OpenStreetDirectorRequestFactory
from protocolbuffers import GameplaySaveData_pb2
from sims4.common import Pack
from sims.university.university_housing_tuning import UniversityHousingTuning
from sims.university.university_utils import UniversityUtils
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableSimMinute
from sims4.utils import classproperty
from situations.service_npcs.modify_lot_items_tuning import ModifyAllLotItems
from venues.venue_constants import ZoneDirectorRequestType
from venues.venue_enums import VenueTypes
from world.region import get_region_instance_from_zone_id, get_region_description_id_from_zone_id
TELEMETRY_GROUP_VENUE = 'VENU'
TELEMETRY_HOOK_TIMESPENT = 'TMSP'
TELEMETRY_FIELD_VENUE = 'venu'
TELEMETRY_FIELD_VENUE_TIMESPENT = 'vtsp'
venue_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_VENUE)
try:
    import _zone
except ImportError:

    class _zone:
        pass


logger = sims4.log.Logger('Venue', default_owner='manus')

class VenueService(Service):
    SPECIAL_EVENT_SCHEDULE_DELAY = TunableSimMinute(description='\n        Number of real time seconds to wait after the loading screen before scheduling\n        special events.\n        ',
      default=10.0)
    VENUE_CLEANUP_ACTIONS = ModifyAllLotItems.TunableFactory()
    ELAPSED_TIME_SINCE_LAST_VISIT_FOR_CLEANUP = TunableSimMinute(description='\n        If more than this amount of sim minutes has elapsed since the lot was\n        last visited, the auto cleanup will happen.\n        ',
      default=720,
      minimum=0)

    def __init__(self):
        self._persisted_background_event_id = None
        self._persisted_special_event_id = None
        self._special_event_start_alarm = None
        self._source_venue = None
        self._active_venue = None
        self._zone_director = None
        self._requested_zone_directors = []
        self._prior_zone_director_proto = None
        self._open_street_director_requests = []
        self._prior_open_street_director_proto = None
        self.build_buy_edit_mode = False
        self.on_venue_type_changed = CallableList()
        self._venue_start_time = None
        self._university_housing_household_validation_alarm = None
        self._university_housing_kick_out_completed = False

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_VENUE_SERVICE

    @property
    def active_venue(self):
        return self._active_venue

    @property
    def source_venue(self):
        return self._source_venue

    def venue_is_type(self, required_type):
        if type(self.active_venue) is required_type:
            return True
        return False

    @staticmethod
    def get_variable_venue_source_venue(test_venue_type):
        if test_venue_type is None:
            return
        sub_venue_types = test_venue_type.sub_venue_types
        if sub_venue_types:
            return test_venue_type
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        for venue_tuning_type in venue_manager.types.values():
            if test_venue_type == venue_tuning_type:
                continue
            if venue_tuning_type.valid_active_venue_type(test_venue_type):
                return venue_tuning_type

    def _set_venue(self, active_venue_type, source_venue_type):
        if active_venue_type is None:
            logger.error('Zone {} has invalid active venue type.', services.current_zone().id)
            return False
            if source_venue_type is None:
                source_venue_type = active_venue_type
        else:
            current_source_venue = self.source_venue
            source_venue_changed = type(current_source_venue) is not source_venue_type
            current_active_venue = self.active_venue
            active_venue_changed = type(current_active_venue) is not active_venue_type
            if not source_venue_changed:
                if not active_venue_changed:
                    return False
            if active_venue_changed:
                if current_active_venue is not None:
                    current_active_venue.shut_down()
                    if self._special_event_start_alarm is not None:
                        alarms.cancel_alarm(self._special_event_start_alarm)
                        self._special_event_start_alarm = None
                else:
                    self._send_venue_time_spent_telemetry()
                    if not source_venue_changed:
                        if source_venue_type is active_venue_type:
                            self._active_venue = self._source_venue
                    self._active_venue = active_venue_type(source_venue_type=source_venue_type)
                self._venue_start_time = services.time_service().sim_now
            if source_venue_changed:
                if source_venue_type is active_venue_type:
                    self._source_venue = self._active_venue
                else:
                    self._source_venue = source_venue_type()
                provider = self._source_venue.civic_policy_provider
                if provider is not None:
                    provider.finalize_startup()
        return active_venue_changed

    def _send_venue_time_spent_telemetry(self):
        if self.active_venue is None or self._venue_start_time is None:
            return
        time_spent_mins = (services.time_service().sim_now - self._venue_start_time).in_minutes()
        if time_spent_mins:
            with telemetry_helper.begin_hook(venue_telemetry_writer, TELEMETRY_HOOK_TIMESPENT) as (hook):
                hook.write_guid(TELEMETRY_FIELD_VENUE, self.active_venue.guid64)
                hook.write_int(TELEMETRY_FIELD_VENUE_TIMESPENT, time_spent_mins)

    def get_venue_tuning(self, zone_id):
        venue_tuning = None
        venue_type = get_current_venue(zone_id)
        if venue_type is not None:
            venue_tuning = services.get_instance_manager(sims4.resources.Types.VENUE).get(venue_type)
        return venue_tuning

    def on_change_venue_type_at_runtime--- This code section failed: ---

 L. 261         0  LOAD_FAST                'self'
                2  LOAD_ATTR                build_buy_edit_mode
                4  POP_JUMP_IF_FALSE    10  'to 10'

 L. 264         6  LOAD_CONST               None
                8  RETURN_VALUE     
             10_0  COME_FROM             4  '4'

 L. 266        10  LOAD_FAST                'self'
               12  LOAD_METHOD              _set_venue
               14  LOAD_FAST                'active_venue_type'
               16  LOAD_FAST                'source_venue_type'
               18  CALL_METHOD_2         2  '2 positional arguments'
               20  STORE_FAST               'type_changed'

 L. 267        22  LOAD_FAST                'self'
               24  LOAD_ATTR                active_venue
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    36  'to 36'

 L. 268        32  LOAD_FAST                'type_changed'
               34  RETURN_VALUE     
             36_0  COME_FROM            30  '30'

 L. 270        36  LOAD_FAST                'self'
               38  LOAD_ATTR                active_venue
               40  STORE_FAST               'active_venue'

 L. 271        42  LOAD_FAST                'type_changed'
               44  POP_JUMP_IF_FALSE   120  'to 120'

 L. 272        46  LOAD_FAST                'active_venue'
               48  LOAD_METHOD              create_zone_director_instance
               50  CALL_METHOD_0         0  '0 positional arguments'
               52  STORE_FAST               'zone_director'

 L. 273        54  LOAD_FAST                'self'
               56  LOAD_ATTR                change_zone_director
               58  LOAD_FAST                'zone_director'
               60  LOAD_CONST               True
               62  LOAD_CONST               ('run_cleanup',)
               64  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               66  POP_TOP          

 L. 274        68  LOAD_FAST                'self'
               70  LOAD_METHOD              start_venue_situations
               72  LOAD_FAST                'active_venue'
               74  CALL_METHOD_1         1  '1 positional argument'
               76  POP_TOP          

 L. 275        78  LOAD_FAST                'self'
               80  LOAD_METHOD              on_venue_type_changed
               82  CALL_METHOD_0         0  '0 positional arguments'
               84  POP_TOP          

 L. 277        86  SETUP_LOOP          134  'to 134'
               88  LOAD_GLOBAL              services
               90  LOAD_METHOD              sim_info_manager
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  LOAD_METHOD              instanced_sims_on_active_lot_gen
               96  CALL_METHOD_0         0  '0 positional arguments'
               98  GET_ITER         
              100  FOR_ITER            116  'to 116'
              102  STORE_FAST               'sim'

 L. 278       104  LOAD_FAST                'sim'
              106  LOAD_ATTR                sim_info
              108  LOAD_METHOD              add_venue_buffs
              110  CALL_METHOD_0         0  '0 positional arguments'
              112  POP_TOP          
              114  JUMP_BACK           100  'to 100'
              116  POP_BLOCK        
              118  JUMP_FORWARD        134  'to 134'
            120_0  COME_FROM            44  '44'

 L. 280       120  LOAD_FAST                'force_start_situations'
              122  POP_JUMP_IF_FALSE   134  'to 134'

 L. 281       124  LOAD_FAST                'self'
              126  LOAD_METHOD              start_venue_situations
              128  LOAD_FAST                'active_venue'
              130  CALL_METHOD_1         1  '1 positional argument'
              132  POP_TOP          
            134_0  COME_FROM           122  '122'
            134_1  COME_FROM           118  '118'
            134_2  COME_FROM_LOOP       86  '86'

 L. 283       134  LOAD_FAST                'type_changed'
              136  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 134_2

    def start_venue_situations(self, active_venue):
        self.create_situations_during_zone_spin_up()
        if self._zone_director.should_create_venue_background_situation:
            active_venue.schedule_background_events(schedule_immediate=True)
            active_venue.schedule_special_events(schedule_immediate=False)
            active_venue.schedule_club_gatherings(schedule_immediate=True)

    def make_venue_type_zone_director_request(self):
        active_venue = self.active_venue
        if active_venue is None:
            raise RuntimeError('Venue type must be determined before requesting a zone director.')
        else:
            zone_director = active_venue.create_zone_director_instance()
            if active_venue is self.source_venue:
                request_type = ZoneDirectorRequestType.AMBIENT_VENUE
            else:
                request_type = ZoneDirectorRequestType.AMBIENT_SUB_VENUE
        self.request_zone_director(zone_director, request_type)

    def setup_lot_premade_status(self):
        services.active_lot().flag_as_premade(True)

    def _select_zone_director(self):
        if self._requested_zone_directors is None:
            raise RuntimeError('Cannot select a zone director twice')
        if not self._requested_zone_directors:
            raise RuntimeError('At least one zone director must be requested')
        requested_zone_directors = self._requested_zone_directors
        self._requested_zone_directors = None
        requested_zone_directors.sort()
        _, zone_director, preserve_state = requested_zone_directors[0]
        self._set_zone_director(zone_director, True)
        if self._prior_zone_director_proto:
            self._zone_director.load((self._prior_zone_director_proto), preserve_state=preserve_state)
            self._prior_zone_director_proto = None
        self._setup_open_street_director()

    def _setup_open_street_director(self):
        street = services.current_street()
        if street is not None:
            if street.open_street_director is not None:
                self._open_street_director_requests.append(OpenStreetDirectorRequestFactory((street.open_street_director), priority=(street.open_street_director.priority)))
        self._zone_director.setup_open_street_director_manager(self._open_street_director_requests, self._prior_open_street_director_proto)
        self._open_street_director_requests = None
        self._prior_open_street_director_proto = None

    @property
    def has_zone_director(self):
        return self._zone_director is not None

    def get_zone_director(self):
        return self._zone_director

    def has_requested_zone_director(self, zone_director):
        if self._requested_zone_directors is None:
            return False
        for _, prior_zone_director, _ in self._requested_zone_directors:
            if prior_zone_director.guid64 == zone_director.guid64:
                return True

        return False

    def get_requested_zone_director(self, zone_director):
        if self._requested_zone_directors is None:
            return
        for _, prior_zone_director, _ in self._requested_zone_directors:
            if prior_zone_director.guid64 == zone_director.guid64:
                return prior_zone_director

    def request_zone_director(self, zone_director, request_type, preserve_state=True):
        if self._requested_zone_directors is None:
            raise RuntimeError('Cannot request a new zone director after one has been selected.')
        if zone_director is None:
            raise ValueError('Cannot request a None zone director.')
        for prior_request_type, prior_zone_director, _ in self._requested_zone_directors:
            if prior_request_type == request_type:
                raise ValueError('Multiple requests for zone directors with the same request type {}.  Original: {} New: {}'.format(request_type, prior_zone_director, zone_director))

        self._requested_zone_directors.append((request_type, zone_director, preserve_state))

    def change_zone_director(self, zone_director, run_cleanup):
        if self._zone_director is None:
            raise RuntimeError('Cannot request a new zone director before one has been selected.')
        if self._zone_director is zone_director:
            raise ValueError('Attempting to change zone director to the same instance')
        self._set_zone_director(zone_director, run_cleanup)

    def _set_zone_director(self, zone_director, run_cleanup):
        if self._zone_director is not None:
            if run_cleanup:
                self._zone_director.process_cleanup_actions()
            else:
                for cleanup_action in self._zone_director._cleanup_actions:
                    zone_director.add_cleanup_action(cleanup_action)

            if zone_director is not None:
                zone_director.transfer_open_street_director(self._zone_director)
                zone_director.transfer_from_zone_director(self._zone_director)
            self._zone_director.on_shutdown()
        self._zone_director = zone_director
        if self._zone_director is not None:
            self._zone_director.on_startup()
            if services.current_zone().is_zone_running:
                self._zone_director.create_situations()

    def request_open_street_director(self, open_street_director_request):
        if services.current_zone().is_zone_running:
            self._zone_director.request_new_open_street_director(open_street_director_request)
            return
        self._open_street_director_requests.append(open_street_director_request)

    def determine_which_situations_to_load(self):
        self._zone_director.determine_which_situations_to_load()

    def get_additional_zone_modifiers(self, zone_id):
        current_venue_tuning = self.get_venue_tuning(zone_id)
        if not current_venue_tuning:
            return ()
        else:
            zone_modifiers = set(current_venue_tuning.zone_modifiers)
            return current_venue_tuning.venue_tiers or zone_modifiers
        current_tier = build_buy.get_venue_tier(zone_id)
        if current_tier != -1:
            zone_modifiers.update(current_venue_tuning.venue_tiers[current_tier].zone_modifiers)
        return zone_modifiers

    def on_client_connect(self, client):
        zone = services.current_zone()
        active_venue_key = get_current_venue(zone.id)
        logger.assert_raise((active_venue_key is not None), ' Venue Type is None for zone id:{}', (zone.id), owner='shouse')
        raw_active_venue_key = get_current_venue((zone.id), allow_ineligible=True)
        logger.assert_raise((raw_active_venue_key is not None), ' Raw Venue Type is None for zone id:{}', (zone.id), owner='shouse')
        if not active_venue_key is None:
            if not raw_active_venue_key is None:
                venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
                active_venue_type = venue_manager.get(active_venue_key)
                raw_active_venue_type = venue_manager.get(raw_active_venue_key)
                source_venue_type = VenueService.get_variable_venue_source_venue(raw_active_venue_type)
                self._set_venue(active_venue_type, source_venue_type)

    def on_cleanup_zone_objects(self, client):
        zone = services.current_zone()
        if client.household_id != zone.lot.owner_household_id:
            time_elapsed = zone.time_elapsed_since_last_save()
            if time_elapsed.in_minutes() > self.ELAPSED_TIME_SINCE_LAST_VISIT_FOR_CLEANUP:
                cleanup = VenueService.VENUE_CLEANUP_ACTIONS()
                cleanup.modify_objects()

    def stop(self):
        self._send_venue_time_spent_telemetry()
        if self.build_buy_edit_mode:
            return
        self._set_zone_director(None, True)

    def create_situations_during_zone_spin_up(self):
        self._zone_director.create_situations_during_zone_spin_up()
        self.initialize_venue_schedules()

    def handle_active_lot_changing_edge_cases(self):
        self._zone_director.handle_active_lot_changing_edge_cases()

    def initialize_venue_schedules(self):
        if not self._zone_director.should_create_venue_background_situation:
            return
        active_venue = self.active_venue
        if active_venue is not None:
            active_venue.set_active_event_ids(self._persisted_background_event_id, self._persisted_special_event_id)
            situation_manager = services.current_zone().situation_manager
            schedule_immediate = self._persisted_background_event_id is None or self._persisted_background_event_id not in situation_manager
            active_venue.schedule_background_events(schedule_immediate=schedule_immediate)
            active_venue.schedule_club_gatherings(schedule_immediate=schedule_immediate)

    def process_traveled_and_persisted_and_resident_sims_during_zone_spin_up(self, traveled_sim_infos, zone_saved_sim_infos, plex_group_saved_sim_infos, open_street_saved_sim_infos, injected_into_zone_sim_infos):
        self._zone_director.process_traveled_and_persisted_and_resident_sims(traveled_sim_infos, zone_saved_sim_infos, plex_group_saved_sim_infos, open_street_saved_sim_infos, injected_into_zone_sim_infos)

    def setup_special_event_alarm(self):
        special_event_time_span = clock.interval_in_sim_minutes(self.SPECIAL_EVENT_SCHEDULE_DELAY)
        self._special_event_start_alarm = alarms.add_alarm(self,
          special_event_time_span,
          (self._schedule_venue_special_events),
          repeating=False)

    def _schedule_venue_special_events(self, alarm_handle):
        if self.active_venue is not None:
            self.active_venue.schedule_special_events(schedule_immediate=True)

    def get_zone_venue_type_valid_for_venue_types(self, zone_id, venue_types, compatible_region=None, ignore_region_compatability_tags=False, region_blacklist=[]):
        if not zone_id:
            return
            venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
            venue_type = venue_manager.get(build_buy.get_current_venue(zone_id))
            if venue_type not in venue_types:
                return
        else:
            if compatible_region is not None:
                venue_region = get_region_instance_from_zone_id(zone_id)
                return venue_region is None or compatible_region.is_region_compatible(venue_region, ignore_tags=ignore_region_compatability_tags) or None
            if region_blacklist:
                venue_region_description_id = get_region_description_id_from_zone_id(zone_id)
                if venue_region_description_id in region_blacklist:
                    return
        return venue_type

    def has_zone_for_venue_type(self, venue_types, compatible_region=None):
        for _ in (self.get_zones_for_venue_type_gen)(*venue_types, **{'compatible_region': compatible_region}):
            return True

        return False

    def get_zones_for_venue_type_gen(self, *venue_types, compatible_region=None, ignore_region_compatability_tags=False, region_blacklist=[]):
        for lot_owner_info in services.get_persistence_service().get_lots_proto_buff_gen():
            zone_id = lot_owner_info.zone_instance_id
            if self.get_zone_venue_type_valid_for_venue_types(zone_id, venue_types,
              compatible_region=compatible_region,
              ignore_region_compatability_tags=ignore_region_compatability_tags,
              region_blacklist=region_blacklist) is not None:
                yield zone_id

    def get_zone_and_venue_type_for_venue_types(self, venue_types, compatible_region=None):
        possible_zone_venue_types = []
        for lot_owner_info in services.get_persistence_service().get_lots_proto_buff_gen():
            zone_id = lot_owner_info.zone_instance_id
            venue_type = self.get_zone_venue_type_valid_for_venue_types(zone_id, venue_types,
              compatible_region=compatible_region)
            if venue_type is not None:
                possible_zone_venue_types.append((zone_id, venue_type))

        if possible_zone_venue_types:
            return random.choice(possible_zone_venue_types)
        return (None, None)

    def save(self, zone_data=None, open_street_data=None, **kwargs):
        active_venue = self.active_venue
        if zone_data is not None:
            if active_venue is not None:
                venue_data = zone_data.gameplay_zone_data.venue_data
                if active_venue.active_background_event_id is not None:
                    venue_data.background_situation_id = active_venue.active_background_event_id
                if active_venue.active_special_event_id is not None:
                    venue_data.special_event_id = active_venue.active_special_event_id
                if self._zone_director is not None:
                    zone_director_data = gameplay_serialization.ZoneDirectorData()
                    self._zone_director.save(zone_director_data, open_street_data)
                    venue_data.zone_director = zone_director_data
                else:
                    if self._prior_open_street_director_proto is not None:
                        open_street_data.open_street_director = self._prior_open_street_director_proto
                    if self._prior_zone_director_proto is not None:
                        venue_data.zone_director = self._prior_zone_director_proto

    def load(self, zone_data=None, **kwargs):
        if zone_data is not None:
            if zone_data.HasField('gameplay_zone_data'):
                if zone_data.gameplay_zone_data.HasField('venue_data'):
                    venue_data = zone_data.gameplay_zone_data.venue_data
                    if venue_data.HasField('background_situation_id'):
                        self._persisted_background_event_id = venue_data.background_situation_id
                    if venue_data.HasField('special_event_id'):
                        self._persisted_special_event_id = venue_data.special_event_id
                    if venue_data.HasField('zone_director'):
                        self._prior_zone_director_proto = gameplay_serialization.ZoneDirectorData()
                        self._prior_zone_director_proto.CopyFrom(venue_data.zone_director)
        open_street_id = services.current_zone().open_street_id
        open_street_data = services.get_persistence_service().get_open_street_proto_buff(open_street_id)
        if open_street_data is not None:
            if open_street_data.HasField('open_street_director'):
                self._prior_open_street_director_proto = gameplay_serialization.OpenStreetDirectorData()
                self._prior_open_street_director_proto.CopyFrom(open_street_data.open_street_director)

    def on_loading_screen_animation_finished(self):
        if self._zone_director is not None:
            self._zone_director.on_loading_screen_animation_finished()

    def set_university_housing_kick_out_completed(self):
        self._university_housing_kick_out_completed = True

    def get_university_housing_kick_out_completed(self):
        return self._university_housing_kick_out_completed

    def run_venue_preparation_operations(self):
        if self.active_venue is None:
            return
        zone = services.current_zone()
        venue_type = self.active_venue.venue_type
        owner_household = zone.lot.get_household()
        if venue_type == VenueTypes.UNIVERSITY_HOUSING:
            if owner_household is not None:
                op = OwnedUniversityHousingLoad(zone.id)
                Distributor.instance().add_op_with_no_owner(op)
                self._university_housing_household_validation_alarm = alarms.add_alarm(self, (UniversityHousingTuning.UNIVERSITY_HOUSING_VALIDATION_CADENCE()),
                  (lambda _: UniversityUtils.validate_household_sims()),
                  repeating=True)

    def validate_university_housing_household_sims(self):
        if self.active_venue.venue_type.venue_type == VenueTypes.UNIVERSITY_HOUSING:
            UniversityUtils.validate_household_sims()


class VenueGameService(Service):

    def __init__(self):
        super().__init__()
        self._zone_provider = dict()
        self.on_venue_type_changed = CallableList()
        self._venue_restore_alarm_handler = None
        self._venue_restore_zone_id = None
        self._venue_restore_type_id = None
        self._sub_venue_loading = False

    def stop(self):
        self._clear_venue_restore_alarm()
        super().stop()

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_VENUE_GAME_SERVICE

    @classproperty
    def required_packs(cls):
        return (Pack.EP09, Pack.EP12)

    def on_cleanup_zone_objects(self, client):
        self.load_providers()
        for provider in self._zone_provider.values():
            provider.finalize_startup()

        if self._venue_restore_zone_id is not None:
            if self._venue_restore_zone_id != services.current_zone_id():
                self.restore_venue_type(self._venue_restore_zone_id, None)

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        for zone_id, provider in self._zone_provider.items():
            if provider is None:
                continue
            zone_data = services.get_persistence_service().get_zone_proto_buff(zone_id)
            if zone_data is None:
                continue
            venue_data = zone_data.gameplay_zone_data.venue_data
            provider.save(venue_data.civic_provider_data)

        if self._venue_restore_zone_id is not None:
            venue_game_data = GameplaySaveData_pb2.PersistableVenueGameService()
            venue_game_data.venue_restore_zone_id = self._venue_restore_zone_id
            venue_game_data.venue_restore_type_id = self._venue_restore_type_id
            venue_game_data.venue_restore_alarm_time = self._venue_restore_alarm_handler.get_remaining_time().in_ticks()
            save_slot_data.gameplay_data.venue_game_service = venue_game_data

    def load_providers(self, zone_data=None):
        persistence_service = services.get_persistence_service()

        def _get_current_venue(zone_id):
            neighborhood_data = persistence_service.get_neighborhood_proto_buf_from_zone_id(zone_id)
            for lot_data in neighborhood_data.lots:
                if zone_id == lot_data.zone_instance_id:
                    return lot_data.venue_key

        current_zone_id = services.current_zone_id()
        zones = services.get_persistence_service().get_save_game_data_proto().zones
        for zone_data_msg in zones:
            if zone_data_msg is None:
                continue
            elif zone_data_msg.zone_id == current_zone_id:
                active_venue_tuning_id = get_current_venue(zone_data_msg.zone_id)
                raw_active_venue_tuning_id = get_current_venue((zone_data_msg.zone_id), allow_ineligible=True)
            else:
                active_venue_tuning_id = _get_current_venue(zone_data_msg.zone_id)
                raw_active_venue_tuning_id = active_venue_tuning_id
            if active_venue_tuning_id is None:
                self.set_provider(zone_data_msg.zone_id, None)
                continue
            venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
            active_venue_type = venue_manager.get(active_venue_tuning_id)
            raw_active_venue_type = venue_manager.get(raw_active_venue_tuning_id)
            source_venue_type = VenueService.get_variable_venue_source_venue(raw_active_venue_type)
            if source_venue_type is None:
                self.set_provider(zone_data_msg.zone_id, None)
                continue
            if not source_venue_type.variable_venues is None:
                if source_venue_type.variable_venues is not None:
                    if not source_venue_type.variable_venues.enable_civic_policy_support:
                        self.set_provider(zone_data_msg.zone_id, None)
                        continue
                else:
                    existing_provider = self.get_provider(zone_data_msg.zone_id)
                    if existing_provider is not None:
                        if existing_provider.source_venue_type is source_venue_type:
                            continue
                    provider = source_venue_type.variable_venues.civic_policy(source_venue_type, active_venue_type)
                    provider or self.set_provider(zone_data_msg.zone_id, None)
                    continue
                self.set_provider(zone_data_msg.zone_id, provider)
                if zone_data_msg.HasField('gameplay_zone_data') and zone_data_msg.gameplay_zone_data.HasField('venue_data') and zone_data_msg.gameplay_zone_data.venue_data.HasField('civic_provider_data'):
                    provider.load(zone_data_msg.gameplay_zone_data.venue_data.civic_provider_data)

    def load(self, zone_data=None):
        self.load_providers(zone_data=zone_data)
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        if save_slot_data_msg.gameplay_data.HasField('venue_game_service'):
            venue_game_data = save_slot_data_msg.gameplay_data.venue_game_service
            self._venue_restore_type_id = venue_game_data.venue_restore_type_id
            self._venue_restore_zone_id = venue_game_data.venue_restore_zone_id
            if self._venue_restore_type_id == services.venue_service().get_venue_tuning(self._venue_restore_zone_id).guid64:
                self._venue_restore_alarm_handler = alarms.add_alarm(self,
                  (TimeSpan(venue_game_data.venue_restore_alarm_time)),
                  (self._restore_venue_type_delay_handler),
                  repeating=False)
            else:
                self._venue_restore_zone_id = None
                self._venue_restore_type_id = None

    def get_zone_for_provider(self, provider):
        zone_manager = services.get_zone_manager()
        for zone, stored_provider in self._zone_provider.items():
            if stored_provider is provider:
                return zone_manager.get(zone, allow_uninstantiated_zones=True)

    def get_provider(self, zone_id):
        return self._zone_provider.get(zone_id)

    def set_provider(self, zone_id, provider):
        if zone_id in self._zone_provider:
            self._zone_provider[zone_id].stop_civic_policy_provider()
            del self._zone_provider[zone_id]
        if provider is not None:
            self._zone_provider[zone_id] = provider

    def change_provider_venue_type(self, provider, active_venue_type, source_venue_type=None):
        zone = self.get_zone_for_provider(provider)
        if zone is None:
            return False
        zone_id = zone.id
        return self.change_venue_type(zone_id, active_venue_type, source_venue_type=source_venue_type, zone=zone)

    def change_venue_type(self, zone_id, active_venue_type, source_venue_type=None, zone=None):
        if not zone:
            zone = services.get_zone_manager().get(zone_id, allow_uninstantiated_zones=True)
        else:
            persistence_service = services.get_persistence_service()
            neighborhood_data = persistence_service.get_neighborhood_proto_buf_from_zone_id(zone_id)
            for lot_data in neighborhood_data.lots:
                if zone_id == lot_data.zone_instance_id:
                    if lot_data.venue_key == active_venue_type.guid64:
                        return False
                    lot_data.venue_key = active_venue_type.guid64
                    if lot_data.sub_venue_infos:
                        for sub_venue_info in lot_data.sub_venue_infos:
                            if sub_venue_info.sub_venue_key == lot_data.venue_key:
                                lot_data.venue_eligible = sub_venue_info.sub_venue_eligible
                                break
                        else:
                            sub_venue_info = lot_data.sub_venue_infos.add()
                            sub_venue_info.sub_venue_key = lot_data.venue_key
                            sub_venue_info.sub_venue_eligible = False
                            lot_data.venue_eligible = False

                    break

            on_active_lot = zone_id == services.current_zone_id()
            if on_active_lot:
                if source_venue_type is None:
                    source_venue_type = VenueService.get_variable_venue_source_venue(active_venue_type)
                services.venue_service().on_change_venue_type_at_runtime(active_venue_type, source_venue_type)
            lot_id = None
            world_id = None
            if zone.is_instantiated:
                lot_id = zone.lot.lot_id
                world_id = zone.world_id
            else:
                save_game_data = persistence_service.get_save_game_data_proto()
                for zone_data in save_game_data.zones:
                    if zone_data.zone_id == zone_id:
                        lot_id = zone_data.lot_id
                        world_id = zone_data.world_id
                        break

        if lot_id is None or world_id is None:
            return False
        if zone.is_instantiated:
            self._sub_venue_loading = True
        distributor = Distributor.instance()
        venue_update_request_msg = Venue_pb2.VenueUpdateRequest()
        venue_update_request_msg.venue_key = active_venue_type.guid64
        venue_update_request_msg.lot_id = lot_id
        venue_update_request_msg.world_id = world_id
        distributor.add_event(Consts_pb2.MSG_SET_SUB_VENUE, venue_update_request_msg)
        distributor.add_event(Consts_pb2.MSG_NS_NEIGHBORHOOD_UPDATE, neighborhood_data)
        self.on_venue_type_changed(zone_id, active_venue_type)
        return True

    def on_sub_venue_finished_loading(self):
        if not self._sub_venue_loading:
            return
        self._sub_venue_loading = False
        for obj in services.object_manager().values():
            footprint_component = obj.get_component(FOOTPRINT_COMPONENT)
            if footprint_component is not None:
                footprint_component.on_finalize_load()

    @property
    def sub_venue_loading(self):
        return self._sub_venue_loading

    def _restore_venue_type_delay_handler(self, _):
        if self._venue_restore_type_id == services.venue_service().get_venue_tuning(self._venue_restore_zone_id).guid64:
            self.restore_venue_type(self._venue_restore_zone_id, None)

    def _clear_venue_restore_alarm(self):
        if self._venue_restore_alarm_handler is not None:
            self._venue_restore_zone_id = None
            alarms.cancel_alarm(self._venue_restore_alarm_handler)
            self._venue_restore_alarm_handler = None
            self._venue_restore_type_id = None

    def restore_venue_type(self, zone_id, delay):
        if delay:
            if zone_id == services.current_zone_id():
                self._venue_restore_alarm_handler = alarms.add_alarm(self,
                  delay,
                  (self._restore_venue_type_delay_handler),
                  repeating=False)
                self._venue_restore_zone_id = zone_id
                self._venue_restore_type_id = services.venue_service().get_venue_tuning(zone_id).guid64
                return
        if zone_id == self._venue_restore_zone_id:
            self._clear_venue_restore_alarm()
        active_venue_type = services.venue_service().get_venue_tuning(zone_id)
        source_venue_type = VenueService.get_variable_venue_source_venue(active_venue_type)
        self.change_venue_type(zone_id, source_venue_type, source_venue_type=source_venue_type)