# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\open_street_director\festival_situations.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 23987 bytes
from event_testing.resolver import SingleSimResolver
from filters.tunable import FilterTermTag
from objects.components.state import StateComponent
from objects.components.state_references import TunableStateValueReference
from objects.components.types import CRAFTING_COMPONENT
from objects.object_creation import TunableObjectCreationDataVariant
from objects.system import create_object
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import Tunable, TunableReference, TunableMapping, TunableEnumEntry, TunableList, TunableTuple
from sims4.utils import classproperty
from situations.ambient.busker_situation import BuskerSituationMixin, BuskSituationState
from situations.ambient.sales_table_vendor_situation import SalesTableVendorSituationMixin
from situations.base_situation import _RequestUserData
from situations.bouncer.bouncer_request import SelectableSimRequestFactory
from situations.bouncer.bouncer_types import BouncerExclusivityCategory, RequestSpawningOption, BouncerRequestPriority
from situations.situation import Situation
from situations.situation_complex import CommonSituationState, SituationComplexCommon, SituationStateData, SituationState, TunableSituationJobAndRoleState
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo
from situations.situation_job import SituationJob
from situations.situation_types import SituationCreationUIOption
import filters.tunable, itertools, services, sims4.resources, situations
from tunable_utils.tested_list import TunableTestedList
logger = sims4.log.Logger('Festival Situations')

