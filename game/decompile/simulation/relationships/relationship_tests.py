# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_tests.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 53529 bytes
from event_testing import TargetIdTypes
from event_testing.results import TestResult, TestResultNumeric
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from caches import cached_test
from interactions import ParticipantType, ParticipantTypeSingleSim
from relationships.compatibility_tuning import CompatibilityLevel
from sims4.math import Operator
from sims4.tuning.tunable import TunableFactory, TunableEnumFlags, TunableTuple, TunableSet, TunableReference, TunableInterval, Tunable, TunableEnumEntry, TunableSingletonFactory, HasTunableSingletonFactory, AutoFactoryInit, TunableVariant, TunableList, TunablePackSafeReference, TunableOperator, TunableRange
import enum, event_testing, services, sims4.resources, singletons, tag
logger = sims4.log.Logger('RelationshipTests', default_owner='msantander')

class RelationshipTestEvents(enum.Int):
    AllRelationshipEvents = 0
    RelationshipChanged = TestEvent.RelationshipChanged
    AddRelationshipBit = TestEvent.AddRelationshipBit
    RemoveRelationshipBit = TestEvent.RemoveRelationshipBit


MIN_RELATIONSHIP_VALUE = -100.0
MAX_RELATIONSHIP_VALUE = 100.0

class BaseRelationshipTest(BaseTest):
    UNIQUE_TARGET_TRACKING_AVAILABLE = True

    @TunableFactory.factory_option
    def participant_type_override(participant_type_enum, participant_type_default):
        return {'target_sim': TunableEnumFlags(description='\n                    Target(s) of the relationship(s).\n                    ',
                         enum_type=participant_type_enum,
                         default=participant_type_default)}

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        overlapping_bits = (value.required_relationship_bits.match_any | value.required_relationship_bits.match_all) & (value.prohibited_relationship_bits.match_any | value.prohibited_relationship_bits.match_all)
        if overlapping_bits:
            logger.error('Tuning error in {}. Cannot have overlapping required and prohibited relationship bits: {}'.format(instance_class, overlapping_bits))

    FACTORY_TUNABLES = {'subject':TunableEnumFlags(description='\n            Owner(s) of the relationship(s).\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Actor), 
     'required_relationship_bits':TunableTuple(match_any=TunableSet(description='\n                Any of these relationship bits will pass the test.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)), pack_safe=True)),
       match_all=TunableSet(description='\n                All of these relationship bits must be present to pass the\n                test.\n                ',
       tunable=TunablePackSafeReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))),
       allow_none=True)), 
     'prohibited_relationship_bits':TunableTuple(match_any=TunableSet(description='\n                If any of these relationship bits match the test will fail.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)), pack_safe=True)),
       match_all=TunableSet(description='\n                All of these relationship bits must match to fail the test.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))))), 
     'relationship_score_interval':TunableInterval(description='\n            The range that the relationship score must be within in order for\n            this test to pass.\n            ',
       tunable_type=float,
       default_lower=MIN_RELATIONSHIP_VALUE,
       default_upper=MAX_RELATIONSHIP_VALUE,
       minimum=MIN_RELATIONSHIP_VALUE,
       maximum=MAX_RELATIONSHIP_VALUE), 
     'test_event':TunableEnumEntry(description='\n            The event that we want to trigger this instance of the tuned test\n            on.\n            ',
       tunable_type=RelationshipTestEvents,
       default=RelationshipTestEvents.AllRelationshipEvents), 
     'verify_tunable_callback':_verify_tunable_callback}
    __slots__ = ('test_events', 'subject', 'required_relationship_bits', 'prohibited_relationship_bits',
                 'track', 'relationship_score_interval', 'initiated')

    def __init__(self, subject, required_relationship_bits, prohibited_relationship_bits, track, relationship_score_interval, test_event, initiated=True, **kwargs):
        (super().__init__)(**kwargs)
        if test_event == RelationshipTestEvents.AllRelationshipEvents:
            self.test_events = (
             TestEvent.RelationshipChanged,
             TestEvent.AddRelationshipBit,
             TestEvent.RemoveRelationshipBit)
        else:
            self.test_events = (
             test_event,)
        self.subject = subject
        self.required_relationship_bits = required_relationship_bits
        self.prohibited_relationship_bits = prohibited_relationship_bits
        self.track = track
        self.relationship_score_interval = relationship_score_interval
        self.initiated = initiated

    @cached_test
    def __call__(self, targets=None):
        if not self.initiated:
            return TestResult.TRUE
        if targets is None:
            return TestResult(False, 'Currently Actor-only relationship tests are unsupported, valid on zone load.')
        if self.track is None:
            self.track = singletons.DEFAULT

    def goal_value(self):
        if self.num_relations:
            return self.num_relations
        return 1


class RelationshipTest(BaseRelationshipTest):
    FACTORY_TUNABLES = {'description':'Gate availability by a relationship status.', 
     'target_sim':TunableEnumFlags(description='\n            Target(s) of the relationship(s).\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'test_incest':TunableVariant(description="\n            Test for incest status. Test passes if this matches the two Sim's\n            incest status.\n            ",
       locked_args={'disabled':None, 
      'is incestuous':True, 
      'is not incestuous':False},
       default='disabled'), 
     'track':TunableReference(description='\n            If set, the test will use the relationship score between sims for\n            this track. If unset, the track defaults to the global module\n            tunable REL_INSPECTOR_TRACK.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='RelationshipTrack',
       allow_none=True,
       pack_safe=True), 
     'num_relations':Tunable(description='\n            Number of Sims with specified relationships required to pass,\n            default(0) is all known relations.\n            \n            If value set to 1 or greater, then test is looking at least that\n            number of relationship to match the criteria.\n            \n            If value is set to 0, then test will pass if relationships being\n            tested must match all criteria of the test to succeed.  For\n            example, if interaction should not appear if any relationship\n            contains a relationship bit, this value should be 0.\n            ',
       tunable_type=int,
       default=0), 
     'invert_num_relations':Tunable(description='\n            If checked then we will check that your Num Relations is less than or\n            equal to the value rather than the other way around.\n            ',
       tunable_type=bool,
       default=False)}
    __slots__ = ('target_sim', 'test_incest', 'num_relations', 'invert_num_relations')

    def __init__(self, target_sim, test_incest, num_relations, invert_num_relations, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target_sim = target_sim
        self.test_incest = test_incest
        self.num_relations = num_relations
        self.invert_num_relations = invert_num_relations

    def get_target_id(self, source_sims=None, target_sims=None, id_type=None):
        if source_sims is None or target_sims is None:
            return
        for target_sim in target_sims:
            if target_sim:
                if target_sim.is_sim:
                    if id_type == TargetIdTypes.HOUSEHOLD:
                        return target_sim.household.id
                return target_sim.id

    def get_expected_args(self):
        return {'source_sims':self.subject,  'target_sims':self.target_sim}

    @cached_test
    def __call__(self, source_sims=None, target_sims=None):
        super().__call__(targets=target_sims)
        if self.num_relations:
            use_threshold = True
            threshold_count = 0
            count_it = True
        else:
            use_threshold = False
        target_sim_count = 0
        for sim_a, sim_a_id in self._subjects_id_gen(source_sims, target_sims):
            rel_tracker = sim_a.relationship_tracker
            for sim_b, sim_b_id in self._targets_id_gen(sim_a, target_sims):
                if sim_b is None:
                    continue
                else:
                    target_sim_count += 1
                    rel_score = rel_tracker.get_relationship_score(sim_b_id, self.track)
                    if rel_score is None:
                        logger.error('{} and {} do not have a relationship score in TunableRelationshipTest.', sim_a, sim_b)
                    if rel_score < self.relationship_score_interval.lower_bound or rel_score > self.relationship_score_interval.upper_bound:
                        if use_threshold:
                            count_it = False
                        else:
                            return TestResult(False, 'Inadequate relationship level ({} not within [{},{}]) between {} and {}.', rel_score,
                              (self.relationship_score_interval.lower_bound), (self.relationship_score_interval.upper_bound),
                              sim_a, sim_b, tooltip=(self.tooltip))
                if self.required_relationship_bits.match_any:
                    for bit in self.required_relationship_bits.match_any:
                        if rel_tracker.has_bit(sim_b_id, bit):
                            break
                    else:
                        if use_threshold:
                            count_it = False
                        else:
                            return TestResult(False, 'Missing all of the match_any required relationship bits between {} and {}.', sim_a,
                              sim_b, tooltip=(self.tooltip))

                for bit in self.required_relationship_bits.match_all:
                    if bit is None:
                        return TestResult(False, 'Missing pack, so relationship bit is None.', tooltip=(self.tooltip))
                        if rel_tracker.has_bit(sim_b_id, bit) or use_threshold:
                            count_it = False
                            break
                        else:
                            return TestResult(False, 'Missing relationship bit ({}) between {} and {}.', bit,
                              sim_a, sim_b, tooltip=(self.tooltip))

                if self.prohibited_relationship_bits.match_any:
                    for bit in self.prohibited_relationship_bits.match_any:
                        if rel_tracker.has_bit(sim_b_id, bit):
                            if use_threshold:
                                count_it = False
                                break
                            else:
                                return TestResult(False, 'Prohibited Relationship ({}) between {} and {}.', bit,
                                  sim_a, sim_b, tooltip=(self.tooltip))

                if self.prohibited_relationship_bits.match_all:
                    for bit in self.prohibited_relationship_bits.match_all:
                        if not rel_tracker.has_bit(sim_b_id, bit):
                            break
                    else:
                        if use_threshold:
                            count_it = False
                        else:
                            return TestResult(False, '{} has all  the match_all prohibited bits with {}.', sim_a,
                              sim_b, tooltip=(self.tooltip))

                    if self.test_incest is not None:
                        is_incestuous = not sim_a.incest_prevention_test(sim_b)
                        if is_incestuous != self.test_incest:
                            return TestResult(False, 'Incest test failed. Needed {}.', (self.test_incest),
                              tooltip=(self.tooltip))
                    if use_threshold:
                        if count_it:
                            threshold_count += 1
                        count_it = True

        if not (use_threshold or target_sims == ParticipantType.AllRelationships):
            if target_sim_count > 0:
                return TestResult.TRUE
            return TestResult(False, 'Nothing compared against, target_sims list is empty.')
            if self.invert_num_relations:
                if not threshold_count <= self.num_relations:
                    return TestResultNumeric(False,
                      'Number of relations required not met',
                      current_value=threshold_count,
                      goal_value=(self.num_relations),
                      is_money=False,
                      tooltip=(self.tooltip))
        elif not threshold_count >= self.num_relations:
            return TestResultNumeric(False,
              'Number of relations required not met',
              current_value=threshold_count,
              goal_value=(self.num_relations),
              is_money=False,
              tooltip=(self.tooltip))
        return TestResult.TRUE

    def _subjects_id_gen(self, source_sims, target_sims):
        if source_sims == ParticipantType.AllRelationships:
            for target in target_sims:
                yield from self._all_related_sims_and_id_gen(target)

        else:
            yield from self._all_specified_sims_and_id_gen(source_sims)
        if False:
            yield None

    def _targets_id_gen(self, source_sim, target_sims):
        if self.target_sim == ParticipantType.AllRelationships:
            yield from self._all_related_sims_and_id_gen(source_sim)
        else:
            yield from self._all_specified_sims_and_id_gen(target_sims)
        if False:
            yield None

    def _all_related_sims_and_id_gen(self, source_sim):
        for sim_b_id in source_sim.relationship_tracker.target_sim_gen():
            sim_b = services.sim_info_manager().get(sim_b_id)
            yield (sim_b, sim_b_id)

    def _all_specified_sims_and_id_gen(self, target_sims):
        for sim in target_sims:
            if sim is None:
                yield (None, None)
            else:
                yield (
                 sim, sim.sim_id)


TunableRelationshipTest = TunableSingletonFactory.create_auto_factory(RelationshipTest)

class ScenarioRelationshipTest(HasTunableSingletonFactory, RelationshipTest):
    FACTORY_TUNABLES = {'target_scenario_roles':TunableList(description='\n            A list of scenario roles. The relationship test will target all other\n            sims in the household of the subject sim that have a tuned scenario \n            role.\n            ',
       tunable=TunableReference(description='\n                The scenario role.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
       class_restrictions=('ScenarioRole', )),
       minlength=1), 
     'locked_args':{'target_sim': ParticipantType.TargetSim}}

    def __init__(self, target_scenario_roles, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target_scenario_roles = target_scenario_roles

    def _targets_id_gen(self, source_sim, target_sims):
        scenario_tracker = source_sim.household.scenario_tracker
        if scenario_tracker is None:
            return
        if scenario_tracker.active_scenario is None:
            return
        for sim_info in scenario_tracker.active_scenario.sim_infos_of_interest_gen(roles=(self.target_scenario_roles)):
            if source_sim is sim_info:
                continue
            yield (
             sim_info, sim_info.id)


TunableScenarioRelationshipTest = TunableSingletonFactory.create_auto_factory(ScenarioRelationshipTest)

class ObjectTypeRelationshipTest(HasTunableSingletonFactory, BaseRelationshipTest):
    FACTORY_TUNABLES = {'description':'Gate availability by a relationship status.\n        \n            Note: \n            This is different than the instance-based Object Relationship Component\n            and applies only to the relationships of Object Based Tracks tuned under\n            relationship tracker module tuning.\n            \n            If object rel does not exist, the test will treat the rel_track value \n            with an assumed value of 0 with no rel-bits.\n            ', 
     'target_type':TunableVariant(description='\n            The type of target we want to test the relationship on.  This will\n            either be a tag set (in the case where we want to test rel on \n            uninstantiated objects) or an object.\n            ',
       tag_set=TunableReference(description='\n                Tag set that defines the target objects of the relationship.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TAG_SET)),
       pack_safe=True),
       object=TunableEnumFlags(description='\n                Target Object of the relationship.\n                ',
       enum_type=ParticipantType,
       default=(ParticipantType.Object)),
       default='object'), 
     'track':TunableReference(description='\n            The object relationship track on which to check for bits and threshold values.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='ObjectRelationshipTrack')}
    __slots__ = ('target_type', )

    def __init__(self, target_type, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target_type = target_type

    def get_expected_args(self):
        return {'source_sims':self.subject, 
         'target_type':self.target_type}

    @cached_test
    def __call__(self, source_sims=None, target_type=None):
        if self.target_type == ParticipantType.AllRelationships:
            logger.error('Object Relationships do not support the All Relationships participant. Failed to test against relationship between source:{} and target:{}', source_sims, self.target_type)
            return
        for sim_a in source_sims:
            sim_a_id = sim_a.id
            rel_tracker = self.track
            relationship_service = services.relationship_service()
            if isinstance(self.target_type, ParticipantType):
                target_object = target_type[0]
                obj_tag_set = relationship_service.get_mapped_tag_set_of_id(target_object.definition.id)
                if obj_tag_set is None:
                    logger.error('{} does not have object relationship tuning. Update the object relationship map.', target_object)
                    return TestResult(False, 'Relationship between {} and {} does not exist.', sim_a,
                      target_object, tooltip=(self.tooltip))
            else:
                obj_tag_set = self.target_type
            rel_score = relationship_service.get_object_relationship_score(sim_a_id, obj_tag_set, track=rel_tracker)
            actual_rel = rel_tracker.initial_value if rel_score is None else rel_score
            if actual_rel not in self.relationship_score_interval:
                return TestResult(False, 'Inadequate relationship level ({} not within [{},{}]) between {} and {}.', rel_score,
                  (self.relationship_score_interval.lower_bound), (self.relationship_score_interval.upper_bound),
                  sim_a, (self.target_type), tooltip=(self.tooltip))
            if self.required_relationship_bits.match_any:
                if rel_score is None:
                    return TestResult(False, 'No relationship between {} and {}.', sim_a,
                      (self.target_type), tooltip=(self.tooltip))
                for bit in self.required_relationship_bits.match_any:
                    if relationship_service.has_object_bit(sim_a_id, obj_tag_set, bit):
                        break
                else:
                    return TestResult(False, 'Missing all of the match_any required relationship bits between {} and {}.', sim_a,
                      (self.target_type), tooltip=(self.tooltip))

            for bit in self.required_relationship_bits.match_all:
                if rel_score is None:
                    return TestResult(False, 'No relationship between {} and {}.', sim_a,
                      (self.target_type), tooltip=(self.tooltip))
                    if bit is None:
                        return TestResult(False, 'Missing pack, so relationship bit is None.', tooltip=(self.tooltip))
                    return relationship_service.has_object_bit(sim_a_id, obj_tag_set, bit) or TestResult(False, 'Missing relationship bit ({}) between {} and {}.', bit,
                      sim_a, (self.target_type), tooltip=(self.tooltip))

            if self.prohibited_relationship_bits.match_any:
                if rel_score is not None:
                    for bit in self.prohibited_relationship_bits.match_any:
                        if relationship_service.has_object_bit(sim_a_id, obj_tag_set, bit):
                            return TestResult(False, 'Prohibited Relationship ({}) between {} and {}.', bit,
                              sim_a, (self.target_type), tooltip=(self.tooltip))

            if self.prohibited_relationship_bits.match_all:
                if rel_score is not None:
                    for bit in self.prohibited_relationship_bits.match_all:
                        if not relationship_service.has_object_bit(sim_a_id, obj_tag_set, bit):
                            break

                    return TestResult(False, '{} has all  the match_all prohibited bits with {}.', sim_a,
                      (self.target_type), tooltip=(self.tooltip))
            return TestResult.TRUE


class ComparativeRelationshipTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject_a':TunableEnumFlags(description='\n            Owner(s) of the relationship(s) to be compared with subject_b.\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Actor), 
     'subject_b':TunableEnumFlags(description='\n            Owner(s) of the relationship(s) to be compared with subject_a.\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target':TunableEnumFlags(description='\n            Target of the relationship(s).\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'track':TunableReference(description='\n            The relationship track to compare.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions='RelationshipTrack'), 
     'fallback':TunableVariant(description='\n            The fallback winner in case subjects a and b have the exact same\n            average relationship with the target.\n            ',
       locked_args={'Subject A':True, 
      'Subject B':False},
       default='Subject A'), 
     'expected_result':TunableVariant(description='\n            The expected result of this relationship comparison.\n            ',
       locked_args={'Subject A has higher relationship with target.':True, 
      'Subject B has higher relationship with target.':False},
       default='Subject A has higher relationship with target.')}

    def get_expected_args(self):
        return {'subject_a':self.subject_a, 
         'subject_b':self.subject_b, 
         'target':self.target}

    def get_average_relationship(self, subjects, targets):
        final_rel = 0
        for target_sim in targets:
            rel = 0
            num_subjects = 0
            tracker = target_sim.relationship_tracker
            for subject_sim in subjects:
                if target_sim == subject_sim:
                    continue
                num_subjects += 1
                rel += tracker.get_relationship_score(subject_sim.id, self.track)

            if num_subjects > 0:
                final_rel += rel / num_subjects

        final_rel /= len(targets)
        return final_rel

    @cached_test
    def __call__(self, subject_a=None, subject_b=None, target=None):
        a_average = self.get_average_relationship(subject_a, target)
        b_average = self.get_average_relationship(subject_b, target)
        a_higher = a_average > b_average
        if a_average == b_average:
            if self.fallback:
                a_higher = True
        if not a_higher:
            if self.expected_result:
                return TestResult(False, 'Sims {} expected to have a higher average relationship with Sims {} than Sims {}, but that is not the case.', subject_a, target, subject_b)
        if a_higher:
            if not self.expected_result:
                return TestResult(False, 'Sims {} expected to have a lower average relationship with Sims {} than Sims {}, but that is not the case.', subject_a, target, subject_b)
        return TestResult.TRUE


class RelationshipBitCountTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumFlags(description='\n            Owner of the relationship.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'rel_bit':TunablePackSafeReference(description="\n            The type of relationship we're looking for.\n            \n            In other words, we're looking for any relationship\n            with this Rel Bit.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)), 
     'relationship_count':TunableRange(description="\n            The number of relationships we want to compare against\n            the sim's actual number of relationships.\n            ",
       tunable_type=int,
       minimum=0,
       default=0), 
     'comparison_operator':TunableOperator(description="\n            The operator to use to compare the sim's\n            actual relationship count vs. the tuned\n            Relationship Count.\n            ",
       default=Operator.EQUAL)}

    def get_expected_args(self):
        return {'sim_infos': self.subject}

    @cached_test
    def __call__(self, sim_infos):
        if self.rel_bit is None:
            return TestResult(False, 'Failed relationship bit count test: Rel Bit is not available due to pack-safeness', tooltip=(self.tooltip))
        sim_info_manager = services.sim_info_manager()
        for sim_info in sim_infos:
            rel_tracker = sim_info.relationship_tracker
            actual_rel_count = 0
            for other_sim_info_id in sim_info.relationship_tracker.target_sim_gen():
                other_sim_info = sim_info_manager.get(other_sim_info_id)
                if other_sim_info is None:
                    continue
                if rel_tracker.has_bit(other_sim_info_id, self.rel_bit):
                    actual_rel_count += 1

            threshold = sims4.math.Threshold(self.relationship_count, self.comparison_operator)
            if not threshold.compare(actual_rel_count):
                operator_symbol = Operator.from_function(self.comparison_operator).symbol
                return TestResult(False, 'Failed relationship bit count test: Actual Relationship Count ({}) {} Tuned Relationship Count ({})',
                  actual_rel_count,
                  operator_symbol,
                  (self.relationship_count),
                  tooltip=(self.tooltip))

        return TestResult.TRUE


class RelationshipBitComparisonTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            Owner of the relationships.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'comparison_operator':TunableOperator(description='\n            The operator to use to compare the sim\'s\n            first vs. second relationship count.\n            Will apply as "a [operator] b"\n            \n            For example:\n            "a greater than b" will only pass if more\n            relationships on the subject have bit a\n            than bit b.\n            ',
       default=Operator.EQUAL), 
     'rel_bit_a':TunablePackSafeReference(description='\n            The first relationship bit to look for.\n            Also considered the left hand side of\n            the comparison.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)), 
     'rel_bit_b':TunablePackSafeReference(description='\n            The second relationship bit to look for.\n            Also considered the right hand side of\n            the comparison.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))}

    def get_expected_args(self):
        return {'sim_infos': self.subject}

    @cached_test
    def __call__(self, sim_infos):
        if self.rel_bit_a is None:
            return TestResult(False, 'Failed relationship bit comparison test: Rel Bit A is not available due to pack safety', tooltip=(self.tooltip))
        else:
            if self.rel_bit_b is None:
                return TestResult(False, 'Failed relationship bit comparison test: Rel Bit B is not available due to pack safety', tooltip=(self.tooltip))
            sim_info_manager = services.sim_info_manager()
            if len(sim_infos) > 1:
                logger.error('More than one subject was found. This should not happen. Subjects: {0}'.format(sim_infos))
            sim_info = next(iter(sim_infos))
            rel_tracker = sim_info.relationship_tracker
            rel_count_a = 0
            rel_count_b = 0
            sim_id = sim_info.id
            for relationship in rel_tracker:
                other_sim_info_id = relationship.get_other_sim_id(sim_id)
                other_sim_info = sim_info_manager.get(other_sim_info_id)
                if other_sim_info is None:
                    continue
                if relationship.has_bit(other_sim_info_id, self.rel_bit_a):
                    rel_count_a += 1
                if relationship.has_bit(other_sim_info_id, self.rel_bit_b):
                    rel_count_b += 1

            threshold = sims4.math.Threshold(rel_count_b, self.comparison_operator)
            operator_symbol = threshold.compare(rel_count_a) or Operator.from_function(self.comparison_operator).symbol
            return TestResult(False, 'Failed relationship bit comparison test: A({}) {} B({}) was False.',
              rel_count_a,
              operator_symbol,
              rel_count_b,
              tooltip=(self.tooltip))
        return TestResult.TRUE


class RelationshipBitTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumFlags(description='\n            Owner(s) of the relationship(s) to be compared with subject_b.\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target':TunableEnumFlags(description='\n            Owner(s) of the relationship(s) to be compared with subject_a.\n            ',
       enum_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'relationship_bits':TunableSet(description='\n            Any of these relationship bits will pass the test.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))),
       minlength=1), 
     'test_event':TunableVariant(description='\n            Event to listen to.\n            ',
       locked_args={'Bit Added':TestEvent.AddRelationshipBit, 
      'Bit Removed':TestEvent.RemoveRelationshipBit},
       default='Bit Added')}

    @property
    def test_events(self):
        return (self.test_event,)

    def get_expected_args(self):
        return {'subject':self.subject, 
         'target':self.target, 
         'relationship_bit':event_testing.test_constants.FROM_EVENT_DATA}

    @cached_test
    def __call__(self, subject, target, relationship_bit):
        if relationship_bit not in self.relationship_bits:
            return TestResult(False, 'Event {} did not trigger for bit {} between Sims {} and {}, bits of interest: {}', relationship_bit, subject, target, self.relationship_bits)
        return TestResult.TRUE


class RelationshipModifiedByStatisticTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'description':'\n            Gate availability by combination of relationship tracks and statistics.\n            ', 
     'subject':TunableEnumFlags(description='\n            Owner(s) of the relationship.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.Actor), 
     'target_sim':TunableEnumFlags(description='\n            Target(s) of the relationship.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.TargetSim), 
     'relationship_tracks':TunableList(description='\n            List of the relationship tracks and respective multipliers.\n            ',
       tunable=TunableTuple(track=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions='RelationshipTrack'),
       multiplier=Tunable(tunable_type=float,
       default=1))), 
     'subject_statistics':TunableList(description='\n            List of the statistics and respective multipliers for the subject.\n            ',
       tunable=TunableTuple(statistic=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Commodity', 'RankedStatistic', 'Skill', 'Statistic', 'LifeSkillStatistic')),
       multiplier=Tunable(tunable_type=float,
       default=1))), 
     'target_statistics':TunableList(description='\n            List of the statistics and respective multipliers for the target.\n            ',
       tunable=TunableTuple(statistic=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Commodity', 'RankedStatistic', 'Skill', 'Statistic', 'LifeSkillStatistic')),
       multiplier=Tunable(tunable_type=float,
       default=1))), 
     'score_interval':TunableInterval(description='\n            The range that the score must be within in order for this test to \n            pass.  Min inclusive, max exclusive.\n            Score is sum of all specified statistics and tracks multiplied by \n            their respective multipliers.\n            ',
       tunable_type=float,
       default_lower=0,
       default_upper=1000)}

    def get_expected_args(self):
        return {'source_sims':self.subject, 
         'target_sims':self.target_sim}

    @cached_test
    def __call__(self, source_sims=None, target_sims=None):
        if target_sims is None:
            return TestResult(False, 'Currently Actor-only relationship tests are unsupported, valid on zone load.')
        value = 0
        for sim_a in source_sims:
            rel_tracker = sim_a.relationship_tracker
            for sim_b in target_sims:
                if sim_b is None:
                    continue
                sim_b_id = sim_b.sim_id
                for track_pair in self.relationship_tracks:
                    score = rel_tracker.get_relationship_score(sim_b_id, track_pair.track)
                    if score is not None:
                        value += score * track_pair.multiplier

                value += RelationshipModifiedByStatisticTest._sum_modified_statistics(sim_a, self.subject_statistics)
                value += RelationshipModifiedByStatisticTest._sum_modified_statistics(sim_b, self.target_statistics)
                if not value < self.score_interval.lower_bound:
                    if value >= self.score_interval.upper_bound:
                        return TestResult(False, 'Inadequate statistic modified relationship level ({} not within [{},{}]) between {} and {}.', value,
                          (self.score_interval.lower_bound), (self.score_interval.upper_bound),
                          sim_a, sim_b, tooltip=(self.tooltip))
                return TestResult(True)

        return TestResult(False, 'No valid actor or target in StatisticModifiedRelationshipTest')

    @staticmethod
    def _sum_modified_statistics(sim, statistics):
        value = 0
        for statistic_pair in statistics:
            stat_type = statistic_pair.statistic
            stat_tracker = sim.get_tracker(stat_type)
            if stat_tracker is not None:
                stat = stat_tracker.get_statistic(stat_type) or stat_type
                score = stat.get_user_value() if hasattr(stat, 'get_user_value') else None
                if score is not None:
                    value += score * statistic_pair.multiplier

        return value


class RelationshipTestBasedScore(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumFlags(description='\n            Owner(s) of the relationship.\n            If there are multiple Subjects/Targets, the score is cumulative.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.Actor), 
     'target_sim':TunableEnumFlags(description='\n            Target(s) of the relationship.\n            If there are multiple Subjects/Targets, the score is cumulative.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.TargetSim), 
     'track_score_mappings':TunableList(description='\n            Mappings of relationship track scores to test based scores.\n            ',
       tunable=TunableTuple(track=TunablePackSafeReference(description='\n                    The relationship track that we are getting rel score from.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions='RelationshipTrack'),
       score_mappings=TunableList(tunable=TunableTuple(rel_score_interval=TunableInterval(description='\n                            If the relationship score is within in this range, the \n                            test based score will be added to the total score. \n                            Min inclusive, max exclusive.\n                            ',
       tunable_type=float,
       default_lower=MIN_RELATIONSHIP_VALUE,
       default_upper=MAX_RELATIONSHIP_VALUE,
       minimum=MIN_RELATIONSHIP_VALUE,
       maximum=MAX_RELATIONSHIP_VALUE),
       test_based_score=Tunable(tunable_type=float,
       default=1)))))}

    def get_expected_args(self):
        return {'source_sims':self.subject, 
         'target_sims':self.target_sim}

    @cached_test
    def __call__(self, source_sims=None, target_sims=None):
        if target_sims is None:
            return TestResult(False, 'Currently Actor-only relationship tests are unsupported, valid on zone load.')
        total_score = 0
        for sim_a in source_sims:
            rel_tracker = sim_a.relationship_tracker
            for sim_b in target_sims:
                if sim_b is None:
                    continue
                sim_b_id = sim_b.sim_id
                for track_mapping_pair in self.track_score_mappings:
                    if track_mapping_pair.track is None:
                        continue
                    rel_score = rel_tracker.get_relationship_score(sim_b_id, track_mapping_pair.track)
                    if rel_score is not None:
                        for score_mapping in track_mapping_pair.score_mappings:
                            if score_mapping.rel_score_interval.lower_bound <= rel_score <= score_mapping.rel_score_interval.upper_bound:
                                total_score += score_mapping.test_based_score

        return TestResultNumeric(True, current_value=total_score, goal_value=0)


class CompatibilityLevelTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {'subject':TunableEnumFlags(description='\n            Owner(s) of the relationship.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.Actor), 
     'target_sim':TunableEnumFlags(description='\n            Target(s) of the relationship.\n            ',
       enum_type=ParticipantTypeSingleSim,
       default=ParticipantType.TargetSim), 
     'compatibility_level':TunableEnumEntry(description='\n            The CompatibilityLevel enum to test for.\n            ',
       tunable_type=CompatibilityLevel,
       default=CompatibilityLevel.NEUTRAL)}

    def get_expected_args(self):
        return {'subject':self.subject, 
         'target':self.target_sim}

    @cached_test
    def __call__(self, subject=None, target=None):
        for sim_a in subject:
            rel_tracker_a = sim_a.relationship_tracker
            for sim_b in target:
                if rel_tracker_a.has_relationship(sim_b.sim_id):
                    if self.compatibility_level != rel_tracker_a.get_compatibility_level(sim_b.sim_id):
                        TestResult(False, 'Compatibility level between {} and {} is not {}', subject, target, (self.compatibility_level), tooltip=(self.tooltip))
                    return TestResult.TRUE

        return TestResult(False, 'No Compatibility exists between {} and {} ', subject, target, tooltip=(self.tooltip))