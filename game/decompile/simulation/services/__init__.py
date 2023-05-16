# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\__init__.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 37438 bytes
import argparse, functools, gc, time
from services.tuning_managers import InstanceTuningManagers
from sims4.resources import INSTANCE_TUNING_DEFINITIONS
from sims4.tuning.instance_manager import TuningInstanceManager
from sims4.tuning.tunable import Tunable, TunableReference
import game_services, paths, sims4.reload, sims4.service_manager
try:
    import _zone
except ImportError:

    class _zone:

        @staticmethod
        def invite_sims_to_zone(*_, **__):
            pass

        @staticmethod
        def get_house_description_id(*_, **__):
            pass

        @staticmethod
        def get_building_type(*_, **__):
            return 0

        @staticmethod
        def get_eco_footprint_value(*_, **__):
            return 0

        @staticmethod
        def get_rent(*_, **__):
            return 0

        @staticmethod
        def get_lot_description_id(*_, **__):
            pass

        @staticmethod
        def get_world_description_id(*_, **__):
            pass

        @staticmethod
        def get_world_id(*_, **__):
            pass

        @staticmethod
        def get_world_and_lot_description_id_from_zone_id(*_, **__):
            pass

        @staticmethod
        def get_is_eco_footprint_compatible_for_world_description(*_, **__):
            return False

        @staticmethod
        def get_hide_from_lot_picker(*_, **__):
            pass

        @staticmethod
        def is_event_enabled(*_, **__):
            pass


invite_sims_to_zone = _zone.invite_sims_to_zone
get_house_description_id = _zone.get_house_description_id
is_event_enabled = _zone.is_event_enabled
get_building_type = _zone.get_building_type
get_eco_footprint_value = _zone.get_eco_footprint_value
get_rent = _zone.get_rent
get_lot_description_id = _zone.get_lot_description_id
get_world_description_id = _zone.get_world_description_id
get_world_id = _zone.get_world_id
get_world_and_lot_description_id_from_zone_id = _zone.get_world_and_lot_description_id_from_zone_id
get_is_eco_footprint_compatible_for_world_description = _zone.get_is_eco_footprint_compatible_for_world_description
get_hide_from_lot_picker = _zone.get_hide_from_lot_picker
with sims4.reload.protected(globals()):
    tuning_managers = InstanceTuningManagers()
    get_instance_manager = tuning_managers.__getitem__
    _account_service = None
    _zone_manager = None
    _server_clock_service = None
    _persistence_service = None
    _distributor_service = None
    _intern_service = None
    _terrain_service = None
    definition_manager = None
    snippet_manager = None
    _terrain_object = None
    _object_leak_tracker = None
for definition in INSTANCE_TUNING_DEFINITIONS:
    accessor_name = definition.manager_name
    accessor = functools.partial(tuning_managers.__getitem__, definition.TYPE_ENUM_VALUE)
    globals()[accessor_name] = accessor

production_logger = sims4.log.ProductionLogger('Services')
logger = sims4.log.Logger('Services')
time_delta = None
gc_collection_enable = True

class TimeStampService(sims4.service_manager.Service):

    def start(self):
        global gc_collection_enable
        global time_delta
        if gc_collection_enable:
            gc.disable()
            production_logger.info('GC disabled')
            gc_collection_enable = False
        else:
            gc.enable()
            production_logger.info('GC enabled')
            gc_collection_enable = True
        time_stamp = time.time()
        production_logger.info('TimeStampService start at {}'.format(time_stamp))
        logger.info('TimeStampService start at {}'.format(time_stamp))
        if time_delta is None:
            time_delta = time_stamp
        else:
            time_delta = time_stamp - time_delta
            production_logger.info('Time delta from loading start is {}'.format(time_delta))
            logger.info('Time delta from loading start is {}'.format(time_delta))
        return True


