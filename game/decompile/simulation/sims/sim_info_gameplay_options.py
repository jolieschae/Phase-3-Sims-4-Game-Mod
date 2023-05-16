# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_gameplay_options.py
# Compiled at: 2018-09-17 22:09:35
# Size of source mod 2**32: 1143 bytes
from _sims4_collections import frozendict
from sims4.common import Pack, is_available_pack
import enum

class SimInfoGameplayOptions(enum.IntFlags):
    ALLOW_FAME = 1
    ALLOW_REPUTATION = 2
    FORCE_CURRENT_ALLOW_FAME_SETTING = 4
    FREEZE_FAME = 8


REQUIRED_PACK_BY_OPTION = frozendict({SimInfoGameplayOptions.ALLOW_FAME: Pack.EP06, 
 SimInfoGameplayOptions.ALLOW_REPUTATION: Pack.EP06, 
 SimInfoGameplayOptions.FORCE_CURRENT_ALLOW_FAME_SETTING: Pack.EP06, 
 SimInfoGameplayOptions.FREEZE_FAME: Pack.EP06})

def is_required_pack_installed(sim_info_gameplay_option):
    pack = REQUIRED_PACK_BY_OPTION.get(sim_info_gameplay_option, None)
    if pack is None:
        return True
    return is_available_pack(pack)