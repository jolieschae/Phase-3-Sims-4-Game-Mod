# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\base.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 946 bytes
__all__ = [
 'MIMEBase']
import email.policy
from email import message

class MIMEBase(message.Message):

    def __init__(self, _maintype, _subtype, *, policy=None, **_params):
        if policy is None:
            policy = email.policy.compat32
        message.Message.__init__(self, policy=policy)
        ctype = '%s/%s' % (_maintype, _subtype)
        (self.add_header)('Content-Type', ctype, **_params)
        self['MIME-Version'] = '1.0'