class CooldownFestivalSituationState(CommonSituationState):
    FACTORY_TUNABLES = {'should_try_and_find_new_situation': Tunable(description='\n            If True then we will try and put these Sims into new situations\n            when they enter this state.\n            ',
                                            tunable_type=bool,
                                            default=False)}

    def __init__(self, *args, should_try_and_find_new_situation=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._should_try_and_find_new_situation = should_try_and_find_new_situation

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        if self._should_try_and_find_new_situation:
            for sim in self.owner.all_sims_in_situation_gen():
                self.owner.manager.bouncer.set_sim_looking_for_new_situation(sim)


class BaseGenericFestivalSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'cooldown_state': CooldownFestivalSituationState.TunableFactory(description='\n            The state that the Situation will go into when the festival open\n            street director notifies it that the festival is going into\n            cooldown.\n            ',
                         locked_args={'allow_join_situation':False, 
                        'time_out':None},
                         tuning_group=(SituationComplexCommon.SITUATION_STATE_GROUP))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def default_job(cls):
        pass

    def put_on_cooldown(self):
        self._change_state(self.cooldown_state())

    @classproperty
    def situation_serialization_option(cls):
        return situations.situation_types.SituationSerializationOption.OPEN_STREETS

    @classproperty
    def always_elevated_importance(cls):
        return True


class StartingFestivalSituationState(CommonSituationState):
    pass


class GenericOneStateFestivalAttendeeSituation(BaseGenericFestivalSituation):
    INSTANCE_TUNABLES = {'initial_state': StartingFestivalSituationState.TunableFactory(description='\n            The first state that the Sims will be put into when this Situation\n            Starts.\n            ',
                        locked_args={'allow_join_situation':True, 
                       'time_out':None},
                        tuning_group=(SituationComplexCommon.SITUATION_STATE_GROUP))}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, StartingFestivalSituationState, factory=(cls.initial_state)),
         SituationStateData(2, CooldownFestivalSituationState, factory=(cls.cooldown_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.initial_state._tuned_values.job_and_role_changes.items())

    def start_situation(self):
        super().start_situation()
        self._change_state(self.initial_state())


lock_instance_tunables(GenericOneStateFestivalAttendeeSituation, exclusivity=(BouncerExclusivityCategory.FESTIVAL_GOER),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)
CREATED_OBJECTS_TOKEN = 'created_objects'

class OneStateFestivalAttendeeWithObjectsSituation(GenericOneStateFestivalAttendeeSituation):
    INSTANCE_TUNABLES = {'objects_to_create': TunableTestedList(description='\n            A tested list of objects to create into the Sims inventory when they are\n            added to the situation.\n            ',
                            tunable_type=TunableTuple(description='\n                Data used for the creation of these objects.\n                ',
                            creation_data=(TunableObjectCreationDataVariant()),
                            initial_states=TunableList(description='\n                    A list of states to apply on the object when they are first created.\n                    ',
                            tunable=(TunableStateValueReference()))))}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._created_objects = None
        reader = self._seed.custom_init_params_reader
        if reader is not None:
            self._created_objects = reader.read_uint64s(CREATED_OBJECTS_TOKEN, ())
            for saved_object_id in self._created_objects:
                self._claim_object(saved_object_id)

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        if self._created_objects is not None:
            return
        self._created_objects = []

        def setup_object(obj):
            obj.set_household_owner_id(sim.household_id)

        resolver = SingleSimResolver(sim.sim_info)
        for obj_creation_data in self.objects_to_create(resolver=resolver):
            try:
                definition, setup_params = obj_creation_data.creation_data.get_creation_params(resolver)
                created_object = create_object(definition, init=setup_object)
                if created_object is None:
                    logger.error('Failed to create object for {}', self)
                    continue
                sim.inventory_component.system_add_object(created_object)
                (obj_creation_data.creation_data.setup_created_object)(resolver, created_object, **setup_params)
                if obj_creation_data.initial_states:
                    if created_object.state_component is None:
                        created_object.add_component(StateComponent(created_object))
                    for initial_state in obj_creation_data.initial_states:
                        if created_object.has_state(initial_state.state):
                            created_object.set_state((initial_state.state), initial_state, from_creation=True)

                if created_object.has_component(CRAFTING_COMPONENT):
                    created_object.crafting_component.update_simoleon_tooltip()
                    created_object.crafting_component.update_quality_tooltip()
                created_object.update_object_tooltip()
                created_object.claim()
                self._created_objects.append(created_object.id)
            except:
                logger.error('Failed to create object for {}', self)

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self._created_objects is not None:
            writer.write_uint64s(CREATED_OBJECTS_TOKEN, self._created_objects)


class StartingTransitioningFestivalSituationState(CommonSituationState):

    def timer_expired(self):
        self._change_state(self.owner.secondary_state())


class SecondaryFestivalSituationState(CommonSituationState):
    pass


class GenericTwoStateFestivalAttendeeSituation(BaseGenericFestivalSituation):
    INSTANCE_TUNABLES = {'initial_state':StartingTransitioningFestivalSituationState.TunableFactory(description='\n            The first state that the Sims will be put into when this Situation\n            Starts.\n            ',
       locked_args={'allow_join_situation': True},
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'secondary_state':SecondaryFestivalSituationState.TunableFactory(description='\n            The second state that this situation will be put into once the\n            first state ends.\n            ',
       locked_args={'allow_join_situation':False, 
      'time_out':None},
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP)}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, StartingTransitioningFestivalSituationState, factory=(cls.initial_state)),
         SituationStateData(2, SecondaryFestivalSituationState, factory=(cls.secondary_state)),
         SituationStateData(3, CooldownFestivalSituationState, factory=(cls.cooldown_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.initial_state._tuned_values.job_and_role_changes.items())

    def start_situation(self):
        super().start_situation()
        self._change_state(self.initial_state())


lock_instance_tunables(GenericTwoStateFestivalAttendeeSituation, exclusivity=(BouncerExclusivityCategory.FESTIVAL_GOER),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)

class EmployeeFestivalSituationState(BaseGenericFestivalSituation):
    INSTANCE_TUNABLES = {'initial_state': StartingFestivalSituationState.TunableFactory(description='\n            The first state that the Sims will be put into when this Situation\n            Starts.\n            ',
                        locked_args={'allow_join_situation':True, 
                       'time_out':None},
                        tuning_group=(SituationComplexCommon.SITUATION_STATE_GROUP))}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, StartingFestivalSituationState, factory=(cls.initial_state)),
         SituationStateData(2, CooldownFestivalSituationState, factory=(cls.cooldown_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.initial_state._tuned_values.job_and_role_changes.items())

    def start_situation(self):
        super().start_situation()
        self._change_state(self.initial_state())


lock_instance_tunables(EmployeeFestivalSituationState, exclusivity=(BouncerExclusivityCategory.FESTIVAL_EMPLOYEE),
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)

class SpecificSimEmployeeFestivalSituation(EmployeeFestivalSituationState):
    INSTANCE_TUNABLES = {'specific_sim_job': TunableReference(description='\n            The job specific Sim that has to be put into this situation no matter their current situation.\n            ',
                           manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))}

    @classmethod
    def get_predefined_guest_list(cls):
        guest_list = SituationGuestList(invite_only=True)
        active_sim_info = services.active_sim_info()
        filter_result = services.sim_filter_service().submit_matching_filter(sim_filter=(cls.specific_sim_job.filter), callback=None,
          requesting_sim_info=active_sim_info,
          allow_yielding=False,
          allow_instanced_sims=True,
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        guest_list.add_guest_info(SituationGuestInfo(filter_result[0].sim_info.sim_id, cls.specific_sim_job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.EVENT_VIP))
        return guest_list


class _SelectableSimsBackgroundSituationState(SituationState):
    pass


class SelectableSimFestivalSituation(BaseGenericFestivalSituation):
    INSTANCE_TUNABLES = {'job_and_role': TunableSituationJobAndRoleState(description='\n            The job and role that the selectable Sims will be given.\n            ')}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _SelectableSimsBackgroundSituationState),
         SituationStateData(2, CooldownFestivalSituationState, factory=(cls.cooldown_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.job_and_role.job, cls.job_and_role.role_state)]

    @classmethod
    def default_job(cls):
        pass

    def start_situation(self):
        super().start_situation()
        self._change_state(_SelectableSimsBackgroundSituationState())

    def _issue_requests(self):
        request = SelectableSimRequestFactory(self, callback_data=_RequestUserData(role_state_type=(self.job_and_role.role_state)),
          job_type=(self.job_and_role.job),
          exclusivity=(self.exclusivity))
        self.manager.bouncer.submit_request(request)


lock_instance_tunables(SelectableSimFestivalSituation, load_open_street_situation_with_selectable_sim=True,
  creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)

class MultiSimStartingFestivalSituationState(CommonSituationState):
    pass


class MultiSimFestivalSituation(BaseGenericFestivalSituation):
    INSTANCE_TUNABLES = {'group_filter':TunableReference(description='\n            The aggregate filter that we use to find the sims for this\n            situation.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER),
       class_restrictions=filters.tunable.TunableAggregateFilter), 
     'situation_job_mapping':TunableMapping(description='\n            A mapping of filter term tag to situation job.\n            \n            The filter term tag is returned as part of the sim filters used to \n            create the guest list for this particular background situation.\n            \n            The situation job is the job that the Sim will be assigned to in\n            the background situation.\n            ',
       key_name='filter_tag',
       key_type=TunableEnumEntry(description='\n                The filter term tag returned with the filter results.\n                ',
       tunable_type=FilterTermTag,
       default=(FilterTermTag.NO_TAG)),
       value_name='job',
       value_type=TunableReference(description='\n                The job the Sim will receive when added to the this situation.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))), 
     'initial_state':MultiSimStartingFestivalSituationState.TunableFactory(description='\n            The first state that the Sims will be put into when this Situation\n            Starts.\n            ',
       locked_args={'allow_join_situation':True, 
      'time_out':None},
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'blacklist_job':SituationJob.TunableReference(description='\n            The default job used for blacklisting Sims from coming back as\n            festival goers.\n            ')}

    @classmethod
    def _states(cls):
        return (SituationStateData(1, MultiSimStartingFestivalSituationState, factory=(cls.initial_state)),
         SituationStateData(2, CooldownFestivalSituationState, factory=(cls.cooldown_state)))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.initial_state._tuned_values.job_and_role_changes.items())

    @classmethod
    def get_predefined_guest_list(cls):
        guest_list = SituationGuestList(invite_only=True)
        situation_manager = services.get_zone_situation_manager()
        worker_filter = cls.group_filter if cls.group_filter is not None else cls.default_job().filter
        instanced_sim_ids = [sim.sim_info.id for sim in services.sim_info_manager().instanced_sims_gen()]
        household_sim_ids = [sim_info.id for sim_info in services.active_household().sim_info_gen()]
        auto_fill_blacklist = situation_manager.get_auto_fill_blacklist(sim_job=(cls.blacklist_job))
        situation_sims = set()
        for situation in situation_manager.get_situations_by_tags(cls.tags):
            situation_sims.update(situation.invited_sim_ids)

        blacklist_sim_ids = set(itertools.chain(situation_sims, instanced_sim_ids, household_sim_ids, auto_fill_blacklist))
        filter_results = services.sim_filter_service().submit_matching_filter(sim_filter=worker_filter, allow_yielding=False,
          blacklist_sim_ids=blacklist_sim_ids,
          gsi_source_fn=(cls.get_sim_filter_gsi_name))
        if not filter_results:
            return
        for result in filter_results:
            job = cls.situation_job_mapping.get(result.tag, cls.default_job())
            guest_list.add_guest_info(SituationGuestInfo(result.sim_info.sim_id, job, RequestSpawningOption.DONT_CARE, BouncerRequestPriority.BACKGROUND_HIGH))

        return guest_list

    def start_situation(self):
        super().start_situation()
        self._change_state(self.initial_state())


lock_instance_tunables(MultiSimFestivalSituation, creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)

class FestivalPerformanceSpaceBuskerSituation(BuskerSituationMixin, BaseGenericFestivalSituation):
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    @classmethod
    def _states(cls):
        return (SituationStateData(1, BuskSituationState, factory=(cls.busk_state)),
         SituationStateData(2, CooldownFestivalSituationState, factory=(cls.cooldown_state)))


lock_instance_tunables(FestivalPerformanceSpaceBuskerSituation, creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  _implies_greeted_status=False)

class FestivalSalesTableVendorSituation(SalesTableVendorSituationMixin, BaseGenericFestivalSituation):
    REMOVE_INSTANCE_TUNABLES = ('cooldown_state', )

    def put_on_cooldown(self):
        self._change_state(self.teardown_state())


lock_instance_tunables(FestivalSalesTableVendorSituation, creation_ui_option=(SituationCreationUIOption.NOT_AVAILABLE),
  duration=0,
  _implies_greeted_status=False)