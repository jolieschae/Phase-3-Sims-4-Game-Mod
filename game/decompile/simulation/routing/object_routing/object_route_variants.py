# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\object_routing\object_route_variants.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 50752 bytes
from _weakrefset import WeakSet
import itertools
from animation.object_animation import ObjectAnimationElement
from balloon.balloon_enums import BALLOON_TYPE_LOOKUP
from balloon.balloon_request import BalloonRequest
from balloon.balloon_variant import BalloonVariant
from balloon.tunable_balloon import TunableBalloon
from event_testing.resolver import SingleObjectResolver, DoubleObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeRoutingBehavior
from interactions.constraint_variants import TunableGeometricConstraintVariant, TunableConstraintVariant
from interactions.constraints import Circle, Anywhere, ANYWHERE
from interactions.utils.animation_reference import TunableRoutingSlotConstraint
from interactions.utils.loot import LootActions, LootOperationList
from objects.components import types
from objects.locators.locator_tuning import LocatorTuning
from objects.object_creation import ObjectCreation
from objects.part import ObjectPart
from placement import FGLTuning
from routing import Goal, SurfaceType, SurfaceIdentifier
from routing.object_routing.object_routing_behavior_actions import ObjectRoutingBehaviorActionAnimation, ObjectRoutingBehaviorActionDestroyObjects, ObjectRoutingBehaviorActionApplyLoot
from routing.waypoints.tunable_waypoint_graph import TunableWaypointGraph
from routing.waypoints.waypoint_generator import WaypointContext
from routing.waypoints.waypoint_generator_variant import TunableWaypointGeneratorVariant
from routing.waypoints.waypoint_stitching import WaypointStitchingVariant
from sims4 import random
from sims4.math import vector3_almost_equal
from sims4.random import weighted_random_item
from sims4.tuning.geometric import TunableDistanceSquared
from sims4.tuning.tunable import OptionalTunable, HasTunableFactory, AutoFactoryInit, Tunable, TunableReference, TunableEnumEntry, TunableEnumSet, TunableList, TunablePercent, TunableVariant, HasTunableSingletonFactory, TunableLocator, TunableRange, TunableTuple
from sims4.tuning.tunable_base import GroupNames
from tag import TunableTags
from world.terrain_enums import TerrainTag
import enum, placement, routing, services, sims4.resources
logger = sims4.log.Logger('ObjectRouteVariants', default_owner='miking')

