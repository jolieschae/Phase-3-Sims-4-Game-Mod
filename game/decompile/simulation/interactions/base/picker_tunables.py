# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\picker_tunables.py
# Compiled at: 2013-10-24 21:28:55
# Size of source mod 2**32: 1397 bytes
from sims4.tuning.tunable import TunableMapping, TunableReference, Tunable
import services, sims4.resources

class TunableBuffWeightMultipliers(TunableMapping):

    def __init__(self, **kwargs):
        (super().__init__)(description='\n            A mapping of buffs to weight multipliers.  These multiplier will be applied \n            to the autonomy_weight whenever the Sim has that buff.\n            ', 
         key_type=TunableReference((services.get_instance_manager(sims4.resources.Types.BUFF)),
  description='\n                The buff the Sim must have to apply this multiplier.\n                '), 
         value_type=Tunable(description='\n                Float value to apply to the recipe weight.  The final recipe score \n                will be autonomy_weight times the product of all applicable buff \n                weight multipliers.\n                ',
  tunable_type=float,
  default=1.0), **kwargs)