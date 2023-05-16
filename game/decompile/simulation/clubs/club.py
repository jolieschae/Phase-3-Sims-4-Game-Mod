# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club.py
# Compiled at: 2020-04-27 17:15:29
# Size of source mod 2**32: 49808 bytes
from collections import namedtuple
import random
from protocolbuffers.Localization_pb2 import LocalizedStringToken
from bucks.club_bucks_tracker import ClubBucksTracker
from cas.cas import get_caspart_bodytype
from clubs import club_tuning
from clubs.club_enums import ClubGatheringStartSource, ClubHangoutSetting, ClubOutfitSetting
from clubs.club_telemetry import club_telemetry_writer, TELEMETRY_HOOK_CLUB_JOIN, TELEMETRY_HOOK_CLUB_QUIT, TELEMETRY_FIELD_CLUB_ID
from clubs.club_tuning import ClubTunables
from date_and_time import create_time_span
from distributor.rollback import ProtocolBufferRollback
from distributor.shared_messages import IconInfoData
from event_testing import test_events
from event_testing.resolver import SingleSimResolver, DoubleSimResolver
from event_testing.test_events import TestEvent
from interactions import ParticipantType
from services.persistence_service import save_unlock_callback
from sims.outfits.outfit_enums import CLOTHING_BODY_TYPES, OutfitCategory
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from sims.sim_info_types import Age, Gender
from sims.sim_info_utils import sim_info_auto_finder
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.tunable import TunablePackSafeReference
from singletons import DEFAULT
from world.region import get_region_instance_from_zone_id
import bucks, build_buy, gsi_handlers, services, sims4, telemetry_helper
logger = sims4.log.Logger('Clubs', default_owner='tastle')
ClubCommodityData = namedtuple('ClubCommodityData', ('static_commodity', 'desire'))