class _ObjectRoutingBehaviorBase(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'route_fail_balloon':OptionalTunable(description='\n            If enabled, show a route failure balloon if this behavior fails to plan a valid path.\n            ',
       tunable=BalloonVariant.TunableFactory(),
       enabled_name='show_balloon'), 
     'route_fail_loot':TunableList(description='\n            Loot to apply if this behavior fails to plan a valid path.\n            ',
       tunable=LootActions.TunableReference()), 
     'one_shot':Tunable(description='\n            If set to true, this behavior will stop running after one iteration.\n            ',
       tunable_type=bool,
       default=False)}

    def __init__(self, obj, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._obj = obj
        self._target = None

    def do_route_fail_gen(self, timeline):
        object_routing_component = self._obj.get_component(types.OBJECT_ROUTING_COMPONENT)
        object_routing_component.on_route_fail()
        target = self.get_target()
        if target is None:
            resolver = SingleObjectResolver(self._obj)
        else:
            resolver = DoubleObjectResolver(self._obj, target)
        self.request_route_fail_balloon(resolver)
        loots = LootOperationList(resolver, self.route_fail_loot)
        loots.apply_operations()
        if False:
            yield None

    def request_route_fail_balloon(self, resolver):
        if self.route_fail_balloon is None:
            return
        else:
            balloons = self.route_fail_balloon.get_balloon_icons(resolver)
            if not balloons:
                return
            balloon = weighted_random_item(balloons)
            if balloon is None:
                return
            icon_info = balloon.icon(resolver, balloon_target_override=None)
            if icon_info[0] is None and icon_info[1] is None:
                return
        category_icon = None
        if balloon.category_icon is not None:
            category_icon = balloon.category_icon(resolver, balloon_target_override=None)
        balloon_type, priority = BALLOON_TYPE_LOOKUP[balloon.balloon_type]
        balloon_overlay = balloon.overlay
        request = BalloonRequest(self._obj, icon_info[0], icon_info[1], balloon_overlay, balloon_type, priority, TunableBalloon.BALLOON_DURATION, 0, 0, category_icon)
        request.distribute()

    def get_routes_gen(self):
        raise NotImplementedError

    def get_target(self):
        return self._target

    def get_target_object(self):
        if self._target is not None:
            if self._target.is_part:
                return self._target.part_owner
        return self._target

    def release_target(self):
        pass

    def get_randomize_orientation(self):
        return False

    def do_target_action_rules_gen(self, timeline, *_):
        return False
        if False:
            yield None

    def on_no_target(self):
        pass

    def consumes_social_transform_constraint(self):
        return False

    def should_plan_route(self):
        return True

    def requires_target_reservation(self):
        return False

    def get_target_reservation_handler(self):
        pass


class ObjectRoutingBehaviorFromWaypointGenerator(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'waypoint_generator':TunableWaypointGeneratorVariant(tuning_group=GroupNames.ROUTING), 
     'waypoint_count':Tunable(description='\n            The number of waypoints per loop.\n            ',
       tunable_type=int,
       default=10), 
     'waypoint_stitching':WaypointStitchingVariant(tuning_group=GroupNames.ROUTING), 
     'return_to_starting_point':OptionalTunable(description='\n            If enabled then the route will return to the starting position\n            within a circle constraint that has a radius of the value tuned\n            here.\n            ',
       tunable=Tunable(description='\n                The radius of the circle constraint to build to satisfy the\n                return to starting point feature.\n                ',
       tunable_type=int,
       default=6),
       enabled_name='radius_to_return_within'), 
     'randomize_orientation':Tunable(description='\n            Make Waypoint orientation random.  Default is velocity aligned.\n            ',
       tunable_type=bool,
       default=False)}

    def get_routes_gen(self):
        waypoint_generator = self.waypoint_generator(WaypointContext(self._obj), None)
        waypoints = []
        constraints = itertools.chain((waypoint_generator.get_start_constraint(),), waypoint_generator.get_waypoint_constraints_gen(self._obj, self.waypoint_count))
        if self.return_to_starting_point is not None:
            obj_start_constraint = Circle((self._obj.position), (self.return_to_starting_point), routing_surface=(self._obj.routing_surface), los_reference_point=None)
            constraints = itertools.chain(constraints, obj_start_constraint)
        else:
            for constraint in constraints:
                goals = list(itertools.chain.from_iterable((h.get_goals() for h in constraint.get_connectivity_handles(self._obj))))
                if not goals:
                    continue
                if self.randomize_orientation:
                    for goal in goals:
                        goal.orientation = sims4.math.angle_to_yaw_quaternion(random.uniform(0.0, sims4.math.TWO_PI))

                waypoints.append(goals)

            return waypoints or False
        routing_context = self._obj.get_routing_context()
        for route_waypoints in self.waypoint_stitching(waypoints, waypoint_generator.loops):
            route = routing.Route((self._obj.routing_location), (route_waypoints[-1]), waypoints=(route_waypoints[:-1]), routing_context=routing_context)
            yield route

        return True

    def get_randomize_orientation(self):
        return self.randomize_orientation


class ObjectRoutingBehaviorFromRoutingSlotConstraint(_ObjectRoutingBehaviorBase):
    _unavailable_objects = WeakSet()
    FACTORY_TUNABLES = {'tags':TunableTags(description='\n            Route to an object matching these tags.\n            ',
       filter_prefixes=('Func', )), 
     'constraint':TunableRoutingSlotConstraint(description='\n            Use the point on the found object defined by this animation boundary\n            condition.\n            ',
       class_restrictions=(
      ObjectAnimationElement,)), 
     'parent_relation':Tunable(description="\n            If checked, then this routing behavior is affected by the object's\n            parenting relation:\n             * We'll prefer to route to our previous parent, if it still exists\n             * We'll only route to objects that have no children\n             * We won't route to objects that other objects have picked to route to\n             * We'll stop routing if an object becomes the target's child\n            ",
       tunable_type=bool,
       default=False)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        objects = services.object_manager().get_objects_matching_tags(self.tags)
        if self.parent_relation:
            object_routing_component = self._obj.get_component(types.OBJECT_ROUTING_COMPONENT)
            objects = sorted(objects, key=(lambda o: o is not object_routing_component.previous_parent))
        for target in objects:
            if not target.is_connected(self._obj):
                continue
            if self.parent_relation:
                if target.children:
                    continue
                if target in self._unavailable_objects:
                    continue
                target.register_for_on_children_changed_callback(self._on_target_changed)
            target.register_on_location_changed(self._on_target_changed)
            self._target = target
            self._unavailable_objects.add(target)
            break
        else:
            self._target = None

    def _on_target_changed(self, child, *_, **__):
        self._target.unregister_for_on_children_changed_callback(self._on_target_changed)
        self._target.unregister_on_location_changed(self._on_target_changed)
        self._unavailable_objects.discard(self._target)
        if child is not self._obj:
            object_routing_component = self._obj.get_component(types.OBJECT_ROUTING_COMPONENT)
            object_routing_component.restart_running_behavior()

    def get_routes_gen(self):
        if self._target is None:
            return False
        routing_slot_constraint = self.constraint.create_constraint(self._obj, self._target)
        goals = list(itertools.chain.from_iterable((h.get_goals() for h in routing_slot_constraint.get_connectivity_handles(self._obj))))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), goals, routing_context=routing_context)
        yield route
        return True

    def release_target(self):
        if self._target is not None:
            self._unavailable_objects.discard(self._target)


