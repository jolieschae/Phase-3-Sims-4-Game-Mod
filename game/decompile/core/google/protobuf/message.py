# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\google\protobuf\message.py
# Compiled at: 2011-01-24 02:39:36
# Size of source mod 2**32: 9937 bytes
__author__ = 'robinson@google.com (Will Robinson)'

class Error(Exception):
    pass


class DecodeError(Error):
    pass


class EncodeError(Error):
    pass


class Message(object):
    __slots__ = []
    DESCRIPTOR = None

    def __deepcopy__(self, memo=None):
        clone = type(self)()
        clone.MergeFrom(self)
        return clone

    def __eq__(self, other_msg):
        raise NotImplementedError

    def __ne__(self, other_msg):
        return not self == other_msg

    def __hash__(self):
        raise TypeError('unhashable object')

    def __str__(self):
        raise NotImplementedError

    def __unicode__(self):
        raise NotImplementedError

    def MergeFrom(self, other_msg):
        raise NotImplementedError

    def CopyFrom(self, other_msg):
        if self is other_msg:
            return
        self.Clear()
        self.MergeFrom(other_msg)

    def Clear(self):
        raise NotImplementedError

    def SetInParent(self):
        raise NotImplementedError

    def IsInitialized(self):
        raise NotImplementedError

    def MergeFromString(self, serialized):
        raise NotImplementedError

    def ParseFromString(self, serialized):
        self.Clear()
        self.MergeFromString(serialized)

    def SerializeToString(self):
        raise NotImplementedError

    def SerializePartialToString(self):
        raise NotImplementedError

    def ListFields(self):
        raise NotImplementedError

    def HasField(self, field_name):
        raise NotImplementedError

    def ClearField(self, field_name):
        raise NotImplementedError

    def HasExtension(self, extension_handle):
        raise NotImplementedError

    def ClearExtension(self, extension_handle):
        raise NotImplementedError

    def ByteSize(self):
        raise NotImplementedError

    def _SetListener(self, message_listener):
        raise NotImplementedError