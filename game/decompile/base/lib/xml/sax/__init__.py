# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\sax\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3700 bytes
from .xmlreader import InputSource
from .handler import ContentHandler, ErrorHandler
from ._exceptions import SAXException, SAXNotRecognizedException, SAXParseException, SAXNotSupportedException, SAXReaderNotAvailable

def parse(source, handler, errorHandler=ErrorHandler()):
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.parse(source)


def parseString(string, handler, errorHandler=ErrorHandler()):
    import io
    if errorHandler is None:
        errorHandler = ErrorHandler()
    else:
        parser = make_parser()
        parser.setContentHandler(handler)
        parser.setErrorHandler(errorHandler)
        inpsrc = InputSource()
        if isinstance(string, str):
            inpsrc.setCharacterStream(io.StringIO(string))
        else:
            inpsrc.setByteStream(io.BytesIO(string))
    parser.parse(inpsrc)


default_parser_list = [
 'xml.sax.expatreader']
_false = 0
if _false:
    import xml.sax.expatreader
import os, sys
if 'PY_SAX_PARSER' in os.environ:
    default_parser_list = os.environ['PY_SAX_PARSER'].split(',')
else:
    del os
    _key = 'python.xml.sax.parser'
    if sys.platform[:4] == 'java':
        if sys.registry.containsKey(_key):
            default_parser_list = sys.registry.getProperty(_key).split(',')

    def make_parser(parser_list=[]):
        for parser_name in parser_list + default_parser_list:
            try:
                return _create_parser(parser_name)
            except ImportError as e:
                try:
                    import sys
                    if parser_name in sys.modules:
                        raise
                finally:
                    e = None
                    del e

            except SAXReaderNotAvailable:
                pass

        raise SAXReaderNotAvailable('No parsers found', None)


    if sys.platform[:4] == 'java':

        def _create_parser(parser_name):
            from org.python.core import imp
            drv_module = imp.importName(parser_name, 0, globals())
            return drv_module.create_parser()


    else:

        def _create_parser(parser_name):
            drv_module = __import__(parser_name, {}, {}, ['create_parser'])
            return drv_module.create_parser()


del sys