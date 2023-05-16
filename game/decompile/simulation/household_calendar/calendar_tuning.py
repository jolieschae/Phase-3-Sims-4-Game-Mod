# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\household_calendar\calendar_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 3667 bytes
from drama_scheduler.drama_node import DramaNodeUiDisplayType
from sims4.common import Pack
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableList, TunableTuple, OptionalTunable, TunableRegionDescription, TunableEnumEntry, Tunable, TunableEnumSet
from sims4.tuning.tunable_base import ExportModes, GroupNames

class CalendarTuning:
    CALENDAR_FILTER_DATA = TunableList(description='\n        A List of Categories and Filters for use in filtering the Calendar data in the SchedulePane.\n        ',
      tunable=TunableTuple(description='\n            A tuple of Category and the filters for the category.\n            ',
      filters=TunableList(description='\n                Filter data used in the calendar\n                ',
      tunable=TunableTuple(description="\n                    Defines a single filter in the Calendar's filter component.\n                    ",
      filter_name=TunableLocalizedString(description="\n                        The name for this filter displayed in the calendar's filter component.\n                        "),
      region_resource=OptionalTunable(description='\n                        If enabled, only entries from zones within this region will be captured by this fiter.\n                        ',
      tunable=TunableRegionDescription(pack_safe=True)),
      entry_types=TunableEnumSet(description='\n                        The entries which will be captured by this filter.\n                        ',
      enum_type=DramaNodeUiDisplayType,
      invalid_enums=[
     DramaNodeUiDisplayType.NO_UI]),
      is_birthday_filter=Tunable(description='\n                        If enabled, birthday entries will be captured by this filter.\n                        ',
      tunable_type=bool,
      default=False),
      is_work_filter=Tunable(description='\n                        If enabled, work entries will be captured by this filter.\n                        ',
      tunable_type=bool,
      default=False),
      is_favorite_filter=Tunable(description='\n                        If enabled, only favorited entries which also match the other criteria, will be captured by this filter.\n                        ',
      tunable_type=bool,
      default=False),
      required_packs=TunableEnumSet(description='\n                        If any packs are tuned here, at least one of them must\n                        be present for this filter to appear in the UI.\n                        ',
      enum_type=Pack,
      enum_default=(Pack.BASE_GAME)),
      export_class_name='CalendarFilterTuple')),
      category_name=TunableLocalizedString(description='\n                The string to be used for the name of the category these filters belong to.\n                '),
      export_class_name='CalendarCategoryTuple'),
      export_modes=(ExportModes.ClientBinary),
      tuning_group=(GroupNames.UI))