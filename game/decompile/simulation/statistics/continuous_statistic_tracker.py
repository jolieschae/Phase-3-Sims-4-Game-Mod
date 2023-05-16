# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\continuous_statistic_tracker.py
# Compiled at: 2020-01-10 19:34:09
# Size of source mod 2**32: 2160 bytes
import sims4.log, statistics.base_statistic_tracker, services
logger = sims4.log.Logger('Statistic')

class ContinuousStatisticTracker(statistics.base_statistic_tracker.BaseStatisticTracker):
    __slots__ = ()

    def get_decay_time(self, stat_type, threshold):
        stat = self.get_statistic(stat_type)
        if stat is not None:
            return stat.get_decay_time(threshold)

    def debug_output_all(self, _connection):
        if self._statistics is None:
            return
        stat_iter = (stat for stat in self._statistics.values() if stat is not None)
        for stat in sorted((list(stat_iter)), key=(lambda stat: stat.stat_type.__name__)):
            sims4.commands.output('{:<44} ID:{:<6} Value: {:-8.2f}, Decay: {:-5.2f}, ChangeRate: {:-5.2f}'.format(stat.__class__.__name__, stat.guid64, stat.get_value(), stat.get_decay_rate(), stat.get_change_rate()), _connection)

    def debug_output_all_automation(self, _connection):
        if self._statistics is None:
            return
        stat_iter = (stat for stat in self._statistics.values() if stat is not None)
        for stat in list(stat_iter):
            sims4.commands.automation_output('CommodityInfo; Type:DATA, Name:{}, Value:{}, Decay:{}'.format(stat.__class__.__name__, stat.get_value(), stat.get_decay_rate()), _connection)

    def set_convergence(self, stat_type, convergence):
        if convergence != stat_type.default_convergence_value:
            stat_inst = self.get_statistic(stat_type, add=(stat_type.add_if_not_in_tracker))
        else:
            stat_inst = self.get_statistic(stat_type)
        if stat_inst is not None:
            if stat_inst.convergence_value != convergence:
                stat_inst.convergence_value = convergence

    def reset_convergence(self, stat_type):
        stat_inst = self.get_statistic(stat_type)
        if stat_inst is not None:
            stat_inst.reset_convergence_value()