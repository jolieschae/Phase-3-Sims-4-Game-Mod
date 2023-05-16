# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\complex\kids_bike_practice_situation.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 38943 bytes
import interactions, interactions.constraints, placement, services, sims4, sims4.log, sims4.math
from event_testing.test_events import TestEvent
from interactions.base.interaction import InteractionFailureOptions
from interactions.context import InteractionContext
from interactions.priority import Priority
from objects.system import create_object
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from situations.situation import Situation
from situations.situation_complex import SituationComplexCommon, CommonSituationState, SituationStateData, InteractionOfInterest, TunableSituationJobAndRoleState, TunableInteractionOfInterest
logger = sims4.log.Logger('KidsBikePracticeSituation', default_owner='jmoline')

class _KidsBikePracticeSituationState(CommonSituationState):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._started_learner_interactions = False
        self._started_both_interactions = False

    def start_initial_interactions(self):
        mentor_sim = self.owner.get_mentor_sim()
        learner_sim = self.owner.get_learner_sim()
        if not self._started_learner_interactions:
            if learner_sim is not None:
                self._started_learner_interactions = True
                self._start_learner_interaction()
        if not self._started_both_interactions:
            if learner_sim is not None:
                if mentor_sim is not None:
                    self._started_both_interactions = True
                    self._start_both_interaction()

    def _start_learner_interaction(self):
        pass

    def _start_both_interaction(self):
        pass


class _WaitForBikePickupState(_KidsBikePracticeSituationState):
    FACTORY_TUNABLES = {'bike_pickup_interaction':TunableInteractionOfInterest(description='\n            The state waits for this interaction to determine the picked up\n            bicycle.  \n            '), 
     'learner_pickup_interaction':OptionalTunable(description="\n            If provided, the situation will push this interaction onto the\n            learner sim if the sim doesn't have the bike in their inventory.\n            ",
       tunable=TunableReference(description='\n                Interaction pushed on learner sim to pick up the bike.  \n                ',
       manager=(services.get_instance_manager(Types.INTERACTION))))}

    def __init__(self, *args, bike_pickup_interaction=None, learner_pickup_interaction=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.bike_pickup_interaction = bike_pickup_interaction
        self.learner_pickup_interaction = learner_pickup_interaction

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        for custom_key in iter(self.bike_pickup_interaction.custom_keys_gen()):
            self._test_event_register(TestEvent.InteractionComplete, custom_key)
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

        self.start_initial_interactions()

    def _start_learner_interaction(self):
        bicycle = self.owner.get_bicycle()
        if self.learner_pickup_interaction is not None:
            if bicycle is not None:
                if not bicycle.is_in_inventory():
                    learner_sim = self.owner.get_learner_sim()
                    result = learner_sim.push_super_affordance(self.learner_pickup_interaction, bicycle, InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High))
                    if not result:
                        logger.error('Failed to run interaction {} for {} because {}.', self.learner_pickup_interaction, self.owner, result)
                        self.owner.end_bike_practice(cancel=True)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
        if event == TestEvent.InteractionComplete and resolver(self.bike_pickup_interaction):
            self.owner._bicycle = resolver.interaction.target
            self._change_state(self.owner.place_bike_state())
        else:
            if event == TestEvent.InteractionExitedPipeline:
                if resolver(self.bike_pickup_interaction):
                    logger.info('Pickup bike interaction {} canceled for {}.', resolver.interaction, self.owner)
                    self.owner.end_bike_practice(cancel=True)


