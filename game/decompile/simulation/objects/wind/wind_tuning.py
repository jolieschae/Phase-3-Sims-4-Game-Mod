# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\wind\wind_tuning.py
# Compiled at: 2020-03-19 14:54:23
# Size of source mod 2**32: 1260 bytes
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, Tunable, TunableTuple, TunableVariant

class WindSpeedEffect(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'wind_speed': TunableTuple(spin_speed=TunableVariant(description='\n                The spin speed level to set for the sim.\n                The locked float are fixed enums on the client.\n                ',
                     locked_args={'OFF':0.0, 
                    'NORMAL':3.0, 
                    'FAST':8.0},
                     default='OFF'),
                     transition_speed=Tunable(description='\n                Set the transition speed of the object.\n                The transition speed defines the speed of the\n                transition between spin speeds.\n                ',
                     tunable_type=float,
                     default=1.0))}