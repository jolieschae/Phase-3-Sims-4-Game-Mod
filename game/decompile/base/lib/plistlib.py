# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\plistlib.py
# Compiled at: 2018-07-31 18:42:56
# Size of source mod 2**32: 30875 bytes
__all__ = [
 "'readPlist'", "'writePlist'", "'readPlistFromBytes'", "'writePlistToBytes'", 
 "'Data'", 
 "'InvalidFileException'", "'FMT_XML'", "'FMT_BINARY'", 
 "'load'", "'dump'", 
 "'loads'", "'dumps'"]
import binascii, codecs, contextlib, datetime, enum_lib as enum
from io import BytesIO
import itertools, os, re, struct
from warnings import warn
from xml.parsers.expat import ParserCreate
PlistFormat = enum.Enum('PlistFormat', 'FMT_XML FMT_BINARY', module=__name__)
globals().update(PlistFormat.__members__)

@contextlib.contextmanager
def _maybe_open(pathOrFile, mode):
    if isinstance(pathOrFile, str):
        with open(pathOrFile, mode) as (fp):
            yield fp
    else:
        yield pathOrFile


def readPlist(pathOrFile):
    warn('The readPlist function is deprecated, use load() instead', DeprecationWarning, 2)
    with _maybe_open(pathOrFile, 'rb') as (fp):
        return load(fp, fmt=None, use_builtin_types=False)


def writePlist(value, pathOrFile):
    warn('The writePlist function is deprecated, use dump() instead', DeprecationWarning, 2)
    with _maybe_open(pathOrFile, 'wb') as (fp):
        dump(value, fp, fmt=FMT_XML, sort_keys=True, skipkeys=False)


def readPlistFromBytes(data):
    warn('The readPlistFromBytes function is deprecated, use loads() instead', DeprecationWarning, 2)
    return load((BytesIO(data)), fmt=None, use_builtin_types=False)


def writePlistToBytes(value):
    warn('The writePlistToBytes function is deprecated, use dumps() instead', DeprecationWarning, 2)
    f = BytesIO()
    dump(value, f, fmt=FMT_XML, sort_keys=True, skipkeys=False)
    return f.getvalue()


class Data:

    def __init__(self, data):
        if not isinstance(data, bytes):
            raise TypeError('data must be as bytes')
        self.data = data

    @classmethod
    def fromBase64(cls, data):
        return cls(_decode_base64(data))

    def asBase64(self, maxlinelength=76):
        return _encode_base64(self.data, maxlinelength)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.data == other.data
        if isinstance(other, bytes):
            return self.data == other
        return NotImplemented

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self.data))


PLISTHEADER = b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
_controlCharPat = re.compile('[\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x0b\\x0c\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f]')

def _encode_base64(s, maxlinelength=76):
    maxbinsize = maxlinelength // 4 * 3
    pieces = []
    for i in range(0, len(s), maxbinsize):
        chunk = s[i:i + maxbinsize]
        pieces.append(binascii.b2a_base64(chunk))

    return (b'').join(pieces)


def _decode_base64(s):
    if isinstance(s, str):
        return binascii.a2b_base64(s.encode('utf-8'))
    return binascii.a2b_base64(s)


_dateParser = re.compile('(?P<year>\\d\\d\\d\\d)(?:-(?P<month>\\d\\d)(?:-(?P<day>\\d\\d)(?:T(?P<hour>\\d\\d)(?::(?P<minute>\\d\\d)(?::(?P<second>\\d\\d))?)?)?)?)?Z', re.ASCII)

def _date_from_string(s):
    order = ('year', 'month', 'day', 'hour', 'minute', 'second')
    gd = _dateParser.match(s).groupdict()
    lst = []
    for key in order:
        val = gd[key]
        if val is None:
            break
        lst.append(int(val))

    return (datetime.datetime)(*lst)


def _date_to_string(d):
    return '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
     d.year, d.month, d.day,
     d.hour, d.minute, d.second)


def _escape(text):
    m = _controlCharPat.search(text)
    if m is not None:
        raise ValueError("strings can't contains control characters; use bytes instead")
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


class _PlistParser:

    def __init__(self, use_builtin_types, dict_type):
        self.stack = []
        self.current_key = None
        self.root = None
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    def parse(self, fileobj):
        self.parser = ParserCreate()
        self.parser.StartElementHandler = self.handle_begin_element
        self.parser.EndElementHandler = self.handle_end_element
        self.parser.CharacterDataHandler = self.handle_data
        self.parser.ParseFile(fileobj)
        return self.root

    def handle_begin_element(self, element, attrs):
        self.data = []
        handler = getattr(self, 'begin_' + element, None)
        if handler is not None:
            handler(attrs)

    def handle_end_element(self, element):
        handler = getattr(self, 'end_' + element, None)
        if handler is not None:
            handler()

    def handle_data(self, data):
        self.data.append(data)

    def add_object(self, value):
        if self.current_key is not None:
            if not isinstance(self.stack[-1], type({})):
                raise ValueError('unexpected element at line %d' % self.parser.CurrentLineNumber)
            self.stack[-1][self.current_key] = value
            self.current_key = None
        else:
            if not self.stack:
                self.root = value
            else:
                if not isinstance(self.stack[-1], type([])):
                    raise ValueError('unexpected element at line %d' % self.parser.CurrentLineNumber)
                self.stack[-1].append(value)

    def get_data(self):
        data = ''.join(self.data)
        self.data = []
        return data

    def begin_dict(self, attrs):
        d = self._dict_type()
        self.add_object(d)
        self.stack.append(d)

    def end_dict(self):
        if self.current_key:
            raise ValueError("missing value for key '%s' at line %d" % (
             self.current_key, self.parser.CurrentLineNumber))
        self.stack.pop()

    def end_key(self):
        if not (self.current_key or isinstance(self.stack[-1], type({}))):
            raise ValueError('unexpected key at line %d' % self.parser.CurrentLineNumber)
        self.current_key = self.get_data()

    def begin_array(self, attrs):
        a = []
        self.add_object(a)
        self.stack.append(a)

    def end_array(self):
        self.stack.pop()

    def end_true(self):
        self.add_object(True)

    def end_false(self):
        self.add_object(False)

    def end_integer(self):
        self.add_object(int(self.get_data()))

    def end_real(self):
        self.add_object(float(self.get_data()))

    def end_string(self):
        self.add_object(self.get_data())

    def end_data(self):
        if self._use_builtin_types:
            self.add_object(_decode_base64(self.get_data()))
        else:
            self.add_object(Data.fromBase64(self.get_data()))

    def end_date(self):
        self.add_object(_date_from_string(self.get_data()))


class _DumbXMLWriter:

    def __init__(self, file, indent_level=0, indent='\t'):
        self.file = file
        self.stack = []
        self._indent_level = indent_level
        self.indent = indent

    def begin_element(self, element):
        self.stack.append(element)
        self.writeln('<%s>' % element)
        self._indent_level += 1

    def end_element(self, element):
        self._indent_level -= 1
        self.writeln('</%s>' % element)

    def simple_element(self, element, value=None):
        if value is not None:
            value = _escape(value)
            self.writeln('<%s>%s</%s>' % (element, value, element))
        else:
            self.writeln('<%s/>' % element)

    def writeln(self, line):
        if line:
            if isinstance(line, str):
                line = line.encode('utf-8')
            self.file.write(self._indent_level * self.indent)
            self.file.write(line)
        self.file.write(b'\n')


