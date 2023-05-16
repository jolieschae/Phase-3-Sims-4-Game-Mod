# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\filters\sim_filter_service.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 57528 bytes
import collections
from filters import sim_filter_handlers
from filters.tunable import FilterResult, FilterTermTag
from interactions.liability import Liability
from objects import ALL_HIDDEN_REASONS
from random import shuffle
from sims4 import random
from sims4.service_manager import Service
from singletons import EMPTY_SET
import enum, filters, gsi_handlers.sim_filter_service_handlers, services, sims4.log
logger = sims4.log.Logger('SimFilter')
SIM_FILTER_GLOBAL_BLACKLIST_LIABILITY = 'SimFilterGlobalBlacklistLiability'

class SimFilterGlobalBlacklistReason(enum.Int, export=False):
    PHONE_CALL = 1
    SIM_INFO_BEING_REMOVED = 2
    MISSING_PET = 3
    RABBIT_HOLE = 4


class SimFilterGlobalBlacklistLiability(Liability):

    def __init__(self, blacklist_sim_ids, reason, **kwargs):
        (super().__init__)(**kwargs)
        self._blacklist_sim_ids = blacklist_sim_ids
        self._reason = reason
        self._has_been_added = False

    def on_add(self, _):
        if self._has_been_added:
            return
        sim_filter_service = services.sim_filter_service()
        if sim_filter_service is not None:
            for sim_id in self._blacklist_sim_ids:
                services.sim_filter_service().add_sim_id_to_global_blacklist(sim_id, self._reason)

        self._has_been_added = True

    def release(self):
        sim_filter_service = services.sim_filter_service()
        if sim_filter_service is not None:
            for sim_id in self._blacklist_sim_ids:
                services.sim_filter_service().remove_sim_id_from_global_blacklist(sim_id, self._reason)


class SimFilterRequestState(enum.Int, export=False):
    SETUP = ...
    RAN_QUERY = ...
    SPAWNING_SIMS = ...
    FILLED_RESULTS = ...
    COMPLETE = ...


class _BaseSimFilterRequest:

    def __init__(self, callback=None, callback_event_data=None, blacklist_sim_ids=None, gsi_logging_data=None, sim_gsi_logging_data=None, required_story_progression_arc=None):
        self._state = SimFilterRequestState.SETUP
        self._callback = callback
        self._callback_event_data = callback_event_data
        self._blacklist_sim_ids = set(blacklist_sim_ids) if blacklist_sim_ids is not None else set()
        self._gsi_logging_data = gsi_logging_data
        self._sim_gsi_logging_data = sim_gsi_logging_data
        self._required_story_progression_arc = required_story_progression_arc

    @property
    def is_complete(self):
        return self._state == SimFilterRequestState.COMPLETE

    def run(self):
        raise NotImplementedError

    def run_without_yielding(self):
        raise NotImplementedError

    def gsi_start_logging(self, request_type, filter_type, yielding, gsi_source_fn):
        if self._gsi_logging_data is None:
            if gsi_handlers.sim_filter_service_handlers.archiver.enabled:
                self._gsi_logging_data = gsi_handlers.sim_filter_service_handlers.SimFilterServiceGSILoggingData(request_type, str(filter_type), yielding, gsi_source_fn)
        if self._sim_gsi_logging_data is None:
            if sim_filter_handlers.archiver.enabled:
                self._sim_gsi_logging_data = sim_filter_handlers.SimFilterGSILoggingData(request_type, str(filter_type), gsi_source_fn)

    def gsi_add_rejected_sim_info(self, sim_info, reason, filter_term=None):
        if self._gsi_logging_data is not None:
            self._gsi_logging_data.add_rejected_sim_info(sim_info, reason, filter_term)

    def gsi_archive_logging(self, filter_results):
        if self._gsi_logging_data is not None:
            gsi_handlers.sim_filter_service_handlers.archive_filter_request(filter_results, self._gsi_logging_data)
            self._gsi_logging_data = None


