# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\server\client.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 49169 bytes
from _collections import defaultdict
from _weakrefset import WeakSet
import itertools, operator, weakref
from protocolbuffers import Sims_pb2, Consts_pb2
from protocolbuffers.DistributorOps_pb2 import Operation, SetWhimBucks
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import create_icon_info_msg
from distributor.system import Distributor
from objects import ALL_HIDDEN_REASONS, HiddenReasonFlag
from objects.object_enums import ResetReason
from server.live_drag_tuning import LiveDragLocation, LiveDragState, LiveDragTuning
from sims4.callback_utils import CallableList
from sims4.utils import constproperty
from vfx import vfx_mask
import distributor.fields, distributor.ops, gsi_handlers, interactions.context, omega, services, sims4.log, telemetry_helper
logger = sims4.log.Logger('Client')
logger_live_drag = sims4.log.Logger('LiveDrag', default_owner='rmccord')
TELEMETRY_GROUP_ACTIVE_SIM = 'ASIM'
TELEMETRY_HOOK_ACTIVE_SIM_CHANGED = 'ASCH'
writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_ACTIVE_SIM)
MSG_ID_NAMES = {}
for name, val in vars(Consts_pb2).items():
    if name.startswith('MSG_'):
        MSG_ID_NAMES[val] = name

