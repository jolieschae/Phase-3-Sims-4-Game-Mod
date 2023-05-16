# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\portal_cost.py
# Compiled at: 2017-10-11 20:00:35
# Size of source mod 2**32: 1719 bytes
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableVariant

class PortalCostTraversalLength(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'multiplier': TunableRange(tunable_type=float,
                     default=1,
                     minimum=0)}

    def __call__(self, start, end):
        if self.multiplier == 1:
            return -1
        cost = (start.position - end.position).magnitude() * self.multiplier
        return cost


class PortalCostFixed(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'cost': TunableRange(tunable_type=float,
               default=1,
               minimum=0,
               maximum=9999)}

    def __call__(self, *_, **__):
        return self.cost


class TunablePortalCostVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        return (super().__init__)(args, traversal_length=PortalCostTraversalLength.TunableFactory(), 
         fixed_cost=PortalCostFixed.TunableFactory(), 
         default='traversal_length', **kwargs)