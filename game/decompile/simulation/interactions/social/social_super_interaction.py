# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\social\social_super_interaction.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 95941 bytes
from animation.posture_manifest_constants import ADJUSTMENT_CONSTRAINT
from autonomy.autonomy_modes_tuning import AutonomyModesTuning
from distributor.shared_messages import IconInfoData
from event_testing import test_events
from event_testing.resolver import DoubleSimResolver
from event_testing.results import TestResult
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, TargetType, PipelineProgress, ParticipantTypeActorTargetSim, ParticipantTypeSingle
from interactions.base.basic import StagingContent, FlexibleLengthContent
from interactions.base.interaction_constants import InteractionQueuePreparationStatus
from interactions.base.super_interaction import SuperInteraction
from interactions.constraints import Anywhere, Constraint, Nowhere, GEOMETRY_INCOMPATIBLE_ANYWHERE
from interactions.context import QueueInsertStrategy, InteractionContext
from interactions.interaction_finisher import FinishingType
from interactions.liability import Liability
from interactions.priority import can_displace, Priority
from interactions.social import SocialInteractionMixin
from interactions.social.greeting_socials import greetings
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.outcome import TunableOutcome
from interactions.utils.satisfy_constraint_interaction import SatisfyConstraintSuperInteraction
from interactions.utils.tunable_icon import TunableIcon
from objects.base_interactions import JoinInteraction, ProxyInteraction
from postures import DerailReason, PostureTrack
from primitives.routing_utils import estimate_distance_between_points
from sims.outfits.outfit_enums import OutfitCategory
from sims.sim import LOSAndSocialConstraintTuning
from sims.sim_info_types import Age
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableTuple, TunableMapping, TunableEnumEntry, Tunable, OptionalTunable, TunableVariant, TunableReference, TunableRange, TunableList
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod, classproperty
from singletons import EMPTY_SET
from socials.group import get_fallback_social_constraint_position
from socials.jig_group import JigGroup
import alarms, assertions, autonomy.autonomy_modes, autonomy.autonomy_util, autonomy.content_sets, caches, clock, interactions.aop, interactions.context, services, sims.sim, sims4.localization, sims4.log, sims4.tuning.tunable
logger = sims4.log.Logger('Socials')

class SocialCompatibilityMixin:

    @caches.cached()
    def test_constraint_compatibility(self):
        with autonomy.autonomy_util.AutonomyAffordanceTimes.profile_section(autonomy.autonomy_util.AutonomyAffordanceTimes.AutonomyAffordanceTimesType.COMPATIBILITY):
            incompatible_sims = set()
            included_sis = set()
            for required_sim in self.required_sims():
                participant_type = self.get_participant_type(required_sim)
                if participant_type is None:
                    logger.error('Required Sim, {}, is not participant in {} when trying to check constraint compatibility.', required_sim,
                      self,
                      owner='jjacobson')
                    return (False, incompatible_sims, included_sis)
                if participant_type == ParticipantType.TargetSim:
                    if self.target_type == TargetType.OBJECT:
                        continue
                for si in required_sim.si_state.all_guaranteed_si_gen(self.priority, self.group_id):
                    if self.super_affordance_klobberers is not None:
                        if self.super_affordance_klobberers(si.affordance):
                            continue
                        else:
                            si_participant_type = si.get_participant_type(required_sim)
                            if bool(participant_type in ParticipantTypeSingle) != bool(si_participant_type in ParticipantTypeSingle):
                                continue
                            required_sim.si_state.are_sis_compatible(self, si, participant_type_a=participant_type, participant_type_b=si_participant_type,
                              for_sim=required_sim) or incompatible_sims.add(required_sim)
                            if required_sim is not self.sim:
                                break
                            else:
                                if required_sim is self.sim:
                                    included_sis.add(si)
                                    if required_sim in incompatible_sims:
                                        continue
                        owned_posture = required_sim.posture_state.get_source_or_owned_posture_for_si(si)
                        if owned_posture is None:
                            continue
                        if owned_posture.track != PostureTrack.BODY:
                            continue
                        source_interaction = owned_posture.source_interaction
                        if source_interaction is None or source_interaction.is_finishing:
                            continue
                        required_sim.si_state.are_sis_compatible(self, source_interaction, participant_type_a=participant_type, participant_type_b=si_participant_type,
                          for_sim=required_sim) or incompatible_sims.add(required_sim)
                        if required_sim is not self.sim:
                            break

            for si in self.sim.si_state:
                if si in included_sis:
                    continue
                if self.sim.si_state.are_sis_compatible(self, si, participant_type_b=(si.get_participant_type(self.sim))):
                    included_sis.add(si)

            if incompatible_sims:
                return (
                 False, incompatible_sims, included_sis)
            return (True, None, included_sis)

    def estimate_distance(self):
        target = self.target
        if target is not None:
            if not target.is_connected(self.sim):
                return (
                 None, False, EMPTY_SET)
        constraint = self.constraint_intersection()
        posture_change = False
        si_constraint_sim = self.sim.posture_state.constraint_intersection
        posture_constraint_sim = self.sim.posture_state.posture_constraint
        constraint_sim = si_constraint_sim.intersect(posture_constraint_sim)
        if not constraint.intersect(constraint_sim).valid:
            posture_change = True
        else:
            target_sim = self.get_participant(ParticipantType.TargetSim)
            if target_sim is not None:
                si_constraint_target = target_sim.posture_state.constraint_intersection
                posture_constraint_target = target_sim.posture_state.posture_constraint
                constraint_target = si_constraint_target.intersect(posture_constraint_target)
                if not constraint.intersect(constraint_target).valid:
                    posture_change = True
        compatible, _, included_sis = self.test_constraint_compatibility()
        estimate = 0 if compatible else None
        return (estimate, posture_change, included_sis)

    def get_sims_with_invalid_paths(self):
        valid, incompatible_sims, _ = self.test_constraint_compatibility()
        if not valid:
            return incompatible_sims
        target_sim = self.get_participant(ParticipantType.TargetSim)
        if target_sim is None:
            return set()
        position, _ = get_fallback_social_constraint_position(self.sim, target_sim, self)
        if position is not None:
            return set()
        return {self.sim}


INTENDED_POSITION_LIABILITY = 'IntendedPositionLiability'

class IntendedPositionLiability(Liability):

    def __init__(self, interaction, sim, **kwargs):
        (super().__init__)(**kwargs)
        self._interaction = interaction
        self._sim_ref = sim.ref()
        sim.routing_component.on_intended_location_changed.append(self._on_intended_location_changed)

    @property
    def _sim(self):
        return self._sim_ref()

    def _on_intended_location_changed(self, *args, **kwargs):
        if self._sim is not None:
            if self._on_intended_location_changed in self._sim.routing_component.on_intended_location_changed:
                self._sim.routing_component.on_intended_location_changed.remove(self._on_intended_location_changed)
        self._interaction.cancel(FinishingType.CONDITIONAL_EXIT, 'TargetSim intended position changed.')

    def release(self):
        super().release()
        if self._sim is not None:
            if self._on_intended_location_changed in self._sim.routing_component.on_intended_location_changed:
                self._sim.routing_component.on_intended_location_changed.remove(self._on_intended_location_changed)


