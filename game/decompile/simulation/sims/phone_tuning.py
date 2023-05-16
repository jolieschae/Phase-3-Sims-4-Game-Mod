# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\phone_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3655 bytes
from event_testing.tests import TunableTestVariant
from interactions.utils.tunable_icon import TunableIcon
from sims4.common import Pack
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunableTuple, TunableList, TunableReference, TunableEnumSet
from sims4.tuning.tunable_base import ExportModes
import services, sims4.resources

class PhoneTuning:
    DISABLE_PHONE_TESTS = TunableList(description='\n        List of tests and tooltip that when passed will disable opening the\n        phone.\n        ',
      tunable=TunableTuple(description='\n            Test that should pass for the phone to be disabled and its tooltip\n            to display to the player when he clicks on the phone.\n            ',
      test=(TunableTestVariant()),
      tooltip=(TunableLocalizedStringFactory())))

    class TunablePhoneBackgroundColorTuple(TunableTuple):

        def __init__(self, *args, **kwargs):
            (super().__init__)(args, bg_image=TunableIcon(description='\n                    Image resource to display as UI phone panel background.\n                    ', pack_safe=True), icon=TunableIcon(description='\n                    Icon to display for phone color selector swatch.\n                    '), required_packs=TunableEnumSet(description='\n                    If any packs are tuned here, at least one of them must\n                    be present for this option to appear in the selector.\n                    If none are tuned, it will always appear.\n                    ', enum_type=Pack, enum_default=(Pack.BASE_GAME)), **kwargs)

    class TunablePhoneCaseTuple(TunableTuple):

        def __init__(self, *args, **kwargs):
            (super().__init__)(args, icon=TunableIcon(description='\n                    Icon to display for phone color selector swatch.\n                    '), trait=TunableReference(description='\n                    Trait associated with cell phone color.\n                    ', allow_none=True, pack_safe=True, manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))), required_packs=TunableEnumSet(description='\n                    If any packs are tuned here, at least one of them must\n                    be present for this option to appear in the selector.\n                    If none are tuned, it will always appear.\n                    ', enum_type=Pack, enum_default=(Pack.BASE_GAME)), **kwargs)

    PHONE_BACKGROUND_COLOR_VARIATION_TUNING = TunableList(description='\n        A list of all of the different colors you can set the cell phone background to be.\n        ',
      tunable=(TunablePhoneBackgroundColorTuple()),
      export_modes=(
     ExportModes.ClientBinary,))
    PHONE_CASE_VARIATION_TUNING = TunableList(description='\n        A list of all of the different cases you can set the cell phone cover to be.\n        ',
      tunable=(TunablePhoneCaseTuple()),
      export_modes=(
     ExportModes.ClientBinary,))