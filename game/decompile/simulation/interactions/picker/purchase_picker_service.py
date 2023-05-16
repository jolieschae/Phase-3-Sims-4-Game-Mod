# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\purchase_picker_service.py
# Compiled at: 2021-05-21 16:19:01
# Size of source mod 2**32: 10069 bytes
import persistence_error_types
from collections import defaultdict
import services
from date_and_time import create_time_span, DateAndTime
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import GlobalResolver
from event_testing.tests import TunableTestSet
from sims4.service_manager import Service
from sims4.tuning.dynamic_enum import DynamicEnum
from protocolbuffers import GameplaySaveData_pb2
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableList, TunableTuple, TunableReference, TunableRange
import sims4.random
from sims4.utils import classproperty
from tunable_time import TunableTimeOfDay

class PurchasePickerGroup(DynamicEnum):
    INVALID = 0


class PurchasePickerGroupData:

    def __init__(self):
        self.item_count_pairs = defaultdict(int)
        self.timestamp = None


class PurchasePickerService(Service):
    PICKER_DATA_GROUPS = TunableMapping(description='\n        A mapping between purchase picker groups and tuning relating\n        to the various limited data that can be provided from the\n        picker.\n        ',
      key_type=TunableEnumEntry(description='\n            The purchase picker group type that this\n            set of purchase picker limited items is linked to.\n            ',
      tunable_type=PurchasePickerGroup,
      default=(PurchasePickerGroup.INVALID),
      invalid_enums=(
     PurchasePickerGroup.INVALID,)),
      value_type=TunableList(description='\n            List of categories of items we will pick from to fulfill the items provider. Number of those items are limited.\n            ',
      tunable=TunableTuple(items_list=TunableMapping(description='\n                    These are items within this category we will pick randomly to fulfill the items provider.\n                    Key is the object definition, weight is the relative chance they will be picked.\n                    ',
      key_type=TunableReference(description='\n                            The object definition we are creating from.\n                            ',
      manager=(services.definition_manager()),
      pack_safe=True),
      value_type=TunableRange(description='\n                            The relative weight of this object. Higher weight has higher chance to be picked.\n                            ',
      tunable_type=float,
      default=1.0,
      minimum=0.0)),
      tests=TunableTestSet(description='\n                    A series of tests that must pass in order for this entire category to be picked by the provider.\n                    '),
      number_of_types_of_items=TunableRange(description='\n                    This will be used to limit the number of types of items in this category.\n                    Say we have 6 kinds of items in the category. If this value is set to 2 we will \n                    randomly select 2 kinds from the 6.\n                    ',
      tunable_type=int,
      default=1,
      minimum=1),
      quantity_for_each_item=TunableRange(description="\n                    Available number of items in each picked kind of item.\n                    For example if we have apple and pear picked, and this number is 3,\n                    then eventually we will have 3 apples and 3 pears in the vendor's sell picker.\n                    ",
      tunable_type=int,
      default=1,
      minimum=1))))
    REFRESH_TIME = TunableTimeOfDay(description='\n        The time of day that the items will refresh in the picker.\n        ')

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_PURCHASE_PICKER_SERVICE

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._purchase_picker_data = {}
        self._refresh_time_always_refresh = False

    def refresh_time_always_refresh(self, always_refresh=False):
        self._refresh_time_always_refresh = always_refresh

    def get_items_for_group(self, purchase_picker_group):
        now = services.time_service().sim_now
        if purchase_picker_group in self._purchase_picker_data:
            time_difference = now - self._purchase_picker_data[purchase_picker_group].timestamp
            if not self._refresh_time_always_refresh:
                if time_difference < create_time_span(days=1):
                    if self._purchase_picker_data[purchase_picker_group].timestamp.time_till_next_day_time(self.REFRESH_TIME) > time_difference:
                        return self._purchase_picker_data[purchase_picker_group].item_count_pairs
            self._purchase_picker_data[purchase_picker_group].item_count_pairs.clear()
        else:
            self._purchase_picker_data[purchase_picker_group] = PurchasePickerGroupData()
        self._purchase_picker_data[purchase_picker_group].timestamp = now
        resolver = GlobalResolver()
        for category in self.PICKER_DATA_GROUPS[purchase_picker_group]:
            if not category.tests.run_tests(resolver):
                continue
            possible_object_def_ids = [(weight, object_def.id) for object_def, weight in category.items_list.items()]
            number_of_types_of_items = min(category.number_of_types_of_items, len(possible_object_def_ids))
            for _ in range(number_of_types_of_items):
                chosen_object_def_id = sims4.random.pop_weighted(possible_object_def_ids)
                self._purchase_picker_data[purchase_picker_group].item_count_pairs[chosen_object_def_id] += category.quantity_for_each_item

        return self._purchase_picker_data[purchase_picker_group].item_count_pairs

    def update_item_count_pairs(self, purchase_picker_group, purchased_item_count_pairs):
        purchase_picker_data = self._purchase_picker_data[purchase_picker_group]
        for def_id in list(purchased_item_count_pairs):
            count = purchased_item_count_pairs[def_id]
            if def_id in purchase_picker_data.item_count_pairs:
                count_to_be_deducted = min(purchase_picker_data.item_count_pairs[def_id], count)
                purchase_picker_data.item_count_pairs[def_id] -= count_to_be_deducted
                purchased_item_count_pairs[def_id] -= count_to_be_deducted
                if purchase_picker_data.item_count_pairs[def_id] == 0:
                    del purchase_picker_data.item_count_pairs[def_id]
                if purchased_item_count_pairs[def_id] == 0:
                    del purchased_item_count_pairs[def_id]

    def has_available_items_for_group(self, purchase_picker_group):
        item_count_pairs = self._purchase_picker_data[purchase_picker_group].item_count_pairs
        if item_count_pairs:
            return True
        return False

    def save(self, object_list=None, zone_data=None, open_street_data=None, save_slot_data=None):
        service_data = GameplaySaveData_pb2.PersistablePurchasePickerService()
        for picker_group, group_data in self._purchase_picker_data.items():
            with ProtocolBufferRollback(service_data.picker_group_data) as (purchase_group_msg):
                purchase_group_msg.picker_group = int(picker_group)
                purchase_group_msg.timestamp = group_data.timestamp.absolute_ticks()
                for item_def_id, quantity in group_data.item_count_pairs.items():
                    with ProtocolBufferRollback(purchase_group_msg.items) as (items_msg):
                        items_msg.object_definition = item_def_id
                        items_msg.quantity = quantity

        save_slot_data.gameplay_data.purchase_picker_service = service_data

    def load(self, zone_data=None):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        service_data = save_slot_data_msg.gameplay_data.purchase_picker_service
        for purchase_group_msg in service_data.picker_group_data:
            group_data = PurchasePickerGroupData()
            group_data.timestamp = DateAndTime(purchase_group_msg.timestamp)
            for items_msg in purchase_group_msg.items:
                group_data.item_count_pairs[items_msg.object_definition] = items_msg.quantity

            self._purchase_picker_data[PurchasePickerGroup(purchase_group_msg.picker_group)] = group_data