def start_global_services(initial_ticks):
    global _account_service
    global _distributor_service
    global _intern_service
    global _zone_manager
    global tuning_managers
    create_server_clock(initial_ticks)
    from distributor.distributor_service import DistributorService
    from intern_service import InternService
    from server.account_service import AccountService
    from services.persistence_service import PersistenceService
    from services.terrain_service import TerrainService
    from sims4.tuning.serialization import FinalizeTuningService
    from zone_manager import ZoneManager
    parser = argparse.ArgumentParser()
    parser.add_argument('--python_autoleak', default=False, action='store_true')
    args, unused_args = parser.parse_known_args()
    if args.python_autoleak:
        create_object_leak_tracker()
    _account_service = AccountService()
    _zone_manager = ZoneManager()
    _distributor_service = DistributorService()
    _intern_service = InternService()
    init_critical_services = [
     server_clock_service(),
     get_persistence_service()]
    services = [
     _distributor_service,
     _intern_service,
     _intern_service.get_start_interning(),
     TimeStampService]
    instantiated_tuning_managers = []
    for definition in INSTANCE_TUNING_DEFINITIONS:
        instantiated_tuning_managers.append(tuning_managers[definition.TYPE_ENUM_VALUE])

    services.append(TuningInstanceManager(instantiated_tuning_managers))
    services.extend([
     FinalizeTuningService,
     TimeStampService,
     _intern_service.get_stop_interning(),
     get_terrain_service(),
     _zone_manager,
     _account_service])
    sims4.core_services.start_services(init_critical_services, services)


def stop_global_services():
    global _account_service
    global _distributor_service
    global _event_manager
    global _intern_service
    global _object_leak_tracker
    global _persistence_service
    global _server_clock_service
    global _terrain_service
    global _zone_manager
    _zone_manager.shutdown()
    _zone_manager = None
    tuning_managers.clear()
    _account_service = None
    _event_manager = None
    _server_clock_service = None
    _persistence_service = None
    _terrain_service = None
    _distributor_service = None
    _intern_service = None
    if _object_leak_tracker is not None:
        _object_leak_tracker = None


def create_object_leak_tracker(start=False):
    global _object_leak_tracker
    from performance.object_leak_tracker import ObjectLeakTracker
    if _object_leak_tracker is None:
        _object_leak_tracker = ObjectLeakTracker()
        if start:
            _object_leak_tracker.start_tracking()
        return True
    return False


def get_object_leak_tracker():
    return _object_leak_tracker


def get_zone_manager():
    return _zone_manager


def current_zone():
    if _zone_manager is not None:
        return _zone_manager.current_zone


def current_zone_id():
    if _zone_manager is not None:
        return sims4.zone_utils.zone_id


def current_zone_info():
    zone = current_zone()
    return zone.get_zone_info()


def current_region():
    zone = current_zone()
    if zone is not None:
        return zone.region


def current_region_instance():
    _region_service = region_service()
    if _region_service is None:
        return
    _current_region = current_region()
    if _current_region is None:
        return
    return _region_service.get_region_instance_by_tuning(_current_region)


def current_street():
    zone = current_zone()
    if zone is not None:
        return zone.street


def get_zone(zone_id, allow_uninstantiated_zones=False):
    if _zone_manager is not None:
        return _zone_manager.get(zone_id, allow_uninstantiated_zones=allow_uninstantiated_zones)


def active_lot():
    zone = current_zone()
    if zone is not None:
        return zone.lot


def active_lot_id():
    lot = active_lot()
    if lot is not None:
        return lot.lot_id


def client_object_managers():
    if game_services.service_manager is not None:
        return game_services.service_manager.client_object_managers
    return ()


def sim_info_manager():
    return game_services.service_manager.sim_info_manager


def posture_graph_service(zone_id=None):
    if zone_id is None:
        zone = current_zone()
        if zone is not None:
            return zone.posture_graph_service
        return
    return _zone_manager.get(zone_id).posture_graph_service


def sim_spawner_service(zone_id=None):
    if zone_id is None:
        return current_zone().sim_spawner_service
    return _zone_manager.get(zone_id).sim_spawner_service


