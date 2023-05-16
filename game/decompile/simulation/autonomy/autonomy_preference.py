# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_preference.py
# Compiled at: 2019-07-08 18:31:36
# Size of source mod 2**32: 3009 bytes
from sims4.tuning.dynamic_enum import DynamicEnum
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, OptionalTunable, Tunable
import enum

class AutonomyPreferenceType(enum.Int):
    ALLOWED = 0
    DISALLOWED = 1
    USE_PREFERENCE = 2
    USE_ONLY = 3


class ObjectPreferenceTag(DynamicEnum):
    INVALID = -1


class TunableAutonomyPreference(TunableTuple):

    def __init__(self, is_scoring, use_only=False, **kwargs):
        (super().__init__)(tag=TunableEnumEntry(description="\n                The preference tag associated with this interaction's \n                ownership settings.\n                ",
  tunable_type=ObjectPreferenceTag,
  default=(ObjectPreferenceTag.INVALID),
  invalid_enums=(
 ObjectPreferenceTag.INVALID,)), 
         should_set=OptionalTunable(description='\n                Whether or not running this interaction sets an autonomy\n                preference for the target object.\n                ',
  tunable=TunableTuple(autonomous=Tunable(description='\n                        Whether or not this should be set when this interaction \n                        is running autonomously.\n                        ',
  tunable_type=bool,
  default=False),
  should_force=Tunable(description='\n                        If True, override any existing preference.\n                        If False, leave existing preference as is.\n                        ',
  tunable_type=bool,
  default=False)),
  enabled_by_default=True,
  disabled_value=False,
  disabled_name='false',
  enabled_name='true'), 
         should_clear=Tunable(description='\n                If True, clears the preference for this object.\n                If False, sets the preference for this object\n                ',
  tunable_type=bool,
  default=False), 
         locked_args={'is_scoring':is_scoring, 
 'use_only':use_only}, **kwargs)