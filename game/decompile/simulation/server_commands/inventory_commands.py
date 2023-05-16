# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server_commands\inventory_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 38406 bytes
from bucks.bucks_utils import BucksUtils
from cas.cas import get_tags_from_outfit
from collections import Counter
from distributor.ops import SendUIMessage
from distributor.system import Distributor
from fashion_trends.fashion_trend_tuning import FashionThriftStoreTuning, FashionTrendTuning
from google.protobuf import text_format
from interactions.base.picker_interaction import PickerInteractionDeliveryMethod
from objects.components.inventory_storage import InventoryStorage
from protocolbuffers import Consts_pb2
from protocolbuffers import SimObjectAttributes_pb2
from protocolbuffers import UI_pb2
from objects.components.inventory_enums import StackScheme
from objects.system import create_object
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, RequiredTargetParam, TunableInstanceParam, OptionalSimInfoParam
from server_commands.ui_commands import ui_dialog_respond
from sims.outfits.outfit_enums import OutfitCategory
from sims4.commands import CommandType
import services, sims4.commands
from sims4.localization import LocalizationHelperTuning

@sims4.commands.Command('inventory.create_in_hidden')
def create_object_in_hidden_inventory(definition_id: int, _connection=None):
    lot = services.active_lot()
    if lot is not None:
        return lot.create_object_in_hidden_inventory(definition_id) is not None
    return False


@sims4.commands.Command('inventory.list_hidden')
def list_objects_in_hidden_inventory(_connection=None):
    lot = services.active_lot()
    if lot is not None:
        hidden_inventory = lot.get_hidden_inventory()
        if hidden_inventory is not None:
            for obj in hidden_inventory:
                sims4.commands.output(str(obj), _connection)

            return True
    return False


@sims4.commands.Command('qa.objects.inventory.list', command_type=(sims4.commands.CommandType.Automation))
def automation_list_active_situations(inventory_obj_id: int=None, _connection=None):
    manager = services.object_manager()
    if inventory_obj_id not in manager:
        sims4.commands.automation_output('ObjectInventory; Status:NoObject, ObjectId:{}'.format(inventory_obj_id), _connection)
        return
    else:
        inventory_obj = manager.get(inventory_obj_id)
        if inventory_obj.inventory_component != None:
            sims4.commands.automation_output('ObjectInventory; Status:Begin, ObjectId:{}'.format(inventory_obj_id), _connection)
            for obj in inventory_obj.inventory_component:
                sims4.commands.automation_output('ObjectInventory; Status:Data, Id:{}, DefId:{}'.format(obj.id, obj.definition.id), _connection)

            sims4.commands.automation_output('ObjectInventory; Status:End', _connection)
        else:
            sims4.commands.automation_output('ObjectInventory; Status:NoInventory, ObjectId:{}'.format(inventory_obj_id), _connection)


@sims4.commands.Command('inventory.purge', command_type=(sims4.commands.CommandType.Cheat))
def purge_sim_inventory(opt_target: OptionalTargetParam=None, _connection=None):
    target = get_optional_target(opt_target, _connection)
    if target is not None:
        target.inventory_component.purge_inventory()
    return False


@sims4.commands.Command('inventory.purchase_picker_response', command_type=(sims4.commands.CommandType.Live))
def purchase_picker_response(inventory_target: RequiredTargetParam, mailman_purchase: bool=False, *def_ids_and_amounts: int, _connection=None):
    total_price = 0
    current_purchased = 0
    objects_to_buy = []
    definition_manager = services.definition_manager()
    for def_id, amount in zip(def_ids_and_amounts[::2], def_ids_and_amounts[1::2]):
        definition = definition_manager.get(def_id)
        if definition is None:
            sims4.commands.output('inventory.purchase_picker_response: Definition not found with id {}'.format(def_id), _connection)
            return False
        purchase_price = definition.price * amount
        total_price += purchase_price
        objects_to_buy.append((definition, amount))

    client = services.client_manager().get(_connection)
    if client is None:
        sims4.commands.output('inventory.purchase_picker_response: No client found to make purchase.', _connection)
        return False
    household = client.household
    if household.funds.money < total_price:
        sims4.commands.output('inventory.purchase_picker_response: Insufficient funds for household to purchase items.', _connection)
        return False
    if mailman_purchase:
        inventory = services.active_lot().get_hidden_inventory()
    else:
        inventory_owner = inventory_target.get_target()
        inventory = inventory_owner.inventory_component
    if inventory is None:
        sims4.commands.output('inventory.purchase_picker_response: Inventory not found for items to be purchased into.', _connection)
        return False
    for definition, amount in objects_to_buy:
        obj = create_object(definition)
        if obj is None:
            sims4.commands.output('inventory.purchase_picker_response: Failed to create object with definition {}.'.format(definition), _connection)
            continue
        obj.set_stack_count(amount)
        if not inventory.player_try_add_object(obj):
            sims4.commands.output('inventory.purchase_picker_response: Failed to add object into inventory: {}'.format(obj), _connection)
            obj.destroy(source=inventory, cause='inventory.purchase_picker_response: Failed to add object into inventory.')
            continue
        obj.set_household_owner_id(household.id)
        obj.try_post_bb_fixup(force_fixup=True, active_household_id=(services.active_household_id()))
        purchase_price = definition.price * amount
        current_purchased += purchase_price

    return household.funds.try_remove(current_purchased, Consts_pb2.TELEMETRY_OBJECT_BUY)


