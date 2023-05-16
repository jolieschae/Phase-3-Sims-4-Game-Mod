# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\protocol_buffer_utils.py
# Compiled at: 2014-10-02 23:10:36
# Size of source mod 2**32: 2550 bytes
from _net_proto2___python import TYPE_MESSAGE, LABEL_REPEATED

def has_field(proto, field_name):
    result = False
    try:
        result = proto.HasField(field_name)
    except ValueError:
        pass

    return result


def persist_fields_for_custom_option(message, custom_option):
    all_clear = True
    if message is None:
        return all_clear
    for name, value in message.DESCRIPTOR.fields_by_name.items():
        options = value.GetOptions()
        if options.Extensions[custom_option]:
            all_clear = False
        elif value.type == TYPE_MESSAGE:
            msg_recur = getattr(message, name)
            recur = (m for m in msg_recur) if value.label == LABEL_REPEATED else (msg_recur,)
            for _msg in recur:
                result = persist_fields_for_custom_option(_msg, custom_option)
                if result:
                    _msg.Clear()
                else:
                    all_clear = False

        else:
            message.ClearField(name)

    return all_clear