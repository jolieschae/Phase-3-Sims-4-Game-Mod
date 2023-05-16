# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\random.py
# Compiled at: 2022-03-10 20:35:09
# Size of source mod 2**32: 3512 bytes
from random import uniform
import random, sims4.math

def _weighted(pairs, random=random, flipped=False):
    weight_index = 1 if flipped else 0
    weights = [x[weight_index] for x in pairs]
    total = sum(weights)
    if total == 0:
        return
    select = random.uniform(0, total)
    for index, weight in enumerate(weights):
        select -= weight
        if select <= 0 and weight > 0:
            return index


def weighted_random_item(pairs, random=random, flipped=False):
    value_index = 0 if flipped else 1
    choice_index = _weighted(pairs, random=random, flipped=flipped)
    if choice_index is not None:
        return pairs[choice_index][value_index]


def weighted_random_index(tuple_of_tuples, random=random):
    choice_index = _weighted(tuple_of_tuples, random=random)
    if choice_index is not None:
        return choice_index


def pop_weighted(pairs, random=random, flipped=False):
    value_index = 0 if flipped else 1
    choice_index = _weighted(pairs, random=random, flipped=flipped)
    if choice_index is not None:
        return pairs.pop(choice_index)[value_index]


def random_chance(chance_value, random=random):
    if chance_value == 0:
        return False
    if chance_value == 100:
        return True
    return random.randint(0, 100) < chance_value


def random_orientation():
    angle = random.randint(0, 360)
    quaternion = sims4.math.angle_to_yaw_quaternion(angle)
    return quaternion


def random_item_from_lists(lists):
    if lists:
        num_items = sum((len(entry) for entry in lists))
        if num_items > 0:
            index = random.randint(0, num_items - 1)
            for i, entry in enumerate(lists):
                if index < len(entry):
                    return (
                     entry[index], i)
                index -= len(entry)

    return (None, None)