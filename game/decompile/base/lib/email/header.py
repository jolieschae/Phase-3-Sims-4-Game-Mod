# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\header.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 24664 bytes
__all__ = [
 'Header',
 'decode_header',
 'make_header']
import re, binascii, email.quoprimime, email.base64mime
from email.errors import HeaderParseError
from email import charset as _charset
Charset = _charset.Charset
NL = '\n'
SPACE = ' '
BSPACE = b' '
SPACE8 = '        '
EMPTYSTRING = ''
MAXLINELEN = 78
FWS = ' \t'
USASCII = Charset('us-ascii')
UTF8 = Charset('utf-8')
ecre = re.compile('\n  =\\?                   # literal =?\n  (?P<charset>[^?]*?)   # non-greedy up to the next ? is the charset\n  \\?                    # literal ?\n  (?P<encoding>[qQbB])  # either a "q" or a "b", case insensitive\n  \\?                    # literal ?\n  (?P<encoded>.*?)      # non-greedy up to the next ?= is the encoded string\n  \\?=                   # literal ?=\n  ', re.VERBOSE | re.MULTILINE)
fcre = re.compile('[\\041-\\176]+:$')
_embedded_header = re.compile('\\n[^ \\t]+:')
_max_append = email.quoprimime._max_append

def decode_header(header):
    if hasattr(header, '_chunks'):
        return [(_charset._encode(string, str(charset)), str(charset)) for string, charset in header._chunks]
    else:
        return ecre.search(header) or [
         (
          header, None)]
    words = []
    for line in header.splitlines():
        parts = ecre.split(line)
        first = True
        while parts:
            unencoded = parts.pop(0)
            if first:
                unencoded = unencoded.lstrip()
                first = False
            if unencoded:
                words.append((unencoded, None, None))
            if parts:
                charset = parts.pop(0).lower()
                encoding = parts.pop(0).lower()
                encoded = parts.pop(0)
                words.append((encoded, encoding, charset))

    droplist = []
    for n, w in enumerate(words):
        if n > 1 and w[1] and words[n - 2][1] and words[n - 1][0].isspace():
            droplist.append(n - 1)

    for d in reversed(droplist):
        del words[d]

    decoded_words = []
    for encoded_string, encoding, charset in words:
        if encoding is None:
            decoded_words.append((encoded_string, charset))
        elif encoding == 'q':
            word = email.quoprimime.header_decode(encoded_string)
            decoded_words.append((word, charset))
        elif encoding == 'b':
            paderr = len(encoded_string) % 4
            if paderr:
                encoded_string += '==='[:4 - paderr]
            try:
                word = email.base64mime.decode(encoded_string)
            except binascii.Error:
                raise HeaderParseError('Base64 decoding error')
            else:
                decoded_words.append((word, charset))
        else:
            raise AssertionError('Unexpected encoding: ' + encoding)

    collapsed = []
    last_word = last_charset = None
    for word, charset in decoded_words:
        if isinstance(word, str):
            word = bytes(word, 'raw-unicode-escape')
        if last_word is None:
            last_word = word
            last_charset = charset
        elif charset != last_charset:
            collapsed.append((last_word, last_charset))
            last_word = word
            last_charset = charset
        elif last_charset is None:
            last_word += BSPACE + word
        else:
            last_word += word

    collapsed.append((last_word, last_charset))
    return collapsed


def make_header(decoded_seq, maxlinelen=None, header_name=None, continuation_ws=' '):
    h = Header(maxlinelen=maxlinelen, header_name=header_name, continuation_ws=continuation_ws)
    for s, charset in decoded_seq:
        if charset is not None:
            if not isinstance(charset, Charset):
                charset = Charset(charset)
        h.append(s, charset)

    return h


