# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\http\client.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 55357 bytes
import email.parser, email.message, http, io, re, socket, collections.abc
from urllib.parse import urlsplit
__all__ = [
 "'HTTPResponse'", "'HTTPConnection'", 
 "'HTTPException'", "'NotConnected'", 
 "'UnknownProtocol'", 
 "'UnknownTransferEncoding'", "'UnimplementedFileMode'", 
 "'IncompleteRead'", 
 "'InvalidURL'", "'ImproperConnectionState'", 
 "'CannotSendRequest'", "'CannotSendHeader'", 
 "'ResponseNotReady'", 
 "'BadStatusLine'", "'LineTooLong'", "'RemoteDisconnected'", 
 "'error'", 
 "'responses'"]
HTTP_PORT = 80
HTTPS_PORT = 443
_UNKNOWN = 'UNKNOWN'
_CS_IDLE = 'Idle'
_CS_REQ_STARTED = 'Request-started'
_CS_REQ_SENT = 'Request-sent'
globals().update(http.HTTPStatus.__members__)
responses = {v: v.phrase for v in http.HTTPStatus.__members__.values()}
MAXAMOUNT = 1048576
_MAXLINE = 65536
_MAXHEADERS = 100
_is_legal_header_name = re.compile(b'[^:\\s][^:\\r\\n]*').fullmatch
_is_illegal_header_value = re.compile(b'\\n(?![ \\t])|\\r(?![ \\t\\n])').search
_METHODS_EXPECTING_BODY = {
 'PATCH', 'POST', 'PUT'}

def _encode(data, name='data'):
    try:
        return data.encode('latin-1')
    except UnicodeEncodeError as err:
        try:
            raise UnicodeEncodeError(err.encoding, err.object, err.start, err.end, "%s (%.20r) is not valid Latin-1. Use %s.encode('utf-8') if you want to send it encoded in UTF-8." % (
             name.title(), data[err.start:err.end], name)) from None
        finally:
            err = None
            del err


class HTTPMessage(email.message.Message):

    def getallmatchingheaders(self, name):
        name = name.lower() + ':'
        n = len(name)
        lst = []
        hit = 0
        for line in self.keys():
            if line[:n].lower() == name:
                hit = 1
            else:
                if not line[:1].isspace():
                    hit = 0
            if hit:
                lst.append(line)

        return lst


def parse_headers(fp, _class=HTTPMessage):
    headers = []
    while 1:
        line = fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise LineTooLong('header line')
        headers.append(line)
        if len(headers) > _MAXHEADERS:
            raise HTTPException('got more than %d headers' % _MAXHEADERS)
        if line in (b'\r\n', b'\n', b''):
            break

    hstring = (b'').join(headers).decode('iso-8859-1')
    return email.parser.Parser(_class=_class).parsestr(hstring)


