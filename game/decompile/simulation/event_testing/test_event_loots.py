# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\test_event_loots.py
# Compiled at: 2019-07-11 21:36:53
# Size of source mod 2**32: 1374 bytes
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingleSim
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry, TunableFactory
import services, singletons

class ProcessEventOp(BaseLootOperation):
    FACTORY_TUNABLES = {'test_event': TunableEnumEntry(description="\n            The test event we'd like to process\n            ",
                     tunable_type=TestEvent,
                     default=(TestEvent.Invalid))}

    def __init__(self, test_event, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._test_event = test_event

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        return (BaseLootOperation.get_participant_tunable)('subject', participant_type_enum=ParticipantTypeSingleSim, **kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        services.get_event_manager().process_event((self._test_event), sim_info=(subject.sim_info))