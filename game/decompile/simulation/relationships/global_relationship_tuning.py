# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\global_relationship_tuning.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 9587 bytes
from relationships.relationship_enums import RelationshipType
from sims4.tuning.tunable import TunableReference, TunablePackSafeReference, Tunable, TunableEnumEntry, TunableList, TunableMapping, TunableSet, TunableTuple
from sims4.tuning.tunable_base import ExportModes, EnumBinaryExportType
import services, sims4.resources

class RelationshipGlobalTuning:
    REL_INSPECTOR_TRACK = TunableReference(description='\n        This is the track that the rel inspector follows.  Any bits that are\n        apart of this track should NOT be marked visible unless you want them\n        showing up in both places.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions='RelationshipTrack')
    DEFAULT_PET_TO_SIM_TRACK = TunablePackSafeReference(description='\n        This is the default relationship track for pet to sim relationships\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions='RelationshipTrack')
    CAREGIVER_RELATIONSHIP_BIT = TunableReference(description='\n        The relationship bit between a Sim and their caregiver, e.g. between a\n        parent and a toddler.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    HAS_MET_RELATIONSHIP_BIT = TunableReference(description='\n        The relationship bit between two Sims that have met each other.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    NEIGHBOR_RELATIONSHIP_BIT = TunableReference(description='\n        The relationship bit automatically applied to sims who live on the same\n        street but in difference households.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    NEIGHBOR_GIVEN_KEY_RELATIONSHIP_BIT = TunablePackSafeReference(description="\n        The relationship bit that signifies if you've given a key to someone.\n        ",
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    MIN_RELATIONSHIP_VALUE = Tunable(description='\n        The minimum value any relationship can be.\n        ',
      tunable_type=float,
      default=100)
    MAX_RELATIONSHIP_VALUE = Tunable(description='\n        The maximum value any relationship can be.\n        ',
      tunable_type=float,
      default=100)
    DEFAULT_RELATIONSHIP_VALUE = Tunable(description='\n        The default value for relationship track scores.\n        ',
      tunable_type=float,
      default=0)
    DEFAULT_SHORT_TERM_CONTEXT_TRACK = TunableReference(description='\n        If no short-term context tracks exist for a relationship, use this\n        default as the prevailing track.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
      class_restrictions=('ShortTermContextRelationshipTrack', ))
    DELAY_UNTIL_RELATIONSHIP_IS_CULLED = Tunable(description='\n        The amount of time, in sim minutes, that it takes before \n        a relationship is culled once all of the tracks have reached\n        convergence.\n        ',
      tunable_type=int,
      default=10)
    ENGAGEMENT_RELATIONSHIP_BIT = TunableReference(description='\n        The relationship bit between two Sims who have been engaged.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    MARRIAGE_RELATIONSHIP_BIT = TunableReference(description="\n        The marriage relationship bit. This tuning references the relationship bit signifying that \n        the sim is a spouse to someone. Whenever this bit is added to a sim's relationship, it has \n        the side effect of updating the spouse_sim_id on a sim's relationship tracker. If the bit \n        goes away, the field is cleared. \n        ",
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    SIGNIFICANT_OTHER_RELATIONSHIP_BITS = TunableList(description='\n        A list of relationship bits that mark the relationship as being between\n        significant others.  Only one of these bits is required for the sims to\n        be considered significant others.\n        ',
      tunable=TunableReference(description='\n            A relationship bit that signifies that a sim is a significant other\n            to someone else.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))))
    FEUD_TARGET = TunablePackSafeReference(description='\n        A reference to the bit a Sim has with a Sim they are Feuding with.\n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))
    MEANINGFUL_RELATIONSHIP_BITS = TunableSet(description='\n        A set of relationship bits that represent a meaningful relationship.\n        ',
      tunable=TunableReference(description='\n            A relationship bit that signifies that this is a meaningful relationship.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))))
    WORKPLACE_RIVAL_RELATIONSHIP_BIT = TunablePackSafeReference(description='\n        A reference to the bit a Sim has with another Sim who is in the same career to make them rivals. \n        ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)))


@staticmethod
def mark_trope_bits(_instance_class, _tunable_name, _source, value):
    for trope_bit in value:
        trope_bit.is_trope_bit = True


class TropeGlobalTuning:
    TROPES = TunableSet(description='\n        A set of relationship bits that represent family dynamics tropes.\n        ',
      tunable=TunableReference(description='\n            A relationship bit that represents a family dynamics trope.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
      pack_safe=True),
      export_modes=(ExportModes.ClientBinary),
      callback=mark_trope_bits)
    RELATIONSHIP_TYPE_TO_BIT = TunableMapping(description='\n        A mapping of relationship type to relationship bit.\n        ',
      key_name='RelationshipType',
      key_type=TunableEnumEntry(tunable_type=RelationshipType,
      default=(RelationshipType.NONE),
      binary_type=(EnumBinaryExportType.EnumUint32)),
      value_name='RelationshipBit',
      value_type=TunablePackSafeReference(description='\n            A relationship bit that maps to the specified relationship type.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT))),
      tuple_name='RelationshipTypeToBit',
      export_modes=(ExportModes.ClientBinary))
    RELATIONSHIP_TYPE_TO_AVAILABLE_TROPES = TunableMapping(description='\n        A mapping of relationship type to all tropes available for that relationship type.\n        ',
      key_name='RelationshipType',
      key_type=TunableEnumEntry(tunable_type=RelationshipType,
      default=(RelationshipType.NONE),
      binary_type=(EnumBinaryExportType.EnumUint32)),
      value_name='AvailableTropes',
      value_type=TunableList(description='\n            A list of Tropes that are available to a Sim with this Relationship Type.\n            ',
      tunable=TunableReference(description='\n                The Trope that is available to a Sim with this Relationship Type.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
      pack_safe=True)),
      tuple_name='RelationshipTypeToAvailableTropes',
      export_modes=(ExportModes.ClientBinary))
    RECIPROCAL_TROPES = TunableList(description='\n        A list of tuples that contain reciprocal unidirectional tropes, used by Client to correctly assign tropes to\n        Sims in CAS.\n        ',
      tunable=TunableTuple(description='\n            A tuple of reciprocal tropes.\n            ',
      authority_trope=TunableReference(description='\n                The authority trope that should be reciprocated.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
      pack_safe=True),
      subordinate_trope=TunableReference(description='\n                The subordinate trope that should be reciprocated.\n                ',
      manager=(services.get_instance_manager(sims4.resources.Types.RELATIONSHIP_BIT)),
      pack_safe=True),
      export_class_name='ReciprocalTropes'),
      export_modes=(ExportModes.ClientBinary))