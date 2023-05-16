# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\reveal_situation.py
# Compiled at: 2021-05-04 14:46:32
# Size of source mod 2**32: 9408 bytes
import services, sims4
from sims.sim_info_types import Species
from sims4.tuning.tunable import TunableReference
from sims4.tuning.tunable_base import GroupNames
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.complex.group_waypoint_situation import GroupWaypointSituation, _GroupWaypointStartState, _GroupWaypointInteractState, _GroupWaypointRouteState, _StartSoloSituationState
from situations.situation_complex import SituationStateData, SituationComplexCommon, TunableSituationJobAndRoleState, CommonInteractionStartedSituationState
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from socials.formation_group import FormationSocialGroup
logger = sims4.log.Logger('Reveal Situation', default_owner='shipark')

class _PreFormationGroupState(CommonInteractionStartedSituationState):

    def _on_interaction_of_interest_started(self):
        self.owner.continue_to_start_state()


class _PostRevealState(CommonInteractionStartedSituationState):

    def on_leader_sim_removed_from_social_group(self):
        pass


class RevealSituation(GroupWaypointSituation):
    INSTANCE_TUNABLES = {'pre_formation_group_state':_PreFormationGroupState.TunableFactory(description='\n            State that runs before the Starting State and gives time for the sims\n            to get into the formation social group.\n            ',
       display_name='0. Pre Formation Group State',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'post_reveal_state':_PostRevealState.TunableFactory(description='\n            State that runs after the Sims have finished viewing the \n            gig-objects.\n            ',
       display_name='5. Post Reveal State',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'decorator_career':TunableReference(manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       tuning_group=GroupNames.SITUATION), 
     'non_member_job_and_role':TunableSituationJobAndRoleState(description='\n            The job and role state for the sims not included in the social group.\n            ')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._social_group_on_start = False

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        jobs_and_roles = super()._get_tuned_job_and_default_role_state_tuples()
        jobs_and_roles.append((cls.non_member_job_and_role.job, cls.non_member_job_and_role.role_state))
        return jobs_and_roles

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _PreFormationGroupState, factory=(cls.pre_formation_group_state)),
         SituationStateData(2, _GroupWaypointStartState, factory=(cls.starting_state)),
         SituationStateData(3, _GroupWaypointRouteState, factory=(cls.route_state)),
         SituationStateData(4, _GroupWaypointInteractState, factory=(cls.interact_state)),
         SituationStateData(5, _PostRevealState, factory=(cls.post_reveal_state)),
         SituationStateData(6, _StartSoloSituationState))

    def on_completed(self):
        self._change_state(self.post_reveal_state())

    def on_anchor_route_fail(self):
        reveal_goal = self.get_main_goal()
        for goal in self._goal_tracker.all_goals_gen():
            if goal.guid64 == reveal_goal.guid64:
                goal.force_complete()
                break

        self._change_state(self.post_reveal_state())

    def start_situation(self):
        super().start_situation()
        self._change_state(self.pre_formation_group_state())

    def on_sim_removed_from_social_group(self, sim, finishing_type):
        pass

    def _initialize_social_group(self):
        host = self.guest_list.host_sim
        if host is None:
            logger.error('No host sim for RevealSituation._initialize_social_group()')
            return False
        social_group = host.get_main_group()
        if social_group is not None:
            if isinstance(social_group, FormationSocialGroup):
                social_group.set_situation(self)
                self._social_group = social_group
        return True

    @classmethod
    def get_predefined_guest_list(cls):
        sim_info = services.active_sim_info()
        guest_list = SituationGuestList(host_sim_id=(sim_info.id), invite_only=True)
        decorator_career = sim_info.career_tracker.get_career_by_uid(cls.decorator_career.guid64)
        if decorator_career is None:
            logger.error('Attempting to create a Reveal Situation, but the active sim {} does not have career {}', sim_info, cls.career)
            return guest_list
        else:
            current_gig = decorator_career.get_current_gig()
            customer_id = current_gig.get_gig_customer()
            if not customer_id:
                logger.error('Attempting to create a Reveal Situation, but there are no client Sims set on the gig for Sim: {}.', sim_info)
                return guest_list
                customer = services.sim_info_manager().get(customer_id)
                if customer is None:
                    logger.error('Attempting to create a Reveal Situation, but the customer id set on the gig for Sim: {} is not a valid id.', sim_info)
                    return guest_list
                customer_household = customer.household
                guest_list.add_guest_info(SituationGuestInfo(sim_info.sim_id, cls.leader_job_and_role.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
                if current_gig.is_commercial_gig:
                    guest_list.add_guest_info(SituationGuestInfo(customer_id, cls.member_job_and_role.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
            else:
                for hh_member in customer_household:
                    if not hh_member.is_toddler_or_younger:
                        if hh_member.species != Species.HUMAN:
                            guest_list.add_guest_info(SituationGuestInfo(hh_member.sim_id, cls.non_member_job_and_role.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
                            continue
                        guest_list.add_guest_info(SituationGuestInfo(hh_member.sim_id, cls.member_job_and_role.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))

        return guest_list