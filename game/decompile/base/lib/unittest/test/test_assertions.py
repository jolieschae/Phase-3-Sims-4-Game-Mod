# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\test_assertions.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 17491 bytes
import datetime, warnings, weakref, unittest
from itertools import product

class Test_Assertions(unittest.TestCase):

    def test_AlmostEqual(self):
        self.assertAlmostEqual(1.00000001, 1.0)
        self.assertNotAlmostEqual(1.0000001, 1.0)
        self.assertRaises(self.failureException, self.assertAlmostEqual, 1.0000001, 1.0)
        self.assertRaises(self.failureException, self.assertNotAlmostEqual, 1.00000001, 1.0)
        self.assertAlmostEqual(1.1, 1.0, places=0)
        self.assertRaises((self.failureException), (self.assertAlmostEqual),
          1.1, 1.0, places=1)
        self.assertAlmostEqual(0, complex(0.1, 0.1), places=0)
        self.assertNotAlmostEqual(0, complex(0.1, 0.1), places=1)
        self.assertRaises((self.failureException), (self.assertAlmostEqual),
          0, complex(0.1, 0.1), places=1)
        self.assertRaises((self.failureException), (self.assertNotAlmostEqual),
          0, complex(0.1, 0.1), places=0)
        self.assertAlmostEqual(float('inf'), float('inf'))
        self.assertRaises(self.failureException, self.assertNotAlmostEqual, float('inf'), float('inf'))

    def test_AmostEqualWithDelta(self):
        self.assertAlmostEqual(1.1, 1.0, delta=0.5)
        self.assertAlmostEqual(1.0, 1.1, delta=0.5)
        self.assertNotAlmostEqual(1.1, 1.0, delta=0.05)
        self.assertNotAlmostEqual(1.0, 1.1, delta=0.05)
        self.assertAlmostEqual(1.0, 1.0, delta=0.5)
        self.assertRaises((self.failureException), (self.assertNotAlmostEqual), 1.0,
          1.0, delta=0.5)
        self.assertRaises((self.failureException), (self.assertAlmostEqual), 1.1,
          1.0, delta=0.05)
        self.assertRaises((self.failureException), (self.assertNotAlmostEqual), 1.1,
          1.0, delta=0.5)
        self.assertRaises(TypeError, (self.assertAlmostEqual), 1.1,
          1.0, places=2, delta=2)
        self.assertRaises(TypeError, (self.assertNotAlmostEqual), 1.1,
          1.0, places=2, delta=2)
        first = datetime.datetime.now()
        second = first + datetime.timedelta(seconds=10)
        self.assertAlmostEqual(first, second, delta=datetime.timedelta(seconds=20))
        self.assertNotAlmostEqual(first, second, delta=datetime.timedelta(seconds=5))

    def test_assertRaises(self):

        def _raise(e):
            raise e

        self.assertRaises(KeyError, _raise, KeyError)
        self.assertRaises(KeyError, _raise, KeyError('key'))
        try:
            self.assertRaises(KeyError, lambda: None)
        except self.failureException as e:
            try:
                self.assertIn('KeyError not raised', str(e))
            finally:
                e = None
                del e

        else:
            self.fail("assertRaises() didn't fail")
        try:
            self.assertRaises(KeyError, _raise, ValueError)
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")
        with self.assertRaises(KeyError) as (cm):
            try:
                raise KeyError
            except Exception as e:
                try:
                    exc = e
                    raise
                finally:
                    e = None
                    del e

        self.assertIs(cm.exception, exc)
        with self.assertRaises(KeyError):
            raise KeyError('key')
        try:
            with self.assertRaises(KeyError):
                pass
        except self.failureException as e:
            try:
                self.assertIn('KeyError not raised', str(e))
            finally:
                e = None
                del e

        else:
            self.fail("assertRaises() didn't fail")
        try:
            with self.assertRaises(KeyError):
                raise ValueError
        except ValueError:
            pass
        else:
            self.fail("assertRaises() didn't let exception pass through")

    def test_assertRaises_frames_survival(self):

        class A:
            pass

        wr = None

        class Foo(unittest.TestCase):

            def foo(self):
                nonlocal wr
                a = A()
                wr = weakref.ref(a)
                try:
                    raise OSError
                except OSError:
                    raise ValueError

            def test_functional(self):
                self.assertRaises(ValueError, self.foo)

            def test_with(self):
                with self.assertRaises(ValueError):
                    self.foo()

        Foo('test_functional').run()
        self.assertIsNone(wr())
        Foo('test_with').run()
        self.assertIsNone(wr())

    def testAssertNotRegex(self):
        self.assertNotRegex('Ala ma kota', 'r+')
        try:
            self.assertNotRegex('Ala ma kota', 'k.t', 'Message')
        except self.failureException as e:
            try:
                self.assertIn('Message', e.args[0])
            finally:
                e = None
                del e

        else:
            self.fail('assertNotRegex should have failed.')


