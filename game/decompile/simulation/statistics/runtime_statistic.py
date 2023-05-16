# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\runtime_statistic.py
# Compiled at: 2014-12-15 00:42:30
# Size of source mod 2**32: 904 bytes
from statistics.statistic import Statistic
import sims4.resources

class RuntimeStatistic(Statistic):
    INSTANCE_SUBCLASSES_ONLY = True

    @classmethod
    def generate(cls, name):
        ProxyClass = type(cls)(name, (cls,), {'INSTANCE_SUBCLASSES_ONLY': True})
        ProxyClass.reloadable = False
        key = sims4.resources.get_resource_key(name, ProxyClass.tuning_manager.TYPE)
        ProxyClass.tuning_manager.register_tuned_class(ProxyClass, key)
        return ProxyClass