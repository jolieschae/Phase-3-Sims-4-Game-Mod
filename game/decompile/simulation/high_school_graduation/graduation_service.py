# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\high_school_graduation\graduation_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 11875 bytes
import persistence_error_types, random, services, sims4
from sims4.common import Pack
from sims4.math import MAX_UINT32
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableSimMinute, TunablePackSafeReference
from sims4.utils import classproperty
logger = sims4.log.Logger('HighSchoolGraduation', default_owner='rfleig')

class GraduationService(Service):
    GRADUATION_DRAMA_NODE = TunablePackSafeReference(description='\n        A reference to the graduation drama node used in code to find the next scheduled graduation event. Please do \n        not tune unless you talk with a GPE first as this should only need to be tuned initially.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)))
    MIN_TIME_REQUIRED_BEFORE_GRADUATION = TunableSimMinute(description='\n        The minimum amount of time before a graduation that a Sim must age up to young adult in order to be considered\n        for the current weeks graduation. If the Sim ages up closer to graduation then they will be considered as\n        graduating as the next possible graduation ceremony.\n        ',
      default=1440)
    DRAMA_NODE_RUNNING = -1

    def __init__(self):
        self._graduating_sims = set()
        self._sims_waiting_to_graduate = set()
        self._current_valedictorian = None
        self._waiting_valedictorian = None

    @classproperty
    def required_packs(cls):
        return (
         Pack.EP12,)

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_GRADUATION_SERVICE

    def graduating_sims_gen(self):
        yield from self._graduating_sims
        yield from self._sims_waiting_to_graduate
        if False:
            yield None

    def current_graduating_sims(self):
        return self._graduating_sims

    def waiting_to_graduate_sims(self):
        return self._sims_waiting_to_graduate

    def add_sim_info_as_graduating(self, sim_info):
        time_to_next_graduation = self.time_to_next_scheduled_graduation()
        if time_to_next_graduation == self.DRAMA_NODE_RUNNING and sim_info.is_npc or time_to_next_graduation != MAX_UINT32:
            if time_to_next_graduation.in_minutes() >= GraduationService.MIN_TIME_REQUIRED_BEFORE_GRADUATION:
                self.add_sim_info_as_current_graduate(sim_info)
                return
        self.add_sim_info_as_waiting_graduate(sim_info)

    def add_sim_info_as_current_graduate(self, sim_info):
        self._graduating_sims.add(sim_info)

    def add_sim_info_as_waiting_graduate(self, sim_info):
        self._sims_waiting_to_graduate.add(sim_info)

    def remove_sim_info_as_graduating(self, sim_info):
        self.remove_sim_info_currently_graduating(sim_info)
        self.remove_sim_info_waiting_to_graduate(sim_info)

    def is_sim_info_graduating(self, sim_info):
        return sim_info in self._graduating_sims

    def remove_sim_info_currently_graduating(self, sim_info):
        if sim_info in self._graduating_sims:
            self._graduating_sims.remove(sim_info)

    def is_sim_info_waiting_to_graduate(self, sim_info):
        return sim_info in self._sims_waiting_to_graduate

    def remove_sim_info_waiting_to_graduate(self, sim_info):
        if sim_info in self._sims_waiting_to_graduate:
            self._sims_waiting_to_graduate.remove(sim_info)

    def time_to_next_scheduled_graduation(self):
        drama_scheduler = services.drama_scheduler_service()
        graduation_drama_nodes = drama_scheduler.get_running_nodes_by_class(GraduationService.GRADUATION_DRAMA_NODE)
        if graduation_drama_nodes:
            return self.DRAMA_NODE_RUNNING
        else:
            processing_node = drama_scheduler.processing_node
            if type(processing_node) == GraduationService.GRADUATION_DRAMA_NODE:
                return self.DRAMA_NODE_RUNNING
            graduation_drama_nodes = drama_scheduler.get_scheduled_nodes_by_class(GraduationService.GRADUATION_DRAMA_NODE)
            return graduation_drama_nodes or MAX_UINT32
        return graduation_drama_nodes[0].get_time_remaining()

    def add_sim_as_valedictorian(self, sim_info):
        if sim_info in self._graduating_sims:
            return self.set_current_valedictorian(sim_info)
        if sim_info in self._sims_waiting_to_graduate:
            return self.set_waiting_valedictorian(sim_info)
        logger.error("Trying to make a Sim the valedictorian when we don't know when they will graduate: {}", sim_info)
        return False

    def set_current_valedictorian(self, sim_info):
        if self._current_valedictorian is None:
            self._current_valedictorian = sim_info
            return True
        return False

    def clear_current_valedictorian(self):
        self._current_valedictorian = None

    def has_current_valedictorian(self):
        return self._current_valedictorian is not None

    def is_current_valedictorian(self, sim_info):
        return sim_info is self._current_valedictorian

    def set_waiting_valedictorian(self, sim_info):
        if self._waiting_valedictorian is None:
            self._waiting_valedictorian = sim_info
            return True
        return False

    def is_waiting_valedictorian(self, sim_info):
        return sim_info is self._waiting_valedictorian

    def clear_waiting_valedictorian(self):
        self._waiting_valedictorian = None

    def choose_random_valedictorian(self):
        graduating_npcs = [sim for sim in self._graduating_sims if sim.is_npc]
        if not graduating_npcs:
            return
        self.set_current_valedictorian(random.choice(graduating_npcs))

    def graduating_sim_count(self):
        return len(self._graduating_sims)

    def move_waiting_graduates_to_current(self):
        self._graduating_sims.update(self._sims_waiting_to_graduate)
        self._sims_waiting_to_graduate.clear()
        self._current_valedictorian = self._waiting_valedictorian
        self._waiting_valedictorian = None

    def clear_current_graduates(self):
        self._graduating_sims.clear()
        self._current_valedictorian = None

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        if save_slot_data is None:
            return
        graduation_save_data = save_slot_data.gameplay_data.graduation_service
        del graduation_save_data.graduating_sim_ids[:]
        del graduation_save_data.waiting_to_graduate_sim_ids[:]
        graduation_save_data.current_valedictorian_id = 0
        for sim in self._graduating_sims:
            graduation_save_data.graduating_sim_ids.append(sim.id)

        for sim in self._sims_waiting_to_graduate:
            graduation_save_data.waiting_to_graduate_sim_ids.append(sim.id)

        if self._current_valedictorian is not None:
            graduation_save_data.current_valedictorian_id = self._current_valedictorian.id
        if self._waiting_valedictorian is not None:
            graduation_save_data.waiting_valedictorian_id = self._waiting_valedictorian.id

    def on_zone_load(self):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        graduation_service_data = save_slot_data_msg.gameplay_data.graduation_service
        sim_info_manager = services.sim_info_manager()
        if sim_info_manager is None:
            return
        for sim_id in graduation_service_data.graduating_sim_ids:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is not None:
                self._graduating_sims.add(sim_info)

        for sim_id in graduation_service_data.waiting_to_graduate_sim_ids:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is not None:
                self._sims_waiting_to_graduate.add(sim_info)

        if not graduation_service_data.current_valedictorian_id == 0:
            sim_info = sim_info_manager.get(graduation_service_data.current_valedictorian_id)
            if sim_info is not None:
                self._current_valedictorian = sim_info
        if not graduation_service_data.waiting_valedictorian_id == 0:
            sim_info = sim_info_manager.get(graduation_service_data.waiting_valedictorian_id)
            if sim_info is not None:
                self._waiting_valedictorian = sim_info