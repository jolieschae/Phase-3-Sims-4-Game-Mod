# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\ntpath.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 23129 bytes
curdir = '.'
pardir = '..'
extsep = '.'
sep = '\\'
pathsep = ';'
altsep = '/'
defpath = '.;C:\\bin'
devnull = 'nul'
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
 "'curdir'", 
 "'pardir'", "'sep'", "'pathsep'", "'defpath'", "'altsep'", 
 "'extsep'", 
 "'devnull'", "'realpath'", "'supports_unicode_filenames'", "'relpath'", 
 "'samefile'", 
 "'sameopenfile'", "'samestat'", "'commonpath'"]

def _get_bothseps(path):
    if isinstance(path, bytes):
        return b'\\/'
    return '\\/'


def normcase(s):
    s = os.fspath(s)
    try:
        if isinstance(s, bytes):
            return s.replace(b'/', b'\\').lower()
        return s.replace('/', '\\').lower()
    except (TypeError, AttributeError):
        if not isinstance(s, (bytes, str)):
            raise TypeError('normcase() argument must be str or bytes, not %r' % s.__class__.__name__) from None
        raise


def isabs(s):
    s = os.fspath(s)
    s = splitdrive(s)[1]
    return len(s) > 0 and s[0] in _get_bothseps(s)


def join(path, *paths):
    path = os.fspath(path)
    if isinstance(path, bytes):
        sep = b'\\'
        seps = b'\\/'
        colon = b':'
    else:
        sep = '\\'
        seps = '\\/'
        colon = ':'
    try:
        if not paths:
            path[:0] + sep
        result_drive, result_path = splitdrive(path)
        for p in map(os.fspath, paths):
            p_drive, p_path = splitdrive(p)
            if p_path and p_path[0] in seps:
                if not (p_drive or result_drive):
                    result_drive = p_drive
                result_path = p_path
                continue
            else:
                if p_drive:
                    if p_drive != result_drive:
                        if p_drive.lower() != result_drive.lower():
                            result_drive = p_drive
                            result_path = p_path
                            continue
                        result_drive = p_drive
                elif result_path and result_path[-1] not in seps:
                    result_path = result_path + sep
                result_path = result_path + p_path

        if result_path:
            if result_path[0] not in seps:
                if result_drive:
                    if result_drive[-1:] != colon:
                        return result_drive + sep + result_path
        return result_drive + result_path
    except (TypeError, AttributeError, BytesWarning):
        (genericpath._check_arg_types)('join', path, *paths)
        raise


def splitdrive(p):
    p = os.fspath(p)
    if len(p) >= 2:
        if isinstance(p, bytes):
            sep = b'\\'
            altsep = b'/'
            colon = b':'
        else:
            sep = '\\'
            altsep = '/'
            colon = ':'
        normp = p.replace(altsep, sep)
        if normp[0:2] == sep * 2:
            if normp[2:3] != sep:
                index = normp.find(sep, 2)
                if index == -1:
                    return (
                     p[:0], p)
                index2 = normp.find(sep, index + 1)
                if index2 == index + 1:
                    return (
                     p[:0], p)
                if index2 == -1:
                    index2 = len(p)
                return (
                 p[:index2], p[index2:])
        if normp[1:2] == colon:
            return (
             p[:2], p[2:])
    return (
     p[:0], p)


def split(p):
    p = os.fspath(p)
    seps = _get_bothseps(p)
    d, p = splitdrive(p)
    i = len(p)
    while i and p[i - 1] not in seps:
        i -= 1

    head, tail = p[:i], p[i:]
    head = head.rstrip(seps) or head
    return (d + head, tail)


def splitext(p):
    p = os.fspath(p)
    if isinstance(p, bytes):
        return genericpath._splitext(p, b'\\', b'/', b'.')
    return genericpath._splitext(p, '\\', '/', '.')


splitext.__doc__ = genericpath._splitext.__doc__

def basename(p):
    return split(p)[1]


def dirname(p):
    return split(p)[0]


def islink(path):
    try:
        st = os.lstat(path)
    except (OSError, AttributeError):
        return False
    else:
        return stat.S_ISLNK(st.st_mode)


def lexists(path):
    try:
        st = os.lstat(path)
    except OSError:
        return False
    else:
        return True


try:
    from nt import _getvolumepathname
except ImportError:
    _getvolumepathname = None

def ismount(path):
    path = os.fspath(path)
    seps = _get_bothseps(path)
    path = abspath(path)
    root, rest = splitdrive(path)
    if root:
        if root[0] in seps:
            return not rest or rest in seps
    if rest in seps:
        return True
    if _getvolumepathname:
        return path.rstrip(seps) == _getvolumepathname(path).rstrip(seps)
    return False


