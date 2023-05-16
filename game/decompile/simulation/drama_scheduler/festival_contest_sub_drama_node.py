# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\festival_contest_sub_drama_node.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 2053 bytes
import services
from date_and_time import create_time_span
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from drama_scheduler.festival_contest_drama_node_mixin import FestivalContestDramaNodeMixin
from drama_scheduler.festival_drama_node import FestivalDramaNode
from sims4.utils import classproperty

class FestivalContestSubDramaNode(FestivalContestDramaNodeMixin, BaseDramaNode):

    @classproperty
    def simless(cls):
        return True

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.FESTIVAL

    @classproperty
    def persist_when_active(cls):
        return True

    def _try_and_start_festival(self, from_resume=False):
        if self.festival_contest_tuning is None:
            return
        self._setup_score_add_alarm()

    def is_during_contest(self):
        return True

    def _run(self):
        self._try_and_start_festival()
        return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE

    def resume(self):
        if self._get_remaining_contest_time() < 0:
            services.drama_scheduler_service().complete_node(self.uid)
        self._try_and_start_festival(from_resume=True)

    def _get_remaining_contest_time(self):
        now = services.time_service().sim_now
        time_since_started = now - self._selected_time
        duration = create_time_span(minutes=(self.festival_contest_tuning._contest_duration))
        time_left_to_go = duration - time_since_started
        return time_left_to_go

    def is_during_pre_festival(self):
        return False

    def is_festival_contest_sub_node(self):
        return True