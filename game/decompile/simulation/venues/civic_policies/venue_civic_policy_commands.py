# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\civic_policies\venue_civic_policy_commands.py
# Compiled at: 2020-10-02 12:44:04
# Size of source mod 2**32: 6364 bytes
import sims4
from civic_policies.base_civic_policy_utilities import CivicPolicyProviderListSelector, debug_automation_output_policy_name_list, debug_automation_output_vote_info
from distributor.ops import CommunityBoardDialog
from distributor.system import Distributor
from server_commands.argument_helpers import OptionalSimInfoParam, get_optional_target, TunableInstanceParam
from sims4.common import Pack
import services

@sims4.commands.Command('civic_policy.venue.enact', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_enact--- This code section failed: ---

 L.  24         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              venue_service
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  LOAD_ATTR                source_venue
                8  STORE_FAST               'source_venue'

 L.  25        10  LOAD_FAST                'source_venue'
               12  LOAD_CONST               None
               14  COMPARE_OP               is
               16  POP_JUMP_IF_TRUE     40  'to 40'

 L.  26        18  LOAD_FAST                'source_venue'
               20  LOAD_ATTR                civic_policy_provider
               22  LOAD_CONST               None
               24  COMPARE_OP               is
               26  POP_JUMP_IF_TRUE     40  'to 40'

 L.  27        28  LOAD_FAST                'source_venue'
               30  LOAD_ATTR                civic_policy_provider
               32  LOAD_METHOD              enact
               34  LOAD_FAST                'policy'
               36  CALL_METHOD_1         1  '1 positional argument'
               38  POP_JUMP_IF_TRUE     76  'to 76'
             40_0  COME_FROM            26  '26'
             40_1  COME_FROM            16  '16'

 L.  28        40  LOAD_GLOBAL              sims4
               42  LOAD_ATTR                commands
               44  LOAD_METHOD              automation_output
               46  LOAD_STR                 'Status; Result:Failed'
               48  LOAD_FAST                '_connection'
               50  CALL_METHOD_2         2  '2 positional arguments'
               52  POP_TOP          

 L.  29        54  LOAD_GLOBAL              sims4
               56  LOAD_ATTR                commands
               58  LOAD_METHOD              cheat_output
               60  LOAD_STR                 '{} not enacted'
               62  LOAD_METHOD              format
               64  LOAD_FAST                'policy'
               66  CALL_METHOD_1         1  '1 positional argument'
               68  LOAD_FAST                '_connection'
               70  CALL_METHOD_2         2  '2 positional arguments'
               72  POP_TOP          
               74  JUMP_FORWARD         90  'to 90'
             76_0  COME_FROM            38  '38'

 L.  31        76  LOAD_GLOBAL              sims4
               78  LOAD_ATTR                commands
               80  LOAD_METHOD              automation_output
               82  LOAD_STR                 'Status; Result:Success'
               84  LOAD_FAST                '_connection'
               86  CALL_METHOD_2         2  '2 positional arguments'
               88  POP_TOP          
             90_0  COME_FROM            74  '74'

Parse error at or near `JUMP_FORWARD' instruction at offset 74


@sims4.commands.Command('civic_policy.venue.repeal', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_repeal--- This code section failed: ---

 L.  39         0  LOAD_GLOBAL              services
                2  LOAD_METHOD              venue_service
                4  CALL_METHOD_0         0  '0 positional arguments'
                6  LOAD_ATTR                source_venue
                8  STORE_FAST               'source_venue'

 L.  40        10  LOAD_FAST                'source_venue'
               12  LOAD_CONST               None
               14  COMPARE_OP               is
               16  POP_JUMP_IF_TRUE     40  'to 40'

 L.  41        18  LOAD_FAST                'source_venue'
               20  LOAD_ATTR                civic_policy_provider
               22  LOAD_CONST               None
               24  COMPARE_OP               is
               26  POP_JUMP_IF_TRUE     40  'to 40'

 L.  42        28  LOAD_FAST                'source_venue'
               30  LOAD_ATTR                civic_policy_provider
               32  LOAD_METHOD              repeal
               34  LOAD_FAST                'policy'
               36  CALL_METHOD_1         1  '1 positional argument'
               38  POP_JUMP_IF_TRUE     76  'to 76'
             40_0  COME_FROM            26  '26'
             40_1  COME_FROM            16  '16'

 L.  43        40  LOAD_GLOBAL              sims4
               42  LOAD_ATTR                commands
               44  LOAD_METHOD              automation_output
               46  LOAD_STR                 'Status; Result:Failed'
               48  LOAD_FAST                '_connection'
               50  CALL_METHOD_2         2  '2 positional arguments'
               52  POP_TOP          

 L.  44        54  LOAD_GLOBAL              sims4
               56  LOAD_ATTR                commands
               58  LOAD_METHOD              cheat_output
               60  LOAD_STR                 '{} not repealed'
               62  LOAD_METHOD              format
               64  LOAD_FAST                'policy'
               66  CALL_METHOD_1         1  '1 positional argument'
               68  LOAD_FAST                '_connection'
               70  CALL_METHOD_2         2  '2 positional arguments'
               72  POP_TOP          
               74  JUMP_FORWARD         90  'to 90'
             76_0  COME_FROM            38  '38'

 L.  46        76  LOAD_GLOBAL              sims4
               78  LOAD_ATTR                commands
               80  LOAD_METHOD              automation_output
               82  LOAD_STR                 'Status; Result:Success'
               84  LOAD_FAST                '_connection'
               86  CALL_METHOD_2         2  '2 positional arguments'
               88  POP_TOP          
             90_0  COME_FROM            74  '74'

Parse error at or near `JUMP_FORWARD' instruction at offset 74


@sims4.commands.Command('civic_policy.venue.vote', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_vote--- This code section failed: ---

 L.  54         0  LOAD_GLOBAL              int
                2  LOAD_FAST                'count'
                4  CALL_FUNCTION_1       1  '1 positional argument'
                6  STORE_FAST               'count'

 L.  55         8  LOAD_GLOBAL              services
               10  LOAD_METHOD              venue_service
               12  CALL_METHOD_0         0  '0 positional arguments'
               14  LOAD_ATTR                source_venue
               16  STORE_FAST               'source_venue'

 L.  56        18  LOAD_FAST                'source_venue'
               20  LOAD_CONST               None
               22  COMPARE_OP               is
               24  POP_JUMP_IF_TRUE     50  'to 50'

 L.  57        26  LOAD_FAST                'source_venue'
               28  LOAD_ATTR                civic_policy_provider
               30  LOAD_CONST               None
               32  COMPARE_OP               is
               34  POP_JUMP_IF_TRUE     50  'to 50'

 L.  58        36  LOAD_FAST                'source_venue'
               38  LOAD_ATTR                civic_policy_provider
               40  LOAD_METHOD              vote
               42  LOAD_FAST                'policy'
               44  LOAD_FAST                'count'
               46  CALL_METHOD_2         2  '2 positional arguments'
               48  POP_JUMP_IF_TRUE     86  'to 86'
             50_0  COME_FROM            34  '34'
             50_1  COME_FROM            24  '24'

 L.  59        50  LOAD_GLOBAL              sims4
               52  LOAD_ATTR                commands
               54  LOAD_METHOD              cheat_output
               56  LOAD_STR                 'Could not add vote to {}'
               58  LOAD_METHOD              format
               60  LOAD_FAST                'policy'
               62  CALL_METHOD_1         1  '1 positional argument'
               64  LOAD_FAST                '_connection'
               66  CALL_METHOD_2         2  '2 positional arguments'
               68  POP_TOP          

 L.  60        70  LOAD_GLOBAL              sims4
               72  LOAD_ATTR                commands
               74  LOAD_METHOD              automation_output
               76  LOAD_STR                 'Status; Result:Failed'
               78  LOAD_FAST                '_connection'
               80  CALL_METHOD_2         2  '2 positional arguments'
               82  POP_TOP          
               84  JUMP_FORWARD        100  'to 100'
             86_0  COME_FROM            48  '48'

 L.  62        86  LOAD_GLOBAL              sims4
               88  LOAD_ATTR                commands
               90  LOAD_METHOD              automation_output
               92  LOAD_STR                 'Status; Result:Success'
               94  LOAD_FAST                '_connection'
               96  CALL_METHOD_2         2  '2 positional arguments'
               98  POP_TOP          
            100_0  COME_FROM            84  '84'

Parse error at or near `JUMP_FORWARD' instruction at offset 84


@sims4.commands.Command('civic_policy.venue.force_end_voting', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def venue_civic_policy_force_end_voting(_connection=None):
    source_venue = services.venue_service.source_venue
    if source_venue is None:
        return False
    provider = source_venue.civic_policy_provider
    if provider is None:
        return False

    def output_enacted_policy_list():
        policies = provider.get_enacted_policies
        for policy in policies:
            sims4.commands.cheat_output'    {}'.formatpolicy_connection

    sims4.commands.cheat_output'Before Enacted Policies'_connection
    output_enacted_policy_list()
    provider.close_voting
    sims4.commands.cheat_output'After Enacted Policies'_connection
    output_enacted_policy_list()


@sims4.commands.Command('civic_policy.venue.show_community_board', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Live))
def venue_civic_policy_show_community_board(opt_sim: OptionalSimInfoParam=None, opt_target_id: int=0, _connection=None):
    street_service = services.street_service
    if street_service is None:
        sims4.commands.automation_output'Pack not loaded'_connection
        sims4.commands.cheat_output'Pack not loaded'_connection
        return
    sim_info = get_optional_target(opt_sim, _connection, target_type=OptionalSimInfoParam)
    source_venue = services.venue_service.source_venue
    if source_venue is None:
        return
    provider = source_venue.civic_policy_provider
    if provider is None:
        return
    op = CommunityBoardDialog(provider, sim_info, opt_target_id)
    Distributor.instance.add_op_with_no_ownerop


@sims4.commands.Command('civic_policy.venue.policy_list', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def civic_policy_list(selector: CivicPolicyProviderListSelector=None, _connection=None):
    source_venue = services.venue_service.source_venue
    if source_venue is None:
        return False
    provider = source_venue.civic_policy_provider
    if provider is None:
        return False
    debug_automation_output_policy_name_list(provider, selector, _connection)


@sims4.commands.Command('civic_policy.venue.vote_count', pack=(Pack.EP09), command_type=(sims4.commands.CommandType.Automation))
def street_civic_policy_vote_count(policy: TunableInstanceParam(sims4.resources.Types.SNIPPET), _connection=None):
    provider = None
    source_venue = services.venue_service.source_venue
    if source_venue is not None:
        provider = source_venue.civic_policy_provider
    debug_automation_output_vote_info(provider, policy, _connection)