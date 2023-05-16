# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\buff_component.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 85685 bytes
from _collections import defaultdict
from collections import Counter
import collections, itertools, operator, random
from protocolbuffers import Commodities_pb2, Sims_pb2
from protocolbuffers.DistributorOps_pb2 import Operation
from buffs import Appropriateness
from date_and_time import create_time_span
from distributor.ops import GenericProtocolBufferOp
from distributor.rollback import ProtocolBufferRollback
from distributor.system import Distributor
from event_testing import test_events
from event_testing.resolver import SingleSimResolver
from interactions import ParticipantTypeSim
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.tunable import TunableContinuation
from objects import ALL_HIDDEN_REASONS
from objects.mixins import AffordanceCacheMixin, ProvidedAffordanceData
from routing.route_enums import RouteEventType
from sims.sim_info_lod import SimInfoLODLevel
from sims4.callback_utils import CallableList
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.tuning.tunable import TunableReference, Tunable, TunableRange, TunableList, TunableTuple, TunableEnumFlags, TunableResourceKey, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import flexmethod
from singletons import DEFAULT, EMPTY_SET
from statistics.statistic_ops import StatisticAddOp
from teleport.teleport_enums import TeleportStyleSource
from teleport.teleport_tuning import TeleportTuning
from ui.ui_dialog_picker import BasePickerRow, TunablePickerDialogVariant, ObjectPickerTuningFlags, ObjectPickerRow, UiObjectPicker
from uid import UniqueIdGenerator
import alarms, caches, enum, gsi_handlers, objects.components.types, services, sims4.log
logger = sims4.log.Logger('BuffTracker', default_owner='msantander')

class BuffUpdateType(enum.Int):
    ADD = 0
    UPDATE = 1
    REMOVE = 2
    export = False


