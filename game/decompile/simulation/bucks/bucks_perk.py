# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_perk.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 11073 bytes
from bucks.bucks_enums import BucksType
from buffs.tunable import TunableBuffReference
from event_testing.tests import TunableTestSetWithTooltip
from interactions.utils.tunable_icon import TunableIconFactory
from rewards.reward_tuning import TunableSpecificReward
from sims4.localization import TunableLocalizedStringFactory, TunableLocalizedString
from sims4.tuning.dynamic_enum import DynamicEnumLocked
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableReference, TunableEnumEntry, Tunable, TunableList, TunableTuple, OptionalTunable, TunableRange, TunableMapping, TunableEnumFlags
from sims4.tuning.tunable_base import GroupNames, ExportModes
import enum, services, sims4
logger = sims4.log.Logger('Bucks', default_owner='tastle')

class BucksUIDisplayFlag(enum.IntFlags):
    LINK_TOP = 1


class BucksPerkTunables:
    PERK_UNLOCKED_TOOLTIP = TunableLocalizedStringFactory(description='\n        A tooltip that will be shown on Perks unlocked manually by the user.\n        \n        Expected Arguments: None.\n        ')
    LINKED_PERK_UNLOCKED_TOOLTIP = TunableLocalizedStringFactory(description="\n        A tooltip that will be shown on Perks unlocked because another Perk's\n        linked_perks list referenced them. Lets the user know why this Perk is\n        no longer available for purchase even though they never explicitely\n        bought it.\n        \n        Expected Arguments: {0.String} - The display name of the Perk that\n        unlocked this one.\n        ")


class BucksPerk(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)):
    INSTANCE_TUNABLES = {'associated_bucks_type':TunableEnumEntry(description='\n            The type of Bucks required to unlock this Perk.\n            ',
       tunable_type=BucksType,
       default=BucksType.INVALID,
       pack_safe=True,
       invalid_enums=(
      BucksType.INVALID,)), 
     'unlock_cost':Tunable(description='\n            How many Bucks of the specified type this Perk costs to unlock.\n            ',
       tunable_type=int,
       default=100), 
     'rewards':TunableList(description='\n            A list of rewards to grant the household when this Perk is\n            unlocked.\n            ',
       tunable=TunableSpecificReward()), 
     'linked_perks':TunableList(description='\n            A list of Perks that will be unlocked along with this one if not\n            already unlocked.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))), 
     'next_level_perk':TunableReference(description='\n            The next perk within this particular chain of perks. \n            If tunable is None, then it either does not belong to a chain\n            or is the last in the chain.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.BUCKS_PERK),
       allow_none=True), 
     'temporary_perk_information':OptionalTunable(TunableTuple(description='\n            Tunables associated with temporary Perks.\n            ',
       duration=TunableRange(description='\n                The tunable number of Sim hours this Perk should last for, if\n                temporary.\n                ',
       tunable_type=int,
       default=1,
       minimum=1),
       unlocked_tooltip=(OptionalTunable(TunableLocalizedStringFactory(description='\n                A tooltip that will be shown on this Perk when unlocked so the\n                user knows when they will be able to buy it again. No expected\n                arguments.\n                '))))), 
     'display_name':TunableLocalizedStringFactory(description="\n            This Perk's display name. No expected arguments.\n            ",
       tuning_group=GroupNames.UI), 
     'perk_description':TunableLocalizedStringFactory(description='\n            The description for this Perk. No expected arguments.\n            ',
       tuning_group=GroupNames.UI), 
     'undiscovered_description':OptionalTunable(description='\n            When enabled will cause a different description to be displayed \n            if the Perk has never been acquired by the Sim.\n            ',
       tunable=TunableLocalizedStringFactory(description='\n                The description for this perk when it has never been acquired\n                by this Sim.\n                '),
       tuning_group=GroupNames.UI), 
     'icon':TunableIconFactory(tuning_group=GroupNames.UI), 
     'ui_display_flags':TunableEnumFlags(description='\n            The display flags for this Perk in the Perks Panel UI.\n            LINK_TOP: Display a line connecting this perk to the perk above it\n            ',
       enum_type=BucksUIDisplayFlag,
       allow_no_flags=True,
       tuning_group=GroupNames.UI), 
     'required_unlocks':OptionalTunable(description='\n            A list of all of the bucks perks that must be unlocked for this one\n            to be available for purchase.\n            ',
       tunable=TunableList(description='\n                List of required perks for this perk to be available.\n                ',
       tunable=TunableReference(description='\n                    Reference to a bucks perk that must be unlocked.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK))))), 
     'lock_on_purchase':OptionalTunable(description='\n            A list of perks to lock when this perk is purchased.\n            ',
       tunable=TunableList(description='\n                List of perks to lock when this perk is unlocked.\n                ',
       tunable=TunableReference(description='\n                    Reference to a bucks perk that must be locked.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK))))), 
     'buffs_to_award':TunableList(description='\n            A list of references to buffs to add to the owner of \n            bucks tracker this perk is unlocked in and optional reason for the\n            buffs.\n            ',
       tunable=TunableBuffReference(description='\n                A pair of Buff and Reason for the buff.\n                ',
       pack_safe=True)), 
     'traits_to_award':TunableList(description='\n            A list of references to traits to add to the owner of \n            bucks tracker this perk is unlocked on. Traits will be\n            removed when the perk is locked.\n            ',
       tunable=TunableReference(description='\n                A reference to a trait to be awarded.\n                ',
       pack_safe=True,
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))), 
     'conflicting_perks':TunableList(description='\n            A list of perks that this perk is mutually exclusive with.\n            \n            When a perk is mutually exclusive with another perk it means that\n            the perk cannot be purchased if that perk has already been purchased.\n            ',
       tunable=TunableReference(description='\n                A reference to a perk that this perk is mutually exclusive with.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))), 
     'loots_on_unlock':TunableList(description='\n            A list of loots to award when this perk is Unlocked.\n            ',
       tunable=TunableReference(description='\n                A loot to be applied.\n                \n                Actor is the Sim that the perk is being unlocked for.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       pack_safe=True)), 
     'loots_on_lock':TunableList(description='\n            A list of loots to award when this perk is Locked.\n            ',
       tunable=TunableReference(description='\n                A loot to be applied.\n                \n                Actor is the Sim that the Perk is being locked for.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       pack_safe=True)), 
     'available_for_puchase_tests':TunableTestSetWithTooltip(description='\n            A set of tests that must pass in order for this perk to be\n            available for purchase. \n            \n            This is enforced on the UI side. If the tests returns False then\n            we will mark the perk as locked and pass along a tooltip, the one\n            from the failed test.\n            \n            For the tooltip the first token is the Sim attempting to unlock the\n            perk. \n            '), 
     'progression_statistic':OptionalTunable(description='\n            If enabled, this ranked statistic tracks the progress towards\n            unlocking this perk. This statistic should tune an AwardPerkLoot\n            in its event data with the ability to award this perk.\n            \n            Use an AwardPerkLoot with the progress strategy to give progress \n            to obtaining the perk.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('RankedStatistic', )))}

    @classmethod
    def _verify_tuning_callback(cls):
        if cls.temporary_perk_information is not None:
            if cls.linked_perks:
                logger.error("A Bucks Perk has been created that's both temporary and has linked Perks. This is not supported. {}", cls)