def expanduser(path):
    path = os.fspath(path)
    if isinstance(path, bytes):
        tilde = b'~'
    else:
        tilde = '~'
    if not path.startswith(tilde):
        return path
    i, n = 1, len(path)
    while i < n and path[i] not in _get_bothseps(path):
        i += 1

    if 'HOME' in os.environ:
        userhome = os.environ['HOME']
    else:
        if 'USERPROFILE' in os.environ:
            userhome = os.environ['USERPROFILE']
        else:
            if 'HOMEPATH' not in os.environ:
                return path
            try:
                drive = os.environ['HOMEDRIVE']
            except KeyError:
                drive = ''

            userhome = join(drive, os.environ['HOMEPATH'])
    if isinstance(path, bytes):
        userhome = os.fsencode(userhome)
    if i != 1:
        userhome = join(dirname(userhome), path[1:i])
    return userhome + path[i:]


def expandvars--- This code section failed: ---

 L. 341         0  LOAD_GLOBAL              os
                2  LOAD_METHOD              fspath
                4  LOAD_FAST                'path'
                6  CALL_METHOD_1         1  '1 positional argument'
                8  STORE_FAST               'path'

 L. 342        10  LOAD_GLOBAL              isinstance
               12  LOAD_FAST                'path'
               14  LOAD_GLOBAL              bytes
               16  CALL_FUNCTION_2       2  '2 positional arguments'
               18  POP_JUMP_IF_FALSE   104  'to 104'

 L. 343        20  LOAD_CONST               b'$'
               22  LOAD_FAST                'path'
               24  COMPARE_OP               not-in
               26  POP_JUMP_IF_FALSE    40  'to 40'
               28  LOAD_CONST               b'%'
               30  LOAD_FAST                'path'
               32  COMPARE_OP               not-in
               34  POP_JUMP_IF_FALSE    40  'to 40'

 L. 344        36  LOAD_FAST                'path'
               38  RETURN_VALUE     
             40_0  COME_FROM            34  '34'
             40_1  COME_FROM            26  '26'

 L. 345        40  LOAD_CONST               0
               42  LOAD_CONST               None
               44  IMPORT_NAME              string
               46  STORE_FAST               'string'

 L. 346        48  LOAD_GLOBAL              bytes
               50  LOAD_FAST                'string'
               52  LOAD_ATTR                ascii_letters
               54  LOAD_FAST                'string'
               56  LOAD_ATTR                digits
               58  BINARY_ADD       
               60  LOAD_STR                 '_-'
               62  BINARY_ADD       
               64  LOAD_STR                 'ascii'
               66  CALL_FUNCTION_2       2  '2 positional arguments'
               68  STORE_FAST               'varchars'

 L. 347        70  LOAD_CONST               b"'"
               72  STORE_FAST               'quote'

 L. 348        74  LOAD_CONST               b'%'
               76  STORE_FAST               'percent'

 L. 349        78  LOAD_CONST               b'{'
               80  STORE_FAST               'brace'

 L. 350        82  LOAD_CONST               b'}'
               84  STORE_FAST               'rbrace'

 L. 351        86  LOAD_CONST               b'$'
               88  STORE_FAST               'dollar'

 L. 352        90  LOAD_GLOBAL              getattr
               92  LOAD_GLOBAL              os
               94  LOAD_STR                 'environb'
               96  LOAD_CONST               None
               98  CALL_FUNCTION_3       3  '3 positional arguments'
              100  STORE_FAST               'environ'
              102  JUMP_FORWARD        174  'to 174'
            104_0  COME_FROM            18  '18'

 L. 354       104  LOAD_STR                 '$'
              106  LOAD_FAST                'path'
              108  COMPARE_OP               not-in
              110  POP_JUMP_IF_FALSE   124  'to 124'
              112  LOAD_STR                 '%'
              114  LOAD_FAST                'path'
              116  COMPARE_OP               not-in
              118  POP_JUMP_IF_FALSE   124  'to 124'

 L. 355       120  LOAD_FAST                'path'
              122  RETURN_VALUE     
            124_0  COME_FROM           118  '118'
            124_1  COME_FROM           110  '110'

 L. 356       124  LOAD_CONST               0
              126  LOAD_CONST               None
              128  IMPORT_NAME              string
              130  STORE_FAST               'string'

 L. 357       132  LOAD_FAST                'string'
              134  LOAD_ATTR                ascii_letters
              136  LOAD_FAST                'string'
              138  LOAD_ATTR                digits
              140  BINARY_ADD       
              142  LOAD_STR                 '_-'
              144  BINARY_ADD       
              146  STORE_FAST               'varchars'

 L. 358       148  LOAD_STR                 "'"
              150  STORE_FAST               'quote'

 L. 359       152  LOAD_STR                 '%'
              154  STORE_FAST               'percent'

 L. 360       156  LOAD_STR                 '{'
              158  STORE_FAST               'brace'

 L. 361       160  LOAD_STR                 '}'
              162  STORE_FAST               'rbrace'

 L. 362       164  LOAD_STR                 '$'
              166  STORE_FAST               'dollar'

 L. 363       168  LOAD_GLOBAL              os
              170  LOAD_ATTR                environ
              172  STORE_FAST               'environ'
            174_0  COME_FROM           102  '102'

 L. 364       174  LOAD_FAST                'path'
              176  LOAD_CONST               None
              178  LOAD_CONST               0
              180  BUILD_SLICE_2         2 
              182  BINARY_SUBSCR    
              184  STORE_FAST               'res'

 L. 365       186  LOAD_CONST               0
              188  STORE_FAST               'index'

 L. 366       190  LOAD_GLOBAL              len
              192  LOAD_FAST                'path'
              194  CALL_FUNCTION_1       1  '1 positional argument'
              196  STORE_FAST               'pathlen'

 L. 367   198_200  SETUP_LOOP         1080  'to 1080'
              202  LOAD_FAST                'index'
              204  LOAD_FAST                'pathlen'
              206  COMPARE_OP               <
          208_210  POP_JUMP_IF_FALSE  1078  'to 1078'

 L. 368       212  LOAD_FAST                'path'
              214  LOAD_FAST                'index'
              216  LOAD_FAST                'index'
              218  LOAD_CONST               1
              220  BINARY_ADD       
              222  BUILD_SLICE_2         2 
              224  BINARY_SUBSCR    
              226  STORE_FAST               'c'

 L. 369       228  LOAD_FAST                'c'
              230  LOAD_FAST                'quote'
              232  COMPARE_OP               ==
          234_236  POP_JUMP_IF_FALSE   348  'to 348'

 L. 370       238  LOAD_FAST                'path'
              240  LOAD_FAST                'index'
              242  LOAD_CONST               1
              244  BINARY_ADD       
              246  LOAD_CONST               None
              248  BUILD_SLICE_2         2 
              250  BINARY_SUBSCR    
              252  STORE_FAST               'path'

 L. 371       254  LOAD_GLOBAL              len
              256  LOAD_FAST                'path'
              258  CALL_FUNCTION_1       1  '1 positional argument'
              260  STORE_FAST               'pathlen'

 L. 372       262  SETUP_EXCEPT        302  'to 302'

 L. 373       264  LOAD_FAST                'path'
              266  LOAD_METHOD              index
              268  LOAD_FAST                'c'
              270  CALL_METHOD_1         1  '1 positional argument'
              272  STORE_FAST               'index'

 L. 374       274  LOAD_FAST                'res'
              276  LOAD_FAST                'c'
              278  LOAD_FAST                'path'
              280  LOAD_CONST               None
              282  LOAD_FAST                'index'
              284  LOAD_CONST               1
              286  BINARY_ADD       
              288  BUILD_SLICE_2         2 
              290  BINARY_SUBSCR    
              292  BINARY_ADD       
              294  INPLACE_ADD      
              296  STORE_FAST               'res'
              298  POP_BLOCK        
              300  JUMP_FORWARD       1068  'to 1068'
            302_0  COME_FROM_EXCEPT    262  '262'

 L. 375       302  DUP_TOP          
              304  LOAD_GLOBAL              ValueError
              306  COMPARE_OP               exception-match
          308_310  POP_JUMP_IF_FALSE   342  'to 342'
              312  POP_TOP          
              314  POP_TOP          
              316  POP_TOP          

 L. 376       318  LOAD_FAST                'res'
              320  LOAD_FAST                'c'
              322  LOAD_FAST                'path'
              324  BINARY_ADD       
              326  INPLACE_ADD      
              328  STORE_FAST               'res'

 L. 377       330  LOAD_FAST                'pathlen'
              332  LOAD_CONST               1
              334  BINARY_SUBTRACT  
              336  STORE_FAST               'index'
              338  POP_EXCEPT       
              340  JUMP_FORWARD       1068  'to 1068'
            342_0  COME_FROM           308  '308'
              342  END_FINALLY      
          344_346  JUMP_FORWARD       1068  'to 1068'
            348_0  COME_FROM           234  '234'

 L. 378       348  LOAD_FAST                'c'
              350  LOAD_FAST                'percent'
              352  COMPARE_OP               ==
          354_356  POP_JUMP_IF_FALSE   590  'to 590'

 L. 379       358  LOAD_FAST                'path'
              360  LOAD_FAST                'index'
              362  LOAD_CONST               1
              364  BINARY_ADD       
              366  LOAD_FAST                'index'
              368  LOAD_CONST               2
              370  BINARY_ADD       
              372  BUILD_SLICE_2         2 
              374  BINARY_SUBSCR    
              376  LOAD_FAST                'percent'
              378  COMPARE_OP               ==
          380_382  POP_JUMP_IF_FALSE   402  'to 402'

 L. 380       384  LOAD_FAST                'res'
              386  LOAD_FAST                'c'
              388  INPLACE_ADD      
              390  STORE_FAST               'res'

 L. 381       392  LOAD_FAST                'index'
              394  LOAD_CONST               1
              396  INPLACE_ADD      
              398  STORE_FAST               'index'
              400  JUMP_FORWARD       1068  'to 1068'
            402_0  COME_FROM           380  '380'

 L. 383       402  LOAD_FAST                'path'
              404  LOAD_FAST                'index'
              406  LOAD_CONST               1
              408  BINARY_ADD       
              410  LOAD_CONST               None
              412  BUILD_SLICE_2         2 
              414  BINARY_SUBSCR    
              416  STORE_FAST               'path'

 L. 384       418  LOAD_GLOBAL              len
              420  LOAD_FAST                'path'
              422  CALL_FUNCTION_1       1  '1 positional argument'
              424  STORE_FAST               'pathlen'

 L. 385       426  SETUP_EXCEPT        442  'to 442'

 L. 386       428  LOAD_FAST                'path'
              430  LOAD_METHOD              index
              432  LOAD_FAST                'percent'
              434  CALL_METHOD_1         1  '1 positional argument'
              436  STORE_FAST               'index'
              438  POP_BLOCK        
              440  JUMP_FORWARD        484  'to 484'
            442_0  COME_FROM_EXCEPT    426  '426'

 L. 387       442  DUP_TOP          
              444  LOAD_GLOBAL              ValueError
              446  COMPARE_OP               exception-match
          448_450  POP_JUMP_IF_FALSE   482  'to 482'
              452  POP_TOP          
              454  POP_TOP          
              456  POP_TOP          

 L. 388       458  LOAD_FAST                'res'
              460  LOAD_FAST                'percent'
              462  LOAD_FAST                'path'
              464  BINARY_ADD       
              466  INPLACE_ADD      
              468  STORE_FAST               'res'

 L. 389       470  LOAD_FAST                'pathlen'
              472  LOAD_CONST               1
              474  BINARY_SUBTRACT  
              476  STORE_FAST               'index'
              478  POP_EXCEPT       
              480  JUMP_FORWARD       1068  'to 1068'
            482_0  COME_FROM           448  '448'
              482  END_FINALLY      
            484_0  COME_FROM           440  '440'

 L. 391       484  LOAD_FAST                'path'
              486  LOAD_CONST               None
              488  LOAD_FAST                'index'
              490  BUILD_SLICE_2         2 
              492  BINARY_SUBSCR    
              494  STORE_FAST               'var'

 L. 392       496  SETUP_EXCEPT        544  'to 544'

 L. 393       498  LOAD_FAST                'environ'
              500  LOAD_CONST               None
              502  COMPARE_OP               is
          504_506  POP_JUMP_IF_FALSE   532  'to 532'

 L. 394       508  LOAD_GLOBAL              os
              510  LOAD_METHOD              fsencode
              512  LOAD_GLOBAL              os
              514  LOAD_ATTR                environ
              516  LOAD_GLOBAL              os
              518  LOAD_METHOD              fsdecode
              520  LOAD_FAST                'var'
              522  CALL_METHOD_1         1  '1 positional argument'
              524  BINARY_SUBSCR    
              526  CALL_METHOD_1         1  '1 positional argument'
              528  STORE_FAST               'value'
              530  JUMP_FORWARD        540  'to 540'
            532_0  COME_FROM           504  '504'

 L. 396       532  LOAD_FAST                'environ'
              534  LOAD_FAST                'var'
              536  BINARY_SUBSCR    
              538  STORE_FAST               'value'
            540_0  COME_FROM           530  '530'
              540  POP_BLOCK        
              542  JUMP_FORWARD        578  'to 578'
            544_0  COME_FROM_EXCEPT    496  '496'

 L. 397       544  DUP_TOP          
              546  LOAD_GLOBAL              KeyError
              548  COMPARE_OP               exception-match
          550_552  POP_JUMP_IF_FALSE   576  'to 576'
              554  POP_TOP          
              556  POP_TOP          
              558  POP_TOP          

 L. 398       560  LOAD_FAST                'percent'
              562  LOAD_FAST                'var'
              564  BINARY_ADD       
              566  LOAD_FAST                'percent'
              568  BINARY_ADD       
              570  STORE_FAST               'value'
              572  POP_EXCEPT       
              574  JUMP_FORWARD        578  'to 578'
            576_0  COME_FROM           550  '550'
              576  END_FINALLY      
            578_0  COME_FROM           574  '574'
            578_1  COME_FROM           542  '542'

 L. 399       578  LOAD_FAST                'res'
              580  LOAD_FAST                'value'
              582  INPLACE_ADD      
              584  STORE_FAST               'res'
          586_588  JUMP_FORWARD       1068  'to 1068'
            590_0  COME_FROM           354  '354'

 L. 400       590  LOAD_FAST                'c'
              592  LOAD_FAST                'dollar'
              594  COMPARE_OP               ==
          596_598  POP_JUMP_IF_FALSE  1060  'to 1060'

 L. 401       600  LOAD_FAST                'path'
              602  LOAD_FAST                'index'
              604  LOAD_CONST               1
              606  BINARY_ADD       
              608  LOAD_FAST                'index'
              610  LOAD_CONST               2
              612  BINARY_ADD       
              614  BUILD_SLICE_2         2 
              616  BINARY_SUBSCR    
              618  LOAD_FAST                'dollar'
              620  COMPARE_OP               ==
          622_624  POP_JUMP_IF_FALSE   646  'to 646'

 L. 402       626  LOAD_FAST                'res'
              628  LOAD_FAST                'c'
              630  INPLACE_ADD      
              632  STORE_FAST               'res'

 L. 403       634  LOAD_FAST                'index'
              636  LOAD_CONST               1
              638  INPLACE_ADD      
              640  STORE_FAST               'index'
          642_644  JUMP_ABSOLUTE      1068  'to 1068'
            646_0  COME_FROM           622  '622'

 L. 404       646  LOAD_FAST                'path'
              648  LOAD_FAST                'index'
              650  LOAD_CONST               1
              652  BINARY_ADD       
              654  LOAD_FAST                'index'
              656  LOAD_CONST               2
              658  BINARY_ADD       
              660  BUILD_SLICE_2         2 
              662  BINARY_SUBSCR    
              664  LOAD_FAST                'brace'
              666  COMPARE_OP               ==
          668_670  POP_JUMP_IF_FALSE   866  'to 866'

 L. 405       672  LOAD_FAST                'path'
              674  LOAD_FAST                'index'
              676  LOAD_CONST               2
              678  BINARY_ADD       
              680  LOAD_CONST               None
              682  BUILD_SLICE_2         2 
              684  BINARY_SUBSCR    
              686  STORE_FAST               'path'

 L. 406       688  LOAD_GLOBAL              len
              690  LOAD_FAST                'path'
              692  CALL_FUNCTION_1       1  '1 positional argument'
              694  STORE_FAST               'pathlen'

 L. 407       696  SETUP_EXCEPT        712  'to 712'

 L. 408       698  LOAD_FAST                'path'
              700  LOAD_METHOD              index
              702  LOAD_FAST                'rbrace'
              704  CALL_METHOD_1         1  '1 positional argument'
              706  STORE_FAST               'index'
              708  POP_BLOCK        
              710  JUMP_FORWARD        758  'to 758'
            712_0  COME_FROM_EXCEPT    696  '696'

 L. 409       712  DUP_TOP          
              714  LOAD_GLOBAL              ValueError
              716  COMPARE_OP               exception-match
          718_720  POP_JUMP_IF_FALSE   756  'to 756'
              722  POP_TOP          
              724  POP_TOP          
              726  POP_TOP          

 L. 410       728  LOAD_FAST                'res'
              730  LOAD_FAST                'dollar'
              732  LOAD_FAST                'brace'
              734  BINARY_ADD       
              736  LOAD_FAST                'path'
              738  BINARY_ADD       
              740  INPLACE_ADD      
              742  STORE_FAST               'res'

 L. 411       744  LOAD_FAST                'pathlen'
              746  LOAD_CONST               1
              748  BINARY_SUBTRACT  
              750  STORE_FAST               'index'
              752  POP_EXCEPT       
              754  JUMP_FORWARD        864  'to 864'
            756_0  COME_FROM           718  '718'
              756  END_FINALLY      
            758_0  COME_FROM           710  '710'

 L. 413       758  LOAD_FAST                'path'
              760  LOAD_CONST               None
              762  LOAD_FAST                'index'
              764  BUILD_SLICE_2         2 
              766  BINARY_SUBSCR    
              768  STORE_FAST               'var'

 L. 414       770  SETUP_EXCEPT        818  'to 818'

 L. 415       772  LOAD_FAST                'environ'
              774  LOAD_CONST               None
              776  COMPARE_OP               is
          778_780  POP_JUMP_IF_FALSE   806  'to 806'

 L. 416       782  LOAD_GLOBAL              os
              784  LOAD_METHOD              fsencode
              786  LOAD_GLOBAL              os
              788  LOAD_ATTR                environ
              790  LOAD_GLOBAL              os
              792  LOAD_METHOD              fsdecode
              794  LOAD_FAST                'var'
              796  CALL_METHOD_1         1  '1 positional argument'
              798  BINARY_SUBSCR    
              800  CALL_METHOD_1         1  '1 positional argument'
              802  STORE_FAST               'value'
              804  JUMP_FORWARD        814  'to 814'
            806_0  COME_FROM           778  '778'

 L. 418       806  LOAD_FAST                'environ'
              808  LOAD_FAST                'var'
              810  BINARY_SUBSCR    
              812  STORE_FAST               'value'
            814_0  COME_FROM           804  '804'
              814  POP_BLOCK        
              816  JUMP_FORWARD        856  'to 856'
            818_0  COME_FROM_EXCEPT    770  '770'

 L. 419       818  DUP_TOP          
              820  LOAD_GLOBAL              KeyError
              822  COMPARE_OP               exception-match
          824_826  POP_JUMP_IF_FALSE   854  'to 854'
              828  POP_TOP          
              830  POP_TOP          
              832  POP_TOP          

 L. 420       834  LOAD_FAST                'dollar'
              836  LOAD_FAST                'brace'
              838  BINARY_ADD       
              840  LOAD_FAST                'var'
              842  BINARY_ADD       
              844  LOAD_FAST                'rbrace'
              846  BINARY_ADD       
              848  STORE_FAST               'value'
              850  POP_EXCEPT       
              852  JUMP_FORWARD        856  'to 856'
            854_0  COME_FROM           824  '824'
              854  END_FINALLY      
            856_0  COME_FROM           852  '852'
            856_1  COME_FROM           816  '816'

 L. 421       856  LOAD_FAST                'res'
              858  LOAD_FAST                'value'
              860  INPLACE_ADD      
              862  STORE_FAST               'res'
            864_0  COME_FROM           754  '754'
              864  JUMP_FORWARD       1058  'to 1058'
            866_0  COME_FROM           668  '668'

 L. 423       866  LOAD_FAST                'path'
              868  LOAD_CONST               None
              870  LOAD_CONST               0
              872  BUILD_SLICE_2         2 
              874  BINARY_SUBSCR    
              876  STORE_FAST               'var'

 L. 424       878  LOAD_FAST                'index'
            880_0  COME_FROM           400  '400'
              880  LOAD_CONST               1
              882  INPLACE_ADD      
              884  STORE_FAST               'index'

 L. 425       886  LOAD_FAST                'path'
              888  LOAD_FAST                'index'
              890  LOAD_FAST                'index'
              892  LOAD_CONST               1
              894  BINARY_ADD       
              896  BUILD_SLICE_2         2 
              898  BINARY_SUBSCR    
              900  STORE_FAST               'c'

 L. 426       902  SETUP_LOOP          958  'to 958'
              904  LOAD_FAST                'c'
          906_908  POP_JUMP_IF_FALSE   956  'to 956'
              910  LOAD_FAST                'c'
              912  LOAD_FAST                'varchars'
              914  COMPARE_OP               in
          916_918  POP_JUMP_IF_FALSE   956  'to 956'

 L. 427       920  LOAD_FAST                'var'
              922  LOAD_FAST                'c'
              924  INPLACE_ADD      
              926  STORE_FAST               'var'

 L. 428       928  LOAD_FAST                'index'
              930  LOAD_CONST               1
              932  INPLACE_ADD      
              934  STORE_FAST               'index'

 L. 429       936  LOAD_FAST                'path'
              938  LOAD_FAST                'index'
              940  LOAD_FAST                'index'
              942  LOAD_CONST               1
              944  BINARY_ADD       
              946  BUILD_SLICE_2         2 
              948  BINARY_SUBSCR    
              950  STORE_FAST               'c'
          952_954  JUMP_BACK           904  'to 904'
            956_0  COME_FROM           916  '916'
            956_1  COME_FROM           906  '906'
              956  POP_BLOCK        
            958_0  COME_FROM_LOOP      902  '902'

 L. 430       958  SETUP_EXCEPT       1006  'to 1006'
            960_0  COME_FROM           480  '480'

 L. 431       960  LOAD_FAST                'environ'
              962  LOAD_CONST               None
              964  COMPARE_OP               is
          966_968  POP_JUMP_IF_FALSE   994  'to 994'

 L. 432       970  LOAD_GLOBAL              os
              972  LOAD_METHOD              fsencode
              974  LOAD_GLOBAL              os
              976  LOAD_ATTR                environ
              978  LOAD_GLOBAL              os
              980  LOAD_METHOD              fsdecode
              982  LOAD_FAST                'var'
              984  CALL_METHOD_1         1  '1 positional argument'
              986  BINARY_SUBSCR    
              988  CALL_METHOD_1         1  '1 positional argument'
              990  STORE_FAST               'value'
              992  JUMP_FORWARD       1002  'to 1002'
            994_0  COME_FROM           966  '966'

 L. 434       994  LOAD_FAST                'environ'
              996  LOAD_FAST                'var'
              998  BINARY_SUBSCR    
             1000  STORE_FAST               'value'
           1002_0  COME_FROM           992  '992'
             1002  POP_BLOCK        
             1004  JUMP_FORWARD       1036  'to 1036'
           1006_0  COME_FROM_EXCEPT    958  '958'

 L. 435      1006  DUP_TOP          
             1008  LOAD_GLOBAL              KeyError
             1010  COMPARE_OP               exception-match
         1012_1014  POP_JUMP_IF_FALSE  1034  'to 1034'
             1016  POP_TOP          
             1018  POP_TOP          
             1020  POP_TOP          
           1022_0  COME_FROM           300  '300'

 L. 436      1022  LOAD_FAST                'dollar'
             1024  LOAD_FAST                'var'
             1026  BINARY_ADD       
             1028  STORE_FAST               'value'
             1030  POP_EXCEPT       
             1032  JUMP_FORWARD       1036  'to 1036'
           1034_0  COME_FROM          1012  '1012'
             1034  END_FINALLY      
           1036_0  COME_FROM          1032  '1032'
           1036_1  COME_FROM          1004  '1004'

 L. 437      1036  LOAD_FAST                'res'
             1038  LOAD_FAST                'value'
             1040  INPLACE_ADD      
             1042  STORE_FAST               'res'

 L. 438      1044  LOAD_FAST                'c'
         1046_1048  POP_JUMP_IF_FALSE  1068  'to 1068'

 L. 439      1050  LOAD_FAST                'index'
             1052  LOAD_CONST               1
             1054  INPLACE_SUBTRACT 
             1056  STORE_FAST               'index'
           1058_0  COME_FROM           864  '864'
             1058  JUMP_FORWARD       1068  'to 1068'
           1060_0  COME_FROM           596  '596'

 L. 441      1060  LOAD_FAST                'res'
           1062_0  COME_FROM           340  '340'
             1062  LOAD_FAST                'c'
             1064  INPLACE_ADD      
             1066  STORE_FAST               'res'
           1068_0  COME_FROM          1058  '1058'
           1068_1  COME_FROM          1046  '1046'
           1068_2  COME_FROM           586  '586'
           1068_3  COME_FROM           344  '344'

 L. 442      1068  LOAD_FAST                'index'
             1070  LOAD_CONST               1
             1072  INPLACE_ADD      
             1074  STORE_FAST               'index'
             1076  JUMP_BACK           202  'to 202'
           1078_0  COME_FROM           208  '208'
             1078  POP_BLOCK        
           1080_0  COME_FROM_LOOP      198  '198'

 L. 443      1080  LOAD_FAST                'res'
             1082  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 880_0