class Header:

    def __init__(self, s=None, charset=None, maxlinelen=None, header_name=None, continuation_ws=' ', errors='strict'):
        if charset is None:
            charset = USASCII
        else:
            if not isinstance(charset, Charset):
                charset = Charset(charset)
            else:
                self._charset = charset
                self._continuation_ws = continuation_ws
                self._chunks = []
                if s is not None:
                    self.append(s, charset, errors)
                if maxlinelen is None:
                    maxlinelen = MAXLINELEN
                self._maxlinelen = maxlinelen
                if header_name is None:
                    self._headerlen = 0
                else:
                    self._headerlen = len(header_name) + 2

    def __str__(self):
        self._normalize()
        uchunks = []
        lastcs = None
        lastspace = None
        for string, charset in self._chunks:
            nextcs = charset
            if nextcs == _charset.UNKNOWN8BIT:
                original_bytes = string.encode('ascii', 'surrogateescape')
                string = original_bytes.decode('ascii', 'replace')
            elif uchunks:
                hasspace = string and self._nonctext(string[0])
                if lastcs not in (None, 'us-ascii'):
                    if nextcs in (None, 'us-ascii'):
                        hasspace or uchunks.append(SPACE)
                        nextcs = None
                elif nextcs not in (None, 'us-ascii'):
                    if not lastspace:
                        uchunks.append(SPACE)
            lastspace = string and self._nonctext(string[-1])
            lastcs = nextcs
            uchunks.append(string)

        return EMPTYSTRING.join(uchunks)

    def __eq__(self, other):
        return other == str(self)

    def append(self, s, charset=None, errors='strict'):
        if charset is None:
            charset = self._charset
        else:
            if not isinstance(charset, Charset):
                charset = Charset(charset)
            elif not isinstance(s, str):
                input_charset = charset.input_codec or 'us-ascii'
                if input_charset == _charset.UNKNOWN8BIT:
                    s = s.decode('us-ascii', 'surrogateescape')
                else:
                    s = s.decode(input_charset, errors)
            output_charset = charset.output_codec or 'us-ascii'
            if output_charset != _charset.UNKNOWN8BIT:
                try:
                    s.encode(output_charset, errors)
                except UnicodeEncodeError:
                    if output_charset != 'us-ascii':
                        raise
                    charset = UTF8

            self._chunks.append((s, charset))

    def _nonctext(self, s):
        return s.isspace() or s in ('(', ')', '\\')

    def encode(self, splitchars=';, \t', maxlinelen=None, linesep='\n'):
        self._normalize()
        if maxlinelen is None:
            maxlinelen = self._maxlinelen
        if maxlinelen == 0:
            maxlinelen = 1000000
        formatter = _ValueFormatter(self._headerlen, maxlinelen, self._continuation_ws, splitchars)
        lastcs = None
        hasspace = lastspace = None
        for string, charset in self._chunks:
            if hasspace is not None:
                hasspace = string and self._nonctext(string[0])
                if lastcs not in (None, 'us-ascii'):
                    if not hasspace or charset not in (None, 'us-ascii'):
                        formatter.add_transition()
                    else:
                        if charset not in (None, 'us-ascii'):
                            if not lastspace:
                                formatter.add_transition()
                else:
                    lastspace = string and self._nonctext(string[-1])
                    lastcs = charset
                    hasspace = False
                    lines = string.splitlines()
                    if lines:
                        formatter.feed('', lines[0], charset)
                    else:
                        formatter.feed('', '', charset)
                for line in lines[1:]:
                    formatter.newline()
                    if charset.header_encoding is not None:
                        formatter.feed(self._continuation_ws, ' ' + line.lstrip(), charset)
                    else:
                        sline = line.lstrip()
                        fws = line[:len(line) - len(sline)]
                        formatter.feed(fws, sline, charset)

                if len(lines) > 1:
                    formatter.newline()

        if self._chunks:
            formatter.add_transition()
        value = formatter._str(linesep)
        if _embedded_header.search(value):
            raise HeaderParseError('header value appears to contain an embedded header: {!r}'.format(value))
        return value

    def _normalize(self):
        chunks = []
        last_charset = None
        last_chunk = []
        for string, charset in self._chunks:
            if charset == last_charset:
                last_chunk.append(string)
            else:
                if last_charset is not None:
                    chunks.append((SPACE.join(last_chunk), last_charset))
                last_chunk = [
                 string]
                last_charset = charset

        if last_chunk:
            chunks.append((SPACE.join(last_chunk), last_charset))
        self._chunks = chunks


