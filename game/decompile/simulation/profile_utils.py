# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\profile_utils.py
# Compiled at: 2020-11-19 09:51:08
# Size of source mod 2**32: 5462 bytes
import time, sims4.log, functools
logger = sims4.log.Logger('Profile')
debug_stack_depth = 0
output_strings = []
all_profile_functions = []
sub_start_time = 0

def sub_time_start():
    global debug_stack_depth
    global sub_start_time
    if debug_stack_depth > 0:
        sub_start_time = time.clock()


def sub_time_end(sub_time_id, precision=5):
    global output_strings
    if debug_stack_depth > 0:
        output_strings.append(('Sub: {1}, Time: {2:.{3}f}', debug_stack_depth, (sub_time_id, time.clock() - sub_start_time, precision)))


def add_string(format_string, indent=0, *args):
    output_strings.append((format_string, indent, args))


class profile_function:

    def __init__(self, indent=None, show_enter=False, id_str='', only_in_stack=False, threshold=None, precision=5, output_filename=None):
        global all_profile_functions
        self.time = 0
        self.total_time = 0
        self.num_calls = 0
        self.func_name = None
        self.show_enter = show_enter
        self.id_str = id_str
        self.threshold = threshold
        self.precision = precision
        self.output_filename = output_filename
        if indent is None:
            self.stack_indent = True
        else:
            self.stack_indent = False
            self.indent = indent
        self.only_in_stack = only_in_stack
        all_profile_functions.append(self)

    def _aftercall(self, func_return, start_time, func_name):
        global debug_stack_depth
        end_time = time.clock()
        self.time = end_time - start_time
        self.total_time += self.time
        self.num_calls += 1
        warning_str = ''
        if self.threshold is not None:
            if self.threshold < self.time:
                warning_str = '(WARNING)'
        debug_stack_depth -= 1
        if self.stack_indent:
            self.indent = debug_stack_depth
        output_strings.append(('Exit: {1}({2}), Num Calls: {3}, Time this Run: {4:.{7}f}{5}, Total Time: {6:.{7}f}',
         self.indent, (func_name, self.id_str, self.num_calls, self.time, warning_str, self.total_time, self.precision)))
        if debug_stack_depth == 0:
            self.print_output_strings()

    def __call__(self, func):

        def wrapper(*args, **kwargs):
            global debug_stack_depth
            if not self.only_in_stack or debug_stack_depth > 0:
                if self.stack_indent:
                    self.indent = debug_stack_depth
                debug_stack_depth += 1
                start_time = time.clock()
                self.func_name = func.__name__
                if self.show_enter:
                    output_strings.append(('Enter: {1}', self.indent, (func.__name__,)))
                function = func(*args, **kwargs)
                self._aftercall(function, start_time, func.__name__)
                return function
            return func(*args, **kwargs)

        return functools.update_wrapper(wrapper, func)

    def print_output_strings(self):
        try:
            if self.output_filename is not None:
                f = open('{}.txt'.format(self.output_filename), 'a')
            for debug_output in output_strings:
                string = debug_output[0]
                output_string = '{}{}'.format('{0}', string)
                indent = debug_output[1]
                indent_str = indent * '   '
                string_args = debug_output[2]
                if self.output_filename is not None:
                    f.write((output_string.format)(indent_str, *string_args) + '\n')
                else:
                    (logger.error)(output_string, indent_str, *string_args)

        finally:
            if self.output_filename is not None:
                f.close()

        del output_strings[:]