# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sickness_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 1678 bytes
from interactions.utils.loot import LootActions
from sims4.tuning.tunable import TunableList, TunableReference
import services, sims4.resources

class SicknessTuning:
    SICKNESS_BUFFS_PLAYER_FACED = TunableList(description="\n        List of buffs that define if a sim is sick from what the player can \n        see.  The way sickness work, a sim might be sick but it may not be \n        visible to the player, so on this list we should only tune the buff's\n        that would make the sim sick on the players perspective.\n        i.e. buffs that would make a child sim take a day of school.\n        ",
      tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
      pack_safe=True))
    LOOT_ACTIONS_ON_CHILD_CAREER_AUTO_SICK = TunableList(description='\n        Loot actions to test and apply on the event its time to go to work \n        and the child sim is sick.\n        i.e. notification...  \n        ',
      tunable=LootActions.TunableReference(pack_safe=True))

    @classmethod
    def is_child_sim_sick(cls, sim_info):
        if not sim_info.is_child:
            return False
        return any((sim_info.has_buff(buff_type) for buff_type in SicknessTuning.SICKNESS_BUFFS_PLAYER_FACED))