class ObjectRouteFromRoutingFormation(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'formation_type': TunableReference(description='\n            The formation type to look for on the target. This is the routing\n            formation that we want to satisfy constraints for.\n            ',
                         manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                         class_restrictions=('RoutingFormation', ))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        routing_component = self._obj.routing_component
        routing_master = routing_component.routing_master
        if routing_master is not None:
            self._target = routing_master
        else:
            self._target = None

    def get_routes_gen(self):
        if self._target is None:
            return False
        slave_data = self._target.get_formation_data_for_slave(self._obj)
        if slave_data is None:
            return False
        starting_location = self._target.intended_location
        transform = slave_data.find_good_location_for_slave(starting_location)
        if transform is None:
            return False
        goal = Goal(routing.Location(transform.translation, transform.orientation, starting_location.routing_surface))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), (goal,), routing_context=routing_context)
        yield route
        return True


class ObjectRouteFromFGL(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'min_distance':TunableRange(description='\n            The minimum distance a point needs to be from the start. \n            ',
       tunable_type=float,
       default=0.0,
       minimum=0.0,
       maximum=FGLTuning.MAX_FGL_DISTANCE), 
     'max_distance':TunableRange(description='\n            The maximum distance from the start position which will be\n            allowed when testing.  If no more valid test points can be\n            found within that distance, the search will give up.\n            ',
       tunable_type=float,
       default=FGLTuning.MAX_FGL_DISTANCE,
       minimum=0.0,
       maximum=FGLTuning.MAX_FGL_DISTANCE), 
     'surface_type_override':OptionalTunable(description="\n            If enabled, we will use this surface type instead of the one from\n            the object's location.\n            ",
       tunable=TunableEnumEntry(description='\n                The surface type we want to force.\n                ',
       tunable_type=SurfaceType,
       default=(SurfaceType.SURFACETYPE_WORLD),
       invalid_enums=(
      SurfaceType.SURFACETYPE_UNKNOWN,))), 
     'terrain_tags':OptionalTunable(description='\n            If enabled, a set of allowed terrain tags. At least one tag must\n            match the terrain under each vertex of the footprint of the supplied\n            object.\n            ',
       tunable=TunableEnumSet(enum_type=TerrainTag,
       enum_default=(TerrainTag.INVALID)))}

    def get_routes_gen(self):
        routing_surface = self._obj.routing_surface
        if self.surface_type_override is not None:
            routing_surface = SurfaceIdentifier(routing_surface.primary_id, routing_surface.secondary_id, self.surface_type_override)
        terrain_tags = list(self.terrain_tags) if self.terrain_tags else []
        starting_location = placement.create_starting_location(transform=(self._obj.location.transform), routing_surface=routing_surface)
        fgl_context = placement.create_fgl_context_for_object(starting_location, (self._obj), min_distance=(self.min_distance),
          max_distance=(self.max_distance),
          terrain_tags=terrain_tags)
        position, orientation, _ = fgl_context.find_good_location()
        if position is None or orientation is None:
            return False
        if vector3_almost_equal(position, starting_location.position):
            return True
        goal = Goal(routing.Location(position, orientation, starting_location.routing_surface))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), (goal,), routing_context=routing_context)
        yield route
        return True


