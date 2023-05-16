# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\temple\temple_room_data.py
# Compiled at: 2017-08-25 18:25:33
# Size of source mod 2**32: 2646 bytes
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableMapping, TunableReference, TunableSet
from snippets import define_snippet
import services, sims4.resources

class TempleRoomData(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'gate':TunableSet(description='\n            A set of states in which the gate in this room can potentially\n            start.\n            ',
       tunable=TunableReference(description='\n                A potential starting state for the gate in this room.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
       class_restrictions=('ObjectStateValue', ))), 
     'traps':TunableMapping(description='\n            A mapping of trap objects to the interactions that can be used in\n            the pool potential of "trigger" interaction. A trap object will be\n            chosen at random from this mapping and placed at each placeholder\n            trap in this room. Once all trap objects have been chosen and placed\n            for a room, all of the mapped interactions will be collected and one\n            random interaction will be chosen as the "trigger" interaction.\n            ',
       key_name='Trap',
       key_type=TunableReference(description='\n                A reference to the trap object.\n                ',
       manager=(services.definition_manager())),
       value_name='Potential Trigger Interactions',
       value_type=TunableSet(description='\n                A set of interactions that, if successfully completed on the\n                chosen trap object, will trigger the loot for the gate in this\n                room.\n                ',
       tunable=TunableReference(description='\n                    One of the potential trigger interactions. This interaction\n                    also needs to be tuned on the object chosen for this trap.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       class_restrictions=('SuperInteraction', ))))}


TunableTempleRoomData, _ = define_snippet('TempleRoomData', TempleRoomData.TunableFactory())