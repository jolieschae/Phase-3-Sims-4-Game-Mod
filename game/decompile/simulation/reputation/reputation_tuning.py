# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\reputation\reputation_tuning.py
# Compiled at: 2018-07-17 13:54:43
# Size of source mod 2**32: 901 bytes
from sims4.tuning.tunable import TunablePackSafeReference
from sims4.tuning.tunable_base import ExportModes
import services, sims4.resources

class ReputationTunables:
    REPUTATION_RANKED_STATISTIC = TunablePackSafeReference(description='\n        The ranked statistic that is to be used for tracking reputation progress.\n        \n        This should not need to be tuned at all. If you think you need to tune\n        this please speak with a GPE before doing so.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('RankedStatistic', ),
      export_modes=(
     ExportModes.ClientBinary,))