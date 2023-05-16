# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\audio\audio_effect_data.py
# Compiled at: 2018-07-16 21:27:57
# Size of source mod 2**32: 859 bytes


class AudioEffectData:

    def __init__(self, effect_id, track_flags=None):
        self._effect_id = effect_id
        self._track_flags = track_flags

    @property
    def effect_id(self):
        return self._effect_id

    @property
    def track_flags(self):
        return self._track_flags