class _PlistWriter(_DumbXMLWriter):

    def __init__(self, file, indent_level=0, indent=b'\t', writeHeader=1, sort_keys=True, skipkeys=False):
        if writeHeader:
            file.write(PLISTHEADER)
        _DumbXMLWriter.__init__(self, file, indent_level, indent)
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    def write(self, value):
        self.writeln('<plist version="1.0">')
        self.write_value(value)
        self.writeln('</plist>')

    def write_value(self, value):
        if isinstance(value, str):
            self.simple_element('string', value)
        else:
            if value is True:
                self.simple_element('true')
            else:
                if value is False:
                    self.simple_element('false')
                else:
                    if isinstance(value, int):
                        if -9223372036854775808 <= value < 18446744073709551616:
                            self.simple_element('integer', '%d' % value)
                        else:
                            raise OverflowError(value)
                    else:
                        if isinstance(value, float):
                            self.simple_element('real', repr(value))
                        else:
                            if isinstance(value, dict):
                                self.write_dict(value)
                            else:
                                if isinstance(value, Data):
                                    self.write_data(value)
                                else:
                                    if isinstance(value, (bytes, bytearray)):
                                        self.write_bytes(value)
                                    else:
                                        if isinstance(value, datetime.datetime):
                                            self.simple_element('date', _date_to_string(value))
                                        else:
                                            if isinstance(value, (tuple, list)):
                                                self.write_array(value)
                                            else:
                                                raise TypeError('unsupported type: %s' % type(value))

    def write_data(self, data):
        self.write_bytes(data.data)

    def write_bytes(self, data):
        self.begin_element('data')
        self._indent_level -= 1
        maxlinelength = max(16, 76 - len(self.indent.replace(b'\t', b'        ') * self._indent_level))
        for line in _encode_base64(data, maxlinelength).split(b'\n'):
            if line:
                self.writeln(line)

        self._indent_level += 1
        self.end_element('data')

    def write_dict(self, d):
        if d:
            self.begin_element('dict')
            if self._sort_keys:
                items = sorted(d.items())
            else:
                items = d.items()
            for key, value in items:
                if not isinstance(key, str):
                    if self._skipkeys:
                        continue
                    raise TypeError('keys must be strings')
                self.simple_element('key', key)
                self.write_value(value)

            self.end_element('dict')
        else:
            self.simple_element('dict')

    def write_array(self, array):
        if array:
            self.begin_element('array')
            for value in array:
                self.write_value(value)

            self.end_element('array')
        else:
            self.simple_element('array')


def _is_fmt_xml(header):
    prefixes = (b'<?xml', b'<plist')
    for pfx in prefixes:
        if header.startswith(pfx):
            return True

    for bom, encoding in (
     (
      codecs.BOM_UTF8, 'utf-8'),
     (
      codecs.BOM_UTF16_BE, 'utf-16-be'),
     (
      codecs.BOM_UTF16_LE, 'utf-16-le')):
        if not header.startswith(bom):
            continue
        for start in prefixes:
            prefix = bom + start.decode('ascii').encode(encoding)
            if header[:len(prefix)] == prefix:
                return True

    return False


class InvalidFileException(ValueError):

    def __init__(self, message='Invalid file'):
        ValueError.__init__(self, message)


_BINARY_FORMAT = {
 1: "'B'", 2: "'H'", 4: "'L'", 8: "'Q'"}
_undefined = object()

