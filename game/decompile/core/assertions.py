# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\assertions.py
# Compiled at: 2015-02-04 17:14:34
# Size of source mod 2**32: 4799 bytes
import functools
from sims4.collections import ListSet
from sims4.repr_utils import standard_repr
import sims4.log
logger = sims4.log.Logger('Assertions')
ENABLE_INTRUSIVE_ASSERTIONS = False

def not_recursive(func):
    return func


def not_recursive_gen(func):
    return func


def hot_path(fn):
    return fn