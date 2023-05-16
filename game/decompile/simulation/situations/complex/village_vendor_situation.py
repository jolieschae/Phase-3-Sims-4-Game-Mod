# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\village_vendor_situation.py
# Compiled at: 2021-04-20 18:17:35
# Size of source mod 2**32: 2239 bytes
from situations.ambient.tend_object_situation import TendObjectSituation
from situations.bouncer.bouncer_types import RequestSpawningOption, BouncerRequestPriority
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
import services, sims4
logger = sims4.log.Logger('VillageVendorSituation', default_owner='yozhang')

class VillageVendorSituation(TendObjectSituation):
    pass


class VillageVendorSpecificSimSituation(VillageVendorSituation):

    @classmethod
    def get_predefined_guest_list(cls):
        guest_list = SituationGuestList(invite_only=True)
        active_sim_info = services.active_sim_info()
        filter_result = services.sim_filter_service().submit_matching_filter(sim_filter=(cls.tendor_job_and_role_state.job.filter), callback=None,
          requesting_sim_info=active_sim_info,
          allow_yielding=False,
          allow_instanced_sims=True,
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        if not filter_result:
            logger.error('Failed to find/create any sims for {}.', cls)
            return guest_list
        guest_list.add_guest_info(SituationGuestInfo(filter_result[0].sim_info.sim_id, cls.tendor_job_and_role_state.job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
        return guest_list