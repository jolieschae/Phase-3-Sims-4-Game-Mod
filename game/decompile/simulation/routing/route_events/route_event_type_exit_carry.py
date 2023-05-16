# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_type_exit_carry.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 8291 bytes
from animation.arb import Arb
from animation.arb_element import distribute_arb_element
from carry.carry_elements import CarryElementHelper
from element_utils import build_element, build_critical_section_with_finally
from interactions.constraints import GLOBAL_STUB_CARRY_TARGET
from routing.route_events.route_event_type_create_carry import _RouteEventTypeCarry
from sims4.tuning.tunable import TunableEnumWithFilter
from tag import Tag
import services, sims4.log
logger = sims4.log.Logger('RouteEvents', default_owner='bosee')

class RouteEventTypeExitCarry(_RouteEventTypeCarry):
    FACTORY_TUNABLES = {'stop_carry_object_tag': TunableEnumWithFilter(description='\n            Tag used to find the object to stop carrying.\n            ',
                                tunable_type=Tag,
                                default=(Tag.INVALID),
                                invalid_enums=(
                               Tag.INVALID,),
                                filter_prefixes=('func', ))}

    @classmethod
    def _verify_tuning_callback(cls, event_data_tuning):
        if len(event_data_tuning.animation_elements) > 1:
            logger.error('RouteEventTypeExitCarry currently only supports a single animation element')

    @classmethod
    def _get_tuning_suggestions(cls, event_data_tuning, print_suggestion):
        print_suggestion('Exit carry route events are highly risky as they cause posture transitions outside the normal transition sequence. This can cause resets and red text when combined with various other circumstances. See umbrellas.', owner='rrodgers')

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._owned_object = None
        self._actually_run_prepare = self._duration_override is None
        self._override_valid_for_scheduling = not self._actually_run_prepare

    @classmethod
    def test(cls, actor, event_data_tuning):
        return super().test(actor, event_data_tuning, ignore_carry=True)

    def prepare(self, actor):
        if not self._actually_run_prepare:
            self._actually_run_prepare = True
            return True

        def set_target(asm):
            asm.set_current_state('entry')
            asm.set_actor(self.animation_elements[0].actor_name, actor)
            asm.set_actor(self.animation_elements[0].target_name, GLOBAL_STUB_CARRY_TARGET)
            return True

        super().prepare(actor, setup_asm_override=set_target)

    def is_valid_for_scheduling(self, actor, path):
        if self._override_valid_for_scheduling:
            return True
        return super().is_valid_for_scheduling(actor, path)

    def should_remove_on_execute(self):
        return False

    def _execute_internal(self, actor):
        left_carry_target = actor.posture_state.left.target
        right_carry_target = actor.posture_state.right.target
        carry_target = None
        if left_carry_target is not None and left_carry_target.has_tag(self.stop_carry_object_tag):
            carry_target = left_carry_target
        else:
            if right_carry_target is not None:
                if right_carry_target.has_tag(self.stop_carry_object_tag):
                    carry_target = right_carry_target
        if carry_target is None:
            actor.routing_component.remove_route_event_by_data(self)
            return
        for exit_carry_event in actor.routing_component.route_event_context.route_event_of_data_type_gen(type(self)):
            if exit_carry_event.event_data._owned_object is carry_target:
                actor.routing_component.remove_route_event_by_data(self)
                return

        self._owned_object = carry_target

        def set_target(asm):
            asm.set_current_state('entry')
            asm.set_actor(self.animation_elements[0].actor_name, actor)
            asm.set_actor(self.animation_elements[0].target_name, carry_target)
            return True

        route_interaction = actor.routing_component.route_interaction
        route_event_animation = self.animation_elements[0](route_interaction, setup_asm_additional=set_target,
          enable_auto_exit=False)
        asm = route_event_animation.get_asm(use_cache=False)
        if asm is None:
            logger.warn('Unable to get a valid Route Event ASM ({}) for {}.', route_event_animation, actor)
            actor.routing_component.remove_route_event_by_data(self)
            return
        self.arb = Arb()

        def _send_arb(timeline):
            route_event_animation.append_to_arb(asm, self.arb)
            route_event_animation.append_exit_to_arb(asm, self.arb)
            distribute_arb_element((self.arb), master=actor, immediate=True)
            return True

        carry_element_helper = CarryElementHelper(interaction=route_interaction, carry_target=carry_target,
          sequence=(build_element(_send_arb)))
        exit_carry_element = carry_element_helper.exit_carry_while_holding(arb=(self.arb))

        def event_finished(_):
            self._owned_object = None
            if actor.routing_component is None:
                return
            actor.routing_component.remove_route_event_by_data(self)

        exit_carry_element = build_critical_section_with_finally(exit_carry_element, event_finished)
        umbrella_timeline = services.time_service().sim_timeline
        umbrella_timeline.schedule(exit_carry_element)