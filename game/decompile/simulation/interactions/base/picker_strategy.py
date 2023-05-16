# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\base\picker_strategy.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9938 bytes
import random, services
from interactions.constraints import ANYWHERE
from postures.posture_graph import DistanceEstimator
from sims4.math import MAX_FLOAT
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory
import crafting, sims4.log
logger = sims4.log.Logger('Interactions')

class PickerEnumerationStrategy(HasTunableSingletonFactory, AutoFactoryInit):

    def __init__(self):
        self._choices = None

    def build_choice_list(self, si, **kwargs):
        raise NotImplementedError

    def find_best_choice(self, si):
        if self._choices is None:
            logger.error('Calling PickerEnumerationStrategy.find_best_choice() without first calling build_choice_list()', owner='rez')
            return
        return random.choice(self._choices)

    def get_choice_by_proximity(self, proximity_participant_type, routing_sim, si):
        posture_graph_service = services.posture_graph_service()
        proximity_participant = si.get_participant(proximity_participant_type)
        if proximity_participant is None:
            proximity_participant = si.sim
        choice = None
        min_distance = MAX_FLOAT
        distance_estimator = DistanceEstimator(posture_graph_service, routing_sim, si, ANYWHERE)
        for obj in self._choices:
            locations = obj.get_locations_for_posture(None)
            for location in locations:
                distance = distance_estimator.estimate_distance((proximity_participant.location, location))
                if distance < min_distance:
                    min_distance = distance
                    choice = obj

        return choice

    @classmethod
    def has_valid_choice(self, target, context, state=None):
        raise NotImplementedError

    @property
    def choices(self):
        return self._choices


class StatePickerEnumerationStrategy(PickerEnumerationStrategy):

    def build_choice_list(self, si, state, **kwargs):
        self._choices = [client_state for client_state in si.target.get_client_states(state) if client_state.show_in_picker if client_state.test_channel(si.target, si.context)]

    def find_best_choice(self, si):
        if not self._choices:
            logger.error('Calling PickerEnumerationStrategy.find_best_choice() without first calling build_choice_list()', owner='rez')
            return
        weights = []
        for client_state in self._choices:
            weight = client_state.calculate_autonomy_weight(si.sim)
            weights.append((weight, client_state))

        logger.assert_log(weights, 'Failed to find choice in autonomous recipe picker', owner='rez')
        choice = sims4.random.pop_weighted(weights)
        return choice

    @classmethod
    def has_valid_choice(cls, target, context, state=None):
        for client_state in target.get_client_states(state):
            if client_state.show_in_picker and client_state.test_channel(target, context):
                return True

        return False


class RecipePickerEnumerationStrategy(PickerEnumerationStrategy):

    def build_choice_list(self, si, candidate_ingredients=[], ingredient_cost_only=False, **kwargs):

        def _test_ingredient_cost_only_available(recipe, candidate_ingredients):
            return recipe.all_ingredients_available(candidate_ingredients, True)

        self._choices = [recipe for recipe in si.recipes if ingredient_cost_only if _test_ingredient_cost_only_available(recipe, candidate_ingredients)]

    def find_best_choice(self, si):
        if self._choices is None:
            logger.error('Calling PickerEnumerationStrategy.find_best_choice() without first calling build_choice_list()', owner='rez')
            return
        else:
            weights = []
            for recipe in self._choices:
                if recipe.all_ingredients_required:
                    continue
                result = crafting.crafting_process.CraftingProcess.recipe_test((si.target), (si.context), recipe, (si.sim), 0, build_error_list=False, from_autonomy=True, check_bucks_costs=False)
                if result:
                    weights.append((recipe.calculate_autonomy_weight(si.sim), recipe))

            weights or logger.error('Failed to find choice in autonomous recipe picker', owner='rez')
            return
        choice = sims4.random.pop_weighted(weights)
        return choice


class SimPickerEnumerationStrategy(PickerEnumerationStrategy):

    def build_choice_list(self, si, sim, test_function=None, **kwargs):
        self._choices = [filter_result for filter_result in (si._get_valid_sim_choices_gen)(si.target, si.context, test_function=test_function, **kwargs)]

    def find_best_choice(self, si):
        if si.order_by_proximity:
            choice = self.get_choice_by_proximity(si.order_by_proximity, si.sim, si)
        else:
            weights = [(filter_result.score, filter_result.sim_info.id) for filter_result in self._choices]
            choice = sims4.random.pop_weighted(weights)
        return choice


class LotPickerEnumerationStrategy(PickerEnumerationStrategy):

    def build_choice_list(self, si, sim, **kwargs):
        self._choices = [filter_result for filter_result in si._get_valid_lot_choices(si.target, si.context)]

    def find_best_choice(self, si):
        choice = random.choice(self._choices)
        return choice


class ObjectPickerEnumerationStrategy(PickerEnumerationStrategy):

    def __init__(self):
        super().__init__()
        self._gen_objects = None

    def build_choice_list(self, si, sim, get_all=False, **kwargs):
        if get_all:
            self._gen_objects = [obj for obj in si._get_objects_with_results_gen(si.target, si.context)]
            self._choices = [obj for obj, results in self._gen_objects for result, _ in iter(results) if result]
        else:
            self._choices = [obj for obj in si._get_objects_gen(si.target, si.context)]

    def get_gen_objects(self, **kwargs):
        return self._gen_objects

    def find_best_choice(self, si):
        if not self._choices:
            return
        elif si.order_by_proximity:
            choice = self.get_choice_by_proximity(si.order_by_proximity, si.sim, si)
        else:
            choice = random.choice(self._choices)
        return choice