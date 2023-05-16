# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_goal_tuning_mixin.py
# Compiled at: 2020-07-01 18:34:08
# Size of source mod 2**32: 2272 bytes
import services, sims4, situations.situation_goal_set
from sims4.localization import TunableLocalizedString
from sims4.tuning.tunable import TunableReference, TunableResourceKey, OptionalTunable, TunableList
from sims4.tuning.tunable_base import GroupNames

class SituationGoalTuningMixin:
    INSTANCE_TUNABLES = FACTORY_TUNABLES = {'main_goal':TunableReference(description='\n            The main goal of the situation. e.g. Get Married\n            .',
       manager=services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL),
       allow_none=True,
       tuning_group=GroupNames.GOALS), 
     'main_goal_audio_sting':TunableResourceKey(description='\n            The sound to play when the main goal of this situation\n            completes.\n            ',
       allow_none=True,
       default=None,
       resource_types=(
      sims4.resources.Types.PROPX,),
       tuning_group=GroupNames.AUDIO), 
     'minor_goal_chains':TunableList(description='\n            A list of goal sets, each one starting a chain of goal sets, for selecting minor goals.\n            The list is in priority order, first being the most important.\n            At most one goal will be selected from each chain.\n            ',
       tunable=situations.situation_goal_set.SituationGoalSet.TunableReference(),
       tuning_group=GroupNames.GOALS), 
     'goal_sub_text':OptionalTunable(description='\n            If enabled, the tuned text will be shown under the goal list.\n            ',
       tunable=TunableLocalizedString(),
       tuning_group=GroupNames.GOALS), 
     'goal_button_text':OptionalTunable(description='\n            If enabled, button with tuned text will be added at \n            the bottom of goals display.\n            ',
       tunable=TunableLocalizedString(),
       tuning_group=GroupNames.GOALS)}