class SocialSuperInteraction(SocialInteractionMixin, SocialCompatibilityMixin, SuperInteraction):
    SKINNY_DIP_SAFEGUARD_INTERACTION = TunableReference(description='\n        An affordance that gets pushed before every Social Super Interaction.\n        This is a safeguard that prevents naked adult Sims from deliberately\n        interacting with child Sims without an outfit change. The interaction\n        should test the target and do nothing except change the Sims outfit to\n        swimwear.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)))
    INSTANCE_TUNABLES = {'affordance_to_push_on_target':TunableVariant(description='\n            Affordance to push on the target sim.\n            ',
       push_self_or_none=Tunable(description='\n                If true will push this affordance on the target sim, else push\n                None\n                ',
       tunable_type=bool,
       default=True),
       push_affordance=sims4.tuning.tunable.TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       default='push_self_or_none',
       tuning_group=GroupNames.SOCIALS), 
     'additional_social_to_run_on_both':OptionalTunable(TunableReference(description="\n                Another SocialSuperInteraction to run on both Sims as part of\n                entering this social. All touching socials should reference a\n                non-touching social to run that is responsible for handling\n                exit conditions so the Sims aren't locked into a touching\n                formation at all times.\n                ",
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
       tuning_group=GroupNames.SOCIALS), 
     '_social_group_type':TunableReference(description='\n            The type of social group to use for this interaction and related\n            interactions.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SOCIAL_GROUP),
       tuning_group=GroupNames.SOCIALS), 
     '_update_social_geometry_if_target_moves':Tunable(description="\n            If True, the social group will account for changes in the positon of\n            the target sim that occur after this interaction was queued. If\n            false, social group constraints can be based on stale target\n            positions. This can in some situations cause the target of a social\n            to route to meet the social's constraints even when they should be\n            the focus. In general, we don't care about this and enabling this\n            option can have a penalty on performance.\n            ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     '_social_group_participant_slot_overrides':OptionalTunable(description='\n            Overrides for the slot index mapping on the jig keyed by\n            participant type. Note: This only works with Jig Social Groups.\n            ',
       tunable=TunableMapping(description='\n                Overrides for the slot index mapping on the jig keyed by\n                participant type. Note: This only works with Jig Social Groups.\n                ',
       key_type=(TunableEnumEntry(ParticipantType, ParticipantType.Actor)),
       value_type=Tunable(description='\n                    The slot index for the participant type.\n                    ',
       tunable_type=int,
       default=0)),
       tuning_group=GroupNames.SOCIALS), 
     '_social_group_leader_override':OptionalTunable(description='\n            If enabled, you can override the sim participant who will be the\n            leader of the social group.  If the leader leaves the group the\n            group will be shutdown.\n            ',
       tunable=TunableEnumEntry(description='\n                The leader of the social group.\n                ',
       tunable_type=ParticipantTypeActorTargetSim,
       default=(ParticipantTypeActorTargetSim.Actor)),
       tuning_group=GroupNames.SOCIALS), 
     'listen_animation':TunableAnimationReference(description='\n            The animation for a Sim to play while running this\n            SocialSuperInteraction and waiting to play a reactionlet.\n            ',
       allow_none=True,
       tuning_group=GroupNames.SOCIALS), 
     'multi_sim_override_data':OptionalTunable(TunableTuple(description='\n                Override data that gets applied to interaction if social group\n                size meets threshold.\n                ',
       threshold=TunableRange(description='\n                    Size of group before display name and icon for interaction\n                    queue will be replaced.  If the group size is larger than\n                    threshold then icon and/or text will be replaced.\n                    ',
       tunable_type=int,
       default=2,
       minimum=1),
       display_text=TunableLocalizedStringFactory(description="\n                    Display text of target of mixer interaction.  Example: Sim\n                    A queues 'Tell Joke', Sim B will see in their queue 'Be\n                    Told Joke'\n                    ",
       default=None),
       icon=TunableIcon(description='\n                    Icon to display if social group becomes larger than\n                    threshold.\n                    ')),
       tuning_group=GroupNames.UI), 
     'outcome':TunableOutcome(allow_social_animation=True,
       allow_route_events=True,
       tuning_group=GroupNames.CORE), 
     'ignores_greetings':Tunable(description="\n            If True, this interaction will not trigger any greetings. This is\n            necessary for actual greeting interactions that may recursively\n            push themselves, or any other interactions that we don't want\n            greetings on.\n            ",
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.SOCIALS), 
     'preserve_group_jig_polygon':Tunable(description='\n            If True, this interaction will preserve the jig polygon of its social\n            group and hold it until exiting the pipeline. This can be used to keep\n            the footprint up even after social group become inactive.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SOCIALS), 
     'must_run_target_si':Tunable(description='\n            If True, this interaction must run the push affordance on target SI. In certain cases, like pushing \n            a continuation to a social but retaining the same social group, it is possible for the target Sim \n            to avoid pushing the their target SI, causing invalid positioning for the target Sim.\n            Setting this to True will ensures that the target SI is run for the target Sim.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'tested_social_group_type':OptionalTunable(description='\n            If enabled, we choose the first entry whose tests pass as the\n            social group of this interaction. If no test pass we will \n            fallback to use "Social Group Type" as default.\n            \n            We cache the tested social group at the beginning of the interaction,\n            so please note we won\'t change social group even after condition changed\n            during the lifespan of this interaction.\n            ',
       tunable=TunableList(description='\n                A list of social group types to test. The first entry whose\n                tests pass will be chosen as the social group of this interaction.\n                ',
       tunable=TunableTuple(social_group_type=TunableReference(description='\n                        The type of social group to use for this interaction and related\n                        interactions if tests pass.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.SOCIAL_GROUP))),
       tests=TunableTestSet(description='\n                        The first entry whose tests pass will be chosen as the social group\n                        of this interaction.\n                        '))),
       tuning_group=GroupNames.SOCIALS)}

    def __init__(self, *args, initiated=True, social_group=None, source_social_si=None, set_work_timestamp=False, **kwargs):
        (super().__init__)(args, initiated=initiated, set_work_timestamp=set_work_timestamp, **kwargs)
        self._initiated = initiated
        self._target_si = None
        self._target_si_test_result = True
        self._social_group = social_group
        self._source_social_si = source_social_si
        self._waiting_start_time = None
        self._waiting_alarm = None
        self._go_nearby_interaction = None
        self._greeting_interaction = None
        self._last_go_nearby_time = None
        self._trying_to_go_nearby_target = False
        self._target_was_going_far_away = False
        self._preserved_group_jig_polygon = None
        self.last_social_group = None
        self._processing_social_group_change = False
        self._processing_notify_queue_head = False
        self._cached_social_group_type = None

    @property
    def target_sim(self):
        return self.get_participant(ParticipantType.TargetSim)

    @property
    def social_group_leader_override(self):
        return self._social_group_leader_override

    def get_source_social_kwargs(self):
        return {'saved_participants': self._saved_participants}

    def get_queued_mixers(self):
        return [mixer for mixer in self.sim.queue.mixer_interactions_gen() if mixer.super_affordance.get_interaction_type() is self.get_interaction_type()]

    def _greet_sim(self, target_sim, social_group):
        if self._greeting_interaction is not None:
            if self._greeting_interaction.is_finishing:
                self._greeting_interaction = None
            else:
                mixer_interactions = self.get_queued_mixers()
                should_greet = True
                if not self.ignores_greetings:
                    if self._greeting_interaction is not None or any((mixer.ignores_greetings for mixer in mixer_interactions)):
                        should_greet = False
                    should_play_targeted_greeting = True
                    for target_social_group in target_sim.get_groups_for_sim_gen():
                        if social_group is target_social_group and sum((1 for group_sim in target_social_group if group_sim is not self.sim)) > 1:
                            should_play_targeted_greeting = False
                            break

                    actor_greeting_resolver = DoubleSimResolver(self.sim.sim_info, target_sim.sim_info)
                    result = False
                    rel_tracker = self.sim.sim_info.relationship_tracker
                    if should_play_targeted_greeting:
                        if not rel_tracker.has_bit(target_sim.sim_info.sim_id, greetings.Greetings.GREETED_RELATIONSHIP_BIT):
                            if should_greet:
                                source_interaction = mixer_interactions[0] if mixer_interactions else self
                                greetings.add_greeted_rel_bit(self.sim.sim_info, target_sim.sim_info)
                                result = greetings.try_push_targeted_greeting_for_sim((self.sim), target_sim, actor_greeting_resolver, source_interaction=source_interaction)
                else:
                    result = False
        else:
            interaction_parameters = {}
            for target_social_group in target_sim.get_groups_for_sim_gen():
                if social_group is target_social_group:
                    picked_sim_ids = set()
                    for group_sim in target_social_group:
                        if group_sim is self.sim:
                            continue

                    interaction_parameters['picked_item_ids'] = frozenset(picked_sim_ids)

            if should_greet:
                if picked_sim_ids:
                    source_interaction = mixer_interactions[0] if mixer_interactions else self
                    result = (greetings.try_push_group_greeting_for_sim)(self.sim, target_sim, actor_greeting_resolver, source_interaction=source_interaction, **interaction_parameters)
                else:
                    result = False
            elif result:
                result.interaction.is_finishing or self._interactions.add(result.interaction)
                self._greeting_interaction = result.interaction
                return result
            return result

    def _get_close_to_target_and_greet(self, force=False):
        now = services.time_service().sim_now
        if self._last_go_nearby_time is not None:
            minimum_delay_between_attempts = LOSAndSocialConstraintTuning.minimum_delay_between_route_nearby_attempts
            if now - self._last_go_nearby_time < clock.interval_in_sim_minutes(minimum_delay_between_attempts):
                return False
        self._last_go_nearby_time = now
        if self._trying_to_go_nearby_target:
            return False
        if self._target_was_going_far_away:
            return False
        if self._go_nearby_interaction is not None:
            if not self._go_nearby_interaction.is_finishing:
                return False
        target_sim = self.target_sim
        if target_sim is None:
            return False
        social_group = self._get_social_group_for_this_interaction()
        if social_group is not None:
            if not social_group.can_get_close_and_wait(self.sim, target_sim):
                return False
        if self._greet_sim(target_sim, social_group):
            force = True
        self._trying_to_go_nearby_target = True
        try:
            result = None
            if self._go_nearby_interaction is not None:
                transition_failed = self._go_nearby_interaction.transition_failed
                self._interactions.discard(self._go_nearby_interaction)
                self._go_nearby_interaction = None
                if transition_failed:
                    self.sim.add_lockout(target_sim, AutonomyModesTuning.LOCKOUT_TIME)
                    self.cancel(FinishingType.TRANSITION_FAILURE, 'SocialSuperInteraction: Failed to _get_close_to_target_and_greet.')
                return False
            if target_sim.intended_location is not None:
                try:
                    distance_to_intended = estimate_distance_between_points(target_sim.position, target_sim.routing_surface, target_sim.intended_location.transform.translation, target_sim.intended_location.routing_surface)
                except:
                    return False
                else:
                    if distance_to_intended is not None:
                        if distance_to_intended > LOSAndSocialConstraintTuning.maximum_intended_distance_to_route_nearby:
                            target_running = target_sim.queue.running
                            if not target_running is None:
                                if can_displace(self, target_running):
                                    self._target_was_going_far_away = True
                                    return False
                    target_sim_position = target_sim.intended_location.transform.translation
                    target_sim_routing_surface = target_sim.intended_location.routing_surface
            else:
                target_sim_position = target_sim.position
                target_sim_routing_surface = target_sim.routing_surface
            if not force:
                distance = (self.sim.position - target_sim_position).magnitude()
                if distance < LOSAndSocialConstraintTuning.constraint_expansion_amount:
                    if target_sim.can_see(self.sim):
                        return False
            sim_posture = self.sim.posture_state.body
            if sim_posture.multi_sim:
                if sim_posture.linked_sim is target_sim:
                    return False
            constraint_cone = greetings.GreetingsSatisfyContraintTuning.CONE_CONSTRAINT.create_constraint((self.sim), target_sim,
              target_position=target_sim_position,
              target_forward=(target_sim.intended_forward),
              routing_surface=target_sim_routing_surface)
            constraint_facing = interactions.constraints.Facing(target_sim, target_position=target_sim_position, facing_range=(sims4.math.PI / 2.0))
            constraint_los = target_sim.los_constraint
            total_constraint = constraint_cone.intersect(constraint_facing).intersect(constraint_los)
            total_constraint = total_constraint.intersect(ADJUSTMENT_CONSTRAINT)
            if not total_constraint.valid:
                return False
            context = InteractionContext((self.sim), (InteractionContext.SOURCE_SCRIPT),
              (self.priority),
              insert_strategy=(QueueInsertStrategy.FIRST),
              cancel_if_incompatible_in_queue=True,
              must_run_next=True)
            result = self.sim.push_super_affordance(SatisfyConstraintSuperInteraction, None, context, constraint_to_satisfy=total_constraint,
              allow_posture_changes=True,
              set_work_timestamp=False,
              name_override='WaitNearby')
            interaction = result.interaction if result else None
            if interaction is None or interaction.is_finishing:
                return False
            intended_position_liability = IntendedPositionLiability(interaction, target_sim)
            interaction.add_liability(INTENDED_POSITION_LIABILITY, intended_position_liability)
            self._go_nearby_interaction = interaction
            self._interactions.add(interaction)
            return True
        finally:
            self._trying_to_go_nearby_target = False

    def _cancel_waiting_alarm(self):
        self._waiting_start_time = None
        if self._waiting_alarm is not None:
            alarms.cancel_alarm(self._waiting_alarm)
            self._waiting_alarm = None
        if self._go_nearby_interaction is not None:
            self._go_nearby_interaction.cancel(FinishingType.SOCIALS, 'Canceled')
            self._interactions.discard(self._go_nearby_interaction)
            self._go_nearby_interaction = None

    def _check_target_status(self, *args, **kwargs):
        if self.pipeline_progress > PipelineProgress.QUEUED:
            self._cancel_waiting_alarm()
            return
        now = services.time_service().sim_now
        maximum_wait_time = self.maximum_time_to_wait_for_other_sims
        if now - self._waiting_start_time > clock.interval_in_sim_minutes(maximum_wait_time):
            self.cancel(FinishingType.INTERACTION_INCOMPATIBILITY, 'Timeout due to incompatibility.')
            self._cancel_waiting_alarm()
        self._get_close_to_target_and_greet()

    def _create_route_nearby_check_alarm(self):
        if self._waiting_alarm is None:
            self._waiting_start_time = services.time_service().sim_now
            route_nearby_frequency = LOSAndSocialConstraintTuning.incompatible_target_sim_route_nearby_frequency
            self._waiting_alarm = alarms.add_alarm(self, (clock.interval_in_sim_minutes(route_nearby_frequency)), (self._check_target_status), repeating=True)
            self._get_close_to_target_and_greet(force=(self.sim.posture.mobile))

    def on_incompatible_in_queue(self):
        super().on_incompatible_in_queue()
        if self.sim in self.get_sims_with_invalid_paths():
            return
        self._create_route_nearby_check_alarm()

    def _on_target_intended_location_changed_callback(self, _):
        if self._social_group is not None:
            self._social_group.refresh_social_geometry(self.target)

    @flexmethod
    def _get_social_group_for_sim(cls, inst, sim, actor=None, target=None):
        inst_or_cls = inst if inst is not None else cls
        for social_group in sim.get_groups_for_sim_gen():
            if type(social_group) is inst_or_cls._get_social_group_type(actor=actor, target=target):
                if social_group.has_been_shutdown:
                    continue
                return social_group

    @flexmethod
    def _get_social_group_type(cls, inst, actor=None, target=None):
        if inst is not None:
            if inst._cached_social_group_type is not None:
                return inst._cached_social_group_type
            actor_sim = inst.sim
            target_sim = inst.target_sim
        else:
            actor_sim = actor
            target_sim = target
        inst_or_cls = inst if inst is not None else cls
        if inst_or_cls.tested_social_group_type is not None:
            if actor_sim is not None:
                if target_sim is not None:
                    resolver = DoubleSimResolver(actor_sim.sim_info, target_sim.sim_info)
                    for entry in inst_or_cls.tested_social_group_type:
                        if entry.tests.run_tests(resolver):
                            if inst is not None:
                                inst._cached_social_group_type = entry.social_group_type
                            return entry.social_group_type

        if inst is not None:
            inst._cached_social_group_type = inst._social_group_type
        return inst_or_cls._social_group_type

    @flexmethod
    def _test(cls, inst, target, context, initiated=True, join=False, **kwargs):
        if target is context.sim:
            return TestResult(False, 'Cannot run a social as a self interaction.')
            if target is None:
                return TestResult(False, 'Cannot run a social with no target.')
            if target.is_sim:
                if target.socials_locked:
                    return TestResult(False, 'Cannot socialize with a Sim who has socials_locked set to true. This Sim is leaving the lot.')
            if context.source == context.SOURCE_AUTONOMY:
                sim = inst.sim if inst is not None else context.sim
                social_group = cls._get_social_group_for_sim(sim, actor=sim, target=target)
                if social_group is not None and target in social_group:
                    attached_si = social_group.get_si_registered_for_sim(sim, affordance=cls)
                    if attached_si is not None:
                        if inst is not None:
                            if attached_si is not inst:
                                return TestResult(False, 'Cannot run social since sim already has an interaction that is registered to group.')
        else:
            return TestResult(False, 'Sim {} is already running matching affordance:{} ', sim, cls)
        inst_or_cls = inst if inst is not None else cls
        return (super(SuperInteraction, inst_or_cls)._test)(target, context, initiated=initiated, **kwargs)

    @classmethod
    def _should_test_affordance_filters(cls, context):
        if context.source == context.SOURCE_AUTONOMY:
            return True
        return super()._should_test_affordance_filters(context)

    @classmethod
    def visual_targets_gen(cls, target, context, **kwargs):
        if cls.target_type & TargetType.ACTOR:
            yield context.sim
        else:
            if cls.target_type & TargetType.TARGET and isinstance(target, sims.sim.Sim):
                yield target
            else:
                for group in context.sim.get_groups_for_sim_gen():
                    for sim in group:
                        yield sim

    @classproperty
    def requires_target_support(cls):
        return False

    @flexmethod
    def is_linked_to(cls, inst, super_affordance):
        if inst is not None:
            target_sim = inst.target_sim
            if target_sim is not None:
                target_social_group = inst._get_social_group_for_sim(target_sim)
                if target_social_group is not None:
                    social_group = inst._get_social_group_for_sim(inst.sim)
                    if social_group is not None:
                        if target_social_group is not social_group:
                            return False
        inst_or_cls = inst if inst is not None else cls
        return super(SocialSuperInteraction, inst_or_cls).is_linked_to(super_affordance)

    @flexmethod
    @assertions.not_recursive_gen
    def _constraint_gen--- This code section failed: ---

 L. 872         0  LOAD_FAST                'inst'
                2  LOAD_CONST               None
                4  COMPARE_OP               is-not
                6  POP_JUMP_IF_FALSE    12  'to 12'
                8  LOAD_FAST                'inst'
               10  JUMP_FORWARD         14  'to 14'
             12_0  COME_FROM             6  '6'
               12  LOAD_FAST                'cls'
             14_0  COME_FROM            10  '10'
               14  STORE_FAST               'inst_or_cls'

 L. 874        16  LOAD_FAST                'participant_type'
               18  LOAD_GLOBAL              ParticipantType
               20  LOAD_ATTR                Actor
               22  COMPARE_OP               ==
               24  POP_JUMP_IF_FALSE   102  'to 102'
               26  LOAD_FAST                'cls'
               28  LOAD_ATTR                relocate_main_group
               30  POP_JUMP_IF_FALSE   102  'to 102'

 L. 875        32  LOAD_FAST                'inst'
               34  LOAD_CONST               None
               36  COMPARE_OP               is
               38  POP_JUMP_IF_TRUE     52  'to 52'
               40  LOAD_FAST                'inst'
               42  LOAD_ATTR                pipeline_progress
               44  LOAD_GLOBAL              PipelineProgress
               46  LOAD_ATTR                RUNNING
               48  COMPARE_OP               <
               50  POP_JUMP_IF_FALSE   102  'to 102'
             52_0  COME_FROM            38  '38'

 L. 877        52  SETUP_LOOP           98  'to 98'
               54  LOAD_GLOBAL              super
               56  LOAD_GLOBAL              SuperInteraction
               58  LOAD_FAST                'inst_or_cls'
               60  CALL_FUNCTION_2       2  '2 positional arguments'
               62  LOAD_ATTR                _constraint_gen
               64  LOAD_FAST                'sim'
               66  LOAD_FAST                'target'
               68  BUILD_TUPLE_2         2 
               70  LOAD_STR                 'participant_type'
               72  LOAD_FAST                'participant_type'
               74  BUILD_MAP_1           1 
               76  LOAD_FAST                'kwargs'
               78  BUILD_MAP_UNPACK_WITH_CALL_2     2 
               80  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               82  GET_ITER         
               84  FOR_ITER             96  'to 96'
               86  STORE_FAST               'constraint'

 L. 878        88  LOAD_FAST                'constraint'
               90  YIELD_VALUE      
               92  POP_TOP          
               94  JUMP_BACK            84  'to 84'
               96  POP_BLOCK        
             98_0  COME_FROM_LOOP       52  '52'

 L. 884        98  LOAD_CONST               None
              100  RETURN_VALUE     
            102_0  COME_FROM            50  '50'
            102_1  COME_FROM            30  '30'
            102_2  COME_FROM            24  '24'

 L. 886       102  LOAD_FAST                'inst'
              104  LOAD_CONST               None
              106  COMPARE_OP               is
              108  POP_JUMP_IF_TRUE    130  'to 130'
              110  LOAD_FAST                'inst'
              112  LOAD_ATTR                social_group
              114  LOAD_CONST               None
              116  COMPARE_OP               is
              118  POP_JUMP_IF_TRUE    130  'to 130'
              120  LOAD_FAST                'inst'
              122  LOAD_ATTR                social_group
              124  LOAD_ATTR                constraint_initialized
          126_128  POP_JUMP_IF_TRUE    514  'to 514'
            130_0  COME_FROM           118  '118'
            130_1  COME_FROM           108  '108'

 L. 888       130  SETUP_LOOP          176  'to 176'
              132  LOAD_GLOBAL              super
              134  LOAD_GLOBAL              SuperInteraction
              136  LOAD_FAST                'inst_or_cls'
              138  CALL_FUNCTION_2       2  '2 positional arguments'
              140  LOAD_ATTR                _constraint_gen
              142  LOAD_FAST                'sim'
              144  LOAD_FAST                'target'
              146  BUILD_TUPLE_2         2 
              148  LOAD_STR                 'participant_type'
              150  LOAD_FAST                'participant_type'
              152  BUILD_MAP_1           1 
              154  LOAD_FAST                'kwargs'
              156  BUILD_MAP_UNPACK_WITH_CALL_2     2 
              158  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              160  GET_ITER         
              162  FOR_ITER            174  'to 174'
              164  STORE_FAST               'constraint'

 L. 889       166  LOAD_FAST                'constraint'
              168  YIELD_VALUE      
              170  POP_TOP          
              172  JUMP_BACK           162  'to 162'
              174  POP_BLOCK        
            176_0  COME_FROM_LOOP      130  '130'

 L. 892       176  LOAD_FAST                'inst'
              178  LOAD_CONST               None
              180  COMPARE_OP               is-not
              182  POP_JUMP_IF_FALSE   194  'to 194'
              184  LOAD_FAST                'inst'
              186  LOAD_ATTR                is_finishing
              188  POP_JUMP_IF_FALSE   194  'to 194'

 L. 893       190  LOAD_CONST               None
              192  RETURN_VALUE     
            194_0  COME_FROM           188  '188'
            194_1  COME_FROM           182  '182'

 L. 913       194  LOAD_FAST                'inst'
              196  LOAD_CONST               None
              198  COMPARE_OP               is
              200  POP_JUMP_IF_FALSE   220  'to 220'

 L. 914       202  LOAD_FAST                'sim'
              204  STORE_FAST               'initiator'

 L. 915       206  LOAD_FAST                'target'
              208  STORE_FAST               'recipient'

 L. 916       210  LOAD_CONST               None
              212  STORE_FAST               'picked_object'

 L. 917       214  LOAD_FAST                'participant_type'
              216  STORE_FAST               'relative_participant'
              218  JUMP_FORWARD        322  'to 322'
            220_0  COME_FROM           200  '200'

 L. 918       220  LOAD_FAST                'inst'
              222  LOAD_ATTR                initiated
              224  POP_JUMP_IF_FALSE   250  'to 250'

 L. 919       226  LOAD_FAST                'inst'
              228  LOAD_ATTR                sim
              230  STORE_FAST               'initiator'

 L. 920       232  LOAD_FAST                'inst'
              234  LOAD_ATTR                target_sim
              236  STORE_FAST               'recipient'

 L. 921       238  LOAD_FAST                'inst'
              240  LOAD_ATTR                picked_object
              242  STORE_FAST               'picked_object'

 L. 922       244  LOAD_FAST                'participant_type'
              246  STORE_FAST               'relative_participant'
              248  JUMP_FORWARD        322  'to 322'
            250_0  COME_FROM           224  '224'

 L. 924       250  LOAD_FAST                'inst'
              252  LOAD_ATTR                target_sim
              254  STORE_FAST               'initiator'

 L. 925       256  LOAD_FAST                'inst'
              258  LOAD_ATTR                sim
              260  STORE_FAST               'recipient'

 L. 926       262  LOAD_FAST                'inst'
              264  LOAD_ATTR                picked_object
              266  STORE_FAST               'picked_object'

 L. 927       268  LOAD_FAST                'participant_type'
              270  LOAD_GLOBAL              ParticipantType
              272  LOAD_ATTR                Actor
              274  COMPARE_OP               ==
          276_278  POP_JUMP_IF_FALSE   288  'to 288'

 L. 928       280  LOAD_GLOBAL              ParticipantType
              282  LOAD_ATTR                TargetSim
              284  STORE_FAST               'relative_participant'
              286  JUMP_FORWARD        322  'to 322'
            288_0  COME_FROM           276  '276'

 L. 929       288  LOAD_FAST                'participant_type'
              290  LOAD_GLOBAL              ParticipantType
              292  LOAD_ATTR                TargetSim
              294  COMPARE_OP               ==
          296_298  POP_JUMP_IF_FALSE   308  'to 308'

 L. 930       300  LOAD_GLOBAL              ParticipantType
              302  LOAD_ATTR                Actor
              304  STORE_FAST               'relative_participant'
              306  JUMP_FORWARD        322  'to 322'
            308_0  COME_FROM           296  '296'

 L. 932       308  LOAD_GLOBAL              ValueError
              310  LOAD_STR                 'Invalid partipant {}'
              312  LOAD_METHOD              format
              314  LOAD_FAST                'participant_type'
              316  CALL_METHOD_1         1  '1 positional argument'
              318  CALL_FUNCTION_1       1  '1 positional argument'
              320  RAISE_VARARGS_1       1  'exception instance'
            322_0  COME_FROM           306  '306'
            322_1  COME_FROM           286  '286'
            322_2  COME_FROM           248  '248'
            322_3  COME_FROM           218  '218'

 L. 934       322  LOAD_FAST                'recipient'
              324  LOAD_CONST               None
              326  COMPARE_OP               is
          328_330  POP_JUMP_IF_TRUE    340  'to 340'
              332  LOAD_FAST                'recipient'
              334  LOAD_ATTR                is_sim
          336_338  POP_JUMP_IF_TRUE    344  'to 344'
            340_0  COME_FROM           328  '328'

 L. 938       340  LOAD_CONST               None
              342  RETURN_VALUE     
            344_0  COME_FROM           336  '336'

 L. 940       344  LOAD_FAST                'initiator'
              346  LOAD_CONST               None
              348  COMPARE_OP               is-not
          350_352  POP_JUMP_IF_FALSE   382  'to 382'
              354  LOAD_FAST                'initiator'
              356  LOAD_FAST                'recipient'
              358  COMPARE_OP               is-not
          360_362  POP_JUMP_IF_FALSE   382  'to 382'

 L. 941       364  LOAD_GLOBAL              get_fallback_social_constraint_position
              366  LOAD_FAST                'initiator'
              368  LOAD_FAST                'recipient'
              370  LOAD_FAST                'inst'
              372  CALL_FUNCTION_3       3  '3 positional arguments'
              374  UNPACK_SEQUENCE_2     2 
              376  STORE_FAST               'fallback_position'
              378  STORE_FAST               'fallback_routing_surface'
              380  JUMP_FORWARD        386  'to 386'
            382_0  COME_FROM           360  '360'
            382_1  COME_FROM           350  '350'

 L. 943       382  LOAD_CONST               None
              384  STORE_FAST               'fallback_position'
            386_0  COME_FROM           380  '380'

 L. 945       386  LOAD_FAST                'fallback_position'
              388  LOAD_CONST               None
              390  COMPARE_OP               is
          392_394  POP_JUMP_IF_FALSE   416  'to 416'

 L. 946       396  LOAD_FAST                'inst'
              398  LOAD_CONST               None
              400  COMPARE_OP               is-not
          402_404  POP_JUMP_IF_FALSE   412  'to 412'

 L. 950       406  LOAD_GLOBAL              GEOMETRY_INCOMPATIBLE_ANYWHERE
              408  YIELD_VALUE      
              410  POP_TOP          
            412_0  COME_FROM           402  '402'

 L. 951       412  LOAD_CONST               None
              414  RETURN_VALUE     
            416_0  COME_FROM           392  '392'

 L. 952       416  LOAD_FAST                'cls'
              418  LOAD_ATTR                _get_social_group_type
              420  LOAD_FAST                'initiator'
              422  LOAD_FAST                'recipient'
              424  LOAD_CONST               ('actor', 'target')
              426  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              428  STORE_FAST               'social_group_type'

 L. 953       430  LOAD_FAST                'social_group_type'
              432  LOAD_ATTR                make_constraint_default
              434  LOAD_FAST                'initiator'
              436  LOAD_FAST                'recipient'

 L. 954       438  LOAD_FAST                'fallback_position'

 L. 955       440  LOAD_FAST                'fallback_routing_surface'

 L. 956       442  LOAD_FAST                'relative_participant'

 L. 957       444  LOAD_FAST                'picked_object'

 L. 958       446  LOAD_FAST                'inst_or_cls'
              448  LOAD_ATTR                _social_group_participant_slot_overrides
              450  LOAD_CONST               ('participant_type', 'picked_object', 'participant_slot_overrides')
              452  CALL_FUNCTION_KW_7     7  '7 total positional and keyword args'
              454  STORE_FAST               'fallback_constraint'

 L. 960       456  LOAD_FAST                'inst'
              458  LOAD_CONST               None
              460  COMPARE_OP               is-not
          462_464  POP_JUMP_IF_FALSE   472  'to 472'
              466  LOAD_FAST                'inst'
              468  LOAD_ATTR                priority
              470  JUMP_FORWARD        474  'to 474'
            472_0  COME_FROM           462  '462'
              472  LOAD_CONST               None
            474_0  COME_FROM           470  '470'
              474  STORE_FAST               'priority'

 L. 961       476  LOAD_FAST                'sim'
              478  LOAD_ATTR                si_state
              480  LOAD_ATTR                is_compatible_constraint
              482  LOAD_FAST                'fallback_constraint'
              484  LOAD_FAST                'priority'
              486  LOAD_FAST                'inst'
              488  LOAD_CONST               ('priority', 'to_exclude')
              490  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
          492_494  POP_JUMP_IF_FALSE   504  'to 504'

 L. 962       496  LOAD_FAST                'fallback_constraint'
              498  YIELD_VALUE      
              500  POP_TOP          
              502  JUMP_FORWARD        510  'to 510'
            504_0  COME_FROM           492  '492'

 L. 964       504  LOAD_GLOBAL              GEOMETRY_INCOMPATIBLE_ANYWHERE
              506  YIELD_VALUE      
              508  POP_TOP          
            510_0  COME_FROM           502  '502'

 L. 965       510  LOAD_CONST               None
              512  RETURN_VALUE     
            514_0  COME_FROM           126  '126'

 L. 967       514  LOAD_FAST                'participant_type'
              516  LOAD_GLOBAL              ParticipantType
              518  LOAD_ATTR                TargetSim
              520  COMPARE_OP               ==
          522_524  POP_JUMP_IF_FALSE   784  'to 784'

 L. 968       526  LOAD_FAST                'cls'
              528  LOAD_ATTR                acquire_targets_as_resource
          530_532  POP_JUMP_IF_TRUE    546  'to 546'

 L. 971       534  LOAD_GLOBAL              Anywhere
              536  CALL_FUNCTION_0       0  '0 positional arguments'
              538  YIELD_VALUE      
              540  POP_TOP          

 L. 972       542  LOAD_CONST               None
              544  RETURN_VALUE     
            546_0  COME_FROM           530  '530'

 L. 976       546  LOAD_FAST                'inst'
              548  LOAD_CONST               None
              550  COMPARE_OP               is-not
          552_554  POP_JUMP_IF_FALSE   668  'to 668'

 L. 977       556  LOAD_FAST                'inst'
              558  LOAD_METHOD              get_target_si
              560  CALL_METHOD_0         0  '0 positional arguments'
              562  UNPACK_SEQUENCE_2     2 
              564  STORE_FAST               'target_si'
              566  STORE_FAST               'test_result'

 L. 978       568  LOAD_FAST                'test_result'
          570_572  POP_JUMP_IF_TRUE    592  'to 592'

 L. 979       574  LOAD_GLOBAL              Nowhere
              576  LOAD_STR                 'SocialSuperInteraction._constraint_gen, target SI test failed({}) SI: {}'
              578  LOAD_FAST                'test_result'
              580  LOAD_FAST                'target_si'
              582  CALL_FUNCTION_3       3  '3 positional arguments'
              584  YIELD_VALUE      
              586  POP_TOP          

 L. 980       588  LOAD_CONST               None
              590  RETURN_VALUE     
            592_0  COME_FROM           570  '570'

 L. 982       592  LOAD_FAST                'target_si'
              594  LOAD_CONST               None
              596  COMPARE_OP               is-not
          598_600  POP_JUMP_IF_FALSE   668  'to 668'

 L. 983       602  LOAD_GLOBAL              issubclass
              604  LOAD_FAST                'target_si'
              606  LOAD_ATTR                affordance
              608  LOAD_GLOBAL              SocialPlaceholderSuperInteraction
              610  CALL_FUNCTION_2       2  '2 positional arguments'
          612_614  POP_JUMP_IF_TRUE    668  'to 668'

 L. 987       616  LOAD_FAST                'target_si'
              618  LOAD_METHOD              get_participant
              620  LOAD_GLOBAL              ParticipantType
              622  LOAD_ATTR                TargetSim
              624  CALL_METHOD_1         1  '1 positional argument'
              626  STORE_FAST               'target_si_target'

 L. 988       628  SETUP_LOOP          664  'to 664'
              630  LOAD_FAST                'target_si'
              632  LOAD_ATTR                constraint_gen
              634  LOAD_FAST                'sim'
              636  LOAD_FAST                'target_si_target'
              638  LOAD_GLOBAL              ParticipantType
              640  LOAD_ATTR                Actor
              642  LOAD_CONST               ('participant_type',)
              644  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              646  GET_ITER         
              648  FOR_ITER            662  'to 662'
              650  STORE_FAST               'constraint'

 L. 989       652  LOAD_FAST                'constraint'
              654  YIELD_VALUE      
              656  POP_TOP          
          658_660  JUMP_BACK           648  'to 648'
              662  POP_BLOCK        
            664_0  COME_FROM_LOOP      628  '628'

 L. 990       664  LOAD_CONST               None
              666  RETURN_VALUE     
            668_0  COME_FROM           612  '612'
            668_1  COME_FROM           598  '598'
            668_2  COME_FROM           552  '552'

 L. 992       668  SETUP_LOOP          716  'to 716'
              670  LOAD_GLOBAL              super
              672  LOAD_GLOBAL              SuperInteraction
              674  LOAD_FAST                'cls'
              676  CALL_FUNCTION_2       2  '2 positional arguments'
              678  LOAD_ATTR                _constraint_gen
              680  LOAD_FAST                'sim'
              682  LOAD_FAST                'target'
              684  BUILD_TUPLE_2         2 
              686  LOAD_STR                 'participant_type'
              688  LOAD_FAST                'participant_type'
              690  BUILD_MAP_1           1 
              692  LOAD_FAST                'kwargs'
              694  BUILD_MAP_UNPACK_WITH_CALL_2     2 
              696  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              698  GET_ITER         
              700  FOR_ITER            714  'to 714'
              702  STORE_FAST               'constraint'

 L. 993       704  LOAD_FAST                'constraint'
              706  YIELD_VALUE      
              708  POP_TOP          
          710_712  JUMP_BACK           700  'to 700'
              714  POP_BLOCK        
            716_0  COME_FROM_LOOP      668  '668'

 L. 995       716  LOAD_FAST                'inst'
              718  LOAD_CONST               None
              720  COMPARE_OP               is-not
          722_724  POP_JUMP_IF_FALSE   892  'to 892'

 L. 996       726  LOAD_FAST                'inst'
              728  LOAD_ATTR                social_group
              730  LOAD_CONST               None
              732  COMPARE_OP               is-not
          734_736  POP_JUMP_IF_FALSE   754  'to 754'

 L. 997       738  LOAD_FAST                'inst'
              740  LOAD_ATTR                social_group
              742  LOAD_METHOD              get_constraint
              744  LOAD_FAST                'sim'
              746  CALL_METHOD_1         1  '1 positional argument'
              748  YIELD_VALUE      
              750  POP_TOP          
              752  JUMP_FORWARD        782  'to 782'
            754_0  COME_FROM           734  '734'

 L. 999       754  LOAD_GLOBAL              logger
              756  LOAD_ATTR                error
              758  LOAD_STR                 'Attempt to get constraint from Social interaction and no constraint exists: {}'

 L.1000       760  LOAD_FAST                'inst'
              762  LOAD_STR                 'maxr'
              764  LOAD_CONST               ('owner',)
              766  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              768  POP_TOP          

 L.1001       770  LOAD_GLOBAL              Anywhere
              772  CALL_FUNCTION_0       0  '0 positional arguments'
              774  YIELD_VALUE      
              776  POP_TOP          

 L.1002       778  LOAD_CONST               None
              780  RETURN_VALUE     
            782_0  COME_FROM           752  '752'
              782  JUMP_FORWARD        892  'to 892'
            784_0  COME_FROM           522  '522'

 L.1004       784  LOAD_FAST                'participant_type'
              786  LOAD_GLOBAL              ParticipantType
              788  LOAD_ATTR                Actor
              790  COMPARE_OP               ==
          792_794  POP_JUMP_IF_FALSE   892  'to 892'

 L.1005       796  SETUP_LOOP          844  'to 844'
              798  LOAD_GLOBAL              super
              800  LOAD_GLOBAL              SuperInteraction
              802  LOAD_FAST                'inst_or_cls'
              804  CALL_FUNCTION_2       2  '2 positional arguments'
              806  LOAD_ATTR                _constraint_gen
              808  LOAD_FAST                'sim'
              810  LOAD_FAST                'target'
              812  BUILD_TUPLE_2         2 
              814  LOAD_STR                 'participant_type'
              816  LOAD_FAST                'participant_type'
              818  BUILD_MAP_1           1 
              820  LOAD_FAST                'kwargs'
              822  BUILD_MAP_UNPACK_WITH_CALL_2     2 
              824  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
              826  GET_ITER         
              828  FOR_ITER            842  'to 842'
              830  STORE_FAST               'constraint'

 L.1006       832  LOAD_FAST                'constraint'
              834  YIELD_VALUE      
              836  POP_TOP          
          838_840  JUMP_BACK           828  'to 828'
              842  POP_BLOCK        
            844_0  COME_FROM_LOOP      796  '796'

 L.1007       844  LOAD_FAST                'inst'
              846  LOAD_CONST               None
              848  COMPARE_OP               is-not
          850_852  POP_JUMP_IF_FALSE   892  'to 892'

 L.1008       854  LOAD_FAST                'inst'
              856  LOAD_ATTR                social_group
              858  LOAD_CONST               None
              860  COMPARE_OP               is-not
          862_864  POP_JUMP_IF_FALSE   892  'to 892'
              866  LOAD_FAST                'participant_type'
              868  LOAD_GLOBAL              ParticipantType
              870  LOAD_ATTR                Actor
              872  COMPARE_OP               ==
          874_876  POP_JUMP_IF_FALSE   892  'to 892'

 L.1009       878  LOAD_FAST                'inst'
              880  LOAD_ATTR                social_group
              882  LOAD_METHOD              get_constraint
              884  LOAD_FAST                'sim'
              886  CALL_METHOD_1         1  '1 positional argument'
              888  YIELD_VALUE      
              890  POP_TOP          
            892_0  COME_FROM           874  '874'
            892_1  COME_FROM           862  '862'
            892_2  COME_FROM           850  '850'
            892_3  COME_FROM           792  '792'
            892_4  COME_FROM           782  '782'
            892_5  COME_FROM           722  '722'

Parse error at or near `COME_FROM' instruction at offset 892_4

    @flexmethod
    def apply_posture_state_and_interaction_to_constraint(cls, inst, posture_state, intersection, participant_type=ParticipantType.Actor, **kwargs):
        if inst is None:
            return intersection.apply_posture_state(posture_state, (cls.get_constraint_resolver)(posture_state, participant_type=participant_type, **kwargs))
        if participant_type == ParticipantType.TargetSim:
            target_si, test_result = inst.get_target_si()
            if not test_result:
                return Nowhere('SocialSuperInteraction.apply_posture_state_and_interaction_to_constraint, target SI test failed({}) SI: {}', test_result, target_si)
            if target_si is not None:
                if posture_state is None or posture_state.sim is target_si.sim:
                    return (target_si.apply_posture_state_and_interaction_to_constraint)(posture_state, intersection, participant_type=ParticipantType.Actor, **kwargs)
        inst_or_cls = inst if inst is not None else cls
        return (super(SuperInteraction, inst_or_cls).apply_posture_state_and_interaction_to_constraint)(posture_state, intersection, participant_type=participant_type, **kwargs)

    @classmethod
    def has_pie_menu_sub_interactions(cls, target, context, **kwargs):
        return autonomy.content_sets.any_content_set_available((context.sim), cls,
          None,
          context,
          potential_targets=(
         target,),
          include_failed_aops_with_tooltip=True)

    def apply_posture_state(self, posture_state, participant_type=ParticipantType.Actor, **kwargs):
        if participant_type == ParticipantType.TargetSim:
            target_si, test_result = self.get_target_si()
            if target_si is not None:
                if not test_result:
                    if posture_state is not None:
                        posture_state.add_constraint(target_si, Nowhere('SocialSuperInteraction.apply_posture_state, target SI test failed({}) SI: {}, posture_state: {}', test_result, target_si, posture_state))
            if target_si is not None:
                return (target_si.apply_posture_state)(posture_state, participant_type=ParticipantType.Actor, **kwargs)
        return (super().apply_posture_state)(posture_state, participant_type=participant_type, **kwargs)

    @classmethod
    def supports_posture_type(cls, *args, **kwargs):
        return True

    def should_visualize_interaction_for_sim(self, participant_type):
        return participant_type == ParticipantType.Actor

    def notify_queue_head(self):
        if self.is_finishing:
            return
        if self._processing_notify_queue_head:
            return
        self._processing_notify_queue_head = True
        try:
            super().notify_queue_head()
            if self.sim in self.get_sims_with_invalid_paths():
                return
            target_sim = self.target_sim
            if target_sim is not None:
                if target_sim.queue is None:
                    logger.error('Trying to displace Sim {} but his queue is None', target_sim, owner='camilogarcia')
                else:
                    interaction_to_displace = target_sim.queue.running
                    if interaction_to_displace is None:
                        interaction_to_displace = target_sim.queue.get_head()
                        if interaction_to_displace is not None:
                            if interaction_to_displace.context.source is not InteractionContext.SOURCE_AUTONOMY:
                                interaction_to_displace = None
                    if interaction_to_displace is not None:
                        if can_displace(self, interaction_to_displace):
                            interaction_to_displace.displace(self, cancel_reason_msg=('Target of higher priority social: {}'.format(self)))
            if self._social_group is None:
                self._choose_social_group()
            if self.sim.sim_info.get_current_outfit()[0] == OutfitCategory.BATHING:
                if self.target.is_sim:
                    if self.target.sim_info.age <= Age.TEEN:
                        if not any((si.affordance is SocialSuperInteraction.SKINNY_DIP_SAFEGUARD_INTERACTION for si in self.sim.get_all_running_and_queued_interactions())):
                            context = InteractionContext((self.sim), (InteractionContext.SOURCE_SCRIPT),
                              priority=(Priority.Critical),
                              insert_strategy=(QueueInsertStrategy.FIRST))
                            self.sim.push_super_affordance(SocialSuperInteraction.SKINNY_DIP_SAFEGUARD_INTERACTION, self.target, context)
            self._get_close_to_target_and_greet()
        finally:
            self._processing_notify_queue_head = False

    def _get_social_group_for_this_interaction(self):
        social_group = None
        target_sim = self.get_participant(ParticipantType.TargetSim)
        if target_sim is None:
            target_sim = self.get_participant(ParticipantType.JoinTarget)
        if target_sim is not None:
            social_group = self._get_social_group_for_sim(target_sim)
        if social_group is None:
            social_group = self._get_social_group_for_sim(self.sim)
        if social_group is None:
            for existing_social_group in services.social_group_manager().objects:
                if existing_social_group.has_been_shutdown:
                    continue
                if type(existing_social_group) is self._get_social_group_type():
                    existing_group_target_sim = existing_social_group._target_sim
                    if not existing_group_target_sim is not None or existing_group_target_sim is self.sim or existing_group_target_sim is target_sim:
                        social_group = existing_social_group
                        break

        if social_group is None:
            if target_sim is None:
                for participant in self.get_participants(ParticipantType.OtherSimsInteractingWithTarget):
                    social_group = self._get_social_group_for_sim(participant)
                    if social_group is not None:
                        break

        if social_group is None:
            target_object = self.get_participant(ParticipantType.Object)
            if target_object is not None:
                if target_object.is_part:
                    target_object = target_object.part_owner
                for existing_social_group in services.social_group_manager().objects:
                    if existing_social_group.has_been_shutdown:
                        continue
                    if type(existing_social_group) is self._get_social_group_type() and existing_social_group.validate_anchor(target_object):
                        social_group = existing_social_group

        if social_group is not None:
            if social_group.has_room_in_group(self.sim):
                if target_sim is not None:
                    social_group = social_group.has_room_in_group(target_sim) or None
            elif self.sim in social_group:
                if target_sim is not None:
                    if target_sim not in social_group:
                        if target_sim.discourage_route_to_join_social_group():
                            social_group = None
        return social_group

    def _derail_on_target_sim_posture_change(self, *args, **kwargs):
        target_sim = self.target_sim
        if target_sim is None:
            return
        if self.transition is None:
            return
        if target_sim in self.transition.get_transitioning_sims() != self.is_target_sim_location_and_posture_valid():
            return
        if target_sim not in self.transition.get_transitioning_sims():
            if self.is_target_sim_location_and_posture_valid():
                return
        if self.transition is not None:
            self.transition.derail(DerailReason.PREEMPTED, self.sim)
            self.transition.derail(DerailReason.PREEMPTED, self.target_sim)

    def _register_derail_on_target_sim_posture_change(self):
        target_sim = self.target_sim
        if target_sim is None:
            return
        if self._derail_on_target_sim_posture_change not in target_sim.on_posture_event:
            target_sim.on_posture_event.append(self._derail_on_target_sim_posture_change)
        if self._derail_on_target_sim_posture_change not in target_sim.routing_component.on_intended_location_changed:
            target_sim.routing_component.on_intended_location_changed.append(self._derail_on_target_sim_posture_change)

    def _unregister_derail_on_target_sim_posture_change(self):
        target_sim = self.target_sim
        if target_sim is None:
            return
        if self._derail_on_target_sim_posture_change in target_sim.on_posture_event:
            target_sim.on_posture_event.remove(self._derail_on_target_sim_posture_change)
        target_sim_routing_component = target_sim.routing_component
        if target_sim_routing_component is not None:
            if self._derail_on_target_sim_posture_change in target_sim_routing_component.on_intended_location_changed:
                target_sim_routing_component.on_intended_location_changed.remove(self._derail_on_target_sim_posture_change)

    def is_target_sim_location_and_posture_valid(self):
        target_sim = self.target_sim
        if target_sim.is_moving:
            return False
        interaction_constraint = self.constraint_intersection(target_sim, posture_state=None, participant_type=(ParticipantType.TargetSim))
        target_sim_transform = interactions.constraints.Transform((target_sim.transform), routing_surface=(target_sim.routing_surface))
        target_sim_posture_constraint = target_sim.posture_state.posture_constraint_strict
        intersection = interaction_constraint.intersect(target_sim_transform).intersect(target_sim_posture_constraint)
        return intersection.valid

    def _get_required_sims(self, for_threading=False):
        required_sims = super()._get_required_sims()
        if not self.require_shared_body_target:
            if self.initiated:
                if not (self.basic_content.staging and for_threading):
                    return required_sims
        else:
            target_sim = self.target_sim
            if target_sim is None:
                return required_sims
            current_constraint = target_sim.posture_state.constraint_intersection
            return any((constraint.geometry is not None for constraint in current_constraint)) or required_sims
        if self.is_target_sim_location_and_posture_valid():
            required_sims = set(required_sims)
            required_sims.discard(target_sim)
            required_sims = frozenset(required_sims)
        self._register_derail_on_target_sim_posture_change()
        return required_sims

    def _choose_social_group(self):
        social_group = self.social_group
        if social_group is None:
            social_group = self._get_social_group_for_this_interaction()
            if social_group is not None:
                if social_group.picked_object is not None:
                    if not social_group.picked_object.is_sim:
                        if social_group.picked_object not in self.preferred_objects:
                            social_group.shutdown(finishing_type=(FinishingType.OBJECT_CHANGED))
                            social_group = None
            if social_group is None:
                target_sim = self.get_participant(ParticipantType.TargetSim)
                social_group_type = self._get_social_group_type()
                social_group = social_group_type(si=self, target_sim=target_sim, participant_slot_overrides=(self._social_group_participant_slot_overrides))
            self._social_group = social_group
            if self.target:
                if self.target.is_sim:
                    if self._update_social_geometry_if_target_moves:
                        self.target.routing_component.on_intended_location_changed.append(self._on_target_intended_location_changed_callback)
            self.refresh_constraints()
        if self.refresh_constraints not in self.social_group.on_constraint_changed:
            self.social_group.on_constraint_changed.append(self.refresh_constraints)
        self.social_group.attach(self)

    def prepare_gen(self, timeline, *args, **kwargs):
        result = yield from (super().prepare_gen)(timeline, *args, **kwargs)
        if result != InteractionQueuePreparationStatus.SUCCESS:
            return result
        self._choose_social_group()
        target_si, target_si_test_result = self.get_target_si()
        if target_si is not None:
            if not target_si_test_result:
                sims.sim_log.log_interaction('Preparing', self, 'social super interaction failed: {}'.format(target_si_test_result))
                return InteractionQueuePreparationStatus.FAILURE
            if target_si._social_group is not None:
                if target_si._social_group is not self.social_group:
                    logger.error('Social group mismatch between Sim and TargetSim in social_super_interaction.prepare')
            target_si._social_group = self.social_group
            result = yield from (target_si.prepare_gen)(timeline, *args, **kwargs)
        return result
        if False:
            yield None

    def _pre_perform(self):
        result = super()._pre_perform()
        self._unregister_derail_on_target_sim_posture_change()
        social_group = self.social_group
        if social_group is None:
            logger.error('SocialSuperInteraction is trying to run without a social group: {}', self, owner='maxr')
            return False
        if self.multi_sim_override_data is not None:
            if self.multi_sim_override_data.icon is not None or self.multi_sim_override_data.display_text is not None:
                self._on_social_group_changed(social_group, invalidate_mixers=False)
        social_group.on_group_changed.append(self._on_social_group_changed)
        return result

    def get_multi_sim_icon_and_name(self):
        icon_info = None
        display_text = None
        if self.multi_sim_override_data.icon is not None:
            icon_info = IconInfoData(icon_resource=(self.multi_sim_override_data.icon))
        if self.multi_sim_override_data.display_text is not None:
            sim_names = []
            actor = self.sim
            for sim in self.social_group:
                if sim is actor:
                    continue
                sim_names.append(sims4.localization.LocalizationHelperTuning.get_sim_name(sim))

            sim_names_loc = (sims4.localization.LocalizationHelperTuning.get_comma_separated_list)(*sim_names)
            display_text = self.multi_sim_override_data.display_text(sim_names_loc)
        return (icon_info, display_text)

    def _run_interaction_gen(self, timeline):
        if not self.is_finishing:
            if self.social_group is not None:
                self.social_group.on_social_super_interaction_run()
            else:
                logger.error('{} is running and has no social group. This should never happen!', self, owner='maxr')
                self.cancel(FinishingType.SOCIALS, 'Social Group is None in _run_interaction_gen')
        yield from super()._run_interaction_gen(timeline)
        if False:
            yield None

    def _retarget_social_interaction(self, social_group):
        actor = self.sim
        target_is_sim = self.target is not None and self.target.is_sim
        if target_is_sim:
            if self.target not in social_group:
                if self._target_si is not None:
                    if self.target is self._target_si.sim:
                        if self._target_si.pipeline_progress == PipelineProgress.NONE:
                            sims.sim_log.log_interaction('Invalidate', self._target_si, 'retarget_social :{}'.format(self))
                            self._target_si.on_removed_from_queue()
                            self._target_si = None
                for target in social_group:
                    if actor is target:
                        continue
                    self.set_target(target)
                    break

    def _on_social_group_changed(self, social_group, invalidate_mixers=True):
        if social_group is None:
            return
        if self._processing_social_group_change:
            return
        try:
            self._processing_social_group_change = True
            actor = self.sim
            if invalidate_mixers:
                actor.invalidate_mixer_interaction_cache(None)
            else:
                self._retarget_social_interaction(social_group)
                if self.multi_sim_override_data is not None and len(social_group) > self.multi_sim_override_data.threshold:
                    icon_info, display_name = self.get_multi_sim_icon_and_name()
                    actor.ui_manager.set_interaction_icon_and_name(self.id, icon_info, display_name)
                else:
                    _, visual_type_data = self.get_interaction_queue_visual_type()
                    if visual_type_data.icon is not None:
                        icon_info = (
                         visual_type_data.icon, None)
                    else:
                        icon_info = self.get_icon_info()
                    if visual_type_data.tooltip_text is not None:
                        display_name = self.create_localized_string(visual_type_data.tooltip_text)
                    else:
                        display_name = self.get_name()
                    actor.ui_manager.set_interaction_icon_and_name(self.id, icon_info, display_name)
        finally:
            self._processing_social_group_change = False

    @property
    def initiated(self):
        return self._initiated

    @classproperty
    def is_social(cls):
        return True

    @property
    def social_group(self):
        return self._social_group

    def get_potential_mixer_targets(self):
        if self.social_group is not None:
            potential_targets = self.social_group.get_potential_mixer_targets(self.sim)
        else:
            potential_targets = set()
        if self.target is not None:
            if not self.target.is_sim:
                potential_targets.add(self.target)
            else:
                if self.pipeline_progress < PipelineProgress.STAGED:
                    potential_targets.add(self.target)
        return potential_targets

    @classproperty
    def linked_interaction_type(cls):
        linked_interaction_type = cls.affordance_to_push_on_target
        if isinstance(linked_interaction_type, bool):
            if linked_interaction_type:
                linked_interaction_type = issubclass(cls, JoinInteraction) or cls
            else:
                return
        basic_content = cls.basic_content
        if not basic_content.staging:
            if basic_content.sleeping:
                if linked_interaction_type is not None:
                    linked_interaction_type = SocialPlaceholderSuperInteraction.generate(linked_interaction_type)
        return linked_interaction_type

    @property
    def canceling_incurs_opportunity_cost(self):
        return True

    def get_target_si(self):
        if self._target_si is None:
            aop, context = self._get_target_aop_and_context()
            if aop is not None and context is not None:
                _, self._target_si, _ = aop.interaction_factory(context)
                self._target_si_test_result = aop.test(context, skip_safe_tests=True)
            else:
                self._target_si, self._target_si_test_result = super().get_target_si()
        elif self.social_group is not None:
            target_sim = self._target_si.sim
            if target_sim is not None:
                if self._should_skip_pushing_target_si(target_sim):
                    self._target_si.invalidate()
                    self._target_si = None
                    self._target_si_test_result = TestResult.TRUE
        return (
         self._target_si, self._target_si_test_result)

    def _get_target_aop_and_context(self):
        target_affordance = self.linked_interaction_type
        target_sim = self.get_participant(ParticipantType.TargetSim)
        if not self.initiated or target_affordance is None or target_sim is None:
            return (None, None)
            if self.social_group is not None:
                if self._should_skip_pushing_target_si(target_sim):
                    return (None, None)
        target_context = interactions.context.InteractionContext(target_sim, (self.context.source),
          (self.priority),
          group_id=(self.group_id),
          insert_strategy=(QueueInsertStrategy.NEXT))
        additional_kwargs = self.get_source_social_kwargs()
        target_aop = (interactions.aop.AffordanceObjectPair)(target_affordance,
 self.sim,
 target_affordance,
 None, social_group=self.social_group, 
         initiated=False, 
         source_social_si=self, 
         picked_object=self.picked_object, 
         disable_saving=True, **additional_kwargs)
        return (
         target_aop, target_context)

    def _should_skip_pushing_target_si(self, target_sim):
        if self.must_run_target_si:
            return False
        return self.social_group.is_sim_active_in_social_group(target_sim)

    def run_additional_social_affordance_gen(self, timeline):
        affordance = self.additional_social_to_run_on_both
        if affordance is None:
            return
        target_sim = self.get_participant(ParticipantType.TargetSim)
        sim_context = self.context.clone_for_sim(self.sim)
        sim_aop = interactions.aop.AffordanceObjectPair(affordance, target_sim,
          affordance,
          None,
          initiated=True)
        sim_execute_result = sim_aop.interaction_factory(sim_context)
        if sim_execute_result:
            sim_si = sim_execute_result.interaction
            target_si, target_test_result = sim_si.get_target_si()
            if target_test_result:
                if target_si is not None:
                    yield from sim_si.run_direct_gen(timeline, source_interaction=self)
                    yield from target_si.run_direct_gen(timeline, source_interaction=self)
                    return True
        return False
        if False:
            yield None

    def invalidate(self):
        super().invalidate()
        if self.pipeline_progress == PipelineProgress.NONE:
            self._target_si = None
            self._source_social_si = None

    def _entered_pipeline(self):
        if self._social_group is not None:
            self._social_group.attach(self)
        return super()._entered_pipeline()

    def _exited_pipeline(self, *args, **kwargs):
        self._unregister_derail_on_target_sim_posture_change()
        (super()._exited_pipeline)(*args, **kwargs)
        self._detach_from_group()
        if self._target_si is not None:
            if self._target_si.pipeline_progress == PipelineProgress.NONE:
                self._target_si.on_removed_from_queue()
            self._target_si = None
        self._cancel_waiting_alarm()
        self._source_social_si = None
        self.last_social_group = None
        self._greeting_interaction = None
        self._go_nearby_interaction = None
        self._preserved_group_jig_polygon = None

    def _cancel(self, finishing_type, *args, propagate_cancelation_to_socials=True, **kwargs):
        if (super()._cancel)(finishing_type, *args, **kwargs):
            self._detach_from_group()
            if finishing_type == FinishingType.USER_CANCEL and self._source_social_si is not None and self._source_social_si.sim is not None:
                self._source_social_si.sim.add_lockout(self.sim, AutonomyModesTuning.LOCKOUT_TIME)
                self.sim.add_lockout(self._source_social_si.sim, AutonomyModesTuning.LOCKOUT_TIME)
        elif propagate_cancelation_to_socials:
            if self._social_group is not None:
                group_count = len(self._social_group) - 1
                if group_count < self._social_group.minimum_sim_count:
                    for interaction in list(self._social_group.get_all_interactions_gen()):
                        if interaction is not self and interaction.running:
                            interaction.cancel(finishing_type, propagate_cancelation_to_socials=False, cancel_reason_msg='Propagating social cancelation pending deferred cancel from running')

    def _trigger_interaction_start_event(self):
        super()._trigger_interaction_start_event()
        if self.linked_interaction_type is None:
            sim = self.get_participant(ParticipantType.TargetSim)
            if sim is not None:
                services.get_event_manager().process_event((test_events.TestEvent.InteractionStart), sim_info=(sim.sim_info),
                  interaction=self,
                  custom_keys=(self.get_keys_to_process_events()))
                self._register_target_event_auto_update()

    def _detach_from_group(self):
        if self.social_group is not None:
            if self.refresh_constraints in self.social_group.on_constraint_changed:
                self.social_group.on_constraint_changed.remove(self.refresh_constraints)
            else:
                if self._on_social_group_changed in self.social_group.on_group_changed:
                    self.social_group.on_group_changed.remove(self._on_social_group_changed)
                if self.target is not None:
                    if self.target.is_sim:
                        if self._update_social_geometry_if_target_moves and self._on_target_intended_location_changed_callback in self.target.routing_component.on_intended_location_changed:
                            self.target.routing_component.on_intended_location_changed.remove(self._on_target_intended_location_changed_callback)
            if self.preserve_group_jig_polygon:
                self._preserved_group_jig_polygon = self.social_group.jig_polygon
            self.social_group.detach(self)
            self.last_social_group = self._social_group
            self._social_group = None

    def _get_similar_interaction(self):
        for interaction in self.sim.running_interactions_gen(self.get_interaction_type()):
            if interaction is not self:
                return interaction

        return self

    def get_attention_cost(self):
        attention_cost = super().get_attention_cost()
        social_context_bit = self.sim.get_social_context()
        if social_context_bit is not None:
            attention_cost += social_context_bit.attention_cost
        return attention_cost

    def _build_pre_elements(self):

        def do_pre_run_behavior(_):
            similar_interaction = self._get_similar_interaction()
            if similar_interaction is not self:
                similar_interaction.cancel((FinishingType.SOCIALS), cancel_reason_msg=('Similar Social SI: {} already running'.format(similar_interaction)))
            if self.target is not None:
                if self.target.is_sim:
                    interaction_type = self.get_interaction_type()
                    mixer_interactions = [mixer for mixer in self.sim.queue.mixer_interactions_gen() if mixer.super_affordance.get_interaction_type() is interaction_type]
                    if self.ignores_greetings or any((mixer.ignores_greetings for mixer in mixer_interactions)):
                        greetings.add_greeted_rel_bit(self.sim.sim_info, self.target.sim_info)

        return do_pre_run_behavior


lock_instance_tunables(SocialSuperInteraction, generate_content_set_as_potential_aops=True)

class SocialPlaceholderSuperInteraction(ProxyInteraction):
    INSTANCE_SUBCLASSES_ONLY = True

    @classmethod
    def generate--- This code section failed: ---

 L.1805         0  LOAD_GLOBAL              super
                2  CALL_FUNCTION_0       0  '0 positional arguments'
                4  LOAD_METHOD              generate
                6  LOAD_FAST                'proxied_affordance'
                8  CALL_METHOD_1         1  '1 positional argument'
               10  STORE_FAST               'result'

 L.1809        12  LOAD_FAST                'proxied_affordance'
               14  LOAD_ATTR                basic_content
               16  STORE_DEREF              'basic_content'

 L.1810        18  LOAD_CLOSURE             'basic_content'
               20  BUILD_TUPLE_1         1 
               22  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               24  LOAD_STR                 'SocialPlaceholderSuperInteraction.generate.<locals>.<dictcomp>'
               26  MAKE_FUNCTION_8          'closure'
               28  LOAD_DEREF               'basic_content'
               30  LOAD_ATTR                AUTO_INIT_KWARGS
               32  GET_ITER         
               34  CALL_FUNCTION_1       1  '1 positional argument'
               36  STORE_FAST               'basic_content_kwargs'

 L.1811        38  LOAD_GLOBAL              StagingContent
               40  LOAD_ATTR                EMPTY
               42  LOAD_FAST                'basic_content_kwargs'
               44  LOAD_STR                 'content'
               46  STORE_SUBSCR     

 L.1813        48  LOAD_GLOBAL              FlexibleLengthContent
               50  BUILD_TUPLE_0         0 
               52  LOAD_FAST                'basic_content_kwargs'
               54  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               56  LOAD_FAST                'result'
               58  STORE_ATTR               basic_content

 L.1814        60  LOAD_FAST                'result'
               62  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 22