# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\travel_group\travel_group_stayover.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 24937 bytes
from collections import defaultdict
from copy import copy
from protocolbuffers import FileSerialization_pb2
from autonomy.autonomy_preference import ObjectPreferenceTag
from drama_scheduler.drama_node import DramaNodeUiDisplayType
from event_testing.resolver import SingleSimResolver
from objects.object_manager import BED_PREFIX_FILTER
from relationships.relationship_bit import RelationshipBit
from sims.household import Household
from sims.sim_info_types import SpeciesExtended, Age
from sims4.tuning.tunable import TunableEnumSet, TunableEnumEntry, TunableEnumWithFilter, TunableList, TunablePackSafeReference, TunableRange, TunableReference, TunableSet, TunableTuple
from situations.situation_guest_list import SituationGuestList, SituationGuestInfo, SituationInvitationPurpose
from situations.situation_job import SituationJob
from travel_group.travel_group import TravelGroup
from tunable_time import TunableTimeSpan
from ui.ui_dialog_notification import UiDialogNotification
import alarms, random, services, sims4.log, tag
logger = sims4.log.Logger('TravelGroupStayover', default_owner='nabaker')

class TravelGroupStayover(TravelGroup):
    OFFLOT_ALARM_INTERVAL = TunableTimeSpan(description='\n        Interval between attempts to bring guests back onto the lot if they have been pulled off the lot.\n        ',
      default_hours=1)
    SS3_PARK_INTERACTIONS = TunableList(description='\n        Interactions in which to park NPC travel mates during SS3.\n        One of which will be randomly selected.\n        ',
      tunable=TunableReference(description='\n            The affordance to push.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions=('SuperInteraction', ),
      pack_safe=True))
    HOUSEHOLD_AND_GUEST_MAXIMUM = TunableRange(description='\n        Maximum number of household members (including roommates) and guests.\n        ',
      tunable_type=int,
      default=9,
      minimum=9)
    GUEST_RELATIONSHIP_BIT = RelationshipBit.TunablePackSafeReference(description='\n        The relationship bit to add between sims in the household that owns the\n        lot, and any guests.\n        ')
    SUMMON_GUEST_SITUATION = TunablePackSafeReference(description='\n        The situation used to bring the guest to the lot, triggers every every offlot alarm interval if the sim is\n        off lot.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))
    SUMMON_GUEST_JOB = SituationJob.TunablePackSafeReference(description='\n        The job for the guest summon situation.\n        ')
    END_STAY_SITUATION = TunablePackSafeReference(description='\n        The situation sims are put into when the stayover ends.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION)))
    END_STAY_SITUATION_GUEST_JOB = SituationJob.TunablePackSafeReference(description='\n        The job for the guests in the end stay situation.\n        ')
    END_STAY_SITUATION_HOST_JOB = SituationJob.TunablePackSafeReference(description='\n        The job for sims in the host household (and any selectable visitors) in the end stay situation.\n        ')
    END_STAY_NOTIFICATION = UiDialogNotification.TunableFactory(description="\n        Notification to show if a stay at active player's zone ends while that zone isn't the active one.\n        ")

    @staticmethod
    def _bed_assignment_tuning_loaded_callback(instance_class, tunable_name, source, value):
        temp_include_tags = defaultdict((lambda: defaultdict(set)))
        temp_exclude_tags = defaultdict((lambda: defaultdict(set)))
        for bed_assignment_tuple in TravelGroupStayover.BED_ASSIGNMENT_DATA:
            for species in bed_assignment_tuple.species:
                for age in bed_assignment_tuple.age:
                    temp_include_tags[species][age].update(bed_assignment_tuple.bed_tags)
                    temp_exclude_tags[species][age].update(bed_assignment_tuple.exclude_bed_tags)

        TravelGroupStayover.BED_INCLUDE_EXCLUDE_TAGS = {}
        for species, age_tags_dict in temp_include_tags.items():
            age_tag_tuple_dict = {}
            TravelGroupStayover.BED_INCLUDE_EXCLUDE_TAGS[species] = age_tag_tuple_dict
            for age, tags in age_tags_dict.items():
                age_tag_tuple_dict[age] = (frozenset(tags), frozenset(temp_exclude_tags[species][age]))

    BED_ASSIGNMENT_DATA = TunableList(description='\n        Data used to automatically assign available beds to sims.\n        If a specific age/species combination appears in multiple entries,\n        the bed tags and exclude bed tags will be the union of all applicable sets.\n        ',
      tunable=TunableTuple(age=TunableEnumSet(description='\n                Ages of sims that should use this bed assignment data.\n                ',
      enum_type=Age,
      enum_default=(Age.YOUNGADULT)),
      species=TunableEnumSet(description='\n                Species of sims that should use this bed assignment data.\n                ',
      enum_type=SpeciesExtended,
      enum_default=(SpeciesExtended.HUMAN),
      invalid_enums=(
     SpeciesExtended.INVALID,)),
      bed_tags=TunableSet(description='\n                Tags that indicate an object is a suitable bed for this age/species.\n                ',
      tunable=TunableEnumWithFilter(tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID),
      filter_prefixes=BED_PREFIX_FILTER)),
      exclude_bed_tags=TunableSet(description="\n                Tags that indicate a bed isn't suitable for this age/species even if it has\n                tags in bed_tags.\n                ",
      tunable=TunableEnumWithFilter(tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID),
      filter_prefixes=BED_PREFIX_FILTER))),
      callback=_bed_assignment_tuning_loaded_callback)
    BED_PREFERENCE_TAG = TunableEnumEntry(description='\n        The preference tag used to claim beds for autonomous use.\n        ',
      tunable_type=ObjectPreferenceTag,
      default=(ObjectPreferenceTag.INVALID),
      invalid_enums=(
     ObjectPreferenceTag.INVALID,))
    STAYOVER_CREATION_INTERACTION = TunableReference(description='\n        The affordance to push when creating/editing a stayover.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
      class_restrictions='SuperInteraction',
      pack_safe=True)

    def __init__(self, behavioral_situation=None, **kwargs):
        (super().__init__)(**kwargs)
        self._behavioral_situation = behavioral_situation
        self._summon_alarm_handle = None
        self._cached_household = None

    def _setup_summon_alarm(self):
        self._summon_alarm_handle = alarms.add_alarm(self, (self.OFFLOT_ALARM_INTERVAL()),
          (self._summon_alarm_callback),
          repeating=True,
          use_sleep_time=False)

    def _summon_alarm_callback(self, _):
        situation_manager = services.get_zone_situation_manager()
        summon_situations = situation_manager.get_situations_by_type(self.SUMMON_GUEST_SITUATION)
        for sim_info in self:
            self._summon_sim(sim_info, summon_situations=summon_situations)

    def on_household_member_added(self, sim_info):
        relationship_tracker = sim_info.relationship_tracker
        for travel_sim_info in self:
            relationship_tracker.add_relationship_bit((travel_sim_info.id), (self.GUEST_RELATIONSHIP_BIT), force_add=True)

    def on_household_member_removed(self, sim_info):
        relationship_tracker = sim_info.relationship_tracker
        for travel_sim_info in self:
            relationship_tracker.remove_relationship_bit(travel_sim_info.id, self.GUEST_RELATIONSHIP_BIT)

    def __repr__(self):
        sim_strings = []
        for sim_info in self._sim_infos:
            sim_strings.append(str(sim_info))

        return 'Travel Group Stayover {} : {}'.format(self.id, '; '.join(sim_strings))

    @property
    def ui_display_type(self):
        return DramaNodeUiDisplayType.STAYOVER

    @property
    def group_type(self):
        return FileSerialization_pb2.TravelGroupData.GROUPTYPE_STAYOVER

    @property
    def situation(self):
        return self._behavioral_situation

    def get_ss3_affordance(self):
        if self._household.is_active_household:
            return random.choice(self.SS3_PARK_INTERACTIONS)

    @property
    def visible_on_calendar(self):
        if len(self) == 0:
            return False
        else:
            active_household = services.active_household()
            return active_household or False
        return active_household.home_zone_id == self._zone_id

    @property
    def report_telemetry(self):
        return True

    def can_add_to_travel_group(self, sim_info):
        if sim_info.is_selectable:
            return False
        return super().can_add_to_travel_group(sim_info)

    @property
    def free_slot_count(self):
        used_slot_count = len(self)
        roommate_service = services.get_roommate_service()
        if roommate_service is not None:
            used_slot_count += roommate_service.get_roommate_count(self._zone_id)
        zone = services.get_zone(self._zone_id)
        return min(super().free_slot_count, self.HOUSEHOLD_AND_GUEST_MAXIMUM - used_slot_count - len(self._household))

    @property
    def _household(self):
        if self._cached_household is None:
            zone_data = services.get_persistence_service().get_zone_proto_buff(self._zone_id)
            if zone_data is None:
                return
            self._cached_household = services.household_manager().get(zone_data.household_id)
        return self._cached_household

    def rent_zone(self, zone_id):
        super().rent_zone(zone_id)
        if self._zone_id == services.current_zone_id():
            self._setup_summon_alarm()
            household = self._household
            if household is None:
                logger.error('Stay over occurring at unoccupied lot: {}', self._zone_id)
                super()._init_preference_tracker(from_load)
                return
            self.object_preference_tracker = copy(household.object_preference_tracker)
            self.object_preference_tracker.owner = self

    def add_sim_info(self, sim_info):
        if not super().add_sim_info(sim_info):
            return False
        relationship_tracker = sim_info.relationship_tracker
        for household_sim_info in self._household:
            relationship_tracker.add_relationship_bit((household_sim_info.id), (self.GUEST_RELATIONSHIP_BIT), force_add=True)

        if self._zone_id == services.current_zone_id():
            self._assign_beds((sim_info,))
            self._summon_sim(sim_info)
            self._begin_behavioral_situation(sim_info)
        return True

    def remove_sim_info(self, sim_info, destroy_on_empty=True):
        super().remove_sim_info(sim_info, destroy_on_empty=destroy_on_empty)
        relationship_tracker = sim_info.relationship_tracker
        for household_sim_info in self._household:
            relationship_tracker.remove_relationship_bit(household_sim_info.id, self.GUEST_RELATIONSHIP_BIT)

        self.object_preference_tracker.clear_sim_restriction((sim_info.sim_id), zone_id=(self._zone_id))
        if self._zone_id == services.current_zone_id():
            if sim_info.is_toddler_or_younger:
                services.daycare_service().refresh_daycare_status(sim_info, exclude_zone_id=(self.zone_id))
            self._destroy_situations(sim_info)

    def _assign_beds(self, sim_infos, avoid_id=None):
        tags_to_sim_infos = defaultdict(list)
        for sim_info in sim_infos:
            object_id, _ = self.object_preference_tracker.get_restricted_object(sim_info.sim_id, self.BED_PREFERENCE_TAG)
            if object_id is not None:
                continue
            age_dict = self.BED_INCLUDE_EXCLUDE_TAGS.get(sim_info.extended_species)
            if age_dict is None:
                continue
            tag_tuple = age_dict.get(sim_info.age)
            if tag_tuple is None:
                continue
            tags_to_sim_infos[tag_tuple].append(sim_info)

        object_manager = services.object_manager()
        for tags, sim_infos in tags_to_sim_infos.items():
            possible_beds = object_manager.get_objects_matching_tags_with_exclusion((tags[0]), (tags[1]), match_any=True)
            available_beds = [bed for bed in possible_beds if bed.id != avoid_id if not self.object_preference_tracker.get_restricted_sims(bed.id, self.BED_PREFERENCE_TAG)]
            if not available_beds:
                continue
            for sim_info in sim_infos:
                self.object_preference_tracker.set_object_restriction(sim_info.sim_id, available_beds.pop(), self.BED_PREFERENCE_TAG)
                if not available_beds:
                    break

    def assign_bed(self, sim_id, avoid_id=None):
        if self._zone_id == services.current_zone_id():
            for sim_info in self:
                if sim_info.sim_id == sim_id:
                    self._assign_beds((sim_info,), avoid_id=avoid_id)
                    return True

        return False

    def _summon_sim(self, sim_info, summon_situations=None):
        if sim_info.zone_id == self._zone_id:
            return
        situation_manager = services.get_zone_situation_manager()
        sim_id = sim_info.sim_id
        if summon_situations is None:
            summon_situations = situation_manager.get_situations_by_type(self.SUMMON_GUEST_SITUATION)
        for situation in summon_situations:
            if sim_id in situation.invited_sim_ids:
                return

        guest_list = self.SUMMON_GUEST_SITUATION.get_predefined_guest_list()
        if guest_list is None:
            guest_list = SituationGuestList(invite_only=True)
        if self.SUMMON_GUEST_JOB is not None:
            guest_list.add_guest_info(SituationGuestInfo.construct_from_purpose(sim_id, self.SUMMON_GUEST_JOB, SituationInvitationPurpose.INVITED))
        situation_manager.create_situation((self.SUMMON_GUEST_SITUATION), guest_list=guest_list,
          spawn_sims_during_zone_spin_up=True,
          user_facing=False)

    def _begin_behavioral_situation(self, sim_info):
        if self._behavioral_situation is None:
            return
        situation_manager = services.get_zone_situation_manager()
        sim_id = sim_info.sim_id
        for situation in situation_manager.get_situations_by_type(self._behavioral_situation):
            if sim_id == situation.guest_list.host_sim_id:
                return

        guest_list = SituationGuestList(host_sim_id=sim_id, invite_only=False)
        situation_manager.create_situation((self._behavioral_situation), guest_list=guest_list,
          spawn_sims_during_zone_spin_up=True,
          user_facing=False)

    def _destroy_situations(self, sim_info):
        situation_manager = services.get_zone_situation_manager()
        sim_id = sim_info.sim_id
        for situation in situation_manager.get_situations_by_type(self.SUMMON_GUEST_SITUATION):
            if sim_id in situation.invited_sim_ids:
                situation_manager.destroy_situation_by_id(situation.id)

        for situation in situation_manager.get_situations_by_type(self._behavioral_situation):
            if sim_id == situation.guest_list.host_sim_id:
                situation_manager.destroy_situation_by_id(situation.id)

    def end_vacation(self):
        if self._zone_id == services.current_zone_id():
            active_household = services.active_household()
            host_sims = list(self._household.instanced_sims_gen())
            if not self._household.is_active_household:
                host_sims.extend(active_household.instanced_sims_gen())
            guest_sims = [sim_info for sim_info in self if sim_info.get_sim_instance()]
            if host_sims:
                if guest_sims:
                    guest_list = self.END_STAY_SITUATION.get_predefined_guest_list()
                    if guest_list is None:
                        guest_list = SituationGuestList(invite_only=True)
                    if self.END_STAY_SITUATION_HOST_JOB is not None:
                        for sim_info in host_sims:
                            guest_list.add_guest_info(SituationGuestInfo.construct_from_purpose(sim_info.sim_id, self.END_STAY_SITUATION_HOST_JOB, SituationInvitationPurpose.INVITED))

                    if self.END_STAY_SITUATION_GUEST_JOB is not None:
                        for sim_info in guest_sims:
                            guest_list.add_guest_info(SituationGuestInfo.construct_from_purpose(sim_info.sim_id, self.END_STAY_SITUATION_GUEST_JOB, SituationInvitationPurpose.INVITED))

                    situation_manager = services.get_zone_situation_manager()
                    situation_manager.create_situation((self.END_STAY_SITUATION), guest_list=guest_list,
                      spawn_sims_during_zone_spin_up=True,
                      user_facing=False)
                    services.travel_group_manager().destroy_travel_group_and_release_zone(self, return_objects=True)
                    return
        self.try_end_notification()
        super().end_vacation()

    def try_end_notification(self):
        active_household = services.active_household()
        if active_household:
            if active_household.home_zone_id == self._zone_id:
                active_sim_info = services.active_sim_info()
                notification = self.END_STAY_NOTIFICATION(active_sim_info, resolver=(SingleSimResolver(active_sim_info)))
                notification.show_dialog()

    def on_destroy(self):
        super().on_destroy()
        if self._summon_alarm_handle:
            alarms.cancel_alarm(self._summon_alarm_handle)
            self._summon_alarm_handle = None
        roommate_service = services.get_roommate_service()
        if roommate_service is not None:
            roommate_service.copy_new_bed_assignments(self.object_preference_tracker, self.zone_id)
        if self._zone_id == services.current_zone_id():
            object_ids_with_preference = self.object_preference_tracker.get_preferred_object_ids()
            if self._household is not None:
                object_ids_with_preference.update(self._household.object_preference_tracker.get_preferred_object_ids())
            object_manager = services.object_manager()
            for object_id in object_ids_with_preference:
                object_instance = object_manager.get(object_id)
                if object_instance is not None:
                    object_instance.update_object_tooltip()

            if roommate_service is not None:
                roommate_service.assign_beds_for_current_zone()

    def on_create(self):
        super().on_create()
        if self.visible_on_calendar:
            calendar_service = services.calendar_service()
            if calendar_service is not None:
                calendar_service.mark_on_calendar(self)

    def validate_loaded_sim_info(self, sim_info):
        return not sim_info.is_selectable

    def load_data(self, travel_group_proto):
        super().load_data(travel_group_proto)
        self._behavioral_situation = services.get_instance_manager(sims4.resources.Types.SITUATION).get(travel_group_proto.situation_id)
        for sim_info in self:
            relationship_tracker = sim_info.relationship_tracker
            for household_sim_info in self._household:
                relationship_tracker.add_relationship_bit((household_sim_info.id), (self.GUEST_RELATIONSHIP_BIT), force_add=True)

        if self._zone_id == services.current_zone_id():
            self._setup_summon_alarm()
            situation_manager = services.get_zone_situation_manager()
            summon_situations = situation_manager.get_situations_by_type(self.SUMMON_GUEST_SITUATION)
            for sim_info in self:
                self._summon_sim(sim_info, summon_situations=summon_situations)
                self._begin_behavioral_situation(sim_info)

            self._assign_beds(self)

    def save_data(self, travel_group_proto):
        super().save_data(travel_group_proto)
        travel_group_proto.situation_id = self._behavioral_situation.guid64