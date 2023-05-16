# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\stored_sim_info_component.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 19939 bytes
import tag
from event_testing.resolver import SingleActorAndObjectResolver
from event_testing.test_events import TestEvent
from objects.object_enums import ResetReason
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from interactions import ParticipantType
from interactions.utils.interaction_elements import XevtTriggeredElement
from interactions.utils.loot_basic_op import BaseTargetedLootOperation, BaseLootOperation
from interactions.utils.loot_ops import RemoveTraitLootOp
from objects.components import Component, types, componentmethod_with_fallback
from sims.sim_info_name_data import SimInfoNameData
from sims4.tuning.tunable import AutoFactoryInit, HasTunableFactory, TunableEnumEntry, OptionalTunable, Tunable, TunableList, TunableVariant, TunableMapping
import services, sims4, zone_types
logger = sims4.log.Logger('Stored Sim Info Component', default_owner='shipark')

class TransferStoredSimInfo(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'clear_stored_sim_on_subject': Tunable(description='\n            If set to False, the Stored Sim will remain on the subject object. If\n            set to True, the Store Sim will be removed from the subject object.\n            ',
                                      tunable_type=bool,
                                      default=False)}

    def __init__(self, *args, clear_stored_sim_on_subject=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._clear_stored_sim_on_subject = clear_stored_sim_on_subject

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error("The Transfer Stored Sim Info loot tuned on: '{}' has a subject participant of None value.", self)
            return
        stored_sim_info = subject.get_component(types.STORED_SIM_INFO_COMPONENT)
        if stored_sim_info is None:
            logger.error("The Transfer Stored Sim Info loot tuned on interaction: '{}' has a subject with no Stored Sim Info Component.", self)
            return
        if target is None:
            logger.error("The Transfer Stored Sim Info loot tuned on interaction: '{}' has a target participant of None value.", self)
            return
        if target.has_component(types.STORED_SIM_INFO_COMPONENT):
            target.remove_component(types.STORED_SIM_INFO_COMPONENT)
        target.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(stored_sim_info.get_stored_sim_id()))
        if self._clear_stored_sim_on_subject:
            subject.remove_component(types.STORED_SIM_INFO_COMPONENT)


class StoreSimInfoLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'replace_current': Tunable(description="\n            If there is a StoredSimInfoComponent on the subject, it will be replaced when this operation is called.\n            If the intent is to add an additional stored SimInfo, uncheck this box.\n            Note: If multiple SimInfo's are stored, you must use StoredSimOrNameDataList to access the data.\n            ",
                          tunable_type=bool,
                          default=True)}

    def __init__(self, replace_current, **kwargs):
        (super().__init__)(**kwargs)
        self._replace_current = replace_current

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None or target is None:
            logger.error('Trying to run Store Sim Info loot action with a None Subject and/or Target. subject:{}, target:{}', subject, target)
            return
        elif not target.is_sim:
            logger.error('Trying to run Store Sim Info loot action on Subject {} with a non Sim Target {}', subject, target)
            return
            if subject.has_component(types.STORED_SIM_INFO_COMPONENT):
                if self._replace_current:
                    subject.remove_component(types.STORED_SIM_INFO_COMPONENT)
                    subject.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(target.sim_id))
                else:
                    stored_sim_info_component = subject.get_component(types.STORED_SIM_INFO_COMPONENT)
                    stored_sim_info_component.add_sim_id_to_list(target.sim_id)
        else:
            subject.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(target.sim_id))


class RemoveSimInfoLootOp(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Trying to run Remove Stored Sim Info loot action with a None Subject')
            return
        if subject.has_component(types.STORED_SIM_INFO_COMPONENT):
            subject.remove_component(types.STORED_SIM_INFO_COMPONENT)


class StoreSimElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description':'\n            An element that retrieves an interaction participant and attaches\n            its information to another interaction participant using a dynamic\n            StoredSimInfoComponent.\n            ', 
     'source_participant':OptionalTunable(description='\n            Specify what participant to store on the destination participant.\n            ',
       tunable=TunableEnumEntry(description='\n                The participant of this interaction whose Sim Info is retrieved\n                to be stored as a component.\n                ',
       tunable_type=ParticipantType,
       default=(ParticipantType.PickedObject),
       invalid_enums=(
      ParticipantType.StoredSimOrNameDataList,)),
       enabled_name='specific_participant',
       disabled_name='no_participant'), 
     'destination_participant':TunableEnumEntry(description='\n            The participant of this interaction to which a\n            StoredSimInfoComponent is added, with the Sim Info of\n            source_participant.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'replace_current':Tunable(description="\n            If there is a StoredSimInfoComponent on the subject, it will be replaced when this operation is called.\n            If the intent is to add an additional stored SimInfo, uncheck this box.\n            Note: If multiple SimInfo's are stored, you must use StoredSimOrNameDataList to access the data.\n            ",
       tunable_type=bool,
       default=True)}

    def _do_behavior(self):
        source = self.interaction.get_participant(participant_type=(self.source_participant)) if self.source_participant is not None else None
        destination = self.interaction.get_participant(participant_type=(self.destination_participant))
        if source is not None:
            if destination is not None:
                if destination.has_component(types.STORED_SIM_INFO_COMPONENT):
                    if self.replace_current:
                        destination.remove_component(types.STORED_SIM_INFO_COMPONENT)
                        destination.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(source.id))
                    else:
                        stored_sim_info_component = destination.get_component(types.STORED_SIM_INFO_COMPONENT)
                        stored_sim_info_component.add_sim_id_to_list(source.id)
                else:
                    destination.add_dynamic_component((types.STORED_SIM_INFO_COMPONENT), sim_id=(source.id))


