# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_types.py
# Compiled at: 2023-03-07 20:30:21
# Size of source mod 2**32: 9817 bytes
from _sims4_collections import frozendict
from routing.portals.portal_tuning import PortalFlags
from sims4.common import Pack
from sims4.tuning.tunable import TunableEnumEntry, TunableList
from tag import Tag
import enum

class Species(enum.Int):
    INVALID = 0
    HUMAN = 1
    DOG = 2
    CAT = 3
    FOX = 5


class SpeciesExtended(Species):
    SMALLDOG = 4

    @staticmethod
    def get_animation_species_param(value):
        if value == SpeciesExtended.HUMAN:
            return 'human'
        if value == SpeciesExtended.DOG:
            return 'dog'
        if value == SpeciesExtended.CAT:
            return 'cat'
        if value == SpeciesExtended.FOX:
            return 'fox'
        if value == SpeciesExtended.SMALLDOG:
            return 'smalldog'
        return ''

    @staticmethod
    def get_species_from_animation_param(species):
        return SpeciesExtended(species.upper())

    @staticmethod
    def get_species(value):
        if value == SpeciesExtended.SMALLDOG:
            return Species.DOG
        return value

    @staticmethod
    def get_species_extended(value):
        if value == Species.HUMAN:
            return (
             SpeciesExtended.HUMAN,)
        if value == Species.CAT:
            return (
             SpeciesExtended.CAT,)
        if value == Species.DOG:
            return (
             SpeciesExtended.DOG, SpeciesExtended.SMALLDOG)
        if value == Species.FOX:
            return (
             SpeciesExtended.FOX,)
        return (
         value,)

    @staticmethod
    def is_age_valid_for_animation_cache(species, age):
        if species == SpeciesExtended.HUMAN:
            return age in Age.get_ages_for_animation_cache()
        return age in (Age.CHILD, Age.ADULT)

    @staticmethod
    def get_portal_flag(value):
        if value == SpeciesExtended.HUMAN:
            return PortalFlags.SPECIES_HUMAN
        if value == SpeciesExtended.DOG:
            return PortalFlags.SPECIES_DOG
        if value == SpeciesExtended.CAT:
            return PortalFlags.SPECIES_CAT
        if value == SpeciesExtended.FOX:
            return PortalFlags.SPECIES_FOX
        if value == SpeciesExtended.SMALLDOG:
            return PortalFlags.SPECIES_SMALLDOG
        return PortalFlags.DEFAULT

    @staticmethod
    def get_required_pack(value):
        if value == SpeciesExtended.DOG or value == SpeciesExtended.SMALLDOG or value == SpeciesExtended.CAT:
            return Pack.EP04
        if value == SpeciesExtended.FOX:
            return Pack.EP11


class Gender(enum.Int):
    MALE = 4096
    FEMALE = 8192

    @property
    def animation_gender_param(self):
        return self.name.lower()

    @staticmethod
    def get_opposite(value):
        if value == Gender.MALE:
            return Gender.FEMALE
        return Gender.MALE


class Age(enum.Int):
    BABY = 1
    TODDLER = 2
    CHILD = 4
    TEEN = 8
    YOUNGADULT = 16
    ADULT = 32
    ELDER = 64
    INFANT = 128
    SEQUENTIAL_VALUE_MAP = frozendict({BABY: 0, 
     INFANT: 1, 
     TODDLER: 2, 
     CHILD: 3, 
     TEEN: 4, 
     YOUNGADULT: 5, 
     ADULT: 6, 
     ELDER: 7})

    def __lt__(self, other):
        return Age.SEQUENTIAL_VALUE_MAP.get(self, self) < Age.SEQUENTIAL_VALUE_MAP.get(other, other)

    def __gt__(self, other):
        return not self.__lt__(other) and self != other

    def __le__(self, other):
        return self.__lt__(other) or self == other

    def __ge__(self, other):
        return self.__gt__(other) or self == other

    def __hash__(self):
        return hash(self.value)

    @property
    def sequential_value(self):
        return Age.SEQUENTIAL_VALUE_MAP[self]

    @classmethod
    def get_ages_for_animation_cache(cls):
        return (
         cls.ADULT, cls.CHILD, cls.TODDLER)

    @property
    def age_for_animation_cache(self):
        if self <= self.TODDLER:
            return self.TODDLER
        if self <= self.CHILD:
            return self.CHILD
        return self.ADULT

    @property
    def animation_age_param(self):
        return self.name.lower()

    @staticmethod
    def get_age_from_animation_param(age):
        return Age(age.upper())

    @staticmethod
    def get_portal_flag(value):
        if value == Age.TODDLER:
            return PortalFlags.AGE_TODDLER
        if value == Age.CHILD:
            return PortalFlags.AGE_CHILD
        if value == Age.INFANT:
            return PortalFlags.AGE_INFANT
        if value in (Age.TEEN, Age.YOUNGADULT, Age.ADULT, Age.ELDER):
            return PortalFlags.AGE_TYAE
        return PortalFlags.DEFAULT


class SimInfoSpawnerTags:
    SIM_SPAWNER_TAGS = TunableList(description='\n        A list of tags for Sims to spawn when traveling and moving on/off lot.\n        Note: Tags are resolved in order until a spawn point has been found that\n        contains the tag.\n        ',
      tunable=TunableEnumEntry(tunable_type=Tag,
      default=(Tag.INVALID)))


class SimSerializationOption(enum.Int, export=False):
    UNDECLARED = 0
    LOT = 1
    OPEN_STREETS = 2


class SimZoneSpinUpAction(enum.Int, export=False):
    NONE = ...
    RESTORE_SI = ...
    PREROLL = ...
    PUSH_GO_HOME = ...