class Club:
    CLUB_JOINED_DRAMA_NODE = TunablePackSafeReference(description='\n        The drama node that will be scheduled when a Sim is added to a club.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.DRAMA_NODE)))

    def __init__(self, club_id, name, icon, description, encouragement_commodity, discouragement_commodity, encouragement_buff, discouragement_buff, social_encouragement_buff, leader=None, leader_id=None, member_ids=None, recent_member_ids=None, membership_criteria=None, rules=None, hangout_setting=ClubHangoutSetting.HANGOUT_NONE, hangout_venue=None, hangout_zone_id=0, invite_only=False, associated_color=None, associated_style=None, uniform_male_child=None, uniform_female_child=None, uniform_male_adult=None, uniform_female_adult=None, club_seed=None, bucks_tracker_data=None, male_adult_mannequin=None, male_child_mannequin=None, female_adult_mannequin=None, female_child_mannequin=None, outfit_setting=ClubOutfitSetting.NO_OUTFIT):
        self._name = name
        self._localized_custom_name = None
        self._description = description
        self._localized_custom_description = None
        self.club_id = club_id
        self.icon = icon
        self.leader = leader
        self.leader_id = leader_id
        self.members = []
        self.club_joined_drama_node_ids = []
        self._recent_member_ids = set(recent_member_ids) if recent_member_ids is not None else set()
        self.member_ids = member_ids
        self.encouragement_commodity = encouragement_commodity
        self.discouragement_commodity = discouragement_commodity
        self.encouragement_buff = encouragement_buff
        self.discouragement_buff = discouragement_buff
        self.social_encouragement_buff = social_encouragement_buff
        self.membership_criteria = []
        self.rules = []
        self.invite_only = invite_only
        self.set_associated_color(associated_color, distribute=False)
        self.set_associated_style(associated_style, distribute=False)
        self.uniform_male_child = uniform_male_child
        self.uniform_female_child = uniform_female_child
        self.uniform_male_adult = uniform_male_adult
        self.uniform_female_adult = uniform_female_adult
        self.club_seed = club_seed
        self.bucks_tracker = ClubBucksTracker(self)
        self._bucks_tracker_data = bucks_tracker_data
        self.male_adult_mannequin = male_adult_mannequin
        self.male_child_mannequin = male_child_mannequin
        self.female_adult_mannequin = female_adult_mannequin
        self.female_child_mannequin = female_child_mannequin
        self.outfit_setting = outfit_setting
        self.hangout_setting = hangout_setting
        self.hangout_venue = hangout_venue
        self.hangout_zone_id = hangout_zone_id
        self._gathering_auto_spawning_schedule = None
        self._gathering_end_time = None
        for criteria in membership_criteria:
            self.add_membership_criteria(criteria)

        for rule in rules:
            self.add_rule(rule)

    def __str__(self):
        name = ''
        if self._name is not None:
            name = self._name
        else:
            if self.club_seed is not None:
                name = self.club_seed.__name__
        return name + '_' + str(self.club_id)

    @property
    def name(self):
        if self._name is not None:
            if self._localized_custom_name is None:
                self._localized_custom_name = LocalizationHelperTuning.get_raw_text(self._name)
        if self._localized_custom_name is not None:
            return self._localized_custom_name
        if self.club_seed is not None:
            return self.club_seed.name
        return LocalizationHelperTuning.get_raw_text('')

    @name.setter
    def name(self, value):
        self._name = value
        self._localized_custom_name = None

    @property
    def description(self):
        if self._description is not None:
            if self._localized_custom_description is None:
                self._localized_custom_description = LocalizationHelperTuning.get_raw_text(self._description)
        return self._localized_custom_description or self.club_seed.description

    @description.setter
    def description(self, value):
        self._description = value
        self._localized_custom_description = None

    @property
    def id(self):
        return self.club_id

    def set_associated_color(self, color, distribute=True):
        self.associated_color = color
        if distribute:
            self.outfit_setting = ClubOutfitSetting.COLOR
            services.get_club_service().distribute_club_update((self,))

    def set_associated_style(self, style, distribute=True):
        self.associated_style = style
        if distribute:
            self.outfit_setting = ClubOutfitSetting.STYLE
            services.get_club_service().distribute_club_update((self,))

    def set_outfit_setting(self, setting, distribute=True):
        if self.outfit_setting != ClubOutfitSetting.NO_OUTFIT:
            if setting == ClubOutfitSetting.NO_OUTFIT:
                club_service = services.get_club_service()
                if club_service is not None:
                    gathering = club_service.clubs_to_gatherings_map.get(self)
                    if gathering is not None:
                        gathering.remove_all_club_outfits()
        self.outfit_setting = setting
        if distribute:
            services.get_club_service().distribute_club_update((self,))

    def member_should_spin_into_club_outfit(self, sim_info):
        for buff in ClubTunables.PROHIBIT_CLUB_OUTFIT_BUFFS:
            if sim_info.has_buff(buff):
                return False

        current_outfit = sim_info.get_current_outfit()
        if current_outfit[0] == OutfitCategory.BATHING:
            return False
        if self.outfit_setting == ClubOutfitSetting.OVERRIDE:
            return self.club_uniform_exists_for_category(sim_info, current_outfit[0])
        if self.outfit_setting == ClubOutfitSetting.NO_OUTFIT:
            return False
        if self.outfit_setting == ClubOutfitSetting.STYLE:
            if self.associated_style is None:
                return False
        return True

    def disband(self):
        services.get_club_service().remove_club(self)

    def is_zone_valid_for_gathering(self, zone_id):
        persistence_service = services.get_persistence_service()
        household_manager = services.household_manager()
        try:
            venue_tuning_id = build_buy.get_current_venue(zone_id)
        except RuntimeError:
            return False
        else:
            venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
            venue_tuning = venue_manager.get(venue_tuning_id)
            if venue_tuning is None:
                return False
            else:
                if not venue_tuning.allowed_for_clubs:
                    return False
                if venue_tuning.is_residential or venue_tuning.is_university_housing:
                    zone_data = persistence_service.get_zone_proto_buff(zone_id)
                    if zone_data is None:
                        return False
                    lot_data = persistence_service.get_lot_data_from_zone_data(zone_data)
                    if lot_data is None:
                        return False
                    household = household_manager.get(lot_data.lot_owner[0].household_id) if lot_data.lot_owner else None
                    if household is None:
                        return False
                    if not any((club_member in self.members for club_member in household)):
                        return False
            return True

    def get_hangout_zone_id(self, prefer_current=False):
        if self.hangout_setting == ClubHangoutSetting.HANGOUT_NONE:
            return 0
        if self.hangout_setting == ClubHangoutSetting.HANGOUT_VENUE:
            current_region = services.current_region()

            def is_valid_zone_id(zone_id):
                if not self.is_zone_valid_for_gathering(zone_id):
                    return False
                else:
                    zone_region = get_region_instance_from_zone_id(zone_id)
                    if zone_region is None:
                        return False
                    return current_region.is_region_compatible(zone_region) or False
                return True

            venue_service = services.venue_service()
            available_zone_ids = tuple(filter(is_valid_zone_id, venue_service.get_zones_for_venue_type_gen(self.hangout_venue)))
            for venue in self.hangout_venue.included_venues_for_club_gathering:
                included_zone_ids = tuple(filter(is_valid_zone_id, venue_service.get_zones_for_venue_type_gen(venue)))
                available_zone_ids += included_zone_ids

            if not available_zone_ids:
                return 0
            if prefer_current:
                current_zone_id = services.current_zone_id()
                if current_zone_id in available_zone_ids:
                    return current_zone_id
            return random.choice(available_zone_ids)
        return self.hangout_zone_id

    @save_unlock_callback
    def show_club_gathering_dialog(self, sim_info, *, flavor_text, start_source=ClubGatheringStartSource.DEFAULT, sender_sim_info=DEFAULT):
        zone_id = self.get_hangout_zone_id()
        if not zone_id:
            return False
        else:
            current_region = services.current_region()
            hangout_region = get_region_instance_from_zone_id(zone_id)
            return current_region.is_region_compatible(hangout_region) or False
        venue_manager = services.get_instance_manager(sims4.resources.Types.VENUE)
        venue_tuning = venue_manager.get(build_buy.get_current_venue(zone_id))

        def on_response(dialog):
            if not dialog.accepted:
                return
            persistence_service = services.get_persistence_service()
            if persistence_service.is_save_locked():
                return
            club_service = services.get_club_service()
            if club_service is None:
                return
            club_service.start_gathering(self, start_source=start_source, host_sim_id=(sim_info.sim_id), invited_sims=(
             sim_info,),
              zone_id=zone_id,
              spawn_sims_during_zone_spin_up=True)

        zone_data = services.get_persistence_service().get_zone_proto_buff(zone_id)
        lot_name = zone_data.name
        sender_sim_info = self.leader if sender_sim_info is DEFAULT else sender_sim_info
        flavor_text = flavor_text(sim_info, sender_sim_info, self)
        additional_tokens = (lot_name, venue_tuning.club_gathering_text(), flavor_text)
        self.show_club_notification(sim_info, (ClubTunables.CLUB_GATHERING_DIALOG), target_sim_id=(sender_sim_info.sim_id),
          additional_tokens=additional_tokens,
          on_response=on_response)

    def show_club_notification(self, sim_info, notification_type, target_sim_id=None, additional_tokens=(), on_response=None):
        notification = notification_type(sim_info, resolver=(DoubleSimResolver(sim_info, self.leader)), target_sim_id=target_sim_id)
        notification.show_dialog(additional_tokens=((self.name,) + tuple(additional_tokens)), icon_override=IconInfoData(icon_resource=(self.icon)),
          on_response=on_response)

    def is_gathering_auto_start_available(self):
        if self._gathering_end_time is not None:
            if self._gathering_end_time + create_time_span(minutes=(ClubTunables.CLUB_GATHERING_AUTO_START_COOLDOWN)) > services.time_service().sim_now:
                return False
        return True

    def get_gathering(self):
        club_service = services.get_club_service()
        if club_service is None:
            return
        return club_service.clubs_to_gatherings_map.get(self)

    def get_member_cap(self):
        cap = services.get_club_service().default_member_cap
        for perk, increase in club_tuning.ClubTunables.CLUB_MEMBER_CAPACITY_INCREASES.items():
            if self.bucks_tracker.is_perk_unlocked(perk):
                cap += increase

        return cap

    def get_leader_score_for_sim_info(self, sim_info, prioritize_npcs=True):
        if sim_info not in self.members:
            logger.error("Club {} attempting to compute leader score for SimInfo {} but they aren't a member.", self, sim_info)
            return
        if prioritize_npcs:
            selectable_sim_score = 0
            npc_sim_score = 1
        else:
            selectable_sim_score = 1
            npc_sim_score = 0
        if sim_info.is_selectable:
            return selectable_sim_score
        return npc_sim_score

    def reassign_leader(self, new_leader=None, prioritize_npcs=True, distribute=True):
        if new_leader not in self.members:
            new_leader = None
        if new_leader is None:
            new_leader = self._find_best_leader(prioritize_npcs=prioritize_npcs)
        if new_leader is None:
            self.disband()
            return
        if new_leader is self.leader:
            return
        self.leader = new_leader
        if distribute:
            services.get_club_service().distribute_club_update((self,))
        services.get_event_manager().process_event((TestEvent.LeaderAssigned), sim_info=(self.leader), associated_clubs=(self,))

    def _find_best_leader(self, *, prioritize_npcs):
        if not self.members:
            return
        return max((self.members), key=(lambda member: self.get_leader_score_for_sim_info(member, prioritize_npcs=prioritize_npcs)))

    @sim_info_auto_finder
    def _get_member_sim_infos(self):
        return self.member_ids

    def can_sim_info_join(self, new_sim_info):
        if new_sim_info in self.members:
            return False
        else:
            if len(self.members) >= self.get_member_cap():
                return False
            else:
                club_service = services.get_club_service()
                return club_service.can_sim_info_join_more_clubs(new_sim_info) or False
            return self.validate_sim_info(new_sim_info) or False
        return True

    def add_member(self, member, distribute=True):
        if member is None:
            logger.error('Attempting to add a None member to club {}.', self)
            return False
        else:
            if not member.can_instantiate_sim:
                return False
            else:
                if member in self.members:
                    logger.error('Attempting to add {} as a member to club {} but they are already a member.', member, self)
                    return False
                self.validate_sim_info(member) or logger.error("Attempting to add {} as a member to club {} but they don't pass all the membership criteria.", member, self)
                return False
            if len(self.members) >= self.get_member_cap():
                logger.error("Attempting to add {} as a member to club {} but it's already at the maximum number of allowed members.", member, self)
                return False
            club_service = services.get_club_service()
            club_service.can_sim_info_join_more_clubs(member) or logger.error("Attempting to add {} as a member to club {} but they've already joined the maximum number of allowed Clubs.", member, self)
            return False
        club_rule_mapping = club_service.club_rule_mapping
        for rule in self.rules:
            for affordance in rule.action():
                club_rule_mapping[member][affordance].add(rule)

        club_service._sim_infos_to_clubs_map[member].add(self)
        self.members.append(member)
        for buff in club_tuning.ClubTunables.BUFFS_NOT_IN_ANY_CLUB:
            member.remove_buff_by_type(buff)

        club_service.reset_sim_info_interaction_club_rewards_cache(sim_info=member)
        if distribute:
            club_service.distribute_club_update((self,))
        zone = services.current_zone()
        if zone.is_zone_running:
            self._recent_member_ids.add(member.sim_id)
            sim = member.get_sim_instance()
            if sim is not None:
                for group in sim.get_groups_for_sim_gen():
                    club_service.on_sim_added_to_social_group(sim, group)

            for other_member in self.members:
                if member is other_member:
                    continue
                resolver = DoubleSimResolver(member, other_member)
                ClubTunables.CLUB_MEMBER_LOOT.apply_to_resolver(resolver)

            with telemetry_helper.begin_hook(club_telemetry_writer, TELEMETRY_HOOK_CLUB_JOIN, sim_info=member) as (hook):
                hook.write_int(TELEMETRY_FIELD_CLUB_ID, self.id)
            if member.is_selectable:
                if member is not self.leader:
                    self.show_club_notification(member, ClubTunables.CLUB_NOTIFICATION_JOIN)
                    if self not in club_service.clubs_to_gatherings_map:
                        self.show_club_gathering_dialog(member, flavor_text=(ClubTunables.CLUB_GATHERING_DIALOG_TEXT_JOIN))
            services.get_event_manager().process_event((TestEvent.ClubMemberAdded), sim_info=member,
              associated_clubs=(
             self,))
            services.get_event_manager().process_event((TestEvent.ClubMemberAdded), sim_info=(self.leader),
              associate_clubs=(
             self,))
            if self.CLUB_JOINED_DRAMA_NODE is not None:
                if member is not self.leader:
                    additional_participants = {ParticipantType.AssociatedClub: (self,), 
                     ParticipantType.AssociatedClubLeader: (self.leader,)}
                    additional_localization_tokens = (self,)
                    resolver = SingleSimResolver(member, additional_participants, additional_localization_tokens)
                    node_id = services.drama_scheduler_service().schedule_node(self.CLUB_JOINED_DRAMA_NODE, resolver)
                    if node_id is not None:
                        self.club_joined_drama_node_ids.append(node_id)
            self.bucks_tracker.award_unlocked_perks(ClubTunables.CLUB_BUCKS_TYPE, member)
        return True

    def remove_member(self, member, distribute=True, can_reassign_leader=True, from_stop=False):
        if member not in self.members:
            logger.error("Attempting to remove {} from club {} but they aren't a member.", member, self)
            return
            club_service = services.get_club_service()
            club_rule_mapping = club_service.club_rule_mapping
            for rule in self.rules:
                for affordance in rule.action():
                    club_rule_mapping[member][affordance].remove(rule)
                    if not club_rule_mapping[member][affordance]:
                        del club_rule_mapping[member][affordance]

                if not club_rule_mapping[member]:
                    del club_rule_mapping[member]

            club_service._sim_infos_to_clubs_map[member].remove(self)
            if not club_service._sim_infos_to_clubs_map[member]:
                del club_service._sim_infos_to_clubs_map[member]
                if not from_stop:
                    for buff in club_tuning.ClubTunables.BUFFS_NOT_IN_ANY_CLUB:
                        member.add_buff(buff.buff_type)

        else:
            member_instance = member.get_sim_instance()
            current_gathering = club_service.sims_to_gatherings_map.get(member_instance)
            if current_gathering is not None:
                if current_gathering.associated_club is self:
                    current_gathering.remove_sim_from_situation(member_instance)
            self.members.remove(member)
            self._recent_member_ids.discard(member.sim_id)
            if member is self.leader:
                self.leader = None
                if can_reassign_leader:
                    self.reassign_leader(prioritize_npcs=(not member.is_selectable), distribute=distribute)
        club_service.reset_sim_info_interaction_club_rewards_cache(sim_info=member)
        if distribute:
            club_service.distribute_club_update((self,))
        zone = services.current_zone()
        if zone.is_zone_running:
            self.validate_club_hangout()
            with telemetry_helper.begin_hook(club_telemetry_writer, TELEMETRY_HOOK_CLUB_QUIT, sim_info=member) as (hook):
                hook.write_int(TELEMETRY_FIELD_CLUB_ID, self.id)
            services.get_event_manager().process_event((TestEvent.ClubMemberRemoved), sim_info=member, associated_clubs=(self,))

    def start_club_effects(self, member):
        member.add_buff((self.encouragement_buff), additional_static_commodities_to_add=(self.encouragement_commodity,))
        member.add_buff((self.discouragement_buff), additional_static_commodities_to_add=(self.discouragement_commodity,))
        member.add_buff(self.social_encouragement_buff)

    def stop_club_effects(self, member):
        member.remove_buff_by_type(self.encouragement_buff)
        member.remove_buff_by_type(self.discouragement_buff)
        member.remove_buff_by_type(self.social_encouragement_buff)

    def _validate_members(self, update_if_invalid=False):
        global_result = True
        for member in list(self.members):
            result = self.validate_sim_info(member, update_if_invalid=update_if_invalid)
            if global_result:
                global_result = result or False

        return global_result

    def validate_sim_info(self, sim_info, update_if_invalid=False):
        if not sim_info.is_human:
            return False
        for criteria in self.membership_criteria:
            result = self._validate_member_against_criteria(sim_info, criteria, update_if_invalid=update_if_invalid)
            if not result:
                return False

        return True

    def _validate_member_against_criteria(self, member, criteria, update_if_invalid=False):
        result = criteria.test_sim_info(member)
        if not result:
            if update_if_invalid:
                self.remove_member(member)
        return result

    def add_membership_criteria(self, criteria):
        for member in self.members:
            self._validate_member_against_criteria(member, criteria, update_if_invalid=True)

        self.membership_criteria.append(criteria)

    def remove_membership_criteria(self, criteria):
        if criteria not in self.membership_criteria:
            logger.error('Attempting to remove Membership Criteria {} from club {} but it was never added.', criteria, self)
            return
        self.membership_criteria.remove(criteria)

    def add_rule(self, rule):
        if rule.action is None:
            return
        else:
            club_service = services.get_club_service()
            club_rule_mapping = club_service.club_rule_mapping
            for member in self.members:
                for affordance in rule.action():
                    club_rule_mapping[member][affordance].add(rule)

            if rule.is_encouraged:
                static_commodity_data = ClubCommodityData(self.encouragement_commodity, 1)
            else:
                static_commodity_data = ClubCommodityData(self.discouragement_commodity, 1)
        for affordance in rule.action():
            affordance.add_additional_static_commodity_data(static_commodity_data)
            club_service.affordance_dirty_cache.add(affordance)

        rule.register_club(self)
        club_service.on_rule_added(rule)
        self.rules.append(rule)

    def remove_rule(self, rule):
        club_service = services.get_club_service()
        club_rule_mapping = club_service.club_rule_mapping
        for member in self.members:
            for affordance in rule.action():
                club_rule_mapping[member][affordance].remove(rule)
                if not club_rule_mapping[member][affordance]:
                    del club_rule_mapping[member][affordance]

            if not club_rule_mapping[member]:
                del club_rule_mapping[member]

        if rule.is_encouraged:
            static_commodity_data = ClubCommodityData(self.encouragement_commodity, 1)
        else:
            static_commodity_data = ClubCommodityData(self.discouragement_commodity, 1)
        for affordance in rule.action():
            affordance.remove_additional_static_commodity_data(static_commodity_data)
            club_service.affordance_dirty_cache.add(affordance)

        club_service.on_rule_removed(rule)
        self.rules.remove(rule)

    def is_gathering_auto_spawning_available(self):
        if self._gathering_auto_spawning_schedule is None:
            r = random.Random(self.club_id)
            schedule = r.choice(ClubTunables.CLUB_GATHERING_AUTO_START_SCHEDULES)
            self._gathering_auto_spawning_schedule = schedule(init_only=True)
        current_time = services.time_service().sim_now
        return self._gathering_auto_spawning_schedule.is_scheduled_time(current_time)

    def is_recent_member(self, sim_info):
        return sim_info.sim_id in self._recent_member_ids

    def get_club_outfit_parts(self, sim_info, outfit_category_and_index=(0, 0)):
        if outfit_category_and_index[0] == OutfitCategory.BATHING:
            return ((), ())
        to_add = ()
        to_remove = ()
        if self.outfit_setting == ClubOutfitSetting.STYLE and self.associated_style is not None:
            to_add, to_remove = sim_info.generate_club_outfit(list((self.associated_style,)), outfit_category_and_index, 1)
        else:
            if self.outfit_setting == ClubOutfitSetting.COLOR and self.associated_color is not None:
                to_add, to_remove = sim_info.generate_club_outfit(list((self.associated_color,)), outfit_category_and_index, 0)
            else:
                if self.outfit_setting == ClubOutfitSetting.OVERRIDE:
                    to_add, to_remove = self.get_cas_parts_from_mannequin_data(sim_info, outfit_category_and_index)
        return (
         to_add, to_remove)

    def get_cas_parts_from_mannequin_data(self, sim_info, outfit_category_and_index):
        to_add = []
        to_remove = []
        mannequin_data = self.get_club_uniform_data(sim_info.age, sim_info.clothing_preference_gender)
        random_outfit = mannequin_data.get_random_outfit(outfit_categories=(outfit_category_and_index[0],))
        if random_outfit[0] == outfit_category_and_index[0]:
            if mannequin_data.has_outfit(random_outfit):
                outfit_data = (mannequin_data.get_outfit)(*random_outfit)
                to_add.extend((part_id for part_id in outfit_data.part_ids if get_caspart_bodytype(part_id) in CLOTHING_BODY_TYPES))
        if to_add:
            for outfit in sim_info.get_outfits_in_category(outfit_category_and_index[0]):
                for part in outfit.part_ids:
                    body_type = get_caspart_bodytype(part)
                    if body_type in CLOTHING_BODY_TYPES and body_type not in outfit_data.body_types:
                        to_remove.append(part)

                break

        return (
         to_add, to_remove)

    def club_uniform_exists_for_category(self, sim_info, category):
        mannequin_data = self.get_club_uniform_data(sim_info.age, sim_info.clothing_preference_gender)
        return mannequin_data.has_outfit((category, 0))

    def on_remove(self, from_stop=False):
        for member in list(self.members):
            self.remove_member(member, distribute=False, can_reassign_leader=False, from_stop=from_stop)

        for criteria in list(self.membership_criteria):
            self.remove_membership_criteria(criteria)

        for rule in list(self.rules):
            self.remove_rule(rule)

        if not from_stop:
            services.get_club_service().update_affordance_cache()
        for drama_node_id in self.club_joined_drama_node_ids:
            services.drama_scheduler_service().cancel_scheduled_node(drama_node_id)

        self.club_joined_drama_node_ids.clear()

    def on_all_households_and_sim_infos_loaded(self, client):
        if self.member_ids is None:
            return
        self.load_club_bucks_tracker(self._bucks_tracker_data)
        self._bucks_tracker_data = None
        sim_info_manager = services.sim_info_manager()
        for member in self._get_member_sim_infos():
            self.add_member(member, distribute=False)

        self.leader = sim_info_manager.get(self.leader_id)
        if self.leader is None:
            self.reassign_leader(distribute=False)
        self.member_ids = None
        self.leader_id = None
        self.validate_club_hangout()

    def validate_club_hangout(self):
        is_valid = True
        if self.hangout_setting == ClubHangoutSetting.HANGOUT_LOT:
            is_valid = self.is_zone_valid_for_gathering(self.hangout_zone_id) or False
        else:
            if self.hangout_setting == ClubHangoutSetting.HANGOUT_VENUE:
                if not self.hangout_venue.allowed_for_clubs:
                    is_valid = False
            else:
                self.hangout_setting = is_valid or ClubHangoutSetting.HANGOUT_NONE
                services.get_club_service().distribute_club_update((self,))
            self._validate_club_gathering_location()

    def _validate_club_gathering_location(self):
        club_gathering = self.get_gathering()
        if club_gathering is None:
            return
        if club_gathering.is_validity_overridden():
            return
        if not self.is_zone_valid_for_gathering(services.current_zone_id()):
            situation_manager = services.get_zone_situation_manager()
            situation_manager.destroy_situation_by_id(club_gathering.id)

    def on_gathering_ended(self, gathering):
        self._gathering_end_time = services.time_service().sim_now
        self._recent_member_ids.clear()

    def get_club_uniform_data(self, age: Age, gender: Gender, sim_id=0):
        if age != Age.CHILD:
            if gender is Gender.MALE:
                if self.male_adult_mannequin is None:
                    self.male_adult_mannequin = SimInfoBaseWrapper(sim_id=sim_id)
                    if self.uniform_male_adult is not None:
                        resource = self.uniform_male_adult
                    else:
                        resource = club_tuning.ClubTunables.DEFAULT_MANNEQUIN_DATA.male_adult
                    self.male_adult_mannequin.load_from_resource(resource)
                return self.male_adult_mannequin
        else:
            if age != Age.CHILD:
                if gender is Gender.FEMALE:
                    if self.female_adult_mannequin is None:
                        self.female_adult_mannequin = SimInfoBaseWrapper(sim_id=sim_id)
                        if self.uniform_female_adult is not None:
                            resource = self.uniform_female_adult
                        else:
                            resource = club_tuning.ClubTunables.DEFAULT_MANNEQUIN_DATA.female_adult
                        self.female_adult_mannequin.load_from_resource(resource)
                    return self.female_adult_mannequin
            if age is Age.CHILD and gender is Gender.MALE:
                if self.male_child_mannequin is None:
                    self.male_child_mannequin = SimInfoBaseWrapper(sim_id=sim_id)
                    if self.uniform_male_child is not None:
                        resource = self.uniform_male_child
                    else:
                        resource = club_tuning.ClubTunables.DEFAULT_MANNEQUIN_DATA.male_child
                    self.male_child_mannequin.load_from_resource(resource)
                return self.male_child_mannequin
        if age is Age.CHILD:
            if gender is Gender.FEMALE:
                if self.female_child_mannequin is None:
                    self.female_child_mannequin = SimInfoBaseWrapper(sim_id=sim_id)
                    if self.uniform_female_child is not None:
                        resource = self.uniform_female_child
                    else:
                        resource = club_tuning.ClubTunables.DEFAULT_MANNEQUIN_DATA.female_child
                    self.female_child_mannequin.load_from_resource(resource)
                return self.female_child_mannequin
        logger.error('Trying to get the club uniform data for an unsupported Age and Gender: {} and {}', str(age), str(gender))

    def handle_club_bucks_earned(self, bucks_type, amount_earned, reason=None):
        if bucks_type != club_tuning.ClubTunables.CLUB_BUCKS_TYPE:
            return
        for member in self.members:
            services.get_event_manager().process_event((test_events.TestEvent.ClubBucksEarned), sim_info=member, amount=amount_earned)

        if gsi_handlers.club_bucks_archive_handlers.is_archive_enabled():
            gsi_handlers.club_bucks_archive_handlers.archive_club_bucks_reward((self.id), amount=amount_earned, reason=reason)

    def load_club_bucks_tracker(self, bucks_tracker_data):
        if bucks_tracker_data is not None:
            self.bucks_tracker.load_data(bucks_tracker_data)

    def save--- This code section failed: ---

 L. 986         0  LOAD_FAST                'self'
                2  LOAD_ATTR                club_id
                4  LOAD_FAST                'club_data'
                6  STORE_ATTR               club_id

 L. 987         8  LOAD_FAST                'self'
               10  LOAD_ATTR                invite_only
               12  LOAD_FAST                'club_data'
               14  STORE_ATTR               invite_only

 L. 988        16  LOAD_FAST                'self'
               18  LOAD_METHOD              get_member_cap
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  LOAD_FAST                'club_data'
               24  STORE_ATTR               member_cap

 L. 990        26  LOAD_FAST                'self'
               28  LOAD_ATTR                leader
               30  LOAD_CONST               None
               32  COMPARE_OP               is-not
               34  POP_JUMP_IF_FALSE    48  'to 48'

 L. 991        36  LOAD_FAST                'self'
               38  LOAD_ATTR                leader
               40  LOAD_ATTR                id
               42  LOAD_FAST                'club_data'
               44  STORE_ATTR               leader
               46  JUMP_FORWARD         74  'to 74'
             48_0  COME_FROM            34  '34'

 L. 992        48  LOAD_FAST                'self'
               50  LOAD_ATTR                leader_id
               52  LOAD_CONST               None
               54  COMPARE_OP               is-not
               56  POP_JUMP_IF_FALSE    68  'to 68'

 L. 993        58  LOAD_FAST                'self'
               60  LOAD_ATTR                leader_id
               62  LOAD_FAST                'club_data'
               64  STORE_ATTR               leader
               66  JUMP_FORWARD         74  'to 74'
             68_0  COME_FROM            56  '56'

 L. 995        68  LOAD_CONST               0
               70  LOAD_FAST                'club_data'
               72  STORE_ATTR               leader
             74_0  COME_FROM            66  '66'
             74_1  COME_FROM            46  '46'

 L. 997        74  LOAD_FAST                'self'
               76  LOAD_ATTR                _name
               78  POP_JUMP_IF_FALSE    88  'to 88'

 L. 998        80  LOAD_FAST                'self'
               82  LOAD_ATTR                _name
               84  LOAD_FAST                'club_data'
               86  STORE_ATTR               name
             88_0  COME_FROM            78  '78'

 L. 999        88  LOAD_FAST                'self'
               90  LOAD_ATTR                _description
               92  POP_JUMP_IF_FALSE   102  'to 102'

 L.1000        94  LOAD_FAST                'self'
               96  LOAD_ATTR                _description
               98  LOAD_FAST                'club_data'
              100  STORE_ATTR               description
            102_0  COME_FROM            92  '92'

 L.1002       102  LOAD_FAST                'self'
              104  LOAD_ATTR                members
              106  POP_JUMP_IF_FALSE   140  'to 140'

 L.1003       108  SETUP_LOOP          174  'to 174'
              110  LOAD_FAST                'self'
              112  LOAD_ATTR                members
              114  GET_ITER         
              116  FOR_ITER            136  'to 136'
              118  STORE_FAST               'member'

 L.1004       120  LOAD_FAST                'club_data'
              122  LOAD_ATTR                members
              124  LOAD_METHOD              append
              126  LOAD_FAST                'member'
              128  LOAD_ATTR                id
              130  CALL_METHOD_1         1  '1 positional argument'
              132  POP_TOP          
              134  JUMP_BACK           116  'to 116'
              136  POP_BLOCK        
              138  JUMP_FORWARD        174  'to 174'
            140_0  COME_FROM           106  '106'

 L.1005       140  LOAD_FAST                'self'
              142  LOAD_ATTR                member_ids
              144  POP_JUMP_IF_FALSE   174  'to 174'

 L.1006       146  SETUP_LOOP          174  'to 174'
              148  LOAD_FAST                'self'
              150  LOAD_ATTR                member_ids
              152  GET_ITER         
              154  FOR_ITER            172  'to 172'
              156  STORE_FAST               'member_id'

 L.1007       158  LOAD_FAST                'club_data'
              160  LOAD_ATTR                members
              162  LOAD_METHOD              append
              164  LOAD_FAST                'member_id'
              166  CALL_METHOD_1         1  '1 positional argument'
              168  POP_TOP          
              170  JUMP_BACK           154  'to 154'
              172  POP_BLOCK        
            174_0  COME_FROM_LOOP      146  '146'
            174_1  COME_FROM           144  '144'
            174_2  COME_FROM           138  '138'
            174_3  COME_FROM_LOOP      108  '108'

 L.1009       174  SETUP_LOOP          202  'to 202'
              176  LOAD_FAST                'self'
              178  LOAD_ATTR                _recent_member_ids
              180  GET_ITER         
              182  FOR_ITER            200  'to 200'
              184  STORE_FAST               'recent_member_id'

 L.1010       186  LOAD_FAST                'club_data'
              188  LOAD_ATTR                recent_members
              190  LOAD_METHOD              append
              192  LOAD_FAST                'recent_member_id'
              194  CALL_METHOD_1         1  '1 positional argument'
              196  POP_TOP          
              198  JUMP_BACK           182  'to 182'
              200  POP_BLOCK        
            202_0  COME_FROM_LOOP      174  '174'

 L.1012       202  LOAD_GLOBAL              sims4
              204  LOAD_ATTR                resources
              206  LOAD_METHOD              get_protobuff_for_key
              208  LOAD_FAST                'self'
              210  LOAD_ATTR                icon
              212  CALL_METHOD_1         1  '1 positional argument'
              214  STORE_FAST               'icon_proto'

 L.1013       216  LOAD_FAST                'icon_proto'
              218  LOAD_FAST                'club_data'
              220  STORE_ATTR               icon

 L.1015       222  LOAD_FAST                'self'
              224  LOAD_ATTR                hangout_setting
              226  LOAD_FAST                'club_data'
              228  STORE_ATTR               hangout_setting

 L.1016       230  LOAD_FAST                'self'
              232  LOAD_ATTR                hangout_setting
              234  LOAD_GLOBAL              ClubHangoutSetting
              236  LOAD_ATTR                HANGOUT_VENUE
              238  COMPARE_OP               ==
          240_242  POP_JUMP_IF_FALSE   264  'to 264'

 L.1017       244  LOAD_GLOBAL              sims4
              246  LOAD_ATTR                resources
              248  LOAD_METHOD              get_protobuff_for_key
              250  LOAD_FAST                'self'
              252  LOAD_ATTR                hangout_venue
              254  LOAD_ATTR                resource_key
              256  CALL_METHOD_1         1  '1 positional argument'
              258  LOAD_FAST                'club_data'
              260  STORE_ATTR               venue_type
              262  JUMP_FORWARD        286  'to 286'
            264_0  COME_FROM           240  '240'

 L.1018       264  LOAD_FAST                'self'
              266  LOAD_ATTR                hangout_setting
              268  LOAD_GLOBAL              ClubHangoutSetting
              270  LOAD_ATTR                HANGOUT_LOT
              272  COMPARE_OP               ==
          274_276  POP_JUMP_IF_FALSE   286  'to 286'

 L.1019       278  LOAD_FAST                'self'
              280  LOAD_ATTR                hangout_zone_id
              282  LOAD_FAST                'club_data'
              284  STORE_ATTR               hangout_zone_id
            286_0  COME_FROM           274  '274'
            286_1  COME_FROM           262  '262'

 L.1021       286  LOAD_FAST                'self'
              288  LOAD_ATTR                club_seed
              290  LOAD_CONST               None
              292  COMPARE_OP               is-not
          294_296  POP_JUMP_IF_FALSE   320  'to 320'

 L.1022       298  LOAD_GLOBAL              sims4
              300  LOAD_ATTR                resources
              302  LOAD_METHOD              get_protobuff_for_key
              304  LOAD_FAST                'self'
              306  LOAD_ATTR                club_seed
              308  LOAD_ATTR                resource_key
              310  CALL_METHOD_1         1  '1 positional argument'
              312  STORE_FAST               'seed_proto'

 L.1023       314  LOAD_FAST                'seed_proto'
              316  LOAD_FAST                'club_data'
              318  STORE_ATTR               club_seed
            320_0  COME_FROM           294  '294'

 L.1025       320  LOAD_FAST                'self'
              322  LOAD_ATTR                associated_color
              324  LOAD_CONST               None
              326  COMPARE_OP               is-not
          328_330  POP_JUMP_IF_FALSE   340  'to 340'

 L.1026       332  LOAD_FAST                'self'
              334  LOAD_ATTR                associated_color
              336  LOAD_FAST                'club_data'
              338  STORE_ATTR               associated_color
            340_0  COME_FROM           328  '328'

 L.1028       340  LOAD_FAST                'self'
              342  LOAD_ATTR                associated_style
              344  LOAD_CONST               None
              346  COMPARE_OP               is-not
          348_350  POP_JUMP_IF_FALSE   360  'to 360'

 L.1029       352  LOAD_FAST                'self'
              354  LOAD_ATTR                associated_style
              356  LOAD_FAST                'club_data'
              358  STORE_ATTR               associated_style
            360_0  COME_FROM           348  '348'

 L.1031       360  SETUP_LOOP          410  'to 410'
              362  LOAD_FAST                'self'
              364  LOAD_ATTR                membership_criteria
              366  GET_ITER         
              368  FOR_ITER            408  'to 408'
              370  STORE_FAST               'criteria'

 L.1032       372  LOAD_GLOBAL              ProtocolBufferRollback
              374  LOAD_FAST                'club_data'
              376  LOAD_ATTR                membership_criteria
              378  CALL_FUNCTION_1       1  '1 positional argument'
              380  SETUP_WITH          398  'to 398'
              382  STORE_FAST               'club_criteria'

 L.1033       384  LOAD_FAST                'criteria'
              386  LOAD_METHOD              save
              388  LOAD_FAST                'club_criteria'
              390  CALL_METHOD_1         1  '1 positional argument'
              392  POP_TOP          
              394  POP_BLOCK        
              396  LOAD_CONST               None
            398_0  COME_FROM_WITH      380  '380'
              398  WITH_CLEANUP_START
              400  WITH_CLEANUP_FINISH
              402  END_FINALLY      
          404_406  JUMP_BACK           368  'to 368'
              408  POP_BLOCK        
            410_0  COME_FROM_LOOP      360  '360'

 L.1035       410  SETUP_LOOP          506  'to 506'
              412  LOAD_FAST                'self'
              414  LOAD_ATTR                rules
              416  GET_ITER         
              418  FOR_ITER            504  'to 504'
              420  STORE_FAST               'rule'

 L.1036       422  LOAD_GLOBAL              ProtocolBufferRollback
              424  LOAD_FAST                'club_data'
              426  LOAD_ATTR                club_rules
              428  CALL_FUNCTION_1       1  '1 positional argument'
              430  SETUP_WITH          494  'to 494'
              432  STORE_FAST               'club_rule'

 L.1037       434  LOAD_FAST                'rule'
              436  LOAD_ATTR                is_encouraged
              438  LOAD_FAST                'club_rule'
              440  STORE_ATTR               encouraged

 L.1039       442  LOAD_GLOBAL              sims4
              444  LOAD_ATTR                resources
              446  LOAD_METHOD              get_protobuff_for_key
              448  LOAD_FAST                'rule'
              450  LOAD_ATTR                action
              452  LOAD_ATTR                resource_key
              454  CALL_METHOD_1         1  '1 positional argument'
              456  STORE_FAST               'action_proto'

 L.1040       458  LOAD_FAST                'action_proto'
              460  LOAD_FAST                'club_rule'
              462  STORE_ATTR               interaction_group

 L.1042       464  LOAD_FAST                'rule'
              466  LOAD_ATTR                with_whom
              468  LOAD_CONST               None
              470  COMPARE_OP               is-not
          472_474  POP_JUMP_IF_FALSE   490  'to 490'

 L.1043       476  LOAD_FAST                'rule'
              478  LOAD_ATTR                with_whom
              480  LOAD_METHOD              save
              482  LOAD_FAST                'club_rule'
              484  LOAD_ATTR                with_whom
              486  CALL_METHOD_1         1  '1 positional argument'
              488  POP_TOP          
            490_0  COME_FROM           472  '472'
              490  POP_BLOCK        
              492  LOAD_CONST               None
            494_0  COME_FROM_WITH      430  '430'
              494  WITH_CLEANUP_START
              496  WITH_CLEANUP_FINISH
              498  END_FINALLY      
          500_502  JUMP_BACK           418  'to 418'
              504  POP_BLOCK        
            506_0  COME_FROM_LOOP      410  '410'

 L.1044       506  LOAD_FAST                'self'
              508  LOAD_ATTR                bucks_tracker
              510  LOAD_METHOD              save_data
              512  LOAD_FAST                'club_data'
              514  CALL_METHOD_1         1  '1 positional argument'
              516  POP_TOP          

 L.1047       518  LOAD_FAST                'self'
              520  LOAD_METHOD              get_club_uniform_data
              522  LOAD_GLOBAL              Age
              524  LOAD_ATTR                ADULT
              526  LOAD_GLOBAL              Gender
              528  LOAD_ATTR                MALE
              530  CALL_METHOD_2         2  '2 positional arguments'
              532  STORE_FAST               'adult_male_mannequin'

 L.1048       534  LOAD_FAST                'adult_male_mannequin'
              536  LOAD_ATTR                id
              538  LOAD_FAST                'club_data'
              540  LOAD_ATTR                club_uniform_adult_male
              542  STORE_ATTR               mannequin_id

 L.1049       544  LOAD_FAST                'self'
              546  LOAD_ATTR                male_adult_mannequin
              548  LOAD_METHOD              save_sim_info
              550  LOAD_FAST                'club_data'
              552  LOAD_ATTR                club_uniform_adult_male
              554  CALL_METHOD_1         1  '1 positional argument'
              556  POP_TOP          

 L.1051       558  LOAD_FAST                'self'
              560  LOAD_METHOD              get_club_uniform_data
              562  LOAD_GLOBAL              Age
              564  LOAD_ATTR                ADULT
              566  LOAD_GLOBAL              Gender
              568  LOAD_ATTR                FEMALE
              570  CALL_METHOD_2         2  '2 positional arguments'
              572  STORE_FAST               'adult_female_mannequin'

 L.1052       574  LOAD_FAST                'adult_female_mannequin'
              576  LOAD_ATTR                id
              578  LOAD_FAST                'club_data'
              580  LOAD_ATTR                club_uniform_adult_female
              582  STORE_ATTR               mannequin_id

 L.1053       584  LOAD_FAST                'self'
              586  LOAD_ATTR                female_adult_mannequin
              588  LOAD_METHOD              save_sim_info
              590  LOAD_FAST                'club_data'
              592  LOAD_ATTR                club_uniform_adult_female
              594  CALL_METHOD_1         1  '1 positional argument'
              596  POP_TOP          

 L.1055       598  LOAD_FAST                'self'
              600  LOAD_METHOD              get_club_uniform_data
              602  LOAD_GLOBAL              Age
              604  LOAD_ATTR                CHILD
              606  LOAD_GLOBAL              Gender
              608  LOAD_ATTR                MALE
              610  CALL_METHOD_2         2  '2 positional arguments'
              612  STORE_FAST               'child_male_mannequin'

 L.1056       614  LOAD_FAST                'child_male_mannequin'
              616  LOAD_ATTR                id
              618  LOAD_FAST                'club_data'
              620  LOAD_ATTR                club_uniform_child_male
              622  STORE_ATTR               mannequin_id

 L.1057       624  LOAD_FAST                'self'
              626  LOAD_ATTR                male_child_mannequin
              628  LOAD_METHOD              save_sim_info
              630  LOAD_FAST                'club_data'
              632  LOAD_ATTR                club_uniform_child_male
              634  CALL_METHOD_1         1  '1 positional argument'
              636  POP_TOP          

 L.1059       638  LOAD_FAST                'self'
              640  LOAD_METHOD              get_club_uniform_data
              642  LOAD_GLOBAL              Age
              644  LOAD_ATTR                CHILD
              646  LOAD_GLOBAL              Gender
              648  LOAD_ATTR                FEMALE
              650  CALL_METHOD_2         2  '2 positional arguments'
              652  STORE_FAST               'female_child_mannequin'

 L.1060       654  LOAD_FAST                'female_child_mannequin'
              656  LOAD_ATTR                id
              658  LOAD_FAST                'club_data'
              660  LOAD_ATTR                club_uniform_child_female
              662  STORE_ATTR               mannequin_id

 L.1061       664  LOAD_FAST                'self'
              666  LOAD_ATTR                female_child_mannequin
              668  LOAD_METHOD              save_sim_info
              670  LOAD_FAST                'club_data'
              672  LOAD_ATTR                club_uniform_child_female
              674  CALL_METHOD_1         1  '1 positional argument'
              676  POP_TOP          

 L.1063       678  LOAD_FAST                'self'
              680  LOAD_ATTR                outfit_setting
              682  LOAD_FAST                'club_data'
              684  STORE_ATTR               outfit_setting

Parse error at or near `COME_FROM_LOOP' instruction at offset 174_3

    def populate_localization_token(self, token):
        token.type = LocalizedStringToken.STRING
        token.text_string = self.name

    def has_members(self):
        return len(self.members) > 0