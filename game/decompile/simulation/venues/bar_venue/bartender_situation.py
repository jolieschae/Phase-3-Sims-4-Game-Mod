# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\bar_venue\bartender_situation.py
# Compiled at: 2021-05-03 17:42:45
# Size of source mod 2**32: 3559 bytes
import services, sims4
from sims4.tuning.instances import lock_instance_tunables
from sims4.utils import classproperty
from situations.bouncer.bouncer_types import BouncerExclusivityCategory, RequestSpawningOption, BouncerRequestPriority
from situations.situation import Situation
from situations.situation_complex import SituationState, SituationComplexCommon, TunableSituationJobAndRoleState, SituationStateData
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from situations.situation_types import SituationCreationUIOption
logger = sims4.log.Logger('BartenderSituation')

class _BartenderSituationState(SituationState):
    pass


class BartenderSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'bartender_job_and_role': TunableSituationJobAndRoleState(description='\n            The job and role of the bartender.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _BartenderSituationState),)

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.bartender_job_and_role.job, cls.bartender_job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(_BartenderSituationState())


lock_instance_tunables(BartenderSituation, exclusivity=(BouncerExclusivityCategory.VENUE_EMPLOYEE),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=False)

class BartenderSpecificSimSituation(BartenderSituation):

    @classmethod
    def get_predefined_guest_list(cls):
        guest_list = SituationGuestList(invite_only=True)
        active_sim_info = services.active_sim_info()
        filter_result = services.sim_filter_service().submit_matching_filter(sim_filter=(cls.bartender_job_and_role.job.filter), callback=None,
          requesting_sim_info=active_sim_info,
          allow_yielding=False,
          allow_instanced_sims=True,
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        if not filter_result:
            logger.error('Failed to find/create any sims for {}.', cls)
            return guest_list
        guest_list.add_guest_info(SituationGuestInfo(filter_result[0].sim_info.sim_id, cls.bartender_job_and_role.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
        return guest_list