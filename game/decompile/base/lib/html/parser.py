# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\html\parser.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 18191 bytes
import re, warnings, _markupbase
from html import unescape
__all__ = [
 'HTMLParser']
interesting_normal = re.compile('[&<]')
incomplete = re.compile('&[a-zA-Z#]')
entityref = re.compile('&([a-zA-Z][-.a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#(?:[0-9]+|[xX][0-9a-fA-F]+)[^0-9a-fA-F]')
starttagopen = re.compile('<[a-zA-Z]')
piclose = re.compile('>')
commentclose = re.compile('--\\s*>')
tagfind_tolerant = re.compile('([a-zA-Z][^\\t\\n\\r\\f />\\x00]*)(?:\\s|/(?!>))*')
attrfind_tolerant = re.compile('((?<=[\\\'"\\s/])[^\\s/>][^\\s/=>]*)(\\s*=+\\s*(\\\'[^\\\']*\\\'|"[^"]*"|(?![\\\'"])[^>\\s]*))?(?:\\s|/(?!>))*')
locatestarttagend_tolerant = re.compile('\n  <[a-zA-Z][^\\t\\n\\r\\f />\\x00]*       # tag name\n  (?:[\\s/]*                          # optional whitespace before attribute name\n    (?:(?<=[\'"\\s/])[^\\s/>][^\\s/=>]*  # attribute name\n      (?:\\s*=+\\s*                    # value indicator\n        (?:\'[^\']*\'                   # LITA-enclosed value\n          |"[^"]*"                   # LIT-enclosed value\n          |(?![\'"])[^>\\s]*           # bare value\n         )\n         (?:\\s*,)*                   # possibly followed by a comma\n       )?(?:\\s|/(?!>))*\n     )*\n   )?\n  \\s*                                # trailing whitespace\n', re.VERBOSE)
endendtag = re.compile('>')
endtagfind = re.compile('</\\s*([a-zA-Z][-.a-zA-Z0-9:_]*)\\s*>')