class BuffComponent(objects.components.Component, AffordanceCacheMixin, component_name=objects.components.types.BUFF_COMPONENT):
    DEFAULT_MOOD = TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.MOOD)), description='The default initial mood.')
    UPDATE_INTENSITY_BUFFER = TunableRange(description="\n        A buffer that prevents a mood from becoming active unless its intensity\n        is greater than the current active mood's intensity plus this amount.\n        \n        For example, if this tunable is 1, and the Sim is in a Flirty mood with\n        intensity 2, then a different mood would become the active mood only if\n        its intensity is 3+.\n        \n        If the predominant mood has an intensity that is less than the active\n        mood's intensity, that mood will become the active mood.\n        ",
      tunable_type=int,
      default=1,
      minimum=0)
    EXCLUSIVE_SET = TunableList(description='\n        A list of buff groups to determine which buffs are exclusive from each\n        other within the same group.  A buff cannot exist in more than one exclusive group.\n        \n        The following rule of exclusivity for a group:\n        1. Higher weight will always be added and remove any lower weight buffs\n        2. Lower weight buff will not be added if a higher weight already exist in component\n        3. Same weight buff will always be added and remove any buff with same weight.\n        \n        Example: Group 1:\n                    Buff1 with weight of 5 \n                    Buff2 with weight of 1\n                    Buff3 with weight of 1\n                 Group 2:\n                    Buff4 with weight of 6\n        \n        If sim has Buff1, trying to add Buff2 or Buff3 will not be added.\n        If sim has Buff2, trying to add Buff3 will remove Buff2 and add Buff3\n        If sim has Buff2, trying to add Buff1 will remove Buff 2 and add Buff3\n        If sim has Buff4, trying to add Buff1, Buff2, or Buff3 will be added and Buff4 will stay \n                          on component \n        ',
      tunable=TunableList(tunable=TunableTuple(buff_type=TunableReference(description='\n                    Buff in exclusive group\n                    ',
      manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
      pack_safe=True),
      weight=Tunable(description='\n                    weight to determine if this buff should be added and\n                    remove other buffs in the exclusive group or not added at all.\n                    \n                    Example: Buff1 with weight of 5 \n                             Buff2 with weight of 1\n                             Buff3 with weight of 1\n                    \n                    If sim has Buff1, trying to add Buff2 or Buff3 will not be added.\n                    If sim has Buff2, trying to add Buff3 will remove Buff2 and add Buff3\n                    if sim has Buff2, trying to add Buff1 will remove Buff 2 and add Buff3\n                    ',
      tunable_type=int,
      default=1))))

    def __init__(self, owner):
        super().__init__(owner)
        self._active_buffs = {}
        self._get_next_handle_id = UniqueIdGenerator()
        self._success_chance_modification = 0
        self._active_mood = self.DEFAULT_MOOD
        self._active_mood_intensity = 0
        self._active_mood_buff_handle = None
        self.on_mood_changed = CallableList()
        self.on_mood_changed.append(self._publish_mood_update)
        self.on_mood_changed.append(self._send_mood_changed_event)
        self.load_in_progress = False
        self._additional_posture_costs = Counter()
        self._additional_posture_costs_ref_count = defaultdict(int)
        self.on_buff_added = CallableList()
        self.on_buff_removed = CallableList()
        self._active_teleport_styles = None
        self.buff_update_alarms = {}
        self.portal_cost_override_map = collections.OrderedDict()
        if self._active_mood is None:
            logger.error('No default mood tuned in buff_component.py')
        else:
            if self._active_mood.buffs:
                initial_buff_ref = self._active_mood.buffs[0]
                if initial_buff_ref:
                    if initial_buff_ref.buff_type:
                        self._active_mood_buff_handle = self.add_buff(initial_buff_ref.buff_type)

    def __iter__(self):
        return self._active_buffs.values().__iter__()

    def __len__(self):
        return len(self._active_buffs)

    def on_sim_ready_to_simulate(self):
        region_instance = services.current_region()
        for region_buff in region_instance.region_buffs:
            self.add_buff_from_op(region_buff)

        weather_service = services.weather_service()
        if weather_service is not None:
            weather_service.apply_weather_option_buffs(self.owner)
        for buff_type, buff in tuple(self._active_buffs.items()):
            if buff_type not in self._active_buffs:
                continue
            buff.on_sim_ready_to_simulate()

        self._publish_mood_update()

    def on_bassinet_ready_to_simulate(self):
        for buff_type, buff in tuple(self._active_buffs.items()):
            if buff_type not in self._active_buffs:
                continue
            buff.on_bassinet_ready_to_simulate()

    def on_sim_removed(self, *args, **kwargs):
        for buff in tuple(self):
            (buff.on_sim_removed)(*args, **kwargs)

        self._remove_non_persist_buffs()

    def on_sim_added_to_skewer(self):
        self._create_and_send_buff_clear_all_msg()
        for buff in self:
            self.send_buff_update_msg(buff, BuffUpdateType.ADD)

    def on_sim_reset(self):
        for buff in self:
            buff.on_sim_reset()

    def clean_up(self):
        for buff_type, buff_entry in tuple(self._active_buffs.items()):
            self.remove_auto_update(buff_type)
            buff_entry.clean_up()

        self._active_buffs.clear()
        self.on_mood_changed.clear()
        self.on_buff_added.clear()
        self.on_buff_removed.clear()

    @objects.components.componentmethod
    def add_buff_from_op(self, buff_type, buff_reason=None):
        can_add, _ = self._can_add_buff_type(buff_type)
        if not can_add:
            return False
        buff_commodity = buff_type.commodity
        if buff_commodity is not None:
            if self.has_buff(buff_type):
                if buff_type.reloot_on_add:
                    buff = self._active_buffs.get(buff_type)
                    buff.apply_all_loot_actions()
                if not buff_type.refresh_on_add:
                    return False
            else:
                tracker = self.owner.get_tracker(buff_commodity)
                if buff_commodity.convergence_value == buff_commodity.max_value:
                    tracker.set_min(buff_commodity)
                else:
                    tracker.set_max(buff_commodity)
            self.set_buff_reason(buff_type, buff_reason, use_replacement=True)
        else:
            self.add_buff(buff_type, buff_reason=buff_reason)
        return True

    @objects.components.componentmethod
    def add_buff(self, buff_type, buff_reason=None, update_mood=True, commodity_guid=None, replacing_buff=None, timeout_string=None, timeout_string_no_next_buff=None, transition_into_buff_id=0, change_rate=None, immediate=False, from_load=False, apply_buff_loot=True, additional_static_commodities_to_add=None, remove_on_zone_unload=True):
        from_load = from_load or self.load_in_progress
        replacement_buff_type, replacement_buff_reason = self._get_replacement_buff_type_and_reason(buff_type, buff_reason)
        if replacement_buff_type is not None:
            return self.owner.add_buff(replacement_buff_type, buff_reason=replacement_buff_reason,
              update_mood=update_mood,
              commodity_guid=commodity_guid,
              replacing_buff=(replacing_buff if replacing_buff is not None else buff_type),
              timeout_string=timeout_string,
              timeout_string_no_next_buff=timeout_string_no_next_buff,
              transition_into_buff_id=transition_into_buff_id,
              change_rate=change_rate,
              immediate=immediate,
              from_load=from_load,
              apply_buff_loot=apply_buff_loot,
              additional_static_commodities_to_add=additional_static_commodities_to_add,
              remove_on_zone_unload=remove_on_zone_unload)
        else:
            can_add, conflicting_buff_type = self._can_add_buff_type(buff_type)
            return can_add or None
        buff = self._active_buffs.get(buff_type)
        if buff is None:
            buff = buff_type((self.owner), commodity_guid, replacing_buff, transition_into_buff_id, additional_static_commodities_to_add=additional_static_commodities_to_add,
              remove_on_zone_unload=remove_on_zone_unload)
            self._active_buffs[buff_type] = buff
            buff.on_add(from_load=from_load, apply_buff_loot=apply_buff_loot)
            provided_affordances = []
            for provided_affordance in buff.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                provided_affordances.append(provided_affordance_data)

            self.add_to_affordance_caches(buff.super_affordances, provided_affordances)
            self.add_to_actor_mixer_cache(buff.actor_mixers)
            self.add_to_provided_mixer_cache(buff.provided_mixers)
            self._update_chance_modifier()
            if update_mood:
                self._update_current_mood()
            if self.owner.household is not None:
                services.get_event_manager().process_event((test_events.TestEvent.BuffBeganEvent), sim_info=(self.owner),
                  sim_id=(self.owner.sim_id),
                  buff=buff_type,
                  custom_keys=(
                 buff_type,))
                self.register_auto_update(self.owner, buff_type)
            self.on_buff_added(buff_type, self.owner.id)
            self._additional_posture_costs.update(buff.additional_posture_costs)
            for posture in buff.additional_posture_costs.keys():
                self._additional_posture_costs_ref_count[posture] += 1

        handle_id = self._get_next_handle_id()
        buff.add_handle(handle_id, buff_reason=buff_reason)
        self.send_buff_update_msg(buff, (BuffUpdateType.ADD), change_rate=change_rate, immediate=immediate)
        if conflicting_buff_type is not None:
            self.remove_buff_by_type(conflicting_buff_type)
        return handle_id

    def _get_replacement_buff_type_and_reason(self, buff_type, buff_reason):
        if buff_type.trait_replacement_buffs is not None:
            trait_tracker = self.owner.trait_tracker
            for trait, replacement_buff_data in sorted((buff_type.trait_replacement_buffs.items()), key=(lambda item: item[1].buff_replacement_priority),
              reverse=True):
                replacement_buff_type = replacement_buff_data.buff_type
                if trait_tracker.has_trait(trait) and replacement_buff_type.can_add(self.owner):
                    replacement_buff_reason = buff_reason if replacement_buff_data.buff_reason is None else replacement_buff_data.buff_reason
                    return (replacement_buff_type, replacement_buff_reason)

        return (None, None)

    def register_auto_update(self, sim_info_in, buff_type_in):
        if buff_type_in in self.buff_update_alarms:
            self.remove_auto_update(buff_type_in)
        if sim_info_in.is_selectable:
            if buff_type_in.visible:
                self.buff_update_alarms[buff_type_in] = alarms.add_alarm(self, create_time_span(minutes=15), lambda _, sim_info=sim_info_in, buff_type=buff_type_in: services.get_event_manager().process_event((test_events.TestEvent.BuffUpdateEvent), sim_info=sim_info,
                  sim_id=(sim_info.sim_id),
                  buff=buff_type), True)

    def remove_auto_update(self, buff_type):
        if buff_type in self.buff_update_alarms:
            alarms.cancel_alarm(self.buff_update_alarms[buff_type])
            del self.buff_update_alarms[buff_type]

    def _remove_posture_costs(self, buff_type):
        self._additional_posture_costs.subtract(buff_type.additional_posture_costs)
        for posture in buff_type.additional_posture_costs.keys():
            self._additional_posture_costs_ref_count[posture] -= 1
            if self._additional_posture_costs_ref_count[posture] <= 0:
                del self._additional_posture_costs[posture]
                del self._additional_posture_costs_ref_count[posture]

    @objects.components.componentmethod
    def remove_buff(self, handle_id, update_mood=True, immediate=False, on_destroy=False):
        for buff_type, buff_entry in self._active_buffs.items():
            if handle_id in buff_entry.handle_ids:
                should_remove = buff_entry.remove_handle(handle_id)
                if should_remove:
                    del self._active_buffs[buff_type]
                    buff_entry.on_remove(apply_loot_on_remove=(not self.load_in_progress and not on_destroy))
                    if not on_destroy:
                        self.update_affordance_caches()
                        if update_mood:
                            self._update_current_mood()
                        self._update_chance_modifier()
                        self.send_buff_update_msg(buff_entry, (BuffUpdateType.REMOVE), immediate=immediate)
                        services.get_event_manager().process_event((test_events.TestEvent.BuffEndedEvent), sim_info=(self.owner),
                          sim_id=(self.owner.sim_id),
                          buff=buff_type,
                          custom_keys=(
                         buff_type,))
                    if buff_type in self.buff_update_alarms:
                        self.remove_auto_update(buff_type)
                    self.on_buff_removed(buff_type, self.owner.id)
                    self._remove_posture_costs(buff_type)
                break

    @objects.components.componentmethod
    def get_buff_type(self, handle_id):
        for buff_type, buff_entry in self._active_buffs.items():
            if handle_id in buff_entry.handle_ids:
                return buff_type

    @objects.components.componentmethod
    def get_buff_by_type(self, buff_type):
        return self._active_buffs.get(buff_type)

    @objects.components.componentmethod
    def has_buff(self, buff_type):
        return buff_type in self._active_buffs

    @objects.components.componentmethod
    def has_buff_with_tag(self, tag):
        return any((buff.has_tag(tag) for buff in self._active_buffs))

    @objects.components.componentmethod
    def has_buff_with_display_type(self, display_type):
        return any((buff_entry.display_type == display_type for buff_type, buff_entry in self._active_buffs.items()))

    @objects.components.componentmethod_with_fallback(lambda *_, **__: ())
    def get_all_buffs_with_tag(self, tag):
        return (buff for buff in self._active_buffs if buff.has_tag(tag))

    @objects.components.componentmethod
    def get_active_buff_types(self):
        return self._active_buffs.keys()

    @objects.components.componentmethod
    def get_buff_reason(self, handle_id):
        for buff_entry in self._active_buffs.values():
            if handle_id in buff_entry.handle_ids:
                return buff_entry.buff_reason

    @objects.components.componentmethod
    def debug_add_buff_by_type(self, buff_type):
        can_add, conflicting_buff_type = self._can_add_buff_type(buff_type)
        if not can_add:
            return False
        elif buff_type.commodity is not None:
            tracker = self.owner.get_tracker(buff_type.commodity)
            state_index = buff_type.commodity.get_state_index_matches_buff_type(buff_type)
            if state_index is not None:
                index = state_index + 1
                if index < len(buff_type.commodity.commodity_states):
                    commodity_to_value = buff_type.commodity.commodity_states[index].value - 1
                else:
                    commodity_to_value = buff_type.commodity.max_value
                tracker.set_value(buff_type.commodity, commodity_to_value)
            else:
                logger.error('commodity ({}) has no states with buff ({}), Buff will not be added.', buff_type.commodity, buff_type)
                return False
        else:
            self.add_buff(buff_type)
        if conflicting_buff_type is not None:
            self.remove_buff_by_type(conflicting_buff_type)
        return True

    @objects.components.componentmethod
    def remove_buffs_by_tags(self, tags, count_to_remove=None, on_destroy=False):
        buffs_tagged = [buff for buff in self._active_buffs.values() if buff.has_any_tag(tags)]
        if count_to_remove is None:
            for buff_entry in buffs_tagged:
                self.remove_buff_entry(buff_entry, on_destroy=on_destroy)

        else:
            random.shuffle(buffs_tagged)
            for buff_entry in buffs_tagged:
                self.remove_buff_entry(buff_entry, on_destroy=on_destroy)
                count_to_remove -= 1
                if count_to_remove <= 0:
                    return

    @objects.components.componentmethod
    def remove_buff_by_type(self, buff_type, on_destroy=False):
        buff_entry = self._active_buffs.get(buff_type, None)
        if buff_entry is not None:
            self.remove_buff_entry(buff_entry, on_destroy=on_destroy)

    @objects.components.componentmethod
    def remove_buff_entry(self, buff_entry, on_destroy=False):
        if buff_entry is not None:
            if buff_entry.commodity is not None:
                tracker = self.owner.get_tracker(buff_entry.commodity)
                commodity_inst = tracker.get_statistic(buff_entry.commodity)
                if commodity_inst is not None and commodity_inst.state_backed:
                    if not on_destroy:
                        logger.warn('By removing buff {}, we are attempting to remove the commodity {},                                      which is backed by a state. This may lead to undesired behavior.                                      Please consider setting the commodity value rather than removing the buff.',
                          buff_entry,
                          commodity_inst, owner='miking')
                    elif commodity_inst is not None and commodity_inst.core:
                        if not on_destroy:
                            logger.callstack('Attempting to explicitly remove the buff {}, which is given by a core commodity.                                           This would result in the removal of a core commodity and will be ignored.                                           Please consider setting the commodity value rather than removing the buff.',
                              buff_entry,
                              owner='tastle', level=(sims4.log.LEVEL_ERROR))
                        return
                    tracker.remove_statistic((buff_entry.commodity), on_destroy=on_destroy)
                else:
                    pass
            if buff_entry.buff_type in self._active_buffs:
                buff_type = buff_entry.buff_type
                del self._active_buffs[buff_type]
                buff_entry.on_remove(apply_loot_on_remove=(not self.load_in_progress and not on_destroy))
                if not on_destroy:
                    self.update_affordance_caches()
                    self._update_chance_modifier()
                    self._update_current_mood()
                    self.send_buff_update_msg(buff_entry, BuffUpdateType.REMOVE)
                    services.get_event_manager().process_event((test_events.TestEvent.BuffEndedEvent), sim_info=(self.owner),
                      sim_id=(self.owner.id),
                      buff=buff_type,
                      custom_keys=(
                     buff_type,))
                else:
                    if self.owner.is_selectable:
                        self._update_current_mood()
                        self.send_buff_update_msg(buff_entry, BuffUpdateType.REMOVE)
                    self.on_buff_removed(buff_type, self.owner.id)
                    self._remove_posture_costs(buff_type)

    @objects.components.componentmethod
    def set_buff_reason(self, buff_type, buff_reason, use_replacement=False):
        buff_commodity = buff_type.commodity
        if use_replacement:
            replacement_buff_type, replacement_buff_reason = self._get_replacement_buff_type_and_reason(buff_type, buff_reason)
            if replacement_buff_type is not None:
                buff_type = replacement_buff_type
                buff_reason = replacement_buff_reason
        if buff_reason is None:
            return
        buff_entry = self._active_buffs.get(buff_type)
        if buff_entry is not None:
            buff_entry.buff_reason = buff_reason
            self.send_buff_update_msg(buff_entry, BuffUpdateType.UPDATE)
        else:
            if buff_commodity is not None:
                tracker = self.owner.get_tracker(buff_commodity)
                stat = tracker.get_statistic(buff_commodity, add=False)
                if stat is not None:
                    stat.force_buff_reason = buff_reason

    @objects.components.componentmethod
    def buff_commodity_changed(self, handle_id, change_rate=None, transition_into_buff_id=0):
        for _, buff_entry in self._active_buffs.items():
            if handle_id in buff_entry.handle_ids:
                if buff_entry.show_timeout:
                    buff_entry.transition_into_buff_id = transition_into_buff_id
                    self.send_buff_update_msg(buff_entry, (BuffUpdateType.UPDATE), change_rate=change_rate)
                break

    @objects.components.componentmethod
    def get_success_chance_modifier(self):
        return self._success_chance_modification

    @objects.components.componentmethod
    def get_actor_scoring_modifier(self, affordance, resolver):
        total = 0
        for buff_entry in self._active_buffs.values():
            total += buff_entry.effect_modification.get_affordance_scoring_modifier(affordance, resolver)

        return total

    @objects.components.componentmethod
    def get_actor_success_modifier(self, affordance, resolver):
        total = 0
        for buff_entry in self._active_buffs.values():
            total += buff_entry.effect_modification.get_affordance_success_modifier(affordance, resolver)

        return total

    @objects.components.componentmethod
    def get_actor_new_pie_menu_icon_and_parent_name(self, affordance, resolver):
        icon = None
        parent = None
        icon_tag = None
        parent_tag = None
        for buff_entry in self._active_buffs.values():
            new_icon, new_parent, new_icon_tag, new_parent_tag = buff_entry.effect_modification.get_affordance_new_pie_menu_icon_and_parent_name(affordance, resolver)
            if new_icon is not None:
                if icon is not None:
                    if icon is not new_icon:
                        logger.error('different valid pie menu icons specified in {}', self, owner='nabaker')
                    else:
                        icon = new_icon
                        if icon_tag is None:
                            icon_tag = new_icon_tag
                        else:
                            icon_tag &= new_icon_tag
                elif new_parent is not None:
                    if parent is not None:
                        if parent is not new_parent:
                            logger.error('different valid pie menu parent names specified in {}', self, owner='nabaker')
                parent = new_parent
                if parent_tag is None:
                    parent_tag = new_parent_tag
                else:
                    parent_tag &= new_parent_tag

        if icon_tag is None:
            icon_tag = set()
        if parent_tag is None:
            parent_tag = set()
        return (
         icon, parent, icon_tag, parent_tag)

    @objects.components.componentmethod
    def get_actor_basic_extras_reversed_gen(self, affordance, resolver):
        for buff_entry in self._active_buffs.values():
            yield from buff_entry.effect_modification.get_affordance_basic_extras_reversed_gen(affordance, resolver)

        if False:
            yield None

    @objects.components.componentmethod
    def test_pie_menu_modifiers(self, affordance):
        buffs = self._get_buffs_with_pie_menu_modifiers()
        for buff in buffs:
            visible, tooltip = buff.effect_modification.test_pie_menu_modifiers(affordance)
            if not visible or tooltip is not None:
                return (
                 visible, tooltip)

        return (True, None)

    @caches.cached
    def _get_buffs_with_pie_menu_modifiers(self):
        return tuple((buff for buff in self._active_buffs.values() if buff.effect_modification.has_pie_menu_modifiers()))

    @objects.components.componentmethod
    def get_mood(self):
        return self._active_mood

    @objects.components.componentmethod
    def get_mood_animation_param_name(self):
        param_name = self._active_mood.asm_param_name
        if param_name is not None:
            return param_name
        mood, _, _ = self._get_largest_mood(predicate=(lambda mood:         if mood.asm_param_name:
True # Avoid dead code: False))
        return mood.asm_param_name

    @objects.components.componentmethod
    def get_mood_intensity(self):
        return self._active_mood_intensity

    @objects.components.componentmethod
    def get_effective_skill_level(self, skill):
        if skill.stat_type == skill:
            skill = self.owner.get_stat_instance(skill) or skill
        user_value = skill.get_user_value()
        modifier = 0
        for buff_entry in self._active_buffs.values():
            modifier += buff_entry.effect_modification.get_effective_skill_modifier(skill)

        return user_value + modifier

    @objects.components.componentmethod
    def effective_skill_modified_buff_gen(self, skill):
        for buff_entry in self._active_buffs.values():
            modifier = buff_entry.effect_modification.get_effective_skill_modifier(skill)
            if modifier != 0:
                yield (
                 buff_entry, modifier)

    @objects.components.componentmethod
    def is_appropriate(self, tags):
        final_appropriateness = Appropriateness.DONT_CARE
        for buff in self._active_buffs:
            appropriateness = buff.get_appropriateness(tags)
            if appropriateness > final_appropriateness:
                final_appropriateness = appropriateness

        if final_appropriateness == Appropriateness.NOT_ALLOWED:
            return False
        return True

    @objects.components.componentmethod
    def get_additional_posture_costs(self):
        return self._additional_posture_costs

    @objects.components.componentmethod
    def add_venue_buffs(self):
        venue_instance = services.get_current_venue()
        for venue_buff in venue_instance.venue_buffs:
            self.add_buff_from_op((venue_buff.buff_type), buff_reason=(venue_buff.buff_reason))

    @objects.components.componentmethod
    def get_super_affordance_availability_gen(self):
        yield from self.get_cached_super_affordances_gen()
        if False:
            yield None

    @objects.components.componentmethod
    def get_target_super_affordance_availability_gen(self, context, target):
        yield from self.get_cached_target_super_affordances_gen(context, target)
        if False:
            yield None

    @objects.components.componentmethod
    def get_actor_mixers(self, super_interaction):
        return self.get_cached_actor_mixers(super_interaction)

    @objects.components.componentmethod
    def get_provided_mixers_gen(self, super_interaction):
        yield from self.get_cached_provided_mixers_gen(super_interaction)
        if False:
            yield None

    @objects.components.componentmethod
    def get_target_provided_affordances_data_gen(self):
        yield from self.get_cached_target_provided_affordances_data_gen()
        if False:
            yield None

    def get_provided_super_affordances(self):
        affordances, target_affordances = set(), list()
        for buff_entry in self:
            affordances.update(buff_entry.super_affordances)
            for provided_affordance in buff_entry.target_super_affordances:
                provided_affordance_data = ProvidedAffordanceData(provided_affordance.affordance, provided_affordance.object_filter, provided_affordance.allow_self)
                target_affordances.append(provided_affordance_data)

        return (
         affordances, target_affordances)

    def get_actor_and_provided_mixers_list(self):
        actor_mixers = [buff_entry.actor_mixers for buff_entry in self]
        provided_mixers = [buff_entry.provided_mixers for buff_entry in self]
        return (actor_mixers, provided_mixers)

    def get_sim_info_from_provider(self):
        return self.owner

    @objects.components.componentmethod
    def add_teleport_style(self, source_type, teleport_style):
        if self._active_teleport_styles is None:
            self._active_teleport_styles = defaultdict(list)
        self._active_teleport_styles[source_type].append(teleport_style)

    @objects.components.componentmethod
    def remove_teleport_style(self, source_type, teleport_style):
        self._active_teleport_styles[source_type].remove(teleport_style)
        if len(self._active_teleport_styles[source_type]) == 0:
            del self._active_teleport_styles[source_type]
        if not self._active_teleport_styles:
            self._active_teleport_styles = None

    @objects.components.componentmethod
    def get_active_teleport_multiplier(self):
        multiplier = 1
        for buff_entry in self._active_buffs.values():
            if buff_entry.teleport_cost_multiplier:
                multiplier *= buff_entry.teleport_cost_multiplier

        return multiplier

    @objects.components.componentmethod_with_fallback(lambda *_, **__: None)
    def get_active_teleport_style(self):
        if self._active_teleport_styles is None:
            return (None, None, False)
        active_multiplier = self.get_active_teleport_multiplier()
        tuned_liability_style = self._active_teleport_styles.get(TeleportStyleSource.TUNED_LIABILITY, None)
        if tuned_liability_style:
            teleport_data, cost = self.get_teleport_data_and_cost(tuned_liability_style[0], active_multiplier)
            return (teleport_data, cost, True)
        for active_teleports in self._active_teleport_styles.values():
            for teleport_style in active_teleports:
                teleport_data, cost = self.get_teleport_data_and_cost(teleport_style, active_multiplier)
                if teleport_data is None:
                    continue
                return (
                 teleport_data, cost, False)

        return (None, None, False)

    @objects.components.componentmethod_with_fallback(lambda *_, **__: False)
    def can_trigger_teleport_style(self, teleport_style):
        active_multiplier = self.get_active_teleport_multiplier()
        _, cost = self.get_teleport_data_and_cost(teleport_style, active_multiplier)
        return cost is not None

    @objects.components.componentmethod_with_fallback(lambda *_, **__: None)
    def get_teleport_cost(self, teleport_data, active_multiplier):
        if teleport_data is None:
            return
            cost_tuning = teleport_data.teleport_cost
            if cost_tuning is not None:
                current_value = self.owner.get_stat_value(teleport_data.teleport_cost.teleport_statistic)
                current_cost = active_multiplier * teleport_data.teleport_cost.cost
                if cost_tuning.cost_is_additive:
                    if current_value + current_cost < cost_tuning.teleport_statistic.max_value:
                        return current_cost
        elif current_value - current_cost > cost_tuning.teleport_statistic.min_value:
            return current_cost

    @objects.components.componentmethod
    def get_teleport_data_and_cost(self, teleport_style, active_multiplier):
        teleport_data = TeleportTuning.get_teleport_data(teleport_style)
        return (teleport_data, self.get_teleport_cost(teleport_data, active_multiplier))

    @objects.components.componentmethod
    def set_portal_cost_override(self, buff, object_tag, new_cost):
        sim = self.owner.sim_info.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            logger.error('Trying to set portal cost override to a non instantiated sim: {}', sim)
            return
        portal_instances = []
        for portal_object in services.object_manager().get_objects_with_tag_gen(object_tag):
            portal_instances += list(portal_object.get_portal_instances())

        if buff not in self.portal_cost_override_map:
            self.portal_cost_override_map[buff] = defaultdict(list)
        self.portal_cost_override_map[buff][object_tag] = (
         portal_instances, new_cost)
        for portal_instance in portal_instances:
            portal_instance.set_portal_cost_override(new_cost, sim, is_sim_specific=True)

    @objects.components.componentmethod
    def clear_portal_cost_override(self, buff):
        sim = self.owner.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            logger.error('Trying to clear portal cost override to a non instantiated sim: {}', sim)
            return
        object_tags_dict = self.portal_cost_override_map[buff]
        del self.portal_cost_override_map[buff]
        for object_tag in object_tags_dict:
            found = False
            for stored_buff in reversed(self.portal_cost_override_map):
                if object_tag in self.portal_cost_override_map[stored_buff]:
                    portal_instances, value = self.portal_cost_override_map[stored_buff][object_tag]
                    for portal_instance in portal_instances:
                        portal_instance.set_portal_cost_override(value, sim, is_sim_specific=True)

                    found = True
                    break

            if not found:
                portal_instances, _ = object_tags_dict[object_tag]
                for portal_instance in portal_instances:
                    portal_instance.clear_portal_cost_override(sim, is_sim_specific=True)

    @objects.components.componentmethod
    def portal_cost_override_map(self, buff):
        return self.portal_cost_override_map.get(buff, None)

    def provide_route_events_from_buffs(self, route_event_context, sim, path, failed_types=None, **kwargs):
        for buff_entry in self:
            if buff_entry.route_events is not None:
                (buff_entry.provide_route_events)(route_event_context, sim, path, failed_types, **kwargs)

    def get_additional_create_ops(self):
        if self.owner.lod == SimInfoLODLevel.MINIMUM:
            return EMPTY_SET
        additional_ops = [GenericProtocolBufferOp(Operation.SIM_MOOD_UPDATE, self._create_mood_update_msg())]
        for buff in self:
            if buff.visible:
                additional_ops.append(GenericProtocolBufferOp(Operation.SIM_BUFF_UPDATE, self._create_buff_update_msg(buff, True)))

        return additional_ops

    def _publish_mood_update(self, **kwargs):
        if self.owner.valid_for_distribution:
            if self.owner.visible_to_client == True:
                Distributor.instance().add_op(self.owner, GenericProtocolBufferOp(Operation.SIM_MOOD_UPDATE, self._create_mood_update_msg()))

    def _send_mood_changed_event(self, old_mood=None, new_mood=None):
        services.get_event_manager().process_event((test_events.TestEvent.MoodChange), sim_info=(self.owner),
          old_mood=old_mood,
          new_mood=new_mood)

    def _create_mood_update_msg(self):
        mood_msg = Commodities_pb2.MoodUpdate()
        mood_msg.sim_id = self.owner.id
        mood_msg.mood_key = self._active_mood.guid64
        mood_msg.mood_intensity = self._active_mood_intensity
        return mood_msg

    def _create_buff_update_msg(self, buff, update_type, change_rate=None):
        buff_msg = Sims_pb2.BuffUpdate()
        buff_msg.buff_id = buff.guid64
        buff_msg.sim_id = self.owner.id
        buff_msg.update_type = update_type
        if buff.buff_reason is not None:
            buff_msg.reason = buff.buff_reason
        else:
            buff_msg.display_type = buff.display_type
            if update_type == BuffUpdateType.ADD or update_type == BuffUpdateType.UPDATE:
                if buff.show_timeout:
                    timeout, rate_multiplier = buff.get_timeout_time()
                    buff_msg.timeout = timeout
                    buff_msg.rate_multiplier = rate_multiplier
                    if change_rate is not None:
                        if change_rate == 0:
                            progress_arrow = Sims_pb2.BUFF_PROGRESS_NONE
                    else:
                        progress_arrow = Sims_pb2.BUFF_PROGRESS_UP if change_rate > 0 and not buff.flip_arrow_for_progress_update else Sims_pb2.BUFF_PROGRESS_DOWN
                else:
                    progress_arrow = Sims_pb2.BUFF_PROGRESS_DOWN if not buff.flip_arrow_for_progress_update else Sims_pb2.BUFF_PROGRESS_UP
            else:
                buff_msg.buff_progress = progress_arrow
        buff_msg.is_mood_buff = buff.is_mood_buff
        buff_msg.commodity_guid = buff.commodity_guid or 0
        if buff.mood_override is not None:
            buff_msg.mood_type_override = buff.mood_override.guid64
        buff_msg.transition_into_buff_id = buff.transition_into_buff_id
        for overlay_type, linked_commodity in buff.motive_panel_overlays.items():
            with ProtocolBufferRollback(buff_msg.motive_overlays) as (motive_overlay):
                motive_overlay.overlay_type = overlay_type
                motive_overlay.commodity_guid = linked_commodity.guid64

        return buff_msg

    def send_buff_update_msg(self, buff, update_type, change_rate=None, immediate=False):
        if not buff.visible:
            if not buff.motive_panel_overlays:
                return
        elif self.owner.valid_for_distribution:
            if self.owner.is_sim and self.owner.is_selectable:
                buff_msg = self._create_buff_update_msg(buff, update_type, change_rate=change_rate)
                if gsi_handlers.buff_handlers.sim_buff_log_archiver.enabled:
                    gsi_handlers.buff_handlers.archive_buff_message(buff_msg, update_type, change_rate)
                Distributor.instance().add_op(self.owner, GenericProtocolBufferOp(Operation.SIM_BUFF_UPDATE, buff_msg))

    def _create_and_send_buff_clear_all_msg(self):
        buff_msg = Sims_pb2.BuffClearAll()
        buff_msg.sim_id = self.owner.sim_id
        Distributor.instance().add_op(self.owner, GenericProtocolBufferOp(Operation.SIM_BUFF_CLEAR_ALL, buff_msg))

    def _can_add_buff_type(self, buff_type):
        if not buff_type.can_add(self.owner):
            return (False, None)
        mood = buff_type.mood_type
        if mood is not None:
            if mood.excluding_traits is not None:
                if self.owner.trait_tracker.has_any_trait(mood.excluding_traits):
                    return (False, None)
        if buff_type.exclusive_index is None:
            return (True, None)
        for conflicting_buff_type in self._active_buffs:
            if conflicting_buff_type is buff_type:
                continue
            if conflicting_buff_type.exclusive_index == buff_type.exclusive_index:
                if buff_type.exclusive_weight < conflicting_buff_type.exclusive_weight:
                    return (False, None)
                return (True, conflicting_buff_type)

        return (True, None)

    def _update_chance_modifier(self):
        positive_success_buff_delta = 0
        negative_success_buff_delta = 1
        for buff_entry in self._active_buffs.values():
            if buff_entry.success_modifier > 0:
                positive_success_buff_delta += buff_entry.get_success_modifier
            else:
                negative_success_buff_delta *= 1 + buff_entry.get_success_modifier

        self._success_chance_modification = positive_success_buff_delta - (1 - negative_success_buff_delta)

    def _get_largest_mood(self, predicate=None, buffs_to_ignore=()):
        weights = {}
        polarity_to_changeable_buffs = collections.defaultdict(list)
        polarity_to_largest_mood_and_weight = {}
        mood_modifiers_mapping = {}
        for buff_entry in self._active_buffs.values():
            this_modifier = buff_entry.effect_modification.get_mood_category_weight_mapping()
            for mood, modifier in this_modifier.items():
                total_modifier = mood_modifiers_mapping.get(mood, 1) * modifier
                mood_modifiers_mapping[mood] = total_modifier

        for buff_entry in self._active_buffs.values():
            current_mood = buff_entry.mood_type
            current_weight = buff_entry.mood_weight
            if current_mood is None or current_weight == 0:
                continue
            if predicate is not None:
                if not predicate(current_mood):
                    continue
                else:
                    if buff_entry in buffs_to_ignore:
                        continue
                    current_polarity = current_mood.buff_polarity
                    if buff_entry.is_changeable:
                        polarity_to_changeable_buffs[current_polarity].append(buff_entry)
                        continue
                    total_current_weight = weights.get(current_mood, 0)
                    total_current_weight += current_weight * mood_modifiers_mapping.get(current_mood, 1.0)
                    weights[current_mood] = total_current_weight
                    largest_mood, largest_weight = polarity_to_largest_mood_and_weight.get(current_polarity, (None,
                                                                                                              None))
                    if largest_mood is None:
                        polarity_to_largest_mood_and_weight[current_polarity] = (
                         current_mood, total_current_weight)
                if total_current_weight > largest_weight:
                    polarity_to_largest_mood_and_weight[current_polarity] = (
                     current_mood, total_current_weight)

        all_changeable_buffs = []
        for buff_polarity, changeable_buffs in polarity_to_changeable_buffs.items():
            largest_mood, largest_weight = polarity_to_largest_mood_and_weight.get(buff_polarity, (None,
                                                                                                   None))
            if largest_mood is not None:
                for buff_entry in changeable_buffs:
                    if buff_entry.mood_override is not largest_mood:
                        all_changeable_buffs.append((buff_entry, largest_mood))
                    largest_weight += buff_entry.mood_weight * mood_modifiers_mapping.get(largest_mood, 1.0)

                polarity_to_largest_mood_and_weight[buff_polarity] = (
                 largest_mood, largest_weight)
            else:
                weights = {}
                largest_weight = 0
                for buff_entry in changeable_buffs:
                    if buff_entry.mood_override is not None:
                        all_changeable_buffs.append((buff_entry, None))
                    current_mood = buff_entry.mood_type
                    current_weight = buff_entry.mood_weight
                    total_current_weight = weights.get(current_mood, 0)
                    total_current_weight += current_weight * mood_modifiers_mapping.get(current_mood, 1.0)
                    weights[current_mood] = total_current_weight
                    if total_current_weight > largest_weight:
                        largest_weight = total_current_weight
                        largest_mood = current_mood

            if largest_mood is not None and largest_weight != 0:
                polarity_to_largest_mood_and_weight[buff_polarity] = (
                 largest_mood, largest_weight)

        largest_weight = 0
        largest_mood = self.DEFAULT_MOOD
        active_mood = self._active_mood
        if polarity_to_largest_mood_and_weight:
            mood, weight = max((polarity_to_largest_mood_and_weight.values()), key=(operator.itemgetter(1)))
            if not weight > largest_weight:
                if weight == largest_weight:
                    if mood is active_mood:
                        largest_weight = weight
                        largest_mood = mood
        return (
         largest_mood, largest_weight, all_changeable_buffs)

    def _update_current_mood(self):
        largest_mood, largest_weight, changeable_buffs = self._get_largest_mood()
        if largest_mood is not None:
            intensity = self._get_intensity_from_mood(largest_mood, largest_weight)
            if self._should_update_mood(largest_mood, intensity, changeable_buffs):
                if self._active_mood_buff_handle is not None:
                    active_mood_buff_handle = self._active_mood_buff_handle
                    self.remove_buff(active_mood_buff_handle, update_mood=False)
                    if active_mood_buff_handle == self._active_mood_buff_handle:
                        self._active_mood_buff_handle = None
                    else:
                        return
                else:
                    old_mood = self._active_mood
                    self._active_mood = largest_mood
                    self._active_mood_intensity = intensity
                    if len(largest_mood.buffs) >= intensity:
                        tuned_buff = largest_mood.buffs[intensity]
                        if tuned_buff is not None:
                            if tuned_buff.buff_type is not None:
                                self._active_mood_buff_handle = self.add_buff((tuned_buff.buff_type), update_mood=False)
                    if gsi_handlers.buff_handlers.sim_mood_log_archiver.enabled:
                        if self.owner.valid_for_distribution and self.owner.visible_to_client == True:
                            gsi_handlers.buff_handlers.archive_mood_message(self.owner.id, self._active_mood, self._active_mood_intensity, self._active_buffs, changeable_buffs)
                caches.clear_all_caches()
                self.on_mood_changed(old_mood=old_mood, new_mood=(self._active_mood))
        for changeable_buff, mood_override in changeable_buffs:
            changeable_buff.mood_override = mood_override
            self.send_buff_update_msg(changeable_buff, BuffUpdateType.UPDATE)

    def _get_intensity_from_mood(self, mood, weight):
        intensity = 0
        for threshold in mood.intensity_thresholds:
            if weight >= threshold:
                intensity += 1
            else:
                break

        if intensity < 0:
            fallback_intensity = max(len(mood.intensity_thresholds) - 1, 0)
            logger.error('Intensity became {} for {}, weight: {}. Setting to {}', intensity, mood, weight, fallback_intensity)
            intensity = fallback_intensity
        return intensity

    def _should_update_mood(self, mood, intensity, changeable_buffs):
        active_mood = self._active_mood
        active_mood_intensity = self._active_mood_intensity
        if mood is active_mood:
            return intensity != active_mood_intensity
        total_weight = sum((buff_entry.mood_weight for buff_entry in self._active_buffs.values() if buff_entry.mood_type is active_mood))
        active_mood_intensity = self._get_intensity_from_mood(active_mood, total_weight)
        if changeable_buffs:
            if not self._active_mood.is_changeable:
                buffs_to_ignore = [changeable_buff for changeable_buff, _ in changeable_buffs]
                largest_mood, largest_weight, _ = self._get_largest_mood(buffs_to_ignore=buffs_to_ignore)
                new_intensity = self._get_intensity_from_mood(largest_mood, largest_weight)
                if self._should_update_mood(largest_mood, new_intensity, None):
                    active_mood = largest_mood
                    active_mood_intensity = new_intensity
        if active_mood.is_changeable:
            if mood.buff_polarity == active_mood.buff_polarity:
                return True
        if not intensity or intensity < active_mood_intensity:
            return True
        if intensity >= active_mood_intensity + self.UPDATE_INTENSITY_BUFFER:
            return True
        if mood is self.DEFAULT_MOOD or active_mood is self.DEFAULT_MOOD:
            return True
        return False

    def on_zone_load(self):
        if services.game_services.service_manager.is_traveling:
            self._active_mood = self.DEFAULT_MOOD
            self._active_mood_intensity = 0
            self._active_mood_buff_handle = None

    def on_zone_unload(self):
        if not services.game_services.service_manager.is_traveling:
            return
        self._remove_non_persist_buffs()

    def remove_all_buffs_with_temporary_commodities(self):
        buff_types_to_remove = set()
        for buff_type, buff in self._active_buffs.items():
            if buff.has_temporary_commodity:
                buff_types_to_remove.add(buff_type)

        if buff_types_to_remove:
            for buff_type in buff_types_to_remove:
                self.remove_buff_by_type(buff_type)

    def _remove_non_persist_buffs(self):
        buff_types_to_remove = set()
        for buff_type, buff in self._active_buffs.items():
            if not buff.commodity is None:
                if buff.commodity.persisted or buff._remove_on_zone_unload:
                    buff_types_to_remove.add(buff_type)

        if buff_types_to_remove:
            for buff_type in buff_types_to_remove:
                self.remove_buff_by_type(buff_type, True)

            self.update_affordance_caches()

    def on_lod_update(self, old_lod, new_lod):
        if new_lod <= old_lod:
            return
        sim = self.owner.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if sim is None:
            if new_lod != SimInfoLODLevel.ACTIVE:
                logger.warn('{} is increasing LOD while not instanced', self.owner)
            return
        for buff_entry in tuple(self._active_buffs.values()):
            buff_entry.on_lod_increase(sim, old_lod, new_lod)


def _update_buffs_with_exclusive_data(buff_manager):
    for index, exclusive_set in enumerate(BuffComponent.EXCLUSIVE_SET):
        for buff_type_data in exclusive_set:
            buff_type = buff_type_data.buff_type
            buff_type.exclusive_index = index
            buff_type.exclusive_weight = buff_type_data.weight


if not sims4.reload.currently_reloading:
    services.get_instance_manager(sims4.resources.Types.BUFF).add_on_load_complete(_update_buffs_with_exclusive_data)

class BuffPickerSuperInteraction(PickerSuperInteraction):

    class BuffHandlingType(enum.IntFlags):
        HIDE = 1
        SELECT = 2
        DISABLE = 4

    INSTANCE_TUNABLES = {'picker_dialog':TunablePickerDialogVariant(description='\n            The item picker dialog.\n            ',
       available_picker_flags=ObjectPickerTuningFlags.ITEM | ObjectPickerTuningFlags.OBJECT,
       tuning_group=GroupNames.PICKERTUNING), 
     'is_add':Tunable(description='\n            If this interaction is trying to add a buff to the targets\n            or to remove a buff from the target sim.\n            Remove is single target only.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PICKERTUNING), 
     'subject':TunableEnumFlags(description='\n            From whom the buffs should be added/removed.\n            ',
       enum_type=ParticipantTypeSim,
       default=ParticipantTypeSim.TargetSim,
       tuning_group=GroupNames.PICKERTUNING), 
     'handle_existing':TunableEnumFlags(description="\n            How buffs that already exist should be handled.\n            Hide = Doesn't show up\n            Select = Selected by default\n            Disable = Disabled by default\n            \n            Only works if single target\n            ",
       enum_type=BuffHandlingType,
       default=BuffHandlingType.HIDE,
       tuning_group=GroupNames.PICKERTUNING), 
     'handle_invalid':TunableEnumFlags(description="\n            How buffs that can't be added should be handled.\n            Hide = Doesn't show up\n            Select = Selected by default\n            Disable = Disabled by default\n            \n            Only works if single target\n            ",
       enum_type=BuffHandlingType,
       default=BuffHandlingType.DISABLE,
       tuning_group=GroupNames.PICKERTUNING), 
     'buffs':TunableList(description='\n            The list of buffs available to select.  If empty will try all.\n            ',
       tunable=TunableTuple(buff=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
       pack_safe=True),
       buff_name=TunableLocalizedStringFactory(allow_none=True),
       buff_description=TunableLocalizedString(allow_none=True),
       buff_icon=TunableResourceKey(default=None,
       resource_types=(sims4.resources.CompoundTypes.IMAGE))),
       tuning_group=GroupNames.PICKERTUNING), 
     'reason':OptionalTunable(description='\n            If set, specify a reason why the buff(s) were added.\n            ',
       tunable=TunableLocalizedString(description='\n                The reason the buffs were added. This will be displayed in the\n                buff tooltip.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'disabled_row_tooltip':OptionalTunable(description='\n            If set, specify a tooltip to indicate why the row is disabled\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                The reason the row is disabled. This will be displayed as the \n                rows tooltip.\n                '),
       tuning_group=GroupNames.PICKERTUNING), 
     'continuations':TunableList(description='\n            List of continuations to push if a buff is actually selected.\n            ',
       tunable=TunableContinuation(),
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @classmethod
    def _buff_type_selection_gen--- This code section failed: ---

 L.1666         0  LOAD_FAST                'cls'
                2  LOAD_ATTR                is_add
                4  POP_JUMP_IF_FALSE   110  'to 110'

 L.1667         6  LOAD_FAST                'cls'
                8  LOAD_ATTR                buffs
               10  POP_JUMP_IF_FALSE    52  'to 52'

 L.1668        12  SETUP_LOOP          108  'to 108'
               14  LOAD_FAST                'cls'
               16  LOAD_ATTR                buffs
               18  GET_ITER         
               20  FOR_ITER             48  'to 48'
               22  STORE_FAST               'buff_info'

 L.1669        24  LOAD_FAST                'buff_info'
               26  LOAD_ATTR                buff
               28  LOAD_FAST                'buff_info'
               30  LOAD_ATTR                buff_name
               32  LOAD_FAST                'buff_info'
               34  LOAD_ATTR                buff_icon
               36  LOAD_FAST                'buff_info'
               38  LOAD_ATTR                buff_description
               40  BUILD_TUPLE_4         4 
               42  YIELD_VALUE      
               44  POP_TOP          
               46  JUMP_BACK            20  'to 20'
               48  POP_BLOCK        
               50  JUMP_ABSOLUTE       148  'to 148'
             52_0  COME_FROM            10  '10'

 L.1671        52  LOAD_GLOBAL              services
               54  LOAD_METHOD              get_instance_manager
               56  LOAD_GLOBAL              sims4
               58  LOAD_ATTR                resources
               60  LOAD_ATTR                Types
               62  LOAD_ATTR                BUFF
               64  CALL_METHOD_1         1  '1 positional argument'
               66  STORE_FAST               'buff_manager'

 L.1672        68  SETUP_LOOP          148  'to 148'
               70  LOAD_FAST                'buff_manager'
               72  LOAD_ATTR                types
               74  LOAD_METHOD              values
               76  CALL_METHOD_0         0  '0 positional arguments'
               78  GET_ITER         
               80  FOR_ITER            106  'to 106'
               82  STORE_FAST               'buff_type'

 L.1673        84  LOAD_FAST                'buff_type'
               86  LOAD_FAST                'buff_type'
               88  LOAD_ATTR                buff_name
               90  LOAD_FAST                'buff_type'
               92  LOAD_ATTR                icon
               94  LOAD_FAST                'buff_type'
               96  LOAD_ATTR                buff_description
               98  BUILD_TUPLE_4         4 
              100  YIELD_VALUE      
              102  POP_TOP          
              104  JUMP_BACK            80  'to 80'
              106  POP_BLOCK        
            108_0  COME_FROM_LOOP       68  '68'
            108_1  COME_FROM_LOOP       12  '12'
              108  JUMP_FORWARD        148  'to 148'
            110_0  COME_FROM             4  '4'

 L.1675       110  SETUP_LOOP          148  'to 148'
              112  LOAD_FAST                'target'
              114  LOAD_METHOD              get_active_buff_types
              116  CALL_METHOD_0         0  '0 positional arguments'
              118  GET_ITER         
              120  FOR_ITER            146  'to 146'
              122  STORE_FAST               'buff_type'

 L.1676       124  LOAD_FAST                'buff_type'
              126  LOAD_FAST                'buff_type'
              128  LOAD_ATTR                buff_name
              130  LOAD_FAST                'buff_type'
              132  LOAD_ATTR                icon
              134  LOAD_FAST                'buff_type'
              136  LOAD_ATTR                buff_description
              138  BUILD_TUPLE_4         4 
              140  YIELD_VALUE      
              142  POP_TOP          
              144  JUMP_BACK           120  'to 120'
              146  POP_BLOCK        
            148_0  COME_FROM_LOOP      110  '110'
            148_1  COME_FROM           108  '108'

Parse error at or near `COME_FROM_LOOP' instruction at offset 108_1

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        target = target if target is not DEFAULT else inst.target
        context = context if context is not DEFAULT else inst.context
        participants = inst_or_cls.get_participants((inst_or_cls.subject), sim=(context.sim), target=target)
        if not participants:
            return
        single_sim = len(participants) == 1
        if not single_sim:
            if not inst_or_cls.is_add:
                logger.error('{} is trying to do a remove buff picker with multiple subjects', self)
        target = participants[0]
        for buff_type, name, icon, description in inst_or_cls._buff_type_selection_gen(target):
            is_enable = True
            is_selected = False
            row_tooltip = None
            if inst_or_cls.is_add and single_sim:
                if target.has_buff(buff_type):
                    if inst_or_cls.handle_existing & BuffPickerSuperInteraction.BuffHandlingType.HIDE:
                        continue
                    if inst_or_cls.handle_existing & BuffPickerSuperInteraction.BuffHandlingType.SELECT:
                        is_selected = True
                    if inst_or_cls.handle_existing & BuffPickerSuperInteraction.BuffHandlingType.DISABLE:
                        is_enable = False
                if not buff_type.can_add(target.sim_info):
                    if inst_or_cls.handle_invalid & BuffPickerSuperInteraction.BuffHandlingType.HIDE:
                        continue
                    if inst_or_cls.handle_invalid & BuffPickerSuperInteraction.BuffHandlingType.SELECT:
                        is_selected = True
                    if inst_or_cls.handle_invalid & BuffPickerSuperInteraction.BuffHandlingType.DISABLE:
                        is_enable = False
            if not is_enable:
                row_tooltip = inst_or_cls.disabled_row_tooltip
            elif inst_or_cls.picker_dialog.factory == UiObjectPicker:
                row = ObjectPickerRow(is_enable=is_enable, name=(name(target.sim_info)),
                  icon=icon,
                  tag=buff_type,
                  row_description=description,
                  row_tooltip=row_tooltip,
                  is_selected=is_selected,
                  tag_list=(buff_type.tags))
            else:
                row = BasePickerRow(is_enable=is_enable, name=(name(target.sim_info)),
                  icon=icon,
                  tag=buff_type,
                  row_description=description,
                  row_tooltip=row_tooltip,
                  is_selected=is_selected)
            yield row

    def _on_buff_picker_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is None:
            return
        for participant in self.get_participants(self.subject):
            if self.is_add:
                participant.add_buff_from_op(choice_tag, buff_reason=(self.reason))
            else:
                participant.remove_buff_by_type(choice_tag)

    def on_choice_selected(self, choice_tag, **kwargs):
        (self._on_buff_picker_choice_selected)(choice_tag, **kwargs)
        if choice_tag is None:
            return
        for continuation in self.continuations:
            self.push_tunable_continuation(continuation)

    def on_multi_choice_selected(self, choice_tags, **kwargs):
        if not choice_tags:
            return
        for tag in choice_tags:
            (self._on_buff_picker_choice_selected)(tag, **kwargs)

        for continuation in self.continuations:
            self.push_tunable_continuation(continuation)