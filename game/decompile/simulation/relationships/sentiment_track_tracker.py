# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\sentiment_track_tracker.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 26694 bytes
import alarms, clock, date_and_time, services, sims4.resources
from balloon.balloon_enums import BALLOON_TYPE_LOOKUP, BalloonTypeEnum
from balloon.balloon_request import BalloonRequest
from balloon.tunable_balloon import TunableBalloon
from date_and_time import create_time_span, TimeSpan
from distributor.shared_messages import IconInfoData
from event_testing.resolver import DoubleSimResolver, SingleSimResolver
from interactions.utils.tunable_icon import TunableIconVariant
from objects.components.types import PROXIMITY_COMPONENT
from relationships.relationship_enums import SentimentSignType
from relationships.relationship_enums import SentimentDurationType
from relationships.relationship_track_tracker import RelationshipTrackTracker
from sims.sim_info_types import Age
from sims4.math import Threshold
from sims4.random import weighted_random_item
from sims4.tuning.geometric import TunableVector3
from sims4.tuning.tunable import Tunable, TunableRange, TunableSimMinute, TunableTuple, TunableEnumEntry, TunableResourceKey
from tunable_multiplier import TunableMultiplier
logger = sims4.log.Logger('Relationship', default_owner='boster')

class DelayedBalloonInfo:

    def __init__(self):
        self.owner_sim_info = None
        self.track_type = None
        self.icon_info = None
        self.alarm_handle = None


