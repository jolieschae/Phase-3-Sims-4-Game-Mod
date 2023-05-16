# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\bouncer\specific_sim_request_factory.py
# Compiled at: 2018-09-17 14:23:26
# Size of source mod 2**32: 871 bytes
from situations.bouncer.bouncer_request import BouncerRequestFactory

class SpecificSimRequestFactory(BouncerRequestFactory):

    def __init__(self, situation, callback_data, job_type, request_priority, exclusivity, sim_id):
        super().__init__(situation, callback_data=callback_data,
          job_type=job_type,
          request_priority=request_priority,
          user_facing=False,
          exclusivity=exclusivity)
        self._sim_id = sim_id

    def _can_assign_sim_to_request(self, sim):
        return sim.sim_id == self._sim_id