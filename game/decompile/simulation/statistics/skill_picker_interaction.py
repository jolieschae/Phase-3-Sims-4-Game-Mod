# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\statistics\skill_picker_interaction.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 6405 bytes
from interactions.base.picker_interaction import PickerSuperInteraction
from sims4.utils import flexmethod
from sims4.tuning.tunable import OptionalTunable, Tunable, TunableInterval, TunableReference
import statistics
from sims4.tuning.tunable_base import GroupNames
from builtins import int
from statistics.skill import Skill
import services
from ui.ui_dialog_picker import ObjectPickerRow
import sims4
from interactions.utils.tunable import TunableContinuation
from interactions import ParticipantType

class SkillPickerSuperInteraction(PickerSuperInteraction):
    INSTANCE_TUNABLES = {'actor_continuation':TunableContinuation(description='\n            If specified, a continuation to push on the actor when a picker \n            selection has been made.\n            ',
       locked_args={'actor': ParticipantType.Actor},
       tuning_group=GroupNames.PICKERTUNING), 
     'show_hidden_skills':Tunable(description=' \n                When true, shows hidden skills in the picker.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.PICKERTUNING), 
     'show_max_level_skills':Tunable(description='\n                When true, will allow skills at max level to be shown in the picker\n                ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.PICKERTUNING), 
     'show_unattained_skills':Tunable(description="\n                When true, will allow skills that the Sim doesn't have at any level to appear.\n                NOTE: If this is true, skill_range_filter will be ignored for skills the Sim does not have\n                already.\n                ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.PICKERTUNING), 
     'skill_range_filter':OptionalTunable(tunable=TunableInterval(description='\n                       A skill must fall within the given range for the actor for that\n                       skill to show up in the picker\n                       ',
       tunable_type=int,
       default_lower=0,
       default_upper=20),
       tuning_group=GroupNames.PICKERTUNING), 
     'stat_to_copy_value_to':OptionalTunable(tunable=TunableReference(description='\n                    If tuned, the value of the picked statistic will be copied to this stat\n                    after picking.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('Skill', )),
       tuning_group=GroupNames.PICKERTUNING)}

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog((self.sim), target_sim=(self.sim))
        return True
        if False:
            yield None

    @classmethod
    def _is_skill_valid(cls, skill, sim):
        if not skill.can_add(sim):
            return False
            if skill.hidden:
                if not cls.show_hidden_skills:
                    return False
            tracker = sim.get_tracker(skill)
            if tracker is None:
                return False
            stat = tracker.get_statistic(skill)
            if stat is None:
                if not cls.show_unattained_skills:
                    return False
        elif stat is not None:
            if not cls.show_max_level_skills:
                if stat.reached_max_level:
                    return False
            if cls.skill_range_filter:
                skill_value = stat.get_user_value()
                if not skill_value < cls.skill_range_filter.lower_bound:
                    if skill_value > cls.skill_range_filter.upper_bound:
                        return False
        return True

    @classmethod
    def has_valid_choice(cls, target, context, **kwargs):
        sim = context.sim
        skill_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for skill in skill_manager.all_skills_gen():
            if cls._is_skill_valid(skill, sim):
                return True

        return False

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        sim = context.sim
        skill_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for skill in skill_manager.all_skills_gen():
            if not cls._is_skill_valid(skill, sim):
                continue
            row = ObjectPickerRow(name=(skill.stat_name), icon=(skill.icon),
              row_description=(skill.skill_description(context.sim)),
              tag=skill)
            yield row

    def on_choice_selected(self, choice_tag, **kwargs):
        if choice_tag is not None:
            if self.stat_to_copy_value_to is not None:
                sim = self._sim
                tracker = sim.get_tracker(choice_tag)
                if tracker is not None:
                    stat = tracker.get_statistic(choice_tag)
                    if stat is not None:
                        tracker.set_value((self.stat_to_copy_value_to), (stat.get_value()), add=True)
            kwargs_copy = kwargs.copy()
            kwargs_copy['picked_statistic'] = choice_tag
            (self.push_tunable_continuation)((self.actor_continuation), **kwargs_copy)