class _ValueFormatter:

    def __init__(self, headerlen, maxlen, continuation_ws, splitchars):
        self._maxlen = maxlen
        self._continuation_ws = continuation_ws
        self._continuation_ws_len = len(continuation_ws)
        self._splitchars = splitchars
        self._lines = []
        self._current_line = _Accumulator(headerlen)

    def _str(self, linesep):
        self.newline()
        return linesep.join(self._lines)

    def __str__(self):
        return self._str(NL)

    def newline(self):
        end_of_line = self._current_line.pop()
        if end_of_line != (' ', ''):
            (self._current_line.push)(*end_of_line)
        elif len(self._current_line) > 0:
            if self._current_line.is_onlyws():
                self._lines[-1] += str(self._current_line)
            else:
                self._lines.append(str(self._current_line))
        self._current_line.reset()

    def add_transition(self):
        self._current_line.push(' ', '')

    def feed(self, fws, string, charset):
        if charset.header_encoding is None:
            self._ascii_split(fws, string, self._splitchars)
            return
        encoded_lines = charset.header_encode_lines(string, self._maxlengths())
        try:
            first_line = encoded_lines.pop(0)
        except IndexError:
            return
        else:
            if first_line is not None:
                self._append_chunk(fws, first_line)
            try:
                last_line = encoded_lines.pop()
            except IndexError:
                return
            else:
                self.newline()
                self._current_line.push(self._continuation_ws, last_line)
                for line in encoded_lines:
                    self._lines.append(self._continuation_ws + line)

    def _maxlengths(self):
        yield self._maxlen - len(self._current_line)
        while True:
            yield self._maxlen - self._continuation_ws_len

    def _ascii_split(self, fws, string, splitchars):
        parts = re.split('([' + FWS + ']+)', fws + string)
        if parts[0]:
            parts[:0] = [
             '']
        else:
            parts.pop(0)
        for fws, part in zip(*[iter(parts)] * 2):
            self._append_chunk(fws, part)

    def _append_chunk(self, fws, string):
        self._current_line.push(fws, string)
        if len(self._current_line) > self._maxlen:
            for ch in self._splitchars:
                for i in range(self._current_line.part_count() - 1, 0, -1):
                    if ch.isspace():
                        fws = self._current_line[i][0]
                        if fws:
                            if fws[0] == ch:
                                break
                    prevpart = self._current_line[i - 1][1]
                    if prevpart and prevpart[-1] == ch:
                        break
                else:
                    continue

                break
            else:
                fws, part = self._current_line.pop()
                if self._current_line._initial_size > 0:
                    self.newline()
                    if not fws:
                        fws = ' '
                self._current_line.push(fws, part)
                return

            remainder = self._current_line.pop_from(i)
            self._lines.append(str(self._current_line))
            self._current_line.reset(remainder)


class _Accumulator(list):

    def __init__(self, initial_size=0):
        self._initial_size = initial_size
        super().__init__()

    def push(self, fws, string):
        self.append((fws, string))

    def pop_from(self, i=0):
        popped = self[i:]
        self[i:] = []
        return popped

    def pop(self):
        if self.part_count() == 0:
            return ('', '')
        return super().pop()

    def __len__(self):
        return sum((len(fws) + len(part) for fws, part in self), self._initial_size)

    def __str__(self):
        return EMPTYSTRING.join((EMPTYSTRING.join((fws, part)) for fws, part in self))

    def reset(self, startval=None):
        if startval is None:
            startval = []
        self[:] = startval
        self._initial_size = 0

    def is_onlyws(self):
        return self._initial_size == 0 and (not self or str(self).isspace())

    def part_count(self):
        return super().__len__()