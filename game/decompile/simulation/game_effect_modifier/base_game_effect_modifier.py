# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\base_game_effect_modifier.py
# Compiled at: 2018-11-16 20:59:40
# Size of source mod 2**32: 799 bytes


class BaseGameEffectModifier:

    def __init__(self, modifier_type):
        self.modifier_type = modifier_type

    def apply_modifier(self, sim_info):
        pass

    def remove_modifier(self, sim_info, handle):
        pass