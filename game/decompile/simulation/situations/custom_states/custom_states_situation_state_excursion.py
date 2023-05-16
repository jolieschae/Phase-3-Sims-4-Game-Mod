# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\custom_states_situation_state_excursion.py
# Compiled at: 2020-04-09 23:07:21
# Size of source mod 2**32: 620 bytes
from situations.custom_states.custom_states_situation_states import CustomStatesSituationState
from snippets import define_snippet, EXCURSION_SITUATION_STATE

class ExcursionSituationState(CustomStatesSituationState):
    pass


TunableExcursionSituationStateReference, TunableExcursionSituationStateSnippet = define_snippet(EXCURSION_SITUATION_STATE, ExcursionSituationState.TunableFactory())