# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\drama_node_do_nothing.py
# Compiled at: 2021-04-12 16:05:24
# Size of source mod 2**32: 513 bytes
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeRunOutcome
from sims4.utils import classproperty

class DoNothingDramaNode(BaseDramaNode):

    @classproperty
    def simless(cls):
        return True

    def _run(self):
        return DramaNodeRunOutcome.SUCCESS_NODE_COMPLETE