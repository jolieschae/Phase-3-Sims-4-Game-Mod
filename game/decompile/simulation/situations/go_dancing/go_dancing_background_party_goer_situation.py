# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\go_dancing\go_dancing_background_party_goer_situation.py
# Compiled at: 2015-07-06 22:03:37
# Size of source mod 2**32: 2225 bytes
from sims4.tuning.instances import lock_instance_tunables
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationStateData, CommonSituationState, TunableSituationJobAndRoleState
from situations.situation_types import SituationCreationUIOption

class _PartyGoerState(CommonSituationState):
    pass


class GoDancingBackgroundPartyGoerSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'party_goer_state':_PartyGoerState.TunableFactory(description='\n            The state for party goers at the go dancing scenario.\n            ',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP,
       display_name='01_party_goer_state'), 
     'party_goer_job_and_role':TunableSituationJobAndRoleState(description='\n            The job and role state for a party goer.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _PartyGoerState, factory=(cls.party_goer_state)),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.party_goer_job_and_role.job, cls.party_goer_job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        return cls.party_goer_job_and_role.job

    def start_situation(self):
        super().start_situation()
        self._change_state(self.party_goer_state())


lock_instance_tunables(GoDancingBackgroundPartyGoerSituation, exclusivity=(BouncerExclusivityCategory.NORMAL),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)