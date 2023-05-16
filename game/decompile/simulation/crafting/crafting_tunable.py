# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\crafting_tunable.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 8505 bytes
from objects.components.inventory_enums import InventoryType
from objects.components.state import CommodityBasedObjectState, ObjectState, CommodityBasedObjectStateValue, ObjectStateValue
from objects.components.state_references import TunableStateValueReference
from services import get_instance_manager
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, Tunable, TunableRange, TunableEnumEntry
from sims4.utils import classproperty
from statistics.static_commodity import StaticCommodity
from statistics.statistic import Statistic
import sims4

class CraftingTuning:
    STATIC_CRAFTING_COMMODITY = StaticCommodity.TunableReference(description='\n        The static commodity all interactions used in recipes must be tagged\n        with.\n        ')
    TURN_STATISTIC = Statistic.TunableReference(description='\n        The statistic used to track turns during a crafting process. Value will\n        be reset to 0 at the start of each phase.\n        ')
    MAX_TURNS_FOR_AUTOSMOKE = TunableRange(description='\n        The maximum number of turns a phase should take during the autosmoke.\n        ',
      tunable_type=int,
      default=2,
      minimum=2)
    PROGRESS_STATISTIC = TunableReference(description='\n        The statistic used to track crafting progress during a crafting process.\n        Recipes using this are complete when the stat maxes out.\n        ',
      manager=(get_instance_manager(sims4.resources.Types.STATISTIC)))
    PROGRESS_VIRTUAL_TURNS = Tunable(description='\n        When a phase is progress-based, this controlls how many turns it appears\n        to have in the crafting quality UI.\n        ',
      tunable_type=int,
      default=10)
    SERVINGS_STATISTIC = Statistic.TunableReference(description='\n        The statistic to link to the servings.\n        ')
    STATE_EFFECT_MAP = TunableMapping(description='\n        A mapping of states to effects that take place when advancing\n        phases.\n        ',
      key_type=TunableStateValueReference(description='\n            A state value. The Object of the interaction will be considered\n            first. If the state is not present, the ActorSurface will be\n            considered.\n            '),
      value_type=TunableReference(description='\n            Actions to apply if the specified state is enabled when advancing\n            phases.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.ACTION))))
    INSUFFICIENT_FUNDS_TOOLTIP = TunableLocalizedStringFactory(description='\n        Grayed-out tooltip message when sim lacks sufficient funds.\n        ',
      default=1906305656)
    INSUFFICIENT_BUCKS_TOOLTIP = TunableLocalizedStringFactory(description='\n        Grayed-out tooltip message when sim lacks sufficient bucks.\n        ',
      default=1906305656)
    QUALITY_STATE = CommodityBasedObjectState.TunableReference(description='\n        The statistic used to track quality during a crafting process.\n        ')
    CONSUMABLE_STATE = CommodityBasedObjectState.TunableReference(description='\n        The statistic used to track consumed state during a crafting process.\n        ')
    FRESHNESS_STATE = CommodityBasedObjectState.TunableReference(description='\n         The object state used to track freshness.\n         ')
    SPOILED_STATE_VALUE = TunableStateValueReference(description='\n         The object state used to track freshness.\n         ',
      class_restrictions=CommodityBasedObjectStateValue)
    SPOILED_STRING = TunableLocalizedString(description='\n         The spoiled object string.\n         ')
    CONSUMABLE_EMPTY_STATE_VALUE = TunableStateValueReference(description="\n         The object state value for empty consumable. Empty consumable doesn't have hovertip.\n         ",
      class_restrictions=CommodityBasedObjectStateValue)
    LOCK_FRESHNESS_STATE_VALUE = TunableStateValueReference(description='\n         Does this object have a lock freshness state value\n         ',
      class_restrictions=ObjectStateValue)
    MASTERWORK_STATE = ObjectState.TunableReference(description='\n        The object state used to track if this is a masterwork or not.\n        ')
    MASTERWORK_STATE_VALUE = TunableStateValueReference(description='\n        The masterwork state value, as opposed to the normal work state value.\n        ')
    QUALITY_STATE_VALUE_MAP = TunableMapping(description='\n        The quality mapping to the UI numbers.\n        ',
      key_type=TunableStateValueReference(description='\n            The quality state values.\n            '),
      value_type=TunableTuple(state_star_number=Tunable(description='\n                The number of stars shows in UI.\n                ',
      tunable_type=int,
      default=0),
      state_string=TunableLocalizedStringFactory(description='\n                The quality state string in Crafting Inspector.\n                ')))
    CONSUMABLE_STATE_VALUE_MAP = TunableMapping(description='\n        The consumable state mapping to the UI numbers.\n        ',
      key_type=TunableStateValueReference(description='\n            The consumable state values.\n            '),
      value_type=TunableLocalizedString(description='\n            The consumable state string in consumable tooltip UI.\n            '))
    DEFAULT_RESUME_AFFORDANCE = TunableReference(description='\n        The affordance that is run when choosing to resume a crafting process.\n        ',
      manager=(get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions=('CraftingResumeInteraction', ))
    SHARED_FRIDGE_INVENTORY_TYPE = TunableEnumEntry(description='\n        Type of inventory used by the fridge objects.\n        ',
      tunable_type=InventoryType,
      default=(InventoryType.UNDEFINED))
    FOOD_POISONING_STATE = ObjectState.TunableReference(description='\n        The object state used to track food poisoning.\n        ',
      pack_safe=True)
    FOOD_POISONING_STATE_VALUE = TunableStateValueReference(description='\n        The object state used when food is contaminated with food poisoning.\n        ',
      class_restrictions=ObjectStateValue,
      pack_safe=True)
    COPY_STATE_VALUE = TunableStateValueReference(description='\n        The object state value used to mark something as a copy and not an \n        original.\n        ',
      class_restrictions=ObjectStateValue,
      pack_safe=True)
    COPY_VALUE_MULTIPLIER = Tunable(description='\n        A modifier value to apply when determining the craftables value if the\n        craftable has the COPY_STATE_VALUE set.\n        ',
      tunable_type=float,
      default=1.0)

    @classproperty
    def QUALITY_STATISTIC(cls):
        return cls.QUALITY_STATE.linked_stat

    @classproperty
    def CONSUME_STATISTIC(cls):
        return cls.CONSUMABLE_STATE.linked_stat

    @classmethod
    def get_quality_state_value(cls, stat_type, quality_stat_value):
        for quality_state, value in cls.QUALITY_STATE_VALUE_MAP.items():
            if quality_state.state is not None and quality_state.state.linked_stat is stat_type and quality_stat_value >= quality_state.range.lower_bound and quality_stat_value < quality_state.range.upper_bound:
                return value