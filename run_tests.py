# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: ef0d6da7bed2fc34
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

#!/usr/bin/env python3
"""
Test runner for Cryptonote application.
Run all tests with: python run_tests.py
Run specific test: python run_tests.py TestCryptoManager.test_encrypt_decrypt
"""

import argparse
import logging
import os
import sys
import time
import unittest
from dataclasses import dataclass
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


@dataclass
class TestTimingEntry:
    name: str
    start: float
    end: Optional[float] = None
    status: str = "RUNNING"

    def duration(self) -> float:
        if self.end is None:
            return 0.0
        return self.end - self.start


class TimedTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity, *, max_duration: Optional[float] = None):
        super().__init__(stream, descriptions, verbosity)
        self.max_duration = max_duration
        self.runner_start = time.perf_counter()
        self._entries: Dict[str, TestTimingEntry] = {}
        self.timing_entries: List[TestTimingEntry] = []
        self._logger = logging.getLogger(__name__)

    def startTest(self, test):
        super().startTest(test)
        now = time.perf_counter()
        entry = TestTimingEntry(name=test.id(), start=now)
        self._entries[test.id()] = entry
        self.timing_entries.append(entry)
        self._logger.info("Starting %s", test.id())
        if self.max_duration and (now - self.runner_start) > self.max_duration:
            self._logger.warning("Max duration %.1fs exceeded before %s", self.max_duration, test.id())
            self.shouldStop = True

    def stopTest(self, test):
        super().stopTest(test)
        now = time.perf_counter()
        entry = self._entries.get(test.id())
        if entry:
            entry.end = now
            if entry.status == "RUNNING":
                entry.status = "PASS"
            self._logger.info("Finished %s [%s] (%.2fs)", entry.name, entry.status, entry.duration())
        if self.max_duration and (now - self.runner_start) > self.max_duration:
            self._logger.warning("Reached max duration %.1fs during %s", self.max_duration, test.id())
            self.shouldStop = True

    def addFailure(self, test, err):
        self._mark_status(test, "FAIL")
        return super().addFailure(test, err)

    def addError(self, test, err):
        self._mark_status(test, "ERROR")
        return super().addError(test, err)

    def addSkip(self, test, reason):
        self._mark_status(test, "SKIP")
        return super().addSkip(test, reason)

    def _mark_status(self, test, status: str):
        entry = self._entries.get(test.id())
        if entry:
            entry.status = status


def make_result_class(max_duration: Optional[float]):
    class ResultWithTimeout(TimedTestResult):
        def __init__(self, stream, descriptions, verbosity):
            super().__init__(stream, descriptions, verbosity, max_duration=max_duration)

    return ResultWithTimeout


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the Cryptonote test suite with enhanced logging.')
    parser.add_argument('--max-duration', type=float, default=0, help='Maximum test run duration in seconds (0 = unlimited).')
    parser.add_argument('--verbosity', type=int, choices=[1, 2, 3], default=2, help='Verbosity level for unittest runner.')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='Log level for this runner.')
    return parser.parse_args()


def log_timetable(result: TimedTestResult, total_run: float, max_duration: Optional[float]):
    entries = getattr(result, 'timing_entries', [])
    if not entries:
        return

    logging.info('--- Testing timetable summary ---')
    sorted_entries = sorted(entries, key=lambda e: e.duration(), reverse=True)
    top_entries = sorted_entries[:5]
    for entry in top_entries:
        logging.info('%s | %s | %.2fs', entry.name, entry.status, entry.duration())

    if len(entries) > len(top_entries):
        logging.info('And %d more tests ran.', len(entries) - len(top_entries))

    if max_duration and total_run >= max_duration:
        logging.warning('Run truncated after %.1fs because max-duration %.1fs was reached.', total_run, max_duration)
    logging.info('Total runtime %.2fs.', total_run)


def print_failure_log(result):
    if result.wasSuccessful():
        return

    print('\n=== ERROR LOG ===', file=sys.stderr)
    for test, trace in result.failures:
        print(f'[FAIL] {test}', file=sys.stderr)
        print(trace, file=sys.stderr)
    for test, trace in result.errors:
        print(f'[ERROR] {test}', file=sys.stderr)
        print(trace, file=sys.stderr)


def main():
    args = parse_arguments()
    logging.basicConfig(level=getattr(logging, args.log_level), format='TEST %(levelname)s: %(message)s')

    max_duration = args.max_duration if args.max_duration > 0 else None
    logging.info('Starting test runner (max-duration=%s).', f'{max_duration}s' if max_duration else 'unlimited')

    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=args.verbosity, resultclass=make_result_class(max_duration))
    start_time = time.perf_counter()
    result = runner.run(suite)
    total_run = time.perf_counter() - start_time

    log_timetable(result, total_run, max_duration)
    print_failure_log(result)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()