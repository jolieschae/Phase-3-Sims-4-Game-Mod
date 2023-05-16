# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\internal\message_listener.py
# Compiled at: 2011-01-24 02:39:36
# Size of source mod 2**32: 3432 bytes
__author__ = 'robinson@google.com (Will Robinson)'

class MessageListener(object):

    def Modified(self):
        raise NotImplementedError


class NullMessageListener(object):

    def Modified(self):
        pass