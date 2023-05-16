# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\traits\traits.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 56673 bytes
from _sims4_collections import frozendict
from animation.animation_constants import InteractionAsmType
from autonomy.content_sets import ContentSet
from buffs.tunable import TunableBuffReference
from crafting.food_restrictions_utils import FoodRestrictionUtils
from event_testing.common_event_tests import CommonEventTestVariant
from event_testing.tests import TunableTestSet
from interactions import ParticipantTypeReactionlet
from interactions.utils.animation_reference import TunableAnimationReference
from interactions.utils.animation_selector import TunableAnimationSelector
from objects.mixins import SuperAffordanceProviderMixin, MixerActorMixin, MixerProviderMixin
from objects.mixins import TargetSuperAffordanceProviderMixin
from sims import sim_info_types
from sims.culling.culling_tuning import CullingBehaviorDefault, CullingBehaviorImmune, CullingBehaviorImportanceAsNpc
from sims.lod_mixin import HasTunableLodMixin
from sims.outfits.outfit_enums import OutfitChangeReason
from sims.sim_info_types import Species, Age, Gender
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.resources import CompoundTypes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableResourceKey, OptionalTunable, TunableReference, TunableList, TunableEnumEntry, TunableSet, TunableMapping, Tunable, HasTunableReference, TunableTuple, TunableEnumFlags, TunableEnumWithFilter, TunableVariant, TunableInteractionAsmResourceKey, TunableStyle, TunableEntitlement
from sims4.tuning.tunable_base import ExportModes, SourceQueries, GroupNames
from sims4.utils import classproperty, constproperty
from statistics.commodity import Commodity
from sims.fixup.sim_info_career_fixup_action import _SimInfoCareerFixupAction
from sims.fixup.sim_info_fixup_action import SimInfoFixupActionTiming
from sims.fixup.sim_info_perk_fixup_action import _SimInfoPerkFixupAction
from sims.fixup.sim_info_skill_fixup_action import _SimInfoSkillFixupAction
from sims.fixup.sim_info_unlock_fixup_action import _SimInfoUnlockFixupAction
from traits.preference_enums import PreferenceTypes
from traits.trait_day_night_tracking import DayNightTracking
from traits.trait_plumbbob_override import PlumbbobOverrideRequest
from traits.trait_type import TraitType
from traits.trait_voice_effect import VoiceEffectRequest
from vfx.vfx_mask import VFXMask, ExcludeVFXMask
import services, sims4.log, tag
logger = sims4.log.Logger('Trait', default_owner='cjiang')

def are_traits_conflicting(trait_a, trait_b):
    if trait_a is None or trait_b is None:
        return False
    return trait_a.is_conflicting(trait_b)


def get_possible_traits(sim_info_data, trait_type=TraitType.PERSONALITY):
    trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
    return [trait for trait in trait_manager.types.values() if trait.trait_type == trait_type if trait.is_valid_trait(sim_info_data)]


class TraitBuffReplacementPriority(DynamicEnum):
    NORMAL = 0


class TraitUICategory(DynamicEnum):
    PERSONALITY = 0
    GENDER = 1
    IDENTITY = 2