class _TargetActionRules(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'chance':TunablePercent(description='\n            A random chance of this action getting applied (default 100%).\n            ',
       default=100), 
     'test':TunableTestSet(description='\n            A test to decide whether or not to apply this particular set of actions to the target object.\n            ',
       tuning_group=GroupNames.TESTS), 
     'actions':TunableList(description='\n            A list of one or more ObjectRoutingBehaviorActions to run on the\n            target object after routing to it. These are applied in sequence.\n            ',
       tunable=TunableVariant(play_animation=(ObjectRoutingBehaviorActionAnimation.TunableFactory()),
       destroy_objects=(ObjectRoutingBehaviorActionDestroyObjects.TunableFactory()),
       apply_loot=(ObjectRoutingBehaviorActionApplyLoot.TunableFactory()),
       default='play_animation')), 
     'abort_if_applied':Tunable(description="\n            Don't run any further actions from this list of action rules if \n            conditions are met and this action is executed.\n            ",
       tunable_type=bool,
       default=False)}


class _RouteTargetType(HasTunableSingletonFactory, AutoFactoryInit):

    def get_objects(self):
        raise NotImplementedError


class _RouteTargetTypeObject(_RouteTargetType):
    FACTORY_TUNABLES = {'tags': TunableTags(description='\n            Tags used to pre-filter the list of potential targets.\n            If any of the tags match the object will be considered.\n            ',
               filter_prefixes=('Func', ))}

    def get_objects(self):
        if self.tags:
            return services.object_manager().get_objects_matching_tags((self.tags), match_any=True)
        return services.object_manager().get_valid_objects_gen()


class _RouteTargetTypeSim(_RouteTargetType):
    FACTORY_TUNABLES = {}

    def get_objects(self):
        return services.sim_info_manager().instanced_sims_gen()


class TunableRoutingBehaviorConstraints(TunableGeometricConstraintVariant):

    def __init__(self, default='circle', **kwargs):
        (super().__init__)(routing_slot=TunableRoutingSlotConstraint(class_restrictions=ObjectAnimationElement), 
         default=default, **kwargs)


class TargetReservationTiming(enum.Int):
    NEVER = 0
    TARGET_ACTION = 1
    ROUTING_BEHAVIOR = 2


