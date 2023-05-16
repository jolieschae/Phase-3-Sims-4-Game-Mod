# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_skill_fixup_action.py
# Compiled at: 2019-09-16 16:25:30
# Size of source mod 2**32: 986 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import Tunable
from statistics.skill import Skill

class _SimInfoSkillFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'skill':Skill.TunableReference(description='\n            The skill which will be assigned to the sim_info.\n            '), 
     'initial_level':Tunable(description='\n            The initial level at which to assign the skill.\n            ',
       tunable_type=int,
       default=1)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def __call__(self, sim_info):
        sim_info.commodity_tracker.set_user_value(self.skill, self.initial_level)