class _SimFilterRequest(_BaseSimFilterRequest):

    def __init__(self, sim_filter=None, requesting_sim_info=None, sim_constraints=None, household_id=None, start_time=None, end_time=None, club=None, tag=FilterTermTag.NO_TAG, optional=True, gsi_source_fn=None, additional_filter_terms=(), include_rabbithole_sims=False, include_missing_pets=False, **kwargs):
        (super().__init__)(**kwargs)
        if sim_filter is None:
            sim_filter = filters.tunable.TunableSimFilter.BLANK_FILTER
        else:
            self._sim_filter = sim_filter
            self._additional_filter_terms = additional_filter_terms
            self._requesting_sim_info = requesting_sim_info
            self._sim_constraints = sim_constraints
            if household_id is not None:
                self._household_id = household_id
            else:
                if requesting_sim_info:
                    self._household_id = requesting_sim_info.household_id
                else:
                    self._household_id = 0
            if start_time is not None:
                self._start_time = start_time.time_since_beginning_of_week()
            else:
                self._start_time = None
            if end_time is not None:
                self._end_time = end_time.time_since_beginning_of_week()
            else:
                self._end_time = None
        self._club = club
        self.tag = tag
        self.optional = optional
        self._gsi_source_fn = gsi_source_fn
        self._include_rabbithole_sims = include_rabbithole_sims
        self._include_missing_pets = include_missing_pets

    def run(self):
        if self._state == SimFilterRequestState.SETUP:
            logger.assert_raise(self._sim_filter is not None, '[rez] Sim Filter is None in _SimFilterRequest.')
            self.gsi_start_logging('_SimFilterRequest', self._sim_filter, False, self._gsi_source_fn)
            results = self._run_filter_query()
            if self._callback is not None:
                self._callback(results, self._callback_event_data)
            self._state = SimFilterRequestState.COMPLETE
            if self._gsi_logging_data is not None:
                self._gsi_logging_data.add_metadata(None, None, self._club, self._blacklist_sim_ids, self.optional, self._required_story_progression_arc)
            self.gsi_archive_logging(results)

    def run_without_yielding(self):
        self.gsi_start_logging('_SimFilterRequest ', self._sim_filter, True, self._gsi_source_fn)
        results = self._run_filter_query()
        if self._gsi_logging_data is not None:
            self._gsi_logging_data.add_metadata(None, None, self._club, self._blacklist_sim_ids, self.optional, self._required_story_progression_arc)
        self.gsi_archive_logging(results)
        return results

    def _get_constrained_sims(self):
        return self._sim_constraints

    def _run_filter_query(self):
        constrained_sim_ids = self._get_constrained_sims()
        results = self._find_sims_matching_filter(constrained_sim_ids=constrained_sim_ids, start_time=(self._start_time),
          end_time=(self._end_time),
          household_id=(self._household_id),
          requesting_sim_info=(self._requesting_sim_info),
          club=(self._club),
          tag=(self.tag))
        sim_filter_service = services.sim_filter_service()
        global_blacklist = sim_filter_service.get_global_blacklist()
        for result in tuple(results):
            sim_info = result.sim_info
            if sim_info.id in self._blacklist_sim_ids or sim_info.id in global_blacklist:
                reasons = sim_filter_service.get_global_blacklist_reason(sim_info.id)
                if reasons:
                    num_reasons = len(reasons)
                    if self._include_rabbithole_sims:
                        if SimFilterGlobalBlacklistReason.RABBIT_HOLE in reasons:
                            num_reasons -= 1
                    if self._include_missing_pets:
                        if SimFilterGlobalBlacklistReason.MISSING_PET in reasons:
                            num_reasons -= 1
                    if num_reasons == 0:
                        continue
                results.remove(result)
                self.gsi_add_rejected_sim_info(sim_info, 'Global Blacklisted' if sim_info.id in global_blacklist else 'Filter Request Blacklisted')
                if self._sim_gsi_logging_data is not None:
                    sim_filter_handlers.archive_filter_request(sim_info, (self._sim_gsi_logging_data), rejected=True, reason=('Global Blacklisted' if sim_info.id in global_blacklist else 'Filter Request Blacklisted'))
                elif self._required_story_progression_arc is not None:
                    rule_set = sim_info.household.story_progression_rule_set
                    if not rule_set.verify(self._required_story_progression_arc.required_rules):
                        results.remove(result)
                        self.gsi_add_rejected_sim_info(sim_info, 'Missing Required Story Progression Rules')
                        if self._sim_gsi_logging_data is not None:
                            sim_filter_handlers.archive_filter_request(sim_info, (self._sim_gsi_logging_data), rejected=True, reason='Missing Required Story Progression Rules')
                    else:
                        sim_info.story_progression_tracker.can_add_arc(self._required_story_progression_arc) or results.remove(result)
                        self.gsi_add_rejected_sim_info(sim_info, 'Cannot seed arc on Sim.')
                        if self._sim_gsi_logging_data is not None:
                            sim_filter_handlers.archive_filter_request(sim_info, (self._sim_gsi_logging_data), rejected=True, reason='Cannot seed arc on Sim.')

        return results

    def _calculate_sim_filter_score(self, sim_info, filter_terms, start_time=None, end_time=None, tag=FilterTermTag.NO_TAG, **kwargs):
        total_result = FilterResult(sim_info=sim_info, tag=tag)
        start_time_ticks = start_time.absolute_ticks() if start_time is not None else None
        end_time_ticks = end_time.absolute_ticks() if end_time is not None else None
        for filter_term in filter_terms:
            result = (filter_term.calculate_score)(sim_info, start_time_ticks=start_time_ticks, end_time_ticks=end_time_ticks, **kwargs)
            result.score = max(result.score, filter_term.minimum_filter_score)
            if self._sim_gsi_logging_data is not None:
                self._sim_gsi_logging_data.add_filter(str(filter_term), result.score)
            total_result.combine_with_other_filter_result(result)
            if total_result.score == 0:
                self.gsi_add_rejected_sim_info(sim_info, '0 score', filter_term)
                if self._sim_gsi_logging_data is not None:
                    sim_filter_handlers.archive_filter_request((result.sim_info), (self._sim_gsi_logging_data), rejected=True, reason='0 Score')
                break

        return total_result

    def _find_sims_matching_filter(self, constrained_sim_ids=None, **kwargs):
        filter_terms = self._sim_filter.get_filter_terms()
        if self._additional_filter_terms:
            filter_terms += self._additional_filter_terms
        sim_info_manager = services.sim_info_manager()
        results = []
        sim_ids = constrained_sim_ids if constrained_sim_ids is not None else sim_info_manager.keys()
        for sim_id in sim_ids:
            sim_info = sim_info_manager.get(sim_id)
            if sim_info is None:
                continue
            result = (self._calculate_sim_filter_score)(sim_info, filter_terms, **kwargs)
            if result.score > 0:
                results.append(result)

        if self._sim_filter.use_weighted_random:
            if len(results) > filters.tunable.TunableSimFilter.TOP_NUMBER_OF_SIMS_TO_LOOK_AT:
                shuffle(results)
        return results


