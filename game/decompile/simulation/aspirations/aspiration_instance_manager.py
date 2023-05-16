# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\aspirations\aspiration_instance_manager.py
# Compiled at: 2018-06-11 16:26:46
# Size of source mod 2**32: 753 bytes
from aspirations.aspiration_types import AspriationType
from sims4.tuning.instance_manager import InstanceManager
import sims4.log
logger = sims4.log.Logger('Aspirations')

class AspirationInstanceManager(InstanceManager):

    def all_whim_sets_gen(self):
        for aspiration in self.types.values():
            if aspiration.aspiration_type == AspriationType.WHIM_SET:
                yield aspiration