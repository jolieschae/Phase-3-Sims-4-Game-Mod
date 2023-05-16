# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\delivery\delivery_tracker.py
# Compiled at: 2021-04-15 16:45:16
# Size of source mod 2**32: 13084 bytes
from collections import namedtuple
from crafting.crafting_interactions import create_craftable
from date_and_time import DateAndTime, TimeSpan
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import SingleSimResolver
from households.household_tracker import HouseholdTracker
from interactions.utils import LootType
from sims4.resources import Types
import alarms, services, sims4.log
from sims4.tuning.tunable import OptionalTunable
from tunable_time import TunableTimeSpan
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
_Delivery = namedtuple('_Delivery', ('sim_id', 'tuning_guid', 'expected_arrival_time'))
logger = sims4.log.Logger('DeliveryTracker', default_owner='jdimailig')

class _DeliveryAlarmHandler:

    def __init__(self, tracker, delivery):
        self._tracker = tracker
        self._delivery = delivery

    def __call__(self, timeline):
        self._tracker.try_do_delivery(self._delivery)


class DeliveryTracker(HouseholdTracker):
    RECIPE_AT_HOME_DELIVERY_NOTIFICATION = OptionalTunable(description='\n            The notification that will be displayed when the Sim is at\n            home when the object(s) would be delivered. The object(s)\n            will end up in hidden inventory waiting to be delivered by\n            the mailman.\n            ',
      tunable=(TunableUiDialogNotificationSnippet()))
    RECIPE_AWAY_DELIVERY_NOTIFICATION = OptionalTunable(description='\n            If enabled, a notification will be displayed when the Sim is not\n            currently home when the object(s) would be delivered.\n            The object will be in the mailbox when they arrive back at their\n            home lot.\n            ',
      tunable=(TunableUiDialogNotificationSnippet()))
    RECIPE_DELIVERY_TIME_SPAN = TunableTimeSpan(description='\n        The amount of time it takes to deliver a craftable when ordered from a Recipe.\n        ',
      default_days=1)

    def __init__(self, household):
        self._household = household
        self._expected_deliveries = {}

    def request_delivery(self, sim_id, delivery_tuning_guid, time_span_from_now=None):
        if not self._household.sim_in_household(sim_id):
            logger.warn('Sim {} not in household {}, {} will not be delivered', sim_id, self._household, delivery_tuning_guid)
            return
        if time_span_from_now is None:
            recipe_manager = services.get_instance_manager(Types.RECIPE)
            delivery_recipe = recipe_manager.get(delivery_tuning_guid, None)
            if delivery_recipe is not None:
                time_span_from_now = DeliveryTracker.RECIPE_DELIVERY_TIME_SPAN()
        expected_arrival_time = services.time_service().sim_now + time_span_from_now
        delivery = _Delivery(sim_id, delivery_tuning_guid, expected_arrival_time)
        self._expected_deliveries[delivery] = alarms.add_alarm(self, time_span_from_now, (_DeliveryAlarmHandler(self, delivery)), cross_zone=True)

    def try_do_delivery(self, delivery):
        sim_info = services.sim_info_manager().get(delivery.sim_id)
        if sim_info is None:
            logger.error(f"Could not perform delivery, Sim {delivery.sim_id} not found.")
            del self._expected_deliveries[delivery]
            return
        loot_tuning_manager = services.get_instance_manager(Types.ACTION)
        delivery_tuning = loot_tuning_manager.get(delivery.tuning_guid)
        if delivery_tuning is not None:
            if delivery_tuning.loot_type == LootType.SCHEDULED_DELIVERY:
                self._try_do_delivery_loot(delivery, delivery_tuning, sim_info)
                return
        recipe_manager = services.get_instance_manager(Types.RECIPE)
        delivery_recipe = recipe_manager.get(delivery.tuning_guid, None)
        if delivery_recipe is not None:
            self._try_do_delivery_recipe(delivery, delivery_recipe, sim_info)
            return
        logger.error(f"Could not perform delivery, the tuning_guid {delivery.tuning_guid} is not a delivery loot or recipe.")
        del self._expected_deliveries[delivery]

    def _try_do_delivery_loot(self, delivery, delivery_tuning, sim_info):
        resolver = SingleSimResolver(sim_info)
        if self._household.home_zone_id == services.current_zone_id():
            delivery_tuning.objects_to_deliver.apply_to_resolver(resolver)
            del self._expected_deliveries[delivery]
            at_home_notification_tuning = delivery_tuning.at_home_notification
            if at_home_notification_tuning is not None:
                at_home_notification = at_home_notification_tuning(sim_info, resolver=resolver)
                at_home_notification.show_dialog()
        else:
            not_home_notification_tuning = delivery_tuning.not_home_notification
            if not_home_notification_tuning is not None:
                not_home_notification = not_home_notification_tuning(sim_info, resolver=resolver)
                not_home_notification.show_dialog()

    def _try_do_delivery_recipe(self, delivery, delivery_recipe, sim_info):
        resolver = SingleSimResolver(sim_info)
        if self._household.home_zone_id == services.current_zone_id():
            craftable = create_craftable(delivery_recipe, None)
            current_zone = services.current_zone()
            if current_zone is not None:
                lot_hidden_inventory = current_zone.lot.get_hidden_inventory()
                if lot_hidden_inventory is not None:
                    if not lot_hidden_inventory.player_try_add_object(craftable):
                        return
            if DeliveryTracker.RECIPE_AT_HOME_DELIVERY_NOTIFICATION is not None:
                notification = DeliveryTracker.RECIPE_AT_HOME_DELIVERY_NOTIFICATION(sim_info, resolver)
                notification.show_dialog()
            del self._expected_deliveries[delivery]
        else:
            if DeliveryTracker.RECIPE_AWAY_DELIVERY_NOTIFICATION is not None:
                notification = DeliveryTracker.RECIPE_AWAY_DELIVERY_NOTIFICATION(sim_info, resolver)
                notification.show_dialog()

    def on_zone_load(self):
        if self._household.home_zone_id != services.current_zone_id():
            return
        sim_now = services.time_service().sim_now
        loot_tuning_manager = services.get_instance_manager(Types.ACTION)
        recipe_manager = services.get_instance_manager(Types.RECIPE)
        for delivery in tuple(self._expected_deliveries):
            if sim_now < delivery.expected_arrival_time:
                continue
            else:
                delivery_tuning = loot_tuning_manager.get(delivery.tuning_guid)
                if delivery_tuning is not None:
                    self._deliver_loot_to_mailbox(delivery, delivery_tuning)
                else:
                    delivery_recipe = recipe_manager.get(delivery.tuning_guid, None)
                    if delivery_recipe is not None:
                        self._deliver_recipe_to_mailbox(delivery, delivery_recipe)
            del self._expected_deliveries[delivery]

    def _deliver_loot_to_mailbox(self, delivery, delivery_tuning):
        if delivery_tuning is None:
            return
        if delivery_tuning.loot_type != LootType.SCHEDULED_DELIVERY:
            logger.error(f"Could not perform delivery for {delivery_tuning}, not a delivery loot.")
            return
        sim_info = services.sim_info_manager().get(delivery.sim_id)
        if sim_info is None:
            logger.error(f"Could not perform delivery for {delivery_tuning}, Sim {delivery.sim_id} not found.")
            return
        resolver = SingleSimResolver(sim_info)
        delivery_tuning.objects_to_deliver.apply_with_placement_override(sim_info, resolver, self._place_object_in_mailbox)

    def _deliver_recipe_to_mailbox(self, delivery, delivery_recipe):
        sim_info = services.sim_info_manager().get(delivery.sim_id)
        if sim_info is None:
            logger.error(f"Could not perform delivery for {delivery_recipe}, Sim {delivery.sim_id} not found.")
            return
        craftable = create_craftable(delivery_recipe, None)
        self._place_object_in_mailbox(sim_info, craftable)

    def _place_object_in_mailbox(self, subject_to_apply, created_object):
        sim_household = subject_to_apply.household
        if sim_household is not None:
            zone = services.get_zone(sim_household.home_zone_id)
            if zone is not None:
                mailbox_inventory = zone.lot.get_mailbox_inventory(sim_household.id)
                if mailbox_inventory is not None:
                    mailbox_inventory.player_try_add_object(created_object)

    def household_lod_cleanup(self):
        self._expected_deliveries = {}

    def load_data(self, household_proto):
        sim_now = services.time_service().sim_now
        for delivery_data in household_proto.deliveries:
            from_now = DateAndTime(delivery_data.expected_arrival_time) - sim_now
            if from_now <= TimeSpan.ZERO:
                delivery = _Delivery(delivery_data.sim_id, delivery_data.delivery_tuning_guid, delivery_data.expected_arrival_time)
                self._expected_deliveries[delivery] = None
            else:
                self.request_delivery(delivery_data.sim_id, delivery_data.delivery_tuning_guid, from_now)

    def save_data(self, household_proto):
        for delivery in self._expected_deliveries:
            with ProtocolBufferRollback(household_proto.deliveries) as (delivery_data):
                delivery_data.sim_id = delivery.sim_id
                delivery_data.delivery_tuning_guid = delivery.tuning_guid
                delivery_data.expected_arrival_time = delivery.expected_arrival_time