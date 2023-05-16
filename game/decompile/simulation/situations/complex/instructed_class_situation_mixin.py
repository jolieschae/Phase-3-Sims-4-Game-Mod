# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\instructed_class_situation_mixin.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 26948 bytes
import random, enum, services, sims4.log
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from event_testing.test_events import TestEvent
from event_testing.test_variants import TunableSituationJobTest
from interactions import ParticipantType
from sims4.random import pop_weighted
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableTuple, TunableSimMinute, TunableInterval, TunableRange, TunableList, TunableReference, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from situations.bouncer.bouncer import Bouncer
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation_by_definition_or_tags import SituationByTags
from situations.situation_complex import TunableInteractionOfInterest, CommonSituationState
from situations.situation_job import SituationJob
from tunable_multiplier import TestedSum
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
logger = sims4.log.Logger('Instructed Class', default_owner='jdimailig')

class ClassReadyFlags(enum.IntFlags, export=False):
    NONE = 0
    TIME_EXPIRED = 1
    INSTRUCTOR_IN_POSITION = 2


REQUIRED_FLAGS_TO_START_CLASS = ClassReadyFlags.TIME_EXPIRED | ClassReadyFlags.INSTRUCTOR_IN_POSITION

class _PreClassState(CommonSituationState):
    PRE_CLASS_TIMEOUT = 'pre_class_timeout'

    def __init__(self, **kwargs):
        (super().__init__)(**kwargs)
        self._ready_flags = ClassReadyFlags.NONE

    def on_activate(self, reader=None):
        logger.debug('Pre class.')
        super().on_activate(reader)
        self._test_event_register(TestEvent.InteractionStart, self.owner.instructor_in_position_interaction)
        self._create_or_load_alarm((self.PRE_CLASS_TIMEOUT), (self.owner.pre_class_state.time_out),
          (lambda _: self.timer_expired()),
          should_persist=True)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionStart:
            if self.owner.instructor_in_position_interaction is resolver.interaction.affordance:
                if any((sim_info is instructor.sim_info for instructor in self.owner.all_sims_in_job_gen(self.owner.instructor_job))):
                    self._on_interaction_of_interest_complete(sim_info=sim_info, resolver=resolver)

    def _on_interaction_of_interest_complete(self, **kwargs):
        self._ready_flags |= ClassReadyFlags.INSTRUCTOR_IN_POSITION
        self._try_advance_state()

    def timer_expired(self):
        self._ready_flags |= ClassReadyFlags.TIME_EXPIRED
        self._try_advance_state()

    def _try_advance_state(self):
        if self._ready_flags == REQUIRED_FLAGS_TO_START_CLASS:
            if not self.owner.cancel_class_if_no_attendees():
                self.owner.advance_state()

    def _get_role_state_overrides(self, sim, job_type, role_state_type, role_affordance_target):
        return (
         None, self.owner.instructor_staffed_object)


class _PostClassState(CommonSituationState):
    POST_CLASS_TIMEOUT = 'post_class_timeout'

    def on_activate(self, reader=None):
        logger.debug('Post class.')
        super().on_activate(reader)
        self._create_or_load_alarm((self.POST_CLASS_TIMEOUT), (self.owner.post_class_state.time_out),
          (lambda _: self.timer_expired()),
          should_persist=True)

    def timer_expired(self):
        self.owner._self_destruct()


INSTRUCTOR_STAFFED_OBJECT = 'instructor_staffed_object'
TEMP_OBJECT_IDS = 'temporary_object_ids'

