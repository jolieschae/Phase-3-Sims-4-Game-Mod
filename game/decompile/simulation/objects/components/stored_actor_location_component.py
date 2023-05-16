# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\stored_actor_location_component.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 8368 bytes
import sims4, services
from protocolbuffers import GameplaySaveData_pb2 as gameplay_serialization
from interactions.aop import AffordanceObjectPair
import interactions.constraints
from objects.components import Component, componentmethod, types
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import TunableReference
from sims4.math import Location, Transform, Vector3, Quaternion
from routing import SurfaceIdentifier
import protocolbuffers.SimObjectAttributes_pb2 as SimObjectAttributes_pb2

class StoredActorLocationTuning:
    GO_TO_STORED_LOCATION_SI = TunableReference(description='\n        The affordance that is provided by the Stored Actor Location\n        Component when there is a set location.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions=('GoToStoredLocationSuperInteraction', ),
      pack_safe=True)
    UNROUTABLE_MESSAGE_OFF_LOT = TunableLocalizedStringFactory(description='\n        The tooltip used when the Stored Location SI is unavailable\n        because the stored location is not on the active lot.\n        ')
    UNROUTABLE_MESSAGE_NOT_CONNECTED = TunableLocalizedStringFactory(description='\n        The tooltip used when the Stored Location SI is unavailable because\n        the stored location does not have routing connectivity to the sim.\n        ')


class StoredLocation:

    def __init__(self, location=None):
        self._location = location

    @property
    def orientation(self):
        if self._location is None:
            logger.warn('Attempting to access the orientation of a stored location with None value.')
            return
        return self._location.transform.orientation

    @property
    def transform(self):
        if self._location is None:
            logger.warn('Attempting to access the transform of a stored location with None value.')
            return
        return self._location.transform

    @property
    def translation(self):
        if self._location is None:
            logger.warn('Attempting to access the translation of a stored location with None value.')
            return
        return self._location.transform.translation

    @property
    def routing_surface(self):
        if self._location is None:
            logger.warn('Attempting to access the routing surface type of a stored location with None value.')
            return
        return self._location.routing_surface

    def save(self, stored_location_data):
        if self._location is None:
            return stored_location_data
        stored_location_data.x = self._location.transform.translation.x
        stored_location_data.y = self._location.transform.translation.y
        stored_location_data.z = self._location.transform.translation.z
        stored_location_data.rot_x = self._location.transform.orientation.x
        stored_location_data.rot_y = self._location.transform.orientation.y
        stored_location_data.rot_z = self._location.transform.orientation.z
        stored_location_data.rot_w = self._location.transform.orientation.w
        stored_location_data.zone = self._location.routing_surface.primary_id
        stored_location_data.level = self._location.routing_surface.secondary_id
        stored_location_data.surface_type = self._location.routing_surface.type
        return stored_location_data

    def load(self, stored_location_data):
        self._location = Location(Transform(Vector3(stored_location_data.x, stored_location_data.y, stored_location_data.z), Quaternion(stored_location_data.rot_x, stored_location_data.rot_y, stored_location_data.rot_z, stored_location_data.rot_w)), SurfaceIdentifier(stored_location_data.zone, stored_location_data.level, stored_location_data.surface_type))


class StoredActorLocationComponent(Component, component_name=types.STORED_ACTOR_LOCATION_COMPONENT, allow_dynamic=True, persistence_key=SimObjectAttributes_pb2.PersistenceMaster.PersistableData.StoredActorLocationComponent):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._stored_location = None

    def get_stored_location(self):
        if self._stored_location is None:
            logger.warn('Attempting to get a stored location with None value from the Stored Actor Location Component on {}.', self.owner)
        return self._stored_location

    @componentmethod
    def store_actor_location(self, sim):
        self._stored_location = StoredLocation(location=(sim.location))

    @componentmethod
    def component_potential_interactions_gen(self, context, **kwargs):
        if self._stored_location is None or StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI is None:
            return
        final_transform = self._stored_location.transform
        final_routing_surface = self._stored_location.routing_surface
        constraint_to_satisfy = interactions.constraints.Transform(final_transform, routing_surface=final_routing_surface)
        yield AffordanceObjectPair((StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI), (self.owner), (StoredActorLocationTuning.GO_TO_STORED_LOCATION_SI), None, constraint_to_satisfy=constraint_to_satisfy)

    def save(self, persistence_master_message):
        if not self._stored_location:
            return
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.StoredActorLocationComponent
        stored_actor_location_component_message = persistable_data.Extensions[protocols.PersistableStoredActorLocationComponent.persistable_data]
        self._stored_location.save(stored_actor_location_component_message.stored_location)
        persistence_master_message.data.extend([persistable_data])

    def load(self, stored_actor_location_component_message):
        stored_actor_location_component_data = stored_actor_location_component_message.Extensions[protocols.PersistableStoredActorLocationComponent.persistable_data]
        if stored_actor_location_component_data.HasField('stored_location'):
            self._stored_location = StoredLocation()
            self._stored_location.load(stored_actor_location_component_data.stored_location)


def add_stored_sim_location(object, sim=None, **kwargs):
    if object is not None:
        object.add_dynamic_component(types.STORED_ACTOR_LOCATION_COMPONENT)
        if sim is not None:
            object.store_actor_location(sim)
        return True
    return False