def locator_manager():
    return current_zone().locator_manager


def object_manager(zone_id=None):
    if zone_id is None:
        zone = current_zone()
    else:
        zone = _zone_manager.get(zone_id)
    if zone is not None:
        return zone.object_manager


def inventory_manager(zone_id=None):
    if zone_id is None:
        zone = current_zone()
        if zone is not None:
            return zone.inventory_manager
        return
    return _zone_manager.get(zone_id).inventory_manager


def prop_manager(zone_id=None):
    if zone_id is None:
        zone = current_zone()
    else:
        zone = _zone_manager.get(zone_id)
    if zone is not None:
        return zone.prop_manager


def social_group_manager():
    return current_zone().social_group_manager


def client_manager():
    return game_services.service_manager.client_manager


def get_first_client():
    return client_manager().get_first_client()


def get_selectable_sims():
    return get_first_client().selectable_sims


def owning_household_id_of_active_lot():
    zone = current_zone()
    if zone is not None:
        return zone.lot.owner_household_id


def owning_household_of_active_lot():
    zone = current_zone()
    if zone is not None:
        return household_manager().get(zone.lot.owner_household_id)


def object_preference_overrides_tracker(create_tracker=True):
    zone = current_zone()
    if zone is not None:
        if create_tracker:
            if zone.object_preference_overrides_tracker is None:
                from autonomy.autonomy_object_preference_tracker import AutonomyObjectPreferenceTracker
                zone.object_preference_overrides_tracker = AutonomyObjectPreferenceTracker()
        return zone.object_preference_overrides_tracker


