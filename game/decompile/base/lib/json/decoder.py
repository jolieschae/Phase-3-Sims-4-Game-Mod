# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\json\decoder.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 12828 bytes
import re
from json import scanner
try:
    from _json import scanstring as c_scanstring
except ImportError:
    c_scanstring = None

__all__ = ['JSONDecoder', 'JSONDecodeError']
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
NaN = float('nan')
PosInf = float('inf')
NegInf = float('-inf')

class JSONDecodeError(ValueError):

    def __init__(self, msg, doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return (
         self.__class__, (self.msg, self.doc, self.pos))


_CONSTANTS = {'-Infinity':NegInf, 
 'Infinity':PosInf, 
 'NaN':NaN}
STRINGCHUNK = re.compile('(.*?)(["\\\\\\x00-\\x1f])', FLAGS)
BACKSLASH = {
 '"': '\'"\'', '\\': "'\\\\'", '/': "'/'", 
 'b': "'\\x08'", 'f': "'\\x0c'", 'n': "'\\n'", 'r': "'\\r'", 't': "'\\t'"}

def _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    if len(esc) == 4:
        if esc[1] not in 'xX':
            try:
                return int(esc, 16)
            except ValueError:
                pass

    msg = 'Invalid \\uXXXX escape'
    raise JSONDecodeError(msg, s, pos)


def py_scanstring(s, end, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match):
    chunks = []
    _append = chunks.append
    begin = end - 1
    while True:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError('Unterminated string starting at', s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        if content:
            _append(content)
        if terminator == '"':
            break
        else:
            if terminator != '\\':
                if strict:
                    msg = 'Invalid control character {0!r} at'.format(terminator)
                    raise JSONDecodeError(msg, s, end)
                else:
                    _append(terminator)
                    continue
            else:
                try:
                    esc = s[end]
                except IndexError:
                    raise JSONDecodeError('Unterminated string starting at', s, begin) from None

        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\escape: {0!r}'.format(esc)
                raise JSONDecodeError(msg, s, end)

            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 55296 <= uni <= 56319:
                if s[end:end + 2] == '\\u':
                    uni2 = _decode_uXXXX(s, end + 1)
                    if 56320 <= uni2 <= 57343:
                        uni = 65536 + (uni - 55296 << 10 | uni2 - 56320)
                        end += 6
                char = chr(uni)
            _append(char)

    return (
     ''.join(chunks), end)


scanstring = c_scanstring or py_scanstring
WHITESPACE = re.compile('[ \\t\\n\\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'

def JSONObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook, memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    nextchar = s[end:end + 1]
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
        if nextchar == '}':
            if object_pairs_hook is not None:
                result = object_pairs_hook(pairs)
                return (result, end + 1)
            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs)
            return (
             pairs, end + 1)
        if nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end)
    end += 1
    while 1:
        key, end = scanstring(s, end, strict)
        key = memo_get(key, key)
        if s[end:end + 1] != ':':
            end = _w(s, end).end()
            if s[end:end + 1] != ':':
                raise JSONDecodeError("Expecting ':' delimiter", s, end)
            end += 1
            try:
                if s[end] in _ws:
                    end += 1
                    if s[end] in _ws:
                        end = _w(s, end + 1).end()
            except IndexError:
                pass

            try:
                value, end = scan_once(s, end)
            except StopIteration as err:
                try:
                    raise JSONDecodeError('Expecting value', s, err.value) from None
                finally:
                    err = None
                    del err

            pairs_append((key, value))
            try:
                nextchar = s[end]
                if nextchar in _ws:
                    end = _w(s, end + 1).end()
                    nextchar = s[end]
            except IndexError:
                nextchar = ''

            end += 1
            if nextchar == '}':
                break
        elif nextchar != ',':
            raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end - 1)

    if object_pairs_hook is not None:
        result = object_pairs_hook(pairs)
        return (result, end)
    pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return (
     pairs, end)


def JSONArray(s_and_end, scan_once, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    values = []
    nextchar = s[end:end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
    if nextchar == ']':
        return (
         values, end + 1)
    _append = values.append
    while True:
        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            try:
                raise JSONDecodeError('Expecting value', s, err.value) from None
            finally:
                err = None
                del err

        _append(value)
        nextchar = s[end:end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        end += 1
        if nextchar == ']':
            break
        else:
            if nextchar != ',':
                raise JSONDecodeError("Expecting ',' delimiter", s, end - 1)
            try:
                if s[end] in _ws:
                    end += 1
                    if s[end] in _ws:
                        end = _w(s, end + 1).end()
            except IndexError:
                pass

    return (
     values, end)


class JSONDecoder(object):

    def __init__(self, *, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, strict=True, object_pairs_hook=None):
        self.object_hook = object_hook
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.parse_constant = parse_constant or _CONSTANTS.__getitem__
        self.strict = strict
        self.object_pairs_hook = object_pairs_hook
        self.parse_object = JSONObject
        self.parse_array = JSONArray
        self.parse_string = scanstring
        self.memo = {}
        self.scan_once = scanner.make_scanner(self)

    def decode(self, s, _w=WHITESPACE.match):
        obj, end = self.raw_decode(s, idx=(_w(s, 0).end()))
        end = _w(s, end).end()
        if end != len(s):
            raise JSONDecodeError('Extra data', s, end)
        return obj

    def raw_decode(self, s, idx=0):
        try:
            obj, end = self.scan_once(s, idx)
        except StopIteration as err:
            try:
                raise JSONDecodeError('Expecting value', s, err.value) from None
            finally:
                err = None
                del err

        return (
         obj, end)