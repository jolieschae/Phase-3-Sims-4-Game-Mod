# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\route_events\route_event_provider.py
# Compiled at: 2020-11-18 17:32:44
# Size of source mod 2**32: 8541 bytes
from element_utils import build_critical_section_with_finally
from elements import ParentElement
from event_testing.resolver import SingleObjectResolver, SingleSimResolver
from interactions import ParticipantType
from routing.route_enums import RouteEventType
from routing.route_events.route_event import RouteEvent
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableList, TunableTuple, TunableEnumEntry
import sims4.log
logger = sims4.log.Logger('RouteEventProviders', default_owner='rmccord')

class RouteEventProviderMixin:

    def on_event_executed(self, route_event, sim):
        pass

    def provide_route_events(self, route_event_context, sim, path, failed_types=None, start_time=0, end_time=None, **kwargs):
        raise NotImplementedError

    def can_provide_route_event--- This code section failed: ---

 L.  66         0  LOAD_FAST                'route_event_cls'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  JUMP_IF_FALSE_OR_POP    32  'to 32'

 L.  67         8  LOAD_FAST                'failed_types'
               10  LOAD_CONST               None
               12  COMPARE_OP               is
               14  POP_JUMP_IF_TRUE     24  'to 24'
               16  LOAD_FAST                'route_event_cls'
               18  LOAD_FAST                'failed_types'
               20  COMPARE_OP               not-in
               22  JUMP_IF_FALSE_OR_POP    32  'to 32'
             24_0  COME_FROM            14  '14'

 L.  68        24  LOAD_FAST                'route_event_cls'
               26  LOAD_METHOD              test
               28  LOAD_FAST                'sim_resolver'
               30  CALL_METHOD_1         1  '1 positional argument'
             32_0  COME_FROM            22  '22'
             32_1  COME_FROM             6  '6'
               32  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 32_1

    def is_route_event_valid(self, route_event, time, sim, path):
        raise NotImplementedError


class RouteEventProviderRequest(RouteEventProviderMixin, ParentElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'route_events':TunableTuple(description='\n            There are two kinds of route events. One is an that has a chance to\n            play every route at a low priority. One is repeating and gets\n            dispersed throughout the route at a very low priority.\n            ',
       single_events=TunableList(description='\n                Single Route Events to possibly play once on a route while the\n                Sim has this request active.\n                ',
       tunable=RouteEvent.TunableReference(description='\n                    A single route event that may happen once when a Sim is\n                    routing with this request on them.\n                    ',
       pack_safe=True)),
       repeating_events=TunableList(description='\n                Repeating Route Events which can occur multiple times over the\n                course of a route while this request is active.\n                ',
       tunable=RouteEvent.TunableReference(description="\n                    A repeating route event which will be dispersed throughout\n                    a Sim's route while they have this request on them.\n                    ",
       pack_safe=True))), 
     'participant':TunableEnumEntry(description='\n            The participant to which the Route Events will be attached.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor)}

    def __init__(self, owner, *args, sequence=(), **kwargs):
        (super().__init__)(*args, **kwargs)
        if hasattr(owner, 'is_super'):
            self._target = next(iter(owner.get_participantsself.participant))
        else:
            self._target = owner
        self._sequence = sequence

    def start(self, *args, **kwargs):
        if self._target.routing_component is None:
            logger.error('Route Event Provider target {} has no routing component.', self._target)
            return
        self._target.routing_component.add_route_event_providerself

    def stop(self, *args, **kwargs):
        if self._target.routing_component is None:
            logger.error('Route Event Provider target {} has no routing component.', self._target)
            return
        self._target.routing_component.remove_route_event_providerself

    def provide_route_events(self, route_event_context, sim, path, failed_types=None, start_time=0, end_time=None, **kwargs):
        if self._target.is_sim:
            resolver = SingleSimResolver(self._target.sim_info)
        else:
            resolver = SingleObjectResolver(self._target)
        for route_event_cls in self.route_events.single_events:
            if self.can_provide_route_event(route_event_cls, failed_types, resolver):
                route_event_context.route_event_already_scheduledroute_event_cls or route_event_context.route_event_already_fully_considered(route_event_cls, self) or route_event_context.add_route_event(RouteEventType.LOW_SINGLE, route_event_cls(provider=self, provider_required=True))

        for route_event_cls in self.route_events.repeating_events:
            if self.can_provide_route_event(route_event_cls, failed_types, resolver):
                route_event_context.route_event_already_fully_considered(route_event_cls, self) or route_event_context.add_route_event(RouteEventType.LOW_REPEAT, route_event_cls(provider=self, provider_required=True))

    def is_route_event_valid(self, route_event, time, sim, path):
        return True

    def _run(self, timeline):
        sequence = build_critical_section_with_finally(self.start, self._sequence, self.stop)
        return timeline.run_childsequence