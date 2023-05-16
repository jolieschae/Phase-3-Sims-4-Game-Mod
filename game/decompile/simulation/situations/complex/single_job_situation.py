# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\single_job_situation.py
# Compiled at: 2015-04-03 17:58:58
# Size of source mod 2**32: 1852 bytes
from role.role_state import RoleState
from sims4.tuning.tunable import TunableTuple
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationState, SituationStateData
from situations.situation_job import SituationJob

class SingleJobSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'job': TunableTuple(description='\n            The job and role which the career Sim is placed into.\n            ',
              situation_job=SituationJob.TunableReference(description='\n                A reference to a SituationJob that can be performed at this Situation.\n                '),
              role_state=RoleState.TunableReference(description='\n                A role state the Sim assigned to the job will perform.\n                '))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, SingleJobSituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.job.situation_job, cls.job.role_state)]

    @classmethod
    def default_job(cls):
        return cls.job.situation_job

    def start_situation(self):
        super().start_situation()
        self._change_state(SingleJobSituationState())


class SingleJobSituationState(SituationState):
    pass