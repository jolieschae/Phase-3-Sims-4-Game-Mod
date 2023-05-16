# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 221690 bytes
import functools, itertools, random
from animation.animation_interaction import AnimationInteraction
from animation.animation_overlay import AnimationOverlayComponent
from animation.animation_utils import AnimationOverrides
from animation.animation_utils import AsmAutoExitInfo, flush_all_animations
from animation.arb_accumulator import with_skippable_animation_time
from animation.awareness.awareness_component import AwarenessComponent
from animation.posture_manifest import Hand
from autonomy import autonomy_modes
from autonomy.autonomy_preference import AutonomyPreferenceType
from broadcasters.environment_score.environment_score_mixin import EnvironmentScoreMixin
from buffs.tunable import TunableBuffReference
from careers.school.school_tuning import SchoolTuning
from carry.carry_utils import get_carried_objects_gen
from carry.carrying_component import CarryingComponent
from date_and_time import DateAndTime
from distributor.ops import SetRelativeLotLocation
from distributor.system import Distributor
from element_utils import build_critical_section_with_finally, build_element, build_critical_section
from ensemble.ensemble_component import EnsembleComponent
from event_testing import test_events
from event_testing.resolver import SingleSimResolver
from interactions import priority, constraints
from interactions.aop import AffordanceObjectPair
from interactions.base.interaction import Interaction
from interactions.base.super_interaction import RallySource
from interactions.context import InteractionContext, QueueInsertStrategy, InteractionSource
from interactions.interaction_finisher import FinishingType
from interactions.interaction_queue import InteractionQueue
from interactions.priority import Priority
from interactions.privacy import PrivacyViolators
from interactions.si_state import SIState
from interactions.utils.death import DeathTracker
from interactions.utils.interaction_liabilities import FITNESS_LIABILITY, FitnessLiability
from interactions.utils.routing import FollowPath
from objects import HiddenReasonFlag, VisibilityState, ALL_HIDDEN_REASONS
from objects.base_interactions import JoinInteraction, AskToJoinInteraction
from objects.components.carryable_component import CarryTargetInteraction
from objects.components.consumable_component import ConsumableComponent
from objects.game_object import GameObject
from objects.mixins import LockoutMixin
from objects.object_enums import ItemLocation, PersistenceType, ResetReason
from objects.part import Part
from placement import WaterDepthInfo
from postures import ALL_POSTURES, posture_graph, PostureTrack
from postures.posture_specs import PostureSpecVariable, get_origin_spec
from postures.posture_state import PostureState
from postures.transition_sequence import DerailReason
from protocolbuffers.Consts_pb2 import MGR_OBJECT
from routing import SurfaceType, SurfaceIdentifier
from routing.portals.portal_tuning import PortalFlags
from services.reset_and_delete_service import ResetRecord
from sims.master_controller import WorkRequest
from sims.outfits.outfit_enums import OutfitCategory, OutfitChangeReason
from sims.outfits.outfit_tuning import OutfitTuning
from sims.sim_info_mixin import HasSimInfoMixin
from sims.sim_info_types import SpeciesExtended, Age
from sims4.callback_utils import CallableList, consume_exceptions, RemovableCallableList
from sims4.geometry import test_point_in_polygon
from sims4.localization import TunableLocalizedString
from sims4.math import Transform
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import Tunable, TunableList, TunableReference, TunableMapping, TunableThreshold, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty, flexmethod, constproperty
from singletons import DEFAULT, EMPTY_SET
from socials.social_tests import SocialContextTest
from teleport.teleport_helper import TeleportHelper
from teleport.teleport_tuning import TeleportTuning
from terrain import get_water_depth, get_water_depth_at_location
from traits.trait_quirks import TraitQuirkSet
from uid import UniqueIdGenerator
from vehicles.vehicle_tuning import get_favorite_tag_for_surface
from world import region
from world.ocean_tuning import OceanTuning
import autonomy.autonomy_request, buffs.buff, build_buy, caches, cas.cas, clock, date_and_time, distributor.fields, distributor.ops, element_utils, elements, enum, gsi_handlers.sim_timeline_handlers, interactions.constraints, objects.components.topic_component, placement, routing, services, sims.multi_motive_buff_tracker, sims.ui_manager, sims4.log, statistics.commodity
try:
    import _zone
except ImportError:

    class _zone:

        @staticmethod
        def add_sim(_):
            pass

        @staticmethod
        def remove_sim(_):
            pass


logger = sims4.log.Logger('Sim')

def __reload__(old_module_vars):
    global GLOBAL_AUTONOMY
    GLOBAL_AUTONOMY = old_module_vars['GLOBAL_AUTONOMY']


class SimulationState(enum.Int, export=False):
    INITIALIZING = 1
    RESETTING = 2
    SIMULATING = 3
    BEING_DESTROYED = 4


class LOSAndSocialConstraintTuning:
    constraint_expansion_amount = Tunable(description="\n        The amount, in meters, to expand the Sim's current constraint by when\n        calculating fallback social constraints. This number should be equal to\n        the tuned radius for the standard social group constraint minus a\n        nominal amount, such as 1 meter to prevent extremely small intersections\n        from being considered valid.\n        ",
      tunable_type=float,
      default=5)
    num_sides_for_circle_expansion_of_point_constraint = Tunable(description='\n        The number of sides to use when creating a circle for expanding point\n        constraints for the fallback social constraint.\n        ',
      tunable_type=int,
      default=8)
    incompatible_target_sim_route_nearby_frequency = Tunable(description='\n        The number of sim minutes to delay in between routing nearby the target\n        Sim of a social interaction if they are in an incompatible state (such\n        as sleeping).\n        ',
      tunable_type=float,
      default=5)
    maximum_intended_distance_to_route_nearby = Tunable(description="\n        The maximum distance in meters from the target Sim's current position to\n        their intended position where a Sim will stop the target Sim instead of\n        routing to their intended position. Note: this only applies to Sims who\n        are trying to socialize with a target Sim at higher-priority than the\n        interaction that Sim is running.\n        ",
      tunable_type=float,
      default=20)
    minimum_delay_between_route_nearby_attempts = Tunable(description="\n        The minimum delay, in Sim minutes, between route nearby attempts when a\n        social is in the head of a Sim's queue. NOTE: This is performance-\n        critical so please don't change this unless you know what you are doing.\n        ",
      tunable_type=float,
      default=5)
    minimum_adjustment_cone_radius = Tunable(description='\n        The minimum radius in meters, that the Sim needs to be in front of the\n        target Sim when running social adjustment before a social super\n        interaction.\n        ',
      tunable_type=float,
      default=0.7)
    adjustment_cone_angle = Tunable(description='\n        The angle in radians of the social adjustment cone in front of the\n        target sim during a social super interaction.\n        ',
      tunable_type=float,
      default=1.5707)


