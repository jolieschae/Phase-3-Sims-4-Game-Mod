# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\animal_preference_handlers.py
# Compiled at: 2021-03-09 18:54:35
# Size of source mod 2**32: 3260 bytes
import date_and_time, services
from objects.components.types import ANIMAL_PREFERENCE_COMPONENT
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
animal_preferences_schema = GsiGridSchema(label='Animal Preferences')
animal_preferences_schema.add_field('animal', label='Animal', width=2, unique_field=True)
animal_preferences_schema.add_field('like_preferences', label='Likes', width=2)
animal_preferences_schema.add_field('dislike_preferences', label='Dislikes')
animal_preferences_schema.add_field('favorite_preference', label='Favorite')
with animal_preferences_schema.add_has_many('knowledge', GsiGridSchema, label='Household Knowledge') as (sub_schema):
    sub_schema.add_field('household_id', label='Household ID', width=0.35)
    sub_schema.add_field('known_preferences', label='Known Preferences', width=0.4)
    sub_schema.add_field('general_cooldown', label='General Readiness', width=0.4)
    sub_schema.add_field('category_cooldown', label='Not Ready Categories', width=0.4)

@GsiHandler('animal_preferences', animal_preferences_schema)
def generate_animal_preferences_data():
    animal_preferences = []
    object_manager = services.object_manager()
    if object_manager is None:
        return animal_preferences
    for animal_obj in object_manager.get_all_objects_with_component_gen(ANIMAL_PREFERENCE_COMPONENT):
        preference_comp = animal_obj.animalpreference_component
        if preference_comp is None:
            continue
        entry = {'animal':str(animal_obj),  'like_preferences':trim_tags(*preference_comp.like_preferences), 
         'dislike_preferences':trim_tags(*preference_comp.dislike_preferences), 
         'favorite_preference':trim_tags(preference_comp.favorite_preference)}
        knowledge_info = []
        entry['knowledge'] = knowledge_info
        for household_id, knowledge in preference_comp.household_knowledge_dictionary.items():
            known_preferences = trim_tags(*knowledge.known_tags)
            is_general_ready = 'READY' if knowledge.check_general_gift_readiness() else 'NOT READY'
            not_ready_categories = []
            for category, time in knowledge.category_gift_timestamps.items():
                if time > date_and_time.DATE_AND_TIME_ZERO:
                    not_ready_categories.append(category)

            knowledge_info.append({'household_id':str(household_id), 
             'known_preferences':known_preferences, 
             'general_cooldown':is_general_ready, 
             'category_cooldown':trim_tags(*not_ready_categories)})

        animal_preferences.append(entry)

    return animal_preferences


def trim_tags(*args):
    result = ''
    first = True
    for long_tag in args:
        if not first:
            result += ', '
        tag = str(long_tag)
        tag = tag.lstrip('Tag.Func')
        tag = tag.lstrip('_')
        first = False
        result += tag

    return result