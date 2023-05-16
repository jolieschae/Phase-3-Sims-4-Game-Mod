# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\travel_group\travel_group_elements.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9632 bytes
from interactions import ParticipantTypeActorTargetSim, ParticipantType, ParticipantTypeSingleSim
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims4.tuning.tunable import Tunable, TunableEnumEntry
from travel_group.travel_group_telemetry import write_travel_group_telemetry, TELEMETRY_HOOK_TRAVEL_GROUP_ADD, TELEMETRY_HOOK_TRAVEL_GROUP_REMOVE
import services, sims4.log
logger = sims4.log.Logger('Travel_Group_Elements', default_owner='rmccord')

class TravelGroupAdd(XevtTriggeredElement):
    FACTORY_TUNABLES = {'travel_group_participant':TunableEnumEntry(description='\n            A participant that belongs to the travel group we care about.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Actor), 
     'target_to_add':TunableEnumEntry(description='\n            The participant we want to add to the travel group.\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.TargetSim), 
     'include_household_travel_group':Tunable(description="\n            If checked, the travel group that any sims in the travel group \n            participant's household will be used in the event that the \n            travel group participant is not actually on vacation.  \n            (e.g. Sim adding himself to his households travel group)\n            ",
       tunable_type=bool,
       default=False), 
     'include_hosted_travel_group':Tunable(description='\n            If checked, include the travel group that is hosted on the participant households home lot.\n            ',
       tunable_type=bool,
       default=False)}

    def _do_behavior(self, *args, **kwargs):
        actors = self.interaction.get_participants(self.travel_group_participant)
        targets = self.interaction.get_participants(self.target_to_add)
        if not (actors and targets):
            logger.error('TravelGroupAdd could not acquire participants.')
            return

        def get_first_travel_group(participants, is_target):
            travel_group = None
            for participant in participants:
                travel_group = participant.travel_group
                if travel_group is None:
                    if not is_target:
                        if self.include_household_travel_group:
                            travel_group = participant.household.get_travel_group()
                        if travel_group is None:
                            if self.include_hosted_travel_group:
                                travel_group = services.travel_group_manager().get_travel_group_by_zone_id(participant.household.home_zone_id)
                if travel_group is not None:
                    break

            return travel_group

        travel_group = get_first_travel_group(actors, False)
        if travel_group is None:
            logger.error('Participant {} does not belong to a travel group.', actors)
            return
        target_travel_group = get_first_travel_group(targets, True)
        if target_travel_group is not None:
            logger.error('Target {} already belongs to a travel group.', targets)
            return
        for target in targets:
            target_sim_info = services.sim_info_manager().get(target.sim_id)
            if not travel_group.can_add_to_travel_group(target_sim_info):
                logger.error('Cannot add Target {} to Travel Group {}.', target, travel_group)
                return
                travel_group.add_sim_info(target_sim_info)

        write_travel_group_telemetry(travel_group, TELEMETRY_HOOK_TRAVEL_GROUP_ADD, sim_info=target_sim_info)


class TravelGroupRemove(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant_to_remove': TunableEnumEntry(description='\n            The participant we want to remove from their travel group.\n            ',
                                tunable_type=ParticipantType,
                                default=(ParticipantType.Actor))}

    def _do_behavior(self, *args, **kwargs):
        resolver = self.interaction.get_resolver()
        participant = resolver.get_participant(self.participant_to_remove)
        if participant is not None:
            travel_group = participant.travel_group
            if travel_group is not None:
                if any((sim_info.can_live_alone for sim_info in travel_group if sim_info is not participant)):
                    travel_group.remove_sim_info(participant)
                else:
                    travel_group.end_vacation()
                write_travel_group_telemetry(travel_group, TELEMETRY_HOOK_TRAVEL_GROUP_REMOVE, sim_info=participant)


class TravelGroupExtend(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            A participant that belongs to the travel group we care about.\n            ',
                      tunable_type=ParticipantTypeActorTargetSim,
                      default=(ParticipantTypeActorTargetSim.Actor))}

    def _do_behavior(self, *args, **kwargs):
        participant = self.interaction.get_participant(self.participant)
        if participant is not None:
            travel_group = participant.travel_group
            if travel_group is None:
                logger.error('Participant {} does not belong to a travel group.', participant)
                return
            travel_group.show_extend_vacation_dialog()


class TravelGroupEnd(XevtTriggeredElement):
    FACTORY_TUNABLES = {'participant': TunableEnumEntry(description='\n            A participant that belongs to the travel group we care about.\n            ',
                      tunable_type=ParticipantTypeActorTargetSim,
                      default=(ParticipantTypeActorTargetSim.Actor))}

    def _do_behavior(self, *args, **kwargs):
        participant = self.interaction.get_participant(self.participant)
        if participant is not None:
            travel_group = participant.travel_group
            if travel_group is None:
                logger.error('Participant {} does not belong to a travel group.', participant)
                return
            travel_group.end_vacation()


class TravelGroupClaimObject(XevtTriggeredElement):
    FACTORY_TUNABLES = {'travel_group_participant':TunableEnumEntry(description='\n            A participant that belongs to the travel group we care about.\n            ',
       tunable_type=ParticipantTypeSingleSim,
       default=ParticipantTypeSingleSim.Actor), 
     'object_participant':TunableEnumEntry(description='\n            The participant object we want the travel group to lay claim to.\n            Any such object will be deleted on load if the travel group fails to reclaim it.\n            (e.g. if the group no longer exists).\n            ',
       tunable_type=ParticipantType,
       default=ParticipantType.Object), 
     'make_transient_on_failure':Tunable(description='\n            If checked, object participant will be made transient on failure to claim.  \n            (i.e. destroyed when no longer being used.)\n            ',
       tunable_type=bool,
       default=True)}

    def _on_claim_failure(self, objects):
        if not self.make_transient_on_failure:
            return
        for obj in objects:
            obj.make_transient()

    def _do_behavior(self, *args, **kwargs):
        objects_to_claim = self.interaction.get_participants(self.object_participant)
        if not objects_to_claim:
            return
        travel_group_member = self.interaction.get_participant(self.travel_group_participant)
        if not travel_group_member:
            logger.error('TravelGroupClaimObject could not acquire travel group participant.')
            self._on_claim_failure(objects_to_claim)
            return
        travel_group = travel_group_member.travel_group
        if travel_group is None:
            logger.error('Participant {} has no travel group in TravelGroupClaimObject', travel_group_member)
            self._on_claim_failure(objects_to_claim)
            return
        travel_group.claim_objects([obj.id for obj in objects_to_claim])