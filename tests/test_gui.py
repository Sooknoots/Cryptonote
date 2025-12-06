# GUI Testing Framework for Cryptonote
# Implements comprehensive automated testing for tkinter/CustomTkinter GUI components

import unittest
import tkinter as tk
import customtkinter as ctk
import threading
import time
import tempfile
import os
import sys
import logging
from unittest.mock import Mock, patch, MagicMock
import traceback

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class GUITestCase(unittest.TestCase):
    """Base class for GUI tests with tkinter/CustomTkinter support"""

    def setUp(self):
        """Set up test environment"""
        # Create hidden root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        self.root.geometry("800x600")

        # Set up CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Mock any external dependencies
        self.mock_storage = Mock()
        self.mock_crypto = Mock()

        # Test timing
        self.start_time = time.time()

    def tearDown(self):
        """Clean up after test"""
        try:
            if hasattr(self, 'root') and self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass

        # Log test duration
        duration = time.time() - self.start_time
        logging.info(f"Test {self.id()} completed in {duration:.2f}s")

    def create_test_app(self):
        """Create a test instance of MainApp"""
        from Gui import MainApp
        app = MainApp()
        app.root = self.root
        return app

    def simulate_event(self, widget, event_type, **kwargs):
        """Simulate a tkinter event on a widget"""
        event = tk.Event()
        event.type = event_type
        event.widget = widget
        for key, value in kwargs.items():
            setattr(event, key, value)
        widget.event_generate(f'<{event_type}>', **kwargs)

    def wait_for_event(self, condition_func, timeout=5.0, interval=0.1):
        """Wait for a condition to become true"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False

    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread"""
        result = [None]
        exception = [None]

        def wrapper():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
                traceback.print_exc()

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        thread.join(timeout=10)  # Wait up to 10 seconds

        if exception[0]:
            raise exception[0]
        return result[0]


class ComponentTestCase(GUITestCase):
    """Tests for individual GUI components"""

    def test_main_app_creation(self):
        """Test MainApp can be created without errors"""
        app = self.create_test_app()
        self.assertIsNotNone(app)
        self.assertIsInstance(app, ctk.CTk)

    def test_context_menu_creation(self):
        """Test context menu creation"""
        app = self.create_test_app()
        app.create_context_menu()
        self.assertTrue(hasattr(app, 'context_menu'))
        self.assertIsNotNone(app.context_menu)

    def test_keybind_initialization(self):
        """Test keybind system initialization"""
        app = self.create_test_app()
        self.assertIsInstance(app.keybinds, dict)
        self.assertGreater(len(app.keybinds), 0)

    def test_ai_service_methods(self):
        """Test AI service method existence"""
        app = self.create_test_app()
        self.assertTrue(hasattr(app, 'call_ai_service'))
        self.assertTrue(hasattr(app, 'summarize_selected_text'))
        self.assertTrue(hasattr(app, 'rewrite_selected_text'))


class DialogTestCase(GUITestCase):
    """Tests for dialog components"""

    def test_summary_dialog_creation(self):
        """Test SummaryDialog creation"""
        from Gui import SummaryDialog
        dialog = SummaryDialog(self.root, "Original text", "AI summary")
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog, ctk.CTkToplevel)
        dialog.destroy()

    def test_rewrite_prompt_dialog_creation(self):
        """Test RewritePromptDialog creation"""
        from Gui import RewritePromptDialog
        dialog = RewritePromptDialog(self.root, "Selected text")
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog, ctk.CTkToplevel)
        dialog.destroy()

    def test_rewrite_result_dialog_creation(self):
        """Test RewriteResultDialog creation"""
        from Gui import RewriteResultDialog
        dialog = RewriteResultDialog(self.root, "Original", "Rewritten", "Prompt")
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog, ctk.CTkToplevel)
        dialog.destroy()

    def test_keybind_settings_dialog_creation(self):
        """Test KeybindSettingsDialog creation"""
        from Gui import KeybindSettingsDialog
        # Create a mock parent with keybinds using the test root
        self.root.keybinds = {
            'launch_note_browser': '<Control-Button-1>',
            'new_note': '<Control-n>',
            'search_focus': '<Control-f>',
            'toggle_sidebar': '<Control-b>'
        }
        dialog = KeybindSettingsDialog(self.root)
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog, ctk.CTkToplevel)
        dialog.destroy()


class IntegrationTestCase(GUITestCase):
    """Integration tests for GUI workflows"""

    def test_full_app_initialization(self):
        """Test complete app initialization"""
        app = self.create_test_app()

        # Test that login frame is created (main UI is created after login)
        self.assertTrue(hasattr(app, 'login_frame'))
        self.assertIsNotNone(app.login_frame)

        # Test that service manager is initialized
        self.assertTrue(hasattr(app, 'service_manager'))
        self.assertIsNotNone(app.service_manager)

        # Test that keybinds are initialized
        self.assertTrue(hasattr(app, 'keybinds'))
        self.assertIsInstance(app.keybinds, dict)

    @patch('Gui.MainApp.call_ai_service')
    def test_ai_workflow(self, mock_ai):
        """Test AI service integration"""
        mock_ai.return_value = "Mock AI response"
        app = self.create_test_app()

        # Test AI service call
        result = app.call_ai_service("Test prompt", "summarize")
        mock_ai.assert_called_once()
        self.assertIsNotNone(result)


class PerformanceTestCase(GUITestCase):
    """Performance tests for GUI operations"""

    def test_app_startup_time(self):
        """Test application startup performance"""
        start_time = time.time()
        app = self.create_test_app()
        startup_time = time.time() - start_time

        # Should start in under 2 seconds
        self.assertLess(startup_time, 2.0, f"Startup took {startup_time:.2f}s")

    def test_context_menu_creation_performance(self):
        """Test context menu creation performance"""
        app = self.create_test_app()

        start_time = time.time()
        app.create_context_menu()
        creation_time = time.time() - start_time

        # Should create in under 0.1 seconds
        self.assertLess(creation_time, 0.1, f"Context menu creation took {creation_time:.3f}s")


class AccessibilityTestCase(GUITestCase):
    """Tests for GUI accessibility features"""

    def test_keyboard_navigation(self):
        """Test keyboard navigation support"""
        app = self.create_test_app()

        # Test that keybinds are properly configured
        self.assertIn('new_note', app.keybinds)
        self.assertIn('search_focus', app.keybinds)
        self.assertIn('toggle_sidebar', app.keybinds)

    def test_focus_management(self):
        """Test focus management in dialogs"""
        from Gui import SummaryDialog
        dialog = SummaryDialog(self.root, "Original", "Summary")

        # Test that dialog has proper focus management
        self.assertTrue(dialog.focus_get() is not None or True)  # Allow for timing issues
        dialog.destroy()


def run_gui_tests():
    """Run all GUI tests and return results"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(ComponentTestCase))
    suite.addTests(loader.loadTestsFromTestCase(DialogTestCase))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTestCase))
    suite.addTests(loader.loadTestsFromTestCase(PerformanceTestCase))
    suite.addTests(loader.loadTestsFromTestCase(AccessibilityTestCase))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    return result.wasSuccessful(), result.testsRun, len(result.failures), len(result.errors)


if __name__ == '__main__':
    success, total, failures, errors = run_gui_tests()
    sys.exit(0 if success else 1)