# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\pizza_delivery_situation.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 32148 bytes
from event_testing.resolver import DoubleSimAndObjectResolver, SingleObjectResolver
from typing import Tuple
import random
from autonomy.autonomy_request import AutonomyDistanceEstimationBehavior
from crafting.crafting_interactions import create_craftable, create_object
from distributor.shared_messages import IconInfoData
from event_testing.test_events import TestEvent
from interactions.utils.loot import LootActions
from objects.components.inventory_enums import StackScheme
from role.role_state import RoleState
from sims4.resources import Types
from sims4.tuning.tunable import TunableMapping, TunableReference, OptionalTunable, Tunable, TunableList
from sims4.tuning.tunable_base import GroupNames
from situations.service_npcs import ServiceNpcEndWorkReason
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, SituationState, SituationStateData, CommonInteractionCompletedSituationState
from situations.situation_job import SituationJob
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import alarms, clock, interactions, services, sims4.log, sims4.tuning.instances, sims4.tuning.tunable, situations.bouncer
USER_SPECIFIED_ID_TOKEN = 'user_specified_data_id'
CRAFTED_OBJECT_ID_TOKEN = 'crafted_object_id'
SELECTED_DEFINITIONS_IDS_TOKEN = 'user_specified_data_selection_definitions'
SELECTED_DEFINITIONS_IDS_COUNTS_TOKEN = 'user_specified_data_selection_counts'
SERVICE_NPC_TYPE_ID_TOKEN = 'service_npc_type_id'
HOUSEHOLD_ID_TOKEN = 'household_id'
HIRING_SIM_ID_TOKEN = 'hiring_sim_id'
logger = sims4.log.Logger('PizzaDelivery', default_owner='bhill')

class WaitForTipState(CommonInteractionCompletedSituationState):

    def _on_interaction_of_interest_complete(self, **kwargs):
        self._change_state(_LeaveState(ServiceNpcEndWorkReason.FINISHED_WORK))

    def _additional_tests(self, sim_info, event, resolver):
        return self.owner.is_sim_info_in_situation(sim_info)

    def timer_expired(self):
        logger.debug('No one tipped the delivery Sim and the Sim is sick of waiting.')
        self._change_state(_LeaveState(ServiceNpcEndWorkReason.FINISHED_WORK))


class _DeliveryDropOffState(CommonInteractionCompletedSituationState):

    def _additional_tests(self, sim_info, event, resolver):
        return self.owner.is_sim_info_in_situation(sim_info)

    def _on_interaction_of_interest_complete(self, **kwargs):
        self._change_state(self.owner.wait_for_tip_state())


class PizzaDeliverySituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'delivery_job':sims4.tuning.tunable.TunableTuple(situation_job=SituationJob.TunableReference(description='\n                A reference to the SituationJob used for the Sim performing the\n                delivery.\n                '),
       ring_doorbell_state=RoleState.TunableReference(description='\n                The state for telling a Sim to go and ring the doorbell.  This\n                is the initial state.\n                '),
       no_front_door_state=RoleState.TunableReference(description='\n                The fallback state for when the delivery Sim cannot reach the\n                front door or no front door exists.\n                '),
       wait_to_deliver_state=RoleState.TunableReference(description='\n                The state for telling a Sim to wait for the other Sim to accept\n                the delivery.\n                '),
       delivery_failure_state=RoleState.TunableReference(description='\n                The state that happens when the Sim has waited for the tuned\n                duration without anyone coming to accept the delivery.\n                '),
       leave_state=RoleState.TunableReference(description='\n                The state for the sim leaving.\n                '),
       delivery_dropoff_state=OptionalTunable(description='\n                This is an optional state that happens after the sim has accepted the delivery\n                and once completed goes into wait for tip state.\n                ',
       tunable=_DeliveryDropOffState.TunableFactory(description='\n                    The state for the sim to drop off the delivery \n                    ')),
       tuning_group=GroupNames.SITUATION), 
     'delivery_completion_affordances':situations.situation_complex.TunableInteractionOfInterest(description='\n            Affordances whose completion signals that the delivery has taken place.\n            ',
       tuning_group=GroupNames.TRIGGERS), 
     'wait_for_customer_duration':sims4.tuning.tunable.TunableSimMinute(description='\n            The amount of time to wait for a Sim to accept the delivery.\n            ',
       default=60,
       tuning_group=GroupNames.SITUATION), 
     'finish_job_notifications':TunableMapping(description='\n            Tune pairs of job finish role states with their notifications.\n            ',
       key_type=ServiceNpcEndWorkReason,
       value_type=TunableUiDialogNotificationSnippet(description='\n                Localized strings to display as notifications when this service\n                NPC finishes his/her work for the day for the matching finish\n                job reason. Parameter 0 is the funds deducted from the\n                household and parameter 1 is the amount added to bills, so you\n                can use {0.Money}, {0.Number}, {1.Money}, or {1.Number}.\n                ')), 
     'wait_for_tip_state':WaitForTipState.TunableFactory(), 
     'container':OptionalTunable(description='\n            The user selection(s) will be stored on the container if enabled.\n            ',
       tunable=sims4.tuning.tunable.TunableTuple(container_object_definition=TunableReference(description='\n                    The object that will be created and the NPC will carry to deliver.\n                    ',
       manager=(services.get_instance_manager(Types.OBJECT))),
       loots_to_apply_on_creation=TunableList(description='\n                    Loot Actions that will be applied upon container creation.\n                    Tests are ran on the object and NPC Sim\n                    ',
       tunable=(LootActions.TunableReference()))),
       tuning_group=GroupNames.SITUATION), 
     'charge_for_recipe':Tunable(description='\n            If set to True, the situation when the delivery is completed\n            will also charge for the recipe alongside the delivery fee.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SITUATION), 
     'loots_to_apply_on_deliverables':TunableList(description='\n            Loot Actions to apply to every item that is being delivered.\n            ',
       tunable=LootActions.TunableReference(pack_safe=True),
       tuning_group=GroupNames.SITUATION)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._service_npc = None
        self._service_start_time = None
        reader = self._seed.custom_init_params_reader
        self._service_npc_type = services.get_instance_manager(sims4.resources.Types.SERVICE_NPC).get(reader.read_uint64(SERVICE_NPC_TYPE_ID_TOKEN, 0))
        if self._service_npc_type is None:
            raise ValueError('Invalid service npc type for situation: {}'.format(self))
        self._hiring_household = services.household_manager().get(reader.read_uint64(HOUSEHOLD_ID_TOKEN, 0))
        self._hiring_sim = services.sim_info_manager().get(reader.read_uint64(HIRING_SIM_ID_TOKEN, 0))
        if self._hiring_household is None:
            raise ValueError('Invalid household for situation: {}'.format(self))
        self._object_definition_to_craft = reader.read_uint64(USER_SPECIFIED_ID_TOKEN, 0)
        selected_definition_ids = reader.read_uint64s(SELECTED_DEFINITIONS_IDS_TOKEN, [])
        selected_definition_counts = reader.read_uint64s(SELECTED_DEFINITIONS_IDS_COUNTS_TOKEN, [])
        self._user_selected_objects_for_container = tuple(zip(selected_definition_ids, selected_definition_counts))
        self._crafted_object_id = reader.read_uint64(CRAFTED_OBJECT_ID_TOKEN, 0)

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        writer.write_uint64(SERVICE_NPC_TYPE_ID_TOKEN, self._service_npc_type.guid64)
        writer.write_uint64(HOUSEHOLD_ID_TOKEN, self._hiring_household.id)
        writer.write_uint64(USER_SPECIFIED_ID_TOKEN, self._object_definition_to_craft)
        writer.write_uint64(CRAFTED_OBJECT_ID_TOKEN, self._crafted_object_id)
        writer.write_uint64(HIRING_SIM_ID_TOKEN, 0 if self._hiring_sim is None else self._hiring_sim.id)
        if self._user_selected_objects_for_container:
            object_definition_ids, object_counts = zip(*self._user_selected_objects_for_container)
            writer.write_uint64s(SELECTED_DEFINITIONS_IDS_TOKEN, object_definition_ids)
            writer.write_uint64s(SELECTED_DEFINITIONS_IDS_COUNTS_TOKEN, object_counts)

    @classmethod
    def _states(cls):
        return (SituationStateData(2, _RingDoorBellState),
         SituationStateData(3, _NoFrontDoorState),
         SituationStateData(4, _WaitForCustomerState),
         SituationStateData(5, _DeliveryDropOffState, factory=(cls.delivery_job.delivery_dropoff_state)),
         SituationStateData(6, WaitForTipState, factory=(cls.wait_for_tip_state)),
         SituationStateData(7, _LeaveState),
         SituationStateData(8, _DeliveryFailureState))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [
         (cls.delivery_job.situation_job,
          cls.delivery_job.ring_doorbell_state)]

    @classmethod
    def default_job(cls):
        return cls.delivery_job.situation_job

    def start_situation(self):
        super().start_situation()
        self._change_state(_RingDoorBellState())

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        self._service_npc = sim
        services.current_zone().service_npc_service.cancel_service(self._hiring_household, self._service_npc_type)

    def _on_remove_sim_from_situation(self, sim):
        super()._on_remove_sim_from_situation(sim)
        self._service_npc = None

    def _on_leaving_situation(self, end_work_reason):
        service_npc_type = self._service_npc_type
        household = self._hiring_household
        try:
            paid_amount = 0
            billed_amount = 0
            if self._object_definition_to_craft != 0:
                now = services.time_service().sim_now
                service_record = household.get_service_npc_record(service_npc_type.guid64)
                service_record.time_last_finished_service = now
                time_worked = now - (self._service_start_time or now)
                time_worked_in_hours = time_worked.in_hours()
                cost = service_npc_type.get_cost(time_worked_in_hours)
                if self.charge_for_recipe:
                    recipe = services.get_instance_manager(sims4.resources.Types.RECIPE).get(self._object_definition_to_craft)
                    original_recipe_cost, _, _ = recipe.get_price(is_retail=True)
                    cost = cost + original_recipe_cost
                if cost > 0:
                    paid_amount, billed_amount = service_npc_type.try_charge_for_service(household, cost)
                    if billed_amount:
                        end_work_reason = ServiceNpcEndWorkReason.NOT_PAID
            self._send_end_work_notification(end_work_reason, paid_amount, billed_amount)
        except Exception as e:
            try:
                logger.exception('Exception while executing _on_leaving_situation for situation {}', self, exc=e)
            finally:
                e = None
                del e

    def _send_end_work_notification(self, end_work_reason, *localization_args):
        notification = self.finish_job_notifications.get(end_work_reason)
        if notification is None:
            return
        for client in services.client_manager().values():
            recipient = client.active_sim
            if recipient is not None:
                dialog = notification(recipient)
                dialog.show_dialog(additional_tokens=localization_args, icon_override=IconInfoData(obj_instance=(self._service_npc)))
                break

    @property
    def _should_cancel_leave_interaction_on_premature_removal(self):
        return True


sims4.tuning.instances.lock_instance_tunables(PizzaDeliverySituation, exclusivity=(situations.bouncer.bouncer_types.BouncerExclusivityCategory.SERVICE),
  creation_ui_option=(situations.situation_types.SituationCreationUIOption.NOT_AVAILABLE))

class _RingDoorBellState(SituationState):

    def __init__(self):
        super().__init__()
        self._interaction = None

    def on_activate(self, reader=None):
        logger.debug('Delivery NPC is entering ring door bell state.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.delivery_job.situation_job, self.owner.delivery_job.ring_doorbell_state)

    def _on_set_sim_role_state(self, sim, job_type, role_state_type, role_affordance_target):
        super()._on_set_sim_role_state(sim, job_type, role_state_type, role_affordance_target)
        self._choose_and_run_interaction()

    def on_deactivate(self):
        if self._interaction is not None:
            self._interaction.unregister_on_finishing_callback(self._on_finishing_callback)
            self._interaction = None
        super().on_deactivate()

    def _choose_and_run_interaction(self):
        self._interaction = self.owner._choose_role_interaction((self.owner._service_npc),
          run_priority=(interactions.priority.Priority.Low))
        if self._interaction is None:
            logger.debug("Delivery NPC couldn't find interaction on front door.")
            self._change_state(_NoFrontDoorState())
            return
        execute_result = interactions.aop.AffordanceObjectPair.execute_interaction(self._interaction)
        if not execute_result:
            logger.debug('Delivery NPC failed to execute interaction on front door.')
            self._interaction = None
            self._change_state(_NoFrontDoorState())
            return
        logger.debug('Delivery NPC starting interaction on front door.')
        self._interaction.register_on_finishing_callback(self._on_finishing_callback)

    def _on_finishing_callback(self, interaction):
        if self._interaction is not interaction:
            return
        if interaction.uncanceled or interaction.was_initially_displaced:
            self._change_state(_WaitForCustomerState())
            return
        logger.debug('Delivery NPC failed interaction on front door.')
        self._change_state(_NoFrontDoorState())

    def _create_container(self):
        container = create_object(self.owner.container.container_object_definition)
        if container:
            if self.owner.container.loots_to_apply_on_creation:
                resolver = DoubleSimAndObjectResolver(self.owner._hiring_sim, self.owner._service_npc, container, self.owner)
                for loot in self.owner.container.loots_to_apply_on_creation:
                    loot.apply_to_resolver(resolver)

        return container

    def _apply_loot_to_deliverable(self, obj):
        resolver = SingleObjectResolver(obj)
        for loot in self.owner.loots_to_apply_on_deliverables:
            loot.apply_to_resolver(resolver)

    def _setup_container_target_object(self):
        if self.owner.container is None:
            logger.error('Attempting setup selection with container object without a container')
            return
        target = self._create_container()
        if target is None:
            logger.error('Could not create container object {}', self.owner.container.container_object_definition)
            return
        hiring_household_id = self.owner._hiring_household.id
        target.set_household_owner_id(hiring_household_id)
        self.owner._service_npc.inventory_component.system_add_object(target)
        for definition_id, amount_to_create in self.owner._user_selected_objects_for_container:
            if target.inventoryitem_component is not None:
                obj = create_object(definition_id)
                if obj is None:
                    logger.error("Could not create object from definition id '{}'", definition_id)
                    continue
                if not target.inventory_component.can_add(obj):
                    obj.destroy(source=self, cause='Could not store the object onto the container due to missing inventory types')
                    logger.error("Attempting to store the object '{}' into '{}'s inventory. Add the inventory type '{}' to the object!", obj, target, target.inventory_component.inventory_type)
                    continue
            self._apply_loot_to_deliverable(obj)
            obj.set_household_owner_id(hiring_household_id)
            if obj.inventoryitem_component.get_stack_scheme() == StackScheme.NONE:
                target.inventory_component.system_add_object(obj)
                for _ in range(amount_to_create - 1):
                    obj = create_object(definition_id)
                    self._apply_loot_to_deliverable(obj)
                    obj.set_household_owner_id(hiring_household_id)
                    target.inventory_component.system_add_object(obj)

            else:
                obj.set_stack_count(amount_to_create)
                target.inventory_component.system_add_object(obj)

        return target

    def _setup_recipe_target_object(self):
        obj_def_to_craft = self.owner._object_definition_to_craft
        if obj_def_to_craft != 0:
            recipe = services.get_instance_manager(sims4.resources.Types.RECIPE).get(obj_def_to_craft)
            if recipe is None and self.owner.container is not None:
                logger.error('No recipe for {}', self)
                return
        else:
            possible_recipes = self.owner._service_npc_type.recipe_picker_on_hire.recipes
            if possible_recipes is None:
                logger.error('No recipe for {}', self)
                return
            recipe = random.choice(possible_recipes)
        place_craftable_in_npc_inventory = True
        if self.owner.container is not None:
            place_craftable_in_npc_inventory = False
        else:
            target = create_craftable(recipe, (self.owner._service_npc), owning_household_id_override=(self.owner._hiring_household.id),
              place_in_inventory=place_craftable_in_npc_inventory)
            self._apply_loot_to_deliverable(target)
            if not place_craftable_in_npc_inventory:
                container_obj = self._create_container()
                if container_obj is None:
                    logger.error('Could not create container object {}', self.owner.container.container_object_definition)
                else:
                    if container_obj.inventoryitem_component is not None:
                        if container_obj.inventory_component.can_add(target):
                            container_obj.set_household_owner_id(self.owner._hiring_household.id)
                            self.owner._service_npc.inventory_component.system_add_object(container_obj)
                            container_obj.inventory_component.system_add_object(target)
                            return container_obj
                    container_obj.destroy(source=self, cause='Could not store the recipe onto the container since the container has no inventory or recipe cannot be stored in an inventory')
        return target

    def _get_role_state_overrides(self, sim, job_type, role_state_type, role_affordance_target):
        if self.owner._crafted_object_id != 0:
            target = services.current_zone().inventory_manager.get(self.owner._crafted_object_id)
        else:
            if self.owner._user_selected_objects_for_container:
                target = self._setup_container_target_object()
            else:
                target = self._setup_recipe_target_object()
            if target is None:
                raise ValueError('No carry target created for {}'.format(self))
            self.owner._crafted_object_id = target.id
        return (
         role_state_type, target)


class _NoFrontDoorState(SituationState):

    def __init__(self):
        super().__init__()
        self._interaction = None

    def on_activate(self, reader=None):
        logger.debug('Delivery NPC is entering the no front door state.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.delivery_job.situation_job, self.owner.delivery_job.no_front_door_state)

    def on_deactivate(self):
        if self._interaction is not None:
            self._interaction.unregister_on_finishing_callback(self._on_finishing_callback)
            self._interaction = None
        super().on_deactivate()

    def _on_set_sim_role_state(self, *args, **kwargs):
        (super()._on_set_sim_role_state)(*args, **kwargs)
        self._choose_and_run_interaction()

    def _choose_and_run_interaction(self):
        self._interaction = self.owner._choose_role_interaction((self.owner._service_npc),
          run_priority=(interactions.priority.Priority.Low), allow_failed_path_plans=True)
        if self._interaction is None:
            logger.debug("Delivery NPC couldn't find the fallback behavior.")
            self._change_state(_DeliveryFailureState())
            return
        execute_result = interactions.aop.AffordanceObjectPair.execute_interaction(self._interaction)
        if not execute_result:
            logger.debug("Delivery NPC couldn't do the fallback behavior.")
            self._change_state(_WaitForCustomerState())
            return
        logger.debug('Delivery NPC doing the fallback behavior.')
        self._interaction.register_on_finishing_callback(self._on_finishing_callback)

    def _on_finishing_callback(self, interaction):
        if self._interaction is not interaction:
            return
        self._change_state(_WaitForCustomerState())


class _WaitForCustomerState(SituationState):

    def __init__(self):
        super().__init__()
        self._timeout_handle = None

    def on_activate(self, reader=None):
        logger.debug('Delivery NPC is entering wait state.')
        super().on_activate(reader)
        self.owner._service_start_time = services.time_service().sim_now
        self.owner._set_job_role_state(self.owner.delivery_job.situation_job, self.owner.delivery_job.wait_to_deliver_state)
        timeout = self.owner.wait_for_customer_duration
        self._timeout_handle = alarms.add_alarm(self, clock.interval_in_sim_minutes(timeout), lambda _: self.timer_expired())
        for custom_key in self.owner.delivery_completion_affordances.custom_keys_gen():
            self._test_event_register(TestEvent.InteractionComplete, custom_key)

    def on_deactivate(self):
        if self._timeout_handle is not None:
            alarms.cancel_alarm(self._timeout_handle)
        super().on_deactivate()

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            if resolver(self.owner.delivery_completion_affordances):
                if sim_info is self.owner._service_npc.sim_info:
                    if self.owner.delivery_job.delivery_dropoff_state is not None:
                        self._change_state(self.owner.delivery_job.delivery_dropoff_state())
                    else:
                        self._change_state(self.owner.wait_for_tip_state())

    def timer_expired(self):
        logger.debug('No one took the delivery and the delivery Sim is sick of waiting.')
        self._change_state(_DeliveryFailureState())


class _DeliveryFailureState(SituationState):

    def on_activate(self, reader=None):
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.delivery_job.situation_job, self.owner.delivery_job.delivery_failure_state)
        self._change_state(_LeaveState(ServiceNpcEndWorkReason.NO_WORK_TO_DO))


class _LeaveState(SituationState):

    def __init__(self, leave_role_reason):
        super().__init__()
        self._leave_role_reason = leave_role_reason

    def on_activate(self, reader=None):
        logger.debug('The delivery NPC is leaving.')
        super().on_activate(reader)
        self.owner._set_job_role_state(self.owner.delivery_job.situation_job, self.owner.delivery_job.leave_state)
        if reader is None:
            self.owner._on_leaving_situation(self._leave_role_reason)