# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\arb_accumulator.py
# Compiled at: 2023-03-07 20:30:20
# Size of source mod 2**32: 22477 bytes
from weakref import WeakKeyDictionary
import time
from animation.animation_sleep_element import AnimationSleepElement
from animation.animation_utils import get_actors_for_arb_sequence
from animation.arb_element import ArbElement, distribute_arb_element
from sims4.tuning.tunable import TunableRealSecond, Tunable
import animation.arb, distributor.system, element_utils, elements, services, sims4.callback_utils, sims4.log, sims4.service_manager
logger = sims4.log.Logger('ArbAccumulator')
dump_logger = sims4.log.LoggerClass('ArbAccumulator')

def _get_actors_for_arb_element_sequence(arb_element_sequence, main_timeline_only=False):
    all_actors = set()
    for arb_element in arb_element_sequence:
        for actor in arb_element._actors(main_timeline_only):
            if actor.is_sim:
                all_actors.add(actor)

    return all_actors


def with_skippable_animation_time(actors, sequence=None):

    def _with_skippable_animation_time(timeline):
        then = time.monotonic()
        yield from element_utils.run_child(timeline, sequence)
        now = time.monotonic()
        duration = now - then
        arb_accumulator = services.current_zone().arb_accumulator_service
        for actor in actors:
            time_debt = arb_accumulator.get_time_debt((actor,))
            new_time_debt = max(0, time_debt - duration)
            arb_accumulator.set_time_debt((actor,), new_time_debt)

        if False:
            yield None

    return element_utils.build_element(_with_skippable_animation_time)