class _MatchingFilterRequest(_SimFilterRequest):

    def __init__(self, number_of_sims_to_find=1, continue_if_constraints_fail=False, conform_if_constraints_fail=False, zone_id=None, allow_instanced_sims=False, optional=True, gsi_source_fn=None, **kwargs):
        (super().__init__)(**kwargs)
        self._continue_if_constraints_fail = continue_if_constraints_fail
        self._conform_if_constraints_fail = conform_if_constraints_fail
        self._number_of_sims_to_find = number_of_sims_to_find
        self._filter_results = []
        self._zone_id = zone_id
        self._allow_instanced_sims = allow_instanced_sims
        self.optional = optional
        self._gsi_source_fn = gsi_source_fn

    def _select_sims_from_results--- This code section failed: ---

 L. 376         0  BUILD_LIST_0          0 
                2  LOAD_FAST                'self'
                4  STORE_ATTR               _filter_results

 L. 377         6  BUILD_LIST_0          0 
                8  LOAD_FAST                'self'
               10  STORE_ATTR               _filter_results_info

 L. 378        12  LOAD_GLOBAL              services
               14  LOAD_METHOD              sim_filter_service
               16  CALL_METHOD_0         0  '0 positional arguments'
               18  LOAD_METHOD              get_global_blacklist
               20  CALL_METHOD_0         0  '0 positional arguments'
               22  STORE_FAST               'global_blacklist'

 L. 379        24  SETUP_LOOP          138  'to 138'
               26  LOAD_GLOBAL              tuple
               28  LOAD_FAST                'results'
               30  CALL_FUNCTION_1       1  '1 positional argument'
               32  GET_ITER         
             34_0  COME_FROM           122  '122'
             34_1  COME_FROM           108  '108'
             34_2  COME_FROM            92  '92'
               34  FOR_ITER            136  'to 136'
               36  STORE_FAST               'result'

 L. 380        38  LOAD_FAST                'result'
               40  LOAD_ATTR                sim_info
               42  STORE_FAST               'sim_info'

 L. 382        44  LOAD_FAST                'self'
               46  LOAD_ATTR                _allow_instanced_sims
               48  POP_JUMP_IF_TRUE     62  'to 62'
               50  LOAD_FAST                'sim_info'
               52  LOAD_ATTR                is_instanced
               54  LOAD_GLOBAL              ALL_HIDDEN_REASONS
               56  LOAD_CONST               ('allow_hidden_flags',)
               58  CALL_FUNCTION_KW_1     1  '1 total positional and keyword args'
               60  POP_JUMP_IF_TRUE    124  'to 124'
             62_0  COME_FROM            48  '48'

 L. 383        62  LOAD_FAST                'sim_info'
               64  LOAD_ATTR                id
               66  LOAD_FAST                'self'
               68  LOAD_ATTR                _blacklist_sim_ids
               70  COMPARE_OP               in
               72  POP_JUMP_IF_TRUE    124  'to 124'

 L. 384        74  LOAD_FAST                'sim_info'
               76  LOAD_ATTR                id
               78  LOAD_FAST                'global_blacklist'
               80  COMPARE_OP               in
               82  POP_JUMP_IF_TRUE    124  'to 124'

 L. 385        84  LOAD_FAST                'self'
               86  LOAD_ATTR                _required_story_progression_arc
               88  LOAD_CONST               None
               90  COMPARE_OP               is-not
               92  POP_JUMP_IF_FALSE    34  'to 34'

 L. 386        94  LOAD_FAST                'sim_info'
               96  LOAD_ATTR                household
               98  LOAD_ATTR                story_progression_rule_set
              100  LOAD_METHOD              verify
              102  LOAD_FAST                'self'
              104  LOAD_ATTR                _required_story_progression_arc
              106  CALL_METHOD_1         1  '1 positional argument'
              108  POP_JUMP_IF_TRUE     34  'to 34'

 L. 387       110  LOAD_FAST                'sim_info'
              112  LOAD_ATTR                story_progression_tracker
              114  LOAD_METHOD              can_add_arc
              116  LOAD_FAST                'self'
              118  LOAD_ATTR                _required_story_progression_arc
              120  CALL_METHOD_1         1  '1 positional argument'
              122  POP_JUMP_IF_TRUE     34  'to 34'
            124_0  COME_FROM            82  '82'
            124_1  COME_FROM            72  '72'
            124_2  COME_FROM            60  '60'

 L. 388       124  LOAD_FAST                'results'
              126  LOAD_METHOD              remove
              128  LOAD_FAST                'result'
              130  CALL_METHOD_1         1  '1 positional argument'
              132  POP_TOP          
              134  JUMP_BACK            34  'to 34'
              136  POP_BLOCK        
            138_0  COME_FROM_LOOP       24  '24'

 L. 390       138  LOAD_GLOBAL              sorted
              140  LOAD_FAST                'results'
              142  LOAD_LAMBDA              '<code_object <lambda>>'
              144  LOAD_STR                 '_MatchingFilterRequest._select_sims_from_results.<locals>.<lambda>'
              146  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              148  LOAD_CONST               True
              150  LOAD_CONST               ('key', 'reverse')
              152  CALL_FUNCTION_KW_3     3  '3 total positional and keyword args'
              154  STORE_FAST               'sorted_results'

 L. 391       156  LOAD_FAST                'self'
              158  LOAD_ATTR                _sim_filter
              160  LOAD_ATTR                use_weighted_random
          162_164  POP_JUMP_IF_FALSE   440  'to 440'

 L. 394       166  LOAD_GLOBAL              filters
              168  LOAD_ATTR                tunable
              170  LOAD_ATTR                TunableSimFilter
              172  LOAD_ATTR                TOP_NUMBER_OF_SIMS_TO_LOOK_AT
              174  STORE_FAST               'index'

 L. 395       176  LOAD_LISTCOMP            '<code_object <listcomp>>'
              178  LOAD_STR                 '_MatchingFilterRequest._select_sims_from_results.<locals>.<listcomp>'
              180  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              182  LOAD_FAST                'sorted_results'
              184  LOAD_CONST               None
              186  LOAD_FAST                'index'
              188  BUILD_SLICE_2         2 
              190  BINARY_SUBSCR    
              192  GET_ITER         
              194  CALL_FUNCTION_1       1  '1 positional argument'
              196  STORE_FAST               'randomization_group'

 L. 397       198  SETUP_LOOP          336  'to 336'
              200  LOAD_FAST                'index'
              202  LOAD_GLOBAL              len
              204  LOAD_FAST                'sorted_results'
              206  CALL_FUNCTION_1       1  '1 positional argument'
              208  COMPARE_OP               <
          210_212  POP_JUMP_IF_FALSE   334  'to 334'
              214  LOAD_GLOBAL              len
              216  LOAD_FAST                'self'
              218  LOAD_ATTR                _filter_results
              220  CALL_FUNCTION_1       1  '1 positional argument'
              222  LOAD_FAST                'sims_to_spawn'
              224  COMPARE_OP               <
          226_228  POP_JUMP_IF_FALSE   334  'to 334'

 L. 399       230  LOAD_GLOBAL              random
              232  LOAD_METHOD              pop_weighted
              234  LOAD_FAST                'randomization_group'
              236  CALL_METHOD_1         1  '1 positional argument'
              238  STORE_FAST               'random_choice'

 L. 402       240  LOAD_FAST                'index'
              242  LOAD_GLOBAL              len
              244  LOAD_FAST                'sorted_results'
              246  CALL_FUNCTION_1       1  '1 positional argument'
              248  COMPARE_OP               <
          250_252  POP_JUMP_IF_FALSE   286  'to 286'

 L. 403       254  LOAD_FAST                'randomization_group'
              256  LOAD_METHOD              append
              258  LOAD_FAST                'sorted_results'
              260  LOAD_FAST                'index'
              262  BINARY_SUBSCR    
              264  LOAD_ATTR                score
              266  LOAD_FAST                'sorted_results'
              268  LOAD_FAST                'index'
              270  BINARY_SUBSCR    
              272  BUILD_TUPLE_2         2 
              274  CALL_METHOD_1         1  '1 positional argument'
              276  POP_TOP          

 L. 404       278  LOAD_FAST                'index'
              280  LOAD_CONST               1
              282  INPLACE_ADD      
              284  STORE_FAST               'index'
            286_0  COME_FROM           250  '250'

 L. 406       286  LOAD_GLOBAL              logger
              288  LOAD_METHOD              info
              290  LOAD_STR                 'Sim ID matching request {0}'
              292  LOAD_FAST                'random_choice'
              294  CALL_METHOD_2         2  '2 positional arguments'
              296  POP_TOP          

 L. 407       298  LOAD_FAST                'self'
              300  LOAD_ATTR                _filter_results
              302  LOAD_METHOD              append
              304  LOAD_FAST                'random_choice'
              306  CALL_METHOD_1         1  '1 positional argument'
              308  POP_TOP          

 L. 408       310  LOAD_FAST                'self'
              312  LOAD_ATTR                _filter_results_info
              314  LOAD_METHOD              append
              316  LOAD_FAST                'random_choice'
              318  LOAD_ATTR                sim_info
              320  CALL_METHOD_1         1  '1 positional argument'
              322  POP_TOP          

 L. 410       324  LOAD_FAST                'index'
              326  LOAD_CONST               1
              328  INPLACE_ADD      
              330  STORE_FAST               'index'
              332  JUMP_BACK           200  'to 200'
            334_0  COME_FROM           226  '226'
            334_1  COME_FROM           210  '210'
              334  POP_BLOCK        
            336_0  COME_FROM_LOOP      198  '198'

 L. 414       336  LOAD_GLOBAL              len
              338  LOAD_FAST                'self'
              340  LOAD_ATTR                _filter_results
              342  CALL_FUNCTION_1       1  '1 positional argument'
              344  LOAD_FAST                'sims_to_spawn'
              346  COMPARE_OP               <
          348_350  POP_JUMP_IF_FALSE   514  'to 514'
              352  LOAD_FAST                'randomization_group'
          354_356  POP_JUMP_IF_FALSE   514  'to 514'

 L. 415       358  SETUP_LOOP          514  'to 514'
              360  LOAD_FAST                'randomization_group'
          362_364  POP_JUMP_IF_FALSE   436  'to 436'
              366  LOAD_GLOBAL              len
              368  LOAD_FAST                'self'
              370  LOAD_ATTR                _filter_results
              372  CALL_FUNCTION_1       1  '1 positional argument'
              374  LOAD_FAST                'self'
              376  LOAD_ATTR                _number_of_sims_to_find
              378  COMPARE_OP               <
          380_382  POP_JUMP_IF_FALSE   436  'to 436'

 L. 417       384  LOAD_GLOBAL              random
              386  LOAD_METHOD              pop_weighted
              388  LOAD_FAST                'randomization_group'
              390  CALL_METHOD_1         1  '1 positional argument'
              392  STORE_FAST               'random_choice'

 L. 419       394  LOAD_GLOBAL              logger
              396  LOAD_METHOD              info
              398  LOAD_STR                 'Sim ID matching request {0}'
              400  LOAD_FAST                'random_choice'
              402  CALL_METHOD_2         2  '2 positional arguments'
              404  POP_TOP          

 L. 420       406  LOAD_FAST                'self'
              408  LOAD_ATTR                _filter_results
              410  LOAD_METHOD              append
              412  LOAD_FAST                'random_choice'
              414  CALL_METHOD_1         1  '1 positional argument'
              416  POP_TOP          

 L. 421       418  LOAD_FAST                'self'
              420  LOAD_ATTR                _filter_results_info
              422  LOAD_METHOD              append
              424  LOAD_FAST                'random_choice'
              426  LOAD_ATTR                sim_info
              428  CALL_METHOD_1         1  '1 positional argument'
              430  POP_TOP          
          432_434  JUMP_BACK           360  'to 360'
            436_0  COME_FROM           380  '380'
            436_1  COME_FROM           362  '362'
              436  POP_BLOCK        
              438  JUMP_FORWARD        514  'to 514'
            440_0  COME_FROM           162  '162'

 L. 425       440  SETUP_LOOP          514  'to 514'
              442  LOAD_FAST                'sorted_results'
              444  GET_ITER         
              446  FOR_ITER            512  'to 512'
              448  STORE_FAST               'result'

 L. 428       450  LOAD_GLOBAL              len
              452  LOAD_FAST                'self'
              454  LOAD_ATTR                _filter_results
              456  CALL_FUNCTION_1       1  '1 positional argument'
              458  LOAD_FAST                'sims_to_spawn'
              460  COMPARE_OP               ==
          462_464  POP_JUMP_IF_FALSE   468  'to 468'

 L. 429       466  BREAK_LOOP       
            468_0  COME_FROM           462  '462'

 L. 431       468  LOAD_GLOBAL              logger
              470  LOAD_METHOD              info
              472  LOAD_STR                 'Sim ID matching request {0}'
              474  LOAD_FAST                'result'
              476  LOAD_ATTR                sim_info
              478  CALL_METHOD_2         2  '2 positional arguments'
              480  POP_TOP          

 L. 432       482  LOAD_FAST                'self'
              484  LOAD_ATTR                _filter_results
              486  LOAD_METHOD              append
              488  LOAD_FAST                'result'
              490  CALL_METHOD_1         1  '1 positional argument'
              492  POP_TOP          

 L. 433       494  LOAD_FAST                'self'
              496  LOAD_ATTR                _filter_results_info
              498  LOAD_METHOD              append
              500  LOAD_FAST                'result'
              502  LOAD_ATTR                sim_info
              504  CALL_METHOD_1         1  '1 positional argument'
              506  POP_TOP          
          508_510  JUMP_BACK           446  'to 446'
              512  POP_BLOCK        
            514_0  COME_FROM_LOOP      440  '440'
            514_1  COME_FROM           438  '438'
            514_2  COME_FROM_LOOP      358  '358'
            514_3  COME_FROM           354  '354'
            514_4  COME_FROM           348  '348'

 L. 435       514  LOAD_FAST                'self'
              516  LOAD_ATTR                _sim_gsi_logging_data
              518  LOAD_CONST               None
              520  COMPARE_OP               is-not
          522_524  POP_JUMP_IF_FALSE   566  'to 566'

 L. 436       526  SETUP_LOOP          566  'to 566'
              528  LOAD_FAST                'self'
              530  LOAD_ATTR                _filter_results
              532  GET_ITER         
              534  FOR_ITER            564  'to 564'
              536  STORE_FAST               'result'

 L. 437       538  LOAD_GLOBAL              sim_filter_handlers
              540  LOAD_ATTR                archive_filter_request
              542  LOAD_FAST                'result'
              544  LOAD_ATTR                sim_info
              546  LOAD_FAST                'self'
              548  LOAD_ATTR                _sim_gsi_logging_data
              550  LOAD_CONST               False
              552  LOAD_STR                 'Score > 0 and chosen for spawning'
              554  LOAD_CONST               ('rejected', 'reason')
              556  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              558  POP_TOP          
          560_562  JUMP_BACK           534  'to 534'
              564  POP_BLOCK        
            566_0  COME_FROM_LOOP      526  '526'
            566_1  COME_FROM           522  '522'

 L. 439       566  LOAD_FAST                'self'
              568  LOAD_ATTR                _filter_results
              570  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `POP_BLOCK' instruction at offset 136

    def _run_filter_query(self):
        results = None
        constrained_sim_ids = self._get_constrained_sims()
        if constrained_sim_ids is not None:
            results = self._find_sims_matching_filter(constrained_sim_ids=constrained_sim_ids, start_time=(self._start_time),
              end_time=(self._end_time),
              household_id=(self._household_id),
              requesting_sim_info=(self._requesting_sim_info),
              club=(self._club),
              tag=(self.tag))
            if not results:
                if not self._continue_if_constraints_fail:
                    return self._filter_results
            else:
                self._select_sims_from_results(results, self._number_of_sims_to_find)
                return len(self._filter_results) == self._number_of_sims_to_find or self._continue_if_constraints_fail or self._filter_results
        results = self._find_sims_matching_filter(start_time=(self._start_time), end_time=(self._end_time),
          household_id=(self._household_id),
          requesting_sim_info=(self._requesting_sim_info),
          club=(self._club),
          tag=(self.tag))
        if results:
            self._filter_results.extend(self._select_sims_from_results(results, self._number_of_sims_to_find - len(self._filter_results)))

    def _create_sim_info(self):
        blacklist_sim_ids = tuple(self._blacklist_sim_ids)
        blacklist_sim_ids += tuple((result.sim_info.sim_id for result in self._filter_results))
        if not self._sim_filter.repurpose_game_breaker:
            blacklist_sim_ids += tuple((sim.sim_info.sim_id for sim in services.sim_info_manager().instanced_sims_gen(allow_hidden_flags=ALL_HIDDEN_REASONS)))
        create_result = self._sim_filter.create_sim_info(zone_id=(self._zone_id), household_id=(self._household_id),
          requesting_sim_info=(self._requesting_sim_info),
          blacklist_sim_ids=blacklist_sim_ids,
          start_time=(self._start_time),
          end_time=(self._end_time),
          additional_filter_terms=(self._additional_filter_terms),
          sim_constraints=(self._sim_constraints))
        if create_result:
            fake_filter_result = FilterResult(sim_info=(create_result.sim_info), tag=(self.tag))
            self._filter_results.append(fake_filter_result)
            logger.info('Created Sim ID to match request {0}', create_result.sim_info.id)
            if self._gsi_logging_data is not None:
                self._gsi_logging_data.add_created_household((create_result.sim_info.household), was_successful=True)
            if self._sim_gsi_logging_data is not None:
                sim_filter_handlers.archive_filter_request((create_result.sim_info), (self._sim_gsi_logging_data), rejected=False, reason='Created to match the filter')
            return True
        if self._gsi_logging_data is not None:
            if create_result.sim_info is not None:
                self._gsi_logging_data.add_created_household((create_result.sim_info.household), was_successful=False)
        return False

    def _create_sim_infos(self):
        while len(self._filter_results) < self._number_of_sims_to_find and not self._create_sim_info():
            break

    def _should_try_conform(self):
        return not self._sim_constraints or self._continue_if_constraints_fail or self._conform_if_constraints_fail

    def run(self):
        if self._state == SimFilterRequestState.SETUP:
            self.gsi_start_logging('_MatchingFilterRequest', self._sim_filter, False, self._gsi_source_fn)
            self._run_filter_query()
            if not len(self._filter_results) == self._number_of_sims_to_find:
                self._state = self._should_try_conform() or SimFilterRequestState.FILLED_RESULTS
            else:
                self._state = SimFilterRequestState.RAN_QUERY
        else:
            if self._state == SimFilterRequestState.RAN_QUERY:
                self._state = SimFilterRequestState.SPAWNING_SIMS
                return
            if self._state == SimFilterRequestState.SPAWNING_SIMS:
                result = self._create_sim_info()
                if not result or len(self._filter_results) == self._number_of_sims_to_find:
                    self._state = SimFilterRequestState.FILLED_RESULTS
        if self._state == SimFilterRequestState.FILLED_RESULTS:
            self._callback(self._filter_results, self._callback_event_data)
            self._state = SimFilterRequestState.COMPLETE
            if self._gsi_logging_data is not None:
                self._gsi_logging_data.add_metadata(self._number_of_sims_to_find, self._allow_instanced_sims, self._club, self._blacklist_sim_ids, self.optional, self._required_story_progression_arc)
            self.gsi_archive_logging(self._filter_results)

    def run_without_yielding(self):
        self.gsi_start_logging('_MatchingFilterRequest', self._sim_filter, True, self._gsi_source_fn)
        self._run_filter_query()
        if self._should_try_conform():
            self._create_sim_infos()
        if self._gsi_logging_data is not None:
            self._gsi_logging_data.add_metadata(self._number_of_sims_to_find, self._allow_instanced_sims, self._club, self._blacklist_sim_ids, self.optional, self._required_story_progression_arc)
        self.gsi_archive_logging(self._filter_results)
        return self._filter_results


class _AggregateFilterRequest(_BaseSimFilterRequest):

    def __init__(self, aggregate_filter=None, filter_sims_with_matching_filter_request=True, gsi_source_fn=None, additional_filter_terms=(), **kwargs):
        (super().__init__)(**kwargs)
        self._aggregate_filter = aggregate_filter
        self._additional_filter_terms = additional_filter_terms
        self._filter_sims_with_matching_filter_request = filter_sims_with_matching_filter_request
        logger.assert_raise(aggregate_filter is not None, 'Filter is None in _AggregateFilterRequest.')
        self._leader_filter_request = None
        self._non_leader_filter_requests = []
        self._leader_sim_info = None
        self._filter_results = []
        self._gsi_source_fn = gsi_source_fn

    def run(self):
        if self._state == SimFilterRequestState.SETUP:
            self.gsi_start_logging('_AggregateFilterRequest', self._aggregate_filter, False, self._gsi_source_fn)
            self._create_leader()
            if self._leader_sim_info is None:
                self._state = SimFilterRequestState.COMPLETE
                self._callback([], self._callback_event_data)
                if self._gsi_logging_data is not None:
                    self._gsi_logging_data.add_metadata(None, None, None, self._blacklist_sim_ids, None, self._required_story_progression_arc)
                self.gsi_archive_logging(self._filter_results)
                return
            self._create_non_leader_filter_requests()
            self._state = SimFilterRequestState.SPAWNING_SIMS
            return
        if self._state == SimFilterRequestState.SPAWNING_SIMS:
            if self._non_leader_filter_requests:
                filter_to_run = self._non_leader_filter_requests.pop()
                result = self._run_sim_filter(filter_to_run)
                if result or filter_to_run.optional:
                    return
                self._filter_results.clear()
                self._state = SimFilterRequestState.FILLED_RESULTS
                return
            self._state = SimFilterRequestState.FILLED_RESULTS
        if self._state == SimFilterRequestState.FILLED_RESULTS:
            self._callback(self._filter_results, self._callback_event_data)
            self._state = SimFilterRequestState.COMPLETE
            if self._gsi_logging_data is not None:
                self._gsi_logging_data.add_metadata(None, None, None, self._blacklist_sim_ids, None, self._required_story_progression_arc)
            self.gsi_archive_logging(self._filter_results)

    def run_without_yielding(self):
        self.gsi_start_logging('_AggregateFilterRequest', self._aggregate_filter, True, self._gsi_source_fn)
        self._create_leader()
        if self._leader_sim_info is None:
            return []
        self._create_non_leader_filter_requests()
        for filter_to_run in self._non_leader_filter_requests:
            result = self._run_sim_filter(filter_to_run)
            if result or filter_to_run.optional:
                continue
            self._filter_results.clear()
            return self._filter_results

        if self._gsi_logging_data is not None:
            self._gsi_logging_data.add_metadata(None, None, None, self._blacklist_sim_ids, None, self._required_story_progression_arc)
        self.gsi_archive_logging(self._filter_results)
        return self._filter_results

    def _create_leader(self):
        self._create_leader_filter_request()
        filter_results = self._leader_filter_request.run_without_yielding()
        if not filter_results:
            return
        self._leader_sim_info = filter_results[0].sim_info
        self._filter_results.append(filter_results[0])
        self._blacklist_sim_ids.add(self._leader_sim_info.sim_id)

    def _create_leader_filter_request(self):
        if self._gsi_logging_data is not None:
            request_type = '_AggregateFilterRequest:_MatchingFilterRequest' if self._filter_sims_with_matching_filter_request else '_AggregateFilterRequest:_SimFilterRequest'
            sub_gsi_logging_data = gsi_handlers.sim_filter_service_handlers.SimFilterServiceGSILoggingData(request_type, 'LeaderFilter:{}'.format(self._aggregate_filter.leader_filter), self._gsi_logging_data.yielding, self._gsi_logging_data.gsi_source_fn)
        else:
            sub_gsi_logging_data = None
        if self._filter_sims_with_matching_filter_request:
            self._leader_filter_request = _MatchingFilterRequest(sim_filter=(self._aggregate_filter.leader_filter.filter), blacklist_sim_ids=(self._blacklist_sim_ids),
              required_story_progression_arc=(self._required_story_progression_arc),
              gsi_logging_data=sub_gsi_logging_data,
              tag=(self._aggregate_filter.leader_filter.tag),
              additional_filter_terms=(self._additional_filter_terms))
        else:
            self._leader_filter_request = _SimFilterRequest(sim_filter=(self._aggregate_filter.leader_filter.filter), blacklist_sim_ids=(self._blacklist_sim_ids),
              required_story_progression_arc=(self._required_story_progression_arc),
              gsi_logging_data=sub_gsi_logging_data,
              tag=(self._aggregate_filter.leader_filter.tag),
              additional_filter_terms=(self._additional_filter_terms))

    def _create_non_leader_filter_requests(self):
        if self._filter_sims_with_matching_filter_request:
            for sim_filter in self._aggregate_filter.filters:
                sub_gsi_logging_data = None
                if self._gsi_logging_data is not None:
                    sub_gsi_logging_data = gsi_handlers.sim_filter_service_handlers.SimFilterServiceGSILoggingData('_AggregateFilterRequest:_MatchingFilterRequest', 'NonLeaderFilter:{}'.format(sim_filter.filter), self._gsi_logging_data.yielding, self._gsi_logging_data.gsi_source_fn)
                self._non_leader_filter_requests.append(_MatchingFilterRequest(sim_filter=(sim_filter.filter), blacklist_sim_ids=(self._blacklist_sim_ids),
                  required_story_progression_arc=(self._required_story_progression_arc),
                  requesting_sim_info=(self._leader_sim_info),
                  gsi_logging_data=sub_gsi_logging_data,
                  tag=(sim_filter.tag),
                  optional=(sim_filter.optional)))

        else:
            for sim_filter in self._aggregate_filter.filters:
                sub_gsi_logging_data = None
                if self._gsi_logging_data is not None:
                    sub_gsi_logging_data = gsi_handlers.sim_filter_service_handlers.SimFilterServiceGSILoggingData('_AggregateFilterRequest:_SimFilterRequest', 'NonLeaderFilter:{}'.format(sim_filter.filter), self._gsi_logging_data.yielding)
                self._non_leader_filter_requests.append(_SimFilterRequest(sim_filter=(sim_filter.filter), blacklist_sim_ids=(self._blacklist_sim_ids),
                  required_story_progression_arc=(self._required_story_progression_arc),
                  requesting_sim_info=(self._leader_sim_info),
                  gsi_logging_data=sub_gsi_logging_data,
                  tag=(sim_filter.tag),
                  optional=(sim_filter.optional)))

    def _run_sim_filter(self, filter_to_run):
        filter_results = filter_to_run.run_without_yielding()
        if filter_results:
            for result in filter_results:
                self._filter_results.append(result)
                self._blacklist_sim_ids.add(result.sim_info.sim_id)

        return bool(filter_results)


class SimFilterService(Service):

    def __init__(self):
        self._filter_requests = []
        self._global_blacklist = {}

    def update(self):
        try:
            if self._filter_requests:
                current_request = self._filter_requests[0]
                current_request.run()
                if current_request.is_complete:
                    del self._filter_requests[0]
        except Exception:
            logger.exception('Exception while updating the sim filter service..')

    @property
    def is_processing_request(self):
        if not self._filter_requests:
            return False
        current_request = self._filter_requests[0]
        if current_request is not None:
            return not current_request.is_complete
        return False

    def add_sim_id_to_global_blacklist(self, sim_id, reason):
        if sim_id not in self._global_blacklist:
            self._global_blacklist[sim_id] = []
        self._global_blacklist[sim_id].append(reason)

    def remove_sim_id_from_global_blacklist(self, sim_id, reason):
        reasons = self._global_blacklist.get(sim_id)
        if reasons is None:
            logger.error('Trying to remove sim id {} to global blacklist without adding it first.', sim_id,
              owner='jjacobson')
            return
        if reason not in reasons:
            logger.error('Trying to remove reason {} from global blacklist with sim id {} without adding it first.', reason,
              sim_id,
              owner='jjacobson')
            return
        self._global_blacklist[sim_id].remove(reason)
        if not self._global_blacklist[sim_id]:
            del self._global_blacklist[sim_id]

    def get_global_blacklist(self):
        return set(self._global_blacklist.keys())

    def get_global_blacklist_reason(self, sim_id):
        return self._global_blacklist.get(sim_id, [])

    def submit_matching_filter(self, number_of_sims_to_find=1, sim_filter=None, callback=None, callback_event_data=None, sim_constraints=None, requesting_sim_info=None, blacklist_sim_ids=EMPTY_SET, required_story_progression_arc=None, continue_if_constraints_fail=False, conform_if_constraints_fail=False, allow_yielding=True, start_time=None, end_time=None, household_id=None, zone_id=None, club=None, allow_instanced_sims=False, additional_filter_terms=(), gsi_source_fn=None):
        request = None
        if sim_filter is not None:
            if sim_filter.is_aggregate_filter():
                request = _AggregateFilterRequest(aggregate_filter=sim_filter, callback=callback,
                  callback_event_data=callback_event_data,
                  blacklist_sim_ids=blacklist_sim_ids,
                  required_story_progression_arc=required_story_progression_arc,
                  filter_sims_with_matching_filter_request=True,
                  additional_filter_terms=additional_filter_terms,
                  gsi_source_fn=gsi_source_fn)
            else:
                request = _MatchingFilterRequest(number_of_sims_to_find=number_of_sims_to_find, continue_if_constraints_fail=continue_if_constraints_fail,
                  conform_if_constraints_fail=conform_if_constraints_fail,
                  sim_filter=sim_filter,
                  callback=callback,
                  callback_event_data=callback_event_data,
                  requesting_sim_info=requesting_sim_info,
                  sim_constraints=sim_constraints,
                  blacklist_sim_ids=blacklist_sim_ids,
                  required_story_progression_arc=required_story_progression_arc,
                  start_time=start_time,
                  end_time=end_time,
                  household_id=household_id,
                  zone_id=zone_id,
                  club=club,
                  allow_instanced_sims=allow_instanced_sims,
                  additional_filter_terms=additional_filter_terms,
                  gsi_source_fn=gsi_source_fn)
            if allow_yielding:
                self._add_filter_request(request)
        else:
            return request.run_without_yielding()

    def submit_filter(self, sim_filter, callback, callback_event_data=None, sim_constraints=None, requesting_sim_info=None, blacklist_sim_ids=EMPTY_SET, required_story_progression_arc=None, allow_yielding=True, start_time=None, end_time=None, household_id=None, club=None, additional_filter_terms=(), gsi_source_fn=None, include_rabbithole_sims=False, include_missing_pets=False):
        request = None
        if sim_filter is not None:
            if sim_filter.is_aggregate_filter():
                request = _AggregateFilterRequest(aggregate_filter=sim_filter, callback=callback,
                  callback_event_data=callback_event_data,
                  blacklist_sim_ids=blacklist_sim_ids,
                  required_story_progression_arc=required_story_progression_arc,
                  filter_sims_with_matching_filter_request=False,
                  additional_filter_terms=additional_filter_terms,
                  gsi_source_fn=gsi_source_fn)
            else:
                request = _SimFilterRequest(sim_filter=sim_filter, callback=callback,
                  callback_event_data=callback_event_data,
                  requesting_sim_info=requesting_sim_info,
                  sim_constraints=sim_constraints,
                  blacklist_sim_ids=blacklist_sim_ids,
                  required_story_progression_arc=required_story_progression_arc,
                  start_time=start_time,
                  end_time=end_time,
                  household_id=household_id,
                  club=club,
                  additional_filter_terms=additional_filter_terms,
                  gsi_source_fn=gsi_source_fn,
                  include_rabbithole_sims=include_rabbithole_sims,
                  include_missing_pets=include_missing_pets)
            if allow_yielding:
                self._add_filter_request(request)
        else:
            return request.run_without_yielding()

    def _add_filter_request(self, filter_request):
        self._filter_requests.append(filter_request)

    def does_sim_match_filter(self, sim_id, sim_filter=None, requesting_sim_info=None, start_time=None, end_time=None, household_id=None, additional_filter_terms=(), gsi_source_fn=None):
        result = self.submit_filter(sim_filter, None, allow_yielding=False, sim_constraints=[
         sim_id],
          requesting_sim_info=requesting_sim_info,
          start_time=start_time,
          end_time=end_time,
          household_id=household_id,
          additional_filter_terms=additional_filter_terms,
          gsi_source_fn=gsi_source_fn)
        if result:
            return True
        return False