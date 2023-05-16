# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\whims\whims_tracker.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 65639 bytes
from _functools import reduce
import collections, game_services, itertools, operator, random
from event_testing.test_events import TestEvent
from objects.mixins import AffordanceCacheMixin, ProvidedAffordanceData
from protocolbuffers import DistributorOps_pb2, GameplaySaveData_pb2
from protocolbuffers.DistributorOps_pb2 import SetWhimBucks
from date_and_time import create_time_span
from distributor.ops import distributor
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing import test_events
from interactions.liability import Liability
from objects import ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims.sim_info_utils import remove_super_affordance_commodity_flags, apply_super_affordance_commodity_flags
from sims4.math import Threshold
from sims4.tuning.tunable import TunableSimMinute, HasTunableFactory, OptionalTunable, AutoFactoryInit, TunableList, TunableEnumEntry, TunableMapping, TunableReference, TunableSet, TunableTuple, Tunable, TunablePercent
from sims4.utils import classproperty
from singletons import EMPTY_SET
from situations.situation_goal_targeted_sim import SituationGoalSimTargetingOptions
from situations.situation_serialization import GoalSeedling
import enum, event_testing, services, sims4.log, sims4.random, telemetry_helper, uid
from traits.trait_type import TraitType
TELEMETRY_GROUP_WHIMS = 'WHIM'
TELEMETRY_HOOK_WHIM_EVENT = 'WEVT'
TELEMETRY_WHIM_EVENT_TYPE = 'wtyp'
TELEMETRY_WHIM_GUID = 'wgui'
TELEMETRY_WHIM_FEAR_TRAIT_GUID = 'fuid'
whim_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_WHIMS)

class TelemetryWhimEvents(enum.Int, export=False):
    CANCELED = 0
    NO_LONGER_AVAILABLE = 1
    COMPLETED = 2
    ADDED = 4
    CHEAT_CLEAR = 5


logger = sims4.log.Logger('Whims', default_owner='jjacobson')

