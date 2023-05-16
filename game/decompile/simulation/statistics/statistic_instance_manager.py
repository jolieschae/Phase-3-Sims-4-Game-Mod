# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\statistic_instance_manager.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 1111 bytes
from sims4.tuning.instance_manager import InstanceManager
import sims4.log
logger = sims4.log.Logger('StatisticInstanceManager')

class StatisticInstanceManager(InstanceManager):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._skills = []

    def register_tuned_class(self, instance, resource_key):
        super().register_tuned_class(instance, resource_key)
        if instance.is_skill:
            self._skills.append(instance)

    def create_class_instances(self):
        self._skills = []
        super().create_class_instances()

        def key(cls):
            return cls.__name__.lower()

        self._skills = tuple(sorted((self._skills), key=key))

    def all_skills_gen(self):
        yield from self._skills
        if False:
            yield None