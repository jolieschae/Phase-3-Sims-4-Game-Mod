# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\__init__.py
# Compiled at: 2013-04-05 19:16:42
# Size of source mod 2**32: 482 bytes
import os, sys, unittest
here = os.path.dirname(__file__)
loader = unittest.defaultTestLoader

def load_tests(*args):
    suite = unittest.TestSuite()
    for fn in os.listdir(here):
        if fn.startswith('test') and fn.endswith('.py'):
            modname = 'unittest.test.testmock.' + fn[:-3]
            __import__(modname)
            module = sys.modules[modname]
            suite.addTest(loader.loadTestsFromModule(module))

    return suite