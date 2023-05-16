# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\state_references.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 1675 bytes
from services import get_instance_manager
from sims4.tuning.tunable import TunableReference, TunablePackSafeReference
from singletons import DEFAULT
from sims4.resources import Types

class TunableStateValueReference(TunableReference):

    def __init__(self, class_restrictions=DEFAULT, **kwargs):
        if class_restrictions is DEFAULT:
            class_restrictions = 'ObjectStateValue'
        (super().__init__)(manager=get_instance_manager(Types.OBJECT_STATE), class_restrictions=class_restrictions, **kwargs)


class TunablePackSafeStateValueReference(TunablePackSafeReference):

    def __init__(self, class_restrictions=DEFAULT, **kwargs):
        if class_restrictions is DEFAULT:
            class_restrictions = 'ObjectStateValue'
        (super().__init__)(manager=get_instance_manager(Types.OBJECT_STATE), class_restrictions=class_restrictions, **kwargs)


class TunableStateTypeReference(TunableReference):

    def __init__(self, class_restrictions=DEFAULT, **kwargs):
        if class_restrictions is DEFAULT:
            class_restrictions = 'ObjectState'
        (super().__init__)(manager=get_instance_manager(Types.OBJECT_STATE), class_restrictions=class_restrictions, **kwargs)