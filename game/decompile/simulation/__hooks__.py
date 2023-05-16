# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\__hooks__.py
# Compiled at: 2019-02-21 21:35:20
# Size of source mod 2**32: 1365 bytes
RELOADER_ENABLED = False
__enable_gc_callback = True
import gc
try:
    import _profile
except:
    __enable_gc_callback = False

def system_init(gameplay):
    import sims4.importer
    sims4.importer.enable()
    print('Server Startup')
    if __enable_gc_callback:
        gc.callbacks.append(_profile.notify_gc_function)


def system_shutdown():
    global RELOADER_ENABLED
    import sims4.importer
    sims4.importer.disable()
    RELOADER_ENABLED = False