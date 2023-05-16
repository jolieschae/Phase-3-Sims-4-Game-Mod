# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_object_preference_tracker.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 17289 bytes
import services
from autonomy.autonomy_preference import AutonomyPreferenceType
from collections import defaultdict
from sims4.log import Logger
from singletons import DEFAULT
from weakref import WeakKeyDictionary
logger = Logger('AutonomyObjectPreference', default_owner='jmoline')

class _ProxyObjectPreferenceTracker:

    def __init__(self, owner, base_tracker):
        self._owner = owner
        self._base_tracker = base_tracker

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def base_tracker(self):
        return self._base_tracker

    @base_tracker.setter
    def base_tracker(self, value):
        self._base_tracker = value

    def get_restricted_object(self, sim_id, preference_tag, zone_id=DEFAULT, disable_overrides=False):
        if not disable_overrides:
            if self._owner.has_sim_preference_override(sim_id, preference_tag):
                override_object_id, override_subroot_index = self._owner.get_restricted_object(sim_id, preference_tag, zone_id=zone_id)
                if override_object_id is not None:
                    return (
                     override_object_id, override_subroot_index)
        else:
            if self._base_tracker is None:
                return (None, None)
            base_object_id, base_subroot_index = self._base_tracker.get_restricted_object(sim_id, preference_tag, zone_id=zone_id)
            if not disable_overrides:
                if self._owner.has_object_preference_override(base_object_id, preference_tag):
                    return (None, None)
        return (
         base_object_id, base_subroot_index)

    def get_restricted_sims(self, object_id, preference_tag):
        if self._owner.has_object_preference_override(object_id, preference_tag):
            override = self._owner.get_restricted_sims(object_id, preference_tag)
            if override is not None:
                return override
        if self._base_tracker is None:
            return
        return self._base_tracker.get_restricted_sims(object_id, preference_tag)

    def get_restricted_sim(self, object_id, subroot_index, preference_tag):
        if self._owner.has_object_preference_override(object_id, preference_tag):
            override = self._owner.get_restricted_sim(object_id, subroot_index, preference_tag)
            if override is not None:
                return override
        if self._base_tracker is None:
            return
        return self._base_tracker.get_restricted_sim(object_id, subroot_index, preference_tag)

    def get_restriction(self, sim_info, game_object, preference_tag, full_object=False, allow_test=True):
        if self._owner.has_sim_preference_override(sim_info.id, preference_tag) or self._owner.has_object_preference_override(game_object.id, preference_tag):
            override = self._owner.get_restriction(sim_info, game_object, preference_tag, full_object=full_object, allow_test=allow_test)
            if override is not None:
                return override
        if self._base_tracker is None:
            return AutonomyPreferenceType.ALLOWED
        return self._base_tracker.get_restriction(sim_info, game_object, preference_tag, full_object=full_object, allow_test=allow_test)

    def set_restriction(self, sim_info, game_objects, preference_tag, should_force):
        unoverriden_game_objects = [game_object for game_object in game_objects if not self._owner.has_object_preference_override(game_object.id, preference_tag)]
        if len(unoverriden_game_objects) == 0:
            return
        if self._base_tracker is not None:
            self._base_tracker.set_restriction(sim_info, unoverriden_game_objects, preference_tag, should_force)

    def set_object_restriction(self, sim_id, obj, preference_tag):
        if self._owner.has_object_preference_override(obj.id, preference_tag):
            return
        if self._base_tracker is not None:
            self._base_tracker.set_object_restriction(sim_id, obj, preference_tag)

    def clear_restriction(self, game_objects, preference_tag):
        unoverriden_game_objects = [game_object for game_object in game_objects if not self._owner.has_object_preference_override(game_object.id, preference_tag)]
        if len(unoverriden_game_objects) == 0:
            return
        if self._base_tracker is not None:
            self._base_tracker.clear_restriction(unoverriden_game_objects, preference_tag)

    def clear_sim_restriction(self, sim_id, zone_id=DEFAULT):
        if self._base_tracker is not None:
            self._base_tracker.clear_sim_restriction(sim_id, zone_id=zone_id)


