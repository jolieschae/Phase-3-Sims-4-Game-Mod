# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\mother_plant_battle_ops.py
# Compiled at: 2018-11-19 23:12:57
# Size of source mod 2**32: 2310 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableReference, TunableEnumEntry
import enum, services, sims4.log
logger = sims4.log.Logger('MotherPlantBattle', default_owner='jjacobson')

class MotherplantBattleStates(enum.Int):
    BASIC = 1
    ATTACK = 2
    INSPIRE = 3
    RALLY = 4
    WARBLING_WARCRY = 5


class MotherplantBattleSituationStateChange(BaseLootOperation):
    FACTORY_TUNABLES = {'motherplant_situation':TunableReference(description='\n            The motherplant battle situation that we will be changing the\n            state of.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'situation_state':TunableEnumEntry(description='\n            Situation state for the motherplant that we will set.\n            ',
       tunable_type=MotherplantBattleStates,
       default=MotherplantBattleStates.BASIC,
       invalid_enums=(
      MotherplantBattleStates.BASIC,))}

    def __init__(self, *args, motherplant_situation, situation_state, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._motherplant_situation = motherplant_situation
        self._situation_state = situation_state

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        situation_manager = services.get_zone_situation_manager()
        motherplant_situation = situation_manager.get_situation_by_type(self._motherplant_situation)
        if motherplant_situation is None:
            logger.error('Sim {} trying to switch situation state {} while not running the motherplant battle situation', subject, self._situation_state)
            return
        motherplant_situation.set_motherplant_situation_state(self._situation_state)