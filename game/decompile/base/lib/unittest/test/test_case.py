# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\test_case.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 74420 bytes
import contextlib, difflib, pprint, pickle, re, sys, logging, warnings, weakref, inspect
from copy import deepcopy
from test import support
import unittest
from unittest.test.support import TestEquality, TestHashing, LoggingResult, LegacyLoggingResult, ResultWithNoStartTestRunStopTestRun
from test.support import captured_stderr
log_foo = logging.getLogger('foo')
log_foobar = logging.getLogger('foo.bar')
log_quux = logging.getLogger('quux')

class Test(object):

    class Foo(unittest.TestCase):

        def runTest(self):
            pass

        def test1(self):
            pass

    class Bar(Foo):

        def test2(self):
            pass

    class LoggingTestCase(unittest.TestCase):

        def __init__(self, events):
            super(Test.LoggingTestCase, self).__init__('test')
            self.events = events

        def setUp(self):
            self.events.append('setUp')

        def test(self):
            self.events.append('test')

        def tearDown(self):
            self.events.append('tearDown')


class Test_TestCase(unittest.TestCase, TestEquality, TestHashing):
    eq_pairs = [
     (
      Test.Foo('test1'), Test.Foo('test1'))]
    ne_pairs = [
     (
      Test.Foo('test1'), Test.Foo('runTest')),
     (
      Test.Foo('test1'), Test.Bar('test1')),
     (
      Test.Foo('test1'), Test.Bar('test2'))]

    def test_init__no_test_name(self):

        class Test(unittest.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        self.assertEqual(Test().id()[-13:], '.Test.runTest')
        test = unittest.TestCase()
        test.assertEqual(3, 3)
        with test.assertRaises(test.failureException):
            test.assertEqual(3, 2)
        with self.assertRaises(AttributeError):
            test.run()

    def test_init__test_name__valid(self):

        class Test(unittest.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        self.assertEqual(Test('test').id()[-10:], '.Test.test')

    def test_init__test_name__invalid(self):

        class Test(unittest.TestCase):

            def runTest(self):
                raise MyException()

            def test(self):
                pass

        try:
            Test('testfoo')
        except ValueError:
            pass
        else:
            self.fail('Failed to raise ValueError')

    def test_countTestCases(self):

        class Foo(unittest.TestCase):

            def test(self):
                pass

        self.assertEqual(Foo('test').countTestCases(), 1)

    def test_defaultTestResult(self):

        class Foo(unittest.TestCase):

            def runTest(self):
                pass

        result = Foo().defaultTestResult()
        self.assertEqual(type(result), unittest.TestResult)

    def test_run_call_order__error_in_setUp(self):
        events = []
        result = LoggingResult(events)

        class Foo(Test.LoggingTestCase):

            def setUp(self):
                super(Foo, self).setUp()
                raise RuntimeError('raised by Foo.setUp')

        Foo(events).run(result)
        expected = ['startTest', 'setUp', 'addError', 'stopTest']
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_setUp_default_result(self):
        events = []

        class Foo(Test.LoggingTestCase):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def setUp(self):
                super(Foo, self).setUp()
                raise RuntimeError('raised by Foo.setUp')

        Foo(events).run()
        expected = ["'startTestRun'", "'startTest'", "'setUp'", "'addError'", 
         "'stopTest'", 
         "'stopTestRun'"]
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test(self):
        events = []
        result = LoggingResult(events)

        class Foo(Test.LoggingTestCase):

            def test(self):
                super(Foo, self).test()
                raise RuntimeError('raised by Foo.test')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addError'", 
         "'stopTest'"]
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_test_default_result(self):
        events = []

        class Foo(Test.LoggingTestCase):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def test(self):
                super(Foo, self).test()
                raise RuntimeError('raised by Foo.test')

        expected = [
         "'startTestRun'", "'startTest'", "'setUp'", "'test'", 
         "'tearDown'", 
         "'addError'", "'stopTest'", "'stopTestRun'"]
        Foo(events).run()
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test(self):
        events = []
        result = LoggingResult(events)

        class Foo(Test.LoggingTestCase):

            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addFailure'", 
         "'stopTest'"]
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_run_call_order__failure_in_test_default_result(self):

        class Foo(Test.LoggingTestCase):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def test(self):
                super(Foo, self).test()
                self.fail('raised by Foo.test')

        expected = [
         "'startTestRun'", "'startTest'", "'setUp'", "'test'", 
         "'tearDown'", 
         "'addFailure'", "'stopTest'", "'stopTestRun'"]
        events = []
        Foo(events).run()
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown(self):
        events = []
        result = LoggingResult(events)

        class Foo(Test.LoggingTestCase):

            def tearDown(self):
                super(Foo, self).tearDown()
                raise RuntimeError('raised by Foo.tearDown')

        Foo(events).run(result)
        expected = ["'startTest'", "'setUp'", "'test'", "'tearDown'", "'addError'", 
         "'stopTest'"]
        self.assertEqual(events, expected)

    def test_run_call_order__error_in_tearDown_default_result(self):

        class Foo(Test.LoggingTestCase):

            def defaultTestResult(self):
                return LoggingResult(self.events)

            def tearDown(self):
                super(Foo, self).tearDown()
                raise RuntimeError('raised by Foo.tearDown')

        events = []
        Foo(events).run()
        expected = ["'startTestRun'", "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addError'", 
         "'stopTest'", "'stopTestRun'"]
        self.assertEqual(events, expected)

    def test_run_call_order_default_result(self):

        class Foo(unittest.TestCase):

            def defaultTestResult(self):
                return ResultWithNoStartTestRunStopTestRun()

            def test(self):
                pass

        Foo('test').run()

    def _check_call_order__subtests(self, result, events, expected_events):

        class Foo(Test.LoggingTestCase):

            def test(self):
                super(Foo, self).test()
                for i in (1, 2, 3):
                    with self.subTest(i=i):
                        if i == 1:
                            self.fail('failure')
                        for j in (2, 3):
                            with self.subTest(j=j):
                                if i * j == 6:
                                    raise RuntimeError('raised by Foo.test')

                1 / 0

        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    def test_run_call_order__subtests(self):
        events = []
        result = LoggingResult(events)
        expected = ["'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addSubTestFailure'", 
         "'addSubTestSuccess'", 
         "'addSubTestFailure'", 
         "'addSubTestFailure'", 
         "'addSubTestSuccess'", 
         "'addError'", "'stopTest'"]
        self._check_call_order__subtests(result, events, expected)

    def test_run_call_order__subtests_legacy(self):
        events = []
        result = LegacyLoggingResult(events)
        expected = ["'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addFailure'", 
         "'stopTest'"]
        self._check_call_order__subtests(result, events, expected)

    def _check_call_order__subtests_success(self, result, events, expected_events):

        class Foo(Test.LoggingTestCase):

            def test(self):
                super(Foo, self).test()
                for i in (1, 2):
                    with self.subTest(i=i):
                        for j in (2, 3):
                            with self.subTest(j=j):
                                pass

        Foo(events).run(result)
        self.assertEqual(events, expected_events)

    def test_run_call_order__subtests_success(self):
        events = []
        result = LoggingResult(events)
        expected = [
         'startTest', 'setUp', 'test', 'tearDown'] + 6 * ['addSubTestSuccess'] + ['addSuccess', 'stopTest']
        self._check_call_order__subtests_success(result, events, expected)

    def test_run_call_order__subtests_success_legacy(self):
        events = []
        result = LegacyLoggingResult(events)
        expected = ["'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addSuccess'", 
         "'stopTest'"]
        self._check_call_order__subtests_success(result, events, expected)

    def test_run_call_order__subtests_failfast(self):
        events = []
        result = LoggingResult(events)
        result.failfast = True

        class Foo(Test.LoggingTestCase):

            def test(self):
                super(Foo, self).test()
                with self.subTest(i=1):
                    self.fail('failure')
                with self.subTest(i=2):
                    self.fail('failure')
                self.fail('failure')

        expected = [
         "'startTest'", "'setUp'", "'test'", "'tearDown'", 
         "'addSubTestFailure'", 
         "'stopTest'"]
        Foo(events).run(result)
        self.assertEqual(events, expected)

    def test_subtests_failfast(self):
        events = []

        class Foo(unittest.TestCase):

            def test_a(self):
                with self.subTest():
                    events.append('a1')
                events.append('a2')

            def test_b(self):
                with self.subTest():
                    events.append('b1')
                with self.subTest():
                    self.fail('failure')
                events.append('b2')

            def test_c(self):
                events.append('c')

        result = unittest.TestResult()
        result.failfast = True
        suite = unittest.makeSuite(Foo)
        suite.run(result)
        expected = [
         'a1', 'a2', 'b1']
        self.assertEqual(events, expected)

    def test_failureException__default(self):

        class Foo(unittest.TestCase):

            def test(self):
                pass

        self.assertIs(Foo('test').failureException, AssertionError)

    def test_failureException__subclassing__explicit_raise(self):
        events = []
        result = LoggingResult(events)

        class Foo(unittest.TestCase):

            def test(self):
                raise RuntimeError()

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)
        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    def test_failureException__subclassing__implicit_raise(self):
        events = []
        result = LoggingResult(events)

        class Foo(unittest.TestCase):

            def test(self):
                self.fail('foo')

            failureException = RuntimeError

        self.assertIs(Foo('test').failureException, RuntimeError)
        Foo('test').run(result)
        expected = ['startTest', 'addFailure', 'stopTest']
        self.assertEqual(events, expected)

    def test_setUp(self):

        class Foo(unittest.TestCase):

            def runTest(self):
                pass

        Foo().setUp()

    def test_tearDown(self):

        class Foo(unittest.TestCase):

            def runTest(self):
                pass

        Foo().tearDown()

    def test_id(self):

        class Foo(unittest.TestCase):

            def runTest(self):
                pass

        self.assertIsInstance(Foo().id(), str)

    def test_run__uses_defaultTestResult(self):
        events = []
        defaultResult = LoggingResult(events)

        class Foo(unittest.TestCase):

            def test(self):
                events.append('test')

            def defaultTestResult(self):
                return defaultResult

        result = Foo('test').run()
        self.assertIs(result, defaultResult)
        expected = ["'startTestRun'", "'startTest'", "'test'", "'addSuccess'", 
         "'stopTest'", 
         "'stopTestRun'"]
        self.assertEqual(events, expected)

    def test_run__returns_given_result(self):

        class Foo(unittest.TestCase):

            def test(self):
                pass

        result = unittest.TestResult()
        retval = Foo('test').run(result)
        self.assertIs(retval, result)

    def test_call__invoking_an_instance_delegates_to_run(self):
        resultIn = unittest.TestResult()
        resultOut = unittest.TestResult()

        class Foo(unittest.TestCase):

            def test(self):
                pass

            def run(self, result):
                self.assertIs(result, resultIn)
                return resultOut

        retval = Foo('test')(resultIn)
        self.assertIs(retval, resultOut)

    def testShortDescriptionWithoutDocstring(self):
        self.assertIsNone(self.shortDescription())

    @unittest.skipIf(sys.flags.optimize >= 2, 'Docstrings are omitted with -O2 and above')
    def testShortDescriptionWithOneLineDocstring(self):
        self.assertEqual(self.shortDescription(), 'Tests shortDescription() for a method with a docstring.')

    @unittest.skipIf(sys.flags.optimize >= 2, 'Docstrings are omitted with -O2 and above')
    def testShortDescriptionWithMultiLineDocstring(self):
        self.assertEqual(self.shortDescription(), 'Tests shortDescription() for a method with a longer docstring.')

    def testAddTypeEqualityFunc(self):

        class SadSnake(object):
            pass

        s1, s2 = SadSnake(), SadSnake()
        self.assertFalse(s1 == s2)

        def AllSnakesCreatedEqual(a, b, msg=None):
            return type(a) == type(b) == SadSnake

        self.addTypeEqualityFunc(SadSnake, AllSnakesCreatedEqual)
        self.assertEqual(s1, s2)

    def testAssertIs(self):
        thing = object()
        self.assertIs(thing, thing)
        self.assertRaises(self.failureException, self.assertIs, thing, object())

    def testAssertIsNot(self):
        thing = object()
        self.assertIsNot(thing, object())
        self.assertRaises(self.failureException, self.assertIsNot, thing, thing)

    def testAssertIsInstance(self):
        thing = []
        self.assertIsInstance(thing, list)
        self.assertRaises(self.failureException, self.assertIsInstance, thing, dict)

    def testAssertNotIsInstance(self):
        thing = []
        self.assertNotIsInstance(thing, dict)
        self.assertRaises(self.failureException, self.assertNotIsInstance, thing, list)

    def testAssertIn(self):
        animals = {'monkey':'banana', 
         'cow':'grass',  'seal':'fish'}
        self.assertIn('a', 'abc')
        self.assertIn(2, [1, 2, 3])
        self.assertIn('monkey', animals)
        self.assertNotIn('d', 'abc')
        self.assertNotIn(0, [1, 2, 3])
        self.assertNotIn('otter', animals)
        self.assertRaises(self.failureException, self.assertIn, 'x', 'abc')
        self.assertRaises(self.failureException, self.assertIn, 4, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertIn, 'elephant', animals)
        self.assertRaises(self.failureException, self.assertNotIn, 'c', 'abc')
        self.assertRaises(self.failureException, self.assertNotIn, 1, [1, 2, 3])
        self.assertRaises(self.failureException, self.assertNotIn, 'cow', animals)

    def testAssertDictContainsSubset(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertDictContainsSubset({}, {})
            self.assertDictContainsSubset({}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a': 1})
            self.assertDictContainsSubset({'a': 1}, {'a':1,  'b':2})
            self.assertDictContainsSubset({'a':1,  'b':2}, {'a':1,  'b':2})
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({1: 'one'}, {})
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a': 2}, {'a': 1})
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'c': 1}, {'a': 1})
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a':1,  'c':1}, {'a': 1})
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'a':1,  'c':1}, {'a': 1})
            one = ''.join((chr(i) for i in range(255)))
            with self.assertRaises(self.failureException):
                self.assertDictContainsSubset({'foo': one}, {'foo': '�'})

    def testAssertEqual(self):
        equal_pairs = [((), ()), ({}, {}), ([], []),
         (
          set(), set()),
         (
          frozenset(), frozenset())]
        for a, b in equal_pairs:
            try:
                self.assertEqual(a, b)
            except self.failureException:
                self.fail('assertEqual(%r, %r) failed' % (a, b))

            try:
                self.assertEqual(a, b, msg='foo')
            except self.failureException:
                self.fail('assertEqual(%r, %r) with msg= failed' % (a, b))

            try:
                self.assertEqual(a, b, 'foo')
            except self.failureException:
                self.fail('assertEqual(%r, %r) with third parameter failed' % (
                 a, b))

        unequal_pairs = [((), []), ({}, set()),
         (
          set([4, 1]), frozenset([4, 2])),
         (
          frozenset([4, 5]), set([2, 3])),
         (
          set([3, 4]), set([5, 4]))]
        for a, b in unequal_pairs:
            self.assertRaises(self.failureException, self.assertEqual, a, b)
            self.assertRaises(self.failureException, self.assertEqual, a, b, 'foo')
            self.assertRaises((self.failureException), (self.assertEqual), a, b, msg='foo')

    def testEquality(self):
        self.assertListEqual([], [])
        self.assertTupleEqual((), ())
        self.assertSequenceEqual([], ())
        a = [
         0, 'a', []]
        b = []
        self.assertRaises(unittest.TestCase.failureException, self.assertListEqual, a, b)
        self.assertRaises(unittest.TestCase.failureException, self.assertListEqual, tuple(a), tuple(b))
        self.assertRaises(unittest.TestCase.failureException, self.assertSequenceEqual, a, tuple(b))
        b.extend(a)
        self.assertListEqual(a, b)
        self.assertTupleEqual(tuple(a), tuple(b))
        self.assertSequenceEqual(a, tuple(b))
        self.assertSequenceEqual(tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, a, tuple(b))
        self.assertRaises(self.failureException, self.assertTupleEqual, tuple(a), b)
        self.assertRaises(self.failureException, self.assertListEqual, None, b)
        self.assertRaises(self.failureException, self.assertTupleEqual, None, tuple(b))
        self.assertRaises(self.failureException, self.assertSequenceEqual, None, tuple(b))
        self.assertRaises(self.failureException, self.assertListEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertTupleEqual, 1, 1)
        self.assertRaises(self.failureException, self.assertSequenceEqual, 1, 1)
        self.assertDictEqual({}, {})
        c = {'x': 1}
        d = {}
        self.assertRaises(unittest.TestCase.failureException, self.assertDictEqual, c, d)
        d.update(c)
        self.assertDictEqual(c, d)
        d['x'] = 0
        self.assertRaises(unittest.TestCase.failureException, self.assertDictEqual, c, d, 'These are unequal')
        self.assertRaises(self.failureException, self.assertDictEqual, None, d)
        self.assertRaises(self.failureException, self.assertDictEqual, [], d)
        self.assertRaises(self.failureException, self.assertDictEqual, 1, 1)

    def testAssertSequenceEqualMaxDiff(self):
        self.assertEqual(self.maxDiff, 640)
        seq1 = 'a' + 'x' * 6400
        seq2 = 'b' + 'x' * 6400
        diff = '\n'.join(difflib.ndiff(pprint.pformat(seq1).splitlines(), pprint.pformat(seq2).splitlines()))
        omitted = unittest.case.DIFF_OMITTED % (len(diff) + 1,)
        self.maxDiff = len(diff) // 2
        try:
            self.assertSequenceEqual(seq1, seq2)
        except self.failureException as e:
            try:
                msg = e.args[0]
            finally:
                e = None
                del e

        else:
            self.fail('assertSequenceEqual did not fail.')
        self.assertLess(len(msg), len(diff))
        self.assertIn(omitted, msg)
        self.maxDiff = len(diff) * 2
        try:
            self.assertSequenceEqual(seq1, seq2)
        except self.failureException as e:
            try:
                msg = e.args[0]
            finally:
                e = None
                del e

        else:
            self.fail('assertSequenceEqual did not fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)
        self.maxDiff = None
        try:
            self.assertSequenceEqual(seq1, seq2)
        except self.failureException as e:
            try:
                msg = e.args[0]
            finally:
                e = None
                del e

        else:
            self.fail('assertSequenceEqual did not fail.')
        self.assertGreater(len(msg), len(diff))
        self.assertNotIn(omitted, msg)

    def testTruncateMessage(self):
        self.maxDiff = 1
        message = self._truncateMessage('foo', 'bar')
        omitted = unittest.case.DIFF_OMITTED % len('bar')
        self.assertEqual(message, 'foo' + omitted)
        self.maxDiff = None
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')
        self.maxDiff = 4
        message = self._truncateMessage('foo', 'bar')
        self.assertEqual(message, 'foobar')

    def testAssertDictEqualTruncates(self):
        test = unittest.TestCase('assertEqual')

        def truncate(msg, diff):
            return 'foo'

        test._truncateMessage = truncate
        try:
            test.assertDictEqual({}, {1: 0})
        except self.failureException as e:
            try:
                self.assertEqual(str(e), 'foo')
            finally:
                e = None
                del e

        else:
            self.fail('assertDictEqual did not fail')

    def testAssertMultiLineEqualTruncates(self):
        test = unittest.TestCase('assertEqual')

        def truncate(msg, diff):
            return 'foo'

        test._truncateMessage = truncate
        try:
            test.assertMultiLineEqual('foo', 'bar')
        except self.failureException as e:
            try:
                self.assertEqual(str(e), 'foo')
            finally:
                e = None
                del e

        else:
            self.fail('assertMultiLineEqual did not fail')

    def testAssertEqual_diffThreshold(self):
        self.assertEqual(self._diffThreshold, 65536)
        self.maxDiff = None
        old_threshold = self._diffThreshold
        self._diffThreshold = 32
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))
        s = 'xxxxxxxxxxxxxxxx'
        with self.assertRaises(self.failureException) as (cm):
            self.assertEqual(s + 'a', s + 'b')
        self.assertIn('^', str(cm.exception))
        self.assertEqual(s + 'a', s + 'a')
        s = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

        def explodingTruncation(message, diff):
            raise SystemError('this should not be raised')

        old_truncate = self._truncateMessage
        self._truncateMessage = explodingTruncation
        self.addCleanup(lambda: setattr(self, '_truncateMessage', old_truncate))
        s1, s2 = s + 'a', s + 'b'
        with self.assertRaises(self.failureException) as (cm):
            self.assertEqual(s1, s2)
        self.assertNotIn('^', str(cm.exception))
        self.assertEqual(str(cm.exception), '%r != %r' % (s1, s2))
        self.assertEqual(s + 'a', s + 'a')

    def testAssertEqual_shorten(self):
        old_threshold = self._diffThreshold
        self._diffThreshold = 0
        self.addCleanup(lambda: setattr(self, '_diffThreshold', old_threshold))
        s = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        s1, s2 = s + 'a', s + 'b'
        with self.assertRaises(self.failureException) as (cm):
            self.assertEqual(s1, s2)
        c = 'xxxx[35 chars]xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        self.assertEqual(str(cm.exception), "'%sa' != '%sb'" % (c, c))
        self.assertEqual(s + 'a', s + 'a')
        p = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
        s1, s2 = s + 'a' + p, s + 'b' + p
        with self.assertRaises(self.failureException) as (cm):
            self.assertEqual(s1, s2)
        c = 'xxxx[85 chars]xxxxxxxxxxx'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, p, c, p))
        p = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
        s1, s2 = s + 'a' + p, s + 'b' + p
        with self.assertRaises(self.failureException) as (cm):
            self.assertEqual(s1, s2)
        c = 'xxxx[91 chars]xxxxx'
        d = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy[56 chars]yyyy'
        self.assertEqual(str(cm.exception), "'%sa%s' != '%sb%s'" % (c, d, c, d))

    def testAssertCountEqual(self):
        a = object()
        self.assertCountEqual([1, 2, 3], [3, 2, 1])
        self.assertCountEqual(['foo', 'bar', 'baz'], ['bar', 'baz', 'foo'])
        self.assertCountEqual(['a', 'a', 2, 2, 3], (a, 2, 3, a, 2))
        self.assertCountEqual([1, '2', 'a', 'a'], ['a', '2', True, 'a'])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         1, 2] + [3] * 100, [1] * 100 + [2, 3])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         1, '2', 'a', 'a'], ['a', '2', True, 1])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         10], [10, 11])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         10, 11], [10])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         10, 11, 10], [10, 11])
        self.assertCountEqual([[1, 2], [3, 4], 0], [False, [3, 4], [1, 2]])
        self.assertCountEqual(iter([1, 2, [], 3, 4]), iter([1, 2, [], 3, 4]))
        self.assertRaises(self.failureException, self.assertCountEqual, [], [divmod, 'x', 1, complex(0.0, 5.0), complex(0.0, 2.0), frozenset()])
        self.assertCountEqual([{'a': 1}, {'b': 2}], [{'b': 2}, {'a': 1}])
        self.assertCountEqual([1, 'x', divmod, []], [divmod, [], 'x', 1])
        self.assertRaises(self.failureException, self.assertCountEqual, [], [divmod, [], 'x', 1, complex(0.0, 5.0), complex(0.0, 2.0), set()])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         [
          1]], [[2]])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         1, 1, 2], [2, 1])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         1, 1, "'2'", "'a'", "'a'"], ['2', '2', True, 'a'])
        self.assertRaises(self.failureException, self.assertCountEqual, [
         1, {'b': 2}, None, True], [{'b': 2}, True, None])
        a = [
         {
          2, 4}, {1, 2}]
        b = a[::-1]
        self.assertCountEqual(a, b)
        diffs = set(unittest.util._count_diff_all_purpose('aaabccd', 'abbbcce'))
        expected = {(3, 1, 'a'), (1, 3, 'b'), (1, 0, 'd'), (0, 1, 'e')}
        self.assertEqual(diffs, expected)
        diffs = unittest.util._count_diff_all_purpose([[]], [])
        self.assertEqual(diffs, [(1, 0, [])])
        diffs = set(unittest.util._count_diff_hashable('aaabccd', 'abbbcce'))
        expected = {(3, 1, 'a'), (1, 3, 'b'), (1, 0, 'd'), (0, 1, 'e')}
        self.assertEqual(diffs, expected)

    def testAssertSetEqual(self):
        set1 = set()
        set2 = set()
        self.assertSetEqual(set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, None, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, [], set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, None)
        self.assertRaises(self.failureException, self.assertSetEqual, set1, [])
        set1 = set(['a'])
        set2 = set()
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a'])
        set2 = set(['a'])
        self.assertSetEqual(set1, set2)
        set1 = set(['a'])
        set2 = set(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a'])
        set2 = frozenset(['a', 'b'])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        set1 = set(['a', 'b'])
        set2 = frozenset(['a', 'b'])
        self.assertSetEqual(set1, set2)
        set1 = set()
        set2 = 'foo'
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)
        self.assertRaises(self.failureException, self.assertSetEqual, set2, set1)
        set1 = set([(0, 1), (2, 3)])
        set2 = set([(4, 5)])
        self.assertRaises(self.failureException, self.assertSetEqual, set1, set2)

    def testInequality(self):
        self.assertGreater(2, 1)
        self.assertGreaterEqual(2, 1)
        self.assertGreaterEqual(1, 1)
        self.assertLess(1, 2)
        self.assertLessEqual(1, 2)
        self.assertLessEqual(1, 1)
        self.assertRaises(self.failureException, self.assertGreater, 1, 2)
        self.assertRaises(self.failureException, self.assertGreater, 1, 1)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1, 2)
        self.assertRaises(self.failureException, self.assertLess, 2, 1)
        self.assertRaises(self.failureException, self.assertLess, 1, 1)
        self.assertRaises(self.failureException, self.assertLessEqual, 2, 1)
        self.assertGreater(1.1, 1.0)
        self.assertGreaterEqual(1.1, 1.0)
        self.assertGreaterEqual(1.0, 1.0)
        self.assertLess(1.0, 1.1)
        self.assertLessEqual(1.0, 1.1)
        self.assertLessEqual(1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertGreater, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertGreaterEqual, 1.0, 1.1)
        self.assertRaises(self.failureException, self.assertLess, 1.1, 1.0)
        self.assertRaises(self.failureException, self.assertLess, 1.0, 1.0)
        self.assertRaises(self.failureException, self.assertLessEqual, 1.1, 1.0)
        self.assertGreater('bug', 'ant')
        self.assertGreaterEqual('bug', 'ant')
        self.assertGreaterEqual('ant', 'ant')
        self.assertLess('ant', 'bug')
        self.assertLessEqual('ant', 'bug')
        self.assertLessEqual('ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertGreater, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, 'ant', 'bug')
        self.assertRaises(self.failureException, self.assertLess, 'bug', 'ant')
        self.assertRaises(self.failureException, self.assertLess, 'ant', 'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, 'bug', 'ant')
        self.assertGreater(b'bug', b'ant')
        self.assertGreaterEqual(b'bug', b'ant')
        self.assertGreaterEqual(b'ant', b'ant')
        self.assertLess(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'bug')
        self.assertLessEqual(b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'bug')
        self.assertRaises(self.failureException, self.assertGreater, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertGreaterEqual, b'ant', b'bug')
        self.assertRaises(self.failureException, self.assertLess, b'bug', b'ant')
        self.assertRaises(self.failureException, self.assertLess, b'ant', b'ant')
        self.assertRaises(self.failureException, self.assertLessEqual, b'bug', b'ant')

    def testAssertMultiLineEqual(self):
        sample_text = 'http://www.python.org/doc/2.3/lib/module-unittest.html\ntest case\n    A test case is the smallest unit of testing. [...]\n'
        revised_sample_text = 'http://www.python.org/doc/2.4.1/lib/module-unittest.html\ntest case\n    A test case is the smallest unit of testing. [...] You may provide your\n    own implementation that does not subclass from TestCase, of course.\n'
        sample_text_error = '- http://www.python.org/doc/2.3/lib/module-unittest.html\n?                             ^\n+ http://www.python.org/doc/2.4.1/lib/module-unittest.html\n?                             ^^^\n  test case\n-     A test case is the smallest unit of testing. [...]\n+     A test case is the smallest unit of testing. [...] You may provide your\n?                                                       +++++++++++++++++++++\n+     own implementation that does not subclass from TestCase, of course.\n'
        self.maxDiff = None
        try:
            self.assertMultiLineEqual(sample_text, revised_sample_text)
        except self.failureException as e:
            try:
                error = str(e).split('\n', 1)[1]
                self.assertEqual(sample_text_error, error)
            finally:
                e = None
                del e

    def testAssertEqualSingleLine(self):
        sample_text = 'laden swallows fly slowly'
        revised_sample_text = 'unladen swallows fly quickly'
        sample_text_error = '- laden swallows fly slowly\n?                    ^^^^\n+ unladen swallows fly quickly\n? ++                   ^^^^^\n'
        try:
            self.assertEqual(sample_text, revised_sample_text)
        except self.failureException as e:
            try:
                error = str(e).split('\n', 1)[1]
                self.assertEqual(sample_text_error, error)
            finally:
                e = None
                del e

    def testEqualityBytesWarning(self):
        if sys.flags.bytes_warning:

            def bytes_warning():
                return self.assertWarnsRegex(BytesWarning, 'Comparison between bytes and string')

        else:

            def bytes_warning():
                return contextlib.ExitStack()

        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertEqual('a', b'a')
        with bytes_warning():
            self.assertNotEqual('a', b'a')
        a = [0, 'a']
        b = [0, b'a']
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertListEqual(a, b)
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertTupleEqual(tuple(a), tuple(b))
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertSequenceEqual(a, tuple(b))
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertSequenceEqual(tuple(a), b)
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertSequenceEqual('a', b'a')
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertSetEqual(set(a), set(b))
        with self.assertRaises(self.failureException):
            self.assertListEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), b)
        a = [0, b'a']
        b = [0]
        with self.assertRaises(self.failureException):
            self.assertListEqual(a, b)
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(tuple(a), b)
        with self.assertRaises(self.failureException):
            self.assertSetEqual(set(a), set(b))
        a = [0]
        b = [0, b'a']
        with self.assertRaises(self.failureException):
            self.assertListEqual(a, b)
        with self.assertRaises(self.failureException):
            self.assertTupleEqual(tuple(a), tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(a, tuple(b))
        with self.assertRaises(self.failureException):
            self.assertSequenceEqual(tuple(a), b)
        with self.assertRaises(self.failureException):
            self.assertSetEqual(set(a), set(b))
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertDictEqual({'a': 0}, {b'a': 0})
        with self.assertRaises(self.failureException):
            self.assertDictEqual({}, {b'a': 0})
        with self.assertRaises(self.failureException):
            self.assertDictEqual({b'a': 0}, {})
        with self.assertRaises(self.failureException):
            self.assertCountEqual([b'a', b'a'], [b'a', b'a', b'a'])
        with bytes_warning():
            self.assertCountEqual(['a', b'a'], ['a', b'a'])
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertCountEqual(['a', 'a'], [b'a', b'a'])
        with bytes_warning():
            with self.assertRaises(self.failureException):
                self.assertCountEqual(['a', 'a', []], [b'a', b'a', []])

    def testAssertIsNone(self):
        self.assertIsNone(None)
        self.assertRaises(self.failureException, self.assertIsNone, False)
        self.assertIsNotNone('DjZoPloGears on Rails')
        self.assertRaises(self.failureException, self.assertIsNotNone, None)

    def testAssertRegex(self):
        self.assertRegex('asdfabasdf', 'ab+')
        self.assertRaises(self.failureException, self.assertRegex, 'saaas', 'aaaa')

    def testAssertRaisesCallable(self):

        class ExceptionMock(Exception):
            pass

        def Stub():
            raise ExceptionMock('We expect')

        self.assertRaises(ExceptionMock, Stub)
        self.assertRaises((ValueError, ExceptionMock), Stub)
        self.assertRaises(ValueError, int, '19', base=8)
        with self.assertRaises(self.failureException):
            self.assertRaises(ExceptionMock, lambda: 0)
        with self.assertWarns(DeprecationWarning):
            self.assertRaises(ExceptionMock, None)
        with self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    def testAssertRaisesContext(self):

        class ExceptionMock(Exception):
            pass

        def Stub():
            raise ExceptionMock('We expect')

        with self.assertRaises(ExceptionMock):
            Stub()
        with self.assertRaises((ValueError, ExceptionMock)) as (cm):
            Stub()
        self.assertIsInstance(cm.exception, ExceptionMock)
        self.assertEqual(cm.exception.args[0], 'We expect')
        with self.assertRaises(ValueError):
            int('19', base=8)
        with self.assertRaises(self.failureException):
            with self.assertRaises(ExceptionMock):
                pass
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertRaises(ExceptionMock, msg='foobar'):
                pass
        with self.assertWarnsRegex(DeprecationWarning, 'foobar'):
            with self.assertRaises(AssertionError):
                with self.assertRaises(ExceptionMock, foobar=42):
                    pass
        with self.assertRaises(ExceptionMock):
            self.assertRaises(ValueError, Stub)

    def testAssertRaisesNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertRaises()
        with self.assertRaises(TypeError):
            self.assertRaises(1)
        with self.assertRaises(TypeError):
            self.assertRaises(object)
        with self.assertRaises(TypeError):
            self.assertRaises((ValueError, 1))
        with self.assertRaises(TypeError):
            self.assertRaises((ValueError, object))

    def testAssertRaisesRefcount(self):

        def func():
            try:
                raise ValueError
            except ValueError:
                raise ValueError

        refcount = sys.getrefcount(func)
        self.assertRaises(ValueError, func)
        self.assertEqual(refcount, sys.getrefcount(func))

    def testAssertRaisesRegex(self):

        class ExceptionMock(Exception):
            pass

        def Stub():
            raise ExceptionMock('We expect')

        self.assertRaisesRegex(ExceptionMock, re.compile('expect$'), Stub)
        self.assertRaisesRegex(ExceptionMock, 'expect$', Stub)
        with self.assertWarns(DeprecationWarning):
            self.assertRaisesRegex(ExceptionMock, 'expect$', None)

    def testAssertNotRaisesRegex(self):
        self.assertRaisesRegex(self.failureException, '^Exception not raised by <lambda>$', self.assertRaisesRegex, Exception, re.compile('x'), lambda: None)
        self.assertRaisesRegex(self.failureException, '^Exception not raised by <lambda>$', self.assertRaisesRegex, Exception, 'x', lambda: None)
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertRaisesRegex(Exception, 'expect', msg='foobar'):
                pass
        with self.assertWarnsRegex(DeprecationWarning, 'foobar'):
            with self.assertRaises(AssertionError):
                with self.assertRaisesRegex(Exception, 'expect', foobar=42):
                    pass

    def testAssertRaisesRegexInvalidRegex(self):

        class MyExc(Exception):
            pass

        self.assertRaises(TypeError, self.assertRaisesRegex, MyExc, lambda: True)

    def testAssertWarnsRegexInvalidRegex(self):

        class MyWarn(Warning):
            pass

        self.assertRaises(TypeError, self.assertWarnsRegex, MyWarn, lambda: True)

    def testAssertRaisesRegexMismatch(self):

        def Stub():
            raise Exception('Unexpected')

        self.assertRaisesRegex(self.failureException, '"\\^Expected\\$" does not match "Unexpected"', self.assertRaisesRegex, Exception, '^Expected$', Stub)
        self.assertRaisesRegex(self.failureException, '"\\^Expected\\$" does not match "Unexpected"', self.assertRaisesRegex, Exception, re.compile('^Expected$'), Stub)

    def testAssertRaisesExcValue(self):

        class ExceptionMock(Exception):
            pass

        def Stub(foo):
            raise ExceptionMock(foo)

        v = 'particular value'
        ctx = self.assertRaises(ExceptionMock)
        with ctx:
            Stub(v)
        e = ctx.exception
        self.assertIsInstance(e, ExceptionMock)
        self.assertEqual(e.args[0], v)

    def testAssertRaisesRegexNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertRaisesRegex()
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(ValueError)
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(1, 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex(object, 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, 1), 'expect')
        with self.assertRaises(TypeError):
            self.assertRaisesRegex((ValueError, object), 'expect')

    def testAssertWarnsCallable(self):

        def _runtime_warn():
            warnings.warn('foo', RuntimeWarning)

        self.assertWarns(RuntimeWarning, _runtime_warn)
        self.assertWarns(RuntimeWarning, _runtime_warn)
        self.assertWarns((DeprecationWarning, RuntimeWarning), _runtime_warn)
        self.assertWarns(RuntimeWarning, (warnings.warn),
          'foo', category=RuntimeWarning)
        with self.assertRaises(self.failureException):
            self.assertWarns(RuntimeWarning, lambda: 0)
        with self.assertWarns(DeprecationWarning):
            self.assertWarns(RuntimeWarning, None)
        with warnings.catch_warnings():
            warnings.simplefilter('default', RuntimeWarning)
            with self.assertRaises(self.failureException):
                self.assertWarns(DeprecationWarning, _runtime_warn)
        with warnings.catch_warnings():
            warnings.simplefilter('error', RuntimeWarning)
            with self.assertRaises(RuntimeWarning):
                self.assertWarns(DeprecationWarning, _runtime_warn)

    def testAssertWarnsContext(self):

        def _runtime_warn():
            warnings.warn('foo', RuntimeWarning)

        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        with self.assertWarns(RuntimeWarning) as (cm):
            _runtime_warn()
        with self.assertWarns((DeprecationWarning, RuntimeWarning)) as (cm):
            _runtime_warn()
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], 'foo')
        self.assertIn('test_case.py', cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        with self.assertWarns(RuntimeWarning):
            _runtime_warn()
            _runtime_warn()
        with self.assertWarns(RuntimeWarning):
            warnings.warn('foo', category=RuntimeWarning)
        with self.assertRaises(self.failureException):
            with self.assertWarns(RuntimeWarning):
                pass
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertWarns(RuntimeWarning, msg='foobar'):
                pass
        with self.assertWarnsRegex(DeprecationWarning, 'foobar'):
            with self.assertRaises(AssertionError):
                with self.assertWarns(RuntimeWarning, foobar=42):
                    pass
        with warnings.catch_warnings():
            warnings.simplefilter('default', RuntimeWarning)
            with self.assertRaises(self.failureException):
                with self.assertWarns(DeprecationWarning):
                    _runtime_warn()
        with warnings.catch_warnings():
            warnings.simplefilter('error', RuntimeWarning)
            with self.assertRaises(RuntimeWarning):
                with self.assertWarns(DeprecationWarning):
                    _runtime_warn()

    def testAssertWarnsNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertWarns()
        with self.assertRaises(TypeError):
            self.assertWarns(1)
        with self.assertRaises(TypeError):
            self.assertWarns(object)
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, 1))
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, object))
        with self.assertRaises(TypeError):
            self.assertWarns((UserWarning, Exception))

    def testAssertWarnsRegexCallable(self):

        def _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)

        self.assertWarnsRegex(RuntimeWarning, 'o+', _runtime_warn, 'foox')
        with self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, 'o+', lambda: 0)
        with self.assertWarns(DeprecationWarning):
            self.assertWarnsRegex(RuntimeWarning, 'o+', None)
        with warnings.catch_warnings():
            warnings.simplefilter('default', RuntimeWarning)
            with self.assertRaises(self.failureException):
                self.assertWarnsRegex(DeprecationWarning, 'o+', _runtime_warn, 'foox')
        with self.assertRaises(self.failureException):
            self.assertWarnsRegex(RuntimeWarning, 'o+', _runtime_warn, 'barz')
        with warnings.catch_warnings():
            warnings.simplefilter('error', RuntimeWarning)
            with self.assertRaises((RuntimeWarning, self.failureException)):
                self.assertWarnsRegex(RuntimeWarning, 'o+', _runtime_warn, 'barz')

    def testAssertWarnsRegexContext(self):

        def _runtime_warn(msg):
            warnings.warn(msg, RuntimeWarning)

        _runtime_warn_lineno = inspect.getsourcelines(_runtime_warn)[1]
        with self.assertWarnsRegex(RuntimeWarning, 'o+') as (cm):
            _runtime_warn('foox')
        self.assertIsInstance(cm.warning, RuntimeWarning)
        self.assertEqual(cm.warning.args[0], 'foox')
        self.assertIn('test_case.py', cm.filename)
        self.assertEqual(cm.lineno, _runtime_warn_lineno + 1)
        with self.assertRaises(self.failureException):
            with self.assertWarnsRegex(RuntimeWarning, 'o+'):
                pass
        with self.assertRaisesRegex(self.failureException, 'foobar'):
            with self.assertWarnsRegex(RuntimeWarning, 'o+', msg='foobar'):
                pass
        with self.assertWarnsRegex(DeprecationWarning, 'foobar'):
            with self.assertRaises(AssertionError):
                with self.assertWarnsRegex(RuntimeWarning, 'o+', foobar=42):
                    pass
        with warnings.catch_warnings():
            warnings.simplefilter('default', RuntimeWarning)
            with self.assertRaises(self.failureException):
                with self.assertWarnsRegex(DeprecationWarning, 'o+'):
                    _runtime_warn('foox')
        with self.assertRaises(self.failureException):
            with self.assertWarnsRegex(RuntimeWarning, 'o+'):
                _runtime_warn('barz')
        with warnings.catch_warnings():
            warnings.simplefilter('error', RuntimeWarning)
            with self.assertRaises((RuntimeWarning, self.failureException)):
                with self.assertWarnsRegex(RuntimeWarning, 'o+'):
                    _runtime_warn('barz')

    def testAssertWarnsRegexNoExceptionType(self):
        with self.assertRaises(TypeError):
            self.assertWarnsRegex()
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(UserWarning)
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(1, 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex(object, 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, 1), 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, object), 'expect')
        with self.assertRaises(TypeError):
            self.assertWarnsRegex((UserWarning, Exception), 'expect')

    @contextlib.contextmanager
    def assertNoStderr(self):
        with captured_stderr() as (buf):
            yield
        self.assertEqual(buf.getvalue(), '')

    def assertLogRecords(self, records, matches):
        self.assertEqual(len(records), len(matches))
        for rec, match in zip(records, matches):
            self.assertIsInstance(rec, logging.LogRecord)
            for k, v in match.items():
                self.assertEqual(getattr(rec, k), v)

    def testAssertLogsDefaults(self):
        with self.assertNoStderr():
            with self.assertLogs() as (cm):
                log_foo.info('1')
                log_foobar.debug('2')
            self.assertEqual(cm.output, ['INFO:foo:1'])
            self.assertLogRecords(cm.records, [{'name': 'foo'}])

    def testAssertLogsTwoMatchingMessages(self):
        with self.assertNoStderr():
            with self.assertLogs() as (cm):
                log_foo.info('1')
                log_foobar.debug('2')
                log_quux.warning('3')
            self.assertEqual(cm.output, ['INFO:foo:1', 'WARNING:quux:3'])
            self.assertLogRecords(cm.records, [
             {'name': 'foo'}, {'name': 'quux'}])

    def checkAssertLogsPerLevel(self, level):
        with self.assertNoStderr():
            with self.assertLogs(level=level) as (cm):
                log_foo.warning('1')
                log_foobar.error('2')
                log_quux.critical('3')
            self.assertEqual(cm.output, ['ERROR:foo.bar:2', 'CRITICAL:quux:3'])
            self.assertLogRecords(cm.records, [
             {'name': 'foo.bar'}, {'name': 'quux'}])

    def testAssertLogsPerLevel(self):
        self.checkAssertLogsPerLevel(logging.ERROR)
        self.checkAssertLogsPerLevel('ERROR')

    def checkAssertLogsPerLogger(self, logger):
        with self.assertNoStderr():
            with self.assertLogs(level='DEBUG') as (outer_cm):
                with self.assertLogs(logger, level='DEBUG') as (cm):
                    log_foo.info('1')
                    log_foobar.debug('2')
                    log_quux.warning('3')
                self.assertEqual(cm.output, ['INFO:foo:1', 'DEBUG:foo.bar:2'])
                self.assertLogRecords(cm.records, [
                 {'name': 'foo'}, {'name': 'foo.bar'}])
            self.assertEqual(outer_cm.output, ['WARNING:quux:3'])

    def testAssertLogsPerLogger(self):
        self.checkAssertLogsPerLogger(logging.getLogger('foo'))
        self.checkAssertLogsPerLogger('foo')

    def testAssertLogsFailureNoLogs(self):
        with self.assertNoStderr():
            with self.assertRaises(self.failureException):
                with self.assertLogs():
                    pass

    def testAssertLogsFailureLevelTooHigh(self):
        with self.assertNoStderr():
            with self.assertRaises(self.failureException):
                with self.assertLogs(level='WARNING'):
                    log_foo.info('1')

    def testAssertLogsFailureMismatchingLogger(self):
        with self.assertLogs('quux', level='ERROR'):
            with self.assertRaises(self.failureException):
                with self.assertLogs('foo'):
                    log_quux.error('1')

    def testDeprecatedMethodNames(self):
        old = (
         (
          self.failIfEqual, (3, 5)),
         (
          self.assertNotEquals, (3, 5)),
         (
          self.failUnlessEqual, (3, 3)),
         (
          self.assertEquals, (3, 3)),
         (
          self.failUnlessAlmostEqual, (2.0, 2.0)),
         (
          self.assertAlmostEquals, (2.0, 2.0)),
         (
          self.failIfAlmostEqual, (3.0, 5.0)),
         (
          self.assertNotAlmostEquals, (3.0, 5.0)),
         (
          self.failUnless, (True, )),
         (
          self.assert_, (True, )),
         (
          self.failUnlessRaises, (TypeError, (lambda _: 3.14 + 'spam'))),
         (
          self.failIf, (False, )),
         (
          self.assertDictContainsSubset, (dict(a=1, b=2), dict(a=1, b=2, c=3))),
         (
          self.assertRaisesRegexp, (KeyError, 'foo', (lambda: {}['foo']))),
         (
          self.assertRegexpMatches, ('bar', 'bar')))
        for meth, args in old:
            with self.assertWarns(DeprecationWarning):
                meth(*args)

    def _testDeprecatedFailMethods(self):
        if sys.version_info[:2] < (3, 3):
            return
        deprecated_names = [
         "'failIfEqual'", "'failUnlessEqual'", "'failUnlessAlmostEqual'", 
         "'failIfAlmostEqual'", 
         "'failUnless'", "'failUnlessRaises'", "'failIf'", 
         "'assertDictContainsSubset'"]
        for deprecated_name in deprecated_names:
            with self.assertRaises(AttributeError):
                getattr(self, deprecated_name)

    def testDeepcopy(self):

        class TestableTest(unittest.TestCase):

            def testNothing(self):
                pass

        test = TestableTest('testNothing')
        deepcopy(test)

    def testPickle(self):
        test = unittest.TestCase('run')
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            pickled_test = pickle.dumps(test, protocol=protocol)
            unpickled_test = pickle.loads(pickled_test)
            self.assertEqual(test, unpickled_test)
            unpickled_test.assertEqual(set(), set())

    def testKeyboardInterrupt(self):

        def _raise(self=None):
            raise KeyboardInterrupt

        def nothing(self):
            pass

        class Test1(unittest.TestCase):
            test_something = _raise

        class Test2(unittest.TestCase):
            setUp = _raise
            test_something = nothing

        class Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _raise

        class Test4(unittest.TestCase):

            def test_something(self):
                self.addCleanup(_raise)

        for klass in (Test1, Test2, Test3, Test4):
            with self.assertRaises(KeyboardInterrupt):
                klass('test_something').run()

    def testSkippingEverywhere(self):

        def _skip(self=None):
            raise unittest.SkipTest('some reason')

        def nothing(self):
            pass

        class Test1(unittest.TestCase):
            test_something = _skip

        class Test2(unittest.TestCase):
            setUp = _skip
            test_something = nothing

        class Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _skip

        class Test4(unittest.TestCase):

            def test_something(self):
                self.addCleanup(_skip)

        for klass in (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.skipped), 1)
            self.assertEqual(result.testsRun, 1)

    def testSystemExit(self):

        def _raise(self=None):
            raise SystemExit

        def nothing(self):
            pass

        class Test1(unittest.TestCase):
            test_something = _raise

        class Test2(unittest.TestCase):
            setUp = _raise
            test_something = nothing

        class Test3(unittest.TestCase):
            test_something = nothing
            tearDown = _raise

        class Test4(unittest.TestCase):

            def test_something(self):
                self.addCleanup(_raise)

        for klass in (Test1, Test2, Test3, Test4):
            result = unittest.TestResult()
            klass('test_something').run(result)
            self.assertEqual(len(result.errors), 1)
            self.assertEqual(result.testsRun, 1)

    @support.cpython_only
    def testNoCycles(self):
        case = unittest.TestCase()
        wr = weakref.ref(case)
        with support.disable_gc():
            del case
            self.assertFalse(wr())

    def test_no_exception_leak(self):

        class MyException(Exception):
            ninstance = 0

            def __init__(self):
                MyException.ninstance += 1
                Exception.__init__(self)

            def __del__(self):
                MyException.ninstance -= 1

        class TestCase(unittest.TestCase):

            def test1(self):
                raise MyException()

            @unittest.expectedFailure
            def test2(self):
                raise MyException()

        for method_name in ('test1', 'test2'):
            testcase = TestCase(method_name)
            testcase.run()
            self.assertEqual(MyException.ninstance, 0)


if __name__ == '__main__':
    unittest.main()