# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\decorator_career_gig.py
# Compiled at: 2022-03-29 18:15:50
# Size of source mod 2**32: 41862 bytes
from objects import ALL_HIDDEN_REASONS
from careers.active_career_gig import ActiveGig
from careers.career_enums import DecoratorGigType, DecoratorGigLotType, GigResult
from careers.career_event_zone_requirement import RequiredCareerEventZoneTunableVariant
from date_and_time import TimeSpan
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from event_testing import test_events
from interactions.utils.tunable_icon import TunableIcon
from protocolbuffers import DistributorOps_pb2, Sims_pb2
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import Tunable, OptionalTunable, TunableTuple, TunableEnumEntry, TunableList, TunablePercent, TunableReference, TunableRange, TunableVariant
from sims4.utils import flexmethod, classproperty
from relationships.relationship_bit import RelationshipBit
from tag import TunableTags, TunableTag
from traits import preference_utils
from traits.trait_type import TraitType
from ui.ui_dialog_picker import ObjectPickerRow
import build_buy, random, services, sims4
logger = sims4.log.Logger('Gig', default_owner='mbilello')

class DecoratorGig(ActiveGig):
    TOP_FLOOR_VALUE = 999
    BOTTOM_FLOOR_VALUE = -999
    INSTANCE_TUNABLES = {'gig_picker_localization_format':TunableLocalizedStringFactory(description='\n            String used to format the description in the gig picker.\n            ',
       allow_none=True), 
     'gig_assignment_aspiration':OptionalTunable(description='\n            An aspiration to use as the assignment for this gig. The objectives\n            of this aspiration\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions='AspirationGig',
       pack_safe=True)), 
     '_decorator_gig_tuning':OptionalTunable(description='\n            Tuning specific to decorator gigs. Leave un-tuned if this gig is\n            not a decorator one.\n            ',
       tunable=TunableTuple(decorator_gig_type=TunableEnumEntry(description='\n                    The type of decorator gig this is.\n                    ',
       tunable_type=DecoratorGigType,
       default=(DecoratorGigType.ROOM_RENOVATION)),
       decorator_gig_type_icon=TunableTuple(name=TunableLocalizedStringFactory(description='\n                        The name to associate with type of decorator gig.\n                        '),
       icon=TunableIcon(description='\n                        The icon to associate with type of decorator gig.\n                        ')),
       decorator_gig_lot_type=TunableEnumEntry(description='\n                    The type of lot for this decorator gig this is.\n                    ',
       tunable_type=DecoratorGigLotType,
       default=(DecoratorGigLotType.RESIDENTIAL)),
       picker_localization_rarity=TunableLocalizedStringFactory(description='\n                    The string to show the gig pay on the picker.\n                    '),
       picker_localization_second_rarity=TunableLocalizedStringFactory(description='\n                    The string to show the gig budget on the picker.\n                    '),
       client_filter=TunableTuple(description='\n                    Tuning for client/customer.\n                    ',
       current_client_rel_bit=OptionalTunable(description='\n                        If tuned, this rel bit will be applied on the client.\n                        ',
       tunable=RelationshipBit.TunableReference(description='\n                            Rel bit to apply.\n                            '))),
       commercial_venue_zone=RequiredCareerEventZoneTunableVariant(description='\n                    The commercial zone type for this gig .\n                    The decorator Sim will automatically travel to this zone\n                    at the beginning of the work shift.\n                    '),
       dependent_situation_tag=TunableTag(description="\n                    Any situation running on the owner of this gig when this\n                    gig is cleaned up will be destroyed. Use this to cleanup\n                    decorator related situations that are not directly tied\n                    to this gig's career event. \n                    ",
       filter_prefixes=('Situation', )),
       preferences_number=Tunable(description='\n                    Number of preferences for this gig.\n                    ',
       tunable_type=int,
       default=0),
       restricted_to_level=OptionalTunable(description="\n                    If enabled, the decorator sim will only be allowed to modify\n                    the tuned level of the customer's lot.\n                    ",
       disabled_name='No_Level_Restrictions',
       enabled_name='Restricted_To_Level',
       tunable=TunableVariant(description='\n                        Number of the level the decorations are restricted to.\n                        0 is the ground floor, 1 is the second floor, -1 is the\n                        basement, etc.\n                        ',
       specific_floor=TunableTuple(description='\n                            Specify a floor for this gig.\n                            ',
       floor=TunableRange(description='\n                                The floor for this gig. 0 is the ground floor, 1 is the second floor, -1 is the first\n                                basement floor, etc.\n                                ',
       tunable_type=int,
       default=0,
       minimum=(-4),
       maximum=3)),
       top_floor=TunableTuple(description='\n                            Used when the gig wants to add a new floor at the top-most level.\n                            ',
       locked_args={'floor': TOP_FLOOR_VALUE}),
       bottom_floor=TunableTuple(description='\n                            Used when the gig wants to add a new floor at the lowest basement level.\n                            ',
       locked_args={'floor': BOTTOM_FLOOR_VALUE}),
       default='specific_floor')),
       tiles_number_restriction=OptionalTunable(description="\n                    If enabled, the decorator sim will only be able to modify the\n                    tile count of the customer's lot by the tuned amount.\n                    ",
       disabled_name='No_Tile_Restrictions',
       enabled_name='Restricted_To_Tile_Count',
       tunable=TunableRange(description="\n                        Indicates the number of tiles the player is allowed to add to the lot for this gig. 0 means the\n                        player can't add any tiles.\n                        ",
       tunable_type=int,
       minimum=0,
       default=0),
       enabled_by_default=True),
       gig_budget_range=TunableTuple(description='\n                    Indicates the amount of simoleons the player has to work with\n                    to complete the decoration. We will choose a random number \n                    from it at the moment of creating the gig.\n                    ',
       min=Tunable(description='\n                        Min for budget.\n                        ',
       tunable_type=int,
       default=0),
       max=Tunable(description='\n                        Max for budget.\n                        ',
       tunable_type=int,
       default=0)),
       new_object_tags=TunableTags(description="\n                    Any object bought through BB will get this tag applied to it\n                    any time the Customer's lot is loaded while this Gig is active.\n                    These tags do not persist through save/load.\n                    "),
       gig_budget_modulo=Tunable(description='\n                    Number to use to apply a modulo operation to the random \n                    budget created from the range so it looks like a real budget.\n                    ',
       tunable_type=int,
       default=1),
       preference_scoring_weight=TunableList(description='\n                    List of [trait_type, weight] used to weight each hit on the \n                    gig preferences list. \n                    trait_type in this case will be Like or Dislike.\n                    ',
       tunable=TunableTuple(trait_type=TunableEnumEntry(description='\n                            The trait type to check.\n                            ',
       tunable_type=TraitType,
       default=(TraitType.PERSONALITY)),
       weight=Tunable(description='\n                            The relative weight of this trait.\n                            ',
       tunable_type=float,
       default=1))),
       budget_scoring=TunableList(description='\n                    List of [+/-min %, +/-max %, score] to score the amount of budget used.\n                    ',
       tunable=TunableTuple(min=TunablePercent(description='\n                            Min percentage of budget used.\n                            ',
       default=0),
       max=TunablePercent(description='\n                            Max percentage of budget used.\n                            ',
       default=0),
       score=Tunable(description='\n                            Score for the percentage of budget used.\n                            ',
       tunable_type=float,
       default=1))),
       budget_over_score=Tunable(description='\n                    Score for going over budget used.\n                    ',
       tunable_type=float,
       default=1),
       base_score=Tunable(description='\n                    Base score to which we will apply all the modifiers and\n                    then use to get a gig result.\n                    ',
       tunable_type=float,
       default=100),
       scoring_results=TunableList(description='\n                    Gig Result based on final score\n                    ',
       tunable=TunableTuple(result_type=TunableEnumEntry(description='\n                            The GigResult enum that represents the outcome of the Gig.\n                            ',
       tunable_type=GigResult,
       default=(GigResult.SUCCESS)),
       min=Tunable(description='\n                            Min of the score range for this result.\n                            ',
       tunable_type=float,
       default=0),
       max=Tunable(description='\n                            Max of the score range for this result.\n                            ',
       tunable_type=float,
       default=0))),
       individual_gig_score_stat=OptionalTunable(description='\n                    If enabled, creates statistic used to apply individual gig score to clients.\n                    ',
       tunable=TunableReference(description='\n                        Statistic used to apply individual gig score to clients.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)))),
       gig_short_title=OptionalTunable(description='\n                    If enabled, the string used as the project title in gig history.\n                    ',
       tunable=(TunableLocalizedStringFactory()))))}

    def __init__(self, owner, customer=None, gig_budget=None, *args, **kwargs):
        (super().__init__)(args, *(owner, customer), **kwargs)
        self._client_preferences = []
        self._known_client_preferences = []
        self._client_hh_name = None
        self._budget_spent_delta = 0
        self._gig_budget = gig_budget
        self._gig_score = 0

    @classproperty
    def decorator_gig_tuning(cls):
        return cls._decorator_gig_tuning

    @classproperty
    def is_commercial_gig(cls):
        return cls._decorator_gig_tuning.decorator_gig_lot_type == DecoratorGigLotType.COMMERCIAL

    def get_client_preferences(self):
        return self._client_preferences

    def get_known_client_preferences(self):
        return self._known_client_preferences

    def get_client_hh_name(self):
        return self._client_hh_name

    def get_gig_budget(self):
        return self._gig_budget

    @classmethod
    def get_aspiration(cls):
        return cls.gig_assignment_aspiration

    def _reserve_gig_location(self):
        if services.get_zone_reservation_service().is_reserved(self._customer_lot_id):
            logger.error('Gig {} attempting to reserve a zone {} that is already reserved. This may cause errors.', self, self._customer_lot_id)
        services.get_zone_reservation_service().reserve_zone(self, self._customer_lot_id)

    def set_up_gig(self):
        super().set_up_gig()
        if self._decorator_gig_tuning is None:
            return
        build_buy.register_build_buy_exit_callback(self.apply_new_object_tags)
        build_buy.register_build_buy_exit_callback(self.process_customer_lot_events)
        client_sim_info = services.sim_info_manager().get(self._customer_id)
        if self._decorator_gig_tuning.decorator_gig_lot_type == DecoratorGigLotType.COMMERCIAL:
            commercial_id = self._decorator_gig_tuning.commercial_venue_zone.get_required_zone_id(self._owner)
            if commercial_id is not None:
                self._customer_lot_id = commercial_id
        self._reserve_gig_location()
        self._client_preferences = client_sim_info.household.get_household_decorator_preferences(preferences_count=(self._decorator_gig_tuning.preferences_number))
        self._known_client_preferences = []
        if client_sim_info is not None:
            self._client_hh_name = client_sim_info.household.name
            if self._decorator_gig_tuning is not None:
                self._owner.relationship_tracker.add_relationship_bit(client_sim_info.id, self._decorator_gig_tuning.client_filter.current_client_rel_bit)
        self._budget_spent_delta = 0

    def on_zone_load(self):
        super().on_zone_load()
        self.apply_new_object_tags()
        self._set_residential_customer_lot_id()

    def _set_residential_customer_lot_id(self):
        if self._decorator_gig_tuning.decorator_gig_lot_type != DecoratorGigLotType.RESIDENTIAL:
            return
        customer_lot_id = self.get_customer_lot_id()
        if customer_lot_id is not None:
            return
        customer_id = self.get_gig_customer()
        if customer_id is None:
            return
        customer_sim_info = services.sim_info_manager().get(customer_id)
        if customer_sim_info is None:
            return
        customer_sim_info_household = customer_sim_info.household
        if customer_sim_info_household is None:
            return
        self._customer_lot_id = customer_sim_info.household.home_zone_id

    def apply_new_object_tags(self):
        if not services.current_zone_id() != self._customer_lot_id:
            return self.decorator_gig_tuning.new_object_tags or None
        else:
            new_object_ids = build_buy.get_gig_objects_added(self._customer_lot_id)
            return new_object_ids or None
        obj_manager = services.object_manager()
        for obj_id in new_object_ids:
            new_obj = obj_manager.get(obj_id)
            new_obj.append_tags(self.decorator_gig_tuning.new_object_tags)

    def process_customer_lot_events(self):
        if services.current_zone_id() == self._customer_lot_id:
            services.get_event_manager().process_event((test_events.TestEvent.OnExitBuildBuy), sim_info=(self._owner))

    @classmethod
    def create_gig_budget(cls):
        if cls._decorator_gig_tuning is not None:
            budget_min = cls._decorator_gig_tuning.gig_budget_range.min
            budget_max = cls._decorator_gig_tuning.gig_budget_range.max
            gig_budget = random.randint(budget_min, budget_max)
            gig_budget -= gig_budget % cls._decorator_gig_tuning.gig_budget_modulo
            return gig_budget
        return 0

    def all_preferences_revealed(self):
        return len(self._known_client_preferences) == len(self._client_preferences)

    def reveal_client_preference(self, count=1):
        if self.all_preferences_revealed():
            return
        preferences_to_reveal = [item for item in self._client_preferences if item not in self._known_client_preferences]
        reveal_count = min(count, len(preferences_to_reveal))
        while reveal_count:
            random_index = random.randint(0, len(preferences_to_reveal) - 1)
            preference = preferences_to_reveal[random_index]
            self._known_client_preferences.append(preference)
            preferences_to_reveal.remove(preference)
            self.send_preferences_update(preference)
            reveal_count -= 1

    def replace_client_preference_by_category(self, category):
        temp_list = []
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        for pref_id in self._known_client_preferences:
            pref_trait = trait_manager.get(pref_id)
            if pref_trait and pref_trait.preference_category is category:
                temp_list.append(pref_trait)

        if not temp_list:
            return False
        else:
            original_pref_trait = random.choice(temp_list)
            candidate_list = preference_utils.get_preferences_by_category(category)
            temp_list.remove(original_pref_trait)
            candidate_list.remove(original_pref_trait)
            for pref in temp_list:
                for conflict_pref in pref.conflicting_traits:
                    candidate_list.remove(conflict_pref)

            for pref_id in self._client_preferences:
                pref_trait = trait_manager.get(pref_id)
                if pref_trait and pref_trait in candidate_list:
                    candidate_list.remove(pref_trait)

            return candidate_list or False
        new_pref_trait = random.choice(candidate_list)
        return self.replace_client_preference(original_pref_trait, new_pref_trait)

    def replace_client_preference(self, original_pref, new_pref):
        original_pref_id = original_pref.guid64
        if original_pref_id not in self._known_client_preferences:
            return False
        new_pref_id = new_pref.guid64
        self._client_preferences[self._client_preferences.index(original_pref_id)] = new_pref_id
        self._known_client_preferences[self._known_client_preferences.index(original_pref_id)] = new_pref_id
        self.send_preferences_update(new_pref_id)
        return True

    def send_preferences_update(self, revealed_preference_id):
        prefs_msg = DistributorOps_pb2.PreferencesUpdate()
        prefs_msg.career_uid = self.career.guid64
        prefs_msg.revealed_preference_id = revealed_preference_id
        prefs_msg.client_preferences.extend(self._client_preferences)
        prefs_msg.known_client_preferences.extend(self._known_client_preferences)
        op = GenericProtocolBufferOp(DistributorOps_pb2.Operation.PREFERENCES_UPDATE, prefs_msg)
        Distributor.instance().add_op(self._owner, op)
        self._owner.career_tracker.resend_career_data()

    def get_pay(self, **kwargs):
        return (super(ActiveGig, self).get_pay)(**kwargs)

    def update_budget_spent(self, amount):
        self._budget_spent_delta += -amount
        if self._budget_spent_delta < 0:
            self._gig_budget += -self._budget_spent_delta
            self._budget_spent_delta = 0
        msg = Sims_pb2.GigBudgetUpdate()
        msg.current_spent = self._budget_spent_delta
        msg.current_budget = self._gig_budget
        msg.vfx_amount = amount
        op = GenericProtocolBufferOp(DistributorOps_pb2.Operation.UPDATE_GIG_BUDGET, msg)
        Distributor.instance().add_op_with_no_owner(op)
        self._owner.career_tracker.resend_career_data()

    def _determine_gig_outcome(self, rabbit_hole=False, **kwargs):
        if self._decorator_gig_tuning is None:
            return
        self.calculate_gig_result(rabbit_hole=rabbit_hole)

    @property
    def gig_score(self):
        return self._gig_score

    @property
    def gig_result(self):
        if self._gig_result:
            return self._gig_result
        previous_gig_result = self._gig_result
        self.calculate_gig_result()
        ret_value = self._gig_result
        self._gig_result = previous_gig_result
        return ret_value

    def calculate_gig_result(self, rabbit_hole=False):
        if self._gig_result == GigResult.CANCELED:
            return
        else:
            self._gig_result = GigResult.SUCCESS
            if self._decorator_gig_tuning is None:
                return
                self._gig_score = self._decorator_gig_tuning.base_score
                if not self.has_attended_gig():
                    self._gig_result = GigResult.CRITICAL_FAILURE
                    return
                if rabbit_hole:
                    return
                trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
                total_likes_multiplier = 1 + self.get_gig_score_for_preferences([trait_manager.get(pref_id) for pref_id in self._client_preferences])
                final_budget_score = 0
                budget_used = self._budget_spent_delta * 100 / self._gig_budget
                if budget_used > 100:
                    final_budget_score = self._decorator_gig_tuning.budget_over_score
            else:
                for budget_score in self._decorator_gig_tuning.budget_scoring:
                    if budget_used < budget_score.max and budget_used >= budget_score.min:
                        final_budget_score = budget_score.score
                        break

        final_score = self._decorator_gig_tuning.base_score * total_likes_multiplier + final_budget_score
        self._gig_score = final_score
        for result_range in self._decorator_gig_tuning.scoring_results:
            if final_score < result_range.max and final_score >= result_range.min:
                self._gig_result = result_range.result_type
                return

    def get_gig_score_for_preferences(self, preferences_list, likes_value=1, dislikes_value=1):
        tags_modified = build_buy.get_gig_tag_changes(self._customer_lot_id)
        likes_changes = 0
        dislikes_changes = 0
        traits_changes = 0
        for preference_trait in preferences_list:
            if preference_trait is None:
                continue
            tags = preference_trait.preference_item.get_any_tags()
            if tags is not None:
                for tag in tags:
                    tag_index = [i for i, v in enumerate(tags_modified) if v[0] == tag]
                    if len(tag_index) > 0:
                        if preference_trait.trait_type == TraitType.LIKE:
                            likes_changes += tags_modified[tag_index[0]][1]
                        elif preference_trait.trait_type == TraitType.DISLIKE:
                            dislikes_changes += tags_modified[tag_index[0]][1]
                        else:
                            traits_changes += tags_modified[tag_index[0]][1]

        likes_multiplier = 1
        dislikes_multiplier = 1
        traits_multiplier = 1
        for score in self._decorator_gig_tuning.preference_scoring_weight:
            if score.trait_type == TraitType.LIKE:
                likes_multiplier = likes_changes * score.weight
            elif score.trait_type == TraitType.DISLIKE:
                dislikes_multiplier = dislikes_changes * score.weight
            else:
                traits_multiplier = traits_changes * score.weight

        final_value = likes_multiplier * likes_value
        final_value += dislikes_multiplier * dislikes_value
        if traits_multiplier > 1:
            final_value += traits_multiplier
        return final_value

    def calculate_gig_score_for_client_household(self, likes_value=1, dislikes_value=1):
        if self._decorator_gig_tuning is None or self._decorator_gig_tuning.individual_gig_score_stat is None:
            return
        client_sim_info = services.sim_info_manager().get(self._customer_id)
        for sim_info in client_sim_info.household._sim_infos:
            preferences = sim_info.trait_tracker.likes + sim_info.trait_tracker.dislikes
            score = self.get_gig_score_for_preferences(preferences, likes_value, dislikes_value)
            stat_tracker = sim_info.statistic_tracker
            if stat_tracker is not None:
                gig_statistic = stat_tracker.get_statistic(self._decorator_gig_tuning.individual_gig_score_stat)
                if gig_statistic is None:
                    gig_statistic = stat_tracker.add_statistic(self._decorator_gig_tuning.individual_gig_score_stat)
                if gig_statistic is not None:
                    gig_statistic.add_value(score)

    @classmethod
    def create_picker_row(cls, owner=None, gig_customer=None, gig_budget=None, enabled=True, **kwargs):
        if gig_customer is None:
            logger.error('create_picker row called for gig {} with no customer', cls)
            return
        customer_hh_name = gig_customer.household.name
        row_tooltip = None if cls.display_description is None else (lambda *_: cls.display_description(owner))
        now = services.time_service().sim_now
        duration = TimeSpan.ONE
        finishing_time = None
        scheduled_time = now + cls.get_time_until_next_possible_gig(now)
        for start_time, end_time in cls.gig_time().get_schedule_entries():
            duration = end_time - start_time
            finishing_time = scheduled_time + duration
            break

        if finishing_time == None:
            logger.error('Decorator Gig {} : No gig start_time found for scheduled_time {} ', cls, scheduled_time)
            return
        description = cls.gig_picker_localization_format(customer_hh_name, cls._decorator_gig_tuning.decorator_gig_type_icon.name(), scheduled_time, finishing_time)
        rarity_text = cls._decorator_gig_tuning.picker_localization_rarity(cls.gig_pay.lower_bound)
        second_rarity_text = cls._decorator_gig_tuning.picker_localization_second_rarity(gig_budget)
        row = ObjectPickerRow(name=(cls.display_name(owner)), icon=(cls.display_icon),
          row_description=description,
          row_tooltip=row_tooltip,
          rarity_text=rarity_text,
          second_rarity_text=second_rarity_text,
          flair_icon=(cls._decorator_gig_tuning.decorator_gig_type_icon.icon),
          flair_name=(cls._decorator_gig_tuning.decorator_gig_type_icon.name()),
          is_enable=enabled)
        row.tag_list = [cls._decorator_gig_tuning.decorator_gig_type]
        row.second_tag_list = [cls._decorator_gig_tuning.decorator_gig_lot_type]
        return row

    def clean_up_gig(self):
        super().clean_up_gig()
        services.get_zone_reservation_service().unreserve_zone(self, self._customer_lot_id)
        build_buy.unregister_build_buy_exit_callback(self.apply_new_object_tags)
        build_buy.unregister_build_buy_exit_callback(self.process_customer_lot_events)
        situation_manager = services.get_zone_situation_manager()
        decorator_sim = self._owner.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
        if decorator_sim:
            dependent_situations = situation_manager.get_situations_sim_is_in_by_tag(decorator_sim, self._decorator_gig_tuning.dependent_situation_tag)
            for situation in dependent_situations:
                situation_manager.destroy_situation_by_id(situation.id)

        if self._owner:
            if self._owner.career_tracker:
                self._owner.career_tracker.clear_photos_from_gig_history()

    def save_gig(self, gig_proto_buff):
        super().save_gig(gig_proto_buff)
        gig_proto_buff.client_preferences.extend(self._client_preferences)
        gig_proto_buff.known_client_preferences.extend(self._known_client_preferences)
        if self._client_hh_name is not None:
            gig_proto_buff.client_hh_name = self._client_hh_name
        gig_proto_buff.budget_spent = self._budget_spent_delta
        gig_proto_buff.gig_budget = self._gig_budget

    def load_gig(self, gig_proto_buff):
        super().load_gig(gig_proto_buff)
        if hasattr(gig_proto_buff, 'client_preferences'):
            self._client_preferences.extend(gig_proto_buff.client_preferences)
        if hasattr(gig_proto_buff, 'known_client_preferences'):
            self._known_client_preferences.extend(gig_proto_buff.known_client_preferences)
        if hasattr(gig_proto_buff, 'client_hh_name'):
            self._client_hh_name = gig_proto_buff.client_hh_name
        if hasattr(gig_proto_buff, 'budget_spent'):
            self._budget_spent_delta = gig_proto_buff.budget_spent
        if hasattr(gig_proto_buff, 'gig_budget'):
            self._gig_budget = gig_proto_buff.gig_budget
        self._reserve_gig_location()
        if self._customer_lot_id is not None:
            build_buy.register_build_buy_exit_callback(self.apply_new_object_tags)
            build_buy.register_build_buy_exit_callback(self.process_customer_lot_events)

    @flexmethod
    def build_gig_msg(cls, inst, msg, sim, gig_time=None, gig_extended_end_time=None, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        (super(__class__, inst_or_cls).build_gig_msg)(msg, sim, gig_time=gig_time, **kwargs)
        if gig_extended_end_time is not None:
            finishing_time = gig_extended_end_time
        else:
            finishing_time = None
            for start_time, end_time in inst_or_cls.gig_time().get_schedule_entries():
                duration = end_time - start_time
                finishing_time = gig_time + duration
                break

        msg.gig_end_time = finishing_time
        msg.client_preferences.extend(inst_or_cls._client_preferences)
        msg.known_client_preferences.extend(inst_or_cls._known_client_preferences)
        if inst_or_cls._client_hh_name is not None:
            msg.client_hh_name = inst_or_cls._client_hh_name
        if inst_or_cls._customer_lot_id is not None:
            msg.client_lot_id = inst_or_cls._customer_lot_id
        msg.budget_spent = inst_or_cls._budget_spent_delta
        msg.gig_budget = inst_or_cls._gig_budget
        msg.aspiration_id = inst_or_cls.gig_assignment_aspiration.guid64
        gig_tuning = inst_or_cls._decorator_gig_tuning
        if gig_tuning:
            if gig_tuning.restricted_to_level is not None:
                msg.use_level_restriction = True
                msg.level_restriction = gig_tuning.restricted_to_level.floor
            msg.tile_restriction = -1 if gig_tuning.tiles_number_restriction is None else gig_tuning.tiles_number_restriction

    def get_gig_history_key(self):
        customer_id = self.get_gig_customer()
        history_key = (customer_id, None)
        decorator_tuning = self.decorator_gig_tuning
        if decorator_tuning is not None:
            lot_type = decorator_tuning.decorator_gig_lot_type
            if lot_type == DecoratorGigLotType.COMMERCIAL:
                lot_id = self.get_customer_lot_id()
                history_key = (None, lot_id)
        return history_key

    @property
    def uses_gig_notifications_for_promotions(self):
        return False


lock_instance_tunables(DecoratorGig, additional_pay_per_overmax_level=None,
  gig_cast_rel_bit_collection_id=None,
  gig_cast=[],
  end_of_gig_overmax_notification=None,
  end_of_gig_overmax_rewardless_notification=None,
  odd_job_tuning=None)