# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\iterators.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2206 bytes
__all__ = [
 'body_line_iterator',
 'typed_subpart_iterator',
 'walk']
import sys
from io import StringIO

def walk(self):
    yield self
    if self.is_multipart():
        for subpart in self.get_payload():
            yield from subpart.walk()


def body_line_iterator(msg, decode=False):
    for subpart in msg.walk():
        payload = subpart.get_payload(decode=decode)
        if isinstance(payload, str):
            yield from StringIO(payload)

    if False:
        yield None


def typed_subpart_iterator(msg, maintype='text', subtype=None):
    for subpart in msg.walk():
        if not subpart.get_content_maintype() == maintype or subtype is None or subpart.get_content_subtype() == subtype:
            yield subpart


def _structure(msg, fp=None, level=0, include_default=False):
    if fp is None:
        fp = sys.stdout
    else:
        tab = ' ' * (level * 4)
        print((tab + msg.get_content_type()), end='', file=fp)
        if include_default:
            print((' [%s]' % msg.get_default_type()), file=fp)
        else:
            print(file=fp)
    if msg.is_multipart():
        for subpart in msg.get_payload():
            _structure(subpart, fp, level + 1, include_default)