# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\electronics\television.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 7591 bytes
from element_utils import build_critical_section, maybe, build_critical_section_with_finally
from interactions.aop import AffordanceObjectPair
from interactions.base.super_interaction import SuperInteraction
from interactions.interaction_finisher import FinishingType
from interactions.utils.animation_reference import TunableAnimationReference
import interactions.utils.conditional_animation as conditional_animation
from objects.components.state_references import TunableStateValueReference
from sims4.geometry import build_rectangle_from_two_points_and_radius
from sims4.tuning.tunable import Tunable
import element_utils, objects.components.state, placement, services

class WatchSuperInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {'off_channel':TunableStateValueReference(description='\n            The off channel. The last Sim using the TV will set the object to\n            this state.\n            '), 
     'required_channel':TunableStateValueReference(description='\n            The channel to watch.\n            '), 
     'remote_animation':TunableAnimationReference(description='\n            The animation for using the TV remote.\n            '), 
     'exit_remote_animation_override':TunableAnimationReference(description='\n            The override animation of using TV remote when exit from watching TV. You want to \n            set this value only if you want a different remote animation for exit, and this \n            animation must support the next posture that you are exiting to.\n            ',
       allow_none=True), 
     'sim_view_discourage_area_width':Tunable(description='\n            The width of the discouragement region placed from a viewing Sim to\n            the TV.\n            ',
       tunable_type=float,
       default=0.4)}
    CHANGE_CHANNEL_XEVT_ID = 101

    def _add_route_goal_suppression_region_to_quadtree(self, *args, **kwargs):
        if self.target is None:
            return
        object_point = self.target.location.transform.translation
        sim_point = self.sim.intended_location.transform.translation
        delta = object_point - sim_point
        delta_length = delta.magnitude()
        sim_point_offset = self.sim_view_discourage_area_width * 2
        if delta_length < sim_point_offset:
            return
        start_point = sim_point + delta / (delta_length / sim_point_offset)
        geo = build_rectangle_from_two_points_and_radius(object_point, start_point, self.sim_view_discourage_area_width)
        services.sim_quadtree().insert(self.sim, self.id, placement.ItemType.ROUTE_GOAL_PENALIZER, geo, self.sim.routing_surface, False, 0)

    def _remove_route_goal_suppression_region_from_quadtree(self):
        services.sim_quadtree().remove(self.id, placement.ItemType.ROUTE_GOAL_PENALIZER, 0)

    def _refresh_watching_discouragement_stand_region(self, *args, **kwargs):
        self._remove_route_goal_suppression_region_from_quadtree()
        self._add_route_goal_suppression_region_to_quadtree()

    def _start_route_goal_suppression(self, _):
        self.sim.routing_component.on_intended_location_changed.append(self._refresh_watching_discouragement_stand_region)
        self._add_route_goal_suppression_region_to_quadtree()

    def _stop_route_goal_suppression(self, _):
        self._remove_route_goal_suppression_region_from_quadtree()
        self.sim.routing_component.on_intended_location_changed.remove(self._refresh_watching_discouragement_stand_region)

    def ensure_state(self, desired_channel, remote_animation_override=None):
        return conditional_animation(self, desired_channel, self.CHANGE_CHANNEL_XEVT_ID, remote_animation_override or self.affordance.remote_animation)

    def _changed_state_callback(self, target, state, old_value, new_value):
        if new_value is not self.off_channel:
            if new_value.affordance is not None:
                context = self.context.clone_for_continuation(self)
                affordance = self.generate_continuation_affordance(new_value.affordance)
                aop = AffordanceObjectPair(affordance, self.target, affordance, None)
                aop.test_and_execute(context)
        self.cancel((FinishingType.OBJECT_CHANGED), cancel_reason_msg=('state: interaction canceled on state change ({} != {})'.format(new_value.value, self.required_channel.value)))

    def _run_interaction_gen(self, timeline):
        result = yield from element_utils.run_child(timeline, build_critical_section_with_finally(self._start_route_goal_suppression, build_critical_section(build_critical_section(self.ensure_state(self.affordance.required_channel), objects.components.state.with_on_state_changed(self.target, self.affordance.required_channel.state, self._changed_state_callback, super()._run_interaction_gen)), maybe((lambda: len(self.target.get_users(sims_only=True)) == 1), self.ensure_state(self.off_channel, self.affordance.exit_remote_animation_override))), self._stop_route_goal_suppression))
        return result
        if False:
            yield None