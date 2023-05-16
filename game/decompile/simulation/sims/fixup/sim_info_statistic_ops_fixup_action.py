# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\fixup\sim_info_statistic_ops_fixup_action.py
# Compiled at: 2020-10-23 18:30:47
# Size of source mod 2**32: 857 bytes
from sims.fixup.sim_info_fixup_action import _SimInfoFixupAction
from sims4.tuning.tunable import TunableList
from statistics.statistic_ops import TunableStatisticChange
from event_testing.resolver import SingleSimResolver

class _SimInfoStatisticOpsFixupAction(_SimInfoFixupAction):
    FACTORY_TUNABLES = {'statistics_list': TunableList(description='\n            A list of Statistics Ops to run on the Sim.\n            ',
                          tunable=(TunableStatisticChange()))}

    def __call__(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        for statistic_op in self.statistics_list:
            statistic_op.apply_to_resolver(resolver)