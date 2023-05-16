# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\bz2_codec.py
# Compiled at: 2014-06-01 03:44:05
# Size of source mod 2**32: 2327 bytes
import codecs, bz2

def bz2_encode(input, errors='strict'):
    return (
     bz2.compress(input), len(input))


def bz2_decode(input, errors='strict'):
    return (
     bz2.decompress(input), len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return bz2_encode(input, errors)

    def decode(self, input, errors='strict'):
        return bz2_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.compressobj = bz2.BZ2Compressor()

    def encode(self, input, final=False):
        if final:
            c = self.compressobj.compress(input)
            return c + self.compressobj.flush()
        return self.compressobj.compress(input)

    def reset(self):
        self.compressobj = bz2.BZ2Compressor()


class IncrementalDecoder(codecs.IncrementalDecoder):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.decompressobj = bz2.BZ2Decompressor()

    def decode(self, input, final=False):
        try:
            return self.decompressobj.decompress(input)
        except EOFError:
            return ''

    def reset(self):
        self.decompressobj = bz2.BZ2Decompressor()


class StreamWriter(Codec, codecs.StreamWriter):
    charbuffertype = bytes


class StreamReader(Codec, codecs.StreamReader):
    charbuffertype = bytes


def getregentry():
    return codecs.CodecInfo(name='bz2',
      encode=bz2_encode,
      decode=bz2_decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader,
      _is_text_encoding=False)