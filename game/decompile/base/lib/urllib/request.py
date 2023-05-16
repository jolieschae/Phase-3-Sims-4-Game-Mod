# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\urllib\request.py
# Compiled at: 2018-08-07 18:29:17
# Size of source mod 2**32: 102724 bytes
import base64, bisect, email, hashlib, http.client, io, os, posixpath, re, socket, string, sys, time, tempfile, contextlib, warnings
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urlparse, urlsplit, urljoin, unwrap, quote, unquote, splittype, splithost, splitport, splituser, splitpasswd, splitattr, splitquery, splitvalue, splittag, to_bytes, unquote_to_bytes, urlunparse
from urllib.response import addinfourl, addclosehook
try:
    import ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True
__all__ = [
 "'Request'", "'OpenerDirector'", "'BaseHandler'", "'HTTPDefaultErrorHandler'", 
 "'HTTPRedirectHandler'", 
 "'HTTPCookieProcessor'", "'ProxyHandler'", 
 "'HTTPPasswordMgr'", "'HTTPPasswordMgrWithDefaultRealm'", 
 "'HTTPPasswordMgrWithPriorAuth'", 
 "'AbstractBasicAuthHandler'", 
 "'HTTPBasicAuthHandler'", "'ProxyBasicAuthHandler'", 
 "'AbstractDigestAuthHandler'", 
 "'HTTPDigestAuthHandler'", "'ProxyDigestAuthHandler'", 
 "'HTTPHandler'", 
 "'FileHandler'", "'FTPHandler'", "'CacheFTPHandler'", 
 "'DataHandler'", 
 "'UnknownHandler'", "'HTTPErrorProcessor'", 
 "'urlopen'", 
 "'install_opener'", "'build_opener'", 
 "'pathname2url'", "'url2pathname'", 
 "'getproxies'", 
 "'urlretrieve'", "'urlcleanup'", "'URLopener'", "'FancyURLopener'"]
__version__ = '%d.%d' % sys.version_info[:2]
_opener = None

def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *, cafile=None, capath=None, cadefault=False, context=None):
    global _opener
    if not cafile:
        if capath or cadefault:
            import warnings
            warnings.warn('cafile, cpath and cadefault are deprecated, use a custom context instead.', DeprecationWarning, 2)
            if context is not None:
                raise ValueError("You can't pass both context and any of cafile, capath, and cadefault")
            if not _have_ssl:
                raise ValueError('SSL support not available')
            context = ssl.create_default_context((ssl.Purpose.SERVER_AUTH), cafile=cafile,
              capath=capath)
            https_handler = HTTPSHandler(context=context)
            opener = build_opener(https_handler)
    elif context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    else:
        if _opener is None:
            _opener = opener = build_opener()
        else:
            opener = _opener
    return opener.open(url, data, timeout)


def install_opener(opener):
    global _opener
    _opener = opener


_url_tempfiles = []

def urlretrieve(url, filename=None, reporthook=None, data=None):
    url_type, path = splittype(url)
    with contextlib.closing(urlopen(url, data)) as (fp):
        headers = fp.info()
        if url_type == 'file':
            if not filename:
                return (
                 os.path.normpath(path), headers)
        elif filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete=False)
            filename = tfp.name
            _url_tempfiles.append(filename)
        with tfp:
            result = (
             filename, headers)
            bs = 8192
            size = -1
            read = 0
            blocknum = 0
            if 'content-length' in headers:
                size = int(headers['Content-Length'])
            if reporthook:
                reporthook(blocknum, bs, size)
            while 1:
                block = fp.read(bs)
                if not block:
                    break
                read += len(block)
                tfp.write(block)
                blocknum += 1
                if reporthook:
                    reporthook(blocknum, bs, size)

    if size >= 0:
        if read < size:
            raise ContentTooShortError('retrieval incomplete: got only %i out of %i bytes' % (
             read, size), result)
    return result


def urlcleanup():
    global _opener
    for temp_file in _url_tempfiles:
        try:
            os.unlink(temp_file)
        except OSError:
            pass

    del _url_tempfiles[:]
    if _opener:
        _opener = None


_cut_port_re = re.compile(':\\d+$', re.ASCII)

def request_host(request):
    url = request.full_url
    host = urlparse(url)[1]
    if host == '':
        host = request.get_header('Host', '')
    host = _cut_port_re.sub('', host, 1)
    return host.lower()


class Request:

    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None):
        self.full_url = url
        self.headers = {}
        self.unredirected_hdrs = {}
        self._data = None
        self.data = data
        self._tunnel_host = None
        for key, value in headers.items():
            self.add_header(key, value)

        if origin_req_host is None:
            origin_req_host = request_host(self)
        self.origin_req_host = origin_req_host
        self.unverifiable = unverifiable
        if method:
            self.method = method

    @property
    def full_url(self):
        if self.fragment:
            return '{}#{}'.format(self._full_url, self.fragment)
        return self._full_url

    @full_url.setter
    def full_url(self, url):
        self._full_url = unwrap(url)
        self._full_url, self.fragment = splittag(self._full_url)
        self._parse()

    @full_url.deleter
    def full_url(self):
        self._full_url = None
        self.fragment = None
        self.selector = ''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if data != self._data:
            self._data = data
            if self.has_header('Content-length'):
                self.remove_header('Content-length')

    @data.deleter
    def data(self):
        self.data = None

    def _parse(self):
        self.type, rest = splittype(self._full_url)
        if self.type is None:
            raise ValueError('unknown url type: %r' % self.full_url)
        self.host, self.selector = splithost(rest)
        if self.host:
            self.host = unquote(self.host)

    def get_method(self):
        default_method = 'POST' if self.data is not None else 'GET'
        return getattr(self, 'method', default_method)

    def get_full_url(self):
        return self.full_url

    def set_proxy(self, host, type):
        if self.type == 'https':
            self._tunnel_host = self._tunnel_host or self.host
        else:
            self.type = type
            self.selector = self.full_url
        self.host = host

    def has_proxy(self):
        return self.selector == self.full_url

    def add_header(self, key, val):
        self.headers[key.capitalize()] = val

    def add_unredirected_header(self, key, val):
        self.unredirected_hdrs[key.capitalize()] = val

    def has_header(self, header_name):
        return header_name in self.headers or header_name in self.unredirected_hdrs

    def get_header(self, header_name, default=None):
        return self.headers.get(header_name, self.unredirected_hdrs.get(header_name, default))

    def remove_header(self, header_name):
        self.headers.pop(header_name, None)
        self.unredirected_hdrs.pop(header_name, None)

    def header_items(self):
        hdrs = self.unredirected_hdrs.copy()
        hdrs.update(self.headers)
        return list(hdrs.items())


class OpenerDirector:

    def __init__(self):
        client_version = 'Python-urllib/%s' % __version__
        self.addheaders = [('User-agent', client_version)]
        self.handlers = []
        self.handle_open = {}
        self.handle_error = {}
        self.process_response = {}
        self.process_request = {}

    def add_handler(self, handler):
        if not hasattr(handler, 'add_parent'):
            raise TypeError('expected BaseHandler instance, got %r' % type(handler))
        added = False
        for meth in dir(handler):
            if meth in ('redirect_request', 'do_open', 'proxy_open'):
                continue
            i = meth.find('_')
            protocol = meth[:i]
            condition = meth[i + 1:]
            if condition.startswith('error'):
                j = condition.find('_') + i + 1
                kind = meth[j + 1:]
                try:
                    kind = int(kind)
                except ValueError:
                    pass

                lookup = self.handle_error.get(protocol, {})
                self.handle_error[protocol] = lookup
            else:
                if condition == 'open':
                    kind = protocol
                    lookup = self.handle_open
                else:
                    if condition == 'response':
                        kind = protocol
                        lookup = self.process_response
                    else:
                        if condition == 'request':
                            kind = protocol
                            lookup = self.process_request
                        else:
                            continue
                        handlers = lookup.setdefault(kind, [])
                        if handlers:
                            bisect.insort(handlers, handler)
                        else:
                            handlers.append(handler)
                        added = True

        if added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)

    def close(self):
        pass

    def _call_chain(self, chain, kind, meth_name, *args):
        handlers = chain.get(kind, ())
        for handler in handlers:
            func = getattr(handler, meth_name)
            result = func(*args)
            if result is not None:
                return result

    def open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if isinstance(fullurl, str):
            req = Request(fullurl, data)
        else:
            req = fullurl
            if data is not None:
                req.data = data
        req.timeout = timeout
        protocol = req.type
        meth_name = protocol + '_request'
        for processor in self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)

        response = self._open(req, data)
        meth_name = protocol + '_response'
        for processor in self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)

        return response

    def _open(self, req, data=None):
        result = self._call_chain(self.handle_open, 'default', 'default_open', req)
        if result:
            return result
        protocol = req.type
        result = self._call_chain(self.handle_open, protocol, protocol + '_open', req)
        if result:
            return result
        return self._call_chain(self.handle_open, 'unknown', 'unknown_open', req)

    def error(self, proto, *args):
        if proto in ('http', 'https'):
            dict = self.handle_error['http']
            proto = args[2]
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        else:
            dict = self.handle_error
            meth_name = proto + '_error'
            http_err = 0
        args = (
         dict, proto, meth_name) + args
        result = (self._call_chain)(*args)
        if result:
            return result
        if http_err:
            args = (
             dict, 'default', 'http_error_default') + orig_args
            return (self._call_chain)(*args)


