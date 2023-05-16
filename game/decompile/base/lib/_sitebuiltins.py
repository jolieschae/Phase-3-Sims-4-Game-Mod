# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_sitebuiltins.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3218 bytes
import sys

class Quitter(object):

    def __init__(self, name, eof):
        self.name = name
        self.eof = eof

    def __repr__(self):
        return 'Use %s() or %s to exit' % (self.name, self.eof)

    def __call__(self, code=None):
        try:
            sys.stdin.close()
        except:
            pass

        raise SystemExit(code)


class _Printer(object):
    MAXLINES = 23

    def __init__(self, name, data, files=(), dirs=()):
        import os
        self._Printer__name = name
        self._Printer__data = data
        self._Printer__lines = None
        self._Printer__filenames = [os.path.join(dir, filename) for dir in dirs for filename in iter(files)]

    def __setup(self):
        if self._Printer__lines:
            return
        data = None
        for filename in self._Printer__filenames:
            try:
                with open(filename, 'r') as (fp):
                    data = fp.read()
                break
            except OSError:
                pass

        if not data:
            data = self._Printer__data
        self._Printer__lines = data.split('\n')
        self._Printer__linecnt = len(self._Printer__lines)

    def __repr__(self):
        self._Printer__setup()
        if len(self._Printer__lines) <= self.MAXLINES:
            return '\n'.join(self._Printer__lines)
        return 'Type %s() to see the full %s text' % ((self._Printer__name,) * 2)

    def __call__(self):
        self._Printer__setup()
        prompt = 'Hit Return for more, or q (and Return) to quit: '
        lineno = 0
        while 1:
            try:
                for i in range(lineno, lineno + self.MAXLINES):
                    print(self._Printer__lines[i])

            except IndexError:
                break
            else:
                lineno += self.MAXLINES
                key = None
                while key is None:
                    key = input(prompt)
                    if key not in ('', 'q'):
                        key = None

                if key == 'q':
                    break


class _Helper(object):

    def __repr__(self):
        return 'Type help() for interactive help, or help(object) for help about object.'

    def __call__(self, *args, **kwds):
        import pydoc
        return (pydoc.help)(*args, **kwds)