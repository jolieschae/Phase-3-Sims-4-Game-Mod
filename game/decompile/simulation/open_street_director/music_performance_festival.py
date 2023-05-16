# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\open_street_director\music_performance_festival.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 15307 bytes
import itertools, services, sims4, telemetry_helper
from live_events.live_event_service import LiveEventName, LiveEventState
from event_testing.resolver import SingleSimResolver
from event_testing.test_events import TestEvent
from interactions.utils.loot import LootActions
from live_festivals import live_festival_tuning
from live_festivals.live_festival_tuning import LiveFestivalEventState
from open_street_director.festival_open_street_director import BaseFestivalOpenStreetDirector, TimedFestivalState, LoadLayerFestivalState, CleanupObjectsFestivalState, FestivalStateInfo, SituationEndedFestivalState
from sims4.tuning.tunable import TunableList, OptionalTunable, TunableEnumEntry
from sims4.tuning.tunable_base import GroupNames
from sims4.utils import classproperty
TELEMETRY_GROUP_LIVE_EVENT = 'LIVE'
TELEMETRY_HOOK_START_PHASE = 'MFPH'
TELEMETRY_FIELD_PHASE_NAME = 'phid'
telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_LIVE_EVENT)

class SpinupFestivalState(LoadLayerFestivalState):

    @classproperty
    def key(cls):
        return 1

    def _get_next_state(self):
        return self._owner.pre_performance_festival_state(self._owner)

    def __repr__(self):
        return 'Spin-Up Phase'


class PrePerformanceState(TimedFestivalState):

    @classproperty
    def key(cls):
        return 2

    def _get_next_state(self):
        if not self._owner.music_performance_festival_states:
            return self._owner.post_performance_festival_state(self._owner)
        state = self._owner.music_performance_festival_states[0]
        return state((self._owner), performance_index=0)

    def __repr__(self):
        return 'Pre-Performance Phase'


class MusicPerformanceFestivalState(SituationEndedFestivalState):
    MUSIC_PERFORMANCE_INDEX_TOKEN = 'music_performance_index'

    def __init__(self, owner, *args, performance_index=None, **kwargs):
        (super().__init__)(owner, *args, **kwargs)
        self.performance_index = performance_index

    @classproperty
    def key(self):
        return 3

    def save(self, writer):
        super().save(writer)
        writer.write_uint32(self.MUSIC_PERFORMANCE_INDEX_TOKEN, self.performance_index)

    def load_custom_state(self, reader=None):
        super().load_custom_state(reader)
        self.performance_index = reader.read_uint32(self.MUSIC_PERFORMANCE_INDEX_TOKEN, 0)

    def _get_next_state(self):
        next_performance_index = self.performance_index + 1
        if next_performance_index >= len(self._owner.music_performance_festival_states):
            return self._owner.post_performance_festival_state(self._owner)
        state = self._owner.music_performance_festival_states[next_performance_index]
        return state((self._owner), performance_index=next_performance_index)

    def _preroll_end_of_state(self):
        situation_manager = services.get_zone_situation_manager()
        for situation in itertools.chain(situation_manager.get_situations_by_type(self.situations_of_interest), situation_manager.get_situations_by_tags(self.situation_tags_of_interest)):
            situation_manager.destroy_situation_by_id(situation.id)

        super()._preroll_end_of_state()

    def __repr__(self):
        return f"Music Performance Phase {self.performance_index + 1}"


class PostPerformanceState(TimedFestivalState):

    @classproperty
    def key(cls):
        return 4

    def _get_next_state(self):
        return self._owner.cooldown_festival_state(self._owner)

    def __repr__(self):
        return 'Post-Performance Phase'


class CooldownFestivalState(TimedFestivalState):

    def on_state_activated(self, reader=None, preroll_time_override=None):
        super().on_state_activated(reader, preroll_time_override)
        self._owner._clean_up_situations()

    @classproperty
    def key(cls):
        return 6

    def _get_next_state(self):
        return self._owner.cleanup_festival_state(self._owner)

    def __repr__(self):
        return 'Cooldown Phase'


class CleanupFestivalState(CleanupObjectsFestivalState):

    @classproperty
    def key(cls):
        return 5

    def _get_next_state(self):
        pass

    def __repr__(self):
        return 'Clean-Up Phase'


