# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\story_progression_handlers.py
# Compiled at: 2022-03-10 20:35:09
# Size of source mod 2**32: 9942 bytes
import services
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
from story_progression.story_progression_result import StoryProgressionResult, StoryProgressionResultType

class GSIStoryProgressionDemographicData:

    def __init__(self):
        self.item_id = None
        self.item_name = None
        self.reason = 'Success'


class GSIStoryProgressionArcData:

    def __init__(self):
        self.arc = None
        self.item_id = None
        self.item_name = None


class GSIStoryProgressionPassData:

    def __init__(self):
        self.story_progression_pass = 'No Pass'
        self.demographic_percentage = 0
        self.demographic_data = []
        self.arcs_seeded = 0
        self.arc_data = []
        self.result = StoryProgressionResult(StoryProgressionResultType.SUCCESS)


story_progression_pass_archive_schema = GsiGridSchema(label='Story Progression Pass Archive')
story_progression_pass_archive_schema.add_field('pass_name', label='Pass', type=(GsiFieldVisualizers.STRING))
story_progression_pass_archive_schema.add_field('demographic_percentage', label='Demographic Percentage', type=(GsiFieldVisualizers.FLOAT))
story_progression_pass_archive_schema.add_field('arcs_seeded', label='Arcs Seeded', type=(GsiFieldVisualizers.INT))
story_progression_pass_archive_schema.add_field('result_type', label='Result')
story_progression_pass_archive_schema.add_field('reason', label='Reason')
with story_progression_pass_archive_schema.add_has_many('demographics', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('item_id', label='Id', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('item_name', label='Item Name', type=(GsiFieldVisualizers.STRING))
    sub_schema.add_field('reason', label='Reason', type=(GsiFieldVisualizers.STRING))
with story_progression_pass_archive_schema.add_has_many('seeded_arcs', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('arc', label='Arc')
    sub_schema.add_field('item_id', label='Id', type=(GsiFieldVisualizers.INT))
    sub_schema.add_field('item_name', label='Item Name', type=(GsiFieldVisualizers.STRING))
story_progression_pass_archiver = GameplayArchiver('story_progression_pass', story_progression_pass_archive_schema,
  max_records=200)

def is_story_progression_pass_archive_enabled():
    return story_progression_pass_archiver.enabled


def archive_story_progression_pass_data(pass_data):
    demographic_entries = []
    for demographic_data in pass_data.demographic_data:
        demographic_entry = {'item_id':demographic_data.item_id, 
         'item_name':demographic_data.item_name, 
         'reason':demographic_data.reason}
        demographic_entries.append(demographic_entry)

    arc_entries = []
    for arc_data in pass_data.arc_data:
        arc_entry = {'arc':str(arc_data.arc), 
         'item_id':arc_data.item_id, 
         'item_name':arc_data.item_name}
        arc_entries.append(arc_entry)

    entry = {'pass_name':pass_data.story_progression_pass,  'demographic_percentage':pass_data.demographic_percentage, 
     'arcs_seeded':pass_data.arcs_seeded, 
     'result_type':str(pass_data.result.result_type), 
     'reason':pass_data.result.reason, 
     'demographics':demographic_entries, 
     'seeded_arcs':arc_entries}
    story_progression_pass_archiver.archive(data=entry)


class GSIStoryProgressionUpdateData:

    def __init__(self):
        self.sim_info = None
        self.household = None
        self.arc = None
        self.chapter = None
        self.result = None


story_progression_update_archive_schema = GsiGridSchema(label='Story Progression Update Archive')
story_progression_update_archive_schema.add_field('who', label='Who', type=(GsiFieldVisualizers.STRING))
story_progression_update_archive_schema.add_field('who_id', label='Id', type=(GsiFieldVisualizers.INT))
story_progression_update_archive_schema.add_field('arc', label='Arc')
story_progression_update_archive_schema.add_field('chapter', label='Chapter')
story_progression_update_archive_schema.add_field('result', label='Result')
story_progression_update_archive_schema.add_field('reason', label='Reason', type=(GsiFieldVisualizers.STRING))
story_progression_update_archiver = GameplayArchiver('story_progression_update', story_progression_update_archive_schema)

def is_story_progression_update_archive_enabled():
    return story_progression_update_archiver.enabled


def archive_story_progression_update_data(update_data):
    if update_data.sim_info is not None:
        who = update_data.sim_info.full_name
        id = update_data.sim_info.sim_id
    else:
        if update_data.household is not None:
            who = update_data.household.name
            id = update_data.household.id
        else:
            return
    entry = {'who':who, 
     'who_id':id, 
     'arc':str(update_data.arc), 
     'chapter':str(update_data.chapter), 
     'result':str(update_data.result.result_type), 
     'reason':update_data.result.reason}
    story_progression_update_archiver.archive(data=entry)


story_progression_tracker_schema = GsiGridSchema(label='Story Progression Tracker', sim_specific=True)
story_progression_tracker_schema.add_field('arc_type', label='Arc')
story_progression_tracker_schema.add_field('chapter_type', label='Chapter')
story_progression_tracker_schema.add_field('status', label='Status', type=(GsiFieldVisualizers.STRING))
story_progression_tracker_schema.add_field('arc_owner', label='Owner', type=(GsiFieldVisualizers.STRING))
with story_progression_tracker_schema.add_has_many('current_chapter_data', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('field', label='Field')
    sub_schema.add_field('data', label='Data')
with story_progression_tracker_schema.add_has_many('historical_chapter_data', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('chapter', label='Chapter')
    sub_schema.add_field('time_completed', label='Time Completed')
    sub_schema.add_field('time_until_expiration', label='Time Until Expiration')

@GsiHandler('story_progression_tracker_view', story_progression_tracker_schema)
def generate_story_progression_view_data(sim_id: int=None):
    story_progression_data = []
    sim_info = services.sim_info_manager().get(sim_id)
    sim_story_progression_tracker = sim_info.story_progression_tracker
    if sim_story_progression_tracker is not None:
        current_arcs = sim_story_progression_tracker.current_arcs
        for arc in current_arcs:
            gsi_data = arc.get_gsi_data()
            gsi_data['status'] = 'Current'
            gsi_data['arc_owner'] = 'Sim'
            story_progression_data.append(gsi_data)

        historical_arcs = sim_story_progression_tracker.historical_arcs
        for arc in historical_arcs:
            gsi_data = arc.get_gsi_data()
            gsi_data['status'] = 'Historical'
            gsi_data['arc_owner'] = 'Sim'
            story_progression_data.append(gsi_data)

    household_story_progression_tracker = sim_info.household.story_progression_tracker
    if household_story_progression_tracker is not None:
        current_arcs = household_story_progression_tracker.current_arcs
        for arc in current_arcs:
            gsi_data = arc.get_gsi_data()
            gsi_data['status'] = 'Current'
            gsi_data['arc_owner'] = 'Household'
            story_progression_data.append(gsi_data)

        historical_arcs = household_story_progression_tracker.historical_arcs
        for arc in historical_arcs:
            gsi_data = arc.get_gsi_data()
            gsi_data['status'] = 'Historical'
            gsi_data['arc_owner'] = 'Household'
            story_progression_data.append(gsi_data)

    return story_progression_data