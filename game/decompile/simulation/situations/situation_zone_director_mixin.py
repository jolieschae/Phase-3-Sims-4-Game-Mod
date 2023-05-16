# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_zone_director_mixin.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1156 bytes
from zone_director import ZoneDirectorBase

class SituationZoneDirectorMixin:
    INSTANCE_TUNABLES = {'_zone_director': ZoneDirectorBase.TunableReference(description='\n            This zone director will automatically be requested by the situation\n            during zone spin up.\n            ')}

    @classmethod
    def get_zone_director_request(cls, host_sim_info=None, zone_id=None):
        return (cls._zone_director(), cls._get_zone_director_request_type())

    @classmethod
    def _get_zone_director_request_type(cls):
        raise NotImplementedError