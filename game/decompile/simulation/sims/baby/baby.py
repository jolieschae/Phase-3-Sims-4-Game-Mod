# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\baby\baby.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 27226 bytes
from contextlib import contextmanager
from protocolbuffers import Commodities_pb2
from protocolbuffers.Consts_pb2 import MSG_SIM_MOOD_UPDATE
from buffs.tunable import TunableBuffReference
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from interactions.interaction_finisher import FinishingType
from interactions.utils.death import DeathTracker
from objects.components.state import ObjectState
from objects.components.state_references import TunableStateValueReference
from objects.game_object import GameObject
from objects.system import create_object
from sims.baby.baby_tuning import BabyTuning
from sims.baby.baby_utils import replace_bassinet
from sims.genealogy_tracker import genealogy_caching
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_mixin import HasSimInfoBasicMixin
from sims.sim_info_types import Gender
from sims4.geometry import QtCircle
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableEnumEntry, TunableTuple, AutoFactoryInit, HasTunableSingletonFactory, OptionalTunable, Tunable
from sims4.utils import constproperty
from statistics.mood import Mood
from tag import Tag
from ui.ui_dialog_notification import UiDialogNotification, TunableUiDialogNotificationSnippet
from vfx import PlayEffect
import build_buy, camera, distributor, distributor.ops, placement, services, sims4, tag
logger = sims4.log.Logger('Baby')

class _BabyRemovalMoment(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'notification':OptionalTunable(description='\n            If enabled, specify a notification to show when this moment is\n            executed.\n            ',
       tunable=TunableUiDialogNotificationSnippet(description='\n                The notification to show when this moment is executed.\n                ')), 
     'vfx':OptionalTunable(description='\n            If enabled, play a visual effect when this moment is executed.\n            ',
       tunable=PlayEffect.TunableFactory(description='\n                The visual effect to play when this moment is executed.\n                ')), 
     'buff':OptionalTunable(description="\n            If enabled, specify a buff to apply to the baby's immediate family\n            when this moment is executed.\n            ",
       tunable=TunableBuffReference(description="\n                The buff to be applied to the baby's immediate family when this\n                moment is executed.\n                ")), 
     'empty_state':TunableStateValueReference(description='\n            The state to set on the empty bassinet after this moment is\n            executed. This should control any reaction broadcasters that we\n            might want to happen when this baby is no longer present.\n            ',
       allow_none=True)}

    def execute_removal_moment(self, baby):
        baby.is_being_removed = True
        sim_info = baby.sim_info
        if self.notification is not None:
            dialog = self.notification(sim_info, SingleSimResolver(sim_info))
            dialog.show_dialog()
        if self.vfx is not None:
            vfx = self.vfx(baby)
            vfx.start()
        camera.focus_on_sim(baby, follow=False)
        sim_info_manager = services.sim_info_manager()
        if self.buff is not None:
            with genealogy_caching():
                for member_id in sim_info.genealogy.get_immediate_family_sim_ids_gen():
                    member_info = sim_info_manager.get(member_id)
                    if member_info.lod != SimInfoLODLevel.MINIMUM:
                        member_info.add_buff_from_op(self.buff.buff_type, self.buff.buff_reason)

        baby.cancel_interactions_running_on_object((FinishingType.TARGET_DELETED), cancel_reason_msg='Baby is being removed.')
        empty_bassinet = replace_bassinet(sim_info, safe_destroy=True)
        if self.empty_state is not None:
            empty_bassinet.set_state(self.empty_state.state, self.empty_state)
        client = sim_info.client
        if client is not None:
            client.set_next_sim_or_none(only_if_this_active_sim_info=sim_info)
            client.selectable_sims.remove_selectable_sim_info(sim_info)
        sim_info.inject_into_inactive_zone((DeathTracker.DEATH_ZONE_ID), start_away_actions=False, skip_instanced_check=True,
          skip_daycare=True)
        sim_info.household.remove_sim_info(sim_info, destroy_if_empty_household=True)
        sim_info.transfer_to_hidden_household()
        sim_info.request_lod(SimInfoLODLevel.MINIMUM)


