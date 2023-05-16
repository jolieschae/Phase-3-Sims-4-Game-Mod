# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_fixup.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 5496 bytes
from sims.fixup.sim_info_appearance_fixup_action import _SimInfoAppearanceFixupAction
from sims.fixup.sim_info_career_fixup_action import _SimInfoCareerFixupAction
from sims.fixup.sim_info_developmental_milestone_ops_fixup_action import _SimInfoDevelopmentalMilestoneOpsFixupAction
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims.fixup.sim_info_outfit_fixup_actions import _SimInfoOutfitTransferFixupAction, _SimInfoRandomizeOutfitFixupAction
from sims.fixup.sim_info_perk_fixup_action import _SimInfoPerkFixupAction
from sims.fixup.sim_info_skill_fixup_action import _SimInfoSkillFixupAction
from sims.fixup.sim_info_unlock_fixup_action import _SimInfoUnlockFixupAction
from sims.fixup.sim_info_favorites_fixup_action import _SimInfoFavoritesFixupAction
from sims.fixup.sim_info_statistic_ops_fixup_action import _SimInfoStatisticOpsFixupAction
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableList, TunableEnumEntry, TunableVariant
from sims4.tuning.tunable_base import GroupNames
import services

class SimInfoFixup(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SIM_INFO_FIXUP)):
    INSTANCE_TUNABLES = {'sim_info_fixup_actions':TunableList(description='\n            A list of fixup actions which will be performed on a sim_info with\n            this sim_info_fixup in fixup tracker\n            ',
       tunable=TunableVariant(career_fixup_action=_SimInfoCareerFixupAction.TunableFactory(description='\n                    A fix up action to set a career with a specific level.\n                    '),
       skill_fixup_action=_SimInfoSkillFixupAction.TunableFactory(description='\n                    A fix up action to set a skill with a specific level.\n                    '),
       unlock_fixup_action=_SimInfoUnlockFixupAction.TunableFactory(description='\n                    A fix up action to unlock certain things for a Sim\n                    '),
       perk_fixup_action=_SimInfoPerkFixupAction.TunableFactory(description='\n                    A fix up action to grant perks to a Sim. It checks perk required\n                    unlock tuning and unlocks prerequisite perks first.\n                    '),
       outfit_transfer_fixup_action=_SimInfoOutfitTransferFixupAction.TunableFactory(description='\n                    SimInfoFixupAction to move outfits between categories for a Sim.\n                    '),
       outfit_randomization_fixup_action=_SimInfoRandomizeOutfitFixupAction.TunableFactory(description='\n                    SimInfoFixupAction to randomize an outfit category for a Sim.\n                    '),
       appearance_fixup_action=_SimInfoAppearanceFixupAction.TunableFactory(description='\n                    SimInfoAppearanceFixupAction to modify the appearance of a Sim.\n                    '),
       favorites_fixup_action=_SimInfoFavoritesFixupAction.TunableFactory(description='\n                    SimFavoritesFixupAction to modify the favorites of a Sim.\n                    '),
       statistic_ops_fixup_action=_SimInfoStatisticOpsFixupAction.TunableFactory(description='\n                    SimInfoStatisticsFixupAction to run statistics ops on a Sim.\n                    '),
       developmental_milestone_ops_fixup_action=_SimInfoDevelopmentalMilestoneOpsFixupAction.TunableFactory(description='\n                    SimInfoDevelopmentalMilestoneFixupAction to run DevelopmentalMilestone State Change ops on a Sim.\n                    '),
       default='career_fixup_action'),
       tuning_group=GroupNames.SPECIAL_CASES), 
     'sim_info_fixup_actions_timing':TunableEnumEntry(description='\n            We use this tuning to define when to apply sim info fixups.\n            Please be sure you consult a GPE whenever you are creating fixup tuning.\n            ',
       tunable_type=SimInfoFixupActionTiming,
       default=SimInfoFixupActionTiming.ON_FIRST_SIMINFO_LOAD,
       tuning_group=GroupNames.SPECIAL_CASES)}

    @classmethod
    def should_apply_fixup_actions(cls, fixup_source):
        if cls.sim_info_fixup_actions_timing == fixup_source:
            return True
        return False

    @classmethod
    def apply_fixup_actions(cls, sim_info):
        for fixup_action in cls.sim_info_fixup_actions:
            fixup_action.fixup_guid = cls.guid
            fixup_action(sim_info)