def object_preference_tracker--- This code section failed: ---

 L. 586         0  LOAD_GLOBAL              current_zone
                2  CALL_FUNCTION_0       0  '0 positional arguments'
                4  STORE_DEREF              'zone'

 L. 587         6  LOAD_DEREF               'zone'
                8  LOAD_CONST               None
               10  COMPARE_OP               is
               12  POP_JUMP_IF_FALSE    18  'to 18'

 L. 588        14  LOAD_CONST               None
               16  RETURN_VALUE     
             18_0  COME_FROM            12  '12'

 L. 589        18  LOAD_CLOSURE             'disable_overrides'
               20  LOAD_CLOSURE             'zone'
               22  BUILD_TUPLE_2         2 
               24  LOAD_CODE                <code_object override_tracker>
               26  LOAD_STR                 'object_preference_tracker.<locals>.override_tracker'
               28  MAKE_FUNCTION_8          'closure'
               30  STORE_FAST               'override_tracker'

 L. 599        32  LOAD_GLOBAL              travel_group_manager
               34  CALL_FUNCTION_0       0  '0 positional arguments'
               36  LOAD_METHOD              get_travel_group_by_zone_id
               38  LOAD_DEREF               'zone'
               40  LOAD_ATTR                id
               42  CALL_METHOD_1         1  '1 positional argument'
               44  STORE_FAST               'travel_group'

 L. 600        46  LOAD_FAST                'travel_group'
               48  LOAD_CONST               None
               50  COMPARE_OP               is-not
               52  POP_JUMP_IF_FALSE   132  'to 132'

 L. 601        54  LOAD_FAST                'require_active_household'
               56  POP_JUMP_IF_FALSE   112  'to 112'

 L. 602        58  LOAD_GLOBAL              household_manager
               60  CALL_FUNCTION_0       0  '0 positional arguments'
               62  LOAD_METHOD              get
               64  LOAD_DEREF               'zone'
               66  LOAD_ATTR                lot
               68  LOAD_ATTR                owner_household_id
               70  CALL_METHOD_1         1  '1 positional argument'
               72  STORE_FAST               'household'

 L. 604        74  LOAD_FAST                'household'
               76  LOAD_CONST               None
               78  COMPARE_OP               is-not
               80  POP_JUMP_IF_FALSE    98  'to 98'

 L. 605        82  LOAD_FAST                'household'
               84  LOAD_ATTR                is_active_household
               86  POP_JUMP_IF_TRUE    112  'to 112'

 L. 606        88  LOAD_FAST                'override_tracker'
               90  LOAD_CONST               None
               92  CALL_FUNCTION_1       1  '1 positional argument'
               94  RETURN_VALUE     
               96  JUMP_FORWARD        112  'to 112'
             98_0  COME_FROM            80  '80'

 L. 608        98  LOAD_FAST                'travel_group'
              100  LOAD_ATTR                is_active_sim_in_travel_group
              102  POP_JUMP_IF_TRUE    112  'to 112'

 L. 609       104  LOAD_FAST                'override_tracker'
              106  LOAD_CONST               None
              108  CALL_FUNCTION_1       1  '1 positional argument'
              110  RETURN_VALUE     
            112_0  COME_FROM           102  '102'
            112_1  COME_FROM            96  '96'
            112_2  COME_FROM            86  '86'
            112_3  COME_FROM            56  '56'

 L. 610       112  LOAD_FAST                'travel_group'
              114  LOAD_ATTR                object_preference_tracker
              116  LOAD_CONST               None
              118  COMPARE_OP               is-not
              120  POP_JUMP_IF_FALSE   132  'to 132'

 L. 611       122  LOAD_FAST                'override_tracker'
              124  LOAD_FAST                'travel_group'
              126  LOAD_ATTR                object_preference_tracker
              128  CALL_FUNCTION_1       1  '1 positional argument'
              130  RETURN_VALUE     
            132_0  COME_FROM           120  '120'
            132_1  COME_FROM            52  '52'

 L. 612       132  LOAD_GLOBAL              household_manager
              134  CALL_FUNCTION_0       0  '0 positional arguments'
              136  LOAD_METHOD              get
              138  LOAD_DEREF               'zone'
              140  LOAD_ATTR                lot
              142  LOAD_ATTR                owner_household_id
              144  CALL_METHOD_1         1  '1 positional argument'
              146  STORE_FAST               'household'

 L. 613       148  LOAD_FAST                'household'
              150  LOAD_CONST               None
              152  COMPARE_OP               is
              154  POP_JUMP_IF_TRUE    166  'to 166'
              156  LOAD_FAST                'require_active_household'
              158  POP_JUMP_IF_FALSE   174  'to 174'
              160  LOAD_FAST                'household'
              162  LOAD_ATTR                is_active_household
              164  POP_JUMP_IF_TRUE    174  'to 174'
            166_0  COME_FROM           154  '154'

 L. 614       166  LOAD_FAST                'override_tracker'
              168  LOAD_CONST               None
              170  CALL_FUNCTION_1       1  '1 positional argument'
              172  RETURN_VALUE     
            174_0  COME_FROM           164  '164'
            174_1  COME_FROM           158  '158'

 L. 615       174  LOAD_FAST                'override_tracker'
              176  LOAD_FAST                'household'
              178  LOAD_ATTR                object_preference_tracker
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 182


def get_active_sim():
    client = client_manager().get_first_client()
    if client is not None:
        return client.active_sim


def active_sim_info():
    client = client_manager().get_first_client()
    if client is not None:
        return client.active_sim_info


def active_household():
    client = client_manager().get_first_client()
    if client is not None:
        return client.household


def active_household_id():
    client = client_manager().get_first_client()
    if client is not None:
        return client.household_id


def active_household_lot_id():
    household = active_household()
    if household is not None:
        home_zone = get_zone(household.home_zone_id)
        if home_zone is not None:
            lot = home_zone.lot
            if lot is not None:
                return lot.lot_id


def privacy_service():
    return current_zone().privacy_service


def autonomy_service():
    return current_zone().autonomy_service


def get_aging_service():
    return game_services.service_manager.aging_service


def get_cheat_service():
    return game_services.service_manager.cheat_service


def neighborhood_population_service():
    return current_zone().neighborhood_population_service


