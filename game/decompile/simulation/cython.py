# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\cython.py
# Compiled at: 2020-02-05 22:30:39
# Size of source mod 2**32: 544 bytes
if __name__ == '__main__':
    import os, sys
    cythonpath, _ = os.path.split(os.path.realpath(__file__))
    sys.path.insert(0, cythonpath)
    from Cython.Compiler.Main import main
    main(command_line=1)
else:
    from Cython.Shadow import *
    from Cython import __version__
    from Cython import load_ipython_extension