class _BinaryPlistParser:

    def __init__(self, use_builtin_types, dict_type):
        self._use_builtin_types = use_builtin_types
        self._dict_type = dict_type

    def parse(self, fp):
        try:
            self._fp = fp
            self._fp.seek(-32, os.SEEK_END)
            trailer = self._fp.read(32)
            if len(trailer) != 32:
                raise InvalidFileException()
            offset_size, self._ref_size, num_objects, top_object, offset_table_offset = struct.unpack('>6xBBQQQ', trailer)
            self._fp.seek(offset_table_offset)
            self._object_offsets = self._read_ints(num_objects, offset_size)
            self._objects = [_undefined] * num_objects
            return self._read_object(top_object)
        except (OSError, IndexError, struct.error, OverflowError,
         UnicodeDecodeError):
            raise InvalidFileException()

    def _get_size(self, tokenL):
        if tokenL == 15:
            m = self._fp.read(1)[0] & 3
            s = 1 << m
            f = '>' + _BINARY_FORMAT[s]
            return struct.unpack(f, self._fp.read(s))[0]
        return tokenL

    def _read_ints(self, n, size):
        data = self._fp.read(size * n)
        if size in _BINARY_FORMAT:
            return struct.unpack('>' + _BINARY_FORMAT[size] * n, data)
        if not size or len(data) != size * n:
            raise InvalidFileException()
        return tuple((int.from_bytes(data[i:i + size], 'big') for i in range(0, size * n, size)))

    def _read_refs(self, n):
        return self._read_ints(n, self._ref_size)

    def _read_object--- This code section failed: ---

 L. 596         0  LOAD_DEREF               'self'
                2  LOAD_ATTR                _objects
                4  LOAD_FAST                'ref'
                6  BINARY_SUBSCR    
                8  STORE_FAST               'result'

 L. 597        10  LOAD_FAST                'result'
               12  LOAD_GLOBAL              _undefined
               14  COMPARE_OP               is-not
               16  POP_JUMP_IF_FALSE    22  'to 22'

 L. 598        18  LOAD_FAST                'result'
               20  RETURN_VALUE     
             22_0  COME_FROM            16  '16'

 L. 600        22  LOAD_DEREF               'self'
               24  LOAD_ATTR                _object_offsets
               26  LOAD_FAST                'ref'
               28  BINARY_SUBSCR    
               30  STORE_FAST               'offset'

 L. 601        32  LOAD_DEREF               'self'
               34  LOAD_ATTR                _fp
               36  LOAD_METHOD              seek
               38  LOAD_FAST                'offset'
               40  CALL_METHOD_1         1  '1 positional argument'
               42  POP_TOP          

 L. 602        44  LOAD_DEREF               'self'
               46  LOAD_ATTR                _fp
               48  LOAD_METHOD              read
               50  LOAD_CONST               1
               52  CALL_METHOD_1         1  '1 positional argument'
               54  LOAD_CONST               0
               56  BINARY_SUBSCR    
               58  STORE_FAST               'token'

 L. 603        60  LOAD_FAST                'token'
               62  LOAD_CONST               240
               64  BINARY_AND       
               66  LOAD_FAST                'token'
               68  LOAD_CONST               15
               70  BINARY_AND       
               72  ROT_TWO          
               74  STORE_FAST               'tokenH'
               76  STORE_FAST               'tokenL'

 L. 605        78  LOAD_FAST                'token'
               80  LOAD_CONST               0
               82  COMPARE_OP               ==
               84  POP_JUMP_IF_FALSE    94  'to 94'

 L. 606        86  LOAD_CONST               None
               88  STORE_FAST               'result'
            90_92  JUMP_FORWARD        656  'to 656'
             94_0  COME_FROM            84  '84'

 L. 608        94  LOAD_FAST                'token'
               96  LOAD_CONST               8
               98  COMPARE_OP               ==
              100  POP_JUMP_IF_FALSE   110  'to 110'

 L. 609       102  LOAD_CONST               False
              104  STORE_FAST               'result'
          106_108  JUMP_FORWARD        656  'to 656'
            110_0  COME_FROM           100  '100'

 L. 611       110  LOAD_FAST                'token'
              112  LOAD_CONST               9
              114  COMPARE_OP               ==
              116  POP_JUMP_IF_FALSE   126  'to 126'

 L. 612       118  LOAD_CONST               True
              120  STORE_FAST               'result'
          122_124  JUMP_FORWARD        656  'to 656'
            126_0  COME_FROM           116  '116'

 L. 617       126  LOAD_FAST                'token'
              128  LOAD_CONST               15
              130  COMPARE_OP               ==
              132  POP_JUMP_IF_FALSE   142  'to 142'

 L. 618       134  LOAD_CONST               b''
              136  STORE_FAST               'result'
          138_140  JUMP_FORWARD        656  'to 656'
            142_0  COME_FROM           132  '132'

 L. 620       142  LOAD_FAST                'tokenH'
              144  LOAD_CONST               16
              146  COMPARE_OP               ==
              148  POP_JUMP_IF_FALSE   186  'to 186'

 L. 621       150  LOAD_GLOBAL              int
              152  LOAD_ATTR                from_bytes
              154  LOAD_DEREF               'self'
              156  LOAD_ATTR                _fp
              158  LOAD_METHOD              read
              160  LOAD_CONST               1
              162  LOAD_FAST                'tokenL'
              164  BINARY_LSHIFT    
              166  CALL_METHOD_1         1  '1 positional argument'

 L. 622       168  LOAD_STR                 'big'
              170  LOAD_FAST                'tokenL'
              172  LOAD_CONST               3
              174  COMPARE_OP               >=
              176  LOAD_CONST               ('signed',)
              178  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              180  STORE_FAST               'result'
          182_184  JUMP_FORWARD        656  'to 656'
            186_0  COME_FROM           148  '148'

 L. 624       186  LOAD_FAST                'token'
              188  LOAD_CONST               34
              190  COMPARE_OP               ==
              192  POP_JUMP_IF_FALSE   222  'to 222'

 L. 625       194  LOAD_GLOBAL              struct
              196  LOAD_METHOD              unpack
              198  LOAD_STR                 '>f'
              200  LOAD_DEREF               'self'
              202  LOAD_ATTR                _fp
              204  LOAD_METHOD              read
              206  LOAD_CONST               4
              208  CALL_METHOD_1         1  '1 positional argument'
              210  CALL_METHOD_2         2  '2 positional arguments'
              212  LOAD_CONST               0
              214  BINARY_SUBSCR    
              216  STORE_FAST               'result'
          218_220  JUMP_FORWARD        656  'to 656'
            222_0  COME_FROM           192  '192'

 L. 627       222  LOAD_FAST                'token'
              224  LOAD_CONST               35
              226  COMPARE_OP               ==
          228_230  POP_JUMP_IF_FALSE   260  'to 260'

 L. 628       232  LOAD_GLOBAL              struct
              234  LOAD_METHOD              unpack
              236  LOAD_STR                 '>d'
              238  LOAD_DEREF               'self'
              240  LOAD_ATTR                _fp
              242  LOAD_METHOD              read
              244  LOAD_CONST               8
              246  CALL_METHOD_1         1  '1 positional argument'
              248  CALL_METHOD_2         2  '2 positional arguments'
              250  LOAD_CONST               0
              252  BINARY_SUBSCR    
              254  STORE_FAST               'result'
          256_258  JUMP_FORWARD        656  'to 656'
            260_0  COME_FROM           228  '228'

 L. 630       260  LOAD_FAST                'token'
              262  LOAD_CONST               51
              264  COMPARE_OP               ==
          266_268  POP_JUMP_IF_FALSE   324  'to 324'

 L. 631       270  LOAD_GLOBAL              struct
              272  LOAD_METHOD              unpack
              274  LOAD_STR                 '>d'
              276  LOAD_DEREF               'self'
              278  LOAD_ATTR                _fp
              280  LOAD_METHOD              read
              282  LOAD_CONST               8
              284  CALL_METHOD_1         1  '1 positional argument'
              286  CALL_METHOD_2         2  '2 positional arguments'
              288  LOAD_CONST               0
              290  BINARY_SUBSCR    
              292  STORE_FAST               'f'

 L. 634       294  LOAD_GLOBAL              datetime
              296  LOAD_METHOD              datetime
              298  LOAD_CONST               2001
              300  LOAD_CONST               1
              302  LOAD_CONST               1
              304  CALL_METHOD_3         3  '3 positional arguments'

 L. 635       306  LOAD_GLOBAL              datetime
              308  LOAD_ATTR                timedelta
              310  LOAD_FAST                'f'
              312  LOAD_CONST               ('seconds',)
              314  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              316  BINARY_ADD       
              318  STORE_FAST               'result'
          320_322  JUMP_FORWARD        656  'to 656'
            324_0  COME_FROM           266  '266'

 L. 637       324  LOAD_FAST                'tokenH'
              326  LOAD_CONST               64
              328  COMPARE_OP               ==
          330_332  POP_JUMP_IF_FALSE   386  'to 386'

 L. 638       334  LOAD_DEREF               'self'
              336  LOAD_METHOD              _get_size
              338  LOAD_FAST                'tokenL'
              340  CALL_METHOD_1         1  '1 positional argument'
              342  STORE_FAST               's'

 L. 639       344  LOAD_DEREF               'self'
              346  LOAD_ATTR                _use_builtin_types
          348_350  POP_JUMP_IF_FALSE   366  'to 366'

 L. 640       352  LOAD_DEREF               'self'
              354  LOAD_ATTR                _fp
              356  LOAD_METHOD              read
              358  LOAD_FAST                's'
              360  CALL_METHOD_1         1  '1 positional argument'
              362  STORE_FAST               'result'
              364  JUMP_FORWARD        656  'to 656'
            366_0  COME_FROM           348  '348'

 L. 642       366  LOAD_GLOBAL              Data
              368  LOAD_DEREF               'self'
              370  LOAD_ATTR                _fp
              372  LOAD_METHOD              read
              374  LOAD_FAST                's'
              376  CALL_METHOD_1         1  '1 positional argument'
              378  CALL_FUNCTION_1       1  '1 positional argument'
              380  STORE_FAST               'result'
          382_384  JUMP_FORWARD        656  'to 656'
            386_0  COME_FROM           330  '330'

 L. 644       386  LOAD_FAST                'tokenH'
              388  LOAD_CONST               80
              390  COMPARE_OP               ==
          392_394  POP_JUMP_IF_FALSE   430  'to 430'

 L. 645       396  LOAD_DEREF               'self'
              398  LOAD_METHOD              _get_size
              400  LOAD_FAST                'tokenL'
              402  CALL_METHOD_1         1  '1 positional argument'
              404  STORE_FAST               's'

 L. 646       406  LOAD_DEREF               'self'
              408  LOAD_ATTR                _fp
              410  LOAD_METHOD              read
              412  LOAD_FAST                's'
              414  CALL_METHOD_1         1  '1 positional argument'
              416  LOAD_METHOD              decode
              418  LOAD_STR                 'ascii'
              420  CALL_METHOD_1         1  '1 positional argument'
              422  STORE_FAST               'result'

 L. 647       424  LOAD_FAST                'result'
              426  STORE_FAST               'result'
              428  JUMP_FORWARD        656  'to 656'
            430_0  COME_FROM           392  '392'

 L. 649       430  LOAD_FAST                'tokenH'
              432  LOAD_CONST               96
              434  COMPARE_OP               ==
          436_438  POP_JUMP_IF_FALSE   474  'to 474'

 L. 650       440  LOAD_DEREF               'self'
              442  LOAD_METHOD              _get_size
              444  LOAD_FAST                'tokenL'
              446  CALL_METHOD_1         1  '1 positional argument'
              448  STORE_FAST               's'

 L. 651       450  LOAD_DEREF               'self'
              452  LOAD_ATTR                _fp
              454  LOAD_METHOD              read
              456  LOAD_FAST                's'
              458  LOAD_CONST               2
              460  BINARY_MULTIPLY  
              462  CALL_METHOD_1         1  '1 positional argument'
              464  LOAD_METHOD              decode
              466  LOAD_STR                 'utf-16be'
              468  CALL_METHOD_1         1  '1 positional argument'
              470  STORE_FAST               'result'
              472  JUMP_FORWARD        656  'to 656'
            474_0  COME_FROM           436  '436'

 L. 656       474  LOAD_FAST                'tokenH'
              476  LOAD_CONST               160
              478  COMPARE_OP               ==
          480_482  POP_JUMP_IF_FALSE   544  'to 544'

 L. 657       484  LOAD_DEREF               'self'
              486  LOAD_METHOD              _get_size
              488  LOAD_FAST                'tokenL'
              490  CALL_METHOD_1         1  '1 positional argument'
              492  STORE_FAST               's'

 L. 658       494  LOAD_DEREF               'self'
              496  LOAD_METHOD              _read_refs
              498  LOAD_FAST                's'
              500  CALL_METHOD_1         1  '1 positional argument'
              502  STORE_FAST               'obj_refs'

 L. 659       504  BUILD_LIST_0          0 
              506  STORE_FAST               'result'

 L. 660       508  LOAD_FAST                'result'
              510  LOAD_DEREF               'self'
              512  LOAD_ATTR                _objects
              514  LOAD_FAST                'ref'
              516  STORE_SUBSCR     

 L. 661       518  LOAD_FAST                'result'
              520  LOAD_METHOD              extend
              522  LOAD_CLOSURE             'self'
              524  BUILD_TUPLE_1         1 
              526  LOAD_GENEXPR             '<code_object <genexpr>>'
              528  LOAD_STR                 '_BinaryPlistParser._read_object.<locals>.<genexpr>'
              530  MAKE_FUNCTION_8          'closure'
              532  LOAD_FAST                'obj_refs'
              534  GET_ITER         
              536  CALL_FUNCTION_1       1  '1 positional argument'
              538  CALL_METHOD_1         1  '1 positional argument'
              540  POP_TOP          
              542  JUMP_FORWARD        656  'to 656'
            544_0  COME_FROM           480  '480'

 L. 669       544  LOAD_FAST                'tokenH'
              546  LOAD_CONST               208
              548  COMPARE_OP               ==
          550_552  POP_JUMP_IF_FALSE   650  'to 650'

 L. 670       554  LOAD_DEREF               'self'
              556  LOAD_METHOD              _get_size
              558  LOAD_FAST                'tokenL'
              560  CALL_METHOD_1         1  '1 positional argument'
              562  STORE_FAST               's'

 L. 671       564  LOAD_DEREF               'self'
              566  LOAD_METHOD              _read_refs
              568  LOAD_FAST                's'
              570  CALL_METHOD_1         1  '1 positional argument'
              572  STORE_FAST               'key_refs'

 L. 672       574  LOAD_DEREF               'self'
              576  LOAD_METHOD              _read_refs
              578  LOAD_FAST                's'
              580  CALL_METHOD_1         1  '1 positional argument'
              582  STORE_FAST               'obj_refs'

 L. 673       584  LOAD_DEREF               'self'
              586  LOAD_METHOD              _dict_type
              588  CALL_METHOD_0         0  '0 positional arguments'
              590  STORE_FAST               'result'

 L. 674       592  LOAD_FAST                'result'
              594  LOAD_DEREF               'self'
              596  LOAD_ATTR                _objects
              598  LOAD_FAST                'ref'
              600  STORE_SUBSCR     

 L. 675       602  SETUP_LOOP          656  'to 656'
              604  LOAD_GLOBAL              zip
              606  LOAD_FAST                'key_refs'
              608  LOAD_FAST                'obj_refs'
              610  CALL_FUNCTION_2       2  '2 positional arguments'
              612  GET_ITER         
              614  FOR_ITER            646  'to 646'
              616  UNPACK_SEQUENCE_2     2 
              618  STORE_FAST               'k'
              620  STORE_FAST               'o'

 L. 676       622  LOAD_DEREF               'self'
              624  LOAD_METHOD              _read_object
              626  LOAD_FAST                'o'
              628  CALL_METHOD_1         1  '1 positional argument'
              630  LOAD_FAST                'result'
              632  LOAD_DEREF               'self'
              634  LOAD_METHOD              _read_object
            636_0  COME_FROM           364  '364'
              636  LOAD_FAST                'k'
              638  CALL_METHOD_1         1  '1 positional argument'
              640  STORE_SUBSCR     
          642_644  JUMP_BACK           614  'to 614'
              646  POP_BLOCK        
              648  JUMP_FORWARD        656  'to 656'
            650_0  COME_FROM           550  '550'

 L. 679       650  LOAD_GLOBAL              InvalidFileException
              652  CALL_FUNCTION_0       0  '0 positional arguments'
              654  RAISE_VARARGS_1       1  'exception instance'
            656_0  COME_FROM           648  '648'
            656_1  COME_FROM_LOOP      602  '602'
            656_2  COME_FROM           542  '542'
            656_3  COME_FROM           472  '472'
            656_4  COME_FROM           428  '428'
            656_5  COME_FROM           382  '382'
            656_6  COME_FROM           320  '320'
            656_7  COME_FROM           256  '256'
            656_8  COME_FROM           218  '218'
            656_9  COME_FROM           182  '182'
           656_10  COME_FROM           138  '138'
           656_11  COME_FROM           122  '122'
           656_12  COME_FROM           106  '106'
           656_13  COME_FROM            90  '90'

 L. 681       656  LOAD_FAST                'result'
              658  LOAD_DEREF               'self'
              660  LOAD_ATTR                _objects
              662  LOAD_FAST                'ref'
              664  STORE_SUBSCR     

 L. 682       666  LOAD_FAST                'result'
              668  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 636_0


