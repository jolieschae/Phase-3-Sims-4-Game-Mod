# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\mood_effect_modifier.py
# Compiled at: 2016-07-12 20:03:07
# Size of source mod 2**32: 1760 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableMapping, AutoFactoryInit, TunableRange
from statistics.mood import Mood

class MoodEffectModifier(HasTunableSingletonFactory, AutoFactoryInit, BaseGameEffectModifier):
    FACTORY_TUNABLES = {'mood_effect_mapping': TunableMapping(key_type=Mood.TunableReference(description='\n                The mood this modifier is attached to.\n                '),
                              value_type=TunableRange(description='\n                The value multiplied on the weight of moods.\n                Defaulted to half all effects\n                ',
                              tunable_type=float,
                              default=0.5,
                              minimum=0.0))}

    def __init__(self, **kwargs):
        (super().__init__)((GameEffectType.MOOD_EFFECT_MODIFIER), **kwargs)

    def get_modifier_by_category(self, category):
        if category not in self.mood_effect_mapping:
            return 1.0
        return self.mood_effect_mapping[category]