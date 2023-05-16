# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\go_here_test.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3616 bytes
import routing, services, sims4
from event_testing.results import TestResult
from server.pick_info import PickType

def go_here_test(target, context, **kwargs):
    position = None
    surface = None
    if context.pick is not None:
        position = context.pick.location
        surface = context.pick.routing_surface
    if target is not None:
        position = target.position
        surface = target.routing_surface
    if position is None:
        return TestResult(False, 'Cannot go here without a pick or target.')
    if context.pick is not None:
        if context.pick.pick_type == PickType.PICK_POOL_EDGE:
            return TestResult.TRUE
    plex_service = services.get_plex_service()
    if plex_service.is_active_zone_a_plex():
        plex_zone_id_at_pick = plex_service.get_plex_zone_at_position(position, surface.secondary_id)
        if plex_zone_id_at_pick is not None:
            if plex_zone_id_at_pick != services.current_zone_id():
                return TestResult(False, 'Pick point in inactive plex')
    routing_location = routing.Location(position, sims4.math.Quaternion.IDENTITY(), surface)
    routing_context = context.sim.get_routing_context()
    objects_to_ignore = set()
    if target is not None:
        if target.is_sim:
            posture_target = target.posture_target
            if posture_target is not None:
                objects_to_ignore.update(posture_target.parenting_hierarchy_gen())
    if context.sim is not None:
        posture_target = context.sim.posture_target
        if posture_target is not None:
            if posture_target.vehicle_component is not None:
                posture_target = posture_target.part_owner if posture_target.is_part else posture_target
                objects_to_ignore.add(posture_target)
    try:
        for obj in objects_to_ignore:
            footprint_component = obj.footprint_component
            if footprint_component is not None:
                routing_context.ignore_footprint_contour(footprint_component.get_footprint_id())

        if not routing.test_connectivity_permissions_for_handle(routing.connectivity.Handle(routing_location), routing_context):
            return TestResult(False, 'Cannot GoHere! Unroutable area.')
    finally:
        for obj in objects_to_ignore:
            footprint_component = obj.footprint_component
            if footprint_component is not None:
                routing_context.remove_footprint_contour_override(footprint_component.get_footprint_id())

    return TestResult.TRUE