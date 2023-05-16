# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\drama_scheduler\stayover_drama_node.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 17716 bytes
import itertools
from drama_scheduler.drama_node import BaseDramaNode, DramaNodeRunOutcome
from drama_scheduler.drama_node_types import DramaNodeType
from event_testing.resolver import DoubleSimResolver
from event_testing.results import TestResult
from event_testing.tests import TunableTestSet
from interactions import ParticipantType, ParticipantTypeSingleSim
from relationships.relationship_bit import RelationshipBit
from sims.genealogy_tracker import genealogy_caching
from sims.household_enums import HouseholdChangeOrigin
from sims.sim_spawner import SimSpawner, SimCreator
from sims4.math import MAX_UINT32
from sims4.tuning.tunable import AutoFactoryInit, HasTunableSingletonFactory, TunableReference, TunableRange, TunableTuple, TunableEnumEntry, TunableVariant, TunableList, OptionalTunable
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
from travel_group.travel_group_stayover import TravelGroupStayover
from ui.ui_dialog import ButtonType, UiDialogOkCancel
import clock, random, services, sims4
logger = sims4.log.Logger('SituationDramaNode', default_owner='nabaker')

class _ParticipantInvitee(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            The participant(s) that will be staying over.\n            ',
                      tunable_type=ParticipantType,
                      default=(ParticipantType.TargetSim))}

    def get_invitees(self, resolver, guid):
        return resolver.get_participants(self.participant)

    def get_count(self, resolver):
        return len(resolver.get_participants(self.participant))

    def has_travel_group(self, resolver):
        for sim_info in resolver.get_participants(self.participant):
            if sim_info.household.get_travel_group() is not None:
                return True

        return False


class _RelativeInvitee(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'participant':TunableEnumEntry(description="\n            The participant that the created sim will be a 'relative' of.\n            ",
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'loot_list':TunableList(description="\n            A list of loot that will be applied between the newly createed 'relative' (Actor) and the specified \n            participant (target sim).\n            ",
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)), 
     'relationship_bit':OptionalTunable(description="\n            When enabled, this relationship bit will be added between the created sim and every sim 'blood' related to\n            the participant (including the participant), up to the specified depth.\n            ",
       tunable=TunableTuple(relationship_bit=RelationshipBit.TunableReference(description='\n                    The relationship bit to add between participant & kin and created sim.\n                    '),
       relationship_depth=TunableRange(description='\n                    Depth from participant for which we will gather kin.\n                    ',
       tunable_type=int,
       default=3,
       minimum=1)))}

    def get_invitees(self, resolver, guid):
        source_sim_info = resolver.get_participant(self.participant)
        if not source_sim_info:
            return
        household = services.household_manager().create_household(services.get_first_client().account)
        sim_creator = SimCreator(gender=(source_sim_info.gender), age=(source_sim_info.age),
          species=(source_sim_info.species),
          first_name=(SimSpawner.get_random_first_name(source_sim_info.gender, source_sim_info.species)),
          last_name=(SimSpawner.get_random_last_name(source_sim_info.gender, source_sim_info.species)))
        sim_info_list, _ = SimSpawner.create_sim_infos((sim_creator,), household=household,
          zone_id=0,
          account=(source_sim_info.account),
          generate_deterministic_sim=True,
          creation_source='stayover relative',
          household_change_origin=(HouseholdChangeOrigin.STAYOVER_RELATIVE))
        sim_info = sim_info_list[0]
        sim_info.apply_genetics(source_sim_info, source_sim_info, seed=(random.randint(1, MAX_UINT32)))
        sim_info.save_sim()
        household.save_data()
        sim_info.resend_physical_attributes()
        sim_info.relationship_tracker.clean_and_send_remaining_relationship_info()
        if self.relationship_bit is not None:
            relationship_tracker = sim_info.relationship_tracker
            ancestor = source_sim_info
            sim_info_manager = services.sim_info_manager()
            up_tree_distance = 0
            with genealogy_caching():
                for _ in range(self.relationship_bit.relationship_depth):
                    ancestor_candidates = tuple(ancestor.genealogy.get_parent_sim_infos_gen())
                    if not ancestor_candidates:
                        break
                    up_tree_distance += 1
                    ancestor = random.choice(ancestor_candidates)

                blood_kin = set([ancestor])
                candidates = set([ancestor])
                for _ in range(self.relationship_bit.relationship_depth + up_tree_distance):
                    new_candidates = set()
                    for _id in itertools.chain.from_iterable((x.genealogy.get_children_sim_ids_gen() for x in candidates)):
                        family_member = sim_info_manager.get(_id)
                        if family_member is not None and family_member not in blood_kin:
                            new_candidates.add(family_member)

                    candidates = new_candidates
                    blood_kin.update(candidates)

                for target_sim_info in blood_kin:
                    relationship_tracker.create_relationship(target_sim_info.sim_id)
                    relationship_tracker.add_relationship_score(target_sim_info.sim_id, 1)
                    relationship_tracker.add_relationship_bit((target_sim_info.sim_id), (self.relationship_bit.relationship_bit), force_add=True)

        resolver = DoubleSimResolver(source_sim_info, sim_info)
        for loot_action in self.loot_list:
            loot_action.apply_to_resolver(resolver)

        return (sim_info,)

    def get_count(self, resolver):
        return 1

    def has_travel_group(self, resolver):
        return False


