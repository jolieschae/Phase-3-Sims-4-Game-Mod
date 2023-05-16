# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\locators\locator_tuning.py
# Compiled at: 2020-04-30 15:48:17
# Size of source mod 2**32: 528 bytes
import services, sims4
from sims4.tuning.tunable import TunableReference

class LocatorTuning:
    TARGET_LOCATOR_ID_STAT = TunableReference(description='\n        The stat name used to check for a target locator id on the routing object.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))