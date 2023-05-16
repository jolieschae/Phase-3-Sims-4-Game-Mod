# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\http\server.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 47281 bytes
__version__ = '0.6'
__all__ = [
 "'HTTPServer'", "'ThreadingHTTPServer'", "'BaseHTTPRequestHandler'", 
 "'SimpleHTTPRequestHandler'", 
 "'CGIHTTPRequestHandler'"]
import copy, datetime, email.utils, html, http.client, io, mimetypes, os, posixpath, select, shutil, socket, socketserver, sys, time, urllib.parse
from functools import partial
from http import HTTPStatus
DEFAULT_ERROR_MESSAGE = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n        "http://www.w3.org/TR/html4/strict.dtd">\n<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">\n        <title>Error response</title>\n    </head>\n    <body>\n        <h1>Error response</h1>\n        <p>Error code: %(code)d</p>\n        <p>Message: %(message)s.</p>\n        <p>Error code explanation: %(code)s - %(explain)s.</p>\n    </body>\n</html>\n'
DEFAULT_ERROR_CONTENT_TYPE = 'text/html;charset=utf-8'

class HTTPServer(socketserver.TCPServer):
    allow_reuse_address = 1

    def server_bind(self):
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


class BaseHTTPRequestHandler(socketserver.StreamRequestHandler):
    sys_version = 'Python/' + sys.version.split()[0]
    server_version = 'BaseHTTP/' + __version__
    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE
    default_request_version = 'HTTP/0.9'

    def parse_request(self):
        self.command = None
        self.request_version = version = self.default_request_version
        self.close_connection = True
        requestline = str(self.raw_requestline, 'iso-8859-1')
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        if len(words) == 0:
            return False
        if len(words) >= 3:
            version = words[-1]
            try:
                if not version.startswith('HTTP/'):
                    raise ValueError
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split('.')
                if len(version_number) != 2:
                    raise ValueError
                version_number = (
                 int(version_number[0]), int(version_number[1]))
            except (ValueError, IndexError):
                self.send_error(HTTPStatus.BAD_REQUEST, 'Bad request version (%r)' % version)
                return False
            else:
                if version_number >= (1, 1):
                    if self.protocol_version >= 'HTTP/1.1':
                        self.close_connection = False
                else:
                    if version_number >= (2, 0):
                        self.send_error(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED, 'Invalid HTTP version (%s)' % base_version_number)
                        return False
                        self.request_version = version
                    elif not 2 <= len(words) <= 3:
                        self.send_error(HTTPStatus.BAD_REQUEST, 'Bad request syntax (%r)' % requestline)
                        return False
                        command, path = words[:2]
                        if len(words) == 2:
                            self.close_connection = True
                            if command != 'GET':
                                self.send_error(HTTPStatus.BAD_REQUEST, 'Bad HTTP/0.9 request type (%r)' % command)
                                return False
                    self.command, self.path = command, path
                    try:
                        self.headers = http.client.parse_headers((self.rfile), _class=(self.MessageClass))
                    except http.client.LineTooLong as err:
                        try:
                            self.send_error(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE, 'Line too long', str(err))
                            return False
                        finally:
                            err = None
                            del err

                    except http.client.HTTPException as err:
                        try:
                            self.send_error(HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE, 'Too many headers', str(err))
                            return False
                        finally:
                            err = None
                            del err

                conntype = self.headers.get('Connection', '')
                if conntype.lower() == 'close':
                    self.close_connection = True
        else:
            if conntype.lower() == 'keep-alive':
                if self.protocol_version >= 'HTTP/1.1':
                    self.close_connection = False
            expect = self.headers.get('Expect', '')
            if expect.lower() == '100-continue':
                if self.protocol_version >= 'HTTP/1.1':
                    if self.request_version >= 'HTTP/1.1':
                        if not self.handle_expect_100():
                            return False
            return True

    def handle_expect_100(self):
        self.send_response_only(HTTPStatus.CONTINUE)
        self.end_headers()
        return True

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(HTTPStatus.NOT_IMPLEMENTED, 'Unsupported method (%r)' % self.command)
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush()
        except socket.timeout as e:
            try:
                self.log_error('Request timed out: %r', e)
                self.close_connection = True
                return
            finally:
                e = None
                del e

    def handle(self):
        self.close_connection = True
        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    def send_error(self, code, message=None, explain=None):
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = ('???', '???')

        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self.log_error('code %d, message %s', code, message)
        self.send_response(code, message)
        self.send_header('Connection', 'close')
        body = None
        if code >= 200:
            if code not in (HTTPStatus.NO_CONTENT,
             HTTPStatus.RESET_CONTENT,
             HTTPStatus.NOT_MODIFIED):
                content = self.error_message_format % {'code':code, 
                 'message':html.escape(message, quote=False), 
                 'explain':html.escape(explain, quote=False)}
                body = content.encode('UTF-8', 'replace')
                self.send_header('Content-Type', self.error_content_type)
                self.send_header('Content-Length', int(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            if body:
                self.wfile.write(body)

    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def send_response_only(self, code, message=None):
        if self.request_version != 'HTTP/0.9':
            if message is None:
                if code in self.responses:
                    message = self.responses[code][0]
                else:
                    message = ''
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(('%s %d %s\r\n' % (
             self.protocol_version, code, message)).encode('latin-1', 'strict'))

    def send_header(self, keyword, value):
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(('%s: %s\r\n' % (keyword, value)).encode('latin-1', 'strict'))
        elif keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            else:
                if value.lower() == 'keep-alive':
                    self.close_connection = False

    def end_headers(self):
        if self.request_version != 'HTTP/0.9':
            self._headers_buffer.append(b'\r\n')
            self.flush_headers()

    def flush_headers(self):
        if hasattr(self, '_headers_buffer'):
            self.wfile.write((b'').join(self._headers_buffer))
            self._headers_buffer = []

    def log_request(self, code='-', size='-'):
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        (self.log_message)(format, *args)

    def log_message(self, format, *args):
        sys.stderr.write('%s - - [%s] %s\n' % (
         self.address_string(),
         self.log_date_time_string(),
         format % args))

    def version_string(self):
        return self.server_version + ' ' + self.sys_version

    def date_time_string(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        return email.utils.formatdate(timestamp, usegmt=True)

    def log_date_time_string(self):
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = '%02d/%3s/%04d %02d:%02d:%02d' % (
         day, self.monthname[month], year, hh, mm, ss)
        return s

    weekdayname = [
     "'Mon'", "'Tue'", "'Wed'", "'Thu'", "'Fri'", "'Sat'", "'Sun'"]
    monthname = [
     None, 
     "'Jan'", "'Feb'", "'Mar'", "'Apr'", "'May'", 
     "'Jun'", 
     "'Jul'", "'Aug'", "'Sep'", "'Oct'", "'Nov'", 
     "'Dec'"]

    def address_string(self):
        return self.client_address[0]

    protocol_version = 'HTTP/1.0'
    MessageClass = http.client.HTTPMessage
    responses = {v: (v.phrase, v.description) for v in HTTPStatus.__members__.values()}


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = 'SimpleHTTP/' + __version__

    def __init__(self, *args, directory=None, **kwargs):
        if directory is None:
            directory = os.getcwd()
        self.directory = directory
        (super().__init__)(*args, **kwargs)

    def do_GET(self):
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                 parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header('Location', new_url)
                self.end_headers()
                return
            for index in ('index.html', 'index.htm'):
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)

        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
            return
        else:
            try:
                fs = os.fstat(f.fileno())
                if 'If-Modified-Since' in self.headers:
                    if 'If-None-Match' not in self.headers:
                        try:
                            ims = email.utils.parsedate_to_datetime(self.headers['If-Modified-Since'])
                        except (TypeError, IndexError, OverflowError, ValueError):
                            pass
                        else:
                            if ims.tzinfo is None:
                                ims = ims.replace(tzinfo=(datetime.timezone.utc))
                        if ims.tzinfo is datetime.timezone.utc:
                            last_modif = datetime.datetime.fromtimestamp(fs.st_mtime, datetime.timezone.utc)
                            last_modif = last_modif.replace(microsecond=0)
                            if last_modif <= ims:
                                self.send_response(HTTPStatus.NOT_MODIFIED)
                                self.end_headers()
                                f.close()
                                return
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', ctype)
                self.send_header('Content-Length', str(fs[6]))
                self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
                self.end_headers()
                return f
            except:
                f.close()
                raise

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, 'No permission to list directory')
            return
        else:
            list.sort(key=(lambda a: a.lower()))
            r = []
            try:
                displaypath = urllib.parse.unquote((self.path), errors='surrogatepass')
            except UnicodeDecodeError:
                displaypath = urllib.parse.unquote(path)

            displaypath = html.escape(displaypath, quote=False)
            enc = sys.getfilesystemencoding()
            title = 'Directory listing for %s' % displaypath
            r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')
            r.append('<html>\n<head>')
            r.append('<meta http-equiv="Content-Type" content="text/html; charset=%s">' % enc)
            r.append('<title>%s</title>\n</head>' % title)
            r.append('<body>\n<h1>%s</h1>' % title)
            r.append('<hr>\n<ul>')
            for name in list:
                fullname = os.path.join(path, name)
                displayname = linkname = name
                if os.path.isdir(fullname):
                    displayname = name + '/'
                    linkname = name + '/'
                if os.path.islink(fullname):
                    displayname = name + '@'
                r.append('<li><a href="%s">%s</a></li>' % (
                 urllib.parse.quote(linkname, errors='surrogatepass'),
                 html.escape(displayname, quote=False)))

            r.append('</ul>\n<hr>\n</body>\n</html>\n')
            encoded = '\n'.join(r).encode(enc, 'surrogateescape')
            f = io.BytesIO()
            f.write(encoded)
            f.seek(0)
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html; charset=%s' % enc)
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            return f

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)

        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)
        path = self.directory
        for word in words:
            if not os.path.dirname(word):
                if word in (os.curdir, os.pardir):
                    continue
                path = os.path.join(path, word)

        if trailing_slash:
            path += '/'
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
     '': "'application/octet-stream'", 
     '.py': "'text/plain'", 
     '.c': "'text/plain'", 
     '.h': "'text/plain'"})


