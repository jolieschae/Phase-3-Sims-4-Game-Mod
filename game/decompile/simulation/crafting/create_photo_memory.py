# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\crafting\create_photo_memory.py
# Compiled at: 2019-05-09 13:43:11
# Size of source mod 2**32: 3036 bytes
from protocolbuffers import DistributorOps_pb2
from distributor.system import Distributor
from interactions import ParticipantTypeSingle, ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import TunableEnumEntry
import sims4
logger = sims4.log.Logger('Photography', default_owner='rrodgers')

class CreatePhotoMemory(XevtTriggeredElement):
    FACTORY_TUNABLES = {'photo_object':TunableEnumEntry(description='\n            The participant object that is the photo.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantType.Object), 
     'memory_sim':TunableEnumEntry(description='\n            The participant Sim that is the Sim making the memory.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantType.Actor)}

    def _create_make_memory_from_photo_op(self, memory_sim, canvas_component):
        make_memory_proto = DistributorOps_pb2.MakeMemoryFromPhoto()
        make_memory_proto.household_id = memory_sim.sim_info.household_id
        for sim in self.interaction.get_participants(participant_type=(ParticipantType.PickedSim)):
            make_memory_proto.sim_ids.append(sim.sim_id)

        make_memory_proto.texture_id = canvas_component.painting_state.texture_id
        make_memory_proto.filter_style = canvas_component.painting_effect
        make_memory_proto.time_stamp = canvas_component.time_stamp
        return GenericProtocolBufferOp(DistributorOps_pb2.Operation.MAKE_MEMORY_FROM_PHOTO, make_memory_proto)

    def _do_behavior(self):
        memory_sim = self.interaction.get_participant(self.memory_sim)
        if memory_sim is None:
            logger.error('create_photo_memory basic extra could not find a sim {}')
            return False
        photo_obj = self.interaction.get_participant(self.photo_object)
        if photo_obj is None:
            logger.error('create_photo_memory basic extra tuned photo_object participant does not exist.')
            return False
        canvas_component = photo_obj.canvas_component
        if canvas_component is None:
            logger.error('create_photo_memory basic extra tuned photo_object participant does not have a canvas component.')
            return False
        op = self._create_make_memory_from_photo_op(memory_sim, canvas_component)
        Distributor.instance().add_op(memory_sim, op)
        return True