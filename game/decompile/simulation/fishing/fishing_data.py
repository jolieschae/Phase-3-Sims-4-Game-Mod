# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fishing\fishing_data.py
# Compiled at: 2021-09-01 13:58:18
# Size of source mod 2**32: 9642 bytes
from collections import namedtuple
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple, TunableReference, TunableRange
from snippets import define_snippet
from tunable_multiplier import TunableMultiplier
import services, sims4.log
logger = sims4.log.Logger('Fishing', default_owner='TrevorLindsey')

class FishingDataBase:

    def get_possible_fish_gen(self):
        yield from self.possible_fish
        if False:
            yield None

    def choose_fish(self, resolver, require_bait=True):
        weighted_fish = [(f.weight.get_multiplier(resolver), f.fish) for f in self.possible_fish if f.fish.cls.can_catch(resolver, require_bait=require_bait)]
        if weighted_fish:
            return sims4.random.weighted_random_item(weighted_fish)

    def choose_treasure(self, resolver):
        weighted_treasures = [(t.weight.get_multiplier(resolver), t.treasure) for t in self.possible_treasures]
        if weighted_treasures:
            return sims4.random.weighted_random_item(weighted_treasures)


class TunedFishingData(FishingDataBase, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'weight_fish':TunableMultiplier.TunableFactory(description='\n            A tunable list of tests and multipliers to apply to the weight \n            used to determine if the Sim will catch a fish instead of treasure \n            or junk. This will be used in conjunction with the Weight Junk and \n            Weight Treasure.\n            '), 
     'weight_junk':TunableMultiplier.TunableFactory(description='\n            A tunable list of tests and multipliers to apply to the weight\n            used to determine if the Sim will catch junk instead of a fish or \n            treasure. This will be used in conjunction with the Weight Fish and \n            Weight Treasure.\n            '), 
     'weight_treasure':TunableMultiplier.TunableFactory(description='\n            A tunable list of tests and multipliers to apply to the weight\n            used to determine if the Sim will catch a treasure instead of fish \n            or junk. This will be used in conjunction with the Weight Fish and \n            Weight Junk.\n            '), 
     'possible_treasures':TunableList(description="\n            If the Sim catches a treasure, we'll pick one of these based on their weights.\n            Higher weighted treasures have a higher chance of being caught.\n            ",
       tunable=TunableTuple(treasure=TunableReference(manager=(services.definition_manager()), pack_safe=True),
       weight=(TunableMultiplier.TunableFactory()))), 
     'possible_fish':TunableList(description="\n            If the Sim catches a fish, we'll pick one of these based on their weights.\n            Higher weighted fish have a higher chance of being caught.\n            ",
       tunable=TunableTuple(fish=TunableReference(manager=(services.definition_manager()),
       pack_safe=True),
       weight=(TunableMultiplier.TunableFactory())))}

    def _verify_tuning_callback(self):
        import fishing.fish_object
        for fish in self.possible_fish:
            if not issubclass(fish.fish.cls, fishing.fish_object.Fish):
                logger.error("Possible Fish on Fishing Data has been tuned but there either isn't a definition tuned for the fish, or the definition currently tuned is not a Fish.\n{}", self)


TunableFishingDataReference, TunableFishingDataSnippet = define_snippet('fishing_data', TunedFishingData.TunableFactory())
PossibleFish = namedtuple('PossibleFish', 'fish, weight')

class DynamicFishingData(FishingDataBase):

    def __init__(self, tuned_fishing_data, owner):
        self.possible_fish = [PossibleFish(possible_fish.fish, possible_fish.weight) for possible_fish in tuned_fishing_data.possible_fish]
        self.weight_fish = tuned_fishing_data.weight_fish
        self.weight_junk = tuned_fishing_data.weight_junk
        self.weight_treasure = tuned_fishing_data.weight_treasure
        self.possible_treasures = tuned_fishing_data.possible_treasures
        self.owner = owner
        self._tuned_fishing_data = tuned_fishing_data

    def _get_fish_catch_multiplier(self, fish):
        weight = fish.cls.catch_multiplier
        for tuned_possible_fish_info in self._tuned_fishing_data.possible_fish:
            if tuned_possible_fish_info.fish is fish:
                weight = tuned_possible_fish_info.weight
                break

        return weight

    def add_possible_fish(self, fish_definitions, should_sync_pond=True):
        for fish in fish_definitions:
            if fish not in [possible_fish.fish for possible_fish in self.possible_fish]:
                self.possible_fish.append(PossibleFish(fish, self._get_fish_catch_multiplier(fish)))

        if not should_sync_pond:
            return
        associated_pond_obj = self.owner.fishing_location_component.associated_pond_obj
        if associated_pond_obj is not None:
            associated_pond_obj.update_and_sync_fish_data(fish_definitions, (self.owner), is_add=True)

    def remove_possible_fish(self, fish_definitions, should_sync_pond=True):
        self.possible_fish = [fish_info for fish_info in self.possible_fish if fish_info.fish not in fish_definitions]
        if not should_sync_pond:
            return
        associated_pond_obj = self.owner.fishing_location_component.associated_pond_obj
        if associated_pond_obj is not None:
            associated_pond_obj.update_and_sync_fish_data(fish_definitions, (self.owner), is_add=False)

    def save(self, msg):
        msg.possible_fish_ids.extend((f.fish.id for f in self.possible_fish))

    def load(self, persistable_data):
        self.possible_fish = []
        for possible_fish_id in persistable_data.possible_fish_ids:
            fish = services.definition_manager().get(possible_fish_id)
            if fish is None:
                continue
            self.possible_fish.append(PossibleFish(fish, self._get_fish_catch_multiplier(fish)))


class FishingBait(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'bait_name':TunableLocalizedStringFactory(description='\n            Name of fishing bait.\n            '), 
     'bait_description':TunableLocalizedStringFactory(description='\n            Description of fishing bait.\n            '), 
     'bait_icon_definition':TunableReference(description='\n            Object definition that will be used to render icon of fishing bait.\n            ',
       manager=services.definition_manager()), 
     'bait_buff':TunableReference(description='\n            Buff of fishing bait.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.BUFF)), 
     'bait_priority':TunableRange(description='\n            The priority of the bait. When an object can be categorized into\n            multiple fishing bait categories, the highest priority category \n            will be chosen.\n            ',
       tunable_type=int,
       default=1,
       minimum=1)}


TunableFishingBaitReference, _ = define_snippet('fishing_bait', FishingBait.TunableFactory())