def _count_to_size(count):
    if count < 256:
        return 1
    if count < 65536:
        return 2
    if count << 1 << 32:
        return 4
    return 8


_scalars = (
 str, int, float, datetime.datetime, bytes)

class _BinaryPlistWriter(object):

    def __init__(self, fp, sort_keys, skipkeys):
        self._fp = fp
        self._sort_keys = sort_keys
        self._skipkeys = skipkeys

    def write(self, value):
        self._objlist = []
        self._objtable = {}
        self._objidtable = {}
        self._flatten(value)
        num_objects = len(self._objlist)
        self._object_offsets = [0] * num_objects
        self._ref_size = _count_to_size(num_objects)
        self._ref_format = _BINARY_FORMAT[self._ref_size]
        self._fp.write(b'bplist00')
        for obj in self._objlist:
            self._write_object(obj)

        top_object = self._getrefnum(value)
        offset_table_offset = self._fp.tell()
        offset_size = _count_to_size(offset_table_offset)
        offset_format = '>' + _BINARY_FORMAT[offset_size] * num_objects
        self._fp.write((struct.pack)(offset_format, *self._object_offsets))
        sort_version = 0
        trailer = (
         sort_version, offset_size, self._ref_size, num_objects,
         top_object, offset_table_offset)
        self._fp.write((struct.pack)(*('>5xBBBQQQ', ), *trailer))

    def _flatten(self, value):
        if isinstance(value, _scalars):
            if (
             type(value), value) in self._objtable:
                return
        elif isinstance(value, Data):
            if (
             type(value.data), value.data) in self._objtable:
                return
            else:
                if id(value) in self._objidtable:
                    return
        else:
            refnum = len(self._objlist)
            self._objlist.append(value)
            if isinstance(value, _scalars):
                self._objtable[(type(value), value)] = refnum
            else:
                if isinstance(value, Data):
                    self._objtable[(type(value.data), value.data)] = refnum
                else:
                    self._objidtable[id(value)] = refnum
        if isinstance(value, dict):
            keys = []
            values = []
            items = value.items()
            if self._sort_keys:
                items = sorted(items)
            for k, v in items:
                if not isinstance(k, str):
                    if self._skipkeys:
                        continue
                    raise TypeError('keys must be strings')
                keys.append(k)
                values.append(v)

            for o in itertools.chain(keys, values):
                self._flatten(o)

        else:
            if isinstance(value, (list, tuple)):
                for o in value:
                    self._flatten(o)

    def _getrefnum(self, value):
        if isinstance(value, _scalars):
            return self._objtable[(type(value), value)]
        if isinstance(value, Data):
            return self._objtable[(type(value.data), value.data)]
        return self._objidtable[id(value)]

    def _write_size(self, token, size):
        if size < 15:
            self._fp.write(struct.pack('>B', token | size))
        else:
            if size < 256:
                self._fp.write(struct.pack('>BBB', token | 15, 16, size))
            else:
                if size < 65536:
                    self._fp.write(struct.pack('>BBH', token | 15, 17, size))
                else:
                    if size < 4294967296:
                        self._fp.write(struct.pack('>BBL', token | 15, 18, size))
                    else:
                        self._fp.write(struct.pack('>BBQ', token | 15, 19, size))

    def _write_object--- This code section failed: ---

 L. 823         0  LOAD_DEREF               'self'
                2  LOAD_METHOD              _getrefnum
                4  LOAD_FAST                'value'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  STORE_FAST               'ref'

 L. 824        10  LOAD_DEREF               'self'
               12  LOAD_ATTR                _fp
               14  LOAD_METHOD              tell
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  LOAD_DEREF               'self'
               20  LOAD_ATTR                _object_offsets
               22  LOAD_FAST                'ref'
               24  STORE_SUBSCR     

 L. 825        26  LOAD_FAST                'value'
               28  LOAD_CONST               None
               30  COMPARE_OP               is
               32  POP_JUMP_IF_FALSE    50  'to 50'

 L. 826        34  LOAD_DEREF               'self'
               36  LOAD_ATTR                _fp
               38  LOAD_METHOD              write
               40  LOAD_CONST               b'\x00'
               42  CALL_METHOD_1         1  '1 positional argument'
               44  POP_TOP          
            46_48  JUMP_FORWARD        996  'to 996'
             50_0  COME_FROM            32  '32'

 L. 828        50  LOAD_FAST                'value'
               52  LOAD_CONST               False
               54  COMPARE_OP               is
               56  POP_JUMP_IF_FALSE    74  'to 74'

 L. 829        58  LOAD_DEREF               'self'
               60  LOAD_ATTR                _fp
               62  LOAD_METHOD              write
               64  LOAD_CONST               b'\x08'
               66  CALL_METHOD_1         1  '1 positional argument'
               68  POP_TOP          
            70_72  JUMP_FORWARD        996  'to 996'
             74_0  COME_FROM            56  '56'

 L. 831        74  LOAD_FAST                'value'
               76  LOAD_CONST               True
               78  COMPARE_OP               is
               80  POP_JUMP_IF_FALSE    98  'to 98'

 L. 832        82  LOAD_DEREF               'self'
               84  LOAD_ATTR                _fp
               86  LOAD_METHOD              write
               88  LOAD_CONST               b'\t'
               90  CALL_METHOD_1         1  '1 positional argument'
               92  POP_TOP          
            94_96  JUMP_FORWARD        996  'to 996'
             98_0  COME_FROM            80  '80'

 L. 834        98  LOAD_GLOBAL              isinstance
              100  LOAD_FAST                'value'
              102  LOAD_GLOBAL              int
              104  CALL_FUNCTION_2       2  '2 positional arguments'
          106_108  POP_JUMP_IF_FALSE   364  'to 364'

 L. 835       110  LOAD_FAST                'value'
              112  LOAD_CONST               0
              114  COMPARE_OP               <
              116  POP_JUMP_IF_FALSE   180  'to 180'

 L. 836       118  SETUP_EXCEPT        146  'to 146'

 L. 837       120  LOAD_DEREF               'self'
              122  LOAD_ATTR                _fp
              124  LOAD_METHOD              write
              126  LOAD_GLOBAL              struct
              128  LOAD_METHOD              pack
              130  LOAD_STR                 '>Bq'
              132  LOAD_CONST               19
              134  LOAD_FAST                'value'
              136  CALL_METHOD_3         3  '3 positional arguments'
              138  CALL_METHOD_1         1  '1 positional argument'
              140  POP_TOP          
              142  POP_BLOCK        
              144  JUMP_FORWARD        178  'to 178'
            146_0  COME_FROM_EXCEPT    118  '118'

 L. 838       146  DUP_TOP          
              148  LOAD_GLOBAL              struct
              150  LOAD_ATTR                error
              152  COMPARE_OP               exception-match
              154  POP_JUMP_IF_FALSE   176  'to 176'
              156  POP_TOP          
              158  POP_TOP          
              160  POP_TOP          

 L. 839       162  LOAD_GLOBAL              OverflowError
              164  LOAD_FAST                'value'
              166  CALL_FUNCTION_1       1  '1 positional argument'
              168  LOAD_CONST               None
              170  RAISE_VARARGS_2       2  'exception instance with __cause__'
              172  POP_EXCEPT       
              174  JUMP_FORWARD        178  'to 178'
            176_0  COME_FROM           154  '154'
              176  END_FINALLY      
            178_0  COME_FROM           174  '174'
            178_1  COME_FROM           144  '144'
              178  JUMP_FORWARD        996  'to 996'
            180_0  COME_FROM           116  '116'

 L. 840       180  LOAD_FAST                'value'
              182  LOAD_CONST               256
              184  COMPARE_OP               <
              186  POP_JUMP_IF_FALSE   212  'to 212'

 L. 841       188  LOAD_DEREF               'self'
              190  LOAD_ATTR                _fp
              192  LOAD_METHOD              write
              194  LOAD_GLOBAL              struct
              196  LOAD_METHOD              pack
              198  LOAD_STR                 '>BB'
              200  LOAD_CONST               16
              202  LOAD_FAST                'value'
              204  CALL_METHOD_3         3  '3 positional arguments'
              206  CALL_METHOD_1         1  '1 positional argument'
              208  POP_TOP          
              210  JUMP_FORWARD        996  'to 996'
            212_0  COME_FROM           186  '186'

 L. 842       212  LOAD_FAST                'value'
              214  LOAD_CONST               65536
              216  COMPARE_OP               <
              218  POP_JUMP_IF_FALSE   244  'to 244'

 L. 843       220  LOAD_DEREF               'self'
              222  LOAD_ATTR                _fp
              224  LOAD_METHOD              write
              226  LOAD_GLOBAL              struct
              228  LOAD_METHOD              pack
              230  LOAD_STR                 '>BH'
              232  LOAD_CONST               17
              234  LOAD_FAST                'value'
              236  CALL_METHOD_3         3  '3 positional arguments'
              238  CALL_METHOD_1         1  '1 positional argument'
              240  POP_TOP          
              242  JUMP_FORWARD        996  'to 996'
            244_0  COME_FROM           218  '218'

 L. 844       244  LOAD_FAST                'value'
              246  LOAD_CONST               4294967296
              248  COMPARE_OP               <
          250_252  POP_JUMP_IF_FALSE   278  'to 278'

 L. 845       254  LOAD_DEREF               'self'
              256  LOAD_ATTR                _fp
              258  LOAD_METHOD              write
              260  LOAD_GLOBAL              struct
              262  LOAD_METHOD              pack
              264  LOAD_STR                 '>BL'
              266  LOAD_CONST               18
              268  LOAD_FAST                'value'
              270  CALL_METHOD_3         3  '3 positional arguments'
              272  CALL_METHOD_1         1  '1 positional argument'
              274  POP_TOP          
              276  JUMP_FORWARD        996  'to 996'
            278_0  COME_FROM           250  '250'

 L. 846       278  LOAD_FAST                'value'
              280  LOAD_CONST               9223372036854775808
              282  COMPARE_OP               <
          284_286  POP_JUMP_IF_FALSE   312  'to 312'

 L. 847       288  LOAD_DEREF               'self'
              290  LOAD_ATTR                _fp
              292  LOAD_METHOD              write
              294  LOAD_GLOBAL              struct
              296  LOAD_METHOD              pack
              298  LOAD_STR                 '>BQ'
              300  LOAD_CONST               19
              302  LOAD_FAST                'value'
              304  CALL_METHOD_3         3  '3 positional arguments'
              306  CALL_METHOD_1         1  '1 positional argument'
              308  POP_TOP          
              310  JUMP_FORWARD        996  'to 996'
            312_0  COME_FROM           284  '284'

 L. 848       312  LOAD_FAST                'value'
              314  LOAD_CONST               18446744073709551616
              316  COMPARE_OP               <
          318_320  POP_JUMP_IF_FALSE   352  'to 352'

 L. 849       322  LOAD_DEREF               'self'
              324  LOAD_ATTR                _fp
              326  LOAD_METHOD              write
              328  LOAD_CONST               b'\x14'
              330  LOAD_FAST                'value'
              332  LOAD_ATTR                to_bytes
              334  LOAD_CONST               16
              336  LOAD_STR                 'big'
              338  LOAD_CONST               True
              340  LOAD_CONST               ('signed',)
              342  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              344  BINARY_ADD       
              346  CALL_METHOD_1         1  '1 positional argument'
              348  POP_TOP          
              350  JUMP_FORWARD        996  'to 996'
            352_0  COME_FROM           318  '318'

 L. 851       352  LOAD_GLOBAL              OverflowError
              354  LOAD_FAST                'value'
              356  CALL_FUNCTION_1       1  '1 positional argument'
              358  RAISE_VARARGS_1       1  'exception instance'
          360_362  JUMP_FORWARD        996  'to 996'
            364_0  COME_FROM           106  '106'

 L. 853       364  LOAD_GLOBAL              isinstance
              366  LOAD_FAST                'value'
              368  LOAD_GLOBAL              float
              370  CALL_FUNCTION_2       2  '2 positional arguments'
          372_374  POP_JUMP_IF_FALSE   402  'to 402'

 L. 854       376  LOAD_DEREF               'self'
              378  LOAD_ATTR                _fp
              380  LOAD_METHOD              write
              382  LOAD_GLOBAL              struct
              384  LOAD_METHOD              pack
              386  LOAD_STR                 '>Bd'
              388  LOAD_CONST               35
              390  LOAD_FAST                'value'
              392  CALL_METHOD_3         3  '3 positional arguments'
              394  CALL_METHOD_1         1  '1 positional argument'
              396  POP_TOP          
          398_400  JUMP_FORWARD        996  'to 996'
            402_0  COME_FROM           372  '372'

 L. 856       402  LOAD_GLOBAL              isinstance
              404  LOAD_FAST                'value'
              406  LOAD_GLOBAL              datetime
              408  LOAD_ATTR                datetime
              410  CALL_FUNCTION_2       2  '2 positional arguments'
          412_414  POP_JUMP_IF_FALSE   464  'to 464'

 L. 857       416  LOAD_FAST                'value'
              418  LOAD_GLOBAL              datetime
              420  LOAD_METHOD              datetime
              422  LOAD_CONST               2001
              424  LOAD_CONST               1
              426  LOAD_CONST               1
              428  CALL_METHOD_3         3  '3 positional arguments'
              430  BINARY_SUBTRACT  
              432  LOAD_METHOD              total_seconds
              434  CALL_METHOD_0         0  '0 positional arguments'
              436  STORE_FAST               'f'

 L. 858       438  LOAD_DEREF               'self'
              440  LOAD_ATTR                _fp
              442  LOAD_METHOD              write
              444  LOAD_GLOBAL              struct
              446  LOAD_METHOD              pack
              448  LOAD_STR                 '>Bd'
              450  LOAD_CONST               51
              452  LOAD_FAST                'f'
              454  CALL_METHOD_3         3  '3 positional arguments'
              456  CALL_METHOD_1         1  '1 positional argument'
              458  POP_TOP          
          460_462  JUMP_FORWARD        996  'to 996'
            464_0  COME_FROM           412  '412'

 L. 860       464  LOAD_GLOBAL              isinstance
              466  LOAD_FAST                'value'
              468  LOAD_GLOBAL              Data
              470  CALL_FUNCTION_2       2  '2 positional arguments'
          472_474  POP_JUMP_IF_FALSE   512  'to 512'

 L. 861       476  LOAD_DEREF               'self'
              478  LOAD_METHOD              _write_size
              480  LOAD_CONST               64
              482  LOAD_GLOBAL              len
              484  LOAD_FAST                'value'
              486  LOAD_ATTR                data
              488  CALL_FUNCTION_1       1  '1 positional argument'
              490  CALL_METHOD_2         2  '2 positional arguments'
              492  POP_TOP          

 L. 862       494  LOAD_DEREF               'self'
              496  LOAD_ATTR                _fp
              498  LOAD_METHOD              write
              500  LOAD_FAST                'value'
              502  LOAD_ATTR                data
              504  CALL_METHOD_1         1  '1 positional argument'
              506  POP_TOP          
          508_510  JUMP_FORWARD        996  'to 996'
            512_0  COME_FROM           472  '472'

 L. 864       512  LOAD_GLOBAL              isinstance
              514  LOAD_FAST                'value'
              516  LOAD_GLOBAL              bytes
              518  LOAD_GLOBAL              bytearray
              520  BUILD_TUPLE_2         2 
              522  CALL_FUNCTION_2       2  '2 positional arguments'
          524_526  POP_JUMP_IF_FALSE   560  'to 560'

 L. 865       528  LOAD_DEREF               'self'
              530  LOAD_METHOD              _write_size
              532  LOAD_CONST               64
              534  LOAD_GLOBAL              len
              536  LOAD_FAST                'value'
              538  CALL_FUNCTION_1       1  '1 positional argument'
              540  CALL_METHOD_2         2  '2 positional arguments'
              542  POP_TOP          

 L. 866       544  LOAD_DEREF               'self'
              546  LOAD_ATTR                _fp
              548  LOAD_METHOD              write
              550  LOAD_FAST                'value'
              552  CALL_METHOD_1         1  '1 positional argument'
              554  POP_TOP          
          556_558  JUMP_FORWARD        996  'to 996'
            560_0  COME_FROM           524  '524'

 L. 868       560  LOAD_GLOBAL              isinstance
              562  LOAD_FAST                'value'
              564  LOAD_GLOBAL              str
              566  CALL_FUNCTION_2       2  '2 positional arguments'
          568_570  POP_JUMP_IF_FALSE   672  'to 672'

 L. 869       572  SETUP_EXCEPT        604  'to 604'

 L. 870       574  LOAD_FAST                'value'
              576  LOAD_METHOD              encode
              578  LOAD_STR                 'ascii'
              580  CALL_METHOD_1         1  '1 positional argument'
              582  STORE_FAST               't'

 L. 871       584  LOAD_DEREF               'self'
              586  LOAD_METHOD              _write_size
              588  LOAD_CONST               80
              590  LOAD_GLOBAL              len
              592  LOAD_FAST                'value'
              594  CALL_FUNCTION_1       1  '1 positional argument'
              596  CALL_METHOD_2         2  '2 positional arguments'
              598  POP_TOP          
              600  POP_BLOCK        
              602  JUMP_FORWARD        656  'to 656'
            604_0  COME_FROM_EXCEPT    572  '572'

 L. 872       604  DUP_TOP          
              606  LOAD_GLOBAL              UnicodeEncodeError
              608  COMPARE_OP               exception-match
          610_612  POP_JUMP_IF_FALSE   654  'to 654'
              614  POP_TOP          
              616  POP_TOP          
              618  POP_TOP          

 L. 873       620  LOAD_FAST                'value'
              622  LOAD_METHOD              encode
              624  LOAD_STR                 'utf-16be'
              626  CALL_METHOD_1         1  '1 positional argument'
              628  STORE_FAST               't'

 L. 874       630  LOAD_DEREF               'self'
              632  LOAD_METHOD              _write_size
              634  LOAD_CONST               96
              636  LOAD_GLOBAL              len
              638  LOAD_FAST                't'
              640  CALL_FUNCTION_1       1  '1 positional argument'
              642  LOAD_CONST               2
              644  BINARY_FLOOR_DIVIDE
              646  CALL_METHOD_2         2  '2 positional arguments'
              648  POP_TOP          
              650  POP_EXCEPT       
              652  JUMP_FORWARD        656  'to 656'
            654_0  COME_FROM           610  '610'
              654  END_FINALLY      
            656_0  COME_FROM           652  '652'
            656_1  COME_FROM           602  '602'

 L. 876       656  LOAD_DEREF               'self'
              658  LOAD_ATTR                _fp
              660  LOAD_METHOD              write
              662  LOAD_FAST                't'
              664  CALL_METHOD_1         1  '1 positional argument'
              666  POP_TOP          
          668_670  JUMP_FORWARD        996  'to 996'
            672_0  COME_FROM           568  '568'

 L. 878       672  LOAD_GLOBAL              isinstance
              674  LOAD_FAST                'value'
              676  LOAD_GLOBAL              list
              678  LOAD_GLOBAL              tuple
              680  BUILD_TUPLE_2         2 
              682  CALL_FUNCTION_2       2  '2 positional arguments'
          684_686  POP_JUMP_IF_FALSE   762  'to 762'

 L. 879       688  LOAD_CLOSURE             'self'
              690  BUILD_TUPLE_1         1 
              692  LOAD_LISTCOMP            '<code_object <listcomp>>'
              694  LOAD_STR                 '_BinaryPlistWriter._write_object.<locals>.<listcomp>'
              696  MAKE_FUNCTION_8          'closure'
              698  LOAD_FAST                'value'
              700  GET_ITER         
              702  CALL_FUNCTION_1       1  '1 positional argument'
              704  STORE_FAST               'refs'

 L. 880       706  LOAD_GLOBAL              len
              708  LOAD_FAST                'refs'
              710  CALL_FUNCTION_1       1  '1 positional argument'
              712  STORE_FAST               's'

 L. 881       714  LOAD_DEREF               'self'
              716  LOAD_METHOD              _write_size
              718  LOAD_CONST               160
              720  LOAD_FAST                's'
              722  CALL_METHOD_2         2  '2 positional arguments'
              724  POP_TOP          

 L. 882       726  LOAD_DEREF               'self'
              728  LOAD_ATTR                _fp
              730  LOAD_METHOD              write
              732  LOAD_GLOBAL              struct
              734  LOAD_ATTR                pack
              736  LOAD_STR                 '>'
              738  LOAD_DEREF               'self'
              740  LOAD_ATTR                _ref_format
              742  LOAD_FAST                's'
              744  BINARY_MULTIPLY  
              746  BINARY_ADD       
              748  BUILD_TUPLE_1         1 
              750  LOAD_FAST                'refs'
              752  BUILD_TUPLE_UNPACK_WITH_CALL_2     2 
              754  CALL_FUNCTION_EX      0  'positional arguments only'
              756  CALL_METHOD_1         1  '1 positional argument'
              758  POP_TOP          
              760  JUMP_FORWARD        996  'to 996'
            762_0  COME_FROM           684  '684'

 L. 884       762  LOAD_GLOBAL              isinstance
              764  LOAD_FAST                'value'
              766  LOAD_GLOBAL              dict
              768  CALL_FUNCTION_2       2  '2 positional arguments'
          770_772  POP_JUMP_IF_FALSE   988  'to 988'

 L. 885       774  BUILD_LIST_0          0 
              776  BUILD_LIST_0          0 
              778  ROT_TWO          
              780  STORE_FAST               'keyRefs'
              782  STORE_FAST               'valRefs'

 L. 887       784  LOAD_DEREF               'self'
              786  LOAD_ATTR                _sort_keys
          788_790  POP_JUMP_IF_FALSE   806  'to 806'

 L. 888       792  LOAD_GLOBAL              sorted
              794  LOAD_FAST                'value'
              796  LOAD_METHOD              items
              798  CALL_METHOD_0         0  '0 positional arguments'
              800  CALL_FUNCTION_1       1  '1 positional argument'
              802  STORE_FAST               'rootItems'
              804  JUMP_FORWARD        814  'to 814'
            806_0  COME_FROM           788  '788'

 L. 890       806  LOAD_FAST                'value'
              808  LOAD_METHOD              items
              810  CALL_METHOD_0         0  '0 positional arguments'
            812_0  COME_FROM           178  '178'
              812  STORE_FAST               'rootItems'
            814_0  COME_FROM           804  '804'

 L. 892       814  SETUP_LOOP          898  'to 898'
              816  LOAD_FAST                'rootItems'
              818  GET_ITER         
              820  FOR_ITER            896  'to 896'
              822  UNPACK_SEQUENCE_2     2 
              824  STORE_FAST               'k'
              826  STORE_FAST               'v'

 L. 893       828  LOAD_GLOBAL              isinstance
              830  LOAD_FAST                'k'
              832  LOAD_GLOBAL              str
              834  CALL_FUNCTION_2       2  '2 positional arguments'
          836_838  POP_JUMP_IF_TRUE    860  'to 860'

 L. 894       840  LOAD_DEREF               'self'
              842  LOAD_ATTR                _skipkeys
            844_0  COME_FROM           210  '210'
          844_846  POP_JUMP_IF_FALSE   852  'to 852'

 L. 895   848_850  CONTINUE            820  'to 820'
            852_0  COME_FROM           844  '844'

 L. 896       852  LOAD_GLOBAL              TypeError
              854  LOAD_STR                 'keys must be strings'
              856  CALL_FUNCTION_1       1  '1 positional argument'
              858  RAISE_VARARGS_1       1  'exception instance'
            860_0  COME_FROM           836  '836'

 L. 897       860  LOAD_FAST                'keyRefs'
              862  LOAD_METHOD              append
              864  LOAD_DEREF               'self'
              866  LOAD_METHOD              _getrefnum
              868  LOAD_FAST                'k'
              870  CALL_METHOD_1         1  '1 positional argument'
              872  CALL_METHOD_1         1  '1 positional argument'
              874  POP_TOP          
            876_0  COME_FROM           242  '242'

 L. 898       876  LOAD_FAST                'valRefs'
              878  LOAD_METHOD              append
              880  LOAD_DEREF               'self'
              882  LOAD_METHOD              _getrefnum
              884  LOAD_FAST                'v'
              886  CALL_METHOD_1         1  '1 positional argument'
              888  CALL_METHOD_1         1  '1 positional argument'
              890  POP_TOP          
          892_894  JUMP_BACK           820  'to 820'
              896  POP_BLOCK        
            898_0  COME_FROM_LOOP      814  '814'

 L. 900       898  LOAD_GLOBAL              len
              900  LOAD_FAST                'keyRefs'
              902  CALL_FUNCTION_1       1  '1 positional argument'
              904  STORE_FAST               's'

 L. 901       906  LOAD_DEREF               'self'
              908  LOAD_METHOD              _write_size
            910_0  COME_FROM           276  '276'
              910  LOAD_CONST               208
              912  LOAD_FAST                's'
              914  CALL_METHOD_2         2  '2 positional arguments'
              916  POP_TOP          

 L. 902       918  LOAD_DEREF               'self'
              920  LOAD_ATTR                _fp
              922  LOAD_METHOD              write
              924  LOAD_GLOBAL              struct
              926  LOAD_ATTR                pack
              928  LOAD_STR                 '>'
              930  LOAD_DEREF               'self'
              932  LOAD_ATTR                _ref_format
              934  LOAD_FAST                's'
              936  BINARY_MULTIPLY  
              938  BINARY_ADD       
              940  BUILD_TUPLE_1         1 
              942  LOAD_FAST                'keyRefs'
            944_0  COME_FROM           310  '310'
              944  BUILD_TUPLE_UNPACK_WITH_CALL_2     2 
              946  CALL_FUNCTION_EX      0  'positional arguments only'
              948  CALL_METHOD_1         1  '1 positional argument'
              950  POP_TOP          

 L. 903       952  LOAD_DEREF               'self'
              954  LOAD_ATTR                _fp
              956  LOAD_METHOD              write
              958  LOAD_GLOBAL              struct
              960  LOAD_ATTR                pack
              962  LOAD_STR                 '>'
              964  LOAD_DEREF               'self'
              966  LOAD_ATTR                _ref_format
              968  LOAD_FAST                's'
              970  BINARY_MULTIPLY  
              972  BINARY_ADD       
              974  BUILD_TUPLE_1         1 
              976  LOAD_FAST                'valRefs'
              978  BUILD_TUPLE_UNPACK_WITH_CALL_2     2 
              980  CALL_FUNCTION_EX      0  'positional arguments only'
              982  CALL_METHOD_1         1  '1 positional argument'
            984_0  COME_FROM           350  '350'
              984  POP_TOP          
              986  JUMP_FORWARD        996  'to 996'
            988_0  COME_FROM           770  '770'

 L. 906       988  LOAD_GLOBAL              TypeError
              990  LOAD_FAST                'value'
              992  CALL_FUNCTION_1       1  '1 positional argument'
              994  RAISE_VARARGS_1       1  'exception instance'
            996_0  COME_FROM           986  '986'
            996_1  COME_FROM           760  '760'
            996_2  COME_FROM           668  '668'
            996_3  COME_FROM           556  '556'
            996_4  COME_FROM           508  '508'
            996_5  COME_FROM           460  '460'
            996_6  COME_FROM           398  '398'
            996_7  COME_FROM           360  '360'
            996_8  COME_FROM            94  '94'
            996_9  COME_FROM            70  '70'
           996_10  COME_FROM            46  '46'

