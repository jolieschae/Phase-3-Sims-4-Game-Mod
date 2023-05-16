# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\tarfile.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 95129 bytes
version = '0.9.0'
__author__ = 'Lars Gustäbel (lars@gustaebel.de)'
__credits__ = 'Gustavo Niemeyer, Niels Gustäbel, Richard Townsend.'
from builtins import open as bltn_open
import sys, os, io, shutil, stat, time, struct, copy, re
try:
    import pwd
except ImportError:
    pwd = None

try:
    import grp
except ImportError:
    grp = None

symlink_exception = (
 AttributeError, NotImplementedError)
try:
    symlink_exception += (OSError,)
except NameError:
    pass

__all__ = [
 "'TarFile'", "'TarInfo'", "'is_tarfile'", "'TarError'", "'ReadError'", 
 "'CompressionError'", 
 "'StreamError'", "'ExtractError'", "'HeaderError'", 
 "'ENCODING'", "'USTAR_FORMAT'", 
 "'GNU_FORMAT'", "'PAX_FORMAT'", 
 "'DEFAULT_FORMAT'", "'open'"]
NUL = b'\x00'
BLOCKSIZE = 512
RECORDSIZE = BLOCKSIZE * 20
GNU_MAGIC = b'ustar  \x00'
POSIX_MAGIC = b'ustar\x0000'
LENGTH_NAME = 100
LENGTH_LINK = 100
LENGTH_PREFIX = 155
REGTYPE = b'0'
AREGTYPE = b'\x00'
LNKTYPE = b'1'
SYMTYPE = b'2'
CHRTYPE = b'3'
BLKTYPE = b'4'
DIRTYPE = b'5'
FIFOTYPE = b'6'
CONTTYPE = b'7'
GNUTYPE_LONGNAME = b'L'
GNUTYPE_LONGLINK = b'K'
GNUTYPE_SPARSE = b'S'
XHDTYPE = b'x'
XGLTYPE = b'g'
SOLARIS_XHDTYPE = b'X'
USTAR_FORMAT = 0
GNU_FORMAT = 1
PAX_FORMAT = 2
DEFAULT_FORMAT = GNU_FORMAT
SUPPORTED_TYPES = (
 REGTYPE, AREGTYPE, LNKTYPE,
 SYMTYPE, DIRTYPE, FIFOTYPE,
 CONTTYPE, CHRTYPE, BLKTYPE,
 GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
 GNUTYPE_SPARSE)
REGULAR_TYPES = (
 REGTYPE, AREGTYPE,
 CONTTYPE, GNUTYPE_SPARSE)
GNU_TYPES = (
 GNUTYPE_LONGNAME, GNUTYPE_LONGLINK,
 GNUTYPE_SPARSE)
PAX_FIELDS = ('path', 'linkpath', 'size', 'mtime', 'uid', 'gid', 'uname', 'gname')
PAX_NAME_FIELDS = {
 'path', 'linkpath', 'uname', 'gname'}
PAX_NUMBER_FIELDS = {
 'atime': 'float', 
 'ctime': 'float', 
 'mtime': 'float', 
 'uid': 'int', 
 'gid': 'int', 
 'size': 'int'}
if os.name == 'nt':
    ENCODING = 'utf-8'
else:
    ENCODING = sys.getfilesystemencoding()

def stn(s, length, encoding, errors):
    s = s.encode(encoding, errors)
    return s[:length] + (length - len(s)) * NUL


def nts(s, encoding, errors):
    p = s.find(b'\x00')
    if p != -1:
        s = s[:p]
    return s.decode(encoding, errors)


def nti(s):
    if s[0] in (128, 255):
        n = 0
        for i in range(len(s) - 1):
            n <<= 8
            n += s[i + 1]

        if s[0] == 255:
            n = -(256 ** (len(s) - 1) - n)
    else:
        try:
            s = nts(s, 'ascii', 'strict')
            n = int(s.strip() or '0', 8)
        except ValueError:
            raise InvalidHeaderError('invalid header')

    return n


def itn(n, digits=8, format=DEFAULT_FORMAT):
    n = int(n)
    if 0 <= n < 8 ** (digits - 1):
        s = bytes('%0*o' % (digits - 1, n), 'ascii') + NUL
    else:
        if format == GNU_FORMAT:
            if -256 ** (digits - 1) <= n < 256 ** (digits - 1):
                if n >= 0:
                    s = bytearray([128])
            else:
                s = bytearray([255])
                n = 256 ** digits + n
            for i in range(digits - 1):
                s.insert(1, n & 255)
                n >>= 8

        else:
            raise ValueError('overflow in number field')
    return s


def calc_chksums(buf):
    unsigned_chksum = 256 + sum(struct.unpack_from('148B8x356B', buf))
    signed_chksum = 256 + sum(struct.unpack_from('148b8x356b', buf))
    return (unsigned_chksum, signed_chksum)


def copyfileobj(src, dst, length=None, exception=OSError, bufsize=None):
    bufsize = bufsize or 16384
    if length == 0:
        return
    if length is None:
        shutil.copyfileobj(src, dst, bufsize)
        return
    blocks, remainder = divmod(length, bufsize)
    for b in range(blocks):
        buf = src.read(bufsize)
        if len(buf) < bufsize:
            raise exception('unexpected end of data')
        dst.write(buf)

    if remainder != 0:
        buf = src.read(remainder)
        if len(buf) < remainder:
            raise exception('unexpected end of data')
        dst.write(buf)


def filemode(mode):
    import warnings
    warnings.warn('deprecated in favor of stat.filemode', DeprecationWarning, 2)
    return stat.filemode(mode)


def _safe_print(s):
    encoding = getattr(sys.stdout, 'encoding', None)
    if encoding is not None:
        s = s.encode(encoding, 'backslashreplace').decode(encoding)
    print(s, end=' ')


class TarError(Exception):
    pass


class ExtractError(TarError):
    pass


class ReadError(TarError):
    pass


class CompressionError(TarError):
    pass


class StreamError(TarError):
    pass


class HeaderError(TarError):
    pass


class EmptyHeaderError(HeaderError):
    pass


class TruncatedHeaderError(HeaderError):
    pass


class EOFHeaderError(HeaderError):
    pass


class InvalidHeaderError(HeaderError):
    pass


class SubsequentHeaderError(HeaderError):
    pass


class _LowLevelFile:

    def __init__(self, name, mode):
        mode = {'r':os.O_RDONLY, 
         'w':os.O_WRONLY | os.O_CREAT | os.O_TRUNC}[mode]
        if hasattr(os, 'O_BINARY'):
            mode |= os.O_BINARY
        self.fd = os.open(name, mode, 438)

    def close(self):
        os.close(self.fd)

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, s):
        os.write(self.fd, s)


class _Stream:

    def __init__(self, name, mode, comptype, fileobj, bufsize):
        self._extfileobj = True
        if fileobj is None:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = False
        if comptype == '*':
            fileobj = _StreamProxy(fileobj)
            comptype = fileobj.getcomptype()
        self.name = name or ''
        self.mode = mode
        self.comptype = comptype
        self.fileobj = fileobj
        self.bufsize = bufsize
        self.buf = b''
        self.pos = 0
        self.closed = False
        try:
            if comptype == 'gz':
                try:
                    import zlib
                except ImportError:
                    raise CompressionError('zlib module is not available')

                self.zlib = zlib
                self.crc = zlib.crc32(b'')
                if mode == 'r':
                    self._init_read_gz()
                    self.exception = zlib.error
                else:
                    self._init_write_gz()
            else:
                if comptype == 'bz2':
                    try:
                        import bz2
                    except ImportError:
                        raise CompressionError('bz2 module is not available')

                    if mode == 'r':
                        self.dbuf = b''
                        self.cmp = bz2.BZ2Decompressor()
                        self.exception = OSError
                    else:
                        self.cmp = bz2.BZ2Compressor()
                else:
                    if comptype == 'xz':
                        try:
                            import lzma
                        except ImportError:
                            raise CompressionError('lzma module is not available')

                        if mode == 'r':
                            self.dbuf = b''
                            self.cmp = lzma.LZMADecompressor()
                            self.exception = lzma.LZMAError
                        else:
                            self.cmp = lzma.LZMACompressor()
                    else:
                        if comptype != 'tar':
                            raise CompressionError('unknown compression type %r' % comptype)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    def __del__(self):
        if hasattr(self, 'closed'):
            if not self.closed:
                self.close()

    def _init_write_gz(self):
        self.cmp = self.zlib.compressobj(9, self.zlib.DEFLATED, -self.zlib.MAX_WBITS, self.zlib.DEF_MEM_LEVEL, 0)
        timestamp = struct.pack('<L', int(time.time()))
        self._Stream__write(b'\x1f\x8b\x08\x08' + timestamp + b'\x02\xff')
        if self.name.endswith('.gz'):
            self.name = self.name[:-3]
        self._Stream__write(self.name.encode('iso-8859-1', 'replace') + NUL)

    def write(self, s):
        if self.comptype == 'gz':
            self.crc = self.zlib.crc32(s, self.crc)
        self.pos += len(s)
        if self.comptype != 'tar':
            s = self.cmp.compress(s)
        self._Stream__write(s)

    def __write(self, s):
        self.buf += s
        while len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            if self.mode == 'w':
                if self.comptype != 'tar':
                    self.buf += self.cmp.flush()
            if self.mode == 'w':
                if self.buf:
                    self.fileobj.write(self.buf)
                    self.buf = b''
                    if self.comptype == 'gz':
                        self.fileobj.write(struct.pack('<L', self.crc))
                        self.fileobj.write(struct.pack('<L', self.pos & 4294967295))
        finally:
            if not self._extfileobj:
                self.fileobj.close()

    def _init_read_gz(self):
        self.cmp = self.zlib.decompressobj(-self.zlib.MAX_WBITS)
        self.dbuf = b''
        if self._Stream__read(2) != b'\x1f\x8b':
            raise ReadError('not a gzip file')
        if self._Stream__read(1) != b'\x08':
            raise CompressionError('unsupported compression method')
        flag = ord(self._Stream__read(1))
        self._Stream__read(6)
        if flag & 4:
            xlen = ord(self._Stream__read(1)) + 256 * ord(self._Stream__read(1))
            self.read(xlen)
        if flag & 8:
            while 1:
                s = self._Stream__read(1)
                if not s or s == NUL:
                    break

        if flag & 16:
            while 1:
                s = self._Stream__read(1)
                if not s or s == NUL:
                    break

        if flag & 2:
            self._Stream__read(2)

    def tell(self):
        return self.pos

    def seek(self, pos=0):
        if pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            for i in range(blocks):
                self.read(self.bufsize)

            self.read(remainder)
        else:
            raise StreamError('seeking backwards is not allowed')
        return self.pos

    def read(self, size=None):
        if size is None:
            t = []
            while True:
                buf = self._read(self.bufsize)
                if not buf:
                    break
                t.append(buf)

            buf = ''.join(t)
        else:
            buf = self._read(size)
        self.pos += len(buf)
        return buf

    def _read(self, size):
        if self.comptype == 'tar':
            return self._Stream__read(size)
        c = len(self.dbuf)
        while c < size:
            buf = self._Stream__read(self.bufsize)
            if not buf:
                break
            try:
                buf = self.cmp.decompress(buf)
            except self.exception:
                raise ReadError('invalid compressed data')

            self.dbuf += buf
            c += len(buf)

        buf = self.dbuf[:size]
        self.dbuf = self.dbuf[size:]
        return buf

    def __read(self, size):
        c = len(self.buf)
        while c < size:
            buf = self.fileobj.read(self.bufsize)
            if not buf:
                break
            self.buf += buf
            c += len(buf)

        buf = self.buf[:size]
        self.buf = self.buf[size:]
        return buf


