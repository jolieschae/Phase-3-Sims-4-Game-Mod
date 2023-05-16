# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\aging\aging_tuning.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 2238 bytes
from sims.aging.aging_data import AgingData
from sims.sim_info_types import Species
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, Tunable, TunableSimMinute
from sims4.tuning.tunable_base import EnumBinaryExportType
from sims.aging.aging_enums import AgeSpeeds

class AgingTuning:
    AGING_DATA = TunableMapping(description='\n        On a per-species level, define all age-related data.\n        ',
      key_type=TunableEnumEntry(description='\n            The species this aging data applies to.\n            ',
      tunable_type=Species,
      default=(Species.HUMAN),
      invalid_enums=(
     Species.INVALID,),
      binary_type=(EnumBinaryExportType.EnumUint32)),
      value_type=(AgingData.TunableFactory()),
      tuple_name='AgingDataMapping')
    AGING_SAVE_LOCK_TOOLTIP = TunableLocalizedStringFactory(description='\n        The tooltip to show in situations where save-lock during Age Up is\n        necessary, i.e. when babies or non-NPC Sims age up.\n        \n        This tooltip is provided one token: the Sim that is aging up.\n        ')
    AGE_SPEED_SETTING = TunableEnumEntry(description='\n        The speed at which all Sims (human, cat, dog, fox) age. Specific values tuned on aging_transition.\n        ',
      tunable_type=AgeSpeeds,
      default=(AgeSpeeds.NORMAL))
    AGE_PROGRESS_UPDATE_TIME = Tunable(description='\n        The update rate, in Sim Days, of age progression in the UI.\n        ',
      tunable_type=float,
      default=0.2)
    AGE_SUPPRESSION_ALARM_TIME = TunableSimMinute(description='\n        Amount of time in sim seconds to suppress aging.\n        ',
      default=5,
      minimum=1)

    @classmethod
    def get_aging_data(cls, species):
        return cls.AGING_DATA[species]

    @classmethod
    def get_age_speed(cls):
        return cls.AGE_SPEED_SETTING