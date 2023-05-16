# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\cp273.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 14439 bytes
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_table)

    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='cp273',
      encode=(Codec().encode),
      decode=(Codec().decode),
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamreader=StreamReader,
      streamwriter=StreamWriter)


decoding_table = '\x00\x01\x02\x03\x9c\t\x86\x7f\x97\x8d\x8e\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x9d\x85\x08\x87\x18\x19\x92\x8f\x1c\x1d\x1e\x1f\x80\x81\x82\x83\x84\n\x17\x1b\x88\x89\x8a\x8b\x8c\x05\x06\x07\x90\x91\x16\x93\x94\x95\x96\x04\x98\x99\x9a\x9b\x14\x15\x9e\x1a \xa0â{àáãåçñÄ.<(+!&éêëèíîïì~Ü$*);^-/Â[ÀÁÃÅÇÑö,%_>?øÉÊËÈÍÎÏÌ`:#§\'="Øabcdefghi«»ðýþ±°jklmnopqrªºæ¸Æ¤µßstuvwxyz¡¿ÐÝÞ®¢£¥·©@¶¼½¾¬|‾¨´×äABCDEFGHI\xadô¦òóõüJKLMNOPQR¹û}ùúÿÖ÷STUVWXYZ²Ô\\ÒÓÕ0123456789³Û]ÙÚ\x9f'
encoding_table = codecs.charmap_build(decoding_table)