class Sim(HasSimInfoMixin, LockoutMixin, EnvironmentScoreMixin, GameObject):
    INSTANCE_TUNABLES = {'_interaction_queue':InteractionQueue.TunableFactory(tuning_group=GroupNames.COMPONENTS), 
     'trait_quirks':TraitQuirkSet.TunableFactory(tuning_group=GroupNames.COMPONENTS), 
     'initial_buff':TunableBuffReference(description='\n            A buff that will be permanently added to the Sim on creation. Used\n            to affect the neutral state of a Sim.\n            '), 
     '_phone_affordances':TunableList(description="\n            A list of affordances generated when the player wants to use the\n            Sim's cell phone.\n            ",
       tunable=TunableReference(description='\n                An affordance that can be run as a solo interaction.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True)), 
     '_relation_panel_affordances':TunableList(description='\n            A list of affordances that are shown when the player clicks on a Sim\n            in the relationship panel. These affordances must be able to run as\n            solo interactions, meaning they cannot have a target object or Sim.\n            \n            When the selected interaction runs, the Subject type \n            "PickedItemId" will be set to the clicked Sim\'s id. For example,\n            a relationship change loot op with Subject as Actor and Target\n            Subject as PickedItemId will change the relationship between the\n            Active Sim and the Sim selected in the Relationship Panel.\n            ',
       tunable=TunableReference(description='\n                An affordance shown when the player clicks on a relation in the\n                relationship panel.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True)), 
     'animation_overlay_component':AnimationOverlayComponent.TunableFactory(description='\n            Tune animation overlays that are constantly played on this Sim.\n            ',
       tuning_group=GroupNames.COMPONENTS), 
     '_carrying_component':CarryingComponent.TunableFactory(description='\n            Define how this Sim picks up, holds, and puts down carryable\n            objects.\n            ',
       tuning_group=GroupNames.COMPONENTS), 
     '_awareness_component':OptionalTunable(description='\n            If enabled, this Sim will react to stimuli using the client-driven\n            awareness system.\n            ',
       tunable=AwarenessComponent.TunableFactory(),
       tuning_group=GroupNames.COMPONENTS), 
     '_ensemble_component':OptionalTunable(description='\n            If enabled, the Sim will have specific ensemble-related\n            functionality. This is not a requirement for Sims to be in\n            ensembles.\n            ',
       tunable=EnsembleComponent.TunableFactory(),
       tuning_group=GroupNames.COMPONENTS), 
     '_school':OptionalTunable(description='\n            If enabled, this Sim is required to be enrolled in school at\n            specific ages.\n            ',
       tunable=SchoolTuning.TunableFactory(),
       tuning_group=GroupNames.COMPONENTS)}
    _reaction_triggers = {}
    FOREIGN_ZONE_BUFF = buffs.buff.Buff.TunableReference(description='\n        This buff is applied to any sim that is not in their home zone.  It is\n        used by autonomy for NPCs to score the GoHome interaction.\n        ')
    BUFF_CLOTHING_REASON = TunableLocalizedString(description='\n        The localized string used to give reason why clothing buff was added.\n        Does not support any tokens.\n        ')
    MULTI_MOTIVE_BUFF_MOTIVES = TunableMapping(description='\n        Buffs, Motives and the threshold needed for that motive to count towards\n        the multi motive buff\n        ',
      key_type=buffs.buff.Buff.TunableReference(description='\n            Buff that is added when all the motives are above their threshold\n            ',
      pack_safe=True),
      value_type=TunableMapping(description='\n            Motives and the threshold needed for that motive to count towards\n            the multi motive buff\n            ',
      key_type=statistics.commodity.Commodity.TunableReference(description='\n                Motive needed above threshold to get the buff\n                ',
      pack_safe=True),
      value_type=TunableThreshold(description='\n                Threshold at which this motive counts for the buff\n                ')))

    def __init__(self, *args, **kwargs):
        self._sim_info = None
        self._simulation_state = SimulationState.INITIALIZING
        (super().__init__)(*args, **kwargs)
        self.add_component(objects.components.topic_component.TopicComponent(self))
        self.add_component(objects.components.sim_inventory_component.SimInventoryComponent(self))
        self.add_component(self.animation_overlay_component(self))
        self.add_component(self._carrying_component(self))
        if self._awareness_component is not None:
            self.add_component(self._awareness_component(self))
        if self._ensemble_component is not None:
            self.add_component(self._ensemble_component(self))
        self.queue = None
        self._is_removed = False
        self._starting_up = False
        self._persistence_group = objects.persistence_groups.PersistenceGroups.SIM
        self._route_fail_disable_count = 0
        self._voice_pitch_override = None
        self.waiting_dialog_response = None
        self._posture_state = None
        self.target_posture = None
        self.waiting_multi_sim_posture = False
        self._si_state = SIState(self)
        self._obj_manager = None
        self._lot_routing_restriction_ref_count = 0
        self.on_social_group_changed = CallableList()
        self._social_groups = []
        self.on_social_geometry_changed = CallableList()
        self.on_putdown_event = CallableList()
        self.on_posture_event = CallableList()
        self._ui_manager = sims.ui_manager.UIManager(self)
        self._posture_compatibility_filter = []
        self._mixers_locked_out = {}
        self._front_page_cooldown = {}
        self.needs_fitness_update = False
        self.asm_auto_exit = AsmAutoExitInfo()
        self.animation_interaction = None
        self.last_affordance = None
        self.last_animation_factory = None
        self._sleeping = False
        self._buff_handles = []
        self.interaction_logging = False
        self.transition_path_logging = False
        self._multi_motive_buff_trackers = []
        self._los_constraint = None
        self._social_group_constraint = None
        self.on_start_up = RemovableCallableList()
        self.object_ids_to_ignore = set()
        self._posture_target_refs = []
        self.next_passive_balloon_unlock_time = DateAndTime(0)
        self.two_person_social_transforms = {}
        self._intended_position_on_active_lot = False
        self.active_transition = None
        self._allow_route_instantly_when_hitting_marks = False
        self.ignore_blocking_near_destination = False
        self.current_object_set_as_head = None
        self._handedness = None
        self._locked_param_cache = {}
        self._socials_locked = False
        self._lock_id_generator = UniqueIdGenerator()
        self._affordance_locks = None
        self.asm_last_call_time = 0
        self.zero_length_asm_calls = 0
        self._dynamic_preroll_commodity_flags_map = None
        self._teleport_style_interactions_to_inject = None
        self.ready_to_be_culled = False

    def __repr__(self):
        if self.sim_info is None:
            if self._simulation_state == SimulationState.INITIALIZING:
                return "sim 'Creating Sim - Unknown Name' {0:#x}".format(self.id)
            return "sim 'Destroyed Sim - Unknown Name' {0:#x}".format(self.id)
        return "<sim '{0}' {1:#x}>".format(self.full_name, self.id)

    def __str__(self):
        if self.sim_info is None:
            if self._simulation_state == SimulationState.INITIALIZING:
                return "sim 'Creating Sim - Unknown Name' {0:#x}".format(self.id)
            return 'Destroyed Sim - Unknown Name ID: {0:#x}'.format(self.id)
        return self.full_name

    @property
    def routing_surface(self):
        return self._location.world_routing_surface or self.parent.routing_surface

    @classproperty
    def reaction_triggers(cls):
        return cls._reaction_triggers

    @constproperty
    def is_sim():
        return True

    @property
    def _anim_overrides_internal(self):
        params = {'sex':self.gender.animation_gender_param, 
         'age':self.age.animation_age_param, 
         'mood':self.get_mood_animation_param_name(), 
         'species':SpeciesExtended.get_animation_species_param(self.extended_species)}
        subroot = self._get_current_subroot()
        if subroot is not None:
            params['subroot'] = subroot
        if self.sim_info.occult_tracker is not None:
            params.update(self.sim_info.occult_tracker.get_anim_overrides())
        params.update(self._get_animation_skill_param())
        return AnimationOverrides(overrides=(super()._anim_overrides_internal), params=params)

    @property
    def sim_info(self):
        return self._sim_info

    @sim_info.setter
    def sim_info(self, value):
        self._sim_info = value
        self.update_rig()

    def update_rig(self):
        self._rig = self._sim_info.rig_key

    @distributor.fields.Field(op=(distributor.ops.SetThumbnail))
    def thumbnail(self):
        return self.sim_info.thumbnail

    @thumbnail.setter
    def thumbnail(self, value):
        self.sim_info.thumbnail = value

    @distributor.fields.Field(op=(distributor.ops.SetOverrideDialogPitch))
    def voice_pitch_override(self):
        return self._voice_pitch_override

    @voice_pitch_override.setter
    def voice_pitch_override(self, value):
        self._voice_pitch_override = value

    @property
    def socials_locked(self):
        return self._socials_locked

    @socials_locked.setter
    def socials_locked(self, value):
        self._socials_locked = value

    @property
    def block_id(self):
        if self.zone_id is not None:
            if self.zone_id != 0:
                return build_buy.get_block_id(self.zone_id, self.location.transform.translation, self.level)
        return 0

    @property
    def parented_vehicle(self):
        parent = self.parent
        if parent is None or parent.vehicle_component is None:
            return
        return parent

    @property
    def parent_may_move(self):
        parent = self.parent
        return parent is not None and parent.may_move

    @property
    def level(self):
        if self.parent is not None:
            return self.parent.level
        if self.in_pool:
            return self.location.routing_surface.secondary_id - 1
        return self.location.routing_surface.secondary_id

    @property
    @caches.cached(maxsize=None)
    def is_dying(self):
        return self.has_buff(DeathTracker.IS_DYING_BUFF)

    @property
    def is_selected(self):
        client = services.client_manager().get_client_by_household(self.household)
        if client is not None:
            return self is client.active_sim
        return False

    @property
    def transition_controller(self):
        if self.queue is not None:
            return self.queue.transition_controller

    def get_transition_global_asm_params(self):
        if self.transition_controller is not None:
            if self.transition_controller.interaction is not None:
                if self.transition_controller.interaction.transition_global_asm_params is not None:
                    return self.transition_controller.interaction.transition_global_asm_params
        return dict()

    def get_transition_asm_params(self):
        if self.transition_controller is not None:
            if self.transition_controller.interaction is not None:
                if self.transition_controller.interaction.transition_asm_params is not None:
                    return self.transition_controller.interaction.transition_asm_params
        return dict()

    @property
    def si_state(self):
        return self._si_state

    @property
    def is_valid_posture_graph_object(self):
        return True

    @property
    def should_route_fail(self):
        return self._route_fail_disable_count == 0

    @property
    def should_mark_as_new(self):
        return False

    def set_allow_route_instantly_when_hitting_marks(self, allow):
        self._allow_route_instantly_when_hitting_marks = allow

    @property
    def is_simulating(self):
        return self._simulation_state == SimulationState.SIMULATING

    @property
    def is_being_destroyed(self):
        return self._simulation_state == SimulationState.RESETTING and self.reset_reason() == ResetReason.BEING_DESTROYED

    @property
    def is_mobile(self):
        return self.sim_info.is_mobile

    @property
    def on_home_lot(self):
        current_zone = services.current_zone()
        if self.household.home_zone_id == current_zone.id:
            active_lot = current_zone.lot
            if active_lot.is_position_on_lot(self.position):
                return True
        return False

    @property
    def affordance_locks(self):
        return self._affordance_locks

    def is_affordance_locked(self, affordance):
        if self._affordance_locks is None:
            return False
        tunable_affordance_filters = []
        for affordance_filter in self._affordance_locks.values():
            if affordance_filter is None:
                return True
            tunable_affordance_filters.append(affordance_filter)

        for affordance_filter in tunable_affordance_filters:
            if not affordance_filter(affordance):
                break
        else:
            return False

        return True

    def set_affordance_lock(self, affordance_filter=None):
        unique_id = self._lock_id_generator()
        if self._affordance_locks is None:
            self._affordance_locks = {}
        self._affordance_locks[unique_id] = affordance_filter
        return unique_id

    def remove_affordance_lock(self, lock_id):
        if self._affordance_locks is None or lock_id not in self._affordance_locks:
            logger.error('Trying to remove a lock id that was already removed or never existed: {}', lock_id)
        del self._affordance_locks[lock_id]
        if not self._affordance_locks:
            self._affordance_locks = None

    def set_location_without_distribution(self, value):
        if self._location.transform.translation != sims4.math.Vector3.ZERO():
            if value.parent is None:
                if value.transform.translation == sims4.math.Vector3.ZERO():
                    logger.callstack(('Attempting to move an unparented object {} to position Zero'.format(self)), level=(sims4.log.LEVEL_ERROR))
        super().set_location_without_distribution(value)

    def update_intended_position_on_active_lot(self, *_, update_ui=False, **__):
        arrival_spawn_point = services.current_zone().active_lot_arrival_spawn_point
        if not (services.active_lot().is_position_on_lot(self.intended_position) or arrival_spawn_point) is not None or test_point_in_polygon(self.intended_position, arrival_spawn_point.get_footprint_polygon()):
            new_intended_position_on_active_lot = True
        else:
            new_intended_position_on_active_lot = False
        on_active_lot = new_intended_position_on_active_lot
        parent = self.parent
        if parent is not None:
            if parent.is_sim:
                on_active_lot = True
        msg = SetRelativeLotLocation(self.id, on_active_lot, self.sim_info.lives_here, self.sim_info.is_in_travel_group())
        distributor = Distributor.instance()
        distributor.add_op(self, msg)
        on_off_lot_update = self._intended_position_on_active_lot != new_intended_position_on_active_lot
        self._intended_position_on_active_lot = new_intended_position_on_active_lot
        if on_off_lot_update or update_ui:
            services.get_event_manager().process_event((test_events.TestEvent.SimActiveLotStatusChanged), sim_info=(self.sim_info), on_active_lot=new_intended_position_on_active_lot)

    def preload_outdoor_streetwear_change(self, final_si, preload_outfit_set):
        weather_service = services.weather_service()
        if weather_service is not None:
            weather_outfit_category_and_index = weather_service.get_weather_outfit_change(SingleSimResolver(self._sim_info))
            if weather_outfit_category_and_index is not None:
                self.transition_controller.outdoor_streetwear_change[self.id] = weather_outfit_category_and_index
                preload_outfit_set.add(weather_outfit_category_and_index)
                return
        if self.sim_info._current_outfit[0] in OutfitTuning.INAPPROPRIATE_STREETWEAR:
            if self.transition_controller is None:
                return
            remaining_transitions = self.transition_controller.get_transition_specs(self)
            for transition_spec in remaining_transitions:
                if transition_spec.portal_obj is not None:
                    outfit_category_and_index = transition_spec.portal_obj.get_on_entry_outfit(final_si, (transition_spec.portal_id), sim_info=(self.sim_info))
                    if outfit_category_and_index is None:
                        continue
                    if outfit_category_and_index[0] in OutfitTuning.INAPPROPRIATE_STREETWEAR:
                        outfit_category_and_index = None
                    break
            else:
                outfit_category_and_index = None

            if outfit_category_and_index is None:
                outfit_category_and_index = self.sim_info.get_outfit_for_clothing_change(final_si, OutfitChangeReason.DefaultOutfit)
            self.transition_controller.outdoor_streetwear_change[self.id] = outfit_category_and_index
            preload_outfit_set.add(outfit_category_and_index)

    @distributor.fields.Field(op=(distributor.ops.SetSimSleepState))
    def sleeping(self):
        return self._sleeping

    @sleeping.setter
    def sleeping(self, value):
        self._sleeping = value

    def save_object(self, object_list, item_location, container_id):
        pass

    def get_location_for_save(self):
        for sim_primitive in self.primitives:
            if isinstance(sim_primitive, FollowPath):
                node = sim_primitive.get_next_non_portal_node()
                if node is None:
                    continue
                position = (sims4.math.Vector3Immutable)(*node.position)
                orientation = (sims4.math.QuaternionImmutable)(*node.orientation)
                break
        else:
            transform = self.transform
            position = transform.translation
            orientation = transform.orientation

        if self.location.world_routing_surface is not None:
            level = self.location.level
        else:
            level = 0
        if self.location.routing_surface is not None:
            surface_id = self.location.routing_surface.type
        else:
            surface_id = 1
        return (position, orientation, level, surface_id)

    def get_inventory_proto_for_save(self):
        inventory_msg = self.inventory_component.save_items()
        if inventory_msg is None:
            return
        inventory = self.inventory_component
        for parented_item in self.children:
            if inventory.should_save_parented_item_to_inventory(parented_item):
                parented_item.save_object(inventory_msg.objects, ItemLocation.SIM_INVENTORY, self.id)

        vehicle = self.parented_vehicle
        if vehicle is not None:
            if inventory.should_save_parented_item_to_inventory(vehicle):
                vehicle.save_object(inventory_msg.objects, ItemLocation.SIM_INVENTORY, self.id)
        return inventory_msg

    def get_vehicles_for_path(self, path):
        supported_vehicles = []
        favorites_tracker = self.sim_info.favorites_tracker
        favorite_vehicle = None
        favorite_tag = get_favorite_tag_for_surface(self.routing_surface.type)
        favorite_vehicle_id = None
        if favorites_tracker is not None:
            if favorite_tag is not None:
                favorite_vehicle_id = favorites_tracker.get_favorite_object_id(favorite_tag)
        for vehicle in self.inventory_component.vehicle_objects_gen():
            if vehicle.vehicle_component.should_deploy_for_path(path, self.routing_surface):
                if vehicle.id == favorite_vehicle_id:
                    favorite_vehicle = vehicle
                    continue
                supported_vehicles.append(vehicle)

        if favorite_vehicle is not None:
            return [
             favorite_vehicle] + supported_vehicles
        return supported_vehicles

    def get_create_after_objs(self):
        super_objs = super().get_create_after_objs()
        return (self.sim_info,) + super_objs

    def set_build_buy_lockout_state(self, lockout_state, lockout_timer=None):
        raise AssertionError('Trying to illegally set a Sim as locked out: {}'.format(self))

    def without_route_failure(self, sequence=None):

        def disable_route_fail(_):
            self._route_fail_disable_count += 1

        def enable_route_fail(_):
            self._route_fail_disable_count -= 1

        return build_critical_section_with_finally(disable_route_fail, sequence, enable_route_fail)

    @property
    def rig(self):
        return self._rig

    def inc_lot_routing_restriction_ref_count(self):
        if not self.is_npc or self.sim_info.lives_here:
            return
        self._lot_routing_restriction_ref_count += 1
        if services.current_zone().lot.is_position_on_lot(self.position):
            return
        if self.pathplan_context.get_key_mask() & routing.FOOTPRINT_KEY_ON_LOT:
            self.pathplan_context.set_key_mask(self.pathplan_context.get_key_mask() & ~routing.FOOTPRINT_KEY_ON_LOT)

    def dec_lot_routing_restriction_ref_count(self):
        if not self.is_npc or self.sim_info.lives_here:
            return
        if self._lot_routing_restriction_ref_count > 0:
            self._lot_routing_restriction_ref_count -= 1
            if self._lot_routing_restriction_ref_count == 0:
                self.pathplan_context.set_key_mask(self.pathplan_context.get_key_mask() | routing.FOOTPRINT_KEY_ON_LOT)

    def clear_lot_routing_restrictions_ref_count(self):
        self._lot_routing_restriction_ref_count = 0
        self.pathplan_context.set_key_mask(self.pathplan_context.get_key_mask() | routing.FOOTPRINT_KEY_ON_LOT)

    def execute_adjustment_interaction(self, affordance, constraint, int_priority, group_id=None, **kwargs):
        aop = AffordanceObjectPair(affordance, None, affordance, None, constraint_to_satisfy=constraint, 
         route_fail_on_transition_fail=False, 
         is_adjustment_interaction=True, **kwargs)
        context = InteractionContext(self, (InteractionContext.SOURCE_SOCIAL_ADJUSTMENT), int_priority, insert_strategy=(QueueInsertStrategy.NEXT),
          group_id=group_id,
          must_run_next=True,
          cancel_if_incompatible_in_queue=True,
          can_derail_if_constraint_invalid=False)
        return aop.test_and_execute(context)

    @property
    def ui_manager(self):
        return self._ui_manager

    def _update_social_geometry_on_location_changed(self, *args, **kwargs):
        social_group = self.get_main_group()
        if social_group is not None:
            social_group.refresh_social_geometry(sim=self)

    def notify_social_group_changed(self, group):
        if self in group:
            if group not in self._social_groups:
                self._social_groups.append(group)
        elif group in self._social_groups:
            self._social_groups.remove(group)
        self.on_social_group_changed(self, group)

    def in_non_adjustable_posture(self):
        for aspect in self._posture_state.aspects:
            if not aspect.allow_social_adjustment:
                return True

        return False

    def filter_supported_postures(self, supported_postures):
        filtered_postures = supported_postures
        if filtered_postures is ALL_POSTURES:
            return ALL_POSTURES
        for filter_func in self._posture_compatibility_filter:
            filtered_postures = filter_func(filtered_postures)

        return filtered_postures

    def may_reserve(self, *args, **kwargs):
        return False

    def on_reset_notification(self, reset_reason):
        super().on_reset_notification(reset_reason)
        self._simulation_state = SimulationState.RESETTING
        self.queue.lock()

    def on_reset_get_interdependent_reset_records(self, reset_reason, reset_records):
        super().on_reset_get_interdependent_reset_records(reset_reason, reset_records)
        master_controller = services.get_master_controller()
        master_controller.add_interdependent_reset_records(self, reset_records)
        for other_sim in master_controller.added_sims():
            if other_sim is not self and other_sim.is_sim and other_sim.has_sim_in_any_queued_interactions_required_sim_cache(self):
                reset_records.append(ResetRecord(other_sim, ResetReason.RESET_EXPECTED, self, 'In required sims of queued interaction.'))

        for social_group in self.get_groups_for_sim_gen():
            for game_object in social_group.get_objects_for_reset():
                if game_object is not self:
                    reset_records.append(ResetRecord(game_object, ResetReason.RESET_EXPECTED, self, 'In social group'))

        for interaction in self.get_all_running_and_queued_interactions():
            if interaction.prepared:
                for other_sim in interaction.required_sims():
                    if other_sim is not self:
                        reset_records.append(ResetRecord(other_sim, ResetReason.RESET_EXPECTED, self, 'required sim in {}'.format(interaction)))

        if self.posture_state is not None:
            for aspect in self.posture_state.aspects:
                target = aspect.target
                if target is not None:
                    if target.is_part:
                        target = target.part_owner
                    reset_records.append(ResetRecord(target, ResetReason.RESET_EXPECTED, self, 'Posture state aspect:{} target:{}'.format(aspect, target)))

        if self.current_object_set_as_head is not None:
            object_on_head = self.current_object_set_as_head()
            if object_on_head is not None:
                if not self.has_component(objects.components.types.PARENT_TO_SIM_HEAD_COMPONENT):
                    self.current_object_set_as_head = None
                    reset_records.append(ResetRecord(object_on_head, (ResetReason.BEING_DESTROYED),
                      source=self,
                      cause='Destroying object parented to head outside parent to sim head component'))
                else:
                    if reset_reason == ResetReason.BEING_DESTROYED:
                        inventory = self.inventory_component
                        if inventory.should_save_parented_item_to_inventory(object_on_head):
                            reset_records.append(ResetRecord(object_on_head, (ResetReason.BEING_DESTROYED),
                              source=self,
                              cause='Destroying object parented to sim, should be stored in inventory'))

    def on_reset_restart(self):
        self._start_animation_interaction()
        self.start_animation_overlays()
        self.update_animation_overlays()
        return False

    def on_state_changed(self, state, old_value, new_value, from_init):
        if not self.is_simulating:
            return
        else:
            affordances = self.sim_info.PHYSIQUE_CHANGE_AFFORDANCES
            reaction_affordance = None
            if not old_value != new_value or state == ConsumableComponent.FAT_STATE or state == ConsumableComponent.FIT_STATE:
                self.needs_fitness_update = True
                if state == ConsumableComponent.FAT_STATE:
                    reaction_affordance = affordances.FAT_CHANGE_NEUTRAL_AFFORDANCE
                    fat_commodity = ConsumableComponent.FAT_COMMODITY
                    old_fat = self.sim_info.fat
                    new_fat = self.commodity_tracker.get_value(fat_commodity)
                    midrange_fat = (fat_commodity.max_value + fat_commodity.min_value) / 2
                    self.sim_info.fat = new_fat
                    if new_fat > midrange_fat:
                        if old_fat < new_fat:
                            if new_fat == fat_commodity.max_value:
                                reaction_affordance = affordances.FAT_CHANGE_MAX_NEGATIVE_AFFORDANCE
                            else:
                                reaction_affordance = affordances.FAT_CHANGE_NEGATIVE_AFFORDANCE
                        elif old_fat > new_fat:
                            reaction_affordance = affordances.FAT_CHANGE_POSITIVE_AFFORDANCE
                    elif new_fat == fat_commodity.min_value:
                        reaction_affordance = affordances.FAT_CHANGE_MAX_POSITIVE_AFFORDANCE
                else:
                    reaction_affordance = affordances.FIT_CHANGE_NEUTRAL_AFFORDANCE
                    old_fit = self.sim_info.fit
                    new_fit = self.commodity_tracker.get_value(ConsumableComponent.FIT_COMMODITY)
                    self.sim_info.fit = new_fit
                    if old_fit < new_fit:
                        reaction_affordance = affordances.FIT_CHANGE_POSITIVE_AFFORDANCE
                    else:
                        reaction_affordance = affordances.FIT_CHANGE_NEGATIVE_AFFORDANCE
                if reaction_affordance is not None:
                    context = InteractionContext(self, (InteractionContext.SOURCE_SCRIPT), (Priority.Low), client=None, pick=None)
                    result = self.push_super_affordance(reaction_affordance, None, context)
                    if result:
                        result.interaction.add_liability(FITNESS_LIABILITY, FitnessLiability(self))
                        return
                self.sim_info.update_fitness_state()

    def _on_navmesh_updated(self):
        self.validate_current_location_or_fgl()
        if self.transition_controller is not None:
            if self.routing_component.current_path is not None and self.routing_component.current_path.nodes.needs_replan():
                if self.transition_controller.succeeded:
                    self.reset(ResetReason.RESET_EXPECTED, None, 'Traversing a path that needs replanning but is not controlled by the transition sequence.')
                elif self.routing_component.current_path.final_location.transform != self.routing_component.current_path.intended_location.transform:
                    self.validate_location(self.routing_component.current_path.intended_location) or self.reset(ResetReason.RESET_EXPECTED, None, "Traversing an path that's been canceled or derailed and the position we've chosen to cancel/derail to is not valid.")
                else:
                    zone = services.current_zone()
                    if zone.is_in_build_buy:
                        self.transition_controller.derail(DerailReason.NAVMESH_UPDATED_BY_BUILD, self)
                    else:
                        self.transition_controller.derail(DerailReason.NAVMESH_UPDATED, self)
        elif self.transition_controller.sim_is_traversing_invalid_portal(self):
            self.reset(ResetReason.RESET_EXPECTED, None, 'Transitioning through a portal that was deleted.')
        self.two_person_social_transforms.clear()

    def validate_location(self, location, from_reset=False):
        if self.is_hidden(allow_hidden_flags=(ALL_HIDDEN_REASONS & ~HiddenReasonFlag.RABBIT_HOLE)):
            return True
        routing_location = routing.Location(location.transform.translation, location.transform.orientation, location.routing_surface)
        water_depth = get_water_depth_at_location(routing_location)
        wading_interval = OceanTuning.get_actor_wading_interval(self)
        if not routing_location.routing_surface.type == routing.SurfaceType.SURFACETYPE_POOL or (build_buy.is_location_pool(location.transform.translation, location.level) or wading_interval is None or water_depth) <= wading_interval.upper_bound:
            return False
        else:
            if not (wading_interval is None and water_depth > 0):
                if wading_interval is not None:
                    if water_depth >= wading_interval.upper_bound:
                        return False
                else:
                    allowed_targets = set()
                    for interaction in itertools.chain((self.queue.running,), self.si_state):
                        if not interaction is None:
                            if interaction.target is None:
                                continue
                            allowed_targets.add(interaction.target)
                            allowed_targets.add(interaction.target.parent)

                    if self.transition_controller is not None:
                        allowed_targets.update(self.transition_controller.relevant_objects)
                    contexts = {obj.raycast_context() for obj in allowed_targets if obj is not None}
                    contexts.add(self.routing_context)
                    on_object_surface = routing_location.routing_surface.type == routing.SurfaceType.SURFACETYPE_OBJECT
                    test_portal_clearance = self.posture.unconstrained and not self.in_pool and not on_object_surface
                    if not from_reset:
                        if on_object_surface:
                            agent_radius = self.posture.unconstrained or routing.FAKE_AGENT_RADIUS_FOR_OBJECT_ROUTING_SURFACE_VALIDATION
                agent_radius = routing.get_default_agent_radius()
            for context in contexts:
                if placement.validate_sim_location(routing_location, agent_radius, context, test_portal_clearance):
                    return True

            return False

    def validate_current_location_or_fgl(self, from_reset=False):
        parent = self.parent
        if parent is not None:
            return parent.is_sim or from_reset or None
            self.clear_parent(parent.transform, parent.routing_surface)
        else:
            zone = services.current_zone()
            if not zone.is_in_build_buy:
                if not from_reset:
                    if not self.can_swim():
                        if self.should_be_swimming_at_position((self.position), (self.location.level), check_can_swim=False) or self.routing_surface.type == SurfaceType.SURFACETYPE_OBJECT:
                            terrain_object = services.terrain_service.terrain_object()
                            _, surface_obj_id = terrain_object.get_routing_surface_height_and_surface_object_at(self.position.x, self.position.z, self.routing_surface)
                            if surface_obj_id != 0:
                                return
                    else:
                        return
        if from_reset:
            if zone.is_in_build_buy:
                services.get_event_manager().process_event((test_events.TestEvent.OnBuildBuyReset), sim_info=(self.sim_info))
        if self.routing_component.current_path is not None:
            if from_reset:
                return
            if any((sim_primitive.is_traversing_invalid_portal() for sim_primitive in self.primitives if isinstance(sim_primitive, FollowPath))):
                self.reset(ResetReason.RESET_EXPECTED, self, 'Traversing invalid portal.')
            return
        location, on_surface = self.get_location_on_nearest_surface_below()
        if self.validate_location(location, from_reset=from_reset):
            if not on_surface:
                if not from_reset:
                    self.reset(ResetReason.RESET_EXPECTED, self, 'Failed to validate location.')
                self.location = location
            return
        ignored_object_ids = {self.sim_id}
        ignored_object_ids.update((child.id for child in self.children_recursive_gen()))
        parent_object = self.parent_object()
        while parent_object is not None:
            ignored_object_ids.add(parent_object.id)
            parent_object = self.parent_object()

        search_flags = placement.FGLSearchFlagsDefault | placement.FGLSearchFlag.USE_SIM_FOOTPRINT | placement.FGLSearchFlag.STAY_IN_CURRENT_BLOCK
        starting_location = placement.create_starting_location(location=location)
        wading_interval = OceanTuning.get_actor_wading_interval(self)
        if wading_interval is None:
            min_wading_depth = None
            max_wading_depth = 0.0
        else:
            if starting_location.routing_surface.type == routing.SurfaceType.SURFACETYPE_POOL:
                min_wading_depth = wading_interval.upper_bound
                max_wading_depth = None
            else:
                min_wading_depth = None
                max_wading_depth = wading_interval.upper_bound
        water_depth_info = WaterDepthInfo(min_water_depth=min_wading_depth, max_water_depth=max_wading_depth)

        def get_reset_location():
            fgl_context = placement.FindGoodLocationContext(starting_location, ignored_object_ids=ignored_object_ids,
              additional_avoid_sim_radius=(routing.get_sim_extra_clearance_distance()),
              search_flags=search_flags,
              routing_context=(self.routing_context),
              water_depth_info=water_depth_info)
            return fgl_context.find_good_location()

        trans, orient, _ = get_reset_location()
        new_location_routing_surface = starting_location.routing_surface

        def _push_location_to_world_surface():
            new_world_surface = routing.SurfaceIdentifier(services.current_zone_id(), self._get_best_valid_level(), routing.SurfaceType.SURFACETYPE_WORLD)
            starting_location.routing_surface = new_world_surface
            return new_world_surface

        if not new_location_routing_surface.type == routing.SurfaceType.SURFACETYPE_OBJECT or trans is None or orient is None:
            new_location_routing_surface = _push_location_to_world_surface()
            trans, orient, _ = get_reset_location()
        else:
            if not routing.test_connectivity_pt_pt(self.routing_location, routing.Location(trans, orient, routing_surface=new_location_routing_surface), self.routing_context):
                new_location_routing_surface = _push_location_to_world_surface()
                trans, orient, _ = get_reset_location()
            else:
                if trans is None or orient is None:
                    if not from_reset:
                        self.reset(ResetReason.RESET_EXPECTED, self, 'Failed to find location.')
                        return
                    self.fgl_reset_to_landing_strip()
                    return
                from_reset or self.reset(ResetReason.RESET_EXPECTED, self, 'Failed to find location.')
            new_transform = sims4.math.Transform(trans, orient)
            self.location = location.clone(transform=new_transform, routing_surface=new_location_routing_surface)

    def fgl_reset_to_landing_strip(self):
        self.reset(ResetReason.RESET_EXPECTED, self, 'Reset to landing strip.')
        zone = services.current_zone()
        spawn_point = zone.active_lot_arrival_spawn_point
        if spawn_point is None:
            self.move_to_landing_strip()
            return
        else:
            spawn_trans, _ = spawn_point.next_spawn_spot()
            location = routing.Location(spawn_trans, routing_surface=(spawn_point.routing_surface))
            success = False
            if self.pathplan_context.get_key_mask() & routing.FOOTPRINT_KEY_ON_LOT:
                self.pathplan_context.set_key_mask(self.pathplan_context.get_key_mask() & ~routing.FOOTPRINT_KEY_ON_LOT)
                should_have_permission = True
            else:
                should_have_permission = False
        try:
            starting_location = placement.create_starting_location(location=location)
            fgl_context = placement.create_fgl_context_for_sim(starting_location, self, additional_avoid_sim_radius=(routing.get_default_agent_radius()),
              routing_context=(self.routing_context))
            trans, orient, _ = fgl_context.find_good_location()
            if trans is not None:
                if orient is not None:
                    transform = Transform(trans, orient)
                    if spawn_point is not None:
                        self.location = self.location.clone(routing_surface=(spawn_point.routing_surface),
                          transform=transform)
                    else:
                        self.location = self.location.clone(transform=transform)
                    success = True
        finally:
            if should_have_permission:
                self.pathplan_context.set_key_mask(self.pathplan_context.get_key_mask() | routing.FOOTPRINT_KEY_ON_LOT)

        return success

    def _get_best_valid_level(self):
        position = sims4.math.Vector3(self.position.x, self.position.y, self.position.z)
        for i in range(self.routing_surface.secondary_id, build_buy.get_lowest_level_allowed() - 1, -1):
            if build_buy.has_floor_at_location(position, i):
                return i

        if self.routing_surface.secondary_id < 0:
            for i in range(self.routing_surface.secondary_id, 0, 1):
                if build_buy.has_floor_at_location(position, i):
                    return i

        return 0

    def get_location_on_nearest_surface_below(self):
        if self.posture_state.valid:
            if not ((self.posture.constrained_by_object or self.posture.consider_constrained_for_on_surface_checks or self.active_transition) is not None):
                return (
                 self.location, True)
        else:
            location = self.location
            level = self._get_best_valid_level()
            if self.location.routing_surface.type == routing.SurfaceType.SURFACETYPE_POOL:
                surface_type = self._should_be_swimming() or routing.SurfaceType.SURFACETYPE_WORLD
            else:
                surface_type = None
            if level != location.routing_surface.secondary_id or surface_type is not None:
                routing_surface = routing.SurfaceIdentifier(location.routing_surface.primary_id, level, surface_type or location.routing_surface.type)
                location = location.clone(routing_surface=routing_surface)
            on_surface = False
            snapped_y = services.terrain_service.terrain_object().get_routing_surface_height_at(location.transform.translation.x, location.transform.translation.z, location.routing_surface)
            LEVEL_SNAP_TOLERANCE = 0.001
            if location.routing_surface == self.routing_surface and sims4.math.almost_equal(snapped_y, (location.transform.translation.y), epsilon=LEVEL_SNAP_TOLERANCE):
                on_surface = True
        translation = sims4.math.Vector3(location.transform.translation.x, snapped_y, location.transform.translation.z)
        location = location.clone(translation=translation)
        return (location, on_surface)

    def move_to_landing_strip(self):
        zone = services.current_zone()
        spawn_point = zone.get_spawn_point()
        if spawn_point is not None:
            trans, _ = spawn_point.next_spawn_spot()
            self.location = self.location.clone(translation=trans, routing_surface=(spawn_point.routing_surface))
            self.fade_in()
            return
        logger.warn('No landing strip exists in zone {}', zone)

    def fade_in(self, fade_duration=None, immediate=False, additional_channels=None):
        if self.posture.is_vehicle:
            vehicle = self.posture.target
            if not immediate:
                additional_channels = [] if additional_channels is None else additional_channels
                additional_channels.append((MGR_OBJECT, vehicle.id, None))
                additional_channels.append((MGR_OBJECT, self.id, None))
            vehicle.fade_in(fade_duration=fade_duration, immediate=immediate, additional_channels=additional_channels)
        super().fade_in(fade_duration=fade_duration, immediate=immediate, additional_channels=additional_channels)

    def fade_out(self, fade_duration=None, immediate=False, additional_channels=None):
        if self.posture.is_vehicle:
            vehicle = self.posture.target
            if not immediate:
                additional_channels = [] if additional_channels is None else additional_channels
                additional_channels.append((MGR_OBJECT, vehicle.id, None))
                additional_channels.append((MGR_OBJECT, self.id, None))
            vehicle.fade_out(fade_duration=fade_duration, immediate=immediate, additional_channels=additional_channels)
        super().fade_out(fade_duration=fade_duration, immediate=immediate, additional_channels=additional_channels)

    def _start_animation_interaction(self):
        animation_interaction_context = InteractionContext(self, InteractionContext.SOURCE_SCRIPT, priority.Priority.High)
        animation_aop = AffordanceObjectPair(AnimationInteraction, None, AnimationInteraction, None)
        self.animation_interaction = animation_aop.interaction_factory(animation_interaction_context).interaction

    def _stop_animation_interaction(self):
        if self.animation_interaction is not None:
            self.animation_interaction.cancel(FinishingType.RESET, 'Sim is being reset.')
            self.animation_interaction.on_removed_from_queue()
            self.animation_interaction = None

    def create_animation_interaction(self):
        animation_interaction_context = InteractionContext(self, InteractionContext.SOURCE_SCRIPT, priority.Priority.High)
        animation_aop = AffordanceObjectPair(AnimationInteraction, None, AnimationInteraction, None)
        return animation_aop.interaction_factory(animation_interaction_context).interaction

    def on_reset_internal_state(self, reset_reason):
        being_destroyed = reset_reason == ResetReason.BEING_DESTROYED
        try:
            try:
                if not being_destroyed:
                    if self.is_npc:
                        if self.sim_info.get_current_outfit()[0] == OutfitCategory.BATHING:
                            if not self.in_pool:
                                self.set_current_outfit((OutfitCategory.EVERYDAY, 0))
                    self.set_last_user_directed_action_time()
                else:
                    services.get_master_controller().on_reset_sim(self, reset_reason)
                    self.hide(HiddenReasonFlag.NOT_INITIALIZED)
                    self.queue.on_reset(being_destroyed)
                    self.si_state.on_reset()
                    self.socials_locked = False
                    if self.posture_state is not None:
                        self.posture_state.on_reset(ResetReason.RESET_EXPECTED)
                    if not being_destroyed:
                        self.sim_info.resend_current_outfit()
                    self._posture_target_refs.clear()
                    self._stop_environment_score()
                    self._stop_animation_interaction()
                    self.stop_animation_overlays()
                    self.zero_length_asm_calls = 0
                    self.ui_manager.remove_all_interactions()
                    self.on_sim_reset(being_destroyed)
                    self.clear_all_autonomy_skip_sis()
                    if being_destroyed:
                        self._remove_multi_motive_buff_trackers()
                    self.asm_auto_exit.clear()
                    self.last_affordance = None
                    self.last_animation_factory = None
                    if not being_destroyed:
                        if not self._is_removed:
                            try:
                                self.validate_current_location_or_fgl(from_reset=True)
                                self.refresh_los_constraint()
                                self.visibility = VisibilityState()
                                self.opacity = 1
                            except Exception:
                                logger.exception('Exception thrown while finding good location for Sim on reset:')

                    services.get_event_manager().process_event((test_events.TestEvent.OnSimReset), sim_info=(self.sim_info))
                    self.two_person_social_transforms.clear()
                    self.current_object_set_as_head = None
                    self.waiting_multi_sim_posture = False
            except:
                logger.exception('TODO: Exception thrown during Sim reset, possibly we should be kicking the Sim out of the game.')
                raise

        finally:
            super().on_reset_internal_state(reset_reason)

    def _reset_reference_arb(self):
        self._reference_arb = None

    def _add_default_buff(self):
        if self.initial_buff.buff_type is not None:
            self.add_buff(self.initial_buff.buff_type, self.initial_buff.buff_reason)

    def running_interactions_gen(self, affordance):
        if self.si_state is not None:
            interaction_type = affordance.get_interaction_type()
            for si in self.si_state.sis_actor_gen():
                if issubclass(si.get_interaction_type(), interaction_type):
                    yield si
                else:
                    linked_interaction_type = si.get_linked_interaction_type()
                if linked_interaction_type is not None and issubclass(linked_interaction_type, interaction_type):
                    yield si

    def get_all_running_and_queued_interactions(self):
        if self.si_state is None or self.queue is None:
            logger.error('Trying to get the running and queued interactions from a Sim that has likely been removed.  Sim={}', self)
            return []
        interactions = [si for si in self.si_state.sis_actor_gen()]
        for si in self.queue:
            interactions.append(si)

        return interactions

    def get_running_and_queued_interactions_by_tag_or_affordance_type(self, type_affordances=EMPTY_SET, tags=EMPTY_SET):
        if self.si_state is None or self.queue is None:
            logger.error('Trying to get the running and queued interactions by tag from a Sim that has likely been removed.  Sim={}', self)
            return []
        running_and_queued_interactions = self.get_all_running_and_queued_interactions()
        interaction_set = set()
        for interaction in running_and_queued_interactions:
            if tags & interaction.affordance.interaction_category_tags:
                interaction_set.add(interaction)
                continue
            running_interaction_type = interaction.get_interaction_type()
            for type_affordance in type_affordances:
                if issubclass(type_affordance.get_interaction_type(), running_interaction_type):
                    interaction_set.add(interaction)
                    break

        return interaction_set

    def get_running_and_queued_interactions_by_tag(self, tags):
        if self.si_state is None or self.queue is None:
            logger.error('Trying to get the running and queued interactions by tag from a Sim that has likely been removed.  Sim={}', self)
            return []
        interaction_set = set()
        for si in self.si_state.sis_actor_gen():
            if tags & si.affordance.interaction_category_tags:
                interaction_set.add(si)

        for si in self.queue:
            if tags & si.affordance.interaction_category_tags:
                interaction_set.add(si)

        return interaction_set

    def has_running_and_queued_interactions_with_liability(self, liability_type):
        for interaction in self.get_all_running_and_queued_interactions():
            if interaction.get_liability(liability_type) is not None:
                return True

        return False

    def has_any_interaction_running_or_queued_of_tags(self, tags):
        running_and_queued_interactions = self.get_all_running_and_queued_interactions()
        for si in running_and_queued_interactions:
            if tags & si.affordance.interaction_category_tags:
                return True

        return False

    def has_any_interaction_running_or_queued_of_types(self, interaction_types):
        for si in self.get_all_running_and_queued_interactions():
            if any((issubclass(a, interaction_types) for a in si.affordances)):
                return True

        return False

    def has_sim_in_any_queued_interactions_required_sim_cache(self, sim_in_question):
        return any((interaction.has_sim_in_required_sim_cache(sim_in_question) for interaction in self.queue))

    def get_running_interactions_by_tags(self, tags):
        interaction_set = set()
        for si in self.si_state.sis_actor_gen():
            if tags & si.affordance.interaction_category_tags:
                interaction_set.add(si)

        return interaction_set

    def has_any_pending_or_running_interactions(self):
        transition_controller = self.transition_controller
        if transition_controller is not None:
            if transition_controller.interaction.visible:
                if not transition_controller.interaction.is_finishing:
                    return True
        for interaction in self.get_all_running_and_queued_interactions():
            if not interaction.visible:
                if not interaction.is_autonomous_picker_interaction:
                    continue
            if interaction.is_super:
                if interaction.pending_complete:
                    continue
            return True

        return False

    @caches.cached
    def _all_affordance_targets(self):
        results = []
        if self.si_state is not None:
            for si in self.si_state.sis_actor_gen():
                if si.is_finishing:
                    continue
                affordance = si.get_interaction_type()
                results.append((affordance, si.target))
                linked_affordance = si.get_linked_interaction_type()
                if linked_affordance is not None:
                    results.append((linked_affordance, si.target))
                for other_target in si.get_potential_mixer_targets():
                    results.append((affordance, other_target))
                    if linked_affordance is not None:
                        results.append((linked_affordance, other_target))

        return frozenset(results)

    @caches.cached
    def _shared_affordance_targets(self, sim):
        affordance_targets_a = self._all_affordance_targets()
        affordance_targets_b = sim._all_affordance_targets()
        both = affordance_targets_a & affordance_targets_b
        if both:
            result = frozenset((affordance for affordance, _ in both))
            return result
        return ()

    def is_running_interaction(self, affordance, target):
        affordance_targets = self._all_affordance_targets()
        return (affordance, target) in affordance_targets

    def are_running_equivalent_interactions(self, sim, affordance):
        shared = self._shared_affordance_targets(sim)
        return affordance in shared

    def _provided_interactions_gen(self, context, **kwargs):
        _generated_affordance = set()
        for interaction in self.si_state:
            if interaction.is_finishing:
                continue
            for affordance_data in interaction.affordance.provided_affordances:
                affordance = affordance_data.affordance
                if affordance in _generated_affordance:
                    continue
                if context.source == InteractionSource.AUTONOMY:
                    if not affordance.allow_autonomous:
                        continue
                if context.sim is self:
                    if not affordance_data.allow_self:
                        continue
                if context.sim is not None:
                    if context.sim.is_running_interaction(affordance, self):
                        continue
                    if self.are_running_equivalent_interactions(context.sim, affordance):
                        continue
                target = interaction.get_participant(affordance_data.target)
                target = target if target is not None else self
                if not affordance_data.object_filter.is_object_valid(target):
                    logger.error('Provided Affordance {} from {} is not valid to run on {}', affordance, interaction, target, owner='rmccord')
                    continue
                carry_target = interaction.get_participant(affordance_data.carry_target)
                provided_affordance = affordance
                if carry_target is not None:
                    provided_affordance = CarryTargetInteraction.generate(affordance, carry_target)
                _generated_affordance.add(affordance)
                if affordance_data.is_linked:
                    depended_on_si = interaction
                    depended_on_until_running = affordance_data.unlink_if_running
                else:
                    depended_on_si = None
                    depended_on_until_running = False
                yield from (provided_affordance.potential_interactions)(target, context, depended_on_si=depended_on_si, depended_on_until_running=depended_on_until_running, **kwargs)

        club_service = services.get_club_service()
        if club_service is not None:
            for club, affordance in club_service.provided_clubs_and_interactions_gen(context, target=self):
                aop = AffordanceObjectPair(affordance, self, affordance, None, associated_club=club, **kwargs)
                if aop.test(context):
                    yield aop

        if context.sim is not None:
            if context.sim is not self:
                for _, _, carried_object in get_carried_objects_gen(context.sim):
                    yield from (carried_object.get_provided_aops_gen)(self, context, **kwargs)

    def get_object_provided_target_affordances_gen(self, target, context, **kwargs):
        sim_inventory_component = self.get_component(objects.components.types.INVENTORY_COMPONENT)
        if sim_inventory_component is None:
            return
        shift_held = context.shift_held if context is not None else False
        for affordance, provided_affordance_data in sim_inventory_component.get_cached_target_super_affordances_gen(context, target):
            if self._can_show_affordance(shift_held, affordance):
                kwargs_copy = kwargs.copy()
                kwargs_copy['object_providing_target_affordance'] = provided_affordance_data.provider_id
                yield from (affordance.potential_interactions)(target, context, **kwargs_copy)

        if False:
            yield None

    def _potential_joinable_interactions_gen(self, context, **kwargs):

        def get_target(interaction, join_participant):
            join_target = interaction.get_participant(join_participant)
            if join_target:
                if isinstance(join_target, Part):
                    join_target = join_target.part_owner
            return join_target

        def get_join_affordance(default, join_info, joining_sim, target):
            if join_info.join_affordance.is_affordance:
                join_affordance = join_info.join_affordance.value
                if join_affordance is None:
                    join_affordance = default
                if target is not None:
                    for interaction in joining_sim.si_state:
                        if interaction.get_interaction_type() is join_affordance:
                            interaction_join_target = get_target(interaction, join_info.join_target)
                            if interaction_join_target is target:
                                return (
                                 None, target)

                return (
                 join_affordance, target)
            if context.source == InteractionSource.AUTONOMY:
                return (
                 None, target)
            commodity_search = join_info.join_affordance.value
            for interaction in joining_sim.si_state:
                if commodity_search.commodity in interaction.commodity_flags:
                    return (
                     None, target)

            join_context = InteractionContext(joining_sim, (InteractionContext.SOURCE_AUTONOMY), (Priority.High),
              client=None, pick=None, always_check_in_use=True)
            constraint = constraints.Circle(target.position, commodity_search.radius, target.routing_surface)
            autonomy_request = autonomy.autonomy_request.AutonomyRequest(joining_sim,
              (autonomy_modes.FullAutonomy), static_commodity_list=(commodity_search.commodity,), context=join_context,
              constraint=constraint,
              limited_autonomy_allowed=True,
              consider_scores_of_zero=True,
              allow_forwarding=False,
              autonomy_mode_label_override='Joinable')
            best_action = services.autonomy_service().find_best_action(autonomy_request)
            if best_action:
                return (
                 best_action, best_action.target)
            return (
             None, target)

        def get_join_aops_gen(interaction, join_sim, joining_sim, join_factory):
            interaction_type = interaction.get_interaction_type()
            join_target_ref = join_sim.ref()
            for joinable_info in interaction.joinable:
                if join_sim is self:
                    if not joinable_info.join_available:
                        continue
                else:
                    if join_sim is context.sim:
                        if not joinable_info.invite_available:
                            continue
                    join_target = get_target(interaction, joinable_info.join_target)
                    if join_target is None and interaction.sim is not self:
                        continue
                joinable_interaction, join_target = get_join_affordance(interaction_type, joinable_info, joining_sim, join_target)
                if joinable_interaction is None:
                    continue
                join_interaction = join_factory(joinable_interaction.affordance, joining_sim, interaction, joinable_info)
                for aop in (join_interaction.potential_interactions)(join_target, context, join_target_ref=join_target_ref, **kwargs):
                    result = aop.test(context)
                    if result or result.tooltip:
                        yield aop

        def create_join_si(affordance, joining_sim, join_interaction, joinable_info):
            return JoinInteraction.generate(affordance, join_interaction, joinable_info)

        def create_invite_to_join_si(affordance, joining_sim, join_interaction, joinable_info):
            return AskToJoinInteraction.generate(affordance, joining_sim, join_interaction, joinable_info)

        if context.sim is not None:
            for interaction in self.si_state.sis_actor_gen():
                if interaction.joinable and not interaction.is_finishing:
                    for aop in get_join_aops_gen(interaction, self, context.sim, create_join_si):
                        yield aop

            for interaction in context.sim.si_state.sis_actor_gen():
                if interaction.joinable and not interaction.is_finishing:
                    for aop in get_join_aops_gen(interaction, context.sim, self, create_invite_to_join_si):
                        yield aop

    def potential_preroll_interactions(self, context, get_interaction_parameters=None, **kwargs):
        potential_affordances = (super().potential_preroll_interactions)(context, get_interaction_parameters=get_interaction_parameters, **kwargs)
        active_roles = self.active_roles()
        if active_roles is None:
            return potential_affordances
        role_affordances = set((role_affordance for active_role in active_roles for role_affordance in active_role.preroll_affordances))
        for affordance in role_affordances:
            if not affordance.is_affordance_available(context=context):
                continue
            else:
                if not self.supports_affordance(affordance):
                    continue
                if get_interaction_parameters is not None:
                    interaction_parameters = get_interaction_parameters(affordance, kwargs)
                else:
                    interaction_parameters = kwargs
            for aop in (affordance.potential_interactions)(self, context, **interaction_parameters):
                potential_affordances.append(aop)

        return potential_affordances

    def _potential_behavior_affordances_gen(self, context, **kwargs):

        def _get_role_state_affordances_gen(active_roles, use_target=False):
            if active_roles is not None:
                role_affordances = set((role_affordance for active_role in active_roles for role_affordance in active_role.role_target_affordances if use_target else active_role.role_affordances))
                for affordance in role_affordances:
                    if self._can_show_affordance(shift_held, affordance):
                        yield affordance

        shift_held = False
        if context is not None:
            shift_held = context.shift_held
        yield from _get_role_state_affordances_gen(self.active_roles())
        for affordance in self.sim_info.get_super_affordance_availability_gen():
            if self._can_show_affordance(shift_held, affordance):
                yield affordance

        for affordance in self.sim_info.trait_tracker.get_cached_super_affordances_gen():
            if self._can_show_affordance(shift_held, affordance):
                yield affordance

        for affordance in self.sim_info.commodity_tracker.get_cached_super_affordances_gen():
            if self._can_show_affordance(shift_held, affordance):
                yield affordance

        for affordance in self.inventory_component.get_cached_super_affordances_gen():
            if self._can_show_affordance(shift_held, affordance):
                yield affordance

        if self.sim_info.unlock_tracker is not None:
            for affordance in self.sim_info.unlock_tracker.get_cached_super_affordances_gen():
                if self._can_show_affordance(shift_held, affordance):
                    yield affordance

        if self.sim_info.career_tracker is not None:
            for affordance in self.sim_info.career_tracker.get_cached_super_affordances_gen():
                if self._can_show_affordance(shift_held, affordance):
                    yield affordance

        if self.sim_info.whim_tracker is not None:
            for affordance in self.sim_info.whim_tracker.get_cached_super_affordances_gen():
                if self._can_show_affordance(shift_held, affordance):
                    yield affordance

        if context is not None:
            if context.sim is not None:
                yield from _get_role_state_affordances_gen((context.sim.active_roles()), use_target=True)
        yield from (super()._potential_behavior_affordances_gen)(context, **kwargs)

    def _get_interactions_gen(self, context, get_interaction_parameters, affordance, **kwargs):
        if context.source == InteractionSource.AUTONOMY:
            if not affordance.allow_autonomous:
                return
        else:
            if context.sim is not None:
                if context.sim.is_running_interaction(affordance, self):
                    return
                if self.are_running_equivalent_interactions(context.sim, affordance):
                    return
            if get_interaction_parameters is not None:
                interaction_parameters = get_interaction_parameters(affordance, kwargs)
            else:
                interaction_parameters = kwargs
        yield from (affordance.potential_interactions)(self, context, **interaction_parameters)
        if False:
            yield None

    def potential_interactions(self, context, get_interaction_parameters=None, ignored_objects=None, **kwargs):
        return (self._potential_interactions_internal)(context, get_interaction_parameters=get_interaction_parameters, **kwargs)

    @caches.cached_generator
    def _potential_interactions_internal(self, context, get_interaction_parameters=None, **kwargs):
        for affordance in self.super_affordances(context):
            yield from (self._get_interactions_gen)(context, get_interaction_parameters, affordance, **kwargs)

        yield from (self._provided_interactions_gen)(context, **kwargs)
        if context.sim is not None:
            for relbit in context.sim.sim_info.relationship_tracker.get_all_bits(self.sim_id):
                for affordance in relbit.super_affordances:
                    yield from (self._get_interactions_gen)(context, get_interaction_parameters, affordance, **kwargs)

        if context.sim is not None:
            yield from (context.sim.get_object_provided_target_affordances_gen)(self, context, **kwargs)
        else:
            yield from (self.sim_info.template_affordance_tracker.get_template_interactions_gen)(context, **kwargs)
            if context.source == InteractionSource.AUTONOMY:
                if context.sim is self:
                    for ensemble in services.ensemble_service().get_all_ensembles_for_sim(self):
                        yield from (ensemble.get_ensemble_autonomous_interactions_gen)(context, **kwargs)

                if context.sim is not self:
                    yield from (self._potential_joinable_interactions_gen)(context, **kwargs)
            else:
                for si in self.si_state.sis_actor_gen():
                    for affordance in si.all_affordances_gen():
                        for aop in (affordance.potential_interactions)((si.target), (si.affordance), si, **kwargs):
                            if aop.affordance.is_allowed_to_forward(self):
                                yield aop

        if context.sim is self:
            yield from (self.get_component_potential_interactions_gen)(context, get_interaction_parameters, **kwargs)

    def potential_phone_interactions(self, context, **kwargs):
        for affordance in self._phone_affordances:
            for aop in (affordance.potential_interactions)(self, context, **kwargs):
                yield aop

        club_service = services.get_club_service()
        if club_service is not None:
            yield from club_service.provided_clubs_and_interactions_for_phone_gen(context)

    def potential_relation_panel_interactions(self, target, context, **kwargs):
        for affordance in self._relation_panel_affordances:
            for aop in (affordance.potential_interactions)(target, context, **kwargs):
                yield aop

    def locked_from_obj_by_privacy(self, obj):
        for privacy in services.privacy_service().privacy_instances:
            if not privacy.privacy_violators & PrivacyViolators.SIM:
                continue
            else:
                if self in privacy.allowed_sims:
                    continue
                if self not in privacy.disallowed_sims and privacy.evaluate_sim(self):
                    continue
            if privacy.intersects_with_object(obj):
                return True

        return False

    @flexmethod
    def super_affordances(cls, inst, context=None):
        inst_or_cls = inst if inst is not None else cls
        for affordance in super(GameObject, inst_or_cls).super_affordances(context):
            yield affordance

    @staticmethod
    def _get_mixer_key(target, affordance, sim_specific):
        mixer_lockout_key = affordance.get_mixer_key_override(target)
        if mixer_lockout_key is not None:
            return mixer_lockout_key
        if sim_specific:
            if target is not None:
                if target.is_sim:
                    return (
                     affordance, target.id)
        return affordance

    def set_sub_action_lockout(self, mixer_interaction, target=None, lock_other_affordance=False, initial_lockout=False):
        now = services.time_service().sim_now
        if initial_lockout:
            lockout_time = mixer_interaction.lock_out_time_initial.random_float()
            sim_specific = False
        else:
            lockout_time = mixer_interaction.lock_out_time.interval.random_float()
            sim_specific = mixer_interaction.lock_out_time.target_based_lock_out
        lockout_time_span = clock.interval_in_sim_minutes(lockout_time)
        lock_out_time = now + lockout_time_span
        mixer_lockout_key = self._get_mixer_key(mixer_interaction.target, mixer_interaction.affordance, sim_specific)
        self._mixers_locked_out[mixer_lockout_key] = lock_out_time
        if not initial_lockout:
            if lock_other_affordance:
                if mixer_interaction.lock_out_affordances is not None:
                    for affordance in mixer_interaction.lock_out_affordances:
                        sim_specific = affordance.lock_out_time.target_based_lock_out if affordance.lock_out_time is not None else False
                        mixer_lockout_key = self._get_mixer_key(mixer_interaction.target, affordance, sim_specific)
                        self._mixers_locked_out[mixer_lockout_key] = lock_out_time

    def update_last_used_interaction(self, interaction):
        if not interaction.is_super:
            if interaction.lock_out_time is not None:
                self.set_sub_action_lockout(interaction, lock_other_affordance=True)
        front_page_cooldown = interaction.content_score.front_page_cooldown if interaction.content_score is not None else None
        if front_page_cooldown is not None:
            cooldown_time = front_page_cooldown.interval.random_float()
            now = services.time_service().sim_now
            cooldown_time_span = clock.interval_in_sim_minutes(cooldown_time)
            cooldown_finish_time = now + cooldown_time_span
            affordance = interaction.affordance
            cur_penalty = self.get_front_page_penalty(affordance)
            penalty = front_page_cooldown.penalty + cur_penalty
            self._front_page_cooldown[affordance] = (
             cooldown_finish_time, penalty)

    def get_front_page_penalty(self, affordance):
        if affordance in self._front_page_cooldown:
            cooldown_finish_time, penalty = self._front_page_cooldown[affordance]
            now = services.time_service().sim_now
            if now >= cooldown_finish_time:
                del self._front_page_cooldown[affordance]
            else:
                return penalty
        return 0

    def is_sub_action_locked_out(self, affordance, target=None):
        if affordance is None:
            return False
            targeted_lockout_key = self._get_mixer_key(target, affordance, True)
            global_lockout_key = self._get_mixer_key(target, affordance, False)
            targeted_unlock_time = self._mixers_locked_out.get(targeted_lockout_key, None)
            global_unlock_time = self._mixers_locked_out.get(global_lockout_key, None)
            if targeted_unlock_time is None:
                if global_unlock_time is None:
                    return False
            now = services.time_service().sim_now
            locked_out = False
            if targeted_unlock_time is not None:
                if now >= targeted_unlock_time:
                    if targeted_lockout_key in self._mixers_locked_out:
                        del self._mixers_locked_out[targeted_lockout_key]
                else:
                    locked_out = True
            if global_unlock_time is not None:
                if now >= global_unlock_time:
                    if global_lockout_key in self._mixers_locked_out:
                        del self._mixers_locked_out[global_lockout_key]
        else:
            locked_out = True
        return locked_out

    def create_default_si(self, target_override=None):
        context = InteractionContext(self, InteractionContext.SOURCE_SCRIPT, priority.Priority.Low)
        if build_buy.is_location_pool(self.position, self.location.level) or self.routing_surface.type == SurfaceType.SURFACETYPE_POOL:
            aop = posture_graph.PostureGraphService.get_swim_aop(self.species)
        else:
            if self.posture.mobile:
                if self.posture.posture_type is not posture_graph.SIM_DEFAULT_POSTURE_TYPE:
                    posture_type = self.posture.posture_type
                    posture_graph_service = services.posture_graph_service()
                    for affordance in posture_graph_service.mobile_posture_providing_affordances:
                        if affordance.provided_posture_type is posture_type:
                            aop = AffordanceObjectPair(affordance, target_override, affordance, None, force_inertial=True)
                            break

                else:
                    aop = posture_graph.PostureGraphService.get_default_aop(self.species, self.sim_info)
            else:
                result = aop.interaction_factory(context)
                result or logger.error('Error creating default si: {}', result.reason)
            return result.interaction

    def pre_add(self, manager, *args, **kwargs):
        (super().pre_add)(manager, *args, **kwargs)
        self.queue = self._interaction_queue(self)
        self._obj_manager = manager
        self.hide(HiddenReasonFlag.NOT_INITIALIZED)

    @property
    def persistence_group(self):
        return self._persistence_group

    @persistence_group.setter
    def persistence_group(self, value):
        logger.callstack('Trying to override the persistence group of sim: {}.', self, owner='msantander')

    def on_add(self):
        super().on_add()
        zone_id = services.current_zone_id()
        _zone.add_sim(self.sim_id, zone_id)
        self.routing_component.on_sim_added()
        with consume_exceptions('SimInfo', 'Error during initial buff creation'):
            self._add_default_buff()
        with consume_exceptions('SimInfo', 'Error during buff addition'):
            if self.sim_info.should_add_foreign_zone_buff(zone_id):
                self.add_buff(self.FOREIGN_ZONE_BUFF)
            self.Buffs.add_venue_buffs()
        with consume_exceptions('SimInfo', 'Error during inventory load'):
            self.inventory_component.load_items(self.sim_info.inventory_data)
        with consume_exceptions('SimInfo', 'Error during template affordance tracker init'):
            self.sim_info.template_affordance_tracker.on_sim_added()
        with consume_exceptions('SimInfo', 'Error updating trait effects'):
            self.sim_info.trait_tracker.update_trait_effects()
        with consume_exceptions('SimInfo', 'Error during spawn condition trigger'):
            self.manager.trigger_sim_spawn_condition(self.sim_id)
        services.get_master_controller().add_sim(self)
        household = self.sim_info.household
        if household is not None:
            if household.scenario_tracker is not None:
                household.scenario_tracker.on_household_member_instanced(self)

    def _should_be_swimming(self):
        return self.should_be_swimming_at_position(self.position, self.location.level)

    def should_be_swimming_at_position(self, position, level=0, check_can_swim=True):
        if build_buy.is_location_pool(position, level):
            return True
        else:
            ocean_data = OceanTuning.get_actor_ocean_data(self)
            if check_can_swim:
                if not self.can_swim():
                    return False
            depth = get_water_depth(position.x, position.z, level)
            if ocean_data is None or ocean_data.wading_interval is None:
                return 0 < depth
            if ocean_data.wading_interval.upper_bound <= depth:
                surface_identifier = SurfaceIdentifier(self.routing_surface.primary_id, self.routing_surface.secondary_id, SurfaceType.SURFACETYPE_POOL)
                location = routing.Location(position, sims4.math.Quaternion.IDENTITY(), surface_identifier)
                routable = routing.test_connectivity_permissions_for_handle(routing.connectivity.Handle(location), self.routing_context)
                if routable:
                    return True
        return False

    def update_face_and_posture_for_aging_gen(self, timeline):
        yield from self._update_face_and_posture_gen(timeline, can_be_carried=(self.age == Age.TODDLER))
        if False:
            yield None

    def _update_face_and_posture_gen(self, timeline, can_be_carried=False):
        target_override = None
        posture_type = None
        previous_posture_type = None
        previous_posture_target = None
        skip_posture_kickstart = False
        if self.posture_state is not None:
            previous_posture_type = self.posture_state.body.posture_type
            previous_posture_target = self.posture_state.body.target
        try:
            posture_graph_service = services.current_zone().posture_graph_service
            if self._should_be_swimming():
                posture_type = posture_graph.SIM_SWIM_POSTURE_TYPE
                location = self.location
                routing_surface = self.routing_surface
                routing_surface = SurfaceIdentifier(routing_surface.primary_id, routing_surface.secondary_id, SurfaceType.SURFACETYPE_POOL)
                snapped_y = services.terrain_service.terrain_object().get_routing_surface_height_at(location.transform.translation.x, location.transform.translation.z, routing_surface)
                if not (routing_surface.type != location.routing_surface.type or sims4.math.almost_equal(location.transform.translation.y, snapped_y)):
                    translation = sims4.math.Vector3(location.transform.translation.x, snapped_y, location.transform.translation.z)
                    self.location = self.location.clone(translation=translation, routing_surface=routing_surface)
            else:
                compatible_postures_and_targets = posture_graph_service.get_compatible_mobile_postures_and_targets(self)
                if compatible_postures_and_targets:
                    for target, compatible_postures in compatible_postures_and_targets.items():
                        if self.posture_state is None or self.posture_state.body.posture_type in compatible_postures:
                            posture_type = self.posture_state.body.posture_type if self.posture_state is not None else compatible_postures[0]
                            target_override = target
                            break
                    else:
                        target_override, posture_types = next(iter(compatible_postures_and_targets.items()))
                        posture_type = next(iter(posture_types), None)

                else:
                    if can_be_carried:
                        if self.posture_state is not None:
                            if self.posture_state.body_target.is_sim:
                                skip_posture_kickstart = True
            if posture_type is None:
                posture_type = posture_graph_service.get_default_posture(self.species, self.sim_info)
            if not skip_posture_kickstart:
                origin_posture_spec = get_origin_spec(posture_type)
                self.posture_state = PostureState(self, None, origin_posture_spec, {PostureSpecVariable.HAND: (Hand.LEFT,)})
                yield from self.posture_state.kickstart_gen(timeline, (self.routing_surface), target_override=target_override)
        except Exception:
            posture_type = posture_graph_service.get_default_posture(self.species, self.sim_info)
            origin_posture_spec = get_origin_spec(posture_type)
            self.posture_state = PostureState(self, None, origin_posture_spec, {PostureSpecVariable.HAND: (Hand.LEFT,)})
            yield from self.posture_state.kickstart_gen(timeline, self.routing_surface)

        self._start_animation_interaction()
        self.start_animation_overlays()
        self.update_animation_overlays()
        if previous_posture_type is not None:
            if previous_posture_type.is_vehicle:
                if previous_posture_target is not None:
                    if previous_posture_target.vehicle_component is not None:
                        if previous_posture_target.inventoryitem_component is not None:
                            if previous_posture_target.vehicle_component.retrieve_tuning is not None:
                                household_owner_id = previous_posture_target.household_owner_id
                                if household_owner_id == self.household_id:
                                    previous_posture_target = previous_posture_target.part_owner if previous_posture_target.is_part else previous_posture_target
                                    self.inventory_component.player_try_add_object(previous_posture_target)
        if False:
            yield None

    def _update_multi_motive_buff_trackers(self):
        for multi_motive_buff_tracker in self._multi_motive_buff_trackers:
            multi_motive_buff_tracker.setup_callbacks()

    def _remove_multi_motive_buff_trackers(self):
        for multi_motive_buff_tracker in self._multi_motive_buff_trackers:
            multi_motive_buff_tracker.cleanup_callbacks()

        self._multi_motive_buff_trackers.clear()

    def add_callbacks(self):
        with consume_exceptions('SimInfo', 'Error during routing initialization'):
            self.routing_component.add_callbacks()
            self.routing_component.on_intended_location_changed.append(self.refresh_los_constraint)
            self.routing_component.on_intended_location_changed.append(self._update_social_geometry_on_location_changed)
            self.routing_component.on_intended_location_changed.append(lambda *_, **__: self.two_person_social_transforms.clear())
            self.routing_component.on_intended_location_changed.append(self.update_intended_position_on_active_lot)
        with consume_exceptions('SimInfo', 'Error during navmesh initialization'):
            zone = services.get_zone(self.zone_id)
            if zone is not None:
                zone.navmesh_change_callbacks.append(self._on_navmesh_updated)
                zone.wall_contour_update_callbacks.append(self._on_navmesh_updated)
                zone.foundation_and_level_height_update_callbacks.append(self.validate_current_location_or_fgl)
        with consume_exceptions('SimInfo', 'Error during outfit initialization'):
            self.sim_info.on_outfit_changed.append(self.on_outfit_changed)

    def remove_callbacks(self):
        zone = services.current_zone()
        if self._on_navmesh_updated in zone.navmesh_change_callbacks:
            zone.navmesh_change_callbacks.remove(self._on_navmesh_updated)
        if self._on_navmesh_updated in zone.wall_contour_update_callbacks:
            zone.wall_contour_update_callbacks.remove(self._on_navmesh_updated)
        if self.validate_current_location_or_fgl in zone.foundation_and_level_height_update_callbacks:
            zone.foundation_and_level_height_update_callbacks.remove(self.validate_current_location_or_fgl)
        if self.on_outfit_changed in self.sim_info.on_outfit_changed:
            self.sim_info.on_outfit_changed.remove(self.on_outfit_changed)
        self.manager.unregister_portal_added_callback(self.portal_added_callback)
        self.routing_component.remove_callbacks()

    def _startup_sim_gen(self, timeline):
        if self._starting_up:
            logger.info('Attempting to run _startup_sim while it is already running on another thread. Request ignored.')
            return
        previous_simulation_state = self._simulation_state
        self._starting_up = True
        try:
            yield from self._update_face_and_posture_gen(timeline)
            self.queue.unlock()
            self.show(HiddenReasonFlag.NOT_INITIALIZED)
            if self._simulation_state == SimulationState.INITIALIZING:
                school_data = self.sim_info.get_school_data()
                if school_data is not None:
                    create_homework = self.sim_info.time_sim_was_saved is None
                    school_data.update_school_data((self.sim_info), create_homework=create_homework)
                self.trait_tracker.on_sim_startup()
                for commodity in tuple(self.commodity_tracker):
                    if commodity.needs_fixup_on_load():
                        commodity.fixup_on_sim_instantiated()

                owning_household_of_active_lot = services.owning_household_of_active_lot()
                if owning_household_of_active_lot is not None:
                    for target_sim_info in owning_household_of_active_lot:
                        self.relationship_tracker.add_relationship_appropriateness_buffs(target_sim_info.id)

                services.relationship_service().on_sim_creation(self)
                self.autonomy_component.start_autonomy_alarm()
                situation_manager = services.get_zone_situation_manager()
                situation_manager.on_begin_sim_creation_notification(self)
                services.sim_spawner_service().on_sim_creation(self)
                situation_manager.on_end_sim_creation_notification(self)
                self.commodity_tracker.start_regular_simulation()
                services.lunar_cycle_service().apply_active_lunar_effects_to_sim(self.sim_info)
                for buff, multi_motive_buff_motives in self.MULTI_MOTIVE_BUFF_MOTIVES.items():
                    self._multi_motive_buff_trackers.append(sims.multi_motive_buff_tracker.MultiMotiveBuffTracker(self, multi_motive_buff_motives, buff))

                self.sim_info.Buffs.on_sim_ready_to_simulate()
                self.sim_info.career_tracker.on_sim_startup()
                self.sim_info.occult_tracker.on_sim_ready_to_simulate(self)
                self.sim_info.trait_tracker.on_sim_ready_to_simulate()
                for static_commodity_type in self.sim_info.STATIC_COMMODITIES_WHILE_INSTANCED:
                    self.sim_info.static_commodity_tracker.add_statistic(static_commodity_type)

                if self.sim_info.whim_tracker is not None:
                    self.sim_info.whim_tracker.load_whims_info_from_proto()
                    self.sim_info.whim_tracker.start_whims_tracker()
                if self.sim_info.developmental_milestone_tracker is not None:
                    if services.current_zone().is_zone_running:
                        self.sim_info.developmental_milestone_tracker.start_milestone_tracker()
                self.update_sleep_schedule()
                if self.sim_info.time_sim_was_saved is None:
                    if self.sim_info.degree_tracker is not None:
                        if self.sim_info.degree_tracker.get_enrolled_major() is not None:
                            self.sim_info.degree_tracker.create_university_objects()
                sims.ghost.Ghost.make_ghost_if_needed(self.sim_info)
                if self.sim_info.is_in_travel_group():
                    travel_group = self.travel_group
                    current_region = services.current_region()
                    travel_group_region = region.get_region_instance_from_zone_id(travel_group.zone_id)
                    if not current_region.is_region_compatible(travel_group_region):
                        if any((sim_info.can_live_alone for sim_info in travel_group if sim_info is not self.sim_info)):
                            travel_group.remove_sim_info(self.sim_info)
            else:
                travel_group.end_vacation()
            if services.current_zone().is_zone_running:
                if self.sim_info.away_action_tracker is not None:
                    self.sim_info.away_action_tracker.refresh()
                services.sim_info_manager().update_greeted_relationships_on_spawn(self.sim_info)
                if self.is_selectable:
                    self.sim_info.start_aspiration_tracker_on_instantiation(force_ui_update=True)
                if self.is_selected:
                    self.client.notify_active_sim_changed(None, new_sim_info=(self.sim_info))
                self.update_portal_locks()
            else:
                if self._simulation_state == SimulationState.RESETTING:
                    self.remove_callbacks()
                    self.Buffs.on_sim_reset()
                self.on_outfit_changed(self.sim_info, self._sim_info.get_current_outfit())
                self.refresh_los_constraint()
                self._simulation_state = SimulationState.SIMULATING
                self.add_callbacks()
                self.on_start_up(self)
                self.on_start_up.clear()
                self._start_environment_score()
                self.update_intended_position_on_active_lot(update_ui=True)
                suntan_tracker = self.sim_info.suntan_tracker
                if suntan_tracker is not None:
                    suntan_tracker.on_start_up(self)
                familiar_tracker = self.sim_info.familiar_tracker
                if familiar_tracker is not None:
                    familiar_tracker.on_sim_startup()
                street_service = services.street_service()
                if street_service is not None:
                    street_service.on_sim_added(self.sim_info)
                if gsi_handlers.sim_info_lifetime_handlers.archiver.enabled:
                    gsi_handlers.sim_info_lifetime_handlers.archive_sim_info_event(self.sim_info, 'instantiated')
        finally:
            self._starting_up = False
            if previous_simulation_state == SimulationState.RESETTING:
                services.current_zone().service_manager.on_sim_reset(self)

        if False:
            yield None

    def on_remove(self):
        household = self.sim_info.household
        if household is not None:
            if household.scenario_tracker is not None:
                household.scenario_tracker.on_household_member_deinstanced(self)
        self.sim_info.Buffs.on_sim_removed()
        self.routing_component.on_sim_removed()
        self._stop_environment_score()
        self.trait_tracker.on_sim_removed()
        familiar_tracker = self.sim_info.familiar_tracker
        if familiar_tracker is not None:
            familiar_tracker.on_sim_removed()
        street_service = services.street_service()
        if street_service is not None:
            street_service.on_sim_removed(self.sim_info)
        self.commodity_tracker.stop_regular_simulation()
        self.commodity_tracker.start_low_level_simulation()
        self.sim_info.template_affordance_tracker.on_sim_removed()
        self.sim_info.time_sim_was_saved = services.time_service().sim_now
        for static_commodity_type in self.sim_info.STATIC_COMMODITIES_WHILE_INSTANCED:
            self.sim_info.static_commodity_tracker.remove_statistic(static_commodity_type)

        self.asm_auto_exit.clear()
        zone = services.current_zone()
        zone.posture_graph_service.update_sim_node_caches(self)
        if zone.master_controller is not None:
            zone.master_controller.remove_sim(self)
        self.on_posture_event.clear()
        _zone.remove_sim(self.sim_id, zone.id)
        self._is_removed = True
        super().on_remove()
        self._posture_state = None
        self.on_start_up.clear()
        self.remove_callbacks()
        zone.sim_quadtree.remove(self.sim_id, placement.ItemType.SIM_POSITION, 0)
        zone.sim_quadtree.remove(self.sim_id, placement.ItemType.SIM_INTENDED_POSITION, 0)
        if self.refresh_los_constraint in zone.wall_contour_update_callbacks:
            zone.wall_contour_update_callbacks.remove(self.refresh_los_constraint)
        self._remove_multi_motive_buff_trackers()
        self.object_ids_to_ignore.clear()
        self._si_state = None
        self._mixers_locked_out.clear()
        self._front_page_cooldown.clear()
        if gsi_handlers.sim_info_lifetime_handlers.archiver.enabled:
            gsi_handlers.sim_info_lifetime_handlers.archive_sim_info_event(self.sim_info, 'deinstantiated')

    def post_remove(self):
        super().post_remove()
        self._clear_clothing_buffs()
        self.queue = None
        if self.ready_to_be_culled:
            zone = services.current_zone()
            if zone is not None:
                if not zone.is_zone_shutting_down:
                    culling_service = services.get_culling_service()
                    culling_service.cull_household((self.sim_info.household), is_important_fn=(lambda _: False))

    @property
    def is_outside(self):
        if self._is_running_interaction_counts_as_inside():
            return False
        return super().is_outside

    @property
    def is_inside_building(self):
        if self._is_running_interaction_counts_as_inside():
            return True
        return super().is_inside_building

    @property
    def is_in_shade(self):
        if self._is_running_interaction_counts_as_in_shade():
            return True
        return False

    def _is_running_interaction_counts_as_inside(self):
        return any((affordance.counts_as_inside for affordance, _ in self._all_affordance_targets()))

    def _is_running_interaction_counts_as_in_shade(self):
        return any((affordance.counts_as_in_shade for affordance, _ in self._all_affordance_targets()))

    @property
    def intended_location(self):
        sim_parent = self.parent
        if sim_parent is not None:
            if sim_parent.is_sim:
                return sim_parent.intended_location
        if self.transition_controller is not None:
            return self.transition_controller.intended_location(self)
        return self.location

    @property
    def intended_transform(self):
        return self.intended_location.world_transform

    @property
    def intended_routing_surface(self):
        return self.intended_location.routing_surface or self.parent.intended_routing_surface

    @property
    def intended_position_on_active_lot(self):
        return self._intended_position_on_active_lot

    def get_intended_location_excluding_transition(self, exclude_transition):
        if self.transition_controller is None or self.transition_controller is exclude_transition:
            return self.location
        return self.intended_location

    def _should_invalidate_location(self):
        return False

    @property
    def preroll_commodity_flags(self):
        if self._dynamic_preroll_commodity_flags_map is None:
            dynamic_preroll_commodity_flags = frozenset()
        else:
            dynamic_preroll_commodity_flags = frozenset((flag for commodity_set in self._dynamic_preroll_commodity_flags_map.values() for flag in commodity_set))
        return super().preroll_commodity_flags | dynamic_preroll_commodity_flags

    def add_dynamic_preroll_commodity_flags(self, key, commodity_flags):
        if self._dynamic_preroll_commodity_flags_map is None:
            self._dynamic_preroll_commodity_flags_map = {}
        self._dynamic_preroll_commodity_flags_map[key] = commodity_flags

    def remove_dynamic_preroll_commodity_flags(self, key):
        if self._dynamic_preroll_commodity_flags_map is not None:
            if key in self._dynamic_preroll_commodity_flags_map:
                del self._dynamic_preroll_commodity_flags_map[key]
            if not self._dynamic_preroll_commodity_flags_map:
                self._dynamic_preroll_commodity_flags_map = None

    def commodities_gen(self):
        for stat in self.commodity_tracker:
            yield stat

    def static_commodities_gen(self):
        for stat in self.static_commodity_tracker:
            yield stat

    def statistics_gen(self):
        for stat in self.statistic_tracker:
            yield stat

    def object_tags_override_off_lot_autonomy_ref_count(self, object_tag_list):
        return self.sim_info.object_tags_override_off_lot_autonomy_ref_count(object_tag_list)

    def all_skills(self):
        return self.sim_info.all_skills()

    def scored_stats_gen(self):
        for stat in self.statistic_tracker.all_statistics():
            if stat.is_scored and self.is_scorable(stat.stat_type):
                yield stat

        for commodity in self.commodity_tracker.all_statistics():
            if commodity.is_scored and self.is_scorable(commodity.stat_type):
                yield commodity

        for static_commodity in self.static_commodity_tracker.all_statistics():
            if static_commodity.is_scored and self.is_scorable(static_commodity.stat_type):
                yield static_commodity

    def force_update_routing_location(self):
        for primitive in self.primitives:
            if hasattr(primitive, 'update_routing_location'):
                primitive.update_routing_location()

    def populate_localization_token(self, *args, **kwargs):
        (self.sim_info.populate_localization_token)(*args, **kwargs)

    def create_posture_interaction_context(self, hand=None):
        return InteractionContext(self, (InteractionContext.SOURCE_POSTURE_GRAPH),
          (Priority.High),
          carry_hand=hand)

    @property
    def posture(self):
        if self.posture_state is not None:
            return self.posture_state.body

    @property
    def posture_target(self):
        if self.posture is not None:
            return self.posture.target

    @distributor.fields.Field(op=(distributor.ops.SetActorPosture), default=None)
    def posture_state(self):
        return self._posture_state

    @posture_state.setter
    def posture_state(self, value):
        if self._posture_state is not None:
            if value is not None:
                if self._posture_state.carry_targets != value.carry_targets:
                    for interaction in self.queue:
                        if interaction.transition is not None and not interaction.transition.running:
                            if interaction.carry_track is not None or interaction.should_carry_create_target():
                                interaction.transition.reset_sim_progress(self)

                if self._posture_state.body != value.body:
                    if self.animation_interaction is not None:
                        self.animation_interaction.clear_animation_liability_cache()
                value.body.fallback_occult_on_posture_reset = self._posture_state.body.get_occult_for_posture_reset()
        else:
            self._posture_state = value
            front_key_mask = PortalFlags.REQUIRE_NO_CARRY
            front_carry_target_found = False
            back_key_mask = PortalFlags.REQUIRE_NO_CARRY_BACK
            back_carry_target_found = False
            for carry_target in value.carry_targets:
                if carry_target is not None:
                    if value.get_carry_track(carry_target) != PostureTrack.BACK:
                        front_carry_target_found = True
                        front_key_mask = front_key_mask & ~carry_target.get_portal_key_make_for_carry()
                    else:
                        back_carry_target_found = True
                        back_key_mask = back_key_mask & ~carry_target.get_portal_key_make_for_carry()

            if front_carry_target_found:
                self.routing_component.clear_portal_mask_flag(front_key_mask)
            else:
                self.routing_component.set_portal_mask_flag(front_key_mask)
            if back_carry_target_found:
                self.routing_component.clear_portal_mask_flag(back_key_mask)
            else:
                self.routing_component.set_portal_mask_flag(back_key_mask)
        self._posture_target_refs.clear()
        for aspect in self._posture_state.aspects:
            if aspect.target is not None:
                self._posture_target_refs.append(aspect.target.ref(lambda _: self.reset(ResetReason.RESET_EXPECTED, self, 'Posture target went away.')))

        if self.posture_state is not None:
            connectivity_handles = self.posture_state.connectivity_handles
            if connectivity_handles is not None:
                self.pathplan_context.connectivity_handles = connectivity_handles

    def is_surface(self, *args, **kwargs):
        return False

    @caches.cached
    def ignore_group_socials(self, excluded_group=None):
        if self.si_state is not None:
            for si in self.si_state:
                if excluded_group is not None:
                    if si.social_group is excluded_group:
                        continue
                if si.ignore_group_socials:
                    return True

        else:
            if self.queue is None:
                return True
            next_interaction = self.queue.peek_head()
            if next_interaction is not None:
                if next_interaction.is_super and next_interaction.ignore_group_socials:
                    if excluded_group is None or next_interaction.social_group is not excluded_group:
                        return True
        return False

    @property
    def disallow_as_mixer_target(self):
        return any((si.disallow_as_mixer_target for si in self.si_state))

    def get_groups_for_sim_gen(self):
        for group in self._social_groups:
            if self in group:
                yield group

    def get_main_group(self):
        for group in self.get_groups_for_sim_gen():
            if not group.is_side_group:
                return group

    def get_visible_group(self):
        visible_group = None
        for group in self.get_groups_for_sim_gen():
            if group.is_visible:
                if not group.is_side_group:
                    return group
                visible_group = group

        return visible_group

    def get_ensemble_sims(self):
        ensemble_sims = set()
        for ensemble in services.ensemble_service().get_all_ensembles_for_sim(self):
            ensemble_sims.update(ensemble)

        return ensemble_sims

    def get_sims_for_rally(self, rally_sources):
        rally_sims = set()
        if RallySource.SOCIAL_GROUP in rally_sources:
            main_group = self.get_visible_group()
            if main_group:
                rally_sims.update(main_group)
        if RallySource.ENSEMBLE in rally_sources:
            ensemble_sims = services.ensemble_service().get_ensemble_sims_for_rally(self)
            if ensemble_sims:
                rally_sims.update(ensemble_sims)
        return rally_sims

    def is_in_side_group(self):
        return any((self in g and g.is_side_group for g in self.get_groups_for_sim_gen()))

    def is_in_group_with(self, target_sim):
        return any((target_sim in group for group in self.get_groups_for_sim_gen()))

    @caches.cached
    def get_social_context(self):
        sims = set((itertools.chain)(*self.get_groups_for_sim_gen()))
        social_context_bit = (SocialContextTest.get_overall_short_term_context_bit)(*sims)
        if social_context_bit is not None:
            size_limit = social_context_bit.size_limit
            if size_limit is not None:
                if len(sims) > size_limit.size:
                    social_context_bit = size_limit.transformation
        return social_context_bit

    def on_social_context_changed(self):
        SocialContextTest.get_overall_short_term_context_bit.cache.clear()
        self.get_social_context.cache.clear()
        for group in self.get_groups_for_sim_gen():
            group.on_social_context_changed()

    def without_social_focus(self, sequence):
        new_sequence = sequence
        for group in self.get_groups_for_sim_gen():
            new_sequence = group.without_social_focus(self, self, new_sequence)

        return new_sequence

    def set_mood_asm_parameter(self, asm, actor_name):
        mood_asm_name = self.get_mood_animation_param_name()
        if mood_asm_name is not None:
            asm.set_actor_parameter(actor_name, self, 'mood', mood_asm_name.lower())

    def set_trait_asm_parameters(self, asm, actor_name):
        asm_param_dict = self.sim_info.trait_tracker.get_default_trait_asm_params(actor_name)
        for param_name, param_value in self._default_anim_params.items():
            asm_param_dict[(param_name, actor_name)] = param_value

        for trait in self.sim_info.get_traits():
            if trait.trait_asm_overrides.trait_asm_param is None:
                continue
            if trait.trait_asm_overrides.param_type is None:
                asm_param_dict[(trait.trait_asm_overrides.trait_asm_param, actor_name)] = True
            else:
                asm_param_dict[(trait.trait_asm_overrides.param_type, actor_name)] = trait.trait_asm_overrides.trait_asm_param

        asm.update_locked_params(asm_param_dict, ignore_virtual_suffix=True)
        self._locked_param_cache.update(asm_param_dict)

    def _get_animation_skill_param(self):
        param_dict = {}
        for skill in self.all_skills():
            if not skill.stat_asm_param.always_apply:
                continue
            asm_param_name, asm_param_value = skill.get_asm_param()
            if asm_param_name is not None and asm_param_value is not None:
                param_dict[asm_param_name] = asm_param_value

        return param_dict

    def get_sim_locked_params(self):
        return self._locked_param_cache

    def evaluate_si_state_and_cancel_incompatible(self, finishing_type, cancel_reason_msg):
        sim_posture_constraint = self.posture_state.posture_constraint_strict
        parent = self.parent
        slave_routing = self.routing_master and self.routing_master.routing_component.is_moving
        if not slave_routing:
            if parent is None or parent.routing_component is None:
                sim_transform_constraint = interactions.constraints.Transform((self.transform), routing_surface=(self.routing_surface))
                sim_constraint = sim_transform_constraint.intersect(sim_posture_constraint)
        else:
            sim_constraint = sim_posture_constraint
        _, included_sis = self.si_state.get_combined_constraint(sim_constraint, None, None, None, True, True)
        for si in self.si_state:
            if si not in included_sis and si.basic_content is not None and si.basic_content.staging:
                si.cancel(finishing_type, cancel_reason_msg)

    def refresh_los_constraint(self, *args, target_position=DEFAULT, **kwargs):
        if target_position is DEFAULT:
            target_position = self.intended_position
            target_forward = self.intended_forward
            target_routing_surface = self.intended_routing_surface
        else:
            target_forward = self.forward
            target_routing_surface = self.routing_surface
        if target_routing_surface == self.lineofsight_component.routing_surface:
            if sims4.math.vector3_almost_equal_2d(target_position, self.lineofsight_component.position):
                return
        target_position = target_position + target_forward * self.lineofsight_component.facing_offset
        self.lineofsight_component.generate(position=target_position, routing_surface=target_routing_surface, lock=True, build_convex=True)
        self._los_constraint = self.lineofsight_component.constraint
        zone = services.current_zone()
        if self.refresh_los_constraint not in zone.wall_contour_update_callbacks:
            zone.wall_contour_update_callbacks.append(self.refresh_los_constraint)
        self._social_group_constraint = None
        master_transform = sims4.math.Transform(target_position, sims4.math.angle_to_yaw_quaternion(sims4.math.vector3_angle(target_forward)))
        for slave_data in self.get_all_routing_slave_data_gen():
            if not slave_data.slave.is_sim:
                continue
            offset = sims4.math.Vector3.ZERO()
            for attachment_info in slave_data.attachment_info_gen():
                offset.x = offset.x + attachment_info.parent_offset.x - attachment_info.offset.x
                offset.z = offset.z + attachment_info.parent_offset.y - attachment_info.offset.y

            transformed_point = master_transform.transform_point(offset)
            slave_data.slave.refresh_los_constraint(target_position=transformed_point)

    @property
    def los_constraint(self):
        return self._los_constraint

    def can_see(self, obj):
        if obj.intended_position is not None:
            obj_position = obj.intended_position
        else:
            obj_position = obj.position
        return self.los_constraint.geometry.contains_point(obj_position)

    def get_social_group_constraint--- This code section failed: ---

 L.3704         0  LOAD_FAST                'self'
                2  LOAD_ATTR                _social_group_constraint
                4  LOAD_CONST               None
                6  COMPARE_OP               is
             8_10  POP_JUMP_IF_FALSE   350  'to 350'

 L.3705        12  LOAD_FAST                'self'
               14  LOAD_ATTR                si_state
               16  LOAD_ATTR                get_total_constraint
               18  LOAD_FAST                'si'
               20  LOAD_CONST               None
               22  COMPARE_OP               is-not
               24  POP_JUMP_IF_FALSE    32  'to 32'
               26  LOAD_FAST                'si'
               28  LOAD_ATTR                priority
               30  JUMP_FORWARD         34  'to 34'
             32_0  COME_FROM            24  '24'
               32  LOAD_CONST               None
             34_0  COME_FROM            30  '30'

 L.3706        34  LOAD_CONST               True

 L.3707        36  LOAD_FAST                'si'
               38  LOAD_CONST               ('priority', 'include_inertial_sis', 'to_exclude')
               40  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               42  STORE_FAST               'si_constraint'

 L.3709        44  SETUP_LOOP          112  'to 112'
               46  LOAD_FAST                'si_constraint'
               48  GET_ITER         
             50_0  COME_FROM            62  '62'
               50  FOR_ITER             68  'to 68'
               52  STORE_FAST               'base_constraint'

 L.3710        54  LOAD_FAST                'base_constraint'
               56  LOAD_ATTR                geometry
               58  LOAD_CONST               None
               60  COMPARE_OP               is-not
               62  POP_JUMP_IF_FALSE    50  'to 50'

 L.3711        64  BREAK_LOOP       
               66  JUMP_BACK            50  'to 50'
               68  POP_BLOCK        

 L.3715        70  LOAD_FAST                'self'
               72  LOAD_ATTR                queue
               74  LOAD_ATTR                running
               76  LOAD_CONST               None
               78  COMPARE_OP               is-not
               80  POP_JUMP_IF_FALSE   112  'to 112'
               82  LOAD_FAST                'self'
               84  LOAD_ATTR                queue
               86  LOAD_ATTR                running
               88  LOAD_ATTR                is_super
               90  POP_JUMP_IF_FALSE   112  'to 112'

 L.3716        92  LOAD_GLOBAL              interactions
               94  LOAD_ATTR                constraints
               96  LOAD_ATTR                Transform
               98  LOAD_FAST                'self'
              100  LOAD_ATTR                transform
              102  LOAD_FAST                'self'
              104  LOAD_ATTR                routing_surface
              106  LOAD_CONST               ('routing_surface',)
              108  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              110  STORE_FAST               'base_constraint'
            112_0  COME_FROM            90  '90'
            112_1  COME_FROM            80  '80'
            112_2  COME_FROM_LOOP       44  '44'

 L.3717       112  LOAD_FAST                'base_constraint'
              114  LOAD_ATTR                geometry
              116  LOAD_CONST               None
              118  COMPARE_OP               is-not
          120_122  POP_JUMP_IF_FALSE   338  'to 338'
              124  LOAD_FAST                'base_constraint'
              126  LOAD_ATTR                geometry
              128  LOAD_ATTR                polygon
          130_132  POP_JUMP_IF_FALSE   338  'to 338'

 L.3718       134  LOAD_FAST                'self'
              136  LOAD_ATTR                los_constraint
              138  STORE_FAST               'los_constraint'

 L.3719       140  LOAD_FAST                'base_constraint'
              142  LOAD_ATTR                geometry
              144  STORE_FAST               'base_geometry'

 L.3720       146  BUILD_LIST_0          0 
              148  STORE_FAST               'expanded_polygons'

 L.3721       150  SETUP_LOOP          276  'to 276'
              152  LOAD_FAST                'base_geometry'
              154  LOAD_ATTR                polygon
              156  GET_ITER         
            158_0  COME_FROM           210  '210'
              158  FOR_ITER            274  'to 274'
              160  STORE_FAST               'sub_polygon'

 L.3722       162  LOAD_GLOBAL              len
              164  LOAD_FAST                'sub_polygon'
              166  CALL_FUNCTION_1       1  '1 positional argument'
              168  LOAD_CONST               1
              170  COMPARE_OP               ==
              172  POP_JUMP_IF_FALSE   200  'to 200'

 L.3724       174  LOAD_GLOBAL              sims4
              176  LOAD_ATTR                geometry
              178  LOAD_METHOD              generate_circle_constraint
              180  LOAD_GLOBAL              LOSAndSocialConstraintTuning
              182  LOAD_ATTR                num_sides_for_circle_expansion_of_point_constraint

 L.3725       184  LOAD_FAST                'sub_polygon'
              186  LOAD_CONST               0
              188  BINARY_SUBSCR    

 L.3726       190  LOAD_GLOBAL              LOSAndSocialConstraintTuning
              192  LOAD_ATTR                constraint_expansion_amount
              194  CALL_METHOD_3         3  '3 positional arguments'
              196  STORE_FAST               'new_polygon'
              198  JUMP_FORWARD        262  'to 262'
            200_0  COME_FROM           172  '172'

 L.3727       200  LOAD_GLOBAL              len
              202  LOAD_FAST                'sub_polygon'
              204  CALL_FUNCTION_1       1  '1 positional argument'
              206  LOAD_CONST               1
              208  COMPARE_OP               >
              210  POP_JUMP_IF_FALSE   158  'to 158'

 L.3728       212  LOAD_GLOBAL              sum
              214  LOAD_FAST                'sub_polygon'
              216  LOAD_GLOBAL              sims4
              218  LOAD_ATTR                math
              220  LOAD_ATTR                Vector3
              222  LOAD_METHOD              ZERO
              224  CALL_METHOD_0         0  '0 positional arguments'
              226  CALL_FUNCTION_2       2  '2 positional arguments'
              228  LOAD_GLOBAL              len
              230  LOAD_FAST                'sub_polygon'
              232  CALL_FUNCTION_1       1  '1 positional argument'
              234  BINARY_TRUE_DIVIDE
              236  STORE_FAST               'center'

 L.3729       238  LOAD_GLOBAL              sims4
              240  LOAD_ATTR                geometry
              242  LOAD_ATTR                inflate_polygon
              244  LOAD_FAST                'sub_polygon'
              246  LOAD_GLOBAL              LOSAndSocialConstraintTuning
              248  LOAD_ATTR                constraint_expansion_amount

 L.3730       250  LOAD_FAST                'center'
              252  LOAD_CONST               ('centroid',)
              254  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              256  STORE_FAST               'new_polygon'
              258  JUMP_FORWARD        262  'to 262'

 L.3732       260  CONTINUE            158  'to 158'
            262_0  COME_FROM           258  '258'
            262_1  COME_FROM           198  '198'

 L.3733       262  LOAD_FAST                'expanded_polygons'
              264  LOAD_METHOD              append
              266  LOAD_FAST                'new_polygon'
              268  CALL_METHOD_1         1  '1 positional argument'
              270  POP_TOP          
              272  JUMP_BACK           158  'to 158'
              274  POP_BLOCK        
            276_0  COME_FROM_LOOP      150  '150'

 L.3735       276  LOAD_GLOBAL              sims4
              278  LOAD_ATTR                geometry
              280  LOAD_METHOD              CompoundPolygon
              282  LOAD_FAST                'expanded_polygons'
              284  CALL_METHOD_1         1  '1 positional argument'
              286  STORE_FAST               'new_compound_polygon'

 L.3736       288  LOAD_GLOBAL              sims4
              290  LOAD_ATTR                geometry
              292  LOAD_METHOD              RestrictedPolygon
              294  LOAD_FAST                'new_compound_polygon'
              296  BUILD_LIST_0          0 
              298  CALL_METHOD_2         2  '2 positional arguments'
              300  STORE_FAST               'new_restricted_polygon'

 L.3737       302  LOAD_GLOBAL              interactions
              304  LOAD_ATTR                constraints
              306  LOAD_ATTR                Constraint
              308  LOAD_FAST                'new_restricted_polygon'

 L.3738       310  LOAD_FAST                'los_constraint'
              312  LOAD_ATTR                routing_surface
              314  LOAD_CONST               ('geometry', 'routing_surface')
              316  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              318  STORE_FAST               'base_constraint'

 L.3739       320  LOAD_FAST                'base_constraint'
              322  LOAD_METHOD              intersect
              324  LOAD_FAST                'los_constraint'
              326  CALL_METHOD_1         1  '1 positional argument'
              328  STORE_FAST               'intersection'

 L.3740       330  LOAD_FAST                'intersection'
              332  LOAD_FAST                'self'
              334  STORE_ATTR               _social_group_constraint
              336  JUMP_FORWARD        350  'to 350'
            338_0  COME_FROM           130  '130'
            338_1  COME_FROM           120  '120'

 L.3742       338  LOAD_GLOBAL              interactions
              340  LOAD_ATTR                constraints
              342  LOAD_METHOD              Anywhere
              344  CALL_METHOD_0         0  '0 positional arguments'
              346  LOAD_FAST                'self'
              348  STORE_ATTR               _social_group_constraint
            350_0  COME_FROM           336  '336'
            350_1  COME_FROM             8  '8'

 L.3744       350  LOAD_FAST                'self'
              352  LOAD_ATTR                _social_group_constraint
              354  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_FAST' instruction at offset 112

    def get_next_work_priority(self):
        if not self.is_simulating:
            return Priority.Critical
        next_interaction = self.queue.get_head()
        if next_interaction is not None:
            return next_interaction.priority
        return Priority.Low

    def get_next_work(self):
        if self.is_being_destroyed:
            logger.error('sim.get_next_work() called for Sim {} when they were in the process of being destroyed.', self, owner='tastle/sscholl')
            return WorkRequest()
            if not self.is_simulating:
                if self._starting_up:
                    return WorkRequest()
            else:
                return WorkRequest(work_element=(elements.GeneratorElement(self._startup_sim_gen)), required_sims=(
                 self,))
                return self.has_work_locks or services.posture_graph_service().has_built_for_zone_spin_up or WorkRequest()
            _ = self.queue._get_head()
            next_interaction = self.queue.get_head()
            if next_interaction is None and services.current_zone().is_zone_running:
                if any((not i.is_super for i in self.queue._autonomy)):
                    for i in tuple(self.queue._autonomy):
                        i.cancel(FinishingType.INTERACTION_QUEUE, 'Blocked interaction in autonomy bucket, canceling all interactions in the autonomy bucket to fix.')

        else:
            self.run_subaction_autonomy()
            next_interaction = self.queue.get_head()
        if next_interaction is not None:
            if next_interaction.is_waiting_pickup_putdown:
                return WorkRequest()
            next_interaction.refresh_and_lock_required_sims()
            required_sims = next_interaction.required_sims(for_threading=True)
            element = elements.GeneratorElement(functools.partial((self._process_interaction_gen), interaction=next_interaction))
            mutexed_resources = next_interaction.get_mutexed_resources()
            required_sims |= mutexed_resources
            return WorkRequest(work_element=element, required_sims=required_sims,
              additional_resources=(next_interaction.required_resources()),
              set_work_timestamp=(next_interaction.set_work_timestamp),
              debug_name=(str(next_interaction)))
        return WorkRequest()

    def get_idle_element(self, duration=10):
        if self.is_being_destroyed:
            logger.error('sim.get_idle_element() called for Sim {} when they were in the process of being destroyed.', self, owner='tastle/sscholl')
        elif not self.is_simulating:
            return (None, None)
            possible_idle_behaviors = []
            for si in self.si_state:
                idle_behavior = si.get_idle_behavior()
                if idle_behavior is not None:
                    possible_idle_behaviors.append((si, idle_behavior))

            if possible_idle_behaviors:
                _, idle_behavior = random.choice(possible_idle_behaviors)
        else:
            idle_behavior = self.posture.get_idle_behavior()
        sleep_behavior = build_element((elements.SoftSleepElement(date_and_time.create_time_span(minutes=duration)),
         self.si_state.process_gen))
        idle_sequence = build_element([
         build_critical_section(idle_behavior, flush_all_animations),
         sleep_behavior])
        idle_sequence = with_skippable_animation_time((self,), sequence=idle_sequence)
        for group in self.get_groups_for_sim_gen():
            idle_sequence = group.with_listener_focus(self, self, idle_sequence)

        def do_idle_behavior(timeline):
            nonlocal idle_sequence
            with gsi_handlers.sim_timeline_handlers.archive_sim_timeline_context_manager(self, 'Sim', 'Process Idle Interaction'):
                try:
                    self.queue._apply_next_pressure()
                    result = yield from element_utils.run_child(timeline, idle_sequence)
                    return result
                finally:
                    idle_sequence = None

            if False:
                yield None

        def cancel_idle_behavior():
            nonlocal idle_sequence
            if idle_sequence is not None:
                idle_sequence.trigger_soft_stop()
                idle_sequence = None

        return (elements.GeneratorElement(do_idle_behavior), cancel_idle_behavior)

    def _process_interaction_gen(self, timeline, interaction=None):
        with gsi_handlers.sim_timeline_handlers.archive_sim_timeline_context_manager(self, 'Sim', 'Process Interaction', interaction):
            try:
                if self.queue.get_head() is not interaction:
                    logger.info('Interaction has changed from {} to {} after work was scheduled. Bailing.', interaction, self.queue.get_head())
                    return
                yield from self.queue.process_one_interaction_gen(timeline)
            finally:
                interaction.unlock_required_sims()

        if False:
            yield None

    def push_super_affordance(self, super_affordance, target, context, **kwargs):
        if isinstance(super_affordance, str):
            super_affordance = services.get_instance_manager(sims4.resources.Types.INTERACTION).get(super_affordance)
            if not super_affordance:
                raise ValueError('{0} is not a super affordance'.format(super_affordance))
        aop = (interactions.aop.AffordanceObjectPair)(super_affordance, target, super_affordance, None, **kwargs)
        res = aop.test_and_execute(context)
        return res

    def test_super_affordance(self, super_affordance, target, context, **kwargs):
        if isinstance(super_affordance, str):
            super_affordance = services.get_instance_manager(sims4.resources.Types.INTERACTION).get(super_affordance)
            if not super_affordance:
                raise ValueError('{0} is not a super affordance'.format(super_affordance))
        aop = (interactions.aop.AffordanceObjectPair)(super_affordance, target, super_affordance, None, **kwargs)
        res = aop.test(context)
        return res

    def running_interactions_with_target_gen(self, target):
        if self.queue is not None:
            if self.queue.running is not None:
                if self.queue.running.is_super:
                    if self.queue.running.target == target:
                        yield self.queue.running
        if self.si_state is not None:
            for test_si in self.si_state:
                if test_si.target == target:
                    yield test_si

    def find_interaction_by_affordance(self, affordance):
        for si in self.queue.queued_super_interactions_gen():
            if si.affordance is affordance:
                return si

        return self.si_state.get_si_by_affordance(affordance)

    def find_interaction_by_id(self, id_to_find):
        id_to_find = self.ui_manager.get_routing_owner_id(id_to_find)
        interaction = None
        if self.queue is not None:
            interaction = self.queue.find_interaction_by_id(id_to_find)
            if interaction is None:
                transition_controller = self.queue.transition_controller
                if transition_controller is not None:
                    target_si, _ = transition_controller.interaction.get_target_si()
                    if target_si is not None:
                        if target_si.id == id_to_find:
                            return target_si
        if interaction is None:
            if self.si_state is not None:
                interaction = self.si_state.find_interaction_by_id(id_to_find)
        return interaction

    def find_continuation_by_id(self, source_id):
        interaction = None
        if self.queue is not None:
            interaction = self.queue.find_continuation_by_id(source_id)
        if interaction is None:
            if self.si_state is not None:
                interaction = self.si_state.find_continuation_by_id(source_id)
        return interaction

    def find_sub_interaction_by_aop_id(self, super_id, aop_id):
        interaction = None
        if self.queue is not None:
            interaction = self.queue.find_sub_interaction(super_id, aop_id)
        return interaction

    def set_autonomy_preference(self, preference, obj, context):
        if preference.is_scoring:
            if preference.should_clear:
                if preference.tag in self.sim_info.autonomy_scoring_preferences:
                    del self.sim_info.autonomy_scoring_preferences[preference.tag]
            else:
                self.sim_info.autonomy_scoring_preferences[preference.tag] = obj.id
        else:
            if preference.use_only:
                object_preference_tracker = services.object_preference_tracker(require_active_household=True)
                if object_preference_tracker is None:
                    return
                target_objects = set()
                if context is not None and context.pick is not None:
                    target_objects = obj.is_part or obj.get_closest_parts_to_position((context.pick.location), restrict_autonomy_preference=True)
                else:
                    target_objects = set()
                if not target_objects:
                    target_objects.add(obj)
                elif preference.should_clear:
                    object_preference_tracker.clear_restriction(target_objects, preference.tag)
                else:
                    object_preference_tracker.set_restriction(self.sim_info, target_objects, preference.tag, preference.should_set.should_force)
            else:
                if preference.should_clear:
                    if preference.tag in self.sim_info.autonomy_use_preferences[preference.tag]:
                        del self.sim_info.autonomy_use_preferences[preference.tag]
                else:
                    self.sim_info.autonomy_use_preferences[preference.tag] = obj.id

    def is_object_scoring_preferred(self, preference_tag, obj):
        return self._check_preference(preference_tag, obj, self.sim_info.autonomy_scoring_preferences)

    def is_object_use_preferred(self, preference_tag, obj):
        return self._check_preference(preference_tag, obj, self.sim_info.autonomy_use_preferences)

    def get_autonomy_preference_type(self, preference_tag, obj, full_object, allow_test=True):
        preference_type = AutonomyPreferenceType.ALLOWED
        object_preference_tracker = services.object_preference_tracker()
        if object_preference_tracker is not None:
            preference_type = object_preference_tracker.get_restriction((self.sim_info), obj,
              preference_tag,
              full_object=full_object,
              allow_test=allow_test)
        if preference_type == AutonomyPreferenceType.ALLOWED:
            if self._check_preference(preference_tag, obj, self.sim_info.autonomy_use_preferences):
                preference_type = AutonomyPreferenceType.USE_PREFERENCE
        return preference_type

    def get_use_only_object(self, preference_tag):
        object_preference_tracker = services.object_preference_tracker()
        if object_preference_tracker is not None:
            object_id, subroot_index = object_preference_tracker.get_restricted_object(self.sim_info.sim_id, preference_tag)
            if object_id is not None:
                obj = services.object_manager().get(object_id)
                if obj is not None:
                    if subroot_index is not None:
                        return obj.get_part_by_index(subroot_index)
                return obj

    @property
    def autonomy_settings(self):
        return self.get_autonomy_settings()

    def _check_preference(self, preference_tag, obj, preference_map):
        obj_id = preference_map.get(preference_tag, None)
        return obj.id == obj_id

    def _clear_clothing_buffs(self):
        for buff_type, buff_handle in self._buff_handles:
            if buff_handle is not None:
                self.remove_buff(buff_handle)
            stat = self.get_stat_instance(buff_type.commodity)
            if stat is not None:
                stat.decay_enabled = True

        self._buff_handles.clear()

    def on_outfit_changed(self, sim_info, category_and_index):
        self.apply_outfit_buffs_for_sim_info(self.sim_info, category_and_index)

    def apply_outfit_buffs_for_sim_info(self, sim_info, category_and_index):
        self._clear_clothing_buffs()
        outfit_data = (sim_info.get_outfit)(*category_and_index)
        outfit_category_tuning = OutfitTuning.OUTFIT_CATEGORY_TUNING.get(category_and_index[0], ())
        for buff in outfit_category_tuning.buffs:
            self._add_outfit_buff(buff.buff_type, buff.buff_reason)

        return outfit_data is None or outfit_data.part_ids or None
        buff_manager = services.get_instance_manager(sims4.resources.Types.BUFF)
        for buff_guid in cas.cas.get_buff_from_part_ids(outfit_data.part_ids):
            buff_type = buff_manager.get(buff_guid)
            if buff_type is None:
                logger.error('Error one of the parts in current outfit does not have a valid buff')
                continue
            self._add_outfit_buff(buff_type, self.BUFF_CLOTHING_REASON)

    def _add_outfit_buff(self, buff_type, reason):
        buff_handle = None
        if buff_type.can_add(self):
            buff_handle = self.add_buff(buff_type, buff_reason=reason)
        else:
            if buff_type.commodity is None:
                return
            stat = self.get_stat_instance(buff_type.commodity)
            if stat is not None:
                stat.decay_enabled = True
        self._buff_handles.append((buff_type, buff_handle))

    def load_staged_interactions(self):
        return self.si_state.load_staged_interactions(self.sim_info.si_state)

    def load_transitioning_interaction(self):
        return self.si_state.load_transitioning_interaction(self.sim_info.si_state)

    def load_queued_interactions(self):
        self.si_state.load_queued_interactions(self.sim_info.si_state)

    def update_related_objects(self, triggering_sim, forced_interaction=None):
        if not triggering_sim.valid_for_distribution:
            return
        else:
            PARTICIPANT_TYPE_MASK = interactions.ParticipantType.Actor | interactions.ParticipantType.Object | interactions.ParticipantType.Listeners | interactions.ParticipantType.CarriedObject | interactions.ParticipantType.CraftingObject | interactions.ParticipantType.ActorSurface
            relevant_obj_ids = set()
            relevant_obj_ids.add(self.id)
            if forced_interaction is not None:
                objs = forced_interaction.get_participants(PARTICIPANT_TYPE_MASK)
                for obj in objs:
                    relevant_obj_ids.add(obj.id)

            for i in self.running_interactions_gen(Interaction):
                objs = i.get_participants(PARTICIPANT_TYPE_MASK)
                for obj in objs:
                    relevant_obj_ids.add(obj.id)

            if self.queue is not None and self.queue.running is not None:
                objs = self.queue.running.get_participants(PARTICIPANT_TYPE_MASK)
                for obj in objs:
                    relevant_obj_ids.add(obj.id)

        op = distributor.ops.SetRelatedObjects(relevant_obj_ids, self.id)
        dist = Distributor.instance()
        dist.add_op(triggering_sim, op)

    def _is_on_spawn_point(self, use_intended_position=False):
        current_zone = services.current_zone()
        if not current_zone:
            return False
        arrival_spawn_point = current_zone.active_lot_arrival_spawn_point
        if arrival_spawn_point is None:
            return False
        position = self.intended_position if use_intended_position else self.position
        return test_point_in_polygon(position, arrival_spawn_point.get_footprint_polygon())

    @caches.cached(maxsize=10)
    def is_on_active_lot(self, tolerance=0, include_spawn_point=False):
        if self.parent is not None:
            return self.parent.is_on_active_lot(tolerance=tolerance)
            lot = services.current_zone().lot
            position = self.position
            if not lot.is_position_on_lot(position, tolerance):
                return include_spawn_point and self._is_on_spawn_point() or False
        else:
            intended_position = self.intended_position
            if intended_position != position:
                if not lot.is_position_on_lot(intended_position, tolerance):
                    return include_spawn_point and self._is_on_spawn_point(use_intended_position=True) or False
        return True

    def log_sim_info(self, *args, **kwargs):
        (self.sim_info.log_sim_info)(*args, **kwargs)

    def should_suppress_social_front_page_when_targeted(self):
        if any((buff.suppress_social_front_page_when_targeted for buff in self.Buffs)):
            return True
        return False

    def discourage_route_to_join_social_group(self):
        return self.sim_info.discourage_route_to_join_social_group()

    def bucks_trackers_gen(self):
        yield from self.sim_info.bucks_trackers_gen()
        if False:
            yield None

    def fill_choices_menu_with_si_state_aops(self, target, context, choice_menu, scoring_gsi_handler):
        for si in self.si_state:
            potential_targets = si.get_potential_mixer_targets()
            for potential_target in potential_targets:
                if target is potential_target:
                    break
                if potential_target.is_part and potential_target.part_owner is target:
                    break
            else:
                continue

            content_set = autonomy.content_sets.generate_content_set(self, (si.super_affordance),
              si,
              context,
              potential_targets=(
             target,),
              scoring_gsi_handler=scoring_gsi_handler,
              check_posture_compatibility=True,
              include_failed_aops_with_tooltip=True,
              aop_kwargs=(si.aop.interaction_parameters))
            for _, aop, test_result in content_set:
                choice_menu.add_aop(aop, context, result_override=test_result, do_test=False)

    def _get_current_subroot(self):
        if self.posture.target is not None:
            if self.posture.target.is_part:
                return str(self.posture.target.subroot_index)

    @property
    def pathplan_context(self):
        return self.routing_component.pathplan_context

    @property
    def routing_context(self):
        return self.routing_component.pathplan_context

    def _create_routing_context(self):
        pass

    def add_teleport_style_interaction_to_inject(self, interaction):
        if self._teleport_style_interactions_to_inject is None:
            self._teleport_style_interactions_to_inject = {}
        elif interaction in self._teleport_style_interactions_to_inject.keys():
            self._teleport_style_interactions_to_inject[interaction] += 1
        else:
            self._teleport_style_interactions_to_inject[interaction] = 1

    def try_remove_teleport_style_interaction_to_inject(self, interaction):
        if self._teleport_style_interactions_to_inject is None:
            logger.error('Attempted to remove a teleport style interaction to inject, but the dict is not initialized.  Interaction: {}', interaction, owner='brgibson')
            return
            if interaction not in self._teleport_style_interactions_to_inject:
                logger.error('Attempted to remove a teleport style interaction to inject, but the entry for this interaction is not in the dict.  Interaction: {}', interaction, owner='brgibson')
                return
            current_ref_count = self._teleport_style_interactions_to_inject[interaction]
            if current_ref_count <= 0:
                logger.error('Ref count for teleport style interaction to inject was zero or below when trying to remove it.  Interaction: {}, Value: {}', interaction, current_ref_count, owner='brgibson')
            current_ref_count -= 1
            if current_ref_count <= 0:
                del self._teleport_style_interactions_to_inject[interaction]
                if not self._teleport_style_interactions_to_inject:
                    self._teleport_style_interactions_to_inject = None
        else:
            self._teleport_style_interactions_to_inject[interaction] = current_ref_count

    def get_teleport_style_affordance_to_inject_list(self):
        if not self._teleport_style_interactions_to_inject:
            return ()
        return list(self._teleport_style_interactions_to_inject.keys())

    def get_teleport_style_interaction_aop(self, interaction, override_pick=None, override_target=None):
        if interaction is None:
            return (None, None, None)
        else:
            sim = interaction.sim
            if sim is None:
                return (None, None, None)
            if not TeleportHelper.can_teleport_style_be_injected_before_interaction(sim, interaction):
                return (None, None, None)
            teleport_style_affordances = self.get_teleport_style_affordance_to_inject_list()
            return teleport_style_affordances or (None, None, None)
        selected_pick = override_pick
        if selected_pick is None:
            selected_pick = interaction.context.pick
        selected_target = override_target
        if selected_target is None:
            selected_target = interaction.target
        interaction_context = InteractionContext(self, (InteractionContext.SOURCE_SCRIPT),
          (Priority.Critical),
          insert_strategy=(QueueInsertStrategy.FIRST),
          group_id=(interaction.group_id),
          pick=selected_pick)
        for teleport_style_affordance in teleport_style_affordances:
            aop = AffordanceObjectPair(teleport_style_affordance, selected_target,
              teleport_style_affordance,
              None,
              route_fail_on_transition_fail=False,
              allow_posture_changes=True,
              depended_on_si=interaction)
            test_result = aop.test(interaction_context)
            if test_result:
                teleport_style_data = TeleportTuning.get_teleport_data(teleport_style_affordance.teleport_style_tuning)
                return (aop, interaction_context, teleport_style_data)

        return (None, None, None)

    def can_sim_teleport_using_teleport_style(self):
        if TeleportHelper.does_routing_slave_prevent_teleport(self):
            return False
        for _, _, carry_object in get_carried_objects_gen(self):
            if carry_object.is_sim:
                return False

        return True

    @property
    def object_radius(self):
        return self.routing_component.object_radius

    @property
    def connectivity_handles(self):
        return self.routing_component.connectivity_handles

    @property
    def is_moving(self):
        return self.routing_component.is_moving


lock_instance_tunables(Sim, _persistence=(PersistenceType.NONE),
  _world_file_object_persists=False)