class TestLongMessage(unittest.TestCase):

    def setUp(self):

        class TestableTestFalse(unittest.TestCase):
            longMessage = False
            failureException = self.failureException

            def testTest(self):
                pass

        class TestableTestTrue(unittest.TestCase):
            longMessage = True
            failureException = self.failureException

            def testTest(self):
                pass

        self.testableTrue = TestableTestTrue('testTest')
        self.testableFalse = TestableTestFalse('testTest')

    def testDefault(self):
        self.assertTrue(unittest.TestCase.longMessage)

    def test_formatMsg(self):
        self.assertEqual(self.testableFalse._formatMessage(None, 'foo'), 'foo')
        self.assertEqual(self.testableFalse._formatMessage('foo', 'bar'), 'foo')
        self.assertEqual(self.testableTrue._formatMessage(None, 'foo'), 'foo')
        self.assertEqual(self.testableTrue._formatMessage('foo', 'bar'), 'bar : foo')
        self.testableTrue._formatMessage(object(), 'foo')

    def test_formatMessage_unicode_error(self):
        one = ''.join((chr(i) for i in range(255)))
        self.testableTrue._formatMessage(one, '�')

    def assertMessages(self, methodName, args, errors):

        def getMethod(i):
            useTestableFalse = i < 2
            if useTestableFalse:
                test = self.testableFalse
            else:
                test = self.testableTrue
            return getattr(test, methodName)

        for i, expected_regex in enumerate(errors):
            testMethod = getMethod(i)
            kwargs = {}
            withMsg = i % 2
            if withMsg:
                kwargs = {'msg': 'oops'}
            with self.assertRaisesRegex((self.failureException), expected_regex=expected_regex):
                testMethod(*args, **kwargs)

    def testAssertTrue(self):
        self.assertMessages('assertTrue', (False, ), [
         '^False is not true$', '^oops$', '^False is not true$',
         '^False is not true : oops$'])

    def testAssertFalse(self):
        self.assertMessages('assertFalse', (True, ), [
         '^True is not false$', '^oops$', '^True is not false$',
         '^True is not false : oops$'])

    def testNotEqual(self):
        self.assertMessages('assertNotEqual', (1, 1), [
         '^1 == 1$', '^oops$', '^1 == 1$',
         '^1 == 1 : oops$'])

    def testAlmostEqual(self):
        self.assertMessages('assertAlmostEqual', (1, 2), [
         '^1 != 2 within 7 places \\(1 difference\\)$', '^oops$',
         '^1 != 2 within 7 places \\(1 difference\\)$',
         '^1 != 2 within 7 places \\(1 difference\\) : oops$'])

    def testNotAlmostEqual(self):
        self.assertMessages('assertNotAlmostEqual', (1, 1), [
         '^1 == 1 within 7 places$', '^oops$',
         '^1 == 1 within 7 places$', '^1 == 1 within 7 places : oops$'])

    def test_baseAssertEqual(self):
        self.assertMessages('_baseAssertEqual', (1, 2), [
         '^1 != 2$', '^oops$', '^1 != 2$', '^1 != 2 : oops$'])

    def testAssertSequenceEqual(self):
        self.assertMessages('assertSequenceEqual', ([], [None]), [
         '\\+ \\[None\\]$', '^oops$', '\\+ \\[None\\]$',
         '\\+ \\[None\\] : oops$'])

    def testAssertSetEqual(self):
        self.assertMessages('assertSetEqual', (set(), set([None])), [
         'None$', '^oops$', 'None$',
         'None : oops$'])

    def testAssertIn(self):
        self.assertMessages('assertIn', (None, []), [
         '^None not found in \\[\\]$', '^oops$',
         '^None not found in \\[\\]$',
         '^None not found in \\[\\] : oops$'])

    def testAssertNotIn(self):
        self.assertMessages('assertNotIn', (None, [None]), [
         '^None unexpectedly found in \\[None\\]$', '^oops$',
         '^None unexpectedly found in \\[None\\]$',
         '^None unexpectedly found in \\[None\\] : oops$'])

    def testAssertDictEqual(self):
        self.assertMessages('assertDictEqual', ({}, {'key': 'value'}), [
         "\\+ \\{'key': 'value'\\}$", '^oops$',
         "\\+ \\{'key': 'value'\\}$",
         "\\+ \\{'key': 'value'\\} : oops$"])

    def testAssertDictContainsSubset(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertMessages('assertDictContainsSubset', ({'key': 'value'}, {}), [
             "^Missing: 'key'$", '^oops$',
             "^Missing: 'key'$",
             "^Missing: 'key' : oops$"])

    def testAssertMultiLineEqual(self):
        self.assertMessages('assertMultiLineEqual', ('', 'foo'), [
         '\\+ foo$', '^oops$',
         '\\+ foo$',
         '\\+ foo : oops$'])

    def testAssertLess(self):
        self.assertMessages('assertLess', (2, 1), [
         '^2 not less than 1$', '^oops$',
         '^2 not less than 1$', '^2 not less than 1 : oops$'])

    def testAssertLessEqual(self):
        self.assertMessages('assertLessEqual', (2, 1), [
         '^2 not less than or equal to 1$', '^oops$',
         '^2 not less than or equal to 1$',
         '^2 not less than or equal to 1 : oops$'])

    def testAssertGreater(self):
        self.assertMessages('assertGreater', (1, 2), [
         '^1 not greater than 2$', '^oops$',
         '^1 not greater than 2$',
         '^1 not greater than 2 : oops$'])

    def testAssertGreaterEqual(self):
        self.assertMessages('assertGreaterEqual', (1, 2), [
         '^1 not greater than or equal to 2$', '^oops$',
         '^1 not greater than or equal to 2$',
         '^1 not greater than or equal to 2 : oops$'])

    def testAssertIsNone(self):
        self.assertMessages('assertIsNone', ('not None', ), [
         "^'not None' is not None$", '^oops$',
         "^'not None' is not None$",
         "^'not None' is not None : oops$"])

    def testAssertIsNotNone(self):
        self.assertMessages('assertIsNotNone', (None, ), [
         '^unexpectedly None$', '^oops$',
         '^unexpectedly None$',
         '^unexpectedly None : oops$'])

    def testAssertIs(self):
        self.assertMessages('assertIs', (None, 'foo'), [
         "^None is not 'foo'$", '^oops$',
         "^None is not 'foo'$",
         "^None is not 'foo' : oops$"])

    def testAssertIsNot(self):
        self.assertMessages('assertIsNot', (None, None), [
         '^unexpectedly identical: None$', '^oops$',
         '^unexpectedly identical: None$',
         '^unexpectedly identical: None : oops$'])

    def testAssertRegex(self):
        self.assertMessages('assertRegex', ('foo', 'bar'), [
         "^Regex didn't match:",
         '^oops$',
         "^Regex didn't match:",
         "^Regex didn't match: (.*) : oops$"])

    def testAssertNotRegex(self):
        self.assertMessages('assertNotRegex', ('foo', 'foo'), [
         '^Regex matched:',
         '^oops$',
         '^Regex matched:',
         '^Regex matched: (.*) : oops$'])

    def assertMessagesCM(self, methodName, args, func, errors):
        p = product((self.testableFalse, self.testableTrue), ({}, {'msg': 'oops'}))
        for (cls, kwargs), err in zip(p, errors):
            method = getattr(cls, methodName)
            with self.assertRaisesRegex(cls.failureException, err):
                with method(*args, **kwargs) as (cm):
                    func()

    def testAssertRaises(self):
        self.assertMessagesCM('assertRaises', (TypeError,), lambda: None, [
         '^TypeError not raised$', '^oops$',
         '^TypeError not raised$',
         '^TypeError not raised : oops$'])

    def testAssertRaisesRegex(self):
        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'unused regex'), lambda: None, [
         '^TypeError not raised$', '^oops$',
         '^TypeError not raised$',
         '^TypeError not raised : oops$'])

        def raise_wrong_message():
            raise TypeError('foo')

        self.assertMessagesCM('assertRaisesRegex', (TypeError, 'regex'), raise_wrong_message, [
         '^"regex" does not match "foo"$', '^oops$',
         '^"regex" does not match "foo"$',
         '^"regex" does not match "foo" : oops$'])

    def testAssertWarns(self):
        self.assertMessagesCM('assertWarns', (UserWarning,), lambda: None, [
         '^UserWarning not triggered$', '^oops$',
         '^UserWarning not triggered$',
         '^UserWarning not triggered : oops$'])

    def testAssertWarnsRegex(self):
        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'unused regex'), lambda: None, [
         '^UserWarning not triggered$', '^oops$',
         '^UserWarning not triggered$',
         '^UserWarning not triggered : oops$'])

        def raise_wrong_message():
            warnings.warn('foo')

        self.assertMessagesCM('assertWarnsRegex', (UserWarning, 'regex'), raise_wrong_message, [
         '^"regex" does not match "foo"$', '^oops$',
         '^"regex" does not match "foo"$',
         '^"regex" does not match "foo" : oops$'])


if __name__ == '__main__':
    unittest.main()