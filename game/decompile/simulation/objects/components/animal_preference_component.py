# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\animal_preference_component.py
# Compiled at: 2021-05-24 15:14:28
# Size of source mod 2**32: 18683 bytes
import random, date_and_time, services, sims4.log
from distributor.rollback import ProtocolBufferRollback
from objects.animals.animal_tests import PreferenceTypes
from objects.components import Component, types
from objects.hovertip import TooltipFieldsComplete
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from sims4.localization import TunableLocalizedString, LocalizationHelperTuning
from sims4.tuning.tunable import Tunable, HasTunableFactory, AutoFactoryInit, TunableMapping
from tag import TunableTags, Tag, TunableTag
logger = sims4.log.Logger('AnimalPreferenceComponent', default_owner='tscott')

class AnimalPreferenceComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.ANIMAL_PREFERENCE_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.AnimalPreferenceComponent):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, assignable_preference_tags, should_always_like_tags, should_always_dislike_tags, **kwargs):
        for tag in should_always_like_tags:
            if tag in assignable_preference_tags:
                logger.error("The 'should_always_like_tags' shouldn't have any repeated tags in the 'assignable_preference_tags' for {}, the tag was {}", instance_class,
                  tag, owner='tscott')

        for tag in should_always_dislike_tags:
            if tag in assignable_preference_tags:
                logger.error("The 'should_always_dislike_tags' shouldn't have any repeated tags in the 'assignable_preference_tags' for {}, the tag was {}", instance_class,
                  tag, owner='tscott')

    TAGS_TO_TEXT = TunableMapping(description='\n        Mapping of tags to localized strings\n        ',
      key_type=TunableTag(description='\n            The tag to associate\n            ',
      filter_prefixes=('Func', )),
      key_name='Tag',
      value_type=TunableLocalizedString(description='\n            The text that should show up when surfacing the tag to the player\n            '),
      value_name='Localized Text')
    FAVORITE_LOC_TEXT = TunableLocalizedString(description='\n        The localized text that should appear in the tooltip to indicate the animal\'s favorite (ie. "Favorite: __")\n        ')
    UNKNOWN_LOC_TEXT = TunableLocalizedString(description='\n        The localized text that should appear in case the favorite preference is not known (ie. "__: None")\n        ')
    FACTORY_TUNABLES = {'assignable_preference_tags':TunableTags(description='\n            A list of tags that the component will make preference decisions on. \n            This list should NOT include tags that the species should always like or dislike\n            ',
       filter_prefixes=('Func', ),
       minlength=1), 
     'should_always_like_tags':TunableTags(description='\n            A list of tags that the species should always like\n            ',
       filter_prefixes=('Func', ),
       minlength=0), 
     'should_always_dislike_tags':TunableTags(description='\n            A list of tags that the species should always dislike\n            ',
       filter_prefixes=('Func', ),
       minlength=0), 
     'normal_gift_readiness_cooldown':Tunable(description='\n            The amount of time (in hours) that it will take for the sims to be able to give a gift to this animal again\n            ',
       tunable_type=int,
       default=24), 
     'category_gift_readiness_cooldown':Tunable(description='\n            The amount of time (in hours) that it will take for the sims to be able to give a specific category of gift again\n            ',
       tunable_type=int,
       default=48), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.like_preferences = []
        self.dislike_preferences = []
        self.favorite_preference = None
        self._household_knowledge_dictionary = {}

    def on_add(self):
        self.setup_preferences()
        self.update_hovertip()

    def update_hovertip(self):
        household_id = services.owning_household_id_of_active_lot()
        if household_id is None:
            return
        if self.test_is_preference_known(household_id, self.favorite_preference):
            if self.favorite_preference in self.TAGS_TO_TEXT:
                favorite_loc_text = self.TAGS_TO_TEXT[self.favorite_preference]
                text = LocalizationHelperTuning.get_name_value_pair(self.FAVORITE_LOC_TEXT, favorite_loc_text)
                self.owner.update_tooltip_field((TooltipFieldsComplete.subtext), text, should_update=True, always_add=True)
            else:
                logger.error("The favorite preference was known but the tag {} wasn't included in tuning's TAGS_TO_TEXT", (self.favorite_preference), owner='tscott')
        else:
            text = LocalizationHelperTuning.get_name_value_pair(self.FAVORITE_LOC_TEXT, self.UNKNOWN_LOC_TEXT)
            self.owner.update_tooltip_field((TooltipFieldsComplete.subtext), text, should_update=True, always_add=True)

    def setup_preferences(self):
        preferences = [
         PreferenceTypes.LIKE, PreferenceTypes.DISLIKE]
        for tag in self.assignable_preference_tags:
            choice = random.choice(preferences)
            self.like_preferences.append(tag) if choice is PreferenceTypes.LIKE else self.dislike_preferences.append(tag)

        for always_like_tag in self.should_always_like_tags:
            self.like_preferences.append(always_like_tag)

        rand_category = random.choice(preferences)
        if rand_category == PreferenceTypes.LIKE:
            rand_fave_tag = random.choice(self.like_preferences)
            self.like_preferences.remove(rand_fave_tag)
        else:
            rand_fave_tag = random.choice(self.dislike_preferences)
            self.dislike_preferences.remove(rand_fave_tag)
        self.favorite_preference = rand_fave_tag
        for always_dislike_tag in self.should_always_dislike_tags:
            self.dislike_preferences.append(always_dislike_tag)

    def save(self, persistence_master_message):
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.AnimalPreferenceComponent
        animal_preference_data = persistable_data.Extensions[protocols.PersistableAnimalPreferenceComponent.persistable_data]
        for like_preference in self.like_preferences:
            animal_preference_data.preferences_data.like_preferences.append(like_preference)

        for dislike_preference in self.dislike_preferences:
            animal_preference_data.preferences_data.dislike_preferences.append(dislike_preference)

        animal_preference_data.preferences_data.favorite_preference = self.favorite_preference
        for knowledge in self._household_knowledge_dictionary.values():
            with ProtocolBufferRollback(animal_preference_data.preferences_data.preference_knowledge) as (knowledge_msg):
                knowledge.save_knowledge(knowledge_msg)

        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        self.like_preferences = []
        self.dislike_preferences = []
        self.favorite_preference = None
        animal_preference_data = persistable_data.Extensions[protocols.PersistableAnimalPreferenceComponent.persistable_data]
        for like_preference in animal_preference_data.preferences_data.like_preferences:
            self.like_preferences.append(Tag(like_preference))

        for dislike_preference in animal_preference_data.preferences_data.dislike_preferences:
            self.dislike_preferences.append(Tag(dislike_preference))

        self.favorite_preference = Tag(animal_preference_data.preferences_data.favorite_preference)
        for knowledge_msg in animal_preference_data.preferences_data.preference_knowledge:
            household_id = knowledge_msg.household_id
            household_helper = AnimalPreferenceHouseholdHelper(household_id, set(), self.normal_gift_readiness_cooldown, self.category_gift_readiness_cooldown)
            household_helper.load_knowledge(knowledge_msg)
            self._household_knowledge_dictionary[household_id] = household_helper

        self.update_hovertip()

    @property
    def household_knowledge_dictionary(self):
        return self._household_knowledge_dictionary

    def test_preference_match(self, tag, preference):
        if preference is PreferenceTypes.LIKE:
            return tag in self.like_preferences
        if preference is PreferenceTypes.DISLIKE:
            return tag in self.dislike_preferences
        return tag == self.favorite_preference

    def test_is_general_ready(self, household_id):
        helper = self.get_household_knowledge_helper(household_id)
        return helper.check_general_gift_readiness()

    def test_is_category_ready(self, household_id, tag):
        helper = self.get_household_knowledge_helper(household_id)
        return helper.check_category_gift_readiness(tag)

    def test_is_preference_known(self, household_id, tag):
        helper = self.get_household_knowledge_helper(household_id)
        return tag in helper.known_tags

    def test_are_all_preferences_known(self, household_id):
        helper = self.get_household_knowledge_helper(household_id)
        return not helper.unknown_tags or len(helper.unknown_tags) == 1 and self.favorite_preference in helper.unknown_tags

    def get_household_knowledge_helper(self, household_id):
        if household_id not in self._household_knowledge_dictionary:
            unknown_tags = set(self.assignable_preference_tags)
            for like_tag in self.should_always_like_tags:
                unknown_tags.add(like_tag)

            for dislike_tag in self.should_always_dislike_tags:
                unknown_tags.add(dislike_tag)

            unknown_tags.add(self.favorite_preference)
            self._household_knowledge_dictionary[household_id] = AnimalPreferenceHouseholdHelper(household_id, unknown_tags, self.normal_gift_readiness_cooldown, self.category_gift_readiness_cooldown)
        return self._household_knowledge_dictionary[household_id]

    def add_preference_knowledge(self, household_id, tag):
        helper = self.get_household_knowledge_helper(household_id)
        if tag not in helper.known_tags:
            helper.known_tags.add(tag)
            helper.unknown_tags.remove(tag)
            if tag is self.favorite_preference:
                self.update_hovertip()

    def trigger_gifting_cooldown(self, household_id, tag):
        helper = self.get_household_knowledge_helper(household_id)
        helper.trigger_gifting_cooldown(tag)

    def clear_preference_knowledge(self):
        self._household_knowledge_dictionary.clear()
        self.update_hovertip()

    def reset_preference_cooldowns(self):
        for knowledge in self._household_knowledge_dictionary.values():
            knowledge.clear_cooldowns()


class AnimalPreferenceHouseholdHelper:

    def __init__(self, household_id, unknown_tags, general_cooldown_amount, category_cooldown_amount):
        self._unknown_tags = unknown_tags
        self._known_tags = set()
        self._household_id = household_id
        self._general_gift_timestamp = date_and_time.DATE_AND_TIME_ZERO
        self._category_gift_timestamps = {}
        self._general_cooldown_amount = general_cooldown_amount
        self._category_cooldown_amount = category_cooldown_amount

    def save_knowledge(self, knowledge_msg):
        knowledge_msg.household_id = self._household_id
        for unknown_tag in self._unknown_tags:
            knowledge_msg.unknown_tags.append(unknown_tag)

        for known_tag in self._known_tags:
            knowledge_msg.known_tags.append(known_tag)

        if self._general_gift_timestamp is not date_and_time.DATE_AND_TIME_ZERO:
            knowledge_msg.general_timestamp = self._general_gift_timestamp
        for category, timestamp in self._category_gift_timestamps.items():
            if timestamp is not date_and_time.DATE_AND_TIME_ZERO:
                with ProtocolBufferRollback(knowledge_msg.category_timestamp) as (category_msg):
                    category_msg.category_tag = category
                    category_msg.timestamp = timestamp

    def load_knowledge(self, knowledge_msg):
        for unknown_tag in knowledge_msg.unknown_tags:
            self._unknown_tags.add(Tag(unknown_tag))

        for known_tag in knowledge_msg.known_tags:
            self._known_tags.add(Tag(known_tag))

        self._general_gift_timestamp = date_and_time.DateAndTime(knowledge_msg.general_timestamp)
        for category_msg in knowledge_msg.category_timestamp:
            tag = Tag(category_msg.category_tag)
            self._category_gift_timestamps[tag] = date_and_time.DateAndTime(category_msg.timestamp)

    @property
    def unknown_tags(self):
        return self._unknown_tags

    @property
    def known_tags(self):
        return self._known_tags

    @property
    def category_gift_timestamps(self):
        return self._category_gift_timestamps

    def add_preference_knowledge(self, tag):
        if tag not in self._known_tags:
            self._known_tags.add(tag)
            self._unknown_tags.remove(tag)

    def check_general_gift_readiness(self):
        now = services.time_service().sim_now
        return now > self._general_gift_timestamp

    def check_category_gift_readiness(self, tag):
        if tag not in self._category_gift_timestamps:
            self._category_gift_timestamps[tag] = date_and_time.DATE_AND_TIME_ZERO
        now = services.time_service().sim_now
        is_ready = now > self._category_gift_timestamps[tag]
        if is_ready:
            self.category_gift_timestamps[tag] = date_and_time.DATE_AND_TIME_ZERO
        return is_ready

    def trigger_gifting_cooldown(self, tag):
        now = services.time_service().sim_now
        general_time_delay = date_and_time.create_time_span(hours=(self._general_cooldown_amount))
        self._general_gift_timestamp = now + general_time_delay
        category_time_delay = date_and_time.create_time_span(hours=(self._category_cooldown_amount))
        self._category_gift_timestamps[tag] = now + category_time_delay

    def clear_cooldowns(self):
        self._general_gift_timestamp = date_and_time.DATE_AND_TIME_ZERO
        self._category_gift_timestamps.clear()