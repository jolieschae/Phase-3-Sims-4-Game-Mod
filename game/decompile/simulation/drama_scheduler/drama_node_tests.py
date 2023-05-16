# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node_tests.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 24384 bytes
from date_and_time import TimeSpan
from drama_scheduler.drama_enums import DramaNodeScoringBucket
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.results import TestResult
from event_testing.test_events import TestEvent
from caches import cached_test
from interactions import ParticipantTypeSingleSim
from sims4.tuning.tunable import Tunable, OptionalTunable, TunableTuple, TunableReference, HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableList, TunableThreshold
import event_testing.test_base, services, sims4
from tunable_time import TunableTimeSpanSingleton
logger = sims4.log.Logger('DramaNodeTests', default_owner='jjacobson')

class FestivalRunningTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be running.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'check_if_on_festival_street':OptionalTunable(description="\n            If enabled, test against if the player is on the festival's street.\n            ",
       tunable=Tunable(description="\n                If checked, this test will pass only if the player is on the\n                festival's street. If unchecked, the test will pass only if the\n                player is not on the festival street.\n                ",
       tunable_type=bool,
       default=True)), 
     'valid_time_blocks':TunableTuple(description='\n            Festival drama nodes have a tunable pre-festival duration that\n            delay festival start to some point after the drama node has\n            started. For example, if the festival drama node has a pre-festival\n            duration of 2 hours and the drama node runs at 8am, the festival\n            will not start until 10am.\n\n            By default, this test passes if the festival drama node is running,\n            regardless if the festival is in its pre-festival duration. This\n            tuning changes that behavior.\n            ',
       pre_festival=Tunable(description='\n                If the festival is currently in its pre-festival duration,\n                test can pass if this is checked and fails if unchecked.\n                ',
       tunable_type=bool,
       default=True),
       running=Tunable(description='\n                If the festival is running (it is past its pre-festival\n                duration), test can pass if this is checked and fails if\n                unchecked.\n                ',
       tunable_type=bool,
       default=True)), 
     'negate':Tunable(description='\n            If enabled this test will pass if no festivals of the tuned\n            requirements are running.\n            ',
       tunable_type=bool,
       default=False), 
     'festivals_to_check':OptionalTunable(description='\n            If enabled then we will only check a subset of all festival drama nodes referenced here.\n            This will only apply if there is no specific drama node specified.\n            ',
       tunable=TunableList(description='\n                A list of festival drama nodes that we want to check against.\n                ',
       tunable=TunableReference(description='\n                    Reference to the festival drama node that we want to check against.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', ))))}
    test_events = (
     TestEvent.FestivalStarted,)

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        for node in drama_scheduler.active_nodes_gen():
            if self.drama_node is None:
                if node.drama_node_type != DramaNodeType.FESTIVAL:
                    continue
                if self.festivals_to_check is not None and type(node) not in self.festivals_to_check:
                    continue
            elif type(node) is not self.drama_node:
                continue
            if self.check_if_on_festival_street is not None:
                if hasattr(node, 'festival_contest_tuning'):
                    if node.is_festival_contest_sub_node():
                        continue
            elif self.check_if_on_festival_street != node.is_on_festival_street():
                continue
            elif node.is_during_pre_festival() and not self.valid_time_blocks.pre_festival:
                continue
            else:
                if not self.valid_time_blocks.running:
                    continue
            if self.negate:
                return TestResult(False, 'Drama nodes match the required conditions.')
            return TestResult.TRUE

        if self.negate:
            return TestResult.TRUE
        return TestResult(False, 'No drama nodes match the required conditions.')


class NextFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at all of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to be the\n                next one.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'negate':Tunable(description='\n            If enabled this test will pass if the next festival is not one of\n            the tuned nodes.\n            ',
       tunable_type=bool,
       default=False), 
     'festivals_to_check':OptionalTunable(description='\n            If enabled then we will only check a subset of all festival drama nodes referenced here.\n            ',
       tunable=TunableList(description='\n                A list of festival drama nodes that we want to check against.\n                ',
       tunable=TunableReference(description='\n                    Reference to the festival drama node that we want to check against.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', ))))}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        best_time = None
        best_nodes = [type(node) for node in drama_scheduler.active_nodes_gen() if node.drama_node_type == DramaNodeType.FESTIVAL and (self.festivals_to_check is None or type(node) in self.festivals_to_check)]
        if not best_nodes:
            for node in drama_scheduler.scheduled_nodes_gen():
                if node.drama_node_type != DramaNodeType.FESTIVAL:
                    continue
                if self.festivals_to_check is not None:
                    if type(node) not in self.festivals_to_check:
                        continue
                    else:
                        new_time = node._selected_time - services.time_service().sim_now
                        if best_time is None or new_time < best_time:
                            best_nodes = [
                             type(node)]
                            best_time = new_time
                    if new_time == best_time:
                        best_nodes.append(type(node))

        if not best_nodes:
            if self.negate:
                return TestResult.TRUE
            return TestResult(False, 'No scheduled Festivals.')
        if self.drama_node is None or self.drama_node in best_nodes:
            if self.negate:
                return TestResult(False, 'Next scheduled Festival matches requested.')
            return TestResult.TRUE
        if self.negate:
            return TestResult.TRUE
        return TestResult(False, "Next scheduled Festival doesn't match requested.")


class TimeUntilFestivalTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_node':OptionalTunable(description='\n            If enabled then we will check a specific type of festival drama\n            node otherwise we will look at any of the festival drama nodes.\n            ',
       tunable=TunableReference(description='\n                Reference to the festival drama node that we want to test.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalDramaNode', )),
       enabled_by_default=True), 
     'max_time':Tunable(description='\n            Maximum time in hours between when the test occurs to the start of\n            the festival in order for the test to return true.\n            ',
       tunable_type=float,
       default=18.0), 
     'negate':Tunable(description='\n            If enabled this test will pass if the requested festival will not\n            start within the specified time.\n            ',
       tunable_type=bool,
       default=False)}

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self):
        drama_scheduler = services.drama_scheduler_service()
        best_time = None
        for node in drama_scheduler.scheduled_nodes_gen():
            if node.drama_node_type != DramaNodeType.FESTIVAL:
                continue
            if self.drama_node is None or self.drama_node is type(node):
                new_time = node.get_time_remaining()
                if best_time is None or new_time < best_time:
                    best_time = new_time

        if best_time is None:
            return self.negate or TestResult(False, 'No scheduled Festivals of type {}.', (self.drama_node),
              tooltip=(self.tooltip))
        else:
            if best_time.in_hours() < self.max_time:
                if self.negate:
                    return TestResult(False, 'Next scheduled Festival is within specified time',
                      tooltip=(self.tooltip))
            elif not self.negate:
                return TestResult(False, "Next scheduled Festival isn't within specified time",
                  tooltip=(self.tooltip))
        return TestResult.TRUE


class DramaNodeTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'drama_nodes':TunableList(description='\n            The types of drama nodes that we want to check.\n            ',
       tunable=TunableReference(description='\n                A Drama node type we want to check.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       pack_safe=True)), 
     'check_scheduled_nodes':Tunable(description='\n            Check against nodes that are scheduled, but not actively running.\n            ',
       tunable_type=bool,
       default=True), 
     'check_active_nodes':Tunable(description='\n            Check against nodes that are actively running.\n            ',
       tunable_type=bool,
       default=True), 
     'situation_type':OptionalTunable(description='\n            If a situation exists on the drama node, specify the type of situation to check.\n            ',
       tunable=TunableReference(description='\n                The type of situation the drama node has. \n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))), 
     'situation_host_sim':OptionalTunable(description='\n            If a situation exist on the drama node, specify who the host of that situation should be.\n            ',
       tunable=TunableEnumEntry(description='\n                The required host of the situation. \n                ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Actor))), 
     'situation_special_object_exists':OptionalTunable(description='\n            If enabled and a situation exists on the drama node, specify if\n            the situation should have a special object associated with it. \n            ',
       tunable=Tunable(description='\n                If checked, require the situation to have a special object. \n                ',
       tunable_type=bool,
       default=True)), 
     'exists':Tunable(description='\n            If checked then this drama node will pass if a node meeting the requirements exists.\n            Otherwise it will pass if there is not a node meeting the requirements.\n            ',
       tunable_type=bool,
       default=True), 
     'receiver_sim':OptionalTunable(description='\n            If enabled we will check that the receiver Sim is the tuned Sim.\n            ',
       tunable=TunableEnumEntry(description='\n                The Sim that we will make sure is the receiver Sim.\n                ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.TargetSim))), 
     'time_to_run':OptionalTunable(description='\n            If enabled then we will check against the remaining time until the the drama node is scheduled to run.\n            ',
       tunable=TunableTuple(threshold=TunableThreshold(description='\n                    A threshold to compare the amount of time left for this drma node to be run.\n                    ',
       value=TunableTimeSpanSingleton(description='\n                        The amount of time to compare against.\n                        '),
       default=(sims4.math.Threshold(TimeSpan.ZERO, sims4.math.Operator.GREATER_OR_EQUAL.function))),
       additional_threshold=OptionalTunable(description='\n                    If enabled then we will have a second threshold to compare against.\n                    ',
       tunable=TunableThreshold(description='\n                        A threshold to compare the amount of time left for this drma node to be run.\n                        ',
       value=TunableTimeSpanSingleton(description='\n                            The amount of time to compare against.\n                            '),
       default=(sims4.math.Threshold(TimeSpan.ZERO, sims4.math.Operator.GREATER_OR_EQUAL.function))))))}

    def get_expected_args(self):
        expected_args = {}
        if self.situation_host_sim is not None:
            expected_args['situation_host_sims'] = self.situation_host_sim
        if self.receiver_sim is not None:
            expected_args['receiver_sim'] = self.receiver_sim
        return expected_args

    @cached_test
    def __call__(self, receiver_sim=None, situation_host_sims=None):
        if not self.drama_nodes:
            if self.exists:
                return TestResult(False, 'No drama node exists meeting the requirements.',
                  tooltip=(self.tooltip))
            return TestResult.TRUE
        drama_scheduler = services.drama_scheduler_service()
        if self.check_scheduled_nodes and self.check_active_nodes:
            drama_node_gen = drama_scheduler.all_nodes_gen
        else:
            if self.check_scheduled_nodes:
                drama_node_gen = drama_scheduler.scheduled_nodes_gen
            else:
                if self.check_active_nodes:
                    drama_node_gen = drama_scheduler.active_nodes_gen
                else:
                    if self.exists:
                        return TestResult(False, 'No drama node exists meeting the requirements.',
                          tooltip=(self.tooltip))
                    return TestResult.TRUE
        if receiver_sim is not None:
            receiver_sim = next(iter(receiver_sim))
        now = services.time_service().sim_now
        for drama_node in drama_node_gen():
            if type(drama_node) not in self.drama_nodes:
                continue
            situation_seed = drama_node.get_situation_seed()
            if situation_seed is not None:
                if self.situation_type is not None:
                    if situation_seed.situation_type != self.situation_type:
                        continue
                    elif situation_host_sims is not None and situation_seed.host_sim_id not in [host_sim.id for host_sim in situation_host_sims]:
                        continue
                    if self.situation_special_object_exists is not None:
                        if self.situation_special_object_exists:
                            if situation_seed.special_object_definition_id is None:
                                continue
                    elif situation_seed.special_object_definition_id is not None:
                        continue
                else:
                    if self.situation_type is not None or situation_host_sims is not None or self.situation_special_object_exists is not None:
                        continue
                    else:
                        if receiver_sim is not None:
                            if drama_node.get_receiver_sim_info() is not receiver_sim:
                                continue
                        if self.time_to_run is not None:
                            time_to_node = drama_node.selected_time - now
                            if not self.time_to_run.threshold.compare(time_to_node):
                                continue
                            if self.time_to_run.additional_threshold is not None:
                                if not self.time_to_run.additional_threshold.compare(time_to_node):
                                    continue
                    if self.exists:
                        return TestResult.TRUE
                    return TestResult(False, 'Drama node meeting the requirements exists when we are asking for non-existence.', tooltip=(self.tooltip))

        if self.exists:
            return TestResult(False, 'No drama node exists meeting the requirements.',
              tooltip=(self.tooltip))
        return TestResult.TRUE


class DramaNodeBucketTest(HasTunableSingletonFactory, AutoFactoryInit, event_testing.test_base.BaseTest):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description='\n            Who or what to apply this test to.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'buckets':TunableList(description='\n            List of drama node buckets to test against.\n            ',
       tunable=TunableEnumEntry(description='\n                Bucket to test against.\n                ',
       tunable_type=DramaNodeScoringBucket,
       default=(DramaNodeScoringBucket.DEFAULT)),
       unique_entries=True), 
     'use_only_scheduled':Tunable(description='\n            If checked, this test will only consider drama nodes that have been \n            scheduled by the drama scheduler service.\n            ',
       tunable_type=bool,
       default=True), 
     'run_visibility_tests':Tunable(description='\n            If checked, run the visibility tests on a drama node to decide \n            whether it would be shown. Otherwise, all drama nodes will be \n            available.\n            ',
       tunable_type=bool,
       default=True)}

    def get_expected_args(self):
        return {'participants': self.participant}

    @cached_test
    def __call__(self, participants):
        sim = next(iter(participants))
        if self.use_only_scheduled:
            drama_nodes = iter(services.drama_scheduler_service().all_nodes_gen())
        else:
            drama_node_manager = services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)
            drama_nodes = (drama_node() for drama_node in drama_node_manager.types.values())
        for drama_node in drama_nodes:
            if self.buckets:
                if drama_node.scoring is None or drama_node.scoring.bucket not in self.buckets:
                    continue
            result = drama_node.create_picker_row(owner=sim, run_visibility_tests=(self.run_visibility_tests))
            if result is not None:
                return TestResult.TRUE

        return TestResult(False, 'No drama nodes available in the given buckets.', tooltip=(self.tooltip))