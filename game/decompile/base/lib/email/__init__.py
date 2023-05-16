# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1828 bytes
__all__ = [
 "'base64mime'", 
 "'charset'", 
 "'encoders'", 
 "'errors'", 
 "'feedparser'", 
 "'generator'", 
 "'header'", 
 "'iterators'", 
 "'message'", 
 "'message_from_file'", 
 "'message_from_binary_file'", 
 "'message_from_string'", 
 "'message_from_bytes'", 
 "'mime'", 
 "'parser'", 
 "'quoprimime'", 
 "'utils'"]

def message_from_string(s, *args, **kws):
    from email.parser import Parser
    return Parser(*args, **kws).parsestr(s)


def message_from_bytes(s, *args, **kws):
    from email.parser import BytesParser
    return BytesParser(*args, **kws).parsebytes(s)


def message_from_file(fp, *args, **kws):
    from email.parser import Parser
    return Parser(*args, **kws).parse(fp)


def message_from_binary_file(fp, *args, **kws):
    from email.parser import BytesParser
    return BytesParser(*args, **kws).parse(fp)