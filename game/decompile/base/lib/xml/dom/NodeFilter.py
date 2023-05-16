# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\dom\NodeFilter.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 963 bytes


class NodeFilter:
    FILTER_ACCEPT = 1
    FILTER_REJECT = 2
    FILTER_SKIP = 3
    SHOW_ALL = 4294967295
    SHOW_ELEMENT = 1
    SHOW_ATTRIBUTE = 2
    SHOW_TEXT = 4
    SHOW_CDATA_SECTION = 8
    SHOW_ENTITY_REFERENCE = 16
    SHOW_ENTITY = 32
    SHOW_PROCESSING_INSTRUCTION = 64
    SHOW_COMMENT = 128
    SHOW_DOCUMENT = 256
    SHOW_DOCUMENT_TYPE = 512
    SHOW_DOCUMENT_FRAGMENT = 1024
    SHOW_NOTATION = 2048

    def acceptNode(self, node):
        raise NotImplementedError