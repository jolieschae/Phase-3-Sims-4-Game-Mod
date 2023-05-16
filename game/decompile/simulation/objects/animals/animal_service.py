# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\animals\animal_service.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 50805 bytes
import random, services, sims4
from animation.animation_constants import CreatureType
from distributor.rollback import ProtocolBufferRollback
from event_testing.resolver import GlobalResolver
from event_testing.tests import TunableTestSet
from objects.components.state import ObjectStateValue
from objects.components.types import ANIMAL_OBJECT_COMPONENT, STATE_COMPONENT, ANIMAL_HOME_COMPONENT, TOOLTIP_COMPONENT, NAME_COMPONENT
from persistence_error_types import ErrorCodes
from protocolbuffers import GameplaySaveData_pb2
from scheduler import WeeklySchedule
from sims4.common import Pack
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableEnumEntry, TunableInterval, TunableList, TunablePackSafeReference, TunableRange, TunableTuple
from sims4.utils import classproperty
import build_buy
logger = sims4.log.Logger('Animal Service', default_owner='skorman')

class AnimalHomeData:

    def __init__(self, animal_home_id, max_occupancy, animal_types, persist_assignment, owner_household_id, zone_id, open_street_id, current_occupancy=0):
        self.id = animal_home_id
        self.current_occupancy = current_occupancy
        self.current_occupancy_by_type = {}
        self.max_occupancy = max_occupancy
        self.animal_types = animal_types
        self.persist_assignment_in_household_inventory = persist_assignment
        self.owner_household_id = owner_household_id
        self.zone_id = zone_id
        self.open_street_id = open_street_id

    def update_occupancy(self, animal_type, add):
        if add:
            self.current_occupancy += 1
            self.current_occupancy_by_type[animal_type] = self.current_occupancy_by_type.get(animal_type, 0) + 1
        else:
            if self.current_occupancy <= 0:
                logger.error('Attempting to remove an animal from empty home with ID {}.', self.id)
            self.current_occupancy -= 1
            self.current_occupancy_by_type[animal_type] = self.current_occupancy_by_type.get(animal_type) - 1

    def update(self, home_id):
        home = services.object_manager().get(home_id)
        if home is None:
            return
            home_component = home.get_component(ANIMAL_HOME_COMPONENT)
            if home_component is None:
                logger.error('Attempting to update Home {} with no AnimalHomeComponent.', home)
                return
            zone = services.current_zone()
            animal_service = services.animal_service()
            if zone is not None:
                self.zone_id = zone.id
                self.open_street_id = zone.open_street_id
                if zone.is_zone_loading and animal_service is not None:
                    animal_service._delayed_home_updates.add(home_id)
        else:
            self.owner_household_id = home.get_household_owner_id()
        if self.max_occupancy is not None:
            return
        self.max_occupancy = home_component.get_max_capacity()
        self.animal_types = home_component.get_eligible_animal_types()
        self.persist_assignment_in_household_inventory = home_component.persist_assignment_in_household_inventory

    def delayed_update(self):
        home = services.object_manager().get(self.id)
        if home is None:
            return
        self.owner_household_id = home.get_household_owner_id()
        zone = services.get_zone(self.zone_id)
        self.open_street_id = zone.open_street_id


