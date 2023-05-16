# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\path_planner\path_plan_loots.py
# Compiled at: 2021-03-09 19:20:42
# Size of source mod 2**32: 3779 bytes
import sims4
from interactions.utils.loot_basic_op import BaseLootOperation
from objects import ALL_HIDDEN_REASONS
from routing.path_planner.path_plan_enums import WadingFootprintKeyMaskBits
from sims4.tuning.tunable import TunableEnumFlags, OptionalTunable, TunableVariant
logger = sims4.log.Logger('PathPlanContext Loots', default_owner='skorman')

class UpdateAllowedWadingDepths(BaseLootOperation):
    USE_TUNED_FLAGS = 1
    FACTORY_TUNABLES = {'allowed_wading_depths': TunableVariant(specific_flags=(OptionalTunable(TunableEnumFlags(description='\n                    Flags that define the wading depth this agent is able to route\n                    through. Each flag has a specific depth assigned to it. \n    \n                    If disabled, the agent will not be allowed to wade through \n                    water entities that consider these flags. Currently these flags \n                    are only considered when routing through ponds.\n    \n                    WADING_DEEP  = 0.7m\n                    WADING_MEDIUM  = 0.5m\n                    WADING_SHALLOW  = 0.35m\n                    WADING_VERY_SHALLOW = 0.15m\n                    ',
                                enum_type=WadingFootprintKeyMaskBits,
                                default=(WadingFootprintKeyMaskBits.WADING_MEDIUM)))),
                                locked_args={'use_tuned_flags': USE_TUNED_FLAGS},
                                default='use_tuned_flags')}

    def __init__(self, allowed_wading_depths, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._allowed_wading_depths = allowed_wading_depths

    def _apply_to_subject_and_target(self, subject, target, resolver):
        if subject.is_sim:
            subject = subject.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)
            if subject is None:
                return
        else:
            routing_component = subject.routing_component
            if routing_component is None:
                logger.error('Trying to update the allowed wading depth for object {}, which does not have a routing component', subject)
                return
            pathplan_context = routing_component.pathplan_context
            if pathplan_context is None:
                logger.error('Trying to update the allowed wading depth for object {}, which does not have a path plan context.', subject)
            elif self._allowed_wading_depths == self.USE_TUNED_FLAGS:
                result = pathplan_context.try_update_allowed_wading_depth_flags(pathplan_context._allowed_wading_depths)
            else:
                result = pathplan_context.try_update_allowed_wading_depth_flags(self._allowed_wading_depths)
            result or logger.error('Trying to update the allowed wading depth for object {}, but the new flags ({}) may cause them to get stuck based on their current intended location {}.', subject, self._allowed_wading_depths, subject.intended_location)