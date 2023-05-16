# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\http\cookiejar.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 78409 bytes
__all__ = [
 "'Cookie'", "'CookieJar'", "'CookiePolicy'", "'DefaultCookiePolicy'", 
 "'FileCookieJar'", 
 "'LWPCookieJar'", "'LoadError'", "'MozillaCookieJar'"]
import copy, datetime, re, time, urllib.parse, urllib.request, threading as _threading, http.client
from calendar import timegm
debug = False
logger = None

def _debug(*args):
    global logger
    if not debug:
        return
    if not logger:
        import logging
        logger = logging.getLogger('http.cookiejar')
    return (logger.debug)(*args)


DEFAULT_HTTP_PORT = str(http.client.HTTP_PORT)
MISSING_FILENAME_TEXT = 'a filename was not supplied (nor was the CookieJar instance initialised with one)'

def _warn_unhandled_exception():
    import io, warnings, traceback
    f = io.StringIO()
    traceback.print_exc(None, f)
    msg = f.getvalue()
    warnings.warn(('http.cookiejar bug!\n%s' % msg), stacklevel=2)


EPOCH_YEAR = 1970

def _timegm(tt):
    year, month, mday, hour, min, sec = tt[:6]
    if year >= EPOCH_YEAR:
        if 1 <= month <= 12:
            if 1 <= mday <= 31:
                if 0 <= hour <= 24:
                    if 0 <= min <= 59:
                        if 0 <= sec <= 61:
                            return timegm(tt)
    return


DAYS = [
 "'Mon'", "'Tue'", "'Wed'", "'Thu'", "'Fri'", "'Sat'", "'Sun'"]
MONTHS = ["'Jan'", "'Feb'", "'Mar'", "'Apr'", "'May'", "'Jun'", 
 "'Jul'", "'Aug'", 
 "'Sep'", "'Oct'", "'Nov'", "'Dec'"]
MONTHS_LOWER = []
for month in MONTHS:
    MONTHS_LOWER.append(month.lower())

