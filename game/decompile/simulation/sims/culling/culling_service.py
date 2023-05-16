# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\culling\culling_service.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 21577 bytes
import itertools, operator
from alarms import add_alarm
from date_and_time import create_time_span, DateAndTime
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from event_testing.test_events import TestEvent
from fame.fame_tuning import FameTunables
from objects import ALL_HIDDEN_REASONS
from objects.components import types
from objects.system import create_object
from protocolbuffers import GameplaySaveData_pb2
from sims.culling.culling_tuning import CullingTuning
from sims.ghost import Ghost
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_types import Age, Species
from sims4.service_manager import Service
from sims4.utils import classproperty
from story_progression.story_progression_action_sim_info_culling import SimInfoCullingScoreInfo
import persistence_error_types, services, sims4.log, sims4.math
logger = sims4.log.Logger('Culling', default_owner='epanero')

class CullingService(Service):
    CULLING_EVENTS = (
     TestEvent.SimDeathTypeSet, TestEvent.HouseholdChanged)
    CULLING_RETRY_TIME = 60

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._max_player_population = 0
        self._culling_ghost_alarm_handles = set()
        self._interacting_sims = {}
        self._sim_ids_to_cull_on_load = set()

    def start(self):
        services.get_event_manager().register(self, self.CULLING_EVENTS)

    def stop(self):
        services.get_event_manager().unregister(self, self.CULLING_EVENTS)

    def load--- This code section failed: ---

 L.  65         0  LOAD_GLOBAL              super
                2  CALL_FUNCTION_0       0  '0 positional arguments'
                4  LOAD_ATTR                load
                6  BUILD_TUPLE_0         0 
                8  LOAD_FAST                '_'
               10  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               12  POP_TOP          

 L.  66        14  BUILD_MAP_0           0 
               16  LOAD_FAST                'self'
               18  STORE_ATTR               _interacting_sims

 L.  67        20  LOAD_GLOBAL              services
               22  LOAD_METHOD              get_persistence_service
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  LOAD_METHOD              get_save_slot_proto_buff
               28  CALL_METHOD_0         0  '0 positional arguments'
               30  STORE_FAST               'save_slot_data_msg'

 L.  68        32  LOAD_FAST                'save_slot_data_msg'
               34  LOAD_CONST               None
               36  COMPARE_OP               is
               38  POP_JUMP_IF_TRUE     62  'to 62'
               40  LOAD_FAST                'save_slot_data_msg'
               42  LOAD_ATTR                gameplay_data
               44  LOAD_CONST               None
               46  COMPARE_OP               is
               48  POP_JUMP_IF_TRUE     62  'to 62'

 L.  69        50  LOAD_FAST                'save_slot_data_msg'
               52  LOAD_ATTR                gameplay_data
               54  LOAD_METHOD              HasField
               56  LOAD_STR                 'culling_service'
               58  CALL_METHOD_1         1  '1 positional argument'
               60  POP_JUMP_IF_TRUE     66  'to 66'
             62_0  COME_FROM            48  '48'
             62_1  COME_FROM            38  '38'

 L.  70        62  LOAD_CONST               None
               64  RETURN_VALUE     
             66_0  COME_FROM            60  '60'

 L.  71        66  LOAD_FAST                'save_slot_data_msg'
               68  LOAD_ATTR                gameplay_data
               70  LOAD_ATTR                culling_service
               72  STORE_FAST               'culling_service'

 L.  72        74  SETUP_LOOP          108  'to 108'
               76  LOAD_FAST                'culling_service'
               78  LOAD_ATTR                interacting_sims
               80  GET_ITER         
               82  FOR_ITER            106  'to 106'
               84  STORE_FAST               'interacting_sim'

 L.  73        86  LOAD_GLOBAL              DateAndTime
               88  LOAD_FAST                'interacting_sim'
               90  LOAD_ATTR                time_stamp
               92  CALL_FUNCTION_1       1  '1 positional argument'
               94  LOAD_FAST                'self'
               96  LOAD_ATTR                _interacting_sims
               98  LOAD_FAST                'interacting_sim'
              100  LOAD_ATTR                sim_id
              102  STORE_SUBSCR     
              104  JUMP_BACK            82  'to 82'
              106  POP_BLOCK        
            108_0  COME_FROM_LOOP       74  '74'

 L.  74       108  SETUP_LOOP          136  'to 136'
              110  LOAD_FAST                'culling_service'
              112  LOAD_ATTR                sims_to_cull
              114  GET_ITER         
              116  FOR_ITER            134  'to 134'
              118  STORE_FAST               'sim'

 L.  75       120  LOAD_FAST                'self'
              122  LOAD_ATTR                _sim_ids_to_cull_on_load
              124  LOAD_METHOD              add
              126  LOAD_FAST                'sim'
              128  CALL_METHOD_1         1  '1 positional argument'
              130  POP_TOP          
              132  JUMP_BACK           116  'to 116'
              134  POP_BLOCK        
            136_0  COME_FROM_LOOP      108  '108'

