# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\ui\book_tuning.py
# Compiled at: 2019-04-16 22:23:51
# Size of source mod 2**32: 1533 bytes
import enum, sims4.resources
logger = sims4.log.Logger('Book', default_owner='jdimailig')

class BookDisplayStyle(enum.Int, export=False):
    DEFAULT = 0
    WITCH = 1


class BookCategoryDisplayType(enum.Int):
    DEFAULT = 0
    WITCH_PRACTICAL_SPELL = 1
    WITCH_MISCHIEF_SPELL = 2
    WITCH_UNTAMED_SPELL = 3
    WITCH_POTION = 4


class BookPageType(enum.Int, export=False):
    BLANK = 0
    FRONT = 1
    CATEGORY_LIST = 2
    CATEGORY_FRONT = 3
    CATEGORY = 4


class BookEntryStatusFlag(enum.IntFlags, export=False):
    ENTRY_UNLOCKED = 1
    ENTRY_NEW = 2