# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\smtplib.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 45300 bytes
import socket, io, re, email.utils, email.message, email.generator, base64, hmac, copy, datetime, sys
from email.base64mime import body_encode as encode_base64
__all__ = [
 "'SMTPException'", "'SMTPServerDisconnected'", "'SMTPResponseException'", 
 "'SMTPSenderRefused'", 
 "'SMTPRecipientsRefused'", "'SMTPDataError'", 
 "'SMTPConnectError'", "'SMTPHeloError'", 
 "'SMTPAuthenticationError'", 
 "'quoteaddr'", "'quotedata'", "'SMTP'"]
SMTP_PORT = 25
SMTP_SSL_PORT = 465
CRLF = '\r\n'
bCRLF = b'\r\n'
_MAXLINE = 8192
OLDSTYLE_AUTH = re.compile('auth=(.*)', re.I)

class SMTPException(OSError):
    pass


class SMTPNotSupportedError(SMTPException):
    pass


class SMTPServerDisconnected(SMTPException):
    pass


class SMTPResponseException(SMTPException):

    def __init__(self, code, msg):
        self.smtp_code = code
        self.smtp_error = msg
        self.args = (code, msg)


class SMTPSenderRefused(SMTPResponseException):

    def __init__(self, code, msg, sender):
        self.smtp_code = code
        self.smtp_error = msg
        self.sender = sender
        self.args = (code, msg, sender)


class SMTPRecipientsRefused(SMTPException):

    def __init__(self, recipients):
        self.recipients = recipients
        self.args = (recipients,)


class SMTPDataError(SMTPResponseException):
    pass


class SMTPConnectError(SMTPResponseException):
    pass


class SMTPHeloError(SMTPResponseException):
    pass


class SMTPAuthenticationError(SMTPResponseException):
    pass


def quoteaddr(addrstring):
    displayname, addr = email.utils.parseaddr(addrstring)
    if (displayname, addr) == ('', ''):
        if addrstring.strip().startswith('<'):
            return addrstring
        return '<%s>' % addrstring
    return '<%s>' % addr


def _addr_only(addrstring):
    displayname, addr = email.utils.parseaddr(addrstring)
    if (displayname, addr) == ('', ''):
        return addrstring
    return addr


def quotedata(data):
    return re.sub('(?m)^\\.', '..', re.sub('(?:\\r\\n|\\n|\\r(?!\\n))', CRLF, data))


def _quote_periods(bindata):
    return re.sub(b'(?m)^\\.', b'..', bindata)


def _fix_eols(data):
    return re.sub('(?:\\r\\n|\\n|\\r(?!\\n))', CRLF, data)


try:
    import ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

