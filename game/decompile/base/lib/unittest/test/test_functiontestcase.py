# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\test_functiontestcase.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5688 bytes
import unittest
from unittest.test.support import LoggingResult

class Test_FunctionTestCase(unittest.TestCase):

    def test_countTestCases(self):
        test = unittest.FunctionTestCase(lambda: None)
        self.assertEqual(test.countTestCases(), 1)

    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')
            raise RuntimeError('raised by setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')

        expected = [
         'startTest', 'setUp', 'addError', 'stopTest']
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            raise RuntimeError('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addError'", 
         "'stopTest'"]
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')
            self.fail('raised by test')

        def tearDown():
            events.append('tearDown')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addFailure'", 
         "'stopTest'"]
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        def setUp():
            events.append('setUp')

        def test():
            events.append('test')

        def tearDown():
            events.append('tearDown')
            raise RuntimeError('raised by tearDown')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", "'addError'", 
         "'stopTest'"]
        unittest.FunctionTestCase(test, setUp, tearDown).run(result)
        self.assertEqual(events, expected)

    def test_id(self):
        test = unittest.FunctionTestCase(lambda: None)
        self.assertIsInstance(test.id(), str)

    def test_shortDescription__no_docstring(self):
        test = unittest.FunctionTestCase(lambda: None)
        self.assertEqual(test.shortDescription(), None)

    def test_shortDescription__singleline_docstring(self):
        desc = 'this tests foo'
        test = unittest.FunctionTestCase((lambda: None), description=desc)
        self.assertEqual(test.shortDescription(), 'this tests foo')


if __name__ == '__main__':
    unittest.main()