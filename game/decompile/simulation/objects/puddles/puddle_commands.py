# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\puddles\puddle_commands.py
# Compiled at: 2015-05-06 20:55:29
# Size of source mod 2**32: 1671 bytes
from objects.puddles import create_puddle, PuddleSize, PuddleLiquid
from objects.puddles.puddle import Puddle
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam
import sims4.commands

@sims4.commands.Command('puddles.create')
def puddle_create(count: int=1, size: PuddleSize=PuddleSize.MediumPuddle, liquid=PuddleLiquid.WATER, obj: OptionalTargetParam=None, _connection=None):
    obj = get_optional_target(obj, _connection)
    if obj is None:
        return False
    for _ in range(count):
        puddle = create_puddle(size, liquid)
        if puddle is None:
            return False
        puddle.place_puddle(obj, max_distance=8)

    return True


@sims4.commands.Command('puddles.evaporate')
def puddle_evaporate(obj_id: RequiredTargetParam, _connection=None):
    obj = obj_id.get_target()
    if obj is None:
        return False
    else:
        return isinstance(obj, Puddle) or False
    obj.evaporate(None)
    return True


@sims4.commands.Command('puddles.grow')
def puddle_grow(obj_id: RequiredTargetParam, _connection=None):
    obj = obj_id.get_target()
    if obj is None:
        return False
    else:
        return isinstance(obj, Puddle) or False
    obj.try_grow_puddle()
    return True