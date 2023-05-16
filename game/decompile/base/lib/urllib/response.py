# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\urllib\response.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2379 bytes
import tempfile
__all__ = [
 'addbase', 'addclosehook', 'addinfo', 'addinfourl']

class addbase(tempfile._TemporaryFileWrapper):

    def __init__(self, fp):
        super(addbase, self).__init__(fp, '<urllib response>', delete=False)
        self.fp = fp

    def __repr__(self):
        return '<%s at %r whose fp = %r>' % (self.__class__.__name__,
         id(self), self.file)

    def __enter__(self):
        if self.fp.closed:
            raise ValueError('I/O operation on closed file')
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class addclosehook(addbase):

    def __init__(self, fp, closehook, *hookargs):
        super(addclosehook, self).__init__(fp)
        self.closehook = closehook
        self.hookargs = hookargs

    def close(self):
        try:
            closehook = self.closehook
            hookargs = self.hookargs
            if closehook:
                self.closehook = None
                self.hookargs = None
                closehook(*hookargs)
        finally:
            super(addclosehook, self).close()


class addinfo(addbase):

    def __init__(self, fp, headers):
        super(addinfo, self).__init__(fp)
        self.headers = headers

    def info(self):
        return self.headers


class addinfourl(addinfo):

    def __init__(self, fp, headers, url, code=None):
        super(addinfourl, self).__init__(fp, headers)
        self.url = url
        self.code = code

    def getcode(self):
        return self.code

    def geturl(self):
        return self.url