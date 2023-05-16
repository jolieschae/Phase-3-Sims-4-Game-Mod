# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_pyio.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 93754 bytes
import os, abc, codecs, errno, stat, sys
from _thread import allocate_lock as Lock
if sys.platform in frozenset({'win32', 'cygwin'}):
    from msvcrt import setmode as _setmode
else:
    _setmode = None
import io
from io import __all__, SEEK_SET, SEEK_CUR, SEEK_END
valid_seek_flags = {
 0, 1, 2}
if hasattr(os, 'SEEK_HOLE'):
    valid_seek_flags.add(os.SEEK_HOLE)
    valid_seek_flags.add(os.SEEK_DATA)
DEFAULT_BUFFER_SIZE = 8192
BlockingIOError = BlockingIOError

def open--- This code section failed: ---

 L. 160         0  LOAD_GLOBAL              isinstance
                2  LOAD_FAST                'file'
                4  LOAD_GLOBAL              int
                6  CALL_FUNCTION_2       2  '2 positional arguments'
                8  POP_JUMP_IF_TRUE     20  'to 20'

 L. 161        10  LOAD_GLOBAL              os
               12  LOAD_METHOD              fspath
               14  LOAD_FAST                'file'
               16  CALL_METHOD_1         1  '1 positional argument'
               18  STORE_FAST               'file'
             20_0  COME_FROM             8  '8'

 L. 162        20  LOAD_GLOBAL              isinstance
               22  LOAD_FAST                'file'
               24  LOAD_GLOBAL              str
               26  LOAD_GLOBAL              bytes
               28  LOAD_GLOBAL              int
               30  BUILD_TUPLE_3         3 
               32  CALL_FUNCTION_2       2  '2 positional arguments'
               34  POP_JUMP_IF_TRUE     48  'to 48'

 L. 163        36  LOAD_GLOBAL              TypeError
               38  LOAD_STR                 'invalid file: %r'
               40  LOAD_FAST                'file'
               42  BINARY_MODULO    
               44  CALL_FUNCTION_1       1  '1 positional argument'
               46  RAISE_VARARGS_1       1  'exception instance'
             48_0  COME_FROM            34  '34'

 L. 164        48  LOAD_GLOBAL              isinstance
               50  LOAD_FAST                'mode'
               52  LOAD_GLOBAL              str
               54  CALL_FUNCTION_2       2  '2 positional arguments'
               56  POP_JUMP_IF_TRUE     70  'to 70'

 L. 165        58  LOAD_GLOBAL              TypeError
               60  LOAD_STR                 'invalid mode: %r'
               62  LOAD_FAST                'mode'
               64  BINARY_MODULO    
               66  CALL_FUNCTION_1       1  '1 positional argument'
               68  RAISE_VARARGS_1       1  'exception instance'
             70_0  COME_FROM            56  '56'

 L. 166        70  LOAD_GLOBAL              isinstance
               72  LOAD_FAST                'buffering'
               74  LOAD_GLOBAL              int
               76  CALL_FUNCTION_2       2  '2 positional arguments'
               78  POP_JUMP_IF_TRUE     92  'to 92'

 L. 167        80  LOAD_GLOBAL              TypeError
               82  LOAD_STR                 'invalid buffering: %r'
               84  LOAD_FAST                'buffering'
               86  BINARY_MODULO    
               88  CALL_FUNCTION_1       1  '1 positional argument'
               90  RAISE_VARARGS_1       1  'exception instance'
             92_0  COME_FROM            78  '78'

 L. 168        92  LOAD_FAST                'encoding'
               94  LOAD_CONST               None
               96  COMPARE_OP               is-not
               98  POP_JUMP_IF_FALSE   122  'to 122'
              100  LOAD_GLOBAL              isinstance
              102  LOAD_FAST                'encoding'
              104  LOAD_GLOBAL              str
              106  CALL_FUNCTION_2       2  '2 positional arguments'
              108  POP_JUMP_IF_TRUE    122  'to 122'

 L. 169       110  LOAD_GLOBAL              TypeError
              112  LOAD_STR                 'invalid encoding: %r'
              114  LOAD_FAST                'encoding'
              116  BINARY_MODULO    
              118  CALL_FUNCTION_1       1  '1 positional argument'
              120  RAISE_VARARGS_1       1  'exception instance'
            122_0  COME_FROM           108  '108'
            122_1  COME_FROM            98  '98'

 L. 170       122  LOAD_FAST                'errors'
              124  LOAD_CONST               None
              126  COMPARE_OP               is-not
              128  POP_JUMP_IF_FALSE   152  'to 152'
              130  LOAD_GLOBAL              isinstance
              132  LOAD_FAST                'errors'
              134  LOAD_GLOBAL              str
              136  CALL_FUNCTION_2       2  '2 positional arguments'
              138  POP_JUMP_IF_TRUE    152  'to 152'

 L. 171       140  LOAD_GLOBAL              TypeError
              142  LOAD_STR                 'invalid errors: %r'
              144  LOAD_FAST                'errors'
              146  BINARY_MODULO    
              148  CALL_FUNCTION_1       1  '1 positional argument'
              150  RAISE_VARARGS_1       1  'exception instance'
            152_0  COME_FROM           138  '138'
            152_1  COME_FROM           128  '128'

 L. 172       152  LOAD_GLOBAL              set
              154  LOAD_FAST                'mode'
              156  CALL_FUNCTION_1       1  '1 positional argument'
              158  STORE_FAST               'modes'

 L. 173       160  LOAD_FAST                'modes'
              162  LOAD_GLOBAL              set
              164  LOAD_STR                 'axrwb+tU'
              166  CALL_FUNCTION_1       1  '1 positional argument'
              168  BINARY_SUBTRACT  
              170  POP_JUMP_IF_TRUE    188  'to 188'
              172  LOAD_GLOBAL              len
              174  LOAD_FAST                'mode'
              176  CALL_FUNCTION_1       1  '1 positional argument'
              178  LOAD_GLOBAL              len
              180  LOAD_FAST                'modes'
              182  CALL_FUNCTION_1       1  '1 positional argument'
              184  COMPARE_OP               >
              186  POP_JUMP_IF_FALSE   200  'to 200'
            188_0  COME_FROM           170  '170'

 L. 174       188  LOAD_GLOBAL              ValueError
              190  LOAD_STR                 'invalid mode: %r'
              192  LOAD_FAST                'mode'
              194  BINARY_MODULO    
              196  CALL_FUNCTION_1       1  '1 positional argument'
              198  RAISE_VARARGS_1       1  'exception instance'
            200_0  COME_FROM           186  '186'

 L. 175       200  LOAD_STR                 'x'
              202  LOAD_FAST                'modes'
              204  COMPARE_OP               in
              206  STORE_FAST               'creating'

 L. 176       208  LOAD_STR                 'r'
              210  LOAD_FAST                'modes'
              212  COMPARE_OP               in
              214  STORE_FAST               'reading'

 L. 177       216  LOAD_STR                 'w'
              218  LOAD_FAST                'modes'
              220  COMPARE_OP               in
              222  STORE_FAST               'writing'

 L. 178       224  LOAD_STR                 'a'
              226  LOAD_FAST                'modes'
              228  COMPARE_OP               in
              230  STORE_FAST               'appending'

 L. 179       232  LOAD_STR                 '+'
              234  LOAD_FAST                'modes'
              236  COMPARE_OP               in
              238  STORE_FAST               'updating'

 L. 180       240  LOAD_STR                 't'
              242  LOAD_FAST                'modes'
              244  COMPARE_OP               in
              246  STORE_FAST               'text'

 L. 181       248  LOAD_STR                 'b'
              250  LOAD_FAST                'modes'
              252  COMPARE_OP               in
              254  STORE_FAST               'binary'

 L. 182       256  LOAD_STR                 'U'
              258  LOAD_FAST                'modes'
              260  COMPARE_OP               in
          262_264  POP_JUMP_IF_FALSE   324  'to 324'

 L. 183       266  LOAD_FAST                'creating'
          268_270  POP_JUMP_IF_TRUE    290  'to 290'
              272  LOAD_FAST                'writing'
          274_276  POP_JUMP_IF_TRUE    290  'to 290'
              278  LOAD_FAST                'appending'
          280_282  POP_JUMP_IF_TRUE    290  'to 290'
              284  LOAD_FAST                'updating'
          286_288  POP_JUMP_IF_FALSE   298  'to 298'
            290_0  COME_FROM           280  '280'
            290_1  COME_FROM           274  '274'
            290_2  COME_FROM           268  '268'

 L. 184       290  LOAD_GLOBAL              ValueError
              292  LOAD_STR                 "mode U cannot be combined with 'x', 'w', 'a', or '+'"
              294  CALL_FUNCTION_1       1  '1 positional argument'
              296  RAISE_VARARGS_1       1  'exception instance'
            298_0  COME_FROM           286  '286'

 L. 185       298  LOAD_CONST               0
              300  LOAD_CONST               None
              302  IMPORT_NAME              warnings
              304  STORE_FAST               'warnings'

 L. 186       306  LOAD_FAST                'warnings'
              308  LOAD_METHOD              warn
              310  LOAD_STR                 "'U' mode is deprecated"

 L. 187       312  LOAD_GLOBAL              DeprecationWarning
              314  LOAD_CONST               2
              316  CALL_METHOD_3         3  '3 positional arguments'
              318  POP_TOP          

 L. 188       320  LOAD_CONST               True
              322  STORE_FAST               'reading'
            324_0  COME_FROM           262  '262'

 L. 189       324  LOAD_FAST                'text'
          326_328  POP_JUMP_IF_FALSE   344  'to 344'
              330  LOAD_FAST                'binary'
          332_334  POP_JUMP_IF_FALSE   344  'to 344'

 L. 190       336  LOAD_GLOBAL              ValueError
              338  LOAD_STR                 "can't have text and binary mode at once"
              340  CALL_FUNCTION_1       1  '1 positional argument'
              342  RAISE_VARARGS_1       1  'exception instance'
            344_0  COME_FROM           332  '332'
            344_1  COME_FROM           326  '326'

 L. 191       344  LOAD_FAST                'creating'
              346  LOAD_FAST                'reading'
              348  BINARY_ADD       
              350  LOAD_FAST                'writing'
              352  BINARY_ADD       
              354  LOAD_FAST                'appending'
              356  BINARY_ADD       
              358  LOAD_CONST               1
              360  COMPARE_OP               >
          362_364  POP_JUMP_IF_FALSE   374  'to 374'

 L. 192       366  LOAD_GLOBAL              ValueError
              368  LOAD_STR                 "can't have read/write/append mode at once"
              370  CALL_FUNCTION_1       1  '1 positional argument'
              372  RAISE_VARARGS_1       1  'exception instance'
            374_0  COME_FROM           362  '362'

 L. 193       374  LOAD_FAST                'creating'
          376_378  POP_JUMP_IF_TRUE    406  'to 406'
              380  LOAD_FAST                'reading'
          382_384  POP_JUMP_IF_TRUE    406  'to 406'
              386  LOAD_FAST                'writing'
          388_390  POP_JUMP_IF_TRUE    406  'to 406'
              392  LOAD_FAST                'appending'
          394_396  POP_JUMP_IF_TRUE    406  'to 406'

 L. 194       398  LOAD_GLOBAL              ValueError
              400  LOAD_STR                 'must have exactly one of read/write/append mode'
              402  CALL_FUNCTION_1       1  '1 positional argument'
              404  RAISE_VARARGS_1       1  'exception instance'
            406_0  COME_FROM           394  '394'
            406_1  COME_FROM           388  '388'
            406_2  COME_FROM           382  '382'
            406_3  COME_FROM           376  '376'

 L. 195       406  LOAD_FAST                'binary'
          408_410  POP_JUMP_IF_FALSE   430  'to 430'
              412  LOAD_FAST                'encoding'
              414  LOAD_CONST               None
              416  COMPARE_OP               is-not
          418_420  POP_JUMP_IF_FALSE   430  'to 430'

 L. 196       422  LOAD_GLOBAL              ValueError
              424  LOAD_STR                 "binary mode doesn't take an encoding argument"
              426  CALL_FUNCTION_1       1  '1 positional argument'
              428  RAISE_VARARGS_1       1  'exception instance'
            430_0  COME_FROM           418  '418'
            430_1  COME_FROM           408  '408'

 L. 197       430  LOAD_FAST                'binary'
          432_434  POP_JUMP_IF_FALSE   454  'to 454'
              436  LOAD_FAST                'errors'
              438  LOAD_CONST               None
              440  COMPARE_OP               is-not
          442_444  POP_JUMP_IF_FALSE   454  'to 454'

 L. 198       446  LOAD_GLOBAL              ValueError
              448  LOAD_STR                 "binary mode doesn't take an errors argument"
              450  CALL_FUNCTION_1       1  '1 positional argument'
              452  RAISE_VARARGS_1       1  'exception instance'
            454_0  COME_FROM           442  '442'
            454_1  COME_FROM           432  '432'

 L. 199       454  LOAD_FAST                'binary'
          456_458  POP_JUMP_IF_FALSE   478  'to 478'
              460  LOAD_FAST                'newline'
              462  LOAD_CONST               None
              464  COMPARE_OP               is-not
          466_468  POP_JUMP_IF_FALSE   478  'to 478'

 L. 200       470  LOAD_GLOBAL              ValueError
              472  LOAD_STR                 "binary mode doesn't take a newline argument"
              474  CALL_FUNCTION_1       1  '1 positional argument'
              476  RAISE_VARARGS_1       1  'exception instance'
            478_0  COME_FROM           466  '466'
            478_1  COME_FROM           456  '456'

 L. 201       478  LOAD_GLOBAL              FileIO
              480  LOAD_FAST                'file'

 L. 205       482  LOAD_FAST                'creating'
          484_486  POP_JUMP_IF_FALSE   494  'to 494'
              488  LOAD_STR                 'x'
          490_492  JUMP_IF_TRUE_OR_POP   496  'to 496'
            494_0  COME_FROM           484  '484'
              494  LOAD_STR                 ''
            496_0  COME_FROM           490  '490'
              496  LOAD_FAST                'reading'
          498_500  POP_JUMP_IF_FALSE   508  'to 508'
              502  LOAD_STR                 'r'
          504_506  JUMP_IF_TRUE_OR_POP   510  'to 510'
            508_0  COME_FROM           498  '498'
              508  LOAD_STR                 ''
            510_0  COME_FROM           504  '504'
              510  BINARY_ADD       
              512  LOAD_FAST                'writing'
          514_516  POP_JUMP_IF_FALSE   524  'to 524'
              518  LOAD_STR                 'w'
          520_522  JUMP_IF_TRUE_OR_POP   526  'to 526'
            524_0  COME_FROM           514  '514'
              524  LOAD_STR                 ''
            526_0  COME_FROM           520  '520'
              526  BINARY_ADD       
              528  LOAD_FAST                'appending'
          530_532  POP_JUMP_IF_FALSE   540  'to 540'
              534  LOAD_STR                 'a'
          536_538  JUMP_IF_TRUE_OR_POP   542  'to 542'
            540_0  COME_FROM           530  '530'
              540  LOAD_STR                 ''
            542_0  COME_FROM           536  '536'
              542  BINARY_ADD       

 L. 206       544  LOAD_FAST                'updating'
          546_548  POP_JUMP_IF_FALSE   556  'to 556'
              550  LOAD_STR                 '+'
          552_554  JUMP_IF_TRUE_OR_POP   558  'to 558'
            556_0  COME_FROM           546  '546'
              556  LOAD_STR                 ''
            558_0  COME_FROM           552  '552'
              558  BINARY_ADD       

 L. 207       560  LOAD_FAST                'closefd'
              562  LOAD_FAST                'opener'
              564  LOAD_CONST               ('opener',)
              566  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              568  STORE_FAST               'raw'

 L. 208       570  LOAD_FAST                'raw'
              572  STORE_FAST               'result'

 L. 209   574_576  SETUP_EXCEPT        864  'to 864'

 L. 210       578  LOAD_CONST               False
              580  STORE_FAST               'line_buffering'

 L. 211       582  LOAD_FAST                'buffering'
              584  LOAD_CONST               1
              586  COMPARE_OP               ==
          588_590  POP_JUMP_IF_TRUE    612  'to 612'
              592  LOAD_FAST                'buffering'
              594  LOAD_CONST               0
              596  COMPARE_OP               <
          598_600  POP_JUMP_IF_FALSE   620  'to 620'
              602  LOAD_FAST                'raw'
              604  LOAD_METHOD              isatty
              606  CALL_METHOD_0         0  '0 positional arguments'
          608_610  POP_JUMP_IF_FALSE   620  'to 620'
            612_0  COME_FROM           588  '588'

 L. 212       612  LOAD_CONST               -1
              614  STORE_FAST               'buffering'

 L. 213       616  LOAD_CONST               True
              618  STORE_FAST               'line_buffering'
            620_0  COME_FROM           608  '608'
            620_1  COME_FROM           598  '598'

 L. 214       620  LOAD_FAST                'buffering'
              622  LOAD_CONST               0
              624  COMPARE_OP               <
          626_628  POP_JUMP_IF_FALSE   696  'to 696'

 L. 215       630  LOAD_GLOBAL              DEFAULT_BUFFER_SIZE
              632  STORE_FAST               'buffering'

 L. 216       634  SETUP_EXCEPT        656  'to 656'

 L. 217       636  LOAD_GLOBAL              os
              638  LOAD_METHOD              fstat
              640  LOAD_FAST                'raw'
              642  LOAD_METHOD              fileno
              644  CALL_METHOD_0         0  '0 positional arguments'
              646  CALL_METHOD_1         1  '1 positional argument'
              648  LOAD_ATTR                st_blksize
              650  STORE_FAST               'bs'
              652  POP_BLOCK        
              654  JUMP_FORWARD        682  'to 682'
            656_0  COME_FROM_EXCEPT    634  '634'

 L. 218       656  DUP_TOP          
              658  LOAD_GLOBAL              OSError
              660  LOAD_GLOBAL              AttributeError
              662  BUILD_TUPLE_2         2 
              664  COMPARE_OP               exception-match
          666_668  POP_JUMP_IF_FALSE   680  'to 680'
              670  POP_TOP          
              672  POP_TOP          
              674  POP_TOP          

 L. 219       676  POP_EXCEPT       
              678  JUMP_FORWARD        696  'to 696'
            680_0  COME_FROM           666  '666'
              680  END_FINALLY      
            682_0  COME_FROM           654  '654'

 L. 221       682  LOAD_FAST                'bs'
              684  LOAD_CONST               1
              686  COMPARE_OP               >
          688_690  POP_JUMP_IF_FALSE   696  'to 696'

 L. 222       692  LOAD_FAST                'bs'
              694  STORE_FAST               'buffering'
            696_0  COME_FROM           688  '688'
            696_1  COME_FROM           678  '678'
            696_2  COME_FROM           626  '626'

 L. 223       696  LOAD_FAST                'buffering'
              698  LOAD_CONST               0
              700  COMPARE_OP               <
          702_704  POP_JUMP_IF_FALSE   714  'to 714'

 L. 224       706  LOAD_GLOBAL              ValueError
              708  LOAD_STR                 'invalid buffering size'
              710  CALL_FUNCTION_1       1  '1 positional argument'
              712  RAISE_VARARGS_1       1  'exception instance'
            714_0  COME_FROM           702  '702'

 L. 225       714  LOAD_FAST                'buffering'
              716  LOAD_CONST               0
              718  COMPARE_OP               ==
          720_722  POP_JUMP_IF_FALSE   742  'to 742'

 L. 226       724  LOAD_FAST                'binary'
          726_728  POP_JUMP_IF_FALSE   734  'to 734'

 L. 227       730  LOAD_FAST                'result'
              732  RETURN_VALUE     
            734_0  COME_FROM           726  '726'

 L. 228       734  LOAD_GLOBAL              ValueError
              736  LOAD_STR                 "can't have unbuffered text I/O"
              738  CALL_FUNCTION_1       1  '1 positional argument'
              740  RAISE_VARARGS_1       1  'exception instance'
            742_0  COME_FROM           720  '720'

 L. 229       742  LOAD_FAST                'updating'
          744_746  POP_JUMP_IF_FALSE   760  'to 760'

 L. 230       748  LOAD_GLOBAL              BufferedRandom
              750  LOAD_FAST                'raw'
              752  LOAD_FAST                'buffering'
              754  CALL_FUNCTION_2       2  '2 positional arguments'
              756  STORE_FAST               'buffer'
              758  JUMP_FORWARD        820  'to 820'
            760_0  COME_FROM           744  '744'

 L. 231       760  LOAD_FAST                'creating'
          762_764  POP_JUMP_IF_TRUE    778  'to 778'
              766  LOAD_FAST                'writing'
          768_770  POP_JUMP_IF_TRUE    778  'to 778'
              772  LOAD_FAST                'appending'
          774_776  POP_JUMP_IF_FALSE   790  'to 790'
            778_0  COME_FROM           768  '768'
            778_1  COME_FROM           762  '762'

 L. 232       778  LOAD_GLOBAL              BufferedWriter
              780  LOAD_FAST                'raw'
              782  LOAD_FAST                'buffering'
              784  CALL_FUNCTION_2       2  '2 positional arguments'
              786  STORE_FAST               'buffer'
              788  JUMP_FORWARD        820  'to 820'
            790_0  COME_FROM           774  '774'

 L. 233       790  LOAD_FAST                'reading'
          792_794  POP_JUMP_IF_FALSE   808  'to 808'

 L. 234       796  LOAD_GLOBAL              BufferedReader
              798  LOAD_FAST                'raw'
              800  LOAD_FAST                'buffering'
              802  CALL_FUNCTION_2       2  '2 positional arguments'
              804  STORE_FAST               'buffer'
              806  JUMP_FORWARD        820  'to 820'
            808_0  COME_FROM           792  '792'

 L. 236       808  LOAD_GLOBAL              ValueError
              810  LOAD_STR                 'unknown mode: %r'
              812  LOAD_FAST                'mode'
              814  BINARY_MODULO    
              816  CALL_FUNCTION_1       1  '1 positional argument'
              818  RAISE_VARARGS_1       1  'exception instance'
            820_0  COME_FROM           806  '806'
            820_1  COME_FROM           788  '788'
            820_2  COME_FROM           758  '758'

 L. 237       820  LOAD_FAST                'buffer'
              822  STORE_FAST               'result'

 L. 238       824  LOAD_FAST                'binary'
          826_828  POP_JUMP_IF_FALSE   834  'to 834'

 L. 239       830  LOAD_FAST                'result'
              832  RETURN_VALUE     
            834_0  COME_FROM           826  '826'

 L. 240       834  LOAD_GLOBAL              TextIOWrapper
              836  LOAD_FAST                'buffer'
              838  LOAD_FAST                'encoding'
              840  LOAD_FAST                'errors'
              842  LOAD_FAST                'newline'
              844  LOAD_FAST                'line_buffering'
              846  CALL_FUNCTION_5       5  '5 positional arguments'
              848  STORE_FAST               'text'

 L. 241       850  LOAD_FAST                'text'
              852  STORE_FAST               'result'

 L. 242       854  LOAD_FAST                'mode'
              856  LOAD_FAST                'text'
              858  STORE_ATTR               mode

 L. 243       860  LOAD_FAST                'result'
              862  RETURN_VALUE     
            864_0  COME_FROM_EXCEPT    574  '574'

 L. 244       864  POP_TOP          
              866  POP_TOP          
              868  POP_TOP          

 L. 245       870  LOAD_FAST                'result'
              872  LOAD_METHOD              close
              874  CALL_METHOD_0         0  '0 positional arguments'
              876  POP_TOP          

 L. 246       878  RAISE_VARARGS_0       0  'reraise'
              880  POP_EXCEPT       
              882  JUMP_FORWARD        886  'to 886'
              884  END_FINALLY      
            886_0  COME_FROM           882  '882'

