# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_phase.py
# Compiled at: 2022-11-01 20:51:01
# Size of source mod 2**32: 19566 bytes
import event_testing, services, sims4
from event_testing.resolver import SingleSimResolver, GlobalResolver, DoubleSimResolver
from event_testing.tests import TestList
from gameplay_scenarios.scenario_outcomes import ScenarioPhaseLoot, ScenarioOutcome
from gameplay_scenarios.scenario_phase_goal import ScenarioPhaseGoal
from gameplay_scenarios.scenario_tests_set import ScenarioTestSet, TunableScenarioBreakTestSet, TunableScenarioBreakTest
from sims4.localization import TunableLocalizedString
from event_testing.results import TestResult
from sims4.tuning.tunable import HasTunableReference, TunableTuple, TunableList, HasTunableFactory, AutoFactoryInit, TunableReference, Tunable
from sims4.tuning.tunable_base import ExportModes, GroupNames
logger = sims4.log.Logger('Scenario Phase')

class PhaseEndingReason:
    COMPLETE = 1
    SKIPPED = 2
    TERMINATED = 3


class ScenarioPhaseOutput(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'output': TunableTuple(description='\n            Data containing condition and next phase or outcome.\n            ',
                 scenario_outcome=ScenarioOutcome.TunableReference(description='\n                The scenario outcome.\n                If this is set, do not set next_phase, because\n                outcome is the end point of the scenario.\n                ',
                 pack_safe=True,
                 allow_none=True,
                 export_modes=(ExportModes.ClientBinary)),
                 next_phase=TunableReference(description='\n                The next phase.\n                If this is set do not set scenario_outcome, because setting this will\n                make scenario progress to next phase and outcome is about what\n                happens in the end of the scenario.\n                ',
                 manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
                 class_restrictions=('ScenarioPhase', ),
                 allow_none=True,
                 pack_safe=True,
                 export_modes=(ExportModes.ClientBinary)),
                 output_loot=ScenarioPhaseLoot.TunableFactory(description='\n                Phase output loot.\n                '),
                 export_class_name='ScenarioPhaseOutputData')}


def get_phase_output_descriptor(output):
    if output.scenario_outcome is not None:
        return 'outcome:{}'.format(output.scenario_outcome.guid64)
    if output.next_phase is not None:
        return 'phase:{}'.format(output.next_phase.guid64)
    return 'invalid'


class TerminatorHandler:

    def __init__(self, scenario, terminator, handle_callback, **kwargs):
        (super().__init__)(**kwargs)
        self._scenario = scenario
        self._terminator = terminator
        self._handle_callback = handle_callback

    @property
    def terminator(self):
        return self._terminator

    def handle_event(self, sim_info, event, resolver):

        def run_test(test_resolver, scenario):
            test_list = TestList([self._terminator.termination_condition.scenario_test.test])
            test_resolver.set_additional_metric_key_data(scenario.current_phase)
            result = test_list.run_tests(test_resolver)
            if result:
                self._handle_callback(self._terminator)

        role = self._terminator.termination_condition.scenario_test.actor_role
        actor_sim_filter = self._terminator.termination_condition.scenario_test.actor_sim_filter
        if role is not None:
            for sim_info_from_role in self._scenario.sim_infos_of_interest_gen([role]):
                if sim_info_from_role == sim_info:
                    run_test(resolver, self._scenario)

        else:
            if actor_sim_filter is not None and self._scenario.get_sim_info_from_sim_filter(actor_sim_filter) == sim_info:
                run_test(resolver, self._scenario)


def run_scenario_test(scenario_test, scenario, phase=None):

    def run_double_sim_test(sim_info, sim_info_2):
        resolver = DoubleSimResolver(sim_info, sim_info_2)
        resolver.set_additional_metric_key_data(scenario.current_phase)
        return TestList([scenario_test.test]).run_tests(resolver)

    def check_and_run_single_or_double_sim_test(sim_info, scenario_test):
        secondary_actor_role = scenario_test.secondary_actor_role
        secondary_actor_sim_filter = scenario_test.secondary_actor_sim_filter
        if secondary_actor_role is not None:
            for sim_info_2 in scenario.sim_infos_of_interest_gen([secondary_actor_role]):
                test_result = True
                if not run_double_sim_test(sim_info, sim_info_2):
                    test_result = False
                    break
                return test_result

        else:
            if secondary_actor_sim_filter is not None:
                sim_info_2 = scenario.get_sim_info_from_sim_filter(secondary_actor_sim_filter)
                if sim_info_2 is not None:
                    return run_double_sim_test(sim_info, sim_info_2)
                logger.error('No sim satisfying secondary_actor_sim_filter conditions is found.')
                return False
            else:
                resolver = event_testing.resolver.DataResolver(sim_info=sim_info, additional_metric_key_data=phase)
            return TestList([scenario_test.test]).run_tests(resolver)

    if scenario_test.actor_role is not None:
        output_result = True
        for sim_info in scenario.sim_infos_of_interest_gen([scenario_test.actor_role]):
            if not check_and_run_single_or_double_sim_test(sim_info, scenario_test):
                output_result = False
                break

        return output_result
        if scenario_test.actor_sim_filter is not None:
            sim_info = scenario.get_sim_info_from_sim_filter(scenario_test.actor_sim_filter)
            if sim_info is not None:
                return check_and_run_single_or_double_sim_test(sim_info, scenario_test)
            logger.error('No sim satisfying actor_sim_filter conditions is found.')
            return False
    else:
        return TestList([scenario_test.test]).run_tests(GlobalResolver(additional_metric_key_data=phase))


