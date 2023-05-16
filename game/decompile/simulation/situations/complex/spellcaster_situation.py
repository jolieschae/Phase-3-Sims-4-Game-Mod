# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\spellcaster_situation.py
# Compiled at: 2019-07-25 16:23:42
# Size of source mod 2**32: 443 bytes
from situations.complex.favorite_object_situation_mixin import FavoriteObjectSituationMixin
from situations.complex.single_job_situation import SingleJobSituation

class SpellcasterSituation(FavoriteObjectSituationMixin, SingleJobSituation):
    pass