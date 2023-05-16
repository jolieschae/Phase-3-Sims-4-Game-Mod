# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\sax\_exceptions.py
# Compiled at: 2013-04-05 19:16:42
# Size of source mod 2**32: 4916 bytes
import sys
if sys.platform[:4] == 'java':
    from java.lang import Exception
del sys

class SAXException(Exception):

    def __init__(self, msg, exception=None):
        self._msg = msg
        self._exception = exception
        Exception.__init__(self, msg)

    def getMessage(self):
        return self._msg

    def getException(self):
        return self._exception

    def __str__(self):
        return self._msg

    def __getitem__(self, ix):
        raise AttributeError('__getitem__')


class SAXParseException(SAXException):

    def __init__(self, msg, exception, locator):
        SAXException.__init__(self, msg, exception)
        self._locator = locator
        self._systemId = self._locator.getSystemId()
        self._colnum = self._locator.getColumnNumber()
        self._linenum = self._locator.getLineNumber()

    def getColumnNumber(self):
        return self._colnum

    def getLineNumber(self):
        return self._linenum

    def getPublicId(self):
        return self._locator.getPublicId()

    def getSystemId(self):
        return self._systemId

    def __str__(self):
        sysid = self.getSystemId()
        if sysid is None:
            sysid = '<unknown>'
        linenum = self.getLineNumber()
        if linenum is None:
            linenum = '?'
        colnum = self.getColumnNumber()
        if colnum is None:
            colnum = '?'
        return '%s:%s:%s: %s' % (sysid, linenum, colnum, self._msg)


class SAXNotRecognizedException(SAXException):
    pass


class SAXNotSupportedException(SAXException):
    pass


class SAXReaderNotAvailable(SAXNotSupportedException):
    pass