class _StreamProxy(object):

    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.buf = self.fileobj.read(BLOCKSIZE)

    def read(self, size):
        self.read = self.fileobj.read
        return self.buf

    def getcomptype(self):
        if self.buf.startswith(b'\x1f\x8b\x08'):
            return 'gz'
        if self.buf[0:3] == b'BZh':
            if self.buf[4:10] == b'1AY&SY':
                return 'bz2'
        if self.buf.startswith((b']\x00\x00\x80', b'\xfd7zXZ')):
            return 'xz'
        return 'tar'

    def close(self):
        self.fileobj.close()


class _FileInFile(object):

    def __init__(self, fileobj, offset, size, blockinfo=None):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = getattr(fileobj, 'name', None)
        self.closed = False
        if blockinfo is None:
            blockinfo = [
             (
              0, size)]
        self.map_index = 0
        self.map = []
        lastpos = 0
        realpos = self.offset
        for offset, size in blockinfo:
            if offset > lastpos:
                self.map.append((False, lastpos, offset, None))
            self.map.append((True, offset, offset + size, realpos))
            realpos += size
            lastpos = offset + size

        if lastpos < self.size:
            self.map.append((False, lastpos, self.size, None))

    def flush(self):
        pass

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return self.fileobj.seekable()

    def tell(self):
        return self.position

    def seek(self, position, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        else:
            if whence == io.SEEK_CUR:
                if position < 0:
                    self.position = max(self.position + position, 0)
                else:
                    self.position = min(self.position + position, self.size)
            elif whence == io.SEEK_END:
                self.position = max(min(self.size + position, self.size), 0)
            else:
                raise ValueError('Invalid argument')
        return self.position

    def read(self, size=None):
        if size is None:
            size = self.size - self.position
        else:
            size = min(size, self.size - self.position)
        buf = b''
        while size > 0:
            while 1:
                data, start, stop, offset = self.map[self.map_index]
                if start <= self.position < stop:
                    break
                else:
                    self.map_index += 1
                    if self.map_index == len(self.map):
                        self.map_index = 0

            length = min(size, stop - self.position)
            if data:
                self.fileobj.seek(offset + (self.position - start))
                b = self.fileobj.read(length)
                if len(b) != length:
                    raise ReadError('unexpected end of data')
                buf += b
            else:
                buf += NUL * length
            size -= length
            self.position += length

        return buf

    def readinto(self, b):
        buf = self.read(len(b))
        b[:len(buf)] = buf
        return len(buf)

    def close(self):
        self.closed = True


class ExFileObject(io.BufferedReader):

    def __init__(self, tarfile, tarinfo):
        fileobj = _FileInFile(tarfile.fileobj, tarinfo.offset_data, tarinfo.size, tarinfo.sparse)
        super().__init__(fileobj)


class TarInfo(object):
    __slots__ = ('name', 'mode', 'uid', 'gid', 'size', 'mtime', 'chksum', 'type', 'linkname',
                 'uname', 'gname', 'devmajor', 'devminor', 'offset', 'offset_data',
                 'pax_headers', 'sparse', 'tarfile', '_sparse_structs', '_link_target')

    def __init__(self, name=''):
        self.name = name
        self.mode = 420
        self.uid = 0
        self.gid = 0
        self.size = 0
        self.mtime = 0
        self.chksum = 0
        self.type = REGTYPE
        self.linkname = ''
        self.uname = ''
        self.gname = ''
        self.devmajor = 0
        self.devminor = 0
        self.offset = 0
        self.offset_data = 0
        self.sparse = None
        self.pax_headers = {}

    @property
    def path(self):
        return self.name

    @path.setter
    def path(self, name):
        self.name = name

    @property
    def linkpath(self):
        return self.linkname

    @linkpath.setter
    def linkpath(self, linkname):
        self.linkname = linkname

    def __repr__(self):
        return '<%s %r at %#x>' % (self.__class__.__name__, self.name, id(self))

    def get_info(self):
        info = {'name':self.name, 
         'mode':self.mode & 4095, 
         'uid':self.uid, 
         'gid':self.gid, 
         'size':self.size, 
         'mtime':self.mtime, 
         'chksum':self.chksum, 
         'type':self.type, 
         'linkname':self.linkname, 
         'uname':self.uname, 
         'gname':self.gname, 
         'devmajor':self.devmajor, 
         'devminor':self.devminor}
        if info['type'] == DIRTYPE:
            if not info['name'].endswith('/'):
                info['name'] += '/'
        return info

    def tobuf(self, format=DEFAULT_FORMAT, encoding=ENCODING, errors='surrogateescape'):
        info = self.get_info()
        if format == USTAR_FORMAT:
            return self.create_ustar_header(info, encoding, errors)
        if format == GNU_FORMAT:
            return self.create_gnu_header(info, encoding, errors)
        if format == PAX_FORMAT:
            return self.create_pax_header(info, encoding)
        raise ValueError('invalid format')

    def create_ustar_header(self, info, encoding, errors):
        info['magic'] = POSIX_MAGIC
        if len(info['linkname'].encode(encoding, errors)) > LENGTH_LINK:
            raise ValueError('linkname is too long')
        if len(info['name'].encode(encoding, errors)) > LENGTH_NAME:
            info['prefix'], info['name'] = self._posix_split_name(info['name'], encoding, errors)
        return self._create_header(info, USTAR_FORMAT, encoding, errors)

    def create_gnu_header(self, info, encoding, errors):
        info['magic'] = GNU_MAGIC
        buf = b''
        if len(info['linkname'].encode(encoding, errors)) > LENGTH_LINK:
            buf += self._create_gnu_long_header(info['linkname'], GNUTYPE_LONGLINK, encoding, errors)
        if len(info['name'].encode(encoding, errors)) > LENGTH_NAME:
            buf += self._create_gnu_long_header(info['name'], GNUTYPE_LONGNAME, encoding, errors)
        return buf + self._create_header(info, GNU_FORMAT, encoding, errors)

    def create_pax_header--- This code section failed: ---

 L. 852         0  LOAD_GLOBAL              POSIX_MAGIC
                2  LOAD_FAST                'info'
                4  LOAD_STR                 'magic'
                6  STORE_SUBSCR     

 L. 853         8  LOAD_FAST                'self'
               10  LOAD_ATTR                pax_headers
               12  LOAD_METHOD              copy
               14  CALL_METHOD_0         0  '0 positional arguments'
               16  STORE_FAST               'pax_headers'

 L. 857        18  SETUP_LOOP          152  'to 152'

 L. 858        20  LOAD_STR                 'name'
               22  LOAD_STR                 'path'
               24  LOAD_GLOBAL              LENGTH_NAME
               26  BUILD_TUPLE_3         3 
               28  LOAD_STR                 'linkname'
               30  LOAD_STR                 'linkpath'
               32  LOAD_GLOBAL              LENGTH_LINK
               34  BUILD_TUPLE_3         3 

 L. 859        36  LOAD_CONST               ('uname', 'uname', 32)
               38  LOAD_CONST               ('gname', 'gname', 32)
               40  BUILD_TUPLE_4         4 
               42  GET_ITER         
             44_0  COME_FROM           134  '134'
               44  FOR_ITER            150  'to 150'
               46  UNPACK_SEQUENCE_3     3 
               48  STORE_FAST               'name'
               50  STORE_FAST               'hname'
               52  STORE_FAST               'length'

 L. 861        54  LOAD_FAST                'hname'
               56  LOAD_FAST                'pax_headers'
               58  COMPARE_OP               in
               60  POP_JUMP_IF_FALSE    64  'to 64'

 L. 863        62  CONTINUE             44  'to 44'
             64_0  COME_FROM            60  '60'

 L. 866        64  SETUP_EXCEPT         86  'to 86'

 L. 867        66  LOAD_FAST                'info'
               68  LOAD_FAST                'name'
               70  BINARY_SUBSCR    
               72  LOAD_METHOD              encode
               74  LOAD_STR                 'ascii'
               76  LOAD_STR                 'strict'
               78  CALL_METHOD_2         2  '2 positional arguments'
               80  POP_TOP          
               82  POP_BLOCK        
               84  JUMP_FORWARD        120  'to 120'
             86_0  COME_FROM_EXCEPT     64  '64'

 L. 868        86  DUP_TOP          
               88  LOAD_GLOBAL              UnicodeEncodeError
               90  COMPARE_OP               exception-match
               92  POP_JUMP_IF_FALSE   118  'to 118'
               94  POP_TOP          
               96  POP_TOP          
               98  POP_TOP          

 L. 869       100  LOAD_FAST                'info'
              102  LOAD_FAST                'name'
              104  BINARY_SUBSCR    
              106  LOAD_FAST                'pax_headers'
              108  LOAD_FAST                'hname'
              110  STORE_SUBSCR     

 L. 870       112  CONTINUE_LOOP        44  'to 44'
              114  POP_EXCEPT       
              116  JUMP_FORWARD        120  'to 120'
            118_0  COME_FROM            92  '92'
              118  END_FINALLY      
            120_0  COME_FROM           116  '116'
            120_1  COME_FROM            84  '84'

 L. 872       120  LOAD_GLOBAL              len
              122  LOAD_FAST                'info'
              124  LOAD_FAST                'name'
              126  BINARY_SUBSCR    
              128  CALL_FUNCTION_1       1  '1 positional argument'
              130  LOAD_FAST                'length'
              132  COMPARE_OP               >
              134  POP_JUMP_IF_FALSE    44  'to 44'

 L. 873       136  LOAD_FAST                'info'
              138  LOAD_FAST                'name'
              140  BINARY_SUBSCR    
              142  LOAD_FAST                'pax_headers'
              144  LOAD_FAST                'hname'
              146  STORE_SUBSCR     
              148  JUMP_BACK            44  'to 44'
              150  POP_BLOCK        
            152_0  COME_FROM_LOOP       18  '18'

 L. 877       152  SETUP_LOOP          258  'to 258'
              154  LOAD_CONST               (('uid', 8), ('gid', 8), ('size', 12), ('mtime', 12))
              156  GET_ITER         
            158_0  COME_FROM           232  '232'
              158  FOR_ITER            256  'to 256'
              160  UNPACK_SEQUENCE_2     2 
              162  STORE_FAST               'name'
              164  STORE_FAST               'digits'

 L. 878       166  LOAD_FAST                'name'
              168  LOAD_FAST                'pax_headers'
              170  COMPARE_OP               in
              172  POP_JUMP_IF_FALSE   184  'to 184'

 L. 880       174  LOAD_CONST               0
              176  LOAD_FAST                'info'
              178  LOAD_FAST                'name'
              180  STORE_SUBSCR     

 L. 881       182  CONTINUE            158  'to 158'
            184_0  COME_FROM           172  '172'

 L. 883       184  LOAD_FAST                'info'
              186  LOAD_FAST                'name'
              188  BINARY_SUBSCR    
              190  STORE_FAST               'val'

 L. 884       192  LOAD_CONST               0
              194  LOAD_FAST                'val'
              196  DUP_TOP          
              198  ROT_THREE        
              200  COMPARE_OP               <=
              202  POP_JUMP_IF_FALSE   220  'to 220'
              204  LOAD_CONST               8
              206  LOAD_FAST                'digits'
              208  LOAD_CONST               1
              210  BINARY_SUBTRACT  
              212  BINARY_POWER     
              214  COMPARE_OP               <
              216  POP_JUMP_IF_FALSE   234  'to 234'
              218  JUMP_FORWARD        224  'to 224'
            220_0  COME_FROM           202  '202'
              220  POP_TOP          
              222  JUMP_FORWARD        234  'to 234'
            224_0  COME_FROM           218  '218'
              224  LOAD_GLOBAL              isinstance
              226  LOAD_FAST                'val'
              228  LOAD_GLOBAL              float
              230  CALL_FUNCTION_2       2  '2 positional arguments'
              232  POP_JUMP_IF_FALSE   158  'to 158'
            234_0  COME_FROM           222  '222'
            234_1  COME_FROM           216  '216'

 L. 885       234  LOAD_GLOBAL              str
              236  LOAD_FAST                'val'
              238  CALL_FUNCTION_1       1  '1 positional argument'
              240  LOAD_FAST                'pax_headers'
              242  LOAD_FAST                'name'
              244  STORE_SUBSCR     

 L. 886       246  LOAD_CONST               0
              248  LOAD_FAST                'info'
              250  LOAD_FAST                'name'
              252  STORE_SUBSCR     
              254  JUMP_BACK           158  'to 158'
              256  POP_BLOCK        
            258_0  COME_FROM_LOOP      152  '152'

 L. 889       258  LOAD_FAST                'pax_headers'
          260_262  POP_JUMP_IF_FALSE   280  'to 280'

 L. 890       264  LOAD_FAST                'self'
              266  LOAD_METHOD              _create_pax_generic_header
              268  LOAD_FAST                'pax_headers'
              270  LOAD_GLOBAL              XHDTYPE
              272  LOAD_FAST                'encoding'
              274  CALL_METHOD_3         3  '3 positional arguments'
              276  STORE_FAST               'buf'
              278  JUMP_FORWARD        284  'to 284'
            280_0  COME_FROM           260  '260'

 L. 892       280  LOAD_CONST               b''
              282  STORE_FAST               'buf'
            284_0  COME_FROM           278  '278'

 L. 894       284  LOAD_FAST                'buf'
              286  LOAD_FAST                'self'
              288  LOAD_METHOD              _create_header
              290  LOAD_FAST                'info'
              292  LOAD_GLOBAL              USTAR_FORMAT
              294  LOAD_STR                 'ascii'
              296  LOAD_STR                 'replace'
              298  CALL_METHOD_4         4  '4 positional arguments'
              300  BINARY_ADD       
              302  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_BLOCK' instruction at offset 256

    @classmethod
    def create_pax_global_header(cls, pax_headers):
        return cls._create_pax_generic_header(pax_headers, XGLTYPE, 'utf-8')

    def _posix_split_name(self, name, encoding, errors):
        components = name.split('/')
        for i in range(1, len(components)):
            prefix = '/'.join(components[:i])
            name = '/'.join(components[i:])
            if len(prefix.encode(encoding, errors)) <= LENGTH_PREFIX and len(name.encode(encoding, errors)) <= LENGTH_NAME:
                break
        else:
            raise ValueError('name is too long')

        return (prefix, name)

    @staticmethod
    def _create_header(info, format, encoding, errors):
        parts = [
         stn(info.get('name', ''), 100, encoding, errors),
         itn(info.get('mode', 0) & 4095, 8, format),
         itn(info.get('uid', 0), 8, format),
         itn(info.get('gid', 0), 8, format),
         itn(info.get('size', 0), 12, format),
         itn(info.get('mtime', 0), 12, format),
         b'        ',
         info.get('type', REGTYPE),
         stn(info.get('linkname', ''), 100, encoding, errors),
         info.get('magic', POSIX_MAGIC),
         stn(info.get('uname', ''), 32, encoding, errors),
         stn(info.get('gname', ''), 32, encoding, errors),
         itn(info.get('devmajor', 0), 8, format),
         itn(info.get('devminor', 0), 8, format),
         stn(info.get('prefix', ''), 155, encoding, errors)]
        buf = struct.pack('%ds' % BLOCKSIZE, (b'').join(parts))
        chksum = calc_chksums(buf[-BLOCKSIZE:])[0]
        buf = buf[:-364] + bytes('%06o\x00' % chksum, 'ascii') + buf[-357:]
        return buf

    @staticmethod
    def _create_payload(payload):
        blocks, remainder = divmod(len(payload), BLOCKSIZE)
        if remainder > 0:
            payload += (BLOCKSIZE - remainder) * NUL
        return payload

    @classmethod
    def _create_gnu_long_header(cls, name, type, encoding, errors):
        name = name.encode(encoding, errors) + NUL
        info = {}
        info['name'] = '././@LongLink'
        info['type'] = type
        info['size'] = len(name)
        info['magic'] = GNU_MAGIC
        return cls._create_header(info, USTAR_FORMAT, encoding, errors) + cls._create_payload(name)

    @classmethod
    def _create_pax_generic_header(cls, pax_headers, type, encoding):
        binary = False
        for keyword, value in pax_headers.items():
            try:
                value.encode('utf-8', 'strict')
            except UnicodeEncodeError:
                binary = True
                break

        records = b''
        if binary:
            records += b'21 hdrcharset=BINARY\n'
        for keyword, value in pax_headers.items():
            keyword = keyword.encode('utf-8')
            if binary:
                value = value.encode(encoding, 'surrogateescape')
            else:
                value = value.encode('utf-8')
            l = len(keyword) + len(value) + 3
            n = p = 0
            while True:
                n = l + len(str(p))
                if n == p:
                    break
                p = n

            records += bytes(str(p), 'ascii') + b' ' + keyword + b'=' + value + b'\n'

        info = {}
        info['name'] = '././@PaxHeader'
        info['type'] = type
        info['size'] = len(records)
        info['magic'] = POSIX_MAGIC
        return cls._create_header(info, USTAR_FORMAT, 'ascii', 'replace') + cls._create_payload(records)

    @classmethod
    def frombuf(cls, buf, encoding, errors):
        if len(buf) == 0:
            raise EmptyHeaderError('empty header')
        else:
            if len(buf) != BLOCKSIZE:
                raise TruncatedHeaderError('truncated header')
            else:
                if buf.count(NUL) == BLOCKSIZE:
                    raise EOFHeaderError('end of file header')
                chksum = nti(buf[148:156])
                if chksum not in calc_chksums(buf):
                    raise InvalidHeaderError('bad checksum')
                obj = cls()
                obj.name = nts(buf[0:100], encoding, errors)
                obj.mode = nti(buf[100:108])
                obj.uid = nti(buf[108:116])
                obj.gid = nti(buf[116:124])
                obj.size = nti(buf[124:136])
                obj.mtime = nti(buf[136:148])
                obj.chksum = chksum
                obj.type = buf[156:157]
                obj.linkname = nts(buf[157:257], encoding, errors)
                obj.uname = nts(buf[265:297], encoding, errors)
                obj.gname = nts(buf[297:329], encoding, errors)
                obj.devmajor = nti(buf[329:337])
                obj.devminor = nti(buf[337:345])
                prefix = nts(buf[345:500], encoding, errors)
                if obj.type == AREGTYPE and obj.name.endswith('/'):
                    obj.type = DIRTYPE
            if obj.type == GNUTYPE_SPARSE:
                pos = 386
                structs = []
                for i in range(4):
                    try:
                        offset = nti(buf[pos:pos + 12])
                        numbytes = nti(buf[pos + 12:pos + 24])
                    except ValueError:
                        break

                    structs.append((offset, numbytes))
                    pos += 24

                isextended = bool(buf[482])
                origsize = nti(buf[483:495])
                obj._sparse_structs = (structs, isextended, origsize)
            if obj.isdir():
                obj.name = obj.name.rstrip('/')
            if prefix and obj.type not in GNU_TYPES:
                obj.name = prefix + '/' + obj.name
        return obj

    @classmethod
    def fromtarfile(cls, tarfile):
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf, tarfile.encoding, tarfile.errors)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        return obj._proc_member(tarfile)

    def _proc_member(self, tarfile):
        if self.type in (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            return self._proc_gnulong(tarfile)
        if self.type == GNUTYPE_SPARSE:
            return self._proc_sparse(tarfile)
        if self.type in (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            return self._proc_pax(tarfile)
        return self._proc_builtin(tarfile)

    def _proc_builtin(self, tarfile):
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        if self.isreg() or self.type not in SUPPORTED_TYPES:
            offset += self._block(self.size)
        tarfile.offset = offset
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)
        return self

    def _proc_gnulong(self, tarfile):
        buf = tarfile.fileobj.read(self._block(self.size))
        try:
            next = self.fromtarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError('missing or bad subsequent header')

        next.offset = self.offset
        if self.type == GNUTYPE_LONGNAME:
            next.name = nts(buf, tarfile.encoding, tarfile.errors)
        else:
            if self.type == GNUTYPE_LONGLINK:
                next.linkname = nts(buf, tarfile.encoding, tarfile.errors)
        return next

    def _proc_sparse(self, tarfile):
        structs, isextended, origsize = self._sparse_structs
        del self._sparse_structs
        while isextended:
            buf = tarfile.fileobj.read(BLOCKSIZE)
            pos = 0
            for i in range(21):
                try:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                except ValueError:
                    break

                if offset:
                    if numbytes:
                        structs.append((offset, numbytes))
                pos += 24

            isextended = bool(buf[504])

        self.sparse = structs
        self.offset_data = tarfile.fileobj.tell()
        tarfile.offset = self.offset_data + self._block(self.size)
        self.size = origsize
        return self

    def _proc_pax(self, tarfile):
        buf = tarfile.fileobj.read(self._block(self.size))
        if self.type == XGLTYPE:
            pax_headers = tarfile.pax_headers
        else:
            pax_headers = tarfile.pax_headers.copy()
        match = re.search(b'\\d+ hdrcharset=([^\\n]+)\\n', buf)
        if match is not None:
            pax_headers['hdrcharset'] = match.group(1).decode('utf-8')
        else:
            hdrcharset = pax_headers.get('hdrcharset')
            if hdrcharset == 'BINARY':
                encoding = tarfile.encoding
            else:
                encoding = 'utf-8'
        regex = re.compile(b'(\\d+) ([^=]+)=')
        pos = 0
        while True:
            match = regex.match(buf, pos)
            if not match:
                break
            else:
                length, keyword = match.groups()
                length = int(length)
                value = buf[match.end(2) + 1:match.start(1) + length - 1]
                keyword = self._decode_pax_field(keyword, 'utf-8', 'utf-8', tarfile.errors)
                if keyword in PAX_NAME_FIELDS:
                    value = self._decode_pax_field(value, encoding, tarfile.encoding, tarfile.errors)
                else:
                    value = self._decode_pax_field(value, 'utf-8', 'utf-8', tarfile.errors)
            pax_headers[keyword] = value
            pos += length

        try:
            next = self.fromtarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError('missing or bad subsequent header')

        if 'GNU.sparse.map' in pax_headers:
            self._proc_gnusparse_01(next, pax_headers)
        else:
            if 'GNU.sparse.size' in pax_headers:
                self._proc_gnusparse_00(next, pax_headers, buf)
            else:
                if pax_headers.get('GNU.sparse.major') == '1':
                    if pax_headers.get('GNU.sparse.minor') == '0':
                        self._proc_gnusparse_10(next, pax_headers, tarfile)
                if self.type in (XHDTYPE, SOLARIS_XHDTYPE):
                    next._apply_pax_info(pax_headers, tarfile.encoding, tarfile.errors)
                    next.offset = self.offset
                    if 'size' in pax_headers:
                        offset = next.offset_data
                        if next.isreg() or next.type not in SUPPORTED_TYPES:
                            offset += next._block(next.size)
                        tarfile.offset = offset
                return next

    def _proc_gnusparse_00(self, next, pax_headers, buf):
        offsets = []
        for match in re.finditer(b'\\d+ GNU.sparse.offset=(\\d+)\\n', buf):
            offsets.append(int(match.group(1)))

        numbytes = []
        for match in re.finditer(b'\\d+ GNU.sparse.numbytes=(\\d+)\\n', buf):
            numbytes.append(int(match.group(1)))

        next.sparse = list(zip(offsets, numbytes))

    def _proc_gnusparse_01(self, next, pax_headers):
        sparse = [int(x) for x in pax_headers['GNU.sparse.map'].split(',')]
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    def _proc_gnusparse_10(self, next, pax_headers, tarfile):
        fields = None
        sparse = []
        buf = tarfile.fileobj.read(BLOCKSIZE)
        fields, buf = buf.split(b'\n', 1)
        fields = int(fields)
        while len(sparse) < fields * 2:
            if b'\n' not in buf:
                buf += tarfile.fileobj.read(BLOCKSIZE)
            number, buf = buf.split(b'\n', 1)
            sparse.append(int(number))

        next.offset_data = tarfile.fileobj.tell()
        next.sparse = list(zip(sparse[::2], sparse[1::2]))

    def _apply_pax_info(self, pax_headers, encoding, errors):
        for keyword, value in pax_headers.items():
            if keyword == 'GNU.sparse.name':
                setattr(self, 'path', value)
            elif keyword == 'GNU.sparse.size':
                setattr(self, 'size', int(value))
            else:
                if keyword == 'GNU.sparse.realsize':
                    setattr(self, 'size', int(value))

        self.pax_headers = pax_headers.copy()

    def _decode_pax_field(self, value, encoding, fallback_encoding, fallback_errors):
        try:
            return value.decode(encoding, 'strict')
        except UnicodeDecodeError:
            return value.decode(fallback_encoding, fallback_errors)

    def _block(self, count):
        blocks, remainder = divmod(count, BLOCKSIZE)
        if remainder:
            blocks += 1
        return blocks * BLOCKSIZE

    def isreg(self):
        return self.type in REGULAR_TYPES

    def isfile(self):
        return self.isreg()

    def isdir(self):
        return self.type == DIRTYPE

    def issym(self):
        return self.type == SYMTYPE

    def islnk(self):
        return self.type == LNKTYPE

    def ischr(self):
        return self.type == CHRTYPE

    def isblk(self):
        return self.type == BLKTYPE

    def isfifo(self):
        return self.type == FIFOTYPE

    def issparse(self):
        return self.sparse is not None

    def isdev(self):
        return self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)


