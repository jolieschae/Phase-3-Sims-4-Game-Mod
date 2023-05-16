# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\topics\tunable.py
# Compiled at: 2018-05-22 17:53:50
# Size of source mod 2**32: 1487 bytes
from interactions.utils.loot_basic_op import BaseTargetedLootOperation
from sims4.tuning.tunable import Tunable, TunableReference
from topics.topic import Topic
import services, sims4.log
logger = sims4.log.Logger('Topic')

class TopicUpdate(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'topic':TunableReference(description='\n            The topic we are updating.',
       manager=services.get_instance_manager(sims4.resources.Types.TOPIC),
       class_restrictions=Topic), 
     'add':Tunable(description='\n            Topic will be added to recipient. if unchecked topic will be\n            removed from recipient.',
       tunable_type=bool,
       default=True)}

    def __init__(self, topic, add, **kwargs):
        (super().__init__)(**kwargs)
        self._topic_type = topic
        self._add = add

    def _apply_to_subject_and_target(self, subject, target, resolver):
        sim = self._get_object_from_recipient(subject)
        if sim is None:
            return
        elif self._add:
            sim.add_topic((self._topic_type), target=target)
        else:
            sim.remove_topic((self._topic_type), target=target)