# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\filters\sim_template.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 48929 bytes
import random
from cas.cas import BaseSimInfo
from sims.global_gender_preference_tuning import AttractionStatus, SexualityStatus
from sims.outfits.outfit_enums import OutfitFilterFlag, BodyType, MatchNotFoundPolicy
from sims.sim_info_base_wrapper import SimInfoBaseWrapper
from sims.sim_info_types import Age, Gender, Species, SpeciesExtended
from sims.sim_spawner_enums import SimNameType
from sims.university.university_tuning import University
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import TunedInstanceMetaclass
from sims4.tuning.tunable import TunableEnumEntry, TunableList, TunableTuple, Tunable, TunableReference, TunableSet, HasTunableReference, OptionalTunable, TunableResourceKey, TunableFactory, TunableInterval, AutoFactoryInit, HasTunableSingletonFactory, TunableVariant, TunablePackSafeReference, TunableRange, TunableEnumFlags, TunableMapping, TunablePercent
from sims4.utils import classproperty
from tag import TunableTag
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList
import enum, services, sims.sim_spawner, sims4.log, sims4.resources, statistics.skill, tag
logger = sims4.log.Logger('SimTemplate')

class SimTemplateType(enum.Int, export=False):
    SIM = 1
    HOUSEHOLD = 2
    PREMADE_SIM = 3
    PREMADE_HOUSEHOLD = 4


class TunableTagSet(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TAG_SET)):
    INSTANCE_TUNABLES = {'tags': TunableSet(TunableEnumEntry((tag.Tag), (tag.Tag.INVALID), description='A specific tag.'))}


class TunableWeightedTagList(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TAG_SET)):
    INSTANCE_TUNABLES = {'weighted_tags': TunableList(description='\n            A list of weighted tags.\n            ',
                        tunable=TunableTuple(description='\n                A tag and the weight associated with it.\n                ',
                        tag=(TunableTag()),
                        weight=TunableRange(tunable_type=float, default=1, minimum=0)))}


class SkillRange(HasTunableSingletonFactory):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        ideal_value = value.ideal_value
        if int(ideal_value) <= value._min_value or int(ideal_value) >= value._max_value:
            logger.error('Ideal value of {} in FilterRange is not within the bounds of {} - {} (inclusive).', ideal_value, (value.min_value), (value.max_value), owner='rez')

    FACTORY_TUNABLES = {'min_value':Tunable(description='\n            The minimum possible skill.\n            ',
       tunable_type=int,
       default=0), 
     'max_value':Tunable(description='\n            The maximum possible skill.\n            ',
       tunable_type=int,
       default=10), 
     'ideal_value':Tunable(description='\n            The ideal value for this skill. If outside of min/max, will be ignored\n            ',
       tunable_type=int,
       default=5), 
     'verify_tunable_callback':_verify_tunable_callback}

    def __init__(self, min_value, max_value, ideal_value):
        self._min_value = int(min_value) - 1
        self._max_value = int(max_value) + 1
        if int(ideal_value) <= self._min_value or int(ideal_value) >= self._max_value:
            logger.error('Ideal value of {} in FilterRange is not within the bounds of {} - {} (inclusive).', ideal_value, min_value, max_value, owner='rez')
        self._ideal_value = int(ideal_value)

    @property
    def min_value(self):
        return self._min_value + 1

    @property
    def max_value(self):
        return self._max_value - 1

    @property
    def ideal_value(self):
        return self._ideal_value

    def get_score(self, value):
        score = 0
        if value < self.ideal_value:
            score = (value - self.min_value) / (self.ideal_value - self.min_value)
        else:
            score = (self.max_value - value) / (self.max_value - self.ideal_value)
        return max(0, min(1, score))

    def random_value(self):
        if self.max_value == self.min_value:
            return self.max_value
        if self._ideal_value < self.min_value or self._ideal_value > self.max_value:
            return random.randint(self.min_value, self.max_value)
        return round(random.triangular(self.min_value, self.max_value, self._ideal_value))


class LiteralAge(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'literal_age': TunableEnumEntry(description="\n            The Sim's age.\n            ",
                      tunable_type=Age,
                      default=(Age.ADULT))}

    def get_age_range(self):
        return (
         self.literal_age, self.literal_age)

    def get_age(self):
        return self.literal_age


class RandomAge(HasTunableSingletonFactory, AutoFactoryInit):

    @staticmethod
    def _verify_tunable_callback(instance_class, tunable_name, source, value):
        if value.min_age > value.max_age:
            logger.error('Tuning error for {}: Min age is greater than max age', instance_class)

    FACTORY_TUNABLES = {'min_age':TunableEnumEntry(description='\n            The minimum age for creation.\n            ',
       tunable_type=Age,
       default=Age.ADULT), 
     'max_age':TunableEnumEntry(description='\n            The maximum Age for creation\n            ',
       tunable_type=Age,
       default=Age.ADULT), 
     'verify_tunable_callback':_verify_tunable_callback}

    def get_age_range(self):
        return (
         self.min_age, self.max_age)

    def get_age(self):
        age_range = [age for age in Age if self.min_age <= age <= self.max_age]
        return random.choice(age_range)


