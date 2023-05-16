# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\nturl2path.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2657 bytes


def url2pathname(url):
    import string, urllib.parse
    url = url.replace(':', '|')
    if '|' not in url:
        if url[:4] == '////':
            url = url[2:]
        components = url.split('/')
        return urllib.parse.unquote('\\'.join(components))
    comp = url.split('|')
    if len(comp) != 2 or comp[0][-1] not in string.ascii_letters:
        error = 'Bad URL: ' + url
        raise OSError(error)
    drive = comp[0][-1].upper()
    components = comp[1].split('/')
    path = drive + ':'
    for comp in components:
        if comp:
            path = path + '\\' + urllib.parse.unquote(comp)

    if path.endswith(':'):
        if url.endswith('/'):
            path += '\\'
    return path


def pathname2url(p):
    import urllib.parse
    if ':' not in p:
        if p[:2] == '\\\\':
            p = '\\\\' + p
        components = p.split('\\')
        return urllib.parse.quote('/'.join(components))
    comp = p.split(':')
    if len(comp) != 2 or len(comp[0]) > 1:
        error = 'Bad path: ' + p
        raise OSError(error)
    drive = urllib.parse.quote(comp[0].upper())
    components = comp[1].split('\\')
    path = '///' + drive + ':'
    for comp in components:
        if comp:
            path = path + '/' + urllib.parse.quote(comp)

    return path