class Client:
    _interaction_source = interactions.context.InteractionContext.SOURCE_PIE_MENU
    _interaction_priority = interactions.priority.Priority.High

    def __init__(self, session_id, account, household_id):
        self.id = session_id
        self.manager = None
        self._account = account
        self._household_id = household_id
        self._choice_menu = None
        self._interaction_parameters = {}
        self.active = True
        self.zone_id = services.current_zone_id()
        self._selectable_sims = SelectableSims(self)
        self._active_sim_info = None
        self._active_sim_changed = CallableList()
        self.ui_objects = weakref.WeakSet()
        self.primitives = ()
        self._live_drag_objects = []
        self._live_drag_start_system = LiveDragLocation.INVALID
        self._live_drag_is_stack = False
        self._live_drag_sell_dialog_active = False
        self.objects_moved_via_live_drag = WeakSet()

    def __repr__(self):
        return '<Client {0:#x}>'.format(self.id)

    @property
    def account(self):
        return self._account

    @distributor.fields.Field(op=(distributor.ops.UpdateClientActiveSim))
    def active_sim_info(self):
        return self._active_sim_info

    resend_active_sim_info = active_sim_info.get_resend()

    @active_sim_info.setter
    def active_sim_info(self, sim_info):
        self._set_active_sim_without_field_distribution(sim_info)

    @property
    def active_sim(self):
        if self.active_sim_info is not None:
            return self.active_sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)

    @active_sim.setter
    def active_sim(self, sim):
        self.active_sim_info = sim.sim_info

    def _set_active_sim_without_field_distribution(self, sim_info):
        if self._active_sim_info is not None:
            if self._active_sim_info is sim_info:
                return
        else:
            current_sim = self._active_sim_info.get_sim_instance() if self._active_sim_info is not None else None
            if sim_info is not None:
                self._active_sim_info = sim_info
                if sim_info.household is not None:
                    sim_info.household.on_active_sim_changed(sim_info)
            else:
                self._active_sim_info = None
        self.notify_active_sim_changed(current_sim, new_sim_info=sim_info)

    @property
    def choice_menu(self):
        return self._choice_menu

    @property
    def interaction_source(self):
        return self._interaction_source

    @interaction_source.setter
    def interaction_source(self, value):
        if value is None:
            if self._interaction_source is not Client._interaction_source:
                del self._interaction_source
        else:
            self._interaction_source = value

    @property
    def interaction_priority(self):
        return self._interaction_priority

    @interaction_priority.setter
    def interaction_priority(self, value):
        if value is None:
            if self._interaction_priority is not Client._interaction_priority:
                del self._interaction_priority
        else:
            self._interaction_priority = value

    @property
    def household_id(self):
        return self._household_id

    @property
    def household(self):
        household_manager = services.household_manager()
        if household_manager is not None:
            return household_manager.get(self._household_id)

    @property
    def selectable_sims(self):
        return self._selectable_sims

    def create_interaction_context(self, sim, **kwargs):
        context = (interactions.context.InteractionContext)(sim,
 self.interaction_source,
 self.interaction_priority, client=self, **kwargs)
        return context

    @property
    def live_drag_objects(self):
        return self._live_drag_objects

    def get_interaction_parameters(self):
        return self._interaction_parameters

    def set_interaction_parameters(self, **kwargs):
        self._interaction_parameters = kwargs

    def set_choices(self, new_choices):
        self._choice_menu = new_choices

    def select_interaction(self, choice_id, revision):
        if self.choice_menu is not None:
            if revision == self.choice_menu.revision:
                choice_menu = self.choice_menu
                self._choice_menu = None
                self.set_interaction_parameters()
                try:
                    return choice_menu.select(choice_id)
                except:
                    if choice_menu.simref is not None:
                        sim = choice_menu.simref()
                        if sim is not None:
                            sim.reset((ResetReason.RESET_ON_ERROR), cause='Exception while selecting interaction from the pie menu.')
                    raise

    def get_create_op(self, *args, **kwargs):
        return (distributor.ops.ClientCreate)(self, *args, is_active=True, **kwargs)

    def get_delete_op(self):
        return distributor.ops.ClientDelete()

    def get_create_after_objs(self):
        active = self.active_sim
        if active is not None:
            yield active
        household = self.household
        if household is not None:
            yield household

    @property
    def valid_for_distribution(self):
        return True

    def refresh_achievement_data(self):
        active_sim_info = None
        if self.active_sim is not None:
            active_sim_info = self.active_sim.sim_info
        self.account.achievement_tracker.refresh_progress(active_sim_info)

    def send_message(self, msg_id, msg):
        if self.active:
            omega.send(self.id, msg_id, msg.SerializeToString())
        else:
            logger.warn('Message sent to client {} after it has already disconnected.', self)

    def validate_selectable_sim(self):
        if not (self._active_sim_info is None or self._active_sim_info.get_is_enabled_in_skewer()):
            self.set_next_sim()

    def set_next_sim(self):
        sim_info = self._selectable_sims.get_next_selectable(self._active_sim_info)
        if sim_info is self.active_sim_info:
            self.resend_active_sim_info()
            return False
        return self.set_active_sim_info(sim_info)

    def set_next_sim_or_none(self, only_if_this_active_sim_info=None):
        if only_if_this_active_sim_info is not None:
            if self._active_sim_info is not only_if_this_active_sim_info:
                return
        sim_info = self._selectable_sims.get_next_selectable(self._active_sim_info)
        if sim_info is None:
            return self.set_active_sim_info(None)
        if sim_info is self._active_sim_info:
            return self.set_active_sim_info(None)
        return self.set_active_sim_info(sim_info)

    def set_active_sim_by_id(self, sim_id, consider_active_sim=True):
        if self.active_sim_info is not None:
            if self.active_sim_info.id == sim_id:
                return False
        for sim_info in self._selectable_sims:
            if sim_info.sim_id == sim_id and not sim_info.get_is_enabled_in_skewer(consider_active_sim=consider_active_sim):
                return False
                returnval = self.set_active_sim_info(sim_info)
                if returnval:
                    if not consider_active_sim:
                        self.send_selectable_sims_update()
                return returnval

        return False

    def set_active_sim(self, sim):
        return self.set_active_sim_info(sim.sim_info)

    def set_active_sim_info(self, sim_info):
        with telemetry_helper.begin_hook(writer, TELEMETRY_HOOK_ACTIVE_SIM_CHANGED, sim_info=sim_info):
            pass
        self.active_sim_info = sim_info
        return self._active_sim_info is not None

    def add_selectable_sim_info(self, sim_info, send_relationship_update=True):
        self._selectable_sims.add_selectable_sim_info(sim_info, send_relationship_update=send_relationship_update)
        if self.active_sim_info is None:
            self.set_next_sim()
        self.household.refresh_aging_updates(sim_info)

    def add_selectable_sim_by_id(self, sim_id):
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info is not None:
            self.add_selectable_sim_info(sim_info)

    def remove_selectable_sim_info(self, sim_info):
        self._selectable_sims.remove_selectable_sim_info(sim_info)
        if self.active_sim_info is None:
            self.set_next_sim()
        self.household.refresh_aging_updates(sim_info)

    def remove_selectable_sim_by_id(self, sim_id):
        if len(self._selectable_sims) <= 1:
            return False
        sim_info = services.sim_info_manager().get(sim_id)
        if sim_info is not None:
            self.remove_selectable_sim_info(sim_info)
        return True

    def make_all_sims_selectable(self):
        self.clear_selectable_sims()
        for sim_info in services.sim_info_manager().objects:
            self._selectable_sims.add_selectable_sim_info(sim_info)

        self.set_next_sim()

    def clear_selectable_sims(self):
        self.active_sim_info = None
        self._selectable_sims.clear_selectable_sims()

    def register_active_sim_changed(self, callback):
        if callback not in self._active_sim_changed:
            self._active_sim_changed.append(callback)

    def unregister_active_sim_changed(self, callback):
        if callback in self._active_sim_changed:
            self._active_sim_changed.remove(callback)

    def on_sim_added_to_skewer(self, sim_info, send_relationship_update=True):
        if send_relationship_update:
            sim_info.relationship_tracker.send_relationship_info()
        else:
            is_zone_running = services.current_zone().is_zone_running
            sim_info.on_sim_added_to_skewer()
            if not is_zone_running:
                sim_info.commodity_tracker.start_low_level_simulation()
            else:
                services.active_household().distribute_household_data()
            sim_info.commodity_tracker.send_commodity_progress_update(from_add=True)
            sim_info.career_tracker.on_sim_added_to_skewer()
            if sim_info.degree_tracker is not None:
                sim_info.degree_tracker.on_sim_added_to_skewer()
            sim_info.send_satisfaction_points_update(SetWhimBucks.LOAD)
            sim_info.resend_trait_ids()
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is not None:
                if is_zone_running:
                    sim.inventory_component.visible_storage.allow_ui = True
                    sim.inventory_component.publish_inventory_items()
                sim.ui_manager.refresh_ui_data()
                services.autonomy_service().logging_sims.add(sim)
                sim_info.start_aspiration_tracker_on_instantiation(force_ui_update=True)
                if sim_info.whim_tracker is not None:
                    sim_info.whim_tracker.start_whims_tracker()
        zone_director = services.venue_service().get_zone_director()
        if zone_director is not None:
            zone_director.on_sim_added_to_skewer(sim_info)
        sim_info.trait_tracker.sort_and_send_commodity_list()

    def on_sim_removed_from_skewer(self, sim_info):
        sim = sim_info.get_sim_instance()
        if sim is not None:
            autonomy_service = services.autonomy_service()
            if autonomy_service is not None:
                autonomy_service.logging_sims.discard(sim)

    def clean_and_send_remaining_relationship_info(self):
        relationship_service = services.relationship_service()
        for sim_info in self.selectable_sims:
            sim_info.relationship_tracker.clean_and_send_remaining_relationship_info()
            relationship_service.clean_and_send_remaining_object_relationships(sim_info.id)

    def cancel_live_drag_on_objects(self):
        for obj in self._live_drag_objects:
            obj.live_drag_component.cancel_live_dragging()

        self._live_drag_objects = []

    def _get_stack_items_from_drag_object--- This code section failed: ---

 L. 514         0  LOAD_FAST                'drag_object'
                2  LOAD_ATTR                inventoryitem_component
                4  LOAD_CONST               None
                6  COMPARE_OP               is
                8  POP_JUMP_IF_FALSE    14  'to 14'

 L. 515        10  LOAD_CONST               (False, None)
               12  RETURN_VALUE     
             14_0  COME_FROM             8  '8'

 L. 517        14  LOAD_FAST                'drag_object'
               16  LOAD_ATTR                inventoryitem_component
               18  LOAD_METHOD              get_inventory
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  STORE_FAST               'previous_inventory'

 L. 518        24  LOAD_FAST                'previous_inventory'
               26  LOAD_CONST               None
               28  COMPARE_OP               is
               30  POP_JUMP_IF_FALSE    36  'to 36'

 L. 519        32  LOAD_CONST               (False, None)
               34  RETURN_VALUE     
             36_0  COME_FROM            30  '30'

 L. 521        36  LOAD_FAST                'drag_object'
               38  LOAD_ATTR                inventoryitem_component
               40  LOAD_METHOD              get_stack_id
               42  CALL_METHOD_0         0  '0 positional arguments'
               44  STORE_FAST               'stack_id'

 L. 522        46  LOAD_FAST                'previous_inventory'
               48  LOAD_METHOD              get_stack_items
               50  LOAD_FAST                'stack_id'
               52  CALL_METHOD_1         1  '1 positional argument'
               54  STORE_FAST               'stack_items'

 L. 523        56  LOAD_FAST                'remove'
               58  POP_JUMP_IF_FALSE   128  'to 128'

 L. 524        60  LOAD_FAST                'is_stack'
               62  POP_JUMP_IF_FALSE   100  'to 100'

 L. 525        64  SETUP_LOOP          126  'to 126'
               66  LOAD_FAST                'stack_items'
               68  GET_ITER         
               70  FOR_ITER             96  'to 96'
               72  STORE_FAST               'item'

 L. 526        74  LOAD_FAST                'previous_inventory'
               76  LOAD_ATTR                try_remove_object_by_id
               78  LOAD_FAST                'item'
               80  LOAD_ATTR                id
               82  LOAD_FAST                'item'
               84  LOAD_METHOD              stack_count
               86  CALL_METHOD_0         0  '0 positional arguments'
               88  LOAD_CONST               ('count',)
               90  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               92  STORE_FAST               'success'
               94  JUMP_BACK            70  'to 70'
               96  POP_BLOCK        
               98  JUMP_ABSOLUTE       132  'to 132'
            100_0  COME_FROM            62  '62'

 L. 528       100  LOAD_FAST                'previous_inventory'
              102  LOAD_ATTR                try_remove_object_by_id
              104  LOAD_FAST                'drag_object'
              106  LOAD_ATTR                id
              108  LOAD_CONST               1
              110  LOAD_CONST               ('count',)
              112  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              114  STORE_FAST               'success'

 L. 529       116  LOAD_FAST                'previous_inventory'
              118  LOAD_METHOD              get_stack_items
              120  LOAD_FAST                'stack_id'
              122  CALL_METHOD_1         1  '1 positional argument'
              124  STORE_FAST               'stack_items'
            126_0  COME_FROM_LOOP       64  '64'
              126  JUMP_FORWARD        132  'to 132'
            128_0  COME_FROM            58  '58'

 L. 531       128  LOAD_CONST               True
              130  STORE_FAST               'success'
            132_0  COME_FROM           126  '126'

 L. 532       132  LOAD_FAST                'success'
              134  LOAD_FAST                'stack_items'
              136  BUILD_TUPLE_2         2 
              138  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 126_0

    def remove_drag_object_and_get_next_item(self, drag_object):
        next_object_id = None
        success, stack_items = self._get_stack_items_from_drag_object(drag_object, remove=True)
        if success:
            if stack_items:
                next_object_id = stack_items[0].id
        return (
         success, next_object_id)

    def get_live_drag_object_value(self, drag_object, is_stack=False):
        _, stack_items = self._get_stack_items_from_drag_object(drag_object, remove=False, is_stack=is_stack)
        value = 0
        if is_stack and stack_items:
            for item in stack_items:
                value += item.current_value * item.stack_count()

        else:
            value = drag_object.current_value
        return value

    def start_live_drag(self, live_drag_object, start_system, is_stack, should_send_start_message: bool=True):
        self._live_drag_start_system = start_system
        success = True
        if is_stack:
            inventoryitem_component = live_drag_object.inventoryitem_component
            stack_id = inventoryitem_component.get_stack_id()
            current_inventory = inventoryitem_component.get_inventory()
            stack_items = current_inventory.get_stack_items(stack_id)
        else:
            stack_items = [
             live_drag_object]
        for item in stack_items:
            live_drag_component = live_drag_object.live_drag_component
            live_drag_component = item.live_drag_component
            if live_drag_component is None:
                logger_live_drag.error('Live Drag Start called on an object with no Live Drag Component. Object: {}'.format(item))
                self.send_live_drag_cancel(live_drag_object.id)
                return
            if not item.in_use or item.in_use_by(self):
                if not live_drag_component.can_live_drag:
                    logger_live_drag.warn('Live Drag Start called on an object that is in use. Object: {}'.format(item))
                    self.send_live_drag_cancel(item.id)
                    return
                success = live_drag_component.start_live_dragging(self, start_system)
                if not success:
                    break
                self._live_drag_objects.append(item)

        if not success:
            self.cancel_live_drag_on_objects()
            self.send_live_drag_cancel(live_drag_object.id, LiveDragLocation.INVALID)
        self._live_drag_is_stack = is_stack
        if gsi_handlers.live_drag_handlers.live_drag_archiver.enabled:
            gsi_handlers.live_drag_handlers.archive_live_drag('Start', 'Operation',
              (LiveDragLocation.GAMEPLAY_SCRIPT),
              start_system,
              live_drag_object_id=(live_drag_object.id))
        if live_drag_object.live_drag_component.active_household_has_sell_permission:
            sell_value = self.get_live_drag_object_value(live_drag_object, self._live_drag_is_stack) if live_drag_object.definition.get_is_deletable() else -1
            for child_object in live_drag_object.get_all_children_gen():
                sell_value += self.get_live_drag_object_value(child_object) if child_object.definition.get_is_deletable() else 0

        else:
            sell_value = -1
        valid_drop_object_ids, valid_stack_id = live_drag_component.get_valid_drop_object_ids()
        icon_info = create_icon_info_msg(live_drag_object.get_icon_info_data())
        if should_send_start_message:
            op = distributor.ops.LiveDragStart(live_drag_object.id, start_system, valid_drop_object_ids, valid_stack_id, sell_value, icon_info)
            distributor_system = Distributor.instance()
            distributor_system.add_op_with_no_owner(op)

    def end_live_drag(self, source_object, target_object=None, end_system=LiveDragLocation.INVALID, location=None):
        live_drag_component = source_object.live_drag_component
        if live_drag_component is None:
            logger_live_drag.error('Live Drag End called on an object with no Live Drag Component. Object: {}'.format(source_object))
            self.send_live_drag_cancel(source_object.id, end_system)
            return
        elif source_object not in self._live_drag_objects:
            logger_live_drag.warn('Live Drag End called on an object not being Live Dragged. Object: {}'.format(source_object))
            self.send_live_drag_cancel(source_object.id, end_system)
            return
            source_object_id = source_object.id
            if end_system == LiveDragLocation.BUILD_BUY:
                self.objects_moved_via_live_drag.add(source_object)
        else:
            self.objects_moved_via_live_drag.discard(source_object)
        self.cancel_live_drag_on_objects()
        next_object_id = None
        success = False
        inventory_item = source_object.inventoryitem_component
        if target_object is not None:
            live_drag_target_component = target_object.live_drag_target_component
            if live_drag_target_component is not None:
                success, next_object_id = live_drag_target_component.drop_live_drag_object(source_object, self._live_drag_is_stack)
            else:
                if source_object.parent_object() is target_object:
                    success = True
                else:
                    if source_object.parent_object() is None and location is not None:
                        inventory_item = source_object.inventoryitem_component
                        if inventory_item is not None:
                            if inventory_item.is_in_inventory():
                                success, next_object_id = self.remove_drag_object_and_get_next_item(source_object)
                        source_object.set_location(location)
                    else:
                        logger_live_drag.error('Live Drag Target Component missing on object: {} and {} cannot be slotted into it.'.format(target_object, source_object))
                        success = False
        else:
            if not (inventory_item is not None and inventory_item.is_in_inventory()):
                if location is not None:
                    source_object.set_location(location)
                success, next_object_id = self.remove_drag_object_and_get_next_item(source_object)
            else:
                success = True
        if location is not None:
            source_object.set_location(location)
        elif success:
            if gsi_handlers.live_drag_handlers.live_drag_archiver.enabled:
                gsi_handlers.live_drag_handlers.archive_live_drag('End', 'Operation',
                  (LiveDragLocation.GAMEPLAY_SCRIPT),
                  end_system,
                  live_drag_object_id=source_object_id,
                  live_drag_target=target_object)
            if not self._live_drag_is_stack:
                next_object_id = None
            op = distributor.ops.LiveDragEnd(source_object_id, self._live_drag_start_system, end_system, next_object_id)
            distributor_system = Distributor.instance()
            distributor_system.add_op_with_no_owner(op)
            self._live_drag_objects = []
            self._live_drag_start_system = LiveDragLocation.INVALID
            self._live_drag_is_stack = False
        else:
            self.send_live_drag_cancel(source_object_id, end_system)

    def cancel_live_drag(self, live_drag_object, end_system=LiveDragLocation.INVALID):
        live_drag_component = live_drag_object.live_drag_component
        if live_drag_component is None:
            logger_live_drag.warn('Live Drag Cancel called on an object with no Live Drag Component. Object: {}'.format(live_drag_object))
            self.send_live_drag_cancel(live_drag_object.id)
            return
        elif live_drag_component.live_drag_state == LiveDragState.NOT_LIVE_DRAGGING:
            logger_live_drag.warn('Live Drag Cancel called on an object not being Live Dragged. Object: {}'.format(live_drag_object))
        else:
            self.cancel_live_drag_on_objects()
        self.send_live_drag_cancel(live_drag_object.id, end_system)

    def sell_live_drag_object(self, live_drag_object, currency_type, end_system=LiveDragLocation.INVALID):
        live_drag_component = live_drag_object.live_drag_component
        if not (live_drag_component is None or live_drag_object.definition.get_is_deletable()):
            logger_live_drag.error("Live Drag Sell called on object with no Live Drag Component or can't be deleted. Object: {}".format(live_drag_object))
            self.send_live_drag_cancel(live_drag_object.id, end_system)
            return

        def sell_response(dialog):
            op = distributor.ops.LiveDragEnd((live_drag_object.id), (self._live_drag_start_system), end_system, next_stack_object_id=None)
            distributor_system = Distributor.instance()
            distributor_system.add_op_with_no_owner(op)
            if not dialog.accepted:
                self.cancel_live_drag_on_objects()
                return
                value = int(self.get_live_drag_object_value(live_drag_object, self._live_drag_is_stack))
                for child_object in live_drag_object.get_all_children_gen():
                    value += self.get_live_drag_object_value(child_object) if child_object.definition.get_is_deletable() else 0

                object_tags = set()
                if self._live_drag_is_stack:
                    _, stack_items = self._get_stack_items_from_drag_object(live_drag_object, remove=True, is_stack=True)
                    for item in stack_items:
                        live_drag_component = item.live_drag_component
                        live_drag_component.cancel_live_dragging(should_reset=False)
                        item.base_value = 0
                        item.set_stack_count(0)
                        object_tags.update(item.get_tags())
                        item.destroy(source=item, cause='Selling stack of live drag objects.')

            else:
                live_drag_object.live_drag_component.cancel_live_dragging(should_reset=False)
                object_tags.update(live_drag_object.get_tags())
                if live_drag_object.is_in_inventory():
                    self.remove_drag_object_and_get_next_item(live_drag_object)
                else:
                    live_drag_object.remove_from_client()
                object_tags = frozenset(object_tags)
                live_drag_object.base_value = 0
                live_drag_object.destroy(source=live_drag_object, cause='Selling live drag object.')
            services.active_household().add_currency_amount(currency_type, value, (Consts_pb2.TELEMETRY_OBJECT_SELL), (self.active_sim), tags=object_tags)
            self._live_drag_objects = []
            self._live_drag_start_system = LiveDragLocation.INVALID
            self._live_drag_is_stack = False
            self._live_drag_sell_dialog_active = False

        favorites_tracker = self.active_sim_info.favorites_tracker
        if favorites_tracker and favorites_tracker.is_favorite_stack(live_drag_object):
            dialog = LiveDragTuning.LIVE_DRAG_SELL_FAVORITE_DIALOG(owner=live_drag_object)
        else:
            if self._live_drag_is_stack:
                dialog = LiveDragTuning.LIVE_DRAG_SELL_STACK_DIALOG(owner=live_drag_object)
            else:
                dialog = LiveDragTuning.LIVE_DRAG_SELL_DIALOG(owner=live_drag_object)
        dialog.show_dialog(on_response=sell_response)
        self._live_drag_sell_dialog_active = True

    def send_live_drag_cancel(self, live_drag_object_id, live_drag_end_system=LiveDragLocation.INVALID):
        if gsi_handlers.live_drag_handlers.live_drag_archiver.enabled:
            gsi_handlers.live_drag_handlers.archive_live_drag('Cancel', 'Operation',
              (LiveDragLocation.GAMEPLAY_SCRIPT),
              live_drag_end_system,
              live_drag_object_id=live_drag_object_id)
        op = distributor.ops.LiveDragCancel(live_drag_object_id, self._live_drag_start_system, live_drag_end_system)
        distributor_system = Distributor.instance()
        distributor_system.add_op_with_no_owner(op)
        if not self._live_drag_sell_dialog_active:
            self._live_drag_objects = []
            self._live_drag_start_system = LiveDragLocation.INVALID
            self._live_drag_is_stack = False

    def on_add(self):
        if self._account is not None:
            self._account.register_client(self)
        for sim_info in self._selectable_sims:
            self.on_sim_added_to_skewer(sim_info)

        distributor = Distributor.instance()
        distributor.add_object(self)
        distributor.add_client(self)
        self.send_selectable_sims_update()
        self.selectable_sims.add_watcher(self, self.send_selectable_sims_update)

    def on_remove(self):
        if self.active_sim is not None:
            self._set_active_sim_without_field_distribution(None)
        if self._account is not None:
            self._account.unregister_client(self)
        for sim_info in self._selectable_sims:
            self.on_sim_removed_from_skewer(sim_info)

        self.selectable_sims.remove_watcher(self)
        distributor = Distributor.instance()
        distributor.remove_client(self)
        self._selectable_sims = None
        self.active = False

    def get_objects_in_view_gen(self):
        for manager in services.client_object_managers():
            for obj in manager.get_all_for_distribution():
                yield obj

    def notify_active_sim_changed(self, old_sim, new_sim_info=None):
        new_sim = new_sim_info.get_sim_instance() if new_sim_info is not None else None
        self._active_sim_changed(old_sim, new_sim)
        vfx_mask.notify_client_mask_update(new_sim_info)

    def _get_selector_visual_type(self, sim_info):
        if sim_info.is_baby:
            return (
             Sims_pb2.SimPB.BABY, None)
            if sim_info.is_infant_or_toddler:
                if services.daycare_service().is_sim_info_at_daycare(sim_info):
                    return (
                     Sims_pb2.SimPB.AT_DAYCARE, None)
            if sim_info.household.missing_pet_tracker.is_pet_missing(sim_info):
                return (
                 Sims_pb2.SimPB.PET_MISSING, None)
            sim = sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            for career in sim_info.careers.values():
                if career.currently_at_work:
                    if career.is_at_active_event:
                        if sim is None:
                            return (
                             Sims_pb2.SimPB.MISSING_ACTIVE_WORK, career.career_category)
                    return (
                     Sims_pb2.SimPB.AT_WORK, career.career_category)
                    if career.is_late:
                        return career.taking_day_off or (
                         Sims_pb2.SimPB.LATE_FOR_WORK, career.career_category)

            if services.get_rabbit_hole_service().should_override_selector_visual_type(sim_info.id):
                return (
                 Sims_pb2.SimPB.OTHER, None)
            if sim is not None:
                if sim.has_hidden_flags(HiddenReasonFlag.RABBIT_HOLE):
                    return (
                     Sims_pb2.SimPB.OTHER, None)
            if services.hidden_sim_service().is_hidden(sim_info.id):
                return (
                 Sims_pb2.SimPB.OTHER, None)
        else:
            active_sim_info = services.active_sim_info()
            if active_sim_info is not None:
                if sim_info.travel_group_id != active_sim_info.travel_group_id:
                    return (
                     Sims_pb2.SimPB.OTHER, None)
            tutorial_service = services.get_tutorial_service()
            if tutorial_service is not None and tutorial_service.is_sim_unselectable(sim_info):
                return (
                 Sims_pb2.SimPB.OTHER, None)
        return (
         Sims_pb2.SimPB.NORMAL, None)

    def send_selectable_sims_update(self):
        msg = Sims_pb2.UpdateSelectableSims()
        for sim_info in self._selectable_sims:
            with ProtocolBufferRollback(msg.sims) as (new_sim):
                new_sim.id = sim_info.sim_id
                if sim_info.career_tracker is None:
                    logger.error('CareerTracker is None for selectable Sim {}'.format(sim_info))
                else:
                    career = sim_info.career_tracker.get_currently_at_work_career()
                    new_sim.at_work = career is not None and not career.is_at_active_event
                new_sim.is_selectable = sim_info.get_is_enabled_in_skewer()
                selector_visual_type, career_category = self._get_selector_visual_type(sim_info)
                new_sim.selector_visual_type = selector_visual_type
                if career_category is not None:
                    new_sim.career_category = career_category
                new_sim.can_care_for_toddler_at_home = sim_info.can_care_for_toddler_at_home
                if not sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                    new_sim.instance_info.zone_id = sim_info.zone_id
                    new_sim.instance_info.world_id = sim_info.world_id
                    new_sim.firstname = sim_info.first_name
                    new_sim.lastname = sim_info.last_name
                    zone_data_proto = services.get_persistence_service().get_zone_proto_buff(sim_info.zone_id)
                    if zone_data_proto is not None:
                        new_sim.instance_info.zone_name = zone_data_proto.name

        distributor = Distributor.instance()
        distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.SELECTABLE_SIMS_UPDATE, msg))

    @constproperty
    def is_sim():
        return False


