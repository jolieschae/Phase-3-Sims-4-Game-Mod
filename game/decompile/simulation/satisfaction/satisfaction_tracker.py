# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\satisfaction\satisfaction_tracker.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 7802 bytes
import distributor
from event_testing import test_events
from protocolbuffers import GameplaySaveData_pb2
import enum, services, sims4.log, sims4.random
from distributor.ops import GenericProtocolBufferOp
from distributor.system import Distributor
from protocolbuffers import Sims_pb2
from protocolbuffers.DistributorOps_pb2 import Operation, SetWhimBucks
from sims.sim_info_lod import SimInfoLODLevel
from sims.sim_info_tracker import SimInfoTracker
from sims4.math import clamp, MAX_INT32
from sims4.tuning.tunable import TunableMapping, TunableReference, TunableTuple, Tunable, TunableEnumEntry, TunableRange
from sims4.utils import classproperty
import telemetry_helper
logger = sims4.log.Logger('Satisfaction', default_owner='mjuskelis')

class SatisfactionTracker(SimInfoTracker):
    TELEMETRY_CHANGE_ASPI = 'ASPI'
    writer = sims4.telemetry.TelemetryWriter(TELEMETRY_CHANGE_ASPI)
    TELEMETRY_SATISFACTION_POINTS_CHANGE = 'SPCH'
    TELEMETRY_SATISFACTION_POINTS_ADD = 'SPAD'
    TELEMETRY_SATISFACTION_POINTS_REMOVE = 'SPRM'
    TELEMETRY_FIELD_SATISFACTION_POINTS_SOURCE = 'spsc'
    TELEMETRY_FIELD_SATISFACTION_POINTS_CHANGE = 'spch'
    TELEMETRY_FIELD_SATISFACTION_POINTS_TOTAL = 'sptl'
    whim_bucks_change_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_SATISFACTION_POINTS_CHANGE)

    class SatisfactionAwardTypes(enum.Int):
        MONEY = 0
        BUFF = 1
        OBJECT = 2
        TRAIT = 3
        CASPART = 4

    MAX_POINTS = TunableRange(description='\n        The maximum number of points a sim can have. \n        ',
      tunable_type=int,
      minimum=1,
      default=MAX_INT32)
    SATISFACTION_STORE_ITEMS = TunableMapping(description='\n        A list of Sim based Tunable Rewards offered from the Satisfaction Store.\n        ',
      key_type=TunableReference(description='\n            The reward to offer.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.REWARD)),
      pack_safe=True),
      value_type=TunableTuple(description='\n            A collection of data about this reward.\n            ',
      cost=Tunable(description='\n                The cost to purchase the reward.\n                ',
      tunable_type=int,
      default=100),
      award_type=TunableEnumEntry(description='\n                The type of the award.\n                ',
      tunable_type=SatisfactionAwardTypes,
      default=(SatisfactionAwardTypes.MONEY))))

    def __init__(self, sim_info):
        self._satisfaction_points = 0
        self._sim_info = sim_info

    def send_satisfaction_points_update(self, reason):
        if self._sim_info.is_selectable:
            op = distributor.ops.SetWhimBucks(self._satisfaction_points, reason)
            Distributor.instance().add_op(self._sim_info, op)

    def get_satisfaction_points(self):
        return self._satisfaction_points

    def set_satisfaction_points(self, value, reason):
        self._satisfaction_points = clamp(0, value, self.MAX_POINTS)
        self.send_satisfaction_points_update(reason)
        services.get_event_manager().process_event((test_events.TestEvent.WhimBucksChanged), sim_info=(self._sim_info))

    def apply_satisfaction_points_delta(self, delta, reason, source=None):
        self.set_satisfaction_points(self._satisfaction_points + delta, reason)
        if source is not None:
            cls = self.__class__
            hook_tag = cls.TELEMETRY_SATISFACTION_POINTS_REMOVE if delta < 0 else cls.TELEMETRY_SATISFACTION_POINTS_ADD
            self._write_delta_telemetry(delta, source, hook_tag)

    def _write_delta_telemetry(self, delta, source, hook_tag):
        cls = self.__class__
        with telemetry_helper.begin_hook((cls.writer), hook_tag, sim_info=(self._sim_info)) as (hook):
            hook.write_int(cls.TELEMETRY_FIELD_SATISFACTION_POINTS_SOURCE, source)
            hook.write_int(cls.TELEMETRY_FIELD_SATISFACTION_POINTS_CHANGE, abs(delta))
            hook.write_int(cls.TELEMETRY_FIELD_SATISFACTION_POINTS_TOTAL, self._satisfaction_points)

    def purchase_satisfaction_reward(self, reward_guid64):
        reward_instance = services.get_instance_manager(sims4.resources.Types.REWARD).get(reward_guid64)
        award = reward_instance
        cost = self.SATISFACTION_STORE_ITEMS[reward_instance].cost
        if self._satisfaction_points < cost:
            logger.debug('Attempting to purchase an award with insufficient funds: Cost: {}, Funds: {}', cost, self._satisfaction_points)
            return
        self.apply_satisfaction_points_delta((-cost), (SetWhimBucks.PURCHASED_REWARD), source=reward_guid64)
        award.give_reward(self._sim_info)

    def send_satisfaction_reward_list(self):
        msg = Sims_pb2.SatisfactionRewards()
        for reward, data in self.SATISFACTION_STORE_ITEMS.items():
            reward_msg = Sims_pb2.SatisfactionReward()
            reward_msg.reward_id = reward.guid64
            reward_msg.cost = data.cost
            reward_msg.affordable = data.cost <= self._sim_info.get_satisfaction_points()
            reward_msg.available = reward.is_valid(self._sim_info)
            reward_msg.type = data.award_type
            unavailable_tooltip = reward.get_unavailable_tooltip(self._sim_info)
            if unavailable_tooltip is not None:
                reward_msg.unavailable_tooltip = unavailable_tooltip
            msg.rewards.append(reward_msg)

        msg.sim_id = self._sim_info.id
        distributor = Distributor.instance()
        distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.SIM_SATISFACTION_REWARDS, msg))

    @classproperty
    def _tracker_lod_threshold(cls):
        return SimInfoLODLevel.FULL

    def on_lod_update(self, old_lod, new_lod):
        if old_lod < self._tracker_lod_threshold:
            sim_msg = services.get_persistence_service().get_sim_proto_buff(self._sim_info.id)
            if sim_msg is not None:
                self.set_satisfaction_points(sim_msg.gameplay_data.whim_bucks, SetWhimBucks.LOAD)