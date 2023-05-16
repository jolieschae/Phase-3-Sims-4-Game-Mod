# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\glob.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5809 bytes
import os, re, fnmatch
__all__ = [
 'glob', 'iglob', 'escape']

def glob(pathname, *, recursive=False):
    return list(iglob(pathname, recursive=recursive))


def iglob(pathname, *, recursive=False):
    it = _iglob(pathname, recursive, False)
    if recursive:
        if _isrecursive(pathname):
            s = next(it)
    return it


def _iglob(pathname, recursive, dironly):
    dirname, basename = os.path.split(pathname)
    if not has_magic(pathname):
        if basename:
            if os.path.lexists(pathname):
                yield pathname
            else:
                if os.path.isdir(dirname):
                    yield pathname
            return
            if not dirname:
                if recursive and _isrecursive(basename):
                    yield from _glob2(dirname, basename, dironly)
        else:
            yield from _glob1(dirname, basename, dironly)
    else:
        return
        if dirname != pathname:
            if has_magic(dirname):
                dirs = _iglob(dirname, recursive, True)
            else:
                dirs = [
                 dirname]
            if has_magic(basename):
                if recursive and _isrecursive(basename):
                    glob_in_dir = _glob2
                else:
                    glob_in_dir = _glob1
        else:
            glob_in_dir = _glob0
    for dirname in dirs:
        for name in glob_in_dir(dirname, basename, dironly):
            yield os.path.join(dirname, name)


def _glob1(dirname, pattern, dironly):
    names = list(_iterdir(dirname, dironly))
    if not _ishidden(pattern):
        names = (x for x in names if not _ishidden(x))
    return fnmatch.filter(names, pattern)


def _glob0(dirname, basename, dironly):
    if (basename or os.path.isdir)(dirname):
        return [
         basename]
    else:
        if os.path.lexists(os.path.join(dirname, basename)):
            return [
             basename]
    return []


def glob0(dirname, pattern):
    return _glob0(dirname, pattern, False)


def glob1(dirname, pattern):
    return _glob1(dirname, pattern, False)


def _glob2(dirname, pattern, dironly):
    yield pattern[:0]
    yield from _rlistdir(dirname, dironly)


def _iterdir(dirname, dironly):
    if not dirname:
        if isinstance(dirname, bytes):
            dirname = bytes(os.curdir, 'ASCII')
        else:
            dirname = os.curdir
    try:
        with os.scandir(dirname) as (it):
            for entry in it:
                try:
                    if not dironly or entry.is_dir():
                        yield entry.name
                except OSError:
                    pass

    except OSError:
        return


def _rlistdir(dirname, dironly):
    names = list(_iterdir(dirname, dironly))
    for x in names:
        if not _ishidden(x):
            yield x
            path = os.path.join(dirname, x) if dirname else x
            for y in _rlistdir(path, dironly):
                yield os.path.join(x, y)


magic_check = re.compile('([*?[])')
magic_check_bytes = re.compile(b'([*?[])')

def has_magic(s):
    if isinstance(s, bytes):
        match = magic_check_bytes.search(s)
    else:
        match = magic_check.search(s)
    return match is not None


def _ishidden(path):
    return path[0] in ('.', 46)


def _isrecursive(pattern):
    if isinstance(pattern, bytes):
        return pattern == b'**'
    return pattern == '**'


def escape(pathname):
    drive, pathname = os.path.splitdrive(pathname)
    if isinstance(pathname, bytes):
        pathname = magic_check_bytes.sub(b'[\\1]', pathname)
    else:
        pathname = magic_check.sub('[\\1]', pathname)
    return drive + pathname