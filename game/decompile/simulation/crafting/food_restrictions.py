# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\food_restrictions.py
# Compiled at: 2021-02-23 18:14:34
# Size of source mod 2**32: 4421 bytes
import sims4
from crafting.food_restrictions_utils import FoodRestrictionUtils
from interactions.utils.loot_basic_op import BaseLootOperation
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.tuning.tunable import TunableReference, TunableVariant, TunableEnumEntry
from sims4.utils import classproperty
logger = sims4.log.Logger('Food Restrictions')

class FoodRestrictionTracker(SimInfoTracker):

    def __init__(self, sim_info):
        self._sim_info = sim_info
        self._food_restriction_ingredients = None

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    @property
    def food_restriction_ingredients(self):
        return self._food_restriction_ingredients

    def add_food_restriction(self, ingredient):
        if ingredient is None:
            return
        if self._food_restriction_ingredients is None:
            self._food_restriction_ingredients = set()
        self._food_restriction_ingredients.add(ingredient)

    def remove_food_restriction(self, ingredient):
        if ingredient is None:
            return
        if ingredient in self._food_restriction_ingredients:
            self._food_restriction_ingredients.remove(ingredient)
            if not self._food_restriction_ingredients:
                self._food_restriction_ingredients = None

    def clear_all_food_restrictions(self):
        self._food_restriction_ingredients = None

    def recipe_has_restriction(self, recipe):
        if recipe is None:
            return False
        else:
            return self._food_restriction_ingredients or False
        return any((ingredient in self._food_restriction_ingredients for ingredient in recipe.food_restriction_ingredients))


class FoodRestrictionOp(BaseLootOperation):
    ADD_FOOD_RESTRICTION = 1
    REMOVE_FOOD_RESTRICTION = 2
    CLEAR_ALL_FOOD_RESTRICTIONS = 3
    FACTORY_TUNABLES = {'food_restriction_ingredient':TunableEnumEntry(description="\n            The food restriction ingredients to add/remove to the sim's\n            list of food restrictions \n            ",
       tunable_type=FoodRestrictionUtils.FoodRestrictionEnum,
       default=FoodRestrictionUtils.FoodRestrictionEnum.INVALID), 
     'action':TunableVariant(description='\n            The action to apply.\n            ',
       locked_args={'add_food_restriction':ADD_FOOD_RESTRICTION, 
      'remove_food_restriction':REMOVE_FOOD_RESTRICTION, 
      'clear_food_restrictions':CLEAR_ALL_FOOD_RESTRICTIONS},
       default='add_food_restriction')}

    def __init__(self, food_restriction_ingredient, action, **kwargs):
        (super().__init__)(**kwargs)
        self._food_restriction_ingredient = food_restriction_ingredient
        self._action = action

    def _apply_to_subject_and_target(self, subject, target, resolver):
        tracker = subject.food_restriction_tracker
        if tracker is None:
            return
            if self._food_restriction_ingredient is not FoodRestrictionUtils.FoodRestrictionEnum.INVALID:
                if self._action == self.ADD_FOOD_RESTRICTION:
                    tracker.add_food_restriction(self._food_restriction_ingredient)
                elif self._action == self.REMOVE_FOOD_RESTRICTION:
                    tracker.remove_food_restriction(self._food_restriction_ingredient)
        elif self._action == self.CLEAR_ALL_FOOD_RESTRICTIONS:
            tracker.clear_all_food_restrictions()
        else:
            logger.error('Trying to add or remove ingredient with INVALID food restriction ingredient.')