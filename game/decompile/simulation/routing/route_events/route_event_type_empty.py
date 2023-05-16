# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_type_empty.py
# Compiled at: 2019-03-18 15:13:30
# Size of source mod 2**32: 1159 bytes
from routing.route_events.route_event_mixins import RouteEventDataBase
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableRange

class RouteEventTypeEmpty(RouteEventDataBase, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'duration_override': TunableRange(description='\n            The duration we want this route event to have. This modifies\n            how much of the route time this event will take up.\n            ',
                            tunable_type=float,
                            default=0.1,
                            minimum=0.1)}

    def prepare(self, actor):
        pass

    def execute(self, actor, **kwargs):
        pass

    def process(self, actor):
        pass