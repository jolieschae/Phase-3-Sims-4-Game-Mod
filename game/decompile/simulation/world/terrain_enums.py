# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\terrain_enums.py
# Compiled at: 2020-03-12 21:42:34
# Size of source mod 2**32: 1536 bytes
from sims4 import hash_util
import enum

class TerrainTag(enum.Int):
    INVALID = 0
    BRICK = hash_util.hash32('brick')
    CARPET = hash_util.hash32('carpet')
    CEMENT = hash_util.hash32('cement')
    DEEPSNOW = hash_util.hash32('deepsnow')
    DIRT = hash_util.hash32('dirt')
    GRASS = hash_util.hash32('grass')
    GRAVEL = hash_util.hash32('gravel')
    HARDWOOD = hash_util.hash32('hardwood')
    LEAVES = hash_util.hash32('leaves')
    LINOLEUM = hash_util.hash32('linoleum')
    MARBLE = hash_util.hash32('marble')
    METAL = hash_util.hash32('metal')
    PUDDLE = hash_util.hash32('puddle')
    SAND = hash_util.hash32('sand')
    SNOW = hash_util.hash32('snow')
    STONE = hash_util.hash32('stone')
    WOOD_DECK = hash_util.hash32('wood deck')