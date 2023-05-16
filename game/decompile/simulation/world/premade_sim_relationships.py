# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\world\premade_sim_relationships.py
# Compiled at: 2020-08-19 14:58:15
# Size of source mod 2**32: 4800 bytes
from _collections import defaultdict
from event_testing.resolver import DoubleSimResolver
from filters.sim_template import SimTemplateType
from interactions.utils.loot import LootActions
from sims4.tuning.tunable import TunableTuple, TunableList
from world.premade_sim_template import PremadeSimTemplate
import services, sims4.log
logger = sims4.log.Logger('PremadeSimRelationships', default_owner='tingyul')

class PremadeSimRelationships:

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        pairs = set()
        for entry in value:
            a = entry.sim_a
            b = entry.sim_b
            if a is None:
                if b is not None:
                    logger.error('Premade Sim has rel with a Sim in unloaded pack. a: {}', a.__name__)
                    continue
            if b is None:
                if a is not None:
                    logger.error('Premade Sim has rel with a Sim in unloaded pack. b: {}', b.__name__)
                    continue
                if entry.relationship_loot is None:
                    logger.error('Premade Sims have relationship loot in unloaded pack. a: {}, b: {}', a.__name__, b.__name__)
                    continue
                if a is b:
                    logger.error('Premade Sim has rel with himself/herself. a: {}, b: {}', a.__name__, b.__name__)
                    continue
                key = (
                 a.guid64, b.guid64)
                if key in pairs:
                    logger.error('Multiple rel tuning between preamde Sims. a: {}, b: {}', a.__name__, b.__name__)
                pairs.add(key)

    RELATIONSHIP_MAP = TunableList(description='\n        Relationship to give between premade Sims in different households.\n        ',
      tunable=TunableTuple(description='\n            Two Sims and a loot. The two Sims must be in different premade\n            households, and there can only be one entry per pair of Sims.\n            ',
      sim_a=PremadeSimTemplate.TunablePackSafeReference(description='\n                Relationship Loot uses this Sim as Actor.\n                '),
      sim_b=PremadeSimTemplate.TunablePackSafeReference(description='\n                Relationship Loot uses this Sim as TargetSim.\n                '),
      relationship_loot=LootActions.TunablePackSafeReference(description='\n                Loot that contains relationship to add between the two Sims.\n                Sim A is Actor and Sim B is TargetSim.\n                ')),
      verify_tunable_callback=_verify_tunable_callback)

    @classmethod
    def apply_relationships(cls, premade_sim_infos):
        loot_matrix = defaultdict(dict)
        for entry in PremadeSimRelationships.RELATIONSHIP_MAP:
            if not entry.sim_a is None:
                if entry.sim_b is None:
                    continue
                loot_matrix[entry.sim_a][entry.sim_b] = entry.relationship_loot

        for premade_sim_template, sim_info in premade_sim_infos.items():
            if premade_sim_template not in loot_matrix:
                continue
            for other_template, rel_loot in loot_matrix[premade_sim_template].items():
                if other_template not in premade_sim_infos:
                    continue
                other_sim_info = premade_sim_infos[other_template]
                resolver = DoubleSimResolver(sim_info, other_sim_info)
                rel_loot.apply_to_resolver(resolver)