class AutonomyObjectPreferenceTracker:

    def __init__(self):
        self._provider_overrides = defaultdict(set)
        self._override_provider = dict()
        self._sim_tag_to_object = dict()
        self._object_tag_to_sim = dict()
        self._proxies = WeakKeyDictionary()
        self._proxy_none = None

    def reset(self):
        self._provider_overrides.clear()
        self._override_provider.clear()
        self._sim_tag_to_object.clear()
        self._object_tag_to_sim.clear()
        self._proxies.clear()

    def override_tracker(self, base_tracker=None):
        if base_tracker is None:
            if self._proxy_none is None:
                self._proxy_none = _ProxyObjectPreferenceTracker(self, None)
            return self._proxy_none
        wrapped_tracker = self._proxies.get(base_tracker)
        if wrapped_tracker is None:
            wrapped_tracker = _ProxyObjectPreferenceTracker(self, base_tracker)
            self._proxies[base_tracker] = wrapped_tracker
        return wrapped_tracker

    def _update_object_tooltip(self, object_id):
        game_object = services.object_manager().get(object_id)
        if game_object is not None:
            game_object.update_object_tooltip()

    def add_preference_tag_override(self, provider, sim_id, object_id, preference_tag):
        override = (
         sim_id, object_id, preference_tag)
        sim_tag = (sim_id, preference_tag)
        object_tag = (object_id, preference_tag)
        old_object_id = self._sim_tag_to_object.get(sim_tag)
        old_object_provider = None
        if old_object_id is not None:
            old_object_provider = self._override_provider[(sim_id, old_object_id, preference_tag)]
        if object_id == old_object_id:
            if provider == old_object_provider:
                logger.warn('Adding the object preference override ({}, {}, {}, {}) multiple times. Additional attempts are ignored.', provider, sim_id, object_id, preference_tag)
                return
        old_sim_id = self._object_tag_to_sim.get(object_tag)
        old_sim_provider = None
        if old_sim_id is not None:
            old_sim_provider = self._override_provider[(old_sim_id, object_id, preference_tag)]
        if old_object_provider is not None:
            logger.warn('New object preference override ({}, {}, {}, {}) replacing old sim => object preference ({}, object={}).', provider, sim_id, object_id, preference_tag, old_object_provider, old_object_id)
            self.remove_preference_tag_override(old_object_provider, sim_id, old_object_id, preference_tag)
        if object_id != old_object_id:
            if old_sim_provider is not None:
                logger.warn('New object preference override ({}, {}, {}, {}) replacing old object => sim preference ({}, sim={}).', provider, sim_id, object_id, preference_tag, old_sim_provider, old_sim_id)
                self.remove_preference_tag_override(old_sim_provider, old_sim_id, object_id, preference_tag)
        self._provider_overrides[provider].add(override)
        self._override_provider[override] = provider
        self._sim_tag_to_object[sim_tag] = object_id
        self._object_tag_to_sim[object_tag] = sim_id
        self._update_object_tooltip(object_id)

    def remove_preference_tag_override(self, provider, sim_id, object_id, preference_tag):
        override = (
         sim_id, object_id, preference_tag)
        if provider not in self._provider_overrides or override not in self._provider_overrides[provider]:
            return
        sim_tag = (
         sim_id, preference_tag)
        object_tag = (object_id, preference_tag)
        provider_overrides = self._provider_overrides[provider]
        provider_overrides.remove(override)
        if len(provider_overrides) == 0:
            del self._provider_overrides[provider]
        del self._override_provider[override]
        del self._sim_tag_to_object[sim_tag]
        del self._object_tag_to_sim[object_tag]
        self._update_object_tooltip(object_id)

    def remove_provider_preference_tag_overrides(self, provider):
        overrides = self._provider_overrides.get(provider)
        if overrides is None:
            return
        del self._provider_overrides[provider]
        for sim_id, object_id, preference_tag in list(overrides):
            override = (
             sim_id, object_id, preference_tag)
            sim_tag = (sim_id, preference_tag)
            object_tag = (object_id, preference_tag)
            del self._override_provider[override]
            del self._sim_tag_to_object[sim_tag]
            del self._object_tag_to_sim[object_tag]
            self._update_object_tooltip(object_id)

    def has_sim_preference_override(self, sim_id, preference_tag):
        sim_tag = (
         sim_id, preference_tag)
        return sim_tag in self._sim_tag_to_object

    def has_object_preference_override(self, object_id, preference_tag):
        object_tag = (
         object_id, preference_tag)
        return object_tag in self._object_tag_to_sim

    def get_restricted_object(self, sim_id, preference_tag, zone_id=DEFAULT):
        sim_tag = (
         sim_id, preference_tag)
        obj_id = self._sim_tag_to_object.get(sim_tag)
        if obj_id is not None:
            return (
             obj_id, None)
        return (None, None)

    def get_restricted_sims(self, object_id, preference_tag):
        object_tag = (
         object_id, preference_tag)
        sim_id = self._object_tag_to_sim.get(object_tag)
        if sim_id is not None:
            return (
             sim_id,)

    def get_restricted_sim(self, object_id, subroot_index, preference_tag):
        object_tag = (
         object_id, preference_tag)
        sim_id = self._object_tag_to_sim.get(object_tag)
        if sim_id is not None:
            return sim_id

    def get_restriction(self, sim_info, game_object, preference_tag, full_object=False, allow_test=True):
        sim_tag = (
         sim_info.id, preference_tag)
        object_tag = (game_object.id, preference_tag)
        obj_id = self._sim_tag_to_object.get(sim_tag)
        sim_id = self._object_tag_to_sim.get(object_tag)
        if obj_id is None:
            if sim_id is None:
                return
        if sim_id != sim_info.id or obj_id != game_object.id:
            return AutonomyPreferenceType.DISALLOWED
        return AutonomyPreferenceType.USE_PREFERENCE