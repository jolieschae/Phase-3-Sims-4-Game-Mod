# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\__main__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 490 bytes
import sys
if sys.argv[0].endswith('__main__.py'):
    import os.path
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + ' -m unittest'
    del os
__unittest = True
from .main import main
main(module=None)