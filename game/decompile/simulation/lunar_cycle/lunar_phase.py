# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\lunar_cycle\lunar_phase.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 4201 bytes
import services, sims4.resources
from date_and_time import create_time_span
from lunar_cycle.lunar_cycle_enums import LunarCycleLengthOption
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableRange, TunableList, TunableReference

class TunablePhaseEffectsByHour(TunableMapping):

    def __init__(self, **kwargs):
        (super().__init__)(key_type=TunableRange(description='\n                Hour offset into the current phase.\n                ',
  tunable_type=int,
  minimum=0,
  maximum=23,
  default=0), 
         value_type=TunableList(description='\n                Effects to apply at the given hour offset.\n                ',
  tunable=TunableReference(description='\n                    Lunar Effect\n                    ',
  manager=(services.get_instance_manager(sims4.resources.Types.LUNAR_CYCLE)),
  class_restrictions=('LunarPhaseEffect', ),
  pack_safe=True)), **kwargs)

    @property
    def export_class(self):
        return 'TunableMapping'


class LunarPhase(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.LUNAR_CYCLE)):
    base_game_only = True
    INSTANCE_TUNABLES = {'length_option_duration_map':TunableMapping(description='\n            A mapping of how long this phase is when a specific length option is set.\n            ',
       key_type=TunableEnumEntry(description='\n                The length option.\n                ',
       tunable_type=LunarCycleLengthOption,
       default=(LunarCycleLengthOption.FULL_LENGTH)),
       value_type=TunableRange(description='\n                The length of this phase (in Sim days) for the given option.\n                ',
       tunable_type=int,
       minimum=0,
       default=1),
       set_default_as_first_entry=True), 
     'effects_by_hour_offset':TunablePhaseEffectsByHour(description="\n            A mapping of hour into the current phase to effects that will be applied at that hour of the phase.\n            \n            This is relative to the lunar cycle 'Phase Change Time of Day' tuning.\n            "), 
     'pre_phase_effects_by_hour_offset':TunablePhaseEffectsByHour(description="\n            A mapping of hour into the current phase to effects that will be applied at that hour of the phase.\n            \n            This is relative to the lunar cycle 'Phase Change Time of Day' tuning.\n            \n            This list of effects affect the phase IMMEDIATELY PRECEDING this tuned phase, if this content \n            is not the active phase yet but will be within the next 24 hours.\n            \n            e.g. these effects are tuned on FULL_MOON, they apply if today is WAXING_GIBBOUS, which is the phase \n            preceding the FULL_MOON phase.  This can be used for effects such as popping a TNS noting there is \n            an upcoming full moon coming tomorrow night.  \n            ")}

    @classmethod
    def get_phase_length(cls, cycle_length_option: LunarCycleLengthOption):
        return create_time_span(days=(cls.length_option_duration_map[cycle_length_option]))