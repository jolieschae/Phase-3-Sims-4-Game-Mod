# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\tunable_offset.py
# Compiled at: 2019-06-06 13:53:41
# Size of source mod 2**32: 3405 bytes
from sims4.math import Vector3, vector3_rotate_axis_angle, TWO_PI
from sims4.tuning.tunable import TunableVariant, TunableAngle, TunableInterval, TunableFactory
from sims4.tuning.geometric import TunableVector3
import random

class TunableOffset(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, fixed=TunableVector3(description='\n                A fixed offset.\n                ',
  default=(Vector3.ZERO())), 
         random_in_circle=TunableRandomOffsetInCircle(description='\n                Specify a random offset within given full/partial circle/donut.\n                '), 
         default='fixed', **kwargs)

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        if isinstance(value, Vector3):
            return (lambda: value)
        return value


class TunableRandomOffsetInCircle(TunableFactory):

    @staticmethod
    def _factory(*args, distance, angle, offset, axis, **kwargs):
        rotation_radians = random.uniform(0, angle) + offset
        distance_vector = Vector3(distance.random_float(), 0, 0)
        return vector3_rotate_axis_angle(distance_vector, rotation_radians, axis)

    FACTORY_TYPE = _factory

    def __init__(self, **kwargs):
        (super().__init__)(distance=TunableInterval(description='\n                The distance range relative to origin point that \n                the generated point should be in.\n                ',
  tunable_type=float,
  minimum=0,
  default_lower=1,
  default_upper=5), 
         angle=TunableAngle(description='\n                The slice of the donut/circle in degrees.\n                ',
  default=TWO_PI), 
         offset=TunableAngle(description='\n                An offset (rotation) in degrees, affecting where the start\n                of the angle is.  This has no effect if angle is 360 degrees.\n                ',
  default=0), 
         axis=TunableVariant(description='\n                Around which axis the position will be located.\n                ',
  default='y',
  locked_args={'x':Vector3.X_AXIS(), 
 'y':Vector3.Y_AXIS(), 
 'z':Vector3.Z_AXIS()}), **kwargs)