# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\animal_home_component.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 16451 bytes
import enum
from animation.animation_constants import CreatureType
from date_and_time import create_time_span
from distributor.shared_messages import create_icon_info_msg, IconInfoData
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.utils.tunable_icon import TunableIcon
from objects.hovertip import TooltipFieldsComplete
from objects.object_creation import ObjectCreation
from objects.placement.placement_helper import _PlacementStrategyLocation
from sims4.common import Pack
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableFactory, AutoFactoryInit, TunableInterval, TunableRange, OptionalTunable, TunableList, TunableEnumEntry, TunableTuple, Tunable
from sims4.utils import classproperty
import alarms, objects.components.types, services, sims4.log, random
logger = sims4.log.Logger('AnimalHomeComponent', default_owner='nabaker')

class AnimalOccupancyUIState(enum.Int):
    INVALID = 0
    DEFAULT_WITH_BG = 1
    ANIMAL_PRESENT = 2
    ANIMAL_ABSENT = 3


class AnimalHomeComponent(AutoFactoryInit, objects.components.Component, HasTunableFactory, allow_dynamic=False, component_name=objects.components.types.ANIMAL_HOME_COMPONENT):
    FACTORY_TUNABLES = {'max_capacity':TunableTuple(description='\n            Maximum number of animals housed in a home.\n            ',
       on_lot=TunableRange(description='\n                Maximum number of animals housed in a home on a lot.\n                ',
       tunable_type=int,
       default=1,
       minimum=1),
       open_street=TunableRange(description='\n                Maximum number of animals housed in a home on the open street.\n                ',
       tunable_type=int,
       default=1,
       minimum=1)), 
     'eligible_animal_data':TunableList(description='\n            List of the types of animals that can live in this home and associated data.\n            ',
       tunable=TunableTuple(description='\n                ',
       animal_type=TunableEnumEntry(description='\n                    Animal Type\n                    ',
       tunable_type=CreatureType,
       default=(CreatureType.Invalid),
       invalid_enums=(
      CreatureType.Invalid,)),
       hovertip_tunables=OptionalTunable(description="\n                    If tuned, the home's hovertip will show the number of animals currently in the home organized under\n                    animal type with this data.\n                    ",
       tunable=TunableTuple(icon=TunableIcon(description='\n                            The icon that matches to this animal type.\n                            '),
       label=TunableLocalizedStringFactory(description='\n                            The text label we want to use.\n                            {0.Number} = the number of animals of this type.\n                            ')))),
       minlength=1), 
     'persist_assignment_in_household_inventory':Tunable(description='\n            When enabled, any assignments to this home will be persisted even\n            if the home/animal is not instanced in household inventory.\n            \n            If true, please also register the matching animal(s) with the lost \n            and found service, as their assignments will be culled otherwise to \n            prevent players from accidentally leaving animals behind on lots \n            forever.\n            ',
       tunable_type=bool,
       default=True), 
     'object_creation_data':OptionalTunable(description='\n            When enabled, this creation data will be used to create inhabitants\n            if tuned to Populate Empty Homes or tuned to periodically spawn\n            inhabitants from the Animal Service.\n            ',
       tunable=ObjectCreation.TunableFactory()), 
     'populate_empty_homes':OptionalTunable(description="\n            If enabled, empty homes will be populated with inhabitants using this\n            component's Object Creation Data.\n            ",
       tunable=TunableTuple(min_inhabitants=TunableInterval(description='\n                    The number of inhabitants to populate in an empty home.\n                    ',
       tunable_type=int,
       default_lower=1,
       default_upper=3,
       minimum=0),
       on_new_home=Tunable(description='\n                    If enabled, new homes are populated if placed from Build/Buy.\n                    ',
       tunable_type=bool,
       default=False),
       on_zone_load=Tunable(description='\n                    If enabled, empty homes are populated after zone load.\n                    ',
       tunable_type=bool,
       default=False),
       on_last_inhabitant_removed=Tunable(description='\n                    If enabled, the home is repopulated after its last inhabitant\n                    is removed (by death or any other means).\n                    ',
       tunable_type=bool,
       default=False),
       tests=TunableTestSet(description='\n                    Conditional tests to determine if empty home population occurs.\n                    '))), 
     'show_absent_animal_type_status':OptionalTunable(description="\n            If tuned, the home's hovertip will show a status if any of the specified animal types are absent.\n            ",
       tunable=TunableTuple(animal_types=TunableList(description='\n                    List of animal types to consider.\n                    ',
       tunable=TunableEnumEntry(tunable_type=CreatureType,
       default=(CreatureType.Invalid),
       invalid_enums=(
      CreatureType.Invalid,))),
       status=TunableLocalizedStringFactory(description='\n                    The status string to show if an animal type is absent.\n                    ')))}

    @classmethod
    def _get_tuning_suggestions(cls, component_tuning, print_suggestion):
        if component_tuning.object_creation_data is not None:
            if isinstance(component_tuning.object_creation_data.location, _PlacementStrategyLocation):
                print_suggestion('Object Creation Data has Location tuned with Position. Consider if the animal home will be placed in the open street area. If so, spawning inhabitants may fail if this occurs in a lot with no household.', owner='bteng')

    REPLENISH_INHABITANTS_ON_ZONE_LOAD_MIN_DELAY_MINUTES = 15
    REPLENISH_INHABITANTS_ON_ZONE_LOAD_RAN_DELAY_MINUTES = 15

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._replenish_inhabitants_alarm_handle = None

    @classproperty
    def required_packs(cls):
        return (Pack.EP11,)

    def get_eligible_animal_types(self):
        return [animal.animal_type for animal in self.eligible_animal_data]

    def on_add(self):
        animal_service = services.animal_service()
        if animal_service is None:
            return
        animal_service.on_home_added(self.owner.id)

    def on_remove(self):
        if self._replenish_inhabitants_alarm_handle is not None:
            alarms.cancel_alarm(self._replenish_inhabitants_alarm_handle)
            self._replenish_inhabitants_alarm_handle = None
        zone = services.current_zone()
        if zone.is_zone_shutting_down:
            return
        animal_service = services.animal_service()
        if animal_service is None:
            return
        animal_service.on_home_destroyed(self.owner.id)

    def on_child_added(self, child, location):
        if child.animalobject_component is None:
            return
        animal_service = services.animal_service()
        if animal_service is None:
            return
        animal_service.assign_animal(child.id, self.owner)

    def test_populate_empty_homes(self):
        if self.populate_empty_homes is None:
            return False
        resolver = SingleObjectResolver(self.owner)
        return self.populate_empty_homes.tests.run_tests(resolver)

    def get_min_inhabitants_to_populate(self):
        if self.populate_empty_homes is None:
            return 0
        return self.populate_empty_homes.min_inhabitants.random_int()

    def try_populate_on_build_buy_exit(self):
        return self.populate_empty_homes is None or self.populate_empty_homes.on_new_home or False
        return self.replenish_inhabitants()

    def try_populate_on_zone_load(self):
        return self.populate_empty_homes is None or self.populate_empty_homes.on_zone_load or False
        if self._replenish_inhabitants_alarm_handle is not None:
            alarms.cancel_alarm(self._replenish_inhabitants_alarm_handle)
        time_span = create_time_span(minutes=(self.REPLENISH_INHABITANTS_ON_ZONE_LOAD_MIN_DELAY_MINUTES)) + create_time_span(minutes=(self.REPLENISH_INHABITANTS_ON_ZONE_LOAD_RAN_DELAY_MINUTES)) * random.random()
        self._replenish_inhabitants_alarm_handle = alarms.add_alarm(self, time_span, self.replenish_inhabitants_alarm_callback)
        return True

    def try_populate_on_last_inhabitant_removed(self):
        return self.populate_empty_homes is None or self.populate_empty_homes.on_last_inhabitant_removed or False
        return self.replenish_inhabitants()

    def create_inhabitant(self):
        if not self.object_creation_data:
            return
        resolver = SingleObjectResolver(self.owner)
        self.object_creation_data.initialize_helper(resolver)
        return self.object_creation_data.create_object(resolver)

    def replenish_inhabitants(self):
        min_inhabitants = self.get_min_inhabitants_to_populate()
        if min_inhabitants == 0:
            return False
        else:
            animal_service = services.animal_service()
            if animal_service is None:
                return False
            if animal_service.get_current_occupancy(self.owner.id) > 0:
                return False
            return self.test_populate_empty_homes() or False
        num_to_create = min(min_inhabitants, self.get_max_capacity())
        for i in range(num_to_create):
            created_inhabitant = self.create_inhabitant()
            if created_inhabitant is not None:
                animal_service.assign_animal(created_inhabitant.id, self.owner)

        return True

    def replenish_inhabitants_alarm_callback(self, handle):
        self.replenish_inhabitants()
        if self._replenish_inhabitants_alarm_handle is not None:
            alarms.cancel_alarm(self._replenish_inhabitants_alarm_handle)
            self._replenish_inhabitants_alarm_handle = None

    def update_tooltip(self, currently_assigned_animal_types):
        absent_animal_status = self.show_absent_animal_type_status
        if absent_animal_status:
            animal_types = absent_animal_status.animal_types
            for animal_type in animal_types:
                if animal_type not in currently_assigned_animal_types:
                    self.owner.update_tooltip_field(TooltipFieldsComplete.stolen_from_text, absent_animal_status.status())
                    break
            else:
                self.owner.update_tooltip_field(TooltipFieldsComplete.stolen_from_text, None)

        icon_infos = []
        for animal in self.eligible_animal_data:
            hovertip_tunables = animal.hovertip_tunables
            if hovertip_tunables is not None:
                num_animals = int(currently_assigned_animal_types.get(animal.animal_type, 0))
                icon_info_data = IconInfoData(icon_resource=(hovertip_tunables.icon))
                label = hovertip_tunables.label(num_animals)
                msg = create_icon_info_msg(icon_info_data, name=label)
                msg.control_id = AnimalOccupancyUIState.ANIMAL_PRESENT if num_animals > 0 else AnimalOccupancyUIState.ANIMAL_ABSENT
                icon_infos.append(msg)

        self.owner.update_tooltip_field(TooltipFieldsComplete.icon_infos, icon_infos)
        self.owner.update_object_tooltip()

    def get_max_capacity(self):
        if self.owner.is_on_active_lot():
            return self.max_capacity.on_lot
        return self.max_capacity.open_street

    def get_free_slot_for_save(self, slot_type, saved_slots):
        animal_service = services.animal_service()
        if animal_service is None:
            return
        for runtime_slot in self.owner.get_runtime_slots_gen(slot_types={slot_type}):
            slot = runtime_slot.slot_name_hash
            if slot not in saved_slots:
                return slot

        logger.error('The number of slots with type {} available on the home obj {} is less than the number ofanimals that need to be slotted. Please check the model for the home or the slot type tunedin save_home_slot_for_gallery on the AnimalObjectComponent.', slot_type,
          (self.owner), owner='amwu')