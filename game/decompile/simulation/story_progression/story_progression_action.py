# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_action.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 3875 bytes
from filters.tunable import TunableSimFilter
from objects import ALL_HIDDEN_REASONS
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit
import services

class _StoryProgressionAction(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'description': '\n            An action defines behavior that is to occur on a certain\n            subset of Sims affected by Story Progression.\n            '}

    def save(self, data):
        pass

    def load(self, data):
        pass

    def should_process(self, options):
        return True

    def process_action(self, story_progression_flags):
        raise NotImplementedError


class _StoryProgressionFilterAction(_StoryProgressionAction):
    FACTORY_TUNABLES = {'sim_filter': TunableSimFilter.TunableReference(description='\n            The subset of Sims this action can operate on.\n            ')}

    def _get_filter(self):
        return self.sim_filter()

    def _apply_action(self, sim_info):
        raise NotImplementedError

    def _pre_apply_action(self):
        pass

    def _post_apply_action(self):
        pass

    def _allow_instanced_sims(self):
        return False

    def get_sim_filter_gsi_name(self):
        return str(self)

    def process_action(self, story_progression_flags):

        def _on_filter_request_complete(results, *_, **__):
            if results is None:
                return
            self._pre_apply_action()
            for result in results:
                sim_info = result.sim_info
                if sim_info is None:
                    continue
                if not self._allow_instanced_sims():
                    sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS) or self._apply_action(sim_info)

            self._post_apply_action()

        services.sim_filter_service().submit_filter((self._get_filter()), _on_filter_request_complete,
          household_id=(services.active_household_id()),
          gsi_source_fn=(self.get_sim_filter_gsi_name))