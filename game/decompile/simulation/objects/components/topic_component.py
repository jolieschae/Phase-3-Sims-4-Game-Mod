# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\topic_component.py
# Compiled at: 2014-06-10 04:56:37
# Size of source mod 2**32: 2895 bytes
from objects.components import Component, types, componentmethod
import collections, services

class TopicComponent(Component, component_name=types.TOPIC_COMPONENT):

    def __init__(self, owner):
        super().__init__(owner)
        self.topics = collections.defaultdict(list)

    @componentmethod
    def get_topics_gen(self):
        for topics in self.topics.values():
            for topic in topics:
                yield topic

    @componentmethod
    def add_topic(self, topic_type, target=None):
        topics = self.topics[topic_type]
        for topic in topics:
            if topic.target_matches(target):
                topic.reset_relevancy()
                break
        else:
            topics.append(topic_type(target))

    @componentmethod
    def decay_topics(self):
        now = services.time_service().sim_now
        for topic_type, topics in tuple(self.topics.items()):
            for topic in tuple(topics):
                if topic.decay_topic(now):
                    topics.remove(topic)

            if not topics:
                del self.topics[topic_type]

    @componentmethod
    def has_topic(self, topic_type, target=None):
        topics = self.topics.get(topic_type)
        if topics is not None:
            return any((t.target_matches(target) for t in topics))
        return False

    @componentmethod
    def topic_currrent_relevancy(self, topic_type, target=None):
        topics = self.topics.get(topic_type)
        if topics is not None:
            for topic in topics:
                if topic.target_matches(target):
                    return topic.current_relevancy

        return 0

    @componentmethod
    def remove_all_topic_of_type(self, topic_type):
        if topic_type in self.topics:
            del self.topics[topic_type]

    @componentmethod
    def remove_topic(self, topic_type, target=None):
        topics = self.topics.get(topic_type)
        if topics is not None:
            for topic in tuple(topics):
                if topic.target is target:
                    topics.remove(topic)

            if not topics:
                del self.topics[topic_type]