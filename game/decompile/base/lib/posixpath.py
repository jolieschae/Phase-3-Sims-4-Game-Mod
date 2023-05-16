# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\posixpath.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 15936 bytes
curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
pathsep = ':'
defpath = ':/bin:/usr/bin'
altsep = None
devnull = '/dev/null'
import os, sys, stat, genericpath
from genericpath import *
__all__ = [
 "'normcase'", "'isabs'", "'join'", "'splitdrive'", "'split'", "'splitext'", 
 "'basename'", 
 "'dirname'", "'commonprefix'", "'getsize'", "'getmtime'", 
 "'getatime'", 
 "'getctime'", "'islink'", "'exists'", "'lexists'", "'isdir'", "'isfile'", 
 "'ismount'", 
 "'expanduser'", "'expandvars'", "'normpath'", "'abspath'", 
 "'samefile'", 
 "'sameopenfile'", "'samestat'", 
 "'curdir'", "'pardir'", "'sep'", "'pathsep'", 
 "'defpath'", "'altsep'", "'extsep'", 
 "'devnull'", "'realpath'", "'supports_unicode_filenames'", 
 "'relpath'", 
 "'commonpath'"]

def _get_sep(path):
    if isinstance(path, bytes):
        return b'/'
    return '/'


def normcase(s):
    s = os.fspath(s)
    if not isinstance(s, (bytes, str)):
        raise TypeError("normcase() argument must be str or bytes, not '{}'".format(s.__class__.__name__))
    return s


def isabs(s):
    s = os.fspath(s)
    sep = _get_sep(s)
    return s.startswith(sep)


def join(a, *p):
    a = os.fspath(a)
    sep = _get_sep(a)
    path = a
    try:
        if not p:
            path[:0] + sep
        for b in map(os.fspath, p):
            if b.startswith(sep):
                path = b
            elif not path or path.endswith(sep):
                path += b
            else:
                path += sep + b

    except (TypeError, AttributeError, BytesWarning):
        (genericpath._check_arg_types)('join', a, *p)
        raise

    return path


def split(p):
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head, tail = p[:i], p[i:]
    if head:
        if head != sep * len(head):
            head = head.rstrip(sep)
    return (
     head, tail)


def splitext(p):
    p = os.fspath(p)
    if isinstance(p, bytes):
        sep = b'/'
        extsep = b'.'
    else:
        sep = '/'
        extsep = '.'
    return genericpath._splitext(p, sep, None, extsep)


splitext.__doc__ = genericpath._splitext.__doc__

def splitdrive(p):
    p = os.fspath(p)
    return (p[:0], p)


def basename(p):
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    return p[i:]


def dirname(p):
    p = os.fspath(p)
    sep = _get_sep(p)
    i = p.rfind(sep) + 1
    head = p[:i]
    if head:
        if head != sep * len(head):
            head = head.rstrip(sep)
    return head


def islink(path):
    try:
        st = os.lstat(path)
    except (OSError, AttributeError):
        return False
    else:
        return stat.S_ISLNK(st.st_mode)


def lexists(path):
    try:
        os.lstat(path)
    except OSError:
        return False
    else:
        return True


def ismount(path):
    try:
        s1 = os.lstat(path)
    except OSError:
        return False
    else:
        if stat.S_ISLNK(s1.st_mode):
            return False
        elif isinstance(path, bytes):
            parent = join(path, b'..')
        else:
            parent = join(path, '..')
        parent = realpath(parent)
        try:
            s2 = os.lstat(parent)
        except OSError:
            return False
        else:
            dev1 = s1.st_dev
            dev2 = s2.st_dev
            if dev1 != dev2:
                return True
            ino1 = s1.st_ino
            ino2 = s2.st_ino
            if ino1 == ino2:
                return True
            return False


def expanduser(path):
    path = os.fspath(path)
    if isinstance(path, bytes):
        tilde = b'~'
    else:
        tilde = '~'
    if not path.startswith(tilde):
        return path
        sep = _get_sep(path)
        i = path.find(sep, 1)
        if i < 0:
            i = len(path)
        if i == 1:
            if 'HOME' not in os.environ:
                import pwd
                userhome = pwd.getpwuid(os.getuid()).pw_dir
            else:
                userhome = os.environ['HOME']
    else:
        import pwd
        name = path[1:i]
    if isinstance(name, bytes):
        name = str(name, 'ASCII')
    else:
        try:
            pwent = pwd.getpwnam(name)
        except KeyError:
            return path
        else:
            userhome = pwent.pw_dir
        if isinstance(path, bytes):
            userhome = os.fsencode(userhome)
            root = b'/'
        else:
            root = '/'
    userhome = userhome.rstrip(root)
    return userhome + path[i:] or root