class Trait(HasTunableReference, SuperAffordanceProviderMixin, TargetSuperAffordanceProviderMixin, HasTunableLodMixin, MixerActorMixin, MixerProviderMixin, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TRAIT)):
    EQUIP_SLOT_NUMBER_MAP = TunableMapping(description='\n        The number of personality traits available to Sims of specific ages.\n        ',
      key_type=TunableEnumEntry(description="\n            The Sim's age.\n            ",
      tunable_type=(sim_info_types.Age),
      default=(sim_info_types.Age.YOUNGADULT)),
      value_type=Tunable(description='\n            The number of personality traits available to a Sim of the specified\n            age.\n            ',
      tunable_type=int,
      default=3),
      key_name='Age',
      value_name='Slot Number')
    PERSONALITY_TRAIT_TAG = TunableEnumEntry(description='\n        The tag that marks a trait as a personality trait.\n        ',
      tunable_type=(tag.Tag),
      default=(tag.Tag.INVALID),
      invalid_enums=(
     tag.Tag.INVALID,))
    DAY_NIGHT_TRACKING_BUFF_TAG = TunableEnumWithFilter(description='\n        The tag that marks buffs as opting in to Day Night Tracking on traits..\n        ',
      tunable_type=(tag.Tag),
      filter_prefixes=[
     'buff'],
      default=(tag.Tag.INVALID),
      invalid_enums=(
     tag.Tag.INVALID,))
    INSTANCE_TUNABLES = {'trait_type':TunableEnumEntry(description='\n            The type of the trait.\n            ',
       tunable_type=TraitType,
       default=TraitType.PERSONALITY,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.APPEARANCE), 
     'display_name':TunableLocalizedStringFactory(description="\n            The trait's display name. This string is provided with the owning\n            Sim as its only token.\n            ",
       allow_none=True,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.APPEARANCE), 
     'display_name_gender_neutral':TunableLocalizedString(description="\n            The trait's gender-neutral display name. This string is not provided\n            any tokens, and thus can't rely on context to properly form\n            masculine and feminine forms.\n            ",
       allow_none=True,
       tuning_group=GroupNames.APPEARANCE), 
     'trait_description':TunableLocalizedStringFactory(description="\n            The trait's description.\n            ",
       allow_none=True,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.APPEARANCE), 
     'trait_origin_description':TunableLocalizedString(description="\n            A description of how the Sim obtained this trait. Can be overloaded\n            for other uses in certain cases:\n            - When the trait type is AGENT this string is the name of the \n                agency's Trade type and will be provided with the owning sim \n                as its token.\n            - When the trait type is HIDDEN and the trait is used by the CAS\n                STORIES flow, this can be used as a secondary description in \n                the CAS Stories UI. If this trait is tagged as a CAREER CAS \n                stories trait, this description will be used to explain which \n                skills are also granted with this career.\n            ",
       allow_none=True,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.APPEARANCE), 
     'icon':TunableResourceKey(description="\n            The trait's icon.\n            ",
       allow_none=True,
       resource_types=CompoundTypes.IMAGE,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.APPEARANCE), 
     'pie_menu_icon':TunableResourceKey(description="\n            The trait's pie menu icon.\n            ",
       resource_types=CompoundTypes.IMAGE,
       default=None,
       allow_none=True,
       tuning_group=GroupNames.APPEARANCE), 
     'listen_animation_overrides':OptionalTunable(description='\n            If enabled, this tunable will provide listen animation overrides \n            for this trait.\n            ',
       tunable=TunableTuple(description='\n                Tunables that define which listen animation overrides should be\n                applied.\n                ',
       default_override=TunableAnimationReference(description='\n                    The default listen animation override.  This should only be\n                    applied if the override map is not defined, or if the \n                    interaction in question is not in the override map.\n                    ',
       callback=None),
       override_map=TunableMapping(description='\n                    A mapping of listen animation overrides to affordances.\n                    ',
       key_type=TunableReference(description='\n                        The affordance that should have its listen animation overridden.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True),
       value_type=TunableAnimationReference(description='\n                        The listen animation for this affordance.\n                        ',
       callback=None))),
       tuning_group=GroupNames.ANIMATION), 
     'reactionlet_overrides':OptionalTunable(description='\n            If enabled, this tunable will provide reactionlet overrides for \n            this trait .\n            ',
       tunable=TunableTuple(description='\n                Tunables that define which reactionlet overrides should be \n                applied.\n                ',
       default_override=TunableAnimationSelector(description='\n                    The default reactionlet override.  This should only be \n                    applied if the override map is not defined, or if the \n                    interaction in question is not in the override map.\n                    ',
       interaction_asm_type=(InteractionAsmType.Reactionlet),
       override_animation_context=True,
       participant_enum_override=(
      ParticipantTypeReactionlet, ParticipantTypeReactionlet.Invalid)),
       override_map=TunableMapping(description='\n                    A mapping of reactionlet overrides to affordances.\n                    ',
       key_type=TunableReference(description='\n                        The affordance that should have its reactionlet overridden.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       pack_safe=True),
       value_type=TunableAnimationSelector(description='\n                        The reactionlet override for this affordance.\n                        ',
       interaction_asm_type=(InteractionAsmType.Reactionlet),
       override_animation_context=True,
       participant_enum_override=(
      ParticipantTypeReactionlet, ParticipantTypeReactionlet.Invalid)))),
       tuning_group=GroupNames.ANIMATION), 
     'trait_asm_overrides':TunableTuple(description='\n            Tunables that will specify if a Trait will add any parameters\n            to the Sim and how it will affect their boundary conditions.\n            ',
       param_type=OptionalTunable(description='\n                Define if this trait is parameterized as an on/off value or as\n                part of an enumeration.\n                ',
       tunable=Tunable(description='\n                    The name of the parameter enumeration. For example, if this\n                    value is tailType, then the tailType actor parameter is set\n                    to the value specified in param_value, for this Sim.\n                    ',
       tunable_type=str,
       default=None),
       disabled_name='boolean',
       enabled_name='enum'),
       trait_asm_param=Tunable(description="\n                The ASM parameter for this trait. If unset, it will be auto-\n                generated depending on the instance name (e.g. 'trait_Clumsy').\n                ",
       tunable_type=str,
       default=None),
       consider_for_boundary_conditions=Tunable(description='\n                If enabled the trait_asm_param will be considered when a Sim\n                is building the goals and validating against its boundary\n                conditions.\n                This should ONLY be enabled, if we need this parameter for\n                cases like a posture transition, or boundary specific cases. \n                On regular cases like an animation outcome, this is not needed.\n                i.e. Vampire trait has an isVampire parameter set to True, so\n                when animatin out of the coffin it does different get in/out \n                animations.  When this is enabled, isVampire will be set to \n                False for every other Sim.\n                ',
       tunable_type=bool,
       default=False),
       tuning_group=GroupNames.ANIMATION), 
     'ages':TunableSet(description='\n            The allowed ages for this trait. If no ages are specified, then all\n            ages are considered valid.\n            ',
       tunable=TunableEnumEntry(tunable_type=Age,
       default=None,
       export_modes=(ExportModes.All)),
       tuning_group=GroupNames.AVAILABILITY), 
     'genders':TunableSet(description='\n            The allowed genders for this trait. If no genders are specified,\n            then all genders are considered valid.\n            ',
       tunable=TunableEnumEntry(tunable_type=Gender,
       default=None,
       export_modes=(ExportModes.All)),
       tuning_group=GroupNames.AVAILABILITY), 
     'species':TunableSet(description='\n            The allowed species for this trait. If not species are specified,\n            then all species are considered valid.\n            ',
       tunable=TunableEnumEntry(tunable_type=Species,
       default=(Species.HUMAN),
       invalid_enums=(
      Species.INVALID,),
       export_modes=(ExportModes.All)),
       tuning_group=GroupNames.AVAILABILITY), 
     'conflicting_traits':TunableList(description='\n            Conflicting traits for this trait. If the Sim has any of the\n            specified traits, then they are not allowed to be equipped with this\n            one.\n            \n            e.g.\n             Family Oriented conflicts with Hates Children, and vice-versa.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       export_modes=ExportModes.All,
       tuning_group=GroupNames.AVAILABILITY), 
     'is_npc_only':Tunable(description='\n            If checked, this trait will get removed from Sims that have a home\n            when the zone is loaded or whenever they switch to a household that\n            has a home zone.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.AVAILABILITY), 
     'entitlement':OptionalTunable(description='\n            If enabled, this trait is locked by an entitlement. Otherwise,\n            this trait is available to all players.\n            ',
       tunable=TunableEntitlement(description='\n                Entitlement required to get this trait.\n                '),
       tuning_group=GroupNames.AVAILABILITY), 
     'cas_selected_icon':TunableResourceKey(description='\n            Icon to be displayed in CAS when this trait has already been applied\n            to a Sim.\n            ',
       resource_types=CompoundTypes.IMAGE,
       default=None,
       allow_none=True,
       export_modes=(
      ExportModes.ClientBinary,),
       tuning_group=GroupNames.CAS), 
     'cas_idle_asm_key':TunableInteractionAsmResourceKey(description='\n            The ASM to use for the CAS idle.\n            ',
       default=None,
       allow_none=True,
       category='asm',
       export_modes=ExportModes.All,
       tuning_group=GroupNames.CAS), 
     'cas_idle_asm_state':Tunable(description='\n            The state to play for the CAS idle.\n            ',
       tunable_type=str,
       default=None,
       source_location='cas_idle_asm_key',
       source_query=SourceQueries.ASMState,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.CAS), 
     'cas_trait_asm_param':Tunable(description='\n            The ASM parameter for this trait for use with CAS ASM state machine,\n            driven by selection of this Trait, i.e. when a player selects the a\n            romantic trait, the Flirty ASM is given to the state machine to\n            play. The name tuned here must match the animation state name\n            parameter expected in Swing.\n            ',
       tunable_type=str,
       default=None,
       export_modes=ExportModes.All,
       tuning_group=GroupNames.CAS), 
     'tags':TunableList(description="\n            The associated categories of the trait. Need to distinguish among\n            'Personality Traits', 'Achievement Traits' and 'Walkstyle\n            Traits'.\n            ",
       tunable=TunableEnumEntry(tunable_type=(tag.Tag),
       default=(tag.Tag.INVALID)),
       export_modes=ExportModes.All,
       tuning_group=GroupNames.CAS), 
     'sim_info_fixup_actions':TunableList(description='\n            A list of fixup actions which will be performed on a sim_info with\n            this trait when it is loaded.\n            ',
       tunable=TunableVariant(career_fixup_action=_SimInfoCareerFixupAction.TunableFactory(description='\n                    A fix up action to set a career with a specific level.\n                    '),
       skill_fixup_action=_SimInfoSkillFixupAction.TunableFactory(description='\n                    A fix up action to set a skill with a specific level.\n                    '),
       unlock_fixup_action=_SimInfoUnlockFixupAction.TunableFactory(description='\n                    A fix up action to unlock certain things for a Sim\n                    '),
       perk_fixup_action=_SimInfoPerkFixupAction.TunableFactory(description='\n                    A fix up action to grant perks to a Sim. It checks perk required\n                    unlock tuning and unlocks prerequisite perks first.\n                    '),
       default='career_fixup_action'),
       tuning_group=GroupNames.CAS), 
     'sim_info_fixup_actions_timing':TunableEnumEntry(description="\n            This is DEPRECATED, don't tune this field. We usually don't do trait-based\n            fixup unless it's related to CAS stories. We keep this field only for legacy\n            support reason.\n            \n            This is mostly to optimize performance when applying fix-ups to\n            a Sim.  We ideally would not like to spend time scanning every Sim \n            on every load to see if they need fixups.  Please be sure you \n            consult a GPE whenever you are creating fixup tuning.\n            ",
       tunable_type=SimInfoFixupActionTiming,
       default=SimInfoFixupActionTiming.ON_FIRST_SIMINFO_LOAD,
       tuning_group=GroupNames.DEPRECATED,
       deprecated=True), 
     'teleport_style_interaction_to_inject':TunableReference(description='\n             When this trait is added to a Sim, if a teleport style interaction\n             is specified, any time another interaction runs, we may run this\n             teleport style interaction to shorten or replace the route to the \n             target.\n             ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION),
       class_restrictions=('TeleportStyleSuperInteraction', ),
       allow_none=True,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'interactions':OptionalTunable(description='\n            Mixer interactions that are available to Sims equipped with this\n            trait.\n            ',
       tunable=ContentSet.TunableFactory(locked_args={'phase_affordances':frozendict(), 
      'phase_tuning':None})), 
     'buffs_add_on_spawn_only':Tunable(description='\n            If unchecked, buffs are added to the Sim as soon as this trait is\n            added. If checked, buffs will be added only when the Sim is\n            instantiated and removed when the Sim uninstantiates.\n            \n            General guidelines: If the buffs only matter to Sims, for example\n            buffs that alter autonomy behavior or walkstyle, this should be\n            checked.\n            ',
       tunable_type=bool,
       default=True), 
     'buffs':TunableList(description='\n            Buffs that should be added to the Sim whenever this trait is\n            equipped.\n            ',
       tunable=TunableBuffReference(pack_safe=True),
       unique_entries=True), 
     'buffs_proximity':TunableList(description='\n            Proximity buffs that are active when this trait is equipped.\n            ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUFF)))), 
     'buff_replacements':TunableMapping(description='\n            A mapping of buff replacement. If Sim has this trait on, whenever he\n            get the buff tuned in the key of the mapping, it will get replaced\n            by the value of the mapping.\n            ',
       key_type=TunableReference(description='\n                Buff that will get replaced to apply on Sim by this trait.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
       reload_dependent=True,
       pack_safe=True),
       value_type=TunableTuple(description='\n                Data specific to this buff replacement.\n                ',
       buff_type=TunableReference(description='\n                    Buff used to replace the buff tuned as key.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.BUFF)),
       reload_dependent=True,
       pack_safe=True),
       buff_reason=OptionalTunable(description='\n                    If enabled, override the buff reason.\n                    ',
       tunable=TunableLocalizedString(description='\n                        The overridden buff reason.\n                        ')),
       buff_replacement_priority=TunableEnumEntry(description="\n                    The priority of this buff replacement, relative to other\n                    replacements. Tune this to be a higher value if you want\n                    this replacement to take precedence.\n                    \n                    e.g.\n                     (NORMAL) trait_HatesChildren (buff_FirstTrimester -> \n                                                   buff_FirstTrimester_HatesChildren)\n                     (HIGH)   trait_Male (buff_FirstTrimester -> \n                                          buff_FirstTrimester_Male)\n                                          \n                     In this case, both traits have overrides on the pregnancy\n                     buffs. However, we don't want males impregnated by aliens\n                     that happen to hate children to lose their alien-specific\n                     buffs. Therefore we tune the male replacement at a higher\n                     priority.\n                    ",
       tunable_type=TraitBuffReplacementPriority,
       default=(TraitBuffReplacementPriority.NORMAL)))), 
     'excluded_mood_types':TunableList(TunableReference(description='\n            List of moods that are prevented by having this trait.\n            ',
       manager=(services.get_instance_manager(sims4.resources.Types.MOOD)))), 
     'outfit_replacements':TunableMapping(description="\n            A mapping of outfit replacements. If the Sim has this trait, outfit\n            change requests are intercepted to produce the tuned result. If\n            multiple traits with outfit replacements exist, the behavior is\n            undefined.\n            \n            Tuning 'Invalid' as a key acts as a fallback and applies to all\n            reasons.\n            \n            Tuning 'Invalid' as a value keeps a Sim in their current outfit.\n            ",
       key_type=TunableEnumEntry(tunable_type=OutfitChangeReason,
       default=(OutfitChangeReason.Invalid)),
       value_type=TunableEnumEntry(tunable_type=OutfitChangeReason,
       default=(OutfitChangeReason.Invalid))), 
     'disable_aging':OptionalTunable(description='\n            If enabled, aging out of specific ages can be disabled.\n            ',
       tunable=TunableTuple(description='\n                The tuning that disables aging out of specific age groups.\n                ',
       allowed_ages=TunableSet(description='\n                    A list of ages that the Sim CAN age out of. If an age is in\n                    this list then the Sim is allowed to age out of it. If an\n                    age is not in this list than a Sim is not allowed to age out\n                    of it. For example, if the list only contains Child and\n                    Teen, then a Child Sim would be able to age up to Teen and\n                    a Teen Sim would be able to age up to Young Adult. But, a\n                    Young Adult, Adult, or Elder Sim would not be able to age\n                    up.\n                    ',
       tunable=TunableEnumEntry(Age, default=(Age.ADULT))),
       tooltip=OptionalTunable(description='\n                    When enabled, this tooltip will be displayed in the aging\n                    progress bar when aging is disabled because of the trait.\n                    ',
       tunable=TunableLocalizedStringFactory(description='\n                        The string that displays in the aging UI when aging up\n                        is disabled due to the trait.\n                        '))),
       tuning_group=GroupNames.SPECIAL_CASES), 
     'can_die':Tunable(description='\n            When set, Sims with this trait are allowed to die. When unset, Sims\n            are prevented from dying.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'culling_behavior':TunableVariant(description='\n            The culling behavior of a Sim with this trait.\n            ',
       default_behavior=CullingBehaviorDefault.TunableFactory(),
       immune_to_culling=CullingBehaviorImmune.TunableFactory(),
       importance_as_npc_score=CullingBehaviorImportanceAsNpc.TunableFactory(),
       default='default_behavior',
       tuning_group=GroupNames.SPECIAL_CASES), 
     'always_send_test_event_on_add':Tunable(description='\n            If checked, will send out a test event when added to a trait\n            tracker even if the receiving sim is hidden or not instanced.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'voice_effect':OptionalTunable(description='\n            The voice effect of a Sim with this trait. This is prioritized\n            against other traits with voice effects.\n            \n            The Sim may only have one voice effect at a time.\n            ',
       tunable=VoiceEffectRequest.TunableFactory()), 
     'plumbbob_override':OptionalTunable(description='\n            If enabled, allows a new plumbbob model to be used when a Sim has\n            this occult type.\n            ',
       tunable=PlumbbobOverrideRequest.TunableFactory()), 
     'vfx_mask':OptionalTunable(description='\n            If enabled when this trait is added the masks will be applied to\n            the Sim affecting the visibility of specific VFX.\n            Example: TRAIT_CHILDREN will provide a mask MASK_CHILDREN which \n            the monster battle object will only display VFX for any Sim \n            using that mask.\n            ',
       tunable=TunableEnumFlags(description="\n                Mask that will be added to the Sim's mask when the trait is\n                added.\n                ",
       enum_type=VFXMask),
       enabled_name='apply_vfx_mask',
       disabled_name='no_vfx_mask'), 
     'exclude_vfx_mask':OptionalTunable(description='\n            If enabled, when this trait is added to a Sim, the mask will be \n            applied, making VFX invisible that are also tagged with this flag.\n            ',
       tunable=TunableEnumFlags(description='\n                The Exclude VFX Mask that will be applied.\n                ',
       enum_type=ExcludeVFXMask),
       enabled_name='apply_exclude_vfx_mask',
       disabled_name='no_exclude_vfx_mask'), 
     'day_night_tracking':OptionalTunable(description="\n            If enabled, allows this trait to track various aspects of day and\n            night via buffs on the owning Sim.\n            \n            For example, if this is enabled and the Sunlight Buff is tuned with\n            buffs, the Sim will get the buffs added every time they're in\n            sunlight and removed when they're no longer in sunlight.\n            ",
       tunable=DayNightTracking.TunableFactory()), 
     'persistable':Tunable(description='\n            If checked then this trait will be saved onto the sim.  If\n            unchecked then the trait will not be saved.\n            Example unchecking:\n            Traits that are applied for the sim being in the region.\n            ',
       tunable_type=bool,
       default=True), 
     'initial_commodities':TunableSet(description='\n            A list of commodities that will be added to a sim on load, if the\n            sim has this trait.\n            \n            If a given commodity is also blacklisted by another trait that the\n            sim also has, it will NOT be added.\n            \n            Example:\n            Adult Age Trait adds Hunger.\n            Vampire Trait blacklists Hunger.\n            Hunger will not be added.\n            ',
       tunable=Commodity.TunableReference(pack_safe=True)), 
     'conditional_commodities':TunableList(description='\n            List of commodities that are conditionally added to a sim, if the\n            sim has this trait.  \n            \n            If a given commodity is also blacklisted by another trait that the\n            sim also has, it will NOT be added.\n            \n            There are no test event listeners on these conditional commodities, instead, the\n            evaluation of the tests will run on load and when a trait with conditional commodities\n            is added/removed. \n            ',
       tunable=TunableTuple(description='\n                Tuple of the commodity and its corresponding test set. \n                ',
       commodity=Commodity.TunableReference(pack_safe=True),
       tests=TunableTestSet(description='\n                    Tests that must pass to add the commodity. \n                    '),
       delay=Tunable(description='\n                    If checked then this commodity will not be tested for addition until after all sims and households \n                    have been loaded.  This may be needed for some tests such as Region which is set after traits have\n                    been loaded.  Use cautiously, as other stuff being loaded won\'t be able to successfully test against\n                    this commodity (or anything added by this commodity) during the load process.\n                    \n                    Note: Testing against other loaded traits themselves does NOT need delay checked.  Testing against \n                    buffs or commodities (or stuff added by same) added by traits WILL need delay checked.  Testing\n                    against other delayed conditional commodities (or stuff added by same) is "Don\'t do that".  Test \n                    against the trait and what the conditional commodities/stuff added by them test for if needed.\n                    ',
       tunable_type=bool,
       default=False))), 
     'initial_commodities_blacklist':TunableSet(description="\n            A list of commodities that will be prevented from being\n            added to a sim that has this trait.\n            \n            This always takes priority over any commodities listed in any\n            trait's initial_commodities.\n            \n            Example:\n            Adult Age Trait adds Hunger.\n            Vampire Trait blacklists Hunger.\n            Hunger will not be added.\n            ",
       tunable=Commodity.TunableReference(pack_safe=True)), 
     'ui_commodity_sort_override':OptionalTunable(description='\n            Optional list of commodities to override the default UI sort order.\n            ',
       tunable=TunableList(description='\n                The position of the commodity in this list represents the sort order.\n                Add all possible combination of traits in the list.\n                If we have two traits which have sort override, we will implement\n                a priority system to determine which determines which trait sort\n                order to use.\n                ',
       tunable=(Commodity.TunableReference()))), 
     'ui_category':OptionalTunable(description='\n            If enabled then this trait will be displayed in a specific category\n            within the relationship panel if this trait would be displayed\n            within that panel.\n            ',
       tunable=TunableEnumEntry(description='\n                The UI trait category that we use to categorize this trait\n                within the relationship panel.\n                ',
       tunable_type=TraitUICategory,
       default=(TraitUICategory.PERSONALITY)),
       export_modes=ExportModes.All,
       enabled_name='ui_trait_category_tag'), 
     'loot_on_trait_add':OptionalTunable(description='\n            If tuned, this list of loots will be applied when trait is added in game.\n            ',
       tunable=TunableList(description='\n                List of loot to apply on the sim when this trait is added not\n                through CAS.\n                ',
       tunable=TunableReference(description='\n                    Loot to apply.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       pack_safe=True))), 
     'npc_leave_lot_interactions':OptionalTunable(description='\n            If enabled, allows tuning a set of Leave Lot and Leave Lot Must Run\n            interactions that this trait provides. NPC Sims with this trait will\n            use these interactions to leave the lot instead of the defaults.\n            ',
       tunable=TunableTuple(description='\n                Leave Lot Now and Leave Lot Now Must Run interactions.\n                ',
       leave_lot_now_interactions=(TunableSet(TunableReference(description='\n                    If tuned, the Sim will consider these interaction when trying to run\n                    any "leave lot" situation.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       allow_none=False,
       pack_safe=True))),
       leave_lot_now_must_run_interactions=(TunableSet(TunableReference(description='\n                    If tuned, the Sim will consider these interaction when trying to run\n                    any "leave lot must run" situation.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.INTERACTION)),
       allow_none=False,
       pack_safe=True))))), 
     'hide_relationships':Tunable(description='\n            If checked, then any relationships with a Sim who has this trait\n            will not be displayed in the UI. This is done by keeping the\n            relationship from having any tracks to actually track which keeps\n            it out of the UI.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.RELATIONSHIP), 
     'whim_set':OptionalTunable(description='\n            If enabled then this trait will offer a whim set to the Sim when it\n            is active.\n            ',
       tunable=TunableReference(description='\n                A whim set that is active when this trait is active.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)),
       class_restrictions=('ObjectivelessWhimSet', ))), 
     'allow_from_gallery':Tunable(description='\n            If checked, then this trait is allowed to be transferred over from\n            Sims downloaded from the gallery.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'remove_on_death':Tunable(description='\n            If checked, when a Sim dies this trait will be removed.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'build_buy_purchase_tracking':OptionalTunable(description='\n            If enabled, allows this trait to track various build-buy purchases\n            via event listening in the trait tracker.\n            ',
       tunable=TunableList(description='\n                Loots to apply to the hamper when clothing pile is being put.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True))), 
     'event_test_based_loots':TunableList(description='\n            A list of tests that are connected to events and loots to play\n            when those tests pass.  These will only be tested for non-NPC\n            Sims.\n            ',
       tunable=TunableTuple(test=CommonEventTestVariant(description='\n                    A test event that is linked to giving the loot.\n                    '),
       loot=TunableReference(description='\n                    The loot to apply when the events pass.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', ),
       pack_safe=True))), 
     'restricted_ingredients':TunableList(description='\n            A list of food ingredients that sims with this trait will have \n            negative effects to when eaten.\n            ',
       tunable=TunableEnumEntry(description='\n                A food ingredient that sims with this trait will have negative\n                effects to when eaten.\n                ',
       tunable_type=(FoodRestrictionUtils.FoodRestrictionEnum),
       default=(FoodRestrictionUtils.FoodRestrictionEnum.INVALID),
       invalid_enums=(
      FoodRestrictionUtils.FoodRestrictionEnum.INVALID,))), 
     'bb_filter_tags':tag.TunableTags(description='\n            If this trait is used to filter the BB catalog, these tags will be\n            used to apply the filter.\n            ',
       export_modes=ExportModes.ClientBinary), 
     'bb_filter_styles':TunableList(description='\n            If this trait is used to filter the BB catalog, these styles will be\n            applied to the filter.\n            ',
       tunable=TunableStyle(description='\n                The style to use as a filter.\n                '),
       allow_none=True,
       export_modes=ExportModes.ClientBinary)}
    _asm_param_name = None
    default_trait_params = set()
    trait_statistic = None

    def __repr__(self):
        return '<Trait:({})>'.format(self.__name__)

    def __str__(self):
        return '{}'.format(self.__name__)

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._asm_param_name = cls.trait_asm_overrides.trait_asm_param
        if cls._asm_param_name is None:
            cls._asm_param_name = cls.__name__
        if cls.trait_asm_overrides.trait_asm_param is not None:
            if cls.trait_asm_overrides.consider_for_boundary_conditions:
                cls.default_trait_params.add(cls.trait_asm_overrides.trait_asm_param)
        for buff, replacement_buff in cls.buff_replacements.items():
            if buff.trait_replacement_buffs is None:
                buff.trait_replacement_buffs = {}
            buff.trait_replacement_buffs[cls] = replacement_buff

        for mood in cls.excluded_mood_types:
            if mood.excluding_traits is None:
                mood.excluding_traits = []
            mood.excluding_traits.append(cls)

    @classmethod
    def _verify_tuning_callback--- This code section failed: ---

 L. 997         0  LOAD_FAST                'cls'
                2  LOAD_ATTR                display_name
                4  POP_JUMP_IF_FALSE    62  'to 62'

 L. 998         6  LOAD_FAST                'cls'
                8  LOAD_ATTR                display_name_gender_neutral
               10  LOAD_ATTR                hash
               12  POP_JUMP_IF_TRUE     30  'to 30'

 L. 999        14  LOAD_GLOBAL              logger
               16  LOAD_ATTR                error
               18  LOAD_STR                 'Trait {} specifies a display name. It must also specify a gender-neutral display name. These must use different string keys.'
               20  LOAD_FAST                'cls'
               22  LOAD_STR                 'BadTuning'
               24  LOAD_CONST               ('owner',)
               26  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               28  POP_TOP          
             30_0  COME_FROM            12  '12'

 L.1000        30  LOAD_FAST                'cls'
               32  LOAD_ATTR                display_name
               34  LOAD_ATTR                _string_id
               36  LOAD_FAST                'cls'
               38  LOAD_ATTR                display_name_gender_neutral
               40  LOAD_ATTR                hash
               42  COMPARE_OP               ==
               44  POP_JUMP_IF_FALSE    62  'to 62'

 L.1001        46  LOAD_GLOBAL              logger
               48  LOAD_ATTR                error
               50  LOAD_STR                 'Trait {} has the same string tuned for its display name and its gender-neutral display name. These must be different strings for localization.'
               52  LOAD_FAST                'cls'
               54  LOAD_STR                 'BadTuning'
               56  LOAD_CONST               ('owner',)
               58  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
               60  POP_TOP          
             62_0  COME_FROM            44  '44'
             62_1  COME_FROM             4  '4'

 L.1002        62  LOAD_FAST                'cls'
               64  LOAD_ATTR                day_night_tracking
               66  LOAD_CONST               None
               68  COMPARE_OP               is-not
               70  POP_JUMP_IF_FALSE   246  'to 246'

 L.1003        72  LOAD_FAST                'cls'
               74  LOAD_ATTR                day_night_tracking
               76  LOAD_ATTR                sunlight_buffs
               78  POP_JUMP_IF_TRUE    122  'to 122'
               80  LOAD_FAST                'cls'
               82  LOAD_ATTR                day_night_tracking
               84  LOAD_ATTR                shade_buffs
               86  POP_JUMP_IF_TRUE    122  'to 122'

 L.1004        88  LOAD_FAST                'cls'
               90  LOAD_ATTR                day_night_tracking
               92  LOAD_ATTR                day_buffs
               94  POP_JUMP_IF_TRUE    122  'to 122'
               96  LOAD_FAST                'cls'
               98  LOAD_ATTR                day_night_tracking
              100  LOAD_ATTR                night_buffs
              102  POP_JUMP_IF_TRUE    122  'to 122'

 L.1005       104  LOAD_GLOBAL              logger
              106  LOAD_ATTR                error
              108  LOAD_STR                 'Trait {} has Day Night Tracking enabled but no buffs are tuned. Either tune buffs or disable the tracking.'
              110  LOAD_FAST                'cls'
              112  LOAD_STR                 'BadTuning'
              114  LOAD_CONST               ('owner',)
              116  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              118  POP_TOP          
              120  JUMP_FORWARD        246  'to 246'
            122_0  COME_FROM           102  '102'
            122_1  COME_FROM            94  '94'
            122_2  COME_FROM            86  '86'
            122_3  COME_FROM            78  '78'

 L.1007       122  LOAD_GLOBAL              Trait
              124  LOAD_ATTR                DAY_NIGHT_TRACKING_BUFF_TAG
              126  STORE_DEREF              'tracking_buff_tag'

 L.1008       128  LOAD_GLOBAL              any
              130  LOAD_CLOSURE             'tracking_buff_tag'
              132  BUILD_TUPLE_1         1 
              134  LOAD_GENEXPR             '<code_object <genexpr>>'
              136  LOAD_STR                 'Trait._verify_tuning_callback.<locals>.<genexpr>'
              138  MAKE_FUNCTION_8          'closure'
              140  LOAD_FAST                'cls'
              142  LOAD_ATTR                day_night_tracking
              144  LOAD_ATTR                sunlight_buffs
              146  GET_ITER         
              148  CALL_FUNCTION_1       1  '1 positional argument'
              150  CALL_FUNCTION_1       1  '1 positional argument'
              152  POP_JUMP_IF_TRUE    232  'to 232'

 L.1009       154  LOAD_GLOBAL              any
              156  LOAD_CLOSURE             'tracking_buff_tag'
              158  BUILD_TUPLE_1         1 
              160  LOAD_GENEXPR             '<code_object <genexpr>>'
              162  LOAD_STR                 'Trait._verify_tuning_callback.<locals>.<genexpr>'
              164  MAKE_FUNCTION_8          'closure'
              166  LOAD_FAST                'cls'
              168  LOAD_ATTR                day_night_tracking
              170  LOAD_ATTR                shade_buffs
              172  GET_ITER         
              174  CALL_FUNCTION_1       1  '1 positional argument'
              176  CALL_FUNCTION_1       1  '1 positional argument'
              178  POP_JUMP_IF_TRUE    232  'to 232'

 L.1010       180  LOAD_GLOBAL              any
              182  LOAD_CLOSURE             'tracking_buff_tag'
              184  BUILD_TUPLE_1         1 
              186  LOAD_GENEXPR             '<code_object <genexpr>>'
              188  LOAD_STR                 'Trait._verify_tuning_callback.<locals>.<genexpr>'
              190  MAKE_FUNCTION_8          'closure'
              192  LOAD_FAST                'cls'
              194  LOAD_ATTR                day_night_tracking
              196  LOAD_ATTR                day_buffs
              198  GET_ITER         
              200  CALL_FUNCTION_1       1  '1 positional argument'
              202  CALL_FUNCTION_1       1  '1 positional argument'
              204  POP_JUMP_IF_TRUE    232  'to 232'

 L.1011       206  LOAD_GLOBAL              any
              208  LOAD_CLOSURE             'tracking_buff_tag'
              210  BUILD_TUPLE_1         1 
              212  LOAD_GENEXPR             '<code_object <genexpr>>'
              214  LOAD_STR                 'Trait._verify_tuning_callback.<locals>.<genexpr>'
              216  MAKE_FUNCTION_8          'closure'
              218  LOAD_FAST                'cls'
              220  LOAD_ATTR                day_night_tracking
              222  LOAD_ATTR                night_buffs
              224  GET_ITER         
              226  CALL_FUNCTION_1       1  '1 positional argument'
              228  CALL_FUNCTION_1       1  '1 positional argument'
              230  POP_JUMP_IF_FALSE   246  'to 246'
            232_0  COME_FROM           204  '204'
            232_1  COME_FROM           178  '178'
            232_2  COME_FROM           152  '152'

 L.1012       232  LOAD_GLOBAL              logger
              234  LOAD_METHOD              error

 L.1021       236  LOAD_STR                 'Trait {} has Day Night tracking with an invalid\n                    buff. All buffs must be tagged with {} in order to be\n                    used as part of Day Night Tracking. Add these buffs with the\n                    understanding that, regardless of what system added them, they\n                    will always be on the Sim when the condition is met (i.e.\n                    Sunlight Buffs always added with sunlight is out) and they will\n                    always be removed when the condition is not met. Even if another\n                    system adds the buff, they will be removed if this trait is\n                    tuned to do that.\n                    '
              238  LOAD_FAST                'cls'
              240  LOAD_DEREF               'tracking_buff_tag'
              242  CALL_METHOD_3         3  '3 positional arguments'
              244  POP_TOP          
            246_0  COME_FROM           230  '230'
            246_1  COME_FROM           120  '120'
            246_2  COME_FROM            70  '70'

 L.1023       246  SETUP_LOOP          292  'to 292'
              248  LOAD_FAST                'cls'
              250  LOAD_ATTR                buffs
              252  GET_ITER         
            254_0  COME_FROM           268  '268'
              254  FOR_ITER            290  'to 290'
              256  STORE_FAST               'buff_reference'

 L.1024       258  LOAD_FAST                'buff_reference'
              260  LOAD_ATTR                buff_type
              262  LOAD_ATTR                broadcaster
              264  LOAD_CONST               None
              266  COMPARE_OP               is-not
              268  POP_JUMP_IF_FALSE   254  'to 254'

 L.1025       270  LOAD_GLOBAL              logger
              272  LOAD_ATTR                error
              274  LOAD_STR                 'Trait {} has a buff {} with a broadcaster tuned that will never be removed. This is a potential performance hit, and a GPE should decide whether this is the best place for such.'
              276  LOAD_FAST                'cls'
              278  LOAD_FAST                'buff_reference'
              280  LOAD_STR                 'rmccord'
              282  LOAD_CONST               ('owner',)
              284  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              286  POP_TOP          
              288  JUMP_BACK           254  'to 254'
              290  POP_BLOCK        
            292_0  COME_FROM_LOOP      246  '246'

 L.1026       292  SETUP_LOOP          332  'to 332'
              294  LOAD_FAST                'cls'
              296  LOAD_ATTR                initial_commodities
              298  GET_ITER         
            300_0  COME_FROM           308  '308'
              300  FOR_ITER            330  'to 330'
              302  STORE_FAST               'commodity'

 L.1027       304  LOAD_FAST                'commodity'
              306  LOAD_ATTR                persisted_tuning
          308_310  POP_JUMP_IF_TRUE    300  'to 300'

 L.1028       312  LOAD_GLOBAL              logger
              314  LOAD_METHOD              error
              316  LOAD_STR                 'Trait {} has an initial commodity {} that does not have persisted tuning.'

 L.1029       318  LOAD_FAST                'cls'

 L.1030       320  LOAD_FAST                'commodity'
              322  CALL_METHOD_3         3  '3 positional arguments'
              324  POP_TOP          
          326_328  JUMP_BACK           300  'to 300'
              330  POP_BLOCK        
            332_0  COME_FROM_LOOP      292  '292'

 L.1031       332  SETUP_LOOP          408  'to 408'
              334  LOAD_FAST                'cls'
              336  LOAD_ATTR                conditional_commodities
              338  GET_ITER         
            340_0  COME_FROM           382  '382'
              340  FOR_ITER            406  'to 406'
              342  STORE_FAST               'commodity_info'

 L.1032       344  LOAD_FAST                'commodity_info'
              346  LOAD_ATTR                commodity
              348  LOAD_ATTR                persisted_tuning
          350_352  POP_JUMP_IF_TRUE    370  'to 370'

 L.1033       354  LOAD_GLOBAL              logger
              356  LOAD_METHOD              error
              358  LOAD_STR                 'Trait {} has a conditional initial commodity {} that does not have persisted tuning.'

 L.1034       360  LOAD_FAST                'cls'

 L.1035       362  LOAD_FAST                'commodity_info'
              364  LOAD_ATTR                commodity
              366  CALL_METHOD_3         3  '3 positional arguments'
              368  POP_TOP          
            370_0  COME_FROM           350  '350'

 L.1036       370  LOAD_GLOBAL              len
              372  LOAD_FAST                'commodity_info'
              374  LOAD_ATTR                tests
              376  CALL_FUNCTION_1       1  '1 positional argument'
              378  LOAD_CONST               0
              380  COMPARE_OP               ==
          382_384  POP_JUMP_IF_FALSE   340  'to 340'

 L.1037       386  LOAD_GLOBAL              logger
              388  LOAD_METHOD              error
              390  LOAD_STR                 'Trait {} has a conditional initial commodity {} that does not have any tests.'

 L.1038       392  LOAD_FAST                'cls'

 L.1039       394  LOAD_FAST                'commodity_info'
              396  LOAD_ATTR                commodity
              398  CALL_METHOD_3         3  '3 positional arguments'
              400  POP_TOP          
          402_404  JUMP_BACK           340  'to 340'
              406  POP_BLOCK        
            408_0  COME_FROM_LOOP      332  '332'

 L.1041       408  LOAD_FAST                'cls'
              410  LOAD_ATTR                is_preference_trait
          412_414  POP_JUMP_IF_FALSE   446  'to 446'

 L.1042       416  LOAD_FAST                'cls'
              418  LOAD_ATTR                trait_type
              420  LOAD_GLOBAL              PreferenceTypes
              422  COMPARE_OP               not-in
          424_426  POP_JUMP_IF_FALSE   474  'to 474'

 L.1043       428  LOAD_GLOBAL              logger
              430  LOAD_METHOD              error
              432  LOAD_STR                 'Trait {} is a preference but has invalid trait type {}'

 L.1044       434  LOAD_FAST                'cls'

 L.1045       436  LOAD_FAST                'cls'
              438  LOAD_ATTR                trait_type
              440  CALL_METHOD_3         3  '3 positional arguments'
              442  POP_TOP          
              444  JUMP_FORWARD        474  'to 474'
            446_0  COME_FROM           412  '412'

 L.1046       446  LOAD_FAST                'cls'
              448  LOAD_ATTR                trait_type
              450  LOAD_GLOBAL              PreferenceTypes
              452  COMPARE_OP               in
          454_456  POP_JUMP_IF_FALSE   474  'to 474'

 L.1047       458  LOAD_GLOBAL              logger
              460  LOAD_METHOD              error
              462  LOAD_STR                 'Trait {} is NOT a preference but has a preference trait type {}'

 L.1048       464  LOAD_FAST                'cls'

 L.1049       466  LOAD_FAST                'cls'
              468  LOAD_ATTR                trait_type
              470  CALL_METHOD_3         3  '3 positional arguments'
              472  POP_TOP          
            474_0  COME_FROM           454  '454'
            474_1  COME_FROM           444  '444'
            474_2  COME_FROM           424  '424'

Parse error at or near `COME_FROM' instruction at offset 246_0

    @constproperty
    def is_gameplay_object_preference_trait():
        return False

    @constproperty
    def is_preference_trait():
        return False

    @classproperty
    def is_object_preference(cls):
        return False

    @classmethod
    def is_preference_subject(cls, subject):
        return False

    @classmethod
    def is_preference_subject_in_subject_set(cls, subject_set):
        return False

    @classproperty
    def is_personality_trait(cls):
        return cls.trait_type == TraitType.PERSONALITY

    @classproperty
    def is_aspiration_trait(cls):
        return cls.trait_type == TraitType.ASPIRATION

    @classproperty
    def is_gender_option_trait(cls):
        return cls.trait_type == TraitType.GENDER_OPTIONS

    @classproperty
    def is_ghost_trait(cls):
        return cls.trait_type == TraitType.GHOST

    @classproperty
    def is_robot_trait(cls):
        return cls.trait_type == TraitType.ROBOT

    @classmethod
    def is_valid_trait(cls, sim_info_data):
        if cls.ages:
            if sim_info_data.age not in cls.ages:
                return False
        else:
            if cls.genders:
                if sim_info_data.gender not in cls.genders:
                    return False
            if cls.species and sim_info_data.species not in cls.species:
                return False
        return True

    @classmethod
    def should_apply_fixup_actions(cls, fixup_source):
        if cls.sim_info_fixup_actions:
            if cls.sim_info_fixup_actions_timing == fixup_source:
                if fixup_source != SimInfoFixupActionTiming.ON_FIRST_SIMINFO_LOAD:
                    logger.warn('Trait {} has fixup actions not from CAS flow.This should only happen to old saves before EP08', cls,
                      owner='yozhang')
                return True
        return False

    @classmethod
    def apply_fixup_actions(cls, sim_info):
        for fixup_action in cls.sim_info_fixup_actions:
            fixup_action(sim_info)

    @classmethod
    def can_age_up(cls, current_age):
        if not cls.disable_aging:
            return True
        return current_age in cls.disable_aging.allowed_ages

    @classmethod
    def is_conflicting(cls, trait):
        if trait is None:
            return False
        else:
            if cls.conflicting_traits:
                if trait in cls.conflicting_traits:
                    return True
            if trait.conflicting_traits and cls in trait.conflicting_traits:
                return True
        return False

    @classmethod
    def get_outfit_change_reason(cls, outfit_change_reason):
        replaced_reason = cls.outfit_replacements.get(outfit_change_reason if outfit_change_reason is not None else OutfitChangeReason.Invalid)
        if replaced_reason is not None:
            return replaced_reason
        if outfit_change_reason is not None:
            replaced_reason = cls.outfit_replacements.get(OutfitChangeReason.Invalid)
            if replaced_reason is not None:
                return replaced_reason
        return outfit_change_reason

    @classmethod
    def get_teleport_style_interaction_to_inject(cls):
        return cls.teleport_style_interaction_to_inject

    @classmethod
    def register_tuned_animation(cls, *_, **__):
        pass