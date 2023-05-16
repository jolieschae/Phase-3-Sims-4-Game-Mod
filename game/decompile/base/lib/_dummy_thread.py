# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\_dummy_thread.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5280 bytes
__all__ = [
 "'error'", "'start_new_thread'", "'exit'", "'get_ident'", "'allocate_lock'", 
 "'interrupt_main'", 
 "'LockType'"]
TIMEOUT_MAX = 2147483648
error = RuntimeError

def start_new_thread(function, args, kwargs={}):
    global _interrupt
    global _main
    if type(args) != type(tuple()):
        raise TypeError('2nd arg must be a tuple')
    else:
        if type(kwargs) != type(dict()):
            raise TypeError('3rd arg must be a dict')
        _main = False
        try:
            function(*args, **kwargs)
        except SystemExit:
            pass
        except:
            import traceback
            traceback.print_exc()

    _main = True
    if _interrupt:
        _interrupt = False
        raise KeyboardInterrupt


def exit():
    raise SystemExit


def get_ident():
    return 1


def allocate_lock():
    return LockType()


def stack_size(size=None):
    if size is not None:
        raise error('setting thread stack size not supported')
    return 0


def _set_sentinel():
    return LockType()


class LockType(object):

    def __init__(self):
        self.locked_status = False

    def acquire(self, waitflag=None, timeout=-1):
        if waitflag is None or waitflag:
            self.locked_status = True
            return True
        else:
            self.locked_status = self.locked_status or True
            return True
        if timeout > 0:
            import time
            time.sleep(timeout)
        return False

    __enter__ = acquire

    def __exit__(self, typ, val, tb):
        self.release()

    def release(self):
        if not self.locked_status:
            raise error
        self.locked_status = False
        return True

    def locked(self):
        return self.locked_status

    def __repr__(self):
        return '<%s %s.%s object at %s>' % (
         'locked' if self.locked_status else 'unlocked',
         self.__class__.__module__,
         self.__class__.__qualname__,
         hex(id(self)))


_interrupt = False
_main = True

def interrupt_main():
    global _interrupt
    if _main:
        raise KeyboardInterrupt
    else:
        _interrupt = True