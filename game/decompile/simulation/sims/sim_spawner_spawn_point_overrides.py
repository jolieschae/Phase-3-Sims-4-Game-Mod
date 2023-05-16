# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_spawner_spawn_point_overrides.py
# Compiled at: 2020-06-24 15:46:34
# Size of source mod 2**32: 1241 bytes
from event_testing.resolver import SingleSimResolver
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableEnumWithFilter
from tag import Tag, SPAWN_PREFIX
from tunable_utils.tested_list import TunableTestedList, STOP_PROCESSING_ALWAYS

class TestedSpawnPointOverride(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tested_list': TunableTestedList(tunable_type=TunableEnumWithFilter(tunable_type=Tag,
                      default=(Tag.INVALID),
                      invalid_enums=(
                     Tag.INVALID,),
                      filter_prefixes=SPAWN_PREFIX),
                      stop_processing_behavior=STOP_PROCESSING_ALWAYS)}

    def get_spawner_tag(self, sim_info):
        resolver = SingleSimResolver(sim_info)
        return next(iter((tag for tag in self.tested_list(resolver=resolver))), None)