# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\event_data_const.py
# Compiled at: 2020-04-20 12:44:12
# Size of source mod 2**32: 1164 bytes
import enum

class ObjectiveDataStorageType(enum.Int, export=False):
    CountData = ...
    IdData = ...


class DataType(enum.Int, export=False):
    RelationshipData = 1
    SimoleanData = 2
    TimeData = 3
    TravelData = 5
    ObjectiveCount = 6
    CareerData = 7
    TagData = 8
    RelativeStartingData = 9
    ClubBucks = 10
    TimeInClubGatherings = 11
    Mood = 12
    BucksData = 13


class RelationshipData(enum.Int, export=False):
    CurrentRelationships = 0
    TotalRelationships = 1


class SimoleonData(enum.Int):
    MoneyFromEvents = 0
    TotalMoneyEarned = 1


class TimeData(enum.Int, export=False):
    SimTime = 0
    ServerTime = 1


class TagData(enum.Int, export=False):
    SimoleonsEarned = 0
    TimeElapsed = 1