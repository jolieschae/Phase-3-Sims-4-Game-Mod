# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\adoption\adoption_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 11829 bytes
from _collections import defaultdict
from contextlib import contextmanager
import itertools
from protocolbuffers import GameplaySaveData_pb2
from cas.cas import generate_random_siminfo
from date_and_time import DateAndTime
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from sims.household_enums import HouseholdChangeOrigin
from sims.pets.breed_tuning import get_random_breed_tag, try_conform_sim_info_to_breed
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from sims.sim_spawner import SimSpawner, SimCreator
from sims4.service_manager import Service
from sims4.tuning.tunable import TunableSimMinute, TunableList, TunableTuple, Tunable
from sims4.utils import classproperty
from traits.traits import Trait
import persistence_error_types, services, sims4

class AdoptionService(Service):
    PET_ADOPTION_CATALOG_LIFETIME = TunableSimMinute(description='\n        The amount of time in Sim minutes before a pet Sim is removed from the adoption catalog.\n        ',
      default=60,
      minimum=0)
    PET_ADOPTION_GENDER_OPTION_TRAITS = TunableList(description='\n        List of gender option traits from which one will be applied to generated\n        Pets based on the tuned weights.\n        ',
      tunable=TunableTuple(description='\n            A weighted gender option trait that might be applied to the\n            generated Pet.\n            ',
      weight=Tunable(description='\n                The relative weight of this trait.\n                ',
      tunable_type=float,
      default=1),
      trait=Trait.TunableReference(description='\n                A gender option trait that might be applied to the generated\n                Pet.\n                ',
      pack_safe=True)))

    def __init__(self):
        self._sim_infos = defaultdict(list)
        self._real_sim_ids = None
        self._creation_times = {}

    @classproperty
    def save_error_code(cls):
        return persistence_error_types.ErrorCodes.SERVICE_SAVE_FAILED_ADOPTION_SERVICE

    def timeout_real_sim_infos(self):
        sim_now = services.time_service().sim_now
        for sim_id in tuple(self._creation_times.keys()):
            elapsed_time = (sim_now - self._creation_times[sim_id]).in_minutes()
            if elapsed_time > self.PET_ADOPTION_CATALOG_LIFETIME:
                del self._creation_times[sim_id]

    def save(self, save_slot_data=None, **kwargs):
        self.timeout_real_sim_infos()
        adoption_service_proto = GameplaySaveData_pb2.PersistableAdoptionService()
        for sim_id, creation_time in self._creation_times.items():
            with ProtocolBufferRollback(adoption_service_proto.adoptable_sim_data) as (msg):
                msg.adoptable_sim_id = sim_id
                msg.creation_time = creation_time.absolute_ticks()

        save_slot_data.gameplay_data.adoption_service = adoption_service_proto

    def on_all_households_and_sim_infos_loaded(self, _):
        save_slot_data = services.get_persistence_service().get_save_slot_proto_buff()
        sim_info_manager = services.sim_info_manager()
        for sim_data in save_slot_data.gameplay_data.adoption_service.adoptable_sim_data:
            sim_info = sim_info_manager.get(sim_data.adoptable_sim_id)
            if sim_info is None:
                continue
            self._creation_times[sim_data.adoptable_sim_id] = DateAndTime(sim_data.creation_time)

    def stop(self):
        self._sim_infos.clear()
        self._creation_times.clear()

    def add_sim_info--- This code section failed: ---

 L. 121         0  LOAD_FAST                'age'
                2  LOAD_FAST                'gender'
                4  LOAD_FAST                'species'
                6  BUILD_TUPLE_3         3 
                8  STORE_FAST               'key'

 L. 123        10  LOAD_GLOBAL              SimInfoBaseWrapper
               12  LOAD_FAST                'age'
               14  LOAD_FAST                'gender'
               16  LOAD_FAST                'species'
               18  LOAD_CONST               ('age', 'gender', 'species')
               20  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               22  STORE_DEREF              'sim_info'

 L. 125        24  LOAD_GLOBAL              generate_random_siminfo
               26  LOAD_DEREF               'sim_info'
               28  LOAD_ATTR                _base
               30  CALL_FUNCTION_1       1  '1 positional argument'
               32  POP_TOP          

 L. 127        34  LOAD_GLOBAL              get_random_breed_tag
               36  LOAD_FAST                'species'
               38  CALL_FUNCTION_1       1  '1 positional argument'
               40  STORE_FAST               'breed_tag'

 L. 128        42  LOAD_FAST                'breed_tag'
               44  LOAD_CONST               None
               46  COMPARE_OP               is-not
               48  POP_JUMP_IF_FALSE    60  'to 60'

 L. 129        50  LOAD_GLOBAL              try_conform_sim_info_to_breed
               52  LOAD_DEREF               'sim_info'
               54  LOAD_FAST                'breed_tag'
               56  CALL_FUNCTION_2       2  '2 positional arguments'
               58  POP_TOP          
             60_0  COME_FROM            48  '48'

 L. 131        60  LOAD_GLOBAL              services
               62  LOAD_METHOD              get_instance_manager
               64  LOAD_GLOBAL              sims4
               66  LOAD_ATTR                resources
               68  LOAD_ATTR                Types
               70  LOAD_ATTR                TRAIT
               72  CALL_METHOD_1         1  '1 positional argument'
               74  STORE_DEREF              'trait_manager'

 L. 132        76  LOAD_CLOSURE             'trait_manager'
               78  BUILD_TUPLE_1         1 
               80  LOAD_SETCOMP             '<code_object <setcomp>>'
               82  LOAD_STR                 'AdoptionService.add_sim_info.<locals>.<setcomp>'
               84  MAKE_FUNCTION_8          'closure'
               86  LOAD_DEREF               'sim_info'
               88  LOAD_ATTR                trait_ids
               90  GET_ITER         
               92  CALL_FUNCTION_1       1  '1 positional argument'
               94  STORE_FAST               'traits'

 L. 136        96  LOAD_DEREF               'sim_info'
               98  LOAD_ATTR                is_pet
              100  POP_JUMP_IF_FALSE   152  'to 152'

 L. 137       102  LOAD_CLOSURE             'sim_info'
              104  BUILD_TUPLE_1         1 
              106  LOAD_LISTCOMP            '<code_object <listcomp>>'
              108  LOAD_STR                 'AdoptionService.add_sim_info.<locals>.<listcomp>'
              110  MAKE_FUNCTION_8          'closure'
              112  LOAD_FAST                'self'
              114  LOAD_ATTR                PET_ADOPTION_GENDER_OPTION_TRAITS
              116  GET_ITER         
              118  CALL_FUNCTION_1       1  '1 positional argument'
              120  STORE_FAST               'gender_option_traits'

 L. 140       122  LOAD_GLOBAL              sims4
              124  LOAD_ATTR                random
              126  LOAD_METHOD              weighted_random_item
              128  LOAD_FAST                'gender_option_traits'
              130  CALL_METHOD_1         1  '1 positional argument'
              132  STORE_FAST               'selected_trait'

 L. 141       134  LOAD_FAST                'selected_trait'
              136  LOAD_CONST               None
              138  COMPARE_OP               is-not
              140  POP_JUMP_IF_FALSE   152  'to 152'

 L. 142       142  LOAD_FAST                'traits'
              144  LOAD_METHOD              add
              146  LOAD_FAST                'selected_trait'
              148  CALL_METHOD_1         1  '1 positional argument'
              150  POP_TOP          
            152_0  COME_FROM           140  '140'
            152_1  COME_FROM           100  '100'

 L. 144       152  LOAD_DEREF               'sim_info'
              154  LOAD_ATTR                set_trait_ids_on_base
              156  LOAD_GLOBAL              list
              158  LOAD_GENEXPR             '<code_object <genexpr>>'
              160  LOAD_STR                 'AdoptionService.add_sim_info.<locals>.<genexpr>'
              162  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              164  LOAD_FAST                'traits'
              166  GET_ITER         
              168  CALL_FUNCTION_1       1  '1 positional argument'
              170  CALL_FUNCTION_1       1  '1 positional argument'
              172  LOAD_CONST               ('trait_ids_override',)
              174  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              176  POP_TOP          

 L. 147       178  LOAD_GLOBAL              SimSpawner
              180  LOAD_METHOD              get_random_first_name
              182  LOAD_FAST                'gender'
              184  LOAD_FAST                'species'
              186  CALL_METHOD_2         2  '2 positional arguments'
              188  LOAD_DEREF               'sim_info'
              190  STORE_ATTR               first_name

 L. 150       192  LOAD_GLOBAL              services
              194  LOAD_METHOD              sim_info_manager
              196  CALL_METHOD_0         0  '0 positional arguments'
              198  LOAD_DEREF               'sim_info'
              200  STORE_ATTR               manager

 L. 151       202  LOAD_GLOBAL              Distributor
              204  LOAD_METHOD              instance
              206  CALL_METHOD_0         0  '0 positional arguments'
              208  LOAD_METHOD              add_object
              210  LOAD_DEREF               'sim_info'
              212  CALL_METHOD_1         1  '1 positional argument'
              214  POP_TOP          

 L. 152       216  LOAD_FAST                'self'
              218  LOAD_ATTR                _sim_infos
              220  LOAD_FAST                'key'
              222  BINARY_SUBSCR    
              224  LOAD_METHOD              append
              226  LOAD_DEREF               'sim_info'
              228  CALL_METHOD_1         1  '1 positional argument'
              230  POP_TOP          