class TunableSimCreator(TunableFactory):

    @staticmethod
    def factory(age_variant=None, full_name=None, **kwargs):
        full_name_key = 0
        first_name_key = 0
        last_name_key = 0
        sim_name_type = SimNameType.DEFAULT
        if isinstance(full_name, SimNameType):
            sim_name_type = full_name
        else:
            if full_name is not None:
                if hasattr(full_name, 'first_name'):
                    first_name_key = full_name.first_name.hash
                    last_name_key = full_name.last_name.hash if full_name.last_name is not None else 0
                else:
                    full_name_key = full_name.hash
        age_of_sim = age_variant.get_age() if age_variant is not None else Age.ADULT
        return (sims.sim_spawner.SimCreator)(**, **kwargs)

    FACTORY_TYPE = factory

    def __init__(self, **kwargs):
        (super().__init__)(gender=TunableEnumEntry(description="\n                The Sim's gender.\n                ",
  tunable_type=Gender,
  default=None), 
         species=TunableEnumEntry(description="\n                The Sim's species.\n                ",
  tunable_type=SpeciesExtended,
  default=(SpeciesExtended.HUMAN),
  invalid_enums=(
 SpeciesExtended.INVALID,)), 
         age_variant=TunableVariant(description="\n                The sim's age for creation. Can be a literal age or random\n                between two ages.\n                ",
  literal=(LiteralAge.TunableFactory()),
  random=(RandomAge.TunableFactory())), 
         resource_key=OptionalTunable(description='\n                If enabled, the Sim will be created using a saved SimInfo file.\n                ',
  tunable=TunableResourceKey(description='\n                    The SimInfo file to use.\n                    ',
  default=None,
  resource_types=(
 sims4.resources.Types.SIMINFO,))), 
         full_name=TunableVariant(description='\n                If specified, then defines how the Sims name will be determined.\n                ',
  enabled=TunableLocalizedString(description="\n                    The Sim's name will be determined by this localized string. \n                    Their first, last and full name will all be set to this.                \n                    "),
  name_type=TunableEnumEntry(description='\n                    The sim name type to use when generating the Sims name\n                    randomly.\n                    ',
  tunable_type=SimNameType,
  default=(SimNameType.DEFAULT)),
  first_and_last_name=TunableTuple(description="\n                    The Sim's name will be determined by the specified localized strings. \n                    This is useful when regenerating a pre-made sim.\n                    ",
  first_name=TunableLocalizedString(description="\n                        The Sim's first name.\n                        "),
  last_name=OptionalTunable(description="\n                        Optionally set the Sim's last name.\n                        ",
  tunable=(TunableLocalizedString()),
  enabled_by_default=True,
  enabled_name='specify_last_name',
  disabled_name='no_last_name')),
  locked_args={'disabled': None},
  default='disabled'), 
         tunable_tag_set=TunableReference(description='\n                The set of tags that this template uses for CAS creation.\n                ',
  manager=(services.get_instance_manager(sims4.resources.Types.TAG_SET)),
  allow_none=True,
  class_restrictions=('TunableTagSet', )), 
         weighted_tag_lists=TunableList(description='\n                A list of weighted tag lists. Each weighted tag list adds\n                a single tag to the set of tags to use for Sim creation.\n                ',
  tunable=TunableReference(description='\n                    A weighted tag list. A single tag is added to the set of\n                    tags for Sim creation from this list based on the weights.\n                    ',
  manager=(services.get_instance_manager(sims4.resources.Types.TAG_SET)),
  class_restrictions=('TunableWeightedTagList', ))), 
         filter_flag=TunableEnumFlags(description='\n                Define how to handle part randomization for the generated outfit.\n                ',
  enum_type=OutfitFilterFlag,
  default=(OutfitFilterFlag.USE_EXISTING_IF_APPROPRIATE | OutfitFilterFlag.USE_VALID_FOR_LIVE_RANDOM),
  allow_no_flags=True), 
         body_type_chance_overrides=TunableMapping(description='\n                Define body type chance overrides for the generate outfit. For\n                example, if BODYTYPE_HAT is mapped to 100%, then the outfit is\n                guaranteed to have a hat if any hat matches the specified tags.\n                ',
  key_type=BodyType,
  value_type=TunablePercent(description='\n                    The chance that a part is applied to the corresponding body\n                    type.\n                    ',
  default=100)), 
         body_type_match_not_found_policy=TunableMapping(description='\n                The policy we should take for a body type that we fail to find a\n                match for. Primary example is to use MATCH_NOT_FOUND_KEEP_EXISTING\n                for generating a tshirt and making sure a sim wearing full body has\n                a lower body cas part.\n                ',
  key_type=BodyType,
  value_type=MatchNotFoundPolicy), **kwargs)


