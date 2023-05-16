# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\temple\temple_utils.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 837 bytes
import services

class TempleUtils:

    @classmethod
    def get_temple_zone_director(cls):
        venue_service = services.venue_service()
        if venue_service is None:
            return
        zone_director = venue_service.get_zone_director()
        if hasattr(zone_director, '_temple_data'):
            return zone_director