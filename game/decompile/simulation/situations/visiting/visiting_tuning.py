# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\visiting_tuning.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 942 bytes
from sims4.tuning.tunable import TunableList, TunableReference
import services, sims4.resources

class VisitingTuning:
    ALWAYS_WELCOME_TRAITS = TunableList(description='\n        Traits that will guarantee that after the Sim is welcomed into a \n        household, it will always be automatically welcomed if he/she comes\n        back.\n        i.e. Vampires are always welcomed after being welcomed once.\n        ',
      tunable=TunableReference(description='\n            Trait reference to make the Sim always be welcomed after they \n            are welcomed once.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
      pack_safe=True))