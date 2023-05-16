# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cas\cas_stories_trait_chooser.py
# Compiled at: 2019-04-15 19:49:39
# Size of source mod 2**32: 1701 bytes
import services, sims4
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableMapping
from sims4.tuning.tunable_base import ExportModes
from traits.traits import Trait

class CasStoriesTraitChooser(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.CAS_STORIES_TRAIT_CHOOSER)):
    INSTANCE_TUNABLES = {'traits': TunableMapping(description='\n            A mapping between the weighting value and the trait that will be\n            assigned. The keys of this map are thresholds. Example: if the\n            desired behavior would be to assign trait_a if the weighting w is \n            between 0.0 and 1.0 and trait_b if w > 1.0, then this map should \n            have two entries: (0.0, trait_a), (1.0, trait_b). The weighting of \n            the lowest weighted trait should always be 0.0, and a weighting of\n            0.0 will always select the lowest trait by convention (although the\n            thresholds are otherwise non-inclusive).\n            ',
                 key_type=float,
                 value_type=(Trait.TunableReference()),
                 key_name='weighting_threshold',
                 value_name='trait_to_assign',
                 tuple_name='CasStoriesTraitChooserThresholds',
                 minlength=1,
                 export_modes=(
                ExportModes.ClientBinary,))}