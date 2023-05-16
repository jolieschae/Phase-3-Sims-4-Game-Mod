# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\object_routing\object_routing_behavior.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 23257 bytes
import date_and_time, elements, sims4
from animation.animation_utils import flush_all_animations
from animation.object_animation import ObjectAnimationElement
from element_utils import build_element
from elements import SubclassableGeneratorElement
from event_testing.resolver import SingleObjectResolver
from interactions.utils.loot import LootActions
from interactions.utils.loot_ops import StateChangeLootOp
from interactions.utils.routing import PlanRoute, FollowPath
from interactions.utils.tested_variant import TunableTestedVariant
from routing.object_routing.object_route_variants import ObjectRoutingBehaviorFromWaypointGenerator, ObjectRoutingBehaviorFromRoutingSlotConstraint, ObjectRouteFromRoutingFormation, ObjectRouteFromFGL, ObjectRouteFromTargetObject, ObjectRouteFromParticipantType, ObjectRoutingBehaviorFromLocator, ObjectRouteFromCreatedObject, ObjectRouteFromSocialTransform
from routing.object_routing.object_routing_behavior_actions import ObjectRoutingBehaviorActionDestroyObjects, ObjectRoutingBehaviorActionAnimation, ObjectRoutingBehaviorActionApplyLoot, ObjectRoutingBehaviorActionProceduralAnimationRotation
from routing.object_routing.object_routing_priority import ObjectRoutingPriority
from routing.walkstyle.walkstyle_request import WalkStyleRequest
from services.object_routing_service import ObjectRoutingService
from sims4.callback_utils import CallableList
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, OptionalTunable, TunableList, TunableVariant, TunableSet, Tunable, TunableEnumEntry
import element_utils, services
logger = sims4.log.Logger('ObjectRoutingBehavior', default_owner='bnguyen')