Parse error at or near `POP_BLOCK' instruction at offset 134

    def cull_pending_sims_on_load(self):
        sim_ids_to_cull = set(self._sim_ids_to_cull_on_load)
        sim_info_manager = services.sim_info_manager()
        for sim_id in sim_ids_to_cull:
            sim_info = sim_info_manager.getsim_id
            if sim_info is None:
                self._sim_ids_to_cull_on_load.removesim_id
                continue
            if sim_info.get_sim_instance() is not None:
                continue
            household = sim_info.household
            if household is None:
                continue
            self.cull_household(household, is_important_fn=(lambda _: False))

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        super().save(object_list, zone_data, open_street_data, save_slot_data)
        persistable_culling_service = GameplaySaveData_pb2.PersistableCullingService()
        for sim_id, time_stamp in self._interacting_sims.items():
            with ProtocolBufferRollback(persistable_culling_service.interacting_sims) as (interacting_sim):
                interacting_sim.sim_id = sim_id
                interacting_sim.time_stamp = time_stamp.absolute_ticks()

        sims_to_cull = persistable_culling_service.sims_to_cull
        for sim_id in self._sim_ids_to_cull_on_load:
            sims_to_cull.appendsim_id

        save_slot_data.gameplay_data.culling_service = persistable_culling_service

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_CULLING_SERVICE

    def save_options(self, options_proto):
        options_proto.max_player_population = self._max_player_population

    def load_options(self, options_proto):
        self._max_player_population = options_proto.max_player_population

    def has_sim_interacted_with_active_sim(self, sim_id):
        return sim_id in self._interacting_sims

    def sim_interacted_with_active_sim(self, sim):
        if not (sim is None or sim).is_sim or sim.sim_info is None:
            logger.error('Attempted to log {} as an interacting Sim', sim, owner='shouse')
            return
        lod = sim.sim_info.lod
        if lod == SimInfoLODLevel.INTERACTED:
            self.add_sim_to_interacted_simssim.sim_info.sim_id
        else:
            if lod < SimInfoLODLevel.INTERACTED:
                if lod != SimInfoLODLevel.MINIMUM:
                    if sim.sim_info.request_lodSimInfoLODLevel.INTERACTED:
                        self.add_sim_to_interacted_simssim.sim_info.sim_id
                    else:
                        logger.error(("Failed to set sim's LOD from {} to INTERACTED".formatlod), owner='shouse')

    def add_sim_to_interacted_sims(self, sim_id):
        self._interacting_sims[sim_id] = services.time_service().sim_now

    def remove_sim_from_interacted_sims(self, sim_id):
        if sim_id in self._interacting_sims:
            del self._interacting_sims[sim_id]

    def get_interacted_sim_ids_in_priority_order(self):
        return sorted((self._interacting_sims.keys()), key=(lambda k: self._interacting_sims[k]),
          reverse=True)

    def handle_event(self, sim_info, event_type, resolver):
        if event_type == TestEvent.SimDeathTypeSet:
            self._add_culling_ghost_commoditysim_info
        else:
            if event_type == TestEvent.HouseholdChanged:
                if sim_info.is_player_sim:
                    if resolver.event_kwargs.get'sim_removed' is None:
                        self._remove_culling_ghost_commoditysim_info

    def on_all_households_and_sim_infos_loaded(self, client):
        sim_info_manager = services.sim_info_manager()
        for sim_info in sim_info_manager.objects:
            if not sim_info.death_type:
                continue
            if sim_info.is_player_sim:
                self._remove_culling_ghost_commoditysim_info
            else:
                self._add_culling_ghost_commoditysim_info

    def on_zone_load(self):
        self._create_pending_urnstones()

    def on_household_culled(self, household):
        if not household.home_zone_id:
            return
        household.cleanup_trackers()

        def is_valid(sim_info):
            if sim_info.age < Age.CHILD:
                return False
            if sim_info.species != Species.HUMAN:
                return False
            return True

        self._display_culling_notification((CullingTuning.CULLING_NOTIFICATION_IN_WORLD), household, is_valid_fn=is_valid)

    def set_sim_as_ready_to_be_culled(self, sim):
        sim.ready_to_be_culled = True
        self._sim_ids_to_cull_on_load.addsim.id

    def get_max_player_population(self):
        return self._max_player_population

    def set_max_player_population(self, max_player_population):
        max_player_population = max(max_player_population, 0)
        self._max_player_population = max_player_population

    def _create_pending_urnstones(self):
        household = services.owning_household_of_active_lot()
        if household is None:
            return
        for sim_info in household.get_pending_urnstone_sim_infos():
            resolver = SingleSimResolver(sim_info)
            urnstone_definition = Ghost.URNSTONE_DEFINITION.get_definitionresolver
            urnstone = create_object(urnstone_definition)
            urnstone.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(sim_info.id))
            try:
                placement_helper = CullingTuning.CULLING_OFFLOT_URNSTONE_PLACEMENT
                if placement_helper.try_place_object(urnstone, resolver):
                    household.pending_urnstone_ids.removesim_info.id
                    continue
                else:
                    urnstone.destroy()
            except:
                urnstone.destroy()
                raise

    def _add_culling_ghost_commodity(self, sim_info):
        if sim_info.lod == SimInfoLODLevel.MINIMUM:
            return
        tracker = sim_info.get_trackerCullingTuning.CULLING_GHOST_COMMODITY
        if tracker is None:
            return
        commodity = tracker.add_statisticCullingTuning.CULLING_GHOST_COMMODITY
        threshold = sims4.math.Threshold(commodity.min_value, operator.le)
        tracker.create_and_add_listener(commodity.stat_type, threshold, self._on_culling_ghost_commodity_min)
        threshold = sims4.math.Threshold(CullingTuning.CULLING_GHOST_WARNING_THRESHOLD, operator.le)
        tracker.create_and_add_listener(commodity.stat_type, threshold, self._on_culling_ghost_commodity_warning)

    def _remove_culling_ghost_commodity(self, sim_info):
        tracker = sim_info.get_trackerCullingTuning.CULLING_GHOST_COMMODITY
        if tracker is None:
            return
        tracker.remove_statisticCullingTuning.CULLING_GHOST_COMMODITY

    def _on_culling_ghost_commodity_min(self, commodity):
        sim_info = commodity.tracker.owner
        sim_info.remove_statisticcommodity.stat_type
        self._on_culling_ghostsim_info

    def _on_culling_ghost_commodity_warning(self, commodity):
        sim_info = commodity.tracker.owner
        self._display_culling_notification(CullingTuning.CULLING_GHOST_WARNING_NOTIFICATION, (sim_info,))

    def _on_culling_ghost(self, sim_info):
        if sim_info.request_lodSimInfoLODLevel.MINIMUM:
            sim_info.household.remove_sim_info(sim_info, destroy_if_empty_household=True)
            sim_info.transfer_to_hidden_household()
            Ghost.play_release_ghost_vfxsim_info
            return

        def on_culling_ghost_retry(handle):
            self._culling_ghost_alarm_handles.discardhandle
            self._on_culling_ghostsim_info

        sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is not None:
            services.get_zone_situation_manager().make_sim_leave_now_must_runsim
        handle = add_alarm(self, create_time_span(minutes=(self.CULLING_RETRY_TIME)), on_culling_ghost_retry)
        self._culling_ghost_alarm_handles.addhandle

    def _display_culling_notification(self, notification, sim_infos, is_valid_fn=(lambda _: True)):
        active_household = services.active_household()
        sim_infos_a = filter(is_valid_fn, sorted(sim_infos, key=(operator.attrgetter'age')))
        sim_infos_b = filter(is_valid_fn, sorted(active_household, key=(operator.attrgetter'age')))
        for sim_info_a, sim_info_b in itertools.product(sim_infos_a, sim_infos_b):
            if not sim_info_a.relationship_tracker.has_relationshipsim_info_b.sim_id:
                continue
            _notification = notification(sim_info_b, resolver=(DoubleSimResolver(sim_info_a, sim_info_b)))
            _notification.show_dialog()
            break

    def cull_household(self, household, *, is_important_fn, gsi_archive=None):
        if gsi_archive is not None:
            gsi_archive.add_household_action(household, action='cull')
        self.on_household_culledhousehold
        household.set_to_hidden()
        for sim_info in tuple(household):
            if is_important_fn(sim_info):
                if sim_info.request_lodSimInfoLODLevel.MINIMUM:
                    if gsi_archive is not None:
                        gsi_archive.add_sim_info_action(sim_info, action='drop to MINIMUM')
                        continue
            sim_id = sim_info.id
            sim_info.remove_permanently(household=household)
            self._sim_ids_to_cull_on_load.discardsim_id
            if gsi_archive is not None:
                gsi_archive.add_sim_info_action(sim_info, action='cull')

    def get_culling_score_for_sim_info(self, sim_info, output=None):
        if output is not None:
            output('Score for {}'.formatsim_info)
        total_score = 0
        for relationship in sim_info.relationship_tracker:
            target_sim_info = relationship.get_other_sim_infosim_info.sim_id
            if not sim_info.is_player_sim:
                if not target_sim_info.is_player_sim:
                    if output is not None:
                        output('\tSkipping {} -> {} NPC-NPC relationship'.format(sim_info, target_sim_info))
                        continue
            if output is not None:
                output('\t{} -> {} Relationship'.format(sim_info, target_sim_info))
            rel_score = relationship.get_relationship_depthsim_info.sim_id * CullingTuning.RELATIONHSIP_DEPTH_WEIGHT
            if output is not None:
                output('\t\tRel Depth score: {}'.formatrel_score)
            rel_track_multiplier_score = len(relationship.relationship_track_tracker) * CullingTuning.RELATIONSHIP_TRACKS_MULTIPLIER
            if output is not None:
                output('\t\tRel Track score: {}'.formatrel_track_multiplier_score)
            rel_score += rel_track_multiplier_score
            last_time_in_days = target_sim_info.get_days_since_instantiation(uninstatiated_time=(CullingTuning.LAST_INSTANTIATED_MAX / 2))
            relationship_instantiation_time_curve = CullingTuning.RELATIONSHIP_INSTANTIATION_TIME_CURVE
            rel_instantiation_multiplier = relationship_instantiation_time_curve.getlast_time_in_days
            if output is not None:
                output('\t\tTarget instantiated {} days ago ({} multiplier)'.format(last_time_in_days, rel_instantiation_multiplier))
            rel_score *= rel_instantiation_multiplier
            total_score += rel_score
            if output is not None:
                output('\t\tRel Score: {}'.formatrel_score)

        total_rel_score = total_score
        if output is not None:
            output('\tTotal Rel Score: {}'.formattotal_rel_score)
        last_time_in_days = sim_info.get_days_since_instantiation(uninstatiated_time=(CullingTuning.LAST_INSTANTIATED_MAX / 2))
        instantiation_score = (CullingTuning.LAST_INSTANTIATED_MAX - last_time_in_days) * CullingTuning.LAST_INSTANTIATED_WEIGHT
        instantiation_score = max(0, instantiation_score)
        if output is not None:
            output('\tInstantiated {} days ago ({} score)'.format(last_time_in_days, instantiation_score))
        total_score += instantiation_score
        importance_score = self._get_culling_score_for_npcsim_info
        if output is not None:
            output('\tImportance Score: {}'.formatimportance_score)
        total_score += importance_score
        if output is not None:
            output('\tFINAL Score: {}'.formattotal_score)
        return SimInfoCullingScoreInfo(total_score, total_rel_score, instantiation_score, importance_score)

    def _get_culling_score_for_npc(self, sim_info):
        if sim_info.is_player_sim:
            return 0
        else:
            score = services.get_service_npc_service().get_culling_npc_scoresim_info.id
            roommate_service = services.get_roommate_service()
            if roommate_service is not None:
                score += roommate_service.get_culling_npc_scoresim_info.id
            score += services.business_service().get_culling_npc_scoresim_info
            score += sum((trait.culling_behavior.get_culling_npc_score() for trait in sim_info.trait_tracker))
            if FameTunables.FAME_RANKED_STATISTIC is not None:
                stat = sim_info.get_statistic((FameTunables.FAME_RANKED_STATISTIC), add=False)
                if stat is not None:
                    score += CullingTuning.FAME_CULLING_BONUS_CURVE.getstat.rank_level
        if sim_info.household.home_zone_id:
            score += CullingTuning.CULLING_SCORE_IN_WORLD
        if sim_info.is_premade_sim:
            score += CullingTuning.CULLING_SCORE_PREMADE
        return score