# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\household_manager.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 28200 bytes
import collections, time, distributor
from protocolbuffers import FileSerialization_pb2, MoveInMoveOut_pb2, Consts_pb2
from build_buy import _buildbuy
from interactions.context import InteractionContext
from interactions.priority import Priority
from relationships import global_relationship_tuning
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims.household_enums import HouseholdChangeOrigin
from sims4.utils import classproperty
from singletons import DEFAULT
from world.travel_tuning import TravelTuning
import build_buy, id_generator, indexed_manager, objects.object_manager, persistence_error_types, server.account, services, sims.household, sims4.log
logger = sims4.log.Logger('HouseholdManager')

class HouseholdFixupHelper:

    def __init__(self):
        self._households_sharing_sims = set()

    def add_shared_sim_household(self, household):
        self._households_sharing_sims.add(household)

    def fix_shared_sim_households(self):
        for household in self._households_sharing_sims:
            if not household.destroy_household_if_empty():
                household.handle_adultless_household(skip_hidden=True, skip_premade=True)


class HouseholdManager(objects.object_manager.DistributableObjectManager):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._loaded = False
        self._save_slot_data = None
        self._pending_household_funds = collections.defaultdict(list)
        self._pending_transfers = {}

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_HOUSEHOLD_MANAGER

    def create_household(self, account, starting_funds=DEFAULT):
        new_household = sims.household.Household(account, starting_funds)
        self.add(new_household)
        return new_household

    def load_households(self):
        if self._loaded:
            return
        if indexed_manager.capture_load_times:
            time_stamp = time.time()
        fixup_helper = HouseholdFixupHelper()
        business_service = services.business_service()
        for household_proto in services.get_persistence_service().all_household_protos():
            household_id = household_proto.household_id
            household = self.get(household_id)
            if household is None:
                household = self._load_household_from_household_proto(household_proto, fixup_helper=fixup_helper)
                business_service.load_legacy_data(household, household_proto)

        fixup_helper.fix_shared_sim_households()
        for household_id in self._pending_household_funds.keys():
            logger.error('Household {} has pending funds leftover from BB after all households were loaded.', household_id, owner='camilogarcia')

        self._pending_household_funds = None
        relationship_service = services.relationship_service()
        if relationship_service is not None:
            relationship_service.purge_invalid_relationships()
        for sim_info in services.sim_info_manager().get_all():
            sim_info.on_all_sim_infos_loaded()
            sim_info.set_default_data()

        if indexed_manager.capture_load_times:
            elapsed_time = time.time() - time_stamp
            indexed_manager.object_load_times['household'] = elapsed_time
        self._loaded = True

    def load_household(self, household_id):
        return self._load_household(household_id)

    def _load_household(self, household_id):
        household = self.get(household_id)
        if household is not None:
            for sim_info in household.sim_info_gen():
                zone_id = services.current_zone_id()
                if sim_info.zone_id != zone_id:
                    householdProto = services.get_persistence_service().get_household_proto_buff(household_id)
                    if householdProto is None:
                        logger.error('unable to find household with household id {}'.household_id)
                        return
                    found_sim = False
                    if householdProto.sims.ids:
                        for sim_id in householdProto.sims.ids:
                            if sim_id == sim_info.sim_id:
                                found_sim = True
                                break

                    if found_sim:
                        sim_proto = services.get_persistence_service().get_sim_proto_buff(sim_id)
                        sim_info.load_sim_info(sim_proto)

            return household
        logger.info('Starting to load household id = {0}', household_id)
        household_proto = services.get_persistence_service().get_household_proto_buff(household_id)
        if household_proto is None:
            sims4.log.error('Persistence', 'Household proto could not be found id = {0}', household_id)
            return
        household = self._load_household_from_household_proto(household_proto)
        return household

    def _load_household_from_household_proto(self, household_proto, fixup_helper=None):
        account = services.account_service().get_account_by_id((household_proto.account_id), try_load_account=True)
        if account is None:
            sims4.log.error('Persistence', "Household account doesn't exist in account ids. Creating temp account", owner='yshan')
            account = server.account.Account(household_proto.account_id, 'TempPersonaName')
        household = sims.household.Household(account)
        resend_sim_infos = household.load_data(household_proto, fixup_helper)
        logger.info('Household loaded. name:{:20} id:{:10} #sim_infos:{:2}', household.name, household.id, len(household))
        self.add(household)
        if resend_sim_infos:
            household.resend_sim_infos()
        household.initialize_sim_infos()
        if household is services.client_manager().get_first_client().household:
            for sim_info in household.sim_info_gen():
                for other_info in household.sim_info_gen():
                    if sim_info is not other_info:
                        relationship_service = services.relationship_service()
                        if relationship_service.has_bit(sim_info.id, other_info.id, global_relationship_tuning.RelationshipGlobalTuning.NEIGHBOR_RELATIONSHIP_BIT):
                            relationship_service.remove_relationship_bit(sim_info.id, other_info.id, global_relationship_tuning.RelationshipGlobalTuning.NEIGHBOR_RELATIONSHIP_BIT)

            household.bills_manager.sanitize_household_inventory()
        if self._pending_household_funds is not None:
            pending_funds_reasons = self._pending_household_funds.get(household.id)
            if pending_funds_reasons is not None:
                del self._pending_household_funds[household.id]
                for fund, reason in pending_funds_reasons:
                    household.funds.add(fund, reason, None)

        return household

    def switch_sim_household(self, sim_info, target_sim_info=None, reason=HouseholdChangeOrigin.UNKNOWN):
        active_household = services.active_household()
        starting_household = sim_info.household
        destination_household = active_household if target_sim_info is None else target_sim_info.household
        self.switch_sim_from_household_to_target_household(sim_info, starting_household, destination_household, reason=reason)

    def switch_sim_from_household_to_target_household(self, sim_info, starting_household, destination_household, destroy_if_empty_household=True, reason=HouseholdChangeOrigin.UNKNOWN):
        active_household = services.active_household()
        if services.hidden_sim_service().is_hidden(sim_info.id):
            services.hidden_sim_service().unhide(sim_info.id)
        elif starting_household is destination_household:
            logger.error('Trying to run AddToHousehold basic extra on a sim who is already in the destination household.')
            return False
            if not destination_household.can_add_sim_info(sim_info):
                logger.error('Trying to run AddToHousehold basic extra when there is no room in the destination household.')
                return False
            starting_household.remove_sim_info(sim_info, destroy_if_empty_household=destroy_if_empty_household, assign_to_none=False)
            destination_household.add_sim_info_to_household(sim_info, reason=reason)
            destination_household.add_household_transfer_buffs(sim_info)
            client = services.client_manager().get_first_client()
            destination_travel_group = destination_household.get_travel_group()
            failed_to_add_to_travel_group = False
            if destination_travel_group is not None:
                if sim_info.is_in_travel_group():
                    if sim_info not in destination_travel_group:
                        old_travel_group = services.travel_group_manager().get_travel_group_by_sim_info(sim_info)
                        old_travel_group.remove_sim_info(sim_info)
                if any((sim.sim_info in destination_travel_group for sim in client.selectable_sims.get_instanced_sims())):
                    can_add_to_travel_group = destination_travel_group.can_add_to_travel_group(sim_info)
                    failed_to_add_to_travel_group = not destination_travel_group.add_sim_info(sim_info) if can_add_to_travel_group else True
                    if can_add_to_travel_group:
                        if failed_to_add_to_travel_group:
                            logger.error('Unable to add Sim {} to travel group.', sim_info, owner='jdimailig')
            if destination_household is active_household:
                client.add_selectable_sim_info(sim_info)
                sim_info.apply_fixup_actions(SimInfoFixupActionTiming.ON_ADDED_TO_ACTIVE_HOUSEHOLD)
        else:
            client.remove_selectable_sim_info(sim_info)
        if sim_info.career_tracker is not None:
            sim_info.career_tracker.remove_invalid_careers()
        if sim_info.aspiration_tracker is not None:
            sim_info.aspiration_tracker.clear_tracked_client_data()
            sim_info.aspiration_tracker.send_event_data_to_client()
        sim = sim_info.get_sim_instance()
        if sim is not None:
            sim.update_intended_position_on_active_lot(update_ui=True)
            situation_manager = services.get_zone_situation_manager()
            for situation in situation_manager.get_situations_sim_is_in(sim):
                if destination_household is active_household:
                    if situation.is_user_facing:
                        continue
                situation_manager.remove_sim_from_situation(sim, situation.id)

            services.daycare_service().on_sim_spawn(sim_info)
            if destination_travel_group is not None:
                if failed_to_add_to_travel_group:
                    interaction_context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, Priority.Critical)
                    sim.push_super_affordance(TravelTuning.GO_HOME_INTERACTION, None, interaction_context)
        return True

    def is_household_stored_in_any_neighborhood_proto(self, household_id):
        for neighborhood_proto in services.get_persistence_service().get_neighborhoods_proto_buf_gen():
            if any((household_id == household_account_proto.household_id for household_account_proto in neighborhood_proto.npc_households)):
                return True

        return False

    def get_by_sim_id(self, sim_id):
        for house in self._objects.values():
            if house.sim_in_household(sim_id):
                return house

    def save(self, **kwargs):
        households = self.get_all()
        for household in households:
            household.save_data()

    def on_all_households_and_sim_infos_loaded(self, client):
        for household in self.get_all():
            household.on_all_households_and_sim_infos_loaded()

    def on_client_disconnect(self, client):
        for household in self.get_all():
            household.on_client_disconnect()

    def on_zone_load(self):
        for household in self.get_all():
            household.on_zone_load()

    def on_zone_unload(self):
        for household in self.get_all():
            household.on_zone_unload()

    @staticmethod
    def get_active_sim_home_zone_id():
        client = services.client_manager().get_first_client()
        if client is not None:
            active_sim = client.active_sim
            if active_sim is not None:
                household = active_sim.household
                if household is not None:
                    return household.home_zone_id

    def try_add_pending_household_funds(self, household_id, funds, reason):
        if self._pending_household_funds is None:
            return False
        self._pending_household_funds[household_id].append((funds, reason))
        return True

    def add_pending_transfer(self, household_id, is_transfer_solo, transfer_proto):
        self._pending_transfers[household_id] = (
         is_transfer_solo, transfer_proto)

    def get_pending_transfer(self, household_id):
        pending_transfer_data = self._pending_transfers.get(household_id, (None, None))
        return pending_transfer_data

    def remove_pending_transfer(self, household_id):
        if household_id in self._pending_transfers:
            del self._pending_transfers[household_id]

    def transfer_household_inventory(self, source_household, target_household):
        active_household = services.active_household()
        target_household.copy_rewards_inventory_from_household(source_household)
        if source_household is active_household:
            self.transfer_active_household_inventory(source_household, target_household)
        else:
            if target_household is active_household:
                self.transfer_inactive_household_inventory(source_household, target_household)
            else:
                logger.error("Trying to transfer household inventory from one inactive household to another, we currently don't support that. Feel free to add if we come up with a use case. S={}, T={}", source_household, target_household)

    def transfer_active_household_inventory(self, source_household, target_household):
        inventory_available = build_buy.is_household_inventory_available(target_household.id)
        source_household_msg = services.get_persistence_service().get_household_proto_buff(source_household.id)
        target_household_msg = services.get_persistence_service().get_household_proto_buff(target_household.id)
        object_manager = services.object_manager()
        object_ids = build_buy.get_object_ids_in_household_inventory(source_household.id)
        for object_id in object_ids:
            object_data_raw = _buildbuy.get_object_data_in_household_inventory(object_id, source_household.id)
            if object_data_raw is None:
                continue
            obj = self.create_object_from_raw_inv_data(object_id, object_data_raw)
            self._transfer_object(target_household, obj, inventory_available, target_household_msg)

        for object_data in source_household_msg.inventory.objects:
            if object_data.object_id in object_ids:
                continue
            obj = object_manager.get(object_data.object_id)
            if obj is None:
                obj = self._create_object_from_object_data(object_data.object_id, object_data)
            if obj is not None:
                self._transfer_object(target_household, obj, inventory_available, target_household_msg)

    def _transfer_object(self, target_household, obj, inventory_available, target_household_msg):
        obj.set_household_owner_id(target_household.id)
        if inventory_available:
            build_buy.move_object_to_household_inventory(obj)
        else:
            if target_household_msg is not None:
                object_data = obj.save_object(target_household_msg.inventory.objects)
                if object_data is not None:
                    object_data.object_id = id_generator.generate_object_id()
            obj.destroy(cause='Merge/Transfer to New Household Inventory')

    def transfer_inactive_household_inventory--- This code section failed: ---

 L. 490         0  LOAD_GLOBAL              build_buy
                2  LOAD_METHOD              is_household_inventory_available
                4  LOAD_FAST                'source_household'
                6  LOAD_ATTR                id
                8  CALL_METHOD_1         1  '1 positional argument'
               10  POP_JUMP_IF_FALSE   100  'to 100'

 L. 491        12  LOAD_GLOBAL              build_buy
               14  LOAD_METHOD              get_object_ids_in_household_inventory
               16  LOAD_FAST                'source_household'
               18  LOAD_ATTR                id
               20  CALL_METHOD_1         1  '1 positional argument'
               22  STORE_FAST               'object_ids'

 L. 492        24  SETUP_LOOP          192  'to 192'
               26  LOAD_FAST                'object_ids'
               28  GET_ITER         
               30  FOR_ITER             96  'to 96'
               32  STORE_FAST               'object_id'

 L. 493        34  LOAD_GLOBAL              _buildbuy
               36  LOAD_METHOD              get_object_data_in_household_inventory
               38  LOAD_FAST                'object_id'
               40  LOAD_FAST                'source_household'
               42  LOAD_ATTR                id
               44  CALL_METHOD_2         2  '2 positional arguments'
               46  STORE_FAST               'object_data_raw'

 L. 494        48  LOAD_FAST                'self'
               50  LOAD_METHOD              create_object_from_raw_inv_data
               52  LOAD_FAST                'object_id'
               54  LOAD_FAST                'object_data_raw'
               56  CALL_METHOD_2         2  '2 positional arguments'
               58  STORE_FAST               'obj'

 L. 495        60  LOAD_GLOBAL              build_buy
               62  LOAD_METHOD              remove_object_from_household_inventory
               64  LOAD_FAST                'object_id'
               66  LOAD_FAST                'source_household'
               68  CALL_METHOD_2         2  '2 positional arguments'
               70  POP_TOP          

 L. 498        72  LOAD_FAST                'obj'
               74  LOAD_METHOD              set_household_owner_id
               76  LOAD_FAST                'target_household'
               78  LOAD_ATTR                id
               80  CALL_METHOD_1         1  '1 positional argument'
               82  POP_TOP          

 L. 499        84  LOAD_GLOBAL              build_buy
               86  LOAD_METHOD              move_object_to_household_inventory
               88  LOAD_FAST                'obj'
               90  CALL_METHOD_1         1  '1 positional argument'
               92  POP_TOP          
               94  JUMP_BACK            30  'to 30'
               96  POP_BLOCK        
               98  JUMP_FORWARD        192  'to 192'
            100_0  COME_FROM            10  '10'

 L. 503       100  LOAD_GLOBAL              services
              102  LOAD_METHOD              get_persistence_service
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  LOAD_METHOD              get_household_proto_buff
              108  LOAD_FAST                'source_household'
              110  LOAD_ATTR                id
              112  CALL_METHOD_1         1  '1 positional argument'
              114  STORE_FAST               'household_msg'

 L. 504       116  LOAD_FAST                'household_msg'
              118  LOAD_CONST               None
              120  COMPARE_OP               is-not
              122  POP_JUMP_IF_FALSE   192  'to 192'

 L. 505       124  SETUP_LOOP          178  'to 178'
              126  LOAD_FAST                'household_msg'
              128  LOAD_ATTR                inventory
              130  LOAD_ATTR                objects
              132  GET_ITER         
              134  FOR_ITER            176  'to 176'
              136  STORE_FAST               'object_msg'

 L. 506       138  LOAD_FAST                'self'
              140  LOAD_METHOD              _create_object_from_object_data
              142  LOAD_FAST                'object_msg'
              144  LOAD_ATTR                object_id
              146  LOAD_FAST                'object_msg'
              148  CALL_METHOD_2         2  '2 positional arguments'
              150  STORE_FAST               'obj'

 L. 507       152  LOAD_FAST                'obj'
              154  LOAD_METHOD              set_household_owner_id
              156  LOAD_FAST                'target_household'
              158  LOAD_ATTR                id
              160  CALL_METHOD_1         1  '1 positional argument'
              162  POP_TOP          

 L. 508       164  LOAD_GLOBAL              build_buy
              166  LOAD_METHOD              move_object_to_household_inventory
              168  LOAD_FAST                'obj'
              170  CALL_METHOD_1         1  '1 positional argument'
              172  POP_TOP          
              174  JUMP_BACK           134  'to 134'
              176  POP_BLOCK        
            178_0  COME_FROM_LOOP      124  '124'

 L. 511       178  LOAD_FAST                'household_msg'
              180  LOAD_ATTR                inventory
              182  LOAD_ATTR                objects
              184  LOAD_CONST               None
              186  LOAD_CONST               None
              188  BUILD_SLICE_2         2 
              190  DELETE_SUBSCR    
            192_0  COME_FROM           122  '122'
            192_1  COME_FROM            98  '98'
            192_2  COME_FROM_LOOP       24  '24'

Parse error at or near `COME_FROM' instruction at offset 192_1

    def create_object_from_raw_inv_data(self, object_id, raw_inv_data, load_object=False):
        object_data = FileSerialization_pb2.ObjectData()
        object_data.ParseFromString(raw_inv_data)
        return self._create_object_from_object_data(object_id, object_data, load_object=load_object)

    def _create_object_from_object_data(self, object_id, object_data, load_object=False):
        post_add_callback = lambda o:         if load_object:
o.load_object(object_data, inline_finalize=True) # Avoid dead code: None
        obj = objects.system.create_object((object_data.guid), obj_id=object_id,
          obj_state=(object_data.state_index),
          post_add=post_add_callback)
        return obj

    def move_household_out_of_lot(self, household, sell_furniture, delta_funds):
        zone_id = household.home_zone_id
        msg = MoveInMoveOut_pb2.MoveInMoveOutData()
        msg.zone_src = zone_id
        msg.zone_dst = 0
        msg.move_out_data_src.sell_furniture = sell_furniture
        msg.move_out_data_src.delta_funds = delta_funds
        msg.notify_gameplay = True
        distributor.system.Distributor.instance().add_event(Consts_pb2.MSG_MOVE_FAMILY_OUT, msg)