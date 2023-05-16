# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fashion_trends\fashion_trend_service.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 38274 bytes
from collections import Counter
from distributor.rollback import ProtocolBufferRollback
from objects.components import ComponentContainer
from objects.components.statistic_component import HasStatisticComponent
from protocolbuffers.Consts_pb2 import FUNDS_CAS_BUY
import elements, random, sims4.log
from cas.cas import randomize_caspart_list, get_tags_from_outfit
from event_testing.resolver import SingleSimResolver
from objects.system import create_object
from persistence_error_types import ErrorCodes
from rewards.tunable_reward_base import TunableRewardBase
from sims.outfits.outfit_enums import OutfitCategory, SpecialOutfitIndex
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from sims.sim_info_types import Age, Gender
from sims4.common import Pack
from sims4.localization import LocalizationHelperTuning
from sims4.math import MAX_UINT32
from sims4.service_manager import Service
from sims4.utils import classproperty, constproperty
from fashion_trends.fashion_trend_tuning import FashionTrendTuning, FashionThriftStoreTuning
import date_and_time, services
logger = sims4.log.Logger('fashion_trend_service', default_owner='anchavez')

class FashionTrendService(Service, ComponentContainer, HasStatisticComponent):

    def __init__(self):
        self._next_trend_shift_ticks = 0
        self._exclusive_item_unlocked = False
        self._processor_trend_shift_schedule = {}
        self._processor_daily_schedule = None
        self._processor_daily_unlock_schedule = None
        self._thrift_store_inventory = []
        self.thrift_store_mannequin = None
        self._sold_fashion_outfits = []
        self._vfx_money_updates = []

    @classproperty
    def required_packs(cls):
        return (Pack.EP12,)

    @classproperty
    def save_error_code(cls):
        return ErrorCodes.SERVICE_SAVE_FAILED_FASHION_TREND_SERVICE

    def start(self):
        self._setup_trend_shift_alarms()
        self._setup_daily_thrift_store_refresh_alarm()
        self._setup_exclusive_item_unlock_alarm()

    def stop(self):
        for processor_index, processor_key in enumerate(self._processor_trend_shift_schedule):
            if self._processor_trend_shift_schedule[processor_key] is not None:
                self._processor_trend_shift_schedule[processor_key].trigger_hard_stop()
                self._processor_trend_shift_schedule[processor_key] = None

        if self._processor_daily_schedule is not None:
            self._processor_daily_schedule.trigger_hard_stop()
            self._processor_daily_schedule = None
        if self._processor_daily_unlock_schedule is not None:
            self._processor_daily_unlock_schedule.trigger_hard_stop()
            self._processor_daily_unlock_schedule = None

    def save(self, save_slot_data=None, **kwargs):
        if save_slot_data is not None:
            if hasattr(save_slot_data.gameplay_data, 'fashion_trend_service'):
                trend_data = save_slot_data.gameplay_data.fashion_trend_service
                trend_data.Clear()
                trend_data.next_trend_shift_ticks = self._next_trend_shift_ticks
                trend_data.thrift_store_inventory.extend(self.get_current_thrift_store_inventory_cas_part_tags())
                statistics = self.statistic_tracker.save()
                trend_data.statistics_tracker.statistics.extend(statistics)
                commodities, _, _ = self.commodity_tracker.save()
                trend_data.commodity_tracker.commodities.extend(commodities)
                active_sim = services.get_active_sim()
                if active_sim is not None:
                    mannequin_data = self.get_mannequin(active_sim.clothing_preference_gender)
                    if mannequin_data is not None:
                        trend_data.thrift_store_mannequin.mannequin_id = mannequin_data.id
                        self.thrift_store_mannequin.save_sim_info(trend_data.thrift_store_mannequin)
                if hasattr(trend_data, 'sold_fashion_outfits'):
                    for sold_fashion_outfit in self._sold_fashion_outfits:
                        with ProtocolBufferRollback(trend_data.sold_fashion_outfits) as (fashion_marketplace_sold_outfit):
                            sold_outfit_sim_ids = sold_fashion_outfit.get('sims')
                            sold_outfit_instanced_sim_ids = [sim.id for sim in services.sim_info_manager().instanced_sims_gen() if sim.id in sold_outfit_sim_ids]
                            sold_outfit_sim_ids.clear()
                            sold_outfit_sim_ids.extend(sold_outfit_instanced_sim_ids)
                            fashion_marketplace_sold_outfit.sim_ids.extend(sold_outfit_instanced_sim_ids)
                            mannequin_sim_info = sold_fashion_outfit.get('mannequin')
                            fashion_marketplace_sold_outfit.outfit_info_data.mannequin_id = mannequin_sim_info.id
                            mannequin_sim_info.save_sim_info(fashion_marketplace_sold_outfit.outfit_info_data)

    def load(self, zone_data=None):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        if save_slot_data is not None:
            if hasattr(save_slot_data.gameplay_data, 'fashion_trend_service'):
                msg = save_slot_data.gameplay_data.fashion_trend_service
                self._next_trend_shift_ticks = msg.next_trend_shift_ticks
                if msg.HasField('thrift_store_mannequin'):
                    self.thrift_store_mannequin = self._load_mannequin_data(msg.thrift_store_mannequin)
                if msg.thrift_store_inventory:
                    self._thrift_store_inventory.extend([inventory_item for inventory_item in msg.thrift_store_inventory])
                self.statistic_tracker.load(msg.statistics_tracker.statistics)
                self.commodity_tracker.load(msg.commodity_tracker.commodities)
                if hasattr(msg, 'sold_fashion_outfits'):
                    if msg.sold_fashion_outfits:
                        for sold_fashion_outfit in msg.sold_fashion_outfits:
                            sold_fashion_outfit_sims = [sim_id for sim_id in sold_fashion_outfit.sim_ids]
                            sold_fashion_outfit_mannequin = self._load_mannequin_data(sold_fashion_outfit.outfit_info_data)
                            self._sold_fashion_outfits.append({'sims':sold_fashion_outfit_sims,  'mannequin':sold_fashion_outfit_mannequin})

    @constproperty
    def is_sim():
        return False

    @property
    def is_downloaded(self):
        return False

    def on_cleanup_zone_objects(self, _):
        if not self._thrift_store_inventory:
            self._randomize_thrift_store_inventory()

    def create_inventory_outfit_on_zone_spin_up(self):
        if self.thrift_store_mannequin is None:
            return
        service_mannequin_outfits = self.thrift_store_mannequin.get_outfits()
        if service_mannequin_outfits is None:
            return
        sim = services.get_active_sim()
        if sim is None:
            logger.warn('There was no valid active sim available')
            return
        active_household = services.active_household()
        if active_household is None:
            logger.warn('There was no active household available')
            return
        persistence_service = services.get_persistence_service()
        if persistence_service is None:
            logger.warn('Persistence Service was not available')
            return
        if FashionThriftStoreTuning.FASHION_OUTFIT_OBJECT_DEFINITION is None:
            logger.warn('Fashion Outfit object definition is not available, tuning may not be exported {}', '')
            return
        exclusive_tags = []
        for refresh_cas_parts_item in FashionThriftStoreTuning.REFRESH_CAS_PART_LIST:
            if refresh_cas_parts_item.is_exclusive:
                exclusive_tags.extend([tag.value for tag in refresh_cas_parts_item.include_tags])

        purchase_amount = 0
        for outfit_index, outfit_data in enumerate(service_mannequin_outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
            outfit_prevalent_trend_tag = self.get_outfit_trend(outfit_data)
            outfit_object_definition = FashionThriftStoreTuning.FASHION_OUTFIT_OBJECT_DEFINITION
            if outfit_prevalent_trend_tag is not None:
                outfit_object_definition = FashionTrendTuning.TRENDS[outfit_prevalent_trend_tag].trend_outfit_object_definition
            outfit_object = create_object(outfit_object_definition)
            if outfit_object.mannequin_component is None:
                logger.error('The specified target does not have a Mannequin component. outfit_object.id={}', outfit_object.id)
                return
                persistence_service.del_mannequin_proto_buff(outfit_object.id)
                sim_info_data_proto = persistence_service.add_mannequin_proto_buff()
                outfit_object.mannequin_component.sim_info_data.add_outfit(OutfitCategory.EVERYDAY, outfit_data)
                outfit_object.mannequin_component.populate_sim_info_data_proto(sim_info_data_proto)
                outfit_cost = self.get_outfit_cost(outfit_data)
                if hasattr(outfit_data, 'title'):
                    outfit_object.name_component.set_custom_name(outfit_data.title)
                outfit_object.update_ownership(sim.sim_info)
                if not sim.inventory_component.player_try_add_object(outfit_object):
                    logger.warn('object failed to be placed into inventory: {}', outfit_object)
                    outfit_object.destroy(source=sim, cause='object failed to be placed into inventory')
                    return
                purchase_amount += outfit_cost
                caspartid_tags_dic = get_tags_from_outfit(service_mannequin_outfits._base, OutfitCategory.EVERYDAY, outfit_index)
                for outfit_part_id, outfit_part_tags in caspartid_tags_dic.items():
                    if any((tag in exclusive_tags for tag in outfit_part_tags)):
                        self._unlock_cas_part(target_sim=sim, cas_part=outfit_part_id)

                if outfit_cost > 0:
                    self._vfx_money_updates.append(outfit_cost)

        service_mannequin_outfits.remove_outfits_in_category(OutfitCategory.EVERYDAY)
        sim_info_data_proto = persistence_service.get_mannequin_proto_buff(self.thrift_store_mannequin.id)
        if hasattr(sim_info_data_proto, 'outfits'):
            sim_info_data_proto.outfits = self.thrift_store_mannequin.save_outfits()
        if purchase_amount > 0:
            active_household.funds.try_remove_amount(purchase_amount, FUNDS_CAS_BUY, sim)

    def get_outfit_trend(self, outfit_data):
        if hasattr(outfit_data, 'trend'):
            if outfit_data.trend != 0:
                return outfit_data.trend

    def get_outfit_all_trend_styles(self, tags):
        trend_tag_counts = Counter()
        for cas_part_tags in tags.values():
            for trend_tag in FashionTrendTuning.TRENDS:
                if trend_tag.value in cas_part_tags:
                    trend_tag_counts[trend_tag] += 1

        return trend_tag_counts

    def get_outfit_prevalent_trend_tag(self, target):
        outfit_prevalent_trend_tag = None
        if target.is_sim:
            sim_outfits = target.get_outfits()
            if sim_outfits is not None and sim_outfits.has_outfit_category(OutfitCategory.SPECIAL):
                sim_outfit_data = sim_outfits.get_outfit(OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION)
                outfit_prevalent_trend_tag = self.get_outfit_trend(sim_outfit_data)
        else:
            outfit_object_mannequin = target.mannequin_component
            if outfit_object_mannequin is not None:
                mannequin_outfits = outfit_object_mannequin.get_outfits()
                if mannequin_outfits is not None:
                    mannequin_outfit_data = mannequin_outfits.get_outfit(OutfitCategory.EVERYDAY, 0)
                    outfit_prevalent_trend_tag = self.get_outfit_trend(mannequin_outfit_data)
        return outfit_prevalent_trend_tag

    def get_outfit_prevalent_trend_name(self, target):
        outfit_prevalent_trend = None
        outfit_prevalent_trend_tag = self.get_outfit_prevalent_trend_tag(target)
        if outfit_prevalent_trend_tag is not None:
            outfit_prevalent_trend = FashionTrendTuning.TRENDS.get(outfit_prevalent_trend_tag).trend_name
        return outfit_prevalent_trend

    def get_outfit_prevalent_trend(self, target):
        outfit_prevalent_trend = None
        outfit_prevalent_trend_name = self.get_outfit_prevalent_trend_name(target)
        if outfit_prevalent_trend_name is not None:
            outfit_prevalent_trend = LocalizationHelperTuning.get_raw_text(outfit_prevalent_trend_name)
        return outfit_prevalent_trend

    def get_outfit_cost(self, outfit_data):
        if hasattr(outfit_data, 'cost'):
            return outfit_data.cost
        return 0

    def get_outfit_suggested_sale_price(self, target):
        outfit_cost = 0
        mannequin = target.mannequin_component
        if mannequin is not None:
            outfits = mannequin.get_outfits()
            if outfits is not None:
                outfit_data = outfits.get_outfit(OutfitCategory.EVERYDAY, 0)
                outfit_cost = self.get_outfit_cost(outfit_data)
        return outfit_cost

    def add_fashion_outfit_to_sold_list(self, source_object):
        if len(self._sold_fashion_outfits) == FashionThriftStoreTuning.MAX_ALLOWED_SOLD_OUTFITS:
            self._sold_fashion_outfits.pop(0)
        mannequin_sim_info_data = source_object.mannequin_component.sim_info_data
        new_entry = {'sims':[],  'mannequin':mannequin_sim_info_data}
        self._sold_fashion_outfits.append(new_entry)

    def apply_sold_fashion_outfit(self, target_sim):
        if target_sim is not None:
            if target_sim.is_sim:
                target_sim_info = target_sim.sim_info
                if not self._sold_fashion_outfits:
                    return
                sold_outfit_selected = None
                for sold_outfit_data in self._sold_fashion_outfits:
                    if target_sim.id in sold_outfit_data.get('sims'):
                        sold_outfit_selected = sold_outfit_data
                        break

                if sold_outfit_selected is None:
                    seeded_random = random.Random()
                    seeded_random.seed(target_sim_info.id)
                    sold_outfit_selected = seeded_random.choice(self._sold_fashion_outfits)
                sold_outfit_mannequin = sold_outfit_selected.get('mannequin')
                if sold_outfit_mannequin is not None:
                    outfits = sold_outfit_mannequin.get_outfits()
                    if outfits is not None:
                        sim_info_source = outfits.get_sim_info()
                        current_outfit_category, current_outfit_index = target_sim_info.get_current_outfit()
                        sold_outfit_assigned_sims = sold_outfit_selected.get('sims')
                        if target_sim.id not in sold_outfit_assigned_sims:
                            sold_outfit_assigned_sims.append(target_sim.id)
                        target_sim_info.generate_merged_outfit(sim_info_source, (
                         OutfitCategory.SITUATION, 0), (
                         current_outfit_category, current_outfit_index), (
                         OutfitCategory.EVERYDAY, 0))
                target_sim_info.set_current_outfit((OutfitCategory.SITUATION, 0))
                target_sim_info.resend_current_outfit()

    def _load_mannequin_data(self, saved_mannequin):
        sim_info = SimInfoBaseWrapper(sim_id=(saved_mannequin.mannequin_id))
        persistence_service = services.get_persistence_service()
        if persistence_service is not None:
            persisted_data = persistence_service.get_mannequin_proto_buff(saved_mannequin.mannequin_id)
            if persisted_data is not None:
                saved_mannequin = persisted_data
        sim_info.load_sim_info(saved_mannequin)
        return sim_info

    def get_mannequin(self, gender, sim_id=0):
        if self.thrift_store_mannequin is not None:
            if self.thrift_store_mannequin.gender == gender:
                return self.thrift_store_mannequin
        elif gender == Gender.MALE:
            resource = FashionThriftStoreTuning.DEFAULT_MANNEQUIN_DATA.male_adult
        else:
            if gender == Gender.FEMALE:
                resource = FashionThriftStoreTuning.DEFAULT_MANNEQUIN_DATA.female_adult
        if resource is None:
            logger.warn('The mannequin template could not be found, tuning may not be exported. resource={}', resource)
            return
        self.thrift_store_mannequin = SimInfoBaseWrapper(sim_id=sim_id)
        self.thrift_store_mannequin.load_from_resource(resource)
        return self.thrift_store_mannequin

    def get_mannequin_pose(self):
        thrift_store_mannequin_tuning_data = FashionThriftStoreTuning.DEFAULT_MANNEQUIN_DATA
        if thrift_store_mannequin_tuning_data is None:
            return
        return thrift_store_mannequin_tuning_data.mannequin_pose

    def get_current_thrift_store_inventory_cas_part_tags(self):
        return [cas_part_tag for cas_part_tag in self._thrift_store_inventory]

    def _unlock_cas_part(self, target_sim, cas_part):
        if not target_sim.is_sim:
            logger.error('Attempting to apply CAS Unlock to {} which is not a Sim.', target_sim)
            return False
        household = target_sim.household
        if not household.part_in_reward_inventory(cas_part):
            household.add_cas_part_to_reward_inventory(cas_part)
        TunableRewardBase.send_unlock_telemetry(target_sim.sim_info, cas_part, 0)
        return True

    def _apply_loots(self, loot_list):
        active_sim = services.get_active_sim()
        if active_sim is not None:
            resolver = SingleSimResolver(active_sim.sim_info)
            for loot in loot_list:
                loot.apply_to_resolver(resolver)

    def has_buff(self, buff_type):
        return False

    def debug_randomize_thrift_store_inventory(self):
        pass

    def _shift_fashion_trend(self, fashion_trend):
        fashion_trend_stat_tracker = self.statistic_tracker
        if fashion_trend_stat_tracker is not None:
            trend_stat = FashionTrendTuning.TRENDS.get(fashion_trend).trend_statistic
            fashion_trend_statistic = fashion_trend_stat_tracker.get_statistic(trend_stat)
            if fashion_trend_statistic is None:
                self.statistic_tracker.add_statistic(trend_stat)
            self._apply_loots(FashionTrendTuning.TRENDS.get(fashion_trend).trend_shift_loot)

    def _apply_vfx_updates(self):
        outfit_purchase_amount = sum(self._vfx_money_updates)
        if outfit_purchase_amount > 0:
            active_household = services.active_household()
            if active_household is not None:
                active_household.funds.send_money_update(vfx_amount=(-outfit_purchase_amount), reason=FUNDS_CAS_BUY)
            self._vfx_money_updates.clear()

    def _setup_trend_shift_alarms(self, process_fashion_trend=None):
        if process_fashion_trend is not None:
            self._schedule_fashion_trend_shift(process_fashion_trend)
        else:
            for fashion_trend in FashionTrendTuning.TRENDS:
                self._schedule_fashion_trend_shift(fashion_trend)

    def _schedule_fashion_trend_shift(self, fashion_trend=None):
        if fashion_trend is None:
            return
        current_time = services.time_service().sim_now
        current_day_hour = date_and_time.create_date_and_time(days=(int(current_time.day())), hours=(int(current_time.hour())))
        fashion_trend_shift_interval_time_delay = FashionTrendTuning.TRENDS.get(fashion_trend).trend_shift_interval()
        trend_shift_start_time = date_and_time.date_and_time_from_week_time(current_time.week(), current_day_hour)
        self._next_trend_shift_ticks = trend_shift_start_time.absolute_ticks()
        schedule_time = trend_shift_start_time + fashion_trend_shift_interval_time_delay
        sim_timeline = services.time_service().sim_timeline
        self._processor_trend_shift_schedule[fashion_trend] = sim_timeline.schedule((elements.GeneratorElement(self._process_trend_shift_schedule_gen(fashion_trend))),
          when=schedule_time)

    def _setup_daily_thrift_store_refresh_alarm(self):
        day_time = date_and_time.create_date_and_time(hours=(int(FashionThriftStoreTuning.DAILY_REFRESH_TIME.hour())),
          minutes=(int(FashionThriftStoreTuning.DAILY_REFRESH_TIME.minute())))
        now = services.time_service().sim_now
        time_delay = now.time_till_next_day_time(day_time, True)
        if time_delay.in_ticks() == 0:
            time_delay = date_and_time.create_time_span(days=1)
        schedule_time = now + time_delay
        sim_timeline = services.time_service().sim_timeline
        self._processor_daily_schedule = sim_timeline.schedule((elements.GeneratorElement(self._process_daily_schedule_gen)),
          when=schedule_time)

    def _setup_exclusive_item_unlock_alarm(self):
        day_time = date_and_time.create_date_and_time(hours=(int(FashionThriftStoreTuning.EXCLUSIVE_ITEM_NOTIFICATION_TIME.hour())),
          minutes=(int(FashionThriftStoreTuning.EXCLUSIVE_ITEM_NOTIFICATION_TIME.minute())))
        now = services.time_service().sim_now
        time_delay = now.time_till_next_day_time(day_time, True)
        if time_delay.in_ticks() == 0:
            time_delay = date_and_time.create_time_span(days=1)
        schedule_time = now + time_delay
        sim_timeline = services.time_service().sim_timeline
        self._processor_daily_unlock_schedule = sim_timeline.schedule((elements.GeneratorElement(self._process_daily_unlock_schedule_gen)),
          when=schedule_time)

    def _randomize_thrift_store_inventory(self):
        random_cas_part_list = []
        seed = random.randint(0, MAX_UINT32)
        if random.random() <= FashionThriftStoreTuning.EXCLUSIVE_ITEM_CHANCE:
            self._exclusive_item_unlocked = True
        else:
            self._exclusive_item_unlocked = False
        for cas_part_type in FashionThriftStoreTuning.REFRESH_CAS_PART_LIST:
            if not self._exclusive_item_unlocked:
                if cas_part_type.is_exclusive:
                    continue
            body_type = cas_part_type.body_type
            count = cas_part_type.count
            include_tags = cas_part_type.include_tags
            exclude_tags = cas_part_type.exclude_tags
            cas_parts_list = randomize_caspart_list(include_tags=(list(include_tags)), exclude_tags=(list(exclude_tags)),
              bodytype=body_type,
              count=count,
              seed=seed)
            random_cas_part_list.extend(cas_parts_list)

        self._thrift_store_inventory = random_cas_part_list
        self._show_daily_refresh_notification()

    def _show_daily_refresh_notification(self):
        if FashionThriftStoreTuning.DAILY_REFRESH_NOTIFICATION:
            active_sim_info = services.active_sim_info()
            notification = FashionThriftStoreTuning.DAILY_REFRESH_NOTIFICATION(active_sim_info, resolver=(SingleSimResolver(active_sim_info)))
            notification.show_dialog()

    def _process_trend_shift_schedule_gen(self, fashion_trend=None):

        def _process_specific_trend_schedule_gen(timeline):
            try:
                try:
                    teardown = False
                    self._shift_fashion_trend(fashion_trend)
                    yield from self._schedule_trend_shift_gen(timeline)
                except GeneratorExit:
                    teardown = True
                    raise
                except Exception as exception:
                    try:
                        logger.exception('Exception while scheduling trend shifts: ', exc=exception,
                          level=(sims4.log.LEVEL_ERROR))
                    finally:
                        exception = None
                        del exception

            finally:
                if not teardown:
                    self._setup_trend_shift_alarms(process_fashion_trend=fashion_trend)

            if False:
                yield None

        return _process_specific_trend_schedule_gen

    def _process_daily_schedule_gen(self, timeline):
        try:
            try:
                teardown = False
                self._randomize_thrift_store_inventory()
                yield from self._schedule_daily_shuffle_gen(timeline)
            except GeneratorExit:
                teardown = True
                raise
            except Exception as exception:
                try:
                    logger.exception('Exception while scheduling daily thrift store refresh: ', exc=exception,
                      level=(sims4.log.LEVEL_ERROR))
                finally:
                    exception = None
                    del exception

        finally:
            if not teardown:
                self._setup_daily_thrift_store_refresh_alarm()

        if False:
            yield None

    def _process_daily_unlock_schedule_gen(self, timeline):
        try:
            try:
                teardown = False
                if FashionThriftStoreTuning.EXCLUSIVE_ITEM_NOTIFICATION:
                    if self._exclusive_item_unlocked:
                        active_sim_info = services.active_sim_info()
                        notification = FashionThriftStoreTuning.EXCLUSIVE_ITEM_NOTIFICATION(active_sim_info, resolver=(SingleSimResolver(active_sim_info)))
                        notification.show_dialog()
                yield from self._schedule_daily_unlock_gen(timeline)
            except GeneratorExit:
                teardown = True
                raise
            except Exception as exception:
                try:
                    logger.exception('Exception while scheduling daily exclusive unlock notification: ', exc=exception,
                      level=(sims4.log.LEVEL_ERROR))
                finally:
                    exception = None
                    del exception

        finally:
            if not teardown:
                self._setup_exclusive_item_unlock_alarm()

        if False:
            yield None

    def _schedule_trend_shift_gen(self, timeline=None):
        active_household = services.active_household()
        if active_household is None:
            return
        if timeline is not None:
            yield timeline.run_child(elements.SleepElement(date_and_time.TimeSpan(0)))

    def _schedule_daily_shuffle_gen(self, timeline=None):
        active_household = services.active_household()
        if active_household is None:
            return
        if timeline is not None:
            yield timeline.run_child(elements.SleepElement(date_and_time.TimeSpan(0)))

    def _schedule_daily_unlock_gen(self, timeline=None):
        active_household = services.active_household()
        if active_household is None:
            return
        if timeline is not None:
            yield timeline.run_child(elements.SleepElement(date_and_time.TimeSpan(0)))

    def on_loading_screen_animation_finished(self):
        self._apply_vfx_updates()