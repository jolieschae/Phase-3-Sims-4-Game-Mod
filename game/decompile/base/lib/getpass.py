# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\getpass.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 6179 bytes
import contextlib, io, os, sys, warnings
__all__ = [
 'getpass', 'getuser', 'GetPassWarning']

class GetPassWarning(UserWarning):
    pass


def unix_getpass(prompt='Password: ', stream=None):
    passwd = None
    with contextlib.ExitStack() as (stack):
        try:
            fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
            tty = io.FileIO(fd, 'w+')
            stack.enter_context(tty)
            input = io.TextIOWrapper(tty)
            stack.enter_context(input)
            if not stream:
                stream = input
        except OSError as e:
            try:
                stack.close()
                try:
                    fd = sys.stdin.fileno()
                except (AttributeError, ValueError):
                    fd = None
                    passwd = fallback_getpass(prompt, stream)

                input = sys.stdin
                if not stream:
                    stream = sys.stderr
            finally:
                e = None
                del e

        if fd is not None:
            try:
                old = termios.tcgetattr(fd)
                new = old[:]
                new[3] &= ~termios.ECHO
                tcsetattr_flags = termios.TCSAFLUSH
                if hasattr(termios, 'TCSASOFT'):
                    tcsetattr_flags |= termios.TCSASOFT
                try:
                    termios.tcsetattr(fd, tcsetattr_flags, new)
                    passwd = _raw_input(prompt, stream, input=input)
                finally:
                    termios.tcsetattr(fd, tcsetattr_flags, old)
                    stream.flush()

            except termios.error:
                if passwd is not None:
                    raise
                if stream is not input:
                    stack.close()
                passwd = fallback_getpass(prompt, stream)

        stream.write('\n')
        return passwd


def win_getpass(prompt='Password: ', stream=None):
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    for c in prompt:
        msvcrt.putwch(c)

    pw = ''
    while 1:
        c = msvcrt.getwch()
        if not c == '\r':
            if c == '\n':
                break
            if c == '\x03':
                raise KeyboardInterrupt
            if c == '\x08':
                pw = pw[:-1]
            else:
                pw = pw + c

    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    return pw


def fallback_getpass(prompt='Password: ', stream=None):
    warnings.warn('Can not control echo on the terminal.', GetPassWarning, stacklevel=2)
    if not stream:
        stream = sys.stderr
    print('Warning: Password input may be echoed.', file=stream)
    return _raw_input(prompt, stream)


def _raw_input(prompt='', stream=None, input=None):
    if not stream:
        stream = sys.stderr
    else:
        if not input:
            input = sys.stdin
        prompt = str(prompt)
        if prompt:
            try:
                stream.write(prompt)
            except UnicodeEncodeError:
                prompt = prompt.encode(stream.encoding, 'replace')
                prompt = prompt.decode(stream.encoding)
                stream.write(prompt)

            stream.flush()
        line = input.readline()
        assert line
    if line[-1] == '\n':
        line = line[:-1]
    return line


def getuser():
    for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.environ.get(name)
        if user:
            return user

    import pwd
    return pwd.getpwuid(os.getuid())[0]


try:
    import termios
    (
     termios.tcgetattr, termios.tcsetattr)
except (ImportError, AttributeError):
    try:
        import msvcrt
    except ImportError:
        getpass = fallback_getpass
    else:
        getpass = win_getpass
else:
    getpass = unix_getpass