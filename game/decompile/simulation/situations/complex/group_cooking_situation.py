# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\group_cooking_situation.py
# Compiled at: 2021-06-14 20:33:22
# Size of source mod 2**32: 17285 bytes
import itertools, services
from interactions.context import InteractionContext, QueueInsertStrategy
from interactions.interaction_finisher import FinishingType
from interactions.priority import Priority
from interactions.utils.interaction_liabilities import SITUATION_LIABILITY, SituationLiability
from sims4.log import Logger
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, OptionalTunable, TunableList
from sims4.tuning.tunable_base import GroupNames
from singletons import DEFAULT
from situations.situation import Situation
from situations.situation_complex import CommonInteractionCompletedSituationState, SituationComplexCommon, SituationStateData, CommonSituationState
from situations.situation_liabilities import RemoveFromSituationLiability
logger = Logger('GroupCooking', default_owner='jjacobson')

class GatherState(CommonInteractionCompletedSituationState):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sims_ran_interaction = set()

    def _on_set_sim_role_state(self, sim, job_type, role_state_type, role_affordance_target):
        super()._on_set_sim_role_state(sim, job_type, role_state_type, role_affordance_target)
        if job_type is not self.owner.head_crafter:
            return
        else:
            context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
              (Priority.Critical),
              run_priority=(Priority.High),
              insert_strategy=(QueueInsertStrategy.NEXT))
            result = sim.push_super_affordance(self.owner.head_crafter_holder_affordance, None, context)
            if result:
                result.interaction.add_liability(SITUATION_LIABILITY, SituationLiability(self.owner))
            else:
                self.owner._self_destruct()

    def _additional_tests(self, sim_info, event, resolver):
        return self.owner.is_sim_info_in_situation(sim_info)

    def _on_interaction_of_interest_complete(self, sim_info=None, **kwargs):
        self._sims_ran_interaction.add(sim_info.sim_id)
        if len(self._sims_ran_interaction) >= self.owner.get_num_sims_in_job(self.owner.other_crafters):
            self._change_state(self.owner.craft_state())

    def timer_expired(self):
        self._change_state(self.owner.craft_state())


class CraftState(CommonSituationState):
    FACTORY_TUNABLES = {'crafting_interaction': TunableReference(description='\n            The interaction to use to actually begin crafting.\n            ',
                               manager=(services.get_instance_manager(Types.INTERACTION)),
                               class_restrictions=('SituationStartGroupCraftingInteraction', ))}

    def __init__(self, crafting_interaction, **kwargs):
        (super().__init__)(**kwargs)
        self._crafting_interaction = crafting_interaction

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        if reader is not None:
            return
        crafting_sim = next(self.owner.all_sims_in_job_gen(self.owner.head_crafter))
        if crafting_sim is None:
            self.owner._self_destruct()
            return
        holding_interaction = crafting_sim.si_state.get_si_by_affordance(self.owner.head_crafter_holder_affordance)
        if holding_interaction is not None:
            holding_interaction.remove_liability(SITUATION_LIABILITY, release=False)
            holding_interaction.cancel(FinishingType.SITUATIONS, 'Holding interaction no longer needed after gathering state.')
        context = InteractionContext(crafting_sim, InteractionContext.SOURCE_PIE_MENU, Priority.High, QueueInsertStrategy.NEXT)
        result = crafting_sim.push_super_affordance((self._crafting_interaction), (self.owner._target),
          context,
          start_crafting_interaction=(self.owner._start_crafting_interaction),
          recipe=(self.owner._recipe),
          crafter=crafting_sim,
          ordering_sim=(self.owner._ordering_sim),
          crafting_target=(self.owner._crafting_target),
          orderer_ids=(self.owner._orderer_ids),
          ingredients=(self.owner._ingredients),
          recipe_funds_source=(self.owner._funds_source),
          paying_sim=(self.owner._paying_sim),
          ingredient_cost_only=(self.owner._ingredient_cost_only),
          situation_id=(self.owner.id))
        self.owner._clear_start_crafting_info()
        if not result:
            self.owner._self_destruct()


class StopOtherCraftersState(CommonSituationState):
    pass


