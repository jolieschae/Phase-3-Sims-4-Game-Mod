# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\feedparser.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 23311 bytes
__all__ = [
 'FeedParser', 'BytesFeedParser']
import re
from email import errors
from email._policybase import compat32
from collections import deque
from io import StringIO
NLCRE = re.compile('\\r\\n|\\r|\\n')
NLCRE_bol = re.compile('(\\r\\n|\\r|\\n)')
NLCRE_eol = re.compile('(\\r\\n|\\r|\\n)\\Z')
NLCRE_crack = re.compile('(\\r\\n|\\r|\\n)')
headerRE = re.compile('^(From |[\\041-\\071\\073-\\176]*:|[\\t ])')
EMPTYSTRING = ''
NL = '\n'
NeedMoreData = object()

class BufferedSubFile(object):

    def __init__(self):
        self._partial = StringIO(newline='')
        self._lines = deque()
        self._eofstack = []
        self._closed = False

    def push_eof_matcher(self, pred):
        self._eofstack.append(pred)

    def pop_eof_matcher(self):
        return self._eofstack.pop()

    def close(self):
        self._partial.seek(0)
        self.pushlines(self._partial.readlines())
        self._partial.seek(0)
        self._partial.truncate()
        self._closed = True

    def readline(self):
        if not self._lines:
            if self._closed:
                return ''
            return NeedMoreData
        line = self._lines.popleft()
        for ateof in reversed(self._eofstack):
            if ateof(line):
                self._lines.appendleft(line)
                return ''

        return line

    def unreadline(self, line):
        self._lines.appendleft(line)

    def push(self, data):
        self._partial.write(data)
        if '\n' not in data:
            if '\r' not in data:
                return
        self._partial.seek(0)
        parts = self._partial.readlines()
        self._partial.seek(0)
        self._partial.truncate()
        if not parts[-1].endswith('\n'):
            self._partial.write(parts.pop())
        self.pushlines(parts)

    def pushlines(self, lines):
        self._lines.extend(lines)

    def __iter__(self):
        return self

    def __next__(self):
        line = self.readline()
        if line == '':
            raise StopIteration
        return line


