# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\leave_situation.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 10166 bytes
import services
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from situations.bouncer.bouncer_request import RequestSpawningOption
from situations.bouncer.bouncer_types import BouncerRequestPriority
from situations.situation import Situation
from situations.situation_complex import SituationStateData
import alarms, clock, role.role_state, sims4.tuning.tunable, situations.base_situation, situations.bouncer.bouncer_request, situations.situation_complex, situations.situation_guest_list, situations.situation_job

class LeaveSituation(situations.situation_complex.SituationComplexCommon):
    INSTANCE_TUNABLES = {'leaving_soon':sims4.tuning.tunable.TunableTuple(situation_job=situations.situation_job.SituationJob.TunableReference(description='\n                                The job given to sims that we want to have leave the lot soon.\n                                '),
       role_state=role.role_state.RoleState.TunableReference(description='\n                                The role state given to the sim that we want to have leave the lot soon.\n                                '),
       tuning_group=GroupNames.ROLES), 
     'leaving_now':sims4.tuning.tunable.TunableTuple(situation_job=situations.situation_job.SituationJob.TunableReference(description='\n                                The job given to sims that we want to have leave the lot now.\n                                '),
       role_state=role.role_state.RoleState.TunableReference(description='\n                                The role state given to the sim to get them off the lot now.\n                                '),
       tuning_group=GroupNames.ROLES)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._leave_enabled = True
        self._leave_request = None

    @classmethod
    def _states(cls):
        return (SituationStateData(1, ForeverState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.leaving_soon.situation_job, cls.leaving_soon.role_state), (cls.leaving_now.situation_job, cls.leaving_now.role_state)]

    @classmethod
    def default_job(cls):
        return cls.leaving_now.situation_job

    def _get_duration(self):
        return 0

    def start_situation(self):
        super().start_situation()
        self._change_state(ForeverState())

    def _create_uninvited_request(self):
        if self._leave_request is not None:
            return
        self._leave_request = situations.bouncer.bouncer_request.BouncerNPCFallbackRequestFactory(self, callback_data=(situations.base_situation._RequestUserData()),
          job_type=(self.leaving_soon.situation_job),
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(self._leave_request)

    def invite_sim_to_leave(self, sim):
        if not self._leave_enabled:
            return
        guest_info = situations.situation_guest_list.SituationGuestInfo((sim.id), (self.leaving_soon.situation_job),
          (RequestSpawningOption.CANNOT_SPAWN),
          (BouncerRequestPriority.EVENT_VIP),
          expectation_preference=True)
        request = self._create_request_from_guest_info(guest_info)
        self.manager.bouncer.submit_request(request)

    @property
    def leave_enabled(self):
        return self._leave_enabled

    def set_leave_enabled(self, enable):
        self._leave_enabled = enable
        if enable and self._leave_request is None:
            self._create_uninvited_request()
        else:
            if not enable:
                if self._leave_request is not None:
                    situation_manager = services.get_zone_situation_manager()
                    for sim in tuple(self.all_sims_in_situation_gen()):
                        situation_manager.remove_sim_from_situation(sim, self.id)

                    self.manager.bouncer.withdraw_request(self._leave_request)
                    self._leave_request = None

    @property
    def _should_cancel_leave_interaction_on_premature_removal(self):
        return True

    @classproperty
    def situation_serialization_option(cls):
        return situations.situation_types.SituationSerializationOption.OPEN_STREETS


class ForeverState(situations.situation_complex.SituationState):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        self._handle = alarms.add_alarm(self, (clock.interval_in_sim_minutes(5)),
          (lambda _: self.timer_expired()),
          repeating=True,
          repeating_time_span=(clock.interval_in_sim_minutes(5)))

    def on_deactivate(self):
        super().on_deactivate()
        if self._handle is not None:
            alarms.cancel_alarm(self._handle)

    def timer_expired(self):
        sims = list(self.owner.all_sims_in_situation_gen())
        for sim in sims:
            if self.owner.sim_has_job(sim, self.owner.leaving_soon.situation_job):
                self.owner._set_job_for_sim(sim, self.owner.leaving_now.situation_job)