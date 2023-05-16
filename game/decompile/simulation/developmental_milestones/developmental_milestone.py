# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\developmental_milestones\developmental_milestone.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 16430 bytes
import services, sims4
from developmental_milestones.developmental_milestone_enums import MilestoneDataClass
from event_testing.tests import TunableTestSet
from interactions.utils.tunable_icon import TunableIcon
from sims.sim_info_types import Age
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory, TunableList
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, Tunable, TunableEnumSet, TunableSet, TunableReference, OptionalTunable, TunableTuple, TunableList, TunablePercent, TunableMapping, TunableEnumEntry, TunableResourceKey
from sims4.tuning.tunable_base import ExportModes, EnumBinaryExportType
logger = sims4.log.Logger('DevelopmentalMilestones', default_owner='shipark')

class DevelopmentalMilestoneCategory(DynamicEnum):
    INVALID = -1


class DevelopmentalMilestone(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)):
    LIFETIME_MILESTONE_PANEL_FILTERS = TunableList(description='\n        Terms used to filter milestone categories shown in the Lifetime Milestone Panel.\n        ',
      tunable=TunableTuple(ages=TunableEnumSet(description='\n                The ages used as filter terms for the filter button.\n                ',
      enum_type=Age,
      enum_default=(Age.INFANT),
      export_modes=(ExportModes.All),
      allow_empty_set=True),
      icon=TunableIcon(description='\n                The icon of the filter button.\n                ',
      export_modes=(ExportModes.All)),
      name=TunableLocalizedString(description='\n                The name of the filter term for display in the UI. Example: "Children and Teens"\n                ',
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      export_class_name='LifetimeMilestoneFilterTerm'),
      export_modes=(ExportModes.All))
    VIEW_MILESTONES_LOOT = TunableList(description='\n        A list of loots to apply to the active sim when the view milestones command is run from the UI.\n        ',
      tunable=TunableReference(description='\n            Loot applied to the active sim.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ),
      pack_safe=True))
    RETROACTIVE_MILESTONES = TunableList(description='\n        A list of loots to apply to the sim. The loot list will be applied\n        to the Sim when:\n        1) the Sim is first initialized and the EP13 content is available.\n        2) EP13 is reinstalled\n        3) LOD update occurs\n        ',
      tunable=TunableReference(description='\n            Loot applied to the sim to grant initial milestones.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
      class_restrictions=('LootActions', ),
      pack_safe=True))
    DEVELOPMENTAL_MILESTONE_UNLOCK_OVERRIDES = TunableMapping(description='\n        A mapping between milestone and its data class. Useful if any event sequencing behavior needs to be specialized. \n        Discuss with a GPE before tuning.\n        ',
      key_type=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)),
      pack_safe=True),
      value_type=TunableEnumEntry(tunable_type=MilestoneDataClass,
      default=(MilestoneDataClass.DEFAULT)))
    DEVELOPMENTAL_MILESTONE_CATEGORIES = TunableMapping(description='\n        A mapping of developmental milestone categories enums to corresponding display data.\n        ',
      key_type=TunableEnumEntry(description='\n            The category type.\n            ',
      tunable_type=DevelopmentalMilestoneCategory,
      default=(DevelopmentalMilestoneCategory.INVALID),
      invalid_enums=(
     DevelopmentalMilestoneCategory.INVALID,),
      binary_type=(EnumBinaryExportType.EnumUint32),
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      value_type=TunableTuple(description='\n            Category display data.\n            ',
      export_class_name='DevelopmentalMilestoneCategoryTuple',
      ages=TunableSet(description='\n                Ages valid for this category.\n                ',
      tunable=TunableEnumEntry(tunable_type=Age,
      default=(Age.ADULT),
      export_modes=(ExportModes.All))),
      name=TunableLocalizedStringFactory(description='\n                The name of this Developmental Milestone.\n                ',
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      tooltip=TunableLocalizedStringFactory(description='\n                Hovertip text to show in the UI.\n                ',
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      icon=TunableResourceKey(description='\n                The icon to be displayed next to this category in the UI.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      default=None,
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      sim_info_panel_default_icon=TunableResourceKey(description='\n                The icon to use on the Sim Info panel when there are new \n                Milestones displayed in this category.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      default=None,
      export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
      sim_info_panel_over_icon=TunableResourceKey(description='\n                The icon to use on the Sim Info panel when there are new \n                Milestones displayed in this category and the mouse is\n                over the button.\n                ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      default=None,
      export_modes=(sims4.tuning.tunable_base.ExportModes.All))),
      tuple_name='DevelopmentalMilestoneCategoryMapping',
      export_modes=(sims4.tuning.tunable_base.ExportModes.All))
    INSTANCE_TUNABLES = {'name':TunableLocalizedString(description='\n            Name of this milestone.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'category':TunableEnumEntry(description='\n            Category where this milestone appears in the UI.\n            ',
       tunable_type=DevelopmentalMilestoneCategory,
       default=DevelopmentalMilestoneCategory.INVALID,
       invalid_enums=(
      DevelopmentalMilestoneCategory.INVALID,),
       binary_type=EnumBinaryExportType.EnumUint32,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'ui_sort_order':Tunable(description='\n            A tuned value that determines the order in which milestones are listed in the UI.\n            ',
       tunable_type=int,
       default=0,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'ages':TunableEnumSet(description='\n            Milestone is limited to the specified age state(s).\n            ',
       enum_type=Age,
       enum_default=Age.INFANT,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'prerequisite_milestones':TunableSet(description='\n            Milestones that must be completed before this milestone becomes available.\n            If none are tuned, it is available at the beginning of the age state.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE)))), 
     'goal':TunableReference(description='\n            The goal that must be completed to unlock the milestone.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)), 
     'commodity':OptionalTunable(description='\n            The commodity used to track progress toward unlocking this milestone.\n            This commodity is added to the Sim when the milestone becomes available,\n            and is removed when it is either completed or the Sim advances to the next age state.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Commodity', ))), 
     'is_primary_milestone':OptionalTunable(description='\n            Primary milestones are visible in the UI when they are active but not yet unlocked.\n            Non-primary milestones are only visible in the UI after they are unlocked.\n            ',
       tunable=TunableTuple(export_class_name='DevelopmentalMilestoneIsPrimaryMilestone',
       hint_text=TunableLocalizedString(description='\n                    Displayed in UI hovertip when the milestone is not yet completed.\n                    ',
       export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
       revealable_name=OptionalTunable(description='\n                    If tuned, use this name when the milestone is in the revealable state. Otherwise,\n                    use the default name.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        Revealable name of the milestone.\n                        '),
       export_modes=(sims4.tuning.tunable_base.ExportModes.All)),
       tests=TunableTestSet(description='\n                    If the tuned tests pass for the Sim, then the milestone will display\n                    as revealable in the UI, otherwise it will not.\n                    ')),
       enabled_name='True',
       disabled_name='False',
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'icon':TunableIcon(description='\n            Icon to show in the UI when this milestone is completed.\n            ',
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'unlocked_text':TunableLocalizedString(description='\n            Text to show in the UI hovertip after the milestone is completed.\n            \n            Supported tokens:\n            {0} = Actor Sim (Sim the milestone unlocked for) - e.g. {0.SimFirstName} \n            {1} = Target Sim - e.g. {1.SimName}\n            {2} = Target Object Name - e.g. {2.ObjectName}\n            {3.String} = Unlocked In Lot Name\n            {4.String} = Unlocked In Region Name\n            {5.String} = Career Display Name (Career the milestone unlocked for)\n            {6.String} = Career Level (Career Level the milestone unlocked for)\n            {7.String} = Death Type (Death Type the milestone unlocked for)\n            {8.String} = Trait Display Name (Trait the milestone unlocked for)\n            ',
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'unlocked_text_no_context':TunableLocalizedString(description='\n            Text to show in the UI hovertip after the milestone is completed if contextual information is not available.\n            ',
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'unlocked_text_target_sim_header':TunableLocalizedString(description="\n            Text to show above the target sim's icon in the UI hovertip after the milestone\n            is completed. e.g. With, Married To\n            \n            Only works if the tuned unlocked_text uses the supported token {1} = Target Sim.\n            ",
       allow_none=True,
       export_modes=sims4.tuning.tunable_base.ExportModes.All), 
     'loot':TunableList(description='\n            Optional loot to apply when this milestone is awarded.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'treat_unlocked_at_age_percentage':OptionalTunable(description="\n            This milestone will be treated as unlocked for unplayed Sims and also auto-assigned to Sims if they become\n            part of an active household if the Sim's percentage of current age state is at or above this tuned percent.\n            ",
       tunable=TunablePercent(default=0),
       enabled_name='Percent'), 
     'repeatable':Tunable(description='\n            If True, the milestone will reset after it is completed.\n            ',
       tunable_type=bool,
       default=False), 
     'retroactive_only':Tunable(description="\n            If True, the milestone is only activated once, during the tracker's\n            initial startup, and will be shut down after retroactive loot is applied.\n            ",
       tunable_type=bool,
       default=False)}
    developmental_milestone_tuning_cache = None

    @staticmethod
    def age_milestones_gen(age):
        milestones = DevelopmentalMilestone.developmental_milestone_tuning_cache.get(age)
        if milestones is not None:
            for milestone in milestones:
                yield milestone

    @classmethod
    def _verify_tuning_callback(cls):
        for milestone in cls.prerequisite_milestones:
            if milestone is cls:
                logger.error('Developmental Milestone {} has itself listed as a prerequisite.', cls, owner='miking')


def build_developmental_milestone_cache(manager):
    DevelopmentalMilestone.developmental_milestone_tuning_cache = {}
    for developmental_milestone in services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE).types.values():
        for age_enum in developmental_milestone.ages:
            milestones = DevelopmentalMilestone.developmental_milestone_tuning_cache.get(age_enum)
            if milestones is None:
                milestones = []
                DevelopmentalMilestone.developmental_milestone_tuning_cache[age_enum] = milestones
            milestones.append(developmental_milestone)


services.get_instance_manager(sims4.resources.Types.DEVELOPMENTAL_MILESTONE).add_on_load_complete(build_developmental_milestone_cache)