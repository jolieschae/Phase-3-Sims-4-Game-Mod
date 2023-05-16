# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\__init__.py
# Compiled at: 2018-08-21 17:23:05
# Size of source mod 2**32: 656 bytes
import services

class UnavailableClubError(Exception):
    pass


class UnavailableClubCriteriaError(Exception):
    pass


def on_sim_killed_or_culled(sim_info):
    club_service = services.get_club_service()
    if club_service is not None:
        club_service.on_sim_killed_or_culled(sim_info)