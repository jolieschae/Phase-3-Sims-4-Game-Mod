# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\fire_visualization.py
# Compiled at: 2018-09-28 17:47:51
# Size of source mod 2**32: 3608 bytes
from debugvis import Context, KEEP_ALTITUDE
from services.fire_service import FireService
from sims4.color import Color
import services, sims4.math, terrain
from sims4.geometry import QtCircle, QtRect

class FireQuadTreeVisualizer:

    def __init__(self, layer):
        self.layer = layer
        self._start()

    def _start(self):
        services.get_fire_service().on_quadtree_changed.append(self._on_quadtree_changed)
        self._on_quadtree_changed()

    def stop(self):
        services.get_fire_service().on_quadtree_changed.remove(self._on_quadtree_changed)

    def _on_quadtree_changed(self):
        fire_service = services.get_fire_service()
        fire_quadtree = fire_service.fire_quadtree
        flammable_quadtree = fire_service.flammable_objects_quadtree
        zone = services.current_zone()
        pos = sims4.math.Vector2(0, 0)
        bounds = sims4.geometry.QtCircle(pos, 10000)
        if fire_quadtree is not None:
            fire_objects = fire_quadtree.query(bounds)
        else:
            fire_objects = []
        if flammable_quadtree is not None:
            flammable_objects = flammable_quadtree.query(bounds)
        else:
            flammable_objects = []
        with Context(self.layer) as (layer):
            layer.set_color(Color.RED)
            for obj in fire_objects:
                level = obj.location.level
                height = terrain.get_lot_level_height(obj.position.x, obj.position.z, level, zone.id) + 0.1
                radius = FireService.FIRE_QUADTREE_RADIUS
                pos = sims4.math.Vector3(obj.position.x, height, obj.position.z)
                layer.add_circle(pos, radius, altitude=KEEP_ALTITUDE)

            layer.set_color(Color.YELLOW)
            for obj in flammable_objects:
                if obj.location.world_routing_surface is None:
                    continue
                else:
                    level = obj.location.level
                    height = terrain.get_lot_level_height(obj.position.x, obj.position.z, level, zone.id) + 0.1
                    object_bounds = obj.object_bounds_for_flammable_object(FireService.FIRE_RETARDANT_EXTRA_OBJECT_RADIUS)
                    if isinstance(object_bounds, QtCircle):
                        pos = sims4.math.Vector3(obj.position.x, height, obj.position.z)
                        layer.add_circle(pos, (object_bounds.radius), altitude=KEEP_ALTITUDE)
                if isinstance(object_bounds, QtRect):
                    v0 = sims4.math.Vector3(object_bounds.a.x, height, object_bounds.a.y)
                    v2 = sims4.math.Vector3(object_bounds.b.x, height, object_bounds.b.y)
                    delta = v2 - v0
                    v1 = v0 + sims4.math.Vector3(delta.x, 0, 0)
                    v3 = v0 + sims4.math.Vector3(0, 0, delta.z)
                    vertices = [v0, v1, v2, v3]
                    layer.add_polygon(vertices, altitude=KEEP_ALTITUDE)