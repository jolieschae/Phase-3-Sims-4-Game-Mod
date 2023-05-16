# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\object_based_situation_zone_director.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 11770 bytes
from _weakrefset import WeakSet
from date_and_time import TimeSpan
from event_testing.resolver import SingleObjectResolver
from objects.components import situation_scheduler_component
from objects.components.types import SITUATION_SCHEDULER_COMPONENT
from scheduler import SituationWeeklyScheduleVariant, WeightedSituationsWeeklySchedule
from sims4.tuning.tunable import TunableMapping, TunableTuple, TunableRange, Tunable
from tag import TunableTag
import services, sims4.log
logger = sims4.log.Logger('ZoneDirector', default_owner='mkartika')

class ObjectBasedSituationData:
    __slots__ = ('situation_schedule', 'schedule_immediate', 'consider_off_lot_objects')

    def __init__(self, situation_schedule=None, schedule_immediate=False, consider_off_lot_objects=True):
        self.situation_schedule = situation_schedule
        self.schedule_immediate = schedule_immediate
        self.consider_off_lot_objects = consider_off_lot_objects


class ObjectBasedSituationZoneDirectorMixin:
    INSTANCE_TUNABLES = {'object_based_situations_schedule':TunableMapping(description='\n            Mapping of object tag to situations schedule. \n            When the object in the tag is exist on the zone lot, the situations\n            will be spawned based on the schedule.\n            ',
       key_type=TunableTag(description='\n                An object tag. If the object exist on the zone lot, situations\n                will be scheduled.\n                ',
       filter_prefixes=('func', )),
       value_type=TunableTuple(description='\n                Data associated with situations schedule.\n                ',
       situation_schedule=SituationWeeklyScheduleVariant(description='\n                    The schedule to trigger the different situations.\n                    ',
       pack_safe=True,
       affected_object_cap=True),
       schedule_immediate=Tunable(description='\n                    This controls the behavior of scheduler if the current time\n                    happens to fall within a schedule entry. If this is True, \n                    a start_callback will trigger immediately for that entry.\n                    If False, the next start_callback will occur on the next entry.\n                    ',
       tunable_type=bool,
       default=False),
       consider_off_lot_objects=Tunable(description='\n                    If True, consider all objects in lot and the open street for\n                    this object situation. If False, only consider objects on\n                    the active lot.\n                    ',
       tunable_type=bool,
       default=True))), 
     'use_object_provided_situations_schedule':Tunable(description='\n            If checked, objects on the lot and supplement or replace elements of\n            Object Based Situations Schedule.\n            ',
       tunable_type=bool,
       default=True)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.affected_objects_map = {}
        self._object_based_situations_schedule = {}

    def create_situations_during_zone_spin_up(self):
        super().create_situations_during_zone_spin_up()
        self._update_object_based_situations_schedule()
        self._cleanup_affected_objects()
        self._setup_affected_objects()

    def on_exit_buildbuy(self):
        super().on_exit_buildbuy()
        self._update_object_based_situations_schedule()
        self._setup_affected_objects()

    def _update_object_based_situations_schedule(self):
        self._object_based_situations_schedule.clear()
        for object_tag, data in self.object_based_situations_schedule.items():
            self._object_based_situations_schedule[object_tag] = data

        if not self.use_object_provided_situations_schedule:
            return
        object_manager = services.object_manager()
        for obj in object_manager.get_valid_objects_gen():
            situation_scheduler_component = obj.get_component(SITUATION_SCHEDULER_COMPONENT)
            if not situation_scheduler_component is None:
                if situation_scheduler_component.can_remove_component:
                    continue
                data = situation_scheduler_component.object_based_situations_schedule
                resolver = SingleObjectResolver(obj)
                if not (data.tests is None or data.tests.run_tests(resolver)):
                    continue
                self._object_based_situations_schedule[data.tag] = ObjectBasedSituationData(data.situation_schedule, data.schedule_immediate, data.consider_off_lot_objects)

    @staticmethod
    def _cleanup_object(obj):
        situation_scheduler_component = obj.get_component(SITUATION_SCHEDULER_COMPONENT)
        if situation_scheduler_component is None:
            return
        elif situation_scheduler_component.can_remove_component:
            obj.remove_component(SITUATION_SCHEDULER_COMPONENT)
        else:
            situation_scheduler_component.destroy_scheduler_and_situations()

    def _cleanup_affected_objects(self):
        object_tags = self._object_based_situations_schedule.keys()
        object_manager = services.object_manager()
        for obj in object_manager.get_valid_objects_gen():
            if not obj.has_any_tag(object_tags):
                self._cleanup_object(obj)

    def _setup_affected_objects(self):
        object_manager = services.object_manager()
        for object_tag, data in self._object_based_situations_schedule.items():
            tagged_objects = []
            if data.consider_off_lot_objects:
                tagged_objects = list(object_manager.get_objects_with_tag_gen(object_tag))
            else:
                tagged_objects = [obj for obj in object_manager.get_objects_with_tag_gen(object_tag) if obj.is_on_active_lot()]
            if not tagged_objects:
                continue
            object_cap = self._get_current_affected_object_cap(data.situation_schedule)
            if object_tag not in self.affected_objects_map:
                self.affected_objects_map[object_tag] = WeakSet()
            affected_objects = self.affected_objects_map[object_tag]
            while len(affected_objects) < object_cap and tagged_objects:
                obj_to_add = tagged_objects.pop()
                if obj_to_add in affected_objects:
                    continue
                else:
                    scheduler = data.situation_schedule(start_callback=(self._start_situations), schedule_immediate=(data.schedule_immediate),
                      extra_data=obj_to_add)
                    if obj_to_add.has_component(SITUATION_SCHEDULER_COMPONENT):
                        obj_to_add.set_situation_scheduler(scheduler)
                    else:
                        obj_to_add.add_dynamic_component(SITUATION_SCHEDULER_COMPONENT, scheduler=scheduler)
                affected_objects.add(obj_to_add)

            while len(affected_objects) > object_cap and affected_objects:
                obj_to_remove = affected_objects.pop()
                self._cleanup_object(obj_to_remove)

    def _start_situations(self, scheduler, alarm_data, obj):
        self._setup_affected_objects()
        if not scheduler.extra_data.has_component(SITUATION_SCHEDULER_COMPONENT):
            return
        elif hasattr(alarm_data.entry, 'weighted_situations'):
            resolver = SingleObjectResolver(obj)
            situation, params = WeightedSituationsWeeklySchedule.get_situation_and_params((alarm_data.entry), resolver=resolver)
        else:
            situation, params = alarm_data.entry.situation, {}
        if situation is None:
            return
        (obj.create_situation)(situation, **params)

    def _get_current_affected_object_cap(self, schedule):
        current_time = services.time_service().sim_now
        best_time, alarm_data = schedule().time_until_next_scheduled_event(current_time, schedule_immediate=True)
        if best_time is None:
            current_affected_object_cap = 0
        else:
            if best_time > TimeSpan.ZERO:
                current_affected_object_cap = 1
            else:
                current_affected_object_cap = alarm_data[0].entry.affected_object_cap
        return current_affected_object_cap