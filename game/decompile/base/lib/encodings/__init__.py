# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5838 bytes
import codecs, sys
from . import aliases
_cache = {}
_unknown = '--unknown--'
_import_tail = ['*']
_aliases = aliases.aliases

class CodecRegistryError(LookupError, SystemError):
    pass


def normalize_encoding(encoding):
    if isinstance(encoding, bytes):
        encoding = str(encoding, 'ascii')
    chars = []
    punct = False
    for c in encoding:
        if c.isalnum() or c == '.':
            if punct:
                if chars:
                    chars.append('_')
            chars.append(c)
            punct = False
        else:
            punct = True

    return ''.join(chars)


def search_function--- This code section failed: ---

 L.  74         0  LOAD_GLOBAL              _cache
                2  LOAD_METHOD              get
                4  LOAD_FAST                'encoding'
                6  LOAD_GLOBAL              _unknown
                8  CALL_METHOD_2         2  '2 positional arguments'
               10  STORE_FAST               'entry'

 L.  75        12  LOAD_FAST                'entry'
               14  LOAD_GLOBAL              _unknown
               16  COMPARE_OP               is-not
               18  POP_JUMP_IF_FALSE    24  'to 24'

 L.  76        20  LOAD_FAST                'entry'
               22  RETURN_VALUE     
             24_0  COME_FROM            18  '18'

 L.  85        24  LOAD_GLOBAL              normalize_encoding
               26  LOAD_FAST                'encoding'
               28  CALL_FUNCTION_1       1  '1 positional argument'
               30  STORE_FAST               'norm_encoding'

 L.  86        32  LOAD_GLOBAL              _aliases
               34  LOAD_METHOD              get
               36  LOAD_FAST                'norm_encoding'
               38  CALL_METHOD_1         1  '1 positional argument'
               40  JUMP_IF_TRUE_OR_POP    58  'to 58'

 L.  87        42  LOAD_GLOBAL              _aliases
               44  LOAD_METHOD              get
               46  LOAD_FAST                'norm_encoding'
               48  LOAD_METHOD              replace
               50  LOAD_STR                 '.'
               52  LOAD_STR                 '_'
               54  CALL_METHOD_2         2  '2 positional arguments'
               56  CALL_METHOD_1         1  '1 positional argument'
             58_0  COME_FROM            40  '40'
               58  STORE_FAST               'aliased_encoding'

 L.  88        60  LOAD_FAST                'aliased_encoding'
               62  LOAD_CONST               None
               64  COMPARE_OP               is-not
               66  POP_JUMP_IF_FALSE    78  'to 78'

 L.  89        68  LOAD_FAST                'aliased_encoding'

 L.  90        70  LOAD_FAST                'norm_encoding'
               72  BUILD_LIST_2          2 
               74  STORE_FAST               'modnames'
               76  JUMP_FORWARD         84  'to 84'
             78_0  COME_FROM            66  '66'

 L.  92        78  LOAD_FAST                'norm_encoding'
               80  BUILD_LIST_1          1 
               82  STORE_FAST               'modnames'
             84_0  COME_FROM            76  '76'

 L.  93        84  SETUP_LOOP          162  'to 162'
               86  LOAD_FAST                'modnames'
               88  GET_ITER         
             90_0  COME_FROM            96  '96'
               90  FOR_ITER            156  'to 156'
               92  STORE_FAST               'modname'

 L.  94        94  LOAD_FAST                'modname'
               96  POP_JUMP_IF_FALSE    90  'to 90'
               98  LOAD_STR                 '.'
              100  LOAD_FAST                'modname'
              102  COMPARE_OP               in
              104  POP_JUMP_IF_FALSE   108  'to 108'

 L.  95       106  CONTINUE             90  'to 90'
            108_0  COME_FROM           104  '104'

 L.  96       108  SETUP_EXCEPT        132  'to 132'

 L.  99       110  LOAD_GLOBAL              __import__
              112  LOAD_STR                 'encodings.'
              114  LOAD_FAST                'modname'
              116  BINARY_ADD       
              118  LOAD_GLOBAL              _import_tail

 L. 100       120  LOAD_CONST               0
              122  LOAD_CONST               ('fromlist', 'level')
              124  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              126  STORE_FAST               'mod'
              128  POP_BLOCK        
              130  JUMP_FORWARD        152  'to 152'
            132_0  COME_FROM_EXCEPT    108  '108'

 L. 101       132  DUP_TOP          
              134  LOAD_GLOBAL              ImportError
              136  COMPARE_OP               exception-match
              138  POP_JUMP_IF_FALSE   150  'to 150'
              140  POP_TOP          
              142  POP_TOP          
              144  POP_TOP          

 L. 104       146  POP_EXCEPT       
              148  JUMP_BACK            90  'to 90'
            150_0  COME_FROM           138  '138'
              150  END_FINALLY      
            152_0  COME_FROM           130  '130'

 L. 106       152  BREAK_LOOP       
              154  JUMP_BACK            90  'to 90'
              156  POP_BLOCK        

 L. 108       158  LOAD_CONST               None
              160  STORE_FAST               'mod'
            162_0  COME_FROM_LOOP       84  '84'

 L. 110       162  SETUP_EXCEPT        174  'to 174'

 L. 111       164  LOAD_FAST                'mod'
              166  LOAD_ATTR                getregentry
              168  STORE_FAST               'getregentry'
              170  POP_BLOCK        
              172  JUMP_FORWARD        198  'to 198'
            174_0  COME_FROM_EXCEPT    162  '162'

 L. 112       174  DUP_TOP          
              176  LOAD_GLOBAL              AttributeError
              178  COMPARE_OP               exception-match
              180  POP_JUMP_IF_FALSE   196  'to 196'
              182  POP_TOP          
              184  POP_TOP          
              186  POP_TOP          

 L. 114       188  LOAD_CONST               None
              190  STORE_FAST               'mod'
              192  POP_EXCEPT       
              194  JUMP_FORWARD        198  'to 198'
            196_0  COME_FROM           180  '180'
              196  END_FINALLY      
            198_0  COME_FROM           194  '194'
            198_1  COME_FROM           172  '172'

 L. 116       198  LOAD_FAST                'mod'
              200  LOAD_CONST               None
              202  COMPARE_OP               is
              204  POP_JUMP_IF_FALSE   218  'to 218'

 L. 118       206  LOAD_CONST               None
              208  LOAD_GLOBAL              _cache
              210  LOAD_FAST                'encoding'
              212  STORE_SUBSCR     

 L. 119       214  LOAD_CONST               None
              216  RETURN_VALUE     
            218_0  COME_FROM           204  '204'

 L. 122       218  LOAD_FAST                'getregentry'
              220  CALL_FUNCTION_0       0  '0 positional arguments'
              222  STORE_FAST               'entry'

 L. 123       224  LOAD_GLOBAL              isinstance
              226  LOAD_FAST                'entry'
              228  LOAD_GLOBAL              codecs
              230  LOAD_ATTR                CodecInfo
              232  CALL_FUNCTION_2       2  '2 positional arguments'
          234_236  POP_JUMP_IF_TRUE    554  'to 554'

 L. 124       238  LOAD_CONST               4
              240  LOAD_GLOBAL              len
              242  LOAD_FAST                'entry'
              244  CALL_FUNCTION_1       1  '1 positional argument'
              246  DUP_TOP          
              248  ROT_THREE        
              250  COMPARE_OP               <=
          252_254  POP_JUMP_IF_FALSE   266  'to 266'
              256  LOAD_CONST               7
              258  COMPARE_OP               <=
          260_262  POP_JUMP_IF_TRUE    288  'to 288'
              264  JUMP_FORWARD        268  'to 268'
            266_0  COME_FROM           252  '252'
              266  POP_TOP          
            268_0  COME_FROM           264  '264'

 L. 125       268  LOAD_GLOBAL              CodecRegistryError
              270  LOAD_STR                 'module "%s" (%s) failed to register'

 L. 126       272  LOAD_FAST                'mod'
              274  LOAD_ATTR                __name__
              276  LOAD_FAST                'mod'
              278  LOAD_ATTR                __file__
              280  BUILD_TUPLE_2         2 
              282  BINARY_MODULO    
              284  CALL_FUNCTION_1       1  '1 positional argument'
              286  RAISE_VARARGS_1       1  'exception instance'
            288_0  COME_FROM           260  '260'

 L. 127       288  LOAD_GLOBAL              callable
              290  LOAD_FAST                'entry'
              292  LOAD_CONST               0
              294  BINARY_SUBSCR    
              296  CALL_FUNCTION_1       1  '1 positional argument'
          298_300  POP_JUMP_IF_FALSE   456  'to 456'
              302  LOAD_GLOBAL              callable
              304  LOAD_FAST                'entry'
              306  LOAD_CONST               1
              308  BINARY_SUBSCR    
              310  CALL_FUNCTION_1       1  '1 positional argument'
          312_314  POP_JUMP_IF_FALSE   456  'to 456'

 L. 128       316  LOAD_FAST                'entry'
              318  LOAD_CONST               2
              320  BINARY_SUBSCR    
              322  LOAD_CONST               None
              324  COMPARE_OP               is-not
          326_328  POP_JUMP_IF_FALSE   344  'to 344'
              330  LOAD_GLOBAL              callable
              332  LOAD_FAST                'entry'
              334  LOAD_CONST               2
              336  BINARY_SUBSCR    
              338  CALL_FUNCTION_1       1  '1 positional argument'
          340_342  POP_JUMP_IF_FALSE   456  'to 456'
            344_0  COME_FROM           326  '326'

 L. 129       344  LOAD_FAST                'entry'
              346  LOAD_CONST               3
              348  BINARY_SUBSCR    
              350  LOAD_CONST               None
              352  COMPARE_OP               is-not
          354_356  POP_JUMP_IF_FALSE   372  'to 372'
              358  LOAD_GLOBAL              callable
              360  LOAD_FAST                'entry'
              362  LOAD_CONST               3
              364  BINARY_SUBSCR    
              366  CALL_FUNCTION_1       1  '1 positional argument'
          368_370  POP_JUMP_IF_FALSE   456  'to 456'
            372_0  COME_FROM           354  '354'

 L. 130       372  LOAD_GLOBAL              len
              374  LOAD_FAST                'entry'
              376  CALL_FUNCTION_1       1  '1 positional argument'
              378  LOAD_CONST               4
              380  COMPARE_OP               >
          382_384  POP_JUMP_IF_FALSE   414  'to 414'
              386  LOAD_FAST                'entry'
              388  LOAD_CONST               4
              390  BINARY_SUBSCR    
              392  LOAD_CONST               None
              394  COMPARE_OP               is-not
          396_398  POP_JUMP_IF_FALSE   414  'to 414'
              400  LOAD_GLOBAL              callable
              402  LOAD_FAST                'entry'
              404  LOAD_CONST               4
              406  BINARY_SUBSCR    
              408  CALL_FUNCTION_1       1  '1 positional argument'
          410_412  POP_JUMP_IF_FALSE   456  'to 456'
            414_0  COME_FROM           396  '396'
            414_1  COME_FROM           382  '382'

 L. 131       414  LOAD_GLOBAL              len
              416  LOAD_FAST                'entry'
              418  CALL_FUNCTION_1       1  '1 positional argument'
              420  LOAD_CONST               5
              422  COMPARE_OP               >
          424_426  POP_JUMP_IF_FALSE   476  'to 476'
              428  LOAD_FAST                'entry'
              430  LOAD_CONST               5
              432  BINARY_SUBSCR    
              434  LOAD_CONST               None
              436  COMPARE_OP               is-not
          438_440  POP_JUMP_IF_FALSE   476  'to 476'
              442  LOAD_GLOBAL              callable
              444  LOAD_FAST                'entry'
              446  LOAD_CONST               5
              448  BINARY_SUBSCR    
              450  CALL_FUNCTION_1       1  '1 positional argument'
          452_454  POP_JUMP_IF_TRUE    476  'to 476'
            456_0  COME_FROM           410  '410'
            456_1  COME_FROM           368  '368'
            456_2  COME_FROM           340  '340'
            456_3  COME_FROM           312  '312'
            456_4  COME_FROM           298  '298'

 L. 132       456  LOAD_GLOBAL              CodecRegistryError
              458  LOAD_STR                 'incompatible codecs in module "%s" (%s)'

 L. 133       460  LOAD_FAST                'mod'
              462  LOAD_ATTR                __name__
              464  LOAD_FAST                'mod'
              466  LOAD_ATTR                __file__
              468  BUILD_TUPLE_2         2 
              470  BINARY_MODULO    
              472  CALL_FUNCTION_1       1  '1 positional argument'
              474  RAISE_VARARGS_1       1  'exception instance'
            476_0  COME_FROM           452  '452'
            476_1  COME_FROM           438  '438'
            476_2  COME_FROM           424  '424'

 L. 134       476  LOAD_GLOBAL              len
              478  LOAD_FAST                'entry'
              480  CALL_FUNCTION_1       1  '1 positional argument'
              482  LOAD_CONST               7
              484  COMPARE_OP               <
          486_488  POP_JUMP_IF_TRUE    504  'to 504'
              490  LOAD_FAST                'entry'
              492  LOAD_CONST               6
              494  BINARY_SUBSCR    
              496  LOAD_CONST               None
              498  COMPARE_OP               is
          500_502  POP_JUMP_IF_FALSE   544  'to 544'
            504_0  COME_FROM           486  '486'

 L. 135       504  LOAD_FAST                'entry'
              506  LOAD_CONST               (None,)
              508  LOAD_CONST               6
              510  LOAD_GLOBAL              len
              512  LOAD_FAST                'entry'
              514  CALL_FUNCTION_1       1  '1 positional argument'
              516  BINARY_SUBTRACT  
              518  BINARY_MULTIPLY  
              520  LOAD_FAST                'mod'
              522  LOAD_ATTR                __name__
              524  LOAD_METHOD              split
              526  LOAD_STR                 '.'
              528  LOAD_CONST               1
              530  CALL_METHOD_2         2  '2 positional arguments'
              532  LOAD_CONST               1
              534  BINARY_SUBSCR    
              536  BUILD_TUPLE_1         1 
              538  BINARY_ADD       
              540  INPLACE_ADD      
              542  STORE_FAST               'entry'
            544_0  COME_FROM           500  '500'

 L. 136       544  LOAD_GLOBAL              codecs
              546  LOAD_ATTR                CodecInfo
              548  LOAD_FAST                'entry'
              550  CALL_FUNCTION_EX      0  'positional arguments only'
              552  STORE_FAST               'entry'
            554_0  COME_FROM           234  '234'

 L. 139       554  LOAD_FAST                'entry'
              556  LOAD_GLOBAL              _cache
              558  LOAD_FAST                'encoding'
              560  STORE_SUBSCR     

 L. 143       562  SETUP_EXCEPT        576  'to 576'

 L. 144       564  LOAD_FAST                'mod'
              566  LOAD_METHOD              getaliases
              568  CALL_METHOD_0         0  '0 positional arguments'
              570  STORE_FAST               'codecaliases'
              572  POP_BLOCK        
              574  JUMP_FORWARD        598  'to 598'
            576_0  COME_FROM_EXCEPT    562  '562'

 L. 145       576  DUP_TOP          
              578  LOAD_GLOBAL              AttributeError
              580  COMPARE_OP               exception-match
          582_584  POP_JUMP_IF_FALSE   596  'to 596'
              586  POP_TOP          
              588  POP_TOP          
              590  POP_TOP          

 L. 146       592  POP_EXCEPT       
              594  JUMP_FORWARD        632  'to 632'
            596_0  COME_FROM           582  '582'
              596  END_FINALLY      
            598_0  COME_FROM           574  '574'

 L. 148       598  SETUP_LOOP          632  'to 632'
              600  LOAD_FAST                'codecaliases'
              602  GET_ITER         
            604_0  COME_FROM           614  '614'
              604  FOR_ITER            630  'to 630'
              606  STORE_FAST               'alias'

 L. 149       608  LOAD_FAST                'alias'
              610  LOAD_GLOBAL              _aliases
              612  COMPARE_OP               not-in
          614_616  POP_JUMP_IF_FALSE   604  'to 604'

 L. 150       618  LOAD_FAST                'modname'
              620  LOAD_GLOBAL              _aliases
              622  LOAD_FAST                'alias'
              624  STORE_SUBSCR     
          626_628  JUMP_BACK           604  'to 604'
              630  POP_BLOCK        
            632_0  COME_FROM_LOOP      598  '598'
            632_1  COME_FROM           594  '594'

 L. 153       632  LOAD_FAST                'entry'
              634  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM' instruction at offset 476_0


codecs.register(search_function)
if sys.platform == 'win32':

    def _alias_mbcs(encoding):
        try:
            import _winapi
            ansi_code_page = 'cp%s' % _winapi.GetACP()
            if encoding == ansi_code_page:
                import encodings.mbcs
                return encodings.mbcs.getregentry()
        except ImportError:
            pass


    codecs.register(_alias_mbcs)