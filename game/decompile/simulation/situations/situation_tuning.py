# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_tuning.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 4582 bytes
import services, sims4.resources, sims4.tuning.instances
from interactions.utils.tunable_icon import TunableIcon
from sims.outfits.outfit_enums import OutfitCategory
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableMapping, TunableEnumWithFilter, TunableTuple, Tunable, OptionalTunable, TunableReference, TunableEnumEntry
from tag import Tag

class SituationStyleData(metaclass=sims4.tuning.instances.HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SNIPPET)):
    INSTANCE_TUNABLES = {'cas_edit_job':OptionalTunable(description='\n            If enabled, shows up to two Sims from a specific job and allows taking them in to CAS.\n            ',
       tunable=TunableTuple(description='\n                The job to show in the UI and the outfit category the Sim should be shown in.\n                ',
       job=TunableReference(description='\n                    This is the Situation Job that can be edited in CAS. Currently, the UI only supports up to 2 Sims in\n                    this job.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB))),
       outfit_category=TunableEnumEntry(description='\n                    The outfit the Sim will wear in the UI. This is also the outfit that will be targeted when in CAS.\n                    ',
       tunable_type=OutfitCategory,
       default=(OutfitCategory.EVERYDAY),
       invalid_enums=(
      OutfitCategory.CURRENT_OUTFIT,)),
       no_sim_selected_icon=TunableIcon(description='\n                    The icon to show in place of a Sim if no Sim has been selected for the tuned Job.\n                    '))), 
     'customizable_guest_attire':OptionalTunable(description='\n            If enabled, allows customizing the guest attire for a Situation.\n            ',
       tunable=TunableTuple(description='\n                Color and Style tuning for the guest attire.\n                ',
       color_map=TunableMapping(description='\n                    A mapping from CAS tags to LocalizedStrings representing available colors for Situation guest attire.\n                    ',
       key_type=TunableEnumWithFilter(description='\n                        A color tag used to find matching CAS parts for the Guests.\n                        ',
       tunable_type=Tag,
       default=(Tag.INVALID),
       filter_prefixes=('color', ),
       pack_safe=True),
       value_type=TunableTuple(description='\n                        The name and hex value for the color.\n                        ',
       color_name=TunableLocalizedString(description='\n                            The name of the Color.\n                            '),
       color_value=Tunable(description='\n                            The hex value of the color.\n                            ',
       tunable_type=str,
       default='ffffffff'))),
       style_map=TunableMapping(description='\n                    A mapping from CAS tags to LocalizedStrings shown in the Situation Creation UI for choosing attire style.\n                    ',
       key_type=TunableEnumWithFilter(description='\n                        The style tag of the CAS parts associated with this style.\n                        ',
       tunable_type=Tag,
       default=(Tag.INVALID),
       filter_prefixes=('style', ),
       invalid_enums=(
      Tag.INVALID,)),
       value_type=TunableLocalizedString(description='\n                        The display name for this style. Shown in a dropdown in the Situation Creation UI.\n                        '))))}