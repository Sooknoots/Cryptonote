# Cryptonote GUI Testing Framework

## Overview

This document describes the comprehensive GUI testing framework implemented for Cryptonote, providing automated testing capabilities for tkinter/CustomTkinter applications.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # pytest configuration and fixtures
├── test_gui.py             # GUI component tests
├── test_e2e.py             # End-to-end workflow tests
└── test_*.py               # Additional test files

run_gui_tests.py            # GUI test runner
pytest.ini                  # pytest configuration
.github/workflows/gui-tests.yml  # CI/CD configuration
```

## Test Categories

### 1. Unit Tests (`run_tests.py`)
- **Purpose**: Test individual components and logic
- **Coverage**: Storage, crypto, models
- **Framework**: unittest
- **Run**: `python run_tests.py`

### 2. GUI Component Tests (`test_gui.py`)
- **Purpose**: Test GUI components in isolation
- **Coverage**: Dialogs, widgets, event handling
- **Framework**: unittest with tkinter fixtures
- **Run**: `python run_gui_tests.py --gui-only`

### 3. Integration Tests
- **Purpose**: Test component interactions
- **Coverage**: UI workflows, data flow
- **Framework**: pytest with fixtures

### 4. End-to-End Tests (`test_e2e.py`)
- **Purpose**: Test complete user workflows
- **Coverage**: Full application workflows
- **Framework**: pytest with PyAutoGUI
- **Run**: `pytest tests/test_e2e.py`

### 5. Performance Tests
- **Purpose**: Measure application performance
- **Coverage**: Startup time, memory usage, responsiveness
- **Framework**: pytest with timing fixtures

## Running Tests

### Development Testing

```bash
# Run all tests
python run_gui_tests.py

# Run only GUI tests
python run_gui_tests.py --gui-only

# Run only unit tests
python run_gui_tests.py --unit-only

# Run with pytest
pytest tests/ -v

# Run specific test class
pytest tests/test_gui.py::DialogTestCase -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Automated Testing on Launch

Set environment variable to enable startup testing:
```bash
export CRYPTONOTE_TEST_MODE=1
python Gui.py
```

### CI/CD Testing

Tests run automatically on:
- Push to master/main
- Pull requests
- Manual workflow dispatch

## Test Fixtures

### tkinter Fixtures
- `tk_root`: Hidden tkinter root window
- `ctk_app`: CustomTkinter application instance
- `temp_db`: Temporary database file

### Mock Fixtures
- `mock_storage`: Mocked storage manager
- `mock_crypto`: Mocked crypto manager

## Writing New Tests

### GUI Component Test Example

```python
import unittest
from tests.test_gui import GUITestCase

class TestMyComponent(GUITestCase):
    def test_component_creation(self):
        """Test component initializes correctly"""
        component = MyComponent(self.root)
        self.assertIsNotNone(component)
        self.assertTrue(component.winfo_exists())
```

### Integration Test Example

```python
@pytest.mark.integration
def test_ui_workflow(tk_root, mock_storage):
    """Test complete UI workflow"""
    app = MainApp(tk_root)
    # Simulate user interactions
    # Assert expected behavior
```

### E2E Test Example

```python
@pytest.mark.slow
def test_full_workflow():
    """Test complete user workflow"""
    # Launch app
    # Automate user interactions with PyAutoGUI
    # Verify results
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
addopts = --tb=short --cov=src --html=reports/test_report.html
markers =
    gui: GUI component tests
    integration: Integration tests
    performance: Performance tests
    accessibility: Accessibility tests
    slow: Slow running tests
```

### Environment Variables

- `CRYPTONOTE_TEST_MODE`: Enable startup testing (1/true/yes)
- `CI`: Skip display-dependent tests in CI
- `DISPLAY`: Required for E2E tests

## Best Practices

### GUI Testing Guidelines

1. **Isolate Components**: Test widgets independently
2. **Mock Dependencies**: Use mocks for external services
3. **Headless Mode**: Run tests without displaying windows
4. **Event Simulation**: Use tkinter.Event for user interactions
5. **Cleanup**: Always destroy widgets after tests

### Performance Testing

1. **Startup Time**: Measure app initialization
2. **Memory Usage**: Monitor resource consumption
3. **UI Responsiveness**: Test event handling speed
4. **Scalability**: Test with large datasets

### CI/CD Integration

1. **Parallel Execution**: Use pytest-xdist for faster runs
2. **Coverage Reports**: Generate HTML coverage reports
3. **Artifact Upload**: Save test results and screenshots
4. **Failure Handling**: Continue on test failures for reporting

## Troubleshooting

### Common Issues

1. **Tkinter Headless**: Use `xvfb-run` on Linux for headless testing
2. **Window Focus**: Ensure test windows don't steal focus
3. **Timing Issues**: Use appropriate waits for async operations
4. **Platform Differences**: Account for OS-specific behavior

### Debugging Tests

```bash
# Verbose output
pytest tests/ -v -s

# Debug specific test
pytest tests/test_gui.py::TestDialogTestCase::test_summary_dialog_creation -xvs

# Generate HTML report
pytest tests/ --html=debug_report.html
```

## Test Reports

### Generated Reports

- `reports/test_report.html`: HTML test report
- `reports/coverage/`: Coverage reports
- `htmlcov/`: Detailed coverage HTML
- `logs/gui_tests.log`: Test execution logs

### Report Contents

- Test execution summary
- Pass/fail status by category
- Performance metrics
- Coverage statistics
- Error details and stack traces

## Future Enhancements

1. **Visual Regression Testing**: Screenshot comparison
2. **Accessibility Testing**: Screen reader compatibility
3. **Cross-Platform Testing**: Multi-OS test matrix
4. **Load Testing**: Stress test with many notes
5. **Automated Screenshots**: UI documentation generation

## Maintenance

### Regular Tasks

1. Update test fixtures for new components
2. Review and update performance baselines
3. Clean up obsolete test files
4. Update CI/CD configuration as needed

### Test Health Monitoring

1. Monitor test execution time trends
2. Track flaky tests and fix them
3. Maintain high coverage levels
4. Review test failure patterns