class HTMLParser(_markupbase.ParserBase):
    CDATA_CONTENT_ELEMENTS = ('script', 'style')

    def __init__(self, *, convert_charrefs=True):
        self.convert_charrefs = convert_charrefs
        self.reset()

    def reset(self):
        self.rawdata = ''
        self.lasttag = '???'
        self.interesting = interesting_normal
        self.cdata_elem = None
        _markupbase.ParserBase.reset(self)

    def feed(self, data):
        self.rawdata = self.rawdata + data
        self.goahead(0)

    def close(self):
        self.goahead(1)

    _HTMLParser__starttag_text = None

    def get_starttag_text(self):
        return self._HTMLParser__starttag_text

    def set_cdata_mode(self, elem):
        self.cdata_elem = elem.lower()
        self.interesting = re.compile('</\\s*%s\\s*>' % self.cdata_elem, re.I)

    def clear_cdata_mode(self):
        self.interesting = interesting_normal
        self.cdata_elem = None

    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            if self.convert_charrefs and not self.cdata_elem:
                j = rawdata.find('<', i)
                if j < 0:
                    amppos = rawdata.rfind('&', max(i, n - 34))
                    if amppos >= 0:
                        if not re.compile('[\\s;]').search(rawdata, amppos):
                            break
                    j = n
                else:
                    match = self.interesting.search(rawdata, i)
                    if match:
                        j = match.start()
                    else:
                        if self.cdata_elem:
                            break
                        j = n
                if i < j:
                    if self.convert_charrefs:
                        self.cdata_elem or self.handle_data(unescape(rawdata[i:j]))
                    else:
                        self.handle_data(rawdata[i:j])
                i = self.updatepos(i, j)
                if i == n:
                    break
            startswith = rawdata.startswith
            if startswith('<', i):
                if starttagopen.match(rawdata, i):
                    k = self.parse_starttag(i)
                else:
                    if startswith('</', i):
                        k = self.parse_endtag(i)
                    else:
                        if startswith('<!--', i):
                            k = self.parse_comment(i)
                        else:
                            if startswith('<?', i):
                                k = self.parse_pi(i)
                            else:
                                if startswith('<!', i):
                                    k = self.parse_html_declaration(i)
                                else:
                                    if i + 1 < n:
                                        self.handle_data('<')
                                        k = i + 1
                                    else:
                                        break
                if k < 0:
                    if not end:
                        break
                    else:
                        k = rawdata.find('>', i + 1)
                        if k < 0:
                            k = rawdata.find('<', i + 1)
                            if k < 0:
                                k = i + 1
                        else:
                            k += 1
                    if self.convert_charrefs:
                        self.cdata_elem or self.handle_data(unescape(rawdata[i:k]))
                else:
                    self.handle_data(rawdata[i:k])
                i = self.updatepos(i, k)
            elif startswith('&#', i):
                match = charref.match(rawdata, i)
                if match:
                    name = match.group()[2:-1]
                    self.handle_charref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                else:
                    if ';' in rawdata[i:]:
                        self.handle_data(rawdata[i:i + 2])
                        i = self.updatepos(i, i + 2)
                    break
            elif startswith('&', i):
                match = entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    k = match.end()
                    if not startswith(';', k - 1):
                        k = k - 1
                    i = self.updatepos(i, k)
                    continue
                else:
                    match = incomplete.match(rawdata, i)
                    if match:
                        if end:
                            if match.group() == rawdata[i:]:
                                k = match.end()
                                if k <= i:
                                    k = n
                                i = self.updatepos(i, i + 1)
                            break
                        else:
                            pass
                    if i + 1 < n:
                        self.handle_data('&')
                        i = self.updatepos(i, i + 1)
                    else:
                        break
                continue

        if end and i < n:
            if (self.cdata_elem or self).convert_charrefs:
                if not self.cdata_elem:
                    self.handle_data(unescape(rawdata[i:n]))
                else:
                    self.handle_data(rawdata[i:n])
            else:
                i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]

    def parse_html_declaration(self, i):
        rawdata = self.rawdata
        if rawdata[i:i + 4] == '<!--':
            return self.parse_comment(i)
        if rawdata[i:i + 3] == '<![':
            return self.parse_marked_section(i)
        if rawdata[i:i + 9].lower() == '<!doctype':
            gtpos = rawdata.find('>', i + 9)
            if gtpos == -1:
                return -1
            self.handle_decl(rawdata[i + 2:gtpos])
            return gtpos + 1
        return self.parse_bogus_comment(i)

    def parse_bogus_comment(self, i, report=1):
        rawdata = self.rawdata
        pos = rawdata.find('>', i + 2)
        if pos == -1:
            return -1
        if report:
            self.handle_comment(rawdata[i + 2:pos])
        return pos + 1

    def parse_pi(self, i):
        rawdata = self.rawdata
        match = piclose.search(rawdata, i + 2)
        if not match:
            return -1
        j = match.start()
        self.handle_pi(rawdata[i + 2:j])
        j = match.end()
        return j

    def parse_starttag(self, i):
        self._HTMLParser__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        rawdata = self.rawdata
        self._HTMLParser__starttag_text = rawdata[i:endpos]
        attrs = []
        match = tagfind_tolerant.match(rawdata, i + 1)
        k = match.end()
        self.lasttag = tag = match.group(1).lower()
        while k < endpos:
            m = attrfind_tolerant.match(rawdata, k)
            if not m:
                break
            attrname, rest, attrvalue = m.group(1, 2, 3)
            if not rest:
                attrvalue = None
            else:
                if not attrvalue[:1] == "'" == attrvalue[-1:]:
                    if attrvalue[:1] == '"' == attrvalue[-1:]:
                        attrvalue = attrvalue[1:-1]
            if attrvalue:
                attrvalue = unescape(attrvalue)
            attrs.append((attrname.lower(), attrvalue))
            k = m.end()

        end = rawdata[k:endpos].strip()
        if end not in ('>', '/>'):
            lineno, offset = self.getpos()
            if '\n' in self._HTMLParser__starttag_text:
                lineno = lineno + self._HTMLParser__starttag_text.count('\n')
                offset = len(self._HTMLParser__starttag_text) - self._HTMLParser__starttag_text.rfind('\n')
            else:
                offset = offset + len(self._HTMLParser__starttag_text)
            self.handle_data(rawdata[i:endpos])
            return endpos
        if end.endswith('/>'):
            self.handle_startendtag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            if tag in self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode(tag)
            return endpos

    def check_for_whole_start_tag(self, i):
        rawdata = self.rawdata
        m = locatestarttagend_tolerant.match(rawdata, i)
        if m:
            j = m.end()
            next = rawdata[j:j + 1]
            if next == '>':
                return j + 1
            if next == '/':
                if rawdata.startswith('/>', j):
                    return j + 2
                if rawdata.startswith('/', j):
                    return -1
                if j > i:
                    return j
                return i + 1
            if next == '':
                return -1
            if next in 'abcdefghijklmnopqrstuvwxyz=/ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                return -1
            if j > i:
                return j
            return i + 1
        raise AssertionError('we should not get here!')

    def parse_endtag(self, i):
        rawdata = self.rawdata
        match = endendtag.search(rawdata, i + 1)
        if not match:
            return -1
        gtpos = match.end()
        match = endtagfind.match(rawdata, i)
        if not match:
            if self.cdata_elem is not None:
                self.handle_data(rawdata[i:gtpos])
                return gtpos
            namematch = tagfind_tolerant.match(rawdata, i + 2)
            if not namematch:
                if rawdata[i:i + 3] == '</>':
                    return i + 3
                return self.parse_bogus_comment(i)
            tagname = namematch.group(1).lower()
            gtpos = rawdata.find('>', namematch.end())
            self.handle_endtag(tagname)
            return gtpos + 1
        elem = match.group(1).lower()
        if self.cdata_elem is not None:
            if elem != self.cdata_elem:
                self.handle_data(rawdata[i:gtpos])
                return gtpos
        self.handle_endtag(elem)
        self.clear_cdata_mode()
        return gtpos

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_charref(self, name):
        pass

    def handle_entityref(self, name):
        pass

    def handle_data(self, data):
        pass

    def handle_comment(self, data):
        pass

    def handle_decl(self, decl):
        pass

    def handle_pi(self, data):
        pass

    def unknown_decl(self, data):
        pass

    def unescape(self, s):
        warnings.warn('The unescape method is deprecated and will be removed in 3.5, use html.unescape() instead.', DeprecationWarning,
          stacklevel=2)
        return unescape(s)