def get_reset_and_delete_service():
    return current_zone().reset_and_delete_service


def venue_service():
    return current_zone().venue_service


def venue_game_service():
    return getattr(game_services.service_manager, 'venue_game_service', None)


def zone_spin_up_service():
    return current_zone().zone_spin_up_service


def household_manager():
    return game_services.service_manager.household_manager


def travel_group_manager(zone_id=None):
    if zone_id is None:
        zone = current_zone()
        if zone is not None:
            return zone.travel_group_manager
        return
    return _zone_manager.get(zone_id).travel_group_manager


def utilities_manager(household_id=None):
    if household_id:
        return get_utilities_manager_by_household_id(household_id)
    return get_utilities_manager_by_zone_id(current_zone_id())


def get_utilities_manager_by_household_id(household_id):
    return game_services.service_manager.utilities_manager.get_manager_for_household(household_id)


def get_utilities_manager_by_zone_id(zone_id):
    return game_services.service_manager.utilities_manager.get_manager_for_zone(zone_id)


def ui_dialog_service():
    return current_zone().ui_dialog_service


def config_service():
    return game_services.service_manager.config_service


def travel_service():
    return current_zone().travel_service


def sim_quadtree():
    return current_zone().sim_quadtree


def single_part_condition_list():
    return current_zone().single_part_condition_list


def multi_part_condition_list():
    return current_zone().multi_part_condition_list


def get_event_manager():
    return game_services.service_manager.event_manager_service


def get_current_venue():
    service = venue_service()
    if service is not None:
        return service.active_venue


def get_intern_service():
    return _intern_service


def get_zone_situation_manager(zone_id=None):
    if zone_id is None:
        return current_zone().situation_manager
    return _zone_manager.get(zone_id).situation_manager


def npc_hosted_situation_service():
    return current_zone().n_p_c_hosted_situation_service


def ensemble_service():
    return current_zone().ensemble_service


def sim_filter_service(zone_id=None):
    if zone_id is None:
        return current_zone().sim_filter_service
    return _zone_manager.get(zone_id).sim_filter_service


def get_photography_service():
    return current_zone().photography_service


def social_group_cluster_service():
    return current_zone().social_group_cluster_service


def on_client_connect(client):
    sims4.core_services.service_manager.on_client_connect(client)
    game_services.service_manager.on_client_connect(client)
    current_zone().service_manager.on_client_connect(client)


def on_client_disconnect(client):
    sims4.core_services.service_manager.on_client_disconnect(client)
    if game_services.service_manager.allow_shutdown:
        game_services.service_manager.on_client_disconnect(client)
    current_zone().service_manager.on_client_disconnect(client)


def on_enter_main_menu():
    pass


def account_service():
    return _account_service


def business_service():
    bs = game_services.service_manager.business_service
    return bs


def get_terrain_service():
    global _terrain_service
    if _terrain_service is None:
        from services.terrain_service import TerrainService
        _terrain_service = TerrainService()
    return _terrain_service


def call_to_action_service():
    return game_services.service_manager.call_to_action_service


def trend_service():
    return game_services.service_manager.trend_service


def fashion_trend_service():
    return getattr(game_services.service_manager, 'fashion_trend_service', None)


def time_service():
    return game_services.service_manager.time_service


def game_clock_service():
    return game_services.service_manager.game_clock


def server_clock_service():
    if _server_clock_service is None:
        return
    return _server_clock_service


def create_server_clock(initial_ticks):
    global _server_clock_service
    import clock
    _server_clock_service = clock.ServerClock(ticks=initial_ticks)


def get_master_controller():
    return current_zone().master_controller


def get_persistence_service():
    global _persistence_service
    if _persistence_service is None:
        from services.persistence_service import PersistenceService
        _persistence_service = PersistenceService()
    return _persistence_service


def get_distributor_service():
    return _distributor_service


def get_fire_service():
    return current_zone().fire_service


def get_career_service():
    return current_zone().career_service


def get_story_progression_service():
    return current_zone().story_progression_service


