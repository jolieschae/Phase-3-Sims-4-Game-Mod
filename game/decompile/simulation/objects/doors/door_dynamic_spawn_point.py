# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\doors\door_dynamic_spawn_point.py
# Compiled at: 2017-10-13 20:03:16
# Size of source mod 2**32: 4622 bytes
from sims4.tuning.tunable import TunableEnumEntry
from singletons import EMPTY_SET
from world.spawn_point import SpawnPoint
from world.spawn_point_enums import SpawnPointPriority, SpawnPointRequestReason
import interactions.constraints, services, sims4.math
logger = sims4.log.Logger('InactiveApartment', default_owner='tingyul')

class InactiveApartmentDoorDynamicSpawnPoint(SpawnPoint):
    SPAWN_POINT_PRIORITY = TunableEnumEntry(description='\n        The priority of the inactive apartment door spawn point.\n        ',
      tunable_type=SpawnPointPriority,
      default=(SpawnPointPriority.DEFAULT))

    def __init__(self, owner, *, is_front):
        self._owner = owner
        self._is_front = is_front
        lot_id = services.active_lot_id() if owner.is_on_active_lot() else 0
        super().__init__(lot_id, (owner.zone_id), routing_surface=(owner.routing_surface))

    @property
    def spawn_point_priority(self):
        return self.SPAWN_POINT_PRIORITY

    def get_tags(self):
        return {
         SpawnPoint.ARRIVAL_SPAWN_POINT_TAG, SpawnPoint.VISITOR_ARRIVAL_SPAWN_POINT_TAG}

    def is_valid(self, sim_info=None, spawn_point_request_reason=SpawnPointRequestReason.DEFAULT):
        if sim_info is None:
            return False
        for plex_door_info in services.get_door_service().get_plex_door_infos():
            if plex_door_info.door_id == self._owner.id:
                break
        else:
            logger.error('Failed to find plex door info for door {}', self._owner)
            return False

        if spawn_point_request_reason == SpawnPointRequestReason.SPAWN:
            if sim_info.prespawn_zone_id == plex_door_info.zone_id:
                return True
            return False
        if spawn_point_request_reason == SpawnPointRequestReason.LEAVE:
            if sim_info.household.home_zone_id == plex_door_info.zone_id:
                return True
            return False
        return False

    def get_approximate_transform(self):
        return sims4.math.Transform(self.next_spawn_spot())

    def get_approximate_center(self):
        return self._get_pos()

    def get_name(self):
        return 'DoorDynamicSpawnPoint: {}, IsFront: {}'.format(self._owner, self._is_front)

    def next_spawn_spot(self):
        pos = self._get_pos()
        orient = self._get_orientation(pos)
        return (pos, orient)

    def validate_connectivity(self, dest_handles):
        pass

    def get_valid_and_invalid_positions(self):
        return (
         (
          self._get_pos(),), tuple())

    def get_position_constraints(self, generalize=False):
        pos = self._get_pos()
        return [interactions.constraints.Position(pos, routing_surface=(self.routing_surface), objects_to_ignore=(set([self.spawn_point_id])))]

    def _get_pos(self):
        front_position, back_position = self._owner.get_door_positions()
        if self._is_front:
            return front_position
        return back_position + (back_position - self._owner.position)

    def _get_orientation(self, pos):
        front_position, _ = self._owner.get_door_positions()
        v = front_position - self._owner.position
        theta = sims4.math.vector3_angle(v)
        return sims4.math.angle_to_yaw_quaternion(theta)

    @property
    def routing_surface(self):
        return self._owner.routing_surface