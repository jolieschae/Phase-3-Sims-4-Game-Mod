# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\secrets.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2111 bytes
__all__ = [
 "'choice'", "'randbelow'", "'randbits'", "'SystemRandom'", 
 "'token_bytes'", 
 "'token_hex'", "'token_urlsafe'", 
 "'compare_digest'"]
import base64, binascii, os
from hmac import compare_digest
from random import SystemRandom
_sysrand = SystemRandom()
randbits = _sysrand.getrandbits
choice = _sysrand.choice

def randbelow(exclusive_upper_bound):
    if exclusive_upper_bound <= 0:
        raise ValueError('Upper bound must be positive.')
    return _sysrand._randbelow(exclusive_upper_bound)


DEFAULT_ENTROPY = 32

def token_bytes(nbytes=None):
    if nbytes is None:
        nbytes = DEFAULT_ENTROPY
    return os.urandom(nbytes)


def token_hex(nbytes=None):
    return binascii.hexlify(token_bytes(nbytes)).decode('ascii')


def token_urlsafe(nbytes=None):
    tok = token_bytes(nbytes)
    return base64.urlsafe_b64encode(tok).rstrip(b'=').decode('ascii')