def daycare_service():
    zone = current_zone()
    if zone is not None:
        return zone.daycare_service


def get_adoption_service():
    return current_zone().adoption_service


def get_laundry_service():
    zone = current_zone()
    if zone is not None:
        if hasattr(zone, 'laundry_service'):
            return zone.laundry_service


def get_object_routing_service():
    zone = current_zone()
    if zone is not None:
        if hasattr(zone, 'object_routing_service'):
            return zone.object_routing_service


def get_landlord_service():
    return getattr(game_services.service_manager, 'landlord_service', None)


def get_roommate_service():
    return getattr(game_services.service_manager, 'roommate_service', None)


def get_club_service():
    return getattr(game_services.service_manager, 'club_service', None)


def get_social_media_service():
    return getattr(game_services.service_manager, 'social_media_service', None)


def get_culling_service():
    return game_services.service_manager.culling_service


def get_gardening_service():
    return current_zone().gardening_service


def drama_scheduler_service():
    return current_zone().drama_schedule_service


def get_plex_service():
    return current_zone().plex_service


def get_door_service():
    return current_zone().door_service


def get_zone_modifier_service():
    return current_zone().zone_modifier_service


def get_demographics_service():
    return current_zone().demographics_service


def get_service_npc_service():
    return current_zone().service_npc_service


def conditional_layer_service():
    return current_zone().conditional_layer_service


def dust_service():
    zone = current_zone()
    if hasattr(zone, 'dust_service'):
        return zone.dust_service


def get_sickness_service():
    return game_services.service_manager.sickness_service


def animal_service():
    return getattr(game_services.service_manager, 'animal_service', None)


def get_prom_service():
    return getattr(game_services.service_manager, 'prom_service', None)


def get_curfew_service():
    return game_services.service_manager.curfew_service


def get_locale():
    client = get_first_client()
    return client.account.locale


def relationship_service():
    return game_services.service_manager.relationship_service


def hidden_sim_service():
    return game_services.service_manager.hidden_sim_service


def weather_service():
    return getattr(game_services.service_manager, 'weather_service', None)


def season_service():
    return getattr(game_services.service_manager, 'season_service', None)


def lot_decoration_service():
    return getattr(game_services.service_manager, 'lot_decoration_service', None)


def get_style_service():
    return game_services.service_manager.style_service


def get_tutorial_service():
    return game_services.service_manager.tutorial_service


def calendar_service():
    return current_zone().calendar_service


def get_rabbit_hole_service():
    return game_services.service_manager.rabbit_hole_service


def holiday_service():
    return getattr(game_services.service_manager, 'holiday_service', None)


def global_policy_service():
    return getattr(game_services.service_manager, 'global_policy_service', None)


def narrative_service():
    return getattr(game_services.service_manager, 'narrative_service', None)


def organization_service():
    return getattr(game_services.service_manager, 'organization_service', None)


def get_object_lost_and_found_service():
    return game_services.service_manager.object_lost_and_found_service


def street_service():
    return getattr(game_services.service_manager, 'street_service', None)


def region_service():
    return getattr(game_services.service_manager, 'region_service', None)


def lifestyle_service():
    return game_services.service_manager.lifestyle_service


def get_live_event_service():
    return getattr(game_services.service_manager, 'live_event_service', None)


def get_zone_reservation_service():
    return game_services.service_manager.zone_reservation_service


def purchase_picker_service():
    return game_services.service_manager.purchase_picker_service


def global_flag_service():
    return game_services.service_manager.global_flag_service


def misc_options_service():
    return game_services.service_manager.misc_options_service


def lunar_cycle_service():
    return game_services.service_manager.lunar_cycle_service


def clan_service():
    return getattr(game_services.service_manager, 'clan_service', None)


def get_graduation_service():
    return getattr(game_services.service_manager, 'graduation_service', None)


def c_api_gsi_dump():
    import server_commands.developer_commands
    server_commands.developer_commands.gsi_dump()