class MusicFestivalOpenStreetDirector(BaseFestivalOpenStreetDirector):
    INSTANCE_TUNABLES = {'spinup_festival_state':SpinupFestivalState.TunableFactory(description='\n            The entry state of the festival, intended for loading in conditional\n            layers and starting up festival employee / festival goer situations.\n            ',
       display_name='1. Spin-up Festival State',
       tuning_group=GroupNames.STATE), 
     'pre_performance_festival_state':PrePerformanceState.TunableFactory(description='\n            The festival state that occurs prior to the first musical act coming\n            on stage and performing.\n            ',
       display_name='2. Pre-Performance Festival State',
       tuning_group=GroupNames.STATE), 
     'music_performance_festival_states':TunableList(description='\n            A list of festival states in which a series of music performance \n            situations will occur, listed in order of appearance. Once the tuned \n            "Situation of Interest" ends, this festival state will progress to \n            the next state. \n            ',
       display_name='3. Music Performance Festival States',
       tuning_group=GroupNames.STATE,
       tunable=MusicPerformanceFestivalState.TunableFactory()), 
     'post_performance_festival_state':PostPerformanceState.TunableFactory(description='\n            The festival state that occurs after the last tuned "Music Performance\n            Festival State".\n            ',
       display_name='4. Post-Performance Festival State',
       tuning_group=GroupNames.STATE), 
     'cooldown_festival_state':CooldownFestivalState.TunableFactory(description='\n            Provides a buffer between the end of all festival situations and the\n            clean-up state where we destroy conditional layers.\n            ',
       display_name='5. Cooldown Festival State.',
       tuning_group=GroupNames.STATE), 
     'cleanup_festival_state':CleanupFestivalState.TunableFactory(description='\n            The final state of the festival, intended for unloading the conditional\n            layers.\n            ',
       display_name='6. Clean-Up Festival State',
       tuning_group=GroupNames.STATE), 
     'welcome_loot':TunableList(description='\n            Loot that will target the active sim and occur on entering a zone \n            where the festival is occurring for the first time.\n            ',
       tunable=LootActions.TunableFactory()), 
     'festival_end_loot':TunableList(description='\n            Loot that will target the active sim and occur when the festival \n            ends while active.\n            ',
       tunable=LootActions.TunableFactory()), 
     'live_event_name':OptionalTunable(description='\n            Live event corresponding to the festival.\n            ',
       tunable=TunableEnumEntry(description='\n                Name of the live event associated with the festival.\n                ',
       tunable_type=LiveEventName,
       default=(LiveEventName.DEFAULT),
       invalid_enums=(
      LiveEventName.DEFAULT,)))}

    @classmethod
    def _states(cls):
        return tuple(cls._gen_states())

    def _load_state(self, reader):
        state_key = reader.read_uint32(self.SAVE_STATE_KEY_TOKEN, 0)
        if state_key == SpinupFestivalState.key:
            return FestivalStateInfo(SpinupFestivalState, self.spinup_festival_state)
            if state_key == PrePerformanceState.key:
                return FestivalStateInfo(PrePerformanceState, self.pre_performance_festival_state)
            if state_key == MusicPerformanceFestivalState.key:
                performance_index = reader.read_uint32(MusicPerformanceFestivalState.MUSIC_PERFORMANCE_INDEX_TOKEN, 0)
                if 0 <= performance_index < len(self.music_performance_festival_states):
                    state = self.music_performance_festival_states[performance_index]
                    return FestivalStateInfo(MusicPerformanceFestivalState, state)
        else:
            if state_key == PostPerformanceState.key:
                return FestivalStateInfo(PostPerformanceState, self.post_performance_festival_state)
            if state_key == CooldownFestivalState.key:
                return FestivalStateInfo(CooldownFestivalState, self.cooldown_festival_state)
            if state_key == CleanupFestivalState.key:
                return FestivalStateInfo(CleanupFestivalState, self.cleanup_festival_state)

    @classmethod
    def _gen_states(cls):
        yield FestivalStateInfo(SpinupFestivalState, cls.spinup_festival_state)
        yield FestivalStateInfo(PrePerformanceState, cls.pre_performance_festival_state)
        for state in cls.music_performance_festival_states:
            yield FestivalStateInfo(MusicPerformanceFestivalState, state)

        yield FestivalStateInfo(PostPerformanceState, cls.post_performance_festival_state)
        yield FestivalStateInfo(CooldownFestivalState, cls.cooldown_festival_state)
        yield FestivalStateInfo(CleanupFestivalState, cls.cleanup_festival_state)

    def _get_starting_state(self):
        return self.spinup_festival_state(self)

    def on_startup(self):
        super().on_startup()
        if not self.was_loaded:
            if not self.did_preroll:
                self.change_state(self._get_starting_state())
            self._send_telemetry_on_starting_up_new_festival(self._current_state)
        if self.live_event_name is not None:
            live_event_service = services.get_live_event_service()
            if live_event_service.is_live_event_data_available():
                self._self_destruct_if_live_event_inactive()
            event_manager = services.get_event_manager()
            event_manager.register_single_event(self, TestEvent.LiveEventStatesProcessed)

    def _send_telemetry_on_starting_up_new_festival(self, festival_state):
        if festival_state is None:
            return
        with telemetry_helper.begin_hook(telemetry_writer, TELEMETRY_HOOK_START_PHASE, sim_info=(services.active_sim_info())) as (hook):
            hook.write_string(TELEMETRY_FIELD_PHASE_NAME, str(festival_state))

    def on_shutdown(self):
        super().on_shutdown()
        event_manager = services.get_event_manager()
        event_manager.unregister_single_event(self, TestEvent.LiveEventStatesProcessed)

    def on_loading_screen_animation_finished(self):
        super().on_loading_screen_animation_finished()
        if not self.was_loaded:
            if not isinstance(self._current_state, self.cooldown_festival_state.factory):
                if not isinstance(self._current_state, self.cleanup_festival_state.factory):
                    active_sim_info = services.active_sim_info()
                    resolver = SingleSimResolver(active_sim_info)
                    for action in self.welcome_loot:
                        action.apply_to_resolver(resolver)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.LiveEventStatesProcessed:
            self._self_destruct_if_live_event_inactive()

    def _self_destruct_if_live_event_inactive(self):
        live_event_data = live_festival_tuning.LiveFestivalTuning.LIVE_FESTIVAL_EVENT_DATA.get(self.live_event_name)
        if live_event_data is not None:
            if live_event_data.state == LiveFestivalEventState.DISABLED:
                self.self_destruct()
                return
        live_event_service = services.get_live_event_service()
        if live_event_service.get_live_event_state(self.live_event_name) == LiveEventState.COMPLETED:
            self.self_destruct()

    def self_destruct(self):
        super().self_destruct()
        active_sim_info = services.active_sim_info()
        resolver = SingleSimResolver(active_sim_info)
        for action in self.festival_end_loot:
            action.apply_to_resolver(resolver)

    def _clean_up(self):
        if self._current_state.key != CleanupFestivalState.key:
            self.change_state(self.cleanup_festival_state(self))