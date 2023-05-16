# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\filters\location_based_filter_terms.py
# Compiled at: 2018-10-23 18:29:17
# Size of source mod 2**32: 1634 bytes
from filters.tunable import FilterTermVariant
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, OptionalTunable, TunableMapping
from snippets import define_snippet
from world.region import Region
import services

class LocationBasedFilterTerms(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'default_filter_terms':OptionalTunable(description='\n            Default filter terms to use if the current region is not specified.\n            ',
       tunable=TunableList(tunable=(FilterTermVariant())),
       disabled_value=()), 
     'region_to_filter_terms':TunableMapping(description='\n            A mapping of region to filter terms.\n            ',
       key_type=Region.TunableReference(pack_safe=True),
       value_type=TunableList(tunable=(FilterTermVariant())))}

    def get_filter_terms(self):
        region = services.current_region()
        if region in self.region_to_filter_terms:
            return self.region_to_filter_terms[region]
        return self.default_filter_terms


_, TunableLocationBasedFilterTermsSnippet = define_snippet('location_based_filter_terms', LocationBasedFilterTerms.TunableFactory())