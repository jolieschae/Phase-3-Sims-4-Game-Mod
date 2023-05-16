# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\preference_tuning.py
# Compiled at: 2021-04-27 18:23:00
# Size of source mod 2**32: 3612 bytes
from interactions.utils.tunable_icon import TunableIcon
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableRange, TunableReference, TunableList
from sims4.tuning.tunable_base import ExportModes
import services, sims4

class PreferenceTuning:
    PREFERENCE_CAPACITY = TunableRange(description='\n        The preference limit on an object.            \n        ',
      tunable_type=int,
      minimum=1,
      default=15,
      export_modes=(ExportModes.All))
    CAS_PREFERENCE_LIKE_RATE = TunableRange(description='\n        The rate of like preferences assigned at random in CAS (0: none, 1: all).            \n        ',
      tunable_type=float,
      minimum=0,
      maximum=1,
      default=0.75,
      export_modes=(ExportModes.All))
    DECORATOR_CAREER_PREFERENCE_CATEGORIES = TunableList(description='\n        A list of preference categories that contain the set of preferences\n        pulled from clients that create constraints for the GP10 Decorator Career.\n        ',
      tunable=TunableReference(description='\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.CAS_PREFERENCE_CATEGORY)),
      pack_safe=True,
      export_modes=(ExportModes.All)))
    CAS_PREFERENCE_MOLECULE_EMPTY_TOOLTIP = TunableLocalizedString(description='\n        The tooltip displayed over the preference molecule if the Sim does not have any set preferences.\n        ',
      export_modes=(ExportModes.ClientBinary))
    CAS_PREFERENCES_CATEGORY_TAB_ICON = TunableIcon(description='\n        The icon shown in the Sim Preferences Selection Panel Tab for Categories.\n        ',
      export_modes=(ExportModes.ClientBinary))
    CAS_PREFERENCES_CATEGORY_TAB_ICON_SELECTED = TunableIcon(description='\n        The icon shown in the Sim Preferences Selection Panel Tab for Categories.\n        ',
      export_modes=(ExportModes.ClientBinary))
    CAS_PREFERENCES_CATEGORY_TAB_TOOLTIP = TunableLocalizedString(description='\n        The tooltip string shown in the Sim Preferences Selection Panel Tab for Categories.\n        ',
      export_modes=(ExportModes.ClientBinary))
    PREFERENCE_SIM_PANEL_EMPTY = TunableLocalizedString(description='\n        The string shown in the Sim Preferences Panel when the Sim has no set preferences.\n        ',
      export_modes=(ExportModes.ClientBinary))
    MAX_PREFERENCE_WARNING = TunableLocalizedString(description='\n        The string shown in the CAS when the Sim has reached the preference capacity.\n        ',
      export_modes=(ExportModes.ClientBinary))
    RANDOMIZE_DIAG_TEXT = TunableLocalizedString(description='\n        The text within the warning dialog that is shown when traits are randomized.\n        ',
      export_modes=(ExportModes.ClientBinary))
    RANDOMIZE_DIAG_TITLE = TunableLocalizedString(description='\n        The title within the warning dialog that is shown when traits are randomized.\n        ',
      export_modes=(ExportModes.ClientBinary))
    RANDOMIZE_DIAG_TOOLTIP = TunableLocalizedString(description='\n        The tooltip string shown on the Randomize button in the Sim Preferences Selection Panel.\n        ',
      export_modes=(ExportModes.ClientBinary))