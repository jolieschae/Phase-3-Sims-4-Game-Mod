# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\dis.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 20423 bytes
import sys, types, collections, io
from opcode import *
from opcode import __all__ as _opcodes_all
__all__ = [
 "'code_info'", "'dis'", "'disassemble'", "'distb'", "'disco'", 
 "'findlinestarts'", 
 "'findlabels'", "'show_code'", 
 "'get_instructions'", "'Instruction'", "'Bytecode'"] + _opcodes_all
del _opcodes_all
_have_code = (
 types.MethodType, types.FunctionType, types.CodeType,
 classmethod, staticmethod, type)
FORMAT_VALUE = opmap['FORMAT_VALUE']

def _try_compile(source, name):
    try:
        c = compile(source, name, 'eval')
    except SyntaxError:
        c = compile(source, name, 'exec')

    return c


def dis(x=None, *, file=None, depth=None):
    if x is None:
        distb(file=file)
        return
    elif hasattr(x, '__func__'):
        x = x.__func__
    elif hasattr(x, '__code__'):
        x = x.__code__
    else:
        if hasattr(x, 'gi_code'):
            x = x.gi_code
        else:
            if hasattr(x, 'ag_code'):
                x = x.ag_code
            else:
                if hasattr(x, 'cr_code'):
                    x = x.cr_code
    if hasattr(x, '__dict__'):
        items = sorted(x.__dict__.items())
        for name, x1 in items:
            if isinstance(x1, _have_code):
                print(('Disassembly of %s:' % name), file=file)
                try:
                    dis(x1, file=file, depth=depth)
                except TypeError as msg:
                    try:
                        print('Sorry:', msg, file=file)
                    finally:
                        msg = None
                        del msg

                print(file=file)

    else:
        if hasattr(x, 'co_code'):
            _disassemble_recursive(x, file=file, depth=depth)
        else:
            if isinstance(x, (bytes, bytearray)):
                _disassemble_bytes(x, file=file)
            else:
                if isinstance(x, str):
                    _disassemble_str(x, file=file, depth=depth)
                else:
                    raise TypeError("don't know how to disassemble %s objects" % type(x).__name__)


def distb(tb=None, *, file=None):
    if tb is None:
        try:
            tb = sys.last_traceback
        except AttributeError:
            raise RuntimeError('no last traceback to disassemble') from None

        while tb.tb_next:
            tb = tb.tb_next

    disassemble((tb.tb_frame.f_code), (tb.tb_lasti), file=file)


COMPILER_FLAG_NAMES = {
 1: "'OPTIMIZED'", 
 2: "'NEWLOCALS'", 
 4: "'VARARGS'", 
 8: "'VARKEYWORDS'", 
 16: "'NESTED'", 
 32: "'GENERATOR'", 
 64: "'NOFREE'", 
 128: "'COROUTINE'", 
 256: "'ITERABLE_COROUTINE'", 
 512: "'ASYNC_GENERATOR'"}

