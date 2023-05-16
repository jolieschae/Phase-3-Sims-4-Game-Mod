# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\postures\posture_interactions.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 1790 bytes
from animation.posture_manifest import Hand
from carry.carry_tuning import CarryPostureStaticTuning
from interactions.base.super_interaction import SuperInteraction
from sims4.tuning.tunable import TunableReference
from sims4.utils import classproperty
import interactions.aop, postures.posture_specs, services, sims4.resources

class HoldObjectBase(SuperInteraction):

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        yield (interactions.aop.AffordanceObjectPair)(cls, target, cls, None, hand=Hand.LEFT, **kwargs)
        yield (interactions.aop.AffordanceObjectPair)(cls, target, cls, None, hand=Hand.RIGHT, **kwargs)
        yield (interactions.aop.AffordanceObjectPair)(cls, target, cls, None, hand=Hand.BACK, **kwargs)


class HoldObject(HoldObjectBase):
    INSTANCE_TUNABLES = {'_carry_posture_type': TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.POSTURE)), description='The carry posture type for this version of HoldObject.')}

    @classmethod
    def get_provided_posture_change(cls, aop):
        return postures.posture_specs.PostureOperation.PickUpObject(cls._carry_posture_type, aop.target)

    @classproperty
    def provided_posture_type(cls):
        return cls._carry_posture_type


class HoldNothing(HoldObjectBase):

    @classmethod
    def get_provided_posture_change(cls, aop):
        return postures.posture_specs.PostureOperation.PickUpObject(CarryPostureStaticTuning.POSTURE_CARRY_NOTHING, None)

    @classproperty
    def provided_posture_type(cls):
        return CarryPostureStaticTuning.POSTURE_CARRY_NOTHING