def normpath(path):
    path = os.fspath(path)
    if isinstance(path, bytes):
        sep = b'\\'
        altsep = b'/'
        curdir = b'.'
        pardir = b'..'
        special_prefixes = (b'\\\\.\\', b'\\\\?\\')
    else:
        sep = '\\'
        altsep = '/'
        curdir = '.'
        pardir = '..'
        special_prefixes = ('\\\\.\\', '\\\\?\\')
    if path.startswith(special_prefixes):
        return path
    path = path.replace(altsep, sep)
    prefix, path = splitdrive(path)
    if path.startswith(sep):
        prefix += sep
        path = path.lstrip(sep)
    comps = path.split(sep)
    i = 0
    while i < len(comps):
        if not comps[i] or comps[i] == curdir:
            del comps[i]
        elif comps[i] == pardir:
            if i > 0 and comps[i - 1] != pardir:
                del comps[i - 1:i + 1]
                i -= 1
            else:
                if i == 0 and prefix.endswith(sep):
                    del comps[i]
                else:
                    i += 1
        else:
            i += 1

    if not prefix:
        if not comps:
            comps.append(curdir)
    return prefix + sep.join(comps)


try:
    from nt import _getfullpathname
except ImportError:

    def abspath(path):
        path = os.fspath(path)
        if not isabs(path):
            if isinstance(path, bytes):
                cwd = os.getcwdb()
            else:
                cwd = os.getcwd()
            path = join(cwd, path)
        return normpath(path)


