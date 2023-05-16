# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tunable_utils\tested_list.py
# Compiled at: 2021-11-22 21:29:05
# Size of source mod 2**32: 2332 bytes
from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import TunableList, TunableTuple, Tunable
from singletons import DEFAULT

class _TestedList(tuple):

    def get_all(self):
        for item_data in self:
            yield item_data.item

    def __call__(self, *, resolver, yield_index=False):
        for index, item_data in enumerate(self):
            if item_data.test.run_tests(resolver):
                if yield_index:
                    yield (
                     index, item_data.item)
                else:
                    yield item_data.item
                if item_data.stop_processing:
                    break


STOP_PROCESSING_ALWAYS = 'stop_processing_always'

class TunableTestedList(TunableList):
    DEFAULT_LIST = _TestedList()

    def __init__(self, *args, tunable_type, stop_processing_behavior=DEFAULT, **kwargs):
        tuple_args = {}
        if stop_processing_behavior is DEFAULT:
            tuple_args['stop_processing'] = Tunable(description='\n                If checked, no other element from this list is considered if\n                this element passes its associated test.\n                ',
              tunable_type=bool,
              default=False)
        else:
            if stop_processing_behavior == STOP_PROCESSING_ALWAYS:
                tuple_args['locked_args'] = {'stop_processing': True}
        (super().__init__)(args, tunable=TunableTuple(description='\n                An entry in this tested list.\n                ', 
                   test=TunableTestSet(), 
                   item=tunable_type, **tuple_args), **kwargs)

    def load_etree_node(self, node, source, expect_error):
        value = super().load_etree_node(node, source, expect_error)
        return _TestedList(value)