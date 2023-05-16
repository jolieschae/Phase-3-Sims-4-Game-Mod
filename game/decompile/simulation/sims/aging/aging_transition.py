# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\aging\aging_transition.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 16186 bytes
from event_testing.resolver import DoubleSimResolver, SingleSimResolver
from interactions.utils.loot import LootActions
from relationships.relationship_bit import RelationshipBit
from sims.sim_dialogs import SimPersonalityAssignmentDialog
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableTuple, TunableReference, TunableList, TunableSet, OptionalTunable, TunableVariant, TunablePercent, TunableMapping, TunableRange
from sims4.tuning.tunable_base import GroupNames
from sims4 import random
from sims.aging.aging_enums import AgeSpeeds
from snippets import define_snippet
from ui.ui_dialog import PhoneRingType
from ui.ui_dialog_notification import UiDialogNotification
import services, random, sims4.resources

class AgingTransition(HasTunableSingletonFactory, AutoFactoryInit):

    class _AgeTransitionShowDialog(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'dialog':SimPersonalityAssignmentDialog.TunableFactory(locked_args={'phone_ring_type': PhoneRingType.NO_RING}), 
         'post_age_up_dialog_loots':TunableList(description='\n                Loots to run after the age up dialog has been closed on the Sim aging up.\n                ',
           tunable=TunableReference(description='\n                    A list of loots to apply to the Sim that is aging up after the age up dialog.\n                    ',
           manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
           pack_safe=True))}

        def __call__(self, sim_info, **kwargs):
            resolver = SingleSimResolver(sim_info)

            def on_response(dlg):
                if dlg.accepted:
                    sim_info.resend_trait_ids()
                    if self.post_age_up_dialog_loots:
                        for loot in self.post_age_up_dialog_loots:
                            loot.apply_to_resolver(resolver)

            dialog = self.dialog(sim_info, assignment_sim_info=sim_info, resolver=resolver)
            (dialog.show_dialog)(on_response=on_response, **kwargs)

    class _AgeTransitionShowNotification(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'dialog': UiDialogNotification.TunableFactory()}

        def __call__(self, sim_info, **__):
            dialog = self.dialog(sim_info, resolver=(SingleSimResolver(sim_info)))
            dialog.show_dialog()

    FACTORY_TUNABLES = {'age_up_warning_notification':OptionalTunable(tunable=UiDialogNotification.TunableFactory(description='\n                Notification to show up when Age Up is impending.\n                ',
       tuning_group=(GroupNames.UI))), 
     'age_up_available_notification':OptionalTunable(tunable=UiDialogNotification.TunableFactory(description='\n                Notification to show when Age Up is ready.\n                ',
       tuning_group=(GroupNames.UI))), 
     '_legacy_age_duration':Tunable(description='\n            The legacy time, in Sim days, required for a Sim to be eligible to\n            transition from this age to the next one. Use maximum of legacy age\n            duration for this value.\n            ',
       tunable_type=float,
       default=1), 
     '_age_durations':TunableTuple(description='\n            The time, in Sim days, required for a Sim to be eligible to\n            transition from this age to the next one. \n            ',
       age_fast=Tunable(tunable_type=float,
       default=1),
       age_normal=Tunable(tunable_type=float,
       default=2),
       age_slow=Tunable(tunable_type=float,
       default=3)), 
     'trait_age_duration_mutliplier':TunableMapping(description='\n            A mapping of trait to age duration multiplier that increases (or technically decreases\n            if the value is less than 1.0) the age duration for this transition.\n            ',
       key_name='trait',
       key_type=TunableReference(description='\n                The trait a Sim must have in order to get the mutlipler for the age duration of this\n                aging transition.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True),
       value_name='age_duration_multiplier',
       value_type=TunableRange(description='\n                The multiplier to apply if the associated trait is equipped on the Sim. Any value\n                above 1.0 will increase and values below 1.0 will decrease the age duration.\n                ',
       tunable_type=float,
       minimum=0,
       default=1.0)), 
     '_use_initial_age_randomization':Tunable(description="\n            If checked, instead of randomizing the duration of each individual age,\n            the sims's initial age progress will be randomly offset on first load. \n            ",
       tunable_type=bool,
       default=True), 
     '_initial_age_randomization_limit':TunablePercent(description='\n            Sets the upper limit, as a percentage value, of how much of an age stage can\n            be randomized within. If set to 50%, anywhere from 0% to 50% of the age stage\n            can be set as completed upon first load.\n            ',
       default=50), 
     'age_transition_warning':Tunable(description='\n            Number of Sim days prior to the transition a Sim will get a warning\n            of impending new age.\n            ',
       tunable_type=float,
       default=1), 
     'age_transition_delay':Tunable(description='\n            Number of Sim days after transition time elapsed before auto- aging\n            occurs.\n            ',
       tunable_type=float,
       default=1), 
     'age_transition_dialog':TunableVariant(description='\n            The dialog or notification that is displayed when the Sim ages up.\n            ',
       show_dialog=_AgeTransitionShowDialog.TunableFactory(),
       show_notification=_AgeTransitionShowNotification.TunableFactory(),
       locked_args={'no_dialog': None},
       default='no_dialog',
       tuning_group=GroupNames.UI), 
     'age_trait':TunableReference(description="\n            The age trait that corresponds to this Sim's age\n            ",
       manager=services.get_instance_manager(sims4.resources.Types.TRAIT)), 
     'age_up_reward_traits':TunableList(description="\n            A list of reward traits that can be given to a sim when they age up\n            via this transition. This is used to detect the trait on the sim\n            so it can be shown in this dialog.\n            \n            It is possible the sim doesn't have any of these traits, in that case\n            nothing is shown.\n            ",
       tunable=TunableReference(description='\n                A reward trait that can be given to a sim when they age up.\n                ',
       manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True)), 
     'age_up_reward_trait_text':TunableLocalizedStringFactory(description='\n            Text to show for reward trait, if applicable.\n            ',
       allow_none=True), 
     'relbit_based_loot':TunableList(description='\n            List of loots given based on bits set in existing relationships.\n            Applied after per household member loot.\n            ',
       tunable=TunableTuple(description='\n                Loot given to sim aging up (actor) and each sim (target) with a\n                "chained" relationship via recursing through the list of relbit\n                sets.\n                ',
       relationship=TunableList(description='\n                    List specifying a series of relationship(s) to recursively \n                    traverse to find the desired target sim.  i.e. to find \n                    "cousins", we get all the "parents".  And then we \n                    get "aunts/uncles" by getting the "siblings" of those \n                    "parents".  And then we finally get the "cousins" by \n                    getting the "children" of those "aunts/uncles".\n                    \n                    So:\n                     Set of "parent" bitflag(s)\n                     Set of "sibling" bitflag(s)\n                     Set of "children" bitflag(s)\n                    \n                    Can also find direct existing relationships by only having a\n                    single entry in the list.\n                    ',
       tunable=TunableSet(description='\n                        Set of relbits to use for this relationship.\n                        ',
       tunable=RelationshipBit.TunableReference(description='\n                            The relationship bit between greeted Sims.\n                            ',
       pack_safe=True))),
       loot=TunableList(description='\n                    Loot given between sim aging up and sims with the previously\n                    specified chain of relbits. (may create a relationship).\n                    ',
       tunable=LootActions.TunableReference(description='\n                        A loot action given to sim aging up.\n                        ',
       pack_safe=True))),
       tuning_group=GroupNames.TRIGGERS), 
     'per_household_member_loot':TunableList(description="\n            Loots given between sim aging up (actor) and each sim in that sims\n            household (target).  Applied before relbit based loot'\n            ",
       tunable=LootActions.TunableReference(description='\n                A loot action given between sim aging up (actor) and each sim in\n                that sims household (target).\n                ',
       pack_safe=True),
       tuning_group=GroupNames.TRIGGERS), 
     'single_sim_loot':TunableList(description='\n            Loots given to sim aging up (actor). Last loot applied.\n            ',
       tunable=LootActions.TunableReference(description='\n                A loot action given to sim aging up.\n                ',
       pack_safe=True),
       tuning_group=GroupNames.TRIGGERS)}

    def get_age_duration(self, sim_info):
        return self._age_durations[sim_info._age_speed_setting] * self._get_age_duration_multiplier(sim_info)

    def get_normal_age_duration(self, sim_info):
        return self._age_durations[AgeSpeeds.NORMAL] * self._get_age_duration_multiplier(sim_info)

    def _get_age_duration_multiplier(self, sim_info):
        total_multiplier = 1.0
        for trait, multiplier in self.trait_age_duration_mutliplier.items():
            if sim_info.has_trait(trait):
                total_multiplier *= multiplier

        return total_multiplier

    def get_randomized_initial_progress(self, sim_info, age_progress):
        if self._use_initial_age_randomization:
            max_randomizable_age_duration = self.get_age_duration(sim_info) * self._initial_age_randomization_limit
            seed = (
             self.age_trait.guid64, sim_info.sim_id)
            rand = random.Random(seed)
            age_progress = rand.uniform(0, max_randomizable_age_duration)
        return age_progress

    def _apply_aging_transition_relbit_loot(self, source_info, cur_info, relbit_based_loot, level):
        if level == len(relbit_based_loot.relationship):
            resolver = DoubleSimResolver(source_info, cur_info)
            for loot in relbit_based_loot.loot:
                loot.apply_to_resolver(resolver)

            return
        relationship_tracker = cur_info.relationship_tracker
        for target_sim_id in relationship_tracker.target_sim_gen():
            if set(relationship_tracker.get_all_bits(target_sim_id)) & relbit_based_loot.relationship[level]:
                new_sim_info = services.sim_info_manager().get(target_sim_id)
                self._apply_aging_transition_relbit_loot(source_info, new_sim_info, relbit_based_loot, level + 1)

    def apply_aging_transition_loot(self, sim_info):
        if self.per_household_member_loot:
            for member_info in sim_info.household.sim_info_gen():
                if member_info is sim_info:
                    continue
                resolver = DoubleSimResolver(sim_info, member_info)
                for household_loot in self.per_household_member_loot:
                    household_loot.apply_to_resolver(resolver)

        for relbit_based_loot in self.relbit_based_loot:
            self._apply_aging_transition_relbit_loot(sim_info, sim_info, relbit_based_loot, 0)

        resolver = SingleSimResolver(sim_info)
        for loot in self.single_sim_loot:
            loot.apply_to_resolver(resolver)

    def show_age_transition_dialog(self, sim_info, **kwargs):
        if self.age_transition_dialog is not None:
            (self.age_transition_dialog)(sim_info, age_up_reward_traits=self.age_up_reward_traits, age_up_reward_trait_text=self.age_up_reward_trait_text, **kwargs)


TunableAgingTransitionReference, _ = define_snippet('Aging_Transition', AgingTransition.TunableFactory())