# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cas\cas_preference_item.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 7228 bytes
import build_buy, services, sims4
from objects.object_tests import ObjectTypeFactory, ObjectTagFactory, TagTestType
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableReference, TunableVariant, TunableRange, TunableMapping, OptionalTunable
from sims4.tuning.tunable_base import ExportModes
from sims4.utils import classproperty
from traits.preference_enums import PreferenceSubject
logger = sims4.log.Logger('CasPreferenceItem', default_owner='spark')

class CasPreferenceItem(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAS_PREFERENCE_ITEM)):
    INSTANCE_TUNABLES = {'cas_preference_category':TunableReference(description='\n            The category this Preference Item belongs to. (E.g. if the Preference\n            Item contains: Trait-Likes-Pink and Trait-Dislikes-Pink, then the category\n            would be Preference-Category-Color.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAS_PREFERENCE_CATEGORY),
       export_modes=ExportModes.All), 
     'like':TunableReference(description='\n            The like-trait for this Preference Item.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT),
       export_modes=ExportModes.All), 
     'dislike':TunableReference(description='\n            The dislike-trait for this Preference Item.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT),
       export_modes=ExportModes.All), 
     'tooltip':OptionalTunable(description='\n            If enabled, the tooltip description text for this item in the CAS Preferences\n            Panel.\n            ',
       tunable=TunableLocalizedString(),
       export_modes=ExportModes.All)}

    @classproperty
    def preference_subject(self):
        raise NotImplementedError

    def target_is_preferred(self, target):
        raise NotImplementedError

    @classmethod
    def get_any_tags(cls):
        pass


class ObjectPreferenceItem(CasPreferenceItem):
    INSTANCE_TUNABLES = {'object_item_def': TunableVariant(definition_id=(ObjectTypeFactory.TunableFactory()),
                          tags=(ObjectTagFactory.TunableFactory()),
                          default='tags')}

    @classproperty
    def preference_subject(self):
        return PreferenceSubject.OBJECT

    def target_is_preferred(self, target):
        return self.object_item_def(target)

    @classmethod
    def get_any_tags(cls):
        if hasattr(cls.object_item_def, 'tag_set'):
            if cls.object_item_def.test_type == TagTestType.CONTAINS_ANY_TAG_IN_SET:
                return cls.object_item_def.tag_set
            logger.error('You are trying to get tags from preference {} without using type CONTAINS_ANY_TAG_IN_SET', cls,
              owner='mbilello')


class StylePreferenceItem(CasPreferenceItem):
    INSTANCE_TUNABLES = {'style_tags': ObjectTagFactory.TunableFactory(description='\n            Validate the tags of the style of the target object against.\n            Style tags can be found in the catalog here: Styles-> Object\n             Styles-> Tags.\n            ')}

    @classproperty
    def preference_subject(self):
        return PreferenceSubject.DECOR

    def target_is_preferred(self, target):
        for style_tag in self.style_tags:
            if build_buy.get_object_or_style_has_tag(target.guid64, style_tag):
                return True

        return False

    @classmethod
    def get_any_tags(cls):
        if cls.style_tags.test_type == TagTestType.CONTAINS_ANY_TAG_IN_SET:
            return cls.style_tags.tag_set
        logger.error('You are trying to get tags from preference {} without using type CONTAINS_ANY_TAG_IN_SET', cls,
          owner='mbilello')


class CharacteristicPreferenceItem(CasPreferenceItem):
    INSTANCE_TUNABLES = {'trait_map': TunableMapping(description='\n            A mapping of the desired traits associated with this PreferenceItem, and \n            the corresponding scores. \n            ',
                    key_type=TunableReference(description='\n                The desired trait.  This could be a standard trait, an activity \n                like/dislike trait, or a lifestyle trait.\n                ',
                    manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
                    pack_safe=True),
                    value_type=TunableRange(description="\n                The score associated with this trait.  If there's a match, this value\n                gets added to the overall compatibility score.\n                ",
                    tunable_type=float,
                    default=1.0))}

    @classproperty
    def preference_subject(self):
        return PreferenceSubject.CHARACTERISTIC

    def target_is_preferred(self, target):
        return False


class ConversationPreferenceItem(CasPreferenceItem):

    @classproperty
    def preference_subject(self):
        return PreferenceSubject.CONVERSATION

    def target_is_preferred(self, target):
        return False