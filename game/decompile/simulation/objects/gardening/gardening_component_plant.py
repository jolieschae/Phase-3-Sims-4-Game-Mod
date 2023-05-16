# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_plant.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 11750 bytes
from objects.gardening.gardening_component_base_plant import _GardeningBasePlantComponent
from protocolbuffers import SimObjectAttributes_pb2 as protocols
import random
from objects.components import types, componentmethod_with_fallback
from objects.components.spawner_component_enums import SpawnerType
from objects.gardening.gardening_tuning import GardeningTuning
from sims4.tuning.tunable import TunableReference, TunableSet
import objects.components.types, placement, services, sims4.log
from sims4.tuning.tunable_hash import TunableStringHash32
logger = sims4.log.Logger('Gardening', default_owner='shipark')

class GardeningPlantComponent(_GardeningBasePlantComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):
    FACTORY_TUNABLES = {'shoot_definition':TunableReference(description='\n            The object definition to use when creating Shoot objects for the\n            splicing system.\n            ',
       manager=services.definition_manager()), 
     'prohibited_vertical_plant_slots':TunableSet(description='\n            The list of slots that are prohibited from spawning fruit if the plant \n            is on the vertical garden.\n            ',
       tunable=TunableStringHash32(description='\n                The hashed name of the slot.\n                ',
       default='_ctnm_spawn_1'))}

    def on_add(self, *args, **kwargs):
        animal_service = services.animal_service()
        if animal_service is not None:
            animal_service.add_weed_eligible_plant(self.owner)
        return (super().on_add)(*args, **kwargs)

    def on_remove(self, *args, **kwargs):
        animal_service = services.animal_service()
        if animal_service is not None:
            animal_service.remove_weed_eligible_plant(self.owner)
        (super().on_remove)(*args, **kwargs)

    def on_finalize_load(self):
        super().on_finalize_load()
        self._refresh_fruit_states()

    def on_location_changed(self, old_location):
        super().on_location_changed(old_location)
        zone = services.current_zone()
        if not zone.is_zone_loading:
            self._refresh_prohibited_spawn_slots()

    def _refresh_prohibited_spawn_slots(self):
        plant = self.owner
        plant_parent = plant.parent
        fruits = tuple(self.owner.children)
        destroyed_fruit = False
        for fruit in fruits:
            gardening_component = fruit.get_component(types.GARDENING_COMPONENT)
            if gardening_component is None:
                continue
            if self.is_prohibited_spawn_slot(fruit.location.slot_hash, plant_parent):
                fruit.destroy()
                destroyed_fruit = True

        return destroyed_fruit or fruits or None
        empty_slot_count = 0
        for runtime_slot in plant.get_runtime_slots_gen():
            if runtime_slot.empty:
                self.is_prohibited_spawn_slot(runtime_slot.slot_name_hash, plant_parent) or empty_slot_count += 1

        plant.force_spawn_object(spawn_type=(SpawnerType.SLOT), ignore_firemeter=True,
          create_slot_obj_count=empty_slot_count)

    def _refresh_fruit_states(self):
        for fruit_state in GardeningTuning.FRUIT_STATES:
            if self.owner.has_state(fruit_state):
                fruit_state_value = self.owner.get_state(fruit_state)
                self._on_fruit_support_state_changed(fruit_state, None, fruit_state_value)

    def _on_fruit_fall_to_ground(self, fruit):
        plant = self.owner
        if fruit.parent is not plant:
            return False
        else:
            return plant.is_on_active_lot() or False
        starting_location = placement.create_starting_location(position=(plant.position),
          routing_surface=(plant.routing_surface))
        fgl_context = placement.create_fgl_context_for_object(starting_location, fruit, ignored_object_ids=(fruit.id,))
        position, orientation, _ = fgl_context.find_good_location()
        if position is None or orientation is None:
            return False
        fruit.move_to(parent=None, translation=position, orientation=orientation, routing_surface=(plant.routing_surface))
        owner = plant.get_household_owner_id()
        if owner is not None:
            fruit.set_household_owner_id(owner)
        decay_commodity = GardeningTuning.FRUIT_DECAY_COMMODITY
        fruit.set_stat_value(decay_commodity, GardeningTuning.FRUIT_DECAY_COMMODITY_DROPPED_VALUE)
        return True

    def _on_fruit_support_state_changed(self, state, old_value, new_value):
        if state not in GardeningTuning.FRUIT_STATES:
            return
        fruit_state_data = GardeningTuning.FRUIT_STATES[state]
        if new_value in fruit_state_data.states:
            return
        objs_to_destroy = []
        fruit_state_behavior = fruit_state_data.behavior
        for fruit in tuple(self.owner.children):
            gardening_component = fruit.get_component(types.GARDENING_COMPONENT)
            if gardening_component is None:
                continue
            elif fruit_state_behavior is not None:
                if random.random() < fruit_state_behavior:
                    if not gardening_component.is_on_tree:
                        continue
                    if self._on_fruit_fall_to_ground(fruit):
                        gardening_component.update_hovertip()
                        continue
            objs_to_destroy.append(fruit)

        if objs_to_destroy:
            services.get_reset_and_delete_service().trigger_batch_destroy(objs_to_destroy)

    def on_state_changed(self, state, old_value, new_value, from_init):
        self._on_fruit_support_state_changed(state, old_value, new_value)
        super().on_state_changed(state, old_value, new_value, from_init)

    def is_prohibited_spawn_slot(self, slot, plant_parent):
        if plant_parent is None or plant_parent.definition not in GardeningTuning.VERTICAL_GARDEN_OBJECTS:
            return False
        if slot in self.prohibited_vertical_plant_slots:
            return True
        return False

    def add_fruit(self, fruit, sprouted_from=False):
        gardening_component = fruit.get_component(types.GARDENING_COMPONENT)
        if sprouted_from:
            state = GardeningTuning.INHERITED_STATE
            state_value = fruit.get_state(state)
            self.owner.set_state(state, state_value)
        else:
            splicing_recipies = self.root_stock_gardening_tuning.splicing_recipies
            if gardening_component.root_stock.main_spawner in splicing_recipies:
                new_fruit = splicing_recipies[gardening_component.root_stock.main_spawner]
                self._add_spawner(new_fruit)
            elif gardening_component.is_shoot:
                self._add_spawner(gardening_component.root_stock.main_spawner)
            else:
                self._add_spawner(fruit.definition)
            self.update_hovertip()

    def create_shoot(self):
        root_stock = self._get_root_stock()
        if root_stock is None:
            return
        shoot = self.root_stock.create_spawned_object(self.owner, self.shoot_definition)
        gardening_component = shoot.get_component(types.GARDENING_COMPONENT)
        gardening_component.fruit_spawner_data = root_stock
        gardening_component._fruit_spawners.append(root_stock)
        gardening_component.update_hovertip()
        return shoot

    def _get_root_stock(self):
        if self.root_stock is None:
            for spawn_obj_def in self.owner.slot_spawner_definitions():
                self._add_spawner(spawn_obj_def[0])

        return self.root_stock

    def can_splice_with(self, shoot):
        gardening_component = shoot.get_component(types.GARDENING_COMPONENT)
        if gardening_component is not None:
            return gardening_component.is_shoot
        return False

    @componentmethod_with_fallback((lambda: None))
    def get_notebook_information(self, reference_notebook_entry, notebook_sub_entries):
        root_stock = self._get_root_stock()
        if root_stock is None:
            return ()
        fruit_definition = root_stock.main_spawner
        notebook_entry = reference_notebook_entry(fruit_definition.id)
        return (notebook_entry,)