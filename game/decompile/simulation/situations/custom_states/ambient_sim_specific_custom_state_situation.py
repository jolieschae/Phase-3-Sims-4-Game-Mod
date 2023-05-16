# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\ambient_sim_specific_custom_state_situation.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 1103 bytes
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_types import BouncerRequestPriority
from situations.bouncer.specific_sim_request_factory import SpecificSimRequestFactory
from situations.custom_states.custom_states_situation import CustomStatesSituation

class AmbientSimSpecificCustomStatesSituation(CustomStatesSituation):

    def _issue_requests(self):
        request = SpecificSimRequestFactory(self, _RequestUserData(), self.default_job(), BouncerRequestPriority.EVENT_DEFAULT_JOB, self.exclusivity, self._guest_list.host_sim_id)
        self.manager.bouncer.submit_request(request)