Parse error at or near `COME_FROM' instruction at offset 298_0


class DocDescriptor:

    def __get__(self, obj, typ):
        return "open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True)\n\n" + open.__doc__


class OpenWrapper:
    __doc__ = DocDescriptor()

    def __new__(cls, *args, **kwargs):
        return open(*args, **kwargs)


try:
    UnsupportedOperation = io.UnsupportedOperation
except AttributeError:

    class UnsupportedOperation(OSError, ValueError):
        pass


class IOBase(metaclass=abc.ABCMeta):

    def _unsupported(self, name):
        raise UnsupportedOperation('%s.%s() not supported' % (
         self.__class__.__name__, name))

    def seek(self, pos, whence=0):
        self._unsupported('seek')

    def tell(self):
        return self.seek(0, 1)

    def truncate(self, pos=None):
        self._unsupported('truncate')

    def flush(self):
        self._checkClosed

    _IOBase__closed = False

    def close(self):
        if not self._IOBase__closed:
            try:
                self.flush
            finally:
                self._IOBase__closed = True

    def __del__(self):
        try:
            self.close
        except:
            pass

    def seekable(self):
        return False

    def _checkSeekable(self, msg=None):
        if not self.seekable:
            raise UnsupportedOperation('File or stream is not seekable.' if msg is None else msg)

    def readable(self):
        return False

    def _checkReadable(self, msg=None):
        if not self.readable:
            raise UnsupportedOperation('File or stream is not readable.' if msg is None else msg)

    def writable(self):
        return False

    def _checkWritable(self, msg=None):
        if not self.writable:
            raise UnsupportedOperation('File or stream is not writable.' if msg is None else msg)

    @property
    def closed(self):
        return self._IOBase__closed

    def _checkClosed(self, msg=None):
        if self.closed:
            raise ValueError('I/O operation on closed file.' if msg is None else msg)

    def __enter__(self):
        self._checkClosed
        return self

    def __exit__(self, *args):
        self.close

    def fileno(self):
        self._unsupported('fileno')

    def isatty(self):
        self._checkClosed
        return False

    def readline(self, size=-1):
        if hasattr(self, 'peek'):

            def nreadahead():
                readahead = self.peek(1)
                if not readahead:
                    return 1
                n = readahead.find(b'\n') + 1 or len(readahead)
                if size >= 0:
                    n = min(n, size)
                return n

        else:

            def nreadahead():
                return 1

        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f"{size!r} is not an integer")
            else:
                size = size_index()
            res = bytearray()
            while size < 0 or len(res) < size:
                b = self.read(nreadahead())
                if not b:
                    break
                res += b
                if res.endswith(b'\n'):
                    break

            return bytes(res)

    def __iter__(self):
        self._checkClosed
        return self

    def __next__(self):
        line = self.readline
        if not line:
            raise StopIteration
        return line

    def readlines(self, hint=None):
        if hint is None or hint <= 0:
            return list(self)
        n = 0
        lines = []
        for line in self:
            lines.append(line)
            n += len(line)
            if n >= hint:
                break

        return lines

    def writelines(self, lines):
        self._checkClosed
        for line in lines:
            self.write(line)


io.IOBase.register(IOBase)

class RawIOBase(IOBase):

    def read(self, size=-1):
        if size is None:
            size = -1
        if size < 0:
            return self.readall
        b = bytearray(size.__index__)
        n = self.readinto(b)
        if n is None:
            return
        del b[n:]
        return bytes(b)

    def readall(self):
        res = bytearray()
        while True:
            data = self.read(DEFAULT_BUFFER_SIZE)
            if not data:
                break
            res += data

        if res:
            return bytes(res)
        return data

    def readinto(self, b):
        self._unsupported('readinto')

    def write(self, b):
        self._unsupported('write')


io.RawIOBase.register(RawIOBase)
from _io import FileIO
RawIOBase.register(FileIO)

class BufferedIOBase(IOBase):

    def read(self, size=-1):
        self._unsupported('read')

    def read1(self, size=-1):
        self._unsupported('read1')

    def readinto(self, b):
        return self._readinto(b, read1=False)

    def readinto1(self, b):
        return self._readinto(b, read1=True)

    def _readinto(self, b, read1):
        if not isinstance(b, memoryview):
            b = memoryview(b)
        else:
            b = b.cast('B')
            if read1:
                data = self.read1(len(b))
            else:
                data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def write(self, b):
        self._unsupported('write')

    def detach(self):
        self._unsupported('detach')


io.BufferedIOBase.register(BufferedIOBase)

class _BufferedIOMixin(BufferedIOBase):

    def __init__(self, raw):
        self._raw = raw

    def seek(self, pos, whence=0):
        new_position = self.raw.seek(pos, whence)
        if new_position < 0:
            raise OSError('seek() returned an invalid position')
        return new_position

    def tell(self):
        pos = self.raw.tell
        if pos < 0:
            raise OSError('tell() returned an invalid position')
        return pos

    def truncate(self, pos=None):
        self.flush
        if pos is None:
            pos = self.tell
        return self.raw.truncate(pos)

    def flush(self):
        if self.closed:
            raise ValueError('flush on closed file')
        self.raw.flush

    def close(self):
        if self.raw is not None:
            if not self.closed:
                try:
                    self.flush
                finally:
                    self.raw.close

    def detach(self):
        if self.raw is None:
            raise ValueError('raw stream already detached')
        self.flush
        raw = self._raw
        self._raw = None
        return raw

    def seekable(self):
        return self.raw.seekable

    @property
    def raw(self):
        return self._raw

    @property
    def closed(self):
        return self.raw.closed

    @property
    def name(self):
        return self.raw.name

    @property
    def mode(self):
        return self.raw.mode

    def __getstate__(self):
        raise TypeError("can not serialize a '{0}' object".format(self.__class__.__name__))

    def __repr__(self):
        modname = self.__class__.__module__
        clsname = self.__class__.__qualname__
        try:
            name = self.name
        except Exception:
            return '<{}.{}>'.format(modname, clsname)
        else:
            return '<{}.{} name={!r}>'.formatmodnameclsnamename

    def fileno(self):
        return self.raw.fileno

    def isatty(self):
        return self.raw.isatty


class BytesIO(BufferedIOBase):

    def __init__(self, initial_bytes=None):
        buf = bytearray()
        if initial_bytes is not None:
            buf += initial_bytes
        self._buffer = buf
        self._pos = 0

    def __getstate__(self):
        if self.closed:
            raise ValueError('__getstate__ on closed file')
        return self.__dict__.copy

    def getvalue(self):
        if self.closed:
            raise ValueError('getvalue on closed file')
        return bytes(self._buffer)

    def getbuffer(self):
        if self.closed:
            raise ValueError('getbuffer on closed file')
        return memoryview(self._buffer)

    def close(self):
        self._buffer.clear
        super().close

    def read(self, size=-1):
        if self.closed:
            raise ValueError('read from closed file')
        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f"{size!r} is not an integer")
            else:
                size = size_index()
            if size < 0:
                size = len(self._buffer)
            if len(self._buffer) <= self._pos:
                return b''
            newpos = min(len(self._buffer), self._pos + size)
            b = self._buffer[self._pos:newpos]
            self._pos = newpos
            return bytes(b)

    def read1(self, size=-1):
        return self.read(size)

    def write(self, b):
        if self.closed:
            raise ValueError('write to closed file')
        if isinstance(b, str):
            raise TypeError("can't write str to binary stream")
        with memoryview(b) as (view):
            n = view.nbytes
        if n == 0:
            return 0
        pos = self._pos
        if pos > len(self._buffer):
            padding = b'\x00' * (pos - len(self._buffer))
            self._buffer += padding
        self._buffer[pos:pos + n] = b
        self._pos += n
        return n

    def seek(self, pos, whence=0):
        if self.closed:
            raise ValueError('seek on closed file')
        else:
            try:
                pos_index = pos.__index__
            except AttributeError:
                raise TypeError(f"{pos!r} is not an integer")
            else:
                pos = pos_index()
            if whence == 0:
                if pos < 0:
                    raise ValueError('negative seek position %r' % (pos,))
                self._pos = pos
            else:
                if whence == 1:
                    self._pos = max(0, self._pos + pos)
                else:
                    if whence == 2:
                        self._pos = max(0, len(self._buffer) + pos)
                    else:
                        raise ValueError('unsupported whence value')
        return self._pos

    def tell(self):
        if self.closed:
            raise ValueError('tell on closed file')
        return self._pos

    def truncate(self, pos=None):
        if self.closed:
            raise ValueError('truncate on closed file')
        if pos is None:
            pos = self._pos
        else:
            try:
                pos_index = pos.__index__
            except AttributeError:
                raise TypeError(f"{pos!r} is not an integer")
            else:
                pos = pos_index()
            if pos < 0:
                raise ValueError('negative truncate position %r' % (pos,))
        del self._buffer[pos:]
        return pos

    def readable(self):
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        return True

    def writable(self):
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        return True

    def seekable(self):
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        return True


class BufferedReader(_BufferedIOMixin):

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        if not raw.readable:
            raise OSError('"raw" argument must be readable.')
        _BufferedIOMixin.__init__(self, raw)
        if buffer_size <= 0:
            raise ValueError('invalid buffer size')
        self.buffer_size = buffer_size
        self._reset_read_buf
        self._read_lock = Lock()

    def readable(self):
        return self.raw.readable

    def _reset_read_buf(self):
        self._read_buf = b''
        self._read_pos = 0

    def read(self, size=None):
        if size is not None:
            if size < -1:
                raise ValueError('invalid number of bytes to read')
        with self._read_lock:
            return self._read_unlocked(size)

    def _read_unlocked(self, n=None):
        nodata_val = b''
        empty_values = (b'', None)
        buf = self._read_buf
        pos = self._read_pos
        if n is None or n == -1:
            self._reset_read_buf
            if hasattr(self.raw, 'readall'):
                chunk = self.raw.readall
                if chunk is None:
                    return buf[pos:] or None
                return buf[pos:] + chunk
            chunks = [
             buf[pos:]]
            current_size = 0
            while True:
                chunk = self.raw.read
                if chunk in empty_values:
                    nodata_val = chunk
                    break
                current_size += len(chunk)
                chunks.append(chunk)

            return (b'').join(chunks) or nodata_val
        avail = len(buf) - pos
        if n <= avail:
            self._read_pos += n
            return buf[pos:pos + n]
        chunks = [
         buf[pos:]]
        wanted = max(self.buffer_size, n)
        while avail < n:
            chunk = self.raw.read(wanted)
            if chunk in empty_values:
                nodata_val = chunk
                break
            avail += len(chunk)
            chunks.append(chunk)

        n = min(n, avail)
        out = (b'').join(chunks)
        self._read_buf = out[n:]
        self._read_pos = 0
        if out:
            return out[:n]
        return nodata_val

    def peek(self, size=0):
        with self._read_lock:
            return self._peek_unlocked(size)

    def _peek_unlocked(self, n=0):
        want = min(n, self.buffer_size)
        have = len(self._read_buf) - self._read_pos
        if have < want or have <= 0:
            to_read = self.buffer_size - have
            current = self.raw.read(to_read)
            if current:
                self._read_buf = self._read_buf[self._read_pos:] + current
                self._read_pos = 0
        return self._read_buf[self._read_pos:]

    def read1(self, size=-1):
        if size < 0:
            size = self.buffer_size
        if size == 0:
            return b''
        with self._read_lock:
            self._peek_unlocked(1)
            return self._read_unlocked(min(size, len(self._read_buf) - self._read_pos))

    def _readinto(self, buf, read1):
        if not isinstance(buf, memoryview):
            buf = memoryview(buf)
        if buf.nbytes == 0:
            return 0
        buf = buf.cast('B')
        written = 0
        with self._read_lock:
            while written < len(buf):
                avail = min(len(self._read_buf) - self._read_pos, len(buf))
                if avail:
                    buf[written:written + avail] = self._read_buf[self._read_pos:self._read_pos + avail]
                    self._read_pos += avail
                    written += avail
                    if written == len(buf):
                        break
                if len(buf) - written > self.buffer_size:
                    n = self.raw.readinto(buf[written:])
                    if not n:
                        break
                    written += n
                else:
                    if not (read1 and written):
                        if not self._peek_unlocked(1):
                            break
                if read1 and written:
                    break

        return written

    def tell(self):
        return _BufferedIOMixin.tell(self) - len(self._read_buf) + self._read_pos

    def seek(self, pos, whence=0):
        if whence not in valid_seek_flags:
            raise ValueError('invalid whence value')
        with self._read_lock:
            if whence == 1:
                pos -= len(self._read_buf) - self._read_pos
            pos = _BufferedIOMixin.seekselfposwhence
            self._reset_read_buf
            return pos


class BufferedWriter(_BufferedIOMixin):

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        if not raw.writable:
            raise OSError('"raw" argument must be writable.')
        _BufferedIOMixin.__init__(self, raw)
        if buffer_size <= 0:
            raise ValueError('invalid buffer size')
        self.buffer_size = buffer_size
        self._write_buf = bytearray()
        self._write_lock = Lock()

    def writable(self):
        return self.raw.writable

    def write(self, b):
        if isinstance(b, str):
            raise TypeError("can't write str to binary stream")
        with self._write_lock:
            if self.closed:
                raise ValueError('write to closed file')
            else:
                if len(self._write_buf) > self.buffer_size:
                    self._flush_unlocked
                before = len(self._write_buf)
                self._write_buf.extend(b)
                written = len(self._write_buf) - before
                if len(self._write_buf) > self.buffer_size:
                    try:
                        self._flush_unlocked
                    except BlockingIOError as e:
                        try:
                            if len(self._write_buf) > self.buffer_size:
                                overage = len(self._write_buf) - self.buffer_size
                                written -= overage
                                self._write_buf = self._write_buf[:self.buffer_size]
                                raise BlockingIOError(e.errno, e.strerror, written)
                        finally:
                            e = None
                            del e

            return written

    def truncate(self, pos=None):
        with self._write_lock:
            self._flush_unlocked
            if pos is None:
                pos = self.raw.tell
            return self.raw.truncate(pos)

    def flush(self):
        with self._write_lock:
            self._flush_unlocked

    def _flush_unlocked(self):
        if self.closed:
            raise ValueError('flush on closed file')
        while self._write_buf:
            try:
                n = self.raw.write(self._write_buf)
            except BlockingIOError:
                raise RuntimeError('self.raw should implement RawIOBase: it should not raise BlockingIOError')

            if n is None:
                raise BlockingIOError(errno.EAGAIN, 'write could not complete without blocking', 0)
            if n > len(self._write_buf) or n < 0:
                raise OSError('write() returned incorrect number of bytes')
            del self._write_buf[:n]

    def tell(self):
        return _BufferedIOMixin.tell(self) + len(self._write_buf)

    def seek(self, pos, whence=0):
        if whence not in valid_seek_flags:
            raise ValueError('invalid whence value')
        with self._write_lock:
            self._flush_unlocked
            return _BufferedIOMixin.seekselfposwhence

    def close(self):
        with self._write_lock:
            if self.raw is None or self.closed:
                return
        try:
            self.flush
        finally:
            with self._write_lock:
                self.raw.close


class BufferedRWPair(BufferedIOBase):

    def __init__(self, reader, writer, buffer_size=DEFAULT_BUFFER_SIZE):
        if not reader.readable:
            raise OSError('"reader" argument must be readable.')
        if not writer.writable:
            raise OSError('"writer" argument must be writable.')
        self.reader = BufferedReader(reader, buffer_size)
        self.writer = BufferedWriter(writer, buffer_size)

    def read(self, size=-1):
        if size is None:
            size = -1
        return self.reader.read(size)

    def readinto(self, b):
        return self.reader.readinto(b)

    def write(self, b):
        return self.writer.write(b)

    def peek(self, size=0):
        return self.reader.peek(size)

    def read1(self, size=-1):
        return self.reader.read1(size)

    def readinto1(self, b):
        return self.reader.readinto1(b)

    def readable(self):
        return self.reader.readable

    def writable(self):
        return self.writer.writable

    def flush(self):
        return self.writer.flush

    def close(self):
        try:
            self.writer.close
        finally:
            self.reader.close

    def isatty(self):
        return self.reader.isatty or self.writer.isatty

    @property
    def closed(self):
        return self.writer.closed


class BufferedRandom(BufferedWriter, BufferedReader):

    def __init__(self, raw, buffer_size=DEFAULT_BUFFER_SIZE):
        raw._checkSeekable
        BufferedReader.__init__selfrawbuffer_size
        BufferedWriter.__init__selfrawbuffer_size

    def seek(self, pos, whence=0):
        if whence not in valid_seek_flags:
            raise ValueError('invalid whence value')
        self.flush
        if self._read_buf:
            with self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
        pos = self.raw.seek(pos, whence)
        with self._read_lock:
            self._reset_read_buf
        if pos < 0:
            raise OSError('seek() returned invalid position')
        return pos

    def tell(self):
        if self._write_buf:
            return BufferedWriter.tell(self)
        return BufferedReader.tell(self)

    def truncate(self, pos=None):
        if pos is None:
            pos = self.tell
        return BufferedWriter.truncate(self, pos)

    def read(self, size=None):
        if size is None:
            size = -1
        self.flush
        return BufferedReader.read(self, size)

    def readinto(self, b):
        self.flush
        return BufferedReader.readinto(self, b)

    def peek(self, size=0):
        self.flush
        return BufferedReader.peek(self, size)

    def read1(self, size=-1):
        self.flush
        return BufferedReader.read1(self, size)

    def readinto1(self, b):
        self.flush
        return BufferedReader.readinto1(self, b)

    def write(self, b):
        if self._read_buf:
            with self._read_lock:
                self.raw.seek(self._read_pos - len(self._read_buf), 1)
                self._reset_read_buf
        return BufferedWriter.write(self, b)


class FileIO(RawIOBase):
    _fd = -1
    _created = False
    _readable = False
    _writable = False
    _appending = False
    _seekable = None
    _closefd = True

    def __init__(self, file, mode='r', closefd=True, opener=None):
        if self._fd >= 0:
            try:
                if self._closefd:
                    os.close(self._fd)
            finally:
                self._fd = -1

        else:
            if isinstance(file, float):
                raise TypeError('integer argument expected, got float')
            else:
                if isinstance(file, int):
                    fd = file
                    if fd < 0:
                        raise ValueError('negative file descriptor')
                else:
                    fd = -1
                assert isinstance(mode, str), 'invalid mode: %s' % (mode,)
            assert set(mode) <= set('xrwab+'), 'invalid mode: %s' % (mode,)
        if sum((c in 'rwax' for c in mode)) != 1 or mode.count('+') > 1:
            raise ValueError('Must have exactly one of create/read/write/append mode and at most one plus')
        if 'x' in mode:
            self._created = True
            self._writable = True
            flags = os.O_EXCL | os.O_CREAT
        else:
            if 'r' in mode:
                self._readable = True
                flags = 0
            else:
                if 'w' in mode:
                    self._writable = True
                    flags = os.O_CREAT | os.O_TRUNC
                else:
                    if 'a' in mode:
                        self._writable = True
                        self._appending = True
                        flags = os.O_APPEND | os.O_CREAT
                    elif '+' in mode:
                        self._readable = True
                        self._writable = True
                    else:
                        if self._readable and self._writable:
                            flags |= os.O_RDWR
                        else:
                            if self._readable:
                                flags |= os.O_RDONLY
                            else:
                                flags |= os.O_WRONLY
                        flags |= getattr(os, 'O_BINARY', 0)
                        noinherit_flag = getattr(os, 'O_NOINHERIT', 0) or getattr(os, 'O_CLOEXEC', 0)
                        flags |= noinherit_flag
                        owned_fd = None
                        try:
                            if fd < 0:
                                if not closefd:
                                    raise ValueError('Cannot use closefd=False with file name')
                                elif opener is None:
                                    fd = os.openfileflags438
                                else:
                                    fd = opener(file, flags)
                                    if not isinstance(fd, int):
                                        raise TypeError('expected integer from opener')
                                    if fd < 0:
                                        raise OSError('Negative file descriptor')
                                    owned_fd = fd
                                    noinherit_flag or os.set_inheritable(fd, False)
                            self._closefd = closefd
                            fdfstat = os.fstat(fd)
                            try:
                                if stat.S_ISDIR(fdfstat.st_mode):
                                    raise IsADirectoryError(errno.EISDIR, os.strerror(errno.EISDIR), file)
                            except AttributeError:
                                pass

                            self._blksize = getattr(fdfstat, 'st_blksize', 0)
                            if self._blksize <= 1:
                                self._blksize = DEFAULT_BUFFER_SIZE
                            if _setmode:
                                _setmode(fd, os.O_BINARY)
                            self.name = file
                            if self._appending:
                                os.lseekfd0SEEK_END
                        except:
                            if owned_fd is not None:
                                os.close(owned_fd)
                            raise

                    self._fd = fd

    def __del__(self):
        if self._fd >= 0:
            if self._closefd:
                if not self.closed:
                    import warnings
                    warnings.warn(('unclosed file %r' % (self,)), ResourceWarning, stacklevel=2,
                      source=self)
                    self.close

    def __getstate__(self):
        raise TypeError("cannot serialize '%s' object", self.__class__.__name__)

    def __repr__(self):
        class_name = '%s.%s' % (self.__class__.__module__,
         self.__class__.__qualname__)
        if self.closed:
            return '<%s [closed]>' % class_name
        try:
            name = self.name
        except AttributeError:
            return '<%s fd=%d mode=%r closefd=%r>' % (
             class_name, self._fd, self.mode, self._closefd)
        else:
            return '<%s name=%r mode=%r closefd=%r>' % (
             class_name, name, self.mode, self._closefd)

    def _checkReadable(self):
        if not self._readable:
            raise UnsupportedOperation('File not open for reading')

    def _checkWritable(self, msg=None):
        if not self._writable:
            raise UnsupportedOperation('File not open for writing')

    def read(self, size=None):
        self._checkClosed
        self._checkReadable
        if size is None or size < 0:
            return self.readall
        try:
            return os.read(self._fd, size)
        except BlockingIOError:
            return

    def readall(self):
        self._checkClosed
        self._checkReadable
        bufsize = DEFAULT_BUFFER_SIZE
        try:
            pos = os.lseekself._fd0SEEK_CUR
            end = os.fstat(self._fd).st_size
            if end >= pos:
                bufsize = end - pos + 1
        except OSError:
            pass

        result = bytearray()
        while True:
            if len(result) >= bufsize:
                bufsize = len(result)
                bufsize += max(bufsize, DEFAULT_BUFFER_SIZE)
            n = bufsize - len(result)
            try:
                chunk = os.read(self._fd, n)
            except BlockingIOError:
                if result:
                    break
                return
            else:
                if not chunk:
                    break
            result += chunk

        return bytes(result)

    def readinto(self, b):
        m = memoryview(b).cast('B')
        data = self.read(len(m))
        n = len(data)
        m[:n] = data
        return n

    def write(self, b):
        self._checkClosed
        self._checkWritable
        try:
            return os.write(self._fd, b)
        except BlockingIOError:
            return

    def seek(self, pos, whence=SEEK_SET):
        if isinstance(pos, float):
            raise TypeError('an integer is required')
        self._checkClosed
        return os.lseekself._fdposwhence

    def tell(self):
        self._checkClosed
        return os.lseekself._fd0SEEK_CUR

    def truncate(self, size=None):
        self._checkClosed
        self._checkWritable
        if size is None:
            size = self.tell
        os.ftruncate(self._fd, size)
        return size

    def close(self):
        if not self.closed:
            try:
                if self._closefd:
                    os.close(self._fd)
            finally:
                super().close

    def seekable(self):
        self._checkClosed
        if self._seekable is None:
            try:
                self.tell
            except OSError:
                self._seekable = False
            else:
                self._seekable = True
        return self._seekable

    def readable(self):
        self._checkClosed
        return self._readable

    def writable(self):
        self._checkClosed
        return self._writable

    def fileno(self):
        self._checkClosed
        return self._fd

    def isatty(self):
        self._checkClosed
        return os.isatty(self._fd)

    @property
    def closefd(self):
        return self._closefd

    @property
    def mode(self):
        if self._created:
            if self._readable:
                return 'xb+'
            return 'xb'
        else:
            if self._appending:
                if self._readable:
                    return 'ab+'
                return 'ab'
            else:
                if self._readable:
                    if self._writable:
                        return 'rb+'
                    return 'rb'
                else:
                    return 'wb'


class TextIOBase(IOBase):

    def read(self, size=-1):
        self._unsupported('read')

    def write(self, s):
        self._unsupported('write')

    def truncate(self, pos=None):
        self._unsupported('truncate')

    def readline(self):
        self._unsupported('readline')

    def detach(self):
        self._unsupported('detach')

    @property
    def encoding(self):
        pass

    @property
    def newlines(self):
        pass

    @property
    def errors(self):
        pass


io.TextIOBase.register(TextIOBase)

class IncrementalNewlineDecoder(codecs.IncrementalDecoder):

    def __init__(self, decoder, translate, errors='strict'):
        codecs.IncrementalDecoder.__init__(self, errors=errors)
        self.translate = translate
        self.decoder = decoder
        self.seennl = 0
        self.pendingcr = False

    def decode(self, input, final=False):
        if self.decoder is None:
            output = input
        else:
            output = self.decoder.decode(input, final=final)
        if self.pendingcr:
            if output or final:
                output = '\r' + output
                self.pendingcr = False
        if output.endswith('\r'):
            if not final:
                output = output[:-1]
                self.pendingcr = True
        crlf = output.count('\r\n')
        cr = output.count('\r') - crlf
        lf = output.count('\n') - crlf
        self.seennl |= (lf and self._LF) | (cr and self._CR) | (crlf and self._CRLF)
        if self.translate:
            if crlf:
                output = output.replace('\r\n', '\n')
            if cr:
                output = output.replace('\r', '\n')
        return output

    def getstate(self):
        if self.decoder is None:
            buf = b''
            flag = 0
        else:
            buf, flag = self.decoder.getstate
        flag <<= 1
        if self.pendingcr:
            flag |= 1
        return (
         buf, flag)

    def setstate(self, state):
        buf, flag = state
        self.pendingcr = bool(flag & 1)
        if self.decoder is not None:
            self.decoder.setstate((buf, flag >> 1))

    def reset(self):
        self.seennl = 0
        self.pendingcr = False
        if self.decoder is not None:
            self.decoder.reset

    _LF = 1
    _CR = 2
    _CRLF = 4

    @property
    def newlines(self):
        return (None, '\n', '\r', ('\r', '\n'), '\r\n', ('\n', '\r\n'), ('\r', '\r\n'),
                ('\r', '\n', '\r\n'))[self.seennl]


class TextIOWrapper(TextIOBase):
    _CHUNK_SIZE = 2048

    def __init__(self, buffer, encoding=None, errors=None, newline=None, line_buffering=False, write_through=False):
        self._check_newline(newline)
        if encoding is None:
            try:
                encoding = os.device_encoding(buffer.fileno)
            except (AttributeError, UnsupportedOperation):
                pass

            if encoding is None:
                try:
                    import locale
                except ImportError:
                    encoding = 'ascii'
                else:
                    encoding = locale.getpreferredencoding(False)
        if not isinstance(encoding, str):
            raise ValueError('invalid encoding: %r' % encoding)
        if not codecs.lookup(encoding)._is_text_encoding:
            msg = '%r is not a text encoding; use codecs.open() to handle arbitrary codecs'
            raise LookupError(msg % encoding)
        if errors is None:
            errors = 'strict'
        else:
            if not isinstance(errors, str):
                raise ValueError('invalid errors: %r' % errors)
        self._buffer = buffer
        self._decoded_chars = ''
        self._decoded_chars_used = 0
        self._snapshot = None
        self._seekable = self._telling = self.buffer.seekable
        self._has_read1 = hasattr(self.buffer, 'read1')
        self._configure(encoding, errors, newline, line_buffering, write_through)

    def _check_newline(self, newline):
        if newline is not None:
            if not isinstance(newline, str):
                raise TypeError('illegal newline type: %r' % (type(newline),))
        if newline not in (None, '', '\n', '\r', '\r\n'):
            raise ValueError('illegal newline value: %r' % (newline,))

    def _configure(self, encoding=None, errors=None, newline=None, line_buffering=False, write_through=False):
        self._encoding = encoding
        self._errors = errors
        self._encoder = None
        self._decoder = None
        self._b2cratio = 0.0
        self._readuniversal = not newline
        self._readtranslate = newline is None
        self._readnl = newline
        self._writetranslate = newline != ''
        self._writenl = newline or os.linesep
        self._line_buffering = line_buffering
        self._write_through = write_through
        if self._seekable:
            if self.writable:
                position = self.buffer.tell
                if position != 0:
                    try:
                        self._get_encoder.setstate(0)
                    except LookupError:
                        pass

    def __repr__(self):
        result = '<{}.{}'.format(self.__class__.__module__, self.__class__.__qualname__)
        try:
            name = self.name
        except Exception:
            pass
        else:
            result += ' name={0!r}'.format(name)
        try:
            mode = self.mode
        except Exception:
            pass
        else:
            result += ' mode={0!r}'.format(mode)
        return result + ' encoding={0!r}>'.format(self.encoding)

    @property
    def encoding(self):
        return self._encoding

    @property
    def errors(self):
        return self._errors

    @property
    def line_buffering(self):
        return self._line_buffering

    @property
    def write_through(self):
        return self._write_through

    @property
    def buffer(self):
        return self._buffer

    def reconfigure(self, *, encoding=None, errors=None, newline=Ellipsis, line_buffering=None, write_through=None):
        if self._decoder is not None:
            if encoding is not None or errors is not None or newline is not Ellipsis:
                raise UnsupportedOperation('It is not possible to set the encoding or newline of stream after the first read')
        if errors is None:
            if encoding is None:
                errors = self._errors
            else:
                errors = 'strict'
        elif not isinstance(errors, str):
            raise TypeError('invalid errors: %r' % errors)
        if encoding is None:
            encoding = self._encoding
        else:
            if not isinstance(encoding, str):
                raise TypeError('invalid encoding: %r' % encoding)
        if newline is Ellipsis:
            newline = self._readnl
        self._check_newline(newline)
        if line_buffering is None:
            line_buffering = self.line_buffering
        if write_through is None:
            write_through = self.write_through
        self.flush
        self._configure(encoding, errors, newline, line_buffering, write_through)

    def seekable(self):
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        return self._seekable

    def readable(self):
        return self.buffer.readable

    def writable(self):
        return self.buffer.writable

    def flush(self):
        self.buffer.flush
        self._telling = self._seekable

    def close(self):
        if self.buffer is not None:
            if not self.closed:
                try:
                    self.flush
                finally:
                    self.buffer.close

    @property
    def closed(self):
        return self.buffer.closed

    @property
    def name(self):
        return self.buffer.name

    def fileno(self):
        return self.buffer.fileno

    def isatty(self):
        return self.buffer.isatty

    def write--- This code section failed: ---

 L.2137         0  LOAD_FAST                'self'
                2  LOAD_ATTR                closed
                4  POP_JUMP_IF_FALSE    14  'to 14'

 L.2138         6  LOAD_GLOBAL              ValueError
                8  LOAD_STR                 'write to closed file'
               10  CALL_FUNCTION_1       1  '1 positional argument'
               12  RAISE_VARARGS_1       1  'exception instance'
             14_0  COME_FROM             4  '4'

 L.2139        14  LOAD_GLOBAL              isinstance
               16  LOAD_FAST                's'
               18  LOAD_GLOBAL              str
               20  CALL_FUNCTION_2       2  '2 positional arguments'
               22  POP_JUMP_IF_TRUE     40  'to 40'

 L.2140        24  LOAD_GLOBAL              TypeError
               26  LOAD_STR                 "can't write %s to text stream"

 L.2141        28  LOAD_FAST                's'
               30  LOAD_ATTR                __class__
               32  LOAD_ATTR                __name__
               34  BINARY_MODULO    
               36  CALL_FUNCTION_1       1  '1 positional argument'
               38  RAISE_VARARGS_1       1  'exception instance'
             40_0  COME_FROM            22  '22'

 L.2142        40  LOAD_GLOBAL              len
               42  LOAD_FAST                's'
               44  CALL_FUNCTION_1       1  '1 positional argument'
               46  STORE_FAST               'length'

 L.2143        48  LOAD_FAST                'self'
               50  LOAD_ATTR                _writetranslate
               52  POP_JUMP_IF_TRUE     60  'to 60'
               54  LOAD_FAST                'self'
               56  LOAD_ATTR                _line_buffering
               58  JUMP_IF_FALSE_OR_POP    66  'to 66'
             60_0  COME_FROM            52  '52'
               60  LOAD_STR                 '\n'
               62  LOAD_FAST                's'
               64  COMPARE_OP               in
             66_0  COME_FROM            58  '58'
               66  STORE_FAST               'haslf'

 L.2144        68  LOAD_FAST                'haslf'
               70  POP_JUMP_IF_FALSE   102  'to 102'
               72  LOAD_FAST                'self'
               74  LOAD_ATTR                _writetranslate
               76  POP_JUMP_IF_FALSE   102  'to 102'
               78  LOAD_FAST                'self'
               80  LOAD_ATTR                _writenl
               82  LOAD_STR                 '\n'
               84  COMPARE_OP               !=
               86  POP_JUMP_IF_FALSE   102  'to 102'

 L.2145        88  LOAD_FAST                's'
               90  LOAD_METHOD              replace
               92  LOAD_STR                 '\n'
               94  LOAD_FAST                'self'
               96  LOAD_ATTR                _writenl
               98  CALL_METHOD_2         2  '2 positional arguments'
              100  STORE_FAST               's'
            102_0  COME_FROM            86  '86'
            102_1  COME_FROM            76  '76'
            102_2  COME_FROM            70  '70'

 L.2146       102  LOAD_FAST                'self'
              104  LOAD_ATTR                _encoder
              106  JUMP_IF_TRUE_OR_POP   114  'to 114'
              108  LOAD_FAST                'self'
              110  LOAD_METHOD              _get_encoder
              112  CALL_METHOD_0         0  '0 positional arguments'
            114_0  COME_FROM           106  '106'
              114  STORE_FAST               'encoder'

 L.2148       116  LOAD_FAST                'encoder'
              118  LOAD_METHOD              encode
              120  LOAD_FAST                's'
              122  CALL_METHOD_1         1  '1 positional argument'
              124  STORE_FAST               'b'

 L.2149       126  LOAD_FAST                'self'
              128  LOAD_ATTR                buffer
              130  LOAD_METHOD              write
              132  LOAD_FAST                'b'
              134  CALL_METHOD_1         1  '1 positional argument'
              136  POP_TOP          

 L.2150       138  LOAD_FAST                'self'
              140  LOAD_ATTR                _line_buffering
              142  POP_JUMP_IF_FALSE   164  'to 164'
              144  LOAD_FAST                'haslf'
              146  POP_JUMP_IF_TRUE    156  'to 156'
              148  LOAD_STR                 '\r'
              150  LOAD_FAST                's'
              152  COMPARE_OP               in
              154  POP_JUMP_IF_FALSE   164  'to 164'
            156_0  COME_FROM           146  '146'

 L.2151       156  LOAD_FAST                'self'
              158  LOAD_METHOD              flush
              160  CALL_METHOD_0         0  '0 positional arguments'
              162  POP_TOP          
            164_0  COME_FROM           154  '154'
            164_1  COME_FROM           142  '142'

 L.2152       164  LOAD_CONST               None
              166  LOAD_FAST                'self'
              168  STORE_ATTR               _snapshot

 L.2153       170  LOAD_FAST                'self'
              172  LOAD_ATTR                _decoder
              174  POP_JUMP_IF_FALSE   186  'to 186'

 L.2154       176  LOAD_FAST                'self'
              178  LOAD_ATTR                _decoder
              180  LOAD_METHOD              reset
              182  CALL_METHOD_0         0  '0 positional arguments'
              184  POP_TOP          
            186_0  COME_FROM           174  '174'

 L.2155       186  LOAD_FAST                'length'
              188  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `STORE_FAST' instruction at offset 66

    def _get_encoder(self):
        make_encoder = codecs.getincrementalencoder(self._encoding)
        self._encoder = make_encoder(self._errors)
        return self._encoder

    def _get_decoder(self):
        make_decoder = codecs.getincrementaldecoder(self._encoding)
        decoder = make_decoder(self._errors)
        if self._readuniversal:
            decoder = IncrementalNewlineDecoder(decoder, self._readtranslate)
        self._decoder = decoder
        return decoder

    def _set_decoded_chars(self, chars):
        self._decoded_chars = chars
        self._decoded_chars_used = 0

    def _get_decoded_chars(self, n=None):
        offset = self._decoded_chars_used
        if n is None:
            chars = self._decoded_chars[offset:]
        else:
            chars = self._decoded_chars[offset:offset + n]
        self._decoded_chars_used += len(chars)
        return chars

    def _rewind_decoded_chars(self, n):
        if self._decoded_chars_used < n:
            raise AssertionError('rewind decoded_chars out of bounds')
        self._decoded_chars_used -= n

    def _read_chunk(self):
        if self._decoder is None:
            raise ValueError('no decoder')
        else:
            if self._telling:
                dec_buffer, dec_flags = self._decoder.getstate
            elif self._has_read1:
                input_chunk = self.buffer.read1(self._CHUNK_SIZE)
            else:
                input_chunk = self.buffer.read(self._CHUNK_SIZE)
            eof = not input_chunk
            decoded_chars = self._decoder.decode(input_chunk, eof)
            self._set_decoded_chars(decoded_chars)
            if decoded_chars:
                self._b2cratio = len(input_chunk) / len(self._decoded_chars)
            else:
                self._b2cratio = 0.0
        if self._telling:
            self._snapshot = (
             dec_flags, dec_buffer + input_chunk)
        return not eof

    def _pack_cookie(self, position, dec_flags=0, bytes_to_feed=0, need_eof=0, chars_to_skip=0):
        return position | dec_flags << 64 | bytes_to_feed << 128 | chars_to_skip << 192 | bool(need_eof) << 256

    def _unpack_cookie(self, bigint):
        rest, position = divmod(bigint, 18446744073709551616)
        rest, dec_flags = divmod(rest, 18446744073709551616)
        rest, bytes_to_feed = divmod(rest, 18446744073709551616)
        need_eof, chars_to_skip = divmod(rest, 18446744073709551616)
        return (position, dec_flags, bytes_to_feed, need_eof, chars_to_skip)

    def tell(self):
        if not self._seekable:
            raise UnsupportedOperation('underlying stream is not seekable')
        if not self._telling:
            raise OSError('telling position disabled by next() call')
        self.flush
        position = self.buffer.tell
        decoder = self._decoder
        if decoder is None or self._snapshot is None:
            if self._decoded_chars:
                raise AssertionError('pending decoded text')
            return position
        dec_flags, next_input = self._snapshot
        position -= len(next_input)
        chars_to_skip = self._decoded_chars_used
        if chars_to_skip == 0:
            return self._pack_cookie(position, dec_flags)
        saved_state = decoder.getstate
        try:
            skip_bytes = int(self._b2cratio * chars_to_skip)
            skip_back = 1
            while 1:
                if skip_bytes > 0:
                    decoder.setstate((b'', dec_flags))
                    n = len(decoder.decode(next_input[:skip_bytes]))
                    if n <= chars_to_skip:
                        b, d = decoder.getstate
                        if not b:
                            dec_flags = d
                            chars_to_skip -= n
                            break
                        skip_bytes -= len(b)
                        skip_back = 1
                    else:
                        skip_bytes -= skip_back
                        skip_back = skip_back * 2
            else:
                skip_bytes = 0
                decoder.setstate((b'', dec_flags))

            start_pos = position + skip_bytes
            start_flags = dec_flags
            if chars_to_skip == 0:
                return self._pack_cookie(start_pos, start_flags)
            bytes_fed = 0
            need_eof = 0
            chars_decoded = 0
            for i in range(skip_bytes, len(next_input)):
                bytes_fed += 1
                chars_decoded += len(decoder.decode(next_input[i:i + 1]))
                dec_buffer, dec_flags = decoder.getstate
                if not dec_buffer:
                    if chars_decoded <= chars_to_skip:
                        start_pos += bytes_fed
                        chars_to_skip -= chars_decoded
                        start_flags, bytes_fed, chars_decoded = dec_flags, 0, 0
                    if chars_decoded >= chars_to_skip:
                        break
            else:
                chars_decoded += len(decoder.decode(b'', final=True))
                need_eof = 1
                if chars_decoded < chars_to_skip:
                    raise OSError("can't reconstruct logical file position")

            return self._pack_cookie(start_pos, start_flags, bytes_fed, need_eof, chars_to_skip)
        finally:
            decoder.setstate(saved_state)

    def truncate(self, pos=None):
        self.flush
        if pos is None:
            pos = self.tell
        return self.buffer.truncate(pos)

    def detach(self):
        if self.buffer is None:
            raise ValueError('buffer is already detached')
        self.flush
        buffer = self._buffer
        self._buffer = None
        return buffer

    def seek(self, cookie, whence=0):

        def _reset_encoder(position):
            try:
                encoder = self._encoder or self._get_encoder
            except LookupError:
                pass
            else:
                if position != 0:
                    encoder.setstate(0)
                else:
                    encoder.reset

        if self.closed:
            raise ValueError('tell on closed file')
        if not self._seekable:
            raise UnsupportedOperation('underlying stream is not seekable')
        if whence == 1:
            if cookie != 0:
                raise UnsupportedOperation("can't do nonzero cur-relative seeks")
            whence = 0
            cookie = self.tell
        if whence == 2:
            if cookie != 0:
                raise UnsupportedOperation("can't do nonzero end-relative seeks")
            self.flush
            position = self.buffer.seek(0, 2)
            self._set_decoded_chars('')
            self._snapshot = None
            if self._decoder:
                self._decoder.reset
            _reset_encoder(position)
            return position
        if whence != 0:
            raise ValueError('unsupported whence (%r)' % (whence,))
        if cookie < 0:
            raise ValueError('negative seek position %r' % (cookie,))
        self.flush
        start_pos, dec_flags, bytes_to_feed, need_eof, chars_to_skip = self._unpack_cookie(cookie)
        self.buffer.seek(start_pos)
        self._set_decoded_chars('')
        self._snapshot = None
        if cookie == 0 and self._decoder:
            self._decoder.reset
        else:
            if self._decoder or dec_flags or chars_to_skip:
                self._decoder = self._decoder or self._get_decoder
                self._decoder.setstate((b'', dec_flags))
                self._snapshot = (dec_flags, b'')
            if chars_to_skip:
                input_chunk = self.buffer.read(bytes_to_feed)
                self._set_decoded_chars(self._decoder.decode(input_chunk, need_eof))
                self._snapshot = (dec_flags, input_chunk)
                if len(self._decoded_chars) < chars_to_skip:
                    raise OSError("can't restore logical file position")
                self._decoded_chars_used = chars_to_skip
            _reset_encoder(cookie)
            return cookie

    def read(self, size=None):
        self._checkReadable
        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f"{size!r} is not an integer")
            else:
                size = size_index()
            decoder = self._decoder or self._get_decoder
            if size < 0:
                result = self._get_decoded_chars + decoder.decode((self.buffer.read), final=True)
                self._set_decoded_chars('')
                self._snapshot = None
                return result
            eof = False
            result = self._get_decoded_chars(size)
            while len(result) < size:
                eof = eof or not self._read_chunk
                result += self._get_decoded_chars(size - len(result))

            return result

    def __next__(self):
        self._telling = False
        line = self.readline
        if not line:
            self._snapshot = None
            self._telling = self._seekable
            raise StopIteration
        return line

    def readline(self, size=None):
        if self.closed:
            raise ValueError('read from closed file')
        if size is None:
            size = -1
        else:
            try:
                size_index = size.__index__
            except AttributeError:
                raise TypeError(f"{size!r} is not an integer")
            else:
                size = size_index()
            line = self._get_decoded_chars
            start = 0
            if not self._decoder:
                self._get_decoder
            pos = endpos = None
            while True:
                if self._readtranslate:
                    pos = line.find('\n', start)
                    if pos >= 0:
                        endpos = pos + 1
                        break
                    else:
                        start = len(line)
                else:
                    if self._readuniversal:
                        nlpos = line.find('\n', start)
                        crpos = line.find('\r', start)
                        if crpos == -1:
                            if nlpos == -1:
                                start = len(line)
                            else:
                                endpos = nlpos + 1
                                break
                        else:
                            if nlpos == -1:
                                endpos = crpos + 1
                                break
                            else:
                                if nlpos < crpos:
                                    endpos = nlpos + 1
                                    break
                                else:
                                    if nlpos == crpos + 1:
                                        endpos = crpos + 2
                                        break
                                    else:
                                        endpos = crpos + 1
                                        break
                    else:
                        pos = line.find(self._readnl)
                        if pos >= 0:
                            endpos = pos + len(self._readnl)
                            break
                        else:
                            if size >= 0:
                                if len(line) >= size:
                                    endpos = size
                                    break
                            while self._read_chunk:
                                if self._decoded_chars:
                                    break

                            if self._decoded_chars:
                                line += self._get_decoded_chars
                        self._set_decoded_chars('')
                        self._snapshot = None
                        return line

            if size >= 0:
                if endpos > size:
                    endpos = size
            self._rewind_decoded_chars(len(line) - endpos)
            return line[:endpos]

    @property
    def newlines(self):
        if self._decoder:
            return self._decoder.newlines


class StringIO(TextIOWrapper):

    def __init__(self, initial_value='', newline='\n'):
        super(StringIO, self).__init__((BytesIO()), encoding='utf-8',
          errors='surrogatepass',
          newline=newline)
        if newline is None:
            self._writetranslate = False
        if initial_value is not None:
            if not isinstance(initial_value, str):
                raise TypeError('initial_value must be str or None, not {0}'.format(type(initial_value).__name__))
            self.write(initial_value)
            self.seek(0)

    def getvalue(self):
        self.flush
        decoder = self._decoder or self._get_decoder
        old_state = decoder.getstate
        decoder.reset
        try:
            return decoder.decode((self.buffer.getvalue), final=True)
        finally:
            decoder.setstate(old_state)

    def __repr__(self):
        return object.__repr__(self)

    @property
    def errors(self):
        pass

    @property
    def encoding(self):
        pass

    def detach(self):
        self._unsupported('detach')