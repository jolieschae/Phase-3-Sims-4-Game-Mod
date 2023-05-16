# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\laundry\laundry_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 12967 bytes
from _weakrefset import WeakSet
import random
from event_testing.register_test_event_mixin import RegisterTestEventMixin
from event_testing.resolver import SingleSimResolver, DoubleObjectResolver
from event_testing.test_events import TestEvent
from laundry.laundry_tuning import LaundryTuning
from objects.system import create_object
from sims4.common import Pack
from sims4.service_manager import Service
from sims4.utils import classproperty
from singletons import DEFAULT, UNSET
import primitives, services, sims4.log
logger = sims4.log.Logger('Laundry', default_owner='mkartika')

class LaundryService(RegisterTestEventMixin, Service):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._laundry_hero_objects = WeakSet()
        self._hampers = WeakSet()
        self._affected_household = None
        self._hero_object_exist_before_bb = False

    @classproperty
    def required_packs(cls):
        return (Pack.SP13,)

    @property
    def hero_object_exist(self):
        if self._laundry_hero_objects:
            return True
        return False

    @property
    def laundry_hero_objects(self):
        return self._laundry_hero_objects

    @property
    def hampers(self):
        return self._hampers

    @property
    def affected_household(self):
        return self._affected_household

    def _get_affected_household(self):
        household = services.active_household()
        if household is None:
            return
        if household.home_zone_id != services.current_zone_id():
            return
        return household

    def _find_hamper_and_laundry_objects(self):
        object_manager = services.object_manager()
        self._laundry_hero_objects = WeakSet((object_manager.get_objects_with_tags_gen)(*LaundryTuning.LAUNDRY_HERO_OBJECT_TAGS))
        if self._affected_household is None:
            return
        self._hampers = WeakSet((object_manager.get_objects_with_tags_gen)(*LaundryTuning.HAMPER_OBJECT_TAGS))

    def _find_closest_hamper(self, sim, hampers):
        estimate_distance = primitives.routing_utils.estimate_distance_helper
        if not hampers:
            return
        return min(hampers, key=(lambda h: estimate_distance(sim, h)))

    def _add_clothing_pile_to_hamper(self, sim, resolver, initial_states=DEFAULT):
        if not self._hampers:
            return False
        else:
            full_hamper_state = LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.full_hamper_state
            available_hampers = set((obj for obj in self._hampers if not obj.state_value_active(full_hamper_state)))
            if not available_hampers:
                return False
            return LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.tests.run_tests(resolver) or False
        if random.random() > LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.chance:
            return True
        obj_def = LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.clothing_pile.definition
        if obj_def is None:
            logger.error('Failed to create clothing pile on hamper for {} because the pile definition is None.', sim)
            return False
        obj = None
        try:
            try:
                obj = create_object(obj_def)
            except:
                logger.error('Failed to create clothing pile {} on hamper for {}.', obj_def, sim)
                if obj is not None:
                    obj.destroy(source=self, cause='Transferred to hamper.')
                return False

        finally:
            if initial_states is DEFAULT:
                initial_states = LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.clothing_pile.initial_states
            for initial_state in initial_states:
                if initial_state.tests.run_tests(resolver):
                    state_val = initial_state.state
                    if obj.has_state(state_val.state):
                        obj.set_state(state_val.state, state_val)

            closest_hamper = self._find_closest_hamper(sim, available_hampers)
            resolver = DoubleObjectResolver(obj, closest_hamper)
            for loot_action in LaundryTuning.PUT_CLOTHING_PILE_ON_HAMPER.loots_to_apply:
                loot_action.apply_to_resolver(resolver)

            obj.destroy(source=self, cause='Transferred to hamper.')

        return True

    def _generate_clothing_pile_on_ground(self, sim, resolver, ground_pile_loot=DEFAULT):
        loot = LaundryTuning.GENERATE_CLOTHING_PILE.loot_to_apply if ground_pile_loot is DEFAULT else ground_pile_loot
        if loot is not None:
            loot.apply_to_resolver(resolver)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            self._update_last_unload_laundry_time()
            self._update_finished_laundry_condition(resolver)

    def _update_last_unload_laundry_time(self):
        if self._affected_household is None:
            return
        self._affected_household.laundry_tracker.update_last_unload_laundry_time()

    def _update_finished_laundry_condition(self, resolver):
        if self._affected_household is None:
            return
        self._affected_household.laundry_tracker.update_finished_laundry_condition(resolver)

    def generate_clothing_pile(self, sim, resolver, initial_states=DEFAULT, ground_pile_loot=DEFAULT):
        if sim.on_home_lot:
            if not self._add_clothing_pile_to_hamper(sim, resolver, initial_states=initial_states):
                self._generate_clothing_pile_on_ground(sim, resolver, ground_pile_loot=ground_pile_loot)

    def is_sim_eligible_for_laundry(self, sim):
        return self._affected_household is None or self.hero_object_exist or False
        if sim.sim_info.is_pet:
            return False
        if sim.household is not self._affected_household:
            return False
        return True

    def on_spin_outfit_change(self, sim, outfit_category_and_index, interaction):
        if not self.is_sim_eligible_for_laundry(sim):
            return
            no_pile_tag = LaundryTuning.GENERATE_CLOTHING_PILE.no_pile_interaction_tag
            if no_pile_tag in interaction.get_category_tags():
                return
        else:
            current_outfit = sim.sim_info.get_current_outfit()[0]
            target_outfit = outfit_category_and_index[0]
            no_pile_outfits = LaundryTuning.GENERATE_CLOTHING_PILE.no_pile_outfit_category
            naked_outfits = LaundryTuning.GENERATE_CLOTHING_PILE.naked_outfit_category
            if current_outfit not in no_pile_outfits:
                if current_outfit not in naked_outfits and target_outfit not in no_pile_outfits:
                    self.generate_clothing_pile(sim, interaction.get_resolver())
        if target_outfit not in naked_outfits:
            self._affected_household.laundry_tracker.apply_laundry_effect(sim)

    def on_service_enabled(self):
        self._affected_household.laundry_tracker.update_last_unload_laundry_time()

    def on_service_disabled(self):
        self._affected_household.laundry_tracker.reset()

    def on_build_buy_enter(self):
        self._hero_object_exist_before_bb = self.hero_object_exist

    def on_build_buy_exit(self):
        self._find_hamper_and_laundry_objects()
        if self._affected_household is not None:
            if self._hero_object_exist_before_bb != self.hero_object_exist:
                if self.hero_object_exist:
                    self.on_service_enabled()
                else:
                    self.on_service_disabled()

    def on_loading_screen_animation_finished(self):
        self._affected_household = self._get_affected_household()
        self._find_hamper_and_laundry_objects()

    def on_zone_load(self):
        interaction_tag = LaundryTuning.PUT_AWAY_FINISHED_LAUNDRY.interaction_tag
        self._register_test_event(TestEvent.InteractionComplete, interaction_tag)

    def on_zone_unload(self):
        self._unregister_for_all_test_events()