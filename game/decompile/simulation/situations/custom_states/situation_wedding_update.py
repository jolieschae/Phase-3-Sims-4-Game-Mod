# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\custom_states\situation_wedding_update.py
# Compiled at: 2022-03-29 18:15:50
# Size of source mod 2**32: 5962 bytes
import services, sims4
from event_testing.tests import TunableTestSet
from interactions.context import InteractionContext
from interactions.priority import Priority
from relationships.relationship_bit import RelationshipBit
from sims.outfits.outfit_enums import OutfitCategory, OutfitChangeReason
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import TunableList, TunableReference, TunableEnumEntry
from situations.custom_states.custom_states_situation import CustomStatesSituation
from situations.situation_job import SituationJob
from situations.situation_types import SituationDisplayType
from tag import Tag
logger = sims4.log.Logger('Wedding Situation Update', default_owner='shipark')

class CustomStateWeddingSituation(CustomStatesSituation):
    INSTANCE_TUNABLES = {'betrothed_job':SituationJob.TunableReference(description='\n            The Situation Job used by the betrothed couple.\n            '), 
     'move_in_together_interaction':TunableReference(description='\n            The affordance to push on the betrothed sims when the wedding event ends.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.INTERACTION)), 
     'player_outfit_tags_jobs':TunableList(description='\n            The jobs that will use the player defined outfit tags.\n            ',
       tunable=SituationJob.TunableReference(description='\n                The Situation Job that will include player defined outfit tags in its uniform.\n                ')), 
     'outfit_change_reason_default':TunableEnumEntry(description='\n            An override applied to wedding jobs if the player has not selected customized outfit.\n            \n            An enum that represents a reason for outfit change for\n            the outfit system, which determines the category of an outfit.\n            ',
       tunable_type=OutfitChangeReason,
       default=OutfitChangeReason.Invalid,
       invalid_enums=(
      OutfitChangeReason.Invalid,)), 
     'preferred_outfit_category':TunableEnumEntry(description="\n            If a sim's outfit in the tuned category complies with one of the tags in the \n            outfit extra tag set, then use that existing outfit instead of \n            generating a new one for wedding jobs. \n            ",
       tunable_type=OutfitCategory,
       default=OutfitCategory.SITUATION)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._betrothed_sims = []

    def _on_set_sim_job(self, sim, job_type):
        super()._on_set_sim_job(sim, job_type)
        if job_type is self.betrothed_job:
            self._betrothed_sims.append(sim)

    def on_remove(self):
        super().on_remove()
        if len(self._betrothed_sims) < 2:
            logger.warn('List of betrothed sims is less than two. Failed to push move-in-together interaction.')
            return
        sim = self._betrothed_sims.pop()
        target = self._betrothed_sims.pop()
        if sim is not None:
            if target is not None:
                priority = Priority.High
                context = InteractionContext(sim, InteractionContext.SOURCE_SCRIPT, priority)
                sim.push_super_affordance(self.move_in_together_interaction, target, context)

    def has_player_customized_outfit(self, job):
        if job not in self.player_outfit_tags_jobs:
            return False
        else:
            return self._seed.has_user_defined_outfit or False
        return self._seed.guest_attire_style != Tag.INVALID or self._seed.guest_attire_color != Tag.INVALID

    def permit_outfit_generation(self, job):
        return self.has_player_customized_outfit(job)

    def get_job_outfit_change_reason(self, job):
        if self.has_player_customized_outfit(job):
            return job.job_uniform.outfit_change_reason
        return self.get_default_job_outfit_change_reason()

    def get_default_job_outfit_change_reason(self):
        return self.outfit_change_reason_default

    def get_preferred_outfit_category(self):
        return self.preferred_outfit_category

    def get_job_outfit_extra_tag_set(self, job):
        if job not in self.player_outfit_tags_jobs:
            return
        else:
            outfit_tag_set = set()
            if self._seed.guest_attire_color is not None:
                if self._seed.guest_attire_color != Tag.INVALID:
                    outfit_tag_set.add(self._seed.guest_attire_color)
            if self._seed.guest_attire_style is not None and self._seed.guest_attire_style != Tag.INVALID:
                outfit_tag_set.add(self._seed.guest_attire_style)
        return outfit_tag_set


lock_instance_tunables(CustomStateWeddingSituation, situation_display_type_override=(SituationDisplayType.ACTIVITY))