USE_DEFINITION_PRICE = -1

@sims4.commands.Command('inventory.purchase_picker_response_by_ids', command_type=(sims4.commands.CommandType.Live))
def purchase_picker_response_by_ids(inventory_target, inventory_source, currency_type, dialog_id, delivery_method=PickerInteractionDeliveryMethod.INVENTORY, object_ids_or_definition_ids=False, *ids_and_amounts_and_price, _connection=None):
    total_price = 0
    current_purchased = 0
    objects_to_buy = []
    definition_manager = services.definition_manager()
    inventory_manager = services.inventory_manager()
    for def_or_obj_id, amount, price in zip(ids_and_amounts_and_price[::3], ids_and_amounts_and_price[1::3], ids_and_amounts_and_price[2::3]):
        if object_ids_or_definition_ids:
            obj_or_definition = inventory_manager.get(def_or_obj_id)
        else:
            obj_or_definition = definition_manager.get(def_or_obj_id)
        if obj_or_definition is None:
            sims4.commands.output('inventory.purchase_picker_response: Object or Definition not found with id {}'.format(def_or_obj_id), _connection)
            sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Object or Definition not found with id {}'.format(def_or_obj_id), _connection)
            return False
        if price == USE_DEFINITION_PRICE:
            price = obj_or_definition.definition.price
        purchase_price = price * amount
        total_price += purchase_price
        objects_to_buy.append((obj_or_definition, price, amount))

    client = services.client_manager().get(_connection)
    if client is None:
        sims4.commands.output('inventory.purchase_picker_response: No client found to make purchase.', _connection)
        sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:No client found to make purchase.', _connection)
        return False
    household = client.household
    if household.get_currency_amount(currency_type) < total_price:
        sims4.commands.output('inventory.purchase_picker_response: Insufficient funds for household to purchase items.', _connection)
        sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Insufficient funds for household to purchase items.', _connection)
        return False
    if delivery_method == PickerInteractionDeliveryMethod.MAILMAN:
        to_inventory = services.active_lot().get_hidden_inventory()
    else:
        if delivery_method == PickerInteractionDeliveryMethod.INVENTORY:
            to_inventory_owner = inventory_target.get_target()
            to_inventory = to_inventory_owner.inventory_component
        if delivery_method == PickerInteractionDeliveryMethod.INVENTORY or delivery_method == PickerInteractionDeliveryMethod.MAILMAN:
            if to_inventory is None:
                sims4.commands.output('inventory.purchase_picker_response: Inventory not found for items to be purchased into.', _connection)
                sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Inventory not found for items to be purchased into.', _connection)
                return False
            elif inventory_source.target_id != 0:
                from_inventory_owner = inventory_source.get_target()
                from_inventory = from_inventory_owner.inventory_component
            else:
                from_inventory = None
            if object_ids_or_definition_ids:
                if from_inventory is None:
                    sims4.commands.output('inventory.purchase_picker_response: Source Inventory not found for items to be cloned from.', _connection)
                    sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Source Inventory not found for items to be cloned from.', _connection)
                    return False
        obj_purchased = dict()
        for obj_or_def, price, amount in objects_to_buy:
            amount_left = amount
            while not amount_left > 0 or delivery_method == PickerInteractionDeliveryMethod.INVENTORY or delivery_method == PickerInteractionDeliveryMethod.MAILMAN:
                if object_ids_or_definition_ids:
                    from_inventory.try_remove_object_by_id(obj_or_def.id, obj_or_def.stack_count())
                    obj = obj_or_def.clone()
                    from_inventory.system_add_object(obj_or_def)
                else:
                    obj = create_object(obj_or_def)
                    if obj is None:
                        sims4.commands.output('inventory.purchase_picker_response: Failed to create object with definition {}.'.format(obj_or_def), _connection)
                        sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Failed to create object with definition {}.'.format(obj_or_def), _connection)
                        amount_left = 0
                        continue
                    else:
                        if obj.inventoryitem_component is None or obj.inventoryitem_component.get_stack_scheme() == StackScheme.NONE:
                            amount_left = amount_left - 1
                        else:
                            obj.set_stack_count(amount)
                            amount_left = 0
                        obj.set_household_owner_id(household.id)
                        obj.try_post_bb_fixup(force_fixup=True, active_household_id=(services.active_household_id()))
                        if delivery_method == PickerInteractionDeliveryMethod.INVENTORY or delivery_method == PickerInteractionDeliveryMethod.MAILMAN:
                            if not to_inventory.player_try_add_object(obj):
                                sims4.commands.output('inventory.purchase_picker_response: Failed to add object into inventory: {}'.format(obj), _connection)
                                sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Failed, Message:Failed to add object into inventory: {}'.format(obj), _connection)
                                obj.destroy(source=to_inventory, cause='inventory.purchase_picker_response: Failed to add object into inventory.')
                                continue
                    if obj.definition.id not in obj_purchased:
                        obj_purchased[obj.definition.id] = {'price':0, 
                         'amount':0,  'obj_ids':[]}
                    if obj.inventoryitem_component.get_stack_scheme() == StackScheme.NONE:
                        purchase_price = price
                        obj_purchased[obj.definition.id]['amount'] += 1
                    else:
                        purchase_price = price * amount
                        obj_purchased[obj.definition.id]['amount'] += amount
                    obj_purchased[obj.definition.id]['price'] += purchase_price
                    obj_purchased[obj.definition.id]['obj_ids'].append(obj.id)
                    current_purchased += purchase_price

        choice_list = []
        choice_counts = []
        object_ids = []
        for obj_def_id, data in obj_purchased.items():
            choice_list.append(obj_def_id)
            choice_counts.append(data['amount'])
            object_ids.append(data['obj_ids'])

        zone = services.current_zone()
        zone.ui_dialog_service.dialog_pick_result_def_ids_and_counts(dialog_id, choice_list, object_ids, choice_counts)
        sims4.commands.automation_output('PurchasePickerResponseInfo; Status:Success', _connection)
        return household.try_remove_currency_amount(currency_type, current_purchased, reason=(Consts_pb2.TELEMETRY_OBJECT_BUY), obj_purchased=obj_purchased)


