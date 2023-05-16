# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\picker\object_fashion_marketplace_picker_interaction.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 12450 bytes
import objects, random, services, sims4, tag
from crafting.crafting_interactions import create_craftable
from crafting.recipe_helpers import get_recipes_matching_tag
from date_and_time import TimeSpan
from distributor.shared_messages import IconInfoData
from interactions.base.picker_interaction import PurchasePickerInteraction
from interactions.utils.tunable_icon import TunableIcon
from objects.components.object_fashion_marketplace_component import ObjectFashionMarketplaceComponent
from objects.components.state import ObjectStateValue
from protocolbuffers import Consts_pb2
from sims.sim_info_types import Gender
from sims.sim_spawner import SimSpawner
from sims4.localization import TunableLocalizedStringFactory
from sims4.random import weighted_random_item
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableRange, TunableList, TunableTuple, Tunable, TunableSet, TunableEnumWithFilter
from sims4.tuning.tunable_base import GroupNames
from tag import TunableTag
from tunable_time import TunableTimeSpan
logger = sims4.log.Logger('ObjectFashionMarketplacePickerInteraction', default_owner='anchavez')

class ObjectFashionMarketplacePickerInteraction(PurchasePickerInteraction):
    OBJECT_FASHION_MARKETPLACE_PURCHASED_STATE_VALUE = ObjectStateValue.TunablePackSafeReference(description='\n        The state value that will be applied to objects after they have\n        been purchased to indicate they have been purchased.\n        ')
    REFRESH_TIME_TEXT = TunableLocalizedStringFactory(description='\n        Text indicating how much time is left until the picker refreshes. Shown\n        in picker. Receives a single time token.\n        ')
    INSTANCE_TUNABLES = {'fashion_tags':TunableSet(description='\n            Tags that determine what recipes will provide objects that appear\n            in this picker.\n            ',
       tunable=TunableEnumWithFilter(tunable_type=(tag.Tag),
       filter_prefixes=[
      'recipe_fashion'],
       default=(tag.Tag.INVALID),
       invalid_enums=(
      tag.Tag.INVALID,)),
       minlength=1,
       tuning_group=GroupNames.PICKERTUNING), 
     'refresh_period':TunableTimeSpan(description="\n            This picker's items will refresh every refresh_period time. They\n            will also refresh if the game is reloaded.\n            ",
       default_hours=1,
       tuning_group=GroupNames.PICKERTUNING), 
     'items_available':TunableRange(description='\n            The number of items available in the picker.\n            ',
       tunable_type=int,
       minimum=1,
       default=1,
       tuning_group=GroupNames.PICKERTUNING), 
     'quality_weights':TunableList(description='\n            Weights and qualities for determining the quality of objects in\n            the picker.\n            ',
       tunable=TunableTuple(state_value=ObjectStateValue.TunableReference(description='\n                    The quality state value.\n                    '),
       weight=Tunable(description='\n                    A weight that will make this quality more likely to appear.\n                    ',
       tunable_type=float,
       default=1)),
       tuning_group=GroupNames.PICKERTUNING), 
     'purchased_tag':TunableTag(filter_prefixes=[
      'inventory_fashion']), 
     'sold_icon':TunableIcon(description='\n            An icon override for picker rows that display sold items.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'sold_description_text':TunableLocalizedStringFactory(description='\n            Description text for picker rows that display sold items.\n            ',
       tuning_group=GroupNames.PICKERTUNING), 
     'default_description_text':TunableLocalizedStringFactory(description='\n            Description text for picker rows that are available. Tokens:\n            0: String, the username of the fictional seller.\n            ',
       tuning_group=GroupNames.PICKERTUNING)}
    purchased_recipes = []
    last_items_period_id = -1
    current_item_data = {}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._populated_objects = []

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        return True

    def _populate_items(self, purchase_picker_data):
        period_id = int(services.time_service().sim_now.absolute_ticks() / self.refresh_period().in_ticks())
        if period_id != ObjectFashionMarketplacePickerInteraction.last_items_period_id:
            ObjectFashionMarketplacePickerInteraction.last_items_period_id = period_id
            ObjectFashionMarketplacePickerInteraction.purchased_recipes = []
            ObjectFashionMarketplacePickerInteraction.current_item_data = {}
            tagged_recipes = set()
            for tag in self.fashion_tags:
                tagged_recipes.update(get_recipes_matching_tag(tag))

            rand = random.Random()
            selected_recipes = rand.sample(tagged_recipes, self.items_available)
            for recipe in selected_recipes:
                definition = recipe.final_product.definition
                if definition is None:
                    logger.error('Recipe {} with no definition cannot be used in PurchaseRecipePickerInteraction', recipe)
                    continue
                quality_weight_pairs = [(quality_weight.weight, quality_weight.state_value) for quality_weight in self.quality_weights]
                quality_state_value = weighted_random_item(quality_weight_pairs)
                obj = create_craftable(recipe, None, quality=quality_state_value, seeded_random=(self._get_seeded_random()))
                price = ObjectFashionMarketplaceComponent.get_suggested_marketplace_sale_price(obj)
                fashion_trend = ObjectFashionMarketplaceComponent.get_prevalent_trend_for_listing(obj)
                obj.destroy(cause='Destroy temporary object in PurchaseRecipePickerInteraction')
                ObjectFashionMarketplacePickerInteraction.current_item_data[definition] = (
                 recipe, quality_state_value, price, fashion_trend)

        for definition, (recipe, quality, price, fashion_trend) in ObjectFashionMarketplacePickerInteraction.current_item_data.items():
            purchase_picker_data.add_definition_to_purchase(definition, custom_price=price, fashion_trend=fashion_trend)

    def _supports_pick_response(self):
        return True

    def _on_picker_selected(self, dialog):
        super()._on_picker_selected(dialog)
        for obj in self._populated_objects:
            obj.destroy(cause='Destroy temporary object in PurchaseRecipePickerInteraction')

        definition_ids, _ = dialog.get_result_definitions_and_counts()
        for definition_id in definition_ids:
            definition = services.definition_manager().get(definition_id)
            ObjectFashionMarketplacePickerInteraction.purchased_recipes.append(definition)
            recipe, quality, price, fashion_trend = ObjectFashionMarketplacePickerInteraction.current_item_data[definition]
            if not services.active_household().funds.try_remove(price, Consts_pb2.TELEMETRY_OBJECT_BUY):
                logger.error('Could not complete object marketplace purchase of {} due to insufficient funds', recipe)
                continue
            obj = create_craftable(recipe, None, inventory_owner=(self.sim), quality=quality, owning_household_id_override=(self.sim.household_id), place_in_inventory=True, seeded_random=(self._get_seeded_random()))
            obj.append_tags((frozenset([self.purchased_tag])), persist=True)
            if self.OBJECT_FASHION_MARKETPLACE_PURCHASED_STATE_VALUE is not None:
                obj.set_state(self.OBJECT_FASHION_MARKETPLACE_PURCHASED_STATE_VALUE.state, self.OBJECT_FASHION_MARKETPLACE_PURCHASED_STATE_VALUE)

    def _get_enabled_option(self, item):
        if item in ObjectFashionMarketplacePickerInteraction.purchased_recipes:
            return False
        return True

    def _get_right_custom_text(self):
        refresh_period = self.refresh_period().in_ticks()
        now = services.time_service().sim_now.absolute_ticks()
        next_period_id = int(now / refresh_period) + 1
        next_period_time = next_period_id * refresh_period
        refresh_time = next_period_time - now
        return self.REFRESH_TIME_TEXT(TimeSpan(refresh_time))

    def _get_availability_option(self, item):
        if item in ObjectFashionMarketplacePickerInteraction.purchased_recipes:
            return 0
        return 1

    def _get_icon_info_data_override_option(self, item):
        if item in ObjectFashionMarketplacePickerInteraction.purchased_recipes:
            return IconInfoData(icon_resource=(self.sold_icon))
        recipe, quality, price, fashion_trend = ObjectFashionMarketplacePickerInteraction.current_item_data[item]
        obj = create_craftable(recipe, None, quality=quality, seeded_random=(self._get_seeded_random()))
        self._populated_objects.append(obj)
        return obj.get_icon_info_data()

    def _get_description_override_option(self, item):
        if item in ObjectFashionMarketplacePickerInteraction.purchased_recipes:
            return self.sold_description_text()
        buyer_name = SimSpawner.get_random_first_name((Gender.MALE), sim_name_type_override=(ObjectFashionMarketplaceComponent.BUYER_NAME_TYPE))
        return self.default_description_text(buyer_name)

    def _get_seeded_random(self):
        seeded_random = random.Random()
        seeded_random.seed(ObjectFashionMarketplacePickerInteraction.last_items_period_id)
        return seeded_random


lock_instance_tunables(ObjectFashionMarketplacePickerInteraction, purchase_list_option=None)