class _PlaceBikeState(_KidsBikePracticeSituationState):
    FACTORY_TUNABLES = {'place_bike_in_world_interaction': TunableReference(description='\n            Interaction pushed on learner sim to put the bike down inside the practice area.  \n            ',
                                          manager=(services.get_instance_manager(Types.INTERACTION)))}

    def __init__(self, *args, place_bike_in_world_interaction=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.place_bike_in_world_interaction = place_bike_in_world_interaction
        self._interactions = InteractionOfInterest(affordances=(
         self.place_bike_in_world_interaction,),
          tags=(frozenset()))

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        for custom_key in iter(self._interactions.custom_keys_gen()):
            self._test_event_register(TestEvent.InteractionComplete, custom_key)
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

        self.start_initial_interactions()

    def _start_learner_interaction(self):
        learner_sim = self.owner.get_learner_sim()
        bicycle = self.owner.get_bicycle()
        if not self.owner.initialize_practice_jig(self.place_bike_in_world_interaction):
            return
        self.owner.set_can_route_in_practice_area(learner_sim, bicycle)
        result = learner_sim.push_super_affordance((self.place_bike_in_world_interaction), bicycle, (InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)),
          allow_posture_changes=True,
          constraint_to_satisfy=(self.owner.get_practice_area_constraint()))
        if not result:
            logger.error('Failed to run interaction {} for {} because {}.', self.place_bike_in_world_interaction, self.owner, result)
            self.owner.end_bike_practice(cancel=True)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
        if event == TestEvent.InteractionComplete and resolver(self._interactions):
            self._change_state(self.owner.practice_riding_state())
        else:
            if event == TestEvent.InteractionExitedPipeline:
                if resolver(self._interactions):
                    logger.info('Place bike interaction {} canceled for {}.', resolver.interaction, self.owner)
                    self.owner.end_bike_practice(cancel=True)


