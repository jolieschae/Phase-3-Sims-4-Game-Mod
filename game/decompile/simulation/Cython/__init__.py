# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\Cython\__init__.py
# Compiled at: 2020-02-05 22:30:39
# Size of source mod 2**32: 370 bytes
from __future__ import absolute_import
from .Shadow import __version__
from .Shadow import *

def load_ipython_extension(ip):
    from Build.IpythonMagic import CythonMagics
    ip.register_magics(CythonMagics)