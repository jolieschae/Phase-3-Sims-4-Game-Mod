# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\pools\pond_visualizer.py
# Compiled at: 2021-06-01 18:18:39
# Size of source mod 2**32: 7389 bytes
import routing, services, sims4, terrain, textwrap
from build_buy import register_build_buy_exit_callback, get_pond_contours_for_wading_depth
from debugvis import Context, KEEP_ALTITUDE
from indexed_manager import CallbackTypes
from objects.pools.pond import Pond
from objects.pools.pond_utils import PondUtils
from routing import SurfaceIdentifier, SurfaceType
from sims4 import commands
from sims4.color import Color, interpolate
from sims4.math import vector_normalize
from visualization.constraint_visualizer import _draw_constraint, _draw_contour

class PondVisualizer:
    POND_COLORS = [
     (
      Color.WHITE, Color.BLUE), (Color.WHITE, Color.ORANGE), (Color.WHITE, Color.GREEN), (Color.WHITE, Color.MAGENTA)]

    def __init__(self, layer, draw_contours=False, pond_obj_id=0):
        self.layer = layer
        self.pond_obj_id = pond_obj_id
        self._draw_contours = draw_contours
        self._start()

    def _start(self):
        object_manager = services.current_zone().object_manager
        object_manager.register_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)
        register_build_buy_exit_callback(self._draw_all_ponds)
        self._draw_all_ponds()

    def stop(self):
        obj_manager = services.current_zone().object_manager
        obj_manager.unregister_callback(CallbackTypes.ON_OBJECT_REMOVE, self._on_object_deleted)

    def _draw_all_ponds(self, *_, **__):
        object_manager = services.object_manager()
        with Context((self.layer), preserve=True) as (context):
            context.layer.clear()
        if self.pond_obj_id:
            pond_obj = object_manager.get(self.pond_obj_id)
            if pond_obj is not None:
                self._draw_pond(pond_obj)
            return
        for pond_obj in PondUtils.get_main_pond_objects_gen():
            self._draw_pond(pond_obj)

    def _on_object_deleted(self, obj):
        if self.pond_obj_id is not None and obj.id == self.pond_obj_id:
            full_command = 'debugvis.portals.stop' + ' {}'.format(self.pond_obj_id)
            client_id = services.client_manager().get_first_client_id()
            commands.execute(full_command, client_id)
        else:
            if isinstance(obj, Pond):
                self._draw_all_ponds()

    def _draw_pond(self, pond_obj):
        with Context((self.layer), preserve=True) as (layer):
            self._display_helper_text(layer)
            if self._draw_contours:
                self._draw_pond_wading_depth(layer, pond_obj)
            else:
                self._draw_pond_fishing_constraints(layer, pond_obj)
                self._draw_edges(layer, pond_obj)

    def _display_helper_text(self, layer):
        pond_visualizer_text = '\n                               =========== Pond Visualizer Info ===========\n                               Outer Edges: Cyan\n                               -------\n                               Fishing edges: White\n                               Fishing Target Locations:\n                                   Red X = rejected due to depth or LOS \n                                   Green X = valid\n                               -------\n                               Depth Contours: White->Color = Shallow->Deep\n                               '
        layer.add_text_screen(sims4.math.Vector2(10, 32), textwrap.dedent(pond_visualizer_text))

    def _draw_edges(self, layer, pond_obj):
        outer_edges = pond_obj.edges(outer_edges_only=True)
        if outer_edges:
            contour = list((edge[0] for edge in outer_edges))
            _draw_contour(layer, contour, Color.CYAN)

    def _draw_pond_wading_depth(self, layer, pond_obj):
        color_idx = pond_obj.pond_id % len(self.POND_COLORS)
        depths = [0, 0.15, 0.35, 0.5, 0.7, 1.0]
        curr = 0
        while curr + 1 < len(depths):
            curr_depth = depths[curr]
            next_depth = depths[curr + 1]
            curr_color = self.POND_COLORS[color_idx][0]
            next_color = self.POND_COLORS[color_idx][1]
            contours = get_pond_contours_for_wading_depth(pond_obj.pond_id, curr_depth, next_depth, SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD))
            if not contours:
                curr += 1
                continue
            ratio = curr_depth / 1.0
            depth_color = interpolate(curr_color, next_color, ratio)
            for contour in contours:
                routing_surface = SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)
                if not routing.test_point_placement_in_navmesh(routing_surface, sims4.geometry.Polygon(contour).centroid()):
                    continue
                _draw_contour(layer, contour, depth_color, altitude=(0.05 + (1.0 - ratio)))

            curr += 1

    def _draw_pond_fishing_constraints(self, layer, pond_obj):
        constraint_constants = PondUtils.FISHING_CONSTRAINT_DATA
        _draw_constraint(layer, pond_obj.get_fishing_constraint(check_in_use=False), (Color.GREY), modify_altitiude=False)
        edges = pond_obj.edges()
        if not edges:
            return
        for start, stop in edges:
            layer.add_segment(stop, start, (Color.WHITE), altitude=KEEP_ALTITUDE)
            layer.add_point(stop, altitude=KEEP_ALTITUDE)
            edge_midpoint = (start + stop) / 2
            along = vector_normalize(stop - start)
            inward = sims4.math.vector_cross(sims4.math.Vector3.Y_AXIS(), along)
            fishing_target_position = edge_midpoint + inward * constraint_constants.distance_from_edge_to_fishing_target
            layer.add_segment(fishing_target_position, edge_midpoint, color=(Color.YELLOW), altitude=KEEP_ALTITUDE)
            if pond_obj.validate_fishing_target_position(fishing_target_position, edge_midpoint):
                layer.add_point(fishing_target_position, color=(Color.GREEN), altitude=KEEP_ALTITUDE)
            else:
                layer.add_point(fishing_target_position, color=(Color.RED), altitude=KEEP_ALTITUDE)