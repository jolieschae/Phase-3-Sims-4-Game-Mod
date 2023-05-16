# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\components\inventory_availability_tuning.py
# Compiled at: 2020-02-28 20:36:09
# Size of source mod 2**32: 3277 bytes
from event_testing.resolver import GlobalResolver
from event_testing.test_variants import RegionTest
from event_testing.tests import TestListLoadingMixin
from sims4.tuning.tunable import TunableList, TunableTuple, TunableVariant
from singletons import EMPTY_SET
from tag import TunableTag
from tunable_utils.tunable_white_black_list import TunableWhiteBlackList

class TunableInventoryAvailabilityTestVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, region=RegionTest.TunableFactory(locked_args={'tooltip':None,  'subject':None}), 
         default='region', **kwargs)


class TunableInventoryAvailabilityTestList(TestListLoadingMixin):

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, tunable=TunableInventoryAvailabilityTestVariant(), **kwargs)


class InventoryAvailabilityTuning:
    ZONE_AVAILABILITY_RULES = TunableList(description='\n        The rules used to determine whether or not specific items are available in a given region/zone.\n        ',
      tunable=TunableTuple(associated_tests=TunableInventoryAvailabilityTestList(description='\n                A set of tests that must pass for this ruleset to be active.  Any tests used here should\n                not be based on anything other than the current zone or venue.\n                '),
      tag_white_black_list=TunableWhiteBlackList(description='\n                If associated tests pass, this white/black list indicates whether this object will be visible based\n                on the tags on the object.\n                ',
      tunable=TunableTag(description='A tag to filter on.',
      filter_prefixes=('Func', )))))


def get_available_rules():
    if not InventoryAvailabilityTuning.ZONE_AVAILABILITY_RULES:
        return EMPTY_SET
    ruleset = []
    resolver = GlobalResolver()
    for rule in InventoryAvailabilityTuning.ZONE_AVAILABILITY_RULES:
        if not rule.associated_tests.run_tests(resolver):
            continue
        ruleset.append(lambda obj: rule.tag_white_black_list.test_collection(obj.build_buy_tags))

    return ruleset