# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\testsentinel.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1366 bytes
import unittest, copy, pickle
from unittest.mock import sentinel, DEFAULT

class SentinelTest(unittest.TestCase):

    def testSentinels(self):
        self.assertEqual(sentinel.whatever, sentinel.whatever, 'sentinel not stored')
        self.assertNotEqual(sentinel.whatever, sentinel.whateverelse, 'sentinel should be unique')

    def testSentinelName(self):
        self.assertEqual(str(sentinel.whatever), 'sentinel.whatever', 'sentinel name incorrect')

    def testDEFAULT(self):
        self.assertIs(DEFAULT, sentinel.DEFAULT)

    def testBases(self):
        self.assertRaises(AttributeError, lambda: sentinel.__bases__)

    def testPickle(self):
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            with self.subTest(protocol=proto):
                pickled = pickle.dumps(sentinel.whatever, proto)
                unpickled = pickle.loads(pickled)
                self.assertIs(unpickled, sentinel.whatever)

    def testCopy(self):
        self.assertIs(copy.copy(sentinel.whatever), sentinel.whatever)
        self.assertIs(copy.deepcopy(sentinel.whatever), sentinel.whatever)


if __name__ == '__main__':
    unittest.main()