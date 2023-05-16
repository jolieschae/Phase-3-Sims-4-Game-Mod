# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\life_event.py
# Compiled at: 2014-05-10 14:58:46
# Size of source mod 2**32: 2693 bytes
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from interactions import ParticipantTypeSingle
from element_utils import build_critical_section
from protocolbuffers import Social_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.tunable import TunableEnumEntry, TunableList, TunableFactory

class LifeEventCategory(DynamicEnumLocked):
    INVALID = 0


class TunableLifeEventElement(TunableFactory):

    @staticmethod
    def _factory(interaction, life_event_category, participants, sequence=None, **kwargs):

        def trigger(_):
            msg = Social_pb2.LifeEventMessage()
            msg.type = life_event_category
            participant_ids = []
            for participant_types in participants:
                participant = interaction.get_participant(participant_types)
                if participant is None:
                    participant_ids.append(0)
                else:
                    participant_ids.append(participant.id)

            msg.sim_ids.extend(participant_ids)
            distributor = Distributor.instance()
            distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.LIFE_EVENT_SEND, msg))

        return build_critical_section(sequence, trigger)

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, description='Trigger a Life Event', 
         life_event_category=TunableEnumEntry(description='\n                Category of life event',
  tunable_type=LifeEventCategory,
  default=(LifeEventCategory.INVALID)), 
         participants=TunableList(description='\n                    A list of participants that will be sent as part of the event.\n                    Order matters.  (i.e. if the string expects actor then target, order should be actor then target)\n                    ',
  tunable=TunableEnumEntry(description='\n                        participant to include in life event',
  tunable_type=ParticipantTypeSingle,
  default=(ParticipantTypeSingle.Actor))), **kwargs)

    FACTORY_TYPE = _factory