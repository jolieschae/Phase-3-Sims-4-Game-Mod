# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\tunable_object_generator.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4046 bytes
from interactions import ParticipantType
from objects.components.stored_object_info_tuning import _ObjectGeneratorFromStoredObjectComponent
from objects.gardening.gardening_object_generator import _ObjectGeneratorFromGardening
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableFactory, TunableVariant, Tunable, TunableReference, TunableSet
import services, sims4

class _ObjectGeneratorFromParticipant(HasTunableSingletonFactory, AutoFactoryInit):

    @TunableFactory.factory_option
    def participant_type_data(*, participant_type, participant_default):
        return {'participant':TunableEnumEntry(description='\n                The participant determining which objects are to be generated.\n                ',
           tunable_type=participant_type,
           default=participant_default), 
         'in_slot':TunableVariant(description='\n                slots of the participant object from which the target objects should be pulled.\n                ',
           by_name=Tunable(description='\n                    The exact name of a slot on the parent object in which the object should be.  \n                    ',
           tunable_type=str,
           default='_ctnm_'),
           by_reference=TunableReference(description='\n                    A particular slot type in which the object should be.\n                    ',
           manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE))),
           by_set_of_references=TunableSet(description='\n                    A set of references that the objects should be in.\n                    ',
           tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE)))),
           locked_args={'use_participant': None},
           default='use_participant')}

    def get_objects(self, resolver, *args, **kwargs):
        participants = (resolver.get_participants)(self.participant, *args, **kwargs)
        if self.in_slot is None:
            return participants
        else:
            slotted_objects = set()
            bone_name_hash = None
            slot_types = None
            if isinstance(self.in_slot, str):
                bone_name_hash = sims4.hash_util.hash32(self.in_slot)
            else:
                if isinstance(self.in_slot, frozenset):
                    slot_types = self.in_slot
                else:
                    slot_types = {
                     self.in_slot}
        for participant in participants:
            for runtime_slot in participant.get_runtime_slots_gen(slot_types=slot_types, bone_name_hash=bone_name_hash):
                slotted_objects.update(runtime_slot.children)

        return slotted_objects


class TunableObjectGeneratorVariant(TunableVariant):

    def __init__(self, *args, participant_type=ParticipantType, participant_default=ParticipantType.Actor, **kwargs):
        (super().__init__)(args, from_participant=_ObjectGeneratorFromParticipant.TunableFactory(participant_type_data={'participant_type':participant_type, 
 'participant_default':participant_default}), 
         from_gardening=_ObjectGeneratorFromGardening.TunableFactory(), 
         from_stored_object_component=_ObjectGeneratorFromStoredObjectComponent.TunableFactory(), 
         default='from_participant', **kwargs)