class FeedParser:

    def __init__(self, _factory=None, *, policy=compat32):
        self.policy = policy
        self._old_style_factory = False
        if _factory is None:
            if policy.message_factory is None:
                from email.message import Message
                self._factory = Message
            else:
                self._factory = policy.message_factory
        else:
            self._factory = _factory
        try:
            _factory(policy=(self.policy))
        except TypeError:
            self._old_style_factory = True

        self._input = BufferedSubFile()
        self._msgstack = []
        self._parse = self._parsegen().__next__
        self._cur = None
        self._last = None
        self._headersonly = False

    def _set_headersonly(self):
        self._headersonly = True

    def feed(self, data):
        self._input.push(data)
        self._call_parse()

    def _call_parse(self):
        try:
            self._parse()
        except StopIteration:
            pass

    def close(self):
        self._input.close()
        self._call_parse()
        root = self._pop_message()
        if root.get_content_maintype() == 'multipart':
            if not root.is_multipart():
                defect = errors.MultipartInvariantViolationDefect()
                self.policy.handle_defect(root, defect)
        return root

    def _new_message(self):
        if self._old_style_factory:
            msg = self._factory()
        else:
            msg = self._factory(policy=(self.policy))
        if self._cur:
            if self._cur.get_content_type() == 'multipart/digest':
                msg.set_default_type('message/rfc822')
        if self._msgstack:
            self._msgstack[-1].attach(msg)
        self._msgstack.append(msg)
        self._cur = msg
        self._last = msg

    def _pop_message(self):
        retval = self._msgstack.pop()
        if self._msgstack:
            self._cur = self._msgstack[-1]
        else:
            self._cur = None
        return retval

    def _parsegen(self):
        self._new_message()
        headers = []
        for line in self._input:
            if line is NeedMoreData:
                yield NeedMoreData
                continue
            if not headerRE.match(line):
                if not NLCRE.match(line):
                    defect = errors.MissingHeaderBodySeparatorDefect()
                    self.policy.handle_defect(self._cur, defect)
                    self._input.unreadline(line)
                break
            headers.append(line)

        self._parse_headers(headers)
        if self._headersonly:
            lines = []
            while True:
                line = self._input.readline()
                if line is NeedMoreData:
                    yield NeedMoreData
                    continue
                if line == '':
                    break
                lines.append(line)

            self._cur.set_payload(EMPTYSTRING.join(lines))
            return
        if self._cur.get_content_type() == 'message/delivery-status':
            while True:
                self._input.push_eof_matcher(NLCRE.match)
                for retval in self._parsegen():
                    if retval is NeedMoreData:
                        yield NeedMoreData
                        continue
                    break

                msg = self._pop_message()
                self._input.pop_eof_matcher()
                while True:
                    line = self._input.readline()
                    if line is NeedMoreData:
                        yield NeedMoreData
                        continue
                    break

                while True:
                    line = self._input.readline()
                    if line is NeedMoreData:
                        yield NeedMoreData
                        continue
                    break

                if line == '':
                    break
                self._input.unreadline(line)

            return
        if self._cur.get_content_maintype() == 'message':
            for retval in self._parsegen():
                if retval is NeedMoreData:
                    yield NeedMoreData
                    continue
                break

            self._pop_message()
            return
        if self._cur.get_content_maintype() == 'multipart':
            boundary = self._cur.get_boundary()
            if boundary is None:
                defect = errors.NoBoundaryInMultipartDefect()
                self.policy.handle_defect(self._cur, defect)
                lines = []
                for line in self._input:
                    if line is NeedMoreData:
                        yield NeedMoreData
                        continue
                    lines.append(line)

                self._cur.set_payload(EMPTYSTRING.join(lines))
                return
            if self._cur.get('content-transfer-encoding', '8bit').lower() not in ('7bit',
                                                                                  '8bit',
                                                                                  'binary'):
                defect = errors.InvalidMultipartContentTransferEncodingDefect()
                self.policy.handle_defect(self._cur, defect)
            else:
                separator = '--' + boundary
                boundaryre = re.compile('(?P<sep>' + re.escape(separator) + ')(?P<end>--)?(?P<ws>[ \\t]*)(?P<linesep>\\r\\n|\\r|\\n)?$')
                capturing_preamble = True
                preamble = []
                linesep = False
                close_boundary_seen = False
                while True:
                    line = self._input.readline()
                    if line is NeedMoreData:
                        yield NeedMoreData
                        continue
                    if line == '':
                        break
                    mo = boundaryre.match(line)
                    if mo:
                        if mo.group('end'):
                            close_boundary_seen = True
                            linesep = mo.group('linesep')
                            break
                        elif capturing_preamble:
                            if preamble:
                                lastline = preamble[-1]
                                eolmo = NLCRE_eol.search(lastline)
                                if eolmo:
                                    preamble[-1] = lastline[:-len(eolmo.group(0))]
                                self._cur.preamble = EMPTYSTRING.join(preamble)
                            capturing_preamble = False
                            self._input.unreadline(line)
                            continue
                        else:
                            while 1:
                                line = self._input.readline()
                                if line is NeedMoreData:
                                    yield NeedMoreData
                                    continue
                                mo = boundaryre.match(line)
                                if not mo:
                                    self._input.unreadline(line)
                                    break

                            self._input.push_eof_matcher(boundaryre.match)
                            for retval in self._parsegen():
                                if retval is NeedMoreData:
                                    yield NeedMoreData
                                    continue
                                break

                            if self._last.get_content_maintype() == 'multipart':
                                epilogue = self._last.epilogue
                                if epilogue == '':
                                    self._last.epilogue = None
                            elif epilogue is not None:
                                mo = NLCRE_eol.search(epilogue)
                                if mo:
                                    end = len(mo.group(0))
                                    self._last.epilogue = epilogue[:-end]
                            else:
                                payload = self._last._payload
                                if isinstance(payload, str):
                                    mo = NLCRE_eol.search(payload)
                                    if mo:
                                        payload = payload[:-len(mo.group(0))]
                                        self._last._payload = payload
                        self._input.pop_eof_matcher()
                        self._pop_message()
                        self._last = self._cur
                    else:
                        preamble.append(line)

                if capturing_preamble:
                    defect = errors.StartBoundaryNotFoundDefect()
                    self.policy.handle_defect(self._cur, defect)
                    self._cur.set_payload(EMPTYSTRING.join(preamble))
                    epilogue = []
                    for line in self._input:
                        if line is NeedMoreData:
                            yield NeedMoreData
                            continue

                    self._cur.epilogue = EMPTYSTRING.join(epilogue)
                    return
                    if not close_boundary_seen:
                        defect = errors.CloseBoundaryNotFoundDefect()
                        self.policy.handle_defect(self._cur, defect)
                        return
                    if linesep:
                        epilogue = [
                         '']
                else:
                    epilogue = []
            for line in self._input:
                if line is NeedMoreData:
                    yield NeedMoreData
                    continue
                epilogue.append(line)

            if epilogue:
                firstline = epilogue[0]
                bolmo = NLCRE_bol.match(firstline)
                if bolmo:
                    epilogue[0] = firstline[len(bolmo.group(0)):]
            self._cur.epilogue = EMPTYSTRING.join(epilogue)
            return
        lines = []
        for line in self._input:
            if line is NeedMoreData:
                yield NeedMoreData
                continue
            lines.append(line)

        self._cur.set_payload(EMPTYSTRING.join(lines))

    def _parse_headers(self, lines):
        lastheader = ''
        lastvalue = []
        for lineno, line in enumerate(lines):
            if line[0] in ' \t':
                if not lastheader:
                    defect = errors.FirstHeaderLineIsContinuationDefect(line)
                    self.policy.handle_defect(self._cur, defect)
                    continue
                lastvalue.append(line)
                continue
            else:
                if lastheader:
                    (self._cur.set_raw)(*self.policy.header_source_parse(lastvalue))
                    lastheader, lastvalue = '', []
                if line.startswith('From '):
                    if lineno == 0:
                        mo = NLCRE_eol.search(line)
                        if mo:
                            line = line[:-len(mo.group(0))]
                        self._cur.set_unixfrom(line)
                        continue
                    else:
                        if lineno == len(lines) - 1:
                            self._input.unreadline(line)
                            return
                        defect = errors.MisplacedEnvelopeHeaderDefect(line)
                        self._cur.defects.append(defect)
                        continue
            i = line.find(':')
            if i == 0:
                defect = errors.InvalidHeaderDefect('Missing header name.')
                self._cur.defects.append(defect)
                continue
            lastheader = line[:i]
            lastvalue = [line]

        if lastheader:
            (self._cur.set_raw)(*self.policy.header_source_parse(lastvalue))


class BytesFeedParser(FeedParser):

    def feed(self, data):
        super().feed(data.decode('ascii', 'surrogateescape'))