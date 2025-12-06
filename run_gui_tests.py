# GUI Test Runner for Cryptonote
# Automatically runs GUI tests on application launch

import sys
import os
import time
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def setup_test_logging():
    """Set up logging for test execution"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - GUI_TEST - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "gui_tests.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_gui_tests_comprehensive():
    """Run comprehensive GUI test suite"""
    logging.info("Starting comprehensive GUI test suite...")

    try:
        # Import test modules
        from tests.test_gui import run_gui_tests

        # Run GUI tests
        success, total, failures, errors = run_gui_tests()

        logging.info(f"GUI Tests completed: {total} tests run")
        logging.info(f"Results: {total - failures - errors} passed, {failures} failed, {errors} errors")

        if not success:
            logging.error("GUI tests failed!")
            return False

        logging.info("All GUI tests passed!")
        return True

    except Exception as e:
        logging.error(f"GUI test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_unit_tests():
    """Run unit tests for non-GUI components"""
    logging.info("Running unit tests...")

    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "run_tests.py",
            "--verbosity", "1",
            "--log-level", "WARNING"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logging.info("Unit tests passed")
            return True
        else:
            logging.error("Unit tests failed")
            logging.error(f"STDOUT: {result.stdout}")
            logging.error(f"STDERR: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logging.error("Unit tests timed out")
        return False
    except Exception as e:
        logging.error(f"Unit test execution failed: {e}")
        return False

def run_performance_tests():
    """Run performance tests"""
    logging.info("Running performance tests...")

    try:
        # Import and run performance tests
        from tests.test_gui import PerformanceTestCase
        import unittest

        suite = unittest.TestLoader().loadTestsFromTestCase(PerformanceTestCase)
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)

        return result.wasSuccessful()

    except Exception as e:
        logging.error(f"Performance test execution failed: {e}")
        return False

def generate_test_report(results, run_flags):
    """Generate a test report"""
    def get_status(result, was_run):
        if not was_run:
            return 'NOT RUN'
        return 'PASS' if result else 'FAIL'
    
    run_results = [results[k] for k in results if run_flags[k]]
    overall_success = all(run_results) if run_results else True
    
    report = f"""
Cryptonote Test Report
=======================

Test Execution Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

Results Summary:
- GUI Tests: {get_status(results['gui'], run_flags['gui'])}
- Unit Tests: {get_status(results['unit'], run_flags['unit'])}
- Performance Tests: {get_status(results['performance'], run_flags['performance'])}

Overall Status: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}

Recommendations:
- {'Application is ready for release' if overall_success else 'Fix failing tests before release'}
- {'GUI performance is acceptable' if results['performance'] else 'Review GUI performance issues'}
"""

    # Save report
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    report_file = report_dir / f"test_report_{int(time.time())}.txt"
    with open(report_file, 'w') as f:
        f.write(report)

    logging.info(f"Test report saved to: {report_file}")
    return report

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Cryptonote GUI Test Runner')
    parser.add_argument('--gui-only', action='store_true', help='Run only GUI tests')
    parser.add_argument('--unit-only', action='store_true', help='Run only unit tests')
    parser.add_argument('--performance-only', action='store_true', help='Run only performance tests')
    parser.add_argument('--skip-report', action='store_true', help='Skip report generation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Setup logging
    setup_test_logging()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info("Cryptonote Test Runner Started")
    logging.info(f"Arguments: {args}")

    start_time = time.time()

    # Determine which tests to run
    run_gui = not args.unit_only and not args.performance_only
    run_unit = not args.gui_only and not args.performance_only
    run_performance = not args.gui_only and not args.unit_only

    results = {'gui': False, 'unit': False, 'performance': False}  # Initialize all results

    # Run tests
    if run_gui:
        results['gui'] = run_gui_tests_comprehensive()

    if run_unit:
        results['unit'] = run_unit_tests()

    if run_performance:
        results['performance'] = run_performance_tests()

    # Calculate execution time
    execution_time = time.time() - start_time
    logging.info(f"Total test execution time: {execution_time:.2f} seconds")

    run_flags = {'gui': run_gui, 'unit': run_unit, 'performance': run_performance}

    # Generate report
    if not args.skip_report:
        report = generate_test_report(results, run_flags)
        print("\n" + "="*50)
        print(report)
        print("="*50)

    # Return overall success
    run_results = [results[k] for k in results if run_flags[k]]
    overall_success = all(run_results) if run_results else True
    logging.info(f"Test suite completed: {'SUCCESS' if overall_success else 'FAILURE'}")

    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(main())