def time2isoz(t=None):
    if t is None:
        dt = datetime.datetime.utcnow()
    else:
        dt = datetime.datetime.utcfromtimestamp(t)
    return '%04d-%02d-%02d %02d:%02d:%02dZ' % (
     dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def time2netscape(t=None):
    if t is None:
        dt = datetime.datetime.utcnow()
    else:
        dt = datetime.datetime.utcfromtimestamp(t)
    return '%s, %02d-%s-%04d %02d:%02d:%02d GMT' % (
     DAYS[dt.weekday()], dt.day, MONTHS[dt.month - 1],
     dt.year, dt.hour, dt.minute, dt.second)


UTC_ZONES = {
 'GMT': None, 'UTC': None, 'UT': None, 'Z': None}
TIMEZONE_RE = re.compile('^([-+])?(\\d\\d?):?(\\d\\d)?$', re.ASCII)

def offset_from_tz_string(tz):
    offset = None
    if tz in UTC_ZONES:
        offset = 0
    else:
        m = TIMEZONE_RE.search(tz)
        if m:
            offset = 3600 * int(m.group(2))
            if m.group(3):
                offset = offset + 60 * int(m.group(3))
            if m.group(1) == '-':
                offset = -offset
    return offset


def _str2time(day, mon, yr, hr, min, sec, tz):
    yr = int(yr)
    if yr > datetime.MAXYEAR:
        return
    try:
        mon = MONTHS_LOWER.index(mon.lower()) + 1
    except ValueError:
        try:
            imon = int(mon)
        except ValueError:
            return
        else:
            if 1 <= imon <= 12:
                mon = imon
            else:
                return

    if hr is None:
        hr = 0
    elif min is None:
        min = 0
    else:
        if sec is None:
            sec = 0
        day = int(day)
        hr = int(hr)
        min = int(min)
        sec = int(sec)
        if yr < 1000:
            cur_yr = time.localtime(time.time())[0]
            m = cur_yr % 100
            tmp = yr
            yr = yr + cur_yr - m
            m = m - tmp
            if abs(m) > 50:
                if m > 0:
                    yr = yr + 100
                else:
                    yr = yr - 100
    t = _timegm((yr, mon, day, hr, min, sec, tz))
    if t is not None:
        if tz is None:
            tz = 'UTC'
        tz = tz.upper()
        offset = offset_from_tz_string(tz)
        if offset is None:
            return
        t = t - offset
    return t


STRICT_DATE_RE = re.compile('^[SMTWF][a-z][a-z], (\\d\\d) ([JFMASOND][a-z][a-z]) (\\d\\d\\d\\d) (\\d\\d):(\\d\\d):(\\d\\d) GMT$', re.ASCII)
WEEKDAY_RE = re.compile('^(?:Sun|Mon|Tue|Wed|Thu|Fri|Sat)[a-z]*,?\\s*', re.I | re.ASCII)
LOOSE_HTTP_DATE_RE = re.compile('^\n    (\\d\\d?)            # day\n       (?:\\s+|[-\\/])\n    (\\w+)              # month\n        (?:\\s+|[-\\/])\n    (\\d+)              # year\n    (?:\n          (?:\\s+|:)    # separator before clock\n       (\\d\\d?):(\\d\\d)  # hour:min\n       (?::(\\d\\d))?    # optional seconds\n    )?                 # optional clock\n       \\s*\n    ([-+]?\\d{2,4}|(?![APap][Mm]\\b)[A-Za-z]+)? # timezone\n       \\s*\n    (?:\\(\\w+\\))?       # ASCII representation of timezone in parens.\n       \\s*$', re.X | re.ASCII)

def http2time(text):
    m = STRICT_DATE_RE.search(text)
    if m:
        g = m.groups()
        mon = MONTHS_LOWER.index(g[1].lower()) + 1
        tt = (int(g[2]), mon, int(g[0]),
         int(g[3]), int(g[4]), float(g[5]))
        return _timegm(tt)
    text = text.lstrip()
    text = WEEKDAY_RE.sub('', text, 1)
    day, mon, yr, hr, min, sec, tz = [
     None] * 7
    m = LOOSE_HTTP_DATE_RE.search(text)
    if m is not None:
        day, mon, yr, hr, min, sec, tz = m.groups()
    else:
        return
        return _str2time(day, mon, yr, hr, min, sec, tz)


ISO_DATE_RE = re.compile('^\n    (\\d{4})              # year\n       [-\\/]?\n    (\\d\\d?)              # numerical month\n       [-\\/]?\n    (\\d\\d?)              # day\n   (?:\n         (?:\\s+|[-:Tt])  # separator before clock\n      (\\d\\d?):?(\\d\\d)    # hour:min\n      (?::?(\\d\\d(?:\\.\\d*)?))?  # optional seconds (and fractional)\n   )?                    # optional clock\n      \\s*\n   ([-+]?\\d\\d?:?(:?\\d\\d)?\n    |Z|z)?               # timezone  (Z is "zero meridian", i.e. GMT)\n      \\s*$', re.X | re.ASCII)

def iso2time(text):
    text = text.lstrip()
    day, mon, yr, hr, min, sec, tz = [
     None] * 7
    m = ISO_DATE_RE.search(text)
    if m is not None:
        yr, mon, day, hr, min, sec, tz, _ = m.groups()
    else:
        return
        return _str2time(day, mon, yr, hr, min, sec, tz)


def unmatched(match):
    start, end = match.span(0)
    return match.string[:start] + match.string[end:]


HEADER_TOKEN_RE = re.compile('^\\s*([^=\\s;,]+)')
HEADER_QUOTED_VALUE_RE = re.compile('^\\s*=\\s*\\"([^\\"\\\\]*(?:\\\\.[^\\"\\\\]*)*)\\"')
HEADER_VALUE_RE = re.compile('^\\s*=\\s*([^\\s;,]*)')
HEADER_ESCAPE_RE = re.compile('\\\\(.)')

def split_header_words(header_values):
    result = []
    for text in header_values:
        orig_text = text
        pairs = []
        while text:
            m = HEADER_TOKEN_RE.search(text)
            if m:
                text = unmatched(m)
                name = m.group(1)
                m = HEADER_QUOTED_VALUE_RE.search(text)
                if m:
                    text = unmatched(m)
                    value = m.group(1)
                    value = HEADER_ESCAPE_RE.sub('\\1', value)
                else:
                    m = HEADER_VALUE_RE.search(text)
                    if m:
                        text = unmatched(m)
                        value = m.group(1)
                        value = value.rstrip()
                    else:
                        value = None
                pairs.append((name, value))
            elif text.lstrip().startswith(','):
                text = text.lstrip()[1:]
                if pairs:
                    result.append(pairs)
                pairs = []
            else:
                non_junk, nr_junk_chars = re.subn('^[=\\s;]*', '', text)
                text = non_junk

        if pairs:
            result.append(pairs)

    return result


HEADER_JOIN_ESCAPE_RE = re.compile('([\\"\\\\])')

def join_header_words(lists):
    headers = []
    for pairs in lists:
        attr = []
        for k, v in pairs:
            if v is not None:
                if not re.search('^\\w+$', v):
                    v = HEADER_JOIN_ESCAPE_RE.sub('\\\\\\1', v)
                    v = '"%s"' % v
                k = '%s=%s' % (k, v)
            attr.append(k)

        if attr:
            headers.append('; '.join(attr))

    return ', '.join(headers)


def strip_quotes(text):
    if text.startswith('"'):
        text = text[1:]
    if text.endswith('"'):
        text = text[:-1]
    return text


def parse_ns_headers(ns_headers):
    known_attrs = ('expires', 'domain', 'path', 'secure', 'version', 'port', 'max-age')
    result = []
    for ns_header in ns_headers:
        pairs = []
        version_set = False
        for ii, param in enumerate(ns_header.split(';')):
            param = param.strip()
            key, sep, val = param.partition('=')
            key = key.strip()
            if not key:
                if ii == 0:
                    break
                else:
                    continue
                val = val.strip() if sep else None
                if ii != 0:
                    lc = key.lower()
                    if lc in known_attrs:
                        key = lc
                    if key == 'version':
                        if val is not None:
                            val = strip_quotes(val)
                        version_set = True
                    else:
                        if key == 'expires':
                            if val is not None:
                                val = http2time(strip_quotes(val))
                pairs.append((key, val))

        if pairs:
            if not version_set:
                pairs.append(('version', '0'))
            result.append(pairs)

    return result


IPV4_RE = re.compile('\\.\\d+$', re.ASCII)

def is_HDN(text):
    if IPV4_RE.search(text):
        return False
    if text == '':
        return False
    if text[0] == '.' or text[-1] == '.':
        return False
    return True


def domain_match(A, B):
    A = A.lower()
    B = B.lower()
    if A == B:
        return True
    else:
        if not is_HDN(A):
            return False
        else:
            i = A.rfind(B)
            if i == -1 or i == 0:
                return False
            return B.startswith('.') or False
        return is_HDN(B[1:]) or False
    return True


def liberal_is_HDN(text):
    if IPV4_RE.search(text):
        return False
    return True


def user_domain_match(A, B):
    A = A.lower()
    B = B.lower()
    if not (liberal_is_HDN(A) and liberal_is_HDN(B)):
        if A == B:
            return True
        return False
    initial_dot = B.startswith('.')
    if initial_dot:
        if A.endswith(B):
            return True
    if not initial_dot:
        if A == B:
            return True
    return False


cut_port_re = re.compile(':\\d+$', re.ASCII)

def request_host(request):
    url = request.get_full_url()
    host = urllib.parse.urlparse(url)[1]
    if host == '':
        host = request.get_header('Host', '')
    host = cut_port_re.sub('', host, 1)
    return host.lower()


def eff_request_host(request):
    erhn = req_host = request_host(request)
    if req_host.find('.') == -1:
        if not IPV4_RE.search(req_host):
            erhn = req_host + '.local'
    return (
     req_host, erhn)


def request_path(request):
    url = request.get_full_url()
    parts = urllib.parse.urlsplit(url)
    path = escape_path(parts.path)
    if not path.startswith('/'):
        path = '/' + path
    return path


def request_port(request):
    host = request.host
    i = host.find(':')
    if i >= 0:
        port = host[i + 1:]
        try:
            int(port)
        except ValueError:
            _debug("nonnumeric port: '%s'", port)
            return

    else:
        port = DEFAULT_HTTP_PORT
    return port


HTTP_PATH_SAFE = "%/;:@&=+$,!~*'()"
ESCAPED_CHAR_RE = re.compile('%([0-9a-fA-F][0-9a-fA-F])')

def uppercase_escaped_char(match):
    return '%%%s' % match.group(1).upper()


def escape_path(path):
    path = urllib.parse.quote(path, HTTP_PATH_SAFE)
    path = ESCAPED_CHAR_RE.sub(uppercase_escaped_char, path)
    return path


def reach(h):
    i = h.find('.')
    if i >= 0:
        b = h[i + 1:]
        i = b.find('.')
        if is_HDN(h):
            if i >= 0 or b == 'local':
                return '.' + b
    return h


def is_third_party(request):
    req_host = request_host(request)
    if not domain_match(req_host, reach(request.origin_req_host)):
        return True
    return False


class Cookie:

    def __init__(self, version, name, value, port, port_specified, domain, domain_specified, domain_initial_dot, path, path_specified, secure, expires, discard, comment, comment_url, rest, rfc2109=False):
        if version is not None:
            version = int(version)
        else:
            if expires is not None:
                expires = int(float(expires))
            if port is None and port_specified is True:
                raise ValueError('if port is None, port_specified must be false')
        self.version = version
        self.name = name
        self.value = value
        self.port = port
        self.port_specified = port_specified
        self.domain = domain.lower()
        self.domain_specified = domain_specified
        self.domain_initial_dot = domain_initial_dot
        self.path = path
        self.path_specified = path_specified
        self.secure = secure
        self.expires = expires
        self.discard = discard
        self.comment = comment
        self.comment_url = comment_url
        self.rfc2109 = rfc2109
        self._rest = copy.copy(rest)

    def has_nonstandard_attr(self, name):
        return name in self._rest

    def get_nonstandard_attr(self, name, default=None):
        return self._rest.get(name, default)

    def set_nonstandard_attr(self, name, value):
        self._rest[name] = value

    def is_expired(self, now=None):
        if now is None:
            now = time.time()
        if self.expires is not None:
            if self.expires <= now:
                return True
        return False

    def __str__(self):
        if self.port is None:
            p = ''
        else:
            p = ':' + self.port
        limit = self.domain + p + self.path
        if self.value is not None:
            namevalue = '%s=%s' % (self.name, self.value)
        else:
            namevalue = self.name
        return '<Cookie %s for %s>' % (namevalue, limit)

    def __repr__(self):
        args = []
        for name in ('version', 'name', 'value', 'port', 'port_specified', 'domain',
                     'domain_specified', 'domain_initial_dot', 'path', 'path_specified',
                     'secure', 'expires', 'discard', 'comment', 'comment_url'):
            attr = getattr(self, name)
            args.append('%s=%s' % (name, repr(attr)))

        args.append('rest=%s' % repr(self._rest))
        args.append('rfc2109=%s' % repr(self.rfc2109))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(args))


