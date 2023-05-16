# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\SituationGoalMultipleSimsInRelationship.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 9069 bytes
import itertools, services, sims4
from event_testing.test_events import TestEvent
from sims4.math import Threshold
from sims.sim_info_types import Species
from sims4.tuning.tunable import TunableReference, TunableVariant, AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableOperator, TunableList, TunableTuple, TunableEnumSet
from situations.situation_goal import SituationGoal

class _RelbitCountStrategy(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'rel_bits':TunableList(description='\n            A list of Rel Bit entries.\n            ',
       tunable=TunableTuple(description='\n                Tuning for a single Rel Bit and whether we require it to be\n                present or absent in the target relationships.\n                ',
       rel_bit=TunableReference(description="\n                    The type of relationship we're looking for.\n                    \n                    In other words, we're looking for any relationship\n                    with this Rel Bit.\n                    ",
       manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))),
       action=TunableVariant(description='\n                    Whether we are checking for the presence or absence of\n                    the tuned Rel Bit.\n                    \n                    Require - We are checking for the presence of this Rel Bit.\n                    Prohibit - We are checking for the absence of this Rel Bit.\n                    ',
       locked_args={'require':True, 
      'prohibit':False},
       default='require'))), 
     'comparison':TunableOperator(description='\n            The comparison to perform against the target relationship count.\n            ',
       default=sims4.math.Operator.EQUAL), 
     'allowed_species':TunableEnumSet(description='\n            Only relationships with sims of these species are considered for the\n            goal.\n            \n            For example, if the goal is testing that all sims in the household\n            are friends with each other, we would want to constrain this to be\n            HUMAN only because dogs and cats use a different set of relationship\n            bits.\n            ',
       enum_type=Species,
       enum_default=Species.HUMAN,
       default_enum_list=[
      Species.HUMAN],
       allow_empty_set=False)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._owner = None

    def setup(self, owner):
        self._owner = owner

    @property
    def target_relationship_bit_count(self):
        raise NotImplementedError

    def is_testing_for_relbit(self, rel_bit):
        for rel_bit_tuple in self.rel_bits:
            if rel_bit_tuple.rel_bit.matches_bit(rel_bit):
                return True

        return False

    def is_complete(self):
        count = 0
        target_rel_bit_count = self.target_relationship_bit_count
        if target_rel_bit_count is None:
            return False
        threshold = Threshold(self.target_relationship_bit_count, self.comparison)
        rel_service = services.relationship_service()
        for sim_info_a, sim_info_b in itertools.permutations(self._owner.all_sim_infos_interested_in_goal_gen(), 2):
            if sim_info_a.species not in self.allowed_species or sim_info_b.species not in self.allowed_species:
                continue
            increase_count = True
            for rel_bit_tuple in self.rel_bits:
                if rel_service.has_bit(sim_info_a.id, sim_info_b.id, rel_bit_tuple.rel_bit) != rel_bit_tuple.action:
                    increase_count = False
                    break

            if increase_count:
                count += 1

        return threshold.compare(count)


class _AllRelationships(_RelbitCountStrategy):

    @property
    def target_relationship_bit_count(self):
        n = sum((1 for sim_info in self._owner.all_sim_infos_interested_in_goal_gen() if sim_info.species in self.allowed_species))
        if n == 0:
            return
        return n * n - n


class _TunedNumberOfRelationships(_RelbitCountStrategy):
    FACTORY_TUNABLES = {'_target_relationship_bit_count': TunableRange(description='\n            The number of relationship bits that this goal is testing against.\n            ',
                                         tunable_type=int,
                                         default=1,
                                         minimum=0)}

    @property
    def target_relationship_bit_count(self):
        return self._target_relationship_bit_count


class SituationGoalMultipleSimsInRelationship(SituationGoal):
    INSTANCE_TUNABLES = {'rel_bit_count_strategy': TunableVariant(description="\n            The number of relbits we're looking for.\n            \n            All Possible: This will test against every sim having the relbit with every other sim.\n            Tuned Literal: This will test a tuned number of sims having the relbit with one another.\n            ",
                                 display_name='Rel Bit Count',
                                 all_possible=(_AllRelationships.TunableFactory()),
                                 tuned_literal=(_TunedNumberOfRelationships.TunableFactory()),
                                 default='all_possible')}

    def setup(self):
        super().setup()
        event_manager = services.get_event_manager()
        event_manager.register_single_event(self, TestEvent.AddRelationshipBit)
        event_manager.register_single_event(self, TestEvent.RemoveRelationshipBit)
        self.rel_bit_count_strategy.setup(self)

    def _decommision(self):
        event_manager = services.get_event_manager()
        event_manager.unregister_single_event(self, TestEvent.AddRelationshipBit)
        event_manager.unregister_single_event(self, TestEvent.RemoveRelationshipBit)
        super()._decommision()

    def handle_event(self, sim_info, event, resolver):
        if not self._valid_event_sim_of_interest(sim_info):
            return
        else:
            target_sim_id = resolver.event_kwargs.get('target_sim_id', 0)
            if not target_sim_id:
                return
            target_sim_info = services.sim_info_manager().get(target_sim_id)
            if not self._valid_event_sim_of_interest(target_sim_info):
                return
            relationship_bit = resolver.event_kwargs.get('relationship_bit', None)
            if relationship_bit is not None:
                return self.rel_bit_count_strategy.is_testing_for_relbit(relationship_bit) or None
        if self._run_goal_completion_tests(sim_info, event, resolver):
            self._increment_completion_count()

    def _run_goal_completion_tests(self, sim_info, event, resolver):
        if not self.rel_bit_count_strategy.is_complete():
            return False
        return super()._run_goal_completion_tests(sim_info, event, resolver)


sims4.tuning.instances.lock_instance_tunables(SituationGoalMultipleSimsInRelationship, _iterations=1)