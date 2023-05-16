# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fashion_trends\fashion_trend_tuning.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 11785 bytes
import sims4
from interactions.utils.loot import LootActions
from interactions.utils.tunable_icon import TunableIconAllPacks
from sims.outfits.outfit_enums import BodyType
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, TunableList, TunableMapping, Tunable, TunablePackSafeResourceKey, TunablePackSafeReference, OptionalTunable, TunablePercent
from sims4.tuning.tunable_base import ExportModes
from statistics.mood import TunableModifiers
from tag import TunableTag, TunableTags
from tunable_time import TunableTimeSpan, TunableTimeOfDay
import services
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet

class FashionThriftStoreTuning:
    DAILY_REFRESH_NOTIFICATION = OptionalTunable(description='\n        If enabled, notification displayed at the DAILY_REFRESH_TIME\n\n        Can be disabled if the decision is made to not display it\n        ',
      tunable=TunableUiDialogNotificationSnippet(description='\n            The notification that will appear when the thrift \n            store daily random shuffle occurs\n            ',
      pack_safe=True))
    DAILY_REFRESH_TIME = TunableTimeOfDay(description='\n        The time of day when the thrift store inventory refreshes.\n\n        Default is 3am\n        ',
      default_hour=3,
      default_minute=0)
    EXCLUSIVE_ITEM_NOTIFICATION = OptionalTunable(description='\n        If enabled, notification displayed if chance for exclusive \n        item is successful in the thrift store daily random shuffle\n        \n        Can be disabled if the decision is made to not display it\n        ',
      tunable=TunableUiDialogNotificationSnippet(description='\n            The notification that will appear when an \n            exclusive item is unlocked from the thrift \n            store daily random shuffle\n            ',
      pack_safe=True))
    EXCLUSIVE_ITEM_NOTIFICATION_TIME = TunableTimeOfDay(description='\n        The time of day for scheduling TNS notifications for rare, super-rare,\n        or exclusive thrift store items are available in the thrift store inventory\n\n        Default is 8am\n        ',
      default_hour=8,
      default_minute=0)
    EXCLUSIVE_ITEM_CHANCE = TunablePercent(description='\n         The chance that an exclusive item from the \n         thrift store random shuffle is successful\n         ',
      default=25)
    RARITY_ITEM_CHANCE = TunableMapping(description='\n        Modifiers to apply to a given rarity tag for the thrift store selection chance.\n        ',
      key_name='rarity_tag',
      key_type=TunableTag(description='\n            The prevalent rarity to tune for cost\n            ',
      filter_prefixes=('fashion_rarity', )),
      value_name='rarity_chance_of_selection',
      value_type=TunableTuple(description='\n            Chance of rarity selection with modifier\n            ',
      selection_chance=TunablePercent(description='\n                The chance that an exclusive item from the \n                thrift store random shuffle is successful\n                ',
      default=100),
      selection_modifier=TunableModifiers(description="\n            Modifiers to apply to an object's environment score\n            ")))
    DOMINANT_TREND_ITEM_COST = TunableMapping(description='\n        Defines the item cost per trend that is prevalent for an outfit\n        ',
      key_name='trend_tag',
      key_type=TunableTag(description='\n            The prevalent trend to tune for cost\n            ',
      filter_prefixes=('style', )),
      value_name='trend_cost',
      value_type=Tunable(description='\n            The cost for item of prevalent trend\n            ',
      tunable_type=float,
      default=0.0))
    DOMINANT_RARITY_ITEM_COST = TunableMapping(description='\n        Defines the item cost per rarity that is prevalent for an outfit\n        ',
      key_name='rarity_tag',
      key_type=TunableTag(description='\n            The prevalent rarity to tune for cost\n            ',
      filter_prefixes=('fashion_rarity', )),
      value_name='rarity_cost',
      value_type=Tunable(description='\n            The cost for item of prevalent rarity\n            ',
      tunable_type=float,
      default=0.0))
    REFRESH_CAS_PART_LIST = TunableList(description='\n        A list of CAS part types to randomize for the daily thrift store refresh\n        ',
      tunable=TunableTuple(description='\n            The data about this trend.\n            ',
      include_tags=TunableTags(description='\n                The tag for CAS parts to include.\n                ',
      filter_prefixes=('fashion_rarity', )),
      exclude_tags=TunableTags(description='\n                The tag for CAS parts to exclude.\n                ',
      filter_prefixes=('fashion_rarity', )),
      body_type=TunableEnumEntry(description='\n                The body type to check.\n                ',
      tunable_type=BodyType,
      default=(BodyType.NONE)),
      count=Tunable(description='\n                The count of CAS parts to return for the \n                randomization of body type parts\n                ',
      tunable_type=int,
      default=0),
      is_exclusive=Tunable(description='\n            If checked, the parts matching these tags will only be included\n            if the tunable chance is success from EXCLUSIVE_ITEM_CHANCE for the daily refresh\n            ',
      tunable_type=bool,
      default=False)))
    FASHION_OUTFIT_OBJECT_DEFINITION = TunablePackSafeReference(description='\n        Object definition of the fashion outfit object to place outfits on\n        after designing in Fashion CAS EditMode\n        ',
      manager=(services.definition_manager()))
    DEFAULT_MANNEQUIN_DATA = TunableTuple(description='\n        References to each of the default mannequin sim infos to use for\n        Thrift Store CAS for the Fashion Trend Service mannequin.\n        ',
      mannequin_pose=TunablePackSafeReference(description='\n            The pose that mannequins in CAS are in when \n            designing the fashion outfits from the Thrift Store Inventory\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ANIMATION)),
      class_restrictions=('ObjectPose', ),
      allow_none=True),
      male_adult=TunablePackSafeResourceKey(description='\n            Default mannequin sim info for male adult Fashion CAS.\n            ',
      resource_types=(
     sims4.resources.Types.SIMINFO,),
      allow_none=True),
      female_adult=TunablePackSafeResourceKey(description='\n            Default mannequin sim info for female adult Fashion CAS.\n            ',
      resource_types=(
     sims4.resources.Types.SIMINFO,),
      allow_none=True))
    MAX_ALLOWED_SOLD_OUTFITS = Tunable(description="\n        The maximum number of sold outfits to track for use in\n        walkbys and situations where the situation job outfit\n        is using 'use_sold_fashion_outfit'\n        \n        Defaults to 10 sold fashion outfits\n        ",
      tunable_type=int,
      default=10)


