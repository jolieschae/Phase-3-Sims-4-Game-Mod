# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\careers\coworker.py
# Compiled at: 2017-05-12 16:28:57
# Size of source mod 2**32: 3935 bytes
from _collections import defaultdict
import itertools
from relationships.relationship_bit import RelationshipBit
import services, sims4.log
logger = sims4.log.Logger('Coworker', default_owner='tingyul')

class CoworkerMixin:
    COWORKER_RELATIONSHIP_BIT = RelationshipBit.TunableReference(description='\n        The relationship bit for coworkers.\n        ')

    def add_coworker_relationship_bit(self):
        if not self.has_coworkers:
            return
        sim_info_manager = services.sim_info_manager()
        for target in sim_info_manager.values():
            if self._sim_info is target:
                continue
            if not target.career_tracker is None:
                if target.career_tracker.get_career_by_uid(self.guid64) is None:
                    continue
                add_coworker_relationship_bit(self._sim_info, target)

    def remove_coworker_relationship_bit(self):
        if not self.has_coworkers:
            return
        for target in self.get_coworker_sim_infos_gen():
            remove_coworker_relationship_bit(self._sim_info, target)

    def get_coworker_sim_infos_gen(self):
        tracker = self._sim_info.relationship_tracker
        for target in tracker.get_target_sim_infos():
            if target is None:
                logger.callstack('SimInfos not all loaded', level=(sims4.log.LEVEL_ERROR))
                continue
            if not tracker.has_bit(target.id, self.COWORKER_RELATIONSHIP_BIT):
                continue
            yield target


def fixup_coworker_relationship_bit():
    career_map = defaultdict(list)
    sim_info_manager = services.sim_info_manager()
    for sim_info in sim_info_manager.values():
        if sim_info.career_tracker is None:
            continue
        for career in sim_info.careers.values():
            if not career.has_coworkers:
                continue
            career_map[career.guid64].append(sim_info)

    for coworkers in career_map.values():
        for a, b in itertools.combinations(coworkers, 2):
            if a is b:
                continue
            if not a.relationship_tracker.has_bit(b.id, CoworkerMixin.COWORKER_RELATIONSHIP_BIT):
                add_coworker_relationship_bit(a, b)


def add_coworker_relationship_bit(a, b):
    a.relationship_tracker.add_relationship_bit(b.id, CoworkerMixin.COWORKER_RELATIONSHIP_BIT)


def remove_coworker_relationship_bit(a, b):
    a.relationship_tracker.remove_relationship_bit(b.id, CoworkerMixin.COWORKER_RELATIONSHIP_BIT)