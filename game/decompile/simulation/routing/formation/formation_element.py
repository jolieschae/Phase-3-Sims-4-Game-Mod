# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\formation\formation_element.py
# Compiled at: 2020-08-13 13:56:20
# Size of source mod 2**32: 3978 bytes
from interactions import ParticipantTypeActorTargetSim, ParticipantTypeSingle
from interactions.interaction_finisher import FinishingType
from interactions.utils.interaction_elements import XevtTriggeredElement
from routing.formation.formation_data import RoutingFormation
from sims4.tuning.tunable import TunableEnumEntry, TunableList, OptionalTunable

class RoutingFormationElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'master':TunableEnumEntry(description='\n            The Sim that is going to be followed.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'slave':TunableEnumEntry(description='\n            The Sim that will be doing the follow.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.TargetSim), 
     'routing_formations':TunableList(description='\n            The routing formations we want to use. We will test them in order\n            until the tests pass.\n            \n            Use this list to do things like minimize interactions based on\n            which hand you want to leash a dog with.\n            ',
       tunable=RoutingFormation.TunableReference(description='\n                The routing formation to use.\n                '),
       minlength=1)}

    def _do_behavior(self, *args, **kwargs):
        master = self.interaction.get_participant(self.master)
        if master is None:
            return False
        slave = self.interaction.get_participant(self.slave)
        if slave is None:
            return False
        if slave is master:
            logger.error('Master and slave are the same: ({}); routing formation is not valid. Interaction: ({})', master, self.interaction)
            return False
        for formation in self.routing_formations:
            if formation.test_formation(master, slave):
                formation(master, slave, interaction=(self.interaction))
                break
        else:
            return False

        return True


class ReleaseRoutingFormationElement(XevtTriggeredElement):
    FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n            The Sim/object whose routing formation is gonna be released.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'target':OptionalTunable(tunable=TunableEnumEntry(description='\n                If enabled, the subject will only release the routing formation with this target.\n                If disabled, the subject will release all routing formations.\n                ',
       tunable_type=ParticipantTypeSingle,
       default=(ParticipantTypeSingle.TargetSim)))}

    def _do_behavior(self, *args, **kwargs):
        subject = self.interaction.get_participant(self.subject)
        if subject is None:
            return False
        target = self.interaction.get_participant(self.target) if self.target else None
        for slave_data in subject.routing_component.get_routing_slave_data():
            if target is None or slave_data.master == target or slave_data.slave == target:
                slave_data.release_formation_data()
                slave_data.interaction.cancel(FinishingType.USER_CANCEL, 'ReleaseRoutingFormationElement: Releasing routing formation.')

        return True