_varprog = None
_varprogb = None

def expandvars(path):
    global _varprog
    global _varprogb
    path = os.fspath(path)
    if isinstance(path, bytes):
        if b'$' not in path:
            return path
        if not _varprogb:
            import re
            _varprogb = re.compile(b'\\$(\\w+|\\{[^}]*\\})', re.ASCII)
        search = _varprogb.search
        start = b'{'
        end = b'}'
        environ = getattr(os, 'environb', None)
    else:
        if '$' not in path:
            return path
        if not _varprog:
            import re
            _varprog = re.compile('\\$(\\w+|\\{[^}]*\\})', re.ASCII)
        search = _varprog.search
        start = '{'
        end = '}'
        environ = os.environ
    i = 0
    while True:
        m = search(path, i)
        if not m:
            break
        i, j = m.span(0)
        name = m.group(1)
        if name.startswith(start):
            if name.endswith(end):
                name = name[1:-1]
        try:
            if environ is None:
                value = os.fsencode(os.environ[os.fsdecode(name)])
            else:
                value = environ[name]
        except KeyError:
            i = j
        else:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail

    return path


def normpath--- This code section failed: ---

 L. 333         0  LOAD_GLOBAL              os
                2  LOAD_METHOD              fspath
                4  LOAD_FAST                'path'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  STORE_FAST               'path'

 L. 334        10  LOAD_GLOBAL              isinstance
               12  LOAD_FAST                'path'
               14  LOAD_GLOBAL              bytes
               16  CALL_FUNCTION_2       2  '2 positional arguments'
               18  POP_JUMP_IF_FALSE    38  'to 38'

 L. 335        20  LOAD_CONST               b'/'
               22  STORE_FAST               'sep'

 L. 336        24  LOAD_CONST               b''
               26  STORE_FAST               'empty'

 L. 337        28  LOAD_CONST               b'.'
               30  STORE_FAST               'dot'

 L. 338        32  LOAD_CONST               b'..'
               34  STORE_FAST               'dotdot'
               36  JUMP_FORWARD         54  'to 54'
             38_0  COME_FROM            18  '18'

 L. 340        38  LOAD_STR                 '/'
               40  STORE_FAST               'sep'

 L. 341        42  LOAD_STR                 ''
               44  STORE_FAST               'empty'

 L. 342        46  LOAD_STR                 '.'
               48  STORE_FAST               'dot'

 L. 343        50  LOAD_STR                 '..'
               52  STORE_FAST               'dotdot'
             54_0  COME_FROM            36  '36'

 L. 344        54  LOAD_FAST                'path'
               56  LOAD_FAST                'empty'
               58  COMPARE_OP               ==
               60  POP_JUMP_IF_FALSE    66  'to 66'

 L. 345        62  LOAD_FAST                'dot'
               64  RETURN_VALUE     
             66_0  COME_FROM            60  '60'

 L. 346        66  LOAD_FAST                'path'
               68  LOAD_METHOD              startswith
               70  LOAD_FAST                'sep'
               72  CALL_METHOD_1         1  '1 positional argument'
               74  STORE_FAST               'initial_slashes'

 L. 349        76  LOAD_FAST                'initial_slashes'
               78  POP_JUMP_IF_FALSE   112  'to 112'

 L. 350        80  LOAD_FAST                'path'
               82  LOAD_METHOD              startswith
               84  LOAD_FAST                'sep'
               86  LOAD_CONST               2
               88  BINARY_MULTIPLY  
               90  CALL_METHOD_1         1  '1 positional argument'
               92  POP_JUMP_IF_FALSE   112  'to 112'
               94  LOAD_FAST                'path'
               96  LOAD_METHOD              startswith
               98  LOAD_FAST                'sep'
              100  LOAD_CONST               3
              102  BINARY_MULTIPLY  
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_JUMP_IF_TRUE    112  'to 112'

 L. 351       108  LOAD_CONST               2
              110  STORE_FAST               'initial_slashes'
            112_0  COME_FROM           106  '106'
            112_1  COME_FROM            92  '92'
            112_2  COME_FROM            78  '78'

 L. 352       112  LOAD_FAST                'path'
              114  LOAD_METHOD              split
              116  LOAD_FAST                'sep'
              118  CALL_METHOD_1         1  '1 positional argument'
              120  STORE_FAST               'comps'

 L. 353       122  BUILD_LIST_0          0 
              124  STORE_FAST               'new_comps'

 L. 354       126  SETUP_LOOP          210  'to 210'
              128  LOAD_FAST                'comps'
              130  GET_ITER         
            132_0  COME_FROM           196  '196'
              132  FOR_ITER            208  'to 208'
              134  STORE_FAST               'comp'

 L. 355       136  LOAD_FAST                'comp'
              138  LOAD_FAST                'empty'
              140  LOAD_FAST                'dot'
              142  BUILD_TUPLE_2         2 
              144  COMPARE_OP               in
              146  POP_JUMP_IF_FALSE   150  'to 150'

 L. 356       148  CONTINUE            132  'to 132'
            150_0  COME_FROM           146  '146'

 L. 357       150  LOAD_FAST                'comp'
              152  LOAD_FAST                'dotdot'
              154  COMPARE_OP               !=
              156  POP_JUMP_IF_TRUE    182  'to 182'
              158  LOAD_FAST                'initial_slashes'
              160  POP_JUMP_IF_TRUE    166  'to 166'
              162  LOAD_FAST                'new_comps'
              164  POP_JUMP_IF_FALSE   182  'to 182'
            166_0  COME_FROM           160  '160'

 L. 358       166  LOAD_FAST                'new_comps'
              168  POP_JUMP_IF_FALSE   194  'to 194'
              170  LOAD_FAST                'new_comps'
              172  LOAD_CONST               -1
              174  BINARY_SUBSCR    
              176  LOAD_FAST                'dotdot'
              178  COMPARE_OP               ==
              180  POP_JUMP_IF_FALSE   194  'to 194'
            182_0  COME_FROM           164  '164'
            182_1  COME_FROM           156  '156'

 L. 359       182  LOAD_FAST                'new_comps'
              184  LOAD_METHOD              append
              186  LOAD_FAST                'comp'
              188  CALL_METHOD_1         1  '1 positional argument'
              190  POP_TOP          
              192  JUMP_BACK           132  'to 132'
            194_0  COME_FROM           180  '180'
            194_1  COME_FROM           168  '168'

 L. 360       194  LOAD_FAST                'new_comps'
              196  POP_JUMP_IF_FALSE   132  'to 132'

 L. 361       198  LOAD_FAST                'new_comps'
              200  LOAD_METHOD              pop
              202  CALL_METHOD_0         0  '0 positional arguments'
              204  POP_TOP          
              206  JUMP_BACK           132  'to 132'
              208  POP_BLOCK        
            210_0  COME_FROM_LOOP      126  '126'

 L. 362       210  LOAD_FAST                'new_comps'
              212  STORE_FAST               'comps'

 L. 363       214  LOAD_FAST                'sep'
              216  LOAD_METHOD              join
              218  LOAD_FAST                'comps'
              220  CALL_METHOD_1         1  '1 positional argument'
              222  STORE_FAST               'path'

 L. 364       224  LOAD_FAST                'initial_slashes'
              226  POP_JUMP_IF_FALSE   240  'to 240'

 L. 365       228  LOAD_FAST                'sep'
              230  LOAD_FAST                'initial_slashes'
              232  BINARY_MULTIPLY  
              234  LOAD_FAST                'path'
              236  BINARY_ADD       
              238  STORE_FAST               'path'
            240_0  COME_FROM           226  '226'

 L. 366       240  LOAD_FAST                'path'
              242  JUMP_IF_TRUE_OR_POP   246  'to 246'
              244  LOAD_FAST                'dot'
            246_0  COME_FROM           242  '242'
              246  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 210_0


