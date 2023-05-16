# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\internal\api_implementation.py
# Compiled at: 2013-10-04 12:43:25
# Size of source mod 2**32: 3550 bytes
__author__ = 'petar@google.com (Petar Petrov)'
import os
_implementation_type = os.getenv('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'python')
_implementation_type = 'cpp'
if _implementation_type != 'python':
    _implementation_type = 'cpp'
    try:
        from google.protobuf.internal import cpp_message
        _implementation_type = 'cpp'
    except ImportError as e:
        try:
            _implementation_type = 'python'
        finally:
            e = None
            del e

_implementation_version_str = os.getenv('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION', '1')
if _implementation_version_str not in ('1', '2'):
    raise ValueError("unsupported PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION_VERSION: '" + _implementation_version_str + "' (supported versions: 1, 2)")
_implementation_version = int(_implementation_version_str)

def Type():
    return _implementation_type


def Version():
    return _implementation_version