else:

    def abspath(path):
        if path:
            path = os.fspath(path)
            try:
                path = _getfullpathname(path)
            except OSError:
                pass

        else:
            if isinstance(path, bytes):
                path = os.getcwdb()
            else:
                path = os.getcwd()
        return normpath(path)


realpath = abspath
supports_unicode_filenames = hasattr(sys, 'getwindowsversion') and sys.getwindowsversion()[3] >= 2

def relpath(path, start=None):
    path = os.fspath(path)
    if isinstance(path, bytes):
        sep = b'\\'
        curdir = b'.'
        pardir = b'..'
    else:
        sep = '\\'
        curdir = '.'
        pardir = '..'
    if start is None:
        start = curdir
    if not path:
        raise ValueError('no path specified')
    start = os.fspath(start)
    try:
        start_abs = abspath(normpath(start))
        path_abs = abspath(normpath(path))
        start_drive, start_rest = splitdrive(start_abs)
        path_drive, path_rest = splitdrive(path_abs)
        if normcase(start_drive) != normcase(path_drive):
            raise ValueError('path is on mount %r, start on mount %r' % (
             path_drive, start_drive))
        start_list = [x for x in start_rest.split(sep) if x]
        path_list = [x for x in path_rest.split(sep) if x]
        i = 0
        for e1, e2 in zip(start_list, path_list):
            if normcase(e1) != normcase(e2):
                break
            i += 1

        rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)
    except (TypeError, ValueError, AttributeError, BytesWarning, DeprecationWarning):
        genericpath._check_arg_types('relpath', path, start)
        raise


