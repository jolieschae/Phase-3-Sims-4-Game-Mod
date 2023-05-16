# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\custom_states_common_tuning.py
# Compiled at: 2021-04-12 13:10:53
# Size of source mod 2**32: 3110 bytes
import services
from event_testing.resolver import GlobalResolver
from sims4.random import weighted_random_item
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple, Tunable
from tunable_multiplier import TunableMultiplier
from tunable_time import TunableTimeOfDay

class RandomWeightedSituationStateKey(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'possible_state_keys': TunableList(description='\n            The possible situation state keys.\n            ',
                              tunable=TunableTuple(situation_key=Tunable(description='\n                    The key of the situation state.\n                    ',
                              tunable_type=str,
                              default=None),
                              weight=TunableMultiplier.TunableFactory(description='\n                    A weight with testable multipliers that is used to \n                    determine how likely this entry is to be picked when \n                    selecting randomly.\n                    ')),
                              minlength=1)}

    def __call__(self):
        resolver = GlobalResolver()
        return weighted_random_item(tuple(((possible_state.weight.get_multiplier(resolver), possible_state.situation_key) for possible_state in self.possible_state_keys)))


class TimeBasedSituationStateKey(HasTunableSingletonFactory):
    FACTORY_TUNABLES = {'situation_key_schedule': TunableList(description='\n            The schedule of situation starting keys.\n            ',
                                 tunable=TunableTuple(description='\n                A time block for a situation key.\n                ',
                                 possible_situation_keys=(RandomWeightedSituationStateKey.TunableFactory()),
                                 time=TunableTimeOfDay(description='\n                    The time of this situation key.  This time block will exist until the next time block tuned.\n                    ',
                                 default_hour=9)),
                                 minlength=1)}

    def __init__(self, situation_key_schedule):
        self._situation_key_schedule = list(situation_key_schedule)
        self._situation_key_schedule.sort(key=(lambda situation_time_block: situation_time_block.time))

    def __call__(self):
        now = services.game_clock_service().now()
        for time_block_index, next_time_block in enumerate((self._situation_key_schedule), start=(-1)):
            time_block = self._situation_key_schedule[time_block_index]
            if now.time_between_day_times(time_block.time, next_time_block.time):
                return time_block.possible_situation_keys()