# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\continuous_statistic_modifier.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 4844 bytes
from _weakrefset import WeakSet
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from sims4.log import StackVar
from sims4.tuning.tunable import HasTunableSingletonFactory, Tunable, TunablePackSafeReference
from statistics.skill import Skill
import services, sims4.log, sims4.resources
logger = sims4.log.LoggerClass('ContinuousStatisticModifier')

class ContinuousStatisticModifier(HasTunableSingletonFactory, BaseGameEffectModifier):

    @staticmethod
    def _verify_tunable_callback(cls, tunable_name, source, value):
        if value.modifier_value == 0:
            logger.error('Trying to tune a Continuous Statistic Modifier to have a value of 0 which will do nothing on: {}.', StackVar(('cls', )))

    FACTORY_TUNABLES = {'description':"\n        The modifier to add to the current statistic modifier of this continuous statistic,\n        resulting in it's increase or decrease over time. Adding this modifier to something by\n        default doesn't change, i.e. a skill, will start that skill to be added to over time.\n        \n        Note:  if statistic is not add_if_not_in_tracker and statistic isn't already there, modifier will not be added\n        even if statistic is added later until/unless this modifier is somehow reapplied.\n        ", 
     'statistic':TunablePackSafeReference(description='\n        "The statistic we are operating on.',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'modifier_value':Tunable(description='\n        The value to add to the modifier. Can be negative.',
       tunable_type=float,
       default=0), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, statistic, modifier_value, **kwargs):
        super().__init__(GameEffectType.CONTINUOUS_STATISTIC_MODIFIER)
        self.statistic = statistic
        self.modifier_value = modifier_value
        self._sim_infos_modified = None

    def apply_modifier(self, sim_info):
        if self.statistic is None:
            return
        stat = sim_info.get_statistic((self.statistic), add=(self.statistic.add_if_not_in_tracker))
        if stat is None:
            return
        if self._sim_infos_modified is None:
            self._sim_infos_modified = WeakSet()
        if sim_info in self._sim_infos_modified:
            logger.error('Sim info {} modified multiple times by same Continuous Statistic {} Modifier', sim_info, self.statistic)
            return
        stat.add_statistic_modifier(self.modifier_value)
        self._sim_infos_modified.add(sim_info)
        if isinstance(stat, Skill):
            sim_info.current_skill_guid = stat.guid64

    def remove_modifier(self, sim_info, handle):
        if self.statistic is None:
            return
            if self._sim_infos_modified is None or sim_info not in self._sim_infos_modified:
                return
            self._sim_infos_modified.remove(sim_info)
            stat = sim_info.get_statistic((self.statistic), add=(self.statistic.add_if_not_in_tracker))
            if stat is None:
                return
        else:
            stat.remove_statistic_modifier(self.modifier_value)
            if isinstance(stat, Skill):
                if stat._statistic_modifier <= 0 and sim_info.current_skill_guid == stat.guid64:
                    sim_info.current_skill_guid = 0