class HTTPResponse(io.BufferedIOBase):

    def __init__(self, sock, debuglevel=0, method=None, url=None):
        self.fp = sock.makefile('rb')
        self.debuglevel = debuglevel
        self._method = method
        self.headers = self.msg = None
        self.version = _UNKNOWN
        self.status = _UNKNOWN
        self.reason = _UNKNOWN
        self.chunked = _UNKNOWN
        self.chunk_left = _UNKNOWN
        self.length = _UNKNOWN
        self.will_close = _UNKNOWN

    def _read_status(self):
        line = str(self.fp.readline(_MAXLINE + 1), 'iso-8859-1')
        if len(line) > _MAXLINE:
            raise LineTooLong('status line')
        if self.debuglevel > 0:
            print('reply:', repr(line))
        if not line:
            raise RemoteDisconnected('Remote end closed connection without response')
        try:
            version, status, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status = line.split(None, 1)
                reason = ''
            except ValueError:
                version = ''

        if not version.startswith('HTTP/'):
            self._close_conn()
            raise BadStatusLine(line)
        try:
            status = int(status)
            if status < 100 or status > 999:
                raise BadStatusLine(line)
        except ValueError:
            raise BadStatusLine(line)

        return (
         version, status, reason)

    def begin--- This code section failed: ---

 L. 290         0  LOAD_FAST                'self'
                2  LOAD_ATTR                headers
                4  LOAD_CONST               None
                6  COMPARE_OP               is-not
                8  POP_JUMP_IF_FALSE    14  'to 14'

 L. 292        10  LOAD_CONST               None
               12  RETURN_VALUE     
             14_0  COME_FROM             8  '8'

 L. 295        14  SETUP_LOOP          120  'to 120'

 L. 296        16  LOAD_FAST                'self'
               18  LOAD_METHOD              _read_status
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  UNPACK_SEQUENCE_3     3 
               24  STORE_FAST               'version'
               26  STORE_FAST               'status'
               28  STORE_FAST               'reason'

 L. 297        30  LOAD_FAST                'status'
               32  LOAD_GLOBAL              CONTINUE
               34  COMPARE_OP               !=
               36  POP_JUMP_IF_FALSE    40  'to 40'

 L. 298        38  BREAK_LOOP       
             40_0  COME_FROM            36  '36'

 L. 300        40  SETUP_LOOP          116  'to 116'
             42_0  COME_FROM           100  '100'

 L. 301        42  LOAD_FAST                'self'
               44  LOAD_ATTR                fp
               46  LOAD_METHOD              readline
               48  LOAD_GLOBAL              _MAXLINE
               50  LOAD_CONST               1
               52  BINARY_ADD       
               54  CALL_METHOD_1         1  '1 positional argument'
               56  STORE_FAST               'skip'

 L. 302        58  LOAD_GLOBAL              len
               60  LOAD_FAST                'skip'
               62  CALL_FUNCTION_1       1  '1 positional argument'
               64  LOAD_GLOBAL              _MAXLINE
               66  COMPARE_OP               >
               68  POP_JUMP_IF_FALSE    78  'to 78'

 L. 303        70  LOAD_GLOBAL              LineTooLong
               72  LOAD_STR                 'header line'
               74  CALL_FUNCTION_1       1  '1 positional argument'
               76  RAISE_VARARGS_1       1  'exception instance'
             78_0  COME_FROM            68  '68'

 L. 304        78  LOAD_FAST                'skip'
               80  LOAD_METHOD              strip
               82  CALL_METHOD_0         0  '0 positional arguments'
               84  STORE_FAST               'skip'

 L. 305        86  LOAD_FAST                'skip'
               88  POP_JUMP_IF_TRUE     92  'to 92'

 L. 306        90  BREAK_LOOP       
             92_0  COME_FROM            88  '88'

 L. 307        92  LOAD_FAST                'self'
               94  LOAD_ATTR                debuglevel
               96  LOAD_CONST               0
               98  COMPARE_OP               >
              100  POP_JUMP_IF_FALSE    42  'to 42'

 L. 308       102  LOAD_GLOBAL              print
              104  LOAD_STR                 'header:'
              106  LOAD_FAST                'skip'
              108  CALL_FUNCTION_2       2  '2 positional arguments'
              110  POP_TOP          
              112  JUMP_BACK            42  'to 42'
              114  POP_BLOCK        
            116_0  COME_FROM_LOOP       40  '40'
              116  JUMP_BACK            16  'to 16'
              118  POP_BLOCK        
            120_0  COME_FROM_LOOP       14  '14'

 L. 310       120  LOAD_FAST                'status'
              122  DUP_TOP          
              124  LOAD_FAST                'self'
              126  STORE_ATTR               code
              128  LOAD_FAST                'self'
              130  STORE_ATTR               status

 L. 311       132  LOAD_FAST                'reason'
              134  LOAD_METHOD              strip
              136  CALL_METHOD_0         0  '0 positional arguments'
              138  LOAD_FAST                'self'
              140  STORE_ATTR               reason

 L. 312       142  LOAD_FAST                'version'
              144  LOAD_CONST               ('HTTP/1.0', 'HTTP/0.9')
              146  COMPARE_OP               in
              148  POP_JUMP_IF_FALSE   158  'to 158'

 L. 314       150  LOAD_CONST               10
              152  LOAD_FAST                'self'
              154  STORE_ATTR               version
              156  JUMP_FORWARD        184  'to 184'
            158_0  COME_FROM           148  '148'

 L. 315       158  LOAD_FAST                'version'
              160  LOAD_METHOD              startswith
              162  LOAD_STR                 'HTTP/1.'
              164  CALL_METHOD_1         1  '1 positional argument'
              166  POP_JUMP_IF_FALSE   176  'to 176'

 L. 316       168  LOAD_CONST               11
              170  LOAD_FAST                'self'
              172  STORE_ATTR               version
              174  JUMP_FORWARD        184  'to 184'
            176_0  COME_FROM           166  '166'

 L. 318       176  LOAD_GLOBAL              UnknownProtocol
              178  LOAD_FAST                'version'
              180  CALL_FUNCTION_1       1  '1 positional argument'
              182  RAISE_VARARGS_1       1  'exception instance'
            184_0  COME_FROM           174  '174'
            184_1  COME_FROM           156  '156'

 L. 320       184  LOAD_GLOBAL              parse_headers
              186  LOAD_FAST                'self'
              188  LOAD_ATTR                fp
              190  CALL_FUNCTION_1       1  '1 positional argument'
              192  DUP_TOP          
              194  LOAD_FAST                'self'
              196  STORE_ATTR               headers
              198  LOAD_FAST                'self'
              200  STORE_ATTR               msg

 L. 322       202  LOAD_FAST                'self'
              204  LOAD_ATTR                debuglevel
              206  LOAD_CONST               0
              208  COMPARE_OP               >
              210  POP_JUMP_IF_FALSE   242  'to 242'

 L. 323       212  SETUP_LOOP          242  'to 242'
              214  LOAD_FAST                'self'
              216  LOAD_ATTR                headers
              218  GET_ITER         
              220  FOR_ITER            240  'to 240'
              222  STORE_FAST               'hdr'

 L. 324       224  LOAD_GLOBAL              print
              226  LOAD_STR                 'header:'
              228  LOAD_FAST                'hdr'
              230  LOAD_STR                 ' '
              232  LOAD_CONST               ('end',)
              234  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              236  POP_TOP          
              238  JUMP_BACK           220  'to 220'
              240  POP_BLOCK        
            242_0  COME_FROM_LOOP      212  '212'
            242_1  COME_FROM           210  '210'

 L. 327       242  LOAD_FAST                'self'
              244  LOAD_ATTR                headers
              246  LOAD_METHOD              get
              248  LOAD_STR                 'transfer-encoding'
              250  CALL_METHOD_1         1  '1 positional argument'
              252  STORE_FAST               'tr_enc'

 L. 328       254  LOAD_FAST                'tr_enc'
          256_258  POP_JUMP_IF_FALSE   288  'to 288'
              260  LOAD_FAST                'tr_enc'
              262  LOAD_METHOD              lower
              264  CALL_METHOD_0         0  '0 positional arguments'
              266  LOAD_STR                 'chunked'
              268  COMPARE_OP               ==
          270_272  POP_JUMP_IF_FALSE   288  'to 288'

 L. 329       274  LOAD_CONST               True
              276  LOAD_FAST                'self'
              278  STORE_ATTR               chunked

 L. 330       280  LOAD_CONST               None
              282  LOAD_FAST                'self'
              284  STORE_ATTR               chunk_left
              286  JUMP_FORWARD        294  'to 294'
            288_0  COME_FROM           270  '270'
            288_1  COME_FROM           256  '256'

 L. 332       288  LOAD_CONST               False
              290  LOAD_FAST                'self'
              292  STORE_ATTR               chunked
            294_0  COME_FROM           286  '286'

 L. 335       294  LOAD_FAST                'self'
              296  LOAD_METHOD              _check_close
              298  CALL_METHOD_0         0  '0 positional arguments'
              300  LOAD_FAST                'self'
              302  STORE_ATTR               will_close

 L. 339       304  LOAD_CONST               None
              306  LOAD_FAST                'self'
              308  STORE_ATTR               length

 L. 340       310  LOAD_FAST                'self'
              312  LOAD_ATTR                headers
              314  LOAD_METHOD              get
              316  LOAD_STR                 'content-length'
              318  CALL_METHOD_1         1  '1 positional argument'
              320  STORE_FAST               'length'

 L. 343       322  LOAD_FAST                'self'
              324  LOAD_ATTR                headers
              326  LOAD_METHOD              get
              328  LOAD_STR                 'transfer-encoding'
              330  CALL_METHOD_1         1  '1 positional argument'
              332  STORE_FAST               'tr_enc'

 L. 344       334  LOAD_FAST                'length'
          336_338  POP_JUMP_IF_FALSE   412  'to 412'
              340  LOAD_FAST                'self'
              342  LOAD_ATTR                chunked
          344_346  POP_JUMP_IF_TRUE    412  'to 412'

 L. 345       348  SETUP_EXCEPT        364  'to 364'

 L. 346       350  LOAD_GLOBAL              int
              352  LOAD_FAST                'length'
              354  CALL_FUNCTION_1       1  '1 positional argument'
              356  LOAD_FAST                'self'
              358  STORE_ATTR               length
              360  POP_BLOCK        
              362  JUMP_FORWARD        392  'to 392'
            364_0  COME_FROM_EXCEPT    348  '348'

 L. 347       364  DUP_TOP          
              366  LOAD_GLOBAL              ValueError
              368  COMPARE_OP               exception-match
          370_372  POP_JUMP_IF_FALSE   390  'to 390'
              374  POP_TOP          
              376  POP_TOP          
              378  POP_TOP          

 L. 348       380  LOAD_CONST               None
              382  LOAD_FAST                'self'
              384  STORE_ATTR               length
              386  POP_EXCEPT       
              388  JUMP_FORWARD        410  'to 410'
            390_0  COME_FROM           370  '370'
              390  END_FINALLY      
            392_0  COME_FROM           362  '362'

 L. 350       392  LOAD_FAST                'self'
              394  LOAD_ATTR                length
              396  LOAD_CONST               0
              398  COMPARE_OP               <
          400_402  POP_JUMP_IF_FALSE   418  'to 418'

 L. 351       404  LOAD_CONST               None
              406  LOAD_FAST                'self'
              408  STORE_ATTR               length
            410_0  COME_FROM           388  '388'
              410  JUMP_FORWARD        418  'to 418'
            412_0  COME_FROM           344  '344'
            412_1  COME_FROM           336  '336'

 L. 353       412  LOAD_CONST               None
              414  LOAD_FAST                'self'
              416  STORE_ATTR               length
            418_0  COME_FROM           410  '410'
            418_1  COME_FROM           400  '400'

 L. 356       418  LOAD_FAST                'status'
              420  LOAD_GLOBAL              NO_CONTENT
              422  COMPARE_OP               ==
          424_426  POP_JUMP_IF_TRUE    476  'to 476'
              428  LOAD_FAST                'status'
              430  LOAD_GLOBAL              NOT_MODIFIED
              432  COMPARE_OP               ==
          434_436  POP_JUMP_IF_TRUE    476  'to 476'

 L. 357       438  LOAD_CONST               100
              440  LOAD_FAST                'status'
              442  DUP_TOP          
              444  ROT_THREE        
              446  COMPARE_OP               <=
          448_450  POP_JUMP_IF_FALSE   462  'to 462'
              452  LOAD_CONST               200
              454  COMPARE_OP               <
          456_458  POP_JUMP_IF_TRUE    476  'to 476'
              460  JUMP_FORWARD        464  'to 464'
            462_0  COME_FROM           448  '448'
              462  POP_TOP          
            464_0  COME_FROM           460  '460'

 L. 358       464  LOAD_FAST                'self'
              466  LOAD_ATTR                _method
              468  LOAD_STR                 'HEAD'
              470  COMPARE_OP               ==
          472_474  POP_JUMP_IF_FALSE   482  'to 482'
            476_0  COME_FROM           456  '456'
            476_1  COME_FROM           434  '434'
            476_2  COME_FROM           424  '424'

 L. 359       476  LOAD_CONST               0
              478  LOAD_FAST                'self'
              480  STORE_ATTR               length
            482_0  COME_FROM           472  '472'

 L. 364       482  LOAD_FAST                'self'
              484  LOAD_ATTR                will_close
          486_488  POP_JUMP_IF_TRUE    516  'to 516'

 L. 365       490  LOAD_FAST                'self'
              492  LOAD_ATTR                chunked
          494_496  POP_JUMP_IF_TRUE    516  'to 516'

 L. 366       498  LOAD_FAST                'self'
              500  LOAD_ATTR                length
              502  LOAD_CONST               None
              504  COMPARE_OP               is
          506_508  POP_JUMP_IF_FALSE   516  'to 516'

 L. 367       510  LOAD_CONST               True
              512  LOAD_FAST                'self'
              514  STORE_ATTR               will_close
            516_0  COME_FROM           506  '506'
            516_1  COME_FROM           494  '494'
            516_2  COME_FROM           486  '486'

