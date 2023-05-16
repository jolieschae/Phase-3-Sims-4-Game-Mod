# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\collection_interactions.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 17180 bytes
from build_buy import ObjectOriginLocation
from distributor.shared_messages import IconInfoData
from interactions.aop import AffordanceObjectPair
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from interactions.base.picker_interaction import ObjectPickerInteraction
from interactions.base.picker_strategy import StatePickerEnumerationStrategy
from objects.collection_manager import CollectionIdentifier, ObjectCollectionData
from objects.components.state import ObjectState, ObjectStateValue
from objects.system import create_object
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableTuple, TunableList
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from singletons import DEFAULT
import build_buy, services, sims4
from ui.ui_dialog import ButtonType
from ui.ui_dialog_picker import ObjectPickerRow
logger = sims4.log.Logger('CollectionInteractions')

class CollectionInteractionData:
    COLLECTION_COMBINING_TUNING = TunableMapping(description='\n        Mapping of collectible id, to states that we allow for collectible\n        combining.\n        ',
      key_type=TunableEnumEntry(description='\n            ID of the collectible that can be combined.\n            ',
      tunable_type=CollectionIdentifier,
      default=(CollectionIdentifier.Unindentified)),
      value_type=TunableTuple(description='\n            Possible states that can be combined on a collectible.\n            Mapping of state values that can be combined to get a new state\n            ',
      states_to_combine=TunableList(description='\n                Any states tuned here will be transfered from the combine \n                collectibles to the resulting object.\n                For example: Frogs will transfer their color and pattern \n                states.\n                ',
      tunable=ObjectState.TunableReference(description='\n                    State that can be inherited by the new collectible.\n                    ')),
      combination_mapping=TunableList(description='\n                Mapping of possible father-mother states to which new\n                state can they generate on the newly created collectible.\n                e.g.  If collectible A has green color state, and collectible\n                B has blue color states the resulting state can be a Green \n                color state.  This means the outcome of the interaction will\n                look for a collectible that has this resulting state value.\n                ',
      tunable=TunableTuple(description='\n                    State combinations to create a new state on the \n                    result collectible.\n                    ',
      father_state=(ObjectStateValue.TunableReference()),
      mother_state=(ObjectStateValue.TunableReference()),
      resulting_state=(ObjectStateValue.TunableReference())))))


class CollectionPickerMixin:
    INSTANCE_TUNABLES = {'collection_type': TunableEnumEntry(description='\n            ID of collectible that can be selected.\n            ',
                          tunable_type=CollectionIdentifier,
                          default=(CollectionIdentifier.Unindentified),
                          tuning_group=(GroupNames.PICKERTUNING))}

    @flexmethod
    def _get_objects_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        sim = context.sim
        household = sim.household
        if household is None:
            return
        collection_tracker = household.collection_tracker
        definition_manager = services.definition_manager()
        for definition_id, collection_data in collection_tracker.collection_data.items():
            if collection_data.collection_id == inst_or_cls.collection_type:
                definition = definition_manager.get(definition_id)
                if definition is not None:
                    yield definition


class StockFishFromCollectionPickerInteraction(CollectionPickerMixin, ObjectPickerInteraction):

    @flexmethod
    def _get_objects_gen(cls, inst, target, context, **kwargs):
        if target is None:
            return
        else:
            fishing_location_component = target.fishing_location_component
            if fishing_location_component is None:
                logger.error('Target {} of StockFishFromCollectionPickerInteraction has no fishing location component. Please check tuning.', target)
                return
            fishing_location_component.can_modify_fishing_data or logger.error("Target {} of StockFishFromCollectionPickerInteraction has 'can modify fishing data' disabled. Please check tuning.", target)
            return
        fish_data = list(target.fishing_location_component.fishing_data.get_possible_fish_gen())
        stocked_fish = [fish_data.fish for fish_data in fish_data]
        yield from stocked_fish
        for fish in (super()._get_objects_gen)(target, context, **kwargs):
            if fish not in stocked_fish:
                yield fish

    @flexmethod
    def create_row(cls, inst, row_obj, context=DEFAULT, target=DEFAULT):
        is_selected = row_obj in [possible_fish.fish for possible_fish in target.fishing_location_component.fishing_data.get_possible_fish_gen()]
        icon_info = IconInfoData(obj_def_id=(row_obj.id), obj_geo_hash=(row_obj.thumbnail_geo_state_hash),
          obj_material_hash=(row_obj.material_variant))
        row_tooltip = lambda *_: LocalizationHelperTuning.get_object_name(row_obj)
        row = ObjectPickerRow(object_id=(row_obj.id), def_id=(row_obj.id),
          icon_info=icon_info,
          tag=row_obj,
          is_selected=is_selected,
          name=(LocalizationHelperTuning.get_object_name(row_obj)),
          row_tooltip=row_tooltip)
        return row

    def on_choice_selected(self, definition, **kwargs):
        if definition is None:
            return
        self.target.fishing_location_component.fishing_data.add_possible_fish((definition,))

    def on_multi_choice_selected(self, definitions, **kwargs):
        definitions = [definition for definition in definitions if definition is not None]
        if not definitions:
            return
        self.target.fishing_location_component.fishing_data.add_possible_fish(definitions)

    def _remove_fish_from_target(self, deselected_fish):
        if not deselected_fish:
            return
        self.target.fishing_location_component.fishing_data.remove_possible_fish(deselected_fish)

    def _on_picker_selected(self, dialog):
        if dialog.response is None or dialog.response != ButtonType.DIALOG_RESPONSE_OK:
            return
        selected_rows = dialog.get_result_rows()
        deselected_rows = [row for row in dialog.picker_rows if row not in selected_rows]
        deselected_definitions = [row.tag for row in deselected_rows]
        self._remove_fish_from_target(deselected_definitions)
        if dialog.multi_select:
            tag_objs = dialog.get_result_tags()
            self.on_multi_choice_selected(tag_objs)
        else:
            tag_obj = dialog.get_single_result_tag()
            self.on_choice_selected(tag_obj)


