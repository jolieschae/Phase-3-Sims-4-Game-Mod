# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\object_relationship_track_tracker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 6350 bytes
import itertools, services, sims4.log
from event_testing.resolver import SingleSimResolver
from statistics.base_statistic_tracker import BaseStatisticTracker
logger = sims4.log.Logger('Object Relationship', default_owner='shipark')

class RelationshipTrackTrackerBase(BaseStatisticTracker):
    __slots__ = ('_rel_data', '__weakref__')

    def __init__(self, rel_data, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._rel_data = rel_data

    def set_longterm_tracks_locked(self, value):
        self._longterm_tracks_locked = value
        self.enable_player_sim_track_decay()

    def is_track_locked(self, track):
        return self._longterm_tracks_locked and not track.is_short_term_context

    @property
    def rel_data(self):
        return self._rel_data

    def enable_player_sim_track_decay(self, to_enable=True):
        if self._statistics is None:
            return
        for track in self._statistics.values():
            if track is not None and track.decay_only_affects_played_sims:
                logger.debug('    Updating track {} for {}', track, self._rel_data)
                track.reset_decay_alarm(use_cached_time=True)

    def are_all_tracks_that_cause_culling_at_convergence(self):
        if self._statistics is None:
            return True
        else:
            tracks_that_cause_culling_at_convergence = [track for track in self._statistics.values() if track is not None if track.causes_delayed_removal_on_convergence]
            return tracks_that_cause_culling_at_convergence or False
        for track in tracks_that_cause_culling_at_convergence:
            if not track.is_at_convergence():
                return False

        return True

    def on_relationship_bit_added(self, bit, sim_id):
        pass

    def on_relationship_bit_removed(self, bit, sim_id):
        pass


class ObjectRelationshipTrackTracker(RelationshipTrackTrackerBase):
    __slots__ = ('load_in_progress', '_longterm_tracks_locked')

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self.load_in_progress = False
        self._longterm_tracks_locked = False

    def add_statistic(self, stat_type, owner=None, **kwargs):
        if self.is_track_locked(stat_type):
            return
        else:
            relationship_track = (super().add_statistic)(stat_type, owner=owner, **kwargs)
            if relationship_track is None:
                return
            relationship_service = services.relationship_service()
            for relationship_multipliers in itertools.chain(relationship_service.get_relationship_multipliers_for_sim(self._rel_data.sim_id_a)):
                for rel_track, multiplier in relationship_multipliers.items():
                    if rel_track is stat_type:
                        relationship_track.add_statistic_multiplier(multiplier)

            if not self.load_in_progress:
                if relationship_track.tested_initial_modifier is not None:
                    sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
                    if sim_info_a is None:
                        return relationship_track
                    modified_amount = relationship_track.tested_initial_modifier.get_max_modifier(SingleSimResolver(sim_info_a))
                    relationship_track.add_value(modified_amount)
        return relationship_track

    def set_value(self, stat_type, value, apply_initial_modifier=False, **kwargs):
        modified_amount = 0.0
        if apply_initial_modifier:
            if stat_type.tested_initial_modifier is not None:
                sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
                if sim_info_a is not None:
                    modified_amount = stat_type.tested_initial_modifier.get_max_modifier(SingleSimResolver(sim_info_a))
        (super().set_value)(stat_type, (value + modified_amount), **kwargs)

    def should_suppress_calculations(self):
        return self.load_in_progress

    def get_statistic(self, stat_type, add=False):
        if stat_type is None:
            logger.error('stat_type is None in ObjectRelationshipTrackTracker.get_statistic()')
            return
        return super().get_statistic(stat_type, add=add)

    @classmethod
    def _tuning_loaded_callback(cls):
        super()._tuning_loaded_callback()
        cls.bit_data = cls.bit_data_tuning()
        cls.bit_data.build_track_data()
        cls._build_utility_curve_from_tuning_data(cls.ad_data)