class InstructedClassSituationMixin:
    INSTANCE_TUNABLES = {'pre_class_state':TunableTuple(description='\n                Pre Class Situation State.  The instructor will idle on the leader object, \n                and class members will join the situation and idle on their objects.\n \n                In addition to the timeout, the state will wait until instructor \n                has started "instructor_in_position" interaction before advancing state.\n                ',
       situation_state=_PreClassState.TunableFactory(locked_args={'time_out': None}),
       time_out=TunableSimMinute(description='\n                    How long the pre class session will last.\n                    ',
       default=15,
       minimum=1),
       tuning_group=GroupNames.STATE), 
     'post_class_state':TunableTuple(description='\n                The final situation state.  Sims in the class will randomly chat after the class.\n                ',
       situation_state=_PostClassState.TunableFactory(locked_args={'time_out': None}),
       time_out=TunableSimMinute(description='\n                    How long the post class session will last.\n                    ',
       default=15,
       minimum=1),
       tuning_group=GroupNames.STATE), 
     '_class_member_job':SituationJob.TunableReference(description='\n                The situation job for class members.\n                ',
       tuning_group=GroupNames.SITUATION), 
     '_instructor_job':SituationJob.TunableReference(description='\n                The situation job given to instructors when they are teaching the class.\n                ',
       tuning_group=GroupNames.SITUATION), 
     'number_of_npc_class_members':TunableInterval(description='\n            The range of how many NPCs will join the class.\n            ',
       tunable_type=int,
       default_lower=1,
       default_upper=3,
       tuning_group=GroupNames.SITUATION), 
     'member_situation_job_test':TunableSituationJobTest(description='\n            The situation job test to determine whether npc sim should be\n            picked as class member.\n            ',
       tuning_group=GroupNames.SITUATION,
       locked_args={'participant':ParticipantType.Actor, 
      'tooltip':None}), 
     'class_invite_situation_tag_blacklist':SituationByTags.TunableFactory(description='\n            In addition to member_situation_job_test and the job filter to filter out Sims, \n            Sims in situations with any of these tags can not be chosen automatically as NPC class members.\n            This can be used to more easily blacklist Sims without polluting the member situation job test.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'num_picked_sim_participants_for_post_class_loots':TunableRange(description="\n            When awarding loots upon advancing to post class state, a number of class members that participated in the\n            class will be 'chosen' as picked Sims for use in the post class loot.\n            ",
       tunable_type=int,
       default=0,
       minimum=0,
       tuning_group=GroupNames.SITUATION), 
     'picked_sim_weights':TestedSum.TunableFactory(description='\n            When trying to fill picked Sims for post class loots, if there are more Sims than the amount in num picked\n            Sim tuning, this weight will be given on each individual Sim for the weighted random choice.\n            ',
       tuning_group=GroupNames.SITUATION), 
     'post_class_loots':TunableList(description='\n            Loots run on all students of the class that will apply both the payments and any other required behavior \n            such as giving feedback when the class transitions to the post-class state.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True),
       tuning_group=GroupNames.SITUATION), 
     'temporary_object_creation_interactions':TunableInteractionOfInterest(description="\n            If any of these interactions are run and create temporary object, that object will be claimed\n            by the situation and existence of the situation is required to make it exempt from object cleanup behavior\n            during zone load.  For example, this can prevent temporary yoga mats from being kept around a player's\n            home zone.\n            ",
       tuning_group=GroupNames.SITUATION), 
     'instructor_in_position_interaction':TunableReference(description="\n            During pre-class, this is the affordance that the instructor must be starting before class \n            can be considered 'started'.  For yoga, this means the instructor must be on \n            (and not just routing to) the yoga mat.\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions=('SuperInteraction', ),
       tuning_group=GroupNames.SITUATION), 
     'class_member_requirement':OptionalTunable(description='\n            If enabled, this situation will destroy itself if there are no class members in position when class \n            is ready to start.\n            ',
       tunable=TunableTuple(class_member_in_position_interaction=TunableReference(description="\n                    During pre-class, at least one class member must be running this interaction when class 'starts'\n                    otherwise we will end the situation due to having no class members.\n                    ",
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions=('SuperInteraction', )),
       no_class_members_dialog=TunableUiDialogNotificationSnippet(description='\n                    The notification to display if there are no class members in position to start the class.\n                    ')),
       tuning_group=GroupNames.SITUATION)}

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def get_class_member_job(cls):
        return cls._class_member_job

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.pre_class_state.situation_state._tuned_values.job_and_role_changes.items())

    def __init__(self, *arg, **kwargs):
        (super().__init__)(*arg, **kwargs)
        self._instructor_staffed_object = None
        self._temp_object_ids = set()

    def load_situation(self):
        self._set_instructor_staffed_object()
        if self._instructor_staffed_object is None:
            logger.error('Unable to find instructor object for situation. {} will not be loaded.', str(type(self)))
            return False
        self._reclaim_temp_objects_on_load()
        self._register_for_object_creation_interactions()
        return super().load_situation()

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        instructor_staffed_object = self._instructor_staffed_object
        if instructor_staffed_object is not None:
            writer.write_uint64(INSTRUCTOR_STAFFED_OBJECT, instructor_staffed_object.id)
        if self._temp_object_ids:
            writer.write_uint64s(TEMP_OBJECT_IDS, self._temp_object_ids)

    def start_situation(self):
        super().start_situation()
        self._set_instructor_staffed_object()
        if self._check_conflicting_classes():
            return
        self._validate_instructors()
        self._add_npc_class_members()
        self._register_for_object_creation_interactions()
        self._change_state(self.pre_class_state.situation_state())

    def _register_for_object_creation_interactions(self):
        self._register_test_event_for_keys(TestEvent.InteractionComplete, self.temporary_object_creation_interactions.custom_keys_gen())

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            if self.is_sim_info_in_situation(sim_info):
                if resolver(self.temporary_object_creation_interactions):
                    self._handle_temporary_object_creation_interaction(resolver.interaction)
        super().handle_event(sim_info, event, resolver)

    def _handle_temporary_object_creation_interaction(self, interaction):
        created_object = interaction.get_participant(ParticipantType.CreatedObject)
        if created_object is None:
            services.get_zone_situation_manager().remove_sim_from_situation(interaction.sim, self.id)
            return
        self._claim_temporary_object(created_object.id)

    def _reclaim_temp_objects_on_load(self):
        reader = self._seed.custom_init_params_reader
        if reader is None:
            return
        temp_object_ids = self._load_object_ids(reader, TEMP_OBJECT_IDS, claim=True)
        if temp_object_ids is not None:
            self._temp_object_ids = set(temp_object_ids)

    def _claim_temporary_object(self, temp_object_id):
        self._temp_object_ids.add(temp_object_id)
        self._claim_object(temp_object_id)

    def get_sim_filter_gsi_name(self):
        return str(self)

    def _gsi_additional_data_gen(self):
        yield (
         'Instructor Staffed Object', str(self.instructor_staffed_object))

    @property
    def instructor_staffed_object(self):
        return self._instructor_staffed_object

    @property
    def instructor_job(self):
        return self._instructor_job

    def _set_instructor_staffed_object(self):
        reader = self._seed.custom_init_params_reader
        if reader is None:
            default_target_id = self._seed.extra_kwargs.get('default_target_id', None)
        else:
            default_target_id = reader.read_uint64(INSTRUCTOR_STAFFED_OBJECT, None)
        if default_target_id is not None:
            self._instructor_staffed_object = services.object_manager().get(default_target_id)
        if self._instructor_staffed_object is None:
            self._self_destruct()

    def _check_conflicting_classes(self):
        situation_manager = services.get_zone_situation_manager()
        for other_class in situation_manager.get_situations_by_tags(self.tags):
            if other_class is self:
                continue
            if other_class.instructor_staffed_object is self._instructor_staffed_object:
                self._self_destruct()
                return True

        return False

    def _validate_instructors(self):
        lead_instructor = self._get_sim_from_guest_list(self.instructor_job)
        if lead_instructor is None:
            logger.warn('No instructors to lead a yoga class!')
            self._self_destruct()
        return lead_instructor

    def _add_npc_class_members(self):
        sim_info_manager = services.sim_info_manager()
        situation_manager = services.get_zone_situation_manager()
        member_num = self.number_of_npc_class_members.random_int()

        def can_add_npc_sim(sim):
            if sim.is_selectable:
                return False
            for situation in situation_manager.get_situations_sim_is_in(sim):
                if self.class_invite_situation_tag_blacklist.match(situation):
                    return False
                    if Bouncer.are_mutually_exclusive(self.exclusivity, situation.exclusivity):
                        return False

            return True

        candidate_ids = [sim.id for sim in sim_info_manager.instanced_sims_on_active_lot_gen() if can_add_npc_sim(sim)]
        sim_filter_service = services.sim_filter_service()
        filter_result_list = sim_filter_service.submit_filter((self.get_class_member_job().filter), None,
          allow_yielding=False,
          sim_constraints=candidate_ids,
          requesting_sim_info=(services.active_sim_info()),
          gsi_source_fn=(self.get_sim_filter_gsi_name))
        tested_filter_result_list = []
        for filter_result in filter_result_list:
            single_sim_resolver = SingleSimResolver(filter_result.sim_info)
            if single_sim_resolver(self.member_situation_job_test):
                tested_filter_result_list.append(filter_result)

        random_results = []
        if len(tested_filter_result_list) < member_num:
            random_results = tested_filter_result_list
        else:
            random_results = random.sample(tested_filter_result_list, member_num)
        class_job = self.get_class_member_job()
        for filter_result in random_results:
            self.invite_sim_to_job(filter_result.sim_info, class_job)

    def cancel_class_if_no_attendees(self):
        if self.class_member_requirement is None:
            return False
        else:
            class_members = self.all_sims_in_job_gen(self._class_member_job)
            class_members or self._show_no_class_members_notification()
            self._self_destruct()
            return True
        required_affordance = self.class_member_requirement.class_member_in_position_interaction
        for class_member_sim in class_members:
            if class_member_sim.si_state.get_si_by_affordance(required_affordance) is not None:
                return False

        self._show_no_class_members_notification()
        self._self_destruct()
        return True

    def _show_no_class_members_notification(self):
        instructor = next(iter(self.all_sims_in_job_gen(self.instructor_job)), None)
        if instructor is None:
            logger.error("No instructors found during show no class member notification, this shouldn't have happened")
            return
        resolver = SingleSimResolver(instructor.sim_info)
        dialog = self.class_member_requirement.no_class_members_dialog((instructor.sim_info), resolver=resolver)
        dialog.show_dialog()

    def advance_state(self):
        next_state = self.get_next_class_state()
        if next_state is self.post_class_state.situation_state:
            self._distribute_post_class_loots()
        self._change_state(next_state())

    def get_next_class_state(self):
        raise NotImplementedError

    def _on_sim_removed_from_situation_prematurely(self, sim, sim_job):
        super()._on_sim_removed_from_situation_prematurely(sim, sim_job)
        if self.num_of_sims > 0:
            return
        self._self_destruct()

    def _distribute_post_class_loots(self):
        if not self.post_class_loots:
            return
        else:
            class_member_sim_infos = tuple((sim.sim_info for sim in self.all_sims_in_job_gen(self._class_member_job)))
            return class_member_sim_infos or None
        instructor_sim_info = next(iter((sim.sim_info for sim in self.all_sims_in_job_gen(self.instructor_job))), None)
        if instructor_sim_info is None:
            logger.error('There is no instructor to target the loots to.')
            return
        picked_class_members = self._choose_picked_sims(class_member_sim_infos, instructor_sim_info)
        for class_member_sim_info in class_member_sim_infos:
            resolver = DoubleSimResolver(class_member_sim_info, instructor_sim_info)
            resolver.set_additional_participant(ParticipantType.Listeners, (instructor_sim_info,))
            if class_member_sim_info in picked_class_members:
                resolver.set_additional_participant(ParticipantType.PickedSim, (class_member_sim_info,))
            else:
                resolver.set_additional_participant(ParticipantType.PickedSim, ())
            for post_class_loot in self.post_class_loots:
                post_class_loot.apply_to_resolver(resolver)

    def _choose_picked_sims(self, class_member_sim_infos, instructor_sim_info):
        num_to_pick = self.num_picked_sim_participants_for_post_class_loots
        if num_to_pick == 0:
            return ()
        if len(class_member_sim_infos) <= num_to_pick:
            return tuple(class_member_sim_infos)
        weighted_list = []
        for class_member_sim_info in class_member_sim_infos:
            resolver = DoubleSimResolver(class_member_sim_info, instructor_sim_info)
            weighted_list.append((self.picked_sim_weights.get_modified_value(resolver), class_member_sim_info))

        picked_members = tuple((pop_weighted(weighted_list) for _ in range(num_to_pick)))
        return picked_members


lock_instance_tunables(InstructedClassSituationMixin, exclusivity=(BouncerExclusivityCategory.INSTRUCTED_CLASS))