@sims4.commands.Command('inventory.sell_picker_response_by_ids', command_type=(sims4.commands.CommandType.Live))
def sell_picker_response_by_ids(inventory_source, currency_type, dialog_id, *ids_and_amounts_and_price, _connection=None):
    total_price = 0
    inventory_manager = services.inventory_manager()
    client = services.client_manager().get(_connection)
    if client is None:
        sims4.commands.output('inventory.sell_picker_response: No client found to make selling.', _connection)
        return False
    elif inventory_source.target_id != 0:
        source_inventory_owner = inventory_source.get_target()
        source_inventory = source_inventory_owner.inventory_component
    else:
        source_inventory = None
    if source_inventory is None:
        sims4.commands.output('inventory.sell_picker_response: Source Inventory not found for items to be sold from.', _connection)
        return False
    for obj_id, amount, price in zip(ids_and_amounts_and_price[::3], ids_and_amounts_and_price[1::3], ids_and_amounts_and_price[2::3]):
        obj = inventory_manager.get(obj_id)
        if obj is None:
            sims4.commands.output('inventory.purchase_picker_response: Object or Definition not found with id {}'.format(obj_id), _connection)
            return False
        if price == USE_DEFINITION_PRICE:
            price = obj.definition.price
        total_price += price * amount

    client.household.add_currency_amount(currency_type, total_price, Consts_pb2.TELEMETRY_OBJECT_SELL)
    zone = services.current_zone()
    sell_dialog = zone.ui_dialog_service.get_dialog(dialog_id)
    if sell_dialog is not None:
        sell_dialog.ids_and_amounts_and_price = ids_and_amounts_and_price
        sell_dialog.source_inventory = source_inventory
    return total_price