def pretty_flags--- This code section failed: ---

 L. 107         0  BUILD_LIST_0          0 
                2  STORE_FAST               'names'

 L. 108         4  SETUP_LOOP           88  'to 88'
                6  LOAD_GLOBAL              range
                8  LOAD_CONST               32
               10  CALL_FUNCTION_1       1  '1 positional argument'
               12  GET_ITER         
             14_0  COME_FROM            66  '66'
             14_1  COME_FROM            32  '32'
               14  FOR_ITER             72  'to 72'
               16  STORE_FAST               'i'

 L. 109        18  LOAD_CONST               1
               20  LOAD_FAST                'i'
               22  BINARY_LSHIFT    
               24  STORE_FAST               'flag'

 L. 110        26  LOAD_FAST                'flags'
               28  LOAD_FAST                'flag'
               30  BINARY_AND       
               32  POP_JUMP_IF_FALSE    14  'to 14'

 L. 111        34  LOAD_FAST                'names'
               36  LOAD_METHOD              append
               38  LOAD_GLOBAL              COMPILER_FLAG_NAMES
               40  LOAD_METHOD              get
               42  LOAD_FAST                'flag'
               44  LOAD_GLOBAL              hex
               46  LOAD_FAST                'flag'
               48  CALL_FUNCTION_1       1  '1 positional argument'
               50  CALL_METHOD_2         2  '2 positional arguments'
               52  CALL_METHOD_1         1  '1 positional argument'
               54  POP_TOP          

 L. 112        56  LOAD_FAST                'flags'
               58  LOAD_FAST                'flag'
               60  INPLACE_XOR      
               62  STORE_FAST               'flags'

 L. 113        64  LOAD_FAST                'flags'
               66  POP_JUMP_IF_TRUE     14  'to 14'

 L. 114        68  BREAK_LOOP       
               70  JUMP_BACK            14  'to 14'
               72  POP_BLOCK        

 L. 116        74  LOAD_FAST                'names'
               76  LOAD_METHOD              append
               78  LOAD_GLOBAL              hex
               80  LOAD_FAST                'flags'
               82  CALL_FUNCTION_1       1  '1 positional argument'
               84  CALL_METHOD_1         1  '1 positional argument'
               86  POP_TOP          
             88_0  COME_FROM_LOOP        4  '4'

 L. 117        88  LOAD_STR                 ', '
               90  LOAD_METHOD              join
               92  LOAD_FAST                'names'
               94  CALL_METHOD_1         1  '1 positional argument'
               96  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `LOAD_FAST' instruction at offset 74


def _get_code_object(x):
    if hasattr(x, '__func__'):
        x = x.__func__
    elif hasattr(x, '__code__'):
        x = x.__code__
    else:
        if hasattr(x, 'gi_code'):
            x = x.gi_code
        else:
            if hasattr(x, 'ag_code'):
                x = x.ag_code
            else:
                if hasattr(x, 'cr_code'):
                    x = x.cr_code
    if isinstance(x, str):
        x = _try_compile(x, '<disassembly>')
    if hasattr(x, 'co_code'):
        return x
    raise TypeError("don't know how to disassemble %s objects" % type(x).__name__)


def code_info(x):
    return _format_code_info(_get_code_object(x))


def _format_code_info(co):
    lines = []
    lines.append('Name:              %s' % co.co_name)
    lines.append('Filename:          %s' % co.co_filename)
    lines.append('Argument count:    %s' % co.co_argcount)
    lines.append('Kw-only arguments: %s' % co.co_kwonlyargcount)
    lines.append('Number of locals:  %s' % co.co_nlocals)
    lines.append('Stack size:        %s' % co.co_stacksize)
    lines.append('Flags:             %s' % pretty_flags(co.co_flags))
    if co.co_consts:
        lines.append'Constants:'
        for i_c in enumerate(co.co_consts):
            lines.append('%4d: %r' % i_c)

    if co.co_names:
        lines.append'Names:'
        for i_n in enumerate(co.co_names):
            lines.append('%4d: %s' % i_n)

    if co.co_varnames:
        lines.append'Variable names:'
        for i_n in enumerate(co.co_varnames):
            lines.append('%4d: %s' % i_n)

    if co.co_freevars:
        lines.append'Free variables:'
        for i_n in enumerate(co.co_freevars):
            lines.append('%4d: %s' % i_n)

    if co.co_cellvars:
        lines.append'Cell variables:'
        for i_n in enumerate(co.co_cellvars):
            lines.append('%4d: %s' % i_n)

    return '\n'.joinlines


def show_code(co, *, file=None):
    print((code_info(co)), file=file)


_Instruction = collections.namedtuple('_Instruction', 'opname opcode arg argval argrepr offset starts_line is_jump_target')
_Instruction.opname.__doc__ = 'Human readable name for operation'
_Instruction.opcode.__doc__ = 'Numeric code for operation'
_Instruction.arg.__doc__ = 'Numeric argument to operation (if any), otherwise None'
_Instruction.argval.__doc__ = 'Resolved arg value (if known), otherwise same as arg'
_Instruction.argrepr.__doc__ = 'Human readable description of operation argument'
_Instruction.offset.__doc__ = 'Start index of operation within bytecode sequence'
_Instruction.starts_line.__doc__ = 'Line started by this opcode (if any), otherwise None'
_Instruction.is_jump_target.__doc__ = 'True if other code jumps to here, otherwise False'
_OPNAME_WIDTH = 20
_OPARG_WIDTH = 5

class Instruction(_Instruction):

    def _disassemble(self, lineno_width=3, mark_as_current=False, offset_width=4):
        fields = []
        if lineno_width:
            if self.starts_line is not None:
                lineno_fmt = '%%%dd' % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            else:
                fields.append(' ' * lineno_width)
        else:
            if mark_as_current:
                fields.append'-->'
            else:
                fields.append'   '
            if self.is_jump_target:
                fields.append'>>'
            else:
                fields.append'  '
        fields.appendrepr(self.offset).rjustoffset_width
        fields.appendself.opname.ljust_OPNAME_WIDTH
        if self.arg is not None:
            fields.appendrepr(self.arg).rjust_OPARG_WIDTH
            if self.argrepr:
                fields.append('(' + self.argrepr + ')')
        return ' '.joinfields.rstrip()


def get_instructions(x, *, first_line=None):
    co = _get_code_object(x)
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    if first_line is not None:
        line_offset = first_line - co.co_firstlineno
    else:
        line_offset = 0
    return _get_instructions_bytes(co.co_code, co.co_varnames, co.co_names, co.co_consts, cell_names, linestarts, line_offset)


def _get_const_info(const_index, const_list):
    argval = const_index
    if const_list is not None:
        argval = const_list[const_index]
    return (
     argval, repr(argval))


def _get_name_info(name_index, name_list):
    argval = name_index
    if name_list is not None:
        argval = name_list[name_index]
        argrepr = argval
    else:
        argrepr = repr(argval)
    return (
     argval, argrepr)


def _get_instructions_bytes(code, varnames=None, names=None, constants=None, cells=None, linestarts=None, line_offset=0):
    labels = findlabels(code)
    starts_line = None
    for offset, op, arg in _unpack_opargs(code):
        if linestarts is not None:
            starts_line = linestarts.get(offset, None)
            if starts_line is not None:
                starts_line += line_offset
        is_jump_target = offset in labels
        argval = None
        argrepr = ''
        if arg is not None:
            argval = arg
            if op in hasconst:
                argval, argrepr = _get_const_info(arg, constants)
            else:
                if op in hasname:
                    argval, argrepr = _get_name_info(arg, names)
                else:
                    if op in hasjrel:
                        argval = offset + 2 + arg
                        argrepr = 'to ' + repr(argval)
                    else:
                        if op in haslocal:
                            argval, argrepr = _get_name_info(arg, varnames)
                        else:
                            if op in hascompare:
                                argval = cmp_op[arg]
                                argrepr = argval
                            else:
                                if op in hasfree:
                                    argval, argrepr = _get_name_info(arg, cells)
                                else:
                                    if op == FORMAT_VALUE:
                                        argval = (
                                         (
                                          None, str, repr, ascii)[arg & 3], bool(arg & 4))
                                        argrepr = ('', 'str', 'repr', 'ascii')[arg & 3]
                                        if argval[1]:
                                            if argrepr:
                                                argrepr += ', '
                                            argrepr += 'with format'
        yield Instruction(opname[op], op, arg, argval, argrepr, offset, starts_line, is_jump_target)


def disassemble(co, lasti=-1, *, file=None):
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    _disassemble_bytes((co.co_code), lasti, (co.co_varnames), (co.co_names), (co.co_consts),
      cell_names, linestarts, file=file)


def _disassemble_recursive(co, *, file=None, depth=None):
    disassemble(co, file=file)
    if depth is None or depth > 0:
        if depth is not None:
            depth = depth - 1
        for x in co.co_consts:
            if hasattr(x, 'co_code'):
                print(file=file)
                print(('Disassembly of %r:' % (x,)), file=file)
                _disassemble_recursive(x, file=file, depth=depth)


def _disassemble_bytes(code, lasti=-1, varnames=None, names=None, constants=None, cells=None, linestarts=None, *, file=None, line_offset=0):
    show_lineno = linestarts is not None
    if show_lineno:
        maxlineno = max(linestarts.values()) + line_offset
        if maxlineno >= 1000:
            lineno_width = len(str(maxlineno))
        else:
            lineno_width = 3
    else:
        lineno_width = 0
    maxoffset = len(code) - 2
    if maxoffset >= 10000:
        offset_width = len(str(maxoffset))
    else:
        offset_width = 4
    for instr in _get_instructions_bytes(code, varnames, names, constants, cells, linestarts, line_offset=line_offset):
        new_source_line = show_lineno and instr.starts_line is not None and instr.offset > 0
        if new_source_line:
            print(file=file)
        is_current_instr = instr.offset == lasti
        print((instr._disassemble(lineno_width, is_current_instr, offset_width)), file=file)


def _disassemble_str(source, **kwargs):
    _disassemble_recursive((_try_compile(source, '<dis>')), **kwargs)


disco = disassemble

def _unpack_opargs(code):
    extended_arg = 0
    for i in range(0, len(code), 2):
        op = code[i]
        if op >= HAVE_ARGUMENT:
            arg = code[i + 1] | extended_arg
            extended_arg = arg << 8 if op == EXTENDED_ARG else 0
        else:
            arg = None
        yield (
         i, op, arg)


def findlabels(code):
    labels = []
    for offset, op, arg in _unpack_opargs(code):
        if arg is not None:
            if op in hasjrel:
                label = offset + 2 + arg
            else:
                if op in hasjabs:
                    label = arg
                else:
                    continue
            if label not in labels:
                labels.appendlabel

    return labels


def findlinestarts(code):
    byte_increments = code.co_lnotab[0::2]
    line_increments = code.co_lnotab[1::2]
    lastlineno = None
    lineno = code.co_firstlineno
    addr = 0
    for byte_incr, line_incr in zip(byte_increments, line_increments):
        if byte_incr:
            if lineno != lastlineno:
                yield (
                 addr, lineno)
                lastlineno = lineno
            addr += byte_incr
        if line_incr >= 128:
            line_incr -= 256
        lineno += line_incr

    if lineno != lastlineno:
        yield (
         addr, lineno)


class Bytecode:

    def __init__(self, x, *, first_line=None, current_offset=None):
        self.codeobj = co = _get_code_object(x)
        if first_line is None:
            self.first_line = co.co_firstlineno
            self._line_offset = 0
        else:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        self._cell_names = co.co_cellvars + co.co_freevars
        self._linestarts = dict(findlinestarts(co))
        self._original_object = x
        self.current_offset = current_offset

    def __iter__(self):
        co = self.codeobj
        return _get_instructions_bytes((co.co_code), (co.co_varnames), (co.co_names), (co.co_consts),
          (self._cell_names), (self._linestarts),
          line_offset=(self._line_offset))

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self._original_object)

    @classmethod
    def from_traceback(cls, tb):
        while tb.tb_next:
            tb = tb.tb_next

        return cls((tb.tb_frame.f_code), current_offset=(tb.tb_lasti))

    def info(self):
        return _format_code_info(self.codeobj)

    def dis(self):
        co = self.codeobj
        if self.current_offset is not None:
            offset = self.current_offset
        else:
            offset = -1
        with io.StringIO() as (output):
            _disassemble_bytes((co.co_code), varnames=(co.co_varnames), names=(co.co_names),
              constants=(co.co_consts),
              cells=(self._cell_names),
              linestarts=(self._linestarts),
              line_offset=(self._line_offset),
              file=output,
              lasti=offset)
            return output.getvalue()


def _test():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=(argparse.FileType()), nargs='?', default='-')
    args = parser.parse_args()
    with args.infile as (infile):
        source = infile.read()
    code = compile(source, args.infile.name, 'exec')
    dis(code)


if __name__ == '__main__':
    _test()