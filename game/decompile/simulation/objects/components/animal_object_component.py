# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\animal_object_component.py
# Compiled at: 2021-06-28 15:11:03
# Size of source mod 2**32: 17313 bytes
import services, sims4
from animation.animation_constants import ActorType
from distributor.fields import Field, ComponentField
from distributor.ops import SetActorType, SetCreatureType
from event_testing.resolver import SingleObjectResolver, DoubleObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.utils.loot import LootOperationList
from objects.animals.animal_loot_ops import AnimalDeathLootActions
from objects.animals.animal_telemetry import send_animal_added_telemetry
from objects.components import types, Component
from objects.components.animal_object_enums import RabbitAnimalType, HenAnimalType, ChickAnimalType, RoosterAnimalType, CowAnimalType, LlamaAnimalType
from objects.components.state import ObjectStateValue
from objects.object_enums import ItemLocation
from objects.slots import SlotType
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from sims4.common import Pack
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableVariant, TunableList, OptionalTunable, TunableTuple
from sims4.utils import classproperty
from tunable_utils.tunable_object_generator import TunableObjectGeneratorVariant
from ui.ui_dialog_notification import UiDialogNotification
logger = sims4.log.Logger('Animal Object Component', default_owner='amwu')

class AnimalObjectComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=types.ANIMAL_OBJECT_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.AnimalObjectComponent):
    FACTORY_TUNABLES = {'animal_type_tuning':TunableVariant(rabbit=RabbitAnimalType.TunableFactory(),
       hen=HenAnimalType.TunableFactory(),
       chick=ChickAnimalType.TunableFactory(),
       rooster=RoosterAnimalType.TunableFactory(),
       cow=CowAnimalType.TunableFactory(),
       llama=LlamaAnimalType.TunableFactory()), 
     'save_home_slot_for_gallery':OptionalTunable(description='\n            If checked and animal has an assigned home, the animal will save a\n            tuned slot on that home when uploaded to the gallery. Upon download, \n            it will be parented to that slot and re-assigned.\n            \n            This is to keep animals and assignments persisted from the gallery, \n            but is not necessary if the animal can be safely reset. It can also\n            be used to reslot animals during regular save/load. Please ensure \n            that the chosen slot type cannot have items in it other than the \n            animal you expect, to prevent collision.\n            ',
       tunable=TunableTuple(home_slot=SlotType.TunableReference(description='\n                    Will parent animal under first available slot of this slot \n                    type on download.\n                    '),
       reset_to_home_slot_tests=OptionalTunable(description='\n                    If the animal passes these tuned tests, it will also be \n                    reset to the home slot of its assigned home whenever it is \n                    reset or loaded from a save/travel.\n    \n                    If this is disabled or the animal is not assigned, the animal will \n                    only be reset on gallery upload.\n                    ',
       tunable=(TunableTestSet()),
       disabled_name='do_not_slot_on_reset'))), 
     'actions_on_destroy':TunableTuple(description='\n            A list of actions to run when this animal dies in the world.\n            Actor resolves to the animal.\n            ',
       loots=TunableList(description='\n                A list of pre-defined loot actions to run when this animal dies\n                in the world. If you need to add per-participant tuning, you \n                can enable action_targets_override to set Object as each \n                participant.\n                \n                e.g. if I wanted to test each Sim in the active household \n                for positive rel with the animal before setting a state, \n                I would enable action_targets_override on ActiveHousehold, and\n                add an ObjectRelationshipTest to this loot -- with Object \n                referring to one Sim in the household, and Actor referring to \n                the animal. The action would then run the loot for each \n                individual Sim.\n                ',
       tunable=AnimalDeathLootActions.TunableReference(pack_safe=True)),
       death_notification_for_active_household=OptionalTunable(description='\n                If enabled, this will display a death notification if a member\n                of the active household had a relationship with this animal.\n                ',
       tunable=(UiDialogNotification.TunableFactory())),
       action_targets_override=OptionalTunable(description='\n                If disabled, the actions will be executed once, where all \n                participants will be retrieved from the owner.\n                \n                If enabled, this loot is executed once for each of the \n                generated objects. The Actor participant still refers to the \n                owning animal, but the Object participant will correspond to \n                this object.\n                ',
       tunable=TunableObjectGeneratorVariant(participant_default=(ParticipantType.ObjectRelationshipsComponent)))), 
     'find_home_states':TunableList(description='\n            Animals that change to these states will attempt to find a home to be assigned to.\n            If the animal is already assigned to a home, nothing will happen.\n            ',
       tunable=ObjectStateValue.TunableReference())}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._reset_home_id = None

    def save_animal_assignment_data(self, msg, saved_slots):
        if self.save_home_slot_for_gallery is None:
            return False
        parent_slot = self.save_home_slot_for_gallery.home_slot
        animal_service = services.animal_service()
        home_obj = animal_service.get_animal_home_obj(self.owner)
        if home_obj is None:
            return False
        slot_hash_override = home_obj.animalhome_component.get_free_slot_for_save(parent_slot, saved_slots)
        if slot_hash_override is None:
            logger.error("The animal's home {} does not have a slot of the expected kind {}.", home_obj, parent_slot)
            return False
        msg.parent_id = home_obj.id
        msg.slot_hash = slot_hash_override
        return True

    def _slot_animal_into_home(self, home):
        if home is None:
            return
        slot_types = {self.save_home_slot_for_gallery.home_slot}
        old_parent_slot = self.owner.parent_slot
        if old_parent_slot is not None:
            if old_parent_slot.slot_types == slot_types:
                return
        for runtime_slot in home.get_runtime_slots_gen(slot_types=slot_types):
            if runtime_slot.is_valid_for_placement(obj=(self.owner)):
                runtime_slot.add_child(self.owner)
                return

    def save(self, persistence_master_message):
        reset_slot = self.save_home_slot_for_gallery
        if reset_slot is None or reset_slot.reset_to_home_slot_tests is None:
            return
        else:
            home = services.animal_service().get_animal_home_obj(self.owner)
            if home is None:
                return
            resolver = SingleObjectResolver(self.owner)
            return reset_slot.reset_to_home_slot_tests.run_tests(resolver) or None
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.AnimalObjectComponent
        component_data = persistable_data.Extensions[protocols.PersistableAnimalObjectComponent.persistable_data]
        component_data.assigned_home_id = home.id
        persistence_master_message.data.extend([persistable_data])

    def load(self, persistable_data):
        reset_slot = self.save_home_slot_for_gallery
        if reset_slot is None or reset_slot.reset_to_home_slot_tests is None:
            return
        component_data = persistable_data.Extensions[protocols.PersistableAnimalObjectComponent.persistable_data]
        self._reset_home_id = component_data.assigned_home_id

    def on_finalize_load(self):
        if self._reset_home_id is None:
            return
        home = services.object_manager().get(self._reset_home_id)
        self._slot_animal_into_home(home)

    def post_component_reset(self):
        reset_slot = self.save_home_slot_for_gallery
        if reset_slot is None or reset_slot.reset_to_home_slot_tests is None:
            return
        else:
            resolver = SingleObjectResolver(self.owner)
            return reset_slot.reset_to_home_slot_tests.run_tests(resolver) or None
        home = services.animal_service().get_animal_home_obj(self.owner)
        self._slot_animal_into_home(home)

    @classproperty
    def required_packs(cls):
        return (
         Pack.EP11,)

    @ComponentField(op=SetActorType, priority=(Field.Priority.HIGH))
    def actor_type(self):
        return ActorType.Creature

    @ComponentField(op=SetCreatureType)
    def creature_type(self):
        return self.animal_type_tuning.creature_type

    def _setup(self):
        self.animal_type_tuning.setup(self.owner)

    def on_object_replaced(self, new_object, destroy_original_obj):
        animal_service = services.animal_service()
        home_obj = animal_service.get_animal_home_obj(self.owner)
        if destroy_original_obj:
            animal_service.assign_animal(self.owner.id, None)
        animal_service.assign_animal(new_object.id, home_obj)

    def on_add(self, *_, **__):
        self.owner.add_ui_metadata('creature_type', self.creature_type)
        zone = services.current_zone()
        animal_service = services.animal_service()
        if not zone.is_zone_loading:
            if not zone.is_in_build_buy:
                self._setup()
            if animal_service is not None:
                animal_service.update_animal_aging(self.owner)
            send_animal_added_telemetry(self.owner)
        if animal_service is not None:
            animal_service.on_animal_added(self.owner.id)

    def on_remove(self, *_, **__):
        zone = services.current_zone()
        if zone.is_zone_shutting_down or self.owner.item_location == ItemLocation.HOUSEHOLD_INVENTORY:
            return
        animal_service = services.animal_service()
        if animal_service is not None:
            animal_service.on_animal_destroyed(self.owner.id)
        if not services.current_zone().is_in_build_buy:
            if self.actions_on_destroy:
                self._run_destruction_actions()

    def _move_to_spawn_point(self, spawner_tags):
        spawn_point = services.current_zone().get_spawn_point(lot_id=(services.active_lot_id()), sim_spawner_tags=spawner_tags)
        if spawn_point is not None:
            translation, orientation = spawn_point.next_spawn_spot()
            self.owner.move_to(translation=translation, orientation=orientation,
              routing_surface=(spawn_point.routing_surface))

    def on_state_changed(self, state, old_value, new_value, from_init):
        animal_tuning = self.animal_type_tuning
        if new_value is animal_tuning.move_to_spawn_point_state_value:
            self._move_to_spawn_point(animal_tuning.move_to_spawn_point_tags)
        if new_value in self.find_home_states:
            if self.owner.id is not 0:
                animal_service = services.animal_service()
                home_obj = animal_service.get_animal_home_obj(self.owner)
                if home_obj is None:
                    assignable_home_obj = animal_service.find_home_obj_with_vacancy(self.owner)
                    if assignable_home_obj is not None:
                        animal_service.assign_animal(self.owner.id, assignable_home_obj)

    def _run_destruction_actions(self):
        resolver = SingleObjectResolver(self.owner)
        loots = []
        if self.actions_on_destroy.action_targets_override is None:
            for loot_list in self.actions_on_destroy.loots:
                loots.append(LootOperationList(resolver, loot_list.loot_actions))

        else:
            for obj in self.actions_on_destroy.action_targets_override.get_objects(resolver):
                resolver = DoubleObjectResolver(self.owner, obj)
                for loot_list in self.actions_on_destroy.loots:
                    loots.append(LootOperationList(resolver, loot_list.loot_actions))

        for loot in loots:
            loot.apply_operations()

        if self.actions_on_destroy.death_notification_for_active_household:
            active_household = services.active_household()
            if active_household is not None:
                sim_infos = tuple(active_household.sim_info_gen())
                for sim_info in sim_infos:
                    if self.owner.objectrelationship_component.has_relationship(sim_info.id):
                        notification = self.actions_on_destroy.death_notification_for_active_household(sim_info, resolver=resolver)
                        notification.show_dialog()
                        break