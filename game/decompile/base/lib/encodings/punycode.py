# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\punycode.py
# Compiled at: 2011-04-08 23:53:23
# Size of source mod 2**32: 7118 bytes
import codecs

def segregate(str):
    base = bytearray()
    extended = set()
    for c in str:
        if ord(c) < 128:
            base.append(ord(c))
        else:
            extended.add(c)

    extended = sorted(extended)
    return (bytes(base), extended)


def selective_len(str, max):
    res = 0
    for c in str:
        if ord(c) < max:
            res += 1

    return res


def selective_find(str, char, index, pos):
    l = len(str)
    while 1:
        pos += 1
        if pos == l:
            return (-1, -1)
        c = str[pos]
        if c == char:
            return (
             index + 1, pos)
        if c < char:
            index += 1


def insertion_unsort(str, extended):
    oldchar = 128
    result = []
    oldindex = -1
    for c in extended:
        index = pos = -1
        char = ord(c)
        curlen = selective_len(str, char)
        delta = (curlen + 1) * (char - oldchar)
        while True:
            index, pos = selective_find(str, c, index, pos)
            if index == -1:
                break
            delta += index - oldindex
            result.append(delta - 1)
            oldindex = index
            delta = 0

        oldchar = char

    return result


def T(j, bias):
    res = 36 * (j + 1) - bias
    if res < 1:
        return 1
    if res > 26:
        return 26
    return res


digits = b'abcdefghijklmnopqrstuvwxyz0123456789'

def generate_generalized_integer(N, bias):
    result = bytearray()
    j = 0
    while True:
        t = T(j, bias)
        if N < t:
            result.append(digits[N])
            return bytes(result)
        result.append(digits[t + (N - t) % (36 - t)])
        N = (N - t) // (36 - t)
        j += 1


def adapt(delta, first, numchars):
    if first:
        delta //= 700
    else:
        delta //= 2
    delta += delta // numchars
    divisions = 0
    while delta > 455:
        delta = delta // 35
        divisions += 36

    bias = divisions + 36 * delta // (delta + 38)
    return bias


def generate_integers(baselen, deltas):
    result = bytearray()
    bias = 72
    for points, delta in enumerate(deltas):
        s = generate_generalized_integer(delta, bias)
        result.extend(s)
        bias = adapt(delta, points == 0, baselen + points + 1)

    return bytes(result)


def punycode_encode(text):
    base, extended = segregate(text)
    deltas = insertion_unsort(text, extended)
    extended = generate_integers(len(base), deltas)
    if base:
        return base + b'-' + extended
    return extended


def decode_generalized_number(extended, extpos, bias, errors):
    result = 0
    w = 1
    j = 0
    while True:
        try:
            char = ord(extended[extpos])
        except IndexError:
            if errors == 'strict':
                raise UnicodeError('incomplete punicode string')
            return (
             extpos + 1, None)
        else:
            extpos += 1
            if 65 <= char <= 90:
                digit = char - 65
            else:
                if 48 <= char <= 57:
                    digit = char - 22
                else:
                    if errors == 'strict':
                        raise UnicodeError("Invalid extended code point '%s'" % extended[extpos])
                    else:
                        return (
                         extpos, None)
            t = T(j, bias)
            result += digit * w
            if digit < t:
                return (
                 extpos, result)
            w = w * (36 - t)
            j += 1


def insertion_sort(base, extended, errors):
    char = 128
    pos = -1
    bias = 72
    extpos = 0
    while extpos < len(extended):
        newpos, delta = decode_generalized_number(extended, extpos, bias, errors)
        if delta is None:
            return base
        pos += delta + 1
        char += pos // (len(base) + 1)
        if char > 1114111:
            if errors == 'strict':
                raise UnicodeError('Invalid character U+%x' % char)
            char = ord('?')
        pos = pos % (len(base) + 1)
        base = base[:pos] + chr(char) + base[pos:]
        bias = adapt(delta, extpos == 0, len(base))
        extpos = newpos

    return base


def punycode_decode(text, errors):
    if isinstance(text, str):
        text = text.encode('ascii')
    else:
        if isinstance(text, memoryview):
            text = bytes(text)
        pos = text.rfind(b'-')
        if pos == -1:
            base = ''
            extended = str(text, 'ascii').upper()
        else:
            base = str(text[:pos], 'ascii', errors)
        extended = str(text[pos + 1:], 'ascii').upper()
    return insertion_sort(base, extended, errors)


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        res = punycode_encode(input)
        return (res, len(input))

    def decode(self, input, errors='strict'):
        if errors not in ('strict', 'replace', 'ignore'):
            raise UnicodeError('Unsupported error handling ' + errors)
        res = punycode_decode(input, errors)
        return (res, len(input))


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return punycode_encode(input)


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        if self.errors not in ('strict', 'replace', 'ignore'):
            raise UnicodeError('Unsupported error handling ' + self.errors)
        return punycode_decode(input, self.errors)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='punycode',
      encode=(Codec().encode),
      decode=(Codec().decode),
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader)