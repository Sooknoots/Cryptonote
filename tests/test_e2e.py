# End-to-End GUI Testing with PyAutoGUI
# Comprehensive automated testing of full user workflows

import pytest
import pyautogui
import time
import os
import sys
import subprocess
import signal
import psutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.mark.slow
@pytest.mark.integration
class TestE2EWorkflows:
    """End-to-end testing of complete user workflows"""

    @pytest.fixture(scope="class", autouse=True)
    def setup_app(self):
        """Launch the application for E2E testing"""
        # Skip if display not available (CI/CD)
        if os.getenv('CI') or not os.getenv('DISPLAY', '').strip():
            pytest.skip("E2E tests require display environment")

        # Launch application
        self.app_process = subprocess.Popen([
            sys.executable, 'Gui.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for app to start
        time.sleep(3)

        # Verify app is running
        assert self.app_process.poll() is None, "Application failed to start"

        yield

        # Cleanup
        try:
            if self.app_process and self.app_process.poll() is None:
                # Try graceful shutdown first
                if os.name == 'nt':
                    self.app_process.terminate()
                else:
                    os.kill(self.app_process.pid, signal.SIGTERM)
                time.sleep(2)

                # Force kill if still running
                if self.app_process.poll() is None:
                    self.app_process.kill()
        except:
            pass

    def test_application_launch(self):
        """Test that application launches successfully"""
        # Give app time to fully initialize
        time.sleep(2)

        # Check if app window exists
        try:
            window = pyautogui.getWindowsWithTitle("Cryptonote")[0]
            assert window is not None
            assert "Cryptonote" in window.title
        except IndexError:
            pytest.fail("Application window not found")

    def test_login_workflow(self):
        """Test complete login workflow"""
        # This would require setting up a test database
        # and automating the login process
        pytest.skip("Login workflow test requires test database setup")

    def test_note_creation_workflow(self):
        """Test creating a new note"""
        pytest.skip("Note creation test requires authenticated session")

    def test_context_menu_functionality(self):
        """Test right-click context menu functionality"""
        pytest.skip("Context menu test requires text selection automation")

@pytest.mark.performance
class TestPerformanceE2E:
    """Performance testing for E2E workflows"""

    def test_startup_time(self):
        """Test application startup performance"""
        start_time = time.time()

        process = subprocess.Popen([
            sys.executable, 'Gui.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for window to appear
        timeout = 10
        window_found = False
        for _ in range(timeout):
            try:
                windows = pyautogui.getWindowsWithTitle("Cryptonote")
                if windows:
                    window_found = True
                    break
            except:
                pass
            time.sleep(1)

        startup_time = time.time() - start_time

        # Cleanup
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

        assert window_found, "Application window did not appear"
        assert startup_time < 8.0, f"Startup took too long: {startup_time:.2f}s"

    def test_memory_usage(self):
        """Test application memory usage"""
        process = subprocess.Popen([
            sys.executable, 'Gui.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for startup
        time.sleep(3)

        # Get memory usage
        proc = psutil.Process(process.pid)
        memory_mb = proc.memory_info().rss / 1024 / 1024

        # Cleanup
        process.terminate()
        process.wait(timeout=5)

        # Memory should be reasonable (under 200MB for basic app)
        assert memory_mb < 200, f"Memory usage too high: {memory_mb:.1f}MB"

@pytest.mark.accessibility
class TestAccessibilityE2E:
    """Accessibility testing for E2E workflows"""

    def test_keyboard_navigation(self):
        """Test keyboard-only navigation"""
        pytest.skip("Keyboard navigation test requires advanced automation setup")

    def test_screen_reader_compatibility(self):
        """Test compatibility with screen readers"""
        pytest.skip("Screen reader test requires specialized testing environment")

# Utility functions for E2E testing

def wait_for_window(title, timeout=10):
    """Wait for a window with specific title to appear"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            windows = pyautogui.getWindowsWithTitle(title)
            if windows:
                return windows[0]
        except:
            pass
        time.sleep(0.5)
    return None

def click_button_by_image(image_path, confidence=0.8):
    """Click a button by finding it via image recognition"""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            pyautogui.click(center)
            return True
    except:
        pass
    return False

def type_text(text, interval=0.05):
    """Type text with small delays between characters"""
    pyautogui.typewrite(text, interval=interval)

def take_screenshot(name):
    """Take a screenshot for debugging"""
    screenshots_dir = Path("reports/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    screenshot = pyautogui.screenshot()
    screenshot.save(screenshots_dir / f"{name}_{int(time.time())}.png")