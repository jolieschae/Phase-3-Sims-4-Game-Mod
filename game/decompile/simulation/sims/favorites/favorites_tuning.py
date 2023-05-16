# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\favorites\favorites_tuning.py
# Compiled at: 2019-07-11 18:55:05
# Size of source mod 2**32: 1688 bytes
import services
from animation.tunable_animation_overrides import TunableAnimationOverrides
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableTuple

class FavoritesTuning:
    FAVORITES_ANIMATION_OVERRIDES = TunableList(description='\n        A list of favorite object definitions and animation overrides. These will\n        be applied any time one of these favorites is used (currently only with \n        prop overrides).\n        ',
      tunable=TunableTuple(description='\n            A set of favorite object definitions and animation overrides to apply\n            when one of those definitions is used as a favorite.\n            ',
      favorite_definitions=TunableSet(description='\n                A set of object definitions. If any object in this set is used as a \n                favorite, the corresponding Animation Overrides will be applied.\n                ',
      tunable=TunableReference(description='\n                    The definition of the favorite.\n                    ',
      manager=(services.definition_manager()),
      pack_safe=True)),
      animation_overrides=TunableAnimationOverrides(description='\n                Any animation overrides to use when one of the listed favorite \n                objects is used. Currently, this only applies to prop overrides.\n                ')))