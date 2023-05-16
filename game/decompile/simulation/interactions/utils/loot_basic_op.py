# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\loot_basic_op.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 16989 bytes
import random, sims4, time
from event_testing.resolver import DoubleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.utils.has_display_text_mixin import HasDisplayTextMixin
from interactions.utils.success_chance import SuccessChance
from objects import ALL_HIDDEN_REASONS
from performance.test_profiling import record_profile_metrics
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableEnumEntry, TunableFactory, OptionalTunable
import interactions, interactions.utils, services, singletons, tag
logger = sims4.log.Logger('LootOperations')
MAXIMUM_LOOT_PARTICIPANTS = 23
with sims4.reload.protected(globals()):
    loot_profile = None

class BaseLootOperation(HasTunableSingletonFactory, HasDisplayTextMixin):
    FACTORY_TUNABLES = {'tests':TunableTestSet(description='\n            The test to decide whether the loot action can be applied.\n            '), 
     'subject_filter_tests':TunableTestSet(description='\n            These tests will be run once per subject. If the subject \n            participant of this loot action resolves to multiple objects, each \n            of those objects will be tested individually. Any subject that \n            fails this test will be ignored by this loot. This will have no \n            effect on whether we consider the loot to have passed testing on\n            on other subjects or targets. We can use this in cases where we \n            want to give loot based on some criteria like "All active household\n            members that are dogs get this loot".\n            \n            These tests will have no effect on "run tests first" as they are\n            only used for participant filtering and not to determine loot \n            success.\n            \n            The resolver used for these tests is a SingleObjectResolver based \n            on subject sim. This means that test should generally be \n            testing against "Actor" and should not assume the presence of \n            additional participants that may be present in the containing loot.\n            Ask a GPE if you have questions.\n            '), 
     'chance':SuccessChance.TunableFactory(description='\n            Percent chance that the loot action will be considered. The\n            chance is evaluated just before running the tests.\n            ')}

    @staticmethod
    def get_participant_tunable(tunable_name, optional=False, description='', participant_type_enum=interactions.ParticipantType, default_participant=interactions.ParticipantType.Actor, invalid_participants=interactions.ParticipantType.Invalid):
        enum_tunable = TunableEnumEntry(description=description, tunable_type=participant_type_enum,
          default=default_participant,
          invalid_enums=invalid_participants)
        if optional:
            return {tunable_name: OptionalTunable(description=description, tunable=enum_tunable)}
        return {tunable_name: enum_tunable}

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        if description is singletons.DEFAULT:
            description = 'The sim(s) the operation is applied to.'
        return (BaseLootOperation.get_participant_tunable)('subject', description=description, **kwargs)

    def __init__(self, *args, subject=interactions.ParticipantType.Actor, target_participant_type=None, advertise=False, tests=None, subject_filter_tests=None, target_filter_tests=None, chance=SuccessChance.ONE, exclusive_to_owning_si=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._advertise = advertise
        self._subject = subject
        self._target_participant_type = target_participant_type
        self._tests = tests
        self._subject_filter_tests = subject_filter_tests
        self._target_filter_tests = target_filter_tests
        self._chance = chance

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self.subject)

    @property
    def advertise(self):
        return self._advertise

    @property
    def tested(self):
        return self._tests is not None

    @property
    def stat(self):
        pass

    def get_stat(self, interaction):
        return self.stat

    @property
    def subject(self):
        return self._subject

    @property
    def target_participant_type(self):
        return self._target_participant_type

    @property
    def chance(self):
        return self._chance

    @property
    def loot_type(self):
        return interactions.utils.LootType.GENERIC

    def test_resolver(self, resolver, ignore_chance=False):
        if not ignore_chance:
            if not self._chance.multipliers:
                if random.random() > self._chance.get_chance(resolver):
                    return False
        else:
            test_result = True
            if self._tests:
                test_result = self._tests.run_tests(resolver)
                if not test_result:
                    return test_result
            if self._chance.multipliers:
                chance = self._chance.get_chance(resolver)
                if ignore_chance:
                    if not chance:
                        return False
                if random.random() > chance:
                    return False
        return test_result

    def _get_display_text_tokens(self, resolver=None):
        if resolver is None:
            return ()
        subject = resolver.get_participant(self._subject)
        if self._target_participant_type is None:
            return (
             subject,)
        target = resolver.get_participant(self._target_participant_type)
        return (subject, target)

    def resolve_participants(self, participant, resolver, filter_tests, resolved_recipient=None):
        if isinstance(participant, tag.Tag):
            if filter_tests:
                logger.error('Filter tests are tuned on a loot operation {} that uses a tag participant. This is not supported for performance reasons.', self)
        else:
            tagged_objects = [obj for obj in services.object_manager().values() if obj.has_tag(participant)]
            yield from tagged_objects
            return
            yield from filter_tests or resolver.get_participants(participant)
            return
        for potential_participant in resolver.get_participants(participant):
            individual_resolver = DoubleObjectResolver(potential_participant, resolved_recipient)
            if not filter_tests.run_tests(individual_resolver):
                continue
            yield potential_participant

    def apply_to_resolver(self, resolver, skip_test=False):
        global loot_profile
        if loot_profile is not None:
            start_time = time.perf_counter()
        elif not skip_test:
            if not self.test_resolver(resolver):
                return (False, None)
        else:
            if loot_profile is not None:
                test_end_time = time.perf_counter()
            target_participant_type = None if self.target_participant_type is interactions.ParticipantType.Invalid else self.target_participant_type
            if self.subject is not None:
                for recipient in self.resolve_participants(self.subject, resolver, self._subject_filter_tests):
                    if target_participant_type is not None:
                        for target_recipient in self.resolve_participants(target_participant_type, resolver, self._target_filter_tests, recipient):
                            self._apply_to_subject_and_target(recipient, target_recipient, resolver)

                    else:
                        self._apply_to_subject_and_target(recipient, None, resolver)

            else:
                if target_participant_type is not None:
                    for target_recipient in self.resolve_participants(target_participant_type, resolver, self._target_filter_tests):
                        self._apply_to_subject_and_target(None, target_recipient, resolver)

                else:
                    self._apply_to_subject_and_target(None, None, resolver)
            if loot_profile is not None:
                resolve_end_time = time.perf_counter()
                test_time = test_end_time - start_time
                resolve_time = resolve_end_time - test_end_time
                loot_name = self.__class__.__name__
                key_name = resolver.profile_metric_key
                resolver_name = type(resolver).__name__
                try:
                    record_profile_metrics(loot_profile, loot_name, resolver_name, key_name, resolve_time, test_time)
                except Exception as e:
                    try:
                        logger.exception('Resetting loot_profile due to an exception {}.', e)
                        loot_profile = None
                    finally:
                        e = None
                        del e

        return (
         True, self._on_apply_completed())

    def _apply_to_subject_and_target(self, subject, target, resolver):
        raise NotImplemented

    def _get_object_from_recipient(self, recipient):
        if recipient is None:
            return
        if recipient.is_sim:
            return recipient.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        return recipient

    def _on_apply_completed(self):
        pass

    def apply_to_interaction_statistic_change_element(self, resolver):
        self.apply_to_resolver(resolver, skip_test=True)


class LootOperationTargetFilterTestMixin:
    FACTORY_TUNABLES = {'target_filter_tests': TunableTestSet(description='\n            As subject filter tests, except per target object. See description\n            of subject filter tests.\n            ')}


class BaseTargetedLootOperation(LootOperationTargetFilterTestMixin, BaseLootOperation):

    @TunableFactory.factory_option
    def target_participant_type_options(description=singletons.DEFAULT, default_participant=interactions.ParticipantType.Invalid, **kwargs):
        if description is singletons.DEFAULT:
            description = 'Participant(s) that subject will apply operations on.'
        return (BaseLootOperation.get_participant_tunable)('target_participant_type', description=description, 
         default_participant=default_participant, **kwargs)