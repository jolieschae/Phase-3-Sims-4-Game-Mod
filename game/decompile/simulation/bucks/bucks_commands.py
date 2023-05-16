# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\bucks\bucks_commands.py
# Compiled at: 2020-10-19 14:00:18
# Size of source mod 2**32: 9360 bytes
from bucks.bucks_enums import BucksType
from bucks.bucks_utils import BucksUtils
from server_commands.argument_helpers import TunableInstanceParam
from sims4.commands import CommandType
import sims4
logger = sims4.log.Logger('Bucks', default_owner='trevor :(')

def get_short_buck_type(buck_type):
    return str(buck_type)[10:]


def get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=False):
    tracker = BucksUtils.get_tracker_for_bucks_type(bucks_type, owner_id, add_if_none=add_if_none)
    if tracker is None:
        sims4.commands.output('Unable to find bucks tracker to unlock perk for Buck Type {} using Owner ID {}.'.format(get_short_buck_type(bucks_type), owner_id), _connection)
    return tracker


def get_bucks_types_without_invalid_gen():
    for bucks_type in BucksType:
        if bucks_type == BucksType.INVALID:
            continue
        yield bucks_type


@sims4.commands.Command('bucks.request_perks_list', command_type=(CommandType.Live))
def request_perks_list(bucks_type: BucksType, owner_id: int=None, sort_by_timestamp: bool=False, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        return False

    def sort_key(perk_message):
        return perk_message.unlock_timestamp

    tracker.send_perks_list_for_bucks_type(bucks_type, sort_key=(sort_key if sort_by_timestamp else None))


@sims4.commands.Command('bucks.unlock_perk', command_type=(CommandType.Live))
def unlock_perk_by_name_or_id(bucks_perk: TunableInstanceParam(sims4.resources.Types.BUCKS_PERK), unlock_for_free: bool=False, bucks_type: BucksType=BucksType.INVALID, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        return False
    elif unlock_for_free:
        tracker.unlock_perk(bucks_perk)
    else:
        tracker.pay_for_and_unlock_perk(bucks_perk)


@sims4.commands.Command('bucks.unlock_multiple_perks', command_type=(CommandType.Live))
def unlock_multiple_perks_with_buck_type(bucks_type: BucksType, owner_id: int, unlock_for_free: bool, *buck_perks: TunableInstanceParam(sims4.resources.Types.BUCKS_PERK), _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        sims4.commands.output('FAILURE\nUnable to create tracker for {} on {}.'.format(bucks_type, owner_id))
        return False
    for perk in buck_perks:
        if unlock_for_free:
            tracker.unlock_perk(perk)
        else:
            tracker.pay_for_and_unlock_perk(perk)


@sims4.commands.Command('bucks.update_bucks_by_amount', command_type=(CommandType.Cheat))
def update_bucks_by_amount(bucks_type: BucksType, amount: int=0, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        return False
    else:
        result = tracker.try_modify_bucks(bucks_type, amount, reason='Added Via Cheat.')
        if not result:
            msg = 'FAILURE\nGiving {} bucks of type {} would result in negative bucks.\nThe most you can remove is {}.'.format(amount, get_short_buck_type(bucks_type), tracker.get_bucks_amount_for_type(bucks_type))
        else:
            msg = 'SUCCESS\n{} bucks of type {} added.\nNew total: {}'.format(amount, get_short_buck_type(bucks_type), tracker.get_bucks_amount_for_type(bucks_type))
    sims4.commands.output(msg, _connection)
    sims4.commands.automation_output(msg, _connection)


@sims4.commands.Command('bucks.request_bucks_list', command_type=(CommandType.Live))
def request_bucks_list(_connection=None):
    for buck_type in get_bucks_types_without_invalid_gen():
        type_str = get_short_buck_type(buck_type)
        sims4.commands.output(' > {}'.format(type_str), _connection)


@sims4.commands.Command('bucks.request_bucks_amounts', command_type=(CommandType.Live))
def request_bucks_amounts(owner_id: int=None, for_bucks_type: BucksType=None, _connection=None):
    for bucks_type in get_bucks_types_without_invalid_gen():
        if for_bucks_type is not None:
            if for_bucks_type is not bucks_type:
                continue
        tracker = BucksUtils.get_tracker_for_bucks_type(bucks_type, owner_id)
        bucks_amount_string = 'No Tracker Found'
        if tracker is not None:
            bucks_amount_string = '{} bucks'.format(tracker.get_bucks_amount_for_type(bucks_type))
        msg = '{} : {}'.format(get_short_buck_type(bucks_type), bucks_amount_string)
        sims4.commands.output(msg, _connection)
        sims4.commands.automation_output(msg, _connection)


@sims4.commands.Command('bucks.lock_perk', command_type=(CommandType.Live))
def lock_perk_by_name_or_id(bucks_perk: TunableInstanceParam(sims4.resources.Types.BUCKS_PERK), bucks_type: BucksType=BucksType.INVALID, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        return False
    tracker.lock_perk(bucks_perk)


@sims4.commands.Command('bucks.lock_all_perks_for_bucks_type', command_type=(CommandType.Live))
def lock_all_perks_for_bucks_type(bucks_type: BucksType=BucksType.INVALID, owner_id: int=None, refund_cost=False, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=True)
    if tracker is None:
        return False
    tracker.lock_all_perks(bucks_type, refund_cost=refund_cost)


@sims4.commands.Command('bucks.has_tracker', command_type=(CommandType.Automation))
def has_buck_tracker(bucks_type: BucksType, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=False)
    bucks_type_exists = tracker.has_bucks_type(bucks_type) if tracker is not None else False
    amount = tracker.get_bucks_amount_for_type(bucks_type) if tracker is not None else 0
    sims4.commands.automation_output('Bucks; TrackerExists:{}, Amount:{}'.format(bucks_type_exists, amount), _connection)


@sims4.commands.Command('bucks.has_perk_unlocked', command_type=(CommandType.Automation))
def has_perk_unlocked(bucks_perk: TunableInstanceParam(sims4.resources.Types.BUCKS_PERK), bucks_type: BucksType, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=False)
    unlocked = tracker is not None and tracker.is_perk_unlocked(bucks_perk)
    sims4.commands.automation_output('HasPerkUnlocked; Unlocked:{}'.format(unlocked), _connection)


@sims4.commands.Command('bucks.reset_recently_locked_perks', command_type=(CommandType.Automation))
def reset_recently_locked_perks(bucks_type: BucksType, owner_id: int=None, _connection=None):
    tracker = get_bucks_tracker(bucks_type, owner_id, _connection, add_if_none=False)
    if tracker is None:
        return False
    tracker.reset_recently_locked_perks(bucks_type)