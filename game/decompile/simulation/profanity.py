# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\profanity.py
# Compiled at: 2017-02-28 13:38:28
# Size of source mod 2**32: 886 bytes
try:
    import _profanity_filter
except:

    class _profanity_filter:

        @staticmethod
        def scan(*_, **__):
            pass

        @staticmethod
        def check(*_, **__):
            pass


scan = _profanity_filter.scan
check = _profanity_filter.check

def is_name_profane(sim_info):
    profanity_count = scan(sim_info.first_name)
    if profanity_count > 0:
        return True
    profanity_count = scan(sim_info.last_name)
    if profanity_count > 0:
        return True
    profanity_count = scan(sim_info.breed_name)
    if profanity_count > 0:
        return True
    return False