Parse error at or near `COME_FROM' instruction at offset 812_0


def _is_fmt_binary(header):
    return header[:8] == b'bplist00'


_FORMATS = {FMT_XML: dict(detect=_is_fmt_xml,
            parser=_PlistParser,
            writer=_PlistWriter), 
 
 FMT_BINARY: dict(detect=_is_fmt_binary,
               parser=_BinaryPlistParser,
               writer=_BinaryPlistWriter)}

def load(fp, *, fmt=None, use_builtin_types=True, dict_type=dict):
    if fmt is None:
        header = fp.read(32)
        fp.seek(0)
        for info in _FORMATS.values():
            if info['detect'](header):
                P = info['parser']
                break
        else:
            raise InvalidFileException()

    else:
        P = _FORMATS[fmt]['parser']
    p = P(use_builtin_types=use_builtin_types, dict_type=dict_type)
    return p.parse(fp)


def loads(value, *, fmt=None, use_builtin_types=True, dict_type=dict):
    fp = BytesIO(value)
    return load(fp,
      fmt=fmt, use_builtin_types=use_builtin_types, dict_type=dict_type)


def dump(value, fp, *, fmt=FMT_XML, sort_keys=True, skipkeys=False):
    if fmt not in _FORMATS:
        raise ValueError('Unsupported format: %r' % (fmt,))
    writer = _FORMATS[fmt]['writer'](fp, sort_keys=sort_keys, skipkeys=skipkeys)
    writer.write(value)


def dumps(value, *, fmt=FMT_XML, skipkeys=False, sort_keys=True):
    fp = BytesIO()
    dump(value, fp, fmt=fmt, skipkeys=skipkeys, sort_keys=sort_keys)
    return fp.getvalue()