# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_loot.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 2306 bytes
import services
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.log import Logger
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference
from story_progression import StoryProgressionArcSeedReason
from story_progression.story_progression_enums import StoryType
logger = Logger('StoryProgression')

class SeedStoryArc(BaseLootOperation):
    FACTORY_TUNABLES = {'story_arc': TunableReference(description='\n            The story arc we are going to seed on the Sim.\n            ',
                    manager=(services.get_instance_manager(Types.STORY_ARC)))}

    def __init__(self, *args, story_arc=None, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._story_arc = story_arc

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if not services.get_story_progression_service().story_progression_enabled:
            logger.info('Attempting to seed story arc {} but StoryProgression has been disabled.', self._story_arc)
            return
        else:
            if self._story_arc.arc_type == StoryType.SIM_BASED:
                story_progression_tracker = subject.story_progression_tracker
            else:
                if self._story_arc.arc_type == StoryType.HOUSEHOLD_BASED:
                    story_progression_tracker = subject.household.story_progression_tracker
                else:
                    logger.error('Attempting to use SeedStoryArc with a story arc of {} which is of type {} that is not supported.', self._story_arc, self._story_arc.arc_type)
                    return
            if not story_progression_tracker.can_add_arc(self._story_arc):
                return
                story_progression_tracker.add_arc((self._story_arc), start_reason=(StoryProgressionArcSeedReason.LOOT))
                if self._story_arc.arc_type == StoryType.SIM_BASED:
                    services.get_story_progression_service().cache_active_arcs_sim_id(subject.sim_id)
            elif self._story_arc.arc_type == StoryType.HOUSEHOLD_BASED:
                services.get_story_progression_service().cache_active_arcs_household_id(subject.household.id)