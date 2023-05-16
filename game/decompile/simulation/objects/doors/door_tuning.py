# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\doors\door_tuning.py
# Compiled at: 2016-03-17 23:02:18
# Size of source mod 2**32: 2566 bytes
from services import get_instance_manager
from sims4.tuning.tunable import TunableTuple, TunableReference
import sims4.resources

class DoorTuning:
    FRONT_DOOR_AVAILABILITY_STATE = TunableTuple(description='\n        State values for front door availability.\n        ',
      enabled=TunableReference(description='\n            State value for door being available to be a front door.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'),
      disabled=TunableReference(description='\n            State value for door being unavailable to be a front door.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'))
    FRONT_DOOR_STATE = TunableTuple(description="\n        State values for a door is or isn't a front door.\n        ",
      enabled=TunableReference(description='\n            State value for door is front door.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'),
      disabled=TunableReference(description='\n            State value for door is not front door.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'))
    INACTIVE_APARTMENT_DOOR_STATE = TunableTuple(description="\n        State values for a door is or isn't for an inactive apartment.\n        ",
      enabled=TunableReference(description='\n            State value for door is for an inactive apartment.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'),
      disabled=TunableReference(description='\n            State value for door is not for an inactive apartment.\n            ',
      manager=(get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'))