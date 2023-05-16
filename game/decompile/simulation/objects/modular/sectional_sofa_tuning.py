# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\modular\sectional_sofa_tuning.py
# Compiled at: 2020-12-17 19:23:25
# Size of source mod 2**32: 488 bytes
import services
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference

class SectionalSofaTuning:
    SECTIONAL_SOFA_OBJECT_DEF = TunableReference(description='\n        Catalog definition for the sectional sofa object.\n        ',
      manager=(services.get_instance_manager(Types.OBJECT)))