Parse error at or near `LOAD_SETCOMP' instruction at offset 80

    def add_real_sim_info(self, sim_info):
        self._creation_times[sim_info.sim_id] = services.time_service().sim_now

    def get_sim_info(self, sim_id):
        for sim_info in itertools.chain.from_iterable(self._sim_infos.values()):
            if sim_info.sim_id == sim_id:
                return sim_info

        for adoptable_sim_id in self._creation_times.keys():
            if sim_id == adoptable_sim_id:
                return services.sim_info_manager().get(adoptable_sim_id)

    @contextmanager
    def real_sim_info_cache(self):
        self.timeout_real_sim_infos()
        self._real_sim_ids = defaultdict(list)
        sim_info_manager = services.sim_info_manager()
        for sim_id in self._creation_times.keys():
            sim_info = sim_info_manager.get(sim_id)
            key = (sim_info.age, sim_info.gender, sim_info.species)
            self._real_sim_ids[key].append(sim_id)

        try:
            yield
        finally:
            self._real_sim_ids.clear()
            self._real_sim_ids = None

    def get_sim_infos(self, interval, age, gender, species):
        key = (
         age, gender, species)
        real_sim_count = len(self._real_sim_ids[key]) if self._real_sim_ids is not None else 0
        entry_count = len(self._sim_infos[key]) + real_sim_count
        if entry_count < interval.lower_bound:
            while entry_count < interval.upper_bound:
                self.add_sim_info(age, gender, species)
                entry_count += 1

        real_sim_infos = []
        if self._real_sim_ids is not None:
            sim_info_manager = services.sim_info_manager()
            for sim_id in tuple(self._real_sim_ids[key]):
                sim_info = sim_info_manager.get(sim_id)
                if sim_info is not None:
                    real_sim_infos.append(sim_info)

        return tuple(itertools.chainself._sim_infos[key]real_sim_infos)

    def remove_sim_info(self, sim_info):
        for sim_infos in self._sim_infos.values():
            if sim_info in sim_infos:
                sim_infos.remove(sim_info)

        if sim_info.sim_id in self._creation_times:
            del self._creation_times[sim_info.sim_id]

    def create_adoption_sim_info(self, sim_info, household=None, account=None, zone_id=None):
        sim_creator = SimCreator(age=(sim_info.age), gender=(sim_info.gender),
          species=(sim_info.extended_species),
          first_name=(sim_info.first_name),
          last_name=(sim_info.last_name))
        sim_info_list, new_household = SimSpawner.create_sim_infos((sim_creator,), household=household,
          account=account,
          zone_id=0,
          creation_source='adoption',
          household_change_origin=(HouseholdChangeOrigin.ADOPTION))
        SimInfoBaseWrapper.copy_physical_attributessim_info_list[0]sim_info
        sim_info_list[0].pelt_layers = sim_info.pelt_layers
        sim_info_list[0].breed_name_key = sim_info.breed_name_key
        sim_info_list[0].load_outfits(sim_info.save_outfits())
        sim_info_list[0].resend_physical_attributes()
        return (
         sim_info_list[0], new_household)

    def convert_base_sim_info_to_full(self, sim_id):
        current_sim_info = self.get_sim_info(sim_id)
        if current_sim_info is None:
            return
        new_sim_info, new_household = self.create_adoption_sim_info(current_sim_info)
        new_household.set_to_hidden()
        self.remove_sim_info(current_sim_info)
        self.add_real_sim_info(new_sim_info)
        return new_sim_info