class _PracticeRidingState(_KidsBikePracticeSituationState):
    FACTORY_TUNABLES = {'bike_riding_practice_interaction':TunableReference(description='\n            Interaction pushed on learner sim to practice riding.  \n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'bike_riding_success_interaction':TunableReference(description='\n            This interaction is expected to run when the learner sim has levelled up.\n            When this interaction completes, the situation will move into the Celebrate\n            state if there is a mentor sim.\n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'mentor_cheering_interaction':TunableInteractionOfInterest(description='\n            The mentor sim is expected to start this interaction as part of the role. The\n            situation watches to see if the interaction is interrupted and if it is, the\n            mentor sim will be removed from the situation.   \n            '), 
     'mentor_cheer_initial_interaction':TunableReference(description='\n            Interaction pushed on mentor sim to start the mentor cheering. This interaction\n            targets the learner sim.\n            ',
       manager=services.get_instance_manager(Types.INTERACTION))}

    def __init__(self, *args, bike_riding_practice_interaction=None, bike_riding_success_interaction=None, mentor_cheering_interaction=None, mentor_cheer_initial_interaction=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.bike_riding_practice_interaction = bike_riding_practice_interaction
        self.bike_riding_success_interaction = bike_riding_success_interaction
        self.mentor_cheering_interaction = mentor_cheering_interaction
        self.mentor_cheer_initial_interaction = mentor_cheer_initial_interaction
        self._completed_interactions = set()
        self._started_interactions = False
        self._success_interactions = InteractionOfInterest(affordances=(
         self.bike_riding_success_interaction,),
          tags=(frozenset()))
        self._cancel_interactions = InteractionOfInterest(affordances=(
         self.bike_riding_practice_interaction,
         self.bike_riding_success_interaction),
          tags=(frozenset()))

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        if reader is not None:
            if not services.object_manager().get(self.owner._bicycle_id):
                self._change_state(self.owner.place_bike_state())
                return
        custom_keys = set()
        custom_keys.update(self._cancel_interactions.custom_keys_gen())
        custom_keys.update(self.mentor_cheering_interaction.custom_keys_gen())
        for custom_key in custom_keys:
            self._test_event_register(TestEvent.InteractionComplete, custom_key)
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

        self.start_initial_interactions()

    def _start_learner_interaction(self):
        if not self.owner.initialize_practice_jig(self.bike_riding_practice_interaction):
            return
        learner_sim = self.owner.get_learner_sim()
        bicycle = self.owner.get_bicycle()
        self.owner.set_can_route_in_practice_area(learner_sim, bicycle)
        result = learner_sim.push_super_affordance((self.bike_riding_practice_interaction), bicycle, (InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)),
          allow_posture_changes=True,
          constraint_to_satisfy=(self.owner.get_practice_area_constraint()))
        if not result:
            logger.error('Failed to run interact {} on {} for {} because {}.', self.bike_riding_practice_interaction, learner_sim, self.owner, result)
            self.owner.end_bike_practice(cancel=True)

    def _start_both_interaction(self):
        mentor_sim = self.owner.get_mentor_sim()
        learner_sim = self.owner.get_learner_sim()
        result = mentor_sim.push_super_affordance((self.mentor_cheer_initial_interaction), learner_sim, (InteractionContext(mentor_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)),
          allow_posture_changes=True,
          constraint_to_satisfy=(self.owner.get_practice_area_constraint()))
        if not result:
            logger.error('Failed to run interact {} on {} for {} because {}.', self.mentor_cheer_initial_interaction, mentor_sim, self.owner, result)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
            if resolver.interaction is not None:
                interaction_def_id = resolver.interaction.guid64
                if event == TestEvent.InteractionComplete:
                    self._completed_interactions.add(interaction_def_id)
        elif event == TestEvent.InteractionExitedPipeline:
            if interaction_def_id in self._completed_interactions:
                self._completed_interactions.remove(interaction_def_id)
                if resolver.interaction.is_finishing_naturally:
                    event_sim = sim_info.get_sim_instance()
                    if event_sim != self.owner.get_learner_sim():
                        return
                    if interaction_def_id != self.bike_riding_practice_interaction.guid64:
                        return
                    if event_sim.queue.find_pushed_interaction_by_id(resolver.interaction.group_id):
                        return
        elif resolver(self._success_interactions):
            self._on_success_interaction(sim_info, event, resolver)
        else:
            if resolver(self.mentor_cheering_interaction):
                self._on_mentor_cheering_interaction(sim_info, event, resolver)
            else:
                if resolver(self._cancel_interactions):
                    self._on_cancel_interaction(sim_info, event, resolver)

    def _on_success_interaction(self, sim_info, event, resolver):
        if event == TestEvent.InteractionComplete:
            if self.owner.get_mentor_sim():
                logger.info('Practice riding complete with mentor {} switching to Celebrate state for {}.', self.owner.get_mentor_sim(), self.owner)
                self._change_state(self.owner.celebrate_state())
            else:
                logger.info('Practice riding complete without mentor. Ending situation {} successfully.', self.owner)
                self.owner.end_bike_practice()
        elif event == TestEvent.InteractionExitedPipeline:
            logger.info('Practice riding interaction {} canceled for {}.', resolver.interaction, self.owner)
            self.owner.end_bike_practice(cancel=True)

    def _on_mentor_cheering_interaction(self, sim_info, event, resolver):
        if event == TestEvent.InteractionExitedPipeline:
            logger.info('Practice riding interaction {} canceled for {}. Removing {} from situation.', resolver.interaction, self.owner, sim_info)
            self.owner.remove_sim_from_situation(sim_info.get_sim_instance())

    def _on_cancel_interaction(self, sim_info, event, resolver):
        if event == TestEvent.InteractionExitedPipeline:
            logger.info('Practice riding interaction {} canceled for {}.', resolver.interaction, self.owner)
            self.owner.end_bike_practice(cancel=True)


class _CelebrateState(_KidsBikePracticeSituationState):
    FACTORY_TUNABLES = {'celebrate_interaction': TunableReference(description='\n            Interaction pushed on learner sim targeted to the mentor sim to celebrate level up.  \n            ',
                                manager=(services.get_instance_manager(Types.INTERACTION)))}

    def __init__(self, *args, celebrate_interaction=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.celebrate_interaction = celebrate_interaction
        self._interactions = InteractionOfInterest(affordances=(
         self.celebrate_interaction,),
          tags=(frozenset()))

    def on_activate(self, reader=None):
        super().on_activate(reader=reader)
        for custom_key in iter(self._interactions.custom_keys_gen()):
            self._test_event_register(TestEvent.InteractionComplete, custom_key)
            self._test_event_register(TestEvent.InteractionExitedPipeline, custom_key)

        self.start_initial_interactions()

    def _start_both_interaction(self):
        learner_sim = self.owner.get_learner_sim()
        mentor_sim = self.owner.get_mentor_sim()
        result = learner_sim.push_super_affordance((self.celebrate_interaction), mentor_sim, (InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)),
          allow_posture_changes=True)
        if not result:
            logger.error('Failed to start celebrate interaction {} for {} because {}.', self.celebrate_interaction, self.owner, result)
            self.owner.end_bike_practice(cancel=True)

    def handle_event(self, sim_info, event, resolver):
        if not self.owner.is_sim_info_in_situation(sim_info):
            return
        if event == TestEvent.InteractionComplete and resolver(self._interactions):
            logger.info('Celebrate state complete. Ending situation {} successfully.', self.owner)
            self.owner.end_bike_practice()
        else:
            if event == TestEvent.InteractionExitedPipeline:
                if resolver(self._interactions):
                    logger.info('Celebrate interaction {} canceled for {}.', resolver.interaction, self.owner)
                    self.owner.end_bike_practice(cancel=True)


class KidsBikePracticeSituation(SituationComplexCommon):
    INSTANCE_TUNABLES = {'learner_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of sim who is learning to ride bike.\n            ',
       tuning_group=GroupNames.ROLES), 
     'mentor_job_and_role_state':TunableSituationJobAndRoleState(description='\n            The job and role state of sim who is acting as a bike riding mentor.\n            ',
       tuning_group=GroupNames.ROLES), 
     'bike_practice_jig':TunableReference(description='\n            The jig to use for the practice area.\n            ',
       manager=services.definition_manager()), 
     'ride_off_into_sunset':TunableReference(description='\n            Interaction pushed on learner sim to ride off into sunset on successful level up.\n            ',
       manager=services.get_instance_manager(Types.INTERACTION)), 
     'wait_for_bike_pickup_state':_WaitForBikePickupState.TunableFactory(description='\n            The state that waits for the bike to be picked up.\n            ',
       display_name='1. Wait For Bike Pickup',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'place_bike_state':_PlaceBikeState.TunableFactory(description='\n            The state where the practice jig is created. The learner\n            sim will also put the bike down in the jig.\n            ',
       display_name='2. Place Bike',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'practice_riding_state':_PracticeRidingState.TunableFactory(description='\n            The state where the learner sim will practice bike riding.\n            ',
       display_name='3. Practice Riding',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP), 
     'celebrate_state':_CelebrateState.TunableFactory(description='\n            The state that will have the mentor sim and learner sim celebrate bike riding success.\n            ',
       display_name='4. Celebrate',
       tuning_group=SituationComplexCommon.SITUATION_STATE_GROUP)}
    REMOVE_INSTANCE_TUNABLES = Situation.NON_USER_FACING_REMOVE_INSTANCE_TUNABLES
    PERSISTED_JIG_DEFINITION = 'jig_def'
    PERSISTED_JIG_TRANSLATION = 'jig_pos'
    PERSISTED_JIG_ORIENTATION = 'jig_orientation'
    PERSISTED_BIKE_ID = 'bike_id'

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._jig_practice_area = None
        self._loaded_practice_area_translation = None
        self._loaded_practice_area_orientation = None
        self._learner = None
        self._mentor = None
        self._bicycle = None
        self._bicycle_id = self._get_init_bicycle(self._seed.extra_kwargs, self._seed.custom_init_params_reader)

    def _get_init_bicycle(self, extra_kwargs, reader):
        if reader is not None:
            return reader.read_uint64(self.PERSISTED_BIKE_ID, None)
        return extra_kwargs.get('default_target_id', None)

    @classmethod
    def _states(cls):
        return (SituationStateData(1, _WaitForBikePickupState, factory=(cls.wait_for_bike_pickup_state)),
         SituationStateData(2, _PlaceBikeState, factory=(cls.place_bike_state)),
         SituationStateData(3, _PracticeRidingState, factory=(cls.practice_riding_state)),
         SituationStateData(4, _CelebrateState, factory=(cls.celebrate_state)))

    @classmethod
    def default_job(cls):
        pass

    @classmethod
    def _get_tuned_job_and_default_role_state_tuples(cls):
        return [(cls.learner_job_and_role_state.job, cls.learner_job_and_role_state.role_state),
         (
          cls.mentor_job_and_role_state.job, cls.mentor_job_and_role_state.role_state)]

    def _destroy(self):
        super()._destroy()
        if self._jig_practice_area is not None:
            self._jig_practice_area.make_transient()
        self._jig_practice_area = None

    def start_situation(self):
        super().start_situation()
        if self._bicycle_id and services.inventory_manager().get(self._bicycle_id):
            self._change_state(self.place_bike_state())
        else:
            self._change_state(self.wait_for_bike_pickup_state())

    def load_situation(self):
        result = super().load_situation()
        if result:
            result = self._load_saved_jig(self._seed.custom_init_params_reader)
        return result

    def _on_add_sim_to_situation(self, sim, job_type, role_state_type_override=None):
        super()._on_add_sim_to_situation(sim, job_type, role_state_type_override)
        self._cur_state.start_initial_interactions()

    def get_learner_sim(self):
        if self._learner is None:
            self._learner = next(iter(self.all_sims_in_job_gen(self.learner_job_and_role_state.job)), None)
        return self._learner

    def get_mentor_sim(self):
        if self._mentor is None:
            self._mentor = next(iter(self.all_sims_in_job_gen(self.mentor_job_and_role_state.job)), None)
        return self._mentor

    def get_bicycle(self):
        if self._bicycle is None:
            if not self._bicycle_id:
                return
            self._bicycle = services.object_manager().get(self._bicycle_id)
            if self._bicycle is None:
                self._bicycle = services.inventory_manager().get(self._bicycle_id)
        return self._bicycle

    def _save_custom_situation(self, writer):
        super()._save_custom_situation(writer)
        if self._jig_practice_area:
            jig = self._jig_practice_area
            transform = jig.location.transform
            writer.write_uint64(self.PERSISTED_JIG_DEFINITION, jig.guid64)
            writer.write_floats(self.PERSISTED_JIG_TRANSLATION, (transform.translation.x, transform.translation.y, transform.translation.z))
            writer.write_floats(self.PERSISTED_JIG_ORIENTATION, (transform.orientation.x, transform.orientation.y, transform.orientation.z, transform.orientation.w))
        if self._bicycle is not None:
            writer.write_uint64(self.PERSISTED_BIKE_ID, self._bicycle.id)

    def _load_saved_jig(self, reader):
        jig_definition = reader.read_uint64(self.PERSISTED_JIG_DEFINITION, None)
        if jig_definition is not None:
            translation = reader.read_floats(self.PERSISTED_JIG_TRANSLATION, None)
            orientation = reader.read_floats(self.PERSISTED_JIG_ORIENTATION, None)
            self._loaded_practice_area_translation = sims4.math.Vector3(translation[0], translation[1], translation[2])
            self._loaded_practice_area_orientation = sims4.math.Quaternion(orientation[0], orientation[1], orientation[2], orientation[3])
        return True

    def initialize_practice_jig(self, interaction):
        if self._jig_practice_area is not None:
            return True
        if self.create_practice_jig():
            return True
        learner_sim = self.get_learner_sim()
        if learner_sim is None:
            self._self_destruct()
            return False
        fail_context = InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)
        learner_sim.push_super_affordance((InteractionFailureOptions.ROUTE_FAILURE_AFFORDANCE), None, fail_context,
          interaction_name=interaction.get_name(target=None, context=fail_context),
          interaction_icon_info=interaction.get_icon_info(target=None, context=fail_context))
        self._self_destruct()
        return False

    def create_practice_jig(self):
        if self._jig_practice_area is not None:
            return True
            learner_sim = self.get_learner_sim()
            if learner_sim is None:
                logger.error('No learner sim for {}', self)
                return False
            jig_definition = self.bike_practice_jig
            if jig_definition is None:
                logger.error('Failed to retrieve a jig definition for {}', self)
                return False
            jig_practice_area = create_object(jig_definition)
            if jig_practice_area is None:
                logger.error('Cannot create jig {} for {}', jig_definition, self)
                return False
        else:
            routing_surface = learner_sim.routing_surface
            search_flags = placement.FGLSearchFlagsDefault | placement.FGLSearchFlag.ALLOW_GOALS_IN_SIM_POSITIONS | placement.FGLSearchFlag.ALLOW_GOALS_IN_SIM_INTENDED_POSITIONS
            if self._loaded_practice_area_translation is not None and self._loaded_practice_area_orientation is not None:
                start_transform = sims4.math.Transform(self._loaded_practice_area_translation, self._loaded_practice_area_orientation)
            else:
                start_transform = learner_sim.transform
            starting_location = placement.create_starting_location(transform=start_transform, routing_surface=routing_surface)
            fgl_context = placement.create_fgl_context_for_object(starting_location, jig_practice_area, search_flags=search_flags,
              routing_context=(learner_sim.routing_component.routing_context),
              ignored_object_ids=(self._get_ignored_object_ids()))
            translation, orientation, _ = fgl_context.find_good_location()
            if translation is None or orientation is None:
                logger.error('Unable to place practice area jig {} for {}', jig_definition, self)
                jig_practice_area.destroy()
                return False
            self._loaded_practice_area_translation_almost_equal(translation) and self._loaded_practice_area_orientation_almost_equal(orientation) or logger.error('Cannot recreate saved jig {} at ({}, {}) for {}', jig_definition, self._loaded_practice_area_translation, self._loaded_practice_area_orientation, self)
            jig_practice_area.destroy()
            return False
        jig_practice_area.move_to(routing_surface=routing_surface, translation=translation,
          orientation=orientation)
        self._jig_practice_area = jig_practice_area
        return True

    def _loaded_practice_area_translation_almost_equal(self, found: sims4.math.Vector3):
        expected = self._loaded_practice_area_translation
        return expected is None or sims4.math.vector3_almost_equal(expected, found)

    def _loaded_practice_area_orientation_almost_equal(self, found: sims4.math.Quaternion):
        expected = self._loaded_practice_area_orientation
        return expected is None or sims4.math.quaternion_almost_equal(expected, found)

    def _get_ignored_object_ids(self):
        ignored_ids = [sim.id for sim in self.all_sims_in_situation_gen()]
        if self._bicycle_id:
            ignored_ids.append(self._bicycle_id)
        return ignored_ids

    def set_can_route_in_practice_area(self, *objs):
        footprint_id = self._jig_practice_area.footprint_component.get_footprint_id()
        for obj in iter(objs):
            obj.routing_component.routing_context.ignore_footprint_contour(footprint_id)

    def get_practice_area_constraint(self):
        return interactions.constraints.Transform((self._jig_practice_area.transform), routing_surface=(self._jig_practice_area.routing_surface))

    def end_bike_practice(self, cancel=False):
        if not cancel:
            learner_sim = self.get_learner_sim()
            bicycle = self.get_bicycle()
            learner_sim.push_super_affordance((self.ride_off_into_sunset), bicycle, (InteractionContext(learner_sim, InteractionContext.SOURCE_SCRIPT, Priority.High)),
              allow_posture_changes=True)
        self._self_destruct()