def commonpath(paths):
    if not paths:
        raise ValueError('commonpath() arg is an empty sequence')
    else:
        paths = tuple(map(os.fspath, paths))
        if isinstance(paths[0], bytes):
            sep = b'\\'
            altsep = b'/'
            curdir = b'.'
        else:
            sep = '\\'
        altsep = '/'
        curdir = '.'
    try:
        drivesplits = [splitdrive(p.replace(altsep, sep).lower()) for p in paths]
        split_paths = [p.split(sep) for d, p in drivesplits]
        try:
            isabs, = set((p[:1] == sep for d, p in drivesplits))
        except ValueError:
            raise ValueError("Can't mix absolute and relative paths") from None

        if len(set((d for d, p in drivesplits))) != 1:
            raise ValueError("Paths don't have the same drive")
        drive, path = splitdrive(paths[0].replace(altsep, sep))
        common = path.split(sep)
        common = [c for c in common if c if c != curdir]
        split_paths = [[c for c in s if c if c != curdir] for s in split_paths]
        s1 = min(split_paths)
        s2 = max(split_paths)
        for i, c in enumerate(s1):
            if c != s2[i]:
                common = common[:i]
                break
        else:
            common = common[:len(s1)]

        prefix = drive + sep if isabs else drive
        return prefix + sep.join(common)
    except (TypeError, AttributeError):
        (genericpath._check_arg_types)(*('commonpath', ), *paths)
        raise


try:
    if sys.getwindowsversion()[:2] >= (6, 0):
        from nt import _getfinalpathname
    else:
        raise ImportError
except (AttributeError, ImportError):

    def _getfinalpathname(f):
        return normcase(abspath(f))


try:
    from nt import _isdir as isdir
except ImportError:
    pass