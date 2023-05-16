# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_tuning.py
# Compiled at: 2018-06-05 20:16:32
# Size of source mod 2**32: 1118 bytes
from sims4.tuning.tunable import TunableReference, TunableRange
import services, sims4.resources

class PostureTuning:
    SIM_CARRIED_POSTURE = TunableReference(description='\n        The default posture representing a Sim being carried by another Sim.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)))
    CONSTRAINT_HEIGHT_TOLERANCE = TunableRange(description='\n        Maximum height tolerance the posture graph will allow for single point \n        constraints from the position of the target object vs the position of \n        the constraint goal.\n        If the height is ever higher than this, a route fail will be generated.\n        This value if modified should be verified with the Animation team since\n        high values will generate pops on the animation.\n        Height values will be in meters.\n        ',
      tunable_type=float,
      default=0.1,
      minimum=0)