class TunableSimTemplate(HasTunableReference, metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SIM_TEMPLATE)):
    INSTANCE_TUNABLES = {'_sim_creation_info':TunableSimCreator(description='\n            The sim creation info that is passed into CAS in order to create the\n            sim.\n            '), 
     '_skills':TunableTuple(description='\n            Skill that will be added to created sim.\n            ',
       explicit=TunableList(description='\n                Skill that will be added to sim\n                ',
       tunable=TunableTuple(skill=statistics.skill.Skill.TunableReference(description='\n                        The skill that will be added.\n                        ',
       pack_safe=True),
       range=SkillRange.TunableFactory(description='\n                        The possible skill range for a skill that will be added\n                        to the generated sim.\n                        '))),
       random=OptionalTunable(description='\n                Enable if you want random amount of skills to be added to sim.\n                ',
       tunable=TunableTuple(interval=TunableInterval(description='\n                        Additional random number skills to be added from the\n                        random list.\n                        ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0),
       choices=TunableList(description='\n                        A list of skills that will be chose for random update.\n                        ',
       tunable=TunableTuple(skill=statistics.skill.Skill.TunableReference(description='\n                                The skill that will be added. If left blank a\n                                random skill will be chosen that is not in the\n                                blacklist.\n                                ',
       pack_safe=True),
       range=SkillRange.TunableFactory(description='\n                                The possible skill range for a skill that will\n                                be added to the generated sim.\n                                ')))),
       disabled_name='no_extra_random',
       enabled_name='additional_random'),
       blacklist=TunableSet(description='\n                A list of skills that that will not be chosen if looking to set\n                a random skill.\n                ',
       tunable=(statistics.skill.Skill.TunableReference()))), 
     '_traits':TunableTuple(description='\n            Traits that will be added to the generated template.\n            ',
       explicit=TunableList(description='\n                A trait that will always be added to sim.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True)),
       num_random=OptionalTunable(description='\n                If enabled a random number of personality traits that will be\n                added to generated sim.\n                ',
       tunable=TunableInterval(tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0)),
       blacklist=TunableSet(description='\n                A list of traits that will not be considered when giving random\n                skills.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.TRAIT)),
       pack_safe=True))), 
     '_ranks':TunableList(description='\n            The ranked statistics that we want to set on the Sim.\n            ',
       tunable=TunableTuple(ranked_statistic=TunablePackSafeReference(description='\n                    The ranked statistic that we are going to set.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC)),
       class_restrictions=('RankedStatistic', )),
       rank=Tunable(description='\n                    The rank value for this filter.\n                    ',
       tunable_type=int,
       default=1))), 
     '_perks':TunableTuple(description='\n            Perks that will be added to the generated template.\n            ',
       explicit=TunableList(description='\n                A perk that will always be added to sim.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)))),
       num_random=OptionalTunable(description='\n                If enabled, we want random amount of perks to be added to sim.\n                ',
       tunable=TunableInterval(tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0)),
       whiteblacklist=TunableWhiteBlackList(description='\n                Pass if perk is in one of the perks in the whitelist, or \n                fail if it is any of the perks in the blacklist.\n                ',
       tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.BUCKS_PERK)),
       pack_safe=True))), 
     '_major':OptionalTunable(description='\n            When enabled allows you to specify a major and university to enroll\n            the Sim into.\n            ',
       tunable=TunableTuple(description='\n                The degree that will be added to the generated Sim.\n                ',
       university=OptionalTunable(description='\n                    When enabled allows you to specify which university the Sim \n                    should be attending. When not enabled a random university will\n                    be assigned.\n                    ',
       tunable=TunableReference(description='\n                        The university to assign the Sim to when enrolling in a \n                        degree\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.UNIVERSITY)),
       pack_safe=True),
       disabled_name='Random',
       enabled_name='Specific'),
       major=OptionalTunable(description='\n                    When enabled allows you to specify which major the Sim will be\n                    enrolled in. When not enabled a random major will be chosen.\n                    ',
       tunable=TunableReference(description='\n                        The degree to enroll the Sim into.\n                        ',
       manager=(services.get_instance_manager(sims4.resources.Types.UNIVERSITY_MAJOR))),
       disabled_name='Random',
       enabled_name='Specific'),
       num_courses_to_enroll_in=TunableRange(description='\n                    The amount of courses to enroll in for the chosen major. \n                    ',
       tunable_type=int,
       minimum=1,
       default=1),
       random_credits_in_range=TunableInterval(description='\n                    The range of random values to be added to the credit count.\n                    ',
       tunable_type=int,
       default_upper=1,
       default_lower=0,
       minimum=0,
       maximum=12))), 
     '_fixups':TunableList(description='\n            Sim info fixups that will be added to the generated sim.\n            ',
       tunable=TunablePackSafeReference(manager=(services.get_instance_manager(sims4.resources.Types.SIM_INFO_FIXUP))))}

    @classmethod
    def _verify_tuning_callback(cls):
        for trait in cls._traits.explicit:
            if trait is not None and trait in cls._traits.blacklist:
                logger.error('SimTemplate: {} - explicit trait ({}) in blacklist.Either update explicit list or remove from blacklist', (cls.__name__),
                  (trait.__name__),
                  owner='designer')

        for perk in cls._perks.explicit:
            if perk is not None:
                cls._perks.whiteblacklist.test_item(perk) or logger.error('SimTemplate: {} - explicit perk ({}) failed to meetwhitelist/blacklist requirements.Either update explicit list or whitelist/blacklist', (cls.__name__),
                  (perk.__name__),
                  owner='designer')

        for skill_data in cls._skills.explicit:
            if skill_data.skill is not None and skill_data.skill in cls._skills.blacklist:
                logger.error('SimTemplate: {} - in explicit skill ({}) in blacklist.Either update explicit list or remove from blacklist', (cls.__name__),
                  (skill_data.skill.__name__),
                  owner='designer')

        if cls._skills.random:
            random_skill_available = any((skill_data.skill is None for skill_data in cls._skills.random.choices))
            if not random_skill_available:
                if len(cls._skills.random.choices) < cls._skills.random.interval.upper_bound:
                    logger.error('SimTemplate: {} - There is not enough entries {} in the random choices to support the upper bound {} of the random amount to add.\n  Possible Fixes:\n    Add a random option into the random->choices \n    Add more options in random->choices\n    or decrease upper bound of random amount.', (cls.__name__),
                      (len(cls._skills.random.choices)),
                      (cls._skills.random.interval.upper_bound),
                      owner='designer')
            for skill_data in cls._skills.random.choices:
                if skill_data.skill is not None and skill_data.skill in cls._skills.blacklist:
                    logger.error('SimTemplate: {} - in random choices skill {} in blacklist.Either update explicit list or remove from blacklist', (cls.__name__),
                      (skill_data.skill),
                      owner='designer')

    @classproperty
    def template_type(cls):
        return SimTemplateType.SIM

    @classproperty
    def sim_creator(cls):
        return cls._sim_creation_info()

    @classmethod
    def _get_sim_info_resource_data(cls, resource_key):
        sim_info = SimInfoBaseWrapper()
        sim_info.load_from_resource(resource_key)
        return {'age_range':(
          sim_info.age, sim_info.age), 
         'gender':sim_info.gender, 
         'species':sim_info.species}

    @classmethod
    def _get_sim_info_creation_data(cls):
        if cls._sim_creation_info.resource_key is not None:
            return cls._get_sim_info_resource_data(cls._sim_creation_info.resource_key)
        return {'age_range':cls._sim_creation_info.age_variant.get_age_range() if cls._sim_creation_info.age_variant is not None else None, 
         'gender':cls._sim_creation_info.gender, 
         'species':cls._sim_creation_info.species}

    @classmethod
    def can_validate_age(cls):
        if cls._sim_creation_info.resource_key is not None:
            if BaseSimInfo is None:
                return False
        return True

    @classmethod
    def matches_creation_data(cls, sim_creator=None, age_min=None):
        sim_info_data = cls._get_sim_info_creation_data()
        if sim_creator is not None:
            if sim_info_data['age_range'] is not None:
                data_age_min, data_age_max = sim_info_data['age_range']
                if not sim_creator.age < data_age_min:
                    if sim_creator.age > data_age_max:
                        return False
            else:
                if sim_info_data['gender'] is not None:
                    if sim_info_data['gender'] != sim_creator.gender:
                        return False
                if sim_info_data['species'] is not None and sim_info_data['species'] != sim_creator.species:
                    return False
        if age_min is not None:
            if sim_info_data['age_range'] is not None:
                data_age_min, data_age_max = sim_info_data['age_range']
                if data_age_min < age_min:
                    return False
        return True

    @classmethod
    def add_template_data_to_sim(cls, sim_info, sim_creator=None):
        cls._add_skills(sim_info)
        cls._add_traits(sim_info, sim_creator)
        cls.add_rank(sim_info, sim_creator)
        cls.add_perks(sim_info, sim_creator)
        cls._add_gender_preference(sim_info)
        cls._enroll_in_university(sim_info, sim_creator)
        cls._add_sim_info_fixups(sim_info, sim_creator)
        sim_info.sim_template_id = cls.guid64
        sim_info.premade_sim_fixup_completed = True

    @classmethod
    def _add_skills(cls, sim_info):
        if not cls._skills.explicit:
            if not cls._skills.random:
                return
        statistic_manager = manager = services.get_instance_manager(sims4.resources.Types.STATISTIC)
        available_skills_types = list(set([stat for stat in statistic_manager.types.values() if stat.is_skill]) - cls._skills.blacklist)
        for skill_data in cls._skills.explicit:
            cls._add_skill_type(sim_info, skill_data, available_skills_types)

        if cls._skills.random:
            num_to_add = cls._skills.random.interval.random_int()
            available_random_skill_data = list(cls._skills.random.choices)
            while num_to_add > 0 and available_random_skill_data and available_skills_types:
                random_skill_data = random.choice(available_random_skill_data)
                if random_skill_data.skill is not None:
                    available_random_skill_data.remove(random_skill_data)
                if cls._add_skill_type(sim_info, random_skill_data, available_skills_types):
                    num_to_add -= 1

    @classmethod
    def _add_skill_type(cls, sim_info, skill_data, available_skills_types):
        skill_type = skill_data.skill
        if skill_type is None:
            skill_type = random.choice(available_skills_types)
        if skill_type is not None:
            if skill_type in available_skills_types:
                available_skills_types.remove(skill_type)
            if skill_type.can_add(sim_info):
                skill_value = skill_type.convert_from_user_value(skill_data.range.random_value())
                sim_info.add_statistic(skill_type, skill_value)
                return True
        return False

    @classmethod
    def _add_traits--- This code section failed: ---

 L. 812         0  LOAD_DEREF               'sim_info'
                2  LOAD_ATTR                trait_tracker
                4  STORE_FAST               'trait_tracker'

 L. 815         6  SETUP_LOOP           36  'to 36'
                8  LOAD_GLOBAL              tuple
               10  LOAD_FAST                'trait_tracker'
               12  LOAD_ATTR                personality_traits
               14  CALL_FUNCTION_1       1  '1 positional argument'
               16  GET_ITER         
               18  FOR_ITER             34  'to 34'
               20  STORE_FAST               'trait'

 L. 816        22  LOAD_DEREF               'sim_info'
               24  LOAD_METHOD              remove_trait
               26  LOAD_FAST                'trait'
               28  CALL_METHOD_1         1  '1 positional argument'
               30  POP_TOP          
               32  JUMP_BACK            18  'to 18'
               34  POP_BLOCK        
             36_0  COME_FROM_LOOP        6  '6'

 L. 818        36  LOAD_FAST                'sim_creator'
               38  LOAD_CONST               None
               40  COMPARE_OP               is-not
               42  POP_JUMP_IF_FALSE    70  'to 70'

 L. 819        44  SETUP_LOOP           70  'to 70'
               46  LOAD_FAST                'sim_creator'
               48  LOAD_ATTR                traits
               50  GET_ITER         
               52  FOR_ITER             68  'to 68'
               54  STORE_FAST               'trait'

 L. 820        56  LOAD_DEREF               'sim_info'
               58  LOAD_METHOD              add_trait
               60  LOAD_FAST                'trait'
               62  CALL_METHOD_1         1  '1 positional argument'
               64  POP_TOP          
               66  JUMP_BACK            52  'to 52'
               68  POP_BLOCK        
             70_0  COME_FROM_LOOP       44  '44'
             70_1  COME_FROM            42  '42'

 L. 823        70  SETUP_LOOP           98  'to 98'
               72  LOAD_FAST                'cls'
               74  LOAD_ATTR                _traits
               76  LOAD_ATTR                explicit
               78  GET_ITER         
               80  FOR_ITER             96  'to 96'
               82  STORE_FAST               'trait'

 L. 824        84  LOAD_DEREF               'sim_info'
               86  LOAD_METHOD              add_trait
               88  LOAD_FAST                'trait'
               90  CALL_METHOD_1         1  '1 positional argument'
               92  POP_TOP          
               94  JUMP_BACK            80  'to 80'
               96  POP_BLOCK        
             98_0  COME_FROM_LOOP       70  '70'

 L. 826        98  LOAD_FAST                'cls'
              100  LOAD_ATTR                _traits
              102  LOAD_ATTR                num_random
          104_106  POP_JUMP_IF_FALSE   280  'to 280'

 L. 827       108  LOAD_FAST                'cls'
              110  LOAD_ATTR                _traits
              112  LOAD_ATTR                num_random
              114  LOAD_METHOD              random_int
              116  CALL_METHOD_0         0  '0 positional arguments'
              118  STORE_FAST               'num_to_add'

 L. 828       120  LOAD_FAST                'num_to_add'
              122  LOAD_CONST               0
              124  COMPARE_OP               >
          126_128  POP_JUMP_IF_FALSE   280  'to 280'

 L. 830       130  LOAD_GLOBAL              services
              132  LOAD_METHOD              get_instance_manager
              134  LOAD_GLOBAL              sims4
              136  LOAD_ATTR                resources
              138  LOAD_ATTR                Types
              140  LOAD_ATTR                TRAIT
              142  CALL_METHOD_1         1  '1 positional argument'
              144  STORE_FAST               'trait_manager'

 L. 831       146  LOAD_CLOSURE             'sim_info'
              148  BUILD_TUPLE_1         1 
              150  LOAD_SETCOMP             '<code_object <setcomp>>'
              152  LOAD_STR                 'TunableSimTemplate._add_traits.<locals>.<setcomp>'
              154  MAKE_FUNCTION_8          'closure'
              156  LOAD_FAST                'trait_manager'
              158  LOAD_ATTR                types
              160  LOAD_METHOD              values
              162  CALL_METHOD_0         0  '0 positional arguments'
              164  GET_ITER         
              166  CALL_FUNCTION_1       1  '1 positional argument'
              168  STORE_FAST               'available_trait_types'

 L. 835       170  LOAD_FAST                'available_trait_types'
              172  LOAD_FAST                'cls'
              174  LOAD_ATTR                _traits
              176  LOAD_ATTR                blacklist
              178  INPLACE_SUBTRACT 
              180  STORE_FAST               'available_trait_types'

 L. 836       182  LOAD_FAST                'available_trait_types'
              184  LOAD_GLOBAL              set
              186  LOAD_FAST                'cls'
              188  LOAD_ATTR                _traits
              190  LOAD_ATTR                explicit
              192  CALL_FUNCTION_1       1  '1 positional argument'
              194  INPLACE_SUBTRACT 
              196  STORE_FAST               'available_trait_types'

 L. 838       198  LOAD_GLOBAL              list
              200  LOAD_FAST                'available_trait_types'
              202  CALL_FUNCTION_1       1  '1 positional argument'
              204  STORE_FAST               'available_trait_types'

 L. 839       206  SETUP_LOOP          280  'to 280'
              208  LOAD_FAST                'num_to_add'
              210  LOAD_CONST               0
              212  COMPARE_OP               >
          214_216  POP_JUMP_IF_FALSE   278  'to 278'
              218  LOAD_FAST                'available_trait_types'
          220_222  POP_JUMP_IF_FALSE   278  'to 278'

 L. 841       224  LOAD_GLOBAL              random
              226  LOAD_METHOD              choice
              228  LOAD_FAST                'available_trait_types'
              230  CALL_METHOD_1         1  '1 positional argument'
              232  STORE_FAST               'trait'

 L. 844       234  LOAD_FAST                'available_trait_types'
              236  LOAD_METHOD              remove
              238  LOAD_FAST                'trait'
              240  CALL_METHOD_1         1  '1 positional argument'
              242  POP_TOP          

 L. 851       244  LOAD_FAST                'trait_tracker'
              246  LOAD_METHOD              can_add_trait
              248  LOAD_FAST                'trait'
              250  CALL_METHOD_1         1  '1 positional argument'
          252_254  POP_JUMP_IF_TRUE    258  'to 258'

 L. 852       256  CONTINUE            208  'to 208'
            258_0  COME_FROM           252  '252'

 L. 855       258  LOAD_DEREF               'sim_info'
              260  LOAD_METHOD              add_trait
              262  LOAD_FAST                'trait'
              264  CALL_METHOD_1         1  '1 positional argument'
              266  POP_TOP          

 L. 856       268  LOAD_FAST                'num_to_add'
              270  LOAD_CONST               1
              272  INPLACE_SUBTRACT 
              274  STORE_FAST               'num_to_add'
              276  JUMP_BACK           208  'to 208'
            278_0  COME_FROM           220  '220'
            278_1  COME_FROM           214  '214'
              278  POP_BLOCK        
            280_0  COME_FROM_LOOP      206  '206'
            280_1  COME_FROM           126  '126'
            280_2  COME_FROM           104  '104'