class SMTP:
    debuglevel = 0
    file = None
    helo_resp = None
    ehlo_msg = 'ehlo'
    ehlo_resp = None
    does_esmtp = 0
    default_port = SMTP_PORT

    def __init__(self, host='', port=0, local_hostname=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
        self._host = host
        self.timeout = timeout
        self.esmtp_features = {}
        self.command_encoding = 'ascii'
        self.source_address = source_address
        if host:
            code, msg = self.connect(host, port)
            if code != 220:
                self.close()
                raise SMTPConnectError(code, msg)
        if local_hostname is not None:
            self.local_hostname = local_hostname
        else:
            fqdn = socket.getfqdn()
            if '.' in fqdn:
                self.local_hostname = fqdn
            else:
                addr = '127.0.0.1'
                try:
                    addr = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    pass

                self.local_hostname = '[%s]' % addr

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            try:
                code, message = self.docmd('QUIT')
                if code != 221:
                    raise SMTPResponseException(code, message)
            except SMTPServerDisconnected:
                pass

        finally:
            self.close()

    def set_debuglevel(self, debuglevel):
        self.debuglevel = debuglevel

    def _print_debug(self, *args):
        if self.debuglevel > 1:
            print(datetime.datetime.now().time(), *args, **{'file': sys.stderr})
        else:
            print(*args, **{'file': sys.stderr})

    def _get_socket(self, host, port, timeout):
        if self.debuglevel > 0:
            self._print_debug('connect: to', (host, port), self.source_address)
        return socket.create_connection((host, port), timeout, self.source_address)

    def connect(self, host='localhost', port=0, source_address=None):
        if source_address:
            self.source_address = source_address
        else:
            if not port:
                if host.find(':') == host.rfind(':'):
                    i = host.rfind(':')
                    if i >= 0:
                        host, port = host[:i], host[i + 1:]
                        try:
                            port = int(port)
                        except ValueError:
                            raise OSError('nonnumeric port')

            port = port or self.default_port
        if self.debuglevel > 0:
            self._print_debug('connect:', (host, port))
        self.sock = self._get_socket(host, port, self.timeout)
        self.file = None
        code, msg = self.getreply()
        if self.debuglevel > 0:
            self._print_debug('connect:', repr(msg))
        return (
         code, msg)

    def send(self, s):
        if self.debuglevel > 0:
            self._print_debug('send:', repr(s))
        if hasattr(self, 'sock') and self.sock:
            if isinstance(s, str):
                s = s.encode(self.command_encoding)
            try:
                self.sock.sendall(s)
            except OSError:
                self.close()
                raise SMTPServerDisconnected('Server not connected')

        else:
            raise SMTPServerDisconnected('please run connect() first')

    def putcmd(self, cmd, args=''):
        if args == '':
            str = '%s%s' % (cmd, CRLF)
        else:
            str = '%s %s%s' % (cmd, args, CRLF)
        self.send(str)

    def getreply(self):
        resp = []
        if self.file is None:
            self.file = self.sock.makefile('rb')
        while 1:
            try:
                line = self.file.readline(_MAXLINE + 1)
            except OSError as e:
                try:
                    self.close()
                    raise SMTPServerDisconnected('Connection unexpectedly closed: ' + str(e))
                finally:
                    e = None
                    del e

            if not line:
                self.close()
                raise SMTPServerDisconnected('Connection unexpectedly closed')
            if self.debuglevel > 0:
                self._print_debug('reply:', repr(line))
            if len(line) > _MAXLINE:
                self.close()
                raise SMTPResponseException(500, 'Line too long.')
            resp.append(line[4:].strip(b' \t\r\n'))
            code = line[:3]
            try:
                errcode = int(code)
            except ValueError:
                errcode = -1
                break

            if line[3:4] != b'-':
                break

        errmsg = (b'\n').join(resp)
        if self.debuglevel > 0:
            self._print_debug('reply: retcode (%s); Msg: %a' % (errcode, errmsg))
        return (
         errcode, errmsg)

    def docmd(self, cmd, args=''):
        self.putcmd(cmd, args)
        return self.getreply()

    def helo(self, name=''):
        self.putcmd('helo', name or self.local_hostname)
        code, msg = self.getreply()
        self.helo_resp = msg
        return (code, msg)

    def ehlo(self, name=''):
        self.esmtp_features = {}
        self.putcmd(self.ehlo_msg, name or self.local_hostname)
        code, msg = self.getreply()
        if code == -1:
            if len(msg) == 0:
                self.close()
                raise SMTPServerDisconnected('Server not connected')
        self.ehlo_resp = msg
        if code != 250:
            return (
             code, msg)
        self.does_esmtp = 1
        resp = self.ehlo_resp.decode('latin-1').split('\n')
        del resp[0]
        for each in resp:
            auth_match = OLDSTYLE_AUTH.match(each)
            if auth_match:
                self.esmtp_features['auth'] = self.esmtp_features.get('auth', '') + ' ' + auth_match.groups(0)[0]
                continue
            m = re.match('(?P<feature>[A-Za-z0-9][A-Za-z0-9\\-]*) ?', each)
            if m:
                feature = m.group('feature').lower()
                params = m.string[m.end('feature'):].strip()
                if feature == 'auth':
                    self.esmtp_features[feature] = self.esmtp_features.get(feature, '') + ' ' + params
                else:
                    self.esmtp_features[feature] = params

        return (
         code, msg)

    def has_extn(self, opt):
        return opt.lower() in self.esmtp_features

    def help(self, args=''):
        self.putcmd('help', args)
        return self.getreply()[1]

    def rset(self):
        self.command_encoding = 'ascii'
        return self.docmd('rset')

    def _rset(self):
        try:
            self.rset()
        except SMTPServerDisconnected:
            pass

    def noop(self):
        return self.docmd('noop')

    def mail(self, sender, options=[]):
        optionlist = ''
        if options:
            if self.does_esmtp:
                if any((x.lower() == 'smtputf8' for x in options)):
                    if self.has_extn('smtputf8'):
                        self.command_encoding = 'utf-8'
                    else:
                        raise SMTPNotSupportedError('SMTPUTF8 not supported by server')
                optionlist = ' ' + ' '.join(options)
        self.putcmd('mail', 'FROM:%s%s' % (quoteaddr(sender), optionlist))
        return self.getreply()

    def rcpt(self, recip, options=[]):
        optionlist = ''
        if options:
            if self.does_esmtp:
                optionlist = ' ' + ' '.join(options)
        self.putcmd('rcpt', 'TO:%s%s' % (quoteaddr(recip), optionlist))
        return self.getreply()

    def data(self, msg):
        self.putcmd('data')
        code, repl = self.getreply()
        if self.debuglevel > 0:
            self._print_debug('data:', (code, repl))
        if code != 354:
            raise SMTPDataError(code, repl)
        else:
            if isinstance(msg, str):
                msg = _fix_eols(msg).encode('ascii')
            q = _quote_periods(msg)
            if q[-2:] != bCRLF:
                q = q + bCRLF
            q = q + b'.' + bCRLF
            self.send(q)
            code, msg = self.getreply()
            if self.debuglevel > 0:
                self._print_debug('data:', (code, msg))
            return (
             code, msg)

    def verify(self, address):
        self.putcmd('vrfy', _addr_only(address))
        return self.getreply()

    vrfy = verify

    def expn(self, address):
        self.putcmd('expn', _addr_only(address))
        return self.getreply()

    def ehlo_or_helo_if_needed(self):
        if self.helo_resp is None:
            if self.ehlo_resp is None:
                if not 200 <= self.ehlo()[0] <= 299:
                    code, resp = self.helo()
                    if not 200 <= code <= 299:
                        raise SMTPHeloError(code, resp)

    def auth(self, mechanism, authobject, *, initial_response_ok=True):
        mechanism = mechanism.upper()
        initial_response = authobject() if initial_response_ok else None
        if initial_response is not None:
            response = encode_base64((initial_response.encode('ascii')), eol='')
            code, resp = self.docmd('AUTH', mechanism + ' ' + response)
        else:
            code, resp = self.docmd('AUTH', mechanism)
        if code == 334:
            challenge = base64.decodebytes(resp)
            response = encode_base64((authobject(challenge).encode('ascii')),
              eol='')
            code, resp = self.docmd(response)
        if code in (235, 503):
            return (
             code, resp)
        raise SMTPAuthenticationError(code, resp)

    def auth_cram_md5(self, challenge=None):
        if challenge is None:
            return
        return self.user + ' ' + hmac.HMAC(self.password.encode('ascii'), challenge, 'md5').hexdigest()

    def auth_plain(self, challenge=None):
        return '\x00%s\x00%s' % (self.user, self.password)

    def auth_login(self, challenge=None):
        if challenge is None:
            return self.user
        return self.password

    def login(self, user, password, *, initial_response_ok=True):
        self.ehlo_or_helo_if_needed()
        if not self.has_extn('auth'):
            raise SMTPNotSupportedError('SMTP AUTH extension not supported by server.')
        advertised_authlist = self.esmtp_features['auth'].split()
        preferred_auths = [
         'CRAM-MD5', 'PLAIN', 'LOGIN']
        authlist = [auth for auth in preferred_auths if auth in advertised_authlist]
        if not authlist:
            raise SMTPException('No suitable authentication method found.')
        self.user, self.password = user, password
        for authmethod in authlist:
            method_name = 'auth_' + authmethod.lower().replace('-', '_')
            try:
                code, resp = self.auth(authmethod,
                  (getattr(self, method_name)), initial_response_ok=initial_response_ok)
                if code in (235, 503):
                    return (
                     code, resp)
            except SMTPAuthenticationError as e:
                try:
                    last_exception = e
                finally:
                    e = None
                    del e

        raise last_exception

    def starttls(self, keyfile=None, certfile=None, context=None):
        self.ehlo_or_helo_if_needed()
        if not self.has_extn('starttls'):
            raise SMTPNotSupportedError('STARTTLS extension not supported by server.')
        else:
            resp, reply = self.docmd('STARTTLS')
            if resp == 220:
                if not _have_ssl:
                    raise RuntimeError('No SSL support included in this Python')
                else:
                    if context is not None:
                        if keyfile is not None:
                            raise ValueError('context and keyfile arguments are mutually exclusive')
                    if context is not None and certfile is not None:
                        raise ValueError('context and certfile arguments are mutually exclusive')
                if not keyfile is not None:
                    if certfile is not None:
                        import warnings
                        warnings.warn('keyfile and certfile are deprecated, use acustom context instead', DeprecationWarning, 2)
                    if context is None:
                        context = ssl._create_stdlib_context(certfile=certfile, keyfile=keyfile)
                    self.sock = context.wrap_socket((self.sock), server_hostname=(self._host))
                    self.file = None
                    self.helo_resp = None
                    self.ehlo_resp = None
                    self.esmtp_features = {}
                    self.does_esmtp = 0
                else:
                    pass
            raise SMTPResponseException(resp, reply)
        return (
         resp, reply)

    def sendmail(self, from_addr, to_addrs, msg, mail_options=[], rcpt_options=[]):
        self.ehlo_or_helo_if_needed()
        esmtp_opts = []
        if isinstance(msg, str):
            msg = _fix_eols(msg).encode('ascii')
        if self.does_esmtp:
            if self.has_extn('size'):
                esmtp_opts.append('size=%d' % len(msg))
            for option in mail_options:
                esmtp_opts.append(option)

        code, resp = self.mail(from_addr, esmtp_opts)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise SMTPSenderRefused(code, resp, from_addr)
        senderrs = {}
        if isinstance(to_addrs, str):
            to_addrs = [
             to_addrs]
        for each in to_addrs:
            code, resp = self.rcpt(each, rcpt_options)
            if code != 250:
                if code != 251:
                    senderrs[each] = (
                     code, resp)
            if code == 421:
                self.close()
                raise SMTPRecipientsRefused(senderrs)

        if len(senderrs) == len(to_addrs):
            self._rset()
            raise SMTPRecipientsRefused(senderrs)
        code, resp = self.data(msg)
        if code != 250:
            if code == 421:
                self.close()
            else:
                self._rset()
            raise SMTPDataError(code, resp)
        return senderrs

    def send_message(self, msg, from_addr=None, to_addrs=None, mail_options=[], rcpt_options={}):
        self.ehlo_or_helo_if_needed()
        resent = msg.get_all('Resent-Date')
        if resent is None:
            header_prefix = ''
        else:
            if len(resent) == 1:
                header_prefix = 'Resent-'
            else:
                raise ValueError("message has more than one 'Resent-' header block")
        if from_addr is None:
            from_addr = msg[header_prefix + 'Sender'] if header_prefix + 'Sender' in msg else msg[header_prefix + 'From']
            from_addr = email.utils.getaddresses([from_addr])[0][1]
        if to_addrs is None:
            addr_fields = [f for f in (msg[header_prefix + 'To'],
             msg[header_prefix + 'Bcc'],
             msg[header_prefix + 'Cc']) if f is not None]
            to_addrs = [a[1] for a in email.utils.getaddresses(addr_fields)]
        msg_copy = copy.copy(msg)
        del msg_copy['Bcc']
        del msg_copy['Resent-Bcc']
        international = False
        try:
            ''.join([from_addr, *to_addrs]).encode('ascii')
        except UnicodeEncodeError:
            if not self.has_extn('smtputf8'):
                raise SMTPNotSupportedError('One or more source or delivery addresses require internationalized email support, but the server does not advertise the required SMTPUTF8 capability')
            international = True

        with io.BytesIO() as (bytesmsg):
            if international:
                g = email.generator.BytesGenerator(bytesmsg,
                  policy=msg.policy.clone(utf8=True))
                mail_options += ['SMTPUTF8', 'BODY=8BITMIME']
            else:
                g = email.generator.BytesGenerator(bytesmsg)
            g.flatten(msg_copy, linesep='\r\n')
            flatmsg = bytesmsg.getvalue()
        return self.sendmail(from_addr, to_addrs, flatmsg, mail_options, rcpt_options)

    def close(self):
        try:
            file = self.file
            self.file = None
            if file:
                file.close()
        finally:
            sock = self.sock
            self.sock = None
            if sock:
                sock.close()

    def quit(self):
        res = self.docmd('quit')
        self.ehlo_resp = self.helo_resp = None
        self.esmtp_features = {}
        self.does_esmtp = False
        self.close()
        return res


if _have_ssl:

    class SMTP_SSL(SMTP):
        default_port = SMTP_SSL_PORT

        def __init__(self, host='', port=0, local_hostname=None, keyfile=None, certfile=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, context=None):
            if context is not None:
                if keyfile is not None:
                    raise ValueError('context and keyfile arguments are mutually exclusive')
            if context is not None:
                if certfile is not None:
                    raise ValueError('context and certfile arguments are mutually exclusive')
            if keyfile is not None or certfile is not None:
                import warnings
                warnings.warn('keyfile and certfile are deprecated, use acustom context instead', DeprecationWarning, 2)
            self.keyfile = keyfile
            self.certfile = certfile
            if context is None:
                context = ssl._create_stdlib_context(certfile=certfile, keyfile=keyfile)
            self.context = context
            SMTP.__init__(self, host, port, local_hostname, timeout, source_address)

        def _get_socket(self, host, port, timeout):
            if self.debuglevel > 0:
                self._print_debug('connect:', (host, port))
            new_socket = socket.create_connection((host, port), timeout, self.source_address)
            new_socket = self.context.wrap_socket(new_socket, server_hostname=(self._host))
            return new_socket


    __all__.append('SMTP_SSL')
LMTP_PORT = 2003

class LMTP(SMTP):
    ehlo_msg = 'lhlo'

    def __init__(self, host='', port=LMTP_PORT, local_hostname=None, source_address=None):
        SMTP.__init__(self, host, port, local_hostname=local_hostname, source_address=source_address)

    def connect(self, host='localhost', port=0, source_address=None):
        if host[0] != '/':
            return SMTP.connect(self, host, port, source_address=source_address)
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.file = None
            self.sock.connect(host)
        except OSError:
            if self.debuglevel > 0:
                self._print_debug('connect fail:', host)
            if self.sock:
                self.sock.close()
            self.sock = None
            raise

        code, msg = self.getreply()
        if self.debuglevel > 0:
            self._print_debug('connect:', msg)
        return (
         code, msg)


if __name__ == '__main__':

    def prompt(prompt):
        sys.stdout.write(prompt + ': ')
        sys.stdout.flush()
        return sys.stdin.readline().strip()


    fromaddr = prompt('From')
    toaddrs = prompt('To').split(',')
    print('Enter message, end with ^D:')
    msg = ''
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        msg = msg + line

    print('Message length is %d' % len(msg))
    server = SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()