def build_opener(*handlers):
    opener = OpenerDirector()
    default_classes = ['ProxyHandler', 'UnknownHandler', 'HTTPHandler', 
     'HTTPDefaultErrorHandler', 
     'HTTPRedirectHandler', 
     'FTPHandler', 'FileHandler', 'HTTPErrorProcessor', 
     'DataHandler']
    if hasattr(http.client, 'HTTPSConnection'):
        default_classes.append(HTTPSHandler)
    skip = set()
    for klass in default_classes:
        for check in handlers:
            if isinstance(check, type):
                if issubclass(check, klass):
                    skip.add(klass)
                elif isinstance(check, klass):
                    skip.add(klass)

    for klass in skip:
        default_classes.remove(klass)

    for klass in default_classes:
        opener.add_handler(klass())

    for h in handlers:
        if isinstance(h, type):
            h = h()
        opener.add_handler(h)

    return opener


class BaseHandler:
    handler_order = 500

    def add_parent(self, parent):
        self.parent = parent

    def close(self):
        pass

    def __lt__(self, other):
        if not hasattr(other, 'handler_order'):
            return True
        return self.handler_order < other.handler_order


class HTTPErrorProcessor(BaseHandler):
    handler_order = 1000

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()
        if not 200 <= code < 300:
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response

    https_response = http_response


class HTTPDefaultErrorHandler(BaseHandler):

    def http_error_default(self, req, fp, code, msg, hdrs):
        raise HTTPError(req.full_url, code, msg, hdrs, fp)


class HTTPRedirectHandler(BaseHandler):
    max_repeats = 4
    max_redirections = 10

    def redirect_request--- This code section failed: ---

 L. 669         0  LOAD_FAST                'req'
                2  LOAD_METHOD              get_method
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'm'

 L. 670         8  LOAD_FAST                'code'
               10  LOAD_CONST               (301, 302, 303, 307)
               12  COMPARE_OP               in
               14  POP_JUMP_IF_FALSE    24  'to 24'
               16  LOAD_FAST                'm'
               18  LOAD_CONST               ('GET', 'HEAD')
               20  COMPARE_OP               in
               22  POP_JUMP_IF_TRUE     58  'to 58'
             24_0  COME_FROM            14  '14'

 L. 671        24  LOAD_FAST                'code'
               26  LOAD_CONST               (301, 302, 303)
               28  COMPARE_OP               in
               30  POP_JUMP_IF_FALSE    40  'to 40'
               32  LOAD_FAST                'm'
               34  LOAD_STR                 'POST'
               36  COMPARE_OP               ==
               38  POP_JUMP_IF_TRUE     58  'to 58'
             40_0  COME_FROM            30  '30'

 L. 672        40  LOAD_GLOBAL              HTTPError
               42  LOAD_FAST                'req'
               44  LOAD_ATTR                full_url
               46  LOAD_FAST                'code'
               48  LOAD_FAST                'msg'
               50  LOAD_FAST                'headers'
               52  LOAD_FAST                'fp'
               54  CALL_FUNCTION_5       5  '5 positional arguments'
               56  RAISE_VARARGS_1       1  'exception instance'
             58_0  COME_FROM            38  '38'
             58_1  COME_FROM            22  '22'

 L. 683        58  LOAD_FAST                'newurl'
               60  LOAD_METHOD              replace
               62  LOAD_STR                 ' '
               64  LOAD_STR                 '%20'
               66  CALL_METHOD_2         2  '2 positional arguments'
               68  STORE_FAST               'newurl'

 L. 685        70  LOAD_CONST               ('content-length', 'content-type')
               72  STORE_DEREF              'CONTENT_HEADERS'

 L. 686        74  LOAD_CLOSURE             'CONTENT_HEADERS'
               76  BUILD_TUPLE_1         1 
               78  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               80  LOAD_STR                 'HTTPRedirectHandler.redirect_request.<locals>.<dictcomp>'
               82  MAKE_FUNCTION_8          'closure'
               84  LOAD_FAST                'req'
               86  LOAD_ATTR                headers
               88  LOAD_METHOD              items
               90  CALL_METHOD_0         0  '0 positional arguments'
               92  GET_ITER         
               94  CALL_FUNCTION_1       1  '1 positional argument'
               96  STORE_FAST               'newheaders'

 L. 688        98  LOAD_GLOBAL              Request
              100  LOAD_FAST                'newurl'

 L. 689       102  LOAD_FAST                'newheaders'

 L. 690       104  LOAD_FAST                'req'
              106  LOAD_ATTR                origin_req_host

 L. 691       108  LOAD_CONST               True
              110  LOAD_CONST               ('headers', 'origin_req_host', 'unverifiable')
              112  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              114  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 78

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers['location']
        else:
            if 'uri' in headers:
                newurl = headers['uri']
            else:
                return
        urlparts = urlparse(newurl)
        if urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(newurl, code, "%s - Redirection to url '%s' is not allowed" % (msg, newurl), headers, fp)
        elif not urlparts.path:
            if urlparts.netloc:
                urlparts = list(urlparts)
                urlparts[2] = '/'
        else:
            newurl = urlunparse(urlparts)
            newurl = quote(newurl,
              encoding='iso-8859-1', safe=(string.punctuation))
            newurl = urljoin(req.full_url, newurl)
            new = self.redirect_request(req, fp, code, msg, headers, newurl)
            if new is None:
                return
                if hasattr(req, 'redirect_dict'):
                    visited = new.redirect_dict = req.redirect_dict
                    if visited.get(newurl, 0) >= self.max_repeats or len(visited) >= self.max_redirections:
                        raise HTTPError(req.full_url, code, self.inf_msg + msg, headers, fp)
            else:
                visited = new.redirect_dict = req.redirect_dict = {}
        visited[newurl] = visited.get(newurl, 0) + 1
        fp.read()
        fp.close()
        return self.parent.open(new, timeout=(req.timeout))

    http_error_301 = http_error_303 = http_error_307 = http_error_302
    inf_msg = 'The HTTP server returned a redirect error that would lead to an infinite loop.\nThe last 30x error message was:\n'


def _parse_proxy(proxy):
    scheme, r_scheme = splittype(proxy)
    if not r_scheme.startswith('/'):
        scheme = None
        authority = proxy
    else:
        if not r_scheme.startswith('//'):
            raise ValueError('proxy URL with no authority: %r' % proxy)
        end = r_scheme.find('/', 2)
        if end == -1:
            end = None
        authority = r_scheme[2:end]
    userinfo, hostport = splituser(authority)
    if userinfo is not None:
        user, password = splitpasswd(userinfo)
    else:
        user = password = None
    return (
     scheme, user, password, hostport)


class ProxyHandler(BaseHandler):
    handler_order = 100

    def __init__(self, proxies=None):
        if proxies is None:
            proxies = getproxies()
        self.proxies = proxies
        for type, url in proxies.items():
            setattr(self, '%s_open' % type, (lambda r, proxy=url, type=type, meth=self.proxy_open: meth(r, proxy, type)))

    def proxy_open(self, req, proxy, type):
        orig_type = req.type
        proxy_type, user, password, hostport = _parse_proxy(proxy)
        if proxy_type is None:
            proxy_type = orig_type
        if req.host:
            if proxy_bypass(req.host):
                return
        if user:
            if password:
                user_pass = '%s:%s' % (unquote(user),
                 unquote(password))
                creds = base64.b64encode(user_pass.encode()).decode('ascii')
                req.add_header('Proxy-authorization', 'Basic ' + creds)
        hostport = unquote(hostport)
        req.set_proxy(hostport, proxy_type)
        if orig_type == proxy_type or orig_type == 'https':
            return
        return self.parent.open(req, timeout=(req.timeout))