class CookiePolicy:

    def set_ok(self, cookie, request):
        raise NotImplementedError()

    def return_ok(self, cookie, request):
        raise NotImplementedError()

    def domain_return_ok(self, domain, request):
        return True

    def path_return_ok(self, path, request):
        return True


class DefaultCookiePolicy(CookiePolicy):
    DomainStrictNoDots = 1
    DomainStrictNonDomain = 2
    DomainRFC2965Match = 4
    DomainLiberal = 0
    DomainStrict = DomainStrictNoDots | DomainStrictNonDomain

    def __init__(self, blocked_domains=None, allowed_domains=None, netscape=True, rfc2965=False, rfc2109_as_netscape=None, hide_cookie2=False, strict_domain=False, strict_rfc2965_unverifiable=True, strict_ns_unverifiable=False, strict_ns_domain=DomainLiberal, strict_ns_set_initial_dollar=False, strict_ns_set_path=False):
        self.netscape = netscape
        self.rfc2965 = rfc2965
        self.rfc2109_as_netscape = rfc2109_as_netscape
        self.hide_cookie2 = hide_cookie2
        self.strict_domain = strict_domain
        self.strict_rfc2965_unverifiable = strict_rfc2965_unverifiable
        self.strict_ns_unverifiable = strict_ns_unverifiable
        self.strict_ns_domain = strict_ns_domain
        self.strict_ns_set_initial_dollar = strict_ns_set_initial_dollar
        self.strict_ns_set_path = strict_ns_set_path
        if blocked_domains is not None:
            self._blocked_domains = tuple(blocked_domains)
        else:
            self._blocked_domains = ()
        if allowed_domains is not None:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    def blocked_domains(self):
        return self._blocked_domains

    def set_blocked_domains(self, blocked_domains):
        self._blocked_domains = tuple(blocked_domains)

    def is_blocked(self, domain):
        for blocked_domain in self._blocked_domains:
            if user_domain_match(domain, blocked_domain):
                return True

        return False

    def allowed_domains(self):
        return self._allowed_domains

    def set_allowed_domains(self, allowed_domains):
        if allowed_domains is not None:
            allowed_domains = tuple(allowed_domains)
        self._allowed_domains = allowed_domains

    def is_not_allowed(self, domain):
        if self._allowed_domains is None:
            return False
        for allowed_domain in self._allowed_domains:
            if user_domain_match(domain, allowed_domain):
                return False

        return True

    def set_ok(self, cookie, request):
        _debug(' - checking cookie %s=%s', cookie.name, cookie.value)
        for n in ('version', 'verifiability', 'name', 'path', 'domain', 'port'):
            fn_name = 'set_ok_' + n
            fn = getattr(self, fn_name)
            if not fn(cookie, request):
                return False

        return True

    def set_ok_version(self, cookie, request):
        if cookie.version is None:
            _debug('   Set-Cookie2 without version attribute (%s=%s)', cookie.name, cookie.value)
            return False
        else:
            if cookie.version > 0:
                if not self.rfc2965:
                    _debug('   RFC 2965 cookies are switched off')
                    return False
            if cookie.version == 0:
                self.netscape or _debug('   Netscape cookies are switched off')
                return False
        return True

    def set_ok_verifiability(self, cookie, request):
        if request.unverifiable:
            if is_third_party(request):
                if cookie.version > 0:
                    if self.strict_rfc2965_unverifiable:
                        _debug('   third-party RFC 2965 cookie during unverifiable transaction')
                        return False
                if cookie.version == 0:
                    if self.strict_ns_unverifiable:
                        _debug('   third-party Netscape cookie during unverifiable transaction')
                        return False
        return True

    def set_ok_name(self, cookie, request):
        if cookie.version == 0:
            if self.strict_ns_set_initial_dollar:
                if cookie.name.startswith('$'):
                    _debug("   illegal name (starts with '$'): '%s'", cookie.name)
                    return False
        return True

    def set_ok_path(self, cookie, request):
        if cookie.path_specified:
            req_path = request_path(request)
            if (cookie.version > 0 or cookie.version) == 0:
                if self.strict_ns_set_path:
                    if not req_path.startswith(cookie.path):
                        _debug('   path attribute %s is not a prefix of request path %s', cookie.path, req_path)
                        return False
        return True

    def set_ok_domain(self, cookie, request):
        if self.is_blocked(cookie.domain):
            _debug('   domain %s is in user block-list', cookie.domain)
            return False
        if self.is_not_allowed(cookie.domain):
            _debug('   domain %s is not in user allow-list', cookie.domain)
            return False
        if cookie.domain_specified:
            req_host, erhn = eff_request_host(request)
            domain = cookie.domain
            if self.strict_domain:
                if domain.count('.') >= 2:
                    i = domain.rfind('.')
                    j = domain.rfind('.', 0, i)
                    if j == 0:
                        tld = domain[i + 1:]
                        sld = domain[j + 1:i]
                        if sld.lower() in ('co', 'ac', 'com', 'edu', 'org', 'net',
                                           'gov', 'mil', 'int', 'aero', 'biz', 'cat',
                                           'coop', 'info', 'jobs', 'mobi', 'museum',
                                           'name', 'pro', 'travel', 'eu'):
                            if len(tld) == 2:
                                _debug('   country-code second level domain %s', domain)
                                return False
            elif domain.startswith('.'):
                undotted_domain = domain[1:]
            else:
                undotted_domain = domain
            embedded_dots = undotted_domain.find('.') >= 0
            if not embedded_dots:
                if domain != '.local':
                    _debug('   non-local domain %s contains no embedded dot', domain)
                    return False
            if cookie.version == 0 and not erhn.endswith(domain) or erhn.startswith('.'):
                if not ('.' + erhn).endswith(domain):
                    _debug('   effective request-host %s (even with added initial dot) does not end with %s', erhn, domain)
                    return False
                else:
                    if cookie.version > 0 or self.strict_ns_domain & self.DomainRFC2965Match:
                        if not domain_match(erhn, domain):
                            _debug('   effective request-host %s does not domain-match %s', erhn, domain)
                            return False
                    if cookie.version > 0 or self.strict_ns_domain & self.DomainStrictNoDots:
                        host_prefix = req_host[:-len(domain)]
                        if host_prefix.find('.') >= 0:
                            if not IPV4_RE.search(req_host):
                                _debug('   host prefix %s for domain %s contains a dot', host_prefix, domain)
                                return False
        return True

    def set_ok_port(self, cookie, request):
        if cookie.port_specified:
            req_port = request_port(request)
            if req_port is None:
                req_port = '80'
            else:
                req_port = str(req_port)
            for p in cookie.port.split(','):
                try:
                    int(p)
                except ValueError:
                    _debug('   bad port %s (not numeric)', p)
                    return False
                else:
                    if p == req_port:
                        break
            else:
                _debug('   request port (%s) not found in %s', req_port, cookie.port)
                return False

        return True

    def return_ok(self, cookie, request):
        _debug(' - checking cookie %s=%s', cookie.name, cookie.value)
        for n in ('version', 'verifiability', 'secure', 'expires', 'port', 'domain'):
            fn_name = 'return_ok_' + n
            fn = getattr(self, fn_name)
            if not fn(cookie, request):
                return False

        return True

    def return_ok_version(self, cookie, request):
        if cookie.version > 0:
            if not self.rfc2965:
                _debug('   RFC 2965 cookies are switched off')
                return False
        if cookie.version == 0:
            if not self.netscape:
                _debug('   Netscape cookies are switched off')
                return False
        return True

    def return_ok_verifiability(self, cookie, request):
        if request.unverifiable:
            if is_third_party(request):
                if cookie.version > 0:
                    if self.strict_rfc2965_unverifiable:
                        _debug('   third-party RFC 2965 cookie during unverifiable transaction')
                        return False
                if cookie.version == 0:
                    if self.strict_ns_unverifiable:
                        _debug('   third-party Netscape cookie during unverifiable transaction')
                        return False
        return True

    def return_ok_secure(self, cookie, request):
        if cookie.secure:
            if request.type != 'https':
                _debug('   secure cookie with non-secure request')
                return False
        return True

    def return_ok_expires(self, cookie, request):
        if cookie.is_expired(self._now):
            _debug('   cookie expired')
            return False
        return True

    def return_ok_port(self, cookie, request):
        if cookie.port:
            req_port = request_port(request)
            if req_port is None:
                req_port = '80'
            for p in cookie.port.split(','):
                if p == req_port:
                    break
            else:
                _debug('   request port %s does not match cookie port %s', req_port, cookie.port)
                return False

        return True

    def return_ok_domain(self, cookie, request):
        req_host, erhn = eff_request_host(request)
        domain = cookie.domain
        if cookie.version == 0:
            if self.strict_ns_domain & self.DomainStrictNonDomain:
                if not cookie.domain_specified:
                    if domain != erhn:
                        _debug('   cookie with unspecified domain does not string-compare equal to request domain')
                        return False
        if cookie.version > 0:
            if not domain_match(erhn, domain):
                _debug('   effective request-host name %s does not domain-match RFC 2965 cookie domain %s', erhn, domain)
                return False
        if cookie.version == 0:
            if not ('.' + erhn).endswith(domain):
                _debug('   request-host %s does not match Netscape cookie domain %s', req_host, domain)
                return False
        return True

    def domain_return_ok(self, domain, request):
        req_host, erhn = eff_request_host(request)
        if not req_host.startswith('.'):
            req_host = '.' + req_host
        if not erhn.startswith('.'):
            erhn = '.' + erhn
        if not req_host.endswith(domain):
            if not erhn.endswith(domain):
                return False
        if self.is_blocked(domain):
            _debug('   domain %s is in user block-list', domain)
            return False
        if self.is_not_allowed(domain):
            _debug('   domain %s is not in user allow-list', domain)
            return False
        return True

    def path_return_ok(self, path, request):
        _debug('- checking cookie path=%s', path)
        req_path = request_path(request)
        if not req_path.startswith(path):
            _debug('  %s does not path-match %s', req_path, path)
            return False
        return True