class ArbSequenceElement(elements.SubclassableGeneratorElement):

    def __init__(self, arb_element_sequence, *args, animate_instantly=False, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._arb_element_sequence = arb_element_sequence
        self._current_arb_element = None
        self._animate_instantly = animate_instantly

    def _run_gen--- This code section failed: ---

 L.  77         0  LOAD_FAST                'self'
                2  LOAD_ATTR                _arb_element_sequence
                4  POP_JUMP_IF_TRUE     10  'to 10'

 L.  78         6  LOAD_CONST               True
                8  RETURN_VALUE     
             10_0  COME_FROM             4  '4'

 L.  80        10  LOAD_CONST               0
               12  STORE_FAST               'duration_must_run'

 L.  82        14  SETUP_LOOP           70  'to 70'
               16  LOAD_FAST                'self'
               18  LOAD_ATTR                _arb_element_sequence
               20  GET_ITER         
               22  FOR_ITER             68  'to 68'
               24  STORE_FAST               'arb_element'

 L.  83        26  LOAD_FAST                'arb_element'
               28  LOAD_ATTR                arb
               30  LOAD_METHOD              get_timing
               32  CALL_METHOD_0         0  '0 positional arguments'
               34  UNPACK_SEQUENCE_3     3 
               36  STORE_FAST               'arb_duration_total'
               38  STORE_FAST               'arb_duration_must_run'
               40  STORE_FAST               'arb_duration_repeat'

 L.  84        42  LOAD_FAST                'arb_duration_total'
               44  LOAD_FAST                'arb_duration_must_run'
               46  BINARY_SUBTRACT  
               48  STORE_FAST               'arb_duration_interrupt'

 L.  87        50  LOAD_FAST                'duration_must_run'
               52  LOAD_FAST                'arb_duration_must_run'
               54  INPLACE_ADD      
               56  STORE_FAST               'duration_must_run'

 L.  91        58  LOAD_FAST                'arb_element'
               60  LOAD_METHOD              distribute
               62  CALL_METHOD_0         0  '0 positional arguments'
               64  POP_TOP          
               66  JUMP_BACK            22  'to 22'
               68  POP_BLOCK        
             70_0  COME_FROM_LOOP       14  '14'

 L.  94        70  LOAD_FAST                'arb_duration_interrupt'
               72  STORE_FAST               'duration_interrupt'

 L.  96        74  LOAD_FAST                'arb_duration_repeat'
               76  STORE_FAST               'duration_repeat'

 L.  99        78  LOAD_GLOBAL              ArbAccumulatorService
               80  LOAD_ATTR                MAXIMUM_TIME_DEBT
               82  LOAD_CONST               0
               84  COMPARE_OP               >
               86  POP_JUMP_IF_FALSE   250  'to 250'

 L. 102        88  LOAD_GLOBAL              _get_actors_for_arb_element_sequence
               90  LOAD_FAST                'self'
               92  LOAD_ATTR                _arb_element_sequence
               94  LOAD_CONST               True
               96  LOAD_CONST               ('main_timeline_only',)
               98  CALL_FUNCTION_KW_2     2  '2 total positional and keyword args'
              100  STORE_FAST               'actors'

 L. 103       102  LOAD_GLOBAL              services
              104  LOAD_METHOD              current_zone
              106  CALL_METHOD_0         0  '0 positional arguments'
              108  LOAD_ATTR                arb_accumulator_service
              110  STORE_FAST               'arb_accumulator'

 L. 104       112  LOAD_FAST                'arb_accumulator'
              114  LOAD_METHOD              get_time_debt
              116  LOAD_FAST                'actors'
              118  CALL_METHOD_1         1  '1 positional argument'
              120  STORE_FAST               'time_debt_max'

 L. 107       122  LOAD_FAST                'arb_accumulator'
              124  LOAD_METHOD              get_shave_time_given_duration_and_debt
              126  LOAD_FAST                'duration_must_run'

 L. 108       128  LOAD_FAST                'time_debt_max'
              130  CALL_METHOD_2         2  '2 positional arguments'
              132  STORE_FAST               'shave_time_actual'

 L. 111       134  LOAD_FAST                'duration_must_run'
              136  LOAD_FAST                'shave_time_actual'
              138  INPLACE_SUBTRACT 
              140  STORE_FAST               'duration_must_run'

 L. 113       142  LOAD_FAST                'shave_time_actual'
              144  POP_JUMP_IF_FALSE   196  'to 196'

 L. 114       146  SETUP_LOOP          250  'to 250'
              148  LOAD_FAST                'actors'
              150  GET_ITER         
              152  FOR_ITER            192  'to 192'
              154  STORE_FAST               'actor'

 L. 117       156  LOAD_FAST                'arb_accumulator'
              158  LOAD_METHOD              get_time_debt
              160  LOAD_FAST                'actor'
              162  BUILD_TUPLE_1         1 
              164  CALL_METHOD_1         1  '1 positional argument'
              166  STORE_FAST               'time_debt'

 L. 118       168  LOAD_FAST                'time_debt'
              170  LOAD_FAST                'shave_time_actual'
              172  INPLACE_ADD      
              174  STORE_FAST               'time_debt'

 L. 119       176  LOAD_FAST                'arb_accumulator'
              178  LOAD_METHOD              set_time_debt
              180  LOAD_FAST                'actor'
              182  BUILD_TUPLE_1         1 
              184  LOAD_FAST                'time_debt'
              186  CALL_METHOD_2         2  '2 positional arguments'
              188  POP_TOP          
              190  JUMP_BACK           152  'to 152'
              192  POP_BLOCK        
              194  JUMP_FORWARD        250  'to 250'
            196_0  COME_FROM           144  '144'

 L. 125       196  LOAD_FAST                'self'
              198  LOAD_ATTR                _arb_element_sequence
              200  LOAD_CONST               -1
              202  BINARY_SUBSCR    
              204  LOAD_ATTR                arb
              206  STORE_DEREF              'last_arb'

 L. 126       208  LOAD_GLOBAL              all
              210  LOAD_CLOSURE             'last_arb'
              212  BUILD_TUPLE_1         1 
              214  LOAD_GENEXPR             '<code_object <genexpr>>'
              216  LOAD_STR                 'ArbSequenceElement._run_gen.<locals>.<genexpr>'
              218  MAKE_FUNCTION_8          'closure'
              220  LOAD_FAST                'actors'
              222  GET_ITER         
              224  CALL_FUNCTION_1       1  '1 positional argument'
              226  CALL_FUNCTION_1       1  '1 positional argument'
              228  POP_JUMP_IF_FALSE   250  'to 250'

 L. 127       230  LOAD_FAST                'duration_must_run'
              232  LOAD_FAST                'time_debt_max'
              234  INPLACE_ADD      
              236  STORE_FAST               'duration_must_run'

 L. 128       238  LOAD_FAST                'arb_accumulator'
              240  LOAD_METHOD              set_time_debt
              242  LOAD_FAST                'actors'
              244  LOAD_CONST               0
              246  CALL_METHOD_2         2  '2 positional arguments'
              248  POP_TOP          
            250_0  COME_FROM           228  '228'
            250_1  COME_FROM           194  '194'
            250_2  COME_FROM_LOOP      146  '146'
            250_3  COME_FROM            86  '86'

 L. 130       250  LOAD_GLOBAL              tuple
              252  LOAD_GENEXPR             '<code_object <genexpr>>'
              254  LOAD_STR                 'ArbSequenceElement._run_gen.<locals>.<genexpr>'
              256  MAKE_FUNCTION_0          'Neither defaults, keyword-only args, annotations, nor closures'
              258  LOAD_FAST                'self'
              260  LOAD_ATTR                _arb_element_sequence
              262  GET_ITER         
              264  CALL_FUNCTION_1       1  '1 positional argument'
              266  CALL_FUNCTION_1       1  '1 positional argument'
              268  STORE_FAST               'arbs'

 L. 131       270  LOAD_GLOBAL              AnimationSleepElement
              272  LOAD_FAST                'duration_must_run'
              274  LOAD_FAST                'duration_interrupt'
              276  LOAD_FAST                'duration_repeat'
              278  LOAD_FAST                'arbs'
              280  LOAD_CONST               ('arbs',)
              282  CALL_FUNCTION_KW_4     4  '4 total positional and keyword args'
              284  STORE_FAST               'animation_sleep_element'

 L. 133       286  LOAD_FAST                'self'
              288  LOAD_ATTR                _animate_instantly
          290_292  POP_JUMP_IF_TRUE    312  'to 312'

 L. 134       294  LOAD_GLOBAL              element_utils
              296  LOAD_METHOD              run_child
              298  LOAD_FAST                'timeline'
              300  LOAD_FAST                'animation_sleep_element'
              302  CALL_METHOD_2         2  '2 positional arguments'
              304  GET_YIELD_FROM_ITER
              306  LOAD_CONST               None
              308  YIELD_FROM       
              310  POP_TOP          
            312_0  COME_FROM           290  '290'

 L. 138       312  LOAD_FAST                'animation_sleep_element'
              314  LOAD_ATTR                optional_time_elapsed
              316  STORE_FAST               'optional_time_elapsed'

 L. 140       318  LOAD_GLOBAL              ArbAccumulatorService
              320  LOAD_ATTR                MAXIMUM_TIME_DEBT
              322  LOAD_CONST               0
              324  COMPARE_OP               >
          326_328  POP_JUMP_IF_FALSE   400  'to 400'

 L. 141       330  LOAD_FAST                'optional_time_elapsed'
              332  LOAD_CONST               0
              334  COMPARE_OP               >
          336_338  POP_JUMP_IF_FALSE   400  'to 400'

 L. 142       340  SETUP_LOOP          400  'to 400'
              342  LOAD_FAST                'actors'
              344  GET_ITER         
              346  FOR_ITER            398  'to 398'
              348  STORE_FAST               'actor'

 L. 143       350  LOAD_FAST                'arb_accumulator'
              352  LOAD_METHOD              get_time_debt
              354  LOAD_FAST                'actor'
              356  BUILD_TUPLE_1         1 
              358  CALL_METHOD_1         1  '1 positional argument'
              360  STORE_FAST               'time_debt'

 L. 144       362  LOAD_FAST                'time_debt'
              364  LOAD_FAST                'optional_time_elapsed'
              366  BINARY_SUBTRACT  
              368  STORE_FAST               'new_time_debt'

 L. 145       370  LOAD_GLOBAL              max
              372  LOAD_FAST                'new_time_debt'
              374  LOAD_CONST               0
              376  CALL_FUNCTION_2       2  '2 positional arguments'
              378  STORE_FAST               'new_time_debt'

 L. 146       380  LOAD_FAST                'arb_accumulator'
              382  LOAD_METHOD              set_time_debt
              384  LOAD_FAST                'actor'
              386  BUILD_TUPLE_1         1 
              388  LOAD_FAST                'new_time_debt'
              390  CALL_METHOD_2         2  '2 positional arguments'
              392  POP_TOP          
          394_396  JUMP_BACK           346  'to 346'
              398  POP_BLOCK        
            400_0  COME_FROM_LOOP      340  '340'
            400_1  COME_FROM           336  '336'
            400_2  COME_FROM           326  '326'

 L. 148       400  LOAD_CONST               True
              402  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 250_2


class _arb_parallelizer:

    def __init__(self, arb_accumulator):
        self._arb_accumulator = arb_accumulator
        self._arb_sequence = None
        self._old_add_arb_fn = None

    def _add_arb(self, arb, on_done_fn=None):
        if arb.empty:
            return
        if self._arb_sequence is None:
            self._arb_sequence = []
        self._arb_sequence.append(arb)

    def __enter__(self):
        self._old_add_arb_fn = self._arb_accumulator.add_arb
        self._arb_accumulator.add_arb = self._add_arb

    def __exit__(self, exc_type, exc_value, traceback):
        self._arb_accumulator.add_arb = self._old_add_arb_fn
        if self._arb_sequence:
            self._arb_accumulator.add_arb(self._arb_sequence)


class ArbAccumulatorService(sims4.service_manager.Service):
    CUSTOM_EVENT = 901
    MAX_XEVT = 999
    MAXIMUM_TIME_DEBT = TunableRealSecond(1, description='\n    The maximum amount of time in seconds to allow the server to run ahead \n    of the client when running a contiguous block of animation/routing to \n    improve blending. Setting this to 0 will disable this feature but ruin blending.')
    MAXIMUM_SHAVE_FRAMES_PER_ANIMATION = Tunable(int, 5, description='\n    The maximum number of frames to shave off of the must-run duration of each \n    animation until we reach a total amount of time debt equal to MAXIMUM_TIME_DEBT.')
    MAXIMUM_SHAVE_ANIMATION_RATIO = Tunable(float, 2, description='\n    The maximum ratio of an animation to shave off. For example, if this\n    is tuned to 2, we will shave off at most 1/2 of the total must-run\n    duration of an animation.\n    ')

    @staticmethod
    def get_shave_time_given_duration_and_debt(duration, debt):
        shave_time_max = max(0, ArbAccumulatorService.MAXIMUM_TIME_DEBT - debt)
        shave_time_requested = min(duration / ArbAccumulatorService.MAXIMUM_SHAVE_ANIMATION_RATIO, 0.03333333333333333 * ArbAccumulatorService.MAXIMUM_SHAVE_FRAMES_PER_ANIMATION)
        shave_time_actual = min(shave_time_max, shave_time_requested)
        return shave_time_actual

    def __init__(self):
        self._arb_sequence = []
        self._on_done = sims4.callback_utils.CallableList()
        self._in_flush = False
        self._custom_xevt_id_generator = self.CUSTOM_EVENT
        self._sequence_parallel = None
        self._time_debt = WeakKeyDictionary()
        self._shave_time = WeakKeyDictionary()

    def get_time_debt(self, sims):
        max_debt = 0
        for sim in sims:
            if sim not in self._time_debt:
                continue
            sim_debt = self._time_debt[sim]
            if sim_debt > max_debt:
                max_debt = sim_debt

        return max_debt

    def set_time_debt(self, sims, debt):
        for sim in sims:
            self._time_debt[sim] = debt

    def _clear(self):
        self._arb_sequence = []
        self._on_done = sims4.callback_utils.CallableList()
        self._custom_xevt_id_generator = self.CUSTOM_EVENT

    def parallelize(self):
        return _arb_parallelizer(self)

    def add_arb(self, arb, on_done_fn=None):
        if isinstance(arb, list):
            arbs = arb
        else:
            arbs = (
             arb,)
        for sub_arb in arbs:
            if not sub_arb._actors():
                logger.error('Attempt to play animation that has no connected actors:')
                sub_arb.log_request_history(dump_logger.error)

        if self._in_flush:
            for sub_arb in arbs:
                logger.debug('\n\nEvent-triggered ARB:\n{}\n\n', sub_arb.get_contents_as_string())
                distribute_arb_element(sub_arb)
                if on_done_fn is not None:
                    on_done_fn()

            return
        self._arb_sequence.append(arb)
        if on_done_fn is not None:
            self._on_done.append(on_done_fn)

    def claim_xevt_id(self):
        event_id = self._custom_xevt_id_generator
        self._custom_xevt_id_generator += 1
        if self._custom_xevt_id_generator == self.MAX_XEVT:
            logger.warn('Excessive XEVT IDs claimed before a flush. This is likely caused by an error in animation requests. -RS')
        return event_id

    def _begin_arb_element(self):
        element = ArbElement((animation.arb.Arb()), event_records=[])
        return element

    def _flush_arb_element(self, element_run_queue, arb_element, all_actors, on_done, closes_sequence):
        if not arb_element.arb.empty:
            if not closes_sequence:
                arb_element.enable_optional_sleep_time = False
            else:
                if arb_element.arb.empty:
                    raise RuntimeError('About to flush an empty Arb')
                element_run_queue.append(arb_element)
                return closes_sequence or self._begin_arb_element()
            return
        return arb_element

    def _append_arb_to_element(self, buffer_arb_element, arb, actors, safe_mode, attach=True):
        if not arb.empty:
            if buffer_arb_element.arb._can_append(arb, safe_mode):
                buffer_arb_element.event_records = buffer_arb_element.event_records or []
                if attach:
                    (buffer_arb_element.attach)(*actors, **{'actor_instances': arb._actor_instances()})
                buffer_arb_element.execute_and_merge_arb(arb, safe_mode)
                return True
        return False

    def _append_arb_element_to_element(self, buffer_arb_element, arb_element, actors, safe_mode):
        if not arb_element.arb.empty:
            if buffer_arb_element.arb._can_append(arb_element.arb, safe_mode):
                buffer_arb_element.event_records = buffer_arb_element.event_records or []
                (buffer_arb_element.attach)(*actors)
                buffer_arb_element.event_records.extend(arb_element.event_records)
                buffer_arb_element.arb.append(arb_element.arb, safe_mode)
                return True
        return False

    def flush(self, timeline, animate_instantly=False):
        arb_sequence = self._arb_sequence
        on_done = self._on_done
        self._clear()
        actors = get_actors_for_arb_sequence(*arb_sequence)
        self._in_flush = True
        try:
            if len(actors) > 0:
                first_unprocessed_arb = 0
                sequence_len = len(arb_sequence)
                buffer_arb_element = None
                element_run_queue = []
                sim_actors = [actor for actor in actors if actor.is_sim]
                with distributor.system.Distributor.instance().dependent_block():
                    while first_unprocessed_arb < sequence_len:
                        if buffer_arb_element is None:
                            buffer_arb_element = self._begin_arb_element()
                        for i in range(first_unprocessed_arb, sequence_len):
                            arb = arb_sequence[i]
                            if isinstance(arb, list):
                                combined_arb = animation.arb.Arb()
                                for sub_arb in arb:
                                    combined_arb.append(sub_arb, False, True)

                                if not buffer_arb_element.arb._can_append(combined_arb, True):
                                    break
                                (buffer_arb_element.attach)(*actors)
                                buffer_arb_element_parallel = self._begin_arb_element()
                                result = self._append_arb_to_element(buffer_arb_element_parallel, combined_arb,
                                  actors,
                                  False, attach=False)
                                arb_sequence[i] = buffer_arb_element_parallel
                                arb = buffer_arb_element_parallel
                                buffer_arb_element_parallel.detach()
                            elif isinstance(arb, ArbElement):
                                append_fn = self._append_arb_element_to_element
                            else:
                                append_fn = self._append_arb_to_element
                            if not append_fn(buffer_arb_element, arb, actors, True):
                                first_unprocessed_arb = i
                                break
                            first_unprocessed_arb = i + 1

                        buffer_arb_element = self._flush_arb_element(element_run_queue, buffer_arb_element, actors, on_done, first_unprocessed_arb == sequence_len)

                self._in_flush = False
                arb_sequence_element = ArbSequenceElement(element_run_queue, animate_instantly=animate_instantly)
                yield from element_utils.run_child(timeline, arb_sequence_element)
        finally:
            self._in_flush = False
            on_done()

        if False:
            yield None