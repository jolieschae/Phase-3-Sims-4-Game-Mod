# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3221 bytes
__all__ = [
 "'TestResult'", "'TestCase'", "'TestSuite'", 
 "'TextTestRunner'", "'TestLoader'", 
 "'FunctionTestCase'", "'main'", 
 "'defaultTestLoader'", "'SkipTest'", "'skip'", 
 "'skipIf'", "'skipUnless'", 
 "'expectedFailure'", "'TextTestResult'", "'installHandler'", 
 "'registerResult'", 
 "'removeResult'", "'removeHandler'"]
__all__.extend(['getTestCaseNames', 'makeSuite', 'findTestCases'])
__unittest = True
from .result import TestResult
from .case import TestCase, FunctionTestCase, SkipTest, skip, skipIf, skipUnless, expectedFailure
from .suite import BaseTestSuite, TestSuite
from .loader import TestLoader, defaultTestLoader, makeSuite, getTestCaseNames, findTestCases
from .main import TestProgram, main
from .runner import TextTestRunner, TextTestResult
from .signals import installHandler, registerResult, removeResult, removeHandler
_TextTestResult = TextTestResult

def load_tests(loader, tests, pattern):
    import os.path
    this_dir = os.path.dirname(__file__)
    return loader.discover(start_dir=this_dir, pattern=pattern)