class HideWhimsLiability(Liability, HasTunableFactory, AutoFactoryInit):
    LIABILITY_TOKEN = 'HideWhimsLiability'
    FACTORY_TUNABLES = {'_reset_time': OptionalTunable(description='\n            If enabled, when this liability is released, all non-locked whims\n            will be reset if this liability exists for longer than this time.\n            ',
                      tunable=TunableSimMinute(description='\n                The amount of time that needs to pass on liability release that\n                the whims will be reset as well as unhidden.\n                ',
                      default=1,
                      minimum=1))}

    def __init__(self, interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._starting_time_stamp = None
        self._sim_info = interaction.sim.sim_info

    def on_run(self):
        if self._starting_time_stamp is not None:
            return
        if self._sim_info.whim_tracker is None:
            return
        self._starting_time_stamp = services.time_service().sim_now
        self._sim_info.whim_tracker.hide_whims()

    def release(self):
        if self._starting_time_stamp is None:
            return
        if self._sim_info.whim_tracker is None:
            return
        should_reset = False
        if self._reset_time is not None:
            current_time = services.time_service().sim_now
            elapsed_time = current_time - self._starting_time_stamp
            should_reset = elapsed_time > create_time_span(minutes=(self._reset_time))
        self._sim_info.whim_tracker.show_whims(reset=should_reset)


_ActiveWhimsetData = collections.namedtuple('_ActiveWhimsetData', ['target', 'callback_data'])

class WhimType(enum.Int):
    INVALID = 0
    LONG_TERM = 1
    SHORT_TERM = 2
    REACTIONARY = 3
    CONFRONTATION = 4


class WhimsTracker(SimInfoTracker, AffordanceCacheMixin):
    WHIM_SLOTS = TunableList(description='\n        A list of entries reserved, defined as what type of whim they should contain.\n        ',
      tunable=TunableEnumEntry(description='\n            The type of whim that the entry should contain.\n            ',
      tunable_type=WhimType,
      default=(WhimType.INVALID),
      invalid_enums=(
     WhimType.INVALID,)))
    WHIM_TYPE_CONFIGURATION = TunableMapping(description='\n        Configuration data for each whim type.\n        ',
      key_type=TunableEnumEntry(description='\n            The type of whim we are configuring.\n            ',
      tunable_type=WhimType,
      default=(WhimType.INVALID),
      invalid_enums=(
     WhimType.INVALID,)),
      value_type=TunableTuple(description='\n            The configuration for this whim type.\n            ',
      fallback_types=TunableList(description='\n                When we are selecting a new whim for a slot of this type and we\n                cannot find a valid whim of this type, what other types can\n                we search for as a fallback? If none are found (or no types\n                are added to this list) then the slot will remain empty.\n                The fallback types are tried in the order listed here.\n                ',
      tunable=TunableEnumEntry(description='\n                    The fallback whim type.\n                    ',
      tunable_type=WhimType,
      default=(WhimType.INVALID),
      invalid_enums=(
     WhimType.INVALID,))),
      can_be_locked=Tunable(description='\n                Can this type of whim be locked?\n                ',
      tunable_type=bool,
      default=True),
      chance_to_populate=TunablePercent(description='\n                The chance that an empty slot of this type will\n                be populated when we offer whims.\n                ',
      default=100)))
    CONSTANT_WHIM_SETS = TunableSet(description='\n        A list of whim sets that will always be active.\n        ',
      tunable=TunableReference(description='\n            A whim set that is always active.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
      class_restrictions=('ObjectivelessWhimSet', )))

    class ActiveWhimsetData:

        def __init__(self, whimset):
            self._whimset = whimset
            self._targets = set()

        @property
        def whimset(self):
            return self._whimset

        @property
        def targets(self):
            return self._targets

        def add_target(self, target):
            self._targets.add(target)

    class WhimSlotData:

        def __init__(self, whim_type, whims_tracker):
            self.whim = None
            self.goal_instance = None
            self.whimset = None
            self._last_refresh = 0
            self.whim_type = whim_type
            self.commodity = None
            self._whims_tracker = whims_tracker

        def __repr__(self):
            return 'SlotData(Whim: {}, Goal: {}, Intended Type: {}, Whimset: {}, Last Refresh: {}, Locked: {})'.format(self.whim, self.goal_instance, self.whim_type, self.whimset, self._last_refresh, self.is_locked())

        def get_gsi_data(self):
            return {'sim_id':str(self._whims_tracker._sim_info.sim_id), 
             'whim':self.whim.__name__ if self.whim is not None else 'None', 
             'goal':self.goal_instance.get_gsi_name() if self.goal_instance is not None else 'None', 
             'goal_instance':self.goal_instance.__class__.__name__ if self.goal_instance is not None else 'None', 
             'whimset':self.whimset.__name__ if self.whim is not None else 'None', 
             'target':str(self._whims_tracker.get_whimset_target(self.whimset)) if self.whim is not None else 'None', 
             'value':self.goal_instance.score if self.goal_instance is not None else 'None', 
             'locked':str(self.is_locked()), 
             'last_refresh':self._last_refresh, 
             'slot_whim_type':str(self.whim_type), 
             'whim_type':str(self.whim.type) if self.whim is not None else 'None', 
             'goal_type':str(type(self.goal_instance)) if self.goal_instance is not None else 'None'}

        def clear(self, telemetry_event=None):
            if self.is_empty():
                return
            sim_info = self._whims_tracker._sim_info
            sim = sim_info.get_sim_instance()
            remove_super_affordance_commodity_flags(sim, self.whim)
            if self.commodity is not None:
                sim_info.commodity_tracker.remove_statistic(self.whim.commodity)
                self.commodity = None
            temp_whimset = self.whimset
            temp_whim = self.whim
            self.whimset = None
            self.whim = None
            temp_goal = self.goal_instance
            if self.goal_instance is not None:
                self.goal_instance.decommision()
                self.goal_instance = None
            if temp_whimset is None:
                logger.error('Tried to handle completed goal {} in slot {} with no whimset!', temp_goal, self)
                return False
            if temp_whim is None:
                logger.error('Tried to emit telemetry for a completed goal {} in slot {} with no whim!', temp_goal, self)
                return False
            if telemetry_event is not None:
                with telemetry_helper.begin_hook(whim_telemetry_writer, TELEMETRY_HOOK_WHIM_EVENT, sim_info=(self._whims_tracker._sim_info)) as (hook):
                    hook.write_int(TELEMETRY_WHIM_EVENT_TYPE, telemetry_event)
                    hook.write_guid(TELEMETRY_WHIM_GUID, temp_goal.guid64)
                    if temp_whim.type is WhimType.CONFRONTATION:
                        corresponding_trait = self._whims_tracker._try_get_source_fear_from_whimset(temp_whimset)
                        if corresponding_trait is None:
                            logger.error('Unable to send telemetry event {} for confrontation whim {} in whimset {}:could not find corresponding fear trait.', telemetry_event, temp_whim, temp_whimset)
                            return False
                        hook.write_guid(TELEMETRY_WHIM_FEAR_TRAIT_GUID, corresponding_trait.guid64)

        def clean_up(self):
            self.whimset = None
            if self.whim is not None:
                sim_info = self._whims_tracker._sim_info
                sim = sim_info.get_sim_instance()
                remove_super_affordance_commodity_flags(sim, self.whim)
                if self.commodity is not None:
                    sim_info.commodity_tracker.remove_statistic(self.whim.commodity)
                    self.commodity = None
                self.whim = None
            if self.goal_instance is not None:
                self.goal_instance.destroy()
                self.goal_instance = None
            self._last_refresh = 0

        def is_locked(self):
            return self.goal_instance is not None and self.goal_instance.locked

        def toggle_locked_status(self):
            if self.goal_instance is not None:
                whim_type = self.whim.type
                config = self._whims_tracker.WHIM_TYPE_CONFIGURATION
                can_lock = True
                if whim_type in config:
                    can_lock = config[whim_type].can_be_locked
                if can_lock:
                    self.goal_instance.toggle_locked_status()

        def is_valid(self):
            if self.goal_instance is None:
                return True
            required_sim_info = self.goal_instance.get_required_target_sim_info()
            return self.goal_instance.can_be_given_as_goal((self._whims_tracker._sim_info), None, inherited_target_sim_info=required_sim_info)

        def is_empty(self):
            return self.goal_instance is None

        def roll_chance_to_populate(self):
            chance = self._whims_tracker.WHIM_TYPE_CONFIGURATION[self.whim_type].chance_to_populate
            return random.random() < chance

        def populate_data(self, goal, whim, whimset):
            if not self.is_empty():
                logger.exception('Tried to populate this slot when the slot is already populated.')
            if goal is None:
                logger.error('Tried to populate the goal for a slot to None.')
                return
            if whim is None:
                logger.error('Tried to populate the whim for a slot to None')
                return
            if whimset is None:
                logger.error('Tried to populate the whimset for a slot to None.')
                return
            goal.setup()
            goal.register_for_on_goal_completed_callback(self._on_goal_completed)
            goal.show_goal_awarded_notification()
            provided_affordances = []
            for provided_affordance in whim.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                provided_affordances.append(provided_affordance_data)

            sim_info = self._whims_tracker._sim_info
            sim = sim_info.get_sim_instance()
            self._whims_tracker.add_to_affordance_caches(whim.super_affordances, provided_affordances)
            apply_super_affordance_commodity_flags(sim, whim, whim.super_affordances)
            if whim.commodity is not None:
                self.commodity = sim_info.commodity_tracker.add_statistic(whim.commodity)
            self.whim = whim
            self.goal_instance = goal
            self.whimset = whimset

        def _on_goal_completed(self, goal, goal_completed):
            if not goal_completed:
                self._whims_tracker._send_goals_update()
                return
            self._whims_tracker._on_goal_completed(self, goal)

    @classproperty
    def max_whims(cls):
        return len(cls.WHIM_SLOTS)

    def __init__(self, sim_info):
        super().__init__()
        self._enabled = True
        self._sim_info = sim_info
        self._goal_id_generator = uid.UniqueIdGenerator(1)
        self._active_whimsets_data = {}
        self._whim_slots = []
        for whim_type in self.WHIM_SLOTS:
            self._whim_slots.append(WhimsTracker.WhimSlotData(whim_type, self))

        self._hidden = False
        self._whim_goal_proto = None
        self._completed_goals = {}
        self._test_results_map = {}
        self._score_multipliers = []
        self._registered_whimset_removal_events = set()

    def start_whims_tracker(self):
        self._populate_slots()

    def set_enabled(self, is_enabled):
        if self._enabled == is_enabled:
            return
        else:
            self._enabled = is_enabled
            if is_enabled:
                self._populate_slots()
            else:
                for whim_slot in self._whim_slots:
                    whim_slot.clear(TelemetryWhimEvents.CANCELED)

        self.update_affordance_caches()
        self._send_goals_update()

    def activate_whimset_from_objective_completion(self, whimset):
        self._activate_whimset(whimset)

    def validate_goals(self):
        sim = self._sim_info.get_sim_instance()
        if sim is None:
            return
        for whim_slot in self._whim_slots:
            if not whim_slot.is_valid():
                whim_slot.clear(TelemetryWhimEvents.NO_LONGER_AVAILABLE)

        self._populate_slots()

    def slots_gen(self):
        for whim_slot in self._whim_slots:
            yield whim_slot

    def is_whim_active(self, whim):
        for slot in self._whim_slots:
            if slot.is_empty() or slot.whim.guid64 == whim.guid64:
                return True

        return False

    def get_active_whimset_data(self):
        whim_sets_with_data = {}
        services.get_event_manager().unregister(self, self._registered_whimset_removal_events)
        self._registered_whimset_removal_events.clear()

        def insert_data(whimset, target=None):
            if whimset not in whim_sets_with_data:
                whim_sets_with_data[whimset] = WhimsTracker.ActiveWhimsetData(whimset)
            if target is not None:
                whim_sets_with_data[whimset].add_target(target)

        for whimset, data in self._active_whimsets_data.items():
            insert_data(whimset, data.target)

        if self._sim_info.primary_aspiration is not None:
            if self._sim_info.primary_aspiration.whim_set is not None:
                insert_data(self._sim_info.primary_aspiration.whim_set)
                self._registered_whimset_removal_events.add(TestEvent.AspirationChanged)
        current_venue = services.get_current_venue()
        if current_venue.whim_set is not None:
            insert_data(current_venue.whim_set)
        for trait in self._sim_info.trait_tracker:
            if trait.whim_set is not None:
                insert_data(trait.whim_set)
                self._registered_whimset_removal_events.add(TestEvent.TraitRemoveEvent)

        sim_id = self._sim_info.sim_id
        target_sims = self._sim_info.relationship_tracker.get_target_sim_infos()
        for target_sim in target_sims:
            for bit in self._sim_info.relationship_tracker.get_all_bits(target_sim.sim_id):
                if bit.whim_set is not None:
                    bit.whim_set.apply_to_target or insert_data(bit.whim_set.whim_set, target_sim)
                    self._registered_whimset_removal_events.add(TestEvent.RemoveRelationshipBit)

            for targets_bit in target_sim.relationship_tracker.get_all_bits(sim_id):
                if targets_bit.whim_set is not None and targets_bit.whim_set.apply_to_target:
                    insert_data(targets_bit.whim_set.whim_set, target_sim)
                    self._registered_whimset_removal_events.add(TestEvent.RemoveRelationshipBit)

        season_service = services.season_service()
        if season_service is not None:
            if season_service.season_content.whim_set is not None:
                insert_data(season_service.season_content.whim_set)
                self._registered_whimset_removal_events.add(TestEvent.SeasonChanged)
        for career in self._sim_info.career_tracker.careers.values():
            if career.whim_set is not None:
                insert_data(career.whim_set)
                self._registered_whimset_removal_events.add(TestEvent.CareerEvent)

        for skill in self._sim_info.all_skills():
            if skill.whim_set is not None:
                insert_data(skill.whim_set)

        object_manager = services.object_manager()
        for whim_set in itertools.chain(self.CONSTANT_WHIM_SETS, object_manager.active_whim_sets):
            insert_data(whim_set)

        zone_director = services.venue_service().get_zone_director()
        open_street_director = zone_director.open_street_director
        if open_street_director is not None:
            if open_street_director.whim_set is not None:
                insert_data(open_street_director.whim_set)
        services.get_event_manager().register(self, self._registered_whimset_removal_events)
        return whim_sets_with_data

    def get_whimset_target(self, whimset):
        whimset_data = self._active_whimsets_data.get(whimset)
        if whimset_data is None:
            return
        return whimset_data.target

    def get_priority(self, whimset):
        return whimset.get_priority(self._sim_info)

    def clean_up(self):
        for whim_slot in self._whim_slots:
            whim_slot.clean_up()

        self._test_results_map.clear()
        self._active_whimsets_data.clear()
        self.update_affordance_caches()

    def refresh_whim(self, whim):
        whim_slot = self._try_get_slot_by_whim(whim)
        if whim_slot is None:
            logger.error('Trying to refresh whim {} when there are no slots with that whim.', whim)
            return
        whim_slot.clear(TelemetryWhimEvents.CANCELED)
        self._populate_slots(prohibited_whims={whim.guid64})

    def toggle_whim_lock(self, whim):
        slot = self._try_get_slot_by_whim(whim)
        if slot is None:
            logger.error('Trying to toggle the lock status of a slot with whim {},but there are no slots with that whim.', whim)
            return
        slot.toggle_locked_status()
        self._send_goals_update()

    def hide_whims(self):
        if self._hidden:
            logger.error('Trying to hide whims when they are already hidden.')
            return
        self._hidden = True
        self.update_affordance_caches()
        self._send_goals_update()

    def show_whims(self, reset=False):
        if not self._hidden:
            logger.error("Trying to show whims when they aren't hidden.")
            return
        self._hidden = False
        if reset:
            self.refresh_whims()
        self.update_affordance_caches()
        self._send_goals_update()

    def refresh_whims(self, types_to_refresh=None, allow_existing_whims=False):
        prohibited_whims = set()
        need_to_send_update = False
        for whim_slot in self._whim_slots:
            if whim_slot.is_empty() or whim_slot.is_locked() or types_to_refresh is not None:
                if whim_slot.whim.type not in types_to_refresh:
                    continue
                else:
                    allow_existing_whims or prohibited_whims.add(whim_slot.whim.guid64)
                whim_slot.clear(TelemetryWhimEvents.CANCELED)
                need_to_send_update = True

        self._populate_slots(prohibited_whims=prohibited_whims)
        if need_to_send_update:
            self._send_goals_update()

    def push_whimset(self, whimset, target=None):
        if whimset.update_on_load:
            self._activate_whimset(whimset)
        else:
            whimset.whims or logger.error('Cannot add whims from an empty whimset {}', whimset)
            return
        possible_types = whimset.found_whim_types
        possible_empty_slots = [item for item in self._whim_slots if item.whim_type in possible_types if item.is_empty()]
        random.shuffle(possible_empty_slots)
        possible_full_slots = [item for item in self._whim_slots if item.whim_type in possible_types if not item.is_empty()]
        random.shuffle(possible_full_slots)
        for whim_slot in itertools.chain(possible_empty_slots, possible_full_slots):
            if self._try_populate_slot_from_whimset(whim_slot, whimset, (set()), permit_clearing_slot=True, target=target):
                self.update_affordance_caches()
                self._send_goals_update()
                return

        logger.error('Unable to add any whims from the target whimset {}', whimset)

    def add_score_multiplier(self, multiplier):
        self._score_multipliers.append(multiplier)
        self._send_goals_update()

    def get_score_multiplier(self):
        return reduce(operator.mul, self._score_multipliers, 1)

    def get_score_for_whim(self, score):
        return int(score * self.get_score_multiplier())

    def remove_score_multiplier(self, multiplier):
        if multiplier in self._score_multipliers:
            self._score_multipliers.remove(multiplier)
        self._send_goals_update()

    def on_zone_unload(self):
        return game_services.service_manager.is_traveling and self._sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED) or None
        self._whim_goal_proto = GameplaySaveData_pb2.WhimsetTrackerData()
        self.save_whims_info_to_proto((self._whim_goal_proto), copy_existing=False)
        self.clean_up()

    def get_provided_super_affordances(self):
        affordances = set()
        target_affordances = list()
        for whim_slot in self._whim_slots:
            if whim_slot.is_empty():
                continue
            whim = whim_slot.whim
            affordances.update(whim.super_affordances)
            for provided_affordance in whim.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                target_affordances.append(provided_affordance_data)

        return (
         affordances, target_affordances)

    def get_sim_info_from_provider(self):
        return self._sim_info

    def cache_whim_goal_proto(self, whim_tracker_proto, skip_load=False):
        if skip_load:
            return
        if self._sim_info.whim_tracker is None:
            return
        self._whim_goal_proto = GameplaySaveData_pb2.WhimsetTrackerData()
        self._whim_goal_proto.CopyFrom(whim_tracker_proto)

    def load_whims_info_from_proto(self):
        if self._sim_info.is_npc:
            return
        if self._whim_goal_proto is None:
            return
        need_to_send_update = False
        for whim_slot in self._whim_slots:
            if not whim_slot.is_empty():
                need_to_send_update = True
                whim_slot.clear()

        if len(self._whim_goal_proto.active_whims) > self.max_whims:
            logger.error('More whims saved than the max number of goals allowed')
            return
        aspiration_manager = services.get_instance_manager(sims4.resources.Types.ASPIRATION)
        whim_manager = services.get_instance_manager(sims4.resources.Types.WHIM)
        sim_info_manager = services.sim_info_manager()
        statistic_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for completed_whim_msg in self._whim_goal_proto.recently_completed_whims:
            whimset = aspiration_manager.get(completed_whim_msg.whimset_guid)
            if whimset is None:
                logger.info('Trying to load unavailable ASPIRATION resource: {}', completed_whim_msg.whimset_guid)
                continue
            goal = self._load_goal_from_proto_message(completed_whim_msg, sim_info_manager)
            if goal is None:
                continue
            self._completed_goals[type(goal)] = (
             goal, whimset)

        for active_whim_msg in self._whim_goal_proto.active_whims:
            if not active_whim_msg.HasField('index'):
                continue
            whimset = aspiration_manager.get(active_whim_msg.whimset_guid)
            if whimset is None:
                logger.info('Trying to load unavailable ASPIRATION resource: {}', active_whim_msg.whimset_guid)
                continue
            whim = whim_manager.get(active_whim_msg.whim_guid)
            if whim is None:
                logger.info('Trying to load unavailable WHIM resource: {}', active_whim_msg.whim_guid)
                continue
            goal = self._load_goal_from_proto_message(active_whim_msg, sim_info_manager)
            if goal is None:
                continue
            whim_index = active_whim_msg.index
            whim_slot = self._whim_slots[whim_index]
            if active_whim_msg.commodity.name_hash is not 0:
                commodity_class = statistic_manager.get(active_whim_msg.commodity.name_hash)
                if commodity_class is None:
                    logger.info('Trying to load unavailable STATISTIC resource {0} for whim {1} ', (active_whim_msg.commodity.name_hash),
                      (active_whim_msg.whim_guid),
                      owner='mjuskelis')
                    continue
                commodity_class.load_statistic_data(self._sim_info.commodity_tracker, active_whim_msg.commodity)
            whim_slot.populate_data(goal, whim, whimset)
            need_to_send_update = True
            logger.info('Whim {} loaded.', whim)

        self._whim_goal_proto = None
        if need_to_send_update:
            self.update_affordance_caches()
            self._send_goals_update()

    def save_whims_info_to_proto(self, whim_tracker_proto, copy_existing=True):
        if self._sim_info.is_npc or copy_existing:
            if self._whim_goal_proto is not None:
                whim_tracker_proto.CopyFrom(self._whim_goal_proto)
                return
        for goal, whimset in self._completed_goals.values():
            with ProtocolBufferRollback(whim_tracker_proto.recently_completed_whims) as (recently_completed_whim_msg):
                recently_completed_whim_msg.whimset_guid = whimset.guid64
                goal_seed = goal.create_seedling()
                goal_seed.finalize_creation_for_save()
                goal_seed.serialize_to_proto(recently_completed_whim_msg.goal_data)

        for index, whim_slot in enumerate(self._whim_slots):
            if whim_slot.is_empty():
                continue
            with ProtocolBufferRollback(whim_tracker_proto.active_whims) as (active_whim_msg):
                active_whim_msg.whimset_guid = whim_slot.whimset.guid64
                active_whim_msg.whim_guid = whim_slot.whim.guid64
                active_whim_msg.index = index
                if whim_slot.commodity is not None:
                    active_whim_msg.commodity = whim_slot.commodity.get_save_message(self._sim_info.commodity_tracker)
                goal_seed = whim_slot.goal_instance.create_seedling()
                goal_seed.finalize_creation_for_save()
                goal_seed.serialize_to_proto(active_whim_msg.goal_data)

        for key in self._active_whimsets_data.keys():
            whim_tracker_proto.active_whimset_guids.append(key.guid64)

    def debug_activate_whimset(self, whimset, chained):
        if not whimset.update_on_load:
            return
        self._activate_whimset(whimset)

    def debug_activate_whim(self, whim, target_info=None):
        whim_slot = self._whim_slots[0]
        if not whim_slot.is_empty():
            whim_slot.clear(TelemetryWhimEvents.CHEAT_CLEAR)
        else:
            goal_factory = whim.goal
            if target_info is not None:
                if goal_factory.IS_TARGETED:
                    goal_factory._target_option = SituationGoalSimTargetingOptions.DebugChoice
            goal = whim.goal(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()),
              inherited_target_sim_info=target_info)
            active_whimsets = self.get_active_whimset_data().keys()
            whimset = None
            if active_whimsets:
                whimset = next(iter(active_whimsets))
            else:
                aspiration_manager = services.get_instance_manager(sims4.resources.Types.ASPIRATION)
            whimset = next(iter(aspiration_manager.all_whim_sets_gen()))
        if whimset is None:
            logger.error('Unable to find any whimsets to use for cheated whim.')
            return
        whim_slot.populate_data(goal, whim, whimset)
        self.update_affordance_caches()
        self._send_goals_update()

    def debug_offer_whim_from_whimset(self, whimset):
        self.push_whimset(whimset)

    def debug_complete_whim(self, whim):
        whim_slot = self._try_get_slot_by_whim(whim)
        if whim_slot is None:
            return
        whim_slot.goal_instance.force_complete()

    def debug_clear_whim(self, whim):
        whim_slot = self._try_get_slot_by_whim(whim)
        if whim_slot is None:
            return
        whim_slot.clear(TelemetryWhimEvents.CHEAT_CLEAR)
        self._send_goals_update()

    def handle_event(self, sim_info, event, resolver):
        if self._sim_info.sim_id == sim_info.sim_id:
            self._remove_whims_with_absent_whimset()

    def _remove_whims_with_absent_whimset(self):
        active_whimset_data = self.get_active_whimset_data()
        needs_update = False
        for slot in self._whim_slots:
            if slot.whimset not in active_whimset_data:
                slot.clear(TelemetryWhimEvents.NO_LONGER_AVAILABLE)
                needs_update = True

        if needs_update:
            self._send_goals_update()

    def _load_goal_from_proto_message(self, proto_message, sim_info_manager):
        goal_seed = GoalSeedling.deserialize_from_proto(proto_message.goal_data)
        if goal_seed is None:
            return
        target_sim_info = None
        if goal_seed.target_id:
            target_sim_info = sim_info_manager.get(goal_seed.target_id)
            if target_sim_info is None:
                return
        secondary_sim_info = None
        if goal_seed.secondary_target_id:
            secondary_sim_info = sim_info_manager.get(goal_seed.secondary_target_id)
            if secondary_sim_info is None:
                return
        return goal_seed.goal_type(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()),
          inherited_target_sim_info=target_sim_info,
          secondary_sim_info=secondary_sim_info,
          count=(goal_seed.count),
          reader=(goal_seed.reader),
          locked=(goal_seed.locked))

    @property
    def _number_of_empty_slots(self):
        return sum((1 for whim_slot in self._whim_slots if whim_slot.is_empty()))

    def _get_currently_active_whim_guids(self):
        return {whim_slot.whim.guid64 for whim_slot in self._whim_slots if not whim_slot.is_empty()}

    def _get_currently_used_whimsets(self):
        return {whim_slot.whimset for whim_slot in self._whim_slots if whim_slot.whimset is not None}

    def _try_get_slot_by_whim(self, whim):
        for whim_slot in self._whim_slots:
            if whim is whim_slot.whim:
                return whim_slot

    def _try_get_targets_from_whimset(self, whimset):
        primary_target = None
        secondary_target = None
        if whimset.force_target is None:
            whimset_data = self._active_whimsets_data.get(whimset)
            if whimset_data is not None:
                primary_target = whimset_data.target
            else:
                primary_target = None
        else:
            primary_target = whimset.force_target(self._sim_info)
            if primary_target is None:
                return
        if whimset.secondary_target is not None:
            secondary_target = whimset.secondary_target(self._sim_info)
            if secondary_target is None:
                return
        return (
         primary_target, secondary_target)

    def _deactivate_whimset(self, whimset):
        if whimset not in self._active_whimsets_data:
            return
        logger.info('Deactivating Whimset {}', whimset)
        if whimset.timeout_retest is not None:
            resolver = event_testing.resolver.SingleSimResolver(self._sim_info)
            if resolver(whimset.timeout_retest.objective_test):
                self._activate_whimset(whimset)
                return
        del self._active_whimsets_data[whimset]
        if self._sim_info.aspiration_tracker is not None:
            self._sim_info.aspiration_tracker.reset_milestone(whimset)
        self._sim_info.remove_statistic(whimset.priority_commodity)

    def _activate_whimset(self, whimset, target=None, chained=False):
        if chained:
            new_priority = whimset.chained_priority
        else:
            new_priority = whimset.activated_priority
        if new_priority == 0:
            return
        else:
            self._sim_info.set_stat_value((whimset.priority_commodity), new_priority, add=True)
            whimset_data = self._active_whimsets_data.get(whimset)
            if whimset_data is None:
                stat = self._sim_info.get_stat_instance(whimset.priority_commodity)
                threshold = Threshold(whimset.priority_commodity.convergence_value, operator.le)

                def remove_active_whimset(_):
                    self._deactivate_whimset(whimset)

                callback_data = stat.create_and_add_callback_listener(threshold, remove_active_whimset)
                self._active_whimsets_data[whimset] = _ActiveWhimsetData(target, callback_data)
                stat.decay_enabled = True
                logger.info('Setting whimset {} to active at priority {}.', whimset, new_priority)
            else:
                logger.info('Setting whimset {} which is already active to new priority value {}.', whimset, new_priority)

    def _on_goal_completed(self, whim_slot, goal):
        parent_whimset = whim_slot.whimset
        whim = whim_slot.whim
        goal_type = type(goal)
        self._completed_goals[goal_type] = (goal, parent_whimset)
        inherited_target_sim_info = goal.get_actual_target_sim_info()
        whim_slot.clear(TelemetryWhimEvents.COMPLETED)
        services.get_event_manager().process_event((test_events.TestEvent.WhimCompleted), sim_info=(self._sim_info),
          whim_completed=whim)
        chain_data = {}
        if whim.chaining_whimset_chance_multiplier is None:
            self._deactivate_whimset(parent_whimset)
        else:
            chain_data[parent_whimset.guid64] = whim.chaining_whimset_chance_multiplier
        op = distributor.ops.SetWhimComplete(whim.guid64)
        Distributor.instance().add_op(self._sim_info, op)
        score = self.get_score_for_whim(goal.score)
        self._sim_info.apply_satisfaction_points_delta(score, (SetWhimBucks.WHIM), source=(goal.guid64))
        logger.info('Goal completed: {}, from whim {}, from Whim Set: {}', goal, whim, parent_whimset)
        self._populate_slots(prohibited_whims={whim.guid64}, whimset_weight_multipliers=chain_data)
        self._send_goals_update()

    def _try_populate_slot_from_whimset(self, slot, whimset, prohibited_whims, permit_clearing_slot=False, target=None):
        targets = self._try_get_targets_from_whimset(whimset)
        if targets is None:
            return False
        primary_target, secondary_target = targets
        if primary_target is None:
            if target is not None:
                primary_target = target
        sim = self._sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED)
        disallowed_whims = self._get_currently_active_whim_guids() | prohibited_whims
        whim_buckets = self._generate_whim_buckets_for_type_and_whimset(slot.whim_type, whimset, disallowed_whims)
        for weighted_whims in whim_buckets:
            while weighted_whims:
                selected_whim = sims4.random.pop_weighted(weighted_whims)
                selected_goal = selected_whim.goal
                old_goal_instance_and_whimset = self._completed_goals.get(selected_goal)
                if old_goal_instance_and_whimset is not None:
                    if old_goal_instance_and_whimset[0].is_on_cooldown():
                        continue
                pretest = False
                try:
                    pretest = selected_goal.can_be_given_as_goal(sim, None, inherited_target_sim_info=primary_target)
                except Exception as inst:
                    try:
                        logger.exception('Exception encountered while running pretest for whim {}: {}', selected_whim, inst)
                    finally:
                        inst = None
                        del inst

                if pretest:
                    goal = selected_goal(sim_info=(self._sim_info), goal_id=(self._goal_id_generator()),
                      inherited_target_sim_info=primary_target,
                      secondary_sim_info=secondary_target)
                    with telemetry_helper.begin_hook(whim_telemetry_writer, TELEMETRY_HOOK_WHIM_EVENT, sim_info=(self._sim_info)) as (hook):
                        hook.write_int(TELEMETRY_WHIM_EVENT_TYPE, TelemetryWhimEvents.ADDED)
                        hook.write_guid(TELEMETRY_WHIM_GUID, goal.guid64)
                        if selected_whim.type is WhimType.CONFRONTATION:
                            corresponding_trait = self._try_get_source_fear_from_whimset(whimset)
                            if corresponding_trait is None:
                                logger.error('Unable to send telemetry for confrontation whim {} in whimset {} beingadded: could not find corresponding fear trait.', selected_whim, whimset)
                                return False
                            hook.write_guid(TELEMETRY_WHIM_FEAR_TRAIT_GUID, corresponding_trait.guid64)
                    if permit_clearing_slot:
                        if not slot.is_empty():
                            slot.clear(TelemetryWhimEvents.CANCELED)
                    slot.populate_data(goal, selected_whim, whimset)
                    return True

        return False

    def _try_get_source_fear_from_whimset(self, whimset):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        for trait in trait_manager.types.values():
            if trait.trait_type != TraitType.FEAR or trait.whim_set != whimset:
                continue
            return trait

    def _generate_whim_buckets_for_type_and_whimset(self, whim_type, whimset, disallowed_whim_guids):
        if len(whimset.whims) == 0:
            return ()
        ordered_buckets = []
        ordered_types = [
         whim_type]
        if whim_type in self.WHIM_TYPE_CONFIGURATION:
            ordered_types.extend(self.WHIM_TYPE_CONFIGURATION[whim_type].fallback_types)
        for ordered_type in ordered_types:
            bucket = []
            for entry in whimset.whims:
                if not entry.whim.guid64 in disallowed_whim_guids:
                    if entry.whim.type is not ordered_type:
                        continue
                    else:
                        bucket.append((entry.weight, entry.whim))

            if bucket:
                ordered_buckets.append(bucket)

        return ordered_buckets

    def _populate_slots(self, prohibited_whimsets=EMPTY_SET, prohibited_whims=EMPTY_SET, whimset_weight_multipliers=None):
        if not self._enabled:
            return
        else:
            if self._number_of_empty_slots == 0:
                return
            if self._sim_info.is_npc:
                return
            return self._sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS_EXCEPT_UNINITIALIZED) or None
        if services.current_zone().is_zone_shutting_down:
            return
        need_to_send_update = False
        for whim_slot in self._whim_slots:
            if whim_slot.is_empty():
                if not whim_slot.roll_chance_to_populate():
                    continue
                possible_whimset_data = self.get_active_whimset_data()
                possible_whimsets = possible_whimset_data.keys()
                possible_whimsets -= self._get_currently_used_whimsets()
                possible_whimsets -= prohibited_whimsets
                prioritized_whimsets = []
                for whimset in possible_whimsets:
                    priority = self.get_priority(whimset)
                    if whimset_weight_multipliers is not None:
                        priority *= whimset_weight_multipliers.get(whimset.guid64, 1)
                    prioritized_whimsets.append((priority, whimset))

                while prioritized_whimsets:
                    whimset = sims4.random.pop_weighted(prioritized_whimsets)
                    if whimset is None:
                        break
                    all_targets = list(possible_whimset_data[whimset].targets)
                    if len(all_targets) <= 0:
                        if self._try_populate_slot_from_whimset(whim_slot, whimset, prohibited_whims):
                            need_to_send_update = True
                            break
                    target_found = False
                    for fallback_target in all_targets:
                        if self._try_populate_slot_from_whimset(whim_slot, whimset, prohibited_whims, target=fallback_target):
                            need_to_send_update = True
                            target_found = True
                            break

                    if target_found:
                        break

        if need_to_send_update:
            self.update_affordance_caches()
            self._send_goals_update()

    def _send_goals_update(self):
        logger.debug('Sending whims update for {}.  Current slots: {}', (self._sim_info),
          (self._whim_slots),
          owner='mjuskelis')
        current_whims = []
        for whim_slot in self._whim_slots:
            whim_goal = DistributorOps_pb2.WhimGoal()
            whim_goal.slot_whim_type = whim_slot.whim_type
            if not whim_slot.is_empty():
                if self._hidden:
                    current_whims.append(whim_goal)
                    continue
                goal = whim_slot.goal_instance
                goal_whimset = whim_slot.whimset
                goal_target = goal.get_required_target_sim_info()
                goal_target_id = goal_target.id if goal_target is not None else 0
                whim_goal.whim_guid64 = whim_slot.whim.guid64
                whim_name = goal.get_display_name()
                if whim_name is not None:
                    whim_goal.whim_name = whim_name
                whim_goal.whim_score = self.get_score_for_whim(goal.score)
                whim_goal.whim_noncancel = goal.noncancelable
                whim_display_icon = goal.display_icon
                if whim_display_icon is not None:
                    whim_goal.whim_icon_key.type = whim_display_icon.type
                    whim_goal.whim_icon_key.group = whim_display_icon.group
                    whim_goal.whim_icon_key.instance = whim_display_icon.instance
                whim_goal.whim_goal_count = goal.max_iterations
                whim_goal.whim_current_count = goal.completed_iterations
                whim_goal.whim_target_sim = goal_target_id
                whim_tooltip = goal.get_display_tooltip()
                if whim_tooltip is not None:
                    whim_goal.whim_tooltip = whim_tooltip
                localization_tokens = goal.get_localization_tokens()
                whim_goal.whim_tooltip_reason = (goal_whimset.whim_reason)(*localization_tokens)
                whim_goal.whim_locked = goal.locked
                whim_type = whim_slot.whim.type
                can_lock = True
                if whim_type in self.WHIM_TYPE_CONFIGURATION:
                    can_lock = self.WHIM_TYPE_CONFIGURATION[whim_type].can_be_locked
                whim_goal.whim_can_lock = can_lock
                whim_goal.whim_type = whim_type
                fluff_description = whim_slot.whim.fluff_description
                if fluff_description is not None:
                    whim_goal.whim_fluff_text = fluff_description(*localization_tokens)
                current_whims.append(whim_goal)

        self._sim_info.current_whims = current_whims

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def on_lod_update(self, old_lod, new_lod):
        if new_lod < self._tracker_lod_threshold:
            self.clean_up()
        else:
            if old_lod < self._tracker_lod_threshold:
                sim_msg = services.get_persistence_service().get_sim_proto_buff(self._sim_info.id)
                if sim_msg is not None:
                    self.cache_whim_goal_proto(sim_msg.gameplay_data.whim_tracker)