def abspath(path):
    path = os.fspath(path)
    if not isabs(path):
        if isinstance(path, bytes):
            cwd = os.getcwdb()
        else:
            cwd = os.getcwd()
        path = join(cwd, path)
    return normpath(path)


def realpath(filename):
    filename = os.fspath(filename)
    path, ok = _joinrealpath(filename[:0], filename, {})
    return abspath(path)


def _joinrealpath--- This code section failed: ---

 L. 394         0  LOAD_GLOBAL              isinstance
                2  LOAD_FAST                'path'
                4  LOAD_GLOBAL              bytes
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_FALSE    24  'to 24'

 L. 395        10  LOAD_CONST               b'/'
               12  STORE_FAST               'sep'

 L. 396        14  LOAD_CONST               b'.'
               16  STORE_FAST               'curdir'

 L. 397        18  LOAD_CONST               b'..'
               20  STORE_FAST               'pardir'
               22  JUMP_FORWARD         36  'to 36'
             24_0  COME_FROM             8  '8'

 L. 399        24  LOAD_STR                 '/'
               26  STORE_FAST               'sep'

 L. 400        28  LOAD_STR                 '.'
               30  STORE_FAST               'curdir'

 L. 401        32  LOAD_STR                 '..'
               34  STORE_FAST               'pardir'
             36_0  COME_FROM            22  '22'

 L. 403        36  LOAD_GLOBAL              isabs
               38  LOAD_FAST                'rest'
               40  CALL_FUNCTION_1       1  '1 positional argument'
               42  POP_JUMP_IF_FALSE    60  'to 60'

 L. 404        44  LOAD_FAST                'rest'
               46  LOAD_CONST               1
               48  LOAD_CONST               None
               50  BUILD_SLICE_2         2 
               52  BINARY_SUBSCR    
               54  STORE_FAST               'rest'

 L. 405        56  LOAD_FAST                'sep'
               58  STORE_FAST               'path'
             60_0  COME_FROM            42  '42'

 L. 407        60  SETUP_LOOP          276  'to 276'
             62_0  COME_FROM            86  '86'
               62  LOAD_FAST                'rest'
            64_66  POP_JUMP_IF_FALSE   274  'to 274'

 L. 408        68  LOAD_FAST                'rest'
               70  LOAD_METHOD              partition
               72  LOAD_FAST                'sep'
               74  CALL_METHOD_1         1  '1 positional argument'
               76  UNPACK_SEQUENCE_3     3 
               78  STORE_FAST               'name'
               80  STORE_FAST               '_'
               82  STORE_FAST               'rest'

 L. 409        84  LOAD_FAST                'name'
               86  POP_JUMP_IF_FALSE    62  'to 62'
               88  LOAD_FAST                'name'
               90  LOAD_FAST                'curdir'
               92  COMPARE_OP               ==
               94  POP_JUMP_IF_FALSE    98  'to 98'

 L. 411        96  CONTINUE             62  'to 62'
             98_0  COME_FROM            94  '94'

 L. 412        98  LOAD_FAST                'name'
              100  LOAD_FAST                'pardir'
              102  COMPARE_OP               ==
              104  POP_JUMP_IF_FALSE   150  'to 150'

 L. 414       106  LOAD_FAST                'path'
              108  POP_JUMP_IF_FALSE   144  'to 144'

 L. 415       110  LOAD_GLOBAL              split
              112  LOAD_FAST                'path'
              114  CALL_FUNCTION_1       1  '1 positional argument'
              116  UNPACK_SEQUENCE_2     2 
              118  STORE_FAST               'path'
              120  STORE_FAST               'name'

 L. 416       122  LOAD_FAST                'name'
              124  LOAD_FAST                'pardir'
              126  COMPARE_OP               ==
              128  POP_JUMP_IF_FALSE   148  'to 148'

 L. 417       130  LOAD_GLOBAL              join
              132  LOAD_FAST                'path'
              134  LOAD_FAST                'pardir'
              136  LOAD_FAST                'pardir'
              138  CALL_FUNCTION_3       3  '3 positional arguments'
              140  STORE_FAST               'path'
              142  JUMP_BACK            62  'to 62'
            144_0  COME_FROM           108  '108'

 L. 419       144  LOAD_FAST                'pardir'
              146  STORE_FAST               'path'
            148_0  COME_FROM           128  '128'

 L. 420       148  CONTINUE             62  'to 62'
            150_0  COME_FROM           104  '104'

 L. 421       150  LOAD_GLOBAL              join
              152  LOAD_FAST                'path'
              154  LOAD_FAST                'name'
              156  CALL_FUNCTION_2       2  '2 positional arguments'
              158  STORE_FAST               'newpath'

 L. 422       160  LOAD_GLOBAL              islink
              162  LOAD_FAST                'newpath'
              164  CALL_FUNCTION_1       1  '1 positional argument'
              166  POP_JUMP_IF_TRUE    174  'to 174'

 L. 423       168  LOAD_FAST                'newpath'
              170  STORE_FAST               'path'

 L. 424       172  CONTINUE             62  'to 62'
            174_0  COME_FROM           166  '166'

 L. 426       174  LOAD_FAST                'newpath'
              176  LOAD_FAST                'seen'
              178  COMPARE_OP               in
              180  POP_JUMP_IF_FALSE   214  'to 214'

 L. 428       182  LOAD_FAST                'seen'
              184  LOAD_FAST                'newpath'
              186  BINARY_SUBSCR    
              188  STORE_FAST               'path'

 L. 429       190  LOAD_FAST                'path'
              192  LOAD_CONST               None
              194  COMPARE_OP               is-not
              196  POP_JUMP_IF_FALSE   200  'to 200'

 L. 431       198  CONTINUE             62  'to 62'
            200_0  COME_FROM           196  '196'

 L. 434       200  LOAD_GLOBAL              join
              202  LOAD_FAST                'newpath'
              204  LOAD_FAST                'rest'
              206  CALL_FUNCTION_2       2  '2 positional arguments'
              208  LOAD_CONST               False
              210  BUILD_TUPLE_2         2 
              212  RETURN_VALUE     
            214_0  COME_FROM           180  '180'

 L. 435       214  LOAD_CONST               None
              216  LOAD_FAST                'seen'
              218  LOAD_FAST                'newpath'
              220  STORE_SUBSCR     

 L. 436       222  LOAD_GLOBAL              _joinrealpath
              224  LOAD_FAST                'path'
              226  LOAD_GLOBAL              os
              228  LOAD_METHOD              readlink
              230  LOAD_FAST                'newpath'
              232  CALL_METHOD_1         1  '1 positional argument'
              234  LOAD_FAST                'seen'
              236  CALL_FUNCTION_3       3  '3 positional arguments'
              238  UNPACK_SEQUENCE_2     2 
              240  STORE_FAST               'path'
              242  STORE_FAST               'ok'

 L. 437       244  LOAD_FAST                'ok'
          246_248  POP_JUMP_IF_TRUE    264  'to 264'

 L. 438       250  LOAD_GLOBAL              join
              252  LOAD_FAST                'path'
              254  LOAD_FAST                'rest'
              256  CALL_FUNCTION_2       2  '2 positional arguments'
              258  LOAD_CONST               False
              260  BUILD_TUPLE_2         2 
              262  RETURN_VALUE     
            264_0  COME_FROM           246  '246'

 L. 439       264  LOAD_FAST                'path'
              266  LOAD_FAST                'seen'
              268  LOAD_FAST                'newpath'
              270  STORE_SUBSCR     
              272  JUMP_BACK            62  'to 62'
            274_0  COME_FROM            64  '64'
              274  POP_BLOCK        
            276_0  COME_FROM_LOOP       60  '60'

 L. 441       276  LOAD_FAST                'path'
              278  LOAD_CONST               True
              280  BUILD_TUPLE_2         2 
              282  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_GLOBAL' instruction at offset 150


