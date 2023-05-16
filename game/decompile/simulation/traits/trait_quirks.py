# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\trait_quirks.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 8252 bytes
import random
from sims.sim_info_types import Age
from sims4.random import pop_weighted
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableTuple, TunableReference, TunableRange, TunableMapping, TunableInterval, Tunable, TunableVariant, TunedInterval, OptionalTunable, TunableEnumEntry
import services, sims4.math, sims4.resources

class _QuirkCountFixed(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'count': Tunable(description='\n            The Sim is going to receive these many quirks from this set.\n            ',
                tunable_type=int,
                default=1)}

    def __call__(self, sim_info, random):
        return self.count


class _QuirkCountDynamic(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'interval':TunableInterval(description='\n            The Sim is going to receive between these many quirks from this set.\n            ',
       tunable_type=int,
       default_lower=0,
       default_upper=1,
       minimum=0), 
     'trait_modifiers':TunableMapping(description='\n            If the Sim is equipped with this trait, the available number of\n            quirks is modified accordingly.\n            \n            NOTE: You can specify negative values to subtract from the count.\n            ',
       key_type=TunableReference(description='\n                The Sim must have this trait in order for the modifier to be\n                applied.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       value_type=TunableTuple(lower_bound_modifier=Tunable(description='\n                    The lower bound of the available quirk count is modified by\n                    this amount.\n                    ',
       tunable_type=int,
       default=1),
       upper_bound_modifier=Tunable(description='\n                    The upper bound of the available quirk count is modified by\n                    this amount.\n                    ',
       tunable_type=int,
       default=1)))}

    def __call__(self, sim_info, random):
        interval = self.interval
        for trait, modifier in self.trait_modifiers.items():
            if sim_info.has_trait(trait):
                interval = TunedInterval(interval.lower_bound + modifier.lower_bound_modifier, interval.upper_bound + modifier.upper_bound_modifier)

        if interval.lower_bound > interval.upper_bound:
            return interval.lower_bound
        return random.randint(interval.lower_bound, interval.upper_bound)


class TraitQuirkSet(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'_quirk_sets': TunableList(description='\n            A list of all the quirk sets for this Sim. One quirk from each set\n            is assigned.\n            ',
                      tunable=TunableTuple(count=TunableVariant(description='\n                    Define how many quirks from this set the Sim is supposed to\n                    receive.\n                    ',
                      fixed=(_QuirkCountFixed.TunableFactory()),
                      dynamic=(_QuirkCountDynamic.TunableFactory()),
                      default='fixed'),
                      entries=TunableList(description='\n                    A quirk set. This Sim is guaranteed to have one and only one of\n                    the quirks tuned here.\n                    ',
                      tunable=TunableTuple(description='\n                        A quirk entry. The weight is relative to other quirks in\n                        this set.\n                        ',
                      quirk_trait=TunableReference(description='\n                            The trait representing this quirk.\n                            ',
                      manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
                      pack_safe=True),
                      quirk_relative_weight=TunableRange(description='\n                            The likelihood that this quirk is assigned relative to\n                            other quirks in this quirk set.\n                            ',
                      tunable_type=float,
                      default=1,
                      minimum=(sims4.math.EPSILON)))),
                      required_age=OptionalTunable(description='\n                    If tuned the quirks will require a specific age.    \n                    ',
                      tunable=TunableEnumEntry(description='\n                        The age required\n                        ',
                      tunable_type=Age,
                      default=(Age.ADULT)))))}

    def add_quirks(self, sim_info):
        if not self._quirk_sets:
            return
        trait_tracker = sim_info.trait_tracker
        r = random.Random(sim_info.sim_id)
        for quirk_set in self._quirk_sets:
            if quirk_set.required_age:
                if sim_info.age != quirk_set.required_age:
                    continue
            quirk_count = quirk_set.count(sim_info, r)
            quirk_count_current = sum((1 for entry in quirk_set.entries if sim_info.has_trait(entry.quirk_trait)))
            if quirk_count_current >= quirk_count:
                continue
            allowed_entries = [(entry.quirk_relative_weight, entry.quirk_trait) for entry in quirk_set.entries if trait_tracker.can_add_trait(entry.quirk_trait)]
            while allowed_entries:
                if quirk_count_current >= quirk_count:
                    break
                quirk_trait = pop_weighted(allowed_entries, random=r)
                if sim_info.add_trait(quirk_trait):
                    quirk_count_current += 1


def add_quirks(sim_info):
    sim_definition = sim_info.get_sim_definition(sim_info.extended_species)
    sim_definition._cls.trait_quirks.add_quirks(sim_info)