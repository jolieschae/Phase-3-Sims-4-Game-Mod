# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\localization\localization_validation.py
# Compiled at: 2014-04-12 18:19:23
# Size of source mod 2**32: 2209 bytes
from protocolbuffers.Localization_pb2 import LocalizedStringToken
import sims4.log, sims4.reload
logger = sims4.log.Logger('Localization', default_owner='epanero')
with sims4.reload.protected(globals()):
    _localized_string_validators = {}

def register_localized_string_validator(validator_gen):
    key = validator_gen.__module__ + validator_gen.__qualname__
    _localized_string_validators[key] = validator_gen


def get_all_strings_to_validate_gen():
    for validator_gen in _localized_string_validators.values():
        try:
            for localized_string_msg in validator_gen():
                if localized_string_msg.hash:
                    yield localized_string_msg

        except Exception as ex:
            try:
                logger.error('Validator {} threw an exception: {}', validator_gen, ex)
            finally:
                ex = None
                del ex


class _LocalizationValidatorPlaceholderSim:

    def __init__(self, is_female=False):
        self._first_name = 'Jane' if is_female else 'John'
        self._last_name = 'Doe'
        self._is_female = is_female

    def populate_localization_token(self, token):
        token.type = LocalizedStringToken.SIM
        token.first_name = self._first_name
        token.last_name = self._last_name
        token.is_female = self._is_female


def get_random_localization_token_sim(*args, **kwargs):
    return _LocalizationValidatorPlaceholderSim(*args, **kwargs)