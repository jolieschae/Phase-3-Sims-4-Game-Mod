# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\sim_backgroud_situation.py
# Compiled at: 2021-04-19 18:16:26
# Size of source mod 2**32: 3252 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import classproperty
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import BouncerRequestFactory
from situations.bouncer.bouncer_types import BouncerRequestPriority
from situations.situation import Situation
from situations.situation_complex import SituationStateData, TunableSituationJobAndRoleState
from situations.situation_types import SituationCreationUIOption, SituationSerializationOption
import situations.situation_complex

class _SimBackgroundSituationMainState(situations.situation_complex.SituationState):
    pass


class SimBackgroundSituation(situations.situation_complex.SituationComplexCommon):
    INSTANCE_TUNABLES = {'job_and_role_state': TunableSituationJobAndRoleState(description='\n            The job and role state for the sims\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classproperty
    def situation_serialization_option(cls):
        return SituationSerializationOption.DONT

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _SimBackgroundSituationMainState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.job_and_role_state.job, cls.job_and_role_state.role_state)]

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(_SimBackgroundSituationMainState())

    def _issue_requests(self):
        request = BouncerRequestFactory(self, callback_data=_RequestUserData(role_state_type=(self.job_and_role_state.role_state)),
          job_type=(self.job_and_role_state.job),
          request_priority=(BouncerRequestPriority.BACKGROUND_LOW),
          user_facing=False,
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(request)


lock_instance_tunables(SimBackgroundSituation, should_send_on_lot_home_in_super_speed_3=True,
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)