# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\fire_situation.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 15630 bytes
from event_testing.test_events import TestEvent
from interactions.context import InteractionContext, InteractionSource
from interactions.interaction_cancel_compatibility import InteractionCancelCompatibility, InteractionCancelReason
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from role.role_state import RoleState
from sims4.tuning.tunable import Tunable, TunableSimMinute, TunableReference
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationState, SituationStateData
from situations.situation_job import SituationJob
import services, sims4.log, sims4.tuning.tunable, situations.bouncer
logger = sims4.log.Logger('Fire', default_owner='rfleig')

class FireSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'victim_job':sims4.tuning.tunable.TunableTuple(situation_job=SituationJob.TunableReference(description='\n                                A reference to the SituationJob used during a fire.\n                                '),
       fire_panic_state=RoleState.TunableReference(description='The state while the sim is panicking due to fire.'),
       fire_unaware_state=RoleState.TunableReference(description='\n                                The state while the sim is unaware there is a \n                                fire on the lot.\n                                '),
       fire_safe_state=RoleState.TunableReference(description='\n                                The state while the Sim has made it safely away\n                                from the fire.\n                                '),
       post_fire_state=RoleState.TunableReference(description='\n                                The state the Sim is in after the fire has gone\n                                out.\n                                '),
       save_infant_or_toddler_state=RoleState.TunableReference(description='\n                                The state the Sim is in while they are saving\n                                an infant or toddler.\n                                '),
       tuning_group=GroupNames.SITUATION), 
     'got_to_safety_interaction':situations.situation_complex.TunableInteractionOfInterest(description='\n            The interaction to look for when a Sim has routed off of the lot\n            and safely escaped the fire.\n            '), 
     'got_to_safety_interaction_carried_sim':situations.situation_complex.TunableInteractionOfInterest(description='\n            The interaction to look for when a carried Sim has routed off of the lot\n            and safely escaped the fire.\n            '), 
     'panic_interaction':situations.situation_complex.TunableInteractionOfInterest(description='\n            The interaction that a sim runs while panicking. \n            '), 
     'go_back_to_panic_interactions':situations.situation_complex.TunableInteractionOfInterest(description='\n            The interactions to look for when a Sim has routed back on to a\n            lot that is on fire which will cause the Sim to go back into panic\n            mode.\n            '), 
     'save_infant_or_toddler_interaction':TunableReference(description='\n            The interaction to push on a Sim to save an infant or toddler from the fire.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions='SuperInteraction'), 
     'TIME_POST_FIRE_IN_SIM_MINUTES':TunableSimMinute(description='\n            Number of Sim minutes that the situation can be in the _PostFireState\n            before the situation ends.\n            ',
       default=60)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _PanicState),
         SituationStateData(2, _UnawareState),
         SituationStateData(3, _SafeState),
         SituationStateData(4, _PostFireState),
         SituationStateData(5, _SaveInfantOrToddlerState))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.victim_job.situation_job, cls.victim_job.fire_panic_state)]

    @classmethod
    def default_job(cls):
        return cls.victim_job.situation_job

    @classproperty
    def has_no_klout(cls):
        return True

    def start_situation(self):
        super().start_situation()
        self._change_state(_UnawareState())

    def advance_to_panic(self):
        curr_state_type = type(self._cur_state)
        if curr_state_type == _UnawareState or curr_state_type == _PostFireState:
            self._change_state(_PanicState())

    def advance_to_post_fire(self):
        self._change_state(_PostFireState())

    def reset_to_unaware(self):
        if type(self._cur_state) != _UnawareState:
            self._cancel_duration_alarm()
            self._change_state(_UnawareState())

    def on_remove(self):
        fire_service = services.get_fire_service()
        if fire_service is not None:
            for sim in self.all_sims_in_situation_gen():
                fire_service.remove_fire_situation(sim)

        super().on_remove()


sims4.tuning.instances.lock_instance_tunables(FireSituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.FIRE),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE),
  duration=0)

