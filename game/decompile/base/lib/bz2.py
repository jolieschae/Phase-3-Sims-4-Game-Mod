# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\bz2.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 12767 bytes
__all__ = [
 "'BZ2File'", "'BZ2Compressor'", "'BZ2Decompressor'", 
 "'open'", "'compress'", 
 "'decompress'"]
__author__ = 'Nadeem Vawda <nadeem.vawda@gmail.com>'
from builtins import open as _builtin_open
import io, os, warnings, _compression
from threading import RLock
from _bz2 import BZ2Compressor, BZ2Decompressor
_MODE_CLOSED = 0
_MODE_READ = 1
_MODE_WRITE = 3

class BZ2File(_compression.BaseStream):

    def __init__(self, filename, mode='r', buffering=None, compresslevel=9):
        self._lock = RLock()
        self._fp = None
        self._closefp = False
        self._mode = _MODE_CLOSED
        if buffering is not None:
            warnings.warn("Use of 'buffering' argument is deprecated", DeprecationWarning)
        else:
            if not 1 <= compresslevel <= 9:
                raise ValueError('compresslevel must be between 1 and 9')
            else:
                if mode in ('', 'r', 'rb'):
                    mode = 'rb'
                    mode_code = _MODE_READ
                else:
                    if mode in ('w', 'wb'):
                        mode = 'wb'
                        mode_code = _MODE_WRITE
                        self._compressor = BZ2Compressor(compresslevel)
                    else:
                        if mode in ('x', 'xb'):
                            mode = 'xb'
                            mode_code = _MODE_WRITE
                            self._compressor = BZ2Compressor(compresslevel)
                        else:
                            if mode in ('a', 'ab'):
                                mode = 'ab'
                                mode_code = _MODE_WRITE
                                self._compressor = BZ2Compressor(compresslevel)
                            else:
                                raise ValueError('Invalid mode: %r' % (mode,))
                if isinstance(filename, (str, bytes, os.PathLike)):
                    self._fp = _builtin_open(filename, mode)
                    self._closefp = True
                    self._mode = mode_code
                else:
                    if hasattr(filename, 'read') or hasattr(filename, 'write'):
                        self._fp = filename
                        self._mode = mode_code
                    else:
                        raise TypeError('filename must be a str, bytes, file or PathLike object')
            if self._mode == _MODE_READ:
                raw = _compression.DecompressReader((self._fp), BZ2Decompressor,
                  trailing_error=OSError)
                self._buffer = io.BufferedReader(raw)
            else:
                self._pos = 0

    def close(self):
        with self._lock:
            if self._mode == _MODE_CLOSED:
                return
            try:
                if self._mode == _MODE_READ:
                    self._buffer.close()
                else:
                    if self._mode == _MODE_WRITE:
                        self._fp.write(self._compressor.flush())
                        self._compressor = None
            finally:
                try:
                    if self._closefp:
                        self._fp.close()
                finally:
                    self._fp = None
                    self._closefp = False
                    self._mode = _MODE_CLOSED
                    self._buffer = None

    @property
    def closed(self):
        return self._mode == _MODE_CLOSED

    def fileno(self):
        self._check_not_closed()
        return self._fp.fileno()

    def seekable(self):
        return self.readable() and self._buffer.seekable()

    def readable(self):
        self._check_not_closed()
        return self._mode == _MODE_READ

    def writable(self):
        self._check_not_closed()
        return self._mode == _MODE_WRITE

    def peek(self, n=0):
        with self._lock:
            self._check_can_read()
            return self._buffer.peek(n)

    def read(self, size=-1):
        with self._lock:
            self._check_can_read()
            return self._buffer.read(size)

    def read1(self, size=-1):
        with self._lock:
            self._check_can_read()
            if size < 0:
                size = io.DEFAULT_BUFFER_SIZE
            return self._buffer.read1(size)

    def readinto(self, b):
        with self._lock:
            self._check_can_read()
            return self._buffer.readinto(b)

    def readline(self, size=-1):
        if not isinstance(size, int):
            if not hasattr(size, '__index__'):
                raise TypeError('Integer argument expected')
            size = size.__index__()
        with self._lock:
            self._check_can_read()
            return self._buffer.readline(size)

    def readlines(self, size=-1):
        if not isinstance(size, int):
            if not hasattr(size, '__index__'):
                raise TypeError('Integer argument expected')
            size = size.__index__()
        with self._lock:
            self._check_can_read()
            return self._buffer.readlines(size)

    def write(self, data):
        with self._lock:
            self._check_can_write()
            compressed = self._compressor.compress(data)
            self._fp.write(compressed)
            self._pos += len(data)
            return len(data)

    def writelines(self, seq):
        with self._lock:
            return _compression.BaseStream.writelines(self, seq)

    def seek(self, offset, whence=io.SEEK_SET):
        with self._lock:
            self._check_can_seek()
            return self._buffer.seek(offset, whence)

    def tell(self):
        with self._lock:
            self._check_not_closed()
            if self._mode == _MODE_READ:
                return self._buffer.tell()
            return self._pos


def open(filename, mode='rb', compresslevel=9, encoding=None, errors=None, newline=None):
    if 't' in mode:
        if 'b' in mode:
            raise ValueError('Invalid mode: %r' % (mode,))
    else:
        if encoding is not None:
            raise ValueError("Argument 'encoding' not supported in binary mode")
        if errors is not None:
            raise ValueError("Argument 'errors' not supported in binary mode")
        if newline is not None:
            raise ValueError("Argument 'newline' not supported in binary mode")
    bz_mode = mode.replace('t', '')
    binary_file = BZ2File(filename, bz_mode, compresslevel=compresslevel)
    if 't' in mode:
        return io.TextIOWrapper(binary_file, encoding, errors, newline)
    return binary_file


def compress(data, compresslevel=9):
    comp = BZ2Compressor(compresslevel)
    return comp.compress(data) + comp.flush()


def decompress(data):
    results = []
    while data:
        decomp = BZ2Decompressor()
        try:
            res = decomp.decompress(data)
        except OSError:
            if results:
                break
            else:
                raise

        results.append(res)
        if not decomp.eof:
            raise ValueError('Compressed data ended before the end-of-stream marker was reached')
        data = decomp.unused_data

    return (b'').join(results)