class TarFile(object):
    debug = 0
    dereference = False
    ignore_zeros = False
    errorlevel = 1
    format = DEFAULT_FORMAT
    encoding = ENCODING
    errors = None
    tarinfo = TarInfo
    fileobject = ExFileObject

    def __init__(self, name=None, mode='r', fileobj=None, format=None, tarinfo=None, dereference=None, ignore_zeros=None, encoding=None, errors='surrogateescape', pax_headers=None, debug=None, errorlevel=None, copybufsize=None):
        modes = {
         'r': "'rb'", 'a': "'r+b'", 'w': "'wb'", 'x': "'xb'"}
        if mode not in modes:
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        self.mode = mode
        self._mode = modes[mode]
        if not fileobj:
            if self.mode == 'a':
                if not os.path.exists(name):
                    self.mode = 'w'
                    self._mode = 'wb'
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            if name is None:
                if hasattr(fileobj, 'name'):
                    if isinstance(fileobj.name, (str, bytes)):
                        name = fileobj.name
            if hasattr(fileobj, 'mode'):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) if name else None
        self.fileobj = fileobj
        if format is not None:
            self.format = format
        if tarinfo is not None:
            self.tarinfo = tarinfo
        if dereference is not None:
            self.dereference = dereference
        if ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        if encoding is not None:
            self.encoding = encoding
        self.errors = errors
        if pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}
        if debug is not None:
            self.debug = debug
        if errorlevel is not None:
            self.errorlevel = errorlevel
        self.copybufsize = copybufsize
        self.closed = False
        self.members = []
        self._loaded = False
        self.offset = self.fileobj.tell()
        self.inodes = {}
        try:
            if self.mode == 'r':
                self.firstmember = None
                self.firstmember = self.next()
            else:
                if self.mode == 'a':
                    while True:
                        self.fileobj.seek(self.offset)
                        try:
                            tarinfo = self.tarinfo.fromtarfile(self)
                            self.members.append(tarinfo)
                        except EOFHeaderError:
                            self.fileobj.seek(self.offset)
                            break
                        except HeaderError as e:
                            try:
                                raise ReadError(str(e))
                            finally:
                                e = None
                                del e

                if self.mode in ('a', 'w', 'x'):
                    self._loaded = True
                    if self.pax_headers:
                        buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                        self.fileobj.write(buf)
                        self.offset += len(buf)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

    @classmethod
    def open(cls, name=None, mode='r', fileobj=None, bufsize=RECORDSIZE, **kwargs):
        if not name:
            if not fileobj:
                raise ValueError('nothing to open')
        if mode in ('r', 'r:*'):

            def not_compressed(comptype):
                return cls.OPEN_METH[comptype] == 'taropen'

            for comptype in sorted((cls.OPEN_METH), key=not_compressed):
                func = getattr(cls, cls.OPEN_METH[comptype])
                if fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    return func(name, 'r', fileobj, **kwargs)
                except (ReadError, CompressionError):
                    if fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue

            raise ReadError('file could not be opened successfully')
        else:
            if ':' in mode:
                filemode, comptype = mode.split(':', 1)
                filemode = filemode or 'r'
                comptype = comptype or 'tar'
                if comptype in cls.OPEN_METH:
                    func = getattr(cls, cls.OPEN_METH[comptype])
                else:
                    raise CompressionError('unknown compression type %r' % comptype)
                return func(name, filemode, fileobj, **kwargs)
            if '|' in mode:
                filemode, comptype = mode.split('|', 1)
                filemode = filemode or 'r'
                comptype = comptype or 'tar'
                if filemode not in ('r', 'w'):
                    raise ValueError("mode must be 'r' or 'w'")
                stream = _Stream(name, filemode, comptype, fileobj, bufsize)
                try:
                    t = cls(name, filemode, stream, **kwargs)
                except:
                    stream.close()
                    raise

                t._extfileobj = False
                return t
            if mode in ('a', 'w', 'x'):
                return (cls.taropen)(name, mode, fileobj, **kwargs)
            raise ValueError('undiscernible mode')

    @classmethod
    def taropen(cls, name, mode='r', fileobj=None, **kwargs):
        if mode not in ('r', 'a', 'w', 'x'):
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        return cls(name, mode, fileobj, **kwargs)

    @classmethod
    def gzopen(cls, name, mode='r', fileobj=None, compresslevel=9, **kwargs):
        if mode not in ('r', 'w', 'x'):
            raise ValueError("mode must be 'r', 'w' or 'x'")
        try:
            import gzip
            gzip.GzipFile
        except (ImportError, AttributeError):
            raise CompressionError('gzip module is not available')

        try:
            fileobj = gzip.GzipFile(name, mode + 'b', compresslevel, fileobj)
        except OSError:
            if fileobj is not None:
                if mode == 'r':
                    raise ReadError('not a gzip file')
            raise

        try:
            t = (cls.taropen)(name, mode, fileobj, **kwargs)
        except OSError:
            fileobj.close()
            if mode == 'r':
                raise ReadError('not a gzip file')
            raise
        except:
            fileobj.close()
            raise

        t._extfileobj = False
        return t

    @classmethod
    def bz2open(cls, name, mode='r', fileobj=None, compresslevel=9, **kwargs):
        if mode not in ('r', 'w', 'x'):
            raise ValueError("mode must be 'r', 'w' or 'x'")
        try:
            import bz2
        except ImportError:
            raise CompressionError('bz2 module is not available')

        fileobj = bz2.BZ2File((fileobj or name), mode, compresslevel=compresslevel)
        try:
            t = (cls.taropen)(name, mode, fileobj, **kwargs)
        except (OSError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise ReadError('not a bzip2 file')
            raise
        except:
            fileobj.close()
            raise

        t._extfileobj = False
        return t

    @classmethod
    def xzopen(cls, name, mode='r', fileobj=None, preset=None, **kwargs):
        if mode not in ('r', 'w', 'x'):
            raise ValueError("mode must be 'r', 'w' or 'x'")
        try:
            import lzma
        except ImportError:
            raise CompressionError('lzma module is not available')

        fileobj = lzma.LZMAFile((fileobj or name), mode, preset=preset)
        try:
            t = (cls.taropen)(name, mode, fileobj, **kwargs)
        except (lzma.LZMAError, EOFError):
            fileobj.close()
            if mode == 'r':
                raise ReadError('not an lzma file')
            raise
        except:
            fileobj.close()
            raise

        t._extfileobj = False
        return t

    OPEN_METH = {
     'tar': "'taropen'", 
     'gz': "'gzopen'", 
     'bz2': "'bz2open'", 
     'xz': "'xzopen'"}

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            if self.mode in ('a', 'w', 'x'):
                self.fileobj.write(NUL * (BLOCKSIZE * 2))
                self.offset += BLOCKSIZE * 2
                blocks, remainder = divmod(self.offset, RECORDSIZE)
                if remainder > 0:
                    self.fileobj.write(NUL * (RECORDSIZE - remainder))
        finally:
            if not self._extfileobj:
                self.fileobj.close()

    def getmember(self, name):
        tarinfo = self._getmember(name)
        if tarinfo is None:
            raise KeyError('filename %r not found' % name)
        return tarinfo

    def getmembers(self):
        self._check()
        if not self._loaded:
            self._load()
        return self.members

    def getnames(self):
        return [tarinfo.name for tarinfo in self.getmembers()]

    def gettarinfo(self, name=None, arcname=None, fileobj=None):
        self._check('awx')
        if fileobj is not None:
            name = fileobj.name
        else:
            if arcname is None:
                arcname = name
            else:
                drv, arcname = os.path.splitdrive(arcname)
                arcname = arcname.replace(os.sep, '/')
                arcname = arcname.lstrip('/')
                tarinfo = self.tarinfo()
                tarinfo.tarfile = self
                if fileobj is None:
                    if hasattr(os, 'lstat'):
                        statres = self.dereference or os.lstat(name)
                    else:
                        statres = os.stat(name)
                else:
                    statres = os.fstat(fileobj.fileno())
            linkname = ''
            stmd = statres.st_mode
            if stat.S_ISREG(stmd):
                inode = (
                 statres.st_ino, statres.st_dev)
                if not self.dereference:
                    if statres.st_nlink > 1 and inode in self.inodes and arcname != self.inodes[inode]:
                        type = LNKTYPE
                        linkname = self.inodes[inode]
                    else:
                        type = REGTYPE
                        if inode[0]:
                            self.inodes[inode] = arcname
                else:
                    if stat.S_ISDIR(stmd):
                        type = DIRTYPE
                    else:
                        if stat.S_ISFIFO(stmd):
                            type = FIFOTYPE
                        else:
                            if stat.S_ISLNK(stmd):
                                type = SYMTYPE
                                linkname = os.readlink(name)
                            else:
                                if stat.S_ISCHR(stmd):
                                    type = CHRTYPE
                                else:
                                    if stat.S_ISBLK(stmd):
                                        type = BLKTYPE
                                    else:
                                        return
                tarinfo.name = arcname
                tarinfo.mode = stmd
                tarinfo.uid = statres.st_uid
                tarinfo.gid = statres.st_gid
                if type == REGTYPE:
                    tarinfo.size = statres.st_size
            else:
                tarinfo.size = 0
        tarinfo.mtime = statres.st_mtime
        tarinfo.type = type
        tarinfo.linkname = linkname
        if pwd:
            try:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            except KeyError:
                pass

        if grp:
            try:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            except KeyError:
                pass

        if type in (CHRTYPE, BLKTYPE):
            if hasattr(os, 'major'):
                if hasattr(os, 'minor'):
                    tarinfo.devmajor = os.major(statres.st_rdev)
                    tarinfo.devminor = os.minor(statres.st_rdev)
        return tarinfo

    def list(self, verbose=True, *, members=None):
        self._check()
        if members is None:
            members = self
        for tarinfo in members:
            if verbose:
                _safe_print(stat.filemode(tarinfo.mode))
                _safe_print('%s/%s' % (tarinfo.uname or tarinfo.uid,
                 tarinfo.gname or tarinfo.gid))
                if tarinfo.ischr() or tarinfo.isblk():
                    _safe_print('%10s' % ('%d,%d' % (tarinfo.devmajor, tarinfo.devminor)))
                else:
                    _safe_print('%10d' % tarinfo.size)
                _safe_print('%d-%02d-%02d %02d:%02d:%02d' % time.localtime(tarinfo.mtime)[:6])
            _safe_print(tarinfo.name + ('/' if tarinfo.isdir() else ''))
            if verbose:
                if tarinfo.issym():
                    _safe_print('-> ' + tarinfo.linkname)
                if tarinfo.islnk():
                    _safe_print('link to ' + tarinfo.linkname)
            print()

    def add(self, name, arcname=None, recursive=True, *, filter=None):
        self._check('awx')
        if arcname is None:
            arcname = name
        elif self.name is not None:
            if os.path.abspath(name) == self.name:
                self._dbg(2, 'tarfile: Skipped %r' % name)
                return
            else:
                self._dbg(1, name)
                tarinfo = self.gettarinfo(name, arcname)
                if tarinfo is None:
                    self._dbg(1, 'tarfile: Unsupported type %r' % name)
                    return
                if filter is not None:
                    tarinfo = filter(tarinfo)
                    if tarinfo is None:
                        self._dbg(2, 'tarfile: Excluded %r' % name)
                        return
            if tarinfo.isreg():
                with bltn_open(name, 'rb') as (f):
                    self.addfile(tarinfo, f)
        elif tarinfo.isdir():
            self.addfile(tarinfo)
            if recursive:
                for f in sorted(os.listdir(name)):
                    self.add((os.path.join(name, f)), (os.path.join(arcname, f)), recursive,
                      filter=filter)

        else:
            self.addfile(tarinfo)

    def addfile(self, tarinfo, fileobj=None):
        self._check('awx')
        tarinfo = copy.copy(tarinfo)
        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)
        bufsize = self.copybufsize
        if fileobj is not None:
            copyfileobj(fileobj, (self.fileobj), (tarinfo.size), bufsize=bufsize)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            if remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE
        self.members.append(tarinfo)

    def extractall(self, path='.', members=None, *, numeric_owner=False):
        directories = []
        if members is None:
            members = self
        for tarinfo in members:
            if tarinfo.isdir():
                directories.append(tarinfo)
                tarinfo = copy.copy(tarinfo)
                tarinfo.mode = 448
            self.extract(tarinfo, path, set_attrs=(not tarinfo.isdir()), numeric_owner=numeric_owner)

        directories.sort(key=(lambda a: a.name))
        directories.reverse()
        for tarinfo in directories:
            dirpath = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, dirpath, numeric_owner=numeric_owner)
                self.utime(tarinfo, dirpath)
                self.chmod(tarinfo, dirpath)
            except ExtractError as e:
                try:
                    if self.errorlevel > 1:
                        raise
                    else:
                        self._dbg(1, 'tarfile: %s' % e)
                finally:
                    e = None
                    del e

    def extract(self, member, path='', set_attrs=True, *, numeric_owner=False):
        self._check('r')
        if isinstance(member, str):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member
        if tarinfo.islnk():
            tarinfo._link_target = os.path.join(path, tarinfo.linkname)
        try:
            self._extract_member(tarinfo, (os.path.join(path, tarinfo.name)), set_attrs=set_attrs,
              numeric_owner=numeric_owner)
        except OSError as e:
            try:
                if self.errorlevel > 0:
                    raise
                else:
                    if e.filename is None:
                        self._dbg(1, 'tarfile: %s' % e.strerror)
                    else:
                        self._dbg(1, 'tarfile: %s %r' % (e.strerror, e.filename))
            finally:
                e = None
                del e

        except ExtractError as e:
            try:
                if self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, 'tarfile: %s' % e)
            finally:
                e = None
                del e

    def extractfile(self, member):
        self._check('r')
        if isinstance(member, str):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member
        if not tarinfo.isreg():
            if tarinfo.type not in SUPPORTED_TYPES:
                return self.fileobject(self, tarinfo)
            if tarinfo.islnk() or tarinfo.issym():
                if isinstance(self.fileobj, _Stream):
                    raise StreamError('cannot extract (sym)link as file object')
                else:
                    return self.extractfile(self._find_link_target(tarinfo))
        else:
            return

    def _extract_member(self, tarinfo, targetpath, set_attrs=True, numeric_owner=False):
        targetpath = targetpath.rstrip('/')
        targetpath = targetpath.replace('/', os.sep)
        upperdirs = os.path.dirname(targetpath)
        if upperdirs:
            if not os.path.exists(upperdirs):
                os.makedirs(upperdirs)
        elif tarinfo.islnk() or tarinfo.issym():
            self._dbg(1, '%s -> %s' % (tarinfo.name, tarinfo.linkname))
        else:
            self._dbg(1, tarinfo.name)
        if tarinfo.isreg():
            self.makefile(tarinfo, targetpath)
        else:
            if tarinfo.isdir():
                self.makedir(tarinfo, targetpath)
            else:
                if tarinfo.isfifo():
                    self.makefifo(tarinfo, targetpath)
                else:
                    if tarinfo.ischr() or tarinfo.isblk():
                        self.makedev(tarinfo, targetpath)
                    else:
                        if tarinfo.islnk() or tarinfo.issym():
                            self.makelink(tarinfo, targetpath)
                        else:
                            if tarinfo.type not in SUPPORTED_TYPES:
                                self.makeunknown(tarinfo, targetpath)
                            else:
                                self.makefile(tarinfo, targetpath)
        if set_attrs:
            self.chown(tarinfo, targetpath, numeric_owner)
            if not tarinfo.issym():
                self.chmod(tarinfo, targetpath)
                self.utime(tarinfo, targetpath)

    def makedir(self, tarinfo, targetpath):
        try:
            os.mkdir(targetpath, 448)
        except FileExistsError:
            pass

    def makefile(self, tarinfo, targetpath):
        source = self.fileobj
        source.seek(tarinfo.offset_data)
        bufsize = self.copybufsize
        with bltn_open(targetpath, 'wb') as (target):
            if tarinfo.sparse is not None:
                for offset, size in tarinfo.sparse:
                    target.seek(offset)
                    copyfileobj(source, target, size, ReadError, bufsize)

                target.seek(tarinfo.size)
                target.truncate()
            else:
                copyfileobj(source, target, tarinfo.size, ReadError, bufsize)

    def makeunknown(self, tarinfo, targetpath):
        self.makefile(tarinfo, targetpath)
        self._dbg(1, 'tarfile: Unknown file type %r, extracted as regular file.' % tarinfo.type)

    def makefifo(self, tarinfo, targetpath):
        if hasattr(os, 'mkfifo'):
            os.mkfifo(targetpath)
        else:
            raise ExtractError('fifo not supported by system')

    def makedev(self, tarinfo, targetpath):
        if hasattr(os, 'mknod'):
            raise hasattr(os, 'makedev') or ExtractError('special devices not supported by system')
        else:
            mode = tarinfo.mode
            if tarinfo.isblk():
                mode |= stat.S_IFBLK
            else:
                mode |= stat.S_IFCHR
        os.mknod(targetpath, mode, os.makedev(tarinfo.devmajor, tarinfo.devminor))

    def makelink(self, tarinfo, targetpath):
        try:
            if tarinfo.issym():
                os.symlink(tarinfo.linkname, targetpath)
            else:
                if os.path.exists(tarinfo._link_target):
                    os.link(tarinfo._link_target, targetpath)
                else:
                    self._extract_member(self._find_link_target(tarinfo), targetpath)
        except symlink_exception:
            try:
                self._extract_member(self._find_link_target(tarinfo), targetpath)
            except KeyError:
                raise ExtractError('unable to resolve link inside archive')

    def chown(self, tarinfo, targetpath, numeric_owner):
        if hasattr(os, 'geteuid'):
            if os.geteuid() == 0:
                g = tarinfo.gid
                u = tarinfo.uid
                if not numeric_owner:
                    try:
                        if grp:
                            g = grp.getgrnam(tarinfo.gname)[2]
                    except KeyError:
                        pass

                    try:
                        if pwd:
                            u = pwd.getpwnam(tarinfo.uname)[2]
                    except KeyError:
                        pass

                try:
                    if tarinfo.issym() and hasattr(os, 'lchown'):
                        os.lchown(targetpath, u, g)
                    else:
                        os.chown(targetpath, u, g)
                except OSError:
                    raise ExtractError('could not change owner')

    def chmod(self, tarinfo, targetpath):
        if hasattr(os, 'chmod'):
            try:
                os.chmod(targetpath, tarinfo.mode)
            except OSError:
                raise ExtractError('could not change mode')

    def utime(self, tarinfo, targetpath):
        if not hasattr(os, 'utime'):
            return
        try:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        except OSError:
            raise ExtractError('could not change modification time')

    def next(self):
        self._check('ra')
        if self.firstmember is not None:
            m = self.firstmember
            self.firstmember = None
            return m
        if self.offset != self.fileobj.tell():
            self.fileobj.seek(self.offset - 1)
            if not self.fileobj.read(1):
                raise ReadError('unexpected end of data')
        else:
            tarinfo = None
            while True:
                try:
                    tarinfo = self.tarinfo.fromtarfile(self)
                except EOFHeaderError as e:
                    try:
                        if self.ignore_zeros:
                            self._dbg(2, '0x%X: %s' % (self.offset, e))
                            self.offset += BLOCKSIZE
                            continue
                    finally:
                        e = None
                        del e

                except InvalidHeaderError as e:
                    try:
                        if self.ignore_zeros:
                            self._dbg(2, '0x%X: %s' % (self.offset, e))
                            self.offset += BLOCKSIZE
                            continue
                        else:
                            if self.offset == 0:
                                raise ReadError(str(e))
                    finally:
                        e = None
                        del e

                except EmptyHeaderError:
                    if self.offset == 0:
                        raise ReadError('empty file')
                except TruncatedHeaderError as e:
                    try:
                        if self.offset == 0:
                            raise ReadError(str(e))
                    finally:
                        e = None
                        del e

                except SubsequentHeaderError as e:
                    try:
                        raise ReadError(str(e))
                    finally:
                        e = None
                        del e

                break

            if tarinfo is not None:
                self.members.append(tarinfo)
            else:
                self._loaded = True
        return tarinfo

    def _getmember(self, name, tarinfo=None, normalize=False):
        members = self.getmembers()
        if tarinfo is not None:
            members = members[:members.index(tarinfo)]
        if normalize:
            name = os.path.normpath(name)
        for member in reversed(members):
            if normalize:
                member_name = os.path.normpath(member.name)
            else:
                member_name = member.name
            if name == member_name:
                return member

    def _load(self):
        while 1:
            tarinfo = self.next()
            if tarinfo is None:
                break

        self._loaded = True

    def _check(self, mode=None):
        if self.closed:
            raise OSError('%s is closed' % self.__class__.__name__)
        if mode is not None:
            if self.mode not in mode:
                raise OSError('bad operation for mode %r' % self.mode)

    def _find_link_target(self, tarinfo):
        if tarinfo.issym():
            linkname = '/'.join(filter(None, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = None
        else:
            linkname = tarinfo.linkname
            limit = tarinfo
        member = self._getmember(linkname, tarinfo=limit, normalize=True)
        if member is None:
            raise KeyError('linkname %r not found' % linkname)
        return member

    def __iter__(self):
        if self._loaded:
            yield from self.members
            return
        index = 0
        if self.firstmember is not None:
            tarinfo = self.next()
            index += 1
            yield tarinfo
        while True:
            if index < len(self.members):
                tarinfo = self.members[index]
            else:
                if not self._loaded:
                    tarinfo = self.next()
                    self._loaded = tarinfo or True
                    return
                else:
                    return
            index += 1
            yield tarinfo

    def _dbg(self, level, msg):
        if level <= self.debug:
            print(msg, file=(sys.stderr))

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True


def is_tarfile(name):
    try:
        t = open(name)
        t.close()
        return True
    except TarError:
        return False


open = TarFile.open

def main--- This code section failed: ---

 L.2450         0  LOAD_CONST               0
                2  LOAD_CONST               None
                4  IMPORT_NAME              argparse
                6  STORE_FAST               'argparse'

 L.2452         8  LOAD_STR                 'A simple command-line interface for tarfile module.'
               10  STORE_FAST               'description'

 L.2453        12  LOAD_FAST                'argparse'
               14  LOAD_ATTR                ArgumentParser
               16  LOAD_FAST                'description'
               18  LOAD_CONST               ('description',)
               20  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               22  STORE_FAST               'parser'

 L.2454        24  LOAD_FAST                'parser'
               26  LOAD_ATTR                add_argument
               28  LOAD_STR                 '-v'
               30  LOAD_STR                 '--verbose'
               32  LOAD_STR                 'store_true'
               34  LOAD_CONST               False

 L.2455        36  LOAD_STR                 'Verbose output'
               38  LOAD_CONST               ('action', 'default', 'help')
               40  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
               42  POP_TOP          

 L.2456        44  LOAD_FAST                'parser'
               46  LOAD_ATTR                add_mutually_exclusive_group
               48  LOAD_CONST               True
               50  LOAD_CONST               ('required',)
               52  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               54  STORE_FAST               'group'

 L.2457        56  LOAD_FAST                'group'
               58  LOAD_ATTR                add_argument
               60  LOAD_STR                 '-l'
               62  LOAD_STR                 '--list'
               64  LOAD_STR                 '<tarfile>'

 L.2458        66  LOAD_STR                 'Show listing of a tarfile'
               68  LOAD_CONST               ('metavar', 'help')
               70  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
               72  POP_TOP          

 L.2459        74  LOAD_FAST                'group'
               76  LOAD_ATTR                add_argument
               78  LOAD_STR                 '-e'
               80  LOAD_STR                 '--extract'
               82  LOAD_STR                 '+'

 L.2460        84  LOAD_CONST               ('<tarfile>', '<output_dir>')

 L.2461        86  LOAD_STR                 'Extract tarfile into target dir'
               88  LOAD_CONST               ('nargs', 'metavar', 'help')
               90  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
               92  POP_TOP          

 L.2462        94  LOAD_FAST                'group'
               96  LOAD_ATTR                add_argument
               98  LOAD_STR                 '-c'
              100  LOAD_STR                 '--create'
              102  LOAD_STR                 '+'

 L.2463       104  LOAD_CONST               ('<name>', '<file>')

 L.2464       106  LOAD_STR                 'Create tarfile from sources'
              108  LOAD_CONST               ('nargs', 'metavar', 'help')
              110  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              112  POP_TOP          

 L.2465       114  LOAD_FAST                'group'
              116  LOAD_ATTR                add_argument
              118  LOAD_STR                 '-t'
              120  LOAD_STR                 '--test'
              122  LOAD_STR                 '<tarfile>'

 L.2466       124  LOAD_STR                 'Test if a tarfile is valid'
              126  LOAD_CONST               ('metavar', 'help')
              128  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              130  POP_TOP          

 L.2467       132  LOAD_FAST                'parser'
              134  LOAD_METHOD              parse_args
              136  CALL_METHOD_0         0  '0 positional arguments'
              138  STORE_FAST               'args'

 L.2469       140  LOAD_FAST                'args'
              142  LOAD_ATTR                test
              144  LOAD_CONST               None
              146  COMPARE_OP               is-not
          148_150  POP_JUMP_IF_FALSE   258  'to 258'

 L.2470       152  LOAD_FAST                'args'
              154  LOAD_ATTR                test
              156  STORE_FAST               'src'

 L.2471       158  LOAD_GLOBAL              is_tarfile
              160  LOAD_FAST                'src'
              162  CALL_FUNCTION_1       1  '1 positional argument'
              164  POP_JUMP_IF_FALSE   236  'to 236'

 L.2472       166  LOAD_GLOBAL              open
              168  LOAD_FAST                'src'
              170  LOAD_STR                 'r'
              172  CALL_FUNCTION_2       2  '2 positional arguments'
              174  SETUP_WITH          208  'to 208'
              176  STORE_FAST               'tar'

 L.2473       178  LOAD_FAST                'tar'
              180  LOAD_METHOD              getmembers
              182  CALL_METHOD_0         0  '0 positional arguments'
              184  POP_TOP          

 L.2474       186  LOAD_GLOBAL              print
              188  LOAD_FAST                'tar'
              190  LOAD_METHOD              getmembers
              192  CALL_METHOD_0         0  '0 positional arguments'
              194  LOAD_GLOBAL              sys
              196  LOAD_ATTR                stderr
              198  LOAD_CONST               ('file',)
              200  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              202  POP_TOP          
              204  POP_BLOCK        
              206  LOAD_CONST               None
            208_0  COME_FROM_WITH      174  '174'
              208  WITH_CLEANUP_START
              210  WITH_CLEANUP_FINISH
              212  END_FINALLY      

 L.2475       214  LOAD_FAST                'args'
              216  LOAD_ATTR                verbose
              218  POP_JUMP_IF_FALSE   254  'to 254'

 L.2476       220  LOAD_GLOBAL              print
              222  LOAD_STR                 '{!r} is a tar archive.'
              224  LOAD_METHOD              format
              226  LOAD_FAST                'src'
              228  CALL_METHOD_1         1  '1 positional argument'
              230  CALL_FUNCTION_1       1  '1 positional argument'
              232  POP_TOP          
              234  JUMP_FORWARD        722  'to 722'
            236_0  COME_FROM           164  '164'

 L.2478       236  LOAD_FAST                'parser'
              238  LOAD_METHOD              exit
              240  LOAD_CONST               1
              242  LOAD_STR                 '{!r} is not a tar archive.\n'
              244  LOAD_METHOD              format
              246  LOAD_FAST                'src'
              248  CALL_METHOD_1         1  '1 positional argument'
              250  CALL_METHOD_2         2  '2 positional arguments'
              252  POP_TOP          
            254_0  COME_FROM           218  '218'
          254_256  JUMP_FORWARD        722  'to 722'
            258_0  COME_FROM           148  '148'

 L.2480       258  LOAD_FAST                'args'
              260  LOAD_ATTR                list
              262  LOAD_CONST               None
              264  COMPARE_OP               is-not
          266_268  POP_JUMP_IF_FALSE   348  'to 348'

 L.2481       270  LOAD_FAST                'args'
              272  LOAD_ATTR                list
              274  STORE_FAST               'src'

 L.2482       276  LOAD_GLOBAL              is_tarfile
              278  LOAD_FAST                'src'
              280  CALL_FUNCTION_1       1  '1 positional argument'
          282_284  POP_JUMP_IF_FALSE   326  'to 326'

 L.2483       286  LOAD_GLOBAL              TarFile
              288  LOAD_METHOD              open
              290  LOAD_FAST                'src'
              292  LOAD_STR                 'r:*'
              294  CALL_METHOD_2         2  '2 positional arguments'
              296  SETUP_WITH          318  'to 318'
              298  STORE_FAST               'tf'

 L.2484       300  LOAD_FAST                'tf'
              302  LOAD_ATTR                list
              304  LOAD_FAST                'args'
              306  LOAD_ATTR                verbose
              308  LOAD_CONST               ('verbose',)
              310  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              312  POP_TOP          
              314  POP_BLOCK        
              316  LOAD_CONST               None
            318_0  COME_FROM_WITH      296  '296'
              318  WITH_CLEANUP_START
              320  WITH_CLEANUP_FINISH
              322  END_FINALLY      
              324  JUMP_FORWARD        722  'to 722'
            326_0  COME_FROM           282  '282'

 L.2486       326  LOAD_FAST                'parser'
              328  LOAD_METHOD              exit
              330  LOAD_CONST               1
              332  LOAD_STR                 '{!r} is not a tar archive.\n'
              334  LOAD_METHOD              format
              336  LOAD_FAST                'src'
              338  CALL_METHOD_1         1  '1 positional argument'
              340  CALL_METHOD_2         2  '2 positional arguments'
              342  POP_TOP          
          344_346  JUMP_FORWARD        722  'to 722'
            348_0  COME_FROM           266  '266'

 L.2488       348  LOAD_FAST                'args'
              350  LOAD_ATTR                extract
              352  LOAD_CONST               None
              354  COMPARE_OP               is-not
          356_358  POP_JUMP_IF_FALSE   556  'to 556'

 L.2489       360  LOAD_GLOBAL              len
              362  LOAD_FAST                'args'
              364  LOAD_ATTR                extract
              366  CALL_FUNCTION_1       1  '1 positional argument'
              368  LOAD_CONST               1
              370  COMPARE_OP               ==
          372_374  POP_JUMP_IF_FALSE   394  'to 394'

 L.2490       376  LOAD_FAST                'args'
              378  LOAD_ATTR                extract
              380  LOAD_CONST               0
              382  BINARY_SUBSCR    
              384  STORE_FAST               'src'

 L.2491       386  LOAD_GLOBAL              os
              388  LOAD_ATTR                curdir
              390  STORE_FAST               'curdir'
              392  JUMP_FORWARD        438  'to 438'
            394_0  COME_FROM           372  '372'

 L.2492       394  LOAD_GLOBAL              len
              396  LOAD_FAST                'args'
              398  LOAD_ATTR                extract
              400  CALL_FUNCTION_1       1  '1 positional argument'
              402  LOAD_CONST               2
              404  COMPARE_OP               ==
          406_408  POP_JUMP_IF_FALSE   422  'to 422'

 L.2493       410  LOAD_FAST                'args'
              412  LOAD_ATTR                extract
              414  UNPACK_SEQUENCE_2     2 
              416  STORE_FAST               'src'
              418  STORE_FAST               'curdir'
              420  JUMP_FORWARD        438  'to 438'
            422_0  COME_FROM           406  '406'

 L.2495       422  LOAD_FAST                'parser'
              424  LOAD_METHOD              exit
              426  LOAD_CONST               1
              428  LOAD_FAST                'parser'
              430  LOAD_METHOD              format_help
              432  CALL_METHOD_0         0  '0 positional arguments'
              434  CALL_METHOD_2         2  '2 positional arguments'
              436  POP_TOP          
            438_0  COME_FROM           420  '420'
            438_1  COME_FROM           392  '392'

 L.2497       438  LOAD_GLOBAL              is_tarfile
              440  LOAD_FAST                'src'
              442  CALL_FUNCTION_1       1  '1 positional argument'
          444_446  POP_JUMP_IF_FALSE   536  'to 536'

 L.2498       448  LOAD_GLOBAL              TarFile
              450  LOAD_METHOD              open
              452  LOAD_FAST                'src'
              454  LOAD_STR                 'r:*'
              456  CALL_METHOD_2         2  '2 positional arguments'
              458  SETUP_WITH          478  'to 478'
              460  STORE_FAST               'tf'

 L.2499       462  LOAD_FAST                'tf'
              464  LOAD_ATTR                extractall
              466  LOAD_FAST                'curdir'
              468  LOAD_CONST               ('path',)
              470  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
              472  POP_TOP          
              474  POP_BLOCK        
              476  LOAD_CONST               None
            478_0  COME_FROM_WITH      458  '458'
              478  WITH_CLEANUP_START
              480  WITH_CLEANUP_FINISH
              482  END_FINALLY      

 L.2500       484  LOAD_FAST                'args'
              486  LOAD_ATTR                verbose
          488_490  POP_JUMP_IF_FALSE   554  'to 554'

 L.2501       492  LOAD_FAST                'curdir'
              494  LOAD_STR                 '.'
              496  COMPARE_OP               ==
          498_500  POP_JUMP_IF_FALSE   514  'to 514'

 L.2502       502  LOAD_STR                 '{!r} file is extracted.'
              504  LOAD_METHOD              format
              506  LOAD_FAST                'src'
              508  CALL_METHOD_1         1  '1 positional argument'
              510  STORE_FAST               'msg'
              512  JUMP_FORWARD        526  'to 526'
            514_0  COME_FROM           498  '498'

 L.2504       514  LOAD_STR                 '{!r} file is extracted into {!r} directory.'
              516  LOAD_METHOD              format

 L.2505       518  LOAD_FAST                'src'
              520  LOAD_FAST                'curdir'
              522  CALL_METHOD_2         2  '2 positional arguments'
              524  STORE_FAST               'msg'
            526_0  COME_FROM           512  '512'

 L.2506       526  LOAD_GLOBAL              print
              528  LOAD_FAST                'msg'
              530  CALL_FUNCTION_1       1  '1 positional argument'
              532  POP_TOP          
              534  JUMP_FORWARD        554  'to 554'
            536_0  COME_FROM           444  '444'

 L.2508       536  LOAD_FAST                'parser'
              538  LOAD_METHOD              exit
              540  LOAD_CONST               1
              542  LOAD_STR                 '{!r} is not a tar archive.\n'
              544  LOAD_METHOD              format
              546  LOAD_FAST                'src'
              548  CALL_METHOD_1         1  '1 positional argument'
              550  CALL_METHOD_2         2  '2 positional arguments'
              552  POP_TOP          
            554_0  COME_FROM           534  '534'
            554_1  COME_FROM           488  '488'
              554  JUMP_FORWARD        722  'to 722'
            556_0  COME_FROM           356  '356'

 L.2510       556  LOAD_FAST                'args'
              558  LOAD_ATTR                create
              560  LOAD_CONST               None
              562  COMPARE_OP               is-not
          564_566  POP_JUMP_IF_FALSE   722  'to 722'

 L.2511       568  LOAD_FAST                'args'
              570  LOAD_ATTR                create
              572  LOAD_METHOD              pop
              574  LOAD_CONST               0
              576  CALL_METHOD_1         1  '1 positional argument'
              578  STORE_FAST               'tar_name'

 L.2512       580  LOAD_GLOBAL              os
              582  LOAD_ATTR                path
              584  LOAD_METHOD              splitext
              586  LOAD_FAST                'tar_name'
              588  CALL_METHOD_1         1  '1 positional argument'
              590  UNPACK_SEQUENCE_2     2 
              592  STORE_FAST               '_'
              594  STORE_FAST               'ext'
            596_0  COLLECTION_START      2  'CONST_DICT'

 L.2515       596  ADD_VALUE                "'gz'"

 L.2516       598  ADD_VALUE                "'gz'"

 L.2518       600  ADD_VALUE                "'xz'"

 L.2519       602  ADD_VALUE                "'xz'"

 L.2521       604  ADD_VALUE                "'bz2'"

 L.2522       606  ADD_VALUE                "'bz2'"

 L.2523       608  ADD_VALUE                "'bz2'"

 L.2524       610  ADD_VALUE                "'bz2'"
              612  ADD_VALUE                ('.gz', '.tgz', '.xz', '.txz', '.bz2', '.tbz', '.tbz2', '.tb2')
              614  BUILD_CONST_DICT      8  ''
              616  STORE_FAST               'compressions'

 L.2526       618  LOAD_FAST                'ext'
              620  LOAD_FAST                'compressions'
              622  COMPARE_OP               in
          624_626  POP_JUMP_IF_FALSE   640  'to 640'
              628  LOAD_STR                 'w:'
              630  LOAD_FAST                'compressions'
              632  LOAD_FAST                'ext'
              634  BINARY_SUBSCR    
              636  BINARY_ADD       
              638  JUMP_FORWARD        642  'to 642'
            640_0  COME_FROM           624  '624'
              640  LOAD_STR                 'w'
            642_0  COME_FROM           638  '638'
              642  STORE_FAST               'tar_mode'

 L.2527       644  LOAD_FAST                'args'
              646  LOAD_ATTR                create
              648  STORE_FAST               'tar_files'

 L.2529       650  LOAD_GLOBAL              TarFile
              652  LOAD_METHOD              open
              654  LOAD_FAST                'tar_name'
              656  LOAD_FAST                'tar_mode'
              658  CALL_METHOD_2         2  '2 positional arguments'
              660  SETUP_WITH          694  'to 694'
              662  STORE_FAST               'tf'

 L.2530       664  SETUP_LOOP          690  'to 690'
              666  LOAD_FAST                'tar_files'
              668  GET_ITER         
              670  FOR_ITER            688  'to 688'
              672  STORE_FAST               'file_name'

 L.2531       674  LOAD_FAST                'tf'
              676  LOAD_METHOD              add
              678  LOAD_FAST                'file_name'
              680  CALL_METHOD_1         1  '1 positional argument'
              682  POP_TOP          
          684_686  JUMP_BACK           670  'to 670'
              688  POP_BLOCK        
            690_0  COME_FROM_LOOP      664  '664'
              690  POP_BLOCK        
              692  LOAD_CONST               None
            694_0  COME_FROM_WITH      660  '660'
              694  WITH_CLEANUP_START
              696  WITH_CLEANUP_FINISH
              698  END_FINALLY      
            700_0  COME_FROM           324  '324'
            700_1  COME_FROM           234  '234'

 L.2533       700  LOAD_FAST                'args'
              702  LOAD_ATTR                verbose
          704_706  POP_JUMP_IF_FALSE   722  'to 722'

 L.2534       708  LOAD_GLOBAL              print
              710  LOAD_STR                 '{!r} file created.'
              712  LOAD_METHOD              format
              714  LOAD_FAST                'tar_name'
              716  CALL_METHOD_1         1  '1 positional argument'
              718  CALL_FUNCTION_1       1  '1 positional argument'
              720  POP_TOP          
            722_0  COME_FROM           704  '704'
            722_1  COME_FROM           564  '564'
            722_2  COME_FROM           554  '554'
            722_3  COME_FROM           344  '344'
            722_4  COME_FROM           254  '254'

Parse error at or near `COME_FROM' instruction at offset 722_3


if __name__ == '__main__':
    main()