# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\puddles\__init__.py
# Compiled at: 2018-02-22 14:33:51
# Size of source mod 2**32: 1954 bytes
import random
from objects.definition_manager import TunableDefinitionList
from sims4.tuning.dynamic_enum import DynamicEnum
import enum, objects.system, sims4.reload
with sims4.reload.protected(globals()):
    _puddle_lookup = {}

class PuddleSize(enum.Int):
    NoPuddle = 0
    SmallPuddle = 1
    MediumPuddle = 2
    LargePuddle = 3


class PuddleLiquid(DynamicEnum, partitioned=True):
    INVALID = -1
    WATER = 0


def create_puddle(puddle_size, puddle_liquid=PuddleLiquid.WATER):
    key = (
     puddle_liquid, puddle_size)
    if key not in _puddle_lookup:
        return
    available_definitions = _puddle_lookup[key]

    def init(obj):
        obj.opacity = 0

    return objects.system.create_object((random.choice(available_definitions)), init=init)


def populuate_puddle_choices_lookup(instance_class, tunable_name, source, value):
    _puddle_lookup.clear()
    for definition in value:
        cls = definition.cls
        key = (cls.puddle_liquid, cls.puddle_size)
        if key not in _puddle_lookup:
            _puddle_lookup[key] = []
        _puddle_lookup[key].append(definition)


class PuddleChoices:
    PUDDLE_DEFINITIONS = TunableDefinitionList(description='\n        All puddles that can be created through gameplay. Should not include\n        block models and other dev-only puddles.\n        ',
      pack_safe=True,
      callback=populuate_puddle_choices_lookup)