def vals_sorted_by_key(adict):
    keys = sorted(adict.keys())
    return map(adict.get, keys)


def deepvalues(mapping):
    values = vals_sorted_by_key(mapping)
    for obj in values:
        mapping = False
        try:
            obj.items
        except AttributeError:
            pass
        else:
            mapping = True
            yield from deepvalues(obj)
        if not mapping:
            yield obj


class Absent:
    pass


class CookieJar:
    non_word_re = re.compile('\\W')
    quote_re = re.compile('([\\"\\\\])')
    strict_domain_re = re.compile('\\.?[^.]*')
    domain_re = re.compile('[^.]*')
    dots_re = re.compile('^\\.+')
    magic_re = re.compile('^\\#LWP-Cookies-(\\d+\\.\\d+)', re.ASCII)

    def __init__(self, policy=None):
        if policy is None:
            policy = DefaultCookiePolicy()
        self._policy = policy
        self._cookies_lock = _threading.RLock()
        self._cookies = {}

    def set_policy(self, policy):
        self._policy = policy

    def _cookies_for_domain(self, domain, request):
        cookies = []
        if not self._policy.domain_return_ok(domain, request):
            return []
        _debug('Checking %s for cookies to return', domain)
        cookies_by_path = self._cookies[domain]
        for path in cookies_by_path.keys():
            if not self._policy.path_return_ok(path, request):
                continue
            cookies_by_name = cookies_by_path[path]
            for cookie in cookies_by_name.values():
                if not self._policy.return_ok(cookie, request):
                    _debug('   not returning cookie')
                    continue
                _debug("   it's a match")
                cookies.append(cookie)

        return cookies

    def _cookies_for_request(self, request):
        cookies = []
        for domain in self._cookies.keys():
            cookies.extend(self._cookies_for_domain(domain, request))

        return cookies

    def _cookie_attrs(self, cookies):
        cookies.sort(key=(lambda a: len(a.path)), reverse=True)
        version_set = False
        attrs = []
        for cookie in cookies:
            version = cookie.version
            if not version_set:
                version_set = True
                if version > 0:
                    attrs.append('$Version=%s' % version)
            if cookie.value is not None:
                if self.non_word_re.search(cookie.value):
                    if version > 0:
                        value = self.quote_re.sub('\\\\\\1', cookie.value)
                    else:
                        value = cookie.value
                elif cookie.value is None:
                    attrs.append(cookie.name)
                else:
                    attrs.append('%s=%s' % (cookie.name, value))
                if version > 0:
                    if cookie.path_specified:
                        attrs.append('$Path="%s"' % cookie.path)
                    if cookie.domain.startswith('.'):
                        domain = cookie.domain
                        if not cookie.domain_initial_dot:
                            if domain.startswith('.'):
                                domain = domain[1:]
                        attrs.append('$Domain="%s"' % domain)
                    if cookie.port is not None:
                        p = '$Port'
                        if cookie.port_specified:
                            p = p + '="%s"' % cookie.port
                        attrs.append(p)

        return attrs

    def add_cookie_header(self, request):
        _debug('add_cookie_header')
        self._cookies_lock.acquire()
        try:
            self._policy._now = self._now = int(time.time())
            cookies = self._cookies_for_request(request)
            attrs = self._cookie_attrs(cookies)
            if attrs:
                if not request.has_header('Cookie'):
                    request.add_unredirected_header('Cookie', '; '.join(attrs))
            if self._policy.rfc2965:
                if not self._policy.hide_cookie2:
                    if not request.has_header('Cookie2'):
                        for cookie in cookies:
                            if cookie.version != 1:
                                request.add_unredirected_header('Cookie2', '$Version="1"')
                                break

        finally:
            self._cookies_lock.release()

        self.clear_expired_cookies()

    def _normalized_cookie_tuples(self, attrs_set):
        cookie_tuples = []
        boolean_attrs = ('discard', 'secure')
        value_attrs = ('version', 'expires', 'max-age', 'domain', 'path', 'port', 'comment',
                       'commenturl')
        for cookie_attrs in attrs_set:
            name, value = cookie_attrs[0]
            max_age_set = False
            bad_cookie = False
            standard = {}
            rest = {}
            for k, v in cookie_attrs[1:]:
                lc = k.lower()
                if not lc in value_attrs:
                    if lc in boolean_attrs:
                        k = lc
                    if k in boolean_attrs:
                        if v is None:
                            v = True
                        else:
                            if k in standard:
                                continue
                            if k == 'domain':
                                if v is None:
                                    _debug('   missing value for domain attribute')
                                    bad_cookie = True
                                    break
                                v = v.lower()
                            if k == 'expires':
                                if max_age_set:
                                    continue
                                if v is None:
                                    _debug('   missing or invalid value for expires attribute: treating as session cookie')
                                    continue
                        if k == 'max-age':
                            max_age_set = True
                            try:
                                v = int(v)
                            except ValueError:
                                _debug('   missing or invalid (non-numeric) value for max-age attribute')
                                bad_cookie = True
                                break

                            k = 'expires'
                            v = self._now + v
                        if k in value_attrs or k in boolean_attrs:
                            if v is None:
                                if k not in ('port', 'comment', 'commenturl'):
                                    _debug('   missing value for %s attribute' % k)
                                    bad_cookie = True
                                    break
                            standard[k] = v
                    else:
                        rest[k] = v

            if bad_cookie:
                continue
            cookie_tuples.append((name, value, standard, rest))

        return cookie_tuples

    def _cookie_from_cookie_tuple(self, tup, request):
        name, value, standard, rest = tup
        domain = standard.get('domain', Absent)
        path = standard.get('path', Absent)
        port = standard.get('port', Absent)
        expires = standard.get('expires', Absent)
        version = standard.get('version', None)
        if version is not None:
            try:
                version = int(version)
            except ValueError:
                return

        secure = standard.get('secure', False)
        discard = standard.get('discard', False)
        comment = standard.get('comment', None)
        comment_url = standard.get('commenturl', None)
        if path is not Absent and path != '':
            path_specified = True
            path = escape_path(path)
        else:
            path_specified = False
            path = request_path(request)
            i = path.rfind('/')
            if i != -1:
                if version == 0:
                    path = path[:i]
                else:
                    path = path[:i + 1]
            if len(path) == 0:
                path = '/'
            domain_specified = domain is not Absent
            domain_initial_dot = False
            if domain_specified:
                domain_initial_dot = bool(domain.startswith('.'))
        if domain is Absent:
            req_host, erhn = eff_request_host(request)
            domain = erhn
        else:
            if not domain.startswith('.'):
                domain = '.' + domain
            port_specified = False
            if port is not Absent:
                if port is None:
                    port = request_port(request)
                else:
                    port_specified = True
                    port = re.sub('\\s+', '', port)
            else:
                port = None
        if expires is Absent:
            expires = None
            discard = True
        else:
            if expires <= self._now:
                try:
                    self.clear(domain, path, name)
                except KeyError:
                    pass

                _debug("Expiring cookie, domain='%s', path='%s', name='%s'", domain, path, name)
                return
            return Cookie(version, name, value, port, port_specified, domain, domain_specified, domain_initial_dot, path, path_specified, secure, expires, discard, comment, comment_url, rest)

    def _cookies_from_attrs_set(self, attrs_set, request):
        cookie_tuples = self._normalized_cookie_tuples(attrs_set)
        cookies = []
        for tup in cookie_tuples:
            cookie = self._cookie_from_cookie_tuple(tup, request)
            if cookie:
                cookies.append(cookie)

        return cookies

    def _process_rfc2109_cookies(self, cookies):
        rfc2109_as_ns = getattr(self._policy, 'rfc2109_as_netscape', None)
        if rfc2109_as_ns is None:
            rfc2109_as_ns = not self._policy.rfc2965
        for cookie in cookies:
            if cookie.version == 1:
                cookie.rfc2109 = True
                if rfc2109_as_ns:
                    cookie.version = 0

    def make_cookies--- This code section failed: ---

 L.1577         0  LOAD_FAST                'response'
                2  LOAD_METHOD              info
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  STORE_FAST               'headers'

 L.1578         8  LOAD_FAST                'headers'
               10  LOAD_METHOD              get_all
               12  LOAD_STR                 'Set-Cookie2'
               14  BUILD_LIST_0          0 
               16  CALL_METHOD_2         2  '2 positional arguments'
               18  STORE_FAST               'rfc2965_hdrs'

 L.1579        20  LOAD_FAST                'headers'
               22  LOAD_METHOD              get_all
               24  LOAD_STR                 'Set-Cookie'
               26  BUILD_LIST_0          0 
               28  CALL_METHOD_2         2  '2 positional arguments'
               30  STORE_FAST               'ns_hdrs'

 L.1581        32  LOAD_FAST                'self'
               34  LOAD_ATTR                _policy
               36  LOAD_ATTR                rfc2965
               38  STORE_FAST               'rfc2965'

 L.1582        40  LOAD_FAST                'self'
               42  LOAD_ATTR                _policy
               44  LOAD_ATTR                netscape
               46  STORE_FAST               'netscape'

 L.1584        48  LOAD_FAST                'rfc2965_hdrs'
               50  POP_JUMP_IF_TRUE     56  'to 56'
               52  LOAD_FAST                'ns_hdrs'
               54  POP_JUMP_IF_FALSE    80  'to 80'
             56_0  COME_FROM            50  '50'

 L.1585        56  LOAD_FAST                'ns_hdrs'
               58  POP_JUMP_IF_TRUE     64  'to 64'
               60  LOAD_FAST                'rfc2965'
               62  POP_JUMP_IF_FALSE    80  'to 80'
             64_0  COME_FROM            58  '58'

 L.1586        64  LOAD_FAST                'rfc2965_hdrs'
               66  POP_JUMP_IF_TRUE     72  'to 72'
               68  LOAD_FAST                'netscape'
               70  POP_JUMP_IF_FALSE    80  'to 80'
             72_0  COME_FROM            66  '66'

 L.1587        72  LOAD_FAST                'netscape'
               74  POP_JUMP_IF_TRUE     84  'to 84'
               76  LOAD_FAST                'rfc2965'
               78  POP_JUMP_IF_TRUE     84  'to 84'
             80_0  COME_FROM            70  '70'
             80_1  COME_FROM            62  '62'
             80_2  COME_FROM            54  '54'

 L.1588        80  BUILD_LIST_0          0 
               82  RETURN_VALUE     
             84_0  COME_FROM            78  '78'
             84_1  COME_FROM            74  '74'

 L.1590        84  SETUP_EXCEPT        106  'to 106'

 L.1591        86  LOAD_FAST                'self'
               88  LOAD_METHOD              _cookies_from_attrs_set

 L.1592        90  LOAD_GLOBAL              split_header_words
               92  LOAD_FAST                'rfc2965_hdrs'
               94  CALL_FUNCTION_1       1  '1 positional argument'
               96  LOAD_FAST                'request'
               98  CALL_METHOD_2         2  '2 positional arguments'
              100  STORE_FAST               'cookies'
              102  POP_BLOCK        
              104  JUMP_FORWARD        136  'to 136'
            106_0  COME_FROM_EXCEPT     84  '84'

 L.1593       106  DUP_TOP          
              108  LOAD_GLOBAL              Exception
              110  COMPARE_OP               exception-match
              112  POP_JUMP_IF_FALSE   134  'to 134'
              114  POP_TOP          
              116  POP_TOP          
              118  POP_TOP          

 L.1594       120  LOAD_GLOBAL              _warn_unhandled_exception
              122  CALL_FUNCTION_0       0  '0 positional arguments'
              124  POP_TOP          

 L.1595       126  BUILD_LIST_0          0 
              128  STORE_FAST               'cookies'
              130  POP_EXCEPT       
              132  JUMP_FORWARD        136  'to 136'
            134_0  COME_FROM           112  '112'
              134  END_FINALLY      
            136_0  COME_FROM           132  '132'
            136_1  COME_FROM           104  '104'

 L.1597       136  LOAD_FAST                'ns_hdrs'
          138_140  POP_JUMP_IF_FALSE   292  'to 292'
              142  LOAD_FAST                'netscape'
          144_146  POP_JUMP_IF_FALSE   292  'to 292'

 L.1598       148  SETUP_EXCEPT        170  'to 170'

 L.1600       150  LOAD_FAST                'self'
              152  LOAD_METHOD              _cookies_from_attrs_set

 L.1601       154  LOAD_GLOBAL              parse_ns_headers
              156  LOAD_FAST                'ns_hdrs'
              158  CALL_FUNCTION_1       1  '1 positional argument'
              160  LOAD_FAST                'request'
              162  CALL_METHOD_2         2  '2 positional arguments'
              164  STORE_FAST               'ns_cookies'
              166  POP_BLOCK        
              168  JUMP_FORWARD        200  'to 200'
            170_0  COME_FROM_EXCEPT    148  '148'

 L.1602       170  DUP_TOP          
              172  LOAD_GLOBAL              Exception
              174  COMPARE_OP               exception-match
              176  POP_JUMP_IF_FALSE   198  'to 198'
              178  POP_TOP          
              180  POP_TOP          
              182  POP_TOP          

 L.1603       184  LOAD_GLOBAL              _warn_unhandled_exception
              186  CALL_FUNCTION_0       0  '0 positional arguments'
              188  POP_TOP          

 L.1604       190  BUILD_LIST_0          0 
              192  STORE_FAST               'ns_cookies'
              194  POP_EXCEPT       
              196  JUMP_FORWARD        200  'to 200'
            198_0  COME_FROM           176  '176'
              198  END_FINALLY      
            200_0  COME_FROM           196  '196'
            200_1  COME_FROM           168  '168'

 L.1605       200  LOAD_FAST                'self'
              202  LOAD_METHOD              _process_rfc2109_cookies
              204  LOAD_FAST                'ns_cookies'
              206  CALL_METHOD_1         1  '1 positional argument'
              208  POP_TOP          

 L.1613       210  LOAD_FAST                'rfc2965'
          212_214  POP_JUMP_IF_FALSE   276  'to 276'

 L.1614       216  BUILD_MAP_0           0 
              218  STORE_FAST               'lookup'

 L.1615       220  SETUP_LOOP          254  'to 254'
              222  LOAD_FAST                'cookies'
              224  GET_ITER         
              226  FOR_ITER            252  'to 252'
              228  STORE_FAST               'cookie'

 L.1616       230  LOAD_CONST               None
              232  LOAD_FAST                'lookup'
              234  LOAD_FAST                'cookie'
              236  LOAD_ATTR                domain
              238  LOAD_FAST                'cookie'
              240  LOAD_ATTR                path
              242  LOAD_FAST                'cookie'
              244  LOAD_ATTR                name
              246  BUILD_TUPLE_3         3 
              248  STORE_SUBSCR     
              250  JUMP_BACK           226  'to 226'
              252  POP_BLOCK        
            254_0  COME_FROM_LOOP      220  '220'

 L.1618       254  LOAD_FAST                'lookup'
              256  BUILD_TUPLE_1         1 
              258  LOAD_CODE                <code_object no_matching_rfc2965>
              260  LOAD_STR                 'CookieJar.make_cookies.<locals>.no_matching_rfc2965'
              262  MAKE_FUNCTION_1          'default'
              264  STORE_FAST               'no_matching_rfc2965'

 L.1621       266  LOAD_GLOBAL              filter
              268  LOAD_FAST                'no_matching_rfc2965'
              270  LOAD_FAST                'ns_cookies'
              272  CALL_FUNCTION_2       2  '2 positional arguments'
              274  STORE_FAST               'ns_cookies'
            276_0  COME_FROM           212  '212'

 L.1623       276  LOAD_FAST                'ns_cookies'
          278_280  POP_JUMP_IF_FALSE   292  'to 292'

 L.1624       282  LOAD_FAST                'cookies'
              284  LOAD_METHOD              extend
              286  LOAD_FAST                'ns_cookies'
              288  CALL_METHOD_1         1  '1 positional argument'
              290  POP_TOP          
            292_0  COME_FROM           278  '278'
            292_1  COME_FROM           144  '144'
            292_2  COME_FROM           138  '138'

 L.1626       292  LOAD_FAST                'cookies'
              294  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 84_1

    def set_cookie_if_ok(self, cookie, request):
        self._cookies_lock.acquire()
        try:
            self._policy._now = self._now = int(time.time())
            if self._policy.set_ok(cookie, request):
                self.set_cookie(cookie)
        finally:
            self._cookies_lock.release()

    def set_cookie(self, cookie):
        c = self._cookies
        self._cookies_lock.acquire()
        try:
            if cookie.domain not in c:
                c[cookie.domain] = {}
            c2 = c[cookie.domain]
            if cookie.path not in c2:
                c2[cookie.path] = {}
            c3 = c2[cookie.path]
            c3[cookie.name] = cookie
        finally:
            self._cookies_lock.release()

    def extract_cookies(self, response, request):
        _debug('extract_cookies: %s', response.info())
        self._cookies_lock.acquire()
        try:
            self._policy._now = self._now = int(time.time())
            for cookie in self.make_cookies(response, request):
                if self._policy.set_ok(cookie, request):
                    _debug(' setting cookie: %s', cookie)
                    self.set_cookie(cookie)

        finally:
            self._cookies_lock.release()

    def clear(self, domain=None, path=None, name=None):
        if name is not None and not domain is None:
            if path is None:
                raise ValueError('domain and path must be given to remove a cookie by name')
            del self._cookies[domain][path][name]
        else:
            if path is not None:
                if domain is None:
                    raise ValueError('domain must be given to remove cookies by path')
                del self._cookies[domain][path]
            else:
                if domain is not None:
                    del self._cookies[domain]
                else:
                    self._cookies = {}

    def clear_session_cookies(self):
        self._cookies_lock.acquire()
        try:
            for cookie in self:
                if cookie.discard:
                    self.clear(cookie.domain, cookie.path, cookie.name)

        finally:
            self._cookies_lock.release()

    def clear_expired_cookies(self):
        self._cookies_lock.acquire()
        try:
            now = time.time()
            for cookie in self:
                if cookie.is_expired(now):
                    self.clear(cookie.domain, cookie.path, cookie.name)

        finally:
            self._cookies_lock.release()

    def __iter__(self):
        return deepvalues(self._cookies)

    def __len__(self):
        i = 0
        for cookie in self:
            i = i + 1

        return i

    def __repr__(self):
        r = []
        for cookie in self:
            r.append(repr(cookie))

        return '<%s[%s]>' % (self.__class__.__name__, ', '.join(r))

    def __str__(self):
        r = []
        for cookie in self:
            r.append(str(cookie))

        return '<%s[%s]>' % (self.__class__.__name__, ', '.join(r))