class ObjectRouteFromTargetObject(_ObjectRoutingBehaviorBase):
    _unavailable_parts = WeakSet()
    FACTORY_TUNABLES = {'radius':OptionalTunable(description='\n            If tuned, only objects within this distance are considered.\n            ',
       tunable=TunableDistanceSquared(default=1)), 
     'target_type':TunableVariant(description='\n            Type of target object to choose (object, sim).\n            ',
       object=_RouteTargetTypeObject.TunableFactory(),
       sim=_RouteTargetTypeSim.TunableFactory(),
       default='object'), 
     'target_selection_test':TunableTestSet(description='\n            A test used for selecting a target.\n            ',
       tuning_group=GroupNames.TESTS), 
     'no_target_loot':TunableList(description="\n            Loot to apply if no target is selected (eg, change state back to 'wander').\n            ",
       tunable=LootActions.TunableReference()), 
     'constraints':TunableList(description='\n            Constraints relative to the relative participant.\n            ',
       tunable=TunableRoutingBehaviorConstraints(description='\n                Use the point on the found object defined by these constraints.\n                ',
       disabled_constraints=('spawn_points', 'spawn_points_with_backup'))), 
     'needs_route':Tunable(description='\n            If disabled, this behavior will run all surrounding actions without generating a route. An example use\n            case: a chicken may want to target and run an authored path to a particular part of its coop, \n            but the coop is unroutable. This can be disabled to allow that to trigger as a routing behavior without\n            requiring connectivity.\n            \n            Actions that may still run:\n                * no_target_loot\n                * target_action_rules\n                * termination_loot\n                * pre_route_animation\n                \n            Will *not* run routing actions.\n            ',
       tunable_type=bool,
       default=True), 
     'target_action_rules':TunableTuple(description='\n            Rules for running TargetObjectActions on the target object.\n            -These will play if the object doesn\'t perform a route.\n            -By default these will play if the route fails or the behavior is cancelled (see the "cancel if route incomplete" checkbox below).\n            -These will not play after a hard stop (restarted/destroyed)\n            -This is a good place to tune anything you\'d normally tune under "routing_actions" or if the behavior isn\'t\n             actually planning a route.\n            \n            Example usage:\n            Assume you have a routing behavior that gets a chicken to move from inside a chicken coop to the nesting\n            slot still within the chicken coop.  There is no actual route involved, just an authored path triggered by\n            an animation.  We\'d tune "needs route" to false then add the authored path animation as a "target action rule"\n            so that it plays despite not running a path.\n            ',
       actions=TunableList(description='\n                A set of conditions and a list of one or more TargetObjectActions to run\n                 on the target object. These are applied in sequence.\n                ',
       tunable=(_TargetActionRules.TunableFactory())),
       cancel_if_route_incomplete=Tunable(description='\n                If tuned, target action rules will not run if the route fails or is interrupted. \n                Note that this is only applicable if the behavior is tuned to run a route (needs_route is True).\n                ',
       tunable_type=bool,
       default=False)), 
     'target_participant':OptionalTunable(description="\n            An alternative to Target Type for more specific targeting.\n            Picks a target that the object will route to.\n            No Target Loot is applied if a target can't be found.\n            ",
       tunable=TunableEnumEntry(tunable_type=ParticipantTypeRoutingBehavior,
       default=(ParticipantType.RoutingTarget))), 
     'target_part':OptionalTunable(description='\n            If tuned, behavior will look for a free part that matches the tuned definition on the chosen target object.\n            This part will be passed to any animation actions.\n            If the target object has no free part, the No Target Loot is applied.\n            ',
       tunable=TunableTuple(part_definition=ObjectPart.TunableReference(description='\n                    The tuning file for the part we intend to target.\n                    '),
       subroot_index=OptionalTunable(description='\n                    If enabled, we will look for a part with a particular subroot index.\n                    ',
       tunable=Tunable(description='\n                        The subroot index associated with the part we want to look at.\n                        ',
       tunable_type=int,
       default=0)))), 
     'target_reservation_timing':TunableEnumEntry(description='\n            Determines if and when we should reserve the target.  If setting to NEVER, be sure that your object does not\n            require the behavior to be exclusive against other behaviors or Sim interactions.  Reservations will be\n            respected while routing.\n\n            NEVER - No target reservation required\n            TARGET_ACTION - Reserve only for the target action\n            ROUTING_BEHAVIOR - Reserve for the duration of the entire routing behavior\n            ',
       tunable_type=TargetReservationTiming,
       default=TargetReservationTiming.TARGET_ACTION)}

    @classmethod
    def _verify_tuning_callback(cls):
        if not cls.target_selection_test:
            if not cls.tags:
                logger.error('No selection test tuned for ObjectRouteFromTargetObject {}.', cls,
                  owner='miking')

    def _find_target_part(self, target):
        if target.parts is not None:
            for part in target.parts:
                if self.target_selection_test:
                    resolver = DoubleObjectResolver(self._obj, part)
                    if not self.target_selection_test.run_tests(resolver):
                        continue
                    elif self.target_part.subroot_index is not None and not part.subroot_index is None:
                        if part.subroot_index != self.target_part.subroot_index:
                            continue
                    if part.part_definition is self.target_part.part_definition and part not in self._unavailable_parts:
                        if not self.requires_target_reservation() or part.may_reserve(self._obj):
                            return part

    def _find_target(self):

        def _filter_valid_targets(targets_source):
            valid_targets = []
            for target in targets_source:
                if self.radius is not None:
                    dist_sq = (target.position - self._obj.position).magnitude_squared()
                    if dist_sq > self.radius:
                        continue
                    else:
                        if target == self:
                            continue
                        is_target_reserved = self.requires_target_reservation() and not target.may_reserve(self._obj)
                        if not target.is_sim:
                            if not self.target_part:
                                if is_target_reserved:
                                    continue
                    if self.target_part is None:
                        if self.target_selection_test:
                            resolver = DoubleObjectResolver(self._obj, target)
                            if not self.target_selection_test.run_tests(resolver):
                                continue
                        valid_targets.append(target)
                        continue
                    valid_part = self._find_target_part(target)
                    if valid_part is not None:
                        valid_targets.append(valid_part)

            return valid_targets

        def _try_mark_part_unavailable(obj):
            if not obj.is_part:
                return
            self._unavailable_parts.add(obj)
            obj.register_for_on_children_changed_callback((self._on_target_changed), part_only=True)

        def _try_reserve_object(obj):
            if obj.is_sim or obj.is_terrain:
                return
            if self.requires_target_reservation():
                if self.target_reservation_timing == TargetReservationTiming.ROUTING_BEHAVIOR:
                    self._reservation_handler = obj.get_reservation_handler(self._obj)
                    if self._reservation_handler:
                        if self._reservation_handler.may_reserve():
                            self._reservation_handler.begin_reservation()

        routing_service = services.get_object_routing_service()
        allow_caching = self._obj.objectrouting_component.allow_target_object_cache
        cache_key = (self._obj.guid64, id(self.target_type))
        objs_set_on_current_run = False
        if self.target_participant is not None:
            resolver = SingleObjectResolver(self._obj)
            objects = resolver.get_participants(self.target_participant)
            objects = [target.get_sim_instance() if (target.is_sim and target.is_instanced()) else target for target in objects if target is not None]
            objs_set_on_current_run = True
        else:
            objects = routing_service.get_objects_from_cache(cache_key) if allow_caching else None
            if objects is None:
                objects = list(self.target_type.get_objects())
                if allow_caching:
                    routing_service.set_objects_cache_for_type(cache_key, objects)
                objs_set_on_current_run = True
            else:
                objects = _filter_valid_targets(objects)
                return objects or None
            if not self.should_plan_route():
                obj = objects[0]
                _try_mark_part_unavailable(obj)
                return obj
            source_handles = [
             routing.connectivity.Handle(self._obj.position, self._obj.routing_surface)]
            dest_handles = []
            for obj in objects:
                parent = obj.parent
                route_to_obj = parent if parent is not None else obj
                constraint = Anywhere()
                for tuned_constraint in self.constraints:
                    constraint = constraint.intersect(tuned_constraint.create_constraint(self._obj, route_to_obj))

                dests = constraint.get_connectivity_handles((self._obj), target=obj)
                if dests:
                    dest_handles.extend(dests)

            if not dest_handles:
                return
            routing_context = self._obj.get_routing_context()
            connections = routing.estimate_path_batch(source_handles, dest_handles, routing_context=routing_context)
            if not connections:
                if allow_caching:
                    if routing_service.clear_cache_for_type(cache_key):
                        if not objs_set_on_current_run:
                            return self._find_target()
                return
            connections.sort(key=(lambda connection: connection[2]))
            best_connection = connections[0]
            best_dest_handle = best_connection[1]
            best_obj = best_dest_handle.target
            if allow_caching:
                routing_service.remove_target_from_cache(cache_key, best_obj)
            _try_mark_part_unavailable(best_obj)
            _try_reserve_object(best_obj)
            return best_obj

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._reservation_handler = None
        self._target = self._find_target()

    def get_routes_gen(self):
        if self._target is None:
            self.on_no_target()
            return False
        routing_slot_constraint = Anywhere()
        for tuned_constraint in self.constraints:
            routing_slot_constraint = routing_slot_constraint.intersect(tuned_constraint.create_constraint(self._obj, self._target))

        goals = list(itertools.chain.from_iterable((h.get_goals() for h in routing_slot_constraint.get_connectivity_handles(self._obj))))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), goals, routing_context=routing_context)
        yield route
        return True

    def do_target_action_rules_gen(self, timeline, route_successful):
        if not self.target_action_rules.actions or self._target is None:
            return
        if self.target_action_rules.cancel_if_route_incomplete:
            if not route_successful:
                return
        resolver = DoubleObjectResolver(self._obj, self._target)
        for target_action_rule in self.target_action_rules.actions:
            if random.random.random() >= target_action_rule.chance:
                continue
            if not target_action_rule.test.run_tests(resolver):
                continue
            if target_action_rule.actions is not None:
                for action in target_action_rule.actions:
                    result = yield from action.run_action_gen(timeline, self._obj, self._target)
                    if not result:
                        return

            if target_action_rule.abort_if_applied:
                return

        if False:
            yield None

    def on_no_target(self):
        self.release_target()
        resolver = SingleObjectResolver(self._obj)
        for loot_action in self.no_target_loot:
            loot_action.apply_to_resolver(resolver)

    def release_target(self):
        if not self._target:
            return
        if self._target.is_part:
            self._target.unregister_for_on_children_changed_callback(self._on_target_changed)
            self._unavailable_parts.discard(self._target)
        if self._reservation_handler is not None:
            self._reservation_handler.end_reservation()

    def _on_target_changed(self, child, location=None, **kwargs):
        if child is self._obj:
            if location is None:
                self.release_target()

    def should_plan_route(self):
        return self.needs_route

    def requires_target_reservation(self):
        return self.target_reservation_timing != TargetReservationTiming.NEVER

    def get_target_reservation_handler(self):
        return self._reservation_handler