class ObjectRoutingBehavior(HasTunableReference, SubclassableGeneratorElement, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'route':TunableVariant(description='\n            Define how this object routes when this behavior is active.\n            ',
       from_waypoints=ObjectRoutingBehaviorFromWaypointGenerator.TunableFactory(),
       from_slot_constraint=ObjectRoutingBehaviorFromRoutingSlotConstraint.TunableFactory(),
       from_routing_formation=ObjectRouteFromRoutingFormation.TunableFactory(),
       from_fgl=ObjectRouteFromFGL.TunableFactory(),
       from_target_object=ObjectRouteFromTargetObject.TunableFactory(),
       from_created_object=ObjectRouteFromCreatedObject.TunableFactory(),
       from_participant_type=ObjectRouteFromParticipantType.TunableFactory(),
       from_locator=ObjectRoutingBehaviorFromLocator.TunableFactory(),
       from_social_transform=ObjectRouteFromSocialTransform.TunableFactory(locked_args={'one_shot': True}),
       default='from_waypoints'), 
     'pre_route_animation':OptionalTunable(description='\n            If enabled, the routing object will play this animation before any\n            route planning/following happens.\n            ',
       tunable=ObjectAnimationElement.TunableReference()), 
     'routing_actions':TunableList(description="\n            A list of things the routing object can do once they have reached a routing destination.\n            -These will not play if the object doesn't perform a route, if the route fails, the behavior is cancelled,\n             or after a hard stop (restarted/destroyed).\n            -This is a good place to tune behaviors that you want to happen ONLY if the object reaches its destination.\n            \n            Notes:\n            -Use target_action_rules instead if your route type is FromTargetObject.\n            -If this behavior uses waypoints, routing actions will occur after every waypoint destination is reached.\n            \n            Example usage:\n            Assume you have a routing behavior that gets a robot vacuum to route to a dust pile, play an animation, then\n            destroy the dust pile.  The animation and object destruction would be handled as routing actions since they\n            should only occur if the robot vacuum actually reaches the dust pile.\n            ",
       tunable=TunableVariant(play_animation=(ObjectRoutingBehaviorActionAnimation.TunableFactory()),
       destroy_objects=(ObjectRoutingBehaviorActionDestroyObjects.TunableFactory()),
       apply_loot=(ObjectRoutingBehaviorActionApplyLoot.TunableFactory()),
       procedural_animation_rotation=(ObjectRoutingBehaviorActionProceduralAnimationRotation.TunableFactory()),
       default='play_animation')), 
     'termination_loot':TunableSet(description='\n            WARNING: Pushing states here that can trigger new routing behaviors can cause problems.  You should tune\n            these state changes in "routing actions", "target action rules", or "success loot". \n        \n            Loot that is applied to the routing object when the behavior is terminated.\n            -These are granted  after normal completion, if any route fails occur, or the behavior is cancelled.\n            -These will not be granted after a hard stop (restarted/destroyed).\n            -This is a good place to tune loot that must occur at the end of the routing behavior.\n            \n            Notes:\n            -There are few valid examples where you\'d actually want to use this.  In general, a combination\n            of "success loot" and "route fail loot" is usually the better option.\n            \n            Example usage:\n            (This is a purely theoretical example) Assume you have a routing behavior that gets an object to route to a\n            location then destroy itself.  Let\'s also assume you want the object to be destroyed no matter if the\n            route failed or the behavior was cancelled. This is where you\'d want to tune the destruction loot.\n            ',
       tunable=LootActions.TunableReference()), 
     'success_loot':TunableSet(description='\n            Loot that is applied to the routing object when the behavior completes successfully.\n            -Success in this case means the behavior was not cancelled mid route, a route fail did not occur,\n             and the routing actions have completed successfully.\n            -This loot is not granted after a hard stop (restarted/destroyed).\n            -This is a good place to tune loot that you want to occur at the end of a successful routing behavior run.\n            \n            Example usage:\n            Assume you have a routing behavior that gets a chicken to route to a food pile, eat from it, then "walk away"\n            if the behavior completed successfully.  The state to trigger the "walk away" behavior would be tuned here.\n            If a sim runs "call over" on the chicken while it is routing to the food pile, the "walk away" would\n            be skipped since the behavior did not complete successfully due to it being cancelled by the new behavior\n            pushed by the "call over" interaction.\n            ',
       tunable=LootActions.TunableReference()), 
     'walkstyle_override':OptionalTunable(description='\n            If enabled, we will override the default walkstyle for any routes\n            in this routing behavior.\n            ',
       tunable=TunableTestedVariant(description='\n                Specify a walkstyle override to use (either a single walkstyle\n                or pick one based on tests). \n                ',
       tunable_type=WalkStyleRequest.TunableFactory(description='\n                    The walkstyle override to use.\n                    '),
       is_noncallable_type=True)), 
     'clear_locomotion_mask':Tunable(description='\n            If enabled, override the locomotion queue mask.  This mask controls\n            which Animation Requests and XEvents get blocked during locomotion.\n            By default, the mask blocks everything.  If cleared, it blocks\n            nothing.  It also lowers the animation track used by locomotion to \n            9,999 from the default of 10,000.  Use with care, ask your GPE.\n            ',
       tunable_type=bool,
       default=False), 
     'object_routing_priority':TunableEnumEntry(description='\n            ObjectRoutingBehaviors with a higher value priority will be allowed to route more often when at the routing\n            SoftCap.  Values are defined in ObjectRoutingPriority module tuning.\n            ',
       tunable_type=ObjectRoutingPriority,
       default=ObjectRoutingPriority.NONE,
       invalid_enums=(
      ObjectRoutingPriority.NONE,)), 
     'interruptible':Tunable(description="\n            When at the routing SoftCap, multi-route behaviors can be interrupted to allow other objects to route.\n            If this value is set to false and this behavior has multiple routes, it won't be interrupted.\n            ",
       tunable_type=bool,
       default=True)}

    def __init__(self, obj, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._obj = obj
        self._route_data = self.route(obj)
        self._canceled = False
        self._pre_route_element = None
        self._path_element = None
        self._route_successful = False
        self._on_run_completed = CallableList()
        self._run_route_success = True
        self.restarting = False

    @classmethod
    def _get_tuning_suggestions(cls, print_suggestion):
        state_change_loot = []
        for loot in cls.termination_loot:
            for action in loot.loot_actions:
                if type(action) is StateChangeLootOp:
                    state_change_loot.append(loot)
                    break

        if len(state_change_loot) > 0:
            print_suggestion('The following loot actions contain state changes and are tuned as termination loot: {}. If any of these states lead to a new routing behavior, they should be tuned in: routing actions, success loot, or target action rules instead.', state_change_loot,
              owner='bnguyen')

    def consumes_social_transform_constraint(self):
        return self._route_data.consumes_social_transform_constraint()

    def register_run_completed_callback(self, callback):
        self._on_run_completed.register(callback)

    def _do_single_route_gen(self, timeline, route):
        if route:
            yield from route.goals or self._do_route_fail_gen(timeline)
            self._route_data.release_target()
            return True
        else:
            self._path_element = plan_primitive = PlanRoute(route, self._obj)
            result = yield from element_utils.run_child(timeline, plan_primitive)
            if not result:
                return result
            else:
                nodes = plan_primitive.path.nodes
                yield from nodes and nodes.plan_success or self._do_route_fail_gen(timeline)
                return True
            if self._canceled:
                return False
            plan_primitive.path.blended_orientation = self._route_data.get_randomize_orientation()
            mask_override = None
            track_override = None
            if self.clear_locomotion_mask:
                mask_override = 0
                track_override = 9999
            self._path_element = follow_path_element = FollowPath((self._obj), (plan_primitive.path), track_override=track_override,
              mask_override=mask_override)
            result = yield from element_utils.run_child(timeline, follow_path_element)
            return result or result
        if self._canceled:
            return False
        for action in self.routing_actions:
            result = yield from action.run_action_gen(timeline, self._obj, self._route_data.get_target())
            if not result:
                return result

        self._route_successful = True
        return True
        if False:
            yield None

    def _run_gen(self, timeline):
        yield from self._acquire_routing_reservation(timeline)
        if self.pre_route_animation is not None:
            animation_element = self.pre_route_animation(self._obj)
            self._pre_route_element = build_element((animation_element, flush_all_animations))
            anim_result = yield from element_utils.run_child(timeline, self._pre_route_element)
            if not anim_result:
                self._on_run_completed(False)
                services.get_object_routing_service().release_routing_reservation(self._obj)
                return anim_result
        result = yield from self._run_gen_internal(timeline)
        self._on_run_completed(result and self._run_route_success)
        if self._route_data.one_shot:
            if self._obj.get_running_behavior() is self:
                self._obj.stop_running_object_routing_behavior()
        return True
        if False:
            yield None

    def _run_gen_internal(self, timeline):

        def do_routes(timeline):
            result = False
            object_routing_service = services.get_object_routing_service()
            route_gen = self._route_data.get_routes_gen()
            while 1:
                try:
                    route = next(route_gen)
                except StopIteration as ex:
                    try:
                        if ex.value is False:
                            yield from self._do_route_fail_gen(timeline)
                            result = False
                        break
                    finally:
                        ex = None
                        del ex

                except Exception as ex:
                    try:
                        logger.exception('Exception while generating object routes: ', exc=ex)
                        result = False
                        break
                    finally:
                        ex = None
                        del ex

                if not object_routing_service.has_routing_reservation(self._obj):
                    yield from self._acquire_routing_reservation(timeline)
                result = yield from self._do_single_route_gen(timeline, route)
                if self.interruptible:
                    object_routing_service.release_routing_reservation(self._obj)
                if not result:
                    break

            object_routing_service.release_routing_reservation(self._obj)
            if not result:
                yield from element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())
            return result
            if False:
                yield None

        route_result = True
        should_plan_route = self._route_data.should_plan_route()
        if should_plan_route:
            if self.walkstyle_override is None:
                route_result = yield from do_routes(timeline)
            else:
                resolver = SingleObjectResolver(self._obj)
                walkstyle_override = self.walkstyle_override(resolver=resolver)
                walkstyle_request = walkstyle_override(self._obj)
                route_result = yield from element_utils.run_child(timeline, walkstyle_request(sequence=do_routes))
        else:
            services.get_object_routing_service().release_routing_reservation(self._obj)
        target = self._route_data.get_target()
        if target:
            route_result = yield from self._perform_target_action_rules(target, timeline, route_result)
        else:
            if not should_plan_route:
                self._route_data.on_no_target()
            else:
                if not self.restarting:
                    resolver = SingleObjectResolver(self._obj)
                    for loot_action in self.termination_loot:
                        loot_action.apply_to_resolver(resolver)

                    if self._route_successful:
                        for loot_action in self.success_loot:
                            loot_action.apply_to_resolver(resolver)

                else:
                    yield from self._route_data.should_plan_route() or element_utils.run_child(timeline, element_utils.sleep_until_next_tick_element())
                route_result or self._route_data.release_target()
            return route_result
        if False:
            yield None

    def _perform_target_action_rules(self, target, timeline, route_result):

        def _perform_target_action_rules_internal(handler):
            try:
                yield from self._route_data.do_target_action_rules_gen(timeline, self._route_successful)
            finally:
                handler.end_reservation()

            if False:
                yield None

        if not target.is_sim:
            yield from self._route_data.requires_target_reservation() or self._route_data.do_target_action_rules_gen(timeline, self._route_successful)
        elif not target.is_terrain:
            existing_reservation_handler = self._route_data.get_target_reservation_handler()
            if existing_reservation_handler:
                yield from _perform_target_action_rules_internal(existing_reservation_handler)
            else:
                reservation_handler = target.get_reservation_handler(self._obj)
                if reservation_handler and reservation_handler.may_reserve():
                    reservation_handler.begin_reservation()
                    yield from _perform_target_action_rules_internal(reservation_handler)
                else:
                    self._route_data.on_no_target()
                    route_result = False
        return route_result
        if False:
            yield None

    def _do_route_fail_gen(self, timeline):
        self._run_route_success = False
        yield from self._route_data.do_route_fail_gen(timeline)
        if False:
            yield None

    def release_target(self):
        self._route_data.release_target()

    def _soft_stop(self):
        self._canceled = True
        if self._pre_route_element is not None:
            self._pre_route_element.trigger_soft_stop()
        if self._path_element is not None:
            self._path_element.trigger_soft_stop()
        services.get_object_routing_service().stop_routable_object(self._obj, False)
        return super()._soft_stop()

    def _hard_stop(self):
        services.get_object_routing_service().stop_routable_object(self._obj, True)
        super()._hard_stop()

    def get_target_object(self):
        if self._route_data is not None:
            return self._route_data.get_target_object()
        return

    def _acquire_routing_reservation(self, timeline):
        object_routing_service = services.get_object_routing_service()
        while not self._canceled:
            if not object_routing_service.has_routing_reservation(self._obj):
                if object_routing_service.can_object_route(self._obj):
                    object_routing_service.acquire_routing_reservation(self._obj)
                else:
                    wait_time_span = date_and_time.create_time_span(minutes=(ObjectRoutingService.ROUTE_WAIT_DURATION))
                    self._pre_route_element = build_element((elements.SoftSleepElement(wait_time_span),))
                    object_routing_service.register_sleep_element(self._obj, self._pre_route_element)
                    yield from element_utils.run_child(timeline, self._pre_route_element)

        if False:
            yield None

    def needs_replan(self):
        if self._path_element is None or self._path_element.path is None or self._path_element.path.nodes is None:
            return False
        return self._path_element.path.nodes.needs_replan()