class _UnawareState(SituationState):

    def on_activate(self, reader=None):
        logger.debug('Sim is entering the Unaware state during a fire.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.victim_job.situation_job, self.owner.victim_job.fire_unaware_state)
        fire_service = services.get_fire_service()
        fire_service.register_for_panic_callback()


class _PanicState(SituationState):

    def on_activate(self, reader=None):
        logger.debug('Sim is entering the Panic State during a fire.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.victim_job.situation_job, self.owner.victim_job.fire_panic_state)
        for custom_key in self.owner.got_to_safety_interaction.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

        for custom_key in self.owner.got_to_safety_interaction_carried_sim.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

        for custom_key in self.owner.panic_interaction.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

    def _on_set_sim_role_state(self, sim, job_type, role_state_type, role_affordance_target):
        super()._on_set_sim_role_state(sim, job_type, role_state_type, role_affordance_target)
        InteractionCancelCompatibility.cancel_interactions_for_reason(sim, InteractionCancelReason.FIRE, FinishingType.FIRE, 'Interaction was canceled due to a fire on the lot.')

    def handle_event(self, sim_info, event, resolver):
        if event is TestEvent.InteractionComplete:
            if not self.owner.is_sim_info_in_situation(sim_info):
                return
            if resolver(self.owner.got_to_safety_interaction) or resolver(self.owner.got_to_safety_interaction_carried_sim):
                self._change_state(_SafeState())
            else:
                if resolver(self.owner.panic_interaction):
                    if services.get_fire_service().has_infant_or_toddler_to_save_for_sim(sim_info):
                        self._change_state(_SaveInfantOrToddlerState())


class _SaveInfantOrToddlerState(SituationState):

    def on_activate(self, reader=None):
        logger.debug('Sim is entering the Save Infant or Toddler state during a fire.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.victim_job.situation_job, self.owner.victim_job.save_infant_or_toddler_state)
        for custom_key in self.owner.got_to_safety_interaction.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

    def _on_set_sim_role_state(self, sim, job_type, role_state_type, role_affordance_target):
        super()._on_set_sim_role_state(sim, job_type, role_state_type, role_affordance_target)
        infant_or_toddler = services.get_fire_service().get_infant_or_toddler_to_save_for_sim(sim.sim_info)
        if infant_or_toddler is None:
            self._change_state(_PanicState())
        InteractionCancelCompatibility.cancel_interactions_for_reason(sim, (InteractionCancelReason.DEATH),
          (FinishingType.FIRE),
          'Interaction was canceled due to saving an infant or toddler from a fire.',
          additional_cancel_sources=(
         InteractionSource.SCRIPT,))
        InteractionCancelCompatibility.cancel_interactions_for_reason(infant_or_toddler, (InteractionCancelReason.DEATH),
          (FinishingType.FIRE),
          'Interaction was canceled due to an infant or toddler being saved from a fire.',
          additional_cancel_sources=(
         InteractionSource.SCRIPT,))
        context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
          (Priority.High),
          client=None,
          pick=None)
        sim.push_super_affordance(self.owner.save_infant_or_toddler_interaction, infant_or_toddler, context)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
            if event is TestEvent.InteractionComplete and resolver(self.owner.got_to_safety_interaction):
                if services.get_fire_service().has_infant_or_toddler_to_save_for_sim(sim_info):
                    self._change_state(_SaveInfantOrToddlerState())
        else:
            self._change_state(_SafeState())


class _SafeState(SituationState):

    def on_activate(self, reader=None):
        logger.debug('Sim is entering the Safe State during a fire.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.victim_job.situation_job, self.owner.victim_job.fire_safe_state)
        for custom_key in self.owner.go_back_to_panic_interactions.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionStart, custom_key)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
        if event is TestEvent.InteractionStart:
            if resolver(self.owner.go_back_to_panic_interactions):
                if resolver.sim_info.get_sim_instance().is_on_active_lot():
                    self._change_state(_PanicState())


class _PostFireState(SituationState):

    def on_activate(self, reader=None):
        logger.debug('Sim is entering the Post Fire State during a fire.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.victim_job.situation_job, self.owner.victim_job.post_fire_state)
        self.owner._set_duration_alarm(duration_override=(self.owner.TIME_POST_FIRE_IN_SIM_MINUTES))
        for custom_key in self.owner.go_back_to_panic_interactions.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionStart, custom_key)

    def handle_event(self, sim_info, event, resolver):
        if event is TestEvent.InteractionStart:
            if resolver(self.owner.go_back_to_panic_interactions):
                self._change_state(_UnawareState())