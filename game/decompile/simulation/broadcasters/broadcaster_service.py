# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\broadcasters\broadcaster_service.py
# Compiled at: 2020-11-19 15:20:58
# Size of source mod 2**32: 31263 bytes
from _collections import defaultdict
from _weakrefset import WeakSet
from collections import namedtuple
from alarms import add_alarm_real_time, cancel_alarm, add_alarm
from clock import interval_in_real_seconds
from indexed_manager import CallbackTypes
from routing.route_enums import RouteEventType
from sims4.callback_utils import CallableList
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableRealSecond
import services, sims4.geometry, sims4.log, sims4.math
logger = sims4.log.Logger('Broadcaster', default_owner='epanero')

class BroadcasterService(Service):
    INTERVAL = TunableRealSecond(description='\n        The time between broadcaster pulses. A lower number will impact\n        performance.\n        ',
      default=5)
    DEFAULT_QUADTREE_RADIUS = 0.1

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._alarm_handle = None
        self._processing_task = None
        self._on_update_callbacks = CallableList()
        self._pending_broadcasters = []
        self._active_broadcasters = []
        self._cluster_requests = {}
        self._object_cache = None
        self._object_cache_tags = None
        self._pending_update = False
        self._quadtrees = defaultdict(sims4.geometry.QuadTree)

    def create_update_alarm(self):
        self._alarm_handle = add_alarm(self, (interval_in_real_seconds(self.INTERVAL)), (self._on_update), repeating=True, use_sleep_time=False)

    def start(self):
        self.create_update_alarm()
        object_manager = services.object_manager()
        object_manager.register_callback(CallbackTypes.ON_OBJECT_LOCATION_CHANGED, self._update_object_cache)
        object_manager.register_callback(CallbackTypes.ON_OBJECT_ADD, self._update_object_cache)
        services.current_zone().wall_contour_update_callbacks.append(self._on_wall_contours_changed)

    def stop(self):
        if self._alarm_handle is not None:
            cancel_alarm(self._alarm_handle)
            self._alarm_handle = None
        if self._processing_task is not None:
            self._processing_task.stop()
            self._processing_task = None
        object_manager = services.object_manager()
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_LOCATION_CHANGED, self._update_object_cache)
        object_manager.unregister_callback(CallbackTypes.ON_OBJECT_ADD, self._update_object_cache)
        services.current_zone().wall_contour_update_callbacks.remove(self._on_wall_contours_changed)

    def add_broadcaster(self, broadcaster):
        if broadcaster not in self._pending_broadcasters:
            self._pending_broadcasters.append(broadcaster)
            if broadcaster.immediate:
                self._pending_update = True
            self._on_update_callbacks()

    def remove_broadcaster(self, broadcaster):
        if broadcaster in self._pending_broadcasters:
            self._pending_broadcasters.remove(broadcaster)
        if broadcaster in self._active_broadcasters:
            self._remove_from_cluster_request(broadcaster)
            self._remove_broadcaster_from_quadtree(broadcaster)
            self._active_broadcasters.remove(broadcaster)
        broadcaster.on_removed()
        self._on_update_callbacks()

    def _activate_pending_broadcasters(self):
        for broadcaster in self._pending_broadcasters:
            self._active_broadcasters.append(broadcaster)
            self.update_cluster_request(broadcaster)
            self._update_object_cache()

        self._pending_broadcasters.clear()

    def _add_broadcaster_to_quadtree(self, broadcaster):
        self._remove_broadcaster_from_quadtree(broadcaster)
        broadcaster_quadtree = self._quadtrees[broadcaster.routing_surface.secondary_id]
        broadcaster_bounds = sims4.geometry.QtCircle(sims4.math.Vector2(broadcaster.position.x, broadcaster.position.z), self.DEFAULT_QUADTREE_RADIUS)
        broadcaster_quadtree.insert(broadcaster, broadcaster_bounds)
        return broadcaster_quadtree

    def _remove_broadcaster_from_quadtree(self, broadcaster):
        broadcaster_quadtree = broadcaster.quadtree
        if broadcaster_quadtree is not None:
            broadcaster_quadtree.remove(broadcaster)

    def update_cluster_request(self, broadcaster):
        if broadcaster not in self._active_broadcasters:
            return
            clustering_request = broadcaster.get_clustering()
            if clustering_request is None:
                return
            self._remove_from_cluster_request(broadcaster)
            cluster_request_key = (type(broadcaster), broadcaster.routing_surface.secondary_id)
            if cluster_request_key in self._cluster_requests:
                cluster_request = self._cluster_requests[cluster_request_key]
                cluster_request.set_object_dirty(broadcaster)
        else:
            cluster_quadtree = self._quadtrees[broadcaster.routing_surface.secondary_id]
            cluster_request = clustering_request((lambda: (self._get_broadcasters_for_cluster_request_gen)(*cluster_request_key)), quadtree=cluster_quadtree)
            self._cluster_requests[cluster_request_key] = cluster_request
        quadtree = self._add_broadcaster_to_quadtree(broadcaster)
        broadcaster.on_added_to_quadtree_and_cluster_request(quadtree, cluster_request)

    def _remove_from_cluster_request(self, broadcaster):
        cluster_request = broadcaster.cluster_request
        if cluster_request is not None:
            cluster_request.set_object_dirty(broadcaster)

    def _is_valid_cache_object(self, obj):
        if obj.is_sim:
            return False
        if self._object_cache_tags:
            object_tags = obj.get_tags()
            if object_tags & self._object_cache_tags:
                return True
            return False
        return True

    def get_object_cache_info(self):
        return (
         self._object_cache, self._object_cache_tags)

    def _generate_object_cache(self):
        self._object_cache = WeakSet((obj for obj in services.object_manager().valid_objects() if self._is_valid_cache_object(obj)))

    def _update_object_cache(self, obj=None):
        if obj is None:
            self._object_cache = None
            self._object_cache_tags = None
            return
        if self._object_cache is not None:
            if self._is_valid_cache_object(obj):
                self._object_cache.add(obj)

    def _is_valid_broadcaster(self, broadcaster):
        broadcasting_object = broadcaster.broadcasting_object
        return broadcasting_object is None or broadcasting_object.visible_to_client or False
        if broadcasting_object.is_in_inventory():
            return False
        if broadcasting_object.parent is not None:
            if broadcasting_object.parent.is_sim:
                return False
        return True

    def _get_broadcasters_for_cluster_request_gen(self, broadcaster_type, broadcaster_level):
        for broadcaster in self._active_broadcasters:
            if broadcaster.guid == broadcaster_type.guid and broadcaster.should_cluster() and broadcaster.routing_surface.secondary_id == broadcaster_level:
                yield broadcaster

    def get_broadcasters_debug_gen(self):
        for cluster_request in self._cluster_requests.values():
            for cluster in cluster_request.get_clusters_gen():
                broadcaster_iter = cluster.objects_gen()
                yield next(broadcaster_iter)

            yield from cluster_request.get_rejects()

        for broadcaster in self._active_broadcasters:
            if broadcaster.should_cluster() or self._is_valid_broadcaster(broadcaster):
                yield broadcaster

    def get_broadcasters_gen(self):
        for cluster_request_key, cluster_request in self._cluster_requests.items():
            is_cluster_dirty = cluster_request.is_dirty()
            if is_cluster_dirty:
                for broadcaster in (self._get_broadcasters_for_cluster_request_gen)(*cluster_request_key):
                    if self._is_valid_broadcaster(broadcaster):
                        broadcaster.regenerate_constraint()

            for cluster in cluster_request.get_clusters_gen():
                linkable_broadcasters_iter = (b for b in cluster.objects_gen() if self._is_valid_broadcaster(b))
                master_broadcaster = next(linkable_broadcasters_iter, None)
                if master_broadcaster is None:
                    continue
                master_broadcaster.set_linked_broadcasters(linkable_broadcasters_iter)
                yield master_broadcaster

            yield from (b for b in cluster_request.get_rejects() if self._is_valid_broadcaster(b))

        for broadcaster in self._active_broadcasters:
            if broadcaster.should_cluster() or self._is_valid_broadcaster(broadcaster):
                yield broadcaster

    PathSegmentData = namedtuple('PathSegmentData', ('prev_pos', 'cur_pos', 'segment_vec',
                                                     'segment_mag_sq', 'segment_normal'))

    def get_broadcasters_along_route_gen(self, sim, path, start_time=0, end_time=0):
        path_segment_datas = {}
        start_index = max(0, path.node_at_time(start_time).index - 1)
        end_index = min(len(path) - 1, path.node_at_time(end_time).index)
        for broadcaster in self.get_broadcasters_gen():
            if broadcaster.route_events:
                if not broadcaster.can_affect(sim):
                    continue
                constraint = broadcaster.get_constraint()
                geometry = constraint.geometry
                if geometry is None:
                    continue
                polygon = geometry.polygon
                if polygon is None:
                    continue
                if not constraint.valid:
                    continue
                found_time = None
                constraint_pos = polygon.centroid()
                constraint_radius_sq = polygon.radius()
                constraint_radius_sq = constraint_radius_sq * constraint_radius_sq
                for index in range(end_index, start_index, -1):
                    prev_index = index - 1
                    prev_node = path.nodes[prev_index]
                    if not constraint.is_routing_surface_valid(prev_node.routing_surface_id):
                        continue
                    else:
                        segment_key = (
                         prev_index, index)
                        segment_data = path_segment_datas.get(segment_key, None)
                        if segment_data is None:
                            cur_node = path.nodes[index]
                            cur_pos = (sims4.math.Vector3)(*cur_node.position)
                            prev_pos = (sims4.math.Vector3)(*prev_node.position)
                            segment_vec = cur_pos - prev_pos
                            segment_mag_sq = segment_vec.magnitude_2d_squared()
                            if sims4.math.almost_equal_sq(segment_mag_sq, 0):
                                unit_segment = None
                            else:
                                unit_segment = segment_vec / sims4.math.sqrt(segment_mag_sq)
                            segment_data = BroadcasterService.PathSegmentData(prev_pos, cur_pos, segment_vec, segment_mag_sq, unit_segment)
                            path_segment_datas[segment_key] = segment_data
                        else:
                            prev_pos, cur_pos, segment_vec, segment_mag_sq, unit_segment = segment_data
                    constraint_vec = constraint_pos - prev_pos
                    if unit_segment is None:
                        constraint_dist_sq = constraint_vec.magnitude_2d_squared()
                        if constraint_radius_sq < constraint_dist_sq:
                            continue
                        elif geometry.test_transform(sims4.math.Transform(prev_pos, (sims4.math.Quaternion)(*prev_node.orientation))):
                            found_time = prev_node.time
                            break
                        else:
                            continue
                    else:
                        constraint_comp = sims4.math.vector_dot_2d(constraint_vec, unit_segment)
                        if constraint_comp <= 0:
                            closest = prev_pos
                        else:
                            if constraint_comp * constraint_comp >= segment_mag_sq:
                                closest = cur_pos
                            else:
                                closest = prev_pos + unit_segment * constraint_comp
                        proj_vec = constraint_pos - closest
                        if constraint_radius_sq < proj_vec.magnitude_2d_squared():
                            continue
                        b = 2 * sims4.math.vector_dot_2d(constraint_vec, segment_vec)
                        discriminant = b * b - 4 * segment_mag_sq * (constraint_vec.magnitude_2d_squared() - constraint_radius_sq)
                        discriminant = sims4.math.sqrt(discriminant)
                        denom = 2 * segment_mag_sq
                        t1 = (b - discriminant) / denom
                        t2 = (b + discriminant) / denom
                        normalized_start, normalized_end = (0, 1)
                        if t1 >= 0:
                            if t1 <= 1:
                                normalized_start = t1
                        if t2 >= 0:
                            if t2 <= 1:
                                normalized_end = t2
                        for transform, _, time in path.get_location_data_along_segment_gen(prev_index, index, start_time=normalized_start,
                          stop_time=normalized_end):
                            if not geometry.test_transform(transform):
                                continue
                            found_time = time
                            break
                        else:
                            continue

                        break

                if found_time is not None:
                    yield (
                     found_time, broadcaster)

    def get_pending_broadcasters_gen(self):
        yield from self._pending_broadcasters
        if False:
            yield None

    def _get_all_objects_gen(self):
        is_any_broadcaster_allowing_objects = True if self._object_cache else False
        if not is_any_broadcaster_allowing_objects:
            for broadcaster in self._active_broadcasters:
                allow_objects, allow_objects_tags = broadcaster.allow_objects.is_affecting_objects()
                if allow_objects:
                    is_any_broadcaster_allowing_objects = True
                    if allow_objects_tags is None:
                        self._object_cache_tags = None
                        break
                    else:
                        if self._object_cache_tags is None:
                            self._object_cache_tags = set()
                        self._object_cache_tags |= allow_objects_tags

        elif is_any_broadcaster_allowing_objects:
            if self._object_cache is None:
                self._generate_object_cache()
            yield from list(self._object_cache)
        else:
            self._object_cache = None
            self._object_cache_tags = None
        yield from services.sim_info_manager().instanced_sims_gen()
        if False:
            yield None

    def register_callback(self, callback):
        if callback not in self._on_update_callbacks:
            self._on_update_callbacks.append(callback)

    def unregister_callback(self, callback):
        if callback in self._on_update_callbacks:
            self._on_update_callbacks.remove(callback)

    def _on_update(self, _):
        self._pending_update = True

    def _on_wall_contours_changed(self, *_, **__):
        self._update_object_cache()

    def provide_route_events(self, route_event_context, sim, path, failed_types=None, start_time=0, end_time=0, **kwargs):
        for time, broadcaster in self.get_broadcasters_along_route_gen(sim, path, start_time=start_time, end_time=end_time):
            resolver = broadcaster.get_resolver(sim)
            for route_event in broadcaster.route_events:
                if broadcaster.can_provide_route_event(route_event, failed_types, resolver):
                    route_event_context.route_event_already_scheduled(route_event, provider=broadcaster) or route_event_context.add_route_event(RouteEventType.BROADCASTER, route_event(time=time, provider=broadcaster, provider_required=True))

    def update(self):
        if self._pending_update:
            self._pending_update = False
            self._update()

    def _is_location_affected(self, constraint, transform, routing_surface):
        if constraint.geometry is not None:
            if not constraint.geometry.test_transform(transform):
                return False
        else:
            return constraint.is_routing_surface_valid(routing_surface) or False
        return True

    def update_broadcasters_one_shot--- This code section failed: ---

 L. 578         0  SETUP_LOOP          146  'to 146'
                2  LOAD_FAST                'self'
                4  LOAD_METHOD              _get_all_objects_gen
                6  CALL_METHOD_0         0  '0 positional arguments'
                8  GET_ITER         
               10  FOR_ITER            144  'to 144'
               12  STORE_FAST               'obj'

 L. 579        14  LOAD_CONST               None
               16  STORE_FAST               'object_transform'

 L. 580        18  LOAD_FAST                'obj'
               20  LOAD_ATTR                routing_surface
               22  STORE_FAST               'routing_surface'

 L. 581        24  SETUP_LOOP          142  'to 142'
               26  LOAD_FAST                'broadcasters'
               28  GET_ITER         
             30_0  COME_FROM           134  '134'
             30_1  COME_FROM           108  '108'
             30_2  COME_FROM            42  '42'
               30  FOR_ITER            140  'to 140'
               32  STORE_FAST               'broadcaster'

 L. 582        34  LOAD_FAST                'broadcaster'
               36  LOAD_METHOD              can_affect
               38  LOAD_FAST                'obj'
               40  CALL_METHOD_1         1  '1 positional argument'
               42  POP_JUMP_IF_FALSE    30  'to 30'

 L. 585        44  LOAD_FAST                'broadcaster'
               46  LOAD_METHOD              get_constraint
               48  CALL_METHOD_0         0  '0 positional arguments'
               50  STORE_FAST               'constraint'

 L. 586        52  LOAD_FAST                'constraint'
               54  LOAD_ATTR                valid
               56  POP_JUMP_IF_TRUE     60  'to 60'

 L. 587        58  CONTINUE             30  'to 30'
             60_0  COME_FROM            56  '56'

 L. 590        60  LOAD_FAST                'object_transform'
               62  LOAD_CONST               None
               64  COMPARE_OP               is
               66  POP_JUMP_IF_FALSE    96  'to 96'

 L. 591        68  LOAD_FAST                'obj'
               70  LOAD_ATTR                parent
               72  STORE_FAST               'parent'

 L. 592        74  LOAD_FAST                'parent'
               76  LOAD_CONST               None
               78  COMPARE_OP               is
               80  POP_JUMP_IF_FALSE    90  'to 90'

 L. 593        82  LOAD_FAST                'obj'
               84  LOAD_ATTR                transform
               86  STORE_FAST               'object_transform'
               88  JUMP_FORWARD         96  'to 96'
             90_0  COME_FROM            80  '80'

 L. 595        90  LOAD_FAST                'parent'
               92  LOAD_ATTR                transform
               94  STORE_FAST               'object_transform'
             96_0  COME_FROM            88  '88'
             96_1  COME_FROM            66  '66'

 L. 597        96  LOAD_FAST                'self'
               98  LOAD_METHOD              _is_location_affected
              100  LOAD_FAST                'constraint'
              102  LOAD_FAST                'object_transform'
              104  LOAD_FAST                'routing_surface'
              106  CALL_METHOD_3         3  '3 positional arguments'
              108  POP_JUMP_IF_FALSE    30  'to 30'

 L. 598       110  LOAD_FAST                'broadcaster'
              112  LOAD_METHOD              apply_broadcaster_effect
              114  LOAD_FAST                'obj'
              116  CALL_METHOD_1         1  '1 positional argument'
              118  POP_TOP          

 L. 599       120  LOAD_FAST                'broadcaster'
              122  LOAD_METHOD              remove_broadcaster_effect
              124  LOAD_FAST                'obj'
              126  CALL_METHOD_1         1  '1 positional argument'
              128  POP_TOP          

 L. 602       130  LOAD_FAST                'obj'
              132  LOAD_ATTR                valid_for_distribution
              134  POP_JUMP_IF_TRUE     30  'to 30'

 L. 603       136  BREAK_LOOP       
              138  JUMP_BACK            30  'to 30'
              140  POP_BLOCK        
            142_0  COME_FROM_LOOP       24  '24'
              142  JUMP_BACK            10  'to 10'
              144  POP_BLOCK        
            146_0  COME_FROM_LOOP        0  '0'

