# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\compatibility_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 5054 bytes
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableInterval, TunableRange, TunableTuple, TunableResourceKey, TunableReference, TunableList
import enum, services, sims4

class CompatibilityLevel(enum.Int):
    AMAZING = 0
    GOOD = 1
    NEUTRAL = 2
    BAD = 3
    AWFUL = 4


class CompatibilityTuning:
    COMPATIBILITY_LEVEL_THRESHOLDS = TunableMapping(description='\n        A mapping of Compatibility levels to the Compatibility score interval.\n        ',
      key_type=TunableEnumEntry(description='\n            The CompatibilityLevel enum.\n            ',
      tunable_type=CompatibilityLevel,
      default=(CompatibilityLevel.NEUTRAL)),
      value_type=TunableInterval(description='\n            The score interval that this level corresponds to.\n            ',
      tunable_type=int,
      default_lower=0,
      default_upper=1))
    COMPATIBILITY_SCORE_RANGE = TunableInterval(description='\n        The acceptable max/min bounds for a Compatibility score.\n        ',
      tunable_type=int,
      default_lower=(-100),
      default_upper=100)
    COMPATIBILITY_SCORE_DEFAULT = TunableRange(description='\n        The default score that all Compatibility scores start at.\n        ',
      tunable_type=int,
      default=0)
    COMPATIBILITY_LEVEL_ICONS_MAP = TunableMapping(description='\n        A mapping of Compatibility levels to the icons used in the UI.\n        ',
      key_type=TunableEnumEntry(description='\n            The CompatibilityLevel enum.\n            ',
      tunable_type=CompatibilityLevel,
      default=(CompatibilityLevel.NEUTRAL)),
      value_type=TunableTuple(description='\n            A tuple of the icons and text that represent this CompatibilityLevel in the UI.\n            ',
      icon=TunableResourceKey(description='\n                The larger of the two icons for this CompatibilityLevel.  This is used\n                for the Relationship tooltip and Sim Profile panel.\n                ',
      default=None,
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      allow_none=True,
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      small_icon=TunableResourceKey(description='\n                The smaller of the two icons for this CompatibilityLevel.  This is used \n                for the Sim portraits in the Relationship panel and Sim Picker.\n                ',
      default=None,
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      allow_none=True,
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      level_name=TunableLocalizedString(description='\n                Name of this Compatibility level.\n                ',
      allow_none=True),
      descriptive_text=TunableLocalizedString(description='\n                Descriptive text for this Compatibility level, used for various tooltips.\n                ',
      allow_none=True)))
    COMPATIBILITY_LEVEL_LOOT_MAP = TunableMapping(description='\n        A mapping of Compatibility levels to loot that will be applied whenever there \n        is a level change.\n        ',
      key_type=TunableEnumEntry(description='\n            The CompatibilityLevel enum.\n            ',
      tunable_type=CompatibilityLevel,
      default=(CompatibilityLevel.NEUTRAL)),
      value_type=TunableReference(description='\n            The loot to applied to the Sim upon CompatibilityLevel update.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ),
      pack_safe=True))
    NPC_PREFERENCE_LOOT = TunableList(description="\n        Loots to apply to NPCs when setting up their Preferences.  This allows Preference  \n        traits to be assigned randomly, but (ideally) weighted against the Sim's existing\n        traits.\n        ",
      tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', 'RandomWeightedLoot'),
      pack_safe=True))
    NPC_PREFERENCE_COUNT_MAX = TunableRange(description='\n        The max number of Preference traits an NPC may be assigned.\n        ',
      tunable_type=int,
      default=1,
      minimum=0)