class StoredSimInfoComponent(Component, component_name=types.STORED_SIM_INFO_COMPONENT, allow_dynamic=True, persistence_key=protocols.PersistenceMaster.PersistableData.StoredSimInfoComponent):
    LOOTS_ON_OBJECT_REMOVE = TunableMapping(description='\n        A mapping of object tag to loots. A list of loots will be apply to the object \n        that has the stored sim component when the object is removed.\n        ',
      key_type=TunableEnumEntry(description='\n            what object to run loots.\n            ',
      tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID),
      pack_safe=True),
      value_type=TunableList(description='\n            loots to apply to the object when object is removed.\n            ',
      tunable=TunableVariant(description='\n                A specific loot to apply.\n                ',
      remove_trait=(RemoveTraitLootOp.TunableFactory()))))

    def __init__(self, *args, sim_id=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim_id_list = []
        if sim_id is not None:
            self._sim_id_list.append(sim_id)
        self._sim_info_name_data_list = []

    def save(self, persistence_master_message):
        persistable_data = protocols.PersistenceMaster.PersistableData()
        persistable_data.type = protocols.PersistenceMaster.PersistableData.StoredSimInfoComponent
        stored_sim_info_component_data = persistable_data.Extensions[protocols.PersistableStoredSimInfoComponent.persistable_data]
        stored_sim_info_component_data.sim_id_list.extend(self._sim_id_list)
        stored_sim_info_component_data.sim_info_name_data_list.extend([SimInfoNameData.generate_sim_info_name_data_msg(sim_info_name_data, use_profanity_filter=False) for sim_info_name_data in self._sim_info_name_data_list])
        persistence_master_message.data.extend([persistable_data])

    def load--- This code section failed: ---

 L. 229         0  LOAD_FAST                'persistable_data'
                2  LOAD_ATTR                Extensions
                4  LOAD_GLOBAL              protocols
                6  LOAD_ATTR                PersistableStoredSimInfoComponent
                8  LOAD_ATTR                persistable_data
               10  BINARY_SUBSCR    
               12  STORE_DEREF              'stored_sim_info_component_data'

 L. 230        14  LOAD_DEREF               'stored_sim_info_component_data'
               16  LOAD_ATTR                sim_id_list
               18  POP_JUMP_IF_FALSE    92  'to 92'

 L. 231        20  LOAD_LISTCOMP            '<code_object <listcomp>>'
               22  LOAD_STR                 'StoredSimInfoComponent.load.<locals>.<listcomp>'
               24  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
               26  LOAD_DEREF               'stored_sim_info_component_data'
               28  LOAD_ATTR                sim_id_list
               30  GET_ITER         
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  LOAD_FAST                'self'
               36  STORE_ATTR               _sim_id_list

 L. 232        38  LOAD_DEREF               'stored_sim_info_component_data'
               40  LOAD_ATTR                sim_info_name_data_list
               42  POP_JUMP_IF_FALSE   238  'to 238'

 L. 233        44  SETUP_LOOP          238  'to 238'
               46  LOAD_DEREF               'stored_sim_info_component_data'
               48  LOAD_ATTR                sim_info_name_data_list
               50  GET_ITER         
               52  FOR_ITER             88  'to 88'
               54  STORE_FAST               '_name_data'

 L. 234        56  LOAD_FAST                'self'
               58  LOAD_ATTR                _sim_info_name_data_list
               60  LOAD_METHOD              append
               62  LOAD_GLOBAL              SimInfoNameData

 L. 235        64  LOAD_FAST                '_name_data'
               66  LOAD_ATTR                gender

 L. 236        68  LOAD_FAST                '_name_data'
               70  LOAD_ATTR                first_name

 L. 237        72  LOAD_FAST                '_name_data'
               74  LOAD_ATTR                last_name

 L. 238        76  LOAD_FAST                '_name_data'
               78  LOAD_ATTR                full_name_key
               80  CALL_FUNCTION_4       4  '4 positional arguments'
               82  CALL_METHOD_1         1  '1 positional argument'
               84  POP_TOP          
               86  JUMP_BACK            52  'to 52'
               88  POP_BLOCK        
               90  JUMP_FORWARD        238  'to 238'
             92_0  COME_FROM            18  '18'

 L. 242        92  LOAD_DEREF               'stored_sim_info_component_data'
               94  LOAD_ATTR                sim_id
               96  BUILD_LIST_1          1 
               98  LOAD_FAST                'self'
              100  STORE_ATTR               _sim_id_list

 L. 243       102  LOAD_FAST                'self'
              104  LOAD_ATTR                _sim_id_list
              106  LOAD_METHOD              extend
              108  LOAD_CLOSURE             'stored_sim_info_component_data'
              110  BUILD_TUPLE_1         1 
              112  LOAD_LISTCOMP            '<code_object <listcomp>>'
              114  LOAD_STR                 'StoredSimInfoComponent.load.<locals>.<listcomp>'
              116  MAKE_FUNCTION_8          'closure'
              118  LOAD_DEREF               'stored_sim_info_component_data'
              120  LOAD_ATTR                sim_id_set
              122  GET_ITER         
              124  CALL_FUNCTION_1       1  '1 positional argument'
              126  CALL_METHOD_1         1  '1 positional argument'
              128  POP_TOP          

 L. 246       130  LOAD_DEREF               'stored_sim_info_component_data'
              132  LOAD_ATTR                sim_info_name_data
              134  POP_JUMP_IF_FALSE   168  'to 168'

 L. 247       136  LOAD_DEREF               'stored_sim_info_component_data'
              138  LOAD_ATTR                sim_info_name_data
              140  STORE_FAST               'sim_info_data'

 L. 248       142  LOAD_GLOBAL              SimInfoNameData
              144  LOAD_FAST                'sim_info_data'
              146  LOAD_ATTR                gender
              148  LOAD_FAST                'sim_info_data'
              150  LOAD_ATTR                first_name
              152  LOAD_FAST                'sim_info_data'
              154  LOAD_ATTR                last_name
              156  LOAD_FAST                'sim_info_data'
              158  LOAD_ATTR                full_name_key
              160  CALL_FUNCTION_4       4  '4 positional arguments'
              162  BUILD_LIST_1          1 
              164  LOAD_FAST                'self'
              166  STORE_ATTR               _sim_info_name_data_list
            168_0  COME_FROM           134  '134'

 L. 249       168  LOAD_DEREF               'stored_sim_info_component_data'
              170  LOAD_ATTR                sim_info_name_data_set
              172  POP_JUMP_IF_FALSE   238  'to 238'

 L. 250       174  SETUP_LOOP          238  'to 238'
              176  LOAD_DEREF               'stored_sim_info_component_data'
              178  LOAD_ATTR                sim_info_name_data_set
              180  GET_ITER         
            182_0  COME_FROM           220  '220'
              182  FOR_ITER            236  'to 236'
              184  STORE_FAST               'sim_info_data'

 L. 251       186  LOAD_GLOBAL              SimInfoNameData

 L. 252       188  LOAD_FAST                'sim_info_data'
              190  LOAD_ATTR                gender

 L. 253       192  LOAD_FAST                'sim_info_data'
              194  LOAD_ATTR                first_name

 L. 254       196  LOAD_FAST                'sim_info_data'
              198  LOAD_ATTR                last_name

 L. 255       200  LOAD_FAST                'sim_info_data'
              202  LOAD_ATTR                full_name_key
              204  CALL_FUNCTION_4       4  '4 positional arguments'
              206  STORE_FAST               'sim_info_namedata'

 L. 256       208  LOAD_FAST                'self'
              210  LOAD_ATTR                _sim_info_name_data_list
              212  LOAD_CONST               0
              214  BINARY_SUBSCR    
              216  LOAD_FAST                'sim_info_namedata'
              218  COMPARE_OP               !=
              220  POP_JUMP_IF_FALSE   182  'to 182'

 L. 257       222  LOAD_FAST                'self'
              224  LOAD_ATTR                _sim_info_name_data_list
              226  LOAD_METHOD              append
              228  LOAD_FAST                'sim_info_namedata'
              230  CALL_METHOD_1         1  '1 positional argument'
              232  POP_TOP          
              234  JUMP_BACK           182  'to 182'
              236  POP_BLOCK        
            238_0  COME_FROM_LOOP      174  '174'
            238_1  COME_FROM           172  '172'
            238_2  COME_FROM            90  '90'
            238_3  COME_FROM_LOOP       44  '44'
            238_4  COME_FROM            42  '42'

Parse error at or near `COME_FROM_LOOP' instruction at offset 238_3

    def on_add(self, *_, **__):
        services.current_zone().register_callback(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED, self._on_households_loaded)

    def _apply_loots_on_object_remove(self):
        if self.LOOTS_ON_OBJECT_REMOVE is None:
            return

        def _apply_loots(sim_id):
            sim_info = services.sim_info_manager().get(sim_id)
            if sim_info is not None:
                resolver = SingleActorAndObjectResolver(sim_info, (self.owner), source=self)
                owner_tags = self.owner.get_tags()
                for tag, loots in self.LOOTS_ON_OBJECT_REMOVE.items():
                    if tag in owner_tags:
                        for loot in loots:
                            loot.apply_to_resolver(resolver)

        for _id in self._sim_id_list:
            _apply_loots(_id)

    def add_sim_id_to_list(self, sim_id):
        if sim_id in self._sim_id_list:
            return
        self._sim_id_list.append(sim_id)

    def on_reset_component_get_interdependent_reset_records(self, reset_reason, reset_records):
        if reset_reason == ResetReason.BEING_DESTROYED:
            if services.current_zone().is_zone_running:
                self._apply_loots_on_object_remove()

    def _on_households_loaded(self, *_, **__):
        sim_info_manager = services.sim_info_manager()
        if len(self._sim_info_name_data_list) == 0:
            for _id in self._sim_id_list:
                sim_info = sim_info_manager.get(_id)
                if sim_info is not None:
                    self._sim_info_name_data_list.append(sim_info.get_name_data())

        self.owner.update_object_tooltip()

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_id(self):
        if len(self._sim_id_list) > 0:
            return self._sim_id_list[0]
        logger.error('The StoredSimComponent on {} does not have a stored sim id.', self.owner)

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_info(self):
        if len(self._sim_id_list) > 0:
            return services.sim_info_manager().get(self._sim_id_list[0])
        logger.error('The StoredSimComponent on {} does not have a stored sim id so no Sim Info could be loaded.', self.owner)

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_info_or_name_data(self):
        if len(self._sim_id_list) > 0:
            sim_info = services.sim_info_manager().get(self._sim_id_list[0])
            if sim_info is not None:
                return sim_info
            return self._sim_info_name_data_list[0]
        logger.error('The StoredSimComponent on {} does not have a stored sim id, so no SimInfo or name data could be loaded.', self.owner)

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_name_data(self):
        if len(self._sim_info_name_data_list) > 0:
            return self._sim_info_name_data_list[0]
        logger.error('The StoredSimComponent on {} does not have a stored sim id so no name data could be loaded.', self.owner)

    @componentmethod_with_fallback((lambda *_, **__: None))
    def get_secondary_stored_sim_info(self, suppress_error=False):
        if len(self._sim_id_list) > 1:
            return services.sim_info_manager().get(self._sim_id_list[1])
        if not suppress_error:
            logger.error('The StoredSimComponent on {} does not have a second stored sim id', self.owner)

    @componentmethod_with_fallback((lambda *_, **__: None))
    def get_secondary_stored_sim_info_or_name_data(self, suppress_error=False):
        if len(self._sim_id_list) > 1:
            sim_info = services.sim_info_manager().get(self._sim_id_list[1])
            if sim_info is not None:
                return sim_info
            return self._sim_info_name_data_list[1]
        if not suppress_error:
            logger.error('The StoredSimComponent on {} does not have a second stored sim id so no SimInfo or name data could be loaded.', self.owner)

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_id_list(self):
        return self._sim_id_list

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_info_or_name_data_list(self):
        sim_info_or_name_data_list = []
        sim_info_manager = services.sim_info_manager()
        for sim_id in self._sim_id_list:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is not None:
                sim_info_or_name_data_list.append(sim_info)
            else:
                return self._sim_info_name_data_list

        return sim_info_or_name_data_list

    @componentmethod_with_fallback((lambda: None))
    def get_stored_sim_name_data_list(self):
        return self._sim_info_name_data_list

    def has_stored_data(self):
        return len(self._sim_info_name_data_list) != 0

    def component_interactable_gen(self):
        yield self