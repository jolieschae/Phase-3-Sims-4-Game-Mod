# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\story_progression_rules_handlers.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 2756 bytes
import services, sims4
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
story_progression_rules_archive_schema = GsiGridSchema(label='Story Progression Rules')
story_progression_rules_archive_schema.add_field('domain', label='Domain', width=0.25)
story_progression_rules_archive_schema.add_field('enabled', label='Enabled', width=0.05)
story_progression_rules_archive_schema.add_field('household_id', label='Household Id', width=1)
with story_progression_rules_archive_schema.add_has_many('Rules', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('rule_name', label='Rule Name', width=0.5)
    sub_schema.add_field('enabled', label='Enabled', width=0.05)
    sub_schema.add_field('rule_id', label='Rule Id', type=(GsiFieldVisualizers.INT), width=1)

@GsiHandler('story_progression_rules', story_progression_rules_archive_schema)
def generate_story_progression_rule_data():
    entries = []
    story_progression_service = services.get_story_progression_service()
    if story_progression_service is None:
        return entries
    entry = generate_story_progression_rule_set_entry(story_progression_service.protected_households_rule_set, 'My Households', '-')
    entries.append(entry)
    entry = generate_story_progression_rule_set_entry(story_progression_service.unprotected_households_rule_set, 'Other Households', '-')
    entries.append(entry)
    household_manager = services.household_manager()
    for household in household_manager._objects.values():
        rule_set = household.story_progression_rule_set
        if rule_set.rules:
            entry = generate_story_progression_rule_set_entry(rule_set, household.name, str(household.id))
            entries.append(entry)

    return entries


def generate_story_progression_rule_set_entry(rule_set, domain, household_id):
    entry = {'domain':domain, 
     'enabled':str(rule_set.enabled), 
     'household_id':household_id}
    instance_manager = services.get_instance_manager(sims4.resources.Types.USER_INTERFACE_INFO)
    rule_data = []
    entry['Rules'] = rule_data
    for key, value in rule_set.rules.items():
        rule_display_info = instance_manager.get(key)
        rule_data_entry = {'rule_name':str(rule_display_info), 
         'enabled':str(value), 
         'rule_id':key}
        rule_data.append(rule_data_entry)

    return entry