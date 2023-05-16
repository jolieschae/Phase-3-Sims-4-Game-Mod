# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\decimal.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 331 bytes
try:
    from _decimal import *
    from _decimal import __doc__
    from _decimal import __version__
    from _decimal import __libmpdec_version__
except ImportError:
    from _pydecimal import *
    from _pydecimal import __doc__
    from _pydecimal import __version__
    from _pydecimal import __libmpdec_version__