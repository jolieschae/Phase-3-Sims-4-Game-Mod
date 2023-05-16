# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\object_routing_service.py
# Compiled at: 2021-04-02 15:06:11
# Size of source mod 2**32: 21819 bytes
import services, sims4
from _collections import defaultdict
from _weakrefset import WeakSet
import alarms
from date_and_time import create_time_span
from event_testing.register_test_event_mixin import RegisterTestEventMixin
from functools import cmp_to_key
from routing.object_routing.object_routing_priority import ObjectRoutingPriority
from sims4.service_manager import Service
from sims4.tuning.tunable import Tunable, TunableSimMinute
from weakref import WeakKeyDictionary
logger = sims4.log.Logger('ObjectRoutingService', default_owner='bnguyen')

class RoutableObjectData:
    __slots__ = ('last_route_timestamp', 'last_sleep_timestamp', 'promoted_priority',
                 'has_routing_reservation', '_sleep_element')

    def __init__(self, last_route_timestamp=None):
        self.last_route_timestamp = last_route_timestamp
        self.last_sleep_timestamp = None
        self.promoted_priority = None
        self.has_routing_reservation = False
        self._sleep_element = None

    def update_last_route_timestamp_to_now(self):
        self.last_route_timestamp = services.time_service().sim_now

    def start_sleeping(self, element):
        self.last_sleep_timestamp = services.time_service().sim_now
        self._sleep_element = element

    def reset_sleep_timer(self):
        self.last_sleep_timestamp = services.time_service().sim_now

    def wake_up(self):
        if not self.is_sleeping():
            logger.error('Trying to wake up RoutableObjectData with no sleep element')
            return
        self.last_sleep_timestamp = None
        self._sleep_element.trigger_soft_stop()
        self._sleep_element = None

    def is_sleeping(self):
        return self._sleep_element is not None


