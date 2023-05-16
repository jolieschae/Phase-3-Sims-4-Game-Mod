# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\unittest\runner.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 7972 bytes
import sys, time, warnings
from . import result
from .signals import registerResult
__unittest = True

class _WritelnDecorator(object):

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')


class TextTestResult(result.TestResult):
    separator1 = '======================================================================'
    separator2 = '----------------------------------------------------------------------'

    def __init__(self, stream, descriptions, verbosity):
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions:
            if doc_first_line:
                return '\n'.join((str(test), doc_first_line))
        return str(test)

    def startTest(self, test):
        super(TextTestResult, self).startTest(test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(' ... ')
            self.stream.flush()

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        if self.showAll:
            self.stream.writeln('ok')
        else:
            if self.dots:
                self.stream.write('.')
                self.stream.flush()

    def addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        if self.showAll:
            self.stream.writeln('ERROR')
        else:
            if self.dots:
                self.stream.write('E')
                self.stream.flush()

    def addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.writeln('FAIL')
        else:
            if self.dots:
                self.stream.write('F')
                self.stream.flush()

    def addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        if self.showAll:
            self.stream.writeln('skipped {0!r}'.format(reason))
        else:
            if self.dots:
                self.stream.write('s')
                self.stream.flush()

    def addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        if self.showAll:
            self.stream.writeln('expected failure')
        else:
            if self.dots:
                self.stream.write('x')
                self.stream.flush()

    def addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
        if self.showAll:
            self.stream.writeln('unexpected success')
        else:
            if self.dots:
                self.stream.write('u')
                self.stream.flush()

    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln('%s: %s' % (flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln('%s' % err)


class TextTestRunner(object):
    resultclass = TextTestResult

    def __init__(self, stream=None, descriptions=True, verbosity=1, failfast=False, buffer=False, resultclass=None, warnings=None, *, tb_locals=False):
        if stream is None:
            stream = sys.stderr
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        with warnings.catch_warnings():
            if self.warnings:
                warnings.simplefilter(self.warnings)
                if self.warnings in ('default', 'always'):
                    warnings.filterwarnings('module', category=DeprecationWarning,
                      message='Please use assert\\w+ instead.')
            startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()

            stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        else:
            run = result.testsRun
            self.stream.writeln('Ran %d test%s in %.3fs' % (
             run, run != 1 and 's' or '', timeTaken))
            self.stream.writeln()
            expectedFails = unexpectedSuccesses = skipped = 0
            try:
                results = map(len, (result.expectedFailures,
                 result.unexpectedSuccesses,
                 result.skipped))
            except AttributeError:
                pass
            else:
                expectedFails, unexpectedSuccesses, skipped = results
            infos = []
            if not result.wasSuccessful():
                self.stream.write('FAILED')
                failed, errored = len(result.failures), len(result.errors)
                if failed:
                    infos.append('failures=%d' % failed)
                elif errored:
                    infos.append('errors=%d' % errored)
                else:
                    self.stream.write('OK')
                if skipped:
                    infos.append('skipped=%d' % skipped)
                if expectedFails:
                    infos.append('expected failures=%d' % expectedFails)
                if unexpectedSuccesses:
                    infos.append('unexpected successes=%d' % unexpectedSuccesses)
                if infos:
                    self.stream.writeln(' (%s)' % (', '.join(infos),))
            else:
                self.stream.write('\n')
        return result