# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\sre_parse.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 40351 bytes
from sre_constants import *
SPECIAL_CHARS = '.\\[{()*+?^$|'
REPEAT_CHARS = '*+?{'
DIGITS = frozenset('0123456789')
OCTDIGITS = frozenset('01234567')
HEXDIGITS = frozenset('0123456789abcdefABCDEF')
ASCIILETTERS = frozenset('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
WHITESPACE = frozenset(' \t\n\r\x0b\x0c')
_REPEATCODES = frozenset({MIN_REPEAT, MAX_REPEAT})
_UNITCODES = frozenset({'ANY', 'RANGE', 'IN', 'LITERAL', 'NOT_LITERAL', 'CATEGORY'})
ESCAPES = {'\\a':(
  LITERAL, ord('\x07')), 
 '\\b':(
  LITERAL, ord('\x08')), 
 '\\f':(
  LITERAL, ord('\x0c')), 
 '\\n':(
  LITERAL, ord('\n')), 
 '\\r':(
  LITERAL, ord('\r')), 
 '\\t':(
  LITERAL, ord('\t')), 
 '\\v':(
  LITERAL, ord('\x0b')), 
 '\\\\':(
  LITERAL, ord('\\'))}
CATEGORIES = {'\\A':(
  AT, AT_BEGINNING_STRING), 
 '\\b':(
  AT, AT_BOUNDARY), 
 '\\B':(
  AT, AT_NON_BOUNDARY), 
 '\\d':(
  IN, [(CATEGORY, CATEGORY_DIGIT)]), 
 '\\D':(
  IN, [(CATEGORY, CATEGORY_NOT_DIGIT)]), 
 '\\s':(
  IN, [(CATEGORY, CATEGORY_SPACE)]), 
 '\\S':(
  IN, [(CATEGORY, CATEGORY_NOT_SPACE)]), 
 '\\w':(
  IN, [(CATEGORY, CATEGORY_WORD)]), 
 '\\W':(
  IN, [(CATEGORY, CATEGORY_NOT_WORD)]), 
 '\\Z':(
  AT, AT_END_STRING)}
FLAGS = {
 'i': 'SRE_FLAG_IGNORECASE', 
 'L': 'SRE_FLAG_LOCALE', 
 'm': 'SRE_FLAG_MULTILINE', 
 's': 'SRE_FLAG_DOTALL', 
 'x': 'SRE_FLAG_VERBOSE', 
 'a': 'SRE_FLAG_ASCII', 
 't': 'SRE_FLAG_TEMPLATE', 
 'u': 'SRE_FLAG_UNICODE'}
TYPE_FLAGS = SRE_FLAG_ASCII | SRE_FLAG_LOCALE | SRE_FLAG_UNICODE
GLOBAL_FLAGS = SRE_FLAG_DEBUG | SRE_FLAG_TEMPLATE

class Verbose(Exception):
    pass


class Pattern:

    def __init__(self):
        self.flags = 0
        self.groupdict = {}
        self.groupwidths = [None]
        self.lookbehindgroups = None

    @property
    def groups(self):
        return len(self.groupwidths)

    def opengroup(self, name=None):
        gid = self.groups
        self.groupwidths.append(None)
        if self.groups > MAXGROUPS:
            raise error('too many groups')
        if name is not None:
            ogid = self.groupdict.get(name, None)
            if ogid is not None:
                raise error('redefinition of group name %r as group %d; was group %d' % (
                 name, gid, ogid))
            self.groupdict[name] = gid
        return gid

    def closegroup(self, gid, p):
        self.groupwidths[gid] = p.getwidth()

    def checkgroup(self, gid):
        return gid < self.groups and self.groupwidths[gid] is not None

    def checklookbehindgroup(self, gid, source):
        if self.lookbehindgroups is not None:
            if not self.checkgroup(gid):
                raise source.error('cannot refer to an open group')
            if gid >= self.lookbehindgroups:
                raise source.error('cannot refer to group defined in the same lookbehind subpattern')


class SubPattern:

    def __init__(self, pattern, data=None):
        self.pattern = pattern
        if data is None:
            data = []
        self.data = data
        self.width = None

    def dump(self, level=0):
        nl = True
        seqtypes = (tuple, list)
        for op, av in self.data:
            print((level * '  ' + str(op)), end='')
            if op is IN:
                print()
                for op, a in av:
                    print((level + 1) * '  ' + str(op), a)

            elif op is BRANCH:
                print()
                for i, a in enumerate(av[1]):
                    if i:
                        print(level * '  ' + 'OR')
                    a.dump(level + 1)

            elif op is GROUPREF_EXISTS:
                condgroup, item_yes, item_no = av
                print('', condgroup)
                item_yes.dump(level + 1)
                if item_no:
                    print(level * '  ' + 'ELSE')
                    item_no.dump(level + 1)
            elif isinstance(av, seqtypes):
                nl = False
                for a in av:
                    if isinstance(a, SubPattern):
                        if not nl:
                            print()
                        a.dump(level + 1)
                        nl = True
                    else:
                        if not nl:
                            print(' ', end='')
                        print(a, end='')
                        nl = False

                if not nl:
                    print()
            else:
                print('', av)

    def __repr__(self):
        return repr(self.data)

    def __len__(self):
        return len(self.data)

    def __delitem__(self, index):
        del self.data[index]

    def __getitem__(self, index):
        if isinstance(index, slice):
            return SubPattern(self.pattern, self.data[index])
        return self.data[index]

    def __setitem__(self, index, code):
        self.data[index] = code

    def insert(self, index, code):
        self.data.insert(index, code)

    def append(self, code):
        self.data.append(code)

    def getwidth(self):
        if self.width is not None:
            return self.width
        lo = hi = 0
        for op, av in self.data:
            if op is BRANCH:
                i = MAXREPEAT - 1
                j = 0
                for av in av[1]:
                    l, h = av.getwidth()
                    i = min(i, l)
                    j = max(j, h)

                lo = lo + i
                hi = hi + j
            elif op is CALL:
                i, j = av.getwidth()
                lo = lo + i
                hi = hi + j
            elif op is SUBPATTERN:
                i, j = av[-1].getwidth()
                lo = lo + i
                hi = hi + j
            elif op in _REPEATCODES:
                i, j = av[2].getwidth()
                lo = lo + i * av[0]
                hi = hi + j * av[1]
            elif op in _UNITCODES:
                lo = lo + 1
                hi = hi + 1
            elif op is GROUPREF:
                i, j = self.pattern.groupwidths[av]
                lo = lo + i
                hi = hi + j
            else:
                if op is GROUPREF_EXISTS:
                    i, j = av[1].getwidth()
                    if av[2] is not None:
                        l, h = av[2].getwidth()
                        i = min(i, l)
                        j = max(j, h)
                    else:
                        i = 0
                    lo = lo + i
                    hi = hi + j

        self.width = (
         min(lo, MAXREPEAT - 1), min(hi, MAXREPEAT))
        return self.width


class Tokenizer:

    def __init__(self, string):
        self.istext = isinstance(string, str)
        self.string = string
        if not self.istext:
            string = str(string, 'latin1')
        self.decoded_string = string
        self.index = 0
        self.next = None
        self._Tokenizer__next()

    def __next(self):
        index = self.index
        try:
            char = self.decoded_string[index]
        except IndexError:
            self.next = None
            return
        else:
            if char == '\\':
                index += 1
                try:
                    char += self.decoded_string[index]
                except IndexError:
                    raise error('bad escape (end of pattern)', self.string, len(self.string) - 1) from None

            self.index = index + 1
            self.next = char

    def match(self, char):
        if char == self.next:
            self._Tokenizer__next()
            return True
        return False

    def get(self):
        this = self.next
        self._Tokenizer__next()
        return this

    def getwhile(self, n, charset):
        result = ''
        for _ in range(n):
            c = self.next
            if c not in charset:
                break
            result += c
            self._Tokenizer__next()

        return result

    def getuntil(self, terminator):
        result = ''
        while True:
            c = self.next
            self._Tokenizer__next()
            if c is None:
                if not result:
                    raise self.error('missing group name')
                raise self.error('missing %s, unterminated name' % terminator, len(result))
            if c == terminator:
                if not result:
                    raise self.error('missing group name', 1)
                break
            result += c

        return result

    @property
    def pos(self):
        return self.index - len(self.next or '')

    def tell(self):
        return self.index - len(self.next or '')

    def seek(self, index):
        self.index = index
        self._Tokenizer__next()

    def error(self, msg, offset=0):
        return error(msg, self.string, self.tell() - offset)


def _class_escape(source, escape):
    code = ESCAPES.get(escape)
    if code:
        return code
    code = CATEGORIES.get(escape)
    if code:
        if code[0] is IN:
            return code
    try:
        c = escape[1:2]
        if c == 'x':
            escape += source.getwhile(2, HEXDIGITS)
            if len(escape) != 4:
                raise source.error('incomplete escape %s' % escape, len(escape))
            return (
             LITERAL, int(escape[2:], 16))
        if c == 'u':
            if source.istext:
                escape += source.getwhile(4, HEXDIGITS)
                if len(escape) != 6:
                    raise source.error('incomplete escape %s' % escape, len(escape))
                return (
                 LITERAL, int(escape[2:], 16))
        if c == 'U':
            if source.istext:
                escape += source.getwhile(8, HEXDIGITS)
                if len(escape) != 10:
                    raise source.error('incomplete escape %s' % escape, len(escape))
                c = int(escape[2:], 16)
                chr(c)
                return (LITERAL, c)
        if c in OCTDIGITS:
            escape += source.getwhile(2, OCTDIGITS)
            c = int(escape[1:], 8)
            if c > 255:
                raise source.error('octal escape value %s outside of range 0-0o377' % escape, len(escape))
            return (
             LITERAL, c)
        if c in DIGITS:
            raise ValueError
        if len(escape) == 2:
            if c in ASCIILETTERS:
                raise source.error('bad escape %s' % escape, len(escape))
            return (
             LITERAL, ord(escape[1]))
    except ValueError:
        pass

    raise source.error('bad escape %s' % escape, len(escape))


def _escape(source, escape, state):
    code = CATEGORIES.get(escape)
    if code:
        return code
    code = ESCAPES.get(escape)
    if code:
        return code
    try:
        c = escape[1:2]
        if c == 'x':
            escape += source.getwhile(2, HEXDIGITS)
            if len(escape) != 4:
                raise source.error('incomplete escape %s' % escape, len(escape))
            return (
             LITERAL, int(escape[2:], 16))
        if c == 'u':
            if source.istext:
                escape += source.getwhile(4, HEXDIGITS)
                if len(escape) != 6:
                    raise source.error('incomplete escape %s' % escape, len(escape))
                return (
                 LITERAL, int(escape[2:], 16))
        if c == 'U':
            if source.istext:
                escape += source.getwhile(8, HEXDIGITS)
                if len(escape) != 10:
                    raise source.error('incomplete escape %s' % escape, len(escape))
                c = int(escape[2:], 16)
                chr(c)
                return (LITERAL, c)
        if c == '0':
            escape += source.getwhile(2, OCTDIGITS)
            return (LITERAL, int(escape[1:], 8))
        if c in DIGITS:
            if source.next in DIGITS:
                escape += source.get()
                if escape[1] in OCTDIGITS and escape[2] in OCTDIGITS:
                    if source.next in OCTDIGITS:
                        escape += source.get()
                        c = int(escape[1:], 8)
                        if c > 255:
                            raise source.error('octal escape value %s outside of range 0-0o377' % escape, len(escape))
                        return (
                         LITERAL, c)
            group = int(escape[1:])
            if group < state.groups:
                if not state.checkgroup(group):
                    raise source.error('cannot refer to an open group', len(escape))
                state.checklookbehindgroup(group, source)
                return (GROUPREF, group)
            raise source.error('invalid group reference %d' % group, len(escape) - 1)
        if len(escape) == 2:
            if c in ASCIILETTERS:
                raise source.error('bad escape %s' % escape, len(escape))
            return (
             LITERAL, ord(escape[1]))
    except ValueError:
        pass

    raise source.error('bad escape %s' % escape, len(escape))


def _uniq(items):
    if len(set(items)) == len(items):
        return items
    newitems = []
    for item in items:
        if item not in newitems:
            newitems.append(item)

    return newitems


def _parse_sub(source, state, verbose, nested):
    items = []
    itemsappend = items.append
    sourcematch = source.match
    start = source.tell()
    while 1:
        itemsappend(_parse(source, state, verbose, nested + 1, not nested and not items))
        if not sourcematch('|'):
            break

    if len(items) == 1:
        return items[0]
    subpattern = SubPattern(state)
    while True:
        prefix = None
        for item in items:
            if not item:
                break
            else:
                if prefix is None:
                    prefix = item[0]
            if item[0] != prefix:
                break
        else:
            for item in items:
                del item[0]

            subpattern.append(prefix)
            continue

        break

    set = []
    for item in items:
        if len(item) != 1:
            break
        op, av = item[0]
        if op is LITERAL:
            set.append((op, av))
        elif op is IN and av[0][0] is not NEGATE:
            set.extend(av)
        else:
            break
    else:
        subpattern.append((IN, _uniq(set)))
        return subpattern

    subpattern.append((BRANCH, (None, items)))
    return subpattern


def _parse--- This code section failed: ---

 L. 477         0  LOAD_GLOBAL              SubPattern
                2  LOAD_FAST                'state'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'subpattern'

 L. 480         8  LOAD_FAST                'subpattern'
               10  LOAD_ATTR                append
               12  STORE_FAST               'subpatternappend'

 L. 481        14  LOAD_FAST                'source'
               16  LOAD_ATTR                get
               18  STORE_FAST               'sourceget'

 L. 482        20  LOAD_FAST                'source'
               22  LOAD_ATTR                match
               24  STORE_FAST               'sourcematch'

 L. 483        26  LOAD_GLOBAL              len
               28  STORE_FAST               '_len'

 L. 484        30  LOAD_GLOBAL              ord
               32  STORE_FAST               '_ord'

 L. 486     34_36  SETUP_LOOP         3128  'to 3128'
             38_0  COME_FROM          2810  '2810'
             38_1  COME_FROM          2806  '2806'

 L. 488        38  LOAD_FAST                'source'
               40  LOAD_ATTR                next
               42  STORE_FAST               'this'

 L. 489        44  LOAD_FAST                'this'
               46  LOAD_CONST               None
               48  COMPARE_OP               is
               50  POP_JUMP_IF_FALSE    54  'to 54'

 L. 490        52  BREAK_LOOP       
             54_0  COME_FROM            50  '50'

 L. 491        54  LOAD_FAST                'this'
               56  LOAD_STR                 '|)'
               58  COMPARE_OP               in
               60  POP_JUMP_IF_FALSE    64  'to 64'

 L. 492        62  BREAK_LOOP       
             64_0  COME_FROM            60  '60'

 L. 493        64  LOAD_FAST                'sourceget'
               66  CALL_FUNCTION_0       0  '0 positional arguments'
               68  POP_TOP          

 L. 495        70  LOAD_FAST                'verbose'
               72  POP_JUMP_IF_FALSE   124  'to 124'

 L. 497        74  LOAD_FAST                'this'
               76  LOAD_GLOBAL              WHITESPACE
               78  COMPARE_OP               in
               80  POP_JUMP_IF_FALSE    84  'to 84'

 L. 498        82  CONTINUE             38  'to 38'
             84_0  COME_FROM            80  '80'

 L. 499        84  LOAD_FAST                'this'
               86  LOAD_STR                 '#'
               88  COMPARE_OP               ==
               90  POP_JUMP_IF_FALSE   124  'to 124'

 L. 500        92  SETUP_LOOP          122  'to 122'
             94_0  COME_FROM           114  '114'

 L. 501        94  LOAD_FAST                'sourceget'
               96  CALL_FUNCTION_0       0  '0 positional arguments'
               98  STORE_FAST               'this'

 L. 502       100  LOAD_FAST                'this'
              102  LOAD_CONST               None
              104  COMPARE_OP               is
              106  POP_JUMP_IF_TRUE    116  'to 116'
              108  LOAD_FAST                'this'
              110  LOAD_STR                 '\n'
              112  COMPARE_OP               ==
              114  POP_JUMP_IF_FALSE    94  'to 94'
            116_0  COME_FROM           106  '106'

 L. 503       116  BREAK_LOOP       
              118  JUMP_BACK            94  'to 94'
              120  POP_BLOCK        
            122_0  COME_FROM_LOOP       92  '92'

 L. 504       122  CONTINUE             38  'to 38'
            124_0  COME_FROM            90  '90'
            124_1  COME_FROM            72  '72'

 L. 506       124  LOAD_FAST                'this'
              126  LOAD_CONST               0
              128  BINARY_SUBSCR    
              130  LOAD_STR                 '\\'
              132  COMPARE_OP               ==
              134  POP_JUMP_IF_FALSE   158  'to 158'

 L. 507       136  LOAD_GLOBAL              _escape
              138  LOAD_FAST                'source'
              140  LOAD_FAST                'this'
              142  LOAD_FAST                'state'
              144  CALL_FUNCTION_3       3  '3 positional arguments'
              146  STORE_FAST               'code'

 L. 508       148  LOAD_FAST                'subpatternappend'
              150  LOAD_FAST                'code'
              152  CALL_FUNCTION_1       1  '1 positional argument'
              154  POP_TOP          
              156  JUMP_BACK            38  'to 38'
            158_0  COME_FROM           134  '134'

 L. 510       158  LOAD_FAST                'this'
              160  LOAD_GLOBAL              SPECIAL_CHARS
              162  COMPARE_OP               not-in
              164  POP_JUMP_IF_FALSE   184  'to 184'

 L. 511       166  LOAD_FAST                'subpatternappend'
              168  LOAD_GLOBAL              LITERAL
              170  LOAD_FAST                '_ord'
              172  LOAD_FAST                'this'
              174  CALL_FUNCTION_1       1  '1 positional argument'
              176  BUILD_TUPLE_2         2 
              178  CALL_FUNCTION_1       1  '1 positional argument'
              180  POP_TOP          
              182  JUMP_BACK            38  'to 38'
            184_0  COME_FROM           164  '164'

 L. 513       184  LOAD_FAST                'this'
              186  LOAD_STR                 '['
              188  COMPARE_OP               ==
          190_192  POP_JUMP_IF_FALSE   990  'to 990'

 L. 514       194  LOAD_FAST                'source'
              196  LOAD_METHOD              tell
              198  CALL_METHOD_0         0  '0 positional arguments'
              200  LOAD_CONST               1
              202  BINARY_SUBTRACT  
              204  STORE_FAST               'here'

 L. 516       206  BUILD_LIST_0          0 
              208  STORE_FAST               'set'

 L. 517       210  LOAD_FAST                'set'
              212  LOAD_ATTR                append
              214  STORE_FAST               'setappend'

 L. 520       216  LOAD_FAST                'source'
              218  LOAD_ATTR                next
              220  LOAD_STR                 '['
              222  COMPARE_OP               ==
          224_226  POP_JUMP_IF_FALSE   264  'to 264'

 L. 521       228  LOAD_CONST               0
              230  LOAD_CONST               None
              232  IMPORT_NAME              warnings
              234  STORE_FAST               'warnings'

 L. 522       236  LOAD_FAST                'warnings'
              238  LOAD_ATTR                warn

 L. 523       240  LOAD_STR                 'Possible nested set at position %d'
              242  LOAD_FAST                'source'
              244  LOAD_METHOD              tell
              246  CALL_METHOD_0         0  '0 positional arguments'
              248  BINARY_MODULO    

 L. 524       250  LOAD_GLOBAL              FutureWarning
              252  LOAD_FAST                'nested'
              254  LOAD_CONST               6
              256  BINARY_ADD       
              258  LOAD_CONST               ('stacklevel',)
              260  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              262  POP_TOP          
            264_0  COME_FROM           224  '224'

 L. 526       264  LOAD_FAST                'sourcematch'
              266  LOAD_STR                 '^'
              268  CALL_FUNCTION_1       1  '1 positional argument'
              270  STORE_FAST               'negate'

 L. 528   272_274  SETUP_LOOP          872  'to 872'

 L. 529       276  LOAD_FAST                'sourceget'
              278  CALL_FUNCTION_0       0  '0 positional arguments'
              280  STORE_FAST               'this'

 L. 530       282  LOAD_FAST                'this'
              284  LOAD_CONST               None
              286  COMPARE_OP               is
          288_290  POP_JUMP_IF_FALSE   312  'to 312'

 L. 531       292  LOAD_FAST                'source'
              294  LOAD_METHOD              error
              296  LOAD_STR                 'unterminated character set'

 L. 532       298  LOAD_FAST                'source'
              300  LOAD_METHOD              tell
              302  CALL_METHOD_0         0  '0 positional arguments'
              304  LOAD_FAST                'here'
              306  BINARY_SUBTRACT  
              308  CALL_METHOD_2         2  '2 positional arguments'
              310  RAISE_VARARGS_1       1  'exception instance'
            312_0  COME_FROM           288  '288'

 L. 533       312  LOAD_FAST                'this'
              314  LOAD_STR                 ']'
              316  COMPARE_OP               ==
          318_320  POP_JUMP_IF_FALSE   332  'to 332'
              322  LOAD_FAST                'set'
          324_326  POP_JUMP_IF_FALSE   332  'to 332'

 L. 534       328  BREAK_LOOP       
              330  JUMP_FORWARD        484  'to 484'
            332_0  COME_FROM           324  '324'
            332_1  COME_FROM           318  '318'

 L. 535       332  LOAD_FAST                'this'
              334  LOAD_CONST               0
              336  BINARY_SUBSCR    
              338  LOAD_STR                 '\\'
              340  COMPARE_OP               ==
          342_344  POP_JUMP_IF_FALSE   358  'to 358'

 L. 536       346  LOAD_GLOBAL              _class_escape
              348  LOAD_FAST                'source'
              350  LOAD_FAST                'this'
              352  CALL_FUNCTION_2       2  '2 positional arguments'
              354  STORE_FAST               'code1'
              356  JUMP_FORWARD        484  'to 484'
            358_0  COME_FROM           342  '342'

 L. 538       358  LOAD_FAST                'set'
          360_362  POP_JUMP_IF_FALSE   472  'to 472'
              364  LOAD_FAST                'this'
              366  LOAD_STR                 '-&~|'
              368  COMPARE_OP               in
          370_372  POP_JUMP_IF_FALSE   472  'to 472'
              374  LOAD_FAST                'source'
              376  LOAD_ATTR                next
              378  LOAD_FAST                'this'
              380  COMPARE_OP               ==
          382_384  POP_JUMP_IF_FALSE   472  'to 472'

 L. 539       386  LOAD_CONST               0
              388  LOAD_CONST               None
              390  IMPORT_NAME              warnings
              392  STORE_FAST               'warnings'

 L. 540       394  LOAD_FAST                'warnings'
              396  LOAD_ATTR                warn

 L. 541       398  LOAD_STR                 'Possible set %s at position %d'

 L. 542       400  LOAD_FAST                'this'
              402  LOAD_STR                 '-'
              404  COMPARE_OP               ==
          406_408  POP_JUMP_IF_FALSE   414  'to 414'
              410  LOAD_STR                 'difference'
              412  JUMP_FORWARD        444  'to 444'
            414_0  COME_FROM           406  '406'

 L. 543       414  LOAD_FAST                'this'
              416  LOAD_STR                 '&'
              418  COMPARE_OP               ==
          420_422  POP_JUMP_IF_FALSE   428  'to 428'
              424  LOAD_STR                 'intersection'
              426  JUMP_FORWARD        444  'to 444'
            428_0  COME_FROM           420  '420'

 L. 544       428  LOAD_FAST                'this'
              430  LOAD_STR                 '~'
              432  COMPARE_OP               ==
          434_436  POP_JUMP_IF_FALSE   442  'to 442'
              438  LOAD_STR                 'symmetric difference'
              440  JUMP_FORWARD        444  'to 444'
            442_0  COME_FROM           434  '434'

 L. 545       442  LOAD_STR                 'union'
            444_0  COME_FROM           440  '440'
            444_1  COME_FROM           426  '426'
            444_2  COME_FROM           412  '412'

 L. 546       444  LOAD_FAST                'source'
              446  LOAD_METHOD              tell
              448  CALL_METHOD_0         0  '0 positional arguments'
              450  LOAD_CONST               1
              452  BINARY_SUBTRACT  
              454  BUILD_TUPLE_2         2 
              456  BINARY_MODULO    

 L. 547       458  LOAD_GLOBAL              FutureWarning
              460  LOAD_FAST                'nested'
              462  LOAD_CONST               6
              464  BINARY_ADD       
              466  LOAD_CONST               ('stacklevel',)
              468  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              470  POP_TOP          
            472_0  COME_FROM           382  '382'
            472_1  COME_FROM           370  '370'
            472_2  COME_FROM           360  '360'

 L. 549       472  LOAD_GLOBAL              LITERAL
              474  LOAD_FAST                '_ord'
              476  LOAD_FAST                'this'
              478  CALL_FUNCTION_1       1  '1 positional argument'
              480  BUILD_TUPLE_2         2 
              482  STORE_FAST               'code1'
            484_0  COME_FROM           356  '356'
            484_1  COME_FROM           330  '330'

 L. 550       484  LOAD_FAST                'sourcematch'
              486  LOAD_STR                 '-'
              488  CALL_FUNCTION_1       1  '1 positional argument'
          490_492  POP_JUMP_IF_FALSE   832  'to 832'

 L. 552       494  LOAD_FAST                'sourceget'
              496  CALL_FUNCTION_0       0  '0 positional arguments'
              498  STORE_FAST               'that'

 L. 553       500  LOAD_FAST                'that'
              502  LOAD_CONST               None
              504  COMPARE_OP               is
          506_508  POP_JUMP_IF_FALSE   530  'to 530'

 L. 554       510  LOAD_FAST                'source'
              512  LOAD_METHOD              error
              514  LOAD_STR                 'unterminated character set'

 L. 555       516  LOAD_FAST                'source'
              518  LOAD_METHOD              tell
              520  CALL_METHOD_0         0  '0 positional arguments'
              522  LOAD_FAST                'here'
              524  BINARY_SUBTRACT  
              526  CALL_METHOD_2         2  '2 positional arguments'
              528  RAISE_VARARGS_1       1  'exception instance'
            530_0  COME_FROM           506  '506'

 L. 556       530  LOAD_FAST                'that'
              532  LOAD_STR                 ']'
              534  COMPARE_OP               ==
          536_538  POP_JUMP_IF_FALSE   592  'to 592'

 L. 557       540  LOAD_FAST                'code1'
              542  LOAD_CONST               0
              544  BINARY_SUBSCR    
              546  LOAD_GLOBAL              IN
              548  COMPARE_OP               is
          550_552  POP_JUMP_IF_FALSE   566  'to 566'

 L. 558       554  LOAD_FAST                'code1'
              556  LOAD_CONST               1
              558  BINARY_SUBSCR    
              560  LOAD_CONST               0
              562  BINARY_SUBSCR    
              564  STORE_FAST               'code1'
            566_0  COME_FROM           550  '550'

 L. 559       566  LOAD_FAST                'setappend'
              568  LOAD_FAST                'code1'
              570  CALL_FUNCTION_1       1  '1 positional argument'
              572  POP_TOP          

 L. 560       574  LOAD_FAST                'setappend'
              576  LOAD_GLOBAL              LITERAL
              578  LOAD_FAST                '_ord'
              580  LOAD_STR                 '-'
              582  CALL_FUNCTION_1       1  '1 positional argument'
              584  BUILD_TUPLE_2         2 
              586  CALL_FUNCTION_1       1  '1 positional argument'
              588  POP_TOP          

 L. 561       590  BREAK_LOOP       
            592_0  COME_FROM           536  '536'

 L. 562       592  LOAD_FAST                'that'
              594  LOAD_CONST               0
              596  BINARY_SUBSCR    
              598  LOAD_STR                 '\\'
              600  COMPARE_OP               ==
          602_604  POP_JUMP_IF_FALSE   618  'to 618'

 L. 563       606  LOAD_GLOBAL              _class_escape
              608  LOAD_FAST                'source'
              610  LOAD_FAST                'that'
              612  CALL_FUNCTION_2       2  '2 positional arguments'
              614  STORE_FAST               'code2'
              616  JUMP_FORWARD        680  'to 680'
            618_0  COME_FROM           602  '602'

 L. 565       618  LOAD_FAST                'that'
              620  LOAD_STR                 '-'
              622  COMPARE_OP               ==
          624_626  POP_JUMP_IF_FALSE   668  'to 668'

 L. 566       628  LOAD_CONST               0
              630  LOAD_CONST               None
              632  IMPORT_NAME              warnings
              634  STORE_FAST               'warnings'

 L. 567       636  LOAD_FAST                'warnings'
              638  LOAD_ATTR                warn

 L. 568       640  LOAD_STR                 'Possible set difference at position %d'

 L. 569       642  LOAD_FAST                'source'
              644  LOAD_METHOD              tell
              646  CALL_METHOD_0         0  '0 positional arguments'
              648  LOAD_CONST               2
              650  BINARY_SUBTRACT  
              652  BINARY_MODULO    

 L. 570       654  LOAD_GLOBAL              FutureWarning
              656  LOAD_FAST                'nested'
              658  LOAD_CONST               6
              660  BINARY_ADD       
              662  LOAD_CONST               ('stacklevel',)
              664  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              666  POP_TOP          
            668_0  COME_FROM           624  '624'

 L. 572       668  LOAD_GLOBAL              LITERAL
              670  LOAD_FAST                '_ord'
              672  LOAD_FAST                'that'
              674  CALL_FUNCTION_1       1  '1 positional argument'
              676  BUILD_TUPLE_2         2 
              678  STORE_FAST               'code2'
            680_0  COME_FROM           616  '616'

 L. 573       680  LOAD_FAST                'code1'
              682  LOAD_CONST               0
              684  BINARY_SUBSCR    
              686  LOAD_GLOBAL              LITERAL
              688  COMPARE_OP               !=
          690_692  POP_JUMP_IF_TRUE    708  'to 708'
              694  LOAD_FAST                'code2'
              696  LOAD_CONST               0
              698  BINARY_SUBSCR    
              700  LOAD_GLOBAL              LITERAL
              702  COMPARE_OP               !=
          704_706  POP_JUMP_IF_FALSE   748  'to 748'
            708_0  COME_FROM           690  '690'

 L. 574       708  LOAD_STR                 'bad character range %s-%s'
              710  LOAD_FAST                'this'
              712  LOAD_FAST                'that'
              714  BUILD_TUPLE_2         2 
              716  BINARY_MODULO    
              718  STORE_FAST               'msg'

 L. 575       720  LOAD_FAST                'source'
              722  LOAD_METHOD              error
              724  LOAD_FAST                'msg'
              726  LOAD_GLOBAL              len
              728  LOAD_FAST                'this'
              730  CALL_FUNCTION_1       1  '1 positional argument'
              732  LOAD_CONST               1
              734  BINARY_ADD       
              736  LOAD_GLOBAL              len
              738  LOAD_FAST                'that'
              740  CALL_FUNCTION_1       1  '1 positional argument'
              742  BINARY_ADD       
              744  CALL_METHOD_2         2  '2 positional arguments'
              746  RAISE_VARARGS_1       1  'exception instance'
            748_0  COME_FROM           704  '704'

 L. 576       748  LOAD_FAST                'code1'
              750  LOAD_CONST               1
              752  BINARY_SUBSCR    
              754  STORE_FAST               'lo'

 L. 577       756  LOAD_FAST                'code2'
              758  LOAD_CONST               1
              760  BINARY_SUBSCR    
              762  STORE_FAST               'hi'

 L. 578       764  LOAD_FAST                'hi'
              766  LOAD_FAST                'lo'
              768  COMPARE_OP               <
          770_772  POP_JUMP_IF_FALSE   814  'to 814'

 L. 579       774  LOAD_STR                 'bad character range %s-%s'
              776  LOAD_FAST                'this'
              778  LOAD_FAST                'that'
              780  BUILD_TUPLE_2         2 
              782  BINARY_MODULO    
              784  STORE_FAST               'msg'

 L. 580       786  LOAD_FAST                'source'
              788  LOAD_METHOD              error
              790  LOAD_FAST                'msg'
              792  LOAD_GLOBAL              len
              794  LOAD_FAST                'this'
              796  CALL_FUNCTION_1       1  '1 positional argument'
              798  LOAD_CONST               1
              800  BINARY_ADD       
              802  LOAD_GLOBAL              len
              804  LOAD_FAST                'that'
              806  CALL_FUNCTION_1       1  '1 positional argument'
              808  BINARY_ADD       
              810  CALL_METHOD_2         2  '2 positional arguments'
              812  RAISE_VARARGS_1       1  'exception instance'
            814_0  COME_FROM           770  '770'

 L. 581       814  LOAD_FAST                'setappend'
              816  LOAD_GLOBAL              RANGE
              818  LOAD_FAST                'lo'
              820  LOAD_FAST                'hi'
              822  BUILD_TUPLE_2         2 
              824  BUILD_TUPLE_2         2 
              826  CALL_FUNCTION_1       1  '1 positional argument'
              828  POP_TOP          
              830  JUMP_BACK           276  'to 276'
            832_0  COME_FROM           490  '490'

 L. 583       832  LOAD_FAST                'code1'
              834  LOAD_CONST               0
              836  BINARY_SUBSCR    
              838  LOAD_GLOBAL              IN
              840  COMPARE_OP               is
          842_844  POP_JUMP_IF_FALSE   858  'to 858'

 L. 584       846  LOAD_FAST                'code1'
              848  LOAD_CONST               1
              850  BINARY_SUBSCR    
              852  LOAD_CONST               0
              854  BINARY_SUBSCR    
              856  STORE_FAST               'code1'
            858_0  COME_FROM           842  '842'

 L. 585       858  LOAD_FAST                'setappend'
              860  LOAD_FAST                'code1'
              862  CALL_FUNCTION_1       1  '1 positional argument'
              864  POP_TOP          
          866_868  JUMP_BACK           276  'to 276'
              870  POP_BLOCK        
            872_0  COME_FROM_LOOP      272  '272'

 L. 587       872  LOAD_GLOBAL              _uniq
              874  LOAD_FAST                'set'
              876  CALL_FUNCTION_1       1  '1 positional argument'
              878  STORE_FAST               'set'

 L. 589       880  LOAD_FAST                '_len'
              882  LOAD_FAST                'set'
              884  CALL_FUNCTION_1       1  '1 positional argument'
              886  LOAD_CONST               1
              888  COMPARE_OP               ==
          890_892  POP_JUMP_IF_FALSE   954  'to 954'
              894  LOAD_FAST                'set'
              896  LOAD_CONST               0
              898  BINARY_SUBSCR    
              900  LOAD_CONST               0
              902  BINARY_SUBSCR    
              904  LOAD_GLOBAL              LITERAL
              906  COMPARE_OP               is
          908_910  POP_JUMP_IF_FALSE   954  'to 954'

 L. 591       912  LOAD_FAST                'negate'
          914_916  POP_JUMP_IF_FALSE   940  'to 940'

 L. 592       918  LOAD_FAST                'subpatternappend'
              920  LOAD_GLOBAL              NOT_LITERAL
              922  LOAD_FAST                'set'
              924  LOAD_CONST               0
              926  BINARY_SUBSCR    
              928  LOAD_CONST               1
              930  BINARY_SUBSCR    
              932  BUILD_TUPLE_2         2 
              934  CALL_FUNCTION_1       1  '1 positional argument'
              936  POP_TOP          
              938  JUMP_FORWARD        952  'to 952'
            940_0  COME_FROM           914  '914'

 L. 594       940  LOAD_FAST                'subpatternappend'
              942  LOAD_FAST                'set'
              944  LOAD_CONST               0
              946  BINARY_SUBSCR    
              948  CALL_FUNCTION_1       1  '1 positional argument'
              950  POP_TOP          
            952_0  COME_FROM           938  '938'
              952  JUMP_FORWARD        988  'to 988'
            954_0  COME_FROM           908  '908'
            954_1  COME_FROM           890  '890'

 L. 596       954  LOAD_FAST                'negate'
          956_958  POP_JUMP_IF_FALSE   976  'to 976'

 L. 597       960  LOAD_FAST                'set'
              962  LOAD_METHOD              insert
              964  LOAD_CONST               0
              966  LOAD_GLOBAL              NEGATE
              968  LOAD_CONST               None
              970  BUILD_TUPLE_2         2 
              972  CALL_METHOD_2         2  '2 positional arguments'
              974  POP_TOP          
            976_0  COME_FROM           956  '956'

 L. 600       976  LOAD_FAST                'subpatternappend'
              978  LOAD_GLOBAL              IN
              980  LOAD_FAST                'set'
              982  BUILD_TUPLE_2         2 
              984  CALL_FUNCTION_1       1  '1 positional argument'
              986  POP_TOP          
            988_0  COME_FROM           952  '952'
              988  JUMP_BACK            38  'to 38'
            990_0  COME_FROM           190  '190'

 L. 602       990  LOAD_FAST                'this'
              992  LOAD_GLOBAL              REPEAT_CHARS
              994  COMPARE_OP               in
          996_998  POP_JUMP_IF_FALSE  1596  'to 1596'

 L. 604      1000  LOAD_FAST                'source'
             1002  LOAD_METHOD              tell
             1004  CALL_METHOD_0         0  '0 positional arguments'
             1006  STORE_FAST               'here'

 L. 605      1008  LOAD_FAST                'this'
             1010  LOAD_STR                 '?'
             1012  COMPARE_OP               ==
         1014_1016  POP_JUMP_IF_FALSE  1030  'to 1030'

 L. 606      1018  LOAD_CONST               (0, 1)
             1020  UNPACK_SEQUENCE_2     2 
             1022  STORE_FAST               'min'
             1024  STORE_FAST               'max'
         1026_1028  JUMP_FORWARD       1360  'to 1360'
           1030_0  COME_FROM          1014  '1014'

 L. 607      1030  LOAD_FAST                'this'
             1032  LOAD_STR                 '*'
             1034  COMPARE_OP               ==
         1036_1038  POP_JUMP_IF_FALSE  1054  'to 1054'

 L. 608      1040  LOAD_CONST               0
             1042  LOAD_GLOBAL              MAXREPEAT
             1044  ROT_TWO          
             1046  STORE_FAST               'min'
             1048  STORE_FAST               'max'
         1050_1052  JUMP_FORWARD       1360  'to 1360'
           1054_0  COME_FROM          1036  '1036'

 L. 610      1054  LOAD_FAST                'this'
             1056  LOAD_STR                 '+'
             1058  COMPARE_OP               ==
         1060_1062  POP_JUMP_IF_FALSE  1078  'to 1078'

 L. 611      1064  LOAD_CONST               1
             1066  LOAD_GLOBAL              MAXREPEAT
             1068  ROT_TWO          
             1070  STORE_FAST               'min'
             1072  STORE_FAST               'max'
         1074_1076  JUMP_FORWARD       1360  'to 1360'
           1078_0  COME_FROM          1060  '1060'

 L. 612      1078  LOAD_FAST                'this'
             1080  LOAD_STR                 '{'
             1082  COMPARE_OP               ==
         1084_1086  POP_JUMP_IF_FALSE  1346  'to 1346'

 L. 613      1088  LOAD_FAST                'source'
             1090  LOAD_ATTR                next
             1092  LOAD_STR                 '}'
             1094  COMPARE_OP               ==
         1096_1098  POP_JUMP_IF_FALSE  1118  'to 1118'

 L. 614      1100  LOAD_FAST                'subpatternappend'
             1102  LOAD_GLOBAL              LITERAL
             1104  LOAD_FAST                '_ord'
             1106  LOAD_FAST                'this'
             1108  CALL_FUNCTION_1       1  '1 positional argument'
             1110  BUILD_TUPLE_2         2 
             1112  CALL_FUNCTION_1       1  '1 positional argument'
             1114  POP_TOP          

 L. 615      1116  CONTINUE             38  'to 38'
           1118_0  COME_FROM          1096  '1096'

 L. 617      1118  LOAD_CONST               0
             1120  LOAD_GLOBAL              MAXREPEAT
             1122  ROT_TWO          
             1124  STORE_FAST               'min'
             1126  STORE_FAST               'max'

 L. 618      1128  LOAD_STR                 ''
             1130  DUP_TOP          
             1132  STORE_FAST               'lo'
             1134  STORE_FAST               'hi'

 L. 619      1136  SETUP_LOOP         1166  'to 1166'
             1138  LOAD_FAST                'source'
             1140  LOAD_ATTR                next
             1142  LOAD_GLOBAL              DIGITS
             1144  COMPARE_OP               in
         1146_1148  POP_JUMP_IF_FALSE  1164  'to 1164'

 L. 620      1150  LOAD_FAST                'lo'
             1152  LOAD_FAST                'sourceget'
             1154  CALL_FUNCTION_0       0  '0 positional arguments'
             1156  INPLACE_ADD      
             1158  STORE_FAST               'lo'
         1160_1162  JUMP_BACK          1138  'to 1138'
           1164_0  COME_FROM          1146  '1146'
             1164  POP_BLOCK        
           1166_0  COME_FROM_LOOP     1136  '1136'

 L. 621      1166  LOAD_FAST                'sourcematch'
             1168  LOAD_STR                 ','
             1170  CALL_FUNCTION_1       1  '1 positional argument'
         1172_1174  POP_JUMP_IF_FALSE  1208  'to 1208'

 L. 622      1176  SETUP_LOOP         1212  'to 1212'
             1178  LOAD_FAST                'source'
             1180  LOAD_ATTR                next
             1182  LOAD_GLOBAL              DIGITS
             1184  COMPARE_OP               in
         1186_1188  POP_JUMP_IF_FALSE  1204  'to 1204'

 L. 623      1190  LOAD_FAST                'hi'
             1192  LOAD_FAST                'sourceget'
             1194  CALL_FUNCTION_0       0  '0 positional arguments'
             1196  INPLACE_ADD      
             1198  STORE_FAST               'hi'
         1200_1202  JUMP_BACK          1178  'to 1178'
           1204_0  COME_FROM          1186  '1186'
             1204  POP_BLOCK        
             1206  JUMP_FORWARD       1212  'to 1212'
           1208_0  COME_FROM          1172  '1172'

 L. 625      1208  LOAD_FAST                'lo'
             1210  STORE_FAST               'hi'
           1212_0  COME_FROM          1206  '1206'
           1212_1  COME_FROM_LOOP     1176  '1176'

 L. 626      1212  LOAD_FAST                'sourcematch'
             1214  LOAD_STR                 '}'
             1216  CALL_FUNCTION_1       1  '1 positional argument'
         1218_1220  POP_JUMP_IF_TRUE   1250  'to 1250'

 L. 627      1222  LOAD_FAST                'subpatternappend'
             1224  LOAD_GLOBAL              LITERAL
             1226  LOAD_FAST                '_ord'
             1228  LOAD_FAST                'this'
             1230  CALL_FUNCTION_1       1  '1 positional argument'
             1232  BUILD_TUPLE_2         2 
             1234  CALL_FUNCTION_1       1  '1 positional argument'
             1236  POP_TOP          

 L. 628      1238  LOAD_FAST                'source'
             1240  LOAD_METHOD              seek
             1242  LOAD_FAST                'here'
             1244  CALL_METHOD_1         1  '1 positional argument'
             1246  POP_TOP          

 L. 629      1248  CONTINUE             38  'to 38'
           1250_0  COME_FROM          1218  '1218'

 L. 631      1250  LOAD_FAST                'lo'
         1252_1254  POP_JUMP_IF_FALSE  1282  'to 1282'

 L. 632      1256  LOAD_GLOBAL              int
             1258  LOAD_FAST                'lo'
             1260  CALL_FUNCTION_1       1  '1 positional argument'
             1262  STORE_FAST               'min'

 L. 633      1264  LOAD_FAST                'min'
             1266  LOAD_GLOBAL              MAXREPEAT
             1268  COMPARE_OP               >=
         1270_1272  POP_JUMP_IF_FALSE  1282  'to 1282'

 L. 634      1274  LOAD_GLOBAL              OverflowError
             1276  LOAD_STR                 'the repetition number is too large'
             1278  CALL_FUNCTION_1       1  '1 positional argument'
             1280  RAISE_VARARGS_1       1  'exception instance'
           1282_0  COME_FROM          1270  '1270'
           1282_1  COME_FROM          1252  '1252'

 L. 635      1282  LOAD_FAST                'hi'
         1284_1286  POP_JUMP_IF_FALSE  1360  'to 1360'

 L. 636      1288  LOAD_GLOBAL              int
             1290  LOAD_FAST                'hi'
             1292  CALL_FUNCTION_1       1  '1 positional argument'
             1294  STORE_FAST               'max'

 L. 637      1296  LOAD_FAST                'max'
             1298  LOAD_GLOBAL              MAXREPEAT
             1300  COMPARE_OP               >=
         1302_1304  POP_JUMP_IF_FALSE  1314  'to 1314'

 L. 638      1306  LOAD_GLOBAL              OverflowError
             1308  LOAD_STR                 'the repetition number is too large'
             1310  CALL_FUNCTION_1       1  '1 positional argument'
             1312  RAISE_VARARGS_1       1  'exception instance'
           1314_0  COME_FROM          1302  '1302'

 L. 639      1314  LOAD_FAST                'max'
             1316  LOAD_FAST                'min'
             1318  COMPARE_OP               <
         1320_1322  POP_JUMP_IF_FALSE  1360  'to 1360'

 L. 640      1324  LOAD_FAST                'source'
             1326  LOAD_METHOD              error
             1328  LOAD_STR                 'min repeat greater than max repeat'

 L. 641      1330  LOAD_FAST                'source'
             1332  LOAD_METHOD              tell
             1334  CALL_METHOD_0         0  '0 positional arguments'
             1336  LOAD_FAST                'here'
             1338  BINARY_SUBTRACT  
             1340  CALL_METHOD_2         2  '2 positional arguments'
             1342  RAISE_VARARGS_1       1  'exception instance'
             1344  JUMP_FORWARD       1360  'to 1360'
           1346_0  COME_FROM          1084  '1084'

 L. 643      1346  LOAD_GLOBAL              AssertionError
             1348  LOAD_STR                 'unsupported quantifier %r'
             1350  LOAD_FAST                'char'
             1352  BUILD_TUPLE_1         1 
             1354  BINARY_MODULO    
             1356  CALL_FUNCTION_1       1  '1 positional argument'
             1358  RAISE_VARARGS_1       1  'exception instance'
           1360_0  COME_FROM          1344  '1344'
           1360_1  COME_FROM          1320  '1320'
           1360_2  COME_FROM          1284  '1284'
           1360_3  COME_FROM          1074  '1074'
           1360_4  COME_FROM          1050  '1050'
           1360_5  COME_FROM          1026  '1026'

 L. 645      1360  LOAD_FAST                'subpattern'
         1362_1364  POP_JUMP_IF_FALSE  1380  'to 1380'

 L. 646      1366  LOAD_FAST                'subpattern'
             1368  LOAD_CONST               -1
             1370  LOAD_CONST               None
             1372  BUILD_SLICE_2         2 
             1374  BINARY_SUBSCR    
             1376  STORE_FAST               'item'
             1378  JUMP_FORWARD       1384  'to 1384'
           1380_0  COME_FROM          1362  '1362'

 L. 648      1380  LOAD_CONST               None
             1382  STORE_FAST               'item'
           1384_0  COME_FROM          1378  '1378'

 L. 649      1384  LOAD_FAST                'item'
         1386_1388  POP_JUMP_IF_FALSE  1408  'to 1408'
             1390  LOAD_FAST                'item'
             1392  LOAD_CONST               0
             1394  BINARY_SUBSCR    
             1396  LOAD_CONST               0
             1398  BINARY_SUBSCR    
             1400  LOAD_GLOBAL              AT
             1402  COMPARE_OP               is
         1404_1406  POP_JUMP_IF_FALSE  1436  'to 1436'
           1408_0  COME_FROM          1386  '1386'

 L. 650      1408  LOAD_FAST                'source'
             1410  LOAD_METHOD              error
             1412  LOAD_STR                 'nothing to repeat'

 L. 651      1414  LOAD_FAST                'source'
             1416  LOAD_METHOD              tell
             1418  CALL_METHOD_0         0  '0 positional arguments'
             1420  LOAD_FAST                'here'
             1422  BINARY_SUBTRACT  
             1424  LOAD_GLOBAL              len
             1426  LOAD_FAST                'this'
             1428  CALL_FUNCTION_1       1  '1 positional argument'
             1430  BINARY_ADD       
             1432  CALL_METHOD_2         2  '2 positional arguments'
             1434  RAISE_VARARGS_1       1  'exception instance'
           1436_0  COME_FROM          1404  '1404'

 L. 652      1436  LOAD_FAST                'item'
             1438  LOAD_CONST               0
             1440  BINARY_SUBSCR    
             1442  LOAD_CONST               0
             1444  BINARY_SUBSCR    
             1446  LOAD_GLOBAL              _REPEATCODES
             1448  COMPARE_OP               in
         1450_1452  POP_JUMP_IF_FALSE  1482  'to 1482'

 L. 653      1454  LOAD_FAST                'source'
             1456  LOAD_METHOD              error
             1458  LOAD_STR                 'multiple repeat'

 L. 654      1460  LOAD_FAST                'source'
             1462  LOAD_METHOD              tell
             1464  CALL_METHOD_0         0  '0 positional arguments'
             1466  LOAD_FAST                'here'
             1468  BINARY_SUBTRACT  
             1470  LOAD_GLOBAL              len
             1472  LOAD_FAST                'this'
             1474  CALL_FUNCTION_1       1  '1 positional argument'
             1476  BINARY_ADD       
             1478  CALL_METHOD_2         2  '2 positional arguments'
             1480  RAISE_VARARGS_1       1  'exception instance'
           1482_0  COME_FROM          1450  '1450'

 L. 655      1482  LOAD_FAST                'item'
             1484  LOAD_CONST               0
             1486  BINARY_SUBSCR    
             1488  LOAD_CONST               0
             1490  BINARY_SUBSCR    
             1492  LOAD_GLOBAL              SUBPATTERN
             1494  COMPARE_OP               is
         1496_1498  POP_JUMP_IF_FALSE  1546  'to 1546'

 L. 656      1500  LOAD_FAST                'item'
             1502  LOAD_CONST               0
             1504  BINARY_SUBSCR    
             1506  LOAD_CONST               1
             1508  BINARY_SUBSCR    
             1510  UNPACK_SEQUENCE_4     4 
             1512  STORE_FAST               'group'
             1514  STORE_FAST               'add_flags'
             1516  STORE_FAST               'del_flags'
             1518  STORE_FAST               'p'

 L. 657      1520  LOAD_FAST                'group'
             1522  LOAD_CONST               None
             1524  COMPARE_OP               is
         1526_1528  POP_JUMP_IF_FALSE  1546  'to 1546'
             1530  LOAD_FAST                'add_flags'
         1532_1534  POP_JUMP_IF_TRUE   1546  'to 1546'
             1536  LOAD_FAST                'del_flags'
         1538_1540  POP_JUMP_IF_TRUE   1546  'to 1546'

 L. 658      1542  LOAD_FAST                'p'
             1544  STORE_FAST               'item'
           1546_0  COME_FROM          1538  '1538'
           1546_1  COME_FROM          1532  '1532'
           1546_2  COME_FROM          1526  '1526'
           1546_3  COME_FROM          1496  '1496'

 L. 659      1546  LOAD_FAST                'sourcematch'
             1548  LOAD_STR                 '?'
             1550  CALL_FUNCTION_1       1  '1 positional argument'
         1552_1554  POP_JUMP_IF_FALSE  1576  'to 1576'

 L. 660      1556  LOAD_GLOBAL              MIN_REPEAT
             1558  LOAD_FAST                'min'
             1560  LOAD_FAST                'max'
             1562  LOAD_FAST                'item'
             1564  BUILD_TUPLE_3         3 
             1566  BUILD_TUPLE_2         2 
             1568  LOAD_FAST                'subpattern'
             1570  LOAD_CONST               -1
             1572  STORE_SUBSCR     
             1574  JUMP_FORWARD       1594  'to 1594'
           1576_0  COME_FROM          1552  '1552'

 L. 662      1576  LOAD_GLOBAL              MAX_REPEAT
             1578  LOAD_FAST                'min'
             1580  LOAD_FAST                'max'
             1582  LOAD_FAST                'item'
             1584  BUILD_TUPLE_3         3 
             1586  BUILD_TUPLE_2         2 
             1588  LOAD_FAST                'subpattern'
             1590  LOAD_CONST               -1
             1592  STORE_SUBSCR     
           1594_0  COME_FROM          1574  '1574'
             1594  JUMP_BACK            38  'to 38'
           1596_0  COME_FROM           996  '996'

 L. 664      1596  LOAD_FAST                'this'
             1598  LOAD_STR                 '.'
             1600  COMPARE_OP               ==
         1602_1604  POP_JUMP_IF_FALSE  1620  'to 1620'

 L. 665      1606  LOAD_FAST                'subpatternappend'
             1608  LOAD_GLOBAL              ANY
             1610  LOAD_CONST               None
             1612  BUILD_TUPLE_2         2 
             1614  CALL_FUNCTION_1       1  '1 positional argument'
             1616  POP_TOP          
             1618  JUMP_BACK            38  'to 38'
           1620_0  COME_FROM          1602  '1602'

 L. 667      1620  LOAD_FAST                'this'
             1622  LOAD_STR                 '('
             1624  COMPARE_OP               ==
         1626_1628  POP_JUMP_IF_FALSE  3062  'to 3062'

 L. 668      1630  LOAD_FAST                'source'
             1632  LOAD_METHOD              tell
             1634  CALL_METHOD_0         0  '0 positional arguments'
             1636  LOAD_CONST               1
             1638  BINARY_SUBTRACT  
             1640  STORE_FAST               'start'

 L. 669      1642  LOAD_CONST               True
             1644  STORE_FAST               'group'

 L. 670      1646  LOAD_CONST               None
             1648  STORE_FAST               'name'

 L. 671      1650  LOAD_CONST               0
             1652  STORE_FAST               'add_flags'

 L. 672      1654  LOAD_CONST               0
             1656  STORE_FAST               'del_flags'

 L. 673      1658  LOAD_FAST                'sourcematch'
             1660  LOAD_STR                 '?'
             1662  CALL_FUNCTION_1       1  '1 positional argument'
         1664_1666  POP_JUMP_IF_FALSE  2856  'to 2856'

 L. 675      1668  LOAD_FAST                'sourceget'
             1670  CALL_FUNCTION_0       0  '0 positional arguments'
             1672  STORE_FAST               'char'

 L. 676      1674  LOAD_FAST                'char'
             1676  LOAD_CONST               None
             1678  COMPARE_OP               is
         1680_1682  POP_JUMP_IF_FALSE  1694  'to 1694'

 L. 677      1684  LOAD_FAST                'source'
             1686  LOAD_METHOD              error
             1688  LOAD_STR                 'unexpected end of pattern'
             1690  CALL_METHOD_1         1  '1 positional argument'
             1692  RAISE_VARARGS_1       1  'exception instance'
           1694_0  COME_FROM          1680  '1680'

 L. 678      1694  LOAD_FAST                'char'
             1696  LOAD_STR                 'P'
             1698  COMPARE_OP               ==
         1700_1702  POP_JUMP_IF_FALSE  1986  'to 1986'

 L. 680      1704  LOAD_FAST                'sourcematch'
             1706  LOAD_STR                 '<'
             1708  CALL_FUNCTION_1       1  '1 positional argument'
         1710_1712  POP_JUMP_IF_FALSE  1764  'to 1764'

 L. 682      1714  LOAD_FAST                'source'
             1716  LOAD_METHOD              getuntil
             1718  LOAD_STR                 '>'
             1720  CALL_METHOD_1         1  '1 positional argument'
             1722  STORE_FAST               'name'

 L. 683      1724  LOAD_FAST                'name'
             1726  LOAD_METHOD              isidentifier
             1728  CALL_METHOD_0         0  '0 positional arguments'
         1730_1732  POP_JUMP_IF_TRUE   1982  'to 1982'

 L. 684      1734  LOAD_STR                 'bad character in group name %r'
             1736  LOAD_FAST                'name'
             1738  BINARY_MODULO    
             1740  STORE_FAST               'msg'

 L. 685      1742  LOAD_FAST                'source'
             1744  LOAD_METHOD              error
             1746  LOAD_FAST                'msg'
             1748  LOAD_GLOBAL              len
             1750  LOAD_FAST                'name'
             1752  CALL_FUNCTION_1       1  '1 positional argument'
             1754  LOAD_CONST               1
             1756  BINARY_ADD       
             1758  CALL_METHOD_2         2  '2 positional arguments'
             1760  RAISE_VARARGS_1       1  'exception instance'
             1762  JUMP_FORWARD       2856  'to 2856'
           1764_0  COME_FROM          1710  '1710'

 L. 686      1764  LOAD_FAST                'sourcematch'
             1766  LOAD_STR                 '='
             1768  CALL_FUNCTION_1       1  '1 positional argument'
         1770_1772  POP_JUMP_IF_FALSE  1932  'to 1932'

 L. 688      1774  LOAD_FAST                'source'
             1776  LOAD_METHOD              getuntil
             1778  LOAD_STR                 ')'
             1780  CALL_METHOD_1         1  '1 positional argument'
             1782  STORE_FAST               'name'

 L. 689      1784  LOAD_FAST                'name'
             1786  LOAD_METHOD              isidentifier
             1788  CALL_METHOD_0         0  '0 positional arguments'
         1790_1792  POP_JUMP_IF_TRUE   1822  'to 1822'

 L. 690      1794  LOAD_STR                 'bad character in group name %r'
             1796  LOAD_FAST                'name'
             1798  BINARY_MODULO    
             1800  STORE_FAST               'msg'

 L. 691      1802  LOAD_FAST                'source'
             1804  LOAD_METHOD              error
             1806  LOAD_FAST                'msg'
             1808  LOAD_GLOBAL              len
             1810  LOAD_FAST                'name'
             1812  CALL_FUNCTION_1       1  '1 positional argument'
             1814  LOAD_CONST               1
             1816  BINARY_ADD       
             1818  CALL_METHOD_2         2  '2 positional arguments'
             1820  RAISE_VARARGS_1       1  'exception instance'
           1822_0  COME_FROM          1790  '1790'

 L. 692      1822  LOAD_FAST                'state'
             1824  LOAD_ATTR                groupdict
             1826  LOAD_METHOD              get
             1828  LOAD_FAST                'name'
             1830  CALL_METHOD_1         1  '1 positional argument'
             1832  STORE_FAST               'gid'

 L. 693      1834  LOAD_FAST                'gid'
             1836  LOAD_CONST               None
             1838  COMPARE_OP               is
         1840_1842  POP_JUMP_IF_FALSE  1872  'to 1872'

 L. 694      1844  LOAD_STR                 'unknown group name %r'
             1846  LOAD_FAST                'name'
             1848  BINARY_MODULO    
             1850  STORE_FAST               'msg'

 L. 695      1852  LOAD_FAST                'source'
             1854  LOAD_METHOD              error
             1856  LOAD_FAST                'msg'
             1858  LOAD_GLOBAL              len
             1860  LOAD_FAST                'name'
             1862  CALL_FUNCTION_1       1  '1 positional argument'
             1864  LOAD_CONST               1
             1866  BINARY_ADD       
             1868  CALL_METHOD_2         2  '2 positional arguments'
             1870  RAISE_VARARGS_1       1  'exception instance'
           1872_0  COME_FROM          1840  '1840'

 L. 696      1872  LOAD_FAST                'state'
             1874  LOAD_METHOD              checkgroup
             1876  LOAD_FAST                'gid'
             1878  CALL_METHOD_1         1  '1 positional argument'
         1880_1882  POP_JUMP_IF_TRUE   1904  'to 1904'

 L. 697      1884  LOAD_FAST                'source'
             1886  LOAD_METHOD              error
             1888  LOAD_STR                 'cannot refer to an open group'

 L. 698      1890  LOAD_GLOBAL              len
             1892  LOAD_FAST                'name'
             1894  CALL_FUNCTION_1       1  '1 positional argument'
             1896  LOAD_CONST               1
             1898  BINARY_ADD       
             1900  CALL_METHOD_2         2  '2 positional arguments'
             1902  RAISE_VARARGS_1       1  'exception instance'
           1904_0  COME_FROM          1880  '1880'

 L. 699      1904  LOAD_FAST                'state'
             1906  LOAD_METHOD              checklookbehindgroup
             1908  LOAD_FAST                'gid'
             1910  LOAD_FAST                'source'
             1912  CALL_METHOD_2         2  '2 positional arguments'
             1914  POP_TOP          

 L. 700      1916  LOAD_FAST                'subpatternappend'
             1918  LOAD_GLOBAL              GROUPREF
             1920  LOAD_FAST                'gid'
             1922  BUILD_TUPLE_2         2 
             1924  CALL_FUNCTION_1       1  '1 positional argument'
             1926  POP_TOP          

 L. 701      1928  CONTINUE             38  'to 38'
             1930  JUMP_FORWARD       2856  'to 2856'
           1932_0  COME_FROM          1770  '1770'

 L. 704      1932  LOAD_FAST                'sourceget'
             1934  CALL_FUNCTION_0       0  '0 positional arguments'
             1936  STORE_FAST               'char'

 L. 705      1938  LOAD_FAST                'char'
             1940  LOAD_CONST               None
             1942  COMPARE_OP               is
         1944_1946  POP_JUMP_IF_FALSE  1958  'to 1958'

 L. 706      1948  LOAD_FAST                'source'
             1950  LOAD_METHOD              error
             1952  LOAD_STR                 'unexpected end of pattern'
             1954  CALL_METHOD_1         1  '1 positional argument'
             1956  RAISE_VARARGS_1       1  'exception instance'
           1958_0  COME_FROM          1944  '1944'

 L. 707      1958  LOAD_FAST                'source'
             1960  LOAD_METHOD              error
             1962  LOAD_STR                 'unknown extension ?P'
             1964  LOAD_FAST                'char'
             1966  BINARY_ADD       

 L. 708      1968  LOAD_GLOBAL              len
             1970  LOAD_FAST                'char'
             1972  CALL_FUNCTION_1       1  '1 positional argument'
             1974  LOAD_CONST               2
             1976  BINARY_ADD       
             1978  CALL_METHOD_2         2  '2 positional arguments'
             1980  RAISE_VARARGS_1       1  'exception instance'
           1982_0  COME_FROM          1730  '1730'
         1982_1984  JUMP_FORWARD       2856  'to 2856'
           1986_0  COME_FROM          1700  '1700'

 L. 709      1986  LOAD_FAST                'char'
             1988  LOAD_STR                 ':'
             1990  COMPARE_OP               ==
         1992_1994  POP_JUMP_IF_FALSE  2004  'to 2004'

 L. 711      1996  LOAD_CONST               None
             1998  STORE_FAST               'group'
         2000_2002  JUMP_FORWARD       2856  'to 2856'
           2004_0  COME_FROM          1992  '1992'

 L. 712      2004  LOAD_FAST                'char'
             2006  LOAD_STR                 '#'
             2008  COMPARE_OP               ==
         2010_2012  POP_JUMP_IF_FALSE  2074  'to 2074'

 L. 714      2014  SETUP_LOOP         2068  'to 2068'
           2016_0  COME_FROM          2056  '2056'

 L. 715      2016  LOAD_FAST                'source'
             2018  LOAD_ATTR                next
             2020  LOAD_CONST               None
             2022  COMPARE_OP               is
         2024_2026  POP_JUMP_IF_FALSE  2048  'to 2048'

 L. 716      2028  LOAD_FAST                'source'
             2030  LOAD_METHOD              error
             2032  LOAD_STR                 'missing ), unterminated comment'

 L. 717      2034  LOAD_FAST                'source'
             2036  LOAD_METHOD              tell
             2038  CALL_METHOD_0         0  '0 positional arguments'
             2040  LOAD_FAST                'start'
             2042  BINARY_SUBTRACT  
             2044  CALL_METHOD_2         2  '2 positional arguments'
             2046  RAISE_VARARGS_1       1  'exception instance'
           2048_0  COME_FROM          2024  '2024'

 L. 718      2048  LOAD_FAST                'sourceget'
             2050  CALL_FUNCTION_0       0  '0 positional arguments'
             2052  LOAD_STR                 ')'
             2054  COMPARE_OP               ==
         2056_2058  POP_JUMP_IF_FALSE  2016  'to 2016'

 L. 719      2060  BREAK_LOOP       
         2062_2064  JUMP_BACK          2016  'to 2016'
             2066  POP_BLOCK        
           2068_0  COME_FROM_LOOP     2014  '2014'

 L. 720      2068  CONTINUE             38  'to 38'
         2070_2072  JUMP_FORWARD       2856  'to 2856'
           2074_0  COME_FROM          2010  '2010'

 L. 722      2074  LOAD_FAST                'char'
             2076  LOAD_STR                 '=!<'
             2078  COMPARE_OP               in
         2080_2082  POP_JUMP_IF_FALSE  2310  'to 2310'

 L. 724      2084  LOAD_CONST               1
             2086  STORE_FAST               'dir'

 L. 725      2088  LOAD_FAST                'char'
             2090  LOAD_STR                 '<'
             2092  COMPARE_OP               ==
         2094_2096  POP_JUMP_IF_FALSE  2186  'to 2186'

 L. 726      2098  LOAD_FAST                'sourceget'
             2100  CALL_FUNCTION_0       0  '0 positional arguments'
             2102  STORE_FAST               'char'

 L. 727      2104  LOAD_FAST                'char'
             2106  LOAD_CONST               None
             2108  COMPARE_OP               is
         2110_2112  POP_JUMP_IF_FALSE  2124  'to 2124'

 L. 728      2114  LOAD_FAST                'source'
             2116  LOAD_METHOD              error
             2118  LOAD_STR                 'unexpected end of pattern'
             2120  CALL_METHOD_1         1  '1 positional argument'
             2122  RAISE_VARARGS_1       1  'exception instance'
           2124_0  COME_FROM          2110  '2110'

 L. 729      2124  LOAD_FAST                'char'
             2126  LOAD_STR                 '=!'
             2128  COMPARE_OP               not-in
         2130_2132  POP_JUMP_IF_FALSE  2158  'to 2158'

 L. 730      2134  LOAD_FAST                'source'
             2136  LOAD_METHOD              error
             2138  LOAD_STR                 'unknown extension ?<'
             2140  LOAD_FAST                'char'
             2142  BINARY_ADD       

 L. 731      2144  LOAD_GLOBAL              len
             2146  LOAD_FAST                'char'
             2148  CALL_FUNCTION_1       1  '1 positional argument'
             2150  LOAD_CONST               2
             2152  BINARY_ADD       
             2154  CALL_METHOD_2         2  '2 positional arguments'
             2156  RAISE_VARARGS_1       1  'exception instance'
           2158_0  COME_FROM          2130  '2130'

 L. 732      2158  LOAD_CONST               -1
             2160  STORE_FAST               'dir'

 L. 733      2162  LOAD_FAST                'state'
             2164  LOAD_ATTR                lookbehindgroups
             2166  STORE_FAST               'lookbehindgroups'

 L. 734      2168  LOAD_FAST                'lookbehindgroups'
             2170  LOAD_CONST               None
             2172  COMPARE_OP               is
         2174_2176  POP_JUMP_IF_FALSE  2186  'to 2186'

 L. 735      2178  LOAD_FAST                'state'
             2180  LOAD_ATTR                groups
             2182  LOAD_FAST                'state'
             2184  STORE_ATTR               lookbehindgroups
           2186_0  COME_FROM          2174  '2174'
           2186_1  COME_FROM          2094  '2094'

 L. 736      2186  LOAD_GLOBAL              _parse_sub
             2188  LOAD_FAST                'source'
             2190  LOAD_FAST                'state'
             2192  LOAD_FAST                'verbose'
             2194  LOAD_FAST                'nested'
             2196  LOAD_CONST               1
             2198  BINARY_ADD       
             2200  CALL_FUNCTION_4       4  '4 positional arguments'
             2202  STORE_FAST               'p'

 L. 737      2204  LOAD_FAST                'dir'
             2206  LOAD_CONST               0
             2208  COMPARE_OP               <
         2210_2212  POP_JUMP_IF_FALSE  2230  'to 2230'

 L. 738      2214  LOAD_FAST                'lookbehindgroups'
             2216  LOAD_CONST               None
             2218  COMPARE_OP               is
         2220_2222  POP_JUMP_IF_FALSE  2230  'to 2230'

 L. 739      2224  LOAD_CONST               None
             2226  LOAD_FAST                'state'
             2228  STORE_ATTR               lookbehindgroups
           2230_0  COME_FROM          2220  '2220'
           2230_1  COME_FROM          2210  '2210'

 L. 740      2230  LOAD_FAST                'sourcematch'
             2232  LOAD_STR                 ')'
             2234  CALL_FUNCTION_1       1  '1 positional argument'
         2236_2238  POP_JUMP_IF_TRUE   2260  'to 2260'

 L. 741      2240  LOAD_FAST                'source'
             2242  LOAD_METHOD              error
             2244  LOAD_STR                 'missing ), unterminated subpattern'

 L. 742      2246  LOAD_FAST                'source'
             2248  LOAD_METHOD              tell
             2250  CALL_METHOD_0         0  '0 positional arguments'
             2252  LOAD_FAST                'start'
             2254  BINARY_SUBTRACT  
             2256  CALL_METHOD_2         2  '2 positional arguments'
             2258  RAISE_VARARGS_1       1  'exception instance'
           2260_0  COME_FROM          2236  '2236'

 L. 743      2260  LOAD_FAST                'char'
             2262  LOAD_STR                 '='
             2264  COMPARE_OP               ==
         2266_2268  POP_JUMP_IF_FALSE  2288  'to 2288'

 L. 744      2270  LOAD_FAST                'subpatternappend'
             2272  LOAD_GLOBAL              ASSERT
             2274  LOAD_FAST                'dir'
             2276  LOAD_FAST                'p'
             2278  BUILD_TUPLE_2         2 
             2280  BUILD_TUPLE_2         2 
             2282  CALL_FUNCTION_1       1  '1 positional argument'
             2284  POP_TOP          
             2286  JUMP_BACK            38  'to 38'
           2288_0  COME_FROM          2266  '2266'

 L. 746      2288  LOAD_FAST                'subpatternappend'
             2290  LOAD_GLOBAL              ASSERT_NOT
             2292  LOAD_FAST                'dir'
             2294  LOAD_FAST                'p'
             2296  BUILD_TUPLE_2         2 
             2298  BUILD_TUPLE_2         2 
             2300  CALL_FUNCTION_1       1  '1 positional argument'
             2302  POP_TOP          

 L. 747      2304  CONTINUE             38  'to 38'
         2306_2308  JUMP_FORWARD       2856  'to 2856'
           2310_0  COME_FROM          2080  '2080'

 L. 749      2310  LOAD_FAST                'char'
             2312  LOAD_STR                 '('
             2314  COMPARE_OP               ==
         2316_2318  POP_JUMP_IF_FALSE  2678  'to 2678'

 L. 751      2320  LOAD_FAST                'source'
             2322  LOAD_METHOD              getuntil
             2324  LOAD_STR                 ')'
             2326  CALL_METHOD_1         1  '1 positional argument'
             2328  STORE_FAST               'condname'

 L. 752      2330  LOAD_FAST                'condname'
             2332  LOAD_METHOD              isidentifier
             2334  CALL_METHOD_0         0  '0 positional arguments'
         2336_2338  POP_JUMP_IF_FALSE  2392  'to 2392'

 L. 753      2340  LOAD_FAST                'state'
             2342  LOAD_ATTR                groupdict
             2344  LOAD_METHOD              get
             2346  LOAD_FAST                'condname'
             2348  CALL_METHOD_1         1  '1 positional argument'
             2350  STORE_FAST               'condgroup'

 L. 754      2352  LOAD_FAST                'condgroup'
             2354  LOAD_CONST               None
             2356  COMPARE_OP               is
         2358_2360  POP_JUMP_IF_FALSE  2536  'to 2536'

 L. 755      2362  LOAD_STR                 'unknown group name %r'
             2364  LOAD_FAST                'condname'
             2366  BINARY_MODULO    
             2368  STORE_FAST               'msg'

 L. 756      2370  LOAD_FAST                'source'
             2372  LOAD_METHOD              error
             2374  LOAD_FAST                'msg'
             2376  LOAD_GLOBAL              len
             2378  LOAD_FAST                'condname'
             2380  CALL_FUNCTION_1       1  '1 positional argument'
             2382  LOAD_CONST               1
             2384  BINARY_ADD       
             2386  CALL_METHOD_2         2  '2 positional arguments'
             2388  RAISE_VARARGS_1       1  'exception instance'
             2390  JUMP_FORWARD       2536  'to 2536'
           2392_0  COME_FROM          2336  '2336'

 L. 758      2392  SETUP_EXCEPT       2420  'to 2420'

 L. 759      2394  LOAD_GLOBAL              int
             2396  LOAD_FAST                'condname'
             2398  CALL_FUNCTION_1       1  '1 positional argument'
             2400  STORE_FAST               'condgroup'

 L. 760      2402  LOAD_FAST                'condgroup'
             2404  LOAD_CONST               0
             2406  COMPARE_OP               <
         2408_2410  POP_JUMP_IF_FALSE  2416  'to 2416'

 L. 761      2412  LOAD_GLOBAL              ValueError
             2414  RAISE_VARARGS_1       1  'exception instance'
           2416_0  COME_FROM          2408  '2408'
             2416  POP_BLOCK        
             2418  JUMP_FORWARD       2472  'to 2472'
           2420_0  COME_FROM_EXCEPT   2392  '2392'

 L. 762      2420  DUP_TOP          
             2422  LOAD_GLOBAL              ValueError
             2424  COMPARE_OP               exception-match
         2426_2428  POP_JUMP_IF_FALSE  2470  'to 2470'
             2430  POP_TOP          
             2432  POP_TOP          
             2434  POP_TOP          

 L. 763      2436  LOAD_STR                 'bad character in group name %r'
             2438  LOAD_FAST                'condname'
             2440  BINARY_MODULO    
             2442  STORE_FAST               'msg'

 L. 764      2444  LOAD_FAST                'source'
             2446  LOAD_METHOD              error
             2448  LOAD_FAST                'msg'
             2450  LOAD_GLOBAL              len
             2452  LOAD_FAST                'condname'
             2454  CALL_FUNCTION_1       1  '1 positional argument'
             2456  LOAD_CONST               1
             2458  BINARY_ADD       
             2460  CALL_METHOD_2         2  '2 positional arguments'
             2462  LOAD_CONST               None
             2464  RAISE_VARARGS_2       2  'exception instance with __cause__'
             2466  POP_EXCEPT       
             2468  JUMP_FORWARD       2472  'to 2472'
           2470_0  COME_FROM          2426  '2426'
             2470  END_FINALLY      
           2472_0  COME_FROM          2468  '2468'
           2472_1  COME_FROM          2418  '2418'

 L. 765      2472  LOAD_FAST                'condgroup'
         2474_2476  POP_JUMP_IF_TRUE   2498  'to 2498'

 L. 766      2478  LOAD_FAST                'source'
             2480  LOAD_METHOD              error
             2482  LOAD_STR                 'bad group number'

 L. 767      2484  LOAD_GLOBAL              len
             2486  LOAD_FAST                'condname'
             2488  CALL_FUNCTION_1       1  '1 positional argument'
             2490  LOAD_CONST               1
             2492  BINARY_ADD       
             2494  CALL_METHOD_2         2  '2 positional arguments'
             2496  RAISE_VARARGS_1       1  'exception instance'
           2498_0  COME_FROM          2474  '2474'

 L. 768      2498  LOAD_FAST                'condgroup'
             2500  LOAD_GLOBAL              MAXGROUPS
             2502  COMPARE_OP               >=
         2504_2506  POP_JUMP_IF_FALSE  2536  'to 2536'

 L. 769      2508  LOAD_STR                 'invalid group reference %d'
             2510  LOAD_FAST                'condgroup'
             2512  BINARY_MODULO    
             2514  STORE_FAST               'msg'

 L. 770      2516  LOAD_FAST                'source'
             2518  LOAD_METHOD              error
             2520  LOAD_FAST                'msg'
             2522  LOAD_GLOBAL              len
             2524  LOAD_FAST                'condname'
             2526  CALL_FUNCTION_1       1  '1 positional argument'
             2528  LOAD_CONST               1
             2530  BINARY_ADD       
             2532  CALL_METHOD_2         2  '2 positional arguments'
             2534  RAISE_VARARGS_1       1  'exception instance'
           2536_0  COME_FROM          2504  '2504'
           2536_1  COME_FROM          2390  '2390'
           2536_2  COME_FROM          2358  '2358'

 L. 771      2536  LOAD_FAST                'state'
             2538  LOAD_METHOD              checklookbehindgroup
             2540  LOAD_FAST                'condgroup'
             2542  LOAD_FAST                'source'
             2544  CALL_METHOD_2         2  '2 positional arguments'
             2546  POP_TOP          

 L. 772      2548  LOAD_GLOBAL              _parse
             2550  LOAD_FAST                'source'
             2552  LOAD_FAST                'state'
             2554  LOAD_FAST                'verbose'
             2556  LOAD_FAST                'nested'
             2558  LOAD_CONST               1
             2560  BINARY_ADD       
             2562  CALL_FUNCTION_4       4  '4 positional arguments'
             2564  STORE_FAST               'item_yes'

 L. 773      2566  LOAD_FAST                'source'
             2568  LOAD_METHOD              match
             2570  LOAD_STR                 '|'
             2572  CALL_METHOD_1         1  '1 positional argument'
         2574_2576  POP_JUMP_IF_FALSE  2620  'to 2620'

 L. 774      2578  LOAD_GLOBAL              _parse
             2580  LOAD_FAST                'source'
             2582  LOAD_FAST                'state'
             2584  LOAD_FAST                'verbose'
             2586  LOAD_FAST                'nested'
             2588  LOAD_CONST               1
             2590  BINARY_ADD       
             2592  CALL_FUNCTION_4       4  '4 positional arguments'
             2594  STORE_FAST               'item_no'

 L. 775      2596  LOAD_FAST                'source'
             2598  LOAD_ATTR                next
             2600  LOAD_STR                 '|'
             2602  COMPARE_OP               ==
         2604_2606  POP_JUMP_IF_FALSE  2624  'to 2624'

 L. 776      2608  LOAD_FAST                'source'
             2610  LOAD_METHOD              error
             2612  LOAD_STR                 'conditional backref with more than two branches'
             2614  CALL_METHOD_1         1  '1 positional argument'
             2616  RAISE_VARARGS_1       1  'exception instance'
             2618  JUMP_FORWARD       2624  'to 2624'
           2620_0  COME_FROM          2574  '2574'

 L. 778      2620  LOAD_CONST               None
             2622  STORE_FAST               'item_no'
           2624_0  COME_FROM          2618  '2618'
           2624_1  COME_FROM          2604  '2604'

 L. 779      2624  LOAD_FAST                'source'
             2626  LOAD_METHOD              match
             2628  LOAD_STR                 ')'
             2630  CALL_METHOD_1         1  '1 positional argument'
         2632_2634  POP_JUMP_IF_TRUE   2656  'to 2656'

 L. 780      2636  LOAD_FAST                'source'
             2638  LOAD_METHOD              error
             2640  LOAD_STR                 'missing ), unterminated subpattern'

 L. 781      2642  LOAD_FAST                'source'
             2644  LOAD_METHOD              tell
             2646  CALL_METHOD_0         0  '0 positional arguments'
             2648  LOAD_FAST                'start'
             2650  BINARY_SUBTRACT  
             2652  CALL_METHOD_2         2  '2 positional arguments'
             2654  RAISE_VARARGS_1       1  'exception instance'
           2656_0  COME_FROM          2632  '2632'

 L. 782      2656  LOAD_FAST                'subpatternappend'
             2658  LOAD_GLOBAL              GROUPREF_EXISTS
             2660  LOAD_FAST                'condgroup'
             2662  LOAD_FAST                'item_yes'
             2664  LOAD_FAST                'item_no'
             2666  BUILD_TUPLE_3         3 
             2668  BUILD_TUPLE_2         2 
             2670  CALL_FUNCTION_1       1  '1 positional argument'
             2672  POP_TOP          

 L. 783      2674  CONTINUE             38  'to 38'
             2676  JUMP_FORWARD       2856  'to 2856'
           2678_0  COME_FROM          2316  '2316'

 L. 785      2678  LOAD_FAST                'char'
             2680  LOAD_GLOBAL              FLAGS
             2682  COMPARE_OP               in
         2684_2686  POP_JUMP_IF_TRUE   2698  'to 2698'
             2688  LOAD_FAST                'char'
             2690  LOAD_STR                 '-'
             2692  COMPARE_OP               ==
         2694_2696  POP_JUMP_IF_FALSE  2832  'to 2832'
           2698_0  COME_FROM          2684  '2684'

 L. 787      2698  LOAD_GLOBAL              _parse_flags
             2700  LOAD_FAST                'source'
             2702  LOAD_FAST                'state'
             2704  LOAD_FAST                'char'
             2706  CALL_FUNCTION_3       3  '3 positional arguments'
             2708  STORE_FAST               'flags'

 L. 788      2710  LOAD_FAST                'flags'
             2712  LOAD_CONST               None
             2714  COMPARE_OP               is
         2716_2718  POP_JUMP_IF_FALSE  2818  'to 2818'

 L. 789      2720  LOAD_FAST                'first'
         2722_2724  POP_JUMP_IF_FALSE  2732  'to 2732'
             2726  LOAD_FAST                'subpattern'
         2728_2730  POP_JUMP_IF_FALSE  2798  'to 2798'
           2732_0  COME_FROM          2722  '2722'

 L. 790      2732  LOAD_CONST               0
             2734  LOAD_CONST               None
             2736  IMPORT_NAME              warnings
             2738  STORE_FAST               'warnings'

 L. 791      2740  LOAD_FAST                'warnings'
             2742  LOAD_ATTR                warn

 L. 792      2744  LOAD_STR                 'Flags not at the start of the expression %r%s'

 L. 793      2746  LOAD_FAST                'source'
             2748  LOAD_ATTR                string
             2750  LOAD_CONST               None
             2752  LOAD_CONST               20
             2754  BUILD_SLICE_2         2 
             2756  BINARY_SUBSCR    

 L. 794      2758  LOAD_GLOBAL              len
             2760  LOAD_FAST                'source'
             2762  LOAD_ATTR                string
             2764  CALL_FUNCTION_1       1  '1 positional argument'
             2766  LOAD_CONST               20
             2768  COMPARE_OP               >
         2770_2772  POP_JUMP_IF_FALSE  2778  'to 2778'
             2774  LOAD_STR                 ' (truncated)'
             2776  JUMP_FORWARD       2780  'to 2780'
           2778_0  COME_FROM          2770  '2770'
             2778  LOAD_STR                 ''
           2780_0  COME_FROM          2776  '2776'
             2780  BUILD_TUPLE_2         2 
             2782  BINARY_MODULO    

 L. 796      2784  LOAD_GLOBAL              DeprecationWarning
             2786  LOAD_FAST                'nested'
             2788  LOAD_CONST               6
             2790  BINARY_ADD       
             2792  LOAD_CONST               ('stacklevel',)
             2794  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
             2796  POP_TOP          
           2798_0  COME_FROM          2728  '2728'

 L. 798      2798  LOAD_FAST                'state'
             2800  LOAD_ATTR                flags
           2802_0  COME_FROM          1930  '1930'
             2802  LOAD_GLOBAL              SRE_FLAG_VERBOSE
             2804  BINARY_AND       
             2806  POP_JUMP_IF_FALSE    38  'to 38'
             2808  LOAD_FAST                'verbose'
             2810  POP_JUMP_IF_TRUE     38  'to 38'

 L. 799      2812  LOAD_GLOBAL              Verbose
             2814  RAISE_VARARGS_1       1  'exception instance'

 L. 800      2816  CONTINUE             38  'to 38'
           2818_0  COME_FROM          2716  '2716'

 L. 802      2818  LOAD_FAST                'flags'
             2820  UNPACK_SEQUENCE_2     2 
             2822  STORE_FAST               'add_flags'
             2824  STORE_FAST               'del_flags'

 L. 803      2826  LOAD_CONST               None
             2828  STORE_FAST               'group'
             2830  JUMP_FORWARD       2856  'to 2856'
           2832_0  COME_FROM          2694  '2694'

 L. 805      2832  LOAD_FAST                'source'
             2834  LOAD_METHOD              error
             2836  LOAD_STR                 'unknown extension ?'
             2838  LOAD_FAST                'char'
             2840  BINARY_ADD       

 L. 806      2842  LOAD_GLOBAL              len
             2844  LOAD_FAST                'char'
             2846  CALL_FUNCTION_1       1  '1 positional argument'
             2848  LOAD_CONST               1
             2850  BINARY_ADD       
             2852  CALL_METHOD_2         2  '2 positional arguments'
             2854  RAISE_VARARGS_1       1  'exception instance'
           2856_0  COME_FROM          2830  '2830'
           2856_1  COME_FROM          2676  '2676'
           2856_2  COME_FROM          2306  '2306'
           2856_3  COME_FROM          2070  '2070'
           2856_4  COME_FROM          2000  '2000'
           2856_5  COME_FROM          1982  '1982'
           2856_6  COME_FROM          1664  '1664'

 L. 809      2856  LOAD_FAST                'group'
             2858  LOAD_CONST               None
             2860  COMPARE_OP               is-not
         2862_2864  POP_JUMP_IF_FALSE  2942  'to 2942'

 L. 810      2866  SETUP_EXCEPT       2882  'to 2882'

 L. 811      2868  LOAD_FAST                'state'
             2870  LOAD_METHOD              opengroup
             2872  LOAD_FAST                'name'
             2874  CALL_METHOD_1         1  '1 positional argument'
             2876  STORE_FAST               'group'
             2878  POP_BLOCK        
             2880  JUMP_FORWARD       2942  'to 2942'
           2882_0  COME_FROM_EXCEPT   2866  '2866'

 L. 812      2882  DUP_TOP          
             2884  LOAD_GLOBAL              error
             2886  COMPARE_OP               exception-match
         2888_2890  POP_JUMP_IF_FALSE  2940  'to 2940'
             2892  POP_TOP          
             2894  STORE_FAST               'err'
             2896  POP_TOP          
             2898  SETUP_FINALLY      2928  'to 2928'

 L. 813      2900  LOAD_FAST                'source'
             2902  LOAD_METHOD              error
             2904  LOAD_FAST                'err'
             2906  LOAD_ATTR                msg
             2908  LOAD_GLOBAL              len
             2910  LOAD_FAST                'name'
             2912  CALL_FUNCTION_1       1  '1 positional argument'
             2914  LOAD_CONST               1
             2916  BINARY_ADD       
             2918  CALL_METHOD_2         2  '2 positional arguments'
             2920  LOAD_CONST               None
             2922  RAISE_VARARGS_2       2  'exception instance with __cause__'
             2924  POP_BLOCK        
             2926  LOAD_CONST               None
           2928_0  COME_FROM_FINALLY  2898  '2898'
             2928  LOAD_CONST               None
             2930  STORE_FAST               'err'
             2932  DELETE_FAST              'err'
             2934  END_FINALLY      
             2936  POP_EXCEPT       
             2938  JUMP_FORWARD       2942  'to 2942'
           2940_0  COME_FROM          2888  '2888'
             2940  END_FINALLY      
           2942_0  COME_FROM          2938  '2938'
           2942_1  COME_FROM          2880  '2880'
           2942_2  COME_FROM          2862  '2862'

 L. 814      2942  LOAD_FAST                'verbose'
         2944_2946  POP_JUMP_IF_TRUE   2958  'to 2958'
             2948  LOAD_FAST                'add_flags'
             2950  LOAD_GLOBAL              SRE_FLAG_VERBOSE
             2952  BINARY_AND       
         2954_2956  JUMP_IF_FALSE_OR_POP  2966  'to 2966'
           2958_0  COME_FROM          2944  '2944'

 L. 815      2958  LOAD_FAST                'del_flags'
             2960  LOAD_GLOBAL              SRE_FLAG_VERBOSE
             2962  BINARY_AND       
             2964  UNARY_NOT        
           2966_0  COME_FROM          2954  '2954'
             2966  STORE_FAST               'sub_verbose'

 L. 816      2968  LOAD_GLOBAL              _parse_sub
             2970  LOAD_FAST                'source'
             2972  LOAD_FAST                'state'
             2974  LOAD_FAST                'sub_verbose'
             2976  LOAD_FAST                'nested'
             2978  LOAD_CONST               1
             2980  BINARY_ADD       
             2982  CALL_FUNCTION_4       4  '4 positional arguments'
             2984  STORE_FAST               'p'

 L. 817      2986  LOAD_FAST                'source'
             2988  LOAD_METHOD              match
             2990  LOAD_STR                 ')'
             2992  CALL_METHOD_1         1  '1 positional argument'
         2994_2996  POP_JUMP_IF_TRUE   3018  'to 3018'

 L. 818      2998  LOAD_FAST                'source'
             3000  LOAD_METHOD              error
             3002  LOAD_STR                 'missing ), unterminated subpattern'

 L. 819      3004  LOAD_FAST                'source'
             3006  LOAD_METHOD              tell
             3008  CALL_METHOD_0         0  '0 positional arguments'
             3010  LOAD_FAST                'start'
             3012  BINARY_SUBTRACT  
             3014  CALL_METHOD_2         2  '2 positional arguments'
             3016  RAISE_VARARGS_1       1  'exception instance'
           3018_0  COME_FROM          2994  '2994'

 L. 820      3018  LOAD_FAST                'group'
             3020  LOAD_CONST               None
             3022  COMPARE_OP               is-not
         3024_3026  POP_JUMP_IF_FALSE  3040  'to 3040'

 L. 821      3028  LOAD_FAST                'state'
             3030  LOAD_METHOD              closegroup
             3032  LOAD_FAST                'group'
             3034  LOAD_FAST                'p'
             3036  CALL_METHOD_2         2  '2 positional arguments'
             3038  POP_TOP          
           3040_0  COME_FROM          3024  '3024'

 L. 822      3040  LOAD_FAST                'subpatternappend'
             3042  LOAD_GLOBAL              SUBPATTERN
             3044  LOAD_FAST                'group'
             3046  LOAD_FAST                'add_flags'
             3048  LOAD_FAST                'del_flags'
             3050  LOAD_FAST                'p'
             3052  BUILD_TUPLE_4         4 
             3054  BUILD_TUPLE_2         2 
             3056  CALL_FUNCTION_1       1  '1 positional argument'
             3058  POP_TOP          
             3060  JUMP_BACK            38  'to 38'
           3062_0  COME_FROM          1626  '1626'

 L. 824      3062  LOAD_FAST                'this'
             3064  LOAD_STR                 '^'
             3066  COMPARE_OP               ==
         3068_3070  POP_JUMP_IF_FALSE  3086  'to 3086'

 L. 825      3072  LOAD_FAST                'subpatternappend'
             3074  LOAD_GLOBAL              AT
             3076  LOAD_GLOBAL              AT_BEGINNING
             3078  BUILD_TUPLE_2         2 
             3080  CALL_FUNCTION_1       1  '1 positional argument'
             3082  POP_TOP          
             3084  JUMP_BACK            38  'to 38'
           3086_0  COME_FROM          3068  '3068'

 L. 827      3086  LOAD_FAST                'this'
             3088  LOAD_STR                 '$'
             3090  COMPARE_OP               ==
         3092_3094  POP_JUMP_IF_FALSE  3110  'to 3110'

 L. 828      3096  LOAD_FAST                'subpatternappend'
             3098  LOAD_GLOBAL              AT
             3100  LOAD_GLOBAL              AT_END
             3102  BUILD_TUPLE_2         2 
             3104  CALL_FUNCTION_1       1  '1 positional argument'
             3106  POP_TOP          
             3108  JUMP_BACK            38  'to 38'
           3110_0  COME_FROM          3092  '3092'

 L. 831      3110  LOAD_GLOBAL              AssertionError
             3112  LOAD_STR                 'unsupported special character %r'
             3114  LOAD_FAST                'char'
             3116  BUILD_TUPLE_1         1 
             3118  BINARY_MODULO    
             3120  CALL_FUNCTION_1       1  '1 positional argument'
             3122  RAISE_VARARGS_1       1  'exception instance'
             3124  JUMP_BACK            38  'to 38'
             3126  POP_BLOCK        
           3128_0  COME_FROM_LOOP       34  '34'

 L. 834      3128  SETUP_LOOP         3234  'to 3234'
             3130  LOAD_GLOBAL              range
             3132  LOAD_GLOBAL              len
             3134  LOAD_FAST                'subpattern'
             3136  CALL_FUNCTION_1       1  '1 positional argument'
             3138  CALL_FUNCTION_1       1  '1 positional argument'
             3140  LOAD_CONST               None
             3142  LOAD_CONST               None
             3144  LOAD_CONST               -1
             3146  BUILD_SLICE_3         3 
             3148  BINARY_SUBSCR    
             3150  GET_ITER         
           3152_0  COME_FROM          3208  '3208'
           3152_1  COME_FROM          3202  '3202'
           3152_2  COME_FROM          3196  '3196'
           3152_3  COME_FROM          3174  '3174'
             3152  FOR_ITER           3232  'to 3232'
             3154  STORE_FAST               'i'

 L. 835      3156  LOAD_FAST                'subpattern'
             3158  LOAD_FAST                'i'
             3160  BINARY_SUBSCR    
             3162  UNPACK_SEQUENCE_2     2 
             3164  STORE_FAST               'op'
             3166  STORE_FAST               'av'

 L. 836      3168  LOAD_FAST                'op'
             3170  LOAD_GLOBAL              SUBPATTERN
             3172  COMPARE_OP               is
         3174_3176  POP_JUMP_IF_FALSE  3152  'to 3152'

 L. 837      3178  LOAD_FAST                'av'
             3180  UNPACK_SEQUENCE_4     4 
             3182  STORE_FAST               'group'
             3184  STORE_FAST               'add_flags'
             3186  STORE_FAST               'del_flags'
             3188  STORE_FAST               'p'

 L. 838      3190  LOAD_FAST                'group'
             3192  LOAD_CONST               None
             3194  COMPARE_OP               is
         3196_3198  POP_JUMP_IF_FALSE  3152  'to 3152'
             3200  LOAD_FAST                'add_flags'
         3202_3204  POP_JUMP_IF_TRUE   3152  'to 3152'
             3206  LOAD_FAST                'del_flags'
         3208_3210  POP_JUMP_IF_TRUE   3152  'to 3152'

 L. 839      3212  LOAD_FAST                'p'
             3214  LOAD_FAST                'subpattern'
             3216  LOAD_FAST                'i'
             3218  LOAD_FAST                'i'
             3220  LOAD_CONST               1
             3222  BINARY_ADD       
             3224  BUILD_SLICE_2         2 
             3226  STORE_SUBSCR     
         3228_3230  JUMP_BACK          3152  'to 3152'
             3232  POP_BLOCK        
           3234_0  COME_FROM_LOOP     3128  '3128'

 L. 841      3234  LOAD_FAST                'subpattern'
             3236  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 2802_0


def _parse_flags(source, state, char):
    sourceget = source.get
    add_flags = 0
    del_flags = 0
    if char != '-':
        while 1:
            flag = FLAGS[char]
            if source.istext:
                if char == 'L':
                    msg = "bad inline flags: cannot use 'L' flag with a str pattern"
                    raise source.error(msg)
            elif char == 'u':
                msg = "bad inline flags: cannot use 'u' flag with a bytes pattern"
                raise source.error(msg)
            add_flags |= flag
            if flag & TYPE_FLAGS:
                if add_flags & TYPE_FLAGS != flag:
                    msg = "bad inline flags: flags 'a', 'u' and 'L' are incompatible"
                    raise source.error(msg)
            char = sourceget()
            if char is None:
                raise source.error('missing -, : or )')
            if char in ')-:':
                break
            if char not in FLAGS:
                msg = 'unknown flag' if char.isalpha() else 'missing -, : or )'
                raise source.error(msg, len(char))

    if char == ')':
        state.flags |= add_flags
        return
    if add_flags & GLOBAL_FLAGS:
        raise source.error('bad inline flags: cannot turn on global flag', 1)
    if char == '-':
        char = sourceget()
        if char is None:
            raise source.error('missing flag')
        if char not in FLAGS:
            msg = 'unknown flag' if char.isalpha() else 'missing flag'
            raise source.error(msg, len(char))
        while 1:
            flag = FLAGS[char]
            if flag & TYPE_FLAGS:
                msg = "bad inline flags: cannot turn off flags 'a', 'u' and 'L'"
                raise source.error(msg)
            del_flags |= flag
            char = sourceget()
            if char is None:
                raise source.error('missing :')
            if char == ':':
                break
            if char not in FLAGS:
                msg = 'unknown flag' if char.isalpha() else 'missing :'
                raise source.error(msg, len(char))

    if del_flags & GLOBAL_FLAGS:
        raise source.error('bad inline flags: cannot turn off global flag', 1)
    if add_flags & del_flags:
        raise source.error('bad inline flags: flag turned on and off', 1)
    return (
     add_flags, del_flags)


def fix_flags(src, flags):
    if isinstance(src, str):
        if flags & SRE_FLAG_LOCALE:
            raise ValueError('cannot use LOCALE flag with a str pattern')
        if not flags & SRE_FLAG_ASCII:
            flags |= SRE_FLAG_UNICODE
        elif flags & SRE_FLAG_UNICODE:
            raise ValueError('ASCII and UNICODE flags are incompatible')
    else:
        if flags & SRE_FLAG_UNICODE:
            raise ValueError('cannot use UNICODE flag with a bytes pattern')
        if flags & SRE_FLAG_LOCALE:
            if flags & SRE_FLAG_ASCII:
                raise ValueError('ASCII and LOCALE flags are incompatible')
    return flags


def parse(str, flags=0, pattern=None):
    source = Tokenizer(str)
    if pattern is None:
        pattern = Pattern()
    pattern.flags = flags
    pattern.str = str
    try:
        p = _parse_subsourcepattern(flags & SRE_FLAG_VERBOSE)0
    except Verbose:
        pattern = Pattern()
        pattern.flags = flags | SRE_FLAG_VERBOSE
        pattern.str = str
        source.seek(0)
        p = _parse_subsourcepatternTrue0

    p.pattern.flags = fix_flags(str, p.pattern.flags)
    if source.next is not None:
        raise source.error('unbalanced parenthesis')
    if flags & SRE_FLAG_DEBUG:
        p.dump()
    return p


def parse_template(source, pattern):
    s = Tokenizer(source)
    sget = s.get
    groups = []
    literals = []
    literal = []
    lappend = literal.append

    def addgroup(index, pos):
        if index > pattern.groups:
            raise s.error('invalid group reference %d' % index, pos)
        if literal:
            literals.append(''.join(literal))
            del literal[:]
        groups.append((len(literals), index))
        literals.append(None)

    groupindex = pattern.groupindex
    while True:
        this = sget()
        if this is None:
            break
        if this[0] == '\\':
            c = this[1]
            if c == 'g':
                name = ''
                if not s.match('<'):
                    raise s.error('missing <')
                name = s.getuntil('>')
                if name.isidentifier():
                    try:
                        index = groupindex[name]
                    except KeyError:
                        raise IndexError('unknown group name %r' % name)

                else:
                    try:
                        index = int(name)
                        if index < 0:
                            raise ValueError
                    except ValueError:
                        raise s.error('bad character in group name %r' % name, len(name) + 1) from None

                    if index >= MAXGROUPS:
                        raise s.error('invalid group reference %d' % index, len(name) + 1)
                    addgroup(index, len(name) + 1)
            elif c == '0':
                if s.next in OCTDIGITS:
                    this += sget()
                    if s.next in OCTDIGITS:
                        this += sget()
                lappend(chr(int(this[1:], 8) & 255))
            elif c in DIGITS:
                isoctal = False
                if s.next in DIGITS:
                    this += sget()
                    if c in OCTDIGITS and this[2] in OCTDIGITS:
                        if s.next in OCTDIGITS:
                            this += sget()
                            isoctal = True
                            c = int(this[1:], 8)
                            if c > 255:
                                raise s.error('octal escape value %s outside of range 0-0o377' % this, len(this))
                            lappend(chr(c))
                isoctal or addgroup(int(this[1:]), len(this) - 1)
            else:
                try:
                    this = chr(ESCAPES[this][1])
                except KeyError:
                    if c in ASCIILETTERS:
                        raise s.error('bad escape %s' % this, len(this))

                lappend(this)
        else:
            lappend(this)

    if literal:
        literals.append(''.join(literal))
    if not isinstance(source, str):
        literals = [None if s is None else s.encode('latin-1') for s in literals]
    return (
     groups, literals)


def expand_template(template, match):
    g = match.group
    empty = match.string[:0]
    groups, literals = template
    literals = literals[:]
    try:
        for index, group in groups:
            literals[index] = g(group) or empty

    except IndexError:
        raise error('invalid group reference %d' % index)

    return empty.join(literals)