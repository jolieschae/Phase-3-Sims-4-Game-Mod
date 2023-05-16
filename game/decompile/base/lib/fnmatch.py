# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\fnmatch.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 4184 bytes
import os, posixpath, re, functools
__all__ = [
 'filter', 'fnmatch', 'fnmatchcase', 'translate']

def fnmatch(name, pat):
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    return fnmatchcase(name, pat)


@functools.lru_cache(maxsize=256, typed=True)
def _compile_pattern(pat):
    if isinstance(pat, bytes):
        pat_str = str(pat, 'ISO-8859-1')
        res_str = translate(pat_str)
        res = bytes(res_str, 'ISO-8859-1')
    else:
        res = translate(pat)
    return re.compile(res).match


def filter(names, pat):
    result = []
    pat = os.path.normcase(pat)
    match = _compile_pattern(pat)
    if os.path is posixpath:
        for name in names:
            if match(name):
                result.append(name)

    else:
        for name in names:
            if match(os.path.normcase(name)):
                result.append(name)

    return result


def fnmatchcase(name, pat):
    match = _compile_pattern(pat)
    return match(name) is not None


def translate(pat):
    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            res = res + '.*'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n:
                if pat[j] == '!':
                    j = j + 1
                elif j < n and pat[j] == ']':
                    j = j + 1
                while j < n and pat[j] != ']':
                    j = j + 1

                if j >= n:
                    res = res + '\\['
            else:
                stuff = pat[i:j]
                if '--' not in stuff:
                    stuff = stuff.replace('\\', '\\\\')
                else:
                    chunks = []
                    k = i + 2 if pat[i] == '!' else i + 1
                    while True:
                        k = pat.find('-', k, j)
                        if k < 0:
                            break
                        chunks.append(pat[i:k])
                        i = k + 1
                        k = k + 3

                    chunks.append(pat[i:j])
                    stuff = '-'.join((s.replace('\\', '\\\\').replace('-', '\\-') for s in chunks))
                stuff = re.sub('([&~|])', '\\\\\\1', stuff)
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                else:
                    if stuff[0] in ('^', '['):
                        stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)

    return '(?s:%s)\\Z' % res