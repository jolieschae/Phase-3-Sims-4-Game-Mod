# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\swimming_mixin.py
# Compiled at: 2019-07-19 15:52:19
# Size of source mod 2**32: 1587 bytes
import routing

class SwimmingMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._provided_routing_surface = None
        self._world_routing_surface = None

    def is_routing_surface_overlapped_at_position(self, _):
        return False

    @property
    def provided_routing_surface(self):
        return self._provided_routing_surface

    @property
    def world_routing_surface(self):
        return self._world_routing_surface

    def _build_routing_surfaces(self):
        self._provided_routing_surface = routing.SurfaceIdentifier(self.zone_id, self._location.world_routing_surface.secondary_id, routing.SurfaceType.SURFACETYPE_POOL)
        self._world_routing_surface = routing.SurfaceIdentifier(self.zone_id, self._location.world_routing_surface.secondary_id, routing.SurfaceType.SURFACETYPE_WORLD)