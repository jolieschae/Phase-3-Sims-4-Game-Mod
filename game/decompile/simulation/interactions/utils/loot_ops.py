# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\interactions\utils\loot_ops.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 75944 bytes
from protocolbuffers import Consts_pb2, UI_pb2, DistributorOps_pb2
from protocolbuffers.DistributorOps_pb2 import SetWhimBucks
from protocolbuffers.InteractionOps_pb2 import TravelSimsToZone
from clock import ClockSpeedMode
from distributor.ops import BreakThroughMessage, GenericProtocolBufferOp
from distributor.system import Distributor
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeSingleSim
from interactions.utils import LootType
from interactions.utils.common import InteractionUtils
from interactions.utils.loot_basic_op import BaseLootOperation, BaseTargetedLootOperation
from objects.components import types
from objects.components.inventory_enums import InventoryType
from objects.components.portal_lock_data import LockAllWithGenusException, LockAllWithSimIdExceptionData, LockAllWithSituationJobExceptionData, LockRankedStatisticData, LockCreatureData
from objects.components.portal_locking_enums import LockPriority, LockType, ClearLock
from objects.components.spawner_component_enums import SpawnerType
from objects.components.state_references import TunableStateValueReference
from objects.gallery_tuning import ContentSource
from objects.slot_strategy import SlotStrategyVariant
from sims.funds import FundsSource, get_funds_for_source
from sims.unlock_tracker import TunableUnlockVariant
from sims4 import math
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, TunableRange, TunableReference, OptionalTunable, TunableRealSecond, TunableVariant, TunableEnumEntry, TunableList, TunableFactory, HasTunableSingletonFactory, AutoFactoryInit, TunablePackSafeReference, TunableTuple, TunableEnumSet
from traits.trait_type import TraitType
from tunable_multiplier import TunableMultiplier
from tunable_utils.tested_list import TunableTestedList
from ui.notebook_tuning import NotebookSubCategories
from ui.ui_dialog import UiDialogOk, CommandArgType, UiDialog, UiDialogResponse
from ui.ui_dialog_labeled_icons import UiDialogAspirationProgress, UiDialogIcons
from ui.ui_dialog_notification import UiDialogNotification
from ui.ui_dialog_notification_story_progression_discovery import UIDialogNotificationStoryProgressionDiscovery
from ui.ui_dialog_reveal_sequence import UiDialogRevealSequence
from ui.ui_lifestyles_dialog import UiDialogNpcDisplay
import build_buy, distributor.system, enum, random, services, sims4.log, sims4.resources, tag, telemetry_helper, venues.venue_constants
logger = sims4.log.Logger('LootOperations')
FLOAT_TO_PERCENT = 0.01
TELEMETRY_GROUP_LOOT_OPS = 'LOOT'
TELEMETRY_HOOK_DETECTIVE_CLUE = 'DECL'
TELEMETRY_DETECTIVE_CLUE_FOUND = 'clue'
loot_op_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_LOOT_OPS)

class BaseGameLootOperation(BaseLootOperation):
    FACTORY_TUNABLES = {'locked_args': {'advertise': False}}


class LifeExtensionLootOp(BaseLootOperation):

    class RestoreDaysFromAgingProgress(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'days_to_restore': TunableRange(tunable_type=int,
                              default=0,
                              minimum=0)}

        def perform(self, subject, *_, **__):
            subject.decrement_age_progress(self.days_to_restore)

    class ResetAgingProgressInCategory(HasTunableSingletonFactory, AutoFactoryInit):

        def perform(self, subject, *_, **__):
            subject.reset_age_progress()

    class AddDaysToAgingProgress(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'days_to_add': TunableRange(tunable_type=int,
                          default=0,
                          minimum=0)}

        def perform(self, subject, *_, **__):
            subject.increment_age_progress(self.days_to_add)

    class FillAgingProgressInCategory(HasTunableSingletonFactory, AutoFactoryInit):

        def perform(self, subject, *_, **__):
            subject.fill_age_progress()

    FACTORY_TUNABLES = {'bonus_days':TunableRange(description="\n            Number of bonus days to be granted to the target's life.\n            ",
       tunable_type=int,
       default=1,
       minimum=0), 
     'modify_aging_progress':TunableVariant(description='\n            If enabled, this loot will modify aging progress of a sim.\n            ',
       restore_days_from_aging_progress=RestoreDaysFromAgingProgress.TunableFactory(),
       reset_aging_progress_in_category=ResetAgingProgressInCategory.TunableFactory(),
       add_days_to_aging_progress=AddDaysToAgingProgress.TunableFactory(),
       fill_aging_progress_in_category=FillAgingProgressInCategory.TunableFactory(),
       locked_args={'disabled': None},
       default='disabled')}

    def __init__(self, bonus_days, modify_aging_progress, **kwargs):
        (super().__init__)(**kwargs)
        self.bonus_days = bonus_days
        self.modify_aging_progress = modify_aging_progress

    @property
    def loot_type(self):
        return LootType.LIFE_EXTENSION

    def _apply_to_subject_and_target(self, subject, target, resolver):
        subject.add_bonus_days(self.bonus_days)
        if self.modify_aging_progress is not None:
            self.modify_aging_progress.perform(subject)


class StateChangeLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will change the state of the subject.\n            ', 
     'state_value':TunableStateValueReference(), 
     'force_update':Tunable(description="\n            If checked, force update the subject's state.\n            ",
       tunable_type=bool,
       default=False)}

    @TunableFactory.factory_option
    def subject_participant_type_options(**kwargs):
        return {'subject': TunableVariant(description='\n            The subject of this loot.\n            ',
                      participant=TunableEnumEntry(description='"\n                The participant type for the subject of this loot.\n                ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.Actor),
                      invalid_enums=(
                     ParticipantType.Invalid,)),
                      all_objects_with_tag=TunableEnumEntry(description='\n                All objects with this tag.\n                ',
                      tunable_type=(tag.Tag),
                      default=(tag.Tag.INVALID),
                      invalid_enums=(
                     tag.Tag.INVALID,)),
                      default='participant')}

    def __init__(self, state_value, force_update, **kwargs):
        (super().__init__)(**kwargs)
        self.state_value = state_value
        self.force_update = force_update

    def _apply_to_subject_and_target(self, subject, target, resolver):
        subject_obj = self._get_object_from_recipient(subject)
        if subject_obj is not None:
            state_value = self.state_value
            subject_obj.set_state((state_value.state), state_value, force_update=(self.force_update))


class DialogLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'dialog': TunableVariant(description='\n            Type of dialog to show.\n            ',
                 dialog_icon=UiDialogIcons.TunableFactory(description='\n                Display a dialog that has tunable icons as content.\n                '),
                 notification=UiDialogNotification.TunableFactory(description='\n                This text will display in a notification pop up when completed.\n                '),
                 dialog_ok=UiDialogOk.TunableFactory(description='\n                Display a dialog with an okay button.\n                '),
                 aspiration_progress=UiDialogAspirationProgress.TunableFactory(description="\n                Display a dialog that will show the Sim's progress towards one\n                or more aspirations.\n                "),
                 reveal_sequence=UiDialogRevealSequence.TunableFactory(description="\n                Display a dialog that will show the Sim's gig photos in a sequence.\n                "),
                 npc_display=UiDialogNpcDisplay.TunableFactory(description='\n                Display a dialog that will show a list of Sims and information\n                about them in a grid.\n                '),
                 story_progression_discovery_notification=UIDialogNotificationStoryProgressionDiscovery.TunableFactory(description='\n                Display a dialog that displays text informing the player of a recently completed story progression\n                chapter. \n                ',
                 locked_args={'text': None}),
                 default='notification')}

    def __init__(self, dialog, **kwargs):
        (super().__init__)(**kwargs)
        self.dialog = dialog

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is not None:
            if not services.current_zone().is_zone_loading:
                owner = subject if subject.is_sim else services.get_active_sim()
                if owner is not None:
                    if owner.is_selectable:
                        dialog = self.dialog(owner, resolver)
                        dialog.show_dialog(event_id=(self.dialog.factory.DIALOG_MSG_TYPE))


class SimInteractionDialogLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'dialog':UiDialog.TunableFactory(description='\n            The dialog that will display to the user.\n            '), 
     'possible_responses':TunableTestedList(description='\n            A tunable tested list of the possible responses to this dialog.\n            ',
       tunable_type=TunableTuple(description='\n                A possible response for this dialog.\n                ',
       text=TunableLocalizedStringFactory(description='\n                    The text of the response field.\n                    '),
       loot=TunableList(description='\n                    A list of loot that will be applied when the player selects this response.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))))}

    def __init__(self, dialog, possible_responses, **kwargs):
        (super().__init__)(**kwargs)
        self.dialog = dialog
        self.possible_responses = possible_responses

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject is None:
            return subject.is_sim or None
        else:
            return target is None or target.is_sim or None
        responses = []
        for index, possible_response in self.possible_responses(resolver=resolver, yield_index=True):
            responses.append(UiDialogResponse(dialog_response_id=index, text=(possible_response.text),
              ui_request=(UiDialogResponse.UiDialogUiRequest.NO_REQUEST)))

        dialog = self.dialog(subject, target_sim_id=(target.id), resolver=resolver)
        dialog.set_responses(responses)

        def response(dialog):
            if 0 <= dialog.response < len(self.possible_responses):
                for loot_action in self.possible_responses[dialog.response].item.loot:
                    loot_action.apply_to_resolver(resolver)

        dialog.show_dialog(on_response=response)


class AddTraitLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will add the specified trait.\n            ', 
     'trait':TunableReference(description='\n            The trait to be added.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT)), 
     'replace_if_available':OptionalTunable(description='\n            The trait to be replaced if the sim has it. If a trait is specified here,\n            this trait will be removed and the trait to add will be added to \n            the index of this removed trait.\n            ',
       tunable=TunablePackSafeReference(description='\n            The trait that will be removed if the sim has it, it will still be removed\n            even if the trait that needs to be added is not added successfully. \n            ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT))))}

    def __init__(self, trait, replace_if_available, **kwargs):
        (super().__init__)(**kwargs)
        self._trait = trait
        self._replace_if_available = replace_if_available

    def _apply_to_subject_and_target(self, subject, target, resolver):
        index = None
        if self._replace_if_available is not None:
            if self._replace_if_available in subject.trait_tracker:
                index = subject.trait_tracker.personality_traits.index(self._replace_if_available)
                subject.remove_trait(self._replace_if_available)
        subject.add_trait((self._trait), index_in_personality_list=index)


class RemoveTraitLootOp(BaseLootOperation):

    class _BaseRemoveTrait(HasTunableSingletonFactory, AutoFactoryInit):

        def get_traits_to_remove(self, subject, target, resolver):
            raise NotImplementedError('Attempting to use the _BaseRemoveTrait base class, use sub-classes instead.')

    class _RemoveSpecificTrait(_BaseRemoveTrait):
        FACTORY_TUNABLES = {'specific_trait': TunablePackSafeReference(description='\n                The trait to be removed.\n                ',
                             manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)))}

        def get_traits_to_remove(self, subject, target, resolver):
            return (
             self.specific_trait,)

    class _RemoveRandomTrait(_BaseRemoveTrait):
        FACTORY_TUNABLES = {'trait_type': TunableEnumEntry(default=(TraitType.PERSONALITY),
                         tunable_type=TraitType,
                         invalid_enums=(TraitType.PERSONALITY))}

        def get_traits_to_remove(self, subject, target, resolver):
            trait_to_remove = None
            traits_to_consider = [trait for trait in subject.trait_tracker if trait.trait_type == self.trait_type]
            if traits_to_consider:
                trait_to_remove = random.choice(traits_to_consider)
            else:
                logger.warn('_RemoveRandomTrait could not find a valid trait to remove.')
            return (trait_to_remove,)

    class _RemoveRandomPersonalityTrait(_BaseRemoveTrait):
        FACTORY_TUNABLES = {'traits_to_not_consider': TunableList(description='\n                Personality traits that should not be considered for removal. Leave\n                blank to consider all personality traits.\n                ',
                                     tunable=TunableReference(description='\n                    A personality trait that should not be removed.\n                    ',
                                     manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
                                     pack_safe=True))}

        def get_traits_to_remove(self, subject, target, resolver):
            trait_to_remove = None
            personality_traits_to_consider = [trait for trait in subject.trait_tracker.personality_traits if trait not in self.traits_to_not_consider]
            if personality_traits_to_consider:
                trait_to_remove = random.choice(personality_traits_to_consider)
            else:
                logger.warn('RemoveRandomPersonalityTraitLootOp could not find a valid personality trait to remove.')
            return (trait_to_remove,)

    class _RemoveTraitsOfType(_BaseRemoveTrait):
        FACTORY_TUNABLES = {'trait_types': TunableEnumSet(description='\n                A set of trait types to find and remove.\n                ',
                          enum_type=TraitType,
                          enum_default=(TraitType.GAMEPLAY),
                          allow_empty_set=False)}

        def get_traits_to_remove(self, subject, target, resolver):
            trait_tracker = subject.trait_tracker
            if trait_tracker is None:
                return ()
            traits = []
            for trait_type in self.trait_types:
                traits.extend(trait_tracker.get_traits_of_type(trait_type))

            return traits

    class _RemoveAllTraitsFromList(_BaseRemoveTrait):
        FACTORY_TUNABLES = {'trait_list': TunableList(description='\n                The list of traits that will be removed.\n                ',
                         tunable=TunableReference(description='\n                    A trait that will be removed by this loot.\n                    ',
                         manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
                         pack_safe=True))}

        def get_traits_to_remove(self, subject, target, resolver):
            return self.trait_list

    FACTORY_TUNABLES = {'trait': TunableVariant(description='\n            Type of trait removal to perform.\n            ',
                specific_trait=(_RemoveSpecificTrait.TunableFactory()),
                random_personality_trait=(_RemoveRandomPersonalityTrait.TunableFactory()),
                random_trait=(_RemoveRandomTrait.TunableFactory()),
                traits_of_type=(_RemoveTraitsOfType.TunableFactory()),
                all_from_list=(_RemoveAllTraitsFromList.TunableFactory()),
                default='specific_trait')}

    def __init__(self, trait, **kwargs):
        (super().__init__)(**kwargs)
        self._trait = trait

    def _apply_to_subject_and_target(self, subject, target, resolver):
        traits_to_remove = self._trait.get_traits_to_remove(subject, target, resolver)
        for trait_to_remove in traits_to_remove:
            if trait_to_remove is not None:
                subject.remove_trait(trait_to_remove)


class HouseholdFundsInterestLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will deliver interest income to the current Household for their current funds,\n            based on the percentage tuned against total held. \n        ', 
     'interest_rate':Tunable(description='\n            The percentage of interest to apply to current funds.\n            ',
       tunable_type=int,
       default=0), 
     'notification':OptionalTunable(description='\n            If enabled, this notification will display when this interest payment is made.\n            Token 0 is the Sim - i.e. {0.SimFirstName}\n            Token 1 is the interest payment amount - i.e. {1.Money}\n            ',
       tunable=UiDialogNotification.TunableFactory())}

    def __init__(self, interest_rate, notification, **kwargs):
        (super().__init__)(**kwargs)
        self._interest_rate = interest_rate
        self._notification = notification

    def _apply_to_subject_and_target(self, subject, target, resolver):
        pay_out = int(subject.household.funds.money * self._interest_rate * FLOAT_TO_PERCENT)
        subject.household.funds.add(pay_out, Consts_pb2.TELEMETRY_INTERACTION_REWARD, self._get_object_from_recipient(subject))
        if self._notification is not None:
            dialog = self._notification(subject, resolver)
            dialog.show_dialog(event_id=(self._notification.factory.DIALOG_MSG_TYPE), additional_tokens=(
             pay_out,))


class FireLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'fire_count': TunableRange(description='\n            The number of fires to create.  Because of placement restrictions or fire availability, \n            there is no guarantee that this many fires will be created.\n            ',
                     tunable_type=int,
                     default=1,
                     minimum=1,
                     maximum=10)}

    def __init__(self, fire_count, **kwargs):
        (super().__init__)(**kwargs)
        self._fire_count = fire_count

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Invalid subject specified for this loot operation. {}  Please fix in tuning.', self)
            return
        subject_obj = self._get_object_from_recipient(subject)
        if subject_obj is None:
            logger.error('No valid object for subject specified for this loot operation. {}  Please fix in tuning.', resolver)
            return
        fire_service = services.get_fire_service()
        fire_service.spawn_fire_at_object(subject_obj, num_fires=(self._fire_count))


class UnlockLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'unlock_item':TunableUnlockVariant(description='\n            The unlock item that will be given to the Sim.\n            Note that if the item has a custom name, it will not be persisted through the Gallery.\n            '), 
     'notification':OptionalTunable(description='\n            If enabled, this notification will display when the item is unlocked.\n            The display name of the unlock will be added as a string token.\n            ',
       tunable=UiDialogNotification.TunableFactory())}

    def __init__(self, unlock_item, notification, **kwargs):
        (super().__init__)(**kwargs)
        self._unlock_item = unlock_item
        self._notification = notification

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Subject {} is None for the loot {}..', self.subject, self)
            return
        else:
            subject.is_sim or logger.error('Subject {} is not Sim for the loot {}.', self.subject, self)
            return
        if subject.unlock_tracker is None:
            return
        if self._unlock_item is None:
            return
        mark_as_new = getattr(self._unlock_item, 'unlock_as_new', False)
        subject.unlock_tracker.add_unlock((self._unlock_item), None, mark_as_new=mark_as_new)
        if self._notification is not None:
            dialog = self._notification(subject, resolver)
            dialog.show_dialog(event_id=(self._notification.factory.DIALOG_MSG_TYPE), response_command_tuple=(
             CommandArgType.ARG_TYPE_INT, subject.sim_id),
              additional_tokens=(
             self._unlock_item.get_display_name(subject),))


class CollectibleShelveItem(BaseLootOperation):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, target_participant_type=ParticipantType.Object, **kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        target_slot = subject.get_collectible_slot()
        if target_slot:
            for runtime_slot in target.get_runtime_slots_gen(bone_name_hash=(sims4.hash_util.hash32(target_slot))):
                if runtime_slot and runtime_slot.empty:
                    runtime_slot.add_child(subject)
                    return True

        return False


class FireDeactivateSprinklerLootOp(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        fire_service = services.get_fire_service()
        if fire_service is not None:
            fire_service.deactivate_sprinkler_system()


class ExtinguishNearbyFireLootOp(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Subject {} is None for the loot {}..', self.subject, self)
            return
        fire_service = services.get_fire_service()
        if fire_service is None:
            logger.error('Fire Service in none when calling the lootop: {}.', self)
            return
        subject = self._get_object_from_recipient(subject)
        fire_service.extinguish_nearby_fires(subject)
        return True


class AwardWhimBucksLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will give the specified number of whim bucks to the sim. \n            ', 
     'whim_bucks':TunableRange(description='\n            The number of whim bucks to give.\n            ',
       tunable_type=int,
       default=1,
       minimum=1)}

    def __init__(self, whim_bucks, **kwargs):
        (super().__init__)(**kwargs)
        self._whim_bucks = whim_bucks

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject is None:
            logger.error('Subject {} is None for the loot {}..', self.subject, self)
            return False
        subject.apply_satisfaction_points_delta(self._whim_bucks, SetWhimBucks.COMMAND)


class RefreshInventoryItemsDecayModifiers(BaseLootOperation):
    FACTORY_TUNABLES = {'inventory_types':TunableList(description='\n            List of inventory type that we need to refresh. Inventory item object\n            which currently is in one of this inventory types will be refreshed.\n            ',
       tunable=TunableEnumEntry(description='\n                The type of inventory.\n                ',
       tunable_type=InventoryType,
       default=(InventoryType.UNDEFINED),
       pack_safe=True)), 
     'locked_args':{'subject': None}}

    def __init__(self, *args, inventory_types, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.inventory_types = inventory_types

    def _apply_to_subject_and_target(self, subject, target, resolver):
        inventory_manager = services.inventory_manager()
        for obj in inventory_manager.objects:
            inventory_item_component = obj.inventoryitem_component
            inventory_type = inventory_item_component.current_inventory_type
            if inventory_type is not None and inventory_type in self.inventory_types:
                inventory_item_component.refresh_decay_modifiers()


class DiscoverClueLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'career_reference':TunableReference(description='\n            A reference to the detective career that keeps track of what clues\n            to display to the player.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.CAREER),
       class_restrictions=('DetectiveCareer', )), 
     'fallback_actions':TunableReference(description='\n            List of loot actions that will occur if there are no more clues to\n            be discovered. This can be used to hook up a notification, for\n            example.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.ACTION),
       allow_none=True,
       class_restrictions=('LootActions', 'RandomWeightedLoot'))}

    def __init__(self, *args, career_reference, fallback_actions, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.career_reference = career_reference
        self.fallback_actions = fallback_actions

    @property
    def loot_type(self):
        return LootType.DISCOVER_CLUE

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject.notebook_tracker is None:
            logger.warn("Trying to award a DiscoverClueLootOp to {}, but they don't have a notebook. LOD issue?", subject)
            return
        else:
            career = subject.careers.get(self.career_reference.guid64)
            if career is None:
                logger.error('Failed to find career {} on Sim {}.', (self.career_reference),
                  subject, owner='bhill')
                return
            clue = career.pop_unused_clue()
            if clue is None:
                if self.fallback_actions:
                    for action in self.fallback_actions:
                        action.apply_to_resolver(resolver)

                return
            if clue.notification is not None:
                dialog = clue.notification(subject, resolver=resolver)
                if dialog is not None:
                    dialog.show_dialog()
        if clue.notebook_entry is not None:
            subject.notebook_tracker.unlock_entry(clue.notebook_entry())
        with telemetry_helper.begin_hook(loot_op_telemetry_writer, TELEMETRY_HOOK_DETECTIVE_CLUE, sim_info=subject) as (hook):
            hook.write_guid(TELEMETRY_DETECTIVE_CLUE_FOUND, clue.guid64)


class NewCrimeLootOp(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'career_reference': TunableReference(description='\n            A reference to the detective career that keeps track of what crime\n            is currently being tracked.\n            ',
                           manager=(services.get_instance_manager(sims4.resources.Types.CAREER)),
                           class_restrictions=('DetectiveCareer', ))}

    def __init__(self, *args, career_reference, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.career_reference = career_reference

    @property
    def loot_type(self):
        return LootType.NEW_CRIME

    def _apply_to_subject_and_target(self, subject, target, resolver):
        career = subject.careers.get(self.career_reference.guid64)
        if career is None:
            logger.error('Failed to find career {} on Sim {}.', (self.career_reference),
              subject, owner='bhill')
            return
        career.create_new_crime_data()


class BreakThroughLootOperation(BaseLootOperation):
    FACTORY_TUNABLES = {'breakthrough_commodity':TunableReference(description='\n            The commodity that tracks the breakthrough progress.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC)), 
     'time':TunableRealSecond(description='\n            The amount of time, in real seconds, to show headline effect.\n            ',
       default=5)}

    def __init__(self, *args, breakthrough_commodity, time, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.breakthrough_commodity = breakthrough_commodity
        self.time = time

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Subject {} is not a Sim for the loot {}.', self.subject, self)
            return
        progress = 0
        commodity = subject.get_statistic((self.breakthrough_commodity), add=False)
        if commodity is not None:
            progress = int(100 * commodity.get_normalized_value())
        op = BreakThroughMessage(sim_id=(subject.id), progress=progress, display_time=(self.time))
        distributor.system.Distributor.instance().add_op(subject, op)


class DestroyObjectsFromInventorySource(enum.Int):
    ALL_STORAGE = 0
    VISIBLE_STORAGE = 1
    HIDDEN_STORAGE = 2


class DestroyObjectsFromInventoryLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':"\n            Destroy every object in the target's inventory that passes the\n            tuned tests.\n            ", 
     'object_tests':TunableTestSet(description='\n            A list of tests to apply to all objects in the target inventory.\n            Every object that passes these tests will be destroyed.\n            '), 
     'object_source':TunableEnumEntry(description="\n            The target's inventory storage types to search for objects to\n            destroy.\n            ",
       tunable_type=DestroyObjectsFromInventorySource,
       default=DestroyObjectsFromInventorySource.ALL_STORAGE), 
     'count':TunableVariant(description='\n            The total number of objects to destroy. If multiple types of objects\n            match the criteria test, an arbitrary set of objects, no more than\n            the specified count, is destroyed.\n            ',
       number=TunableRange(tunable_type=int, default=1, minimum=0),
       locked_args={'all': math.MAX_INT32},
       default='all'), 
     'award_value':OptionalTunable(description="\n            If necessary, define how an amount corresponding to the objects'\n            value is given to Sims.\n            ",
       tunable=TunableTuple(recipient=TunableEnumEntry(description='\n                    Who to award funds to.\n                    ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Actor),
       invalid_enums=(
      ParticipantTypeSingleSim.Invalid,)),
       funds=TunableEnumEntry(description='\n                    Where to award funds to.  This can go to household\n                    funds by default, or to business funds.\n                    ',
       tunable_type=FundsSource,
       default=(FundsSource.HOUSEHOLD)),
       multiplier=TunableRange(description='\n                    Value multiplier for the award.\n                    ',
       tunable_type=float,
       default=1.0,
       minimum=0.0),
       tested_multipliers=TunableMultiplier.TunableFactory(description='\n                    Each multiplier that passes its test set will be applied to\n                    each award payment.\n                    ')))}

    def __init__(self, *args, object_tests, object_source, count, award_value, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.object_tests = object_tests
        self.object_source = object_source
        self.count = count
        self.award_value = award_value

    def _apply_to_subject_and_target(self, subject, target, resolver):
        inventory = self._get_subject_inventory(subject)
        if inventory is None:
            return
        objects_to_destroy = self._get_objects_and_award_values(inventory, resolver)
        award_value = 0
        pending_count = self.count
        for obj, value in objects_to_destroy.items():
            count = min(pending_count, obj.stack_count())
            if inventory.try_destroy_object(obj, count=count, source=self, cause='Destroying specified objects from inventory loot op.'):
                pending_count -= count
                if self.award_value:
                    award_value += count * value
                else:
                    logger.error('Error trying to destroy object {}.', obj)
                if pending_count <= 0:
                    break

        if award_value > 0:
            recipient = resolver.get_participant(self.award_value.recipient)
            if recipient is None:
                logger.error("Couldn't find appropriate recipient to award funds to.", owner='amwu')
                return
            recipient = recipient.get_sim_instance()
            funds = get_funds_for_source((self.award_value.funds), sim=recipient)
            if funds is None:
                logger.error("Couldn't find appropriate source to award funds to.", owner='amwu')
                return
            tags = set()
            if resolver.interaction is not None:
                tags |= resolver.interaction.get_category_tags()
            funds.add(award_value, (Consts_pb2.TELEMETRY_OBJECT_SELL), recipient, tags=tags)

    def get_simoleon_delta(self, interaction, target, context, **interaction_parameters):
        if self.award_value is None:
            return (
             0, FundsSource.HOUSEHOLD)
        resolver = (interaction.get_resolver)(target, context, **interaction_parameters)
        subject = resolver.get_participant(self.subject)
        inventory = self._get_subject_inventory(subject)
        if inventory is None:
            return (
             0, FundsSource.HOUSEHOLD)
        objects_values = self._get_objects_and_award_values(inventory, resolver)
        award_value = 0
        pending_count = self.count
        for obj, value in objects_values.items():
            count = min(pending_count, obj.stack_count())
            pending_count -= count
            award_value += count * value
            if pending_count <= 0:
                break

        return (
         award_value, self.award_value.funds)

    def _get_subject_inventory(self, subject):
        if subject.is_sim:
            subject = subject.get_sim_instance()
        inventory = getattr(subject, 'inventory_component', None)
        if inventory is None:
            logger.error('Subject {} does not have an inventory to check for objects to destroy.', subject)
            return
        return inventory

    def _get_object_source(self, inventory):
        if self.object_source == DestroyObjectsFromInventorySource.ALL_STORAGE:
            obj_source = inventory
        else:
            if self.object_source == DestroyObjectsFromInventorySource.VISIBLE_STORAGE:
                obj_source = inventory.visible_storage
            else:
                if self.object_source == DestroyObjectsFromInventorySource.HIDDEN_STORAGE:
                    obj_source = inventory.hidden_storage
                else:
                    logger.error('Unknown object source type {} to check for objects to destroy.', self.object_source)
                    obj_source = ()
        return obj_source

    def _get_objects_and_award_values(self, inventory, resolver):
        obj_source = self._get_object_source(inventory)
        objects_to_destroy = {}
        for obj in obj_source:
            single_object_resolver = SingleObjectResolver(obj)
            if not self.object_tests.run_tests(single_object_resolver):
                continue
            objects_to_destroy[obj] = self._get_object_value(obj, resolver) if self.award_value else 0

        return objects_to_destroy

    def _get_object_value(self, obj, resolver):
        multiplier = self.award_value.tested_multipliers.get_multiplier(resolver)
        return int(obj.current_value * self.award_value.multiplier * multiplier)


class DestroyObjectsSource(enum.Int):
    INVENTORY = 0
    IN_WORLD = 1


class DestroyTargetObjectsLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'award_value':OptionalTunable(description="\n            If necessary, define how an amount corresponding to the objects'\n            value is given to Sims.\n            ",
       tunable=TunableTuple(recipient=TunableEnumEntry(description='\n                    Who to award funds to.\n                    ',
       tunable_type=ParticipantTypeSingleSim,
       default=(ParticipantTypeSingleSim.Actor),
       invalid_enums=(
      ParticipantTypeSingleSim.Invalid,)),
       funds=TunableEnumEntry(description="\n                    Where to award funds to.  This can go to household\n                    funds by default, or to business funds.\n                    \n                    If the recipient does not resolve to an instanced Sim,\n                    these will award by default to the subject's household\n                    or the business for the zone.\n                    ",
       tunable_type=FundsSource,
       default=(FundsSource.HOUSEHOLD)),
       multiplier=TunableRange(description='\n                    Value multiplier for the award.\n                    ',
       tunable_type=float,
       default=1.0,
       minimum=0.0),
       tested_multipliers=TunableMultiplier.TunableFactory(description='\n                    Each multiplier that passes its test set will be applied to\n                    each award payment.\n                    '))), 
     'object_source':TunableEnumEntry(description='\n            Source that we are destroying objects from.\n            ',
       tunable_type=DestroyObjectsSource,
       default=DestroyObjectsSource.INVENTORY)}

    def __init__(self, *args, award_value, object_source, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.award_value = award_value
        self.object_source = object_source

    def _destroy_inventory_object(self, household, obj, value):
        total_value = 0
        if household is not None:
            if obj.content_source == ContentSource.HOUSEHOLD_INVENTORY_PROXY:
                original_household_funds = household.funds.money
                removed_from_household_inventory = build_buy.remove_object_from_household_inventory(obj.id, household)
                if removed_from_household_inventory:
                    total_value -= household.funds.money - original_household_funds
                    obj.destroy(source=self, cause='Destroying specified objects from household inventory for loot op.')
                    if self.award_value:
                        total_value += value
                else:
                    logger.error('Failed to destroy object {} ({})', obj, removed_from_household_inventory)
                return total_value
        else:
            inventory = self._get_object_inventory(obj)
            if inventory is not None and inventory.try_destroy_object(obj, source=self, cause='Destroying specified objects from inventory loot op.'):
                if self.award_value:
                    total_value += value
            else:
                logger.error('Error trying to destroy object {}.', obj)
        return total_value

    def _apply_to_subject_and_target(self, subject, target, resolver):
        household = self._get_subject_household(subject)
        objects_to_destroy = self._get_objects_and_award_values(subject, resolver)
        award_value = 0
        for obj, value in objects_to_destroy.items():
            if self.object_source == DestroyObjectsSource.INVENTORY:
                award_value += self._destroy_inventory_object(household, obj, value)
            elif self.object_source == DestroyObjectsSource.IN_WORLD:
                if obj.is_in_inventory():
                    logger.error('Trying to destroy an object {} that is not in world.', obj)
                    continue
                obj.schedule_destroy_asap(source=self, cause='Destroying specified objects from world for loot op.')
            if self.award_value:
                award_value += value

        if award_value != 0:
            tags = set()
            if resolver.interaction is not None:
                tags |= resolver.interaction.get_category_tags()
            funds = None
            recipient = None
            if self.award_value is not None:
                recipient = resolver.get_participant(self.award_value.recipient)
                if recipient is not None:
                    recipient = recipient.get_sim_instance()
                    funds = get_funds_for_source((self.award_value.funds), sim=recipient)
                else:
                    if self.award_value.funds == FundsSource.BUSINESS:
                        business_manager = services.business_service().get_business_manager_for_zone()
                        if business_manager is not None:
                            funds = business_manager.funds
            if funds is None:
                if household is not None:
                    funds = household.funds
                if funds is not None:
                    if award_value < 0:
                        funds.try_remove_amount((-award_value), (Consts_pb2.TELEMETRY_OBJECT_SELL), sim=recipient,
                          require_full_amount=False)
                    else:
                        funds.add(award_value, (Consts_pb2.TELEMETRY_OBJECT_SELL), sim=recipient, tags=tags)
            else:
                pass

    def get_simoleon_delta(self, interaction, target, context, **interaction_parameters):
        if self.award_value is None:
            return (
             0, FundsSource.HOUSEHOLD)
        resolver = (interaction.get_resolver)(target, context, **interaction_parameters)
        subject = resolver.get_participant(self.subject)
        objects_values = self._get_objects_and_award_values(subject, resolver)
        award_value = 0
        for value in objects_values.values():
            award_value += value

        return (award_value, self.award_value.funds)

    def _get_object_inventory(self, obj):
        if obj.is_sim:
            return
        inventoryitem_component = getattr(obj, 'inventoryitem_component', None)
        if inventoryitem_component is not None:
            if inventoryitem_component.inventory_owner is not None:
                return getattr(inventoryitem_component.inventory_owner, 'inventory_component', None)

    def _get_subject_household(self, subject):
        if subject.is_sim:
            return subject.household
        if subject.household_owner_id is not None:
            return services.household_manager().get(subject.household_owner_id)

    def _get_objects_and_award_values(self, subject, resolver):
        objects_to_destroy = {}
        objects_to_destroy[subject] = self._get_object_value(subject, resolver)
        return objects_to_destroy

    def _get_object_value(self, obj, resolver):
        if self.award_value:
            multiplier = self.award_value.tested_multipliers.get_multiplier(resolver)
            return int(obj.current_value * self.award_value.multiplier * multiplier)
        return 0


class RemoveNotebookEntry(BaseLootOperation):
    FACTORY_TUNABLES = {'subcategory_id':TunableEnumEntry(description='\n            Subcategory type.\n            ',
       tunable_type=NotebookSubCategories,
       default=NotebookSubCategories.INVALID,
       invalid_enums=(
      NotebookSubCategories.INVALID,)), 
     'removal_type':OptionalTunable(description='\n            Option to select if we want to remove by subcategory (like remove\n            all clues) or by a specific entry.\n            ',
       tunable=TunableList(description='\n                List of entries to be removed.\n                ',
       tunable=TunableReference(description="\n                    The entry that will be removed from the player's notebook.\n                    ",
       manager=(services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)),
       pack_safe=True)),
       disabled_name='all_entries',
       enabled_name='remove_by_reference')}

    def __init__(self, *args, subcategory_id, removal_type, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.subcategory_id = subcategory_id
        self.removal_type = removal_type

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Subject {} is not a Sim for the loot {}.', self.subject, self)
            return
        elif subject.notebook_tracker is None:
            logger.warn("Trying to remove a notebook entry from {}, but they don't have a notebook. LOD issue?", subject)
            return
            if self.removal_type is None:
                subject.notebook_tracker.remove_entries_by_subcategory(self.subcategory_id)
        else:
            for entry in self.removal_type:
                subject.notebook_tracker.remove_entry_by_reference(self.subcategory_id, entry)


class IncrementCommunityChallengeCount(BaseLootOperation):
    FACTORY_TUNABLES = {'count': Tunable(description='\n            The number to increment the community count by.\n            ',
                tunable_type=int,
                default=1)}

    def __init__(self, *args, count, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._count = count

    def _apply_to_subject_and_target(self, subject, target, resolver):
        msg = UI_pb2.IncrementCommunityCollectableCount()
        msg_type = DistributorOps_pb2.Operation.MSG_INCREMENT_COMMUNITY_COLLECTABLE_COUNT
        msg.count = self._count
        distributor = Distributor.instance()
        distributor.add_op_with_no_owner(GenericProtocolBufferOp(msg_type, msg))


def _validate_lock_target(loot, target):
    if not target.has_locking_component():
        logger.error('Target {} is not locked out by the loot {}.', target, loot, owner='mkartika')
        return False
    return True


class LockDoor(BaseTargetedLootOperation):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        if not value.replace_same_lock_type:
            if value.lock_data.factory is not LockAllWithSimIdExceptionData:
                logger.error('Lock Data {} is tuned to not replace same lock type. This is not supported.', (value.lock_data.factory), owner='nsavalani')

    FACTORY_TUNABLES = {'replace_same_lock_type':Tunable(description='\n            If True, it will replace the same type of lock data in the locking\n            component, otherwise it will update the existing data.\n            ',
       tunable_type=bool,
       default=True), 
     'clear_existing_locks':TunableEnumEntry(description='\n            Which locks should be cleared before adding the new lock data.\n            ',
       tunable_type=ClearLock,
       default=ClearLock.CLEAR_ALL), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, *args, lock_data, replace_same_lock_type, clear_existing_locks, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.lock_data = lock_data
        self.replace_same_lock_type = replace_same_lock_type
        self.clear_existing_locks = clear_existing_locks

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not _validate_lock_target(self, target):
            return
        lock_data = self.lock_data()
        lock_data.setup_data(subject, target, resolver)
        target.add_lock_data(lock_data, replace_same_lock_type=(self.replace_same_lock_type),
          clear_existing_locks=(self.clear_existing_locks))

    @TunableFactory.factory_option
    def lock_data_options(requires_sim_subject=True):
        variants = {'lock_all_with_genus_exception': LockAllWithGenusException.TunableFactory()}
        default_variant = 'lock_all_with_genus_exception'
        if requires_sim_subject:
            variants.update({'lock_all_with_simid_exception':LockAllWithSimIdExceptionData.TunableFactory(), 
             'lock_all_with_situation_job_exception':LockAllWithSituationJobExceptionData.TunableFactory(), 
             'lock_ranked_statistic':LockRankedStatisticData.TunableFactory(), 
             'lock_creature':LockCreatureData.TunableFactory()})
            default_variant = 'lock_all_with_simid_exception'
        return {'lock_data': TunableVariant(**variants, **{'default': default_variant})}

    @TunableFactory.factory_option
    def target_participant_type_options(description='The object to lock.', **kwargs):
        return (BaseLootOperation.get_participant_tunable)('target_participant_type', description=description, 
         default_participant=ParticipantType.Object, **kwargs)


class UnlockDoor(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'unlock_type': OptionalTunable(description='\n            The type of the lock we want to remove, by default should be everything.\n            ',
                      tunable=TunableEnumEntry(tunable_type=LockType,
                      default=(LockType.LOCK_ALL_WITH_SIMID_EXCEPTION)),
                      disabled_name='unlock_every_type')}

    def __init__(self, *args, unlock_type, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.unlock_type = unlock_type

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not _validate_lock_target(self, target):
            return
        target.remove_locks(lock_type=(self.unlock_type), lock_priority=(LockPriority.PLAYER_LOCK))

    @TunableFactory.factory_option
    def target_participant_type_options(description='The object to unlock.', **kwargs):
        return (BaseLootOperation.get_participant_tunable)('target_participant_type', description=description, 
         default_participant=ParticipantType.Object, **kwargs)


class UnlockHiddenAspirationTrack(BaseLootOperation):
    FACTORY_TUNABLES = {'aspiration_track': TunableReference(description='\n            The Hidden Aspiration Track to unlock so that is can be selected during gameplay.',
                           manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK)))}

    def __init__(self, *args, aspiration_track, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._aspiration_track = aspiration_track

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Subject {} is not a Sim for the loot {}.', self.subject, self)
            return
        aspiration_tracker = subject.sim_info.aspiration_tracker
        if aspiration_tracker is None:
            logger.error('Attempting to unlock a hidden aspiration for NPC {} in loot {}', self.subject, self)
            return
        aspiration_tracker.unlock_hidden_aspiration_track(self._aspiration_track)


class SetPrimaryAspirationTrack(BaseLootOperation):
    FACTORY_TUNABLES = {'aspiration_track': TunableReference(description='\n            The Aspiration Track to set as primary',
                           manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION_TRACK)))}

    def __init__(self, *args, aspiration_track, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._aspiration_track = aspiration_track

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Subject {} is not a Sim for the loot {}.', self.subject, self)
            return
        subject.sim_info.primary_aspiration = self._aspiration_track


class ResetAspiration(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'aspiration': TunableReference(description='\n            The aspiration that we want to reset.\n            ',
                     manager=(services.get_instance_manager(sims4.resources.Types.ASPIRATION)))}

    def __init__(self, *args, aspiration, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.aspiration = aspiration

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('Subject {} is not a Sim for the loot {}.', self.subject, self)
            return
        aspiration_tracker = subject.aspiration_tracker
        if aspiration_tracker is None:
            return
        aspiration_tracker.reset_milestone(self.aspiration)


class SummonNPC(BaseLootOperation):
    FACTORY_TUNABLES = {'summoning_purpose': TunableEnumEntry(description='\n                The purpose that is used to summon the NPC to the lot.  Defined\n                in venue tuning.\n                ',
                            tunable_type=(venues.venue_constants.NPCSummoningPurpose),
                            default=(venues.venue_constants.NPCSummoningPurpose.DEFAULT))}

    def __init__(self, *args, summoning_purpose, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.summoning_purpose = summoning_purpose

    @property
    def target_participant_type(self):
        return ParticipantType.TargetSim

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not target.is_sim:
            logger.error('target {} is not a Sim for the loot {}.', target, self, owner='cjiang')
            return False
        services.current_zone().venue_service.active_venue.summon_npcs((target,), self.summoning_purpose)


class TravelToTargetSim(BaseLootOperation):

    @property
    def target_participant_type(self):
        return ParticipantType.TargetSim

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            logger.error('subject {} is not a Sim for the loot {}.', subject, self, owner='cjiang')
            return False
        else:
            target.is_sim or logger.error('target {} is not a Sim for the loot {}.', target, self, owner='cjiang')
            return False
        if services.get_persistence_service().is_save_locked():
            return
        travel_info = TravelSimsToZone()
        travel_info.zone_id = target.household.home_zone_id
        travel_info.sim_ids.append(subject.id)
        distributor.system.Distributor.instance().add_event(Consts_pb2.MSG_TRAVEL_SIMS_TO_ZONE, travel_info)
        services.game_clock_service().set_clock_speed(ClockSpeedMode.PAUSED)


class SlotObjects(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'slot_strategy': SlotStrategyVariant(description='\n            The slot strategy we want to use to place objects from the transfer\n            source into slots on the target.\n            ')}

    def __init__(self, *args, slot_strategy, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.slot_strategy = slot_strategy

    def _apply_to_subject_and_target(self, subject, target, resolver):
        slot_strategy = self.slot_strategy(resolver)
        if not slot_strategy.slot_objects():
            logger.warn('Failed to slot [Subject: {}] to [Target: {}] using [SlotStrategy: {}]', subject, target, self.slot_strategy)


class PutNearLoot(BaseTargetedLootOperation):
    FACTORY_TUNABLES = {'target_tags_override':OptionalTunable(description="\n            If tuned we'll retrieve a random object matching these tags to use as\n            the target object instead of using the loot's target participant.\n            ",
       tunable=tag.TunableTags()), 
     'fallback_to_spawn_point':Tunable(description='\n            If enabled, a spawn point will be used as a fallback if FGL fails. \n            If disabled, the Subject will stay wherever they are.\n            ',
       tunable_type=bool,
       default=True), 
     'use_fgl':Tunable(description="\n            If enabled, use fgl to place the subject near the target. Otherwise,\n            try to place the object directly at the target's location. \n            ",
       tunable_type=bool,
       default=True)}

    def __init__(self, *args, target_tags_override, fallback_to_spawn_point, use_fgl, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.target_tags_override = target_tags_override
        self.fallback_to_spawn_point = fallback_to_spawn_point
        self.use_fgl = use_fgl

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if self.target_tags_override is not None:
            obj_manager = services.object_manager()
            potential_targets = list((obj_manager.get_objects_with_tags_gen)(*self.target_tags_override))
            if len(potential_targets) > 0:
                target = random.choice(potential_targets)
        elif target is not None:
            InteractionUtils.do_put_near(subject, target, self.fallback_to_spawn_point, self.use_fgl)
        else:
            logger.error('Missing target for PutNearLoot')


class ForceSpawnObjects(BaseTargetedLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if target.spawner_component is None:
            logger.error('Target {} does not have a spawner component.', target, owner='amwu')
            return
        for data in target.spawner_component.spawner_data:
            spawn_type = data.spawner_option.spawn_type
            if spawn_type == SpawnerType.SLOT:
                empty_slot_count = 0
                for slot in target.get_runtime_slots_gen():
                    gardening_component = target.get_component(types.GARDENING_COMPONENT)
                    spawn_prohibited = gardening_component is not None and gardening_component.is_prohibited_spawn_slot(slot.slot_name_hash, target)
                    if slot.empty:
                        spawn_prohibited or empty_slot_count += 1

                target.force_spawn_object(spawn_type=spawn_type, create_slot_obj_count=empty_slot_count)
            else:
                target.force_spawn_object(spawn_type=spawn_type)


class DoNothingLootOp(BaseLootOperation):

    def _apply_to_subject_and_target(self, subject, target, resolver):
        pass


class AddTraitListLootOp(BaseLootOperation):
    FACTORY_TUNABLES = {'description':'\n            This loot will add X amount of non conflicting random traits from a list.\n            ', 
     'trait_list':TunableList(description='\n            The list of traits that can be added.\n            ',
       tunable=TunableReference(description='\n                A trait that can be added by this loot.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True)), 
     'amount':TunableRange(description='\n            The amount of traits that will be added from the list.\n            ',
       tunable_type=int,
       default=1,
       minimum=1)}

    def __init__(self, *args, trait_list, amount, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.trait_list = trait_list
        self.amount = amount

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not self.trait_list:
            return
        trait_tracker = subject.trait_tracker
        new_trait_list = list(self.trait_list)
        random.shuffle(new_trait_list)
        amount_added = 0
        while amount_added < self.amount:
            if trait_tracker.can_add_trait(new_trait_list[-1]):
                subject.add_trait(new_trait_list[-1])
                amount_added += 1
            new_trait_list.pop()
            return new_trait_list or None