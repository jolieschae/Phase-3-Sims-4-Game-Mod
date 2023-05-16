# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\omega.py
# Compiled at: 2012-10-02 19:05:18
# Size of source mod 2**32: 729 bytes
try:
    import _omega
except ImportError:

    class _omega:

        @staticmethod
        def send(session_id, msg_id, data):
            return True


_send = _omega.send

def send(session_id, msg_id, data):
    if not _send(session_id, msg_id, data):
        raise KeyError('Failed to find ZoneSessionContext for [ZoneSessionId: 0x{:016x}]'.format(session_id))