class ObjectRouteFromCreatedObject(ObjectRouteFromTargetObject):
    FACTORY_TUNABLES = {'create_route_target':ObjectCreation.TunableFactory(), 
     'locked_args':{'target_participant':ParticipantType.Invalid, 
      'target_selection_test':None, 
      'target_type':None, 
      'target_part':None}}

    def _find_target(self):
        creation_data = self.create_route_target
        if creation_data is None:
            logger.error('Create Route Target data is missing in Object Route From Created Object', owner='bteng')
            return
        resolver = SingleObjectResolver(self._obj)
        creation_data.initialize_helper(resolver)
        return creation_data.create_object(resolver)

    def __init__(self, *args, **kwargs):
        (super(ObjectRouteFromCreatedObject, self).__init__)(*args, **kwargs)


class ObjectRouteFromParticipantType(_ObjectRoutingBehaviorBase):
    FACTORY_TUNABLES = {'target_participant':TunableEnumEntry(description='\n            The target that the object is routing to.\n            ',
       tunable_type=ParticipantTypeRoutingBehavior,
       default=ParticipantType.RoutingTarget), 
     'constraints':TunableList(description='\n            Constraints relative to the relative participant.\n            ',
       tunable=TunableGeometricConstraintVariant(description='\n                Use the point on the target participant object defined by these geometric constraints.\n                ',
       disabled_constraints=('spawn_points', 'spawn_points_with_backup'))), 
     'no_target_loot':TunableList(description="\n            Loot to apply if no target is selected (eg, change state back to 'wander').\n            ",
       tunable=LootActions.TunableReference())}

    def get_routes_gen(self):
        resolver = SingleObjectResolver(self._obj)
        self._target = resolver.get_participant(self.target_participant)
        if self._target is not None:
            if self._target.is_sim:
                self._target = self._target.get_sim_instance()
        if self._target is None:
            self.on_no_target()
            return False
        target_obj_constraint = ANYWHERE
        for tuned_constraint in self.constraints:
            target_obj_constraint = target_obj_constraint.intersect(tuned_constraint.create_constraint(self._obj, self._target))

        goals = list(itertools.chain.from_iterable((h.get_goals() for h in target_obj_constraint.get_connectivity_handles(self._obj))))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), goals, routing_context=routing_context)
        yield route
        return True

    def on_no_target(self):
        resolver = SingleObjectResolver(self._obj)
        for loot_action in self.no_target_loot:
            loot_action.apply_to_resolver(resolver)


