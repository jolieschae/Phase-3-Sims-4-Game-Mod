# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\commodity_tracker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 13679 bytes
from objects.mixins import AffordanceCacheMixin, ProvidedAffordanceData
from sims.sim_info_lod import SimInfoLODLevel
from statistics.continuous_statistic_tracker import ContinuousStatisticTracker
from statistics.skill import Skill
from statistics.statistic_enums import CommodityTrackerSimulationLevel
import services, sims, sims4.log
logger = sims4.log.Logger('Commodities')

class CommodityTracker(AffordanceCacheMixin, ContinuousStatisticTracker):
    __slots__ = ('simulation_level', 'load_in_progress', '_super_affordances_cache',
                 '_target_provided_affordances_cache', '_actor_mixers_cache', '_provided_mixers_cache')

    def __init__(self, owner):
        super().__init__(owner)
        self.simulation_level = CommodityTrackerSimulationLevel.REGULAR_SIMULATION
        self.load_in_progress = False

    def add_statistic(self, stat_type, create_instance=True, **kwargs):
        commodity = (super().add_statistic)(stat_type, create_instance=create_instance, **kwargs)
        if commodity is not None:
            self.owner.statistic_component.apply_statistic_modifiers_on_stat(commodity)
        return commodity

    def should_suppress_calculations(self):
        return self.suppress_callback_alarm_calculation or self.load_in_progress

    def remove_listener(self, listener):
        stat_type = listener.statistic_type
        super().remove_listener(listener)
        self._cleanup_noncore_commodity(stat_type)

    def _cleanup_noncore_commodity(self, stat_type):
        commodity = self.get_statistic(stat_type)
        if commodity is not None:
            if not commodity.core:
                if commodity.remove_on_convergence:
                    if commodity.is_at_convergence():
                        self.remove_statistic(stat_type)

    def set_value(self, stat_type, value, from_load=False, from_init=False, **kwargs):
        (super().set_value)(stat_type, value, from_load=from_load, from_init=from_init, **kwargs)
        self._cleanup_noncore_commodity(stat_type)

    def add_value(self, stat_type, increment, **kwargs):
        (super().add_value)(stat_type, increment, **kwargs)
        self._cleanup_noncore_commodity(stat_type)

    def send_commodity_progress_update(self, from_add=False):
        for statistic in tuple(self._statistics_values_gen()):
            if not statistic.can_decay():
                continue
            statistic.create_and_send_commodity_update_msg(from_add=from_add)

    def on_initial_startup(self):
        for commodity in tuple(self._statistics_values_gen()):
            commodity.on_initial_startup()
            self._cleanup_noncore_commodity(commodity.stat_type)

        self.check_for_unneeded_initial_statistics()
        if self.owner.is_sim:
            self.send_commodity_progress_update(from_add=True)

    def start_low_level_simulation(self):
        self.simulation_level = CommodityTrackerSimulationLevel.LOW_LEVEL_SIMULATION
        self.stop_regular_simulation()
        for commodity in tuple(self._statistics_values_gen()):
            commodity.start_low_level_simulation()

        self.check_for_unneeded_initial_statistics()
        owner = self.owner
        if owner is not None:
            if owner.is_selectable:
                self.send_commodity_progress_update(from_add=True)

    def stop_low_level_simulation(self):
        for commodity in tuple(self._statistics_values_gen()):
            commodity.stop_low_level_simulation()

    def start_regular_simulation(self):
        self.simulation_level = CommodityTrackerSimulationLevel.REGULAR_SIMULATION
        self.stop_low_level_simulation()
        self.on_initial_startup()
        self._owner.trait_tracker.sort_and_send_commodity_list()

    def stop_regular_simulation(self):
        for commodity in tuple(self._statistics_values_gen()):
            commodity.stop_regular_simulation()

    def on_zone_load(self):
        for commodity in self._statistics_values_gen():
            commodity.on_zone_load()

    def _load_delayed_active_statistics(self):
        statistic_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for commodity_proto in self._delayed_active_lod_statistics:
            commodity_class = statistic_manager.get(commodity_proto.name_hash)
            commodity_class.load_statistic_data(self, commodity_proto)

        self._delayed_active_lod_statistics = None

    def _get_stat_data_for_active_lod(self, statistic):
        return statistic.get_save_message(self)

    def save(self):
        commodities = []
        skills = []
        ranked_statistics = []
        for stat in tuple(self._statistics_values_gen()):
            if not stat.persisted:
                continue
            try:
                stat.save_statistic(commodities, skills, ranked_statistics, self)
            except Exception as e:
                try:
                    logger.error('Exception {} thrown while trying to save stat {}', e, stat)
                finally:
                    e = None
                    del e

        if self._delayed_active_lod_statistics is not None:
            statistic_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
            for commodity_proto in self._delayed_active_lod_statistics:
                commodity_class = statistic_manager.get(commodity_proto.name_hash)
                commodity_class.save_for_delayed_active_lod(commodity_proto, commodities, skills, ranked_statistics)

        return (
         commodities, skills, ranked_statistics)

    def load(self, statistics, skip_load=False, update_affordance_cache=True):
        statistic_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        try:
            self.load_in_progress = True
            owner_lod = self._owner.lod if isinstance(self._owner, sims.sim_info.SimInfo) else None
            for commodity_proto in statistics:
                commodity_class = statistic_manager.get(commodity_proto.name_hash)
                if commodity_class is None:
                    logger.info('Trying to load unavailable STATISTIC resource: {}', (commodity_proto.name_hash), owner='rez')
                    continue
                if not commodity_class.persisted:
                    logger.info('Trying to load unavailable STATISTIC resource: {}', (commodity_proto.name_hash), owner='rez')
                    continue
                if commodity_class.is_commodity:
                    if commodity_class._test_on_load:
                        foundTrait = False
                        for trait in commodity_class._test_on_load:
                            if trait is not None and self.owner.trait_tracker.has_trait(trait):
                                foundTrait = True
                                break

                        if not foundTrait:
                            continue
                if self.statistics_to_skip_load is not None:
                    if commodity_class in self.statistics_to_skip_load:
                        continue
                if commodity_class.is_skill:
                    if commodity_proto.value == commodity_class.initial_value:
                        continue
                if skip_load:
                    if commodity_class.remove_on_convergence:
                        logger.info('Not loading {} because load is not required.', commodity_class, owner='rez')
                        continue
                if not self._should_add_commodity_from_gallery(commodity_class, skip_load):
                    continue
                if owner_lod is not None:
                    if owner_lod < commodity_class.min_lod_value:
                        if commodity_class.min_lod_value >= SimInfoLODLevel.ACTIVE:
                            if self._delayed_active_lod_statistics is None:
                                self._delayed_active_lod_statistics = list()
                            self._delayed_active_lod_statistics.append(commodity_proto)
                            continue
                    commodity_class.load_statistic_data(self, commodity_proto)

        finally:
            self.statistics_to_skip_load = None
            self.load_in_progress = False

        if update_affordance_cache:
            self.update_affordance_caches()

    def get_sim(self):
        return self._owner.get_sim_instance()

    def update_all_commodities(self):
        commodities_to_update = tuple(self._statistics_values_gen())
        for commodity in commodities_to_update:
            commodity._update_value()

        self.check_for_unneeded_initial_statistics()

    def get_all_commodities(self):
        if self._statistics is None:
            return ()
        stat_iter = self._statistics.values()
        return tuple((stat for stat in stat_iter if stat is not None))

    def get_provided_super_affordances(self):
        affordances, target_affordances = set(), list()
        for commodity in self._statistics_values_gen():
            if not commodity.is_skill:
                continue
            skill_affordances, skill_target_affordances = commodity.get_skill_provided_affordances()
            affordances.update(skill_affordances)
            for provided_affordance in skill_target_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                target_affordances.append(provided_affordance_data)

        return (
         affordances, target_affordances)

    def get_actor_and_provided_mixers_list(self):
        actor_mixers = []
        for commodity in self._statistics_values_gen():
            if commodity.is_skill:
                skill_provided_actor_mixers = commodity.get_skill_provided_actor_mixers()
                if skill_provided_actor_mixers is not None:
                    actor_mixers.append(skill_provided_actor_mixers)

        return (
         actor_mixers, ())

    def get_sim_info_from_provider(self):
        return self.owner