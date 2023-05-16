# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_bootlocale.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1847 bytes
import sys, _locale
if sys.platform.startswith('win'):

    def getpreferredencoding(do_setlocale=True):
        if sys.flags.utf8_mode:
            return 'UTF-8'
        return _locale._getdefaultlocale()[1]


else:
    try:
        _locale.CODESET
    except AttributeError:
        if hasattr(sys, 'getandroidapilevel'):

            def getpreferredencoding(do_setlocale=True):
                return 'UTF-8'


        else:

            def getpreferredencoding(do_setlocale=True):
                if sys.flags.utf8_mode:
                    return 'UTF-8'
                import locale
                return locale.getpreferredencoding(do_setlocale)


    else:

        def getpreferredencoding(do_setlocale=True):
            if sys.flags.utf8_mode:
                return 'UTF-8'
            result = _locale.nl_langinfo(_locale.CODESET)
            if not result:
                if sys.platform == 'darwin':
                    result = 'UTF-8'
            return result