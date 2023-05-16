# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\sim_knowledge.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 15516 bytes
import singletons
from sims.global_gender_preference_tuning import GlobalGenderPreferenceTuning
from protocolbuffers import SimObjectAttributes_pb2 as protocols
from careers.career_unemployment import CareerUnemployment
import services, sims4
from traits.trait_tracker import TraitTracker
logger = sims4.log.Logger('Relationship', default_owner='jjacobson')

class SimKnowledge:
    __slots__ = ('_rel_data', '_known_traits', '_knows_career', '_known_stats', '_knows_major',
                 '_knows_romantic_preference', '_knows_woohoo_preference', '_known_romantic_genders',
                 '_known_woohoo_genders', '_known_exploring_sexuality')

    def __init__(self, rel_data):
        self._rel_data = rel_data
        self._known_traits = None
        self._knows_career = False
        self._known_stats = None
        self._knows_major = False
        self._knows_romantic_preference = False
        self._knows_woohoo_preference = False
        self._known_romantic_genders = None
        self._known_woohoo_genders = None
        self._known_exploring_sexuality = None

    def add_known_trait(self, trait, notify_client=True):
        return_value = False
        if trait.trait_type in TraitTracker.KNOWLEDGE_TRAIT_TYPES:
            if self._known_traits is None:
                self._known_traits = set()
            if trait not in self._known_traits:
                return_value = True
                self._known_traits.add(trait)
            if notify_client:
                self._rel_data.relationship.send_relationship_info()
        else:
            logger.error("Try to add trait of a type not allowed for knowledge {} to Sim {}'s knowledge about to Sim {}", trait, self._rel_data.sim_id_a, self._rel_data.sim_id_b)
        return return_value

    def remove_known_trait(self, trait, notify_client=True):
        if trait.trait_type in TraitTracker.KNOWLEDGE_TRAIT_TYPES and not self._known_traits is None:
            if trait not in self._known_traits:
                return
            self._known_traits.remove(trait)
            if notify_client:
                self._rel_data.relationship.send_relationship_info()
            else:
                logger.error("Try to remove trait of a type not allowed for knowledge {} from Sim {}'s knowledge about to Sim {}", trait, self._rel_data.sim_id_a, self._rel_data.sim_id_b)

    @property
    def known_traits(self):
        if self._known_traits is None:
            return ()
        return self._known_traits

    @property
    def knows_romantic_preference(self):
        return self._knows_romantic_preference

    @property
    def known_romantic_genders(self):
        if self._known_romantic_genders is None:
            return singletons.EMPTY_SET
        return self._known_romantic_genders

    @property
    def get_known_exploring_sexuality(self):
        return self._known_exploring_sexuality

    def add_knows_romantic_preference(self, notify_client=True):
        if self._knows_romantic_preference:
            return False
        target_sim_info = self._rel_data.find_target_sim_info()
        if target_sim_info is None:
            return False
        genders = set()
        for gender, trait_pair in GlobalGenderPreferenceTuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING.items():
            attracted_trait = trait_pair.is_attracted_trait
            if attracted_trait is None:
                logger.error('Missing romantic preference trait tuning for {} gender.', gender, owner='amwu')
                return False
                if target_sim_info.has_trait(attracted_trait):
                    genders.add(gender)

        self._knows_romantic_preference = True
        self._known_romantic_genders = frozenset(genders)
        self._known_exploring_sexuality = target_sim_info.is_exploring_sexuality
        if notify_client:
            self._rel_data.relationship.send_relationship_info()
        return True

    def remove_knows_romantic_preference(self, notify_client=True):
        if not self._knows_romantic_preference:
            return
        self._knows_romantic_preference = False
        self._known_romantic_genders = None
        self._known_exploring_sexuality = None
        if notify_client:
            self._rel_data.relationship.send_relationship_info()

    @property
    def knows_woohoo_preference(self):
        return self._knows_woohoo_preference

    @property
    def known_woohoo_genders(self):
        if self._known_woohoo_genders is None:
            return singletons.EMPTY_SET
        return self._known_woohoo_genders

    def add_knows_woohoo_preference(self, notify_client=True):
        if self._knows_woohoo_preference:
            return False
        target_sim_info = self._rel_data.find_target_sim_info()
        if target_sim_info is None:
            return False
        genders = set()
        for gender, trait_pair in GlobalGenderPreferenceTuning.WOOHOO_PREFERENCE_TRAITS_MAPPING.items():
            attracted_trait = trait_pair.is_attracted_trait
            if attracted_trait is None:
                logger.error('Missing woohoo preference trait tuning for {} gender.', gender, owner='amwu')
                return False
                if target_sim_info.has_trait(attracted_trait):
                    genders.add(gender)

        self._knows_woohoo_preference = True
        self._known_woohoo_genders = frozenset(genders)
        if notify_client:
            self._rel_data.relationship.send_relationship_info()
        return True

    def remove_knows_woohoo_preference(self, notify_client=True):
        if not self._knows_woohoo_preference:
            return
        self._knows_woohoo_preference = False
        self._known_woohoo_genders = None
        if notify_client:
            self._rel_data.relationship.send_relationship_info()

    @property
    def knows_career(self):
        return self._knows_career

    def add_knows_career(self, notify_client=True):
        return_value = not self._knows_career
        self._knows_career = True
        if notify_client:
            self._rel_data.relationship.send_relationship_info()
        return return_value

    def remove_knows_career(self, notify_client=True):
        self._knows_career = False
        if notify_client:
            self._rel_data.relationship.send_relationship_info()

    def get_known_careers(self):
        if self._knows_career:
            target_sim_info = self._rel_data.find_target_sim_info()
            if target_sim_info is not None:
                if target_sim_info.career_tracker.has_career:
                    careers = tuple((career for career in target_sim_info.careers.values() if career.is_visible_career if not career.is_course_slot))
                    if careers:
                        return careers
                if target_sim_info.career_tracker.retirement is not None:
                    return (
                     target_sim_info.career_tracker.retirement,)
                return (
                 CareerUnemployment(target_sim_info),)
        return ()

    def get_known_careertrack_ids(self):
        return (career_track.current_track_tuning.guid64 for career_track in self.get_known_careers())

    def add_known_stat(self, stat, notify_client=True):
        if self._known_stats is None:
            self._known_stats = set()
        self._known_stats.add(stat)
        if notify_client:
            self._rel_data.relationship.send_relationship_info()

    def get_known_stats(self):
        return self._known_stats

    @property
    def knows_major(self):
        return self._knows_major

    def add_knows_major(self, notify_client=True):
        return_value = not self._knows_major
        self._knows_major = True
        if notify_client:
            self._rel_data.relationship.send_relationship_info()
        return return_value

    def remove_knows_major(self, notify_client=True):
        self._knows_major = False
        if notify_client:
            self._rel_data.relationship.send_relationship_info()

    def get_known_major(self):
        if self._knows_major:
            target_sim_info = self._rel_data.find_target_sim_info()
            if target_sim_info is not None:
                if target_sim_info.degree_tracker:
                    return target_sim_info.degree_tracker.get_major()

    def get_known_major_career(self):
        if self._knows_major:
            target_sim_info = self._rel_data.find_target_sim_info()
            if target_sim_info is not None:
                if target_sim_info.career_tracker.has_career:
                    careers = tuple((career for career in target_sim_info.careers.values() if career.is_visible_career if career.is_course_slot))
                    if careers:
                        return careers
        return ()

    def get_save_data(self):
        save_data = protocols.SimKnowledge()
        for trait in self.known_traits:
            save_data.trait_ids.append(trait.guid64)

        save_data.knows_career = self._knows_career
        if self._known_stats is not None:
            for stat in self._known_stats:
                save_data.stats.append(stat.guid64)

        save_data.knows_major = self._knows_major
        save_data.knows_romantic_preference = self._knows_romantic_preference
        save_data.knows_woohoo_preference = self._knows_woohoo_preference
        if self._known_romantic_genders is not None:
            for gender in self._known_romantic_genders:
                save_data.known_romantic_genders.append(gender)

        if self._known_woohoo_genders is not None:
            for gender in self._known_woohoo_genders:
                save_data.known_woohoo_genders.append(gender)

        if self._known_exploring_sexuality is not None:
            save_data.known_exploring_sexuality = self._known_exploring_sexuality
        return save_data

    def load_knowledge(self, save_data):
        trait_manager = services.get_instance_manager(sims4.resources.Types.TRAIT)
        stat_manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        for trait_inst_id in save_data.trait_ids:
            trait = trait_manager.get(trait_inst_id)
            if trait is not None:
                if self._known_traits is None:
                    self._known_traits = set()
                self._known_traits.add(trait)

        for stat_id in save_data.stats:
            if self._known_stats is None:
                self._known_stats = set()
            stat = stat_manager.get(stat_id)
            if stat is not None:
                self._known_stats.add(stat)

        self._knows_career = save_data.knows_career
        if hasattr(save_data, 'knows_major'):
            self._knows_major = save_data.knows_major
        if hasattr(save_data, 'knows_romantic_preference'):
            self._knows_romantic_preference = save_data.knows_romantic_preference
        if hasattr(save_data, 'knows_woohoo_preference'):
            self._knows_woohoo_preference = save_data.knows_woohoo_preference
        if self._knows_romantic_preference:
            self._known_romantic_genders = frozenset(save_data.known_romantic_genders)
        if self._knows_woohoo_preference:
            self._known_woohoo_genders = frozenset(save_data.known_woohoo_genders)
        if hasattr(save_data, 'known_exploring_sexuality'):
            self._known_exploring_sexuality = save_data.known_exploring_sexuality