class LoadError(OSError):
    pass


class FileCookieJar(CookieJar):

    def __init__(self, filename=None, delayload=False, policy=None):
        CookieJar.__init__(self, policy)
        if filename is not None:
            try:
                filename + ''
            except:
                raise ValueError('filename must be string-like')

        self.filename = filename
        self.delayload = bool(delayload)

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        raise NotImplementedError()

    def load(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        with open(filename) as (f):
            self._really_load(f, filename, ignore_discard, ignore_expires)

    def revert(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        self._cookies_lock.acquire()
        try:
            old_state = copy.deepcopy(self._cookies)
            self._cookies = {}
            try:
                self.load(filename, ignore_discard, ignore_expires)
            except OSError:
                self._cookies = old_state
                raise

        finally:
            self._cookies_lock.release()


def lwp_cookie_str(cookie):
    h = [
     (
      cookie.name, cookie.value),
     (
      'path', cookie.path),
     (
      'domain', cookie.domain)]
    if cookie.port is not None:
        h.append(('port', cookie.port))
    if cookie.path_specified:
        h.append(('path_spec', None))
    if cookie.port_specified:
        h.append(('port_spec', None))
    if cookie.domain_initial_dot:
        h.append(('domain_dot', None))
    if cookie.secure:
        h.append(('secure', None))
    if cookie.expires:
        h.append(('expires',
         time2isoz(float(cookie.expires))))
    if cookie.discard:
        h.append(('discard', None))
    if cookie.comment:
        h.append(('comment', cookie.comment))
    if cookie.comment_url:
        h.append(('commenturl', cookie.comment_url))
    keys = sorted(cookie._rest.keys())
    for k in keys:
        h.append((k, str(cookie._rest[k])))

    h.append(('version', str(cookie.version)))
    return join_header_words([h])


class LWPCookieJar(FileCookieJar):

    def as_lwp_str(self, ignore_discard=True, ignore_expires=True):
        now = time.time()
        r = []
        for cookie in self:
            if not ignore_discard:
                if cookie.discard:
                    continue
                elif not ignore_expires:
                    if cookie.is_expired(now):
                        continue
                r.append('Set-Cookie3: %s' % lwp_cookie_str(cookie))

        return '\n'.join(r + [''])

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        with open(filename, 'w') as (f):
            f.write('#LWP-Cookies-2.0\n')
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        if not self.magic_re.search(magic):
            msg = '%r does not look like a Set-Cookie3 (LWP) format file' % filename
            raise LoadError(msg)
        now = time.time()
        header = 'Set-Cookie3:'
        boolean_attrs = ('port_spec', 'path_spec', 'domain_dot', 'secure', 'discard')
        value_attrs = ('version', 'port', 'path', 'domain', 'expires', 'comment', 'commenturl')
        try:
            while 1:
                line = f.readline()
                if line == '':
                    break
                if not line.startswith(header):
                    continue
                line = line[len(header):].strip()
                for data in split_header_words([line]):
                    name, value = data[0]
                    standard = {}
                    rest = {}
                    for k in boolean_attrs:
                        standard[k] = False

                    for k, v in data[1:]:
                        if k is not None:
                            lc = k.lower()
                        else:
                            lc = None
                        if not lc in value_attrs:
                            if lc in boolean_attrs:
                                k = lc
                            if k in boolean_attrs:
                                if v is None:
                                    v = True
                                standard[k] = v
                            elif k in value_attrs:
                                standard[k] = v
                            else:
                                rest[k] = v

                    h = standard.get
                    expires = h('expires')
                    discard = h('discard')
                    if expires is not None:
                        expires = iso2time(expires)
                    if expires is None:
                        discard = True
                    domain = h('domain')
                    domain_specified = domain.startswith('.')
                    c = Cookie(h('version'), name, value, h('port'), h('port_spec'), domain, domain_specified, h('domain_dot'), h('path'), h('path_spec'), h('secure'), expires, discard, h('comment'), h('commenturl'), rest)
                    if not ignore_discard:
                        if c.discard:
                            continue
                    if not ignore_expires:
                        if c.is_expired(now):
                            continue
                        self.set_cookie(c)

        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError('invalid Set-Cookie3 format file %r: %r' % (
             filename, line))


class MozillaCookieJar(FileCookieJar):
    magic_re = re.compile('#( Netscape)? HTTP Cookie File')
    header = '# Netscape HTTP Cookie File\n# http://curl.haxx.se/rfc/cookie_spec.html\n# This is a generated file!  Do not edit.\n\n'

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()
        magic = f.readline()
        if not self.magic_re.search(magic):
            raise LoadError('%r does not look like a Netscape format cookies file' % filename)
        try:
            while 1:
                line = f.readline()
                if line == '':
                    break
                if line.endswith('\n'):
                    line = line[:-1]
                if line.strip().startswith(('#', '$')) or line.strip() == '':
                    continue
                domain, domain_specified, path, secure, expires, name, value = line.split('\t')
                secure = secure == 'TRUE'
                domain_specified = domain_specified == 'TRUE'
                if name == '':
                    name = value
                    value = None
                initial_dot = domain.startswith('.')
                discard = False
                if expires == '':
                    expires = None
                    discard = True
                c = Cookie(0, name, value, None, False, domain, domain_specified, initial_dot, path, False, secure, expires, discard, None, None, {})
                if not ignore_discard:
                    if c.discard:
                        continue
                if not ignore_expires:
                    if c.is_expired(now):
                        continue
                    self.set_cookie(c)

        except OSError:
            raise
        except Exception:
            _warn_unhandled_exception()
            raise LoadError('invalid Netscape format cookies file %r: %r' % (
             filename, line))

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None:
                filename = self.filename
            else:
                raise ValueError(MISSING_FILENAME_TEXT)
        with open(filename, 'w') as (f):
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard:
                    if cookie.discard:
                        continue
                    elif not ignore_expires:
                        if cookie.is_expired(now):
                            continue
                        else:
                            if cookie.secure:
                                secure = 'TRUE'
                            else:
                                secure = 'FALSE'
                            if cookie.domain.startswith('.'):
                                initial_dot = 'TRUE'
                            else:
                                initial_dot = 'FALSE'
                        if cookie.expires is not None:
                            expires = str(cookie.expires)
                    else:
                        expires = ''
                    if cookie.value is None:
                        name = ''
                        value = cookie.name
                    else:
                        name = cookie.name
                        value = cookie.value
                    f.write('\t'.join([cookie.domain, initial_dot, cookie.path,
                     secure, expires, name, value]) + '\n')