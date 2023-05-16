# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\etree\ElementInclude.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5334 bytes
import copy
from . import ElementTree
XINCLUDE = '{http://www.w3.org/2001/XInclude}'
XINCLUDE_INCLUDE = XINCLUDE + 'include'
XINCLUDE_FALLBACK = XINCLUDE + 'fallback'

class FatalIncludeError(SyntaxError):
    pass


def default_loader(href, parse, encoding=None):
    if parse == 'xml':
        with open(href, 'rb') as (file):
            data = ElementTree.parse(file).getroot()
    else:
        if not encoding:
            encoding = 'UTF-8'
        with open(href, 'r', encoding=encoding) as (file):
            data = file.read()
    return data


def include(elem, loader=None):
    if loader is None:
        loader = default_loader
    i = 0
    while i < len(elem):
        e = elem[i]
        if e.tag == XINCLUDE_INCLUDE:
            href = e.get('href')
            parse = e.get('parse', 'xml')
            if parse == 'xml':
                node = loader(href, parse)
                if node is None:
                    raise FatalIncludeError('cannot load %r as %r' % (href, parse))
                node = copy.copy(node)
                if e.tail:
                    node.tail = (node.tail or '') + e.tail
                elem[i] = node
            else:
                if parse == 'text':
                    text = loader(href, parse, e.get('encoding'))
                    if text is None:
                        raise FatalIncludeError('cannot load %r as %r' % (href, parse))
                    elif i:
                        node = elem[i - 1]
                        node.tail = (node.tail or '') + text + (e.tail or '')
                    else:
                        elem.text = (elem.text or '') + text + (e.tail or '')
                    del elem[i]
                    continue
                else:
                    raise FatalIncludeError('unknown parse type in xi:include tag (%r)' % parse)
        else:
            if e.tag == XINCLUDE_FALLBACK:
                raise FatalIncludeError('xi:fallback tag must be child of xi:include (%r)' % e.tag)
            else:
                include(e, loader)
        i = i + 1