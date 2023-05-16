# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\pool_venue\lounger_situation.py
# Compiled at: 2020-01-21 17:33:11
# Size of source mod 2**32: 1880 bytes
import random
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableSimMinute
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationState, SituationComplexCommon, TunableSituationJobAndRoleState, SituationStateData
from situations.situation_types import SituationCreationUIOption

class _LoungerSituationState(SituationState):
    pass


class PoolVenueLoungerSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'lounger_job_and_role': TunableSituationJobAndRoleState(description='\n            The job and role for Pool Venue lounger.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _LoungerSituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.lounger_job_and_role.job, cls.lounger_job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        return cls.lounger_job_and_role.job

    def start_situation(self):
        super().start_situation()
        self._change_state(_LoungerSituationState())


lock_instance_tunables(PoolVenueLoungerSituation, exclusivity=(BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)