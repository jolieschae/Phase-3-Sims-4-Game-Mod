# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_cycle_tuning.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 1758 bytes
import services, sims4.resources
from lunar_cycle.lunar_cycle_enums import LunarPhaseType
from sims4.tuning.tunable import TunableEnumEntry, TunableRange, TunableMapping, TunableReference

class LunarCycleTuning:
    INITIAL_LUNAR_PHASE = TunableEnumEntry(description='\n        The lunar phase that the player begins in upon first activating the feature from new game or \n        game content installation.\n        ',
      tunable_type=LunarPhaseType,
      default=(LunarPhaseType.NEW_MOON))
    PHASE_CHANGE_TIME_OF_DAY = TunableRange(description='\n        Hour of the day during which the phase change occurs, at this time all lunar effects for the next 24 hours\n        will be scheduled; any other changes such as objects needing to switch states during a phase change will also \n        occur at this time.\n        ',
      tunable_type=int,
      default=7,
      minimum=0,
      maximum=23)
    LUNAR_PHASE_MAP = TunableMapping(description='\n        A mapping of enum to the content instance of a lunar phase.\n        ',
      key_type=TunableEnumEntry(description='\n            The lunar phase.\n            ',
      default=(LunarPhaseType.NEW_MOON),
      tunable_type=LunarPhaseType),
      value_type=TunableReference(description='\n            Content of this lunar phase as specified by the given lunar phase instance tuning.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.LUNAR_CYCLE)),
      class_restrictions=('LunarPhase', )))