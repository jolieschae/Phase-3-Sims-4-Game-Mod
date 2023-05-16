# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\roommate_service_utils\roommate_tests.py
# Compiled at: 2021-03-15 20:14:30
# Size of source mod 2**32: 9230 bytes
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantTypeSingleSim, ParticipantType
from services.roommate_service_utils.roommate_enums import RoommateLeaveReason
from sims4.tuning.tunable import Tunable, TunableVariant, TunableEnumSet, TunableEnumEntry, HasTunableSingletonFactory, AutoFactoryInit
import services

class RoommateTests(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):

    class IsRoommateTest(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n                The participant against which to run this test.\n                ',
           tunable_type=ParticipantTypeSingleSim,
           default=ParticipantTypeSingleSim.Actor), 
         'household':TunableVariant(description='\n                Which household the participant must be a roommate of.\n                ',
           participant_sim_household=TunableEnumEntry(description='\n                    The sim whose household the participant must be a roommate of.\n                    ',
           tunable_type=ParticipantTypeSingleSim,
           default=(ParticipantTypeSingleSim.TargetSim)),
           locked_args={'any_household':None, 
          'active_household':ParticipantType.ActiveHousehold},
           default='any_household'), 
         'invert':Tunable(description='\n                If true, the test will pass if the sim is a valid roommate\n                Otherwise will pass if the sim is not.\n                ',
           tunable_type=bool,
           default=False)}

        def get_expected_args(self):
            expected_args = {}
            if self.household is not None:
                expected_args['households'] = self.household
            expected_args['test_targets'] = self.subject
            return expected_args

        def test(self, tooltip=None, test_targets=(), households=None):
            roommate_service = services.get_roommate_service()
            if roommate_service is None:
                if self.invert:
                    return TestResult.TRUE
                return TestResult(False, 'There are no roommates, but testing to be one', tooltip=tooltip)
            household_id = None
            if households is not None:
                if not households:
                    if self.invert:
                        return True
                    return TestResult(False, "Can't be a roommate of missing participant {}", (self.household), tooltip=tooltip)
                household_id = households[0].household_id
            for target in test_targets:
                if roommate_service.is_sim_info_roommate(target.sim_info, household_id):
                    if self.invert:
                        return TestResult(False, "{} is a roommate but shouldn't be", target, tooltip=tooltip)
                    else:
                        return self.invert or TestResult(False, '{} is not a roommate but should be', target, tooltip=tooltip)

            return TestResult.TRUE

    class RoommateRoomTest(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'invert': Tunable(description='\n                If checked, invert the test\n                ',
                     tunable_type=bool,
                     default=False)}

        def get_expected_args(self):
            return {}

        def test(self, tooltip=None):
            roommate_service = services.get_roommate_service()
            if roommate_service is None:
                if self.invert:
                    return TestResult.TRUE
                return TestResult(False, 'No room for roommates if the is no service', tooltip=tooltip)
            zone_id = services.active_household().home_zone_id
            if roommate_service.get_available_roommate_count_for_zone(zone_id) > 0:
                if self.invert:
                    return TestResult(False, "Is room for roommate but we don't want room", tooltip=tooltip)
                return TestResult.TRUE
            if self.invert:
                return TestResult.TRUE
            return TestResult(False, "Isn't room for roommate but we want room", tooltip=tooltip)

    class RoommateAdTest(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'invert': Tunable(description='\n                If checked, invert the test\n                ',
                     tunable_type=bool,
                     default=False)}

        def get_expected_args(self):
            return {}

        def test(self, tooltip=None):
            roommate_service = services.get_roommate_service()
            if roommate_service is None:
                if self.invert:
                    return TestResult.TRUE
                return TestResult(False, 'No roommate service, so roommate ad is off', tooltip=tooltip)
            if roommate_service.are_interviews_scheduled():
                if self.invert:
                    return TestResult(False, 'Ad is on, but testing for it off', tooltip=tooltip)
                return TestResult.TRUE
            if self.invert:
                return TestResult.TRUE
            return TestResult(False, 'Ad is off, but testing for it on', tooltip=tooltip)

    class RoommateLeaveReasonTest(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n                The subject\n                ',
           tunable_type=ParticipantTypeSingleSim,
           default=ParticipantTypeSingleSim.Actor), 
         'reasons':TunableEnumSet(description='\n                Reasons to be tested for.\n                ',
           enum_type=RoommateLeaveReason,
           invalid_enums=(
          RoommateLeaveReason.INVALID,)), 
         'invert':Tunable(description='\n                If checked, invert the test\n                ',
           tunable_type=bool,
           default=False)}

        def get_expected_args(self):
            return {'test_targets': self.subject}

        def test(self, tooltip=None, test_targets=()):
            roommate_service = services.get_roommate_service()
            if roommate_service is None:
                if self.invert:
                    return TestResult.TRUE
                return TestResult(False, "No roommate service, so sim can't have leave reason", tooltip=tooltip)
            for target in test_targets:
                if roommate_service.has_leave_reasons(target.sim_info, self.reasons):
                    if self.invert:
                        return TestResult(False, "{} has leave reasons {} but shouldn't be", target, (self.reasons), tooltip=tooltip)
                    else:
                        return self.invert or TestResult(False, '{} does not have reasons {} should be', target, (self.reasons), tooltip=tooltip)

            return TestResult.TRUE

    FACTORY_TUNABLES = {'test_type': TunableVariant(description='\n            The type of roommate test to perform.\n            ',
                    is_roommate_test=(IsRoommateTest.TunableFactory()),
                    roommate_room_test=(RoommateRoomTest.TunableFactory()),
                    roommate_ad_test=(RoommateAdTest.TunableFactory()),
                    roommate_leave_reason_test=(RoommateLeaveReasonTest.TunableFactory()),
                    default='roommate_room_test')}

    def get_expected_args(self):
        return self.test_type.get_expected_args()

    @cached_test
    def __call__(self, **kwargs):
        return (self.test_type.test)(tooltip=self.tooltip, **kwargs)