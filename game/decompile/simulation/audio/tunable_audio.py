# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\audio\tunable_audio.py
# Compiled at: 2019-06-05 18:07:17
# Size of source mod 2**32: 648 bytes
from sims4.resources import Types
from sims4.tuning.tunable import TunablePackSafeResourceKey

class TunableAudioAllPacks(TunablePackSafeResourceKey):

    def __init__(self, *, description='The audio file.', **kwargs):
        (super().__init__)(None, resource_types=(Types.PROPX,), description=description, **kwargs)

    @property
    def validate_pack_safe(self):
        return False