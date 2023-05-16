# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\priority.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 2870 bytes
import enum

class Priority(enum.Int):
    Low = 1
    High = 2
    Critical = 3


class PriorityExtended(Priority, export=False):
    SubLow = 0


def can_priority_displace(priority_new, priority_existing, allow_clobbering=False):
    if priority_new is None:
        return False
    if allow_clobbering:
        return priority_new >= priority_existing
    return priority_new > priority_existing


def can_displace(interaction_new, interaction_existing, allow_clobbering=False, use_max_priority=False):
    existing_interaction_priority = interaction_existing.priority
    if use_max_priority:
        super_priority = interaction_existing.super_interaction.priority if interaction_existing.super_interaction is not None else Priority.Low
        existing_interaction_priority = max(super_priority, existing_interaction_priority)
    else:
        return can_priority_displace((interaction_new.priority), existing_interaction_priority, allow_clobbering=allow_clobbering) or False
    if interaction_existing.is_waiting_pickup_putdown:
        return False
    return not interaction_existing.is_cancel_aop