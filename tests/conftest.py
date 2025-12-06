# pytest configuration and fixtures for GUI testing

import pytest
import tkinter as tk
import customtkinter as ctk
import tempfile
import os
import sys
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment for all tests"""
    # Set CustomTkinter to test mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    yield

    # Cleanup after all tests
    # Close any remaining tkinter windows
    try:
        root = tk._default_root
        if root:
            root.quit()
    except:
        pass

@pytest.fixture
def temp_db():
    """Create a temporary database file for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as f:
        temp_file = f.name

    yield temp_file

    # Cleanup
    try:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    except:
        pass

@pytest.fixture
def mock_storage():
    """Mock storage manager for testing"""
    storage = Mock()
    storage.load = Mock(return_value=True)
    storage.save = Mock(return_value=True)
    storage.create_new = Mock(return_value=True)
    storage.is_open = True
    return storage

@pytest.fixture
def mock_crypto():
    """Mock crypto manager for testing"""
    crypto = Mock()
    crypto.encrypt = Mock(return_value=b"encrypted_data")
    crypto.decrypt = Mock(return_value=b"decrypted_data")
    return crypto

@pytest.fixture
def tk_root():
    """Create a tkinter root for GUI testing"""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    root.geometry("800x600")

    yield root

    # Cleanup
    try:
        root.quit()
        root.destroy()
    except:
        pass

@pytest.fixture
def ctk_app(tk_root):
    """Create a CustomTkinter app instance for testing"""
    app = ctk.CTk()
    app.withdraw()  # Hide the window

    yield app

    # Cleanup
    try:
        app.quit()
        app.destroy()
    except:
        pass

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "gui: GUI component tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "accessibility: Accessibility tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add gui marker to GUI-related tests
        if 'gui' in item.nodeid.lower() or 'dialog' in item.nodeid.lower():
            item.add_marker(pytest.mark.gui)

        # Add integration marker to integration tests
        if 'integration' in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)

        # Add performance marker to performance tests
        if 'performance' in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)

        # Add accessibility marker to accessibility tests
        if 'accessibility' in item.nodeid.lower():
            item.add_marker(pytest.mark.accessibility)

def pytest_html_report_title(report):
    """Set the HTML report title"""
    report.title = "Cryptonote GUI Test Report"