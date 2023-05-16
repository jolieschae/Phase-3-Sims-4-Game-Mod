# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\encodings\idna.py
# Compiled at: 2013-04-05 19:16:39
# Size of source mod 2**32: 9479 bytes
import stringprep, re, codecs
from unicodedata import ucd_3_2_0 as unicodedata
dots = re.compile('[.。．｡]')
ace_prefix = b'xn--'
sace_prefix = 'xn--'

def nameprep--- This code section failed: ---

 L.  16         0  BUILD_LIST_0          0 
                2  STORE_FAST               'newlabel'

 L.  17         4  SETUP_LOOP           46  'to 46'
                6  LOAD_FAST                'label'
                8  GET_ITER         
               10  FOR_ITER             44  'to 44'
               12  STORE_FAST               'c'

 L.  18        14  LOAD_GLOBAL              stringprep
               16  LOAD_METHOD              in_table_b1
               18  LOAD_FAST                'c'
               20  CALL_METHOD_1         1  '1 positional argument'
               22  POP_JUMP_IF_FALSE    26  'to 26'

 L.  20        24  CONTINUE             10  'to 10'
             26_0  COME_FROM            22  '22'

 L.  21        26  LOAD_FAST                'newlabel'
               28  LOAD_METHOD              append
               30  LOAD_GLOBAL              stringprep
               32  LOAD_METHOD              map_table_b2
               34  LOAD_FAST                'c'
               36  CALL_METHOD_1         1  '1 positional argument'
               38  CALL_METHOD_1         1  '1 positional argument'
               40  POP_TOP          
               42  JUMP_BACK            10  'to 10'
               44  POP_BLOCK        
             46_0  COME_FROM_LOOP        4  '4'

 L.  22        46  LOAD_STR                 ''
               48  LOAD_METHOD              join
               50  LOAD_FAST                'newlabel'
               52  CALL_METHOD_1         1  '1 positional argument'
               54  STORE_FAST               'label'

 L.  25        56  LOAD_GLOBAL              unicodedata
               58  LOAD_METHOD              normalize
               60  LOAD_STR                 'NFKC'
               62  LOAD_FAST                'label'
               64  CALL_METHOD_2         2  '2 positional arguments'
               66  STORE_FAST               'label'

 L.  28        68  SETUP_LOOP          184  'to 184'
               70  LOAD_FAST                'label'
               72  GET_ITER         
             74_0  COME_FROM           166  '166'
               74  FOR_ITER            182  'to 182'
               76  STORE_FAST               'c'

 L.  29        78  LOAD_GLOBAL              stringprep
               80  LOAD_METHOD              in_table_c12
               82  LOAD_FAST                'c'
               84  CALL_METHOD_1         1  '1 positional argument'
               86  POP_JUMP_IF_TRUE    168  'to 168'

 L.  30        88  LOAD_GLOBAL              stringprep
               90  LOAD_METHOD              in_table_c22
               92  LOAD_FAST                'c'
               94  CALL_METHOD_1         1  '1 positional argument'
               96  POP_JUMP_IF_TRUE    168  'to 168'

 L.  31        98  LOAD_GLOBAL              stringprep
              100  LOAD_METHOD              in_table_c3
              102  LOAD_FAST                'c'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  POP_JUMP_IF_TRUE    168  'to 168'

 L.  32       108  LOAD_GLOBAL              stringprep
              110  LOAD_METHOD              in_table_c4
              112  LOAD_FAST                'c'
              114  CALL_METHOD_1         1  '1 positional argument'
              116  POP_JUMP_IF_TRUE    168  'to 168'

 L.  33       118  LOAD_GLOBAL              stringprep
              120  LOAD_METHOD              in_table_c5
              122  LOAD_FAST                'c'
              124  CALL_METHOD_1         1  '1 positional argument'
              126  POP_JUMP_IF_TRUE    168  'to 168'

 L.  34       128  LOAD_GLOBAL              stringprep
              130  LOAD_METHOD              in_table_c6
              132  LOAD_FAST                'c'
              134  CALL_METHOD_1         1  '1 positional argument'
              136  POP_JUMP_IF_TRUE    168  'to 168'

 L.  35       138  LOAD_GLOBAL              stringprep
              140  LOAD_METHOD              in_table_c7
              142  LOAD_FAST                'c'
              144  CALL_METHOD_1         1  '1 positional argument'
              146  POP_JUMP_IF_TRUE    168  'to 168'

 L.  36       148  LOAD_GLOBAL              stringprep
              150  LOAD_METHOD              in_table_c8
              152  LOAD_FAST                'c'
              154  CALL_METHOD_1         1  '1 positional argument'
              156  POP_JUMP_IF_TRUE    168  'to 168'

 L.  37       158  LOAD_GLOBAL              stringprep
              160  LOAD_METHOD              in_table_c9
              162  LOAD_FAST                'c'
              164  CALL_METHOD_1         1  '1 positional argument'
              166  POP_JUMP_IF_FALSE    74  'to 74'
            168_0  COME_FROM           156  '156'
            168_1  COME_FROM           146  '146'
            168_2  COME_FROM           136  '136'
            168_3  COME_FROM           126  '126'
            168_4  COME_FROM           116  '116'
            168_5  COME_FROM           106  '106'
            168_6  COME_FROM            96  '96'
            168_7  COME_FROM            86  '86'

 L.  38       168  LOAD_GLOBAL              UnicodeError
              170  LOAD_STR                 'Invalid character %r'
              172  LOAD_FAST                'c'
              174  BINARY_MODULO    
              176  CALL_FUNCTION_1       1  '1 positional argument'
              178  RAISE_VARARGS_1       1  'exception instance'
              180  JUMP_BACK            74  'to 74'
              182  POP_BLOCK        
            184_0  COME_FROM_LOOP       68  '68'

 L.  41       184  LOAD_LISTCOMP            '<code_object <listcomp>>'
              186  LOAD_STR                 'nameprep.<locals>.<listcomp>'
              188  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              190  LOAD_FAST                'label'
              192  GET_ITER         
              194  CALL_FUNCTION_1       1  '1 positional argument'
              196  STORE_FAST               'RandAL'

 L.  42       198  SETUP_LOOP          268  'to 268'
              200  LOAD_FAST                'RandAL'
              202  GET_ITER         
            204_0  COME_FROM           254  '254'
            204_1  COME_FROM           210  '210'
              204  FOR_ITER            266  'to 266'
              206  STORE_FAST               'c'

 L.  43       208  LOAD_FAST                'c'
              210  POP_JUMP_IF_FALSE   204  'to 204'

 L.  50       212  LOAD_GLOBAL              any
              214  LOAD_GENEXPR             '<code_object <genexpr>>'
              216  LOAD_STR                 'nameprep.<locals>.<genexpr>'
              218  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              220  LOAD_FAST                'label'
              222  GET_ITER         
              224  CALL_FUNCTION_1       1  '1 positional argument'
              226  CALL_FUNCTION_1       1  '1 positional argument'
              228  POP_JUMP_IF_FALSE   238  'to 238'

 L.  51       230  LOAD_GLOBAL              UnicodeError
              232  LOAD_STR                 'Violation of BIDI requirement 2'
              234  CALL_FUNCTION_1       1  '1 positional argument'
              236  RAISE_VARARGS_1       1  'exception instance'
            238_0  COME_FROM           228  '228'

 L.  57       238  LOAD_FAST                'RandAL'
              240  LOAD_CONST               0
              242  BINARY_SUBSCR    
          244_246  POP_JUMP_IF_FALSE   256  'to 256'
              248  LOAD_FAST                'RandAL'
              250  LOAD_CONST               -1
              252  BINARY_SUBSCR    
              254  POP_JUMP_IF_TRUE    204  'to 204'
            256_0  COME_FROM           244  '244'

 L.  58       256  LOAD_GLOBAL              UnicodeError
              258  LOAD_STR                 'Violation of BIDI requirement 3'
              260  CALL_FUNCTION_1       1  '1 positional argument'
              262  RAISE_VARARGS_1       1  'exception instance'
              264  JUMP_BACK           204  'to 204'
              266  POP_BLOCK        
            268_0  COME_FROM_LOOP      198  '198'

 L.  60       268  LOAD_FAST                'label'
              270  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_BLOCK' instruction at offset 182


