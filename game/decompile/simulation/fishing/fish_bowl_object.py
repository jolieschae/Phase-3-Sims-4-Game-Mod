# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\fishing\fish_bowl_object.py
# Compiled at: 2020-05-14 16:52:19
# Size of source mod 2**32: 7222 bytes
from protocolbuffers import UI_pb2 as ui_protocols
from event_testing.tests import CompoundTestList
from objects.components import types
import broadcasters.environment_score.environment_score_component, objects.game_object, sims4.log, vfx
logger = sims4.log.Logger('Fishing', default_owner='TrevorLindsey')

class FishBowl(objects.game_object.GameObject):
    VFX_SLOT_HASH = sims4.hash_util.hash32('_FX_')

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._fish_vfx = None
        self.add_component(FishBowlTooltipComponent(self, custom_tooltips=(), state_value_numbers=(),
          state_value_strings=(),
          tooltip_tests=(CompoundTestList()),
          update_if_stat_or_buck_changes=False,
          update_on_game_option_changed=False))
        self._disable_tooltip()

    def get_fish(self):
        for obj in self.inventory_component:
            return obj

    def on_object_added_to_inventory(self, fish):
        current_fish = self.get_fish()
        if not current_fish or current_fish is not fish:
            logger.error("The fish_added function was called but there is\n            either no fish in this fish bowl or the fish in it doesn't match\n            the fish making the function called.")
            return
        if current_fish.fishbowl_vfx is not None:
            self._fish_vfx = vfx.PlayEffect(self, current_fish.fishbowl_vfx, self.VFX_SLOT_HASH)
            self._fish_vfx.start()
        self._enable_tooltip()
        self.add_dynamic_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)

    def on_object_removed_from_inventory(self, fish):
        if self._fish_vfx is not None:
            self._fish_vfx.stop()
            self._fish_vfx = None
        tooltip_component = self.get_component(types.TOOLTIP_COMPONENT)
        if tooltip_component is not None:
            tooltip_component.remove_tooltip_listeners()
        self._disable_tooltip()
        self.remove_component(objects.components.types.ENVIRONMENT_SCORE_COMPONENT)

    def _ui_metadata_gen(self):
        fish = self.get_fish()
        if fish is not None:
            yield from fish._ui_metadata_gen()
        else:
            return
        if False:
            yield None

    def get_environment_score(self, sim, ignore_disabled_state=False):
        fish = self.get_fish()
        if fish is None:
            return broadcasters.environment_score.environment_score_component.EnvironmentScoreComponent.ENVIRONMENT_SCORE_ZERO
        return fish.get_environment_score(sim, ignore_disabled_state=ignore_disabled_state)

    def potential_interactions(self, *args, **kwargs):
        fish = self.get_fish()
        if fish is not None:
            yield from (fish.potential_interactions)(*args, **kwargs)
        yield from (super().potential_interactions)(*args, **kwargs)
        if False:
            yield None

    def _enable_tooltip(self):
        self.hover_tip = ui_protocols.UiObjectMetadata.HOVER_TIP_CUSTOM_OBJECT
        self.update_object_tooltip()

    def _disable_tooltip(self):
        self.hover_tip = ui_protocols.UiObjectMetadata.HOVER_TIP_DISABLED
        self.update_object_tooltip()


class FishBowlTooltipComponent(objects.components.tooltip_component.TooltipComponent):

    def _ui_metadata_gen(self):
        fish = self.owner.get_fish()
        if fish is None:
            return
        yield from fish._ui_metadata_gen()
        if False:
            yield None

    def _get_fish_tooltip_component(self):
        fish = self.owner.get_fish()
        if fish is None:
            return
        return fish.get_component(types.TOOLTIP_COMPONENT)

    def _get_custom_tooltips(self):
        fish_tooltip_component = self._get_fish_tooltip_component()
        if fish_tooltip_component is None:
            return super()._get_custom_tooltips()
        return fish_tooltip_component._get_custom_tooltips()

    def _get_tooltip_owner(self):
        fish = self.owner.get_fish()
        if fish is None or fish.get_component(types.TOOLTIP_COMPONENT) is None:
            return self.owner
        return fish

    @property
    def should_update_if_stat_or_buck_changes(self):
        fish_tooltip_component = self._get_fish_tooltip_component()
        if fish_tooltip_component is None:
            return self.update_if_stat_or_buck_changes
        return fish_tooltip_component.update_if_stat_or_buck_changes

    @property
    def should_update_on_game_option_changed(self):
        fish_tooltip_component = self._get_fish_tooltip_component()
        if fish_tooltip_component is None:
            return self.update_on_game_option_changed
        return fish_tooltip_component.update_on_game_option_changed