class GroupCraftingSituation(SituationComplexCommon):
    CRAFTING_OBJECT_TOKEN = 'crafting_object'
    INSTANCE_TUNABLES = {'gather_state':GatherState.TunableFactory(tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'craft_state':CraftState.TunableFactory(tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'stop_other_crafters_state':OptionalTunable(description='\n            If enabled then there will be a special state to have\n            other Sims cease their faux crafting behavior part of\n            the way through the crafting process.\n            Example: When cooking we would like the Sims to stop\n            using the crafting on the counter interactions once\n            the main Sim transitions to put the food into the\n            oven.\n            ',
       tunable=StopOtherCraftersState.TunableFactory(),
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'head_crafter':TunableReference(description='\n            The head chef who will actually be cooking the meal.\n            ',
       manager=services.get_instance_manager(Types.SITUATION_JOB),
       tuning_group=GroupNames.ROLES), 
     'other_crafters':TunableReference(description='\n            Other chefs who will be helping out with cooking.\n            ',
       manager=services.get_instance_manager(Types.SITUATION_JOB),
       tuning_group=GroupNames.ROLES), 
     'other_sims':OptionalTunable(description='\n            If enabled then this other job will exist to put other instanced Sims\n            into the situation.  This can be used to add autonomy to those other Sims.\n            An example of wanting to use this would be to prevent those Sims from\n            trying to autonomously craft while the main group crafting is going on.\n            ',
       tunable=TunableReference(description='\n                The job that other instanced Sims will be put into.\n                ',
       manager=(services.get_instance_manager(Types.SITUATION_JOB)),
       tuning_group=(GroupNames.ROLES))), 
     'head_crafter_holder_affordance':TunableReference(description='\n            Interaction that lives on the head crafter in the gather phase.\n            Cancelling this interaction will cause the situation to end.\n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'helper_crafter_holder_affordance':TunableReference(description='\n            Interaction that lives on the other crafters throughout their\n            time in the situation.  Cancelling this interaction will cause\n            them to leave the situation.\n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'interactions_to_cancel_on_removal':TunableList(description='\n            A list of interactions to remove on Sims when they are removed\n            from the situation.\n            ',
       tunable=TunableReference(description='\n                Interaction to cancel when the Sim leaves the situation.\n                ',
       manager=(services.get_instance_manager(Types.INTERACTION))))}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._crafting_process = None
        reader = self._seed.custom_init_params_reader
        if reader is None:
            self._start_crafting_interaction = self._seed.extra_kwargs.get('start_crafting_interaction', None)
            self._target = self._seed.extra_kwargs.get('target', None)
            self._recipe = self._seed.extra_kwargs.get('recipe', None)
            self._ordering_sim = self._seed.extra_kwargs.get('ordering_sim', None)
            self._crafting_target = self._seed.extra_kwargs.get('crafting_target', None)
            self._orderer_ids = self._seed.extra_kwargs.get('orderer_ids', DEFAULT)
            self._ingredients = self._seed.extra_kwargs.get('ingredients', ())
            self._funds_source = self._seed.extra_kwargs.get('funds_source', None)
            self._paying_sim = self._seed.extra_kwargs.get('paying_sim', None)
            self._ingredient_cost_only = self._seed.extra_kwargs.get('ingredient_cost_only', False)
        else:
            self._start_crafting_interaction = None
            self._target = None
            self._recipe = None
            self._ordering_sim = None
            self._crafting_target = None
            self._orderer_ids = None
            self._ingredients = None
            self._funds_source = None
            self._paying_sim = None
            self._ingredient_cost_only = None
            crafting_ico_id = reader.read_uint64(GroupCraftingSituation.CRAFTING_OBJECT_TOKEN, None)
        if crafting_ico_id is not None:
            crafting_ico = services.object_manager().get(crafting_ico_id)
            if crafting_ico is not None:
                self._crafting_process = crafting_ico.get_crafting_process()

    def start_situation(self):
        super().start_situation()
        self._change_state(self.gather_state())

    def load_situation(self):
        if self._crafting_process is None:
            return False
        return super().load_situation()

    @classmethod
    def _states(cls):
        if cls.stop_other_crafters_state is None:
            return (
             SituationStateData.from_auto_factory(1, cls.gather_state),
             SituationStateData.from_auto_factory(2, cls.craft_state))
        return (
         SituationStateData.from_auto_factory(1, cls.gather_state),
         SituationStateData.from_auto_factory(2, cls.craft_state),
         SituationStateData.from_auto_factory(3, cls.stop_other_crafters_state))

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return list(cls.gather_state._tuned_values.job_and_role_changes.items())

    @classmethod
    def default_job(cls):
        return cls.other_sims

    def save_situation(self):
        if self._state_to_uid(self._cur_state) == 1:
            return
        return super().save_situation()

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self._crafting_process is not None:
            writer.write_uint64(GroupCraftingSituation.CRAFTING_OBJECT_TOKEN, self._crafting_process.current_ico.id)

    def _destroy(self):
        super()._destroy()
        self._clear_start_crafting_info()
        if self._crafting_process is not None:
            self._crafting_process.clear_linked_situation()
            self._crafting_process = None

    def _clear_start_crafting_info(self):
        self._start_crafting_interaction = None
        self._target = None
        self._recipe = None
        self._ordering_sim = None
        self._crafting_target = None
        self._orderer_ids = None
        self._ingredients = None
        self._funds_source = None
        self._paying_sim = None
        self._ingredient_cost_only = None

    def set_crafting_process(self, crafting_process):
        self._crafting_process = crafting_process

    def get_situation_crafting_object(self):
        if self._crafting_process is None:
            logger.error("Attempting to get crafting process that hasn't been set yet on GroupCraftingSituation")
            return
        return self._crafting_process.current_ico

    def stop_other_crafting_sims(self):
        if self.stop_other_crafters_state is None:
            return
        self._change_state(self.stop_other_crafters_state())

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        if job_type is not self.other_crafters:
            return
        else:
            context = InteractionContext(sim, (InteractionContext.SOURCE_SCRIPT),
              (Priority.Critical),
              run_priority=(Priority.High),
              insert_strategy=(QueueInsertStrategy.NEXT))
            result = sim.push_super_affordance(self.helper_crafter_holder_affordance, None, context)
            if result:
                result.interaction.add_liability(RemoveFromSituationLiability.LIABILITY_TOKEN, RemoveFromSituationLiability(sim, self))
            else:
                self.remove_sim_from_situation(sim)

    def _on_remove_sim_from_situation(self, sim):
        super()._on_remove_sim_from_situation(sim)
        for si in itertools.chain(sim.si_state, sim.queue):
            if type(si) is self.helper_crafter_holder_affordance:
                si.remove_liability(RemoveFromSituationLiability.LIABILITY_TOKEN)
                si.cancel(FinishingType.SITUATIONS, 'Holding interaction no longer needed because sim is leaving situation.')