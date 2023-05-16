# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\linecache.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5489 bytes
import functools, sys, os, tokenize
__all__ = [
 'getline', 'clearcache', 'checkcache']

def getline(filename, lineno, module_globals=None):
    lines = getlines(filename, module_globals)
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1]
    return ''


cache = {}

def clearcache():
    global cache
    cache = {}


def getlines(filename, module_globals=None):
    if filename in cache:
        entry = cache[filename]
        if len(entry) != 1:
            return cache[filename][2]
    try:
        return updatecache(filename, module_globals)
    except MemoryError:
        clearcache()
        return []


def checkcache(filename=None):
    if filename is None:
        filenames = list(cache.keys())
    else:
        if filename in cache:
            filenames = [
             filename]
        else:
            return
    for filename in filenames:
        entry = cache[filename]
        if len(entry) == 1:
            continue
        size, mtime, lines, fullname = entry
        if mtime is None:
            continue
        try:
            stat = os.stat(fullname)
        except OSError:
            del cache[filename]
            continue

        if size != stat.st_size or mtime != stat.st_mtime:
            del cache[filename]


def updatecache(filename, module_globals=None):
    if filename in cache:
        if len(cache[filename]) != 1:
            del cache[filename]
    elif filename:
        if filename.startswith('<'):
            if filename.endswith('>'):
                return []
    else:
        fullname = filename
        try:
            stat = os.stat(fullname)
        except OSError:
            basename = filename
            if lazycache(filename, module_globals):
                try:
                    data = cache[filename][0]()
                except (ImportError, OSError):
                    pass
                else:
                    if data is None:
                        return []
                    cache[filename] = (
                     len(data), None,
                     [line + '\n' for line in data.splitlines()], fullname)
                    return cache[filename][2]
            if os.path.isabs(filename):
                return []
            for dirname in sys.path:
                try:
                    fullname = os.path.join(dirname, basename)
                except (TypeError, AttributeError):
                    continue

                try:
                    stat = os.stat(fullname)
                    break
                except OSError:
                    pass

            else:
                return []

    try:
        with tokenize.open(fullname) as (fp):
            lines = fp.readlines()
    except OSError:
        return []
    else:
        if lines:
            if not lines[-1].endswith('\n'):
                lines[-1] += '\n'
        size, mtime = stat.st_size, stat.st_mtime
        cache[filename] = (size, mtime, lines, fullname)
        return lines


def lazycache(filename, module_globals):
    if filename in cache:
        if len(cache[filename]) == 1:
            return True
        return False
        if filename:
            if filename.startswith('<'):
                if filename.endswith('>'):
                    return False
    elif module_globals:
        if '__loader__' in module_globals:
            name = module_globals.get('__name__')
            loader = module_globals['__loader__']
            get_source = getattr(loader, 'get_source', None)
            if name:
                if get_source:
                    get_lines = functools.partial(get_source, name)
                    cache[filename] = (get_lines,)
                    return True
    return False