def ToASCII(label):
    try:
        label = label.encode('ascii')
    except UnicodeError:
        pass
    else:
        if 0 < len(label) < 64:
            return label
        raise UnicodeError('label empty or too long')
    label = nameprep(label)
    try:
        label = label.encode('ascii')
    except UnicodeError:
        pass
    else:
        if 0 < len(label) < 64:
            return label
        raise UnicodeError('label empty or too long')
    if label.startswith(sace_prefix):
        raise UnicodeError('Label starts with ACE prefix')
    label = label.encode('punycode')
    label = ace_prefix + label
    if 0 < len(label) < 64:
        return label
    raise UnicodeError('label empty or too long')


def ToUnicode(label):
    if isinstance(label, bytes):
        pure_ascii = True
    else:
        try:
            label = label.encode('ascii')
            pure_ascii = True
        except UnicodeError:
            pure_ascii = False

        label = pure_ascii or nameprep(label)
        try:
            label = label.encode('ascii')
        except UnicodeError:
            raise UnicodeError('Invalid character in IDN label')

        if not label.startswith(ace_prefix):
            return str(label, 'ascii')
        label1 = label[len(ace_prefix):]
        result = label1.decode('punycode')
        label2 = ToASCII(result)
        if str(label, 'ascii').lower() != str(label2, 'ascii'):
            raise UnicodeError('IDNA does not round-trip', label, label2)
        return result


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        if errors != 'strict':
            raise UnicodeError('unsupported error handling ' + errors)
        else:
            return input or (b'', 0)
        try:
            result = input.encode('ascii')
        except UnicodeEncodeError:
            pass
        else:
            labels = result.split(b'.')
            for label in labels[:-1]:
                if not 0 < len(label) < 64:
                    raise UnicodeError('label empty or too long')

            if len(labels[-1]) >= 64:
                raise UnicodeError('label too long')
            return (
             result, len(input))
            result = bytearray()
            labels = dots.split(input)
            if labels:
                trailing_dot = labels[-1] or b'.'
                del labels[-1]
            else:
                trailing_dot = b''
            for label in labels:
                if result:
                    result.extend(b'.')
                result.extend(ToASCII(label))

            return (
             bytes(result + trailing_dot), len(input))

    def decode(self, input, errors='strict'):
        if errors != 'strict':
            raise UnicodeError('Unsupported error handling ' + errors)
        elif not input:
            return ('', 0)
            if not isinstance(input, bytes):
                input = bytes(input)
            if ace_prefix not in input:
                try:
                    return (
                     input.decode('ascii'), len(input))
                except UnicodeDecodeError:
                    pass

            labels = input.split(b'.')
            if labels and len(labels[-1]) == 0:
                trailing_dot = '.'
                del labels[-1]
        else:
            trailing_dot = ''
        result = []
        for label in labels:
            result.append(ToUnicode(label))

        return ('.'.join(result) + trailing_dot, len(input))


