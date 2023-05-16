# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\test\testmock\__main__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 641 bytes
import os, unittest

def load_tests(loader, standard_tests, pattern):
    this_dir = os.path.dirname(__file__)
    pattern = pattern or 'test*.py'
    top_level_dir = os.path.dirname(os.path.dirname(os.path.dirname(this_dir)))
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern, top_level_dir=top_level_dir)
    standard_tests.addTests(package_tests)
    return standard_tests


if __name__ == '__main__':
    unittest.main()