class AnimalService(Service):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        animal_types = {}
        for auto_assignment_schedule in AnimalService.AUTO_ASSIGN_NEW_INHABITANTS:
            if auto_assignment_schedule.animal_type in animal_types.keys():
                logger.error('Animal type {} tuned more than once in AUTO_ASSIGN_NEW_INHABITANTS', auto_assignment_schedule.animal_type)
            animal_types[auto_assignment_schedule.animal_type] = True

    GARDENING_HELP_STATE = ObjectStateValue.TunableReference(description='\n        The gardening help state that animals have when\n        gardening help is enabled.\n        ')
    GARDENING_HELP_WEED_STATES = TunableList(description='\n        For animals with gardening help enabled,\n        these are the relevant weed states on plants to watch for.                 \n        ',
      tunable=(ObjectStateValue.TunableReference()))
    GARDENING_HELP_ANIMAL_STATES = TunableList(description="\n        For animals with gardening help enabled, these are the states that\n        an animal will transition from/to whenever the plant's state changes.\n        The order of these lists is the preference in the animal to pick.\n        ",
      tunable=TunableTuple(animal_type=TunableEnumEntry(tunable_type=CreatureType,
      default=(CreatureType.Rabbit),
      invalid_enums=(
     CreatureType.Invalid,)),
      states=TunableList(tunable=TunableTuple(from_state=(ObjectStateValue.TunableReference()),
      to_state=(ObjectStateValue.TunableReference())))))
    AUTO_ASSIGN_NEW_INHABITANTS = TunableList(description='\n        On a schedule, automatically assigns new animals to existing homes\n        that have vacancy. The assignment will try to assign existing homeless\n        animals before creating new animals. \n        ',
      tunable=TunableTuple(animal_type=TunableEnumEntry(description='\n                The animal home type to scan for on the existing lot.\n                ',
      tunable_type=CreatureType,
      default=(CreatureType.Rabbit)),
      weekly_schedule=WeeklySchedule.TunableFactory(description='\n                Determines when to trigger the auto-assignment.\n                '),
      num_assignments_per_home=TunableInterval(description='\n                The number of auto-assignments per home. The value is a random number\n                between the lower and upper bounds, inclusively.\n                ',
      tunable_type=int,
      default_lower=1,
      default_upper=1,
      minimum=0),
      max_homes_to_assign=TunableInterval(description='\n                When auto-assignment triggers, this is the maximum number of homes to\n                randomly pick. Homes at max capacity are excluded. The value is a random\n                number between the lower and upper bounds, inclusively.\n                \n                For example:\n                The value is randomly 3.\n                15 homes are on the lot (10 empty or partially full, 5 full)\n                From the 10 homes, 3 are randomly picked for auto-assignment.\n                ',
      tunable_type=int,
      default_lower=1,
      default_upper=1,
      minimum=0),
      tests=TunableTestSet(description='\n                Conditional tests to determine if auto-assignment occurs.\n                ')),
      verify_tunable_callback=_verify_tunable_callback)
    MAX_EMPTY_HOMES_TO_POPULATE = TunableTuple(description='\n        Some Animal Home Component objects are configured to populate empty homes\n        for the following conditions. These settings configure the maximum number\n        of empty homes that can be populated at one time.\n        ',
      on_new_homes=TunableRange(description='\n            The limit on number of new homes to populate if placed during Build/Buy.\n            ',
      tunable_type=int,
      default=5,
      minimum=0,
      maximum=5),
      on_zone_load=TunableRange(description='\n            The limit on number of empty homes to populate after zone load.\n            ',
      tunable_type=int,
      default=5,
      minimum=0,
      maximum=5))
    AGING_STATISTIC = TunablePackSafeReference(description='\n        The statistic we are operating on.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('Commodity', ))

    def __init__(self):
        self._animal_assignment_map = {}
        self._objs_destroyed_in_bb = {}
        self._weed_eligible_plants = []
        self._registered_homes = {}
        self._registered_animals = {}
        self._home_ids_registered_in_bb = []
        self._active_weekly_schedules = []
        self._creature_aging_enabled = True
        self._delayed_home_updates = set()

    def start(self):
        self._start_auto_assignment_schedules()

    def stop(self):
        self._stop_auto_assignment_schedules()

    @classproperty
    def required_packs(cls):
        return (Pack.EP11,)

    @property
    def animal_assignment_map(self):
        return self._animal_assignment_map

    @classproperty
    def save_error_code(cls):
        return ErrorCodes.SERVICE_SAVE_FAILED_ANIMAL_SERVICE

    def save(self, save_slot_data=None, **kwargs):
        service_data = GameplaySaveData_pb2.PersistableAnimalService()
        object_manager = services.object_manager()
        for animal_id, home_data in self._animal_assignment_map.items():
            if services.current_zone().is_in_build_buy:
                if self._is_obj_destroyed_in_bb(animal_id):
                    continue
            with ProtocolBufferRollback(service_data.animal_data) as (animal_data):
                animal_data.obj_id = animal_id
                animal_data.animal_type = self._registered_animals[animal_id]
                if home_data is not None:
                    home_id = home_data.id
                    if services.current_zone().is_in_build_buy:
                        if self._is_obj_destroyed_in_bb(home_id):
                            continue
                        if not home_data.persist_assignment_in_household_inventory:
                            if self._is_obj_modified_in_bb(animal_id) or self._is_obj_modified_in_bb(home_id):
                                animal = object_manager.get(animal_id)
                                home = object_manager.get(home_id)
                                if animal is None or home is None:
                                    continue
                    animal_data.home_id = home_id
                    if home_data.owner_household_id is not None:
                        animal_data.owner_household_id = home_data.owner_household_id
                    if home_data.zone_id is not None:
                        animal_data.zone_id = home_data.zone_id
                    if home_data.open_street_id is not None:
                        animal_data.open_street_id = home_data.open_street_id

        save_slot_data.gameplay_data.animal_service = service_data

    def load(self, **_):
        save_slot_data_msg = services.get_persistence_service().get_save_slot_proto_buff()
        if not save_slot_data_msg.gameplay_data.HasField('animal_service'):
            return
        service_data = save_slot_data_msg.gameplay_data.animal_service
        for animal_data in service_data.animal_data:
            self._registered_animals[animal_data.obj_id] = animal_data.animal_type
            if animal_data.HasField('home_id'):
                home_data = self._registered_homes.get(animal_data.home_id)
                if home_data is None:
                    owner_household_id = None
                    zone_id = None
                    open_street_id = None
                    if animal_data.HasField('owner_household_id'):
                        if animal_data.owner_household_id != 0:
                            owner_household_id = animal_data.owner_household_id
                    if animal_data.HasField('zone_id'):
                        if animal_data.zone_id != 0:
                            zone_id = animal_data.zone_id
                    if animal_data.HasField('open_street_id'):
                        if animal_data.open_street_id != 0:
                            open_street_id = animal_data.open_street_id
                    home_data = AnimalHomeData(animal_data.home_id, None, None, True, owner_household_id, zone_id, open_street_id)
                    self._registered_homes[animal_data.home_id] = home_data
            else:
                home_data = None
            self._move_animal_home(animal_data.obj_id, home_data)

    def load_options(self, options_proto):
        self._creature_aging_enabled = options_proto.creature_aging_enabled

    def save_options(self, options_proto):
        options_proto.creature_aging_enabled = self._creature_aging_enabled

    def update_aging(self):
        for animal_id in self._registered_animals.keys():
            animal = services.object_manager().get(animal_id)
            if animal is None:
                animal = services.inventory_manager().get(animal_id)
            if animal is None:
                continue
            self.update_animal_aging(animal)

    def update_animal_aging(self, animal):
        aging_statistic = animal.get_stat_instance(self.AGING_STATISTIC)
        if aging_statistic is None:
            return
        aging_statistic.decay_enabled = self._creature_aging_enabled

    def set_aging_enabled(self, enabled):
        self._creature_aging_enabled = enabled
        self.update_aging()

    def on_zone_load(self):
        num_empty_homes_populated = 0
        obj_manager = services.object_manager()
        for home_id, home_data in self._registered_homes.items():
            if num_empty_homes_populated >= self.MAX_EMPTY_HOMES_TO_POPULATE.on_zone_load:
                break
            else:
                if home_data.current_occupancy > 0:
                    continue
                home = obj_manager.get(home_id)
                if home is None:
                    continue
                home.has_component(ANIMAL_HOME_COMPONENT) or logger.error('Registered home {} does not have an Animal Home Component.', home)
                continue
            if home.animalhome_component.try_populate_on_zone_load():
                num_empty_homes_populated += 1

        for animal_id, _ in self._animal_assignment_map.items():
            animal_obj = obj_manager.get(animal_id)
            if animal_obj is not None:
                animal_obj.update_object_tooltip()

        for home_id in self._delayed_home_updates:
            home_data = self._registered_homes.get(home_id)
            if home_data is None:
                logger.error('Expecting home {} to be already registered.', home_id)
                continue
            home_data.delayed_update()

        self._delayed_home_updates.clear()

    def on_cleanup_zone_objects--- This code section failed: ---

 L. 442         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              current_zone
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'zone'

 L. 443         8  LOAD_FAST                'zone'
               10  LOAD_CONST               None
               12  COMPARE_OP               is
               14  POP_JUMP_IF_FALSE    20  'to 20'

 L. 444        16  LOAD_CONST               None
               18  RETURN_VALUE     
             20_0  COME_FROM            14  '14'

 L. 446        20  LOAD_GLOBAL              services
               22  LOAD_METHOD              household_manager
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  STORE_FAST               'household_manager'

 L. 447        28  LOAD_GLOBAL              services
               30  LOAD_METHOD              inventory_manager
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  STORE_FAST               'inventory_manager'

 L. 448        36  LOAD_GLOBAL              services
               38  LOAD_METHOD              object_manager
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  STORE_FAST               'obj_manager'

 L. 449        44  LOAD_GLOBAL              services
               46  LOAD_METHOD              get_instance_manager
               48  LOAD_GLOBAL              sims4
               50  LOAD_ATTR                resources
               52  LOAD_ATTR                Types
               54  LOAD_ATTR                VENUE
               56  CALL_METHOD_1         1  '1 positional argument'
               58  STORE_FAST               'venue_manager'

 L. 451        60  LOAD_FAST                'zone'
               62  LOAD_ATTR                id
               64  STORE_DEREF              'zone_id'

 L. 452        66  LOAD_FAST                'zone'
               68  LOAD_ATTR                open_street_id
               70  STORE_DEREF              'street_id'

 L. 454        72  LOAD_FAST                'venue_manager'
               74  LOAD_METHOD              get
               76  LOAD_GLOBAL              build_buy
               78  LOAD_METHOD              get_current_venue
               80  LOAD_DEREF               'zone_id'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  CALL_METHOD_1         1  '1 positional argument'
               86  STORE_FAST               'current_venue_tuning'

 L. 455        88  LOAD_FAST                'zone'
               90  LOAD_METHOD              get_active_lot_owner_household
               92  CALL_METHOD_0         0  '0 positional arguments'
               94  STORE_FAST               'lot_owner_household'

 L. 456        96  LOAD_FAST                'lot_owner_household'
               98  LOAD_CONST               None
              100  COMPARE_OP               is-not
              102  POP_JUMP_IF_FALSE   110  'to 110'
              104  LOAD_FAST                'lot_owner_household'
              106  LOAD_ATTR                id
              108  JUMP_FORWARD        112  'to 112'
            110_0  COME_FROM           102  '102'
              110  LOAD_CONST               None
            112_0  COME_FROM           108  '108'
              112  STORE_FAST               'lot_owner_household_id'

 L. 457       114  LOAD_FAST                'current_venue_tuning'
              116  LOAD_ATTR                is_residential
              118  JUMP_IF_TRUE_OR_POP   124  'to 124'
              120  LOAD_FAST                'current_venue_tuning'
              122  LOAD_ATTR                is_university_housing
            124_0  COME_FROM           118  '118'
              124  STORE_FAST               'is_residential'

 L. 460       126  LOAD_CLOSURE             'street_id'
              128  LOAD_CLOSURE             'zone_id'
              130  BUILD_TUPLE_2         2 
              132  LOAD_LAMBDA              '<code_object <lambda>>'
              134  LOAD_STR                 'AnimalService.on_cleanup_zone_objects.<locals>.<lambda>'
              136  MAKE_FUNCTION_8          'closure'
              138  STORE_DEREF              'is_home_in_current_zone_or_street'

 L. 462       140  LOAD_CLOSURE             'is_home_in_current_zone_or_street'
              142  BUILD_TUPLE_1         1 
              144  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              146  LOAD_STR                 'AnimalService.on_cleanup_zone_objects.<locals>.<dictcomp>'
              148  MAKE_FUNCTION_8          'closure'
              150  LOAD_FAST                'self'
              152  LOAD_ATTR                _animal_assignment_map
              154  LOAD_METHOD              items
              156  CALL_METHOD_0         0  '0 positional arguments'
              158  GET_ITER         
              160  CALL_FUNCTION_1       1  '1 positional argument'
              162  STORE_FAST               'assignments_to_check'

 L. 465       164  BUILD_MAP_0           0 
              166  STORE_FAST               'assignments_to_delete'

 L. 466       168  LOAD_GLOBAL              set
              170  CALL_FUNCTION_0       0  '0 positional arguments'
              172  STORE_FAST               'homeless_animals_to_delete'

 L. 467   174_176  SETUP_LOOP          450  'to 450'
              178  LOAD_FAST                'assignments_to_check'
              180  LOAD_METHOD              items
              182  CALL_METHOD_0         0  '0 positional arguments'
              184  GET_ITER         
            186_0  COME_FROM           292  '292'
          186_188  FOR_ITER            448  'to 448'
              190  UNPACK_SEQUENCE_2     2 
              192  STORE_FAST               'animal_id'
              194  STORE_FAST               'home_data'

 L. 469       196  LOAD_FAST                'obj_manager'
              198  LOAD_METHOD              get
              200  LOAD_FAST                'animal_id'
              202  CALL_METHOD_1         1  '1 positional argument'
              204  JUMP_IF_TRUE_OR_POP   214  'to 214'
              206  LOAD_FAST                'inventory_manager'
              208  LOAD_METHOD              get
              210  LOAD_FAST                'animal_id'
              212  CALL_METHOD_1         1  '1 positional argument'
            214_0  COME_FROM           204  '204'
              214  STORE_FAST               'animal'

 L. 472       216  LOAD_FAST                'home_data'
              218  LOAD_CONST               None
              220  COMPARE_OP               is
          222_224  POP_JUMP_IF_FALSE   306  'to 306'

 L. 473       226  LOAD_FAST                'animal'
              228  LOAD_CONST               None
              230  COMPARE_OP               is
              232  POP_JUMP_IF_FALSE   244  'to 244'

 L. 474       234  LOAD_CONST               True
              236  LOAD_FAST                'assignments_to_delete'
              238  LOAD_FAST                'animal_id'
              240  STORE_SUBSCR     
              242  JUMP_BACK           186  'to 186'
            244_0  COME_FROM           232  '232'

 L. 476       244  LOAD_FAST                'lot_owner_household'
              246  LOAD_CONST               None
              248  COMPARE_OP               is-not
          250_252  POP_JUMP_IF_FALSE   262  'to 262'
              254  LOAD_FAST                'is_residential'
          256_258  POP_JUMP_IF_FALSE   262  'to 262'

 L. 477       260  CONTINUE            186  'to 186'
            262_0  COME_FROM           256  '256'
            262_1  COME_FROM           250  '250'

 L. 478       262  LOAD_FAST                'animal'
              264  LOAD_METHOD              get_household_owner_id
              266  CALL_METHOD_0         0  '0 positional arguments'
              268  STORE_FAST               'household_id'

 L. 479       270  LOAD_FAST                'household_id'
              272  LOAD_CONST               None
              274  COMPARE_OP               is
          276_278  POP_JUMP_IF_TRUE    294  'to 294'
              280  LOAD_FAST                'household_manager'
              282  LOAD_METHOD              get
              284  LOAD_FAST                'household_id'
              286  CALL_METHOD_1         1  '1 positional argument'
              288  LOAD_CONST               None
              290  COMPARE_OP               is
              292  POP_JUMP_IF_FALSE   186  'to 186'
            294_0  COME_FROM           276  '276'

 L. 480       294  LOAD_FAST                'homeless_animals_to_delete'
              296  LOAD_METHOD              add
              298  LOAD_FAST                'animal'
              300  CALL_METHOD_1         1  '1 positional argument'
              302  POP_TOP          

 L. 481       304  CONTINUE            186  'to 186'
            306_0  COME_FROM           222  '222'

 L. 484       306  LOAD_FAST                'home_data'
              308  LOAD_ATTR                id
              310  STORE_FAST               'home_id'

 L. 485       312  LOAD_FAST                'obj_manager'
              314  LOAD_METHOD              get
              316  LOAD_FAST                'home_id'
              318  CALL_METHOD_1         1  '1 positional argument'
              320  STORE_FAST               'home'

 L. 486       322  LOAD_FAST                'animal'
              324  LOAD_CONST               None
              326  COMPARE_OP               is-not
          328_330  POP_JUMP_IF_FALSE   344  'to 344'
              332  LOAD_FAST                'home'
              334  LOAD_CONST               None
              336  COMPARE_OP               is-not
          338_340  POP_JUMP_IF_FALSE   344  'to 344'

 L. 487       342  CONTINUE            186  'to 186'
            344_0  COME_FROM           338  '338'
            344_1  COME_FROM           328  '328'

 L. 491       344  LOAD_FAST                'home_data'
              346  LOAD_ATTR                owner_household_id
          348_350  JUMP_IF_TRUE_OR_POP   354  'to 354'
              352  LOAD_FAST                'lot_owner_household_id'
            354_0  COME_FROM           348  '348'
              354  STORE_FAST               'owner_household_id'

 L. 496       356  LOAD_FAST                'home'
              358  LOAD_CONST               None
              360  COMPARE_OP               is
          362_364  POP_JUMP_IF_FALSE   370  'to 370'
              366  LOAD_FAST                'home_id'
              368  JUMP_FORWARD        372  'to 372'
            370_0  COME_FROM           362  '362'
              370  LOAD_FAST                'animal_id'
            372_0  COME_FROM           368  '368'
              372  STORE_FAST               'obj_id_to_check'

 L. 497       374  LOAD_FAST                'owner_household_id'
              376  LOAD_CONST               None
              378  COMPARE_OP               is-not
          380_382  JUMP_IF_FALSE_OR_POP   390  'to 390'
              384  LOAD_FAST                'owner_household_id'
              386  LOAD_FAST                'household_manager'
              388  COMPARE_OP               in
            390_0  COME_FROM           380  '380'
              390  STORE_FAST               'has_owning_household'

 L. 498       392  LOAD_FAST                'has_owning_household'
          394_396  POP_JUMP_IF_FALSE   434  'to 434'
              398  LOAD_FAST                'home_data'
              400  LOAD_ATTR                persist_assignment_in_household_inventory
          402_404  POP_JUMP_IF_FALSE   434  'to 434'

 L. 499       406  LOAD_GLOBAL              build_buy
              408  LOAD_METHOD              is_household_inventory_available
              410  LOAD_FAST                'owner_household_id'
              412  CALL_METHOD_1         1  '1 positional argument'
          414_416  POP_JUMP_IF_FALSE   434  'to 434'

 L. 500       418  LOAD_GLOBAL              build_buy
              420  LOAD_METHOD              object_exists_in_household_inventory
              422  LOAD_FAST                'obj_id_to_check'
              424  LOAD_FAST                'owner_household_id'
              426  CALL_METHOD_2         2  '2 positional arguments'
          428_430  POP_JUMP_IF_FALSE   434  'to 434'

 L. 501       432  CONTINUE            186  'to 186'
            434_0  COME_FROM           428  '428'
            434_1  COME_FROM           414  '414'
            434_2  COME_FROM           402  '402'
            434_3  COME_FROM           394  '394'

 L. 502       434  LOAD_FAST                'animal'
              436  LOAD_CONST               None
              438  COMPARE_OP               is
              440  LOAD_FAST                'assignments_to_delete'
              442  LOAD_FAST                'animal_id'
              444  STORE_SUBSCR     
              446  JUMP_BACK           186  'to 186'
              448  POP_BLOCK        
            450_0  COME_FROM_LOOP      174  '174'

 L. 504       450  SETUP_LOOP          486  'to 486'
              452  LOAD_FAST                'assignments_to_delete'
              454  LOAD_METHOD              items
              456  CALL_METHOD_0         0  '0 positional arguments'
              458  GET_ITER         
              460  FOR_ITER            484  'to 484'
              462  UNPACK_SEQUENCE_2     2 
              464  STORE_FAST               'animal_id'
              466  STORE_FAST               'should_delete_registration'

 L. 505       468  LOAD_FAST                'self'
              470  LOAD_METHOD              remove_animal_assignment
              472  LOAD_FAST                'animal_id'
              474  LOAD_FAST                'should_delete_registration'
              476  CALL_METHOD_2         2  '2 positional arguments'
              478  POP_TOP          
          480_482  JUMP_BACK           460  'to 460'
              484  POP_BLOCK        
            486_0  COME_FROM_LOOP      450  '450'

 L. 506       486  SETUP_LOOP          514  'to 514'
              488  LOAD_FAST                'homeless_animals_to_delete'
              490  GET_ITER         
              492  FOR_ITER            512  'to 512'
              494  STORE_FAST               'animal'

 L. 507       496  LOAD_FAST                'animal'
              498  LOAD_ATTR                destroy
              500  LOAD_STR                 'Destroying homeless unowned animals on load.'
              502  LOAD_CONST               ('cause',)
              504  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              506  POP_TOP          
          508_510  JUMP_BACK           492  'to 492'
              512  POP_BLOCK        
            514_0  COME_FROM_LOOP      486  '486'

 L. 511       514  BUILD_LIST_0          0 
              516  STORE_FAST               'homes_to_delete'

 L. 512       518  SETUP_LOOP          610  'to 610'
              520  LOAD_FAST                'self'
              522  LOAD_ATTR                _registered_homes
              524  LOAD_METHOD              items
              526  CALL_METHOD_0         0  '0 positional arguments'
              528  GET_ITER         
            530_0  COME_FROM           590  '590'
              530  FOR_ITER            608  'to 608'
              532  UNPACK_SEQUENCE_2     2 
              534  STORE_FAST               'home_id'
              536  STORE_FAST               'home_data'

 L. 513       538  LOAD_FAST                'home_data'
              540  LOAD_ATTR                zone_id
              542  LOAD_DEREF               'zone_id'
              544  COMPARE_OP               !=
          546_548  POP_JUMP_IF_FALSE   566  'to 566'
              550  LOAD_FAST                'home_data'
              552  LOAD_ATTR                open_street_id
              554  LOAD_DEREF               'street_id'
              556  COMPARE_OP               !=
          558_560  POP_JUMP_IF_FALSE   566  'to 566'

 L. 514   562_564  CONTINUE            530  'to 530'
            566_0  COME_FROM           558  '558'
            566_1  COME_FROM           546  '546'

 L. 515       566  LOAD_FAST                'obj_manager'
              568  LOAD_METHOD              get
              570  LOAD_FAST                'home_id'
              572  CALL_METHOD_1         1  '1 positional argument'
              574  LOAD_CONST               None
              576  COMPARE_OP               is-not
          578_580  POP_JUMP_IF_FALSE   586  'to 586'

 L. 516   582_584  CONTINUE            530  'to 530'
            586_0  COME_FROM           578  '578'

 L. 517       586  LOAD_FAST                'home_data'
              588  LOAD_ATTR                current_occupancy
          590_592  POP_JUMP_IF_TRUE    530  'to 530'

 L. 518       594  LOAD_FAST                'homes_to_delete'
              596  LOAD_METHOD              append
              598  LOAD_FAST                'home_id'
              600  CALL_METHOD_1         1  '1 positional argument'
              602  POP_TOP          
          604_606  JUMP_BACK           530  'to 530'
              608  POP_BLOCK        
            610_0  COME_FROM_LOOP      518  '518'

 L. 519       610  SETUP_LOOP          634  'to 634'
              612  LOAD_FAST                'homes_to_delete'
              614  GET_ITER         
              616  FOR_ITER            632  'to 632'
              618  STORE_FAST               'home_id'

 L. 520       620  LOAD_FAST                'self'
              622  LOAD_ATTR                _registered_homes
              624  LOAD_FAST                'home_id'
              626  DELETE_SUBSCR    
          628_630  JUMP_BACK           616  'to 616'
              632  POP_BLOCK        
            634_0  COME_FROM_LOOP      610  '610'

Parse error at or near `LOAD_DICTCOMP' instruction at offset 144

    def on_build_buy_exit(self):
        self.fixup_objs_destroyed_in_bb()
        num_empty_homes_populated = 0
        for home_id in self._home_ids_registered_in_bb:
            home = services.object_manager().get(home_id)
            if home is None:
                continue
            if num_empty_homes_populated >= self.MAX_EMPTY_HOMES_TO_POPULATE.on_new_homes:
                break
            if not home.has_component(ANIMAL_HOME_COMPONENT):
                logger.error('Registered home {} does not have an Animal Home Component.', home)
                continue
            if home.animalhome_component.try_populate_on_build_buy_exit():
                num_empty_homes_populated += 1

        self._home_ids_registered_in_bb.clear()

    def register_home(self, home):
        home_component = home.get_component(ANIMAL_HOME_COMPONENT)
        if home_component is None:
            logger.error('Home {} should have AnimalHomeComponent.', home)
            return False
        home_id = home.id
        zone = services.current_zone()
        new_home = AnimalHomeData(home_id, home_component.get_max_capacity(), home_component.get_eligible_animal_types(), home_component.persist_assignment_in_household_inventory, home.get_household_owner_id(), services.current_zone_id(), zone.open_street_id if zone is not None else None)
        self._registered_homes[home_id] = new_home
        if services.current_zone().is_in_build_buy:
            self._home_ids_registered_in_bb.append(home_id)
        self._update_home_tooltip(home_id)
        name_component = home.get_component(NAME_COMPONENT)
        if name_component is not None:
            name_component.add_name_changed_callback(self._on_home_name_changed)
        return True

    def is_registered_home(self, home_id):
        return home_id in self._registered_homes

    def _update_home_tooltip(self, home_id):
        home_obj = services.object_manager().get(home_id)
        home_data = self._registered_homes[home_id]
        if home_obj is not None:
            if home_obj.has_component(TOOLTIP_COMPONENT):
                home_obj.animalhome_component.update_tooltip(home_data.current_occupancy_by_type)

    def _move_animal_home(self, animal_id, home_data=None):
        prev_home = self._animal_assignment_map.get(animal_id)
        animal_type = self._registered_animals.get(animal_id)
        if animal_type is None:
            logger.error('Object ID {} is not a registered animal.', animal_id)
            return
        if prev_home is not None:
            prev_home.update_occupancy(animal_type, add=False)
            self._update_home_tooltip(prev_home.id)
        self._animal_assignment_map[animal_id] = home_data
        if home_data is not None:
            home_data.update_occupancy(animal_type, add=True)
            self._update_home_tooltip(home_data.id)
        animal = services.object_manager().get(animal_id)
        if animal is not None:
            animal.on_hovertip_requested()

    def _is_valid_for_assignment(self, home, animal):
        if home is None:
            return True
        home_data = self._registered_homes.get(home.id)
        if home_data is None:
            logger.error('Obj {} is not a registered home in the AnimalService.', home)
            return False
        if animal is None:
            logger.error('Animal id {} is not currently instantiated.', animal)
            return False
        if animal.animalobject_component.creature_type not in home_data.animal_types:
            logger.error('Trying to assign animal {} of invalid type {} to home {}', animal, animal.animalobject_component.creature_type, home)
            return False
        if home_data.current_occupancy >= home_data.max_occupancy:
            return False
        return True

    def _is_obj_destroyed_in_bb(self, obj_id):
        destroy_count = self._objs_destroyed_in_bb.get(obj_id, 0)
        if destroy_count > 0:
            return True
        return False

    def _is_obj_modified_in_bb(self, obj_id):
        if obj_id not in self._objs_destroyed_in_bb:
            return False
        return self._objs_destroyed_in_bb[obj_id] <= 0

    def assign_animal(self, animal_id, home=None):
        animal = services.object_manager().get(animal_id) or services.inventory_manager().get(animal_id)
        if animal_id not in self._animal_assignment_map:
            animal is None or animal.has_component(ANIMAL_OBJECT_COMPONENT) or logger.error('Obj id {} does not map to a valid animal.', animal_id)
            return False
        if not self._is_valid_for_assignment(home, animal):
            if animal_id in self._registered_animals:
                return
        if animal_id not in self._registered_animals:
            self._registered_animals[animal_id] = animal.animalobject_component.creature_type
        home_data = self._registered_homes.get(home.id) if home is not None else None
        self._move_animal_home(animal_id, home_data)
        return True

    def remove_animal_assignment(self, animal_id, should_delete_registration=False):
        animal_type = self._registered_animals.get(animal_id)
        home_data = self._animal_assignment_map.pop(animal_id, None)
        if animal_type is None or home_data is None:
            return
        if should_delete_registration:
            del self._registered_animals[animal_id]
        home_data.update_occupancy(animal_type, add=False)
        home_id = home_data.id
        self._update_home_tooltip(home_id)
        if not home_data.current_occupancy:
            home_obj = services.object_manager().get(home_id)
            if home_obj is not None:
                if home_obj.has_component(ANIMAL_HOME_COMPONENT):
                    home_obj.animalhome_component.try_populate_on_last_inhabitant_removed()

    def transfer_animal_assignment(self, old_animal_id, new_animal_id):
        home_data = self._animal_assignment_map.get(old_animal_id)
        self._move_animal_home(old_animal_id, None)
        self._move_animal_home(new_animal_id, home_data)

    def get_assigned_animal_ids(self, home_id=None):

        def is_assigned(home_data):
            return home_id is None or home_data is not None and home_id == home_data.id

        animal_map = self._animal_assignment_map.items()
        return [animal_id for animal_id, home_data in animal_map if is_assigned(home_data)]

    def get_homeless_animal_ids(self):
        animal_map = self._animal_assignment_map.items()
        return [animal_id for animal_id, home_data in animal_map if home_data is None]

    def get_homeless_animal_objs(self, animal_type=None, max_amount=None):
        animal_ids = self.get_homeless_animal_ids()
        obj_manager = services.object_manager()
        return_list = []
        for animal_id in animal_ids:
            animal_object = obj_manager.get(animal_id)
            if animal_object is None:
                continue
            if not animal_type is None:
                if animal_type == animal_object.animalobject_component.animal_type_tuning.creature_type:
                    return_list.append(animal_object)
                if max_amount is not None and max_amount == len(return_list):
                    break

        return return_list

    def get_animal_home_id(self, animal_id):
        home_data = self._animal_assignment_map.get(animal_id)
        if home_data is None:
            return
        return home_data.id

    def get_animal_home_max_capacity(self, object_id):
        home_data = self._animal_assignment_map.get(object_id) or self._registered_homes.get(object_id)
        if home_data is None:
            return
        return home_data.max_occupancy

    def get_current_occupancy(self, home_id):
        home_data = self._registered_homes.get(home_id)
        if home_data is None:
            logger.error('Home ID {} is not registered with the AnimalService.', home_id)
            return
        return home_data.current_occupancy

    def find_home_obj_with_vacancy(self, animal_obj):
        for home_obj in services.object_manager().get_all_objects_with_component_gen(ANIMAL_HOME_COMPONENT):
            if self._is_valid_for_assignment(home_obj, animal_obj):
                return home_obj

    def get_animal_home_obj(self, animal):
        home_id = self.get_animal_home_id(animal.id)
        if home_id is None:
            return
        animal_home = services.object_manager().get(home_id) or services.inventory_manager().get(home_id)
        return animal_home

    def get_animal_home_assignee_objs(self, home):
        if home is None:
            return
        else:
            home.has_component(ANIMAL_HOME_COMPONENT) or logger.error('Provided home object {} does not have an Animal Home Component.', home)
            return
        obj_manager = services.object_manager()
        inventory_manager = services.inventory_manager()

        def get_obj(assigned_animal_id):
            return obj_manager.get(assigned_animal_id) or inventory_manager.get(assigned_animal_id)

        animal_objs = set((get_obj(animal_id) for animal_id in self.get_assigned_animal_ids(home.id)))
        animal_objs.discard(None)
        return animal_objs

    def add_weed_eligible_plant(self, plant_obj):
        if not plant_obj.has_component(STATE_COMPONENT):
            return
        plant_obj.add_state_changed_callback(self._on_plant_object_state_changed)
        self._weed_eligible_plants.append(plant_obj)

    def remove_weed_eligible_plant(self, plant_obj):
        if not plant_obj.has_component(STATE_COMPONENT):
            return
        if plant_obj in self._weed_eligible_plants:
            plant_obj.remove_state_changed_callback(self._on_plant_object_state_changed)
            self._weed_eligible_plants.remove(plant_obj)

    def _on_plant_object_state_changed(self, owner, state, old_value, new_value):
        if old_value == new_value:
            return
        if new_value not in self.GARDENING_HELP_WEED_STATES:
            return
        all_animals_gen = services.object_manager().get_all_objects_with_component_gen(ANIMAL_OBJECT_COMPONENT)
        gardening_help_animals = [animal for animal in all_animals_gen if animal.state_value_active(self.GARDENING_HELP_STATE)]
        if len(gardening_help_animals) == 0:
            return
        for entry in self.GARDENING_HELP_ANIMAL_STATES:
            animals_of_matching_type = [animal for animal in gardening_help_animals if animal.animalobject_component.animal_type_tuning.creature_type == entry.animal_type]
            for state_pair in entry.states:
                animals_of_matching_state = [animal for animal in animals_of_matching_type if animal.state_value_active(state_pair.from_state)]
                if len(animals_of_matching_state) == 0:
                    continue
                animal = random.choice(animals_of_matching_state)
                animal.set_state(state_pair.to_state.state, state_pair.to_state)
                return

    def _toggle_destroyed_obj(self, obj_id, should_destroy):
        if services.current_zone().is_in_build_buy:
            is_obj_already_destroyed = self._objs_destroyed_in_bb.get(obj_id, 0)
            destroy_op = 1 if should_destroy else -1
            self._objs_destroyed_in_bb[obj_id] = is_obj_already_destroyed + destroy_op

    def on_home_destroyed(self, home_id):
        self._toggle_destroyed_obj(home_id, should_destroy=True)
        if not services.current_zone().is_in_build_buy:
            for animal_id in self.get_assigned_animal_ids(home_id):
                self.assign_animal(animal_id, None)

            del self._registered_homes[home_id]

    def on_home_added(self, home_id):
        self._toggle_destroyed_obj(home_id, should_destroy=False)
        home_data = self._registered_homes.get(home_id)
        if home_data is None:
            home = services.object_manager().get(home_id)
            if home is None:
                logger.error('An unregistered home with ID {} should be instantiated.', home_id)
            self.register_home(home)
            zone = services.current_zone()
            if zone is not None:
                if zone.is_zone_loading:
                    self._delayed_home_updates.add(home_id)
            return
        home_data.update(home_id)
        self._update_home_tooltip(home_id)

    def _on_home_name_changed(self, home_object):
        animal_objs = self.get_animal_home_assignee_objs(home_object)
        if animal_objs is None:
            return
        for animal in animal_objs:
            animal.update_object_tooltip()

    def on_animal_destroyed(self, animal_id):
        self._toggle_destroyed_obj(animal_id, should_destroy=True)
        if not services.current_zone().is_in_build_buy:
            self.remove_animal_assignment(animal_id)

    def on_animal_added(self, animal_id):
        self._toggle_destroyed_obj(animal_id, should_destroy=False)
        if services.object_manager().get(animal_id) is None:
            return
        if animal_id not in self._animal_assignment_map:
            self.assign_animal(animal_id, home=None)

    def fixup_objs_destroyed_in_bb(self):
        if not self._objs_destroyed_in_bb:
            return
        ids_to_clear = []
        obj_manager = services.object_manager()
        for animal_id, home_data in self._animal_assignment_map.items():
            if home_data is None:
                continue
            home_id = home_data.id
            if self._is_obj_destroyed_in_bb(home_id):
                ids_to_clear.append(animal_id)
                continue
            if home_data.persist_assignment_in_household_inventory or self._is_obj_modified_in_bb(animal_id) or self._is_obj_modified_in_bb(home_id):
                animal = obj_manager.get(animal_id)
                home = obj_manager.get(home_id)
                if animal is None or home is None:
                    ids_to_clear.append(animal_id)

        for animal_id in ids_to_clear:
            self.assign_animal(animal_id, None)

        registrations_to_clear = []
        for obj_id, destroyed_count in self._objs_destroyed_in_bb.items():
            if not destroyed_count:
                if obj_id in self._home_ids_registered_in_bb:
                    if obj_manager.get(obj_id) is None:
                        del self._registered_homes[obj_id]
                        self._home_ids_registered_in_bb.remove(obj_id)
                if destroyed_count > 0:
                    if obj_id in self._animal_assignment_map:
                        self.remove_animal_assignment(obj_id)
                    elif obj_id in self._registered_homes:
                        del self._registered_homes[obj_id]

        self._objs_destroyed_in_bb.clear()

    def _start_auto_assignment_schedules(self):
        for auto_assignment_schedule in self.AUTO_ASSIGN_NEW_INHABITANTS:
            active_weekly_schedule = auto_assignment_schedule.weekly_schedule(start_callback=(self._auto_assign_new_inhabitants_from_schedule),
              extra_data={'animal_type':auto_assignment_schedule.animal_type, 
             'num_assignments_per_home':auto_assignment_schedule.num_assignments_per_home, 
             'max_homes_to_assign':auto_assignment_schedule.max_homes_to_assign, 
             'tests':auto_assignment_schedule.tests})
            self._active_weekly_schedules.append(active_weekly_schedule)

    def _stop_auto_assignment_schedules(self):
        for active_weekly_schedule in self._active_weekly_schedules:
            active_weekly_schedule.destroy()

        self._active_weekly_schedules.clear()

    def _auto_assign_new_inhabitants_from_schedule(self, scheduler, alarm_data, extra_data):
        animal_type = extra_data.get('animal_type')
        num_assignments_per_home = extra_data.get('num_assignments_per_home')
        max_homes_to_assign = extra_data.get('max_homes_to_assign')
        tests = extra_data.get('tests')
        self._auto_assign_new_inhabitants(animal_type, num_assignments_per_home, max_homes_to_assign, tests)

    def _auto_assign_new_inhabitants(self, animal_type, num_assignments_per_home, max_homes_to_assign, tests):

        def _pick_homes(inner_animal_type, num_homes_to_assign):
            if num_homes_to_assign == 0:
                return []
            eligible_homes = []
            for animal_home_obj in services.object_manager().get_all_objects_with_component_gen(ANIMAL_HOME_COMPONENT):
                current_occupancy = self.get_current_occupancy(animal_home_obj.id)
                if inner_animal_type in animal_home_obj.animalhome_component.get_eligible_animal_types() and current_occupancy < animal_home_obj.animalhome_component.get_max_capacity():
                    eligible_homes.append(animal_home_obj)

            if len(eligible_homes) > num_homes_to_assign:
                return random.sample(eligible_homes, num_homes_to_assign)
            return eligible_homes

        def _assign_inhabitants(inner_home, inner_animal_type, num_assignments):
            if num_assignments == 0:
                return
            current_occupancy = self.get_current_occupancy(inner_home.id)
            num_assignments = min(num_assignments, inner_home.animalhome_component.get_max_capacity() - current_occupancy)
            homeless_animals = self.get_homeless_animal_objs(inner_animal_type, num_assignments)
            for homeless_animal in homeless_animals:
                self.assign_animal(homeless_animal.id, inner_home)

            remaining_assignments = num_assignments - len(homeless_animals)
            for i in range(remaining_assignments):
                inner_home.animalhome_component.create_inhabitant()

        if not tests.run_tests(GlobalResolver()):
            return
        homes = _pick_homes(animal_type, max_homes_to_assign.random_int())
        for home in homes:
            _assign_inhabitants(home, animal_type, num_assignments_per_home.random_int())