class IncrementalEncoder(codecs.BufferedIncrementalEncoder):

    def _buffer_encode(self, input, errors, final):
        if errors != 'strict':
            raise UnicodeError('unsupported error handling ' + errors)
        else:
            if not input:
                return (b'', 0)
            labels = dots.split(input)
            trailing_dot = b''
            if labels:
                if not labels[-1]:
                    trailing_dot = b'.'
                    del labels[-1]
                else:
                    if not final:
                        del labels[-1]
                        if labels:
                            trailing_dot = b'.'
        result = bytearray()
        size = 0
        for label in labels:
            if size:
                result.extend(b'.')
                size += 1
            result.extend(ToASCII(label))
            size += len(label)

        result += trailing_dot
        size += len(trailing_dot)
        return (bytes(result), size)


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):

    def _buffer_decode(self, input, errors, final):
        if errors != 'strict':
            raise UnicodeError('Unsupported error handling ' + errors)
        else:
            if not input:
                return ('', 0)
            if isinstance(input, str):
                labels = dots.split(input)
            else:
                input = str(input, 'ascii')
                labels = input.split('.')
            trailing_dot = ''
            if labels:
                if not labels[-1]:
                    trailing_dot = '.'
                    del labels[-1]
                else:
                    if not final:
                        del labels[-1]
                        if labels:
                            trailing_dot = '.'
        result = []
        size = 0
        for label in labels:
            result.append(ToUnicode(label))
            if size:
                size += 1
            size += len(label)

        result = '.'.join(result) + trailing_dot
        size += len(trailing_dot)
        return (result, size)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='idna',
      encode=(Codec().encode),
      decode=(Codec().decode),
      incrementalencoder=IncrementalEncoder,
      incrementaldecoder=IncrementalDecoder,
      streamwriter=StreamWriter,
      streamreader=StreamReader)