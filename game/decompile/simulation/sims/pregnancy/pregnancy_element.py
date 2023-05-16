# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\pregnancy\pregnancy_element.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 6134 bytes
import random
from filters.tunable import TunableSimFilter
from interactions import ParticipantTypeSingle
from interactions.utils.death import get_death_interaction
from interactions.utils.interaction_elements import XevtTriggeredElement
from sims.pregnancy.pregnancy_enums import PregnancyOrigin
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableVariant, Tunable
import services

class PregnancyElement(XevtTriggeredElement):

    class _PregnancyParentParticipant(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'subject':TunableEnumEntry(description='\n                The participant of the interaction that is to be the\n                impregnator.\n                ',
           tunable_type=ParticipantTypeSingle,
           default=ParticipantTypeSingle.TargetSim), 
         'single_sim_is_allowed':Tunable(description='\n                The participant can be the same Sim as the Sim becoming\n                pregnant. This allows single Sim pregnancy.\n                ',
           tunable_type=bool,
           default=False)}

        def get_parent(self, interaction, pregnancy_subject_sim_info):
            parent = interaction.get_participant(self.subject)
            return (parent.sim_info, self.single_sim_is_allowed)

    class _PregnancyParentFilter(HasTunableSingletonFactory, AutoFactoryInit):
        FACTORY_TUNABLES = {'filter': TunableSimFilter.TunableReference(description='\n                The filter to use to find a parent.\n                ')}

        def get_sim_filter_gsi_name(self):
            return str(self)

        def get_parent(self, interaction, pregnancy_subject_sim_info):
            filter_results = services.sim_filter_service().submit_matching_filter(sim_filter=(self.filter), allow_yielding=False,
              requesting_sim_info=pregnancy_subject_sim_info,
              gsi_source_fn=(self.get_sim_filter_gsi_name))
            if filter_results:
                parent = random.choice([filter_result.sim_info for filter_result in filter_results])
                return parent
            return (None, False)

    FACTORY_TUNABLES = {'pregnancy_subject':TunableEnumEntry(description='\n            The participant of this interaction that is to be impregnated. There\n            are no age or gender restrictions on this Sim, so ensure that you\n            are tuning the appropriate tests to avoid unwanted pregnancies.\n            ',
       tunable_type=ParticipantTypeSingle,
       default=ParticipantTypeSingle.Actor), 
     'pregnancy_parent':TunableVariant(description='\n            The participant of this interaction that is to be the impregnator.\n            ',
       from_participant=_PregnancyParentParticipant.TunableFactory(),
       from_filter=_PregnancyParentFilter.TunableFactory(),
       default='from_participant'), 
     'pregnancy_origin':TunableEnumEntry(description='\n            Define the origin of this pregnancy. This value is used to determine\n            some of the random elements at birth.\n            ',
       tunable_type=PregnancyOrigin,
       default=PregnancyOrigin.DEFAULT)}

    def _do_behavior(self, *args, **kwargs):
        subject_sim = self.interaction.get_participant(self.pregnancy_subject)
        return subject_sim is None or subject_sim.household.free_slot_count or None
        death_interaction = get_death_interaction(subject_sim)
        if death_interaction is not None:
            return
        subject_sim_info = subject_sim.sim_info
        parent_sim_info, single_sim_is_allowed = self.pregnancy_parent.get_parent(self.interaction, subject_sim_info)
        if parent_sim_info is None:
            return
        subject_sim_info.pregnancy_tracker.start_pregnancy(subject_sim_info, parent_sim_info, pregnancy_origin=(self.pregnancy_origin), single_sim_is_allowed=single_sim_is_allowed)