class SequentialGoalResetHandler:

    def __init__(self, scenario, goal_sequence_tuple, sequence_index, **kwargs):
        (super().__init__)(**kwargs)
        self._scenario = scenario
        self._goal_sequence_tuple = goal_sequence_tuple
        self._sequence_index = sequence_index

    @property
    def tests(self):
        reset_tests = []
        for test_tuple in self._goal_sequence_tuple.sequence_reset_conditions.scenario_tests:
            reset_tests.append(test_tuple.scenario_test.test)

        return reset_tests

    def handle_event(self, sim_info, event, resolver):
        for test_tuple in self._goal_sequence_tuple.sequence_reset_conditions.scenario_tests:
            role = test_tuple.scenario_test.actor_role
            if role is None:
                return
            for sim_info_from_role in self._scenario.sim_infos_of_interest_gen([role]):
                if sim_info_from_role == sim_info:
                    test_list = TestList([test_tuple.scenario_test.test])
                    result = test_list.run_tests(resolver)
                    if result:
                        self._scenario.on_goal_sequence_reset(self._goal_sequence_tuple.goal_sequence, self._sequence_index)
                    return


class ScenarioPhase(HasTunableReference, metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'phase_objective':TunableLocalizedString(description='\n            Phase objective text.\n            ',
       tuning_group=GroupNames.UI), 
     'pre_tests':ScenarioTestSet.TunableFactory(description='\n            A set of tests on the player sim and environment that all must\n            pass for the phase to be activated. e.g. Player Sim\n            has cooking skill level 7.\n            ',
       tuning_group=GroupNames.TESTS), 
     'intro_loot':ScenarioPhaseLoot.TunableFactory(description='\n            Phase intro loot.\n            These are applied only when the phase starts.\n            '), 
     'goals':TunableList(description='\n            A collection of goals that can be either independent or sequential.           \n            Each item here is a list of goals that needs to be completed in order.\n            Each list in the collection is independent of each other.\n            ',
       tunable=TunableTuple(description='\n                Data containing goal sequence and its reset condition.\n                Add only one goal if goal will be stand alone/independent.\n                ',
       goal_sequence=TunableList(description='\n                    A list of goals which needs to be completed in order,\n                    based on which each goal is defined.\n                    Add only one goal if goal will be stand alone/independent.\n                    ',
       tunable=ScenarioPhaseGoal.TunableFactory(description='\n                        A scenario phase goal.\n                        ')),
       sequence_reset_conditions=TunableScenarioBreakTestSet.TunableFactory(description='\n                    Reset conditions for a goal sequence.\n                    If any of the tests in conditions list pass sequence will be reset.\n                    Only one test pass is enough for sequence reset.\n                    ',
       export_modes=(ExportModes.ServerXML)),
       export_class_name='TunableScenarioGoals')), 
     'phase_fallback_output':ScenarioPhaseOutput.TunableFactory(description='\n            If all other outputs fail this will be the output.\n            It does not have any conditions.\n            '), 
     'phase_outputs':TunableList(description='\n            List of possible outputs.\n            ',
       tunable=TunableTuple(description='\n                Data containing phase output with its conditions.\n                ',
       output=ScenarioPhaseOutput.TunableFactory(description='\n                    A phase output containing loot and next phase or outcome.\n                    '),
       conditions=ScenarioTestSet.TunableFactory(description='\n                    List of conditions. Connected output will be selected only if all of its condition tests pass.\n                    '),
       export_class_name='ScenarioPhaseOutputListData')), 
     'terminators':TunableList(description='\n            List of Terminators.\n            If any terminator test is triggered, the current phase will be terminated.\n            ',
       tunable=TunableTuple(description='\n                Data containing termination condition and description text of terminator. \n                ',
       termination_condition=TunableScenarioBreakTest.TunableFactory(description='\n                    A test to determine if the terminator is triggered.\n                    '),
       terminator_description_text=TunableLocalizedString(description='\n                    Description text for terminator (only for debug purposes).\n                    ')))}

    def __init__(self, scenario, **kwargs):
        (super().__init__)(**kwargs)
        self._scenario = scenario
        self._terminator_handlers = []
        self._goal_sequence_reset_handlers = []

    def __str__(self):
        return self.__class__.__name__

    def on_start(self):
        self.register_phase_terminators()
        self.register_goal_sequence_reset_tests()

    def end_phase(self, reason, end_description):
        self.unregister_phase_terminators()
        self.unregister_goal_sequence_reset_tests()
        self._scenario.on_phase_ended(reason, end_description)

    def on_load(self):
        self.register_phase_terminators()
        self.register_goal_sequence_reset_tests()

    def register_phase_terminators(self):
        for terminator in self.terminators:
            self._terminator_handlers.append(TerminatorHandler(self._scenario, terminator, self.on_terminator_triggered))
            services.get_event_manager().register_tests(self._terminator_handlers[-1], (terminator.termination_condition.scenario_test.test,))

    def unregister_phase_terminators(self):
        for terminator_handler in self._terminator_handlers:
            services.get_event_manager().unregister_tests(terminator_handler, (terminator_handler.terminator.termination_condition.scenario_test.test,))

        self._terminator_handlers.clear()

    def on_terminator_triggered(self, terminator):
        self.choose_output_and_progress(PhaseEndingReason.TERMINATED, terminator.terminator_description_text)

    def register_goal_sequence_reset_tests(self):
        for sequence_index, goal_sequence_tuple in enumerate(self.goals):
            if len(goal_sequence_tuple.sequence_reset_conditions.scenario_tests) != 0:
                goal_sequence_reset_handler = SequentialGoalResetHandler(self._scenario, goal_sequence_tuple, sequence_index)
                self._goal_sequence_reset_handlers.append(goal_sequence_reset_handler)
                services.get_event_manager().register_tests(goal_sequence_reset_handler, goal_sequence_reset_handler.tests)

    def unregister_goal_sequence_reset_tests(self):
        for goal_sequence_reset_handler in self._goal_sequence_reset_handlers:
            services.get_event_manager().unregister_tests(goal_sequence_reset_handler, goal_sequence_reset_handler.tests)

        self._terminator_handlers.clear()

    def choose_output_and_progress(self, phase_end_reason, termination_description_text=None):
        key = 0
        for phase_output in self.phase_outputs:
            output_result = True
            for test_tuple in phase_output.conditions.scenario_tests:
                if not run_scenario_test(test_tuple.scenario_test, self._scenario, self):
                    output_result = False
                    break

            if output_result:
                self.progress_with_output((phase_output.output.output),
                  key,
                  give_warning=False,
                  phase_end_reason=phase_end_reason,
                  termination_description_text=termination_description_text)
                return
            key += 1

        self.progress_with_output((self.phase_fallback_output.output),
          (-1),
          give_warning=True,
          phase_end_reason=phase_end_reason,
          termination_description_text=termination_description_text)

    def progress_with_output(self, output, output_key, give_warning, phase_end_reason, termination_description_text):
        self._scenario.apply_loot(output.output_loot.loots)
        self._scenario.on_phase_output_triggered(output_key, output.next_phase)
        end_text = get_phase_output_descriptor(output)
        if termination_description_text is not None:
            end_text = '{} ({})'.format(end_text, termination_description_text)
        else:
            self.end_phase(phase_end_reason, end_text)
            if output.scenario_outcome is not None:
                self._scenario.end_scenario(output.scenario_outcome, self)
            else:
                if output.next_phase is not None:
                    self._scenario.start_phase(output.next_phase(scenario=(self._scenario)))
                else:
                    if give_warning:
                        logger.warn('No fallback output in phase {}.', self)

    def run_pre_tests(self):
        for pre_test in self.pre_tests.scenario_tests:
            if not run_scenario_test(pre_test.scenario_test, self._scenario, self):
                return False

        return True

    @classmethod
    def goals_gen(cls):
        for goal_sequence_tuple in cls.goals:
            for goal_tuple in goal_sequence_tuple.goal_sequence:
                yield goal_tuple.goal

    @classmethod
    def mandatory_goals_list(cls):
        return [goal for goal in cls.goals_gen() if goal.mandatory]