class FashionTrendTuning:
    TRENDS = TunableMapping(description='\n        Defines the loots that will shift the associated trend\n        ',
      key_name='trend_tag',
      key_type=TunableTag(description='\n            The trend to create a statistic for and how often it shifts\n            ',
      filter_prefixes=('style', )),
      value_name='trend_statistics_and_shift_loots',
      value_type=TunableTuple(description='\n            Trend Name, Trend Icon, Trend Object Definition, \n            Statistics for Fashion Trends and the associated\n            Loots to shift Fashion Trends up/down given the\n            tuned shift interval\n            ',
      trend_name=TunableLocalizedString(description='\n                The trend name used to display in tooltips\n                ',
      default=None,
      export_modes=(ExportModes.All)),
      trend_icon=TunableIconAllPacks(description='\n                The Icon for this trend in UI and inventory.\n                ',
      export_modes=(ExportModes.All)),
      trend_outfit_object_definition=TunablePackSafeReference(description='\n                Object definition of the fashion outfit object for the \n                associated Trend to place outfits on\n                after designing in Fashion CAS EditMode\n                ',
      manager=(services.definition_manager())),
      trend_statistic=TunablePackSafeReference(description='\n                The statistic used to track the tuned trend\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('Statistic', )),
      trend_shift_loot=TunableList(description='\n                Loot applied when the Trend is shifted\n                ',
      tunable=LootActions.TunableReference(description='\n                    Loot applied when the Trend shifts.\n                    ',
      pack_safe=True)),
      trend_shift_interval=TunableTimeSpan(description='\n                The amount of time it takes before the tuned\n                trend is shifted using the tuned loot\n                \n                Defaults to every hour\n                ',
      default_hours=1),
      export_class_name='FashionTrendItem',
      export_modes=(ExportModes.ServerXML)),
      export_modes=(ExportModes.All),
      tuple_name='FashionTrendTuple')
    TREND_SHIFT_INTERVAL = TunableTimeSpan(description='\n        The amount of time it takes before trends refresh.\n        ',
      default_hours=1)