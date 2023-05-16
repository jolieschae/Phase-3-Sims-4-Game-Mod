# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\mime\image.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1876 bytes
__all__ = [
 'MIMEImage']
import imghdr
from email import encoders
from email.mime.nonmultipart import MIMENonMultipart

class MIMEImage(MIMENonMultipart):

    def __init__(self, _imagedata, _subtype=None, _encoder=encoders.encode_base64, *, policy=None, **_params):
        if _subtype is None:
            _subtype = imghdr.what(None, _imagedata)
        if _subtype is None:
            raise TypeError('Could not guess image MIME subtype')
        (MIMENonMultipart.__init__)(self, 'image', _subtype, policy=policy, **_params)
        self.set_payload(_imagedata)
        _encoder(self)