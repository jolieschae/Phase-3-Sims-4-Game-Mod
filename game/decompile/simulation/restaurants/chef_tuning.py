# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\restaurants\chef_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 3505 bytes
from interactions.utils.loot import LootActions
from sims4.tuning.tunable import TunablePackSafeReference, Tunable, TunableReference
import services, sims4.resources

class ChefTuning:
    CHEF_STATION_POT_OBJECT = TunablePackSafeReference(description="\n        The pot object to create at the chef's station.\n        ",
      manager=(services.definition_manager()))
    CHEF_STATION_PAN_OBJECT = TunablePackSafeReference(description="\n        The pan object to create at the chef's station.\n        ",
      manager=(services.definition_manager()))
    CHEF_STATION_CUTTING_BOARD_OBJECT = TunablePackSafeReference(description="\n        The cutting board object to create at the chef's station.\n        ",
      manager=(services.definition_manager()))
    CHEF_STATION_PAN_SLOT = Tunable(description='\n        The name of the slot in which the pan object should be placed.\n        ',
      tunable_type=str,
      default='_ctnm_SimInteraction_1')
    CHEF_STATION_POT_SLOT = Tunable(description='\n        The name of the slot in which the pot object should be placed.\n        ',
      tunable_type=str,
      default='_ctnm_SimInteraction_2')
    CHEF_STATION_CUTTING_BOARD_SLOT = Tunable(description='\n        The name of the slot in which the cutting board object should be placed.\n        ',
      tunable_type=str,
      default='_ctnm_SimInteraction_4')
    CHEF_STATION_SERVE_SLOT_TYPE = TunableReference(description='\n        The slot type of the serve slots on the chef station.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE)))
    CHEF_STATION_SERVING_PLATTER_OBJECT = TunablePackSafeReference(description="\n        The serving platter object the chef will create and place when they're\n        done cooking an order.\n        ",
      manager=(services.definition_manager()))
    CHEF_HAS_ORDER_BUFF = TunablePackSafeReference(description='\n        The buff a chef should get when they have an order. This should drive\n        them to do the active cooking animations.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.BUFF)))
    CHEF_COMPLIMENT_LOOT = LootActions.TunablePackSafeReference(description="\n        The loot action to trigger when a customer compliments a chef. This\n        won't happen until the waitstaff deliver the compliment.\n        \n        The customer Sim will be the Actor and the Chef will be TargetSim.\n        ")
    CHEF_INSULT_LOOT = LootActions.TunablePackSafeReference(description="\n        The loot action to trigger when a customer insults a chef. This won't\n        happen until the waitstaff deliver the insult.\n        \n        The customer Sim will be the Actor and the Chef will be TargetSim.\n        ")
    PICK_UP_ORDER_INTERACTION = TunablePackSafeReference(description='\n        The interaction the sim will run when they pick their order up from the\n        Chef Station. This is only used when a Sim places an order directly at\n        the chef station.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))