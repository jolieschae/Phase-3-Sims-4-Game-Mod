# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\base64_codec.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1588 bytes
import codecs, base64

def base64_encode(input, errors='strict'):
    return (
     base64.encodebytes(input), len(input))


def base64_decode(input, errors='strict'):
    return (
     base64.decodebytes(input), len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return base64_encode(input, errors)

    def decode(self, input, errors='strict'):
        return base64_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return base64.encodebytes(input)


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return base64.decodebytes(input)


class StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes


class StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes


def getregentry():
    return codecs.CodecInfo(name='base64',
      encode=base64_encode,
      decode=base64_decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader,
      _is_text_encoding=False)