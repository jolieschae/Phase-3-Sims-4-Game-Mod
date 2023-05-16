# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\service_npcs\butler\butler_loot_ops.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 2707 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunablePackSafeReference, TunableVariant, TunableEnumEntry
import enum, services, sims4.log
logger = sims4.log.Logger('ButlerLootOps', default_owner='camilogarcia')

class ButlerSituationStates(enum.Int):
    DEFAULT = 1
    CLEANING = 2
    GARDENING = 3
    CHILDCARE = 4
    REPAIR = 5


class ButlerSituationStateChange(BaseLootOperation):
    FACTORY_TUNABLES = {'butler_situation':TunablePackSafeReference(description="\n            The Situation who's state will change.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION)), 
     'operation':TunableVariant(description='\n            Enable or disable operation for tuned tone.\n            ',
       locked_args={'enable':True, 
      'disable':False},
       default='enable'), 
     'situation_state':TunableEnumEntry(description='\n            Situation state for the butler that should be enabled or disabled\n            depending on the operation.\n            ',
       tunable_type=ButlerSituationStates,
       default=ButlerSituationStates.DEFAULT,
       invalid_enums=(
      ButlerSituationStates.DEFAULT,))}

    def __init__(self, *args, butler_situation, operation, situation_state, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._butler_situation = butler_situation
        self._operation = operation
        self._situation_state = situation_state

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        else:
            situation_manager = services.get_zone_situation_manager()
            butler_situation = situation_manager.get_situation_by_type(self._butler_situation)
            if butler_situation is None:
                logger.error('Sim {} trying to switch situation state {} while not running the butler situation', subject, self._situation_state)
                return
                if self._operation:
                    butler_situation.enable_situation_state(self._situation_state)
            else:
                butler_situation.disable_situation_state(self._situation_state)