class HTTPPasswordMgr:

    def __init__(self):
        self.passwd = {}

    def add_password(self, realm, uri, user, passwd):
        if isinstance(uri, str):
            uri = [
             uri]
        if realm not in self.passwd:
            self.passwd[realm] = {}
        for default_port in (True, False):
            reduced_uri = tuple((self.reduce_uri(u, default_port) for u in uri))
            self.passwd[realm][reduced_uri] = (user, passwd)

    def find_user_password(self, realm, authuri):
        domains = self.passwd.get(realm, {})
        for default_port in (True, False):
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uris, authinfo in domains.items():
                for uri in uris:
                    if self.is_suburi(uri, reduced_authuri):
                        return authinfo

        return (None, None)

    def reduce_uri(self, uri, default_port=True):
        parts = urlsplit(uri)
        if parts[1]:
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] or '/'
        else:
            scheme = None
            authority = uri
            path = '/'
        host, port = splitport(authority)
        if default_port:
            if port is None:
                if scheme is not None:
                    dport = {'http':80, 
                     'https':443}.get(scheme)
                    if dport is not None:
                        authority = '%s:%d' % (host, dport)
        return (
         authority, path)

    def is_suburi(self, base, test):
        if base == test:
            return True
        if base[0] != test[0]:
            return False
        common = posixpath.commonprefix((base[1], test[1]))
        if len(common) == len(base[1]):
            return True
        return False


class HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):

    def find_user_password(self, realm, authuri):
        user, password = HTTPPasswordMgr.find_user_password(self, realm, authuri)
        if user is not None:
            return (
             user, password)
        return HTTPPasswordMgr.find_user_password(self, None, authuri)


class HTTPPasswordMgrWithPriorAuth(HTTPPasswordMgrWithDefaultRealm):

    def __init__(self, *args, **kwargs):
        self.authenticated = {}
        (super().__init__)(*args, **kwargs)

    def add_password(self, realm, uri, user, passwd, is_authenticated=False):
        self.update_authenticated(uri, is_authenticated)
        if realm is not None:
            super().add_password(None, uri, user, passwd)
        super().add_password(realm, uri, user, passwd)

    def update_authenticated(self, uri, is_authenticated=False):
        if isinstance(uri, str):
            uri = [
             uri]
        for default_port in (True, False):
            for u in uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    def is_authenticated(self, authuri):
        for default_port in (True, False):
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uri in self.authenticated:
                if self.is_suburi(uri, reduced_authuri):
                    return self.authenticated[uri]


class AbstractBasicAuthHandler:
    rx = re.compile('(?:.*,)*[ \t]*([^ \t]+)[ \t]+realm=(["\']?)([^"\']*)\\2', re.I)

    def __init__(self, password_mgr=None):
        if password_mgr is None:
            password_mgr = HTTPPasswordMgr()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password

    def http_error_auth_reqed(self, authreq, host, req, headers):
        authreq = headers.get(authreq, None)
        if authreq:
            scheme = authreq.split()[0]
            if scheme.lower() != 'basic':
                raise ValueError("AbstractBasicAuthHandler does not support the following scheme: '%s'" % scheme)
            else:
                mo = AbstractBasicAuthHandler.rx.search(authreq)
                if mo:
                    scheme, quote, realm = mo.groups()
                    if quote not in ('"', "'"):
                        warnings.warn('Basic Auth Realm was unquoted', UserWarning, 2)
                    if scheme.lower() == 'basic':
                        return self.retry_http_basic_auth(host, req, realm)

    def retry_http_basic_auth(self, host, req, realm):
        user, pw = self.passwd.find_user_password(realm, host)
        if pw is not None:
            raw = '%s:%s' % (user, pw)
            auth = 'Basic ' + base64.b64encode(raw.encode()).decode('ascii')
            if req.get_header(self.auth_header, None) == auth:
                return
            req.add_unredirected_header(self.auth_header, auth)
            return self.parent.open(req, timeout=(req.timeout))
        return

    def http_request(self, req):
        return hasattr(self.passwd, 'is_authenticated') and self.passwd.is_authenticated(req.full_url) or req
        if not req.has_header('Authorization'):
            user, passwd = self.passwd.find_user_password(None, req.full_url)
            credentials = '{0}:{1}'.format(user, passwd).encode()
            auth_str = base64.standard_b64encode(credentials).decode()
            req.add_unredirected_header('Authorization', 'Basic {}'.format(auth_str.strip()))
        return req

    def http_response(self, req, response):
        if hasattr(self.passwd, 'is_authenticated'):
            if 200 <= response.code < 300:
                self.passwd.update_authenticated(req.full_url, True)
            else:
                self.passwd.update_authenticated(req.full_url, False)
        return response

    https_request = http_request
    https_response = http_response


class HTTPBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):
    auth_header = 'Authorization'

    def http_error_401(self, req, fp, code, msg, headers):
        url = req.full_url
        response = self.http_error_auth_reqed('www-authenticate', url, req, headers)
        return response


class ProxyBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):
    auth_header = 'Proxy-authorization'

    def http_error_407(self, req, fp, code, msg, headers):
        authority = req.host
        response = self.http_error_auth_reqed('proxy-authenticate', authority, req, headers)
        return response


_randombytes = os.urandom

class AbstractDigestAuthHandler:

    def __init__(self, passwd=None):
        if passwd is None:
            passwd = HTTPPasswordMgr()
        self.passwd = passwd
        self.add_password = self.passwd.add_password
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = None

    def reset_retry_count(self):
        self.retried = 0

    def http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, None)
        if self.retried > 5:
            raise HTTPError(req.full_url, 401, 'digest auth failed', headers, None)
        else:
            self.retried += 1
        if authreq:
            scheme = authreq.split()[0]
            if scheme.lower() == 'digest':
                return self.retry_http_digest_auth(req, authreq)
            if scheme.lower() != 'basic':
                raise ValueError("AbstractDigestAuthHandler does not support the following scheme: '%s'" % scheme)

    def retry_http_digest_auth(self, req, auth):
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(filter(None, parse_http_list(challenge)))
        auth = self.get_authorization(req, chal)
        if auth:
            auth_val = 'Digest %s' % auth
            if req.headers.get(self.auth_header, None) == auth_val:
                return
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout=(req.timeout))
            return resp

    def get_cnonce(self, nonce):
        s = '%s:%s:%s:' % (self.nonce_count, nonce, time.ctime())
        b = s.encode('ascii') + _randombytes(8)
        dig = hashlib.sha1(b).hexdigest()
        return dig[:16]

    def get_authorization(self, req, chal):
        try:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            opaque = chal.get('opaque', None)
        except KeyError:
            return
        else:
            H, KD = self.get_algorithm_impls(algorithm)
            if H is None:
                return
            user, pw = self.passwd.find_user_password(realm, req.full_url)
            if user is None:
                return
            else:
                if req.data is not None:
                    entdig = self.get_entity_digest(req.data, chal)
                else:
                    entdig = None
                A1 = '%s:%s:%s' % (user, realm, pw)
                A2 = '%s:%s' % (req.get_method(),
                 req.selector)
                if qop == 'auth':
                    if nonce == self.last_nonce:
                        self.nonce_count += 1
                    else:
                        self.nonce_count = 1
                        self.last_nonce = nonce
                    ncvalue = '%08x' % self.nonce_count
                    cnonce = self.get_cnonce(nonce)
                    noncebit = '%s:%s:%s:%s:%s' % (nonce, ncvalue, cnonce, qop, H(A2))
                    respdig = KD(H(A1), noncebit)
                else:
                    if qop is None:
                        respdig = KD(H(A1), '%s:%s' % (nonce, H(A2)))
                    else:
                        raise URLError("qop '%s' is not supported." % qop)
            base = 'username="%s", realm="%s", nonce="%s", uri="%s", response="%s"' % (
             user, realm, nonce, req.selector,
             respdig)
            if opaque:
                base += ', opaque="%s"' % opaque
            if entdig:
                base += ', digest="%s"' % entdig
            base += ', algorithm="%s"' % algorithm
            if qop:
                base += ', qop=auth, nc=%s, cnonce="%s"' % (ncvalue, cnonce)
            return base

    def get_algorithm_impls(self, algorithm):
        if algorithm == 'MD5':
            H = lambda x: hashlib.md5(x.encode('ascii')).hexdigest()
        else:
            if algorithm == 'SHA':
                H = lambda x: hashlib.sha1(x.encode('ascii')).hexdigest()
            else:
                raise ValueError('Unsupported digest authentication algorithm %r' % algorithm)
        KD = lambda s, d: H('%s:%s' % (s, d))
        return (H, KD)

    def get_entity_digest(self, data, chal):
        pass


class HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    auth_header = 'Authorization'
    handler_order = 490

    def http_error_401(self, req, fp, code, msg, headers):
        host = urlparse(req.full_url)[1]
        retry = self.http_error_auth_reqed('www-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry


class ProxyDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    auth_header = 'Proxy-Authorization'
    handler_order = 490

    def http_error_407(self, req, fp, code, msg, headers):
        host = req.host
        retry = self.http_error_auth_reqed('proxy-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry


class AbstractHTTPHandler(BaseHandler):

    def __init__(self, debuglevel=0):
        self._debuglevel = debuglevel

    def set_http_debuglevel(self, level):
        self._debuglevel = level

    def _get_content_length(self, request):
        return http.client.HTTPConnection._get_content_length(request.data, request.get_method())

    def do_request_(self, request):
        host = request.host
        if not host:
            raise URLError('no host given')
        elif request.data is not None:
            data = request.data
            if isinstance(data, str):
                msg = 'POST data should be bytes, an iterable of bytes, or a file object. It cannot be of type str.'
                raise TypeError(msg)
            if not request.has_header('Content-type'):
                request.add_unredirected_header('Content-type', 'application/x-www-form-urlencoded')
            if not request.has_header('Content-length'):
                if not request.has_header('Transfer-encoding'):
                    content_length = self._get_content_length(request)
                    if content_length is not None:
                        request.add_unredirected_header('Content-length', str(content_length))
                    else:
                        request.add_unredirected_header('Transfer-encoding', 'chunked')
        sel_host = host
        if request.has_proxy():
            scheme, sel = splittype(request.selector)
            sel_host, sel_path = splithost(sel)
        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if not request.has_header(name):
                request.add_unredirected_header(name, value)

        return request

    def do_open--- This code section failed: ---

 L.1280         0  LOAD_FAST                'req'
                2  LOAD_ATTR                host
                4  STORE_FAST               'host'

 L.1281         6  LOAD_FAST                'host'
                8  POP_JUMP_IF_TRUE     18  'to 18'

 L.1282        10  LOAD_GLOBAL              URLError
               12  LOAD_STR                 'no host given'
               14  CALL_FUNCTION_1       1  '1 positional argument'
               16  RAISE_VARARGS_1       1  'exception instance'
             18_0  COME_FROM             8  '8'

 L.1285        18  LOAD_FAST                'http_class'
               20  LOAD_FAST                'host'
               22  BUILD_TUPLE_1         1 
               24  LOAD_STR                 'timeout'
               26  LOAD_FAST                'req'
               28  LOAD_ATTR                timeout
               30  BUILD_MAP_1           1 
               32  LOAD_FAST                'http_conn_args'
               34  BUILD_MAP_UNPACK_WITH_CALL_2     2 
               36  CALL_FUNCTION_EX_KW     1  'keyword and positional arguments'
               38  STORE_FAST               'h'

 L.1286        40  LOAD_FAST                'h'
               42  LOAD_METHOD              set_debuglevel
               44  LOAD_FAST                'self'
               46  LOAD_ATTR                _debuglevel
               48  CALL_METHOD_1         1  '1 positional argument'
               50  POP_TOP          

 L.1288        52  LOAD_GLOBAL              dict
               54  LOAD_FAST                'req'
               56  LOAD_ATTR                unredirected_hdrs
               58  CALL_FUNCTION_1       1  '1 positional argument'
               60  STORE_DEREF              'headers'

 L.1289        62  LOAD_DEREF               'headers'
               64  LOAD_METHOD              update
               66  LOAD_CLOSURE             'headers'
               68  BUILD_TUPLE_1         1 
               70  LOAD_DICTCOMP            '<code_object <dictcomp>>'
               72  LOAD_STR                 'AbstractHTTPHandler.do_open.<locals>.<dictcomp>'
               74  MAKE_FUNCTION_8          'closure'
               76  LOAD_FAST                'req'
               78  LOAD_ATTR                headers
               80  LOAD_METHOD              items
               82  CALL_METHOD_0         0  '0 positional arguments'
               84  GET_ITER         
               86  CALL_FUNCTION_1       1  '1 positional argument'
               88  CALL_METHOD_1         1  '1 positional argument'
               90  POP_TOP          

 L.1301        92  LOAD_STR                 'close'
               94  LOAD_DEREF               'headers'
               96  LOAD_STR                 'Connection'
               98  STORE_SUBSCR     

 L.1302       100  LOAD_DICTCOMP            '<code_object <dictcomp>>'
              102  LOAD_STR                 'AbstractHTTPHandler.do_open.<locals>.<dictcomp>'
              104  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              106  LOAD_DEREF               'headers'
              108  LOAD_METHOD              items
              110  CALL_METHOD_0         0  '0 positional arguments'
              112  GET_ITER         
              114  CALL_FUNCTION_1       1  '1 positional argument'
              116  STORE_DEREF              'headers'

 L.1304       118  LOAD_FAST                'req'
              120  LOAD_ATTR                _tunnel_host
              122  POP_JUMP_IF_FALSE   174  'to 174'

 L.1305       124  BUILD_MAP_0           0 
              126  STORE_FAST               'tunnel_headers'

 L.1306       128  LOAD_STR                 'Proxy-Authorization'
              130  STORE_FAST               'proxy_auth_hdr'

 L.1307       132  LOAD_FAST                'proxy_auth_hdr'
              134  LOAD_DEREF               'headers'
              136  COMPARE_OP               in
              138  POP_JUMP_IF_FALSE   158  'to 158'

 L.1308       140  LOAD_DEREF               'headers'
              142  LOAD_FAST                'proxy_auth_hdr'
              144  BINARY_SUBSCR    
              146  LOAD_FAST                'tunnel_headers'
              148  LOAD_FAST                'proxy_auth_hdr'
              150  STORE_SUBSCR     

 L.1311       152  LOAD_DEREF               'headers'
              154  LOAD_FAST                'proxy_auth_hdr'
              156  DELETE_SUBSCR    
            158_0  COME_FROM           138  '138'

 L.1312       158  LOAD_FAST                'h'
              160  LOAD_ATTR                set_tunnel
              162  LOAD_FAST                'req'
              164  LOAD_ATTR                _tunnel_host
              166  LOAD_FAST                'tunnel_headers'
              168  LOAD_CONST               ('headers',)
              170  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              172  POP_TOP          
            174_0  COME_FROM           122  '122'

 L.1314       174  SETUP_EXCEPT        272  'to 272'

 L.1315       176  SETUP_EXCEPT        216  'to 216'

 L.1316       178  LOAD_FAST                'h'
              180  LOAD_ATTR                request
              182  LOAD_FAST                'req'
              184  LOAD_METHOD              get_method
              186  CALL_METHOD_0         0  '0 positional arguments'
              188  LOAD_FAST                'req'
              190  LOAD_ATTR                selector
              192  LOAD_FAST                'req'
              194  LOAD_ATTR                data
              196  LOAD_DEREF               'headers'

 L.1317       198  LOAD_FAST                'req'
              200  LOAD_METHOD              has_header
              202  LOAD_STR                 'Transfer-encoding'
              204  CALL_METHOD_1         1  '1 positional argument'
              206  LOAD_CONST               ('encode_chunked',)
              208  CALL_FUNCTION_KW_5     5  '5 total positional and keyword args'
              210  POP_TOP          
              212  POP_BLOCK        
              214  JUMP_FORWARD        260  'to 260'
            216_0  COME_FROM_EXCEPT    176  '176'

 L.1318       216  DUP_TOP          
              218  LOAD_GLOBAL              OSError
              220  COMPARE_OP               exception-match
          222_224  POP_JUMP_IF_FALSE   258  'to 258'
              226  POP_TOP          
              228  STORE_FAST               'err'
              230  POP_TOP          
              232  SETUP_FINALLY       246  'to 246'

 L.1319       234  LOAD_GLOBAL              URLError
              236  LOAD_FAST                'err'
              238  CALL_FUNCTION_1       1  '1 positional argument'
              240  RAISE_VARARGS_1       1  'exception instance'
              242  POP_BLOCK        
              244  LOAD_CONST               None
            246_0  COME_FROM_FINALLY   232  '232'
              246  LOAD_CONST               None
              248  STORE_FAST               'err'
              250  DELETE_FAST              'err'
              252  END_FINALLY      
              254  POP_EXCEPT       
              256  JUMP_FORWARD        260  'to 260'
            258_0  COME_FROM           222  '222'
              258  END_FINALLY      
            260_0  COME_FROM           256  '256'
            260_1  COME_FROM           214  '214'

 L.1320       260  LOAD_FAST                'h'
              262  LOAD_METHOD              getresponse
              264  CALL_METHOD_0         0  '0 positional arguments'
              266  STORE_FAST               'r'
              268  POP_BLOCK        
              270  JUMP_FORWARD        294  'to 294'
            272_0  COME_FROM_EXCEPT    174  '174'

 L.1321       272  POP_TOP          
              274  POP_TOP          
              276  POP_TOP          

 L.1322       278  LOAD_FAST                'h'
              280  LOAD_METHOD              close
              282  CALL_METHOD_0         0  '0 positional arguments'
              284  POP_TOP          

 L.1323       286  RAISE_VARARGS_0       0  'reraise'
              288  POP_EXCEPT       
              290  JUMP_FORWARD        294  'to 294'
              292  END_FINALLY      
            294_0  COME_FROM           290  '290'
            294_1  COME_FROM           270  '270'

 L.1328       294  LOAD_FAST                'h'
              296  LOAD_ATTR                sock
          298_300  POP_JUMP_IF_FALSE   318  'to 318'

 L.1329       302  LOAD_FAST                'h'
              304  LOAD_ATTR                sock
              306  LOAD_METHOD              close
              308  CALL_METHOD_0         0  '0 positional arguments'
              310  POP_TOP          

 L.1330       312  LOAD_CONST               None
              314  LOAD_FAST                'h'
              316  STORE_ATTR               sock
            318_0  COME_FROM           298  '298'

 L.1332       318  LOAD_FAST                'req'
              320  LOAD_METHOD              get_full_url
              322  CALL_METHOD_0         0  '0 positional arguments'
              324  LOAD_FAST                'r'
              326  STORE_ATTR               url

 L.1338       328  LOAD_FAST                'r'
              330  LOAD_ATTR                reason
              332  LOAD_FAST                'r'
              334  STORE_ATTR               msg

 L.1339       336  LOAD_FAST                'r'
              338  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_DICTCOMP' instruction at offset 70


class HTTPHandler(AbstractHTTPHandler):

    def http_open(self, req):
        return self.do_open(http.client.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_


if hasattr(http.client, 'HTTPSConnection'):

    class HTTPSHandler(AbstractHTTPHandler):

        def __init__(self, debuglevel=0, context=None, check_hostname=None):
            AbstractHTTPHandler.__init__(self, debuglevel)
            self._context = context
            self._check_hostname = check_hostname

        def https_open(self, req):
            return self.do_open((http.client.HTTPSConnection), req, context=(self._context),
              check_hostname=(self._check_hostname))

        https_request = AbstractHTTPHandler.do_request_


    __all__.append('HTTPSHandler')
else:

    class HTTPCookieProcessor(BaseHandler):

        def __init__(self, cookiejar=None):
            import http.cookiejar
            if cookiejar is None:
                cookiejar = http.cookiejar.CookieJar()
            self.cookiejar = cookiejar

        def http_request(self, request):
            self.cookiejar.add_cookie_header(request)
            return request

        def http_response(self, request, response):
            self.cookiejar.extract_cookies(response, request)
            return response

        https_request = http_request
        https_response = http_response


    class UnknownHandler(BaseHandler):

        def unknown_open(self, req):
            type = req.type
            raise URLError('unknown url type: %s' % type)


    def parse_keqv_list(l):
        parsed = {}
        for elt in l:
            k, v = elt.split('=', 1)
            if v[0] == '"':
                if v[-1] == '"':
                    v = v[1:-1]
            parsed[k] = v

        return parsed


    def parse_http_list(s):
        res = []
        part = ''
        escape = quote = False
        for cur in s:
            if escape:
                part += cur
                escape = False
                continue
            if quote:
                if cur == '\\':
                    escape = True
                    continue
                else:
                    if cur == '"':
                        quote = False
                part += cur
                continue
            if cur == ',':
                res.append(part)
                part = ''
                continue
            if cur == '"':
                quote = True
            part += cur

        if part:
            res.append(part)
        return [part.strip() for part in res]


    class FileHandler(BaseHandler):

        def file_open(self, req):
            url = req.selector
            if url[:2] == '//' and url[2:3] != '/' and req.host and req.host != 'localhost':
                if req.host not in self.get_names():
                    raise URLError('file:// scheme is supported only on localhost')
            else:
                return self.open_local_file(req)

        names = None

        def get_names(self):
            if FileHandler.names is None:
                try:
                    FileHandler.names = tuple(socket.gethostbyname_ex('localhost')[2] + socket.gethostbyname_ex(socket.gethostname())[2])
                except socket.gaierror:
                    FileHandler.names = (
                     socket.gethostbyname('localhost'),)

            return FileHandler.names

        def open_local_file(self, req):
            import email.utils, mimetypes
            host = req.host
            filename = req.selector
            localfile = url2pathname(filename)
            try:
                stats = os.stat(localfile)
                size = stats.st_size
                modified = email.utils.formatdate((stats.st_mtime), usegmt=True)
                mtype = mimetypes.guess_type(filename)[0]
                headers = email.message_from_string('Content-type: %s\nContent-length: %d\nLast-modified: %s\n' % (
                 mtype or 'text/plain', size, modified))
                if host:
                    host, port = splitport(host)
                elif not host or (port or _safe_gethostbyname(host)) in self.get_names():
                    if host:
                        origurl = 'file://' + host + filename
                    else:
                        origurl = 'file://' + filename
                    return addinfourl(open(localfile, 'rb'), headers, origurl)
            except OSError as exp:
                try:
                    raise URLError(exp)
                finally:
                    exp = None
                    del exp

            raise URLError('file not on local host')


    def _safe_gethostbyname(host):
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            return


    class FTPHandler(BaseHandler):

        def ftp_open(self, req):
            import ftplib, mimetypes
            host = req.host
            if not host:
                raise URLError('ftp error: no host given')
            else:
                host, port = splitport(host)
                if port is None:
                    port = ftplib.FTP_PORT
                else:
                    port = int(port)
                user, host = splituser(host)
                if user:
                    user, passwd = splitpasswd(user)
                else:
                    passwd = None
            host = unquote(host)
            user = user or ''
            passwd = passwd or ''
            try:
                host = socket.gethostbyname(host)
            except OSError as msg:
                try:
                    raise URLError(msg)
                finally:
                    msg = None
                    del msg

            path, attrs = splitattr(req.selector)
            dirs = path.split('/')
            dirs = list(map(unquote, dirs))
            dirs, file = dirs[:-1], dirs[-1]
            if dirs:
                if not dirs[0]:
                    dirs = dirs[1:]
            try:
                fw = self.connect_ftp(user, passwd, host, port, dirs, req.timeout)
                type = file and 'I' or 'D'
                for attr in attrs:
                    attr, value = splitvalue(attr)
                    if attr.lower() == 'type' and value in ('a', 'A', 'i', 'I', 'd',
                                                            'D'):
                        type = value.upper()

                fp, retrlen = fw.retrfile(file, type)
                headers = ''
                mtype = mimetypes.guess_type(req.full_url)[0]
                if mtype:
                    headers += 'Content-type: %s\n' % mtype
                if retrlen is not None:
                    if retrlen >= 0:
                        headers += 'Content-length: %d\n' % retrlen
                headers = email.message_from_string(headers)
                return addinfourl(fp, headers, req.full_url)
            except ftplib.all_errors as exp:
                try:
                    exc = URLError('ftp error: %r' % exp)
                    raise exc.with_traceback(sys.exc_info()[2])
                finally:
                    exp = None
                    del exp

        def connect_ftp(self, user, passwd, host, port, dirs, timeout):
            return ftpwrapper(user, passwd, host, port, dirs, timeout, persistent=False)


    class CacheFTPHandler(FTPHandler):

        def __init__(self):
            self.cache = {}
            self.timeout = {}
            self.soonest = 0
            self.delay = 60
            self.max_conns = 16

        def setTimeout(self, t):
            self.delay = t

        def setMaxConns(self, m):
            self.max_conns = m

        def connect_ftp(self, user, passwd, host, port, dirs, timeout):
            key = (
             user, host, port, '/'.join(dirs), timeout)
            if key in self.cache:
                self.timeout[key] = time.time() + self.delay
            else:
                self.cache[key] = ftpwrapper(user, passwd, host, port, dirs, timeout)
                self.timeout[key] = time.time() + self.delay
            self.check_cache()
            return self.cache[key]

        def check_cache(self):
            t = time.time()
            if self.soonest <= t:
                for k, v in list(self.timeout.items()):
                    if v < t:
                        self.cache[k].close()
                        del self.cache[k]
                        del self.timeout[k]

            self.soonest = min(list(self.timeout.values()))
            if len(self.cache) == self.max_conns:
                for k, v in list(self.timeout.items()):
                    if v == self.soonest:
                        del self.cache[k]
                        del self.timeout[k]
                        break

                self.soonest = min(list(self.timeout.values()))

        def clear_cache(self):
            for conn in self.cache.values():
                conn.close()

            self.cache.clear()
            self.timeout.clear()


    class DataHandler(BaseHandler):

        def data_open(self, req):
            url = req.full_url
            scheme, data = url.split(':', 1)
            mediatype, data = data.split(',', 1)
            data = unquote_to_bytes(data)
            if mediatype.endswith(';base64'):
                data = base64.decodebytes(data)
                mediatype = mediatype[:-7]
            if not mediatype:
                mediatype = 'text/plain;charset=US-ASCII'
            headers = email.message_from_string('Content-type: %s\nContent-length: %d\n' % (
             mediatype, len(data)))
            return addinfourl(io.BytesIO(data), headers, url)


    MAXFTPCACHE = 10
    if os.name == 'nt':
        from nturl2path import url2pathname, pathname2url
    else:

        def url2pathname(pathname):
            return unquote(pathname)


        def pathname2url(pathname):
            return quote(pathname)


    ftpcache = {}

    class URLopener:
        _URLopener__tempfiles = None
        version = 'Python-urllib/%s' % __version__

        def __init__(self, proxies=None, **x509):
            msg = '%(class)s style of invoking requests is deprecated. Use newer urlopen functions/methods' % {'class': self.__class__.__name__}
            warnings.warn(msg, DeprecationWarning, stacklevel=3)
            if proxies is None:
                proxies = getproxies()
            self.proxies = proxies
            self.key_file = x509.get('key_file')
            self.cert_file = x509.get('cert_file')
            self.addheaders = [('User-Agent', self.version), ('Accept', '*/*')]
            self._URLopener__tempfiles = []
            self._URLopener__unlink = os.unlink
            self.tempcache = None
            self.ftpcache = ftpcache

        def __del__(self):
            self.close()

        def close(self):
            self.cleanup()

        def cleanup(self):
            if self._URLopener__tempfiles:
                for file in self._URLopener__tempfiles:
                    try:
                        self._URLopener__unlink(file)
                    except OSError:
                        pass

                del self._URLopener__tempfiles[:]
            if self.tempcache:
                self.tempcache.clear()

        def addheader(self, *args):
            self.addheaders.append(args)

        def open(self, fullurl, data=None):
            fullurl = unwrap(to_bytes(fullurl))
            fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
            if self.tempcache:
                if fullurl in self.tempcache:
                    filename, headers = self.tempcache[fullurl]
                    fp = open(filename, 'rb')
                    return addinfourl(fp, headers, fullurl)
            urltype, url = splittype(fullurl)
            if not urltype:
                urltype = 'file'
            elif urltype in self.proxies:
                proxy = self.proxies[urltype]
                urltype, proxyhost = splittype(proxy)
                host, selector = splithost(proxyhost)
                url = (host, fullurl)
            else:
                proxy = None
            name = 'open_' + urltype
            self.type = urltype
            name = name.replace('-', '_')
            if not hasattr(self, name):
                if proxy:
                    return self.open_unknown_proxy(proxy, fullurl, data)
                return self.open_unknown(fullurl, data)
            try:
                if data is None:
                    return getattr(self, name)(url)
                return getattr(self, name)(url, data)
            except (HTTPError, URLError):
                raise
            except OSError as msg:
                try:
                    raise OSError('socket error', msg).with_traceback(sys.exc_info()[2])
                finally:
                    msg = None
                    del msg

        def open_unknown(self, fullurl, data=None):
            type, url = splittype(fullurl)
            raise OSError('url error', 'unknown url type', type)

        def open_unknown_proxy(self, proxy, fullurl, data=None):
            type, url = splittype(fullurl)
            raise OSError('url error', 'invalid proxy for %s' % type, proxy)

        def retrieve(self, url, filename=None, reporthook=None, data=None):
            url = unwrap(to_bytes(url))
            if self.tempcache:
                if url in self.tempcache:
                    return self.tempcache[url]
            type, url1 = splittype(url)
            if filename is None:
                if not type or type == 'file':
                    try:
                        fp = self.open_local_file(url1)
                        hdrs = fp.info()
                        fp.close()
                        return (url2pathname(splithost(url1)[1]), hdrs)
                    except OSError as msg:
                        try:
                            pass
                        finally:
                            msg = None
                            del msg

            fp = self.open(url, data)
            try:
                headers = fp.info()
                if filename:
                    tfp = open(filename, 'wb')
                else:
                    garbage, path = splittype(url)
                    garbage, path = splithost(path or '')
                    path, garbage = splitquery(path or '')
                    path, garbage = splitattr(path or '')
                    suffix = os.path.splitext(path)[1]
                    fd, filename = tempfile.mkstemp(suffix)
                    self._URLopener__tempfiles.append(filename)
                    tfp = os.fdopen(fd, 'wb')
                try:
                    result = (
                     filename, headers)
                    if self.tempcache is not None:
                        self.tempcache[url] = result
                    bs = 8192
                    size = -1
                    read = 0
                    blocknum = 0
                    if 'content-length' in headers:
                        size = int(headers['Content-Length'])
                    if reporthook:
                        reporthook(blocknum, bs, size)
                    while 1:
                        block = fp.read(bs)
                        if not block:
                            break
                        read += len(block)
                        tfp.write(block)
                        blocknum += 1
                        if reporthook:
                            reporthook(blocknum, bs, size)

                finally:
                    tfp.close()

            finally:
                fp.close()

            if size >= 0:
                if read < size:
                    raise ContentTooShortError('retrieval incomplete: got only %i out of %i bytes' % (
                     read, size), result)
            return result

        def _open_generic_http(self, connection_factory, url, data):
            user_passwd = None
            proxy_passwd = None
            if isinstance(url, str):
                host, selector = splithost(url)
                if host:
                    user_passwd, host = splituser(host)
                    host = unquote(host)
                realhost = host
            else:
                host, selector = url
                proxy_passwd, host = splituser(host)
                urltype, rest = splittype(selector)
                url = rest
                user_passwd = None
                if urltype.lower() != 'http':
                    realhost = None
                else:
                    realhost, rest = splithost(rest)
                    if realhost:
                        user_passwd, realhost = splituser(realhost)
                    if user_passwd:
                        selector = '%s://%s%s' % (urltype, realhost, rest)
                    if proxy_bypass(realhost):
                        host = realhost
                    else:
                        if not host:
                            raise OSError('http error', 'no host given')
                        else:
                            if proxy_passwd:
                                proxy_passwd = unquote(proxy_passwd)
                                proxy_auth = base64.b64encode(proxy_passwd.encode()).decode('ascii')
                            else:
                                proxy_auth = None
                            if user_passwd:
                                user_passwd = unquote(user_passwd)
                                auth = base64.b64encode(user_passwd.encode()).decode('ascii')
                            else:
                                auth = None
                        http_conn = connection_factory(host)
                        headers = {}
                        if proxy_auth:
                            headers['Proxy-Authorization'] = 'Basic %s' % proxy_auth
                        if auth:
                            headers['Authorization'] = 'Basic %s' % auth
                        if realhost:
                            headers['Host'] = realhost
                        headers['Connection'] = 'close'
                        for header, value in self.addheaders:
                            headers[header] = value

                        if data is not None:
                            headers['Content-Type'] = 'application/x-www-form-urlencoded'
                            http_conn.request('POST', selector, data, headers)
                        else:
                            http_conn.request('GET', selector, headers=headers)
                    try:
                        response = http_conn.getresponse()
                    except http.client.BadStatusLine:
                        raise URLError('http protocol error: bad status line')

                    if 200 <= response.status < 300:
                        return addinfourl(response, response.msg, 'http:' + url, response.status)
                    return self.http_error(url, response.fp, response.status, response.reason, response.msg, data)

        def open_http(self, url, data=None):
            return self._open_generic_http(http.client.HTTPConnection, url, data)

        def http_error(self, url, fp, errcode, errmsg, headers, data=None):
            name = 'http_error_%d' % errcode
            if hasattr(self, name):
                method = getattr(self, name)
                if data is None:
                    result = method(url, fp, errcode, errmsg, headers)
                else:
                    result = method(url, fp, errcode, errmsg, headers, data)
                if result:
                    return result
            return self.http_error_default(url, fp, errcode, errmsg, headers)

        def http_error_default(self, url, fp, errcode, errmsg, headers):
            fp.close()
            raise HTTPError(url, errcode, errmsg, headers, None)

        if _have_ssl:

            def _https_connection(self, host):
                return http.client.HTTPSConnection(host, key_file=(self.key_file),
                  cert_file=(self.cert_file))

            def open_https(self, url, data=None):
                return self._open_generic_http(self._https_connection, url, data)

        def open_file(self, url):
            if not isinstance(url, str):
                raise URLError('file error: proxy support for file protocol currently not implemented')
            if url[:2] == '//' and url[2:3] != '/' and url[2:12].lower() != 'localhost/':
                raise ValueError('file:// scheme is supported only on localhost')
            else:
                return self.open_local_file(url)

        def open_local_file(self, url):
            import email.utils, mimetypes
            host, file = splithost(url)
            localname = url2pathname(file)
            try:
                stats = os.stat(localname)
            except OSError as e:
                try:
                    raise URLError(e.strerror, e.filename)
                finally:
                    e = None
                    del e

            size = stats.st_size
            modified = email.utils.formatdate((stats.st_mtime), usegmt=True)
            mtype = mimetypes.guess_type(url)[0]
            headers = email.message_from_string('Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' % (
             mtype or 'text/plain', size, modified))
            if not host:
                urlfile = file
                if file[:1] == '/':
                    urlfile = 'file://' + file
                return addinfourl(open(localname, 'rb'), headers, urlfile)
            host, port = splitport(host)
            if not port:
                if socket.gethostbyname(host) in (localhost(),) + thishost():
                    urlfile = file
                    if file[:1] == '/':
                        urlfile = 'file://' + file
                    else:
                        if file[:2] == './':
                            raise ValueError('local file url may start with / or file:. Unknown url of type: %s' % url)
                        return addinfourl(open(localname, 'rb'), headers, urlfile)
            raise URLError('local file error: not on local host')

        def open_ftp(self, url):
            if not isinstance(url, str):
                raise URLError('ftp error: proxy support for ftp protocol currently not implemented')
            else:
                import mimetypes
                host, path = splithost(url)
                if not host:
                    raise URLError('ftp error: no host given')
                else:
                    host, port = splitport(host)
                    user, host = splituser(host)
                    if user:
                        user, passwd = splitpasswd(user)
                    else:
                        passwd = None
                    host = unquote(host)
                    user = unquote(user or '')
                    passwd = unquote(passwd or '')
                    host = socket.gethostbyname(host)
                    if not port:
                        import ftplib
                        port = ftplib.FTP_PORT
                    else:
                        port = int(port)
                path, attrs = splitattr(path)
                path = unquote(path)
                dirs = path.split('/')
                dirs, file = dirs[:-1], dirs[-1]
                if dirs:
                    if not dirs[0]:
                        dirs = dirs[1:]
                if dirs:
                    if not dirs[0]:
                        dirs[0] = '/'
                key = (
                 user, host, port, '/'.join(dirs))
                if len(self.ftpcache) > MAXFTPCACHE:
                    for k in list(self.ftpcache):
                        if k != key:
                            v = self.ftpcache[k]
                            del self.ftpcache[k]
                            v.close()

                try:
                    if key not in self.ftpcache:
                        self.ftpcache[key] = ftpwrapper(user, passwd, host, port, dirs)
                    else:
                        if not file:
                            type = 'D'
                        else:
                            type = 'I'
                        for attr in attrs:
                            attr, value = splitvalue(attr)
                            if attr.lower() == 'type' and value in ('a', 'A', 'i',
                                                                    'I', 'd', 'D'):
                                type = value.upper()

                        fp, retrlen = self.ftpcache[key].retrfile(file, type)
                        mtype = mimetypes.guess_type('ftp:' + url)[0]
                        headers = ''
                        if mtype:
                            headers += 'Content-Type: %s\n' % mtype
                        if retrlen is not None and retrlen >= 0:
                            headers += 'Content-Length: %d\n' % retrlen
                    headers = email.message_from_string(headers)
                    return addinfourl(fp, headers, 'ftp:' + url)
                except ftperrors() as exp:
                    try:
                        raise URLError('ftp error %r' % exp).with_traceback(sys.exc_info()[2])
                    finally:
                        exp = None
                        del exp

        def open_data(self, url, data=None):
            if not isinstance(url, str):
                raise URLError('data error: proxy support for data protocol currently not implemented')
            else:
                try:
                    type, data = url.split(',', 1)
                except ValueError:
                    raise OSError('data error', 'bad data URL')

                if not type:
                    type = 'text/plain;charset=US-ASCII'
                semi = type.rfind(';')
                if semi >= 0:
                    if '=' not in type[semi:]:
                        encoding = type[semi + 1:]
                        type = type[:semi]
                    else:
                        encoding = ''
                    msg = []
                    msg.append('Date: %s' % time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time())))
                    msg.append('Content-type: %s' % type)
                    if encoding == 'base64':
                        data = base64.decodebytes(data.encode('ascii')).decode('latin-1')
                else:
                    data = unquote(data)
            msg.append('Content-Length: %d' % len(data))
            msg.append('')
            msg.append(data)
            msg = '\n'.join(msg)
            headers = email.message_from_string(msg)
            f = io.StringIO(msg)
            return addinfourl(f, headers, url)


    class FancyURLopener(URLopener):

        def __init__(self, *args, **kwargs):
            (URLopener.__init__)(self, *args, **kwargs)
            self.auth_cache = {}
            self.tries = 0
            self.maxtries = 10

        def http_error_default(self, url, fp, errcode, errmsg, headers):
            return addinfourl(fp, headers, 'http:' + url, errcode)

        def http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
            self.tries += 1
            try:
                if self.maxtries:
                    if self.tries >= self.maxtries:
                        if hasattr(self, 'http_error_500'):
                            meth = self.http_error_500
                        else:
                            meth = self.http_error_default
                        return meth(url, fp, 500, 'Internal Server Error: Redirect Recursion', headers)
                result = self.redirect_internal(url, fp, errcode, errmsg, headers, data)
                return result
            finally:
                self.tries = 0

        def redirect_internal(self, url, fp, errcode, errmsg, headers, data):
            if 'location' in headers:
                newurl = headers['location']
            else:
                if 'uri' in headers:
                    newurl = headers['uri']
                else:
                    return
            fp.close()
            newurl = urljoin(self.type + ':' + url, newurl)
            urlparts = urlparse(newurl)
            if urlparts.scheme not in ('http', 'https', 'ftp', ''):
                raise HTTPError(newurl, errcode, errmsg + " Redirection to url '%s' is not allowed." % newurl, headers, fp)
            return self.open(newurl)

        def http_error_301(self, url, fp, errcode, errmsg, headers, data=None):
            return self.http_error_302(url, fp, errcode, errmsg, headers, data)

        def http_error_303(self, url, fp, errcode, errmsg, headers, data=None):
            return self.http_error_302(url, fp, errcode, errmsg, headers, data)

        def http_error_307(self, url, fp, errcode, errmsg, headers, data=None):
            if data is None:
                return self.http_error_302(url, fp, errcode, errmsg, headers, data)
            return self.http_error_default(url, fp, errcode, errmsg, headers)

        def http_error_401(self, url, fp, errcode, errmsg, headers, data=None, retry=False):
            if 'www-authenticate' not in headers:
                URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
            else:
                stuff = headers['www-authenticate']
                match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
                if not match:
                    URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
                scheme, realm = match.groups()
                if scheme.lower() != 'basic':
                    URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
                retry or URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
            name = 'retry_' + self.type + '_basic_auth'
            if data is None:
                return getattr(self, name)(url, realm)
            return getattr(self, name)(url, realm, data)

        def http_error_407(self, url, fp, errcode, errmsg, headers, data=None, retry=False):
            if 'proxy-authenticate' not in headers:
                URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
            else:
                stuff = headers['proxy-authenticate']
                match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
                if not match:
                    URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
                scheme, realm = match.groups()
                if scheme.lower() != 'basic':
                    URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
                retry or URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
            name = 'retry_proxy_' + self.type + '_basic_auth'
            if data is None:
                return getattr(self, name)(url, realm)
            return getattr(self, name)(url, realm, data)

        def retry_proxy_http_basic_auth(self, url, realm, data=None):
            host, selector = splithost(url)
            newurl = 'http://' + host + selector
            proxy = self.proxies['http']
            urltype, proxyhost = splittype(proxy)
            proxyhost, proxyselector = splithost(proxyhost)
            i = proxyhost.find('@') + 1
            proxyhost = proxyhost[i:]
            user, passwd = self.get_user_passwd(proxyhost, realm, i)
            if not user:
                if not passwd:
                    return
            proxyhost = '%s:%s@%s' % (quote(user, safe=''),
             quote(passwd, safe=''), proxyhost)
            self.proxies['http'] = 'http://' + proxyhost + proxyselector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)

        def retry_proxy_https_basic_auth(self, url, realm, data=None):
            host, selector = splithost(url)
            newurl = 'https://' + host + selector
            proxy = self.proxies['https']
            urltype, proxyhost = splittype(proxy)
            proxyhost, proxyselector = splithost(proxyhost)
            i = proxyhost.find('@') + 1
            proxyhost = proxyhost[i:]
            user, passwd = self.get_user_passwd(proxyhost, realm, i)
            if not user:
                if not passwd:
                    return
            proxyhost = '%s:%s@%s' % (quote(user, safe=''),
             quote(passwd, safe=''), proxyhost)
            self.proxies['https'] = 'https://' + proxyhost + proxyselector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)

        def retry_http_basic_auth(self, url, realm, data=None):
            host, selector = splithost(url)
            i = host.find('@') + 1
            host = host[i:]
            user, passwd = self.get_user_passwd(host, realm, i)
            if not user:
                if not passwd:
                    return
            host = '%s:%s@%s' % (quote(user, safe=''),
             quote(passwd, safe=''), host)
            newurl = 'http://' + host + selector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)

        def retry_https_basic_auth(self, url, realm, data=None):
            host, selector = splithost(url)
            i = host.find('@') + 1
            host = host[i:]
            user, passwd = self.get_user_passwd(host, realm, i)
            if not user:
                if not passwd:
                    return
            host = '%s:%s@%s' % (quote(user, safe=''),
             quote(passwd, safe=''), host)
            newurl = 'https://' + host + selector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)

        def get_user_passwd(self, host, realm, clear_cache=0):
            key = realm + '@' + host.lower()
            if key in self.auth_cache:
                if clear_cache:
                    del self.auth_cache[key]
                else:
                    return self.auth_cache[key]
            user, passwd = self.prompt_user_passwd(host, realm)
            if user or passwd:
                self.auth_cache[key] = (
                 user, passwd)
            return (
             user, passwd)

        def prompt_user_passwd(self, host, realm):
            import getpass
            try:
                user = input('Enter username for %s at %s: ' % (realm, host))
                passwd = getpass.getpass('Enter password for %s in %s at %s: ' % (
                 user, realm, host))
                return (user, passwd)
            except KeyboardInterrupt:
                print()
                return (None, None)


    _localhost = None

    def localhost():
        global _localhost
        if _localhost is None:
            _localhost = socket.gethostbyname('localhost')
        return _localhost


    _thishost = None

    def thishost():
        global _thishost
        if _thishost is None:
            try:
                _thishost = tuple(socket.gethostbyname_ex(socket.gethostname())[2])
            except socket.gaierror:
                _thishost = tuple(socket.gethostbyname_ex('localhost')[2])

        return _thishost


    _ftperrors = None

    def ftperrors():
        global _ftperrors
        if _ftperrors is None:
            import ftplib
            _ftperrors = ftplib.all_errors
        return _ftperrors


    _noheaders = None

    def noheaders():
        global _noheaders
        if _noheaders is None:
            _noheaders = email.message_from_string('')
        return _noheaders


    class ftpwrapper:

        def __init__(self, user, passwd, host, port, dirs, timeout=None, persistent=True):
            self.user = user
            self.passwd = passwd
            self.host = host
            self.port = port
            self.dirs = dirs
            self.timeout = timeout
            self.refcount = 0
            self.keepalive = persistent
            try:
                self.init()
            except:
                self.close()
                raise

        def init(self):
            import ftplib
            self.busy = 0
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port, self.timeout)
            self.ftp.login(self.user, self.passwd)
            _target = '/'.join(self.dirs)
            self.ftp.cwd(_target)

        def retrfile(self, file, type):
            import ftplib
            self.endtransfer()
            if type in ('d', 'D'):
                cmd = 'TYPE A'
                isdir = 1
            else:
                cmd = 'TYPE ' + type
                isdir = 0
            try:
                self.ftp.voidcmd(cmd)
            except ftplib.all_errors:
                self.init()
                self.ftp.voidcmd(cmd)

            conn = None
            if file:
                if not isdir:
                    try:
                        cmd = 'RETR ' + file
                        conn, retrlen = self.ftp.ntransfercmd(cmd)
                    except ftplib.error_perm as reason:
                        try:
                            if str(reason)[:3] != '550':
                                raise URLError('ftp error: %r' % reason).with_traceback(sys.exc_info()[2])
                        finally:
                            reason = None
                            del reason

            if not conn:
                self.ftp.voidcmd('TYPE A')
                if file:
                    pwd = self.ftp.pwd()
                    try:
                        try:
                            self.ftp.cwd(file)
                        except ftplib.error_perm as reason:
                            try:
                                raise URLError('ftp error: %r' % reason) from reason
                            finally:
                                reason = None
                                del reason

                    finally:
                        self.ftp.cwd(pwd)

                    cmd = 'LIST ' + file
                else:
                    cmd = 'LIST'
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            self.busy = 1
            ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
            self.refcount += 1
            conn.close()
            return (
             ftpobj, retrlen)

        def endtransfer(self):
            self.busy = 0

        def close(self):
            self.keepalive = False
            if self.refcount <= 0:
                self.real_close()

        def file_close(self):
            self.endtransfer()
            self.refcount -= 1
            if self.refcount <= 0:
                if not self.keepalive:
                    self.real_close()

        def real_close(self):
            self.endtransfer()
            try:
                self.ftp.close()
            except ftperrors():
                pass


    def getproxies_environment():
        proxies = {}
        for name, value in os.environ.items():
            name = name.lower()
            if value and name[-6:] == '_proxy':
                proxies[name[:-6]] = value

        if 'REQUEST_METHOD' in os.environ:
            proxies.pop('http', None)
        for name, value in os.environ.items():
            if name[-6:] == '_proxy':
                name = name.lower()
                if value:
                    proxies[name[:-6]] = value
                else:
                    proxies.pop(name[:-6], None)

        return proxies


    def proxy_bypass_environment(host, proxies=None):
        if proxies is None:
            proxies = getproxies_environment()
        try:
            no_proxy = proxies['no']
        except KeyError:
            return 0
        else:
            if no_proxy == '*':
                return 1
            hostonly, port = splitport(host)
            no_proxy_list = [proxy.strip() for proxy in no_proxy.split(',')]
            for name in no_proxy_list:
                if name:
                    name = name.lstrip('.')
                    name = re.escape(name)
                    pattern = '(.+\\.)?%s$' % name
                    if re.match(pattern, hostonly, re.I) or re.match(pattern, host, re.I):
                        return 1

            return 0


    def _proxy_bypass_macosx_sysconf(host, proxy_settings):
        from fnmatch import fnmatch
        hostonly, port = splitport(host)

        def ip2num(ipAddr):
            parts = ipAddr.split('.')
            parts = list(map(int, parts))
            if len(parts) != 4:
                parts = (parts + [0, 0, 0, 0])[:4]
            return parts[0] << 24 | parts[1] << 16 | parts[2] << 8 | parts[3]

        if '.' not in host:
            if proxy_settings['exclude_simple']:
                return True
        hostIP = None
        for value in proxy_settings.get('exceptions', ()):
            if not value:
                continue
            m = re.match('(\\d+(?:\\.\\d+)*)(/\\d+)?', value)
            if m is not None:
                if hostIP is None:
                    try:
                        hostIP = socket.gethostbyname(hostonly)
                        hostIP = ip2num(hostIP)
                    except OSError:
                        continue

                    base = ip2num(m.group(1))
                    mask = m.group(2)
                    if mask is None:
                        mask = 8 * (m.group(1).count('.') + 1)
                    else:
                        mask = int(mask[1:])
                    mask = 32 - mask
                    if hostIP >> mask == base >> mask:
                        return True
                elif fnmatch(host, value):
                    return True

        return False


    if sys.platform == 'darwin':
        from _scproxy import _get_proxy_settings, _get_proxies

        def proxy_bypass_macosx_sysconf(host):
            proxy_settings = _get_proxy_settings()
            return _proxy_bypass_macosx_sysconf(host, proxy_settings)


        def getproxies_macosx_sysconf():
            return _get_proxies()


        def proxy_bypass(host):
            proxies = getproxies_environment()
            if proxies:
                return proxy_bypass_environment(host, proxies)
            return proxy_bypass_macosx_sysconf(host)


        def getproxies():
            return getproxies_environment() or getproxies_macosx_sysconf()


    else:
        getproxies = getproxies_environment
    proxy_bypass = proxy_bypass_environment