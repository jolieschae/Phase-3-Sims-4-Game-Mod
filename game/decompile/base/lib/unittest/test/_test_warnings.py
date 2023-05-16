# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\_test_warnings.py
# Compiled at: 2013-04-05 19:16:42
# Size of source mod 2**32: 2377 bytes
import sys, unittest, warnings

def warnfun():
    warnings.warn('rw', RuntimeWarning)


class TestWarnings(unittest.TestCase):

    def test_assert(self):
        self.assertEquals(4, 4)
        self.assertEquals(4, 4)
        self.assertEquals(4, 4)

    def test_fail(self):
        self.failUnless(1)
        self.failUnless(True)

    def test_other_unittest(self):
        self.assertAlmostEqual(4, 4)
        self.assertNotAlmostEqual(8, 2)

    def test_deprecation(self):
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)
        warnings.warn('dw', DeprecationWarning)

    def test_import(self):
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)
        warnings.warn('iw', ImportWarning)

    def test_warning(self):
        warnings.warn('uw')
        warnings.warn('uw')
        warnings.warn('uw')

    def test_function(self):
        warnfun()
        warnfun()
        warnfun()


if __name__ == '__main__':
    with warnings.catch_warnings(record=True) as (ws):
        if len(sys.argv) == 2:
            unittest.main(exit=False, warnings=(sys.argv.pop()))
        else:
            unittest.main(exit=False)
    for w in ws:
        print(w.message)