class StayoverDramaNode(BaseDramaNode):
    INSTANCE_TUNABLES = {'stayover_behavioral_situation':TunableReference(description='\n            The behavioral situation that will run for the guest sims in the stay over.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION),
       class_restrictions='AmbientSimSpecificCustomStatesSituation',
       tuning_group=GroupNames.SITUATION), 
     'duration':TunableRange(description='\n            Duration of the stayover in days.\n            ',
       tunable_type=int,
       default=1,
       minimum=1,
       tuning_group=GroupNames.TIME), 
     'invitees':TunableVariant(description='\n            Sims that should be part of the stayover.\n            ',
       participant=_ParticipantInvitee.TunableFactory(),
       relative=_RelativeInvitee.TunableFactory(),
       default='participant',
       tuning_group=GroupNames.PARTICIPANT), 
     'stayover_prompt_messages':TunableList(description='\n            A List of tests and UiDialogs that should be considered for showing\n            as an npc stayover request. \n            \n            If more than one dialog passes all of its tests,\n            then one dialog will be chosen at random.\n            \n            If no dialogs pass, the node will fail.\n            \n            Receiver sim is Actor.  Sender sim is TargetSim.\n            ',
       tunable=TunableTuple(description='\n                A combination of UiDialog and tests where if the tuned tests pass\n                then the dialog will be considered as a choice to be displayed. \n                After all choices have been tested one of the dialogs will be\n                chosen at random.\n                ',
       dialog=UiDialogOkCancel.TunableFactory(description='\n                    The message that will be displayed when this stayover\n                    tries to start for the initiating sim.\n                    '),
       tests=(TunableTestSet()),
       dialog_complete_loot_list=TunableList(description='\n                    A list of loots that will always be applied, either when the player responds to the dialog or, if the \n                    dialog is a phone ring or text message, when the dialog times out due to the player ignoring it.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)),
       dialog_canceled_loot_list=TunableList(description='\n                    A list of loots that will only be applied when the player responds canceling the dialog.  If the dialog is a\n                    phone ring or text message then this loot will NOT be triggered when the dialog times out due to the\n                    player ignoring it.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True)),
       dialog_seen_loot_list=TunableList(description='\n                    A list of loots that will only be applied when the player responds to the dialog.  If the dialog is a\n                    phone ring or text message then this loot will NOT be triggered when the dialog times out due to the\n                    player ignoring it.\n                    ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
       class_restrictions=('LootActions', 'RandomWeightedLoot'),
       pack_safe=True))))}

    @classproperty
    def drama_node_type(cls):
        return DramaNodeType.STAYOVER

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._chosen_dialog_data = None

    def _test(self, resolver, skip_run_tests=False):
        if self._receiver_sim_info is None:
            return TestResult(False, 'No receiver sim.')
        else:
            household = self._receiver_sim_info.household
            return household or TestResult(False, 'No Household.')
        if household.get_travel_group() is not None:
            return TestResult(False, 'Household already in Travel Group.')
        if self.invitees.has_travel_group(resolver):
            return TestResult(False, 'Invitees already in Travel Group.')
        total_count = len(household) + self.invitees.get_count(resolver)
        roommate_service = services.get_roommate_service()
        if roommate_service is not None:
            total_count += roommate_service.get_roommate_count(household.home_zone_id)
        if total_count > TravelGroupStayover.HOUSEHOLD_AND_GUEST_MAXIMUM:
            return TestResult(False, 'Too many sims.')
        return super()._test(resolver, skip_run_tests=skip_run_tests)

    def _run(self):
        self._choose_dialog()
        if self._chosen_dialog_data is None or self._chosen_dialog_data.dialog is None:
            return DramaNodeRunOutcome.FAILURE
        sim_info = self._receiver_sim_info
        resolver = DoubleSimResolver(self._sender_sim_info, self._receiver_sim_info)
        confirm_dialog = self._chosen_dialog_data.dialog(sim_info, target_sim_id=(self._sender_sim_info.sim_id), resolver=resolver)
        confirm_dialog.show_dialog(on_response=(self._on_confirm_dialog_response))
        return DramaNodeRunOutcome.SUCCESS_NODE_INCOMPLETE

    def _on_confirm_dialog_response(self, dialog):
        resolver = self._get_resolver()
        for loot_action in self._chosen_dialog_data.dialog_complete_loot_list:
            loot_action.apply_to_resolver(resolver)

        if dialog.response is not None:
            if dialog.response == ButtonType.DIALOG_RESPONSE_CANCEL:
                for loot_action in self._chosen_dialog_data.dialog_canceled_loot_list:
                    loot_action.apply_to_resolver(resolver)

        if dialog.response is not None:
            if dialog.response != ButtonType.DIALOG_RESPONSE_NO_RESPONSE:
                for loot_action in self._chosen_dialog_data.dialog_seen_loot_list:
                    loot_action.apply_to_resolver(resolver)

        if not dialog.accepted:
            services.drama_scheduler_service().complete_node(self.uid)
            return
        invited_sim_infos = self.invitees.get_invitees(resolver, self.guid64)
        if invited_sim_infos:
            create_timestamp = services.time_service().sim_now
            end_timestamp = create_timestamp + clock.interval_in_sim_days(self.duration)
            zone_id = self._receiver_sim_info.household.home_zone_id
            travel_group_manager = services.travel_group_manager()
            travel_group_manager.create_travel_group_and_rent_zone(sim_infos=invited_sim_infos, zone_id=zone_id, played=False, create_timestamp=create_timestamp,
              end_timestamp=end_timestamp,
              cost=0,
              stayover_situation=(self.stayover_behavioral_situation))
        services.drama_scheduler_service().complete_node(self.uid)

    def _choose_dialog(self):
        choices = []
        resolver = DoubleSimResolver(self._receiver_sim_info, self._sender_sim_info)
        for dialog_data in self.stayover_prompt_messages:
            if dialog_data.tests.run_tests(resolver):
                choices.append(dialog_data)

        if choices:
            self._chosen_dialog_data = random.choice(choices)