# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\visiting\keyholder_visiting_situation.py
# Compiled at: 2018-07-18 19:19:19
# Size of source mod 2**32: 2425 bytes
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable_base import GroupNames
from situations.situation import Situation
from situations.situation_complex import SituationStateData
from situations.situation_types import SituationCreationUIOption
from situations.visiting.visiting_situation_common import VisitingNPCSituation
import role.role_state, sims4.tuning.tunable, situations.bouncer.bouncer_types, situations.situation_complex

class KeyholderVisitSituationState(situations.situation_complex.SituationState):
    pass


class KeyholderVisitSituation(VisitingNPCSituation):
    INSTANCE_TUNABLES = {'greeted_keyholder_sims': sims4.tuning.tunable.TunableTuple(situation_job=situations.situation_job.SituationJob.TunableReference(description='\n                    The job given to keyholders in the visiting situation.\n                    '),
                                 role_state=role.role_state.RoleState.TunableReference(description='\n                    The role state given to keyholders in the visiting situation.\n                    '),
                                 tuning_group=(GroupNames.ROLES))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, KeyholderVisitSituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.greeted_npc_sims.situation_job, cls.greeted_npc_sims.role_state)]

    @classmethod
    def default_job(cls):
        return cls.greeted_npc_sims.situation_job

    def start_situation(self):
        super().start_situation()
        self._change_state(KeyholderVisitSituationState())


lock_instance_tunables(KeyholderVisitSituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.VISIT),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=True)