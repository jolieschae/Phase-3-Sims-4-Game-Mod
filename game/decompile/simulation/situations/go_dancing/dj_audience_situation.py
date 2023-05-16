# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\go_dancing\dj_audience_situation.py
# Compiled at: 2015-07-06 13:55:00
# Size of source mod 2**32: 2190 bytes
from sims4.tuning.instances import lock_instance_tunables
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationStateData, CommonSituationState, TunableSituationJobAndRoleState
from situations.situation_types import SituationCreationUIOption

class _DjAudienceState(CommonSituationState):
    pass


class DjAudienceSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'dj_audience_state':_DjAudienceState.TunableFactory(description='\n            The main state for a dj audience Sim.\n            ',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP,
       display_name='01_dj_audience_state'), 
     'dj_audience_job_and_role':TunableSituationJobAndRoleState(description='\n            The job and role state for the dj audience members.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _DjAudienceState, factory=(cls.dj_audience_state)),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.dj_audience_job_and_role.job, cls.dj_audience_job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        return cls.dj_audience_job_and_role.situation_job

    def start_situation(self):
        super().start_situation()
        self._change_state(self.dj_audience_state())


lock_instance_tunables(DjAudienceSituation, exclusivity=(BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)