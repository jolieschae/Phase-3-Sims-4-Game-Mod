# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\body_type_level_commodity.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 4910 bytes
import sims4
from sims.outfits.outfit_enums import BodyType
from sims4.tuning.tunable import TunableRange, TunableList, TunableEnumEntry
from statistics.commodity import TunableCommodityState, Commodity
logger = sims4.log.Logger('BodyTypeLevelCommodity', default_owner='skorman')
with sims4.reload.protected(globals()):
    BODY_TYPE_TO_LEVEL_COMMODITY = {}

class TunableBodyTypeLevelCommodityState(TunableCommodityState):

    def __init__(self, **kwargs):
        (super().__init__)(body_type_client_level=TunableRange(description='\n                The integer representation of this state (level) \n                on the client.\n                ',
                                   tunable_type=int,
                                   minimum=0,
                                   default=0), **kwargs)


class BodyTypeLevelCommodity(Commodity):
    INSTANCE_TUNABLES = {'states':TunableList(description="\n             Commodity states based on thresholds. This should be ordered\n             from lowest to highest value. If the higher the value the worse the\n             commodity gets, check the field 'States Ordered Best To Worst'.\n             ",
       tunable=TunableBodyTypeLevelCommodityState()), 
     'body_type':TunableEnumEntry(description='\n            The body type this commodity is associated with.\n            ',
       tunable_type=BodyType,
       default=BodyType.NONE,
       invalid_enums=(
      BodyType.NONE,))}

    @classmethod
    def _tuning_loaded_callback(cls):
        super()._tuning_loaded_callback()
        if cls.body_type in BODY_TYPE_TO_LEVEL_COMMODITY:
            logger.error('Multiple BodyTypeLevelCommodities found for BodyType {}. Please check tuning.', cls.body_type)
        BODY_TYPE_TO_LEVEL_COMMODITY[cls.body_type] = cls
        cls._level_to_commodity_state = {state.body_type_client_level: state for state in cls.commodity_states}

    @classmethod
    def _verify_tuning_callback(cls):
        client_level_values = [state.body_type_client_level for state in cls.states]
        if len(client_level_values) != len(set(client_level_values)):
            logger.error('Duplicate Body Type Client Levels found in commodity states for {}.', cls)

    def _set_state(self, new_state_index, current_value, apply_state_enter_loot=False, send_client_update=True):
        new_state = self.commodity_states[new_state_index]
        sim = self.tracker.owner
        if not sim is None:
            sim.is_sim or logger.error('BodyTypeLevelCommodity {} has an owner that is not a sim, which is not allowed. Owner is {}.', self, sim)
            if self._current_state_index is None:
                self._current_state_index = self.get_state_index()
        else:
            return
        body_type_level_tracker = sim.body_type_level_tracker
        if body_type_level_tracker is None:
            if self._current_state_index is None:
                self._current_state_index = self.get_state_index()
            return
        body_type_level_tracker.request_client_level_change(self.body_type, new_state.body_type_client_level)
        super()._set_state(new_state_index, current_value, apply_state_enter_loot=apply_state_enter_loot,
          send_client_update=send_client_update)

    def set_level(self, level):
        if self._current_state_index is not None:
            if self.commodity_states[self._current_state_index].body_type_client_level == level:
                return
        state = self._level_to_commodity_state.get(level)
        if state is None:
            logger.error('Could not set {} to level {} because no matching commodity state was found. Please check tuning.', self, level)
            return
        self.set_value(state.value)

    def get_level(self):
        if self._current_state_index is None:
            return 0
        return self.commodity_states[self._current_state_index].body_type_client_level