# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\focus\focus_ops.py
# Compiled at: 2018-04-18 17:02:11
# Size of source mod 2**32: 630 bytes
from protocolbuffers import DistributorOps_pb2
from distributor.ops import Op

class SetFocusScore(Op):

    def __init__(self, focus_score):
        super().__init__()
        self.op = DistributorOps_pb2.SetFocusScore()
        focus_score.populate_focus_score_msg(self.op)

    def write(self, msg):
        self.serialize_op(msg, self.op, DistributorOps_pb2.Operation.SET_FOCUS_SCORE)