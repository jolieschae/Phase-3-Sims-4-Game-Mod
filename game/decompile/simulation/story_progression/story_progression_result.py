# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\story_progression\story_progression_result.py
# Compiled at: 2022-03-10 20:35:10
# Size of source mod 2**32: 3249 bytes
import enum

class StoryProgressionResultType(enum.Int, export=False):
    SUCCESS = ...
    SUCCESS_MAKE_HISTORICAL = ...
    ERROR = ...
    FAILED_TESTS = ...
    FAILED_PRECONDITIONS = ...
    FAILED_NEXT_CHAPTER = ...
    FAILED_ACTION = ...
    FAILED_DEMOGRAPHICS = ...
    FAILED_NO_ARCS = ...
    FAILED_ROTATION = ...


STORY_PROGRESSION_RESULT_TYPE_STRINGS = {StoryProgressionResultType.SUCCESS: 'SUCCESS', 
 StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL: 'SUCCESS_MAKE_HISTORICAL', 
 StoryProgressionResultType.ERROR: 'ERROR', 
 StoryProgressionResultType.FAILED_TESTS: 'FAILED_TESTS', 
 StoryProgressionResultType.FAILED_PRECONDITIONS: 'FAILED_PRECONDITIONS', 
 StoryProgressionResultType.FAILED_NEXT_CHAPTER: 'FAILED_NEXT_CHAPTER', 
 StoryProgressionResultType.FAILED_ACTION: 'FAILED_ACTION', 
 StoryProgressionResultType.FAILED_DEMOGRAPHICS: 'FAILED_DEMOGRAPHICS', 
 StoryProgressionResultType.FAILED_NO_ARCS: 'FAILED_NO_ARCS', 
 StoryProgressionResultType.FAILED_ROTATION: 'FAILED_ROTATION'}

class StoryProgressionResult:

    def __init__(self, result_type, *args):
        self._result_type = result_type
        if args:
            self._reason, self._format_args = args[0], args[1:]
        else:
            self._reason, self._format_args = (None, ())

    def __bool__(self):
        return self._result_type == StoryProgressionResultType.SUCCESS or self._result_type == StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL

    @property
    def reason(self):
        if self._format_args:
            if self._reason:
                self._reason = (self._reason.format)(*self._format_args)
                self._format_args = ()
        return self._reason

    def __str__(self):
        if self.reason:
            return self.reason
        return str(self._result_type)

    @property
    def result_type(self):
        return self._result_type

    @property
    def should_be_made_historical(self):
        return self._result_type == StoryProgressionResultType.SUCCESS_MAKE_HISTORICAL