class SelectableSims:

    def __init__(self, client):
        self._selectable_sim_infos = []
        self.client = client
        self._watchers = defaultdict(list)
        self._can_select_pets = False

    def __iter__(self):
        return iter(sorted((self._selectable_sim_infos), key=(lambda x: (-x.species, x.age, x.age_progress)), reverse=True))

    def __contains__(self, sim_info):
        return sim_info in self._selectable_sim_infos

    def __bool__(self):
        if self._selectable_sim_infos:
            return True
        return False

    def __len__(self):
        return len(self._selectable_sim_infos)

    @property
    def can_select_pets(self):
        return self._can_select_pets

    @can_select_pets.setter
    def can_select_pets(self, value):
        self._can_select_pets = value
        self.notify_dirty()
        if not value:
            self.client.validate_selectable_sim()

    def add_selectable_sim_info(self, sim_info, send_relationship_update=True):
        if sim_info not in self._selectable_sim_infos:
            self._selectable_sim_infos.append(sim_info)
            self.client.on_sim_added_to_skewer(sim_info, send_relationship_update=send_relationship_update)
            self.notify_dirty()

    def remove_selectable_sim_info(self, sim_info):
        exists = sim_info in self._selectable_sim_infos
        if exists:
            self._selectable_sim_infos.remove(sim_info)
            self.client.on_sim_removed_from_skewer(sim_info)
            self.notify_dirty()

    def get_next_selectable(self, current_selected_sim_info):
        if not any((s.get_is_enabled_in_skewer() for s in self)):
            return
        if current_selected_sim_info is not None:
            current_selected_sim_info = current_selected_sim_info not in self._selectable_sim_infos or current_selected_sim_info.get_is_enabled_in_skewer() or None
        iterator = filter(operator.methodcaller('get_is_enabled_in_skewer'), itertools.cycle(self))
        for sim_info in iterator:
            if current_selected_sim_info is None or sim_info is current_selected_sim_info:
                return next(iterator)

    def clear_selectable_sims(self):
        removed_list = list(self._selectable_sim_infos)
        self._selectable_sim_infos = []
        for sim_info in removed_list:
            self.client.on_sim_removed_from_skewer(sim_info)

        self.notify_dirty()

    def add_watcher(self, handle, f):
        self._watchers[handle].append(f)
        return handle

    def remove_watcher(self, handle):
        del self._watchers[handle]

    def notify_dirty(self):
        for watcher in itertools.chain.from_iterable(self._watchers.values()):
            watcher()

    def get_instanced_sims(self, allow_hidden_flags=0):
        sims = []
        for sim_info in self:
            sim = sim_info.get_sim_instance(allow_hidden_flags=allow_hidden_flags)
            if sim is not None:
                sims.append(sim)

        return sims