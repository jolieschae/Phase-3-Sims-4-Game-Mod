# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\festival_contest_ops.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 10913 bytes
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import SingleObjectResolver
from interactions import ParticipantType, ParticipantTypeSingleSim
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableList, OptionalTunable, TunableFactory, Tunable, TunableRange, TunableReference, TunableMapping, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
import services, sims4, singletons
logger = sims4.log.Logger('DramaNode', default_owner='msundaram')

class FestivalContestSubmitElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'success_notification_by_rank':TunableList(description='\n            Notifications displayed if submitted object is large enough to be ranked in\n            the contest. Index refers to the place that the player is in currently.\n            1st, 2nd, 3rd, etc.\n            ',
       tunable=UiDialogNotification.TunableFactory(),
       tuning_group=GroupNames.UI), 
     'unranked_notification':OptionalTunable(description='\n            If enabled, notification displayed if submitted object is not large enough to rank in\n            the contest. \n            ',
       tunable=TunableUiDialogNotificationSnippet(description='\n                The notification that will appear when the submitted object does not rank.\n                '),
       tuning_group=GroupNames.UI), 
     'festival_submit_affordance_drama_node_map':TunableMapping(description='\n            map of festival submit picker affordances to festival contest drama node and sub nodes\n            ',
       key_type=TunableReference(description='\n                Reference to the picker affordance running the associated \n                drama node based on picked object.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       allow_none=False),
       value_type=TunableReference(description='\n                A drama node or sub node that we will check against the running \n                festivals for the picker affordance\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)),
       class_restrictions=('FestivalContestDramaNode', 'FestivalContestSubDramaNode')),
       tuning_group=GroupNames.GENERAL), 
     'participant_to_submit':TunableEnumEntry(description='\n            The participant to be used when submitting an object to a competition. This is by default PickedObject as that\n            is what most of the contests expect to use.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.PickedObject)}

    def _do_behavior(self):
        resolver = self.interaction.get_resolver()
        obj = self.interaction.get_participant(self.participant_to_submit)
        picker_affordances = self.interaction.continuation_affordance_chain
        festival_submit_affordance_drama_node_map = self.festival_submit_affordance_drama_node_map
        if obj is None:
            logger.error('{} does not have {} participant', resolver, self.participant_to_submit)
            return False
        sim = self.interaction.sim
        if sim is None:
            logger.error('{} does not have sim participant', resolver)
            return False
        drama_node_for_affordance = None
        if picker_affordances:
            for picker_affordance in picker_affordances:
                if picker_affordance in festival_submit_affordance_drama_node_map:
                    drama_node_for_affordance = festival_submit_affordance_drama_node_map[picker_affordance]
                    break

        running_contests = services.drama_scheduler_service().get_running_nodes_by_drama_node_type(DramaNodeType.FESTIVAL)
        for contest in running_contests:
            if drama_node_for_affordance is not None:
                if drama_node_for_affordance is not type(contest):
                    continue
            if hasattr(contest, 'festival_contest_tuning'):
                if contest.festival_contest_tuning is None:
                    continue
                if contest.is_during_pre_festival():
                    continue
                if self._enter_object_into_contest(contest, sim, obj, resolver):
                    return True

        logger.error('{} no valid active Contest', resolver)
        return False

    def _enter_object_into_contest(self, contest, sim, obj, resolver):
        object_test_resolver = SingleObjectResolver(obj)
        if not contest.festival_contest_tuning._object_tests.run_tests(object_test_resolver):
            return False
        score = contest.festival_contest_tuning._score_method.calculate_score_for_contest(obj_entry=obj, resolver=resolver)
        if score is None:
            return False
        if contest.festival_contest_tuning._destroy_object_on_submit:
            if not self._destroy_object(contest, sim, obj, resolver):
                return False
        self._add_score(contest, sim, obj, resolver, score)
        contest.festival_contest_tuning._score_method.post_submit(obj)
        return True

    def _destroy_object(self, contest, sim, obj, resolver):
        obj.make_transient()
        return True

    def _add_score(self, contest, sim, obj, resolver, score):
        rank = contest.add_score(sim.id, obj.id, score)
        if rank is not None:
            if rank >= len(self.success_notification_by_rank):
                return
            notification = self.success_notification_by_rank[rank]
            dialog = notification(sim, target_sim_id=(sim.id),
              resolver=resolver)
            dialog.show_dialog()
        else:
            if self.unranked_notification is not None:
                dialog = self.unranked_notification(sim, target_sim_id=(sim.id),
                  resolver=resolver)
                dialog.show_dialog()


class FestivalContestAwardWinners(BaseLootOperation):
    FACTORY_TUNABLES = {'skip_if_no_entry': Tunable(description='\n            Skip showing the results if the player did not enter the contest.\n            ',
                           tunable_type=bool,
                           default=False)}

    def __init__(self, *args, skip_if_no_entry=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._skip_if_no_entry = skip_if_no_entry

    def _apply_to_subject_and_target(self, subject, target, resolver):
        running_contests = services.drama_scheduler_service().get_running_nodes_by_drama_node_type(DramaNodeType.FESTIVAL)
        for contest in running_contests:
            if hasattr(contest, 'festival_contest_tuning'):
                if contest.festival_contest_tuning is None:
                    continue
                if contest.is_during_pre_festival():
                    continue
                show_fallback_dialog = contest.has_user_submitted_entry() if self._skip_if_no_entry else True
                contest.award_winners(show_fallback_dialog=show_fallback_dialog)
            return

        logger.error('No festival contest is currently running, cannot award winners')

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        return (BaseLootOperation.get_participant_tunable)('subject', participant_type_enum=ParticipantTypeSingleSim, **kwargs)


class FestivalContestAddScoreMultiplier(BaseLootOperation):
    FACTORY_TUNABLES = {'multiplier':TunableRange(description="\n            The amount that the Sim's score within a contest will be multiplied.\n            ",
       tunable_type=float,
       default=1.0,
       minimum=0), 
     'contest':TunableReference(description='\n            A reference to the contest to add the multiplier to.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.DRAMA_NODE),
       pack_safe=True,
       class_restrictions=('FestivalContestDramaNode', 'MajorOrganizationEventDramaNode',
                           'FestivalContestSubDramaNode'))}

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        return (BaseLootOperation.get_participant_tunable)('subject', participant_type_enum=ParticipantTypeSingleSim, **kwargs)

    def __init__(self, *args, multiplier=1.0, contest=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._multiplier = multiplier
        self._contest = contest

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self._contest is None:
            return
        running_contests = services.drama_scheduler_service().get_running_nodes_by_class(self._contest)
        for contest in running_contests:
            if contest.is_during_pre_festival():
                continue
            contest.add_sim_score_multiplier(subject.sim_id, self._multiplier)
            return

        logger.error('No festival contest of type {} is currently running.  Cannot apply multiplier.')