# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_log.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 9612 bytes
from collections import defaultdict
import services
from sims.sim_info_types import Age
from sims4.commands import CheatOutput
from sims4.reload import protected
from sims4.utils import create_csv
from story_progression.story_progression_demographics import ResidentialLotDemographicFunction
with protected(globals()):
    story_progression_log = None

class StoryProgressionDemographicRecord:
    GHOST = 'GHOST'

    def __init__(self):
        self._time_stamp = None
        self._occupied_residential_lots = 0
        self._homeless_households = 0
        self._sims_by_life_demographic = defaultdict(int)
        self._sims_in_careers_by_life_demographic = defaultdict(int)
        self._lot_demographic_results = {}

    def fill_record(self):
        self._time_stamp = services.time_service().sim_now
        for household in services.household_manager().values():
            if household.home_zone_id != 0:
                self._occupied_residential_lots += 1
            else:
                if not household.hidden:
                    self._homeless_households += 1
            for sim_info in household:
                sim_age_key = StoryProgressionDemographicRecord.GHOST if sim_info.is_ghost else sim_info.age
                self._sims_by_life_demographic[sim_age_key] += 1
                if sim_info.career_tracker is None:
                    continue
                for career in sim_info.career_tracker:
                    if career.is_school_career:
                        continue
                    self._sims_in_careers_by_life_demographic[sim_age_key] += 1
                    break

        for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
            result = ResidentialLotDemographicFunction.get_residential_lots_demographics(None, neighborhood_proto, True)
            self._lot_demographic_results[neighborhood_proto.neighborhood_id] = result[0]

    def dump_record(self, file):
        record = str(self._time_stamp) + ','
        record += str(self._occupied_residential_lots) + ','
        record += str(self._homeless_households)
        for age in Age:
            record += ',' + str(self._sims_by_life_demographic[age])

        record += ',' + str(self._sims_by_life_demographic[StoryProgressionDemographicRecord.GHOST])
        for age in Age:
            record += ',' + str(self._sims_in_careers_by_life_demographic[age])

        record += ',' + str(self._sims_in_careers_by_life_demographic[StoryProgressionDemographicRecord.GHOST])
        for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
            record += ',' + str(self._lot_demographic_results[neighborhood_proto.neighborhood_id])

        record += '\n'
        file.write(record)


class StoryProgressionUpdateRecord:

    def __init__(self):
        self._time_stamp = None
        self._name = None
        self._arc = None
        self._chapter = None
        self._outcome = None
        self._extras = None

    def fill_record(self, tracker, arc, chapter, outcome):
        self._time_stamp = services.time_service().sim_now
        self._name = tracker.owner_name
        self._arc = str(arc)
        self._chapter = str(chapter)
        self._outcome = str(outcome)
        self._extras = chapter.get_csv_data()

    def dump_record(self, file):
        record = str(self._time_stamp) + ','
        record += self._name + ','
        record += self._arc + ','
        record += self._chapter + ','
        record += self._outcome
        if self._extras is not None:
            record += ',' + self._extras
        record += '\n'
        file.write(record)


class StoryProgressionLog:

    def __init__(self):
        self._demographic_records = []
        self._update_records = []

    def clear(self):
        self._demographic_records.clear()
        self._update_records.clear()

    def add_story_progression_demographic_record(self):
        record = StoryProgressionDemographicRecord()
        record.fill_record()
        self._demographic_records.append(record)

    def add_story_progression_update_record(self, tracker, arc, chapter, outcome):
        record = StoryProgressionUpdateRecord()
        record.fill_record(tracker, arc, chapter, outcome)
        self._update_records.append(record)

    def dump_demographic_records(self, connection=None):

        def callback(file):
            header = 'In Game Time,Occupied Lots,Homeless Households'
            for age in Age:
                header += ',' + str(age) + ' Sims'

            header += ',GHOST Sims'
            for age in Age:
                header += ',' + str(age) + ' Sims In Careers'

            header += ',GHOST Sims In Careers'
            for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
                header += ',Neighborhood Ratio %: ' + str(neighborhood_proto.neighborhood_id) + ' [' + neighborhood_proto.name + ']'

            header += '\n'
            file.write(header)
            for record in self._demographic_records:
                record.dump_record(file)

        create_csv('story_progression_demographics_record', callback=callback, connection=connection)

    def dump_process_records(self, connection=None):

        def callback(file):
            file.write('In Game Time,Sim/Household Name,Arc,Chapter,Outcome,Additional Data\n')
            for record in self._update_records:
                record.dump_record(file)

        create_csv('story_progression_update_record', callback=callback, connection=connection)

    def dump_records(self):
        self.dump_demographic_records()
        self.dump_process_records()


def start_story_progression_log():
    global story_progression_log
    if story_progression_log is not None:
        return
    story_progression_log = StoryProgressionLog()


def stop_story_progression_log():
    global story_progression_log
    if story_progression_log is None:
        return
    story_progression_log.clear()
    story_progression_log = None


def clear_story_progression_log():
    if story_progression_log is None:
        return
    story_progression_log.clear()


def dump_story_progression_log(connection=None):
    output = CheatOutput(connection)
    if story_progression_log is None:
        output('Story Progression Logging is disabled.  Please enable using |story_progression.story_progression_log.enable')
        return
    story_progression_log.dump_demographic_records(connection=connection)
    output('Story Progression Logging dumped. The file will be written to the same directory as the executable, and has the name story_progression_demographics_record-YYYY-MM-DD-hh-mm-ss.csv')
    story_progression_log.dump_process_records(connection=connection)
    output('Story Progression Logging dumped. The file will be written to the same directory as the executable, and has the name story_progression_update_record-YYYY-MM-DD-hh-mm-ss.csv')


def log_story_progression_demographics():
    if story_progression_log is None:
        return
    story_progression_log.add_story_progression_demographic_record()


def log_story_progression_update(tracker, arc, chapter, outcome):
    if story_progression_log is None:
        return
    story_progression_log.add_story_progression_update_record(tracker, arc, chapter, outcome)