def _url_collapse_path(path):
    path, _, query = path.partition('?')
    path = urllib.parse.unquote(path)
    path_parts = path.split('/')
    head_parts = []
    for part in path_parts[:-1]:
        if part == '..':
            head_parts.pop()

    if path_parts:
        tail_part = path_parts.pop()
        if tail_part:
            if tail_part == '..':
                head_parts.pop()
                tail_part = ''
            elif tail_part == '.':
                tail_part = ''
    else:
        tail_part = ''
    if query:
        tail_part = '?'.join((tail_part, query))
    splitpath = ('/' + '/'.join(head_parts), tail_part)
    collapsed_path = '/'.join(splitpath)
    return collapsed_path


nobody = None

def nobody_uid():
    global nobody
    if nobody:
        return nobody
    try:
        import pwd
    except ImportError:
        return -1
    else:
        try:
            nobody = pwd.getpwnam('nobody')[2]
        except KeyError:
            nobody = 1 + max((x[2] for x in pwd.getpwall()))

        return nobody


def executable(path):
    return os.access(path, os.X_OK)


class CGIHTTPRequestHandler(SimpleHTTPRequestHandler):
    have_fork = hasattr(os, 'fork')
    rbufsize = 0

    def do_POST(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            self.send_error(HTTPStatus.NOT_IMPLEMENTED, 'Can only POST to CGI scripts')

    def send_head(self):
        if self.is_cgi():
            return self.run_cgi()
        return SimpleHTTPRequestHandler.send_head(self)

    def is_cgi(self):
        collapsed_path = _url_collapse_path(self.path)
        dir_sep = collapsed_path.find('/', 1)
        head, tail = collapsed_path[:dir_sep], collapsed_path[dir_sep + 1:]
        if head in self.cgi_directories:
            self.cgi_info = (
             head, tail)
            return True
        return False

    cgi_directories = [
     '/cgi-bin', '/htbin']

    def is_executable(self, path):
        return executable(path)

    def is_python(self, path):
        head, tail = os.path.splitext(path)
        return tail.lower() in ('.py', '.pyw')

    def run_cgi--- This code section failed: ---

 L.1029         0  LOAD_FAST                'self'
                2  LOAD_ATTR                cgi_info
                4  UNPACK_SEQUENCE_2     2 
                6  STORE_FAST               'dir'
                8  STORE_FAST               'rest'

 L.1030        10  LOAD_FAST                'dir'
               12  LOAD_STR                 '/'
               14  BINARY_ADD       
               16  LOAD_FAST                'rest'
               18  BINARY_ADD       
               20  STORE_FAST               'path'

 L.1031        22  LOAD_FAST                'path'
               24  LOAD_METHOD              find
               26  LOAD_STR                 '/'
               28  LOAD_GLOBAL              len
               30  LOAD_FAST                'dir'
               32  CALL_FUNCTION_1       1  '1 positional argument'
               34  LOAD_CONST               1
               36  BINARY_ADD       
               38  CALL_METHOD_2         2  '2 positional arguments'
               40  STORE_FAST               'i'

 L.1032        42  SETUP_LOOP          140  'to 140'
               44  LOAD_FAST                'i'
               46  LOAD_CONST               0
               48  COMPARE_OP               >=
               50  POP_JUMP_IF_FALSE   138  'to 138'

 L.1033        52  LOAD_FAST                'path'
               54  LOAD_CONST               None
               56  LOAD_FAST                'i'
               58  BUILD_SLICE_2         2 
               60  BINARY_SUBSCR    
               62  STORE_FAST               'nextdir'

 L.1034        64  LOAD_FAST                'path'
               66  LOAD_FAST                'i'
               68  LOAD_CONST               1
               70  BINARY_ADD       
               72  LOAD_CONST               None
               74  BUILD_SLICE_2         2 
               76  BINARY_SUBSCR    
               78  STORE_FAST               'nextrest'

 L.1036        80  LOAD_FAST                'self'
               82  LOAD_METHOD              translate_path
               84  LOAD_FAST                'nextdir'
               86  CALL_METHOD_1         1  '1 positional argument'
               88  STORE_FAST               'scriptdir'

 L.1037        90  LOAD_GLOBAL              os
               92  LOAD_ATTR                path
               94  LOAD_METHOD              isdir
               96  LOAD_FAST                'scriptdir'
               98  CALL_METHOD_1         1  '1 positional argument'
              100  POP_JUMP_IF_FALSE   134  'to 134'

 L.1038       102  LOAD_FAST                'nextdir'
              104  LOAD_FAST                'nextrest'
              106  ROT_TWO          
              108  STORE_FAST               'dir'
              110  STORE_FAST               'rest'

 L.1039       112  LOAD_FAST                'path'
              114  LOAD_METHOD              find
              116  LOAD_STR                 '/'
              118  LOAD_GLOBAL              len
              120  LOAD_FAST                'dir'
              122  CALL_FUNCTION_1       1  '1 positional argument'
              124  LOAD_CONST               1
              126  BINARY_ADD       
              128  CALL_METHOD_2         2  '2 positional arguments'
              130  STORE_FAST               'i'
              132  JUMP_BACK            44  'to 44'
            134_0  COME_FROM           100  '100'

 L.1041       134  BREAK_LOOP       
              136  JUMP_BACK            44  'to 44'
            138_0  COME_FROM            50  '50'
              138  POP_BLOCK        
            140_0  COME_FROM_LOOP       42  '42'

 L.1044       140  LOAD_FAST                'rest'
              142  LOAD_METHOD              partition
              144  LOAD_STR                 '?'
              146  CALL_METHOD_1         1  '1 positional argument'
              148  UNPACK_SEQUENCE_3     3 
              150  STORE_FAST               'rest'
              152  STORE_FAST               '_'
              154  STORE_FAST               'query'

 L.1048       156  LOAD_FAST                'rest'
              158  LOAD_METHOD              find
              160  LOAD_STR                 '/'
              162  CALL_METHOD_1         1  '1 positional argument'
              164  STORE_FAST               'i'

 L.1049       166  LOAD_FAST                'i'
              168  LOAD_CONST               0
              170  COMPARE_OP               >=
              172  POP_JUMP_IF_FALSE   202  'to 202'

 L.1050       174  LOAD_FAST                'rest'
              176  LOAD_CONST               None
              178  LOAD_FAST                'i'
              180  BUILD_SLICE_2         2 
              182  BINARY_SUBSCR    
              184  LOAD_FAST                'rest'
              186  LOAD_FAST                'i'
              188  LOAD_CONST               None
              190  BUILD_SLICE_2         2 
              192  BINARY_SUBSCR    
              194  ROT_TWO          
              196  STORE_FAST               'script'
              198  STORE_FAST               'rest'
              200  JUMP_FORWARD        212  'to 212'
            202_0  COME_FROM           172  '172'

 L.1052       202  LOAD_FAST                'rest'
              204  LOAD_STR                 ''
              206  ROT_TWO          
              208  STORE_FAST               'script'
              210  STORE_FAST               'rest'
            212_0  COME_FROM           200  '200'

 L.1054       212  LOAD_FAST                'dir'
              214  LOAD_STR                 '/'
              216  BINARY_ADD       
              218  LOAD_FAST                'script'
              220  BINARY_ADD       
              222  STORE_FAST               'scriptname'

 L.1055       224  LOAD_FAST                'self'
              226  LOAD_METHOD              translate_path
              228  LOAD_FAST                'scriptname'
              230  CALL_METHOD_1         1  '1 positional argument'
              232  STORE_FAST               'scriptfile'

 L.1056       234  LOAD_GLOBAL              os
              236  LOAD_ATTR                path
              238  LOAD_METHOD              exists
              240  LOAD_FAST                'scriptfile'
              242  CALL_METHOD_1         1  '1 positional argument'
          244_246  POP_JUMP_IF_TRUE    270  'to 270'

 L.1057       248  LOAD_FAST                'self'
              250  LOAD_METHOD              send_error

 L.1058       252  LOAD_GLOBAL              HTTPStatus
              254  LOAD_ATTR                NOT_FOUND

 L.1059       256  LOAD_STR                 'No such CGI script (%r)'
              258  LOAD_FAST                'scriptname'
              260  BINARY_MODULO    
              262  CALL_METHOD_2         2  '2 positional arguments'
              264  POP_TOP          

 L.1060       266  LOAD_CONST               None
              268  RETURN_VALUE     
            270_0  COME_FROM           244  '244'

 L.1061       270  LOAD_GLOBAL              os
              272  LOAD_ATTR                path
              274  LOAD_METHOD              isfile
              276  LOAD_FAST                'scriptfile'
              278  CALL_METHOD_1         1  '1 positional argument'
          280_282  POP_JUMP_IF_TRUE    306  'to 306'

 L.1062       284  LOAD_FAST                'self'
              286  LOAD_METHOD              send_error

 L.1063       288  LOAD_GLOBAL              HTTPStatus
              290  LOAD_ATTR                FORBIDDEN

 L.1064       292  LOAD_STR                 'CGI script is not a plain file (%r)'
              294  LOAD_FAST                'scriptname'
              296  BINARY_MODULO    
              298  CALL_METHOD_2         2  '2 positional arguments'
              300  POP_TOP          

 L.1065       302  LOAD_CONST               None
              304  RETURN_VALUE     
            306_0  COME_FROM           280  '280'

 L.1066       306  LOAD_FAST                'self'
              308  LOAD_METHOD              is_python
              310  LOAD_FAST                'scriptname'
              312  CALL_METHOD_1         1  '1 positional argument'
              314  STORE_FAST               'ispy'

 L.1067       316  LOAD_FAST                'self'
              318  LOAD_ATTR                have_fork
          320_322  POP_JUMP_IF_TRUE    330  'to 330'
              324  LOAD_FAST                'ispy'
          326_328  POP_JUMP_IF_TRUE    364  'to 364'
            330_0  COME_FROM           320  '320'

 L.1068       330  LOAD_FAST                'self'
              332  LOAD_METHOD              is_executable
              334  LOAD_FAST                'scriptfile'
              336  CALL_METHOD_1         1  '1 positional argument'
          338_340  POP_JUMP_IF_TRUE    364  'to 364'

 L.1069       342  LOAD_FAST                'self'
              344  LOAD_METHOD              send_error

 L.1070       346  LOAD_GLOBAL              HTTPStatus
              348  LOAD_ATTR                FORBIDDEN

 L.1071       350  LOAD_STR                 'CGI script is not executable (%r)'
              352  LOAD_FAST                'scriptname'
              354  BINARY_MODULO    
              356  CALL_METHOD_2         2  '2 positional arguments'
              358  POP_TOP          

 L.1072       360  LOAD_CONST               None
              362  RETURN_VALUE     
            364_0  COME_FROM           338  '338'
            364_1  COME_FROM           326  '326'

 L.1076       364  LOAD_GLOBAL              copy
              366  LOAD_METHOD              deepcopy
              368  LOAD_GLOBAL              os
              370  LOAD_ATTR                environ
              372  CALL_METHOD_1         1  '1 positional argument'
              374  STORE_FAST               'env'

 L.1077       376  LOAD_FAST                'self'
              378  LOAD_METHOD              version_string
              380  CALL_METHOD_0         0  '0 positional arguments'
              382  LOAD_FAST                'env'
              384  LOAD_STR                 'SERVER_SOFTWARE'
              386  STORE_SUBSCR     

 L.1078       388  LOAD_FAST                'self'
              390  LOAD_ATTR                server
              392  LOAD_ATTR                server_name
              394  LOAD_FAST                'env'
              396  LOAD_STR                 'SERVER_NAME'
              398  STORE_SUBSCR     

 L.1079       400  LOAD_STR                 'CGI/1.1'
              402  LOAD_FAST                'env'
              404  LOAD_STR                 'GATEWAY_INTERFACE'
              406  STORE_SUBSCR     

 L.1080       408  LOAD_FAST                'self'
              410  LOAD_ATTR                protocol_version
              412  LOAD_FAST                'env'
              414  LOAD_STR                 'SERVER_PROTOCOL'
              416  STORE_SUBSCR     

 L.1081       418  LOAD_GLOBAL              str
              420  LOAD_FAST                'self'
              422  LOAD_ATTR                server
              424  LOAD_ATTR                server_port
              426  CALL_FUNCTION_1       1  '1 positional argument'
              428  LOAD_FAST                'env'
              430  LOAD_STR                 'SERVER_PORT'
              432  STORE_SUBSCR     

 L.1082       434  LOAD_FAST                'self'
              436  LOAD_ATTR                command
              438  LOAD_FAST                'env'
              440  LOAD_STR                 'REQUEST_METHOD'
              442  STORE_SUBSCR     

 L.1083       444  LOAD_GLOBAL              urllib
              446  LOAD_ATTR                parse
              448  LOAD_METHOD              unquote
              450  LOAD_FAST                'rest'
              452  CALL_METHOD_1         1  '1 positional argument'
              454  STORE_FAST               'uqrest'

 L.1084       456  LOAD_FAST                'uqrest'
              458  LOAD_FAST                'env'
              460  LOAD_STR                 'PATH_INFO'
              462  STORE_SUBSCR     

 L.1085       464  LOAD_FAST                'self'
              466  LOAD_METHOD              translate_path
              468  LOAD_FAST                'uqrest'
              470  CALL_METHOD_1         1  '1 positional argument'
              472  LOAD_FAST                'env'
              474  LOAD_STR                 'PATH_TRANSLATED'
              476  STORE_SUBSCR     

 L.1086       478  LOAD_FAST                'scriptname'
              480  LOAD_FAST                'env'
              482  LOAD_STR                 'SCRIPT_NAME'
              484  STORE_SUBSCR     

 L.1087       486  LOAD_FAST                'query'
          488_490  POP_JUMP_IF_FALSE   500  'to 500'

 L.1088       492  LOAD_FAST                'query'
              494  LOAD_FAST                'env'
              496  LOAD_STR                 'QUERY_STRING'
              498  STORE_SUBSCR     
            500_0  COME_FROM           488  '488'

 L.1089       500  LOAD_FAST                'self'
              502  LOAD_ATTR                client_address
              504  LOAD_CONST               0
              506  BINARY_SUBSCR    
              508  LOAD_FAST                'env'
              510  LOAD_STR                 'REMOTE_ADDR'
              512  STORE_SUBSCR     

 L.1090       514  LOAD_FAST                'self'
              516  LOAD_ATTR                headers
              518  LOAD_METHOD              get
              520  LOAD_STR                 'authorization'
              522  CALL_METHOD_1         1  '1 positional argument'
              524  STORE_FAST               'authorization'

 L.1091       526  LOAD_FAST                'authorization'
          528_530  POP_JUMP_IF_FALSE   700  'to 700'

 L.1092       532  LOAD_FAST                'authorization'
              534  LOAD_METHOD              split
              536  CALL_METHOD_0         0  '0 positional arguments'
              538  STORE_FAST               'authorization'

 L.1093       540  LOAD_GLOBAL              len
              542  LOAD_FAST                'authorization'
              544  CALL_FUNCTION_1       1  '1 positional argument'
              546  LOAD_CONST               2
              548  COMPARE_OP               ==
          550_552  POP_JUMP_IF_FALSE   700  'to 700'

 L.1094       554  LOAD_CONST               0
              556  LOAD_CONST               None
              558  IMPORT_NAME              base64
              560  STORE_FAST               'base64'
              562  LOAD_CONST               0
              564  LOAD_CONST               None
              566  IMPORT_NAME              binascii
              568  STORE_FAST               'binascii'

 L.1095       570  LOAD_FAST                'authorization'
              572  LOAD_CONST               0
              574  BINARY_SUBSCR    
              576  LOAD_FAST                'env'
              578  LOAD_STR                 'AUTH_TYPE'
              580  STORE_SUBSCR     

 L.1096       582  LOAD_FAST                'authorization'
              584  LOAD_CONST               0
              586  BINARY_SUBSCR    
              588  LOAD_METHOD              lower
              590  CALL_METHOD_0         0  '0 positional arguments'
              592  LOAD_STR                 'basic'
              594  COMPARE_OP               ==
          596_598  POP_JUMP_IF_FALSE   700  'to 700'

 L.1097       600  SETUP_EXCEPT        636  'to 636'

 L.1098       602  LOAD_FAST                'authorization'
              604  LOAD_CONST               1
              606  BINARY_SUBSCR    
              608  LOAD_METHOD              encode
              610  LOAD_STR                 'ascii'
              612  CALL_METHOD_1         1  '1 positional argument'
              614  STORE_FAST               'authorization'

 L.1099       616  LOAD_FAST                'base64'
              618  LOAD_METHOD              decodebytes
              620  LOAD_FAST                'authorization'
              622  CALL_METHOD_1         1  '1 positional argument'
              624  LOAD_METHOD              decode

 L.1100       626  LOAD_STR                 'ascii'
              628  CALL_METHOD_1         1  '1 positional argument'
              630  STORE_FAST               'authorization'
              632  POP_BLOCK        
              634  JUMP_FORWARD        664  'to 664'
            636_0  COME_FROM_EXCEPT    600  '600'

 L.1101       636  DUP_TOP          
              638  LOAD_FAST                'binascii'
              640  LOAD_ATTR                Error
              642  LOAD_GLOBAL              UnicodeError
              644  BUILD_TUPLE_2         2 
              646  COMPARE_OP               exception-match
          648_650  POP_JUMP_IF_FALSE   662  'to 662'
              652  POP_TOP          
              654  POP_TOP          
              656  POP_TOP          

 L.1102       658  POP_EXCEPT       
              660  JUMP_FORWARD        700  'to 700'
            662_0  COME_FROM           648  '648'
              662  END_FINALLY      
            664_0  COME_FROM           634  '634'

 L.1104       664  LOAD_FAST                'authorization'
              666  LOAD_METHOD              split
              668  LOAD_STR                 ':'
              670  CALL_METHOD_1         1  '1 positional argument'
              672  STORE_FAST               'authorization'

 L.1105       674  LOAD_GLOBAL              len
              676  LOAD_FAST                'authorization'
              678  CALL_FUNCTION_1       1  '1 positional argument'
              680  LOAD_CONST               2
              682  COMPARE_OP               ==
          684_686  POP_JUMP_IF_FALSE   700  'to 700'

 L.1106       688  LOAD_FAST                'authorization'
              690  LOAD_CONST               0
              692  BINARY_SUBSCR    
              694  LOAD_FAST                'env'
              696  LOAD_STR                 'REMOTE_USER'
              698  STORE_SUBSCR     
            700_0  COME_FROM           684  '684'
            700_1  COME_FROM           660  '660'
            700_2  COME_FROM           596  '596'
            700_3  COME_FROM           550  '550'
            700_4  COME_FROM           528  '528'

 L.1108       700  LOAD_FAST                'self'
              702  LOAD_ATTR                headers
              704  LOAD_METHOD              get
              706  LOAD_STR                 'content-type'
              708  CALL_METHOD_1         1  '1 positional argument'
              710  LOAD_CONST               None
              712  COMPARE_OP               is
          714_716  POP_JUMP_IF_FALSE   734  'to 734'

 L.1109       718  LOAD_FAST                'self'
              720  LOAD_ATTR                headers
              722  LOAD_METHOD              get_content_type
              724  CALL_METHOD_0         0  '0 positional arguments'
              726  LOAD_FAST                'env'
              728  LOAD_STR                 'CONTENT_TYPE'
              730  STORE_SUBSCR     
              732  JUMP_FORWARD        748  'to 748'
            734_0  COME_FROM           714  '714'

 L.1111       734  LOAD_FAST                'self'
              736  LOAD_ATTR                headers
              738  LOAD_STR                 'content-type'
              740  BINARY_SUBSCR    
              742  LOAD_FAST                'env'
              744  LOAD_STR                 'CONTENT_TYPE'
              746  STORE_SUBSCR     
            748_0  COME_FROM           732  '732'

 L.1112       748  LOAD_FAST                'self'
              750  LOAD_ATTR                headers
              752  LOAD_METHOD              get
              754  LOAD_STR                 'content-length'
              756  CALL_METHOD_1         1  '1 positional argument'
              758  STORE_FAST               'length'

 L.1113       760  LOAD_FAST                'length'
          762_764  POP_JUMP_IF_FALSE   774  'to 774'

 L.1114       766  LOAD_FAST                'length'
              768  LOAD_FAST                'env'
              770  LOAD_STR                 'CONTENT_LENGTH'
              772  STORE_SUBSCR     
            774_0  COME_FROM           762  '762'

 L.1115       774  LOAD_FAST                'self'
              776  LOAD_ATTR                headers
              778  LOAD_METHOD              get
              780  LOAD_STR                 'referer'
              782  CALL_METHOD_1         1  '1 positional argument'
              784  STORE_FAST               'referer'

 L.1116       786  LOAD_FAST                'referer'
          788_790  POP_JUMP_IF_FALSE   800  'to 800'

 L.1117       792  LOAD_FAST                'referer'
              794  LOAD_FAST                'env'
              796  LOAD_STR                 'HTTP_REFERER'
              798  STORE_SUBSCR     
            800_0  COME_FROM           788  '788'

 L.1118       800  BUILD_LIST_0          0 
              802  STORE_FAST               'accept'

 L.1119       804  SETUP_LOOP          884  'to 884'
              806  LOAD_FAST                'self'
              808  LOAD_ATTR                headers
              810  LOAD_METHOD              getallmatchingheaders
              812  LOAD_STR                 'accept'
              814  CALL_METHOD_1         1  '1 positional argument'
              816  GET_ITER         
              818  FOR_ITER            882  'to 882'
              820  STORE_FAST               'line'

 L.1120       822  LOAD_FAST                'line'
              824  LOAD_CONST               None
              826  LOAD_CONST               1
              828  BUILD_SLICE_2         2 
              830  BINARY_SUBSCR    
              832  LOAD_STR                 '\t\n\r '
              834  COMPARE_OP               in
          836_838  POP_JUMP_IF_FALSE   856  'to 856'

 L.1121       840  LOAD_FAST                'accept'
              842  LOAD_METHOD              append
              844  LOAD_FAST                'line'
              846  LOAD_METHOD              strip
              848  CALL_METHOD_0         0  '0 positional arguments'
              850  CALL_METHOD_1         1  '1 positional argument'
              852  POP_TOP          
              854  JUMP_BACK           818  'to 818'
            856_0  COME_FROM           836  '836'

 L.1123       856  LOAD_FAST                'accept'
              858  LOAD_FAST                'line'
              860  LOAD_CONST               7
              862  LOAD_CONST               None
              864  BUILD_SLICE_2         2 
              866  BINARY_SUBSCR    
              868  LOAD_METHOD              split
              870  LOAD_STR                 ','
              872  CALL_METHOD_1         1  '1 positional argument'
              874  BINARY_ADD       
              876  STORE_FAST               'accept'
          878_880  JUMP_BACK           818  'to 818'
              882  POP_BLOCK        
            884_0  COME_FROM_LOOP      804  '804'

 L.1124       884  LOAD_STR                 ','
              886  LOAD_METHOD              join
              888  LOAD_FAST                'accept'
              890  CALL_METHOD_1         1  '1 positional argument'
              892  LOAD_FAST                'env'
              894  LOAD_STR                 'HTTP_ACCEPT'
              896  STORE_SUBSCR     

 L.1125       898  LOAD_FAST                'self'
              900  LOAD_ATTR                headers
              902  LOAD_METHOD              get
              904  LOAD_STR                 'user-agent'
              906  CALL_METHOD_1         1  '1 positional argument'
              908  STORE_FAST               'ua'

 L.1126       910  LOAD_FAST                'ua'
          912_914  POP_JUMP_IF_FALSE   924  'to 924'

 L.1127       916  LOAD_FAST                'ua'
              918  LOAD_FAST                'env'
              920  LOAD_STR                 'HTTP_USER_AGENT'
              922  STORE_SUBSCR     
            924_0  COME_FROM           912  '912'

 L.1128       924  LOAD_GLOBAL              filter
              926  LOAD_CONST               None
              928  LOAD_FAST                'self'
              930  LOAD_ATTR                headers
              932  LOAD_METHOD              get_all
              934  LOAD_STR                 'cookie'
              936  BUILD_LIST_0          0 
              938  CALL_METHOD_2         2  '2 positional arguments'
              940  CALL_FUNCTION_2       2  '2 positional arguments'
              942  STORE_FAST               'co'

 L.1129       944  LOAD_STR                 ', '
              946  LOAD_METHOD              join
              948  LOAD_FAST                'co'
              950  CALL_METHOD_1         1  '1 positional argument'
              952  STORE_FAST               'cookie_str'

 L.1130       954  LOAD_FAST                'cookie_str'
          956_958  POP_JUMP_IF_FALSE   968  'to 968'

 L.1131       960  LOAD_FAST                'cookie_str'
              962  LOAD_FAST                'env'
              964  LOAD_STR                 'HTTP_COOKIE'
              966  STORE_SUBSCR     
            968_0  COME_FROM           956  '956'

 L.1135       968  SETUP_LOOP          996  'to 996'
              970  LOAD_CONST               ('QUERY_STRING', 'REMOTE_HOST', 'CONTENT_LENGTH', 'HTTP_USER_AGENT', 'HTTP_COOKIE', 'HTTP_REFERER')
              972  GET_ITER         
              974  FOR_ITER            994  'to 994'
              976  STORE_FAST               'k'

 L.1137       978  LOAD_FAST                'env'
              980  LOAD_METHOD              setdefault
              982  LOAD_FAST                'k'
              984  LOAD_STR                 ''
              986  CALL_METHOD_2         2  '2 positional arguments'
              988  POP_TOP          
          990_992  JUMP_BACK           974  'to 974'
              994  POP_BLOCK        
            996_0  COME_FROM_LOOP      968  '968'

 L.1139       996  LOAD_FAST                'self'
              998  LOAD_METHOD              send_response
             1000  LOAD_GLOBAL              HTTPStatus
             1002  LOAD_ATTR                OK
             1004  LOAD_STR                 'Script output follows'
             1006  CALL_METHOD_2         2  '2 positional arguments'
             1008  POP_TOP          

 L.1140      1010  LOAD_FAST                'self'
             1012  LOAD_METHOD              flush_headers
             1014  CALL_METHOD_0         0  '0 positional arguments'
             1016  POP_TOP          

 L.1142      1018  LOAD_FAST                'query'
             1020  LOAD_METHOD              replace
             1022  LOAD_STR                 '+'
             1024  LOAD_STR                 ' '
             1026  CALL_METHOD_2         2  '2 positional arguments'
             1028  STORE_FAST               'decoded_query'

 L.1144      1030  LOAD_FAST                'self'
             1032  LOAD_ATTR                have_fork
         1034_1036  POP_JUMP_IF_FALSE  1324  'to 1324'

 L.1146      1038  LOAD_FAST                'script'
             1040  BUILD_LIST_1          1 
             1042  STORE_FAST               'args'

 L.1147      1044  LOAD_STR                 '='
             1046  LOAD_FAST                'decoded_query'
             1048  COMPARE_OP               not-in
         1050_1052  POP_JUMP_IF_FALSE  1064  'to 1064'

 L.1148      1054  LOAD_FAST                'args'
             1056  LOAD_METHOD              append
             1058  LOAD_FAST                'decoded_query'
             1060  CALL_METHOD_1         1  '1 positional argument'
             1062  POP_TOP          
           1064_0  COME_FROM          1050  '1050'

 L.1149      1064  LOAD_GLOBAL              nobody_uid
             1066  CALL_FUNCTION_0       0  '0 positional arguments'
             1068  STORE_FAST               'nobody'

 L.1150      1070  LOAD_FAST                'self'
             1072  LOAD_ATTR                wfile
             1074  LOAD_METHOD              flush
             1076  CALL_METHOD_0         0  '0 positional arguments'
             1078  POP_TOP          

 L.1151      1080  LOAD_GLOBAL              os
             1082  LOAD_METHOD              fork
             1084  CALL_METHOD_0         0  '0 positional arguments'
             1086  STORE_FAST               'pid'

 L.1152      1088  LOAD_FAST                'pid'
             1090  LOAD_CONST               0
             1092  COMPARE_OP               !=
         1094_1096  POP_JUMP_IF_FALSE  1186  'to 1186'

 L.1154      1098  LOAD_GLOBAL              os
             1100  LOAD_METHOD              waitpid
             1102  LOAD_FAST                'pid'
             1104  LOAD_CONST               0
             1106  CALL_METHOD_2         2  '2 positional arguments'
             1108  UNPACK_SEQUENCE_2     2 
             1110  STORE_FAST               'pid'
             1112  STORE_FAST               'sts'

 L.1156      1114  SETUP_LOOP         1164  'to 1164'
           1116_0  COME_FROM          1152  '1152'
             1116  LOAD_GLOBAL              select
             1118  LOAD_METHOD              select
             1120  LOAD_FAST                'self'
             1122  LOAD_ATTR                rfile
             1124  BUILD_LIST_1          1 
             1126  BUILD_LIST_0          0 
             1128  BUILD_LIST_0          0 
             1130  LOAD_CONST               0
             1132  CALL_METHOD_4         4  '4 positional arguments'
             1134  LOAD_CONST               0
             1136  BINARY_SUBSCR    
         1138_1140  POP_JUMP_IF_FALSE  1162  'to 1162'

 L.1157      1142  LOAD_FAST                'self'
             1144  LOAD_ATTR                rfile
             1146  LOAD_METHOD              read
             1148  LOAD_CONST               1
             1150  CALL_METHOD_1         1  '1 positional argument'
         1152_1154  POP_JUMP_IF_TRUE   1116  'to 1116'

 L.1158      1156  BREAK_LOOP       
         1158_1160  JUMP_BACK          1116  'to 1116'
           1162_0  COME_FROM          1138  '1138'
             1162  POP_BLOCK        
           1164_0  COME_FROM_LOOP     1114  '1114'

 L.1159      1164  LOAD_FAST                'sts'
         1166_1168  POP_JUMP_IF_FALSE  1182  'to 1182'

 L.1160      1170  LOAD_FAST                'self'
             1172  LOAD_METHOD              log_error
             1174  LOAD_STR                 'CGI script exit status %#x'
             1176  LOAD_FAST                'sts'
             1178  CALL_METHOD_2         2  '2 positional arguments'
             1180  POP_TOP          
           1182_0  COME_FROM          1166  '1166'

 L.1161      1182  LOAD_CONST               None
             1184  RETURN_VALUE     
           1186_0  COME_FROM          1094  '1094'

 L.1163      1186  SETUP_EXCEPT       1280  'to 1280'

 L.1164      1188  SETUP_EXCEPT       1204  'to 1204'

 L.1165      1190  LOAD_GLOBAL              os
             1192  LOAD_METHOD              setuid
             1194  LOAD_FAST                'nobody'
             1196  CALL_METHOD_1         1  '1 positional argument'
             1198  POP_TOP          
             1200  POP_BLOCK        
             1202  JUMP_FORWARD       1226  'to 1226'
           1204_0  COME_FROM_EXCEPT   1188  '1188'

 L.1166      1204  DUP_TOP          
             1206  LOAD_GLOBAL              OSError
             1208  COMPARE_OP               exception-match
         1210_1212  POP_JUMP_IF_FALSE  1224  'to 1224'
             1214  POP_TOP          
             1216  POP_TOP          
             1218  POP_TOP          

 L.1167      1220  POP_EXCEPT       
             1222  JUMP_FORWARD       1226  'to 1226'
           1224_0  COME_FROM          1210  '1210'
             1224  END_FINALLY      
           1226_0  COME_FROM          1222  '1222'
           1226_1  COME_FROM          1202  '1202'

 L.1168      1226  LOAD_GLOBAL              os
             1228  LOAD_METHOD              dup2
             1230  LOAD_FAST                'self'
             1232  LOAD_ATTR                rfile
             1234  LOAD_METHOD              fileno
             1236  CALL_METHOD_0         0  '0 positional arguments'
             1238  LOAD_CONST               0
             1240  CALL_METHOD_2         2  '2 positional arguments'
             1242  POP_TOP          

 L.1169      1244  LOAD_GLOBAL              os
             1246  LOAD_METHOD              dup2
             1248  LOAD_FAST                'self'
             1250  LOAD_ATTR                wfile
             1252  LOAD_METHOD              fileno
             1254  CALL_METHOD_0         0  '0 positional arguments'
             1256  LOAD_CONST               1
             1258  CALL_METHOD_2         2  '2 positional arguments'
             1260  POP_TOP          

 L.1170      1262  LOAD_GLOBAL              os
             1264  LOAD_METHOD              execve
             1266  LOAD_FAST                'scriptfile'
             1268  LOAD_FAST                'args'
             1270  LOAD_FAST                'env'
             1272  CALL_METHOD_3         3  '3 positional arguments'
             1274  POP_TOP          
             1276  POP_BLOCK        
             1278  JUMP_FORWARD       1714  'to 1714'
           1280_0  COME_FROM_EXCEPT   1186  '1186'

 L.1171      1280  POP_TOP          
             1282  POP_TOP          
             1284  POP_TOP          

 L.1172      1286  LOAD_FAST                'self'
             1288  LOAD_ATTR                server
             1290  LOAD_METHOD              handle_error
             1292  LOAD_FAST                'self'
             1294  LOAD_ATTR                request
             1296  LOAD_FAST                'self'
             1298  LOAD_ATTR                client_address
             1300  CALL_METHOD_2         2  '2 positional arguments'
             1302  POP_TOP          

 L.1173      1304  LOAD_GLOBAL              os
             1306  LOAD_METHOD              _exit
             1308  LOAD_CONST               127
             1310  CALL_METHOD_1         1  '1 positional argument'
             1312  POP_TOP          
             1314  POP_EXCEPT       
             1316  JUMP_FORWARD       1714  'to 1714'
             1318  END_FINALLY      
         1320_1322  JUMP_FORWARD       1714  'to 1714'
           1324_0  COME_FROM          1034  '1034'

 L.1177      1324  LOAD_CONST               0
             1326  LOAD_CONST               None
             1328  IMPORT_NAME              subprocess
             1330  STORE_FAST               'subprocess'

 L.1178      1332  LOAD_FAST                'scriptfile'
             1334  BUILD_LIST_1          1 
             1336  STORE_FAST               'cmdline'

 L.1179      1338  LOAD_FAST                'self'
             1340  LOAD_METHOD              is_python
             1342  LOAD_FAST                'scriptfile'
             1344  CALL_METHOD_1         1  '1 positional argument'
         1346_1348  POP_JUMP_IF_FALSE  1408  'to 1408'

 L.1180      1350  LOAD_GLOBAL              sys
             1352  LOAD_ATTR                executable
             1354  STORE_FAST               'interp'

 L.1181      1356  LOAD_FAST                'interp'
             1358  LOAD_METHOD              lower
             1360  CALL_METHOD_0         0  '0 positional arguments'
             1362  LOAD_METHOD              endswith
             1364  LOAD_STR                 'w.exe'
             1366  CALL_METHOD_1         1  '1 positional argument'
         1368_1370  POP_JUMP_IF_FALSE  1396  'to 1396'

 L.1183      1372  LOAD_FAST                'interp'
             1374  LOAD_CONST               None
             1376  LOAD_CONST               -5
             1378  BUILD_SLICE_2         2 
             1380  BINARY_SUBSCR    
             1382  LOAD_FAST                'interp'
             1384  LOAD_CONST               -4
             1386  LOAD_CONST               None
             1388  BUILD_SLICE_2         2 
             1390  BINARY_SUBSCR    
             1392  BINARY_ADD       
             1394  STORE_FAST               'interp'
           1396_0  COME_FROM          1368  '1368'

 L.1184      1396  LOAD_FAST                'interp'
             1398  LOAD_STR                 '-u'
             1400  BUILD_LIST_2          2 
             1402  LOAD_FAST                'cmdline'
             1404  BINARY_ADD       
             1406  STORE_FAST               'cmdline'
           1408_0  COME_FROM          1346  '1346'

 L.1185      1408  LOAD_STR                 '='
             1410  LOAD_FAST                'query'
             1412  COMPARE_OP               not-in
         1414_1416  POP_JUMP_IF_FALSE  1428  'to 1428'

 L.1186      1418  LOAD_FAST                'cmdline'
             1420  LOAD_METHOD              append
             1422  LOAD_FAST                'query'
             1424  CALL_METHOD_1         1  '1 positional argument'
             1426  POP_TOP          
           1428_0  COME_FROM          1414  '1414'

 L.1187      1428  LOAD_FAST                'self'
             1430  LOAD_METHOD              log_message
             1432  LOAD_STR                 'command: %s'
             1434  LOAD_FAST                'subprocess'
             1436  LOAD_METHOD              list2cmdline
             1438  LOAD_FAST                'cmdline'
             1440  CALL_METHOD_1         1  '1 positional argument'
             1442  CALL_METHOD_2         2  '2 positional arguments'
             1444  POP_TOP          

 L.1188      1446  SETUP_EXCEPT       1460  'to 1460'

 L.1189      1448  LOAD_GLOBAL              int
             1450  LOAD_FAST                'length'
             1452  CALL_FUNCTION_1       1  '1 positional argument'
             1454  STORE_FAST               'nbytes'
             1456  POP_BLOCK        
             1458  JUMP_FORWARD       1490  'to 1490'
           1460_0  COME_FROM_EXCEPT   1446  '1446'

 L.1190      1460  DUP_TOP          
             1462  LOAD_GLOBAL              TypeError
             1464  LOAD_GLOBAL              ValueError
             1466  BUILD_TUPLE_2         2 
             1468  COMPARE_OP               exception-match
         1470_1472  POP_JUMP_IF_FALSE  1488  'to 1488'
             1474  POP_TOP          
             1476  POP_TOP          
             1478  POP_TOP          

 L.1191      1480  LOAD_CONST               0
             1482  STORE_FAST               'nbytes'
             1484  POP_EXCEPT       
             1486  JUMP_FORWARD       1490  'to 1490'
           1488_0  COME_FROM          1470  '1470'
             1488  END_FINALLY      
           1490_0  COME_FROM          1486  '1486'
           1490_1  COME_FROM          1458  '1458'

 L.1192      1490  LOAD_FAST                'subprocess'
             1492  LOAD_ATTR                Popen
             1494  LOAD_FAST                'cmdline'

 L.1193      1496  LOAD_FAST                'subprocess'
             1498  LOAD_ATTR                PIPE

 L.1194      1500  LOAD_FAST                'subprocess'
             1502  LOAD_ATTR                PIPE

 L.1195      1504  LOAD_FAST                'subprocess'
             1506  LOAD_ATTR                PIPE

 L.1196      1508  LOAD_FAST                'env'
             1510  LOAD_CONST               ('stdin', 'stdout', 'stderr', 'env')
             1512  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
             1514  STORE_FAST               'p'

 L.1198      1516  LOAD_FAST                'self'
             1518  LOAD_ATTR                command
             1520  LOAD_METHOD              lower
             1522  CALL_METHOD_0         0  '0 positional arguments'
             1524  LOAD_STR                 'post'
             1526  COMPARE_OP               ==
         1528_1530  POP_JUMP_IF_FALSE  1556  'to 1556'
             1532  LOAD_FAST                'nbytes'
             1534  LOAD_CONST               0
             1536  COMPARE_OP               >
         1538_1540  POP_JUMP_IF_FALSE  1556  'to 1556'

 L.1199      1542  LOAD_FAST                'self'
             1544  LOAD_ATTR                rfile
             1546  LOAD_METHOD              read
             1548  LOAD_FAST                'nbytes'
             1550  CALL_METHOD_1         1  '1 positional argument'
             1552  STORE_FAST               'data'
             1554  JUMP_FORWARD       1560  'to 1560'
           1556_0  COME_FROM          1538  '1538'
           1556_1  COME_FROM          1528  '1528'

 L.1201      1556  LOAD_CONST               None
             1558  STORE_FAST               'data'
           1560_0  COME_FROM          1554  '1554'

 L.1203      1560  SETUP_LOOP         1614  'to 1614'
           1562_0  COME_FROM          1602  '1602'
             1562  LOAD_GLOBAL              select
             1564  LOAD_METHOD              select
             1566  LOAD_FAST                'self'
             1568  LOAD_ATTR                rfile
             1570  LOAD_ATTR                _sock
             1572  BUILD_LIST_1          1 
             1574  BUILD_LIST_0          0 
             1576  BUILD_LIST_0          0 
             1578  LOAD_CONST               0
             1580  CALL_METHOD_4         4  '4 positional arguments'
             1582  LOAD_CONST               0
             1584  BINARY_SUBSCR    
         1586_1588  POP_JUMP_IF_FALSE  1612  'to 1612'

 L.1204      1590  LOAD_FAST                'self'
             1592  LOAD_ATTR                rfile
             1594  LOAD_ATTR                _sock
             1596  LOAD_METHOD              recv
             1598  LOAD_CONST               1
             1600  CALL_METHOD_1         1  '1 positional argument'
         1602_1604  POP_JUMP_IF_TRUE   1562  'to 1562'

 L.1205      1606  BREAK_LOOP       
         1608_1610  JUMP_BACK          1562  'to 1562'
           1612_0  COME_FROM          1586  '1586'
             1612  POP_BLOCK        
           1614_0  COME_FROM_LOOP     1560  '1560'

 L.1206      1614  LOAD_FAST                'p'
             1616  LOAD_METHOD              communicate
             1618  LOAD_FAST                'data'
             1620  CALL_METHOD_1         1  '1 positional argument'
             1622  UNPACK_SEQUENCE_2     2 
             1624  STORE_FAST               'stdout'
             1626  STORE_FAST               'stderr'

 L.1207      1628  LOAD_FAST                'self'
             1630  LOAD_ATTR                wfile
             1632  LOAD_METHOD              write
             1634  LOAD_FAST                'stdout'
             1636  CALL_METHOD_1         1  '1 positional argument'
             1638  POP_TOP          

 L.1208      1640  LOAD_FAST                'stderr'
         1642_1644  POP_JUMP_IF_FALSE  1658  'to 1658'

 L.1209      1646  LOAD_FAST                'self'
             1648  LOAD_METHOD              log_error
             1650  LOAD_STR                 '%s'
             1652  LOAD_FAST                'stderr'
             1654  CALL_METHOD_2         2  '2 positional arguments'
             1656  POP_TOP          
           1658_0  COME_FROM          1642  '1642'

 L.1210      1658  LOAD_FAST                'p'
             1660  LOAD_ATTR                stderr
             1662  LOAD_METHOD              close
             1664  CALL_METHOD_0         0  '0 positional arguments'
             1666  POP_TOP          

 L.1211      1668  LOAD_FAST                'p'
           1670_0  COME_FROM          1278  '1278'
             1670  LOAD_ATTR                stdout
             1672  LOAD_METHOD              close
             1674  CALL_METHOD_0         0  '0 positional arguments'
             1676  POP_TOP          

 L.1212      1678  LOAD_FAST                'p'
             1680  LOAD_ATTR                returncode
             1682  STORE_FAST               'status'

 L.1213      1684  LOAD_FAST                'status'
         1686_1688  POP_JUMP_IF_FALSE  1704  'to 1704'

 L.1214      1690  LOAD_FAST                'self'
             1692  LOAD_METHOD              log_error
             1694  LOAD_STR                 'CGI script exit status %#x'
             1696  LOAD_FAST                'status'
             1698  CALL_METHOD_2         2  '2 positional arguments'
             1700  POP_TOP          
             1702  JUMP_FORWARD       1714  'to 1714'
           1704_0  COME_FROM          1686  '1686'

 L.1216      1704  LOAD_FAST                'self'
             1706  LOAD_METHOD              log_message
           1708_0  COME_FROM          1316  '1316'
             1708  LOAD_STR                 'CGI script exited OK'
             1710  CALL_METHOD_1         1  '1 positional argument'
             1712  POP_TOP          
           1714_0  COME_FROM          1702  '1702'
           1714_1  COME_FROM          1320  '1320'

Parse error at or near `COME_FROM' instruction at offset 1670_0


def test(HandlerClass=BaseHTTPRequestHandler, ServerClass=ThreadingHTTPServer, protocol='HTTP/1.0', port=8000, bind=''):
    server_address = (
     bind, port)
    HandlerClass.protocol_version = protocol
    with ServerClass(server_address, HandlerClass) as (httpd):
        sa = httpd.socket.getsockname()
        serve_message = 'Serving HTTP on {host} port {port} (http://{host}:{port}/) ...'
        print(serve_message.format(host=(sa[0]), port=(sa[1])))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cgi', action='store_true', help='Run as CGI Server')
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS', help='Specify alternate bind address [default: all interfaces]')
    parser.add_argument('--directory', '-d', default=(os.getcwd()), help='Specify alternative directory [default:current directory]')
    parser.add_argument('port', action='store', default=8000,
      type=int,
      nargs='?',
      help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    if args.cgi:
        handler_class = CGIHTTPRequestHandler
    else:
        handler_class = partial(SimpleHTTPRequestHandler, directory=(args.directory))
    test(HandlerClass=handler_class, port=(args.port), bind=(args.bind))