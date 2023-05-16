# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\application.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1358 bytes
__all__ = [
 'MIMEApplication']
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart

class MIMEApplication(MIMENonMultipart):

    def __init__(self, _data, _subtype='octet-stream', _encoder=encoders.encode_base64, *, policy=None, **_params):
        if _subtype is None:
            raise TypeError('Invalid application MIME subtype')
        (MIMENonMultipart.__init__)(self, 'application', _subtype, policy=policy, **_params)
        self.set_payload(_data)
        _encoder(self)