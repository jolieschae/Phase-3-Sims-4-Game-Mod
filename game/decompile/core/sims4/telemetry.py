# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Core\sims4\telemetry.py
# Compiled at: 2021-03-09 14:10:00
# Size of source mod 2**32: 14959 bytes
import bisect, enum, services, sims4.collections, sims4.log, sims4.reload
try:
    import _telemetry
except ImportError:

    class _telemetry:

        @staticmethod
        def log_event(session_id, module_key, group_key, hook_key, attributes):
            pass


__all__ = ['TelemetryWriter']
with sims4.reload.protected(globals()):
    _archiver_map = {}
    _filters = []
logger = sims4.log.Logger('Telemetry')
DEFAULT_MODULE_TAG = 'GAME'
RESERVED_FIELDS = {
 'hip_'}

class RuleAction(enum.Int):
    DROP = 0
    COLLECT = 1


def add_filter_rule(priority, module_tag, group_tag, hook_tag, fields, action):
    fields = sims4.collections.frozendict(fields)
    key = _get_key(module_tag, group_tag, hook_tag)
    record = (priority, key, fields, action)
    bisect.insort(_filters, record)


def remove_filter_rule(priority, module_tag, group_tag, hook_tag, fields, action):
    fields = sims4.collections.frozendict(fields)
    key = _get_key(module_tag, group_tag, hook_tag)
    record = (priority, key, fields, action)
    index = bisect.bisect_left(_filters, record)
    if index != len(_filters):
        if _filters[index] == record:
            del _filters[index]
            return True
    return False


class TelemetryWriter:

    def __init__(self, group_tag, module_tag=DEFAULT_MODULE_TAG):
        self.module_tag = module_tag
        self.group_tag = group_tag

    def begin_hook(self, hook_tag, valid_for_npc=False):
        return _TelemetryHookWriter(self, hook_tag, valid_for_npc)


def check_telemetry_tag(tag):
    pass


class _TelemetryHookWriter:

    def __init__(self, writer, hook_tag, valid_for_npc):
        self.session_id = 0
        self.disabled_hook = False
        self.module_tag = writer.module_tag
        self.group_tag = writer.group_tag
        self.hook_tag = hook_tag
        self.valid_for_npc = valid_for_npc
        self.data = []

    def write_bool(self, tag, value):
        output = '1' if value else '0'
        self.data.append((tag, output))

    def write_int(self, tag, value):
        output = str(int(value))
        self.data.append((tag, output))

    def write_localized_string(self, tag, localized_string):
        output = '{0:#x}'.format(localized_string.hash)
        self.data.append((tag, output))

    def write_enum(self, tag, value):
        output = str(value)
        self.data.append((tag, output))

    def write_guid(self, tag, value):
        output = '_' + str(int(value))
        self.data.append((tag, output))

    def write_float(self, tag, value, precision=2):
        output = '{0:.{1}f}'.format(value, precision)
        self.data.append((tag, output))

    def write_string(self, tag, value):
        self.data.append((tag, value))

    def _commit(self):
        if self.disabled_hook:
            return
        else:
            return _check_filter(self.module_tag, self.group_tag, self.hook_tag, self.data) or None
        _telemetry.log_event(self.session_id, self.module_tag, self.group_tag, self.hook_tag, self.data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            self._commit()
            return
        else:
            return isinstance(exc_value, Exception) or False
        sims4.log.exception('Telemetry', 'Exception while processing telemetry hooks!')
        return True


def _get_key(module_tag, group_tag, hook_tag):
    key = []
    if module_tag is not None:
        key.append(module_tag)
        if group_tag is not None:
            key.append(group_tag)
            if hook_tag is not None:
                key.append(hook_tag)
    return tuple(key)


def _check_filter(module_tag, group_tag, hook_tag, data):
    for _, tags, fields, action in _filters:
        l = len(tags)
        match = False
        if l == 3:
            match = tags[2] == hook_tag and tags[1] == group_tag and tags[0] == module_tag
        else:
            if l == 2:
                match = tags[1] == group_tag and tags[0] == module_tag
            else:
                if l == 1:
                    match = tags[0] == module_tag
                else:
                    if l == 0:
                        match = True
        if match:
            if not fields or _check_fields(fields, data):
                return action == RuleAction.COLLECT

    return True


def _check_fields(fields, data):
    expected = len(fields)
    if not expected:
        return True
    matches = 0
    for key, value in data:
        if key in fields:
            if fields[key] != value:
                return False
            matches += 1
            if matches == expected:
                return True

    return False


FIELD_ACCOUNT_ID = 'acct'
FIELD_SIM_ID = 'simi'
FIELD_SIM_CLASS = 'clss'
FIELD_HOUSEHOLD_ID = 'hous'
FIELD_ZONE_ID = 'zone'
FIELD_TIME = 'time'
FIELD_SIM_MOOD = 'mood'
FIELD_SIM_OCCULTS = 'aoct'
FIELD_SIM_CURRENT_OCCULTS = 'coct'
FIELD_SIM_POSITION_X = 'posx'
FIELD_SIM_POSITION_Y = 'posy'
FIELD_SIM_POSITION_Z = 'posz'
FIELD_LOT_DESCRIPTION_ID = 'ldid'

def _write_common_data(hook, sim_id=0, household_id=0, session_id=0, sim_time=0, sim_mood=0, sim_class=0, occult_types=0, current_occult_types=0, sim_position=None):
    hook.session_id = session_id
    zone_id = sims4.zone_utils.zone_id
    if zone_id is not None:
        hook.write_int(FIELD_ZONE_ID, zone_id)
    hook.write_int(FIELD_SIM_ID, sim_id)
    hook.write_guid(FIELD_SIM_CLASS, sim_class)
    hook.write_int(FIELD_HOUSEHOLD_ID, household_id)
    hook.write_int(FIELD_TIME, sim_time)
    hook.write_guid(FIELD_SIM_MOOD, sim_mood)
    hook.write_int(FIELD_SIM_OCCULTS, occult_types)
    hook.write_int(FIELD_SIM_CURRENT_OCCULTS, current_occult_types)
    if sim_position is not None:
        hook.write_float(FIELD_SIM_POSITION_X, sim_position.x)
        hook.write_float(FIELD_SIM_POSITION_Y, sim_position.y)
        hook.write_float(FIELD_SIM_POSITION_Z, sim_position.z)
        current_zone = services.current_zone()
        if current_zone is not None:
            _, lot_description_id = services.get_world_and_lot_description_id_from_zone_id(current_zone.id)
            hook.write_int(FIELD_LOT_DESCRIPTION_ID, lot_description_id)


def begin_hook(writer, hook_tag, **kwargs):
    hook = writer.begin_hook(hook_tag)
    _write_common_data(hook, **kwargs)
    return hook