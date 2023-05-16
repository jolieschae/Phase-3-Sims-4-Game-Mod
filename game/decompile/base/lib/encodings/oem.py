# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\oem.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1060 bytes
from codecs import oem_encode, oem_decode
import codecs
encode = oem_encode

def decode(input, errors='strict'):
    return oem_decode(input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return oem_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = oem_decode


class StreamWriter(codecs.StreamWriter):
    encode = oem_encode


class StreamReader(codecs.StreamReader):
    decode = oem_decode


def getregentry():
    return codecs.CodecInfo(name='oem',
      encode=encode,
      decode=decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)