supports_unicode_filenames = sys.platform == 'darwin'

def relpath(path, start=None):
    if not path:
        raise ValueError('no path specified')
    else:
        path = os.fspath(path)
        if isinstance(path, bytes):
            curdir = b'.'
            sep = b'/'
            pardir = b'..'
        else:
            curdir = '.'
            sep = '/'
            pardir = '..'
        if start is None:
            start = curdir
        else:
            start = os.fspath(start)
    try:
        start_list = [x for x in abspath(start).split(sep) if x]
        path_list = [x for x in abspath(path).split(sep) if x]
        i = len(commonprefix([start_list, path_list]))
        rel_list = [
         pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)
    except (TypeError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        raise


def commonpath(paths):
    if not paths:
        raise ValueError('commonpath() arg is an empty sequence')
    else:
        paths = tuple(map(os.fspath, paths))
        if isinstance(paths[0], bytes):
            sep = b'/'
            curdir = b'.'
        else:
            sep = '/'
        curdir = '.'
    try:
        split_paths = [path.split(sep) for path in paths]
        try:
            isabs, = set((p[:1] == sep for p in paths))
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths") from None

        split_paths = [[c for c in s if c if c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        common = s1
        for i, c in enumerate(s1):
            if c != s2[i]:
                common = s1[:i]
                break

        prefix = sep if isabs else sep[:0]
        return prefix + sep.join(common)
    except (TypeError, AttributeError):
        (genericpath._check_arg_types)(*('commonpath', ), *paths)
        raise