class ObjectRoutingService(RegisterTestEventMixin, Service):
    CACHE_INVALIDATION_TIME = TunableSimMinute(description='\n        The interval used to clear the cache\n        The cache is used to store valid targets when calling ObjectRouteFromTargetObject _find_target\n        by tuning object type (cleaner, fixer, gardening, party bots for example)\n        ',
      default=15,
      minimum=1)
    OBJECT_ROUTING_HARD_CAP = Tunable(description='\n        Hard cap defining how many objects can be routing simultaneously.\n        ',
      tunable_type=int,
      default=30)
    OBJECT_ROUTING_SOFT_CAP_THRESHOLD = Tunable(description='\n        Used to determine the SoftCap for how many objects can be routing simultaneously.\n        SoftCap = SimCap - SimsInZone + OBJECT_ROUTING_SOFT_CAP_THRESHOLD.\n        Only CRITICAL priority ObjectRoutingBehaviors can bypass this soft cap.\n        ',
      tunable_type=int,
      default=5)
    ROUTE_WAIT_DURATION = TunableSimMinute(description='\n        When an ObjectRoutingBehavior is blocked from routing due to being at the routing SoftCap,\n        how many sim minutes to wait before trying again.\n        ',
      default=1,
      minimum=1)
    PROMOTION_WAIT_DURATION = TunableSimMinute(description="\n        When an ObjectRoutingBehavior is blocked from routing due to being at the routing SoftCap,\n        how many sim minutes to wait before promoting the behavior's priority.\n        ",
      default=5,
      minimum=1)

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._active_objects = defaultdict(WeakSet)
        self._route_cache = {}
        timespan = create_time_span(minutes=(self.CACHE_INVALIDATION_TIME))
        self._cache_clear_timer = alarms.add_alarm(self, timespan, (self._clear_cache), repeating=True)
        self._routable_objects = WeakKeyDictionary()
        self._soft_cap_debug_override = None
        self._hard_cap_debug_override = None
        self._soft_cap_threshold_debug_override = None

    def on_active_routing_start(self, obj, tracking_category, behavior):
        self._active_objects[tracking_category].add(obj)

    def on_active_routing_stop(self, obj, tracking_category):
        self._active_objects[tracking_category].remove(obj)

    def get_active_routing_object_set(self, tracking_category):
        return self._active_objects[tracking_category]

    def get_active_routing_object_count(self, tracking_category):
        return len(self.get_active_routing_object_set(tracking_category))

    def add_routable_object(self, obj):
        if obj in self._routable_objects:
            logger.error('Trying to add routable object {} which is already being tracked by the ObjectRoutingService'.format(obj))
            return
        data = RoutableObjectData()
        data.update_last_route_timestamp_to_now()
        self._routable_objects[obj] = data

    def remove_routable_object(self, obj):
        if obj not in self._routable_objects:
            logger.error('Trying to remove routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        del self._routable_objects[obj]

    def acquire_routing_reservation(self, obj):
        if self.has_routing_reservation(obj):
            logger.error('Object {} already has a routing reservation, it cannot acquire another'.format(obj))
            return
        data = self._routable_objects.get(obj)
        data.has_routing_reservation = True
        data.update_last_route_timestamp_to_now()
        data.promoted_priority = None

    def release_routing_reservation(self, obj):
        if not self.has_routing_reservation(obj):
            return
        data = self._routable_objects.get(obj)
        data.has_routing_reservation = False
        sorted_objects = self._get_promoted_and_sorted_objects()
        for obj in sorted_objects:
            data = self._routable_objects.get(obj)
            if data.is_sleeping() and self.can_object_route(obj, sorted_objects):
                self.acquire_routing_reservation(obj)
                data.wake_up()
                break

    def has_routing_reservation(self, obj):
        if obj not in self._routable_objects:
            logger.error('Trying to retrieve routing reservation for routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return False
        data = self._routable_objects.get(obj)
        return data.has_routing_reservation

    def register_sleep_element(self, obj, element):
        if obj not in self._routable_objects:
            logger.error('Trying to register sleep element for routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        data = self._routable_objects.get(obj)
        data.start_sleeping(element)

    def get_object_promoted_routing_priority(self, obj):
        if obj not in self._routable_objects:
            logger.error('Trying to get promoted routing priority for routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        data = self._routable_objects.get(obj)
        return data.promoted_priority

    def get_object_last_route_timestamp(self, obj):
        if obj not in self._routable_objects:
            logger.error('Trying to get last route timestamp for routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        data = self._routable_objects.get(obj)
        return data.last_route_timestamp

    def get_object_last_sleep_timestamp(self, obj):
        if obj not in self._routable_objects:
            logger.error('Trying to get last sleep timestamp for routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        data = self._routable_objects.get(obj)
        return data.last_sleep_timestamp

    def stop_routable_object(self, obj, hard_stop):
        if obj not in self._routable_objects:
            logger.error('Trying to stop routable object {} which is not being tracked by the ObjectRoutingService'.format(obj))
            return
        self.release_routing_reservation(obj)
        if hard_stop:
            self.remove_routable_object(obj)
            self.add_routable_object(obj)
        else:
            data = self._routable_objects.get(obj)
            timestamp = data.last_route_timestamp
            data.__init__(timestamp)

    def can_object_route(self, obj, sorted_objects=None):
        num_reservations = self._get_num_routing_reservations()
        if num_reservations >= self._get_object_routing_hard_cap():
            return False
        soft_cap = self._get_object_routing_soft_cap()
        if len(self._routable_objects) <= soft_cap:
            return True
        if num_reservations >= soft_cap:
            priority = self._get_object_routing_priority(obj)
            if priority is ObjectRoutingPriority.NONE:
                logger.error("RoutableObject {} is set to priority NONE, we shouldn't be querying if it can route.".format(obj))
            return priority is ObjectRoutingPriority.CRITICAL
        if sorted_objects is None:
            sorted_objects = self._get_promoted_and_sorted_objects()
        index = sorted_objects.index(obj)
        return index < soft_cap

    def get_sorted_objects(self):
        return sorted((self._routable_objects.keys()), key=(cmp_to_key(self._compare_routable_objects)))

    def set_object_routing_soft_cap_debug_override(self, override):
        self._soft_cap_debug_override = override

    def set_object_routing_hard_cap_debug_override(self, override):
        self._hard_cap_debug_override = override

    def set_object_routing_soft_cap_threshold_debug_override(self, override):
        self._soft_cap_threshold_debug_override = override

    def set_objects_cache_for_type(self, route_object_type, objects):
        self._route_cache[route_object_type] = objects

    def get_objects_from_cache(self, route_object_type):
        if route_object_type in self._route_cache:
            objects = self._route_cache[route_object_type]
            if not objects:
                return
            return objects

    def clear_cache_for_type(self, route_object_type):
        if route_object_type in self._route_cache:
            del self._route_cache[route_object_type]
            return True
        return False

    def remove_target_from_cache(self, route_object_type, target):
        if route_object_type in self._route_cache:
            for obj in reversed(self._route_cache[route_object_type]):
                if obj == target:
                    self._route_cache[route_object_type].remove(obj)
                    break

    def routable_objects_gen(self):
        for obj in self._routable_objects.keys():
            if obj is not None:
                yield obj

    def _clear_cache(self, handle):
        self._route_cache.clear()

    def _get_object_routing_priority(self, obj, ignore_promoted=False):
        promoted_priority = self.get_object_promoted_routing_priority(obj)
        if promoted_priority is not None:
            if ignore_promoted is False:
                return promoted_priority
        return obj.get_object_routing_priority()

    def _promote_objects_priorities(self):
        objects_to_promote = list()
        active_priorities = set()
        time_now = services.time_service().sim_now
        for obj, data in self._routable_objects.items():
            active_priorities.add(self._get_object_routing_priority(obj))
            active_priorities.add(self._get_object_routing_priority(obj, True))
            if not data.is_sleeping():
                continue
            time_delta = time_now - data.last_sleep_timestamp
            if time_delta.in_minutes() >= self.PROMOTION_WAIT_DURATION:
                objects_to_promote.append(obj)

        sorted_active_priorities = sorted(active_priorities, key=(cmp_to_key(ObjectRoutingPriority.compare)))
        for obj in objects_to_promote:
            priority = self._get_object_routing_priority(obj)
            index = sorted_active_priorities.index(priority)
            if index != 0:
                data = self._routable_objects.get(obj)
                data.promoted_priority = sorted_active_priorities[index - 1]
                data.reset_sleep_timer()

    def _get_promoted_and_sorted_objects(self):
        self._promote_objects_priorities()
        return self.get_sorted_objects()

    def _get_object_routing_soft_cap(self):
        if self._soft_cap_debug_override is not None:
            return self._soft_cap_debug_override
        threshold = self.OBJECT_ROUTING_SOFT_CAP_THRESHOLD
        if self._soft_cap_threshold_debug_override is not None:
            threshold = self._soft_cap_threshold_debug_override
        sim_cap = services.sim_spawner_service().NPC_SOFT_CAP
        num_sims = services.get_master_controller().get_num_sims()
        soft_cap = sim_cap - num_sims + threshold
        return max(soft_cap, 1)

    def _get_object_routing_hard_cap(self):
        if self._hard_cap_debug_override is not None:
            return self._hard_cap_debug_override
        return self.OBJECT_ROUTING_HARD_CAP

    def _get_num_routing_reservations(self):
        count = 0
        for data in self._routable_objects.values():
            if data.has_routing_reservation:
                count += 1

        return count

    def _compare_routable_objects(self, x, y):
        x_priority = self._get_object_routing_priority(x)
        y_priority = self._get_object_routing_priority(y)
        compare_val = ObjectRoutingPriority.compare(x_priority, y_priority)
        if compare_val != 0:
            return compare_val
        data_x = self._routable_objects.get(x)
        data_y = self._routable_objects.get(y)
        return data_x.last_route_timestamp.absolute_ticks() - data_y.last_route_timestamp.absolute_ticks()