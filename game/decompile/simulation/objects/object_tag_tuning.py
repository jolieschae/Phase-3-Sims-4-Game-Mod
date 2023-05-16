# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\object_tag_tuning.py
# Compiled at: 2017-06-22 18:50:12
# Size of source mod 2**32: 2692 bytes
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableSet, TunableFactory
from tag import TunableTag, TunableTags
import interactions, sims4.log, singletons
logger = sims4.log.Logger('Object Tag Tuning', default_owner='skorman')

class ApplyTagsToObject(BaseLootOperation):
    FACTORY_TUNABLES = {'apply_unpersisted_tags':TunableTags(description='\n                A set of unpersisted category tags to apply to the finished product.\n                '), 
     'apply_persisted_tags':TunableTags(description='\n                A set of persisted category tags to apply to the finished product.\n                ')}

    def __init__(self, apply_unpersisted_tags, apply_persisted_tags, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._apply_unpersisted_tags = apply_unpersisted_tags
        self._apply_persisted_tags = apply_persisted_tags

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            return
        elif hasattr(subject, 'append_tags'):
            subject.append_tags((self._apply_unpersisted_tags), persist=False)
            subject.append_tags((self._apply_persisted_tags), persist=True)
        else:
            logger.error("ApplyTagsToObject Tuning: Subject {} does not have attribute 'append_tags'", subject)

    @TunableFactory.factory_option
    def subject_participant_type_options(description=singletons.DEFAULT, **kwargs):
        if description is singletons.DEFAULT:
            description = 'The object the tags are applied to.'
        return (BaseLootOperation.get_participant_tunable)('subject', description=description, 
         default_participant=interactions.ParticipantType.Object, **kwargs)