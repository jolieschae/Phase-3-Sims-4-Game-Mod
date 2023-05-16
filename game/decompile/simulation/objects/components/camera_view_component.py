# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\camera_view_component.py
# Compiled at: 2017-10-30 14:04:02
# Size of source mod 2**32: 1935 bytes
import math
from objects.components import Component, componentmethod
from objects.components.types import CAMERA_VIEW_COMPONENT
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, Tunable, TunableAngle
import sims4.math

class CameraViewComponent(Component, HasTunableFactory, AutoFactoryInit, component_name=CAMERA_VIEW_COMPONENT):
    FACTORY_TUNABLES = {'rotation':TunableAngle(description='\n            The offset in degrees from the facing vector that we will use to \n            place the camera position.\n            ',
       default=0.0), 
     'distance':Tunable(description='\n            The distance from the owners position to place the camera.\n            ',
       tunable_type=float,
       default=1.0), 
     'height':Tunable(description='\n            If you want to increase the height of the camera for a specific\n            viewpoint.\n            ',
       tunable_type=float,
       default=0.0)}

    @componentmethod
    def get_camera_position(self):
        forward = self.owner.forward
        sin = math.sin(self.rotation)
        cos = math.cos(self.rotation)
        rotation = sims4.math.Vector3(forward.x * cos + forward.z * sin, forward.y, -forward.x * sin + forward.z * cos)
        final_pos = self.owner.position + rotation * self.distance
        final_pos.y += self.height
        return final_pos