@sims4.commands.Command('inventory.open_ui', command_type=(sims4.commands.CommandType.Live))
def open_inventory_ui(inventory_obj: RequiredTargetParam, _connection=None):
    obj = inventory_obj.get_target()
    if obj is None:
        sims4.commands.output('Failed to get inventory_obj: {}.'.format(inventory_obj), _connection)
        return False
    comp = obj.inventory_component
    if comp is None:
        sims4.commands.output('inventory_obj does not have an inventory component: {}.'.format(inventory_obj), _connection)
        return False
    comp.open_ui_panel()
    return True


@sims4.commands.Command('inventory.view_update', command_type=(sims4.commands.CommandType.Live))
def inventory_view_update(obj_id: int=0, _connection=None):
    obj = services.current_zone().find_object(obj_id)
    if obj is not None:
        obj.inventory_view_update()
        return True
    return False


@sims4.commands.Command('inventory.sim_inventory_sell_multiple', command_type=(sims4.commands.CommandType.Live))
def sim_inventory_sell_multiple(msg: str, _connection=None):
    proto = UI_pb2.InventorySellRequest()
    text_format.Merge(msg, proto)
    if proto is None:
        return
    sim_info = services.sim_info_manager().get(proto.sim_id)
    if sim_info is None:
        return
    inventory_component = sim_info.get_sim_instance().inventory_component
    if inventory_component is None:
        return
    sell_value = 0
    objs = []
    inventory_stack_items = inventory_component.get_stack_items_map(proto.stacks)
    if proto.stacks is not None:
        for stack_id in proto.stacks:
            stack_items = inventory_stack_items.get(stack_id, None)
            if stack_items is None:
                continue
            for item in stack_items:
                if item.non_deletable_by_user:
                    break
                sell_value += item.current_value * item.stack_count()
                objs.append(item)

    if proto.items is not None:
        inventory_manager = services.inventory_manager()
        for item_data in proto.items:
            if item_data not in inventory_component:
                continue
            item = inventory_manager.get(item_data.id)
            if item is None:
                continue
            if item.non_deletable_by_user:
                continue
            sell_value += item.current_value * item_data.count
            item.update_stack_count(-item_data.count)
            if item.stack_count() < 1:
                objs.append(item)
            else:
                inventory_component.push_inventory_item_update_msg(item)

    if objs:
        services.active_household().add_currency_amount(proto.currency_type, sell_value, Consts_pb2.TELEMETRY_OBJECT_SELL, sim_info)
        services.get_reset_and_delete_service().trigger_batch_destroy(objs)
    op = SendUIMessage('InventorySellItemsComplete')
    Distributor.instance().add_op_with_no_owner(op)


@sims4.commands.Command('inventory.sim_inventory_favorite_multiple', command_type=(sims4.commands.CommandType.Live))
def sim_inventory_favorite_multiple(sim_id: int=0, is_add: bool=False, *items: int, _connection=None):
    sim_info = services.sim_info_manager().get(sim_id)
    if sim_info is None:
        return
    favorites_tracker = sim_info.favorites_tracker
    if favorites_tracker is None:
        return
    inventory_component = sim_info.get_sim_instance().inventory_component
    if inventory_component is None:
        return
    inventory_manager = services.inventory_manager()
    for item_id in items:
        item = inventory_manager.get(item_id)
        if is_add:
            favorites_tracker.set_favorite_stack(item)
        else:
            favorites_tracker.unset_favorite_stack(item)
        inventory_component.push_inventory_item_stack_update_msg(item)


@sims4.commands.Command('inventory.sim_inventory_census.instanced_sims', command_type=(CommandType.Automation))
def sim_inventory_census_instances_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    for sim in services.sim_info_manager().instanced_sims_gen():
        inv_comp = sim.inventory_component
        output('{:50} Inventory: {:4} Shelved: {:4}'.format(inv_comp, len(inv_comp), inv_comp.get_shelved_object_count()))


