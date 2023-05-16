# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\social_media\social_media_loot.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 5558 bytes
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry
from social_media import SocialMediaPostType, SocialMediaNarrative, SocialMediaPolarity
import services

class SocialMediaPostLoot(BaseLootOperation):
    FACTORY_TUNABLES = {'post_type':TunableEnumEntry(description='\n            A SocialMediaPostType enum entry.\n            ',
       tunable_type=SocialMediaPostType,
       default=SocialMediaPostType.DEFAULT), 
     'narrative':TunableEnumEntry(description='\n            A SocialMediaNarrative enum entry.\n            ',
       tunable_type=SocialMediaNarrative,
       default=SocialMediaNarrative.FRIENDLY)}

    def __init__(self, post_type, narrative, **kwargs):
        (super().__init__)(**kwargs)
        self._post_type = post_type
        self._narrative = narrative

    def _apply_to_subject_and_target(self, subject, target, resolver):
        social_media_service = services.get_social_media_service()
        if social_media_service is None:
            return
        if subject is None:
            return
        author_sim_id = subject.id
        target = subject.get_random_pc_social_media_target()
        if self._post_type == SocialMediaPostType.FRIEND_REQUEST:
            target = social_media_service.get_possible_new_social_media_friend(subject)
        target_sim_id = target.id if target is not None else None
        social_media_service.create_post(self._post_type, author_sim_id, target_sim_id, self._narrative)


class SocialMediaReactionLoot(BaseLootOperation):
    FACTORY_TUNABLES = {'post_type':TunableEnumEntry(description='\n            The SocialMediaPostType of the post to react to.\n            ',
       tunable_type=SocialMediaPostType,
       default=SocialMediaPostType.DEFAULT), 
     'post_narrative':TunableEnumEntry(description='\n            The SocialMediaNarrative of the post to react to.\n            ',
       tunable_type=SocialMediaNarrative,
       default=SocialMediaNarrative.FRIENDLY), 
     'reaction_narrative':TunableEnumEntry(description='\n            The SocialMediaNarrative of the reaction.\n            ',
       tunable_type=SocialMediaNarrative,
       default=SocialMediaNarrative.FRIENDLY), 
     'reaction_polarity':TunableEnumEntry(description='\n            The SocialMediaPolarity of the reaction.\n            ',
       tunable_type=SocialMediaPolarity,
       default=SocialMediaPolarity.POSITIVE)}

    def __init__(self, post_type, post_narrative, reaction_narrative, reaction_polarity, **kwargs):
        (super().__init__)(**kwargs)
        self._post_type = post_type
        self._post_narrative = post_narrative
        self._reaction_narrative = reaction_narrative
        self._reaction_polarity = reaction_polarity

    def _apply_to_subject_and_target(self, subject, target, resolver):
        social_media_service = services.get_social_media_service()
        if social_media_service is None:
            return
        if subject is None:
            return
        author_sim_id = subject.id
        target = subject.get_random_pc_social_media_target()
        if target is not None:
            target_sim_id = target.id
            social_media_service.add_reaction_to_post_narrative(self._post_type, author_sim_id, target_sim_id, self._post_narrative, self._reaction_narrative, self._reaction_polarity)


class SocialMediaAddFriendLoot(BaseLootOperation):
    FACTORY_TUNABLES = {'recipient':TunableEnumEntry(description='\n            The Sim asking to be friends.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Invalid,
       invalid_enums=(
      ParticipantType.Invalid,)), 
     'target':TunableEnumEntry(description='\n            The target Sim to befriend.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Invalid,
       invalid_enums=(
      ParticipantType.Invalid,)), 
     'locked_args':{'subject':ParticipantType.Invalid, 
      'subject_filter_tests':None, 
      'target_filter_tests':None}}

    def __init__(self, recipient, target, **kwargs):
        (super().__init__)(**kwargs)
        self._recipient = recipient
        self._target = target

    def apply_to_resolver(self, resolver, skip_test=False):
        if not skip_test:
            if not self.test_resolver(resolver):
                return (False, None)
        social_media_service = services.get_social_media_service()
        if social_media_service is None:
            return (False, None)
        author_sim_info = resolver.get_participants(self._recipient)[0]
        author_sim_id = author_sim_info.id
        target_sim_info = resolver.get_participants(self._target)[0]
        target_sim_id = target_sim_info.id
        social_media_service.add_social_media_friend(author_sim_id, target_sim_id)