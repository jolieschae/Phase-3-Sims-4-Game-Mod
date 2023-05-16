# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\walkstyle\wading_tests.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 13434 bytes
import build_buy
from event_testing import test_base
from event_testing.results import TestResult
from caches import cached_test
from interactions import ParticipantTypeSingle
from objects import ALL_HIDDEN_REASONS
from objects.pools.pond_utils import PondUtils
from sims4.math import Vector2
from sims4.tuning.geometric import TunableVector2
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableVariant, Tunable, TunableInterval, TunableList
from terrain import get_water_depth
from world.ocean_tuning import OceanTuning
import routing

class _CustomIntervalTest(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'height_range': TunableInterval(tunable_type=float,
                       default_lower=(-1000),
                       default_upper=1000,
                       minimum=(-1000),
                       maximum=1000)}

    def evaluate(self, subject, water_height, wading_interval, negate, tooltip):
        lower_bound = self.height_range.lower_bound
        upper_bound = self.height_range.upper_bound
        in_interval = lower_bound <= water_height <= upper_bound
        if in_interval:
            if negate:
                return TestResult(False, f"{subject} cannot go here. Water height {water_height} is between {lower_bound} and {upper_bound} and negate is True.", tooltip=tooltip)
            return TestResult.TRUE
        else:
            if negate:
                return TestResult.TRUE
            return TestResult(False, f"{subject} cannot go here. Water height {water_height} is not between {lower_bound} and {upper_bound}", tooltip=tooltip)


class _WalkHereTest:

    def evaluate(self, subject, water_height, wading_interval, negate, tooltip):
        if wading_interval is None:
            sim = subject.get_sim_instance()
            if sim is None:
                return TestResult(False, 'Failed wading test since the sim is none', tooltip=tooltip)
            if sim.routing_surface.type == routing.SurfaceType.SURFACETYPE_WORLD:
                if negate:
                    return TestResult(False, f"{subject} can walk on the world routing surface, but the test is negated.", tooltip=tooltip)
                return TestResult.TRUE
            if negate:
                return TestResult.TRUE
            return TestResult(False, f"{subject} cannot walk here as they have no wading interval and are not on the world routing surface.", tooltip=tooltip)
        if water_height < wading_interval.lower_bound:
            if negate:
                return TestResult(False, f"{subject} can walk here, but the test is negated. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)
            return TestResult.TRUE
        if negate:
            return TestResult.TRUE
        return TestResult(False, f"{subject} cannot walk here. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)


class _WetHereTest:

    def evaluate(self, subject, water_height, wading_interval, negate, tooltip):
        if wading_interval is None:
            if negate:
                return TestResult.TRUE
            return TestResult(False, f"{subject} no wading water defined in world.", tooltip=tooltip)
        if 0 < water_height:
            if water_height < wading_interval.lower_bound:
                if negate:
                    return TestResult(False, f"{subject} can walk here, but the test is negated. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)
                return TestResult.TRUE
        if negate:
            return TestResult.TRUE
        return TestResult(False, f"{subject} cannot walk here. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)


class _WadeHereTest:

    def evaluate(self, subject, water_height, wading_interval, negate, tooltip):
        if wading_interval is None:
            return TestResult(False, f"No wading interval found for {subject}.", tooltip=tooltip)
        if water_height in wading_interval:
            if negate:
                return TestResult(False, f"{subject} can wade here, but the test is negated. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)
            return TestResult.TRUE
        if negate:
            return TestResult.TRUE
        return TestResult(False, f"{subject} cannot wade here. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)


class _SwimHereTest:

    def evaluate(self, subject, water_height, wading_interval, negate, tooltip):
        if wading_interval is None:
            sim = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return TestResult(False, f"{subject} is not instanced.", tooltip=tooltip)
            if sim.routing_surface.type == routing.SurfaceType.SURFACETYPE_POOL:
                if negate:
                    return TestResult(False, f"{subject} can swim on the pool routing surface, but the test is negated.", tooltip=tooltip)
                return TestResult.TRUE
            if negate:
                return TestResult.TRUE
            return TestResult(False, f"{subject} cannot swim here as they have no wading interval and are not on the pool routing surface.", tooltip=tooltip)
        if water_height > wading_interval.upper_bound:
            if negate:
                return TestResult(False, f"{subject} can swim here, but the test is negated. Water height: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)
            return TestResult.TRUE
        if negate:
            return TestResult.TRUE
        return TestResult(False, f"{subject} cannot swim here. Water height offset: {water_height} Wading interval: {wading_interval}.", tooltip=tooltip)


class WadingIntervalTest(HasTunableSingletonFactory, AutoFactoryInit, test_base.BaseTest):
    WATER_DEPTH_ON_LAND = -1.0
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The subject to test to determine if they should walk, wade or swim\n            based on the water height at the targets location.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'target':TunableEnumEntry(description='\n            The target whose location will be used to determine the water\n            height.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Object), 
     'test':TunableVariant(description='\n            The type of test to run against the subjects wading interval and \n            the targets location.\n            ',
       default='walk_here',
       custom=_CustomIntervalTest.TunableFactory(),
       locked_args={'walk_here':_WalkHereTest(), 
      'wet_here':_WetHereTest(), 
      'wade_here':_WadeHereTest(), 
      'swim_here':_SwimHereTest()}), 
     'negate':Tunable(description='\n            If checked, negate the result of the specified test.\n            ',
       tunable_type=bool,
       default=False), 
     'extra_offset_points':TunableList(description='\n            A list of extra offset points to check up around the target location.\n            All these points along with the original location need to satisfy the\n            water height in order to pass the test.\n            ',
       tunable=TunableVector2(description='\n                Offset to the target location.\n                ',
       default=(TunableVector2.DEFAULT_ZERO),
       x_axis_name='X',
       y_axis_name='Z'))}

    def get_expected_args(self):
        return {'subjects':self.subject, 
         'targets':self.target}

    @cached_test
    def __call__(self, subjects, targets):
        subject = next(iter(subjects), None)
        if subject is None:
            return TestResult(False, 'WadingTest: Subject is None')
        target = next(iter(targets), None)
        if target is None:
            return TestResult(False, 'WadingTest: Target is None.')
        if target.is_sim:
            target = target.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if target is None:
                return TestResult(False, 'WadingTest: Target Sim is not instanced.')
        elif bool(build_buy.get_pond_id(target.position)):
            wading_interval = PondUtils.get_actor_wading_interval(subject)
        else:
            wading_interval = OceanTuning.get_actor_wading_interval(subject)
        if target.location is None or target.location.routing_surface is None:
            water_height = WadingIntervalTest.WATER_DEPTH_ON_LAND
            return self.test.evaluate(subject, water_height, wading_interval, self.negate, self.tooltip)
        target_translation = target.location.transform.translation
        locations_to_test = []
        locations_to_test.append(Vector2(target_translation[0], target_translation[2]))
        for offset in self.extra_offset_points:
            locations_to_test.append(Vector2(target_translation[0] + offset.x, target_translation[2] + offset.y))

        if len(locations_to_test) > 1:
            subject_inst = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS) if subject.is_sim else subject
            subject_translation = subject_inst.location.transform.translation
            subject_location = Vector2(subject_translation[0], subject_translation[2])
            locations_to_test.sort(key=(lambda loc: (loc - subject_location).magnitude_squared()), reverse=True)
        result = TestResult.TRUE
        for location in locations_to_test:
            water_height = get_water_depth(location.x, location.y, target.location.level)
            result = self.test.evaluate(subject, water_height, wading_interval, self.negate, self.tooltip)
            if not result:
                return result

        return result