# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\time_of_day_component.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9513 bytes
from weakref import WeakKeyDictionary
import random, time
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.utils.success_chance import SuccessChance
from objects.components import Component, types
from objects.components.state_references import TunableStateTypeReference, TunableStateValueReference
from sims4.tuning.tunable import HasTunableFactory, TunableRange, TunableTuple, TunableMapping, TunableList, TunableReference
import alarms, clock, date_and_time, elements, services, sims4.resources
logger = sims4.log.Logger('TimeOfDayComponent', default_owner='nabaker')

class TimeOfDayComponent(Component, HasTunableFactory, component_name=types.TIME_OF_DAY_COMPONENT):
    MAX_SECONDS_PER_LOOP = 0.03333333333333333
    FACTORY_TUNABLES = {'state_changes': TunableMapping(description='\n            A mapping from state to times of the day when the state should be \n            set to a tuned value.\n            ',
                        key_type=TunableStateTypeReference(description='\n                The state to be set.\n                '),
                        value_type=TunableList(description='\n                List of times to modify the state at.\n                ',
                        tunable=TunableTuple(start_time=TunableRange(description='\n                        The start time (24 hour clock time) for the Day_Time state.\n                        ',
                        tunable_type=float,
                        default=0,
                        minimum=0,
                        maximum=24),
                        value=TunableStateValueReference(description='\n                        New state value.\n                        '),
                        loot_list=TunableList(description='\n                        A list of loot operations to apply when changing state.\n                        ',
                        tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
                        class_restrictions=('LootActions', ),
                        pack_safe=True)),
                        chance=SuccessChance.TunableFactory(description='\n                        Percent chance that the state change will be considered. \n                        The chance is evaluated just before running the tests.\n                        '),
                        tests=TunableTestSet(description='\n                        Test to decide whether the state change can be applied.\n                        '))))}

    def __init__(self, owner, *, state_changes):
        super().__init__(owner)
        self.state_changes = state_changes
        self._start_times = set()

    @classmethod
    def _handle_alarm_gen(cls, alarm_time, timeline):
        time_of_day_alarms = services.time_service().time_of_day_alarms
        if alarm_time not in time_of_day_alarms:
            logger.error('Trying to handle unscheduled alarm')
            return
        _, object_dicts = time_of_day_alarms[alarm_time]
        if not object_dicts:
            del time_of_day_alarms[alarm_time]
            return
        start_time = time.clock()

        def timeslice_if_needed_gen(timeline):
            nonlocal start_time
            time_now = time.clock()
            elapsed_time = time_now - start_time
            if elapsed_time < cls.MAX_SECONDS_PER_LOOP:
                return
            sleep_element = elements.SleepElement(date_and_time.TimeSpan(0))
            yield timeline.run_child(sleep_element)
            start_time = time.clock()

        for timed_object in list(object_dicts):
            state_changes = object_dicts.get(timed_object, [])
            yield from timeslice_if_needed_gen(timeline)
            for state, change in state_changes:
                if cls._apply_state_change(timed_object, state, change) and timed_object not in object_dicts:
                    break

        now = services.time_service().sim_now + date_and_time.create_time_span(minutes=1)
        new_handle = cls.schedule_timeline(timeline, alarm_time, now)
        time_of_day_alarms[alarm_time] = (new_handle, object_dicts)
        if False:
            yield None

    @classmethod
    def _apply_state_change(cls, owner, state, change):
        resolver = SingleObjectResolver(owner)
        chance = change.chance.get_chance(resolver)
        if random.random() > chance:
            return False
        else:
            return change.tests.run_tests(resolver) or False
        owner.set_state(state, change.value)
        for loot_action in change.loot_list:
            loot_action.apply_to_resolver(resolver)

        return True

    @classmethod
    def schedule_timeline(cls, timeline, alarm_time, now):

        def alarm_callback_gen(timeline):
            yield from cls._handle_alarm_gen(alarm_time, timeline)
            if False:
                yield None

        end_time = now.time_of_next_day_time(date_and_time.create_date_and_time(hours=alarm_time))
        return timeline.schedule(elements.GeneratorElement(alarm_callback_gen), end_time)

    @classmethod
    def _add_alarm(cls, owner, start_times, cur_state, state, change):
        now = services.time_service().sim_now
        time_to_day = clock.time_until_hour_of_day(now, change.start_time)
        time_of_day_alarms = services.time_service().time_of_day_alarms
        time_of_day_tuple = time_of_day_alarms.get(change.start_time)
        if time_of_day_tuple is None:
            alarm_handle = cls.schedule_timeline(services.time_service().sim_timeline, change.start_time, now)
            time_of_day_tuple = (alarm_handle, WeakKeyDictionary())
            time_of_day_alarms[change.start_time] = time_of_day_tuple
        object_dicts = time_of_day_tuple[1]
        state_changes = object_dicts.get(owner)
        if state_changes is None:
            state_changes = []
            object_dicts[owner] = state_changes
        state_changes.append((state, change))
        start_times.add(change.start_time)
        if cur_state is None or time_to_day > cur_state[0]:
            return (
             time_to_day, change)
        return cur_state

    def _setup_state_changes(self):
        for state, changes in self.state_changes.items():
            current_state = None
            for change in changes:
                current_state = self._add_alarm(self.owner, self._start_times, current_state, state, change)

            if current_state is not None:
                self._apply_state_change(self.owner, state, current_state[1])

    def on_finalize_load(self):
        self._setup_state_changes()

    def on_add(self):
        zone = services.current_zone()
        if zone.is_zone_loading:
            return
        self._setup_state_changes()

    def on_remove(self):
        time_of_day_alarms = services.time_service().time_of_day_alarms
        for alarm_time in self._start_times:
            time_of_day_tuple = time_of_day_alarms.get(alarm_time)
            if time_of_day_tuple:
                time_of_day_tuple[1].pop(self.owner, None)
                time_of_day_tuple[1] or time_of_day_tuple[0].trigger_hard_stop()
                del time_of_day_alarms[alarm_time]

        self._start_times.clear()