# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\statistic_static_modifier.py
# Compiled at: 2019-02-27 16:43:46
# Size of source mod 2**32: 6137 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from sims.sim_info_lod import SimInfoLODLevel
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableRange, Tunable, TunablePackSafeReference, TunableTuple, TunableVariant
from statistics.statistic import Statistic
import enum, services, sims4.log
logger = sims4.log.Logger('statistics', default_owner='nabaker')

class StatisticStaticModifierOption(enum.Int):
    CEILING = ...
    FLOOR = ...
    DELTA = ...
    NORMALIZE = ...


class StatisticStaticModifier(HasTunableSingletonFactory, BaseGameEffectModifier):
    FACTORY_TUNABLES = {'statistic':Statistic.TunablePackSafeReference(description='\n            "The statistic we are operating on.'), 
     'modifier':TunableVariant(description='\n            How we want to modify the statistic. \n            ',
       ceiling=TunableTuple(description='\n                Cap the value at the specified number.\n                ',
       number=Tunable(description='\n                    The number to cap the value at. Can be negative.\n                    ',
       tunable_type=int,
       default=0),
       priority=TunableRange(description='\n                    The priority in which to apply the modifier.  Higher are later\n                    ',
       tunable_type=int,
       default=2,
       minimum=2),
       locked_args={'option': StatisticStaticModifierOption.CEILING}),
       floor=TunableTuple(description='\n                floor the value at the specified number.\n                ',
       number=Tunable(description='\n                    The number to floor the value at. Can be negative.\n                    ',
       tunable_type=int,
       default=0),
       priority=TunableRange(description='\n                    The priority in which to apply the modifier.  Higher are later\n                    ',
       tunable_type=int,
       default=2,
       minimum=2),
       locked_args={'option': StatisticStaticModifierOption.FLOOR}),
       delta=TunableTuple(description='\n                Modify the value by the specified number.\n                ',
       number=Tunable(description='\n                    The number to modify the value by. Can be negative.\n                    ',
       tunable_type=int,
       default=0),
       locked_args={'option':StatisticStaticModifierOption.DELTA, 
      'priority':0}),
       normalize=TunableTuple(description='\n                Normalize (i.e. move towards default) the value by the specified number.\n                ',
       number=Tunable(description='\n                    The number to modify the value by. Can be negative.\n                    ',
       tunable_type=int,
       default=0),
       locked_args={'option':StatisticStaticModifierOption.NORMALIZE, 
      'priority':1}),
       default='delta')}

    def __init__(self, statistic, modifier, **kwargs):
        super().__init__(GameEffectType.STATISTIC_STATIC_MODIFIER)
        self._statistic = statistic
        self._option = modifier.option
        self._number = modifier.number
        self.priority = modifier.priority

    def apply_modifier(self, sim_info):
        if self._statistic is None:
            return
        stat = sim_info.get_statistic((self._statistic), add=True)
        if stat is None:
            if sim_info.lod != SimInfoLODLevel.MINIMUM:
                logger.warn('Unable to add statistic: {} to sim: {} for statistic_static_modifier.  Perhaps statistic min lod value should be lower', self._statistic, sim_info)
            return
        stat.add_statistic_static_modifier(self)

    def remove_modifier(self, sim_info, handle):
        if self._statistic is None:
            return
        stat = sim_info.get_statistic(self._statistic)
        if stat is None:
            return
        stat.remove_statistic_static_modifier(self)

    def apply(self, value, default_value):
        if self._option == StatisticStaticModifierOption.NORMALIZE:
            if value > default_value:
                value -= self._number
                if value < default_value:
                    value = default_value
            else:
                value += default_value
                if value > default_value:
                    value = default_value
            return value
        if self._option == StatisticStaticModifierOption.DELTA:
            return value + self._number
        if self._option == StatisticStaticModifierOption.CEILING:
            if value > self._number:
                value = self._number
            return value
        if value < self._number:
            value = self._number
        return value