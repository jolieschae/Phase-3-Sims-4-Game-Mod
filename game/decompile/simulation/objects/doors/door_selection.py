# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\doors\door_selection.py
# Compiled at: 2016-03-02 21:26:01
# Size of source mod 2**32: 2281 bytes
from interactions import ParticipantTypeActorTargetSim
from objects.doors.door_tuning import DoorTuning
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry
import services

class DoorSelectFrontDoor(HasTunableSingletonFactory, AutoFactoryInit):

    def get_door(self, sim, target=None):
        return services.get_door_service().get_front_door()


class DoorSelectParticipantApartmentDoor(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description="\n            The participant who's door we want to use.\n            ",
                      tunable_type=ParticipantTypeActorTargetSim,
                      default=(ParticipantTypeActorTargetSim.Actor))}

    def get_door(self, sim, target=None):
        participant_sim = None
        if self.participant == ParticipantTypeActorTargetSim.Actor:
            participant_sim = sim
        else:
            if self.participant == ParticipantTypeActorTargetSim.TargetSim:
                participant_sim = target
            else:
                return participant_sim is None or participant_sim.is_sim or None
            door_service = services.get_door_service()
            plex_door_infos = door_service.get_plex_door_infos()
            home_zone_id = participant_sim.household.home_zone_id
            if home_zone_id == services.current_zone_id():
                return door_service.get_front_door()
            state = DoorTuning.INACTIVE_APARTMENT_DOOR_STATE.enabled.state
            for plex_door_info in plex_door_infos:
                if plex_door_info.zone_id != home_zone_id:
                    continue
                door = services.object_manager().get(plex_door_info.door_id)
                if door is not None and door.get_state(state) is DoorTuning.INACTIVE_APARTMENT_DOOR_STATE.enabled:
                    return door