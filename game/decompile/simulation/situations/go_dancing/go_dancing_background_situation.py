# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\go_dancing\go_dancing_background_situation.py
# Compiled at: 2015-07-06 17:17:29
# Size of source mod 2**32: 4100 bytes
from sims4.tuning.instances import lock_instance_tunables
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import SelectableSimRequestFactory
from situations.bouncer.bouncer_types import BouncerExclusivityCategory
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationStateData, TunableSituationJobAndRoleState, SituationState
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo, SituationInvitationPurpose
from situations.situation_types import SituationCreationUIOption
import services

class _GoDancingGenericState(SituationState):
    pass


class GoDancingBackgroundSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'generic_sim_job':TunableSituationJobAndRoleState(description="\n            A job and role state that essentially does nothing but filter out\n            Sims that shouldn't be placed in the party-goer situation.\n            "), 
     'party_goer_situation':Situation.TunableReference(description='\n            The individual, party-goer situation we want to use for\n            Sims that show up at the party so they want to dance and more.\n            ',
       class_restrictions=('GoDancingBackgroundPartyGoerSituation', ))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _GoDancingGenericState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.generic_sim_job.job, cls.generic_sim_job.role_state)]

    @classmethod
    def default_job(cls):
        return cls.generic_sim_job.job

    def start_situation(self):
        super().start_situation()
        self._change_state(_GoDancingGenericState())

    def _issue_requests(self):
        request = SelectableSimRequestFactory(self, callback_data=_RequestUserData(role_state_type=(self.generic_sim_job.role_state)),
          job_type=(self.generic_sim_job.job),
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(request)

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        situation_manager = services.get_zone_situation_manager()
        guest_list = SituationGuestList(invite_only=True)
        guest_info = SituationGuestInfo.construct_from_purpose(sim.sim_info.id, self.party_goer_situation.default_job(), SituationInvitationPurpose.INVITED)
        guest_list.add_guest_info(guest_info)
        situation_manager.create_situation((self.party_goer_situation), guest_list=guest_list,
          user_facing=False)


lock_instance_tunables(GoDancingBackgroundSituation, exclusivity=(BouncerExclusivityCategory.PRE_VISIT),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=False)