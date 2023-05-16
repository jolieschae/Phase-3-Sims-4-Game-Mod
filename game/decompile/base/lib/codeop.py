# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\codeop.py
# Compiled at: 2011-04-08 23:53:22
# Size of source mod 2**32: 6162 bytes
import __future__
_features = [getattr(__future__, fname) for fname in __future__.all_feature_names]
__all__ = [
 'compile_command', 'Compile', 'CommandCompiler']
PyCF_DONT_IMPLY_DEDENT = 512

def _maybe_compile(compiler, source, filename, symbol):
    for line in source.split('\n'):
        line = line.strip()
        if line and line[0] != '#':
            break
    else:
        if symbol != 'eval':
            source = 'pass'

    err = err1 = err2 = None
    code = code1 = code2 = None
    try:
        code = compiler(source, filename, symbol)
    except SyntaxError as err:
        try:
            pass
        finally:
            err = None
            del err

    try:
        code1 = compiler(source + '\n', filename, symbol)
    except SyntaxError as e:
        try:
            err1 = e
        finally:
            e = None
            del e

    try:
        code2 = compiler(source + '\n\n', filename, symbol)
    except SyntaxError as e:
        try:
            err2 = e
        finally:
            e = None
            del e

    if code:
        return code
    if not code1:
        if repr(err1) == repr(err2):
            raise err1


def _compile(source, filename, symbol):
    return compile(source, filename, symbol, PyCF_DONT_IMPLY_DEDENT)


def compile_command(source, filename='<input>', symbol='single'):
    return _maybe_compile(_compile, source, filename, symbol)


class Compile:

    def __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT

    def __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        for feature in _features:
            if codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag

        return codeob


class CommandCompiler:

    def __init__(self):
        self.compiler = Compile()

    def __call__(self, source, filename='<input>', symbol='single'):
        return _maybe_compile(self.compiler, source, filename, symbol)