# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_service.py
# Compiled at: 2018-11-16 19:04:28
# Size of source mod 2**32: 2017 bytes
from _collections import defaultdict
from sims4.service_manager import Service
import sims4.geometry

class GardeningService(Service):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._gardening_quadtrees = defaultdict(sims4.geometry.QuadTree)

    def add_gardening_object(self, obj):
        quadtree = self._gardening_quadtrees[obj.level]
        quadtree.insert(obj, obj.get_bounding_box())

    def get_gardening_objects(self, *, level, center, radius):
        if level not in self._gardening_quadtrees:
            return
        if isinstance(center, sims4.math.Vector3):
            center = sims4.math.Vector2(center.x, center.z)
        bounds = sims4.geometry.QtCircle(center, radius)
        quadtree = self._gardening_quadtrees[level]
        results = quadtree.query(bounds)
        return results

    def move_gardening_object(self, obj):
        for quadtree in self._gardening_quadtrees.values():
            quadtree.remove(obj)

        self.add_gardening_object(obj)

    def remove_gardening_object(self, obj):
        quadtree = self._gardening_quadtrees[obj.level]
        quadtree.remove(obj)