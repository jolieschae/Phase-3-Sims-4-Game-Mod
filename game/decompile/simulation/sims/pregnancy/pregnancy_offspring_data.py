# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\pregnancy\pregnancy_offspring_data.py
# Compiled at: 2017-05-18 21:34:54
# Size of source mod 2**32: 1060 bytes
from protocolbuffers.Localization_pb2 import LocalizedStringToken
from sims.sim_info_types import Gender
from singletons import DEFAULT

class PregnancyOffspringData:

    def __init__(self, age, gender, species, genetics, first_name='', last_name='', traits=DEFAULT):
        self.age = age
        self.gender = gender
        self.species = species
        self.genetics = genetics
        self.first_name = first_name
        self.last_name = last_name
        self.traits = [] if traits is DEFAULT else traits

    @property
    def is_female(self):
        return self.gender == Gender.FEMALE

    def populate_localization_token(self, token):
        token.type = LocalizedStringToken.SIM
        token.first_name = self.first_name
        token.last_name = self.last_name
        token.is_female = self.is_female