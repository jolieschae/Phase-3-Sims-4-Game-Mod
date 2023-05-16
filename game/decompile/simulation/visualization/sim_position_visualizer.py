# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\visualization\sim_position_visualizer.py
# Compiled at: 2017-06-28 15:23:15
# Size of source mod 2**32: 3715 bytes
from debugvis import Context
from sims4.color import pseudo_random_color
from sims4.geometry import QtCircle
import routing, sims4.math

class SimPositionVisualizer:

    def __init__(self, sim, layer):
        self.sim = sim
        self.layer = layer
        self.start()

    def start(self):
        self.sim.register_on_location_changed(self._on_position_changed)
        routing_component = self.sim.routing_component
        routing_component.on_follow_path.append(self._on_position_changed)
        self.redraw(self.sim)

    def stop(self):
        routing_component = self.sim.routing_component
        if self._on_position_changed in routing_component.on_follow_path:
            routing_component.on_follow_path.remove(self._on_position_changed)
        if self.sim._on_location_changed_callbacks is not None:
            if self._on_position_changed in self.sim._on_location_changed_callbacks:
                self.sim.unregister_on_location_changed(self._on_position_changed)
        with Context(self.layer):
            pass

    def redraw(self, sim):
        routing_context = sim.get_routing_context()
        routing_polygon = routing_context.get_quadtree_polygon()

        def _draw_polygon(position, *, color):
            if isinstance(routing_polygon, QtCircle):
                layer.add_circle(position, (routing_polygon.radius), color=color)
            else:
                layer.add_polygon((list(routing_polygon)), color=color)

        with Context((self.layer), altitude=0.1, routing_surface=(sim.routing_surface)) as (layer):
            position_color = pseudo_random_color(sim.id)
            position = sim.position
            orientation = sim.orientation
            _draw_polygon(position, color=position_color)
            if orientation != sims4.math.Quaternion.ZERO():
                angle = sims4.math.yaw_quaternion_to_angle(orientation)
                layer.add_arrow(position, angle, color=position_color)
            if sim.parent is not None:
                return
            intended_transform = sim.intended_transform
            intended_position = intended_transform.translation
            intended_position_color = pseudo_random_color(sim.id + 1)
            _draw_polygon(intended_position, color=intended_position_color)
            intended_orientation = intended_transform.orientation
            if intended_orientation != sims4.math.Quaternion.ZERO():
                angle = sims4.math.yaw_quaternion_to_angle(intended_orientation)
                layer.add_arrow(intended_position, angle, color=intended_position_color)

    def _on_position_changed(self, *_, **__):
        self.redraw(self.sim)