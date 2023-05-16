# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\game_effect_modifier\relationship_track_decay_locker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 4920 bytes
from game_effect_modifier.base_game_effect_modifier import BaseGameEffectModifier
from game_effect_modifier.game_effect_type import GameEffectType
from sims4.tuning.tunable import HasTunableSingletonFactory, TunableReference
import services, sims4.resources, zone_types

class RelationshipTrackDecayLocker(HasTunableSingletonFactory, BaseGameEffectModifier):
    FACTORY_TUNABLES = {'description':'\n        A modifier for locking the decay of a relationship track.\n        ', 
     'relationship_track':TunableReference(description='\n        The relationship track to lock.\n        ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('RelationshipTrack', ))}

    def __init__(self, relationship_track, **kwargs):
        super().__init__(GameEffectType.RELATIONSHIP_TRACK_DECAY_LOCKER)
        self._track_type = relationship_track

    def apply_modifier(self, sim_info):

        def _all_sim_infos_loaded_callback(*arg, **kwargs):
            zone = services.current_zone()
            zone.unregister_callback(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED, _all_sim_infos_loaded_callback)
            self._set_decay_lock_all_relationships(sim_info, lock=True)
            self._initialize_create_relationship_callback(sim_info)

        zone = services.current_zone()
        if not zone.have_households_and_sim_infos_loaded:
            if not zone.is_zone_running:
                zone.register_callback(zone_types.ZoneState.HOUSEHOLDS_AND_SIM_INFOS_LOADED, _all_sim_infos_loaded_callback)
                return
        self._set_decay_lock_all_relationships(sim_info)
        self._initialize_create_relationship_callback(sim_info)

    def _initialize_create_relationship_callback(self, owner):
        tracker = owner.relationship_tracker
        tracker.add_create_relationship_listener(self._relationship_added_callback)

    def _set_decay_lock_all_relationships(self, owner, lock=True):
        tracker = owner.relationship_tracker
        sim_info_manager = services.sim_info_manager()
        for other_sim_id in tracker.target_sim_gen():
            other_sim_info = sim_info_manager.get(other_sim_id)
            if other_sim_info is None:
                continue
            track = tracker.get_relationship_track(other_sim_id, (self._track_type), add=True)
            other_tracker = other_sim_info.relationship_tracker
            other_track = other_tracker.get_relationship_track((owner.id), (self._track_type), add=True)
            if not track is None:
                if other_track is None:
                    continue
                if lock:
                    track.add_decay_rate_modifier(0)
                    other_track.add_decay_rate_modifier(0)
                else:
                    track.remove_decay_rate_modifier(0)
                    other_track.remove_decay_rate_modifier(0)

    def _relationship_added_callback(self, _, relationship):
        sim_a_track = relationship.get_track((relationship.sim_id_a), (self._track_type), add=True)
        sim_b_track = relationship.get_track((relationship.sim_id_b), (self._track_type), add=True)
        if sim_a_track is not None:
            sim_a_track.add_decay_rate_modifier(0)
        if sim_a_track is not sim_b_track:
            sim_b_track.add_decay_rate_modifier(0)

    def remove_modifier(self, sim_info, handle):
        tracker = sim_info.relationship_tracker
        tracker.remove_create_relationship_listener(self._relationship_added_callback)
        self._set_decay_lock_all_relationships(sim_info, lock=False)