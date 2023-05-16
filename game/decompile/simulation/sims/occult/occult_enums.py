# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\occult\occult_enums.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 418 bytes
import enum

class OccultType(enum.IntFlags):
    HUMAN = 1
    ALIEN = 2
    VAMPIRE = 4
    MERMAID = 8
    WITCH = 16
    WEREWOLF = 32