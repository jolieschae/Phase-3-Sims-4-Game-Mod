# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\socials\bouquet_toss_group.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 3539 bytes
from event_testing.register_test_event_mixin import RegisterTestEventMixin
from event_testing.test_events import TestEvent
from interactions import ParticipantType
from interactions.constraint_variants import TunableConstraintVariant
from interactions.constraints import Anywhere
from interactions.interaction_finisher import FinishingType
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableList
from situations.situation_complex import TunableInteractionOfInterest
from socials.group import SocialGroup
import sims4
logger = sims4.log.Logger('Bouquet Toss')

class BouquetTossGroup(RegisterTestEventMixin, SocialGroup):
    INSTANCE_TUNABLES = {'non_leader_constraint':TunableList(tunable=TunableConstraintVariant(description='\n                Constraints for sims in this group that are not the leader. The\n                target of these constraints is the group leader. \n                ')), 
     'bouquet_toss_interactions':TunableInteractionOfInterest(description='\n            Interactions that will end the social group. Used for ending the \n            group when the toss occurs.\n            ')}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        for custom_key in self.bouquet_toss_interactions.custom_keys_gen():
            self._register_test_event(TestEvent.InteractionComplete, custom_key)

    def handle_event(self, _, event, resolver):
        if event == TestEvent.InteractionComplete:
            if resolver(self.bouquet_toss_interactions):
                self.shutdown(FinishingType.NATURAL)

    def shutdown(self, finishing_type):
        super().shutdown(finishing_type)
        self._unregister_for_all_test_events()

    @classmethod
    def make_constraint_default(cls, sim, target, position, routing_surface, participant_type=ParticipantType.Actor, picked_object=None, **kwargs):
        final_constraint = Anywhere()
        for constraint_tuning in cls.non_leader_constraint:
            constraint = constraint_tuning.create_constraint(sim, sim)
            final_constraint = final_constraint.intersect(constraint)

        return final_constraint

    def _get_constraint(self, sim):
        if sim is self.group_leader_sim:
            return Anywhere()
        return self._constraint

    def refresh_social_geometry(self, sim=None):
        if sim is self.group_leader_sim:
            self.regenerate_constraint_and_validate_members()
        super().refresh_social_geometry(sim=sim)


lock_instance_tunables(BouquetTossGroup, include_default_facing_constraint=False)