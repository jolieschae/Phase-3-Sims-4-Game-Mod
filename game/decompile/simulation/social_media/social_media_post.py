# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_post.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4233 bytes
from distributor.rollback import ProtocolBufferRollback
from id_generator import generate_object_id
import sims4
logger = sims4.log.Logger('Social Media', default_owner='mbilello')

class SocialMediaPost:
    __slots__ = ('post_id', 'author_sim_id', 'target_sim_id', 'narrative', 'post_type',
                 'post_time', 'post_text', 'reactions')

    def __init__(self, author_sim_id, target_sim_id, narrative, post_type, post_time, post_text, post_id=None):
        self.post_id = generate_object_id() if post_id is None else post_id
        self.author_sim_id = author_sim_id
        self.target_sim_id = target_sim_id
        self.narrative = narrative
        self.post_type = post_type
        self.post_time = post_time
        self.post_text = post_text
        self.reactions = []

    def save(self, post_data):
        post_data.post_id = self.post_id
        post_data.author_sim_id = self.author_sim_id
        post_data.target_sim_id = self.target_sim_id if (self.target_sim_id is not None and self.target_sim_id > 0) else 0
        post_data.narrative = self.narrative
        post_data.post_type = self.post_type
        post_data.post_time = self.post_time.absolute_ticks()
        post_data.post_text = self.post_text
        for reaction in self.reactions:
            with ProtocolBufferRollback(post_data.reactions) as (post_reaction):
                reaction.save_reaction(post_reaction)

    def sim_has_reacted(self, sim_id):
        return any((sim_id in reaction.reacted_sims for reaction in self.reactions))

    def total_reactions(self):
        total = 0
        for reaction in self.reactions:
            total = total + reaction.count

        return total


class SocialMediaDirectMessage:
    __slots__ = ('message_id', 'message_post', 'reply_post')

    def __init__(self, message_post, reply_post=None, message_id=None):
        self.message_id = generate_object_id() if message_id is None else message_id
        self.message_post = message_post
        self.reply_post = reply_post

    def save_dm(self, dm_data):
        dm_data.message_id = self.message_id
        self.message_post.save(dm_data.message_post)
        if self.reply_post is not None:
            self.reply_post.save(dm_data.reply_post)


class SocialMediaPostReaction:
    __slots__ = ('narrative', 'polarity', 'count', 'reacted_sims')

    def __init__(self, narrative, polarity, count=1):
        self.narrative = narrative
        self.polarity = polarity
        self.count = count
        self.reacted_sims = []

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.narrative == other.narrative and self.polarity == other.polarity

    def save_reaction(self, reaction_data):
        reaction_data.narrative_type = self.narrative
        reaction_data.polarity_type = self.polarity
        reaction_data.count = self.count
        reaction_data.reacted_sims.extend(self.reacted_sims)