Parse error at or near `LOAD_SETCOMP' instruction at offset 150

    @classmethod
    def add_rank(cls, sim_info, sim_creator=None, suppress_telemetry=False):
        for rank in cls._ranks:
            ranked_statistic = rank.ranked_statistic
            if ranked_statistic is None:
                continue
            sim_info.commodity_tracker.add_statistic(ranked_statistic)
            stat = sim_info.commodity_tracker.get_statistic(ranked_statistic)
            rank_level = stat.rank_level
            if rank_level == rank.rank:
                continue
            points_needed = stat.points_to_rank(rank.rank)
            stat.refresh_threshold_callback()
            if suppress_telemetry:
                with stat.suppress_level_up_telemetry():
                    stat.set_value(points_needed, from_load=True)
            else:
                stat.set_value(points_needed, from_load=True)

    @classmethod
    def add_perks--- This code section failed: ---

 L. 895         0  LOAD_FAST                'sim_info'
                2  LOAD_ATTR                get_bucks_tracker
                4  LOAD_CONST               False
                6  LOAD_CONST               ('add_if_none',)
                8  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               10  STORE_DEREF              'bucks_tracker'

 L. 898        12  LOAD_DEREF               'bucks_tracker'
               14  LOAD_CONST               None
               16  COMPARE_OP               is-not
               18  POP_JUMP_IF_FALSE    28  'to 28'

 L. 899        20  LOAD_DEREF               'bucks_tracker'
               22  LOAD_METHOD              clear_bucks_tracker
               24  CALL_METHOD_0         0  '0 positional arguments'
               26  POP_TOP          
             28_0  COME_FROM            18  '18'

 L. 901        28  LOAD_DEREF               'cls'
               30  LOAD_ATTR                _perks
               32  LOAD_ATTR                explicit
               34  POP_JUMP_IF_FALSE    88  'to 88'

 L. 903        36  LOAD_DEREF               'bucks_tracker'
               38  LOAD_CONST               None
               40  COMPARE_OP               is
               42  POP_JUMP_IF_FALSE    56  'to 56'

 L. 904        44  LOAD_FAST                'sim_info'
               46  LOAD_ATTR                get_bucks_tracker
               48  LOAD_CONST               True
               50  LOAD_CONST               ('add_if_none',)
               52  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               54  STORE_DEREF              'bucks_tracker'
             56_0  COME_FROM            42  '42'

 L. 907        56  SETUP_LOOP           88  'to 88'
               58  LOAD_DEREF               'cls'
               60  LOAD_ATTR                _perks
               62  LOAD_ATTR                explicit
               64  GET_ITER         
               66  FOR_ITER             86  'to 86'
               68  STORE_FAST               'perk'

 L. 908        70  LOAD_DEREF               'bucks_tracker'
               72  LOAD_ATTR                unlock_perk
               74  LOAD_FAST                'perk'
               76  LOAD_FAST                'suppress_telemetry'
               78  LOAD_CONST               ('suppress_telemetry',)
               80  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
               82  POP_TOP          
               84  JUMP_BACK            66  'to 66'
               86  POP_BLOCK        
             88_0  COME_FROM_LOOP       56  '56'
             88_1  COME_FROM            34  '34'

 L. 910        88  LOAD_DEREF               'cls'
               90  LOAD_ATTR                _perks
               92  LOAD_ATTR                num_random
               94  POP_JUMP_IF_FALSE   242  'to 242'

 L. 911        96  LOAD_DEREF               'cls'
               98  LOAD_ATTR                _perks
              100  LOAD_ATTR                num_random
              102  LOAD_METHOD              random_int
              104  CALL_METHOD_0         0  '0 positional arguments'
              106  STORE_FAST               'num_to_add'

 L. 912       108  LOAD_FAST                'num_to_add'
              110  LOAD_CONST               0
              112  COMPARE_OP               >
              114  POP_JUMP_IF_FALSE   242  'to 242'

 L. 914       116  LOAD_GLOBAL              services
              118  LOAD_METHOD              get_instance_manager
              120  LOAD_GLOBAL              sims4
              122  LOAD_ATTR                resources
              124  LOAD_ATTR                Types
              126  LOAD_ATTR                BUCKS_PERK
              128  CALL_METHOD_1         1  '1 positional argument'
              130  STORE_FAST               'bucks_perk_manager'

 L. 915       132  LOAD_CLOSURE             'bucks_tracker'
              134  LOAD_CLOSURE             'cls'
              136  BUILD_TUPLE_2         2 
              138  LOAD_SETCOMP             '<code_object <setcomp>>'
              140  LOAD_STR                 'TunableSimTemplate.add_perks.<locals>.<setcomp>'
              142  MAKE_FUNCTION_8          'closure'
              144  LOAD_FAST                'bucks_perk_manager'
              146  LOAD_ATTR                types
              148  LOAD_METHOD              values
              150  CALL_METHOD_0         0  '0 positional arguments'
              152  GET_ITER         
              154  CALL_FUNCTION_1       1  '1 positional argument'
              156  STORE_FAST               'available_bucks_perk_types'

 L. 920       158  LOAD_FAST                'available_bucks_perk_types'
              160  LOAD_GLOBAL              set
              162  LOAD_DEREF               'cls'
              164  LOAD_ATTR                _perks
              166  LOAD_ATTR                explicit
              168  CALL_FUNCTION_1       1  '1 positional argument'
              170  INPLACE_SUBTRACT 
              172  STORE_FAST               'available_bucks_perk_types'

 L. 922       174  LOAD_GLOBAL              list
              176  LOAD_FAST                'available_bucks_perk_types'
              178  CALL_FUNCTION_1       1  '1 positional argument'
              180  STORE_FAST               'available_bucks_perk_types'

 L. 923       182  SETUP_LOOP          242  'to 242'
              184  LOAD_FAST                'num_to_add'
              186  LOAD_CONST               0
              188  COMPARE_OP               >
              190  POP_JUMP_IF_FALSE   240  'to 240'
              192  LOAD_FAST                'available_bucks_perk_types'
              194  POP_JUMP_IF_FALSE   240  'to 240'

 L. 925       196  LOAD_GLOBAL              random
              198  LOAD_METHOD              choice
              200  LOAD_FAST                'available_bucks_perk_types'
              202  CALL_METHOD_1         1  '1 positional argument'
              204  STORE_FAST               'perk'

 L. 928       206  LOAD_FAST                'available_bucks_perk_types'
              208  LOAD_METHOD              remove
              210  LOAD_FAST                'perk'
              212  CALL_METHOD_1         1  '1 positional argument'
              214  POP_TOP          

 L. 931       216  LOAD_DEREF               'bucks_tracker'
              218  LOAD_ATTR                unlock_perk
              220  LOAD_FAST                'perk'
              222  LOAD_FAST                'suppress_telemetry'
              224  LOAD_CONST               ('suppress_telemetry',)
              226  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              228  POP_TOP          

 L. 932       230  LOAD_FAST                'num_to_add'
              232  LOAD_CONST               1
              234  INPLACE_SUBTRACT 
              236  STORE_FAST               'num_to_add'
              238  JUMP_BACK           184  'to 184'
            240_0  COME_FROM           194  '194'
            240_1  COME_FROM           190  '190'
              240  POP_BLOCK        
            242_0  COME_FROM_LOOP      182  '182'
            242_1  COME_FROM           114  '114'
            242_2  COME_FROM            94  '94'

Parse error at or near `LOAD_SETCOMP' instruction at offset 138

    @classmethod
    def _enroll_in_university(cls, sim_info, sim_creator=None):
        if cls._major is not None:
            degree_tracker = sim_info.degree_tracker
            if degree_tracker is None:
                logger.error("SimInfo {} was created without a degree tracker. Can't assign them a university and major.")
                return
            university = University.choose_random_university() if cls._major.university is None else cls._major.university
            major = University.choose_random_major() if cls._major.major is None else cls._major.major
            if university is None or major is None:
                logger.error('Unable to find a major or university (or both) to enroll the Sim in.')
                return
            degree_tracker.process_acceptance(send_telemetry=False)
            if not degree_tracker.is_accepted_degree(university, major):
                degree_tracker.set_accepted_degree(university, major)
            degree_tracker.add_credits(cls._major.random_credits_in_range.random_int())
            degree_tracker.enroll(major, university, cls._major.num_courses_to_enroll_in, [])

    @classmethod
    def _add_sim_info_fixups(cls, sim_info, sim_creator=None):
        fixup_tracker = sim_info.fixup_tracker
        if fixup_tracker is not None:
            for fixup in cls._fixups:
                fixup_tracker.add_fixup(fixup)

    @classmethod
    def _add_gender_preference(cls, sim_info):
        gender_preference_tuning = sims.global_gender_preference_tuning.GlobalGenderPreferenceTuning
        if not sim_info.is_exploring_sexuality:
            return
        else:
            for gender in sims.sim_info_types.Gender:
                is_attracted = sim_info.has_trait(gender_preference_tuning.ROMANTIC_PREFERENCE_TRAITS_MAPPING[gender].is_attracted_trait)
                if is_attracted:
                    return

            if gender_preference_tuning.enable_autogeneration_same_sex_preference:
                sexuality_status_choices = [(sexuality_status.weight, sexuality_status.exploring_sexuality) for sexuality_status in gender_preference_tuning.ENABLED_AUTOGENERATION_EXPLORING_SEXUALITY_WEIGHTS]
            else:
                sexuality_status_choices = [(sexuality_status.weight, sexuality_status.exploring_sexuality) for sexuality_status in gender_preference_tuning.EXPLORING_SEXUALITY_WEIGHTS]
        sexuality_status_choice = sims4.random.weighted_random_item(sexuality_status_choices)
        sexuality_status_trait = gender_preference_tuning.EXPLORING_SEXUALITY_TRAITS_MAPPING[sexuality_status_choice]
        if sexuality_status_trait is None:
            logger.error('Missing tuned trait for exploring sexuality.', owner='amwu')
            return
        is_exploring = sexuality_status_choice == SexualityStatus.EXPLORING
        if not is_exploring:
            old_trait = gender_preference_tuning.EXPLORING_SEXUALITY_TRAITS_MAPPING[SexualityStatus.EXPLORING]
            sim_info.remove_trait(old_trait)
            sim_info.add_trait(sexuality_status_trait)
        for gender in sims.sim_info_types.Gender:
            if gender_preference_tuning.enable_autogeneration_same_sex_preference:
                attraction_status_choices = [(attraction_info.weight, attraction_info.attraction_status) for attraction_info in gender_preference_tuning.ENABLED_AUTOGENERATION_SAME_SEX_PREFERENCE_WEIGHTS[gender]]
            else:
                attraction_status_choices = [(attraction_info.weight, attraction_info.attraction_status) for attraction_info in gender_preference_tuning.GENDER_PREFERENCE_WEIGHTS[gender]]
            attraction_status_choice = sims4.random.weighted_random_item(attraction_status_choices)
            should_be_attracted = attraction_status_choice == AttractionStatus.ATTRACTED
            if should_be_attracted:
                gender_preference_stat_type = gender_preference_tuning.GENDER_PREFERENCE[gender]
                sim_info.set_stat_value(gender_preference_stat_type, gender_preference_stat_type.max_value)
            attracted_trait = gender_preference_tuning.WOOHOO_PREFERENCE_TRAITS_MAPPING[gender].is_attracted_trait
            nonattracted_trait = gender_preference_tuning.WOOHOO_PREFERENCE_TRAITS_MAPPING[gender].not_attracted_trait
            if not attracted_trait is None:
                if nonattracted_trait is None:
                    logger.error("Missing tuned trait(s) for {}'s woohoo orientation.", gender, owner='amwu')
                    continue
                should_be_attracted |= is_exploring
                desired_trait = attracted_trait if should_be_attracted else nonattracted_trait
                conflicting_trait = nonattracted_trait if should_be_attracted else attracted_trait
                if sim_info.has_trait(conflicting_trait):
                    sim_info.remove_trait(conflicting_trait)
                sim_info.add_trait(desired_trait)


class TunableTemplateChooser(metaclass=TunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TEMPLATE_CHOOSER)):
    INSTANCE_TUNABLES = {'_templates': TunableList(description='\n            A list of templates that can be chosen from this template chooser.\n            ',
                     tunable=TunableTuple(description='\n                The template and weights that can be chosen.\n                ',
                     template=TunableSimTemplate.TunableReference(description='\n                    A template that can be chosen.\n                    ',
                     pack_safe=True),
                     weight=Tunable(description='\n                    Weight of this template being chosen.\n                    ',
                     tunable_type=int,
                     default=1)))}

    @classmethod
    def choose_template(cls):
        possible_templates = [(template_weight_pair.weight, template_weight_pair.template) for template_weight_pair in cls._templates]
        return sims4.random.pop_weighted(possible_templates)