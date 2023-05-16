# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\cp65001.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1149 bytes
import codecs, functools
if not hasattr(codecs, 'code_page_encode'):
    raise LookupError('cp65001 encoding is only available on Windows')
encode = functools.partial(codecs.code_page_encode, 65001)
_decode = functools.partial(codecs.code_page_decode, 65001)

def decode(input, errors='strict'):
    return codecs.code_page_decode(65001, input, errors, True)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return encode(input, self.errors)[0]


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    _buffer_decode = _decode


class StreamWriter(codecs.StreamWriter):
    encode = encode


class StreamReader(codecs.StreamReader):
    decode = _decode


def getregentry():
    return codecs.CodecInfo(name='cp65001',
      encode=encode,
      decode=decode,
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)