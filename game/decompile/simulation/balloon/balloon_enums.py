# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\balloon\balloon_enums.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1114 bytes
from protocolbuffers import Sims_pb2
import enum

class BalloonTypeEnum(enum.Int):
    THOUGHT = 0
    SPEECH = 1
    DISTRESS = 2
    SENTIMENT = 3
    SENTIMENT_INFANT = 4


BALLOON_TYPE_LOOKUP = {BalloonTypeEnum.THOUGHT: (Sims_pb2.AddBalloon.THOUGHT_TYPE, Sims_pb2.AddBalloon.THOUGHT_PRIORITY), 
 BalloonTypeEnum.SPEECH: (Sims_pb2.AddBalloon.SPEECH_TYPE, Sims_pb2.AddBalloon.SPEECH_PRIORITY), 
 BalloonTypeEnum.DISTRESS: (Sims_pb2.AddBalloon.DISTRESS_TYPE, Sims_pb2.AddBalloon.MOTIVE_FAILURE_PRIORITY), 
 BalloonTypeEnum.SENTIMENT: (Sims_pb2.AddBalloon.SENTIMENT_TYPE, Sims_pb2.AddBalloon.SENTIMENT_PRIORITY), 
 BalloonTypeEnum.SENTIMENT_INFANT: (Sims_pb2.AddBalloon.SENTIMENT_INFANT_TYPE, Sims_pb2.AddBalloon.SENTIMENT_INFANT_PRIORITY)}