Parse error at or near `COME_FROM_LOOP' instruction at offset 142_0

    def _update(self):
        try:
            self._activate_pending_broadcasters()
            current_broadcasters = set(self.get_broadcasters_gen())
            for obj in self._get_all_objects_gen():
                object_transform = None
                is_affected = False
                for broadcaster in current_broadcasters:
                    if broadcaster.can_affect(obj):
                        constraint = broadcaster.get_constraint()
                        if not constraint.valid:
                            continue
                        if object_transform is None:
                            parent = obj.parent
                            if parent is None:
                                object_transform = obj.transform
                            else:
                                object_transform = parent.transform
                        if self._is_location_affected(constraint, object_transform, obj.routing_surface):
                            broadcaster.apply_broadcaster_effect(obj)
                            if not obj.valid_for_distribution:
                                is_affected = False
                                break
                            is_affected = True

                if is_affected or self._object_cache is not None:
                    self._object_cache.discard(obj)

            for broadcaster in current_broadcasters:
                broadcaster.on_processed()

        finally:
            self._on_update_callbacks()


class BroadcasterRealTimeService(BroadcasterService):

    def create_update_alarm(self):
        self._alarm_handle = add_alarm_real_time(self, (interval_in_real_seconds(self.INTERVAL)), (self._on_update), repeating=True, use_sleep_time=False)