lock_instance_tunables(StockFishFromCollectionPickerInteraction, collection_type=(CollectionIdentifier.Fish),
  continuation=None)

class CombineCollectiblesPickerInteraction(ObjectPickerInteraction):

    @flexmethod
    def _get_objects_gen(cls, inst, target, context, **kwargs):
        interaction_col_id, _, _ = ObjectCollectionData.get_collection_info_by_definition(target.definition.id)
        if inst:
            inst._combine_data = CollectionInteractionData.COLLECTION_COMBINING_TUNING.get(interaction_col_id)
            inst._collectible_data = set(ObjectCollectionData.get_collection_data(interaction_col_id).object_list)
        for collectible in context.sim.inventory_component:
            if collectible.id == target.id:
                if collectible.stack_count() == 1:
                    continue
            if collectible.collectable_component:
                collectible_id, _, _ = ObjectCollectionData.get_collection_info_by_definition(collectible.definition.id)
                if collectible_id == interaction_col_id:
                    yield collectible

    def on_choice_selected(self, choice_tag, **kwargs):
        mother = choice_tag
        if mother is None:
            return
        father = self.target
        transferable_states = {}
        for state in self._combine_data.states_to_combine:
            mother_state = mother.get_state(state)
            father_state = father.get_state(state)
            transferable_states[state] = [mother_state, father_state]
            for combine_data in self._combine_data.combination_mapping:
                if combine_data.father_state == father_state and combine_data.mother_state == mother_state:
                    transferable_states[state].append(combine_data.resulting_state)

        if not transferable_states:
            logger.error('CombineCollectiblesPickerInteraction: {} and {} collectibles have no transferable states', mother, father, owner='camilogarcia')
            return
        states_to_transfer = []
        for states in transferable_states.values():
            states_to_transfer.append(sims4.random.random.choice(states))

        target_match = len(states_to_transfer)
        possible_outcomes = []
        for collectable in self._collectible_data:
            match = 0
            for target_states in collectable.collectable_item.cls._components.state._tuned_values.states:
                if target_states.default_value in states_to_transfer:
                    match += 1

            if match == target_match:
                possible_outcomes.append(collectable.collectable_item)

        if not possible_outcomes:
            logger.error('CombineCollectiblesPickerInteraction: No possible result when combining  {} and {}', mother, father, owner='camilogarcia')
            return
        definition_to_create = sims4.random.random.choice(possible_outcomes)
        obj = create_object(definition_to_create)
        if obj is None:
            logger.error('CombineCollectiblesPickerInteraction: Failed to create object when combining  {} and {}', mother, father, owner='camilogarcia')
            return
        obj.update_ownership(self.sim.sim_info)
        self.sim.inventory_component.player_try_add_object(obj) or obj.set_household_owner_id(services.active_household_id())
        if not build_buy.move_object_to_household_inventory(obj, object_location_type=(ObjectOriginLocation.SIM_INVENTORY)):
            logger.error('CombineCollectiblesPickerInteraction: Failed to add object {} to household inventory.', obj, owner='rmccord')
        self._push_continuation(obj)

    def __init__(self, *args, **kwargs):
        self._combine_data = None
        self._collectible_data = None
        choice_enumeration_strategy = StatePickerEnumerationStrategy()
        (super().__init__)(args, choice_enumeration_strategy=choice_enumeration_strategy, **kwargs)


class AwardCollectiblesInteraction(ImmediateSuperInteraction):

    def _run_interaction_gen(self, timeline):
        self._give_objects_for_collection_type()
        return True
        if False:
            yield None

    def _object_definitions_gen(self):
        collection_type = self.interaction_parameters.get('collection_type')
        if collection_type is None:
            return
        collection_data = ObjectCollectionData.get_collection_data(collection_type)
        if collection_data is None:
            return
        yield from (i.collectable_item for i in collection_data.object_list)
        yield from (i.collectable_item for i in collection_data.bonus_object_list)
        if False:
            yield None

    @flexmethod
    def _get_name(cls, inst, target=DEFAULT, context=DEFAULT, collection_type=None, **interaction_parameters):
        if collection_type is None:
            return
        collection_data = ObjectCollectionData.get_collection_data(collection_type)
        return cls.display_name(collection_data.collection_name)

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        for collection_type in CollectionIdentifier.values:
            if CollectionIdentifier.Unindentified == collection_type:
                continue
            if ObjectCollectionData.get_collection_data(collection_type) is None:
                continue
            yield AffordanceObjectPair(cls, target, cls, None, collection_type=collection_type, **kwargs)

    def _give_objects_for_collection_type(self, **kwargs):
        for obj_def in self._object_definitions_gen():
            obj = create_object(obj_def)
            if obj is None:
                logger.error('AwardCollectiblesInteraction: Failed to create object {}', obj_def, owner='jdimailig')
                continue
            obj.update_ownership(self.sim.sim_info)
            if not self.sim.inventory_component.player_try_add_object(obj):
                obj.set_household_owner_id(services.active_household_id())
                build_buy.move_object_to_household_inventory(obj, object_location_type=(ObjectOriginLocation.SIM_INVENTORY)) or logger.error('AwardCollectiblesInteraction: Failed to add object {} to household inventory.', obj, owner='jdimailig')