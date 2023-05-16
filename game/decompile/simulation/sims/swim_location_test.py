# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\swim_location_test.py
# Compiled at: 2020-11-12 10:43:21
# Size of source mod 2**32: 4186 bytes
from event_testing import test_base
from event_testing.results import TestResult
from caches import cached_test
from interactions import ParticipantTypeSingle
from routing import SurfaceType
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableVariant, Tunable

class _SwimInPoolTest:

    def evaluate(self, sim, in_tooltip, invert):
        if sim.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
            if sim.in_pool:
                if invert:
                    return TestResult(False, 'Test inverted: {} is in a pool.', sim, tooltip=in_tooltip)
                return TestResult.TRUE
        if invert:
            return TestResult.TRUE
        return TestResult(False, '{} is not in a pool.', sim, tooltip=in_tooltip)


class _SwimInOceanTest:

    def evaluate(self, sim, in_tooltip, invert):
        if sim.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
            if not sim.in_pool:
                if invert:
                    return TestResult(False, 'Test inverted: {} is in an ocean.', sim, tooltip=in_tooltip)
                return TestResult.TRUE
        if invert:
            return TestResult.TRUE
        return TestResult(False, '{} is not in an ocean.', sim, tooltip=in_tooltip)


class _SimInWaterTest:

    def evaluate(self, sim, in_tooltip, invert):
        if sim.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
            if invert:
                return TestResult(False, 'Test inverted: {} is in the water.', sim, tooltip=in_tooltip)
            return TestResult.TRUE
        if invert:
            return TestResult.TRUE
        return TestResult(False, '{} is not in the water.', sim, tooltip=in_tooltip)


class SwimLocationTest(HasTunableSingletonFactory, AutoFactoryInit, test_base.BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The subject to test to determine whether they are\n            in a certain body of water\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'test':TunableVariant(description='\n            The type of body of water we are testing for\n            ',
       default='swim_in_pool',
       locked_args={'swim_in_pool':_SwimInPoolTest(), 
      'swim_in_ocean':_SwimInOceanTest(), 
      'any':_SimInWaterTest()}), 
     'invert':Tunable(description='\n            Inverts the result of tuned test.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects):
        subject = next(iter(subjects), None)
        if subject is None:
            return TestResult(False, 'SwimLocationTest: Subject is None')
            if subject.is_sim:
                sim = subject.get_sim_instance()
                if sim is None:
                    return TestResult(False, 'SwimLocationTest: Sim is not instanced')
                return self.test.evaluate(sim, self.tooltip, self.invert)
        else:
            return TestResult(False, 'SwimLocationTest: Subject is not a Sim')