class ObjectRoutingBehaviorFromLocator(_ObjectRoutingBehaviorBase):

    class _LocatorIdFactory(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {}

        def get_locator_ids(self, routing_object):
            raise NotImplementedError

    class _LocatorIdFactory_Tuned(_LocatorIdFactory):
        FACTORY_TUNABLES = {'locator_id': TunableLocator(description='Specific locator id to use.')}

        def get_locator_ids(self, routing_object):
            return (
             self.locator_id,)

    class _LocatorIdFactory_BasedOnStatistic(_LocatorIdFactory):

        def get_locator_id(self, routing_object):
            target_locator_id_stat = LocatorTuning.TARGET_LOCATOR_ID_STAT
            tracker = routing_object.get_tracker(target_locator_id_stat)
            if tracker is not None:
                if tracker.has_statistic(target_locator_id_stat):
                    stat = tracker.get_statistic(target_locator_id_stat)
                    if stat is not None:
                        return stat.get_value()

    class _LocatorIdFactory_FromObjectRoutingComponent(_LocatorIdFactory):

        def get_locator_ids(self, routing_object):
            return routing_object.routing_component.get_object_routing_component().locators

    FACTORY_TUNABLES = {'locator':TunableVariant(description='\n            Locator to use. Can be tuned, provided by a statistic, or \n            dynamically provided by the ObjectRoutingComponent.\n            ',
       tuned=_LocatorIdFactory_Tuned.TunableFactory(),
       based_on_statistic=_LocatorIdFactory_BasedOnStatistic.TunableFactory(),
       from_object_routing_component=_LocatorIdFactory_FromObjectRoutingComponent.TunableFactory(),
       default='tuned'), 
     'constraint_radius':TunableRange(description='\n            The radius, in meters, for the locator constraint\n            constraints.\n            ',
       tunable_type=float,
       default=1.5,
       minimum=0)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._runtime_constraint = None

    def get_routes_gen(self):
        locator_ids = self.locator.get_locator_ids(self._obj)
        if not locator_ids:
            return False
        waypoints = []
        for locator_id in locator_ids:
            waypoint_constraint = TunableWaypointGraph.locator_to_waypoint_constraint(locator_id, self.constraint_radius, self._obj.routing_surface)
            goals = list(itertools.chain.from_iterable((h.get_goals() for h in waypoint_constraint.get_connectivity_handles(self._obj))))
            waypoints.append(goals)

        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), (waypoints[-1]), waypoints=(waypoints[:-1]),
          routing_context=routing_context)
        yield route
        return True


class ObjectRouteFromSocialTransform(_ObjectRoutingBehaviorBase):

    def get_routes_gen(self):
        constraint = self._obj.get_social_transform_constraint()
        if constraint is None:
            return True
        goals = list(itertools.chain.from_iterable((h.get_goals() for h in constraint.get_connectivity_handles(self._obj))))
        routing_context = self._obj.get_routing_context()
        route = routing.Route((self._obj.routing_location), goals, routing_context=routing_context)
        self._obj.set_social_transform_constraint(None)
        yield route
        return True

    def consumes_social_transform_constraint(self):
        return True