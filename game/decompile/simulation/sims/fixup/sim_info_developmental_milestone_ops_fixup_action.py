# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_developmental_milestone_ops_fixup_action.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 1066 bytes
from developmental_milestones.developmental_milestone_ops import DevelopmentalMilestoneStateChangeLootOp
from event_testing.resolver import SingleSimResolver
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import TunableList

class _SimInfoDevelopmentalMilestoneOpsFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'developmental_milestone_state_change_list': TunableList(description='\n            A list of Developmental Milestones State Change Ops to run on the Sim.\n            ',
                                                    tunable=(DevelopmentalMilestoneStateChangeLootOp.TunableFactory()))}

    def __call__(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for developmental_milestone_op in self.developmental_milestone_state_change_list:
            developmental_milestone_op.apply_to_resolver(resolver)