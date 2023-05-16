# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\notebook\notebook_entry_ops.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 11742 bytes
from fishing import fishing_data
from interactions import ParticipantTypeObject
from interactions.utils.loot_basic_op import BaseLootOperation
from notebook.notebook_entry import SubEntryData
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableEnumEntry, TunablePackSafeReference, TunableVariant, OptionalTunable, TunableList, TunableTuple
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
import services, sims4.log
logger = sims4.log.Logger('Notebook')

class NotebookEntryLootOp(BaseLootOperation):

    class _NotebookEntryFromParticipant(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry':TunableReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory) but we will use the the object \n                reference to populate the rest of the data. \n                ',
           manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY),
           pack_safe=True), 
         'entry_participant':TunableEnumEntry(description='\n                Participant on which we will get the noteboook entry information \n                from.\n                ',
           tunable_type=ParticipantTypeObject,
           default=ParticipantTypeObject.Object), 
         'entry_sublist_participant':TunableList(description='\n                List of participants on which we will get the notebook entry \n                sublist information from.\n                ',
           tunable=TunableEnumEntry(tunable_type=ParticipantTypeObject,
           default=(ParticipantTypeObject.PickedObject)),
           unique_entries=True)}

        def get_entries(self, resolver):
            entry_target = resolver.get_participant(self.entry_participant)
            if entry_target is None:
                logger.error('Notebook entry {} for entry participant {} is None, participant type is probably invalid for this loot.', self, self.entry_participant)
                return
            sub_entries = None
            for sub_entry_participant in self.entry_sublist_participant:
                sub_entry = resolver.get_participant(sub_entry_participant)
                if sub_entry is None:
                    continue
                if sub_entries is None:
                    sub_entries = []
                sub_entries.append(sub_entry)

            return entry_target.get_notebook_information(self.reference_notebook_entry, sub_entries)

    class _NotebookEntryFromParticipantDefinition(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry':TunableReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory) but we will use the the object \n                reference to populate the rest of the data. \n                ',
           manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY),
           pack_safe=True), 
         'entry_participant':TunableEnumEntry(description='\n                Participant on which we will get the noteboook entry information \n                from.\n                ',
           tunable_type=ParticipantTypeObject,
           default=ParticipantTypeObject.Object)}

        def get_entries(self, resolver):
            entry_target = resolver.get_participant(self.entry_participant)
            if entry_target is None:
                logger.error('Notebook entry {} for entry participant {} is None, participant type is probably invalid for this loot.', self, self.entry_participant)
                return
            return (
             self.reference_notebook_entry(entry_object_definition_id=(entry_target.definition.id)),)

    class _NotebookEntryFromReference(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'notebook_entry': TunableReference(description='\n                Create a new entry filling up all the fields for an entry.\n                ',
                             manager=(services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)),
                             pack_safe=True)}

        def get_entries(self, resolver):
            return (
             self.notebook_entry(),)

    class _NotebookEntryFromRecipe(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry':TunablePackSafeReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory).   \n                ',
           manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)), 
         'recipe':TunablePackSafeReference(description='\n                The recipe to use to create the notebook entry.  This recipe\n                should have the use_ingredients tunable set so the notebook\n                system has data to populate the entry.\n                ',
           manager=services.get_instance_manager(sims4.resources.Types.RECIPE))}

        def get_entries(self, resolver):
            if self.recipe is None or self.reference_notebook_entry is None:
                return
            sub_entries = (
             SubEntryData(self.recipe.guid64, False),)
            return (self.reference_notebook_entry(None, sub_entries=sub_entries),)

    class _NotebookEntryFromFishingData(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'reference_notebook_entry':TunablePackSafeReference(description='\n                Reference to a notebook entry where we will get the core notebook\n                data (category, subcategory).   \n                ',
           manager=services.get_instance_manager(sims4.resources.Types.NOTEBOOK_ENTRY)), 
         'fishing_data':fishing_data.TunableFishingDataSnippet(description='\n                Fishing data reference.\n                ')}

        def get_entries(self, resolver):
            if self.fishing_data is None or self.reference_notebook_entry is None:
                return
            interaction = resolver.interaction
            if interaction is None:
                logger.error('{} tried to create notebook entry using fishing data outside the scope of an interaction', resolver,
                  owner='jdimailig')
                return
            fish = self.fishing_data.choose_fish(resolver, require_bait=False)
            if fish is None:
                logger.error('{} tried to create notebook entry using fishing data {}, but there was no possible fish.', resolver,
                  (self.fishing_data), owner='tythompson')
                return
            if interaction.get_saved_participant(0) is not None:
                logger.error('{} already has a saved participant {} which will be overwritten', interaction,
                  (interaction.get_saved_participant(0)), owner='jdimailig')
            interaction.set_saved_participant(0, fish)
            return (
             self.reference_notebook_entry(entry_object_definition_id=(fish.id)),)

    FACTORY_TUNABLES = {'notebook_entry':TunableVariant(description='\n            Type of unlock for notebook entries.\n            ',
       create_new_entry=_NotebookEntryFromReference.TunableFactory(),
       create_entry_from_participant=_NotebookEntryFromParticipant.TunableFactory(),
       create_entry_from_participant_definition=_NotebookEntryFromParticipantDefinition.TunableFactory(),
       create_entry_from_recipe=_NotebookEntryFromRecipe.TunableFactory(),
       create_entry_from_fishing_data=_NotebookEntryFromFishingData.TunableFactory()), 
     'notifications':TunableTuple(description='\n            Notifications to show when adding notebook entry.\n            ',
       unlocked_success_notification=OptionalTunable(description='\n                If enabled, a notification will be shown when a new\n                notebook entry is successfully unlocked.\n                ',
       tunable=(TunableUiDialogNotificationSnippet())),
       unlocked_failed_notification=OptionalTunable(description='\n                If enabled, a notification will be shown when failing to \n                unlock a new notebook entry because the notebook already has \n                identical entry.\n                ',
       tunable=(TunableUiDialogNotificationSnippet())))}

    def __init__(self, *args, notebook_entry, notifications, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.notebook_entry = notebook_entry
        self.notifications = notifications

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not subject.is_sim:
            return False
        else:
            if subject.notebook_tracker is None:
                logger.warn('Trying to unlock a notebook entry on {}, but the notebook tracker is None. LOD issue?', subject)
                return False
            unlocked_entries = self.notebook_entry.get_entries(resolver)
            return unlocked_entries or False
        for unlocked_entry in unlocked_entries:
            subject.notebook_tracker.unlock_entry(unlocked_entry, notifications=(self.notifications), resolver=resolver)