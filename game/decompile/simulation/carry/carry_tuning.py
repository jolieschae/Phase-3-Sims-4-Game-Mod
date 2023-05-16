# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\carry\carry_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 6254 bytes
from event_testing.tests import TunableTestSet
from postures import PostureTrack
from sims4.tuning.tunable import TunableReference, TunableTuple, TunableMapping, TunableEnumEntry, TunableList, TunablePackSafeReference, Tunable, TunableRange
import services, sims4.resources
from sims4.tuning.tunable_hash import TunableStringHash32
from tunable_multiplier import TestedSum

class CarryPostureStaticTuning:
    POSTURE_CARRY_NOTHING = TunableReference(description='\n            Reference to the posture that represents carrying nothing\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)),
      class_restrictions='CarryingNothing')
    POSTURE_CARRY_OBJECT = TunableReference(description='\n        Reference to the posture that represents carrying an Object\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)),
      class_restrictions='CarryingObject')


class CarryTuning:
    RALLY_INTERACTION_CARRY_RULES = TunableTuple(description='\n        Global rules related to carry while running rally interactions.\n        ',
      min_carry_distance=Tunable(description="\n            Only initiate carry if the carryable sim's route distance is larger than this min distance. \n            ",
      tunable_type=float,
      default=1),
      wait_to_carry_affordance=TunableReference(description='\n            The affordance to push to a carrying sim while they are waiting the carryable sim to drag them into carry.\n            This affordance is just for the player UI feedback purpose, should do nothing but show an icon in the\n            interaction queue indicating the sim is doing something.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))))
    CARRY_PATH_CONSTRAINT_RULES = TunableTuple(description='\n        Global rules related to Carry Path Constraint.\n        ',
      min_carry_distance=Tunable(description="\n            Only initiate carry if the carryable sim's route distance is larger than this min distance. \n            ",
      tunable_type=float,
      default=1))
    CARRYABLE_SIMS_FIXUP_RULES = TunableTuple(description="\n        Fixup rules for carryable sims in different scenarios (such as after travel, moving into a lot, being adopted)\n        We use these rules to carry sims (especially infants) immediately in those scenarios so they won't look bad\n        laying on the ground.\n        ",
      carry_hand_affordance_mappings=TunableMapping(description='\n            A mapping of carry hand to carry rules. Usually each hand can carry one carryable sim.\n            ',
      key_type=TunableEnumEntry(description="\n                The carrying sim's carry hand.\n                ",
      tunable_type=PostureTrack,
      default=(PostureTrack.RIGHT)),
      value_type=TunableList(description='\n                Carry owning affordances and corresponding joint for the carry hand.\n                ',
      tunable=TunableTuple(owning_affordance=TunablePackSafeReference(description='\n                        The affordance to push a Sim to carry the carryable sim. We run \n                        affordance tests against the carryable sim, if all affordances \n                        in the list fails we will skip that sim and try the next carryable sim.\n                        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      parenting_joint=TunableStringHash32(description='\n                        The joint of the carrier sim to parent the carryable sim to.\n                        ')))),
      priority_test_sums=TestedSum.TunableFactory(description='\n            Tested sums to create a priority list for carryable sims. We will try to carry sims\n            who has highest scores first.\n            '),
      carryable_sim_eligibility_tests=TunableTestSet(description='\n            Tunable tests that run on carryable sims to check if we should carry \n            them at all.\n            '),
      carrying_sim_eligibility_tests=TunableTestSet(description='\n            Tunable tests that run on carrying sims to check eligibility for\n            carrying any sim.\n            '))
    MAXIMUM_PUTDOWN_DERAILMENT = TunableRange(description="\n        The maximum putdown derailment request for each interaction.\n        An interaction will request putdown derailment to wait for the carried sim to be putdown somewwhere.\n        After the initial putdown, the interaction may keep requesting putdown derailment if the new location\n        still doesn't satisfy the constraint (either due to bugs or as designed). To prevent them from getting\n        into this pickup-putdown loop, we added this constant to restrict the maximum derailment request.\n        ",
      tunable_type=int,
      default=1,
      minimum=1)
    PUTDOWN_DERAILMENT_INTERACTION_MAP = TunableMapping(description='\n        Mapping of specific interactions to a maximum putdown derailment request count.\n        The values tuned here will override the MAXIMUM_PUTDOWN_DERAILMENT tuned value \n        ONLY for the interactions tuned here.\n        ',
      key_type=TunablePackSafeReference(description='\n            The interaction requesting putdown derailments.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION))),
      value_type=TunableRange(description='\n            The maximum putdown derailment request count for this interaction.\n            ',
      tunable_type=int,
      default=1,
      minimum=1))