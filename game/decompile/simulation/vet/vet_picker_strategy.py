# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\vet\vet_picker_strategy.py
# Compiled at: 2017-08-29 16:59:17
# Size of source mod 2**32: 1296 bytes
from interactions.base.picker_strategy import SimPickerEnumerationStrategy
from vet.vet_clinic_handlers import log_vet_flow_entry
from vet.vet_clinic_utils import get_vet_clinic_zone_director

class VetCustomerPickerEnumerationStrategy(SimPickerEnumerationStrategy):

    def find_best_choice(self, si):
        if not self._choices:
            return
        actor_id = si.sim.sim_id
        vzd = get_vet_clinic_zone_director()
        if vzd is None:
            return
        waiting_sim_infos = tuple((result.sim_info for result in self._choices))
        for pet in vzd.waiting_sims_gen(actor_id):
            if pet.sim_info in waiting_sim_infos:
                log_vet_flow_entry(repr(si.sim), type(self).__name__, '{} chose {}'.format(repr(si), repr(pet.sim_info)))
                vzd.reserve_waiting_sim(pet.sim_id, actor_id)
                return pet.sim_id