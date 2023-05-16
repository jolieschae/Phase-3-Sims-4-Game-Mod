# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\gardening\gardening_component_crop_plant.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 15478 bytes
import build_buy, random, services
from objects.components.state import ObjectStateValue, StateComponent
from objects.components.state_references import TunableStateValueReference
from objects.gardening.gardening_component_base_plant import _GardeningBasePlantComponent
from objects.components import types, componentmethod_with_fallback
from objects.gardening.gardening_tuning import GardeningTuning
from protocolbuffers import Consts_pb2, SimObjectAttributes_pb2 as protocols
import objects.components.types, sims4.log
from sims.funds import FundsSource, get_funds_for_source
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, TunableInterval
from singletons import UNSET
logger = sims4.log.Logger('Gardening', default_owner='miking')

class GardeningCropPlantComponent(_GardeningBasePlantComponent, component_name=objects.components.types.GARDENING_COMPONENT, persistence_key=protocols.PersistenceMaster.PersistableData.GardeningComponent):
    FACTORY_TUNABLES = {'crop_yield_results':TunableMapping(description='\n            Mapping of crop_yield_state (commodity-backed state which is used to select a growth result)\n            to plant_growth_result.\n            ',
       key_type=TunableStateValueReference(description='\n                Plant object state being mapped.\n                ',
       class_restrictions=ObjectStateValue),
       value_type=TunableTuple(description='\n                Plant growth result tuning.\n                ',
       harvestable_object=TunableReference(description='\n                                                    Object(s) to be spawned when the plant is harvested.\n                                                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.OBJECT))),
       number_of_harvestables=sims4.tuning.tunable.Tunable(description='\n                    How many harvestable objects to spawn when the plant is harvested.\n                    ',
       tunable_type=int,
       default=1),
       weight_range=TunableInterval(description='\n                    Base crop weight range for this result.\n                    ',
       tunable_type=float,
       default_lower=0.0,
       default_upper=10.0,
       minimum=0.0),
       weight_sigma=sims4.tuning.tunable.Tunable(description='\n                    Crop weight standard deviation for this result.\n                    ',
       tunable_type=float,
       default=1.0))), 
     'plant_quality_commodity':TunableReference(description='\n            A commodity used to track the quality of the harvestables on the plant.\n            Applied directly to harvestables when they are harvested.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'plant_weight_commodity':TunableReference(description='\n            A commodity used to track the weight of the harvestables on the plant.\n            Used as a percentage/multiplier to determine the base weight of the harvested fruit,\n            between the tuned min and max weight of the growth result.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'harvestable_weight_commodity':TunableReference(description='\n            A commodity used to track the weight of the harvestables.\n            Applied to harvestables when they are harvested.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._crop_weights = None
        self._sell_value = None

    def _save(self, persistable_data):
        gardening_component_data = persistable_data.Extensions[protocols.PersistableGardeningComponent.persistable_data]
        gardening_component_data.ClearField('crop_weights')
        if self._crop_weights:
            gardening_component_data.crop_weights.extend(self._crop_weights)
        super()._save(persistable_data)

    def load(self, persistable_data):
        gardening_component_data = persistable_data.Extensions[protocols.PersistableGardeningComponent.persistable_data]
        if gardening_component_data.crop_weights:
            self._crop_weights = [crop_weight for crop_weight in gardening_component_data.crop_weights]
        else:
            self._crop_weights = None
        super().load(persistable_data)

    @componentmethod_with_fallback((lambda: None))
    def get_notebook_information(self, reference_notebook_entry, notebook_sub_entries):
        return ()

    def supports_harvest(self):
        return True

    def get_crop_weights(self):
        yield_result = self._determine_crop_yield_result()
        if yield_result is None:
            logger.error('GardeningCropPlantComponent.get_crop_weights() called but no yield_result was chosen.')
            return
        if self._crop_weights is not None:
            if len(self._crop_weights) != yield_result.number_of_harvestables:
                logger.error('GardeningCropPlantComponent.get_crop_weights() number of weights mismatch: {} != {}.', len(self._crop_weights), yield_result.number_of_harvestables)
                self._crop_weights = None
        if self._crop_weights is None:
            plant_object = self.owner
            weight_commodity_value = plant_object.get_stat_value(self.plant_weight_commodity)
            weight_min = yield_result.weight_range.lower_bound
            weight_max = yield_result.weight_range.upper_bound
            weight_sigma = yield_result.weight_sigma
            base_weight = (weight_max - weight_min) * weight_commodity_value + weight_min
            logger.info('get_crop_weights(): Plant {} creating {} crops of object type {}, weight commodity = {}. base weight = {}.', plant_object, yield_result.number_of_harvestables, yield_result.harvestable_object, weight_commodity_value, base_weight)
            self._crop_weights = []
            for _ in range(yield_result.number_of_harvestables):
                crop_weight = random.normalvariate(base_weight, weight_sigma)
                logger.info('crop weight = {}.', crop_weight)
                self._crop_weights.append(crop_weight)

        return self._crop_weights

    def on_harvest(self, sim, sell_immediately):
        plant_object = self.owner
        yield_result = self._determine_crop_yield_result()
        crop_quality_value = plant_object.get_stat_value(self.plant_quality_commodity)
        weights = self.get_crop_weights()
        if weights is not None:
            for crop_weight in weights:
                crop_object = self._create_crop_object(sim, yield_result.harvestable_object, crop_weight, crop_quality_value)
                if crop_object is not None:
                    if sell_immediately:
                        self._sell_crop_object(sim, crop_object)
                    else:
                        self._add_crop_object_to_inventory(sim, crop_object)

        self._crop_weights = None
        self._sell_value = None

    def get_simoleon_delta(self):
        if self._sell_value is None:
            self._sell_value = 0
            weights = self.get_crop_weights()
            if weights is not None:
                plant_object = self.owner
                yield_result = self._determine_crop_yield_result()
                if yield_result is not None:
                    crop_cls = yield_result.harvestable_object.cls
                    gardening_component = crop_cls.tuned_components.gardening
                    base_value = yield_result.harvestable_object.price
                    weight_multiplier = gardening_component.weight_money_multiplier
                    quality_multiplier = 1.0
                    if GardeningTuning.CROP_FRUIT_QUALITY_STATE is not None:
                        quality_value = plant_object.get_stat_value(self.plant_quality_commodity)
                        quality_state = StateComponent.get_state_from_stat_value(GardeningTuning.CROP_FRUIT_QUALITY_STATE, quality_value)
                        if 'change_value' in quality_state.new_client_state.ops:
                            value_change_op = quality_state.new_client_state.ops['change_value']
                            if value_change_op is not UNSET:
                                state_component = crop_cls.tuned_components.state
                                quality_multiplier += value_change_op(state_component).get_value_delta(value_change_op._tuned_values.change_percentage)
                    for crop_weight in weights:
                        crop_base_value = base_value + int(crop_weight * weight_multiplier)
                        crop_value = round(crop_base_value * quality_multiplier)
                        self._sell_value += crop_value

        return (
         self._sell_value, FundsSource.HOUSEHOLD)

    def _determine_crop_yield_result(self):
        first_state_value = next(iter(self.crop_yield_results))
        state = first_state_value.state if first_state_value is not None else None
        if state is None:
            logger.error('_get_yield_result(): no state selected. Check crop_yield_results tuning on the plant object {}.', self.owner)
            return
        plant_object = self.owner
        if not plant_object.has_state(state):
            logger.error('_get_yield_result(): plant object does not have the required state {}.', state)
            return
        state_value = plant_object.get_state(state)
        return self.crop_yield_results[state_value]

    def _create_crop_object(self, sim, object_to_create, crop_weight, crop_quality_value):
        if not sim.is_selectable:
            return
        if object_to_create is None:
            logger.error('_create_crop_object(): object_to_create is None.')
            return
        created_object = objects.system.create_object(object_to_create)
        if created_object is None:
            logger.error('_create_crop_object(): failed to create object {}.', object_to_create)
            return
        created_object.set_stat_value(self.harvestable_weight_commodity, crop_weight)
        created_object.set_stat_value(self.plant_quality_commodity, crop_quality_value)
        crop_fruit_component = created_object.get_component(types.GARDENING_COMPONENT)
        crop_fruit_component.update_crop_cost(crop_weight)
        created_object.update_ownership(sim)
        return created_object

    @staticmethod
    def _add_crop_object_to_inventory(sim, crop_object):
        if sim.inventory_component.can_add(crop_object):
            sim.inventory_component.player_try_add_object(crop_object) or logger.error('_add_crop_object_to_inventory(): Failed to add object {} to sim inventory of sim {}.', crop_object, sim)
            crop_object.make_transient()
        else:
            if not build_buy.move_object_to_household_inventory(crop_object):
                logger.error('_add_crop_object_to_inventory(): Failed to add object {} to household inventory.', crop_object)
                crop_object.make_transient()

    @staticmethod
    def _sell_crop_object(sim, crop_object):
        sell_value = crop_object.current_value
        if sell_value:
            funds = get_funds_for_source((FundsSource.HOUSEHOLD), sim=sim)
            funds.add(sell_value, Consts_pb2.TELEMETRY_OBJECT_SELL, sim)
        crop_object.make_transient()