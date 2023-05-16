# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\service_npcs\service_npc_record.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 7672 bytes
from date_and_time import DateAndTime
from sims4.resources import Types
import services, sims4.log
logger = sims4.log.Logger('ServiceNPCManager', default_owner='camilogarcia')

class ServiceNpcRecord:

    def __init__(self, service_id, household):
        self._service_id = service_id
        self._household = household
        self._preferred_service_sim_ids = set()
        self._fired_service_sim_ids = set()
        self.hired = False
        self.recurring = False
        self.time_last_started_service = None
        self.time_last_finished_service = None
        self.user_specified_data_id = None
        self.user_specified_selections = None
        self.hiring_sim_id = None

    def __repr__(self):
        return '{} {}'.format(self._household, services.get_instance_manager(Types.SERVICE_NPC).get(self._service_id))

    def add_fired_sim(self, sim_id):
        self._fired_service_sim_ids.add(sim_id)

    def add_preferred_sim(self, sim_id):
        if sim_id in self._fired_service_sim_ids:
            logger.error('{} is adding {} to the preferred list despite being in the fired list.', self, sim_id)
            self._fired_service_sim_ids.remove(sim_id)
        return self._preferred_service_sim_ids.add(sim_id)

    def remove_preferred_sim(self, sim_id):
        if sim_id in self._preferred_service_sim_ids:
            self._preferred_service_sim_ids.remove(sim_id)

    def get_preferred_sim_id(self, household=None):
        self._validate_preferred_sim_ids()
        if self._preferred_service_sim_ids:
            return next(iter(self._preferred_service_sim_ids), None)

    def _validate_preferred_sim_ids(self):
        if self._household is not None:
            for sim_id in tuple(self._preferred_service_sim_ids):
                if self._household.sim_in_household(sim_id):
                    self._preferred_service_sim_ids.remove(sim_id)

    @property
    def service_id(self):
        return self._service_id

    @property
    def preferred_sim_ids(self):
        return self._preferred_service_sim_ids

    @property
    def fired_sim_ids(self):
        return self._fired_service_sim_ids

    def on_cancel_service(self):
        self.hired = False
        self.time_last_started_service = None
        self.time_last_finished_service = None
        self.recurring = False

    def save_npc_record(self, record_msg):
        record_msg.service_type = self._service_id
        record_msg.preferred_sim_ids.extend(self._preferred_service_sim_ids)
        record_msg.fired_sim_ids.extend(self._fired_service_sim_ids)
        record_msg.hired = self.hired
        if self.hiring_sim_id is not None:
            record_msg.hiring_sim_id = self.hiring_sim_id
        if self.time_last_started_service is not None:
            record_msg.time_last_started_service = self.time_last_started_service.absolute_ticks()
        record_msg.recurring = self.recurring
        if self.time_last_finished_service is not None:
            record_msg.time_last_finished_service = self.time_last_finished_service.absolute_ticks()
        if self.user_specified_data_id is not None:
            record_msg.user_specified_data_id = self.user_specified_data_id
        if self.user_specified_selections is not None:
            record_msg.user_specified_data_selection.extend(self.user_specified_selections[0])
            record_msg.user_specified_data_selection_count.extend(self.user_specified_selections[1])

    def load_npc_record(self, record_msg):
        self._service_id = record_msg.service_type
        self._preferred_service_sim_ids.clear()
        self._fired_service_sim_ids.clear()
        self._preferred_service_sim_ids = set(record_msg.preferred_sim_ids)
        self._fired_service_sim_ids = set(record_msg.fired_sim_ids)
        self.hired = record_msg.hired
        self.hiring_sim_id = record_msg.hiring_sim_id
        if record_msg.HasField('time_last_started_service'):
            self.time_last_started_service = DateAndTime(record_msg.time_last_started_service)
        self.recurring = record_msg.recurring
        if record_msg.HasField('time_last_finished_service'):
            self.time_last_finished_service = DateAndTime(record_msg.time_last_finished_service)
        if record_msg.HasField('user_specified_data_id'):
            self.user_specified_data_id = record_msg.user_specified_data_id
        if record_msg.user_specified_data_selection:
            if record_msg.user_specified_data_selection_count:
                data_selections = list(record_msg.user_specified_data_selection)
                data_selections_counts = list(record_msg.user_specified_data_selection_count)
                self.user_specified_selections = (data_selections, data_selections_counts)

    def load_fixup(self):
        mgr = services.sim_info_manager()

        def is_valid(sim_id):
            si = mgr.get(sim_id)
            return si is not None and si.can_instantiate_sim

        fired = set(self._fired_service_sim_ids)
        self._fired_service_sim_ids = set([i for i in fired if is_valid(i)])
        preferred = set(self._preferred_service_sim_ids)
        self._preferred_service_sim_ids = set([i for i in preferred if is_valid(i)])
        intersection = self._fired_service_sim_ids & self._preferred_service_sim_ids
        if intersection:
            logger.error('{} duplicated {} in fired and preferred lists.', self, intersection)