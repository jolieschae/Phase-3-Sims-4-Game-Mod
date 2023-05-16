# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\outfits\outfit_tracker.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 31641 bytes
from _collections import defaultdict
from collections import namedtuple
import operator, random, weakref
from protocolbuffers import Outfits_pb2
from animation import get_throwaway_animation_context
from animation.animation_utils import create_run_animation, flush_all_animations
from animation.arb import Arb
from animation.asm import create_asm
from element_utils import build_critical_section
from event_testing.resolver import SingleSimResolver
from gsi_handlers import outfit_handlers
from objects import ALL_HIDDEN_REASONS
from sims.outfits.outfit_enums import OutfitCategory, NON_RANDOMIZABLE_OUTFIT_CATEGORIES, OutfitChangeReason, OutfitFilterFlag, SpecialOutfitIndex
from sims.outfits.outfit_tuning import OutfitTuning
from singletons import DEFAULT
import element_utils, services, sims4.log
logger = sims4.log.Logger('Outfits', default_owner='epanero')
OutfitPriority = namedtuple('OutfitPriority', ('change_reason', 'priority', 'interaction_ref'))

class OutfitTrackerMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._default_outfit_priorities = []
        self._randomize_daily = defaultdict((lambda: True))
        self._last_randomize = defaultdict((lambda: None))
        self._daily_defaults = {}
        self._outfit_dirty = set()

    def add_default_outfit_priority(self, interaction, outfit_change_reason, priority):
        interaction_ref = weakref.ref(interaction) if interaction is not None else None
        outfit_priority = OutfitPriority(outfit_change_reason, priority, interaction_ref)
        self._default_outfit_priorities.append(outfit_priority)
        return id(outfit_priority)

    def add_outfit(self, outfit_category: OutfitCategory, outfit_data):
        outfit_category, outfit_index = self._base.add_outfit(outfit_category, outfit_data)
        return (OutfitCategory(outfit_category), outfit_index)

    def can_switch_to_outfit(self, outfit_category_and_index) -> bool:
        if outfit_category_and_index is None:
            return False
        if self.outfit_is_dirty(outfit_category_and_index[0]):
            return True
        if self._current_outfit == outfit_category_and_index:
            return False
        return True

    def _get_random_daily_outfit(self, outfit_category):
        current_time = services.time_service().sim_now
        existing_default = outfit_category in self._daily_defaults
        last_randomize_time = self._last_randomize[outfit_category]
        if not existing_default or current_time.absolute_days() - last_randomize_time.absolute_days() >= 1 or current_time.day() != last_randomize_time.day():
            index = 0
            number_of_outfits = self.get_number_of_outfits_in_category(outfit_category)
            if number_of_outfits > 1:
                if existing_default:
                    index = random.randrange(number_of_outfits - 1)
                    exclusion = self._daily_defaults[outfit_category]
                    if index >= exclusion:
                        index += 1
                else:
                    index = random.randrange(number_of_outfits)
            self._daily_defaults[outfit_category] = index
            self._last_randomize[outfit_category] = current_time
        return (
         outfit_category, self._daily_defaults[outfit_category])

    def generate_unpopulated_outfits(self, outfit_categories):
        for outfit_category in outfit_categories:
            if not self.has_outfit((outfit_category, 0)):
                self.generate_outfit(outfit_category=outfit_category)

    def handle_regional_outfits(self):
        if self.is_pet:
            return
        else:
            region_instance = services.current_region()
            restrictions = region_instance.outfit_category_restrictions
            if restrictions.travel_groups_only:
                if not self.is_in_travel_group():
                    return
            required_outfit_category = restrictions.required_outfit_category
            if required_outfit_category is not None:
                required_outfit_category.generate_outfit(self)
            restrictions.allowed_outfits.test_item(self.get_current_outfit()[0]) or self.set_current_outfit((region_instance.default_outfit_category, 0))

    def handle_career_outfits(self):
        sim = self.get_sim_info()
        for career in sim.careers.values():
            if career.has_outfit():
                sim.has_outfit((OutfitCategory.CAREER, 0)) or career.generate_outfit()
                return

    def get_all_outfit_entries(self):
        for outfit_category in OutfitCategory:
            if outfit_category == OutfitCategory.CURRENT_OUTFIT:
                continue
            for outfit_index in range(self.get_number_of_outfits_in_category(outfit_category)):
                yield (
                 outfit_category, outfit_index)

    def get_all_outfits(self):
        for outfit_category in OutfitCategory:
            if outfit_category == OutfitCategory.CURRENT_OUTFIT:
                continue
            yield (
             outfit_category, self.get_outfits_in_category(outfit_category))

    def get_change_outfit_element(self, outfit_category_and_index, do_spin=True, interaction=None):

        def change_outfit(timeline):
            arb = Arb()
            self.try_set_current_outfit(outfit_category_and_index, do_spin=do_spin, arb=arb, interaction=interaction)
            if not arb.empty:
                clothing_element = create_run_animation(arb)
                yield from element_utils.run_child(timeline, clothing_element)
            if False:
                yield None

        return change_outfit

    def get_change_outfit_element_and_archive_change_reason(self, outfit_category_and_index, do_spin=True, interaction=None, change_reason=None):
        if outfit_handlers.archiver.enabled:
            outfit_handlers.log_outfit_change(self.get_sim_info(), outfit_category_and_index, change_reason)
        return self.get_change_outfit_element(outfit_category_and_index, do_spin, interaction)

    def get_default_outfit(self, interaction=None, resolver=None):
        default_outfit = OutfitPriority(None, 0, None)
        if self._default_outfit_priorities:
            default_outfit = max((self._default_outfit_priorities), key=(operator.attrgetter('priority')))
        if interaction is not None or resolver is not None:
            return self.get_outfit_for_clothing_change(interaction, (default_outfit.change_reason), resolver=resolver)
        if default_outfit.interaction_ref() is not None:
            return self.get_outfit_for_clothing_change(default_outfit.interaction_ref(), default_outfit.change_reason)
        return self._current_outfit

    def get_next_outfit_for_category(self, outfit_category):
        return (
         outfit_category, self.get_number_of_outfits_in_category(outfit_category))

    def get_number_of_outfits_in_category(self, outfit_category):
        return len(self.get_outfits_in_category(outfit_category))

    def get_outfit(self, outfit_category: OutfitCategory, outfit_index: int):
        if not self.has_outfit((outfit_category, outfit_index)):
            self.generate_outfit(outfit_category, outfit_index)
        try:
            return self._base.get_outfit(outfit_category, outfit_index)
        except RuntimeError as exception:
            try:
                logger.callstack("Exception '{}' encountered in get_outfit", exception,
                  level=(sims4.log.LEVEL_ERROR))
                return
            finally:
                exception = None
                del exception

    def get_outfit_change(self, interaction, change_reason, resolver=None, **kwargs):
        if change_reason is not None:
            outfit_category_and_index = self.get_outfit_for_clothing_change(interaction, change_reason, resolver=resolver)
            if outfit_category_and_index is not None:
                return build_critical_section((self.get_change_outfit_element_and_archive_change_reason)(
 outfit_category_and_index, interaction=interaction, change_reason=change_reason, **kwargs), flush_all_animations)

    def get_outfit_for_clothing_change(self, interaction, reason, resolver=None):
        for trait in self.get_traits():
            reason = trait.get_outfit_change_reason(reason)

        if reason == OutfitChangeReason.Invalid:
            return self._current_outfit
        if reason == OutfitChangeReason.DefaultOutfit:
            return self.get_default_outfit(interaction=interaction, resolver=resolver)
        if reason == OutfitChangeReason.PreviousClothing:
            return self._previous_outfit
        if reason == OutfitChangeReason.RandomOutfit:
            return self.get_random_outfit()
        if reason == OutfitChangeReason.CurrentOutfit:
            return self._current_outfit
        if reason == OutfitChangeReason.FashionOutfit:
            return self.get_special_fashion_outfit()
        if reason == OutfitChangeReason.ExitBedNPC:
            if self.is_npc:
                return self._previous_outfit
            return
        resolver_to_use = resolver or interaction.get_resolver()
        outfit_change = None
        if reason in OutfitTuning.OUTFIT_CHANGE_REASONS:
            test_group_and_outfit_list = OutfitTuning.OUTFIT_CHANGE_REASONS[reason]
            for test_group_and_outfit in test_group_and_outfit_list:
                outfit_category = test_group_and_outfit.outfit_category
                if outfit_category == OutfitCategory.BATHING:
                    if not self.has_outfit_category(OutfitCategory.BATHING):
                        self.generate_outfit((OutfitCategory.BATHING), filter_flag=(OutfitFilterFlag.NONE))
                if outfit_category != OutfitCategory.CURRENT_OUTFIT:
                    if interaction is not None:
                        if not (hasattr(interaction, 'career_uid') and interaction.career_uid):
                            if not self.has_outfit_category(outfit_category):
                                continue
                if test_group_and_outfit.tests:
                    if test_group_and_outfit.tests.run_tests(resolver_to_use):
                        if test_group_and_outfit.outfit_category == OutfitCategory.CURRENT_OUTFIT or test_group_and_outfit.outfit_category == self._current_outfit[0]:
                            outfit_change = self._current_outfit
                        else:
                            if self._previous_outfit == (OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION):
                                outfit_change = self.get_special_fashion_outfit()
                            else:
                                if self._randomize_daily[outfit_category]:
                                    outfit_change = self._get_random_daily_outfit(outfit_category)
                                else:
                                    outfit_change = (
                                     outfit_category, 0)
                    break

        if outfit_change is None:
            outfit_change = (
             OutfitCategory.EVERYDAY, 0)
        outfit_change = self._run_weather_fixup(reason, outfit_change, resolver_to_use)
        outfit_change = self._run_career_fixup(outfit_change, interaction)
        outfit_change = self._run_fashion_fixup(outfit_change)
        return outfit_change

    def _run_weather_fixup(self, reason, outfit_change, resolver):
        weather_service = services.weather_service()
        if weather_service is None:
            return outfit_change
        else:
            sim = self.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if sim is None:
                return outfit_change
            weather_outfit_change = weather_service.get_weather_outfit_change(resolver, reason=reason)
            if weather_outfit_change is None:
                return outfit_change
            return sim.is_outside or outfit_change
        if reason in weather_service.WEATHER_OUFTIT_CHANGE_REASONS_TO_IGNORE:
            return outfit_change
        return weather_outfit_change

    def _run_career_fixup--- This code section failed: ---

 L. 412         0  LOAD_FAST                'self'
                2  LOAD_ATTR                get_sim_instance
                4  LOAD_GLOBAL              ALL_HIDDEN_REASONS
                6  LOAD_CONST               ('allow_hidden_flags',)
                8  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               10  STORE_FAST               'sim'

 L. 415        12  LOAD_FAST                'sim'
               14  LOAD_CONST               None
               16  COMPARE_OP               is
               18  POP_JUMP_IF_FALSE    24  'to 24'

 L. 416        20  LOAD_FAST                'outfit_change'
               22  RETURN_VALUE     
             24_0  COME_FROM            18  '18'

 L. 419        24  LOAD_FAST                'self'
               26  LOAD_ATTR                _career_tracker
               28  LOAD_METHOD              has_part_time_career_outfit
               30  CALL_METHOD_0         0  '0 positional arguments'
               32  POP_JUMP_IF_TRUE     48  'to 48'
               34  LOAD_FAST                'self'
               36  LOAD_ATTR                _career_tracker
               38  LOAD_METHOD              has_school_outfit
               40  CALL_METHOD_0         0  '0 positional arguments'
               42  POP_JUMP_IF_TRUE     48  'to 48'

 L. 420        44  LOAD_FAST                'outfit_change'
               46  RETURN_VALUE     
             48_0  COME_FROM            42  '42'
             48_1  COME_FROM            32  '32'

 L. 422        48  LOAD_FAST                'outfit_change'
               50  LOAD_CONST               0
               52  BINARY_SUBSCR    
               54  LOAD_GLOBAL              OutfitCategory
               56  LOAD_ATTR                CAREER
               58  COMPARE_OP               !=
               60  POP_JUMP_IF_TRUE     90  'to 90'

 L. 423        62  LOAD_FAST                'interaction'
               64  LOAD_CONST               None
               66  COMPARE_OP               is
               68  POP_JUMP_IF_TRUE     90  'to 90'

 L. 424        70  LOAD_GLOBAL              hasattr
               72  LOAD_FAST                'interaction'
               74  LOAD_STR                 'career_uid'
               76  CALL_FUNCTION_2       2  '2 positional arguments'
               78  POP_JUMP_IF_FALSE    90  'to 90'

 L. 425        80  LOAD_FAST                'interaction'
               82  LOAD_ATTR                career_uid
               84  LOAD_CONST               None
               86  COMPARE_OP               ==
               88  POP_JUMP_IF_FALSE    94  'to 94'
             90_0  COME_FROM            78  '78'
             90_1  COME_FROM            68  '68'
             90_2  COME_FROM            60  '60'

 L. 426        90  LOAD_FAST                'outfit_change'
               92  RETURN_VALUE     
             94_0  COME_FROM            88  '88'

 L. 428        94  LOAD_FAST                'interaction'
               96  LOAD_ATTR                career_uid
               98  LOAD_CONST               None
              100  COMPARE_OP               is-not
              102  POP_JUMP_IF_FALSE   176  'to 176'

 L. 430       104  LOAD_FAST                'self'
              106  LOAD_METHOD              remove_outfits_in_category
              108  LOAD_GLOBAL              OutfitCategory
              110  LOAD_ATTR                CAREER
              112  CALL_METHOD_1         1  '1 positional argument'
              114  POP_TOP          

 L. 432       116  LOAD_FAST                'self'
              118  LOAD_ATTR                _career_tracker
              120  LOAD_METHOD              get_career_by_uid
              122  LOAD_FAST                'interaction'
              124  LOAD_ATTR                career_uid
              126  CALL_METHOD_1         1  '1 positional argument'
              128  STORE_FAST               'career'

 L. 433       130  LOAD_FAST                'career'
              132  LOAD_METHOD              generate_outfit
              134  CALL_METHOD_0         0  '0 positional arguments'
              136  POP_TOP          

 L. 434       138  LOAD_FAST                'self'
              140  LOAD_METHOD              has_outfit_category
              142  LOAD_GLOBAL              OutfitCategory
              144  LOAD_ATTR                CAREER
              146  CALL_METHOD_1         1  '1 positional argument'
              148  POP_JUMP_IF_TRUE    162  'to 162'

 L. 438       150  LOAD_GLOBAL              OutfitCategory
              152  LOAD_ATTR                EVERYDAY
              154  LOAD_CONST               0
              156  BUILD_TUPLE_2         2 
              158  STORE_FAST               'career_outfit_change'
              160  JUMP_FORWARD        172  'to 172'
            162_0  COME_FROM           148  '148'

 L. 440       162  LOAD_GLOBAL              OutfitCategory
              164  LOAD_ATTR                CAREER
              166  LOAD_CONST               0
              168  BUILD_TUPLE_2         2 
              170  STORE_FAST               'career_outfit_change'
            172_0  COME_FROM           160  '160'

 L. 441       172  LOAD_FAST                'career_outfit_change'
              174  RETURN_VALUE     
            176_0  COME_FROM           102  '102'

 L. 443       176  LOAD_FAST                'outfit_change'
              178  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `RETURN_VALUE' instruction at offset 178

    def _run_fashion_fixup(self, outfit_change):
        if self._previous_outfit == (OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION):
            return self._previous_outfit
        return outfit_change

    def get_outfits_in_category(self, outfit_category: OutfitCategory):
        return self._base.get_outfits_in_category(outfit_category)

    def get_random_outfit(self, outfit_categories=()):
        valid_outfits = []
        for outfit_category, outfit_index in self.get_all_outfit_entries():
            if outfit_categories:
                if outfit_category not in outfit_categories:
                    continue
            if outfit_category == OutfitCategory.CURRENT_OUTFIT:
                continue
            if outfit_category in NON_RANDOMIZABLE_OUTFIT_CATEGORIES:
                continue
            valid_outfits.append((outfit_category, outfit_index))

        if valid_outfits:
            return random.choice(valid_outfits)
        if self.occult_tracker is None:
            return (
             OutfitCategory.EVERYDAY, 0)
        return (
         self.occult_tracker.get_fallback_outfit_category(self.current_occult_types), 0)

    def get_special_fashion_outfit(self):
        if self.has_outfit_category(OutfitCategory.SPECIAL):
            return (
             OutfitCategory.SPECIAL, SpecialOutfitIndex.FASHION)
        return self._current_outfit

    def get_sim_info(self):
        return self

    def has_outfit(self, outfit):
        return self._base.has_outfit(outfit[0], outfit[1])

    def has_outfit_category(self, outfit_category):
        return self.has_outfit((outfit_category, 0))

    def has_cas_part(self, cas_part):
        try:
            outfit = (self._base.get_outfit)(*self._current_outfit)
            if outfit is None:
                return False
            return cas_part in outfit.part_ids
        except RuntimeError as exception:
            try:
                logger.callstack("Exception '{}' encountered in has_cas_part: ", exception,
                  level=(sims4.log.LEVEL_ERROR))
                return False
            finally:
                exception = None
                del exception

    def is_wearing_outfit(self, category_and_index):
        if self.outfit_is_dirty(category_and_index[0]):
            return False
        return self._current_outfit == category_and_index

    def load_outfits(self, outfit_msg):
        self._base.outfits = outfit_msg.SerializeToString()

    def remove_default_outfit_priority(self, outfit_priority_id):
        for index, value in enumerate(self._default_outfit_priorities):
            if id(value) == outfit_priority_id:
                self._default_outfit_priorities.pop(index)
                break

    def remove_outfit(self, outfit_category: OutfitCategory, outfit_index: int=DEFAULT):
        outfit_index = self.get_number_of_outfits_in_category(outfit_category) - 1 if outfit_index is DEFAULT else outfit_index
        return self._base.remove_outfit(outfit_category, outfit_index)

    def remove_outfits_in_category(self, outfit_category: OutfitCategory):
        while self.has_outfit((outfit_category, 0)):
            self.remove_outfit(outfit_category, 0)

    def remove_all_but_one_outfit_in_category(self, outfit_category: OutfitCategory):
        while self.has_outfit((outfit_category, 1)):
            self.remove_outfit(outfit_category, 1)

    def clear_outfits_to_minimum(self):
        for outfit_category, _ in self.get_all_outfits():
            if outfit_category is OutfitCategory.EVERYDAY:
                self.remove_all_but_one_outfit_in_category(outfit_category)
            else:
                self.remove_outfits_in_category(outfit_category)

    def save_outfits(self):
        outfits_msg = Outfits_pb2.OutfitList()
        outfits_msg.ParseFromString(self._base.outfits)
        return outfits_msg

    def set_outfit_flags(self, outfit_category: OutfitCategory, outfit_index: int, outfit_flags: int):
        outfit_flags_low = int(outfit_flags & 18446744073709551615)
        outfit_flags_high = int(outfit_flags >> 64 & 18446744073709551615)
        return self._base.set_outfit_flags(outfit_category, outfit_index, outfit_flags_low, outfit_flags_high)

    def _apply_on_outfit_changed_loot(self):
        is_sim = getattr(self, 'is_sim', False)
        if is_sim:
            resolver = SingleSimResolver(self)
            for loot_action in OutfitTuning.LOOT_ON_OUTFIT_CHANGE:
                loot_action.apply_to_resolver(resolver)

    def try_set_current_outfit(self, outfit_category_and_index, do_spin=False, arb=None, interaction=None):
        sim = self.get_sim_instance()
        if sim is None:
            do_spin = False
        elif arb is None:
            logger.error('Must pass in a valid ARB for the clothing spin.')
            do_spin = False
        elif self.can_switch_to_outfit(outfit_category_and_index):
            if do_spin:
                did_change = False

                def set_ending(*_, **__):
                    nonlocal did_change
                    if not did_change:
                        laundry_service = services.get_laundry_service()
                        if laundry_service is not None:
                            laundry_service.on_spin_outfit_change(sim, outfit_category_and_index, interaction)
                        if self.set_current_outfit(outfit_category_and_index):
                            self._apply_on_outfit_changed_loot()
                        did_change = True

                arb.register_event_handler(set_ending, handler_id=100)
                if sim is not None:
                    animation_element_tuning = OutfitTuning.OUTFIT_CHANGE_ANIMATION
                    clothing_context = get_throwaway_animation_context()
                    clothing_change_asm = create_asm((animation_element_tuning.asm_key), context=clothing_context)
                    clothing_change_asm.update_locked_params(sim.get_transition_asm_params())
                    result = sim.posture.setup_asm_interaction(clothing_change_asm, sim, None, animation_element_tuning.actor_name, None)
                    sim.set_trait_asm_parameters(clothing_change_asm, animation_element_tuning.actor_name)
                    if not result:
                        logger.error('Could not setup asm for Clothing Change. {}', result)
                    clothing_change_asm.request(animation_element_tuning.begin_states[0], arb)
            elif self.set_current_outfit(outfit_category_and_index):
                self._apply_on_outfit_changed_loot()

    def set_outfit_dirty(self, outfit_category):
        self._outfit_dirty.add(outfit_category)

    def clear_outfit_dirty(self, outfit_category):
        self._outfit_dirty.discard(outfit_category)

    def outfit_is_dirty(self, outfit_category):
        if outfit_category in self._outfit_dirty:
            return True
        return False