class SentimentTrackTracker(RelationshipTrackTracker):
    SENTIMENT_CAP = TunableRange(description='\n        Maximum amount of sentiments that one sim can have towards another individual sim.\n        If someone wants to make this a value higher than 4, please sync up with a GPE lead first.\n        ',
      tunable_type=int,
      default=4,
      maximum=4,
      minimum=1)
    PROXIMITY_LOOT_COOLDOWN = TunableSimMinute(description='\n        The number of seconds until a sim is allowed to attempt to roll to get a buff from a SentimentTrack that \n        they have towards a specific sim.\n        ',
      default=100,
      minimum=0)
    PROXIMITY_NO_LOOT_CHANCE_WEIGHT = TunableMultiplier.TunableFactory(description='\n        The weighted chance that a sim may roll to not get a loot when coming in proximity of a sim that they have a\n        sentiment towards.\n        ')
    NEGATIVE_LONG_TERM_VALUE_THRESHOLD = Tunable(description='\n        The SentimentTrack value below which a positive long-term SentimentTrack can replace a negative \n        long-term SentimentTrack\n        ',
      tunable_type=int,
      default=1)
    LONG_TERM_PRIORITY_VALUE_THRESHOLD = Tunable(description='\n        The SentimentTrack value below which a lower priority long-term SentimentTrack can replace a higher priority \n        long-term SentimentTrack.\n        ',
      tunable_type=int,
      default=1)
    PRIORITY_VALUE_ADJUSTMENT = Tunable(description='\n        When failing to add an opposite sign long-term SentimentTrack due to existing having higher priority,\n        This will be a whole number value added to the existing long term SentimentTrack value.\n        ',
      tunable_type=int,
      default=0)
    LONG_TERM_VALUE_ADJUSTMENT = Tunable(description='\n        When failing to add a positive long-term SentimentTrack. This will be a whole number value added to the \n        negative long term SentimentTrack value.\n        ',
      tunable_type=int,
      default=1)
    NEGATIVE_SHORT_TERM_VALUE_THRESHOLD = Tunable(description='\n        SentimentTrack value below which a positive short-term SentimentTrack can\n        replace all negative short-term SentimentTracks\n        ',
      tunable_type=int,
      default=1)
    SHORT_TERM_VALUE_ADJUSTMENT = Tunable(description='\n        When failing to add a positive short-term SentimentTrack. This will be a whole number value added to the \n        existing negative short term SentimentTrack values.\n        ',
      tunable_type=int,
      default=1)
    BALLOON_DATA = TunableTuple(description='\n        Information that will be used to create a balloon when a sentiment gets added to a sim.\n        ',
      balloon_types=TunableTuple(description='\n            The Visual Style of the balloon background.\n            ',
      default_type=TunableEnumEntry(description='\n                The default visual style of the balloon background.\n                ',
      tunable_type=BalloonTypeEnum,
      default=(BalloonTypeEnum.SENTIMENT)),
      infant_type=TunableEnumEntry(description="\n                The infant's visual style of the balloon background.\n                ",
      tunable_type=BalloonTypeEnum,
      default=(BalloonTypeEnum.SENTIMENT_INFANT))),
      icon=TunableIconVariant(description='\n            The Icon that will be showed within the balloon.\n            '),
      overlay=TunableResourceKey(description='\n            The overlay for the balloon, if present.\n            ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      default=None,
      allow_none=True),
      duration=TunableRange(description='\n            The duration, in seconds, that a balloon should last.\n            ',
      tunable_type=float,
      default=(TunableBalloon.BALLOON_DURATION),
      minimum=0.0),
      balloon_view_offsets=TunableTuple(description='\n            The Vector3 offsets from the balloon bone to the thought balloon. \n            ',
      default_offset=TunableVector3(description='\n                The default Vector3 offset from the balloon bone to the thought balloon. \n                ',
      default=(TunableVector3.DEFAULT_ZERO)),
      infant_offset=TunableVector3(description='\n                The infant Vector3 offset from the balloon bone to the thought balloon. \n                ',
      default=(TunableVector3.DEFAULT_ZERO))),
      balloon_stack_window_seconds=TunableRange(description='\n            The delay in seconds that a sentiment bubble should wait and see\n            if similar sentiments on the same sim is triggered (generally towards multiple other sims).\n            If similar sentiments are detected within the time window, they will be condensed into a \n            "multi-sentiment" visual treatment. Numbers are in sim seconds \n            ',
      tunable_type=int,
      default=10,
      minimum=10),
      multi_sim_icon=TunableResourceKey(description='\n            The Icon that will be showed within the balloon for sentiments towards multiple sims.\n            ',
      resource_types=(sims4.resources.CompoundTypes.IMAGE),
      default=None,
      allow_none=True))
    _balloon_info_map = {}
    __slots__ = 'proximity_cooldown_end_time'

    def __init__(self, rel_data):
        super().__init__(rel_data)
        self.proximity_cooldown_end_time = None

    def on_sim_creation(self, sim):
        if len(self) > 0:
            instanced_actor = services.sim_info_manager().get(self.rel_data.sim_id_a).get_sim_instance()
            if instanced_actor is sim:
                instanced_actor.get_component(PROXIMITY_COMPONENT).register_proximity_callback(self.rel_data.sim_id_b, self._on_target_in_proximity)

    def on_initial_startup(self):
        self.add_on_remove_callback(self._on_num_sentiments_changed)

    def _try_add_sentiment_longterm(self, new_track, current_short_term_list, current_long_term):
        if len(current_short_term_list) > 0:
            if current_short_term_list[0].sign != new_track.sign:
                self._remove_sentiment_list(current_short_term_list)
                current_short_term_list = []
        if current_long_term is None:
            if len(self) >= SentimentTrackTracker.SENTIMENT_CAP:
                if len(current_short_term_list) > 0:
                    self.remove_statistic(current_short_term_list[0].stat_type)
            return True
        if new_track.long_term_priority != current_long_term.long_term_priority:
            current_priority = -1 if current_long_term.long_term_priority is None else current_long_term.long_term_priority
            new_priority = -1 if new_track.long_term_priority is None else new_track.long_term_priority
            if current_priority < new_priority:
                self.remove_statistic(current_long_term.stat_type)
                return True
            minutes_to_decay = current_long_term.get_decay_time(Threshold(value=0))
            if minutes_to_decay < SentimentTrackTracker.LONG_TERM_PRIORITY_VALUE_THRESHOLD:
                self.remove_statistic(current_long_term.stat_type)
                return True
            if new_track.sign != current_long_term.sign:
                self.add_value(current_long_term.stat_type, SentimentTrackTracker.PRIORITY_VALUE_ADJUSTMENT)
            return False
        if new_track.sign == current_long_term.sign or current_long_term.sign is SentimentSignType.POSITIVE:
            self.remove_statistic(current_long_term.stat_type)
            return True
        minutes_to_decay = current_long_term.get_decay_time(Threshold(value=0))
        if minutes_to_decay < SentimentTrackTracker.NEGATIVE_LONG_TERM_VALUE_THRESHOLD:
            self.remove_statistic(current_long_term.stat_type)
            return True
        self.add_value(current_long_term.stat_type, SentimentTrackTracker.LONG_TERM_VALUE_ADJUSTMENT)
        return False

    def _remove_sentiment_list(self, sentiment_list):
        for sentiment_track in sentiment_list:
            self._clean_up_rel_bits(sentiment_track)
            self.remove_statistic(sentiment_track.stat_type)

    def _clean_up_rel_bits(self, sentiment_track):
        old_bit, _ = sentiment_track.update_instance_data()
        if old_bit is not None:
            sim_id_a = sentiment_track.tracker.rel_data.sim_id_a
            sim_id_b = sentiment_track.tracker.rel_data.sim_id_b
            sentiment_track.tracker.rel_data.relationship.remove_bit(sim_id_b, sim_id_a, old_bit)

    def _try_add_sentiment_shortterm(self, new_track, current_short_term_list, current_long_term):
        if len(current_short_term_list) > 0:
            if new_track.sign == current_short_term_list[0].sign:
                if new_track.stat_type in current_short_term_list:
                    self.remove_statistic(new_track.stat_type)
                else:
                    if len(self) >= SentimentTrackTracker.SENTIMENT_CAP:
                        self.remove_statistic(current_short_term_list[0].stat_type)
                return True
            if new_track.sign is SentimentSignType.NEGATIVE:
                self._remove_sentiment_list(current_short_term_list)
                return True
            furthest_from_decay = current_short_term_list[-1]
            if self.get_value(furthest_from_decay.stat_type) < SentimentTrackTracker.NEGATIVE_SHORT_TERM_VALUE_THRESHOLD:
                self._remove_sentiment_list(current_short_term_list)
                return True
            for short_term_track in current_short_term_list:
                self.add_value(short_term_track.stat_type, SentimentTrackTracker.SHORT_TERM_VALUE_ADJUSTMENT)

            return False
        return current_long_term is None or SentimentTrackTracker.SENTIMENT_CAP >= 2

    def set_max(self, stat_type):
        stat = self.add_statistic(stat_type)
        if stat is not None:
            self.set_value(stat_type, stat.max_value)

    def add_statistic(self, new_track, owner=None, **kwargs):
        if self.rel_data.is_object_rel():
            logger.error('Error, can not apply a sentiment towards an object. \n                            Implement an ObjectSentimentTrackTracker class if we need to support\n                            sim->object sentiments')
            return
        else:
            current_short_term_list = []
            current_long_term = None
            for current_track in self:
                if current_track.duration == SentimentDurationType.LONG:
                    current_long_term = current_track
                else:
                    current_short_term_list.append(current_track)

            if current_short_term_list:
                current_short_term_list.sort(key=(lambda t: self.get_value(t)))
            if new_track.duration == SentimentDurationType.LONG:
                can_add = self._try_add_sentiment_longterm(new_track, current_short_term_list, current_long_term)
            else:
                can_add = self._try_add_sentiment_shortterm(new_track, current_short_term_list, current_long_term)
        stat = None
        if can_add:
            stat = (super().add_statistic)(new_track, owner, **kwargs)
        if stat is not None:
            self._on_num_sentiments_changed()
            self.show_sentiment_balloon(stat)
        return stat

    def _cancel_alarm(self):
        balloon_info = SentimentTrackTracker._balloon_info_map.get(self.rel_data.sim_id_a)
        if balloon_info is not None:
            if balloon_info.alarm_handle is not None:
                alarms.cancel_alarm(balloon_info.alarm_handle)
                balloon_info.alarm_handle = None

    def _unregister_proximity_callback(self):
        actor_sim_info = services.sim_info_manager().get(self.rel_data.sim_id_a)
        if actor_sim_info is None:
            return
        instanced_actor = actor_sim_info.get_sim_instance()
        if instanced_actor:
            instanced_actor.get_component(PROXIMITY_COMPONENT).unregister_proximity_callback(self.rel_data.sim_id_b, self._on_target_in_proximity)

    def destroy(self):
        self._cancel_alarm()
        self._unregister_proximity_callback()
        if self.rel_data.sim_id_a in SentimentTrackTracker._balloon_info_map:
            del SentimentTrackTracker._balloon_info_map[self.rel_data.sim_id_a]
        super().destroy()

    def _get_balloon_view_offset(self, sim_info):
        if sim_info is not None:
            if sim_info.age == Age.INFANT:
                return self.BALLOON_DATA.balloon_view_offsets.infant_offset
        return self.BALLOON_DATA.balloon_view_offsets.default_offset

    def _get_balloon_type(self, sim_info):
        if sim_info is not None:
            if sim_info.age == Age.INFANT:
                return self.BALLOON_DATA.balloon_types.infant_type
        return self.BALLOON_DATA.balloon_types.default_type

    def _show_delayed_balloon(self, handle):
        balloon_info = SentimentTrackTracker._balloon_info_map.get(self.rel_data.sim_id_a)
        sim_info = balloon_info.owner_sim_info
        balloon_type, priority = BALLOON_TYPE_LOOKUP[self._get_balloon_type(sim_info)]
        request = BalloonRequest(sim_info, None, None, self.BALLOON_DATA.overlay, balloon_type, priority, self.BALLOON_DATA.duration, None, None, balloon_info.icon_info, self._get_balloon_view_offset(sim_info), balloon_info.track_type)
        request.distribute()
        self._cancel_alarm()
        del SentimentTrackTracker._balloon_info_map[self.rel_data.sim_id_a]

    def show_sentiment_balloon(self, new_track_stat):
        balloon_owner_sim_info = services.object_manager().get(self.rel_data.sim_id_a)
        sentiment_target_sim_info = services.object_manager().get(self.rel_data.sim_id_b)
        if balloon_owner_sim_info is None or sentiment_target_sim_info is None:
            return
        else:
            balloon_info = SentimentTrackTracker._balloon_info_map.get(self.rel_data.sim_id_a)
            if balloon_info is None:
                SentimentTrackTracker._balloon_info_map[self.rel_data.sim_id_a] = balloon_info = DelayedBalloonInfo()
                resolver = SingleSimResolver(sentiment_target_sim_info)
                balloon_info.icon_info = self.BALLOON_DATA.icon(resolver, balloon_target_override=None)
                balloon_info.track_type = new_track_stat
                balloon_info.owner_sim_info = balloon_owner_sim_info
            else:
                balloon_info.icon_info = IconInfoData(self.BALLOON_DATA.multi_sim_icon)
        self._cancel_alarm()
        alarm_duration = TimeSpan(self.BALLOON_DATA.balloon_stack_window_seconds * date_and_time.REAL_MILLISECONDS_PER_SIM_SECOND)
        balloon_info.alarm_handle = alarms.add_alarm(self, alarm_duration, self._show_delayed_balloon)

    def set_value(self, stat_type, value, apply_initial_modifier=False, **kwargs):
        (super().set_value)(stat_type, value, apply_initial_modifier, **kwargs)

    def _on_num_sentiments_changed(self, *_):
        actor_sim_info = services.sim_info_manager().get(self.rel_data.sim_id_a)
        if actor_sim_info is None:
            return
            instanced_actor = actor_sim_info.get_sim_instance()
            if instanced_actor is not None:
                num_sentiments = len(self)
                if num_sentiments == 0:
                    instanced_actor.get_component(PROXIMITY_COMPONENT).unregister_proximity_callback(self.rel_data.sim_id_b, self._on_target_in_proximity)
        elif num_sentiments == 1:
            target_sim_id = self.rel_data.sim_id_b
            callback = self._on_target_in_proximity
            proximity_component = instanced_actor.get_component(PROXIMITY_COMPONENT)
            if not proximity_component.has_proximity_callback(target_sim_id, callback):
                proximity_component.register_proximity_callback(self.rel_data.sim_id_b, self._on_target_in_proximity)
                self.proximity_cooldown_end_time = services.time_service().sim_now + create_time_span(minutes=(self.PROXIMITY_LOOT_COOLDOWN))

    def _on_target_in_proximity(self, target_sim):
        sim_now = services.time_service().sim_now
        if self.proximity_cooldown_end_time is not None:
            if sim_now < self.proximity_cooldown_end_time:
                return
        self.proximity_cooldown_end_time = sim_now + clock.interval_in_sim_minutes(self.PROXIMITY_LOOT_COOLDOWN)
        actor_sim_info = services.sim_info_manager().get(self.rel_data.sim_id_a)
        target_sim_info = services.sim_info_manager().get(self.rel_data.sim_id_b)
        resolver = DoubleSimResolver(actor_sim_info, target_sim_info)
        is_target_sim_bassinet = target_sim.is_bassinet
        weighted_loots = [(sentiment.proximity_loot_chance_weight.get_multiplier(resolver), sentiment.loot_on_proximity) for sentiment in self if is_target_sim_bassinet if sentiment.should_proximity_loot_include_bassinet]
        weighted_loots.append((self.PROXIMITY_NO_LOOT_CHANCE_WEIGHT.get_multiplier(resolver), None))
        random_loots = weighted_random_item(weighted_loots)
        if random_loots is not None:
            for loot in random_loots:
                loot.apply_to_resolver(resolver)