@sims4.commands.Command('inventory.sim_inventory_census.save_slot', command_type=(CommandType.Automation))
def sim_inventory_census_save_slot(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    definition_manager = services.definition_manager()
    active_household_id = services.active_household_id()
    total_objs = 0
    total_objs_active_house = 0
    total_objs_all_player_houses = 0
    counter = Counter()
    stack_counter = Counter()
    for sim_info in services.sim_info_manager().values():
        inventory_objs = len(sim_info.inventory_data.objects)
        for obj in sim_info.inventory_data.objects:
            obj_def = definition_manager.get(obj.guid)
            if obj_def is not None:
                counter[obj_def] += 1
            save_data = SimObjectAttributes_pb2.PersistenceMaster()
            save_data.ParseFromString(obj.attributes)
            for data in save_data.data:
                if data.type == SimObjectAttributes_pb2.PersistenceMaster.PersistableData.InventoryItemComponent:
                    comp_data = data.Extensions[SimObjectAttributes_pb2.PersistableInventoryItemComponent.persistable_data]
                    stack_counter[obj_def] += comp_data.stack_count

        total_objs += inventory_objs
        if sim_info.is_player_sim:
            total_objs_all_player_houses += inventory_objs
        if sim_info.household.id == active_household_id:
            total_objs_active_house += inventory_objs

    dump = []
    dump.append(('#inventory objs', total_objs))
    dump.append(('#inventory objs active house', total_objs_active_house))
    dump.append(('#inventory objs all player houses', total_objs_all_player_houses))
    for name, value in dump:
        output('{:50} : {}'.format(name, value))

    output('{}'.format('----------------------------------------------------------------------------------------------------'))
    output('{:75} : {} / {}'.format('Obj Definition', 'PlayerFacing', 'Stacks'))
    for obj_def, count in stack_counter.most_common():
        output('{:75} : {:4} / {:4}'.format(obj_def, count, counter.get(obj_def)))

    return dump


@sims4.commands.Command('inventory.create_and_add_object_to_inventory')
def create_and_add_object_to_inventory(to_inventory_object_id: RequiredTargetParam, definition_id: int, _connection=None):
    to_inventory_owner = to_inventory_object_id.get_target()
    to_inventory = to_inventory_owner.inventory_component
    if to_inventory is None:
        sims4.commands.output('to inventory object does not have an inventory component: {}'.format(to_inventory_owner), _connection)
        return False
    obj = create_object(definition_id)
    if not to_inventory.player_try_add_object(obj):
        sims4.commands.output('object failed to be placed into inventory: {}'.format(obj), _connection)
        obj.destroy(source=to_inventory, cause='object failed to be placed into inventory')
        return False
    sims4.commands.output('object {} placed into inventory'.format(obj), _connection)
    return True


@sims4.commands.Command('qa.object_def.valid_inventory_types', command_type=(sims4.commands.CommandType.Automation))
def qa_object_def_valid_inventory_types(object_definition: TunableInstanceParam(sims4.resources.Types.OBJECT), _connection=None):
    sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:Begin', _connection)
    if object_definition is None:
        sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:End')
        return False
    if object_definition.cls._components.inventory_item is not None:
        valid_inventory_types = object_definition.cls._components.inventory_item._tuned_values.valid_inventory_types
        if valid_inventory_types is not None:
            for inventory_type in valid_inventory_types:
                sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:Data, InventoryType:{}'.format(inventory_type), _connection)

    sims4.commands.automation_output('QaObjDefValidInventoryTypes; Status:End', _connection)


@sims4.commands.Command('inventory.check_fashion_outfits', command_type=(sims4.commands.CommandType.DebugOnly))
def check_fashion_outfits_inventory(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    sim_inventory.open_ui_panel()
    for inventory_item in sim_inventory:
        mannequin = inventory_item.mannequin_component
        sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
        if mannequin is not None:
            outfits = mannequin.get_outfits()
            if outfits is None:
                sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                return False
            output = sims4.commands.Output(_connection)
            output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
            for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

    return True


@sims4.commands.Command('inventory.get_inventory_outfit_tags', command_type=(sims4.commands.CommandType.DebugOnly))
def get_inventory_outfit_tags(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    dominant_trend_cost = {}
    for dominant_trend_tag, trend_cost in FashionThriftStoreTuning.DOMINANT_TREND_ITEM_COST.items():
        dominant_trend_cost[dominant_trend_tag] = trend_cost
        sims4.commands.output('{}:{} = {}'.format(dominant_trend_tag, dominant_trend_tag.value, trend_cost), _connection)

    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    fashion_trend_service = services.fashion_trend_service()
    if fashion_trend_service is None:
        sims4.commands.output('Could not access fashion trend service', _connection)
        return False
    sim_inventory.open_ui_panel()
    for inventory_item in sim_inventory:
        mannequin = inventory_item.mannequin_component
        sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
        if mannequin is not None:
            outfits = mannequin.get_outfits()
            if outfits is None:
                sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                return False
            output = sims4.commands.Output(_connection)
            output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
            for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

            tags = get_tags_from_outfit(outfits._base, OutfitCategory.EVERYDAY, 0)
            sims4.commands.output('Tags for outfit are: {}'.format(tags), _connection)
            inventory_outfit_data = outfits.get_outfit(OutfitCategory.EVERYDAY, 0)
            prevalent_trend_tag = fashion_trend_service.get_outfit_trend(inventory_outfit_data)
            sims4.commands.output('The dominant trend tag is: {}'.format(prevalent_trend_tag), _connection)
            all_trend_style_tags = fashion_trend_service.get_outfit_all_trend_styles(tags)
            sims4.commands.output('The trend style tags for this outfit are: {}'.format(all_trend_style_tags), _connection)
            if prevalent_trend_tag is not None:
                prevalent_trend_tag_hash = FashionTrendTuning.TRENDS[prevalent_trend_tag].trend_name
                prevalent_trend_tag_loc_object = LocalizationHelperTuning.get_raw_text(prevalent_trend_tag_hash)
                sims4.commands.output('The dominant trend hash is: {}'.format(prevalent_trend_tag_hash), _connection)
                sims4.commands.output('The dominant trend localized string object is: {}'.format(prevalent_trend_tag_loc_object), _connection)
                sims4.commands.output('Trend Icon: {}'.format(inventory_item.icon), _connection)
            sims4.commands.output('', _connection)

    return True


@sims4.commands.Command('inventory.check_hidden_inventory_outfits', command_type=(sims4.commands.CommandType.DebugOnly))
def check_hidden_inventory_outfits(_connection=None):
    sim = services.get_active_sim()
    if sim is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    for inventory_item in sim_inventory:
        inventory_item_hidden = inventory_item.inventoryitem_component.is_hidden
        if inventory_item_hidden:
            sims4.commands.output('Outfit {} is hidden'.format(inventory_item), _connection)
            mannequin = inventory_item.mannequin_component
            sims4.commands.output('inventory_item {} - {}'.format(inventory_item, mannequin), _connection)
            if mannequin is not None:
                outfits = mannequin.get_outfits()
                if outfits is None:
                    sims4.commands.output('there are no outfits on mannequin {}'.format(mannequin.id), _connection)
                    return False
                output = sims4.commands.Output(_connection)
                output('Outfits: {}'.format(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)))
                for outfit_index, outfit_data in enumerate(outfits.get_outfits_in_category(OutfitCategory.EVERYDAY)):
                    output('\t\t{}: {}'.format(outfit_index, ', '.join((str(part) for part in outfit_data.part_ids))))

                sims4.commands.output('', _connection)

    return True


@sims4.commands.Command('inventory.open_ui_with_preselection', command_type=(sims4.commands.CommandType.Live))
def open_ui_with_preselection(opt_sim: OptionalSimInfoParam=None, filter_tag: int=None, _connection=None):
    sim_info = get_optional_target(opt_target=opt_sim, _connection=_connection, target_type=OptionalSimInfoParam)
    if sim_info is None:
        sims4.commands.output('No valid target specified.', _connection)
        return False
    sim = sim_info.get_sim_instance()
    if sim is None:
        sims4.commands.output('No valid sim specified.', _connection)
        return False
    sim_inventory = sim.inventory_component
    if sim_inventory is None:
        sims4.commands.output('No valid inventory for sim.', _connection)
        return False
    if filter_tag is None:
        sims4.commands.output('No valid filter tag supplied.', _connection)
        return False
    sim_inventory.open_ui_panel_with_preselected_filters(filter_tag=filter_tag)
    return True