class Baby(GameObject, HasSimInfoBasicMixin):
    MAX_PLACEMENT_ATTEMPTS = 8
    BASSINET_EMPTY_STATE = TunableStateValueReference(description='\n        The state value for an empty bassinet.\n        ')
    BASSINET_BABY_STATE = TunableStateValueReference(description='\n        The state value for a non-empty bassinet.\n        ')
    BASSINET_BABY_TRAIT_STATES = TunableMapping(description="\n        Specify any object states that are determined by the baby's traits. For\n        example, tune a state with a geometry state override to handle Alien\n        babies having their own geometry state.\n        ",
      key_type=TunableReference(description='\n            A trait that would cause babies to have a specific state..\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
      pack_safe=True),
      value_type=TunableStateValueReference(description='\n            The state associated with this trait.\n            ',
      pack_safe=True))
    DEFAULT_CORNER_POSTION_TOWARDS_CENTER_SCALE = Tunable(description='\n        This scale specifies how much the default spawn postion of infant\n        should be pushed towards center. This applies only if the default \n        position is the corner.\n        ',
      tunable_type=float,
      default=1.0)
    STATUS_STATE = ObjectState.TunableReference(description='\n        The state defining the overall status of the baby (e.g. happy, crying,\n        sleeping). We use this because we need to reapply this state to restart\n        animations after a load.\n        ')
    BABY_MOOD_MAPPING = TunableMapping(description='\n        From baby state (happy, crying, sleep) to in game mood.\n        ',
      key_type=(TunableStateValueReference()),
      value_type=(Mood.TunableReference()))
    BABY_AGE_UP = TunableTuple(description='\n        Multiple settings for baby age up moment.\n        ',
      age_up_affordance=TunableReference(description='\n            The affordance to run when baby age up to kid.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions='SuperInteraction'),
      copy_states=TunableList(description='\n            The list of the state we want to copy from the original baby\n            bassinet to the new bassinet to play idle.\n            ',
      tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectState')),
      idle_state_value=TunableReference(description='\n            The state value to apply on the new baby bassinet with the age up\n            special idle animation/vfx linked.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
      class_restrictions='ObjectStateValue'),
      statistics_to_transfer=TunableList(description="\n            On aging up the baby, we will transfer this list of statistics from bassinet object to the aged up\n            sim's sim info.\n            ",
      tunable=TunableReference(description="\n                A statistic that will be transferred from the bassinet to the aged up sim's sim info.\n                ",
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      pack_safe=True)))
    BABY_PLACEMENT_TAGS = TunableList(description='\n        When trying to place a baby bassinet on the lot, we attempt to place it\n        near other objects on the lot. Those objects are determined in priority\n        order by this tuned list. It will try to place next to all objects of\n        the matching types, before trying to place the baby in the middle of the\n        lot, and then finally trying the mailbox. If all FGL placements fail, we\n        put the baby into the household inventory.\n        ',
      tunable=TunableEnumEntry(description='\n            Attempt to place the baby near objects with this tag set.\n            ',
      tunable_type=Tag,
      default=(Tag.INVALID)))
    REMOVAL_MOMENT_STATES = TunableMapping(description='\n        A mapping of states to removal moments. When the baby is set to\n        specified state, then the removal moment will execute and the object\n        (and Sim) will be destroyed.\n        ',
      key_type=TunableStateValueReference(description='\n            The state that triggers the removal moment.\n            ',
      pack_safe=True),
      value_type=_BabyRemovalMoment.TunableFactory(description='\n            The moment that will execute when the specified state is triggered.\n            '))
    FAILED_PLACEMENT_NOTIFICATION = UiDialogNotification.TunableFactory(description='\n        The notification to show if a baby could not be spawned into the world\n        because FGL failed. This is usually due to the player cluttering their\n        lot with objects. Token 0 is the baby.\n        ')
    DEFAULT_QUADTREE_RADIUS = 0.1

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._sim_info = None
        self.state_component.state_trigger_enabled = False
        self.is_being_removed = False
        self.replacement_bassinet = None
        self._pending_removal_moment = None

    def get_delete_op(self, *args, **kwargs):
        if self.replacement_bassinet is not None:
            return distributor.ops.ObjectReplace(replacement_obj=(self.replacement_bassinet))
        return (super().get_delete_op)(*args, **kwargs)

    def may_reserve(self, *args, **kwargs):
        if self.is_being_removed:
            return False
        return (super().may_reserve)(*args, **kwargs)

    def set_sim_info(self, sim_info):
        self._sim_info = sim_info
        if self._sim_info is not None:
            self.state_component.state_trigger_enabled = True
            self.enable_baby_state()

    @constproperty
    def is_bassinet():
        return True

    @property
    def sim_info(self):
        return self._sim_info

    @property
    def sim_id(self):
        if self._sim_info is not None:
            return self._sim_info.sim_id
        return self.id

    def get_age_up_addordance(self):
        return Baby.BABY_AGE_UP.age_up_affordance

    def _transfer_statistics_to_sim_info(self):
        for stat in Baby.BABY_AGE_UP.statistics_to_transfer:
            tracker = self.get_tracker(stat)
            if not tracker is None:
                if not tracker.has_statistic(stat):
                    continue
                value = tracker.get_value(stat)
                self.sim_info.add_statistic(stat, value)

    @contextmanager
    def replacing_for_age_up(self):
        self.is_aging_up_baby = True
        try:
            yield
        finally:
            self.is_aging_up_baby = False

    def replace_for_age_up(self, interaction=None):
        self._transfer_statistics_to_sim_info()
        self.geometry_state = 'babyOff'
        if interaction is not None:
            interaction.set_target(None)
        new_bassinet = create_object(self.definition)
        new_bassinet.location = self.location
        self.replacement_bassinet = new_bassinet
        new_bassinet.set_sim_info(self.sim_info)
        new_bassinet.copy_state_values(self, state_list=(Baby.BABY_AGE_UP.copy_states))
        idle_state_value = Baby.BABY_AGE_UP.idle_state_value
        new_bassinet.set_state(idle_state_value.state, idle_state_value)
        if interaction is not None:
            interaction.set_target(new_bassinet)
        with self.replacing_for_age_up():
            self.destroy(source=(self.sim_info), cause='Replacing bassinet for age up.')
        return new_bassinet

    def place_in_good_location(self, position=None, routing_surface=None):
        plex_service = services.get_plex_service()
        is_active_zone_a_plex = plex_service.is_active_zone_a_plex()

        def try_to_place_bassinet(position, routing_surface=None, **kwargs):
            starting_location = placement.create_starting_location(position=position, routing_surface=routing_surface)
            fgl_context = (placement.create_fgl_context_for_object)(starting_location, self, **kwargs)
            translation, orientation, _ = fgl_context.find_good_location()
            if translation is not None:
                if orientation is not None:
                    if is_active_zone_a_plex:
                        if routing_surface is None or plex_service.get_plex_zone_at_position(translation, routing_surface.secondary_id) is None:
                            return False
                    self.move_to(translation=translation, orientation=orientation)
                    if routing_surface is not None:
                        self.move_to(routing_surface=routing_surface)
                    return True
            return False

        if position is not None:
            if try_to_place_bassinet(position, routing_surface=routing_surface):
                return True
        lot = services.active_lot()
        for tag in Baby.BABY_PLACEMENT_TAGS:
            for attempt, obj in enumerate(services.object_manager().get_objects_with_tag_gen(tag)):
                position = obj.position
                routing_surface = obj.routing_surface
                if lot.is_position_on_lot(position):
                    if try_to_place_bassinet(position, routing_surface=routing_surface,
                      max_distance=10):
                        return
                if attempt >= Baby.MAX_PLACEMENT_ATTEMPTS:
                    break

        position = lot.get_default_position(corner_towards_center_scale=(self.DEFAULT_CORNER_POSTION_TOWARDS_CENTER_SCALE))
        try_to_place_bassinet(position) or self.update_ownership((self.sim_info), make_sim_owner=False)
        if not build_buy.move_object_to_household_inventory(self):
            logger.error('Failed to place bassinet in household inventory.', owner='rmccord')
        if self.is_selectable:
            failed_placement_notification = Baby.FAILED_PLACEMENT_NOTIFICATION(self.sim_info, SingleSimResolver(self.sim_info))
            failed_placement_notification.show_dialog()

    def populate_localization_token(self, *args, **kwargs):
        if self.sim_info is not None:
            return (self.sim_info.populate_localization_token)(*args, **kwargs)
        logger.warn('self.sim_info is None in baby.populate_localization_token', owner='epanero', trigger_breakpoint=True)
        return (super().populate_localization_token)(*args, **kwargs)

    def enable_baby_state(self):
        if self._sim_info is None:
            return
        self.set_state(self.BASSINET_BABY_STATE.state, self.BASSINET_BABY_STATE)
        status_state = self.get_state(self.STATUS_STATE)
        self.set_state((status_state.state), status_state, force_update=True)
        for trait, trait_state in self.BASSINET_BABY_TRAIT_STATES.items():
            if self._sim_info.has_trait(trait):
                self.set_state(trait_state.state, trait_state)

        self._sim_info.Buffs.on_bassinet_ready_to_simulate()
        self._add_location_to_quadtree()

    def empty_baby_state(self):
        self.set_state(self.BASSINET_EMPTY_STATE.state, self.BASSINET_EMPTY_STATE)
        services.sim_quadtree().remove(self.id, placement.ItemType.SIM_POSITION, 0)

    def on_state_changed(self, state, old_value, new_value, from_init):
        super().on_state_changed(state, old_value, new_value, from_init)
        if self._sim_info is not None:
            sim_info_associated_baby = services.object_manager().get(self._sim_info.sim_id)
            if sim_info_associated_baby is None:
                pass
            elif sim_info_associated_baby.age is sim_info_associated_baby.age.BABY:
                if sim_info_associated_baby.id is not self.id:
                    self.baby_cloth = BabyTuning.get_baby_cloth_info(self._sim_info)
                else:
                    baby_skin_tone_op = distributor.ops.SetBabySkinTone((BabyTuning.get_baby_cloth_info(self._sim_info), self._sim_info.sim_id))
                    distributor.system.Distributor.instance().add_op(self._sim_info, baby_skin_tone_op)
                    services.get_event_manager().process_event((TestEvent.NewbornStateChanged), sim_info=(self._sim_info),
                      custom_keys=(
                     new_value.guid64,))
        removal_moment = self.REMOVAL_MOMENT_STATES.get(new_value)
        if removal_moment is not None:
            if self._sim_info is not None:
                removal_moment.execute_removal_moment(self)
            else:
                self._pending_removal_moment = removal_moment
            return
        if self.manager is not None:
            if new_value in self.BABY_MOOD_MAPPING:
                mood = self.BABY_MOOD_MAPPING[new_value]
                mood_msg = Commodities_pb2.MoodUpdate()
                mood_msg.sim_id = self.id
                mood_msg.mood_key = mood.guid64
                mood_msg.mood_intensity = 1
                distributor.shared_messages.add_object_message(self, MSG_SIM_MOOD_UPDATE, mood_msg, False)

    def load_object(self, object_data, **kwargs):
        self._sim_info = services.sim_info_manager().get(self.sim_id)
        (super().load_object)(object_data, **kwargs)
        if self._sim_info is not None:
            services.daycare_service().refresh_daycare_status(self._sim_info)

    def _validate_location(self):
        plex_service = services.get_plex_service()
        if not plex_service.is_active_zone_a_plex():
            return
        if plex_service.get_plex_zone_at_position(self.position, self.level) is not None:
            return
        self.place_in_good_location()

    def on_finalize_load(self):
        sim_info = services.sim_info_manager().get(self.sim_id)
        if sim_info is None or sim_info.household is not services.active_lot().get_household():
            replace_bassinet(sim_info, bassinet=self)
        else:
            self.set_sim_info(sim_info)
            self._validate_location()
            if self._pending_removal_moment is not None:
                self._pending_removal_moment.execute_removal_moment(self)
                self._pending_removal_moment = None
        super().on_finalize_load()

    def _add_location_to_quadtree(self):
        if self._sim_info is None:
            return
        quadtree_geometry = QtCircle(sims4.math.Vector2(self.position.x, self.position.z), self.DEFAULT_QUADTREE_RADIUS)
        services.sim_quadtree().insert(self, self.id, placement.ItemType.SIM_POSITION, quadtree_geometry, self.routing_surface, False, 0)

    def on_location_changed(self, old_location):
        super().on_location_changed(old_location)
        self._add_location_to_quadtree()

    def on_remove(self):
        services.sim_quadtree().remove(self.id, placement.ItemType.SIM_POSITION, 0)
        super().on_remove()