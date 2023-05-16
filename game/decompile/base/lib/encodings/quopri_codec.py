# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\quopri_codec.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1581 bytes
import codecs, quopri
from io import BytesIO

def quopri_encode(input, errors='strict'):
    f = BytesIO(input)
    g = BytesIO()
    quopri.encode(f, g, quotetabs=True)
    return (g.getvalue(), len(input))


def quopri_decode(input, errors='strict'):
    f = BytesIO(input)
    g = BytesIO()
    quopri.decode(f, g)
    return (g.getvalue(), len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return quopri_encode(input, errors)

    def decode(self, input, errors='strict'):
        return quopri_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return quopri_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return quopri_decode(input, self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes


class StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes


def getregentry():
    return codecs.CodecInfo(name='quopri',
      encode=quopri_encode,
      decode=quopri_decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader,
      _is_text_encoding=False)