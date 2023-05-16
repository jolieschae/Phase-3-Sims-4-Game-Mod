# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\custom_states_situation_states.py
# Compiled at: 2021-04-12 13:26:22
# Size of source mod 2**32: 4645 bytes
import services
from sims4.resources import Types
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, TunableList, TunableVariant, AutoFactoryInit, HasTunableSingletonFactory
from situations.custom_states.custom_states_common_tuning import RandomWeightedSituationStateKey
from situations.effect_triggering_situation_state import DurationTrigger, TimeOfDayTrigger, TestEventTrigger, CustomStatesSituationReplaceSituation, CustomStatesSituationGiveLoot, CustomStatesSituationEndSituation
from situations.situation_complex import EffectTriggeringSituationState
from snippets import CUSTOM_STATES_SITUATION_STATE, define_snippet

class CustomStatesSituationStateChange(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'possible_states': RandomWeightedSituationStateKey.TunableFactory()}

    def __call__(self, situation_state):
        situation_state.owner.change_state_by_key(self.possible_states())


class CustomStatesSituationState(EffectTriggeringSituationState):
    FACTORY_TUNABLES = {'job_and_role_changes':TunableMapping(description='\n            A mapping between situation jobs and role states that defines\n            what role states we want to switch to for sims on which jobs\n            when this situation state is entered.\n            \n            If a situation role does not need to change it does not need to\n            be specified.\n            ',
       key_type=TunableReference(description="\n                A reference to a SituationJob that we will use to change\n                sim's role state.\n                ",
       manager=(services.get_instance_manager(Types.SITUATION_JOB))),
       key_name='Situation Job',
       value_type=TunableReference(description='\n                The role state that we will switch sims of the linked job\n                into.\n                ',
       manager=(services.get_instance_manager(Types.ROLE_STATE))),
       value_name='Role State'), 
     'triggers':TunableList(description='\n            A link between effects and triggers for those effects.\n            ',
       tunable=TunableTuple(description='\n                A grouping of an effect and triggers for that effect.\n                ',
       effect=TunableVariant(description='\n                    The effect that will occur when one of the triggers is met.\n                    ',
       change_state=(CustomStatesSituationStateChange.TunableFactory()),
       end_situation=(CustomStatesSituationEndSituation.TunableFactory()),
       loot=(CustomStatesSituationGiveLoot.TunableFactory()),
       replace_situation=(CustomStatesSituationReplaceSituation.TunableFactory()),
       default='change_state'),
       triggers=TunableList(description='\n                    The different triggers that are linked to this effect.\n                    ',
       tunable=TunableVariant(description='\n                        A trigger to perform an effect within the situation.\n                        ',
       duration=(DurationTrigger.TunableFactory()),
       time_of_day=(TimeOfDayTrigger.TunableFactory()),
       test_event=(TestEventTrigger.TunableFactory()),
       default='duration'))))}

    def __init__(self, job_and_role_changes, triggers):
        super().__init__(triggers)
        self._job_and_role_changes = job_and_role_changes

    def on_activate(self, reader=None):
        super().on_activate(reader)
        for job, role_state in self._job_and_role_changes.items():
            self.owner._set_job_role_state(job, role_state)


TunableCustomStatesSituationStateReference, TunableCustomStatesSituationStateSnippet = define_snippet(CUSTOM_STATES_SITUATION_STATE, CustomStatesSituationState.TunableFactory())