Parse error at or near `COME_FROM' instruction at offset 482_0

    def _check_close(self):
        conn = self.headers.get('connection')
        if self.version == 11:
            if conn:
                if 'close' in conn.lower():
                    return True
            return False
        if self.headers.get('keep-alive'):
            return False
        if conn:
            if 'keep-alive' in conn.lower():
                return False
        pconn = self.headers.get('proxy-connection')
        if pconn:
            if 'keep-alive' in pconn.lower():
                return False
        return True

    def _close_conn(self):
        fp = self.fp
        self.fp = None
        fp.close()

    def close(self):
        try:
            super().close()
        finally:
            if self.fp:
                self._close_conn()

    def flush(self):
        super().flush()
        if self.fp:
            self.fp.flush()

    def readable(self):
        return True

    def isclosed(self):
        return self.fp is None

    def read(self, amt=None):
        if self.fp is None:
            return b''
            if self._method == 'HEAD':
                self._close_conn()
                return b''
            if amt is not None:
                b = bytearray(amt)
                n = self.readinto(b)
                return memoryview(b)[:n].tobytes()
            if self.chunked:
                return self._readall_chunked()
            if self.length is None:
                s = self.fp.read()
        else:
            try:
                s = self._safe_read(self.length)
            except IncompleteRead:
                self._close_conn()
                raise

            self.length = 0
        self._close_conn()
        return s

    def readinto(self, b):
        if self.fp is None:
            return 0
            if self._method == 'HEAD':
                self._close_conn()
                return 0
            if self.chunked:
                return self._readinto_chunked(b)
            if self.length is not None:
                if len(b) > self.length:
                    b = memoryview(b)[0:self.length]
            n = self.fp.readinto(b)
            if not n:
                if b:
                    self._close_conn()
        elif self.length is not None:
            self.length -= n
            if not self.length:
                self._close_conn()
        return n

    def _read_next_chunk_size(self):
        line = self.fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise LineTooLong('chunk size')
        i = line.find(b';')
        if i >= 0:
            line = line[:i]
        try:
            return int(line, 16)
        except ValueError:
            self._close_conn()
            raise

    def _read_and_discard_trailer(self):
        while 1:
            line = self.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong('trailer line')
            if not line:
                break
            if line in (b'\r\n', b'\n', b''):
                break

    def _get_chunk_left(self):
        chunk_left = self.chunk_left
        if not chunk_left:
            if chunk_left is not None:
                self._safe_read(2)
            try:
                chunk_left = self._read_next_chunk_size()
            except ValueError:
                raise IncompleteRead(b'')

            if chunk_left == 0:
                self._read_and_discard_trailer()
                self._close_conn()
                chunk_left = None
            self.chunk_left = chunk_left
        return chunk_left

    def _readall_chunked(self):
        value = []
        try:
            while True:
                chunk_left = self._get_chunk_left()
                if chunk_left is None:
                    break
                value.append(self._safe_read(chunk_left))
                self.chunk_left = 0

            return (b'').join(value)
        except IncompleteRead:
            raise IncompleteRead((b'').join(value))

    def _readinto_chunked(self, b):
        total_bytes = 0
        mvb = memoryview(b)
        try:
            while True:
                chunk_left = self._get_chunk_left()
                if chunk_left is None:
                    return total_bytes
                if len(mvb) <= chunk_left:
                    n = self._safe_readinto(mvb)
                    self.chunk_left = chunk_left - n
                    return total_bytes + n
                temp_mvb = mvb[:chunk_left]
                n = self._safe_readinto(temp_mvb)
                mvb = mvb[n:]
                total_bytes += n
                self.chunk_left = 0

        except IncompleteRead:
            raise IncompleteRead(bytes(b[0:total_bytes]))

    def _safe_read(self, amt):
        s = []
        while amt > 0:
            chunk = self.fp.read(min(amt, MAXAMOUNT))
            if not chunk:
                raise IncompleteRead((b'').join(s), amt)
            s.append(chunk)
            amt -= len(chunk)

        return (b'').join(s)

    def _safe_readinto(self, b):
        total_bytes = 0
        mvb = memoryview(b)
        while total_bytes < len(b):
            if MAXAMOUNT < len(mvb):
                temp_mvb = mvb[0:MAXAMOUNT]
                n = self.fp.readinto(temp_mvb)
            else:
                n = self.fp.readinto(mvb)
            if not n:
                raise IncompleteRead(bytes(mvb[0:total_bytes]), len(b))
            mvb = mvb[n:]
            total_bytes += n

        return total_bytes

    def read1(self, n=-1):
        if not self.fp is None:
            if self._method == 'HEAD':
                return b''
            if self.chunked:
                return self._read1_chunked(n)
            if self.length is not None:
                if n < 0 or n > self.length:
                    n = self.length
            result = self.fp.read1(n)
            if not result:
                if n:
                    self._close_conn()
        elif self.length is not None:
            self.length -= len(result)
        return result

    def peek(self, n=-1):
        if self.fp is None or self._method == 'HEAD':
            return b''
        if self.chunked:
            return self._peek_chunked(n)
        return self.fp.peek(n)

    def readline(self, limit=-1):
        if not self.fp is None:
            if self._method == 'HEAD':
                return b''
            if self.chunked:
                return super().readline(limit)
            if self.length is not None:
                if limit < 0 or limit > self.length:
                    limit = self.length
            result = self.fp.readline(limit)
            if not result:
                if limit:
                    self._close_conn()
        elif self.length is not None:
            self.length -= len(result)
        return result

    def _read1_chunked(self, n):
        chunk_left = self._get_chunk_left()
        if chunk_left is None or n == 0:
            return b''
        if not 0 <= n <= chunk_left:
            n = chunk_left
        read = self.fp.read1(n)
        self.chunk_left -= len(read)
        if not read:
            raise IncompleteRead(b'')
        return read

    def _peek_chunked(self, n):
        try:
            chunk_left = self._get_chunk_left()
        except IncompleteRead:
            return b''
        else:
            if chunk_left is None:
                return b''
            return self.fp.peek(chunk_left)[:chunk_left]

    def fileno(self):
        return self.fp.fileno()

    def getheader(self, name, default=None):
        if self.headers is None:
            raise ResponseNotReady()
        else:
            headers = self.headers.get_all(name) or default
            return isinstance(headers, str) or hasattr(headers, '__iter__') or headers
        return ', '.join(headers)

    def getheaders(self):
        if self.headers is None:
            raise ResponseNotReady()
        return list(self.headers.items())

    def __iter__(self):
        return self

    def info(self):
        return self.headers

    def geturl(self):
        return self.url

    def getcode(self):
        return self.status


class HTTPConnection:
    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'
    response_class = HTTPResponse
    default_port = HTTP_PORT
    auto_open = 1
    debuglevel = 0

    @staticmethod
    def _is_textIO(stream):
        return isinstance(stream, io.TextIOBase)

    @staticmethod
    def _get_content_length(body, method):
        if body is None:
            if method.upper() in _METHODS_EXPECTING_BODY:
                return 0
        else:
            return
            if hasattr(body, 'read'):
                return
            try:
                mv = memoryview(body)
                return mv.nbytes
            except TypeError:
                pass

        if isinstance(body, str):
            return len(body)

    def __init__(self, host, port=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, blocksize=8192):
        self.timeout = timeout
        self.source_address = source_address
        self.blocksize = blocksize
        self.sock = None
        self._buffer = []
        self._HTTPConnection__response = None
        self._HTTPConnection__state = _CS_IDLE
        self._method = None
        self._tunnel_host = None
        self._tunnel_port = None
        self._tunnel_headers = {}
        self.host, self.port = self._get_hostport(host, port)
        self._create_connection = socket.create_connection

    def set_tunnel(self, host, port=None, headers=None):
        if self.sock:
            raise RuntimeError("Can't set up tunnel for established connection")
        else:
            self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)
            if headers:
                self._tunnel_headers = headers
            else:
                self._tunnel_headers.clear()

    def _get_hostport(self, host, port):
        if port is None:
            i = host.rfind(':')
            j = host.rfind(']')
            if i > j:
                try:
                    port = int(host[i + 1:])
                except ValueError:
                    if host[i + 1:] == '':
                        port = self.default_port
                    else:
                        raise InvalidURL("nonnumeric port: '%s'" % host[i + 1:])

                host = host[:i]
            else:
                port = self.default_port
            if host:
                if host[0] == '[':
                    if host[-1] == ']':
                        host = host[1:-1]
        return (
         host, port)

    def set_debuglevel(self, level):
        self.debuglevel = level

    def _tunnel(self):
        connect_str = 'CONNECT %s:%d HTTP/1.0\r\n' % (self._tunnel_host,
         self._tunnel_port)
        connect_bytes = connect_str.encode('ascii')
        self.send(connect_bytes)
        for header, value in self._tunnel_headers.items():
            header_str = '%s: %s\r\n' % (header, value)
            header_bytes = header_str.encode('latin-1')
            self.send(header_bytes)

        self.send(b'\r\n')
        response = self.response_class((self.sock), method=(self._method))
        version, code, message = response._read_status()
        if code != http.HTTPStatus.OK:
            self.close()
            raise OSError('Tunnel connection failed: %d %s' % (code,
             message.strip()))
        while 1:
            line = response.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong('header line')
            if not line:
                break
            if line in (b'\r\n', b'\n', b''):
                break
            if self.debuglevel > 0:
                print('header:', line.decode())

    def connect(self):
        self.sock = self._create_connection((
         self.host, self.port), self.timeout, self.source_address)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self._tunnel_host:
            self._tunnel()

    def close(self):
        self._HTTPConnection__state = _CS_IDLE
        try:
            sock = self.sock
            if sock:
                self.sock = None
                sock.close()
        finally:
            response = self._HTTPConnection__response
            if response:
                self._HTTPConnection__response = None
                response.close()

    def send(self, data):
        if self.sock is None:
            if self.auto_open:
                self.connect()
            else:
                raise NotConnected()
        elif self.debuglevel > 0:
            print('send:', repr(data))
        else:
            if hasattr(data, 'read'):
                if self.debuglevel > 0:
                    print('sendIng a read()able')
                encode = self._is_textIO(data)
                if encode:
                    if self.debuglevel > 0:
                        print('encoding file using iso-8859-1')
                while True:
                    datablock = data.read(self.blocksize)
                    if not datablock:
                        break
                    if encode:
                        datablock = datablock.encode('iso-8859-1')
                    self.sock.sendall(datablock)

                return
            try:
                self.sock.sendall(data)
            except TypeError:
                if isinstance(data, collections.abc.Iterable):
                    for d in data:
                        self.sock.sendall(d)

                else:
                    raise TypeError('data should be a bytes-like object or an iterable, got %r' % type(data))

    def _output(self, s):
        self._buffer.append(s)

    def _read_readable(self, readable):
        if self.debuglevel > 0:
            print('sendIng a read()able')
        encode = self._is_textIO(readable)
        if encode:
            if self.debuglevel > 0:
                print('encoding file using iso-8859-1')
        while True:
            datablock = readable.read(self.blocksize)
            if not datablock:
                break
            if encode:
                datablock = datablock.encode('iso-8859-1')
            yield datablock

    def _send_output(self, message_body=None, encode_chunked=False):
        self._buffer.extend((b'', b''))
        msg = (b'\r\n').join(self._buffer)
        del self._buffer[:]
        self.send(msg)
        if message_body is not None:
            if hasattr(message_body, 'read'):
                chunks = self._read_readable(message_body)
            else:
                try:
                    memoryview(message_body)
                except TypeError:
                    try:
                        chunks = iter(message_body)
                    except TypeError:
                        raise TypeError('message_body should be a bytes-like object or an iterable, got %r' % type(message_body))

                else:
                    chunks = (
                     message_body,)
                for chunk in chunks:
                    if not chunk:
                        if self.debuglevel > 0:
                            print('Zero length chunk ignored')
                            continue
                        if encode_chunked:
                            if self._http_vsn == 11:
                                chunk = f"{len(chunk):X}\r\n".encode('ascii') + chunk + b'\r\n'
                        self.send(chunk)

            if encode_chunked:
                if self._http_vsn == 11:
                    self.send(b'0\r\n\r\n')

    def putrequest(self, method, url, skip_host=False, skip_accept_encoding=False):
        if self._HTTPConnection__response:
            if self._HTTPConnection__response.isclosed():
                self._HTTPConnection__response = None
            elif self._HTTPConnection__state == _CS_IDLE:
                self._HTTPConnection__state = _CS_REQ_STARTED
            else:
                raise CannotSendRequest(self._HTTPConnection__state)
            self._method = method
            if not url:
                url = '/'
            request = '%s %s %s' % (method, url, self._http_vsn_str)
            self._output(request.encode('ascii'))
            if self._http_vsn == 11:
                if not skip_host:
                    netloc = ''
                    if url.startswith('http'):
                        nil, netloc, nil, nil, nil = urlsplit(url)
                    if netloc:
                        try:
                            netloc_enc = netloc.encode('ascii')
                        except UnicodeEncodeError:
                            netloc_enc = netloc.encode('idna')

                        self.putheader('Host', netloc_enc)
            else:
                if self._tunnel_host:
                    host = self._tunnel_host
                    port = self._tunnel_port
                else:
                    host = self.host
                    port = self.port
                try:
                    host_enc = host.encode('ascii')
                except UnicodeEncodeError:
                    host_enc = host.encode('idna')

                if host.find(':') >= 0:
                    host_enc = b'[' + host_enc + b']'
                if port == self.default_port:
                    self.putheader('Host', host_enc)
                else:
                    host_enc = host_enc.decode('ascii')
                    self.putheader('Host', '%s:%s' % (host_enc, port))
            skip_accept_encoding or self.putheader('Accept-Encoding', 'identity')
        else:
            pass

    def putheader(self, header, *values):
        if self._HTTPConnection__state != _CS_REQ_STARTED:
            raise CannotSendHeader()
        else:
            if hasattr(header, 'encode'):
                header = header.encode('ascii')
            assert _is_legal_header_name(header), 'Invalid header name %r' % (header,)
        values = list(values)
        for i, one_value in enumerate(values):
            if hasattr(one_value, 'encode'):
                values[i] = one_value.encode('latin-1')
            else:
                if isinstance(one_value, int):
                    values[i] = str(one_value).encode('ascii')
            if _is_illegal_header_value(values[i]):
                raise ValueError('Invalid header value %r' % (values[i],))

        value = (b'\r\n\t').join(values)
        header = header + b': ' + value
        self._output(header)

    def endheaders(self, message_body=None, *, encode_chunked=False):
        if self._HTTPConnection__state == _CS_REQ_STARTED:
            self._HTTPConnection__state = _CS_REQ_SENT
        else:
            raise CannotSendHeader()
        self._send_output(message_body, encode_chunked=encode_chunked)

    def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
        self._send_request(method, url, body, headers, encode_chunked)

    def _send_request(self, method, url, body, headers, encode_chunked):
        header_names = frozenset((k.lower() for k in headers))
        skips = {}
        if 'host' in header_names:
            skips['skip_host'] = 1
        elif 'accept-encoding' in header_names:
            skips['skip_accept_encoding'] = 1
        else:
            (self.putrequest)(method, url, **skips)
            if 'content-length' not in header_names:
                if 'transfer-encoding' not in header_names:
                    encode_chunked = False
                    content_length = self._get_content_length(body, method)
                    if content_length is None:
                        if body is not None:
                            if self.debuglevel > 0:
                                print('Unable to determine size of %r' % body)
                            encode_chunked = True
                            self.putheader('Transfer-Encoding', 'chunked')
                    else:
                        self.putheader('Content-Length', str(content_length))
            else:
                encode_chunked = False
        for hdr, value in headers.items():
            self.putheader(hdr, value)

        if isinstance(body, str):
            body = _encode(body, 'body')
        self.endheaders(body, encode_chunked=encode_chunked)

    def getresponse(self):
        if self._HTTPConnection__response:
            if self._HTTPConnection__response.isclosed():
                self._HTTPConnection__response = None
        else:
            if self._HTTPConnection__state != _CS_REQ_SENT or self._HTTPConnection__response:
                raise ResponseNotReady(self._HTTPConnection__state)
            elif self.debuglevel > 0:
                response = self.response_class((self.sock), (self.debuglevel), method=(self._method))
            else:
                response = self.response_class((self.sock), method=(self._method))
            try:
                try:
                    response.begin()
                except ConnectionError:
                    self.close()
                    raise

                self._HTTPConnection__state = _CS_IDLE
                if response.will_close:
                    self.close()
                else:
                    self._HTTPConnection__response = response
                return response
            except:
                response.close()
                raise


try:
    import ssl
except ImportError:
    pass
else:

    class HTTPSConnection(HTTPConnection):
        default_port = HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, *, context=None, check_hostname=None, blocksize=8192):
            super(HTTPSConnection, self).__init__(host, port, timeout, source_address,
              blocksize=blocksize)
            if key_file is not None or cert_file is not None or check_hostname is not None:
                import warnings
                warnings.warn('key_file, cert_file and check_hostname are deprecated, use a custom context instead.', DeprecationWarning, 2)
            self.key_file = key_file
            self.cert_file = cert_file
            if context is None:
                context = ssl._create_default_https_context()
            will_verify = context.verify_mode != ssl.CERT_NONE
            if check_hostname is None:
                check_hostname = context.check_hostname
            if check_hostname:
                if not will_verify:
                    raise ValueError('check_hostname needs a SSL context with either CERT_OPTIONAL or CERT_REQUIRED')
            if key_file or cert_file:
                context.load_cert_chain(cert_file, key_file)
            self._context = context
            if check_hostname is not None:
                self._context.check_hostname = check_hostname

        def connect(self):
            super().connect()
            if self._tunnel_host:
                server_hostname = self._tunnel_host
            else:
                server_hostname = self.host
            self.sock = self._context.wrap_socket((self.sock), server_hostname=server_hostname)


    __all__.append('HTTPSConnection')

class HTTPException(Exception):
    pass


class NotConnected(HTTPException):
    pass


class InvalidURL(HTTPException):
    pass


class UnknownProtocol(HTTPException):

    def __init__(self, version):
        self.args = (
         version,)
        self.version = version


class UnknownTransferEncoding(HTTPException):
    pass


class UnimplementedFileMode(HTTPException):
    pass


class IncompleteRead(HTTPException):

    def __init__(self, partial, expected=None):
        self.args = (
         partial,)
        self.partial = partial
        self.expected = expected

    def __repr__(self):
        if self.expected is not None:
            e = ', %i more expected' % self.expected
        else:
            e = ''
        return '%s(%i bytes read%s)' % (self.__class__.__name__,
         len(self.partial), e)

    def __str__(self):
        return repr(self)


class ImproperConnectionState(HTTPException):
    pass


class CannotSendRequest(ImproperConnectionState):
    pass


class CannotSendHeader(ImproperConnectionState):
    pass


class ResponseNotReady(ImproperConnectionState):
    pass


class BadStatusLine(HTTPException):

    def __init__(self, line):
        if not line:
            line = repr(line)
        self.args = (
         line,)
        self.line = line


class LineTooLong(HTTPException):

    def __init__(self, line_type):
        HTTPException.__init__(self, 'got more than %d bytes when reading %s' % (
         _MAXLINE, line_type))


class RemoteDisconnected(ConnectionResetError, BadStatusLine):

    def __init__(self, *pos, **kw):
        BadStatusLine.__init__(self, '')
        (ConnectionResetError.__init__)(self, *pos, **kw)


error = HTTPException