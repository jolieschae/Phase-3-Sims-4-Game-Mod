# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_bit_add.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 3912 bytes
from relationships.relationship_track import RelationshipTrack
from interactions.utils.loot_basic_op import BaseLootOperation
from relationships.relationship_bit import RelationshipBit
from sims4.tuning.tunable import TunableReference, TunableRange, TunableList, TunableTuple, Tunable
import interactions.utils, services, sims4

class RelationshipBitOnFilteredSims(BaseLootOperation):
    FACTORY_TUNABLES = {'rel_bits':TunableList(description='\n            List of relationship bits to add onto the sims that match the filter.\n            ',
       tunable=RelationshipBit.TunablePackSafeReference(description='\n                A relationship bit to add onto the sims that match the filter.\n                ')), 
     'relationship_score':Tunable(description='\n            The relationship score to add to sims that match the filter.\n            ',
       default=1,
       tunable_type=int), 
     'filter_settings':TunableTuple(sim_filter=TunableReference(description='\n                A filter to apply on the sim population.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER))),
       desired_sim_count=TunableRange(description='\n                The desired number of Sims to add rel bits to.\n                ',
       tunable_type=int,
       default=1,
       minimum=1),
       use_requesting_sim=Tunable(description='\n                If checked, use the subject as the requesting sim info\n                for the usage of using relationship constraints.\n                ',
       tunable_type=bool,
       default=False))}

    def __init__(self, rel_bits, relationship_score, filter_settings, **kwargs):
        (super().__init__)(**kwargs)
        self._rel_bits = rel_bits
        self._rel_score = relationship_score
        self._filter_settings = filter_settings

    @property
    def loot_type(self):
        return interactions.utils.LootType.RELATIONSHIP_BIT

    def _apply_to_subject_and_target(self, subject, target, resolver):
        relationship_tracker = subject.relationship_tracker

        def filter_callback(filter_results, bouncer_request):
            for result in filter_results:
                for rel_bit in self._rel_bits:
                    relationship_tracker.add_relationship_score(result.sim_info.sim_id, self._rel_score)
                    relationship_tracker.add_relationship_bit(result.sim_info.sim_id, rel_bit)

        requesting_sim = subject if self._filter_settings.use_requesting_sim else None
        filter_service = services.sim_filter_service()
        filter_service.submit_matching_filter(number_of_sims_to_find=(self._filter_settings.desired_sim_count), sim_filter=(self._filter_settings.sim_filter),
          callback=filter_callback,
          requesting_sim_info=requesting_sim,
          blacklist_sim_ids={
         subject.id},
          gsi_source_fn=(lambda: 'RelationshipBitOnFilteredSims Loot: Adding {} to filtered sims'.format(str(self._rel_bits))))