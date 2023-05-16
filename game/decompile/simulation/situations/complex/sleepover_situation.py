# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\sleepover_situation.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 19202 bytes
import build_buy, services, sims4
from autonomy.autonomy_preference import ObjectPreferenceTag
from event_testing.test_events import TestEvent
from interactions import ParticipantType
from interactions.context import InteractionContext
from interactions.priority import Priority
from objects.system import create_object
from random import choice
from sims.sim_info_types import Age
from sims4.log import Logger
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableSet, OptionalTunable, TunableEnumEntry, Tunable
from sims4.tuning.tunable_base import GroupNames
from situations.situation_complex import SituationComplexCommon, CommonSituationState, TunableInteractionOfInterest, SituationStateData, InteractionOfInterest
from situations.situation_zone_director_mixin import SituationZoneDirectorMixin
from venues.venue_constants import ZoneDirectorRequestType
logger = Logger('SleepoverSituation', default_owner='jmoline')

class _PreSleepState(CommonSituationState):
    FACTORY_TUNABLES = {'ask_to_set_up_sleeping_bag_interaction':TunableInteractionOfInterest(description='\n            When run, the targetted Sim will have a sleeping bag created for them in their inventory that the situation \n            will claim and assign to them, and the Sim will attempt to swipe it into world.\n            '), 
     'sleeping_bag_definitions':TunableSet(description='\n            The sleeping bag object that NPC sims will create (unless they are toddlers).\n            ',
       minlength=1,
       tunable=TunableReference(services.get_instance_manager(Types.OBJECT))), 
     'toddler_sleeping_bag_definitions':TunableSet(description='\n            The sleeping bag object that toddler NPC sims will create.\n            ',
       minlength=1,
       tunable=TunableReference(services.get_instance_manager(Types.OBJECT))), 
     'add_sleeping_bag_to_world_interaction':TunableReference(description='\n            Interaction pushed on Sims to place sleeping bag into the world.  \n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'time_for_bed_interaction':TunableInteractionOfInterest(description='\n            When time for bed interaction is called, we will move to the sleep state.\n            '), 
     'setup_sleeping_bags_for_all_sims':Tunable(description='\n            If True, create sleeping bags for all situation sims instead of\n            just the clicked sim.\n            ',
       tunable_type=bool,
       default=False), 
     'locked_args':{'time_out': None}}

    def __init__(self, *args, **kwargs):
        super_kwargs = dict(kwargs)
        for my_kwarg_key, my_kwarg_value in kwargs.items():
            if my_kwarg_key not in self.FACTORY_TUNABLES:
                continue
            del super_kwargs[my_kwarg_key]
            setattr(self, my_kwarg_key, my_kwarg_value)

        self.add_sleeping_bag_to_world = InteractionOfInterest(affordances=(
         self.add_sleeping_bag_to_world_interaction,),
          tags=(frozenset()))
        (super().__init__)(*args, **super_kwargs)

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        custom_keys = set()
        custom_keys.update(self.ask_to_set_up_sleeping_bag_interaction.custom_keys_gen())
        custom_keys.update(self.add_sleeping_bag_to_world.custom_keys_gen())
        custom_keys.update(self.time_for_bed_interaction.custom_keys_gen())
        for custom_key in custom_keys:
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

        custom_keys = set()
        custom_keys.update(self.add_sleeping_bag_to_world.custom_keys_gen())
        for custom_key in custom_keys:
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            if resolver(self.time_for_bed_interaction):
                logger.info('Time for bed interaction {} on {} complete for {}.', resolver.interaction, sim_info, self.owner)
                self._change_state(self.owner.sleep_state())
            else:
                if resolver(self.ask_to_set_up_sleeping_bag_interaction):
                    if self.setup_sleeping_bags_for_all_sims:
                        for situation_sim in self.owner.all_sims_in_situation_gen():
                            self._setup_sleeping_bag(situation_sim.sim_info)

                    else:
                        target_sim_info = resolver.get_participant(ParticipantType.TargetSim)
                        if sim_info is not target_sim_info and target_sim_info is not None:
                            logger.info('Setup sleeping bag interaction {} on {} to {} complete for {}.', resolver.interaction, sim_info, target_sim_info, self.owner)
                            self._setup_sleeping_bag(target_sim_info)
        else:
            if event == TestEvent.InteractionExitedPipeline:
                if resolver(self.add_sleeping_bag_to_world):
                    sleeping_bag_id = resolver.interaction.target.id
                    if services.object_manager().get(sleeping_bag_id) is None:
                        logger.warn('Add sleeping bag to world interaction {} on {} done for {}. Sleeping bag not found in world, removing sleeping bag.', resolver.interaction, sim_info, self.owner)
                        self.owner.remove_sleeping_bag(sim_info.id)
                    else:
                        logger.info('Add sleeping bag to world interaction {} on {} done for {}. Sleeping bag found in world.', resolver.interaction, sim_info, self.owner)

    def _setup_sleeping_bag(self, target_sim_info):
        existing_sleeping_bag_id = self.owner._object_ids.get(target_sim_info.id)
        if existing_sleeping_bag_id:
            if services.current_zone().find_object(existing_sleeping_bag_id):
                return
            logger.warn('Sleeping bag already tracked for sim {}, but could not find it creating new sleeping bag.', target_sim_info)
        target_sim = target_sim_info.get_sim_instance()
        if target_sim is None:
            return
        possible_objects = self.toddler_sleeping_bag_definitions if target_sim.age == Age.TODDLER else self.sleeping_bag_definitions
        def_to_create = choice(tuple(possible_objects))
        sleeping_bag = create_object(def_to_create)
        if sleeping_bag is None:
            logger.error('Failed to create a sleeping bag for {}.', target_sim)
            return
        sleeping_bag.current_value = 0
        if sleeping_bag.objectrelationship_component is not None:
            if not sleeping_bag.objectrelationship_component.add_relationship(target_sim.id):
                logger.error('Failed to add object relationship for {} and sleeping bag.', target_sim)
                sleeping_bag.destroy()
                return
        if not target_sim.inventory_component.player_try_add_object(sleeping_bag):
            logger.error("Failed to add {} to {}'s inventory, check whether sleeping bag is inventoryable.", sleeping_bag, target_sim)
            sleeping_bag.destroy()
            return
        if not target_sim.push_super_affordance(self.add_sleeping_bag_to_world_interaction, sleeping_bag, InteractionContext(target_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)):
            logger.error("Failed to run {} for {}'s sleeping bag.", self.add_sleeping_bag_to_world, target_sim)
            sleeping_bag.destroy()
            return
        self.owner.track_sleeping_bag(target_sim.id, sleeping_bag.id)
        sleeping_bag.update_ownership(services.get_active_sim())


class _SleepState(CommonSituationState):
    FACTORY_TUNABLES = {'time_to_wake_up_interaction': TunableInteractionOfInterest(description='\n            When any interaction here is run, we transition to the post-sleep state.\n            ')}

    def __init__(self, *args, time_to_wake_up_interaction=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.time_to_wake_up_interaction = time_to_wake_up_interaction

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        for custom_key in self.time_to_wake_up_interaction.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            if resolver(self.time_to_wake_up_interaction):
                if self.owner.is_sim_info_in_situation(sim_info):
                    self._change_state(self.owner.postsleep_state())

    def timer_expired(self):
        self._change_state(self.owner.postsleep_state())


class _PostSleepState(CommonSituationState):
    pass


class SleepoverSituation(SituationZoneDirectorMixin, SituationComplexCommon):
    INSTANCE_TUNABLES = {'presleep_state':_PreSleepState.TunableFactory(display_name='1. Pre-Sleep State',
       tuning_group=GroupNames.STATE), 
     'sleep_state':_SleepState.TunableFactory(display_name='2. Sleep State',
       tuning_group=GroupNames.STATE), 
     'postsleep_state':_PostSleepState.TunableFactory(display_name='3. Post-Sleep State',
       tuning_group=GroupNames.STATE), 
     'sleeping_bag_autonomy_preference_tag':OptionalTunable(description='\n            If enabled, this autonomy preference will be set on the sim for the created sleeping bag.\n            ',
       tunable=TunableEnumEntry(description='\n                The preference tag associated with the sleeping bag autonomy preference.\n                ',
       tunable_type=ObjectPreferenceTag,
       default=(ObjectPreferenceTag.INVALID),
       invalid_enums=(
      ObjectPreferenceTag.INVALID,)),
       tuning_group=GroupNames.AUTONOMY)}
    OBJECT_IDS = 'object_ids'
    OWNER_IDS = 'owner_ids'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._object_ids = dict()
        reader = self._seed.custom_init_params_reader
        if reader is not None:
            object_ids = reader.read_uint64s(self.OBJECT_IDS, ())
            owner_ids = reader.read_uint64s(self.OWNER_IDS, ())
            for sim_id, sleeping_bag_id in zip(owner_ids, object_ids):
                if sim_id is None or sleeping_bag_id is None:
                    logger.error('Unmatched sim/sleeping bag id pair {} => {} while loading {}.', sim_id, sleeping_bag_id, self)
                elif not services.sim_info_manager().is_sim_id_valid(sim_id):
                    logger.warn('Culling invalid owner {} while loading {}.', sim_id, self)
                else:
                    self.track_sleeping_bag(sim_id, sleeping_bag_id)

    @classmethod
    def _states(cls):
        return [
         SituationStateData(0, _PreSleepState, factory=(cls.presleep_state)),
         SituationStateData(1, _SleepState, factory=(cls.sleep_state)),
         SituationStateData(2, _PostSleepState, factory=(cls.postsleep_state))]

    @classmethod
    def get_possible_zone_ids_for_situation(cls, host_sim_info=None, guest_ids=None):
        possible_zones = []
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_service = services.current_zone().venue_service
        for venue_tuning in cls.compatible_venues:
            if venue_tuning.is_residential:
                if host_sim_info is not None:
                    home_zone_id = host_sim_info.household.home_zone_id
                    home_venue_tuning = venue_manager.get(build_buy.get_current_venue(home_zone_id))
                    if home_venue_tuning.is_residential:
                        possible_zones.append(home_zone_id)
            else:
                possible_zones.extend(venue_service.get_zones_for_venue_type_gen(venue_tuning))

        return possible_zones

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.presleep_state._tuned_values.job_and_role_changes.items())

    @classmethod
    def get_zone_director_request(cls, host_sim_info=None, zone_id=None):
        if host_sim_info is None or zone_id is None or host_sim_info.household.home_zone_id != zone_id:
            return super().get_zone_director_request(host_sim_info=host_sim_info, zone_id=zone_id)
        return (None, None)

    @classmethod
    def _get_zone_director_request_type(cls):
        return ZoneDirectorRequestType.SOCIAL_EVENT

    def start_situation(self):
        super().start_situation()
        self._change_state(self.presleep_state())

    def _destroy(self):
        super()._destroy()
        self.remove_all_sleeping_bags()
        if self.sleeping_bag_autonomy_preference_tag is not None:
            services.object_preference_overrides_tracker().remove_provider_preference_tag_overrides(self)

    def _on_remove_sim_from_situation(self, sim):
        super()._on_remove_sim_from_situation(sim)
        self.remove_sleeping_bag(sim.id)

    def track_sleeping_bag(self, sim_id, sleeping_bag_id):
        self._object_ids[sim_id] = sleeping_bag_id
        self._claim_object(sleeping_bag_id)
        if self.sleeping_bag_autonomy_preference_tag is not None:
            services.object_preference_overrides_tracker().add_preference_tag_override(self, sim_id, sleeping_bag_id, self.sleeping_bag_autonomy_preference_tag)

    def remove_all_sleeping_bags(self):
        if not self._object_ids:
            return
        for sim_id in tuple(self._object_ids):
            self.remove_sleeping_bag(sim_id)

        self._object_ids.clear()

    def remove_sleeping_bag(self, sim_id):
        if sim_id not in self._object_ids:
            return
        sleeping_bag_id = self._object_ids[sim_id]
        self._object_ids.pop(sim_id, None)
        sleeping_bag = services.object_manager().get(sleeping_bag_id)
        if sleeping_bag is None:
            sleeping_bag = services.inventory_manager().get(sleeping_bag_id)
            if sleeping_bag is None:
                logger.error('Could not find created sleeping bag {} for {} in object_manager or inventory_manager for {}.', sleeping_bag_id, services.sim_info_manager().get(sim_id), self)
        if sleeping_bag is not None:
            sleeping_bag.make_transient()
        if self.sleeping_bag_autonomy_preference_tag is not None:
            services.object_preference_overrides_tracker().remove_preference_tag_override(self, sim_id, sleeping_bag_id, self.sleeping_bag_autonomy_preference_tag)

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if not self._object_ids:
            return
        owner_ids, object_ids = zip(*self._object_ids.items())
        writer.write_uint64s(self.OBJECT_IDS, object_ids)
        writer.write_uint64s(self.OWNER_IDS, owner_ids)