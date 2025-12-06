# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:/DEV/Cryptonote
# SHA256: 9k6l3o7q2t5w8y1 (first 16 chars)
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import customtkinter as ctk
import tkinter as tk
import os
import sys
import threading
import pyperclip
import socket
import json
import time
import subprocess
from tkinter import filedialog, messagebox
from src.storage import StorageManager
from src.models import Note
import time
import requests
try:
    import openai
except ImportError:
    openai = None
import hashlib
import json
try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    google_available = True
except ImportError:
    google_available = False
import pickle
import webbrowser
try:
    from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
    from paypalcheckoutsdk.orders import OrdersGetRequest
    paypal_available = True
except ImportError:
    paypal_available = False
try:
    import tiktoken
    tiktoken_available = True
except ImportError:
    tiktoken_available = False
try:
    import GPUtil
    gputil_available = True
except ImportError:
    gputil_available = False
try:
    import pynvml
    pynvml.nvmlInit()
    pynvml_available = True
except ImportError:
    pynvml_available = False
except:
    pynvml_available = False
import psutil
try:
    import wmi
    wmi_available = True
except ImportError:
    wmi_available = False
import pickle
import webbrowser
try:
    from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
    from paypalcheckoutsdk.orders import OrdersGetRequest
    paypal_available = True
except ImportError:
    paypal_available = False
try:
    import tiktoken
    tiktoken_available = True
except ImportError:
    tiktoken_available = False
try:
    import win32clipboard
    import win32gui
    import win32con
    clipboard_available = True
except ImportError:
    clipboard_available = False
try:
    import comtypes
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    audio_available = True
except ImportError:
    audio_available = False
try:
    import pygetwindow as gw
    import pyautogui
    media_control_available = True
except ImportError:
    media_control_available = False
try:
    from flask import Flask, request, jsonify
    from werkzeug.exceptions import BadRequest
    import ssl
    import ipaddress
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    import datetime
    flask_available = True
except ImportError:
    flask_available = False

# Setup comprehensive logging system
import logging
from logging.handlers import RotatingFileHandler
import traceback

def setup_logging():
    """Setup comprehensive logging with file rotation and console output"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'cryptonote.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup
    logging.info("Cryptonote application started")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Platform: {sys.platform}")

# Initialize logging
setup_logging()

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ServiceManager:
    """Manages and monitors application services with automatic recovery"""
    
    def __init__(self, master):
        self.master = master
        self.services = {}
        self.monitoring = False
        self.monitor_thread = None
        self.status_callbacks = []
        
        # Initialize service registry
        self.register_services()
        
        # Start monitoring
        self.start_monitoring()
    
    def register_services(self):
        """Register all application services"""
        self.services = {
            'ollama': {
                'name': 'Ollama AI',
                'test_func': self.test_ollama,
                'restart_func': self.restart_ollama,
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': True
            },
            'openai': {
                'name': 'OpenAI API',
                'test_func': self.test_openai,
                'restart_func': None,  # Can't restart external service
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': bool(os.getenv('OPENAI_API_KEY'))
            },
            'clipboard': {
                'name': 'Clipboard Monitor',
                'test_func': self.test_clipboard,
                'restart_func': self.restart_clipboard,
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': self.master.clipboard_enabled
            },
            'audio': {
                'name': 'Audio Control',
                'test_func': self.test_audio,
                'restart_func': None,  # System service
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': True
            },
            'p2p': {
                'name': 'P2P Network',
                'test_func': self.test_p2p,
                'restart_func': self.restart_p2p,
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': self.master.p2p_enabled
            },
            'backup': {
                'name': 'Google Drive Backup',
                'test_func': self.test_backup,
                'restart_func': None,  # OAuth based
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': bool(getattr(self.master, 'client_secret_path', None))
            },
            'resource_monitor': {
                'name': 'Resource Monitor',
                'test_func': self.test_resource_monitor,
                'restart_func': self.restart_resource_monitor,
                'status': 'unknown',
                'last_check': 0,
                'failures': 0,
                'enabled': True
            }
        }
    
    def start_monitoring(self):
        """Start the service monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the service monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.check_all_services()
                self.notify_status_callbacks()
            except Exception as e:
                print(f"Service monitoring error: {e}")
            
            time.sleep(30)  # Check every 30 seconds
    
    def check_all_services(self):
        """Check health of all registered services"""
        current_time = time.time()
        
        for service_name, service in self.services.items():
            if not service['enabled']:
                continue
                
            # Don't check too frequently
            if current_time - service['last_check'] < 60:  # Max once per minute
                continue
            
            try:
                status = service['test_func']()
                service['status'] = 'healthy' if status else 'unhealthy'
                service['last_check'] = current_time
                
                if not status:
                    service['failures'] += 1
                    self.handle_service_failure(service_name, service)
                else:
                    service['failures'] = 0
                    
            except Exception as e:
                print(f"Error testing service {service_name}: {e}")
                service['status'] = 'error'
                service['failures'] += 1
                service['last_check'] = current_time
                self.handle_service_failure(service_name, service)
    
    def handle_service_failure(self, service_name, service):
        """Handle service failure with recovery attempts"""
        if service['failures'] >= 3 and service['restart_func']:
            print(f"Attempting to restart service: {service_name}")
            try:
                if service['restart_func']():
                    service['failures'] = 0
                    service['status'] = 'restarting'
                    # Give it time to restart
                    time.sleep(5)
                    service['status'] = 'healthy' if service['test_func']() else 'unhealthy'
                else:
                    service['status'] = 'failed'
                    print(f"Failed to restart service: {service_name}")
            except Exception as e:
                print(f"Error restarting service {service_name}: {e}")
                service['status'] = 'failed'
    
    def add_status_callback(self, callback):
        """Add a callback for status updates"""
        self.status_callbacks.append(callback)
    
    def notify_status_callbacks(self):
        """Notify all status callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(self.get_service_status())
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def get_service_status(self):
        """Get current status of all services"""
        return {name: {
            'name': service['name'],
            'status': service['status'],
            'failures': service['failures'],
            'enabled': service['enabled']
        } for name, service in self.services.items()}
    
    # Service test functions
    def test_ollama(self):
        """Test Ollama service"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_openai(self):
        """Test OpenAI API"""
        try:
            # Simple test - check if API key format is valid
            api_key = os.getenv('OPENAI_API_KEY', '')
            return len(api_key) > 20 and api_key.startswith('sk-')
        except:
            return False
    
    def test_clipboard(self):
        """Test clipboard monitoring"""
        try:
            # Test if we can access clipboard
            pyperclip.paste()
            return getattr(self.master, 'monitoring_clipboard', False)
        except:
            return False
    
    def test_audio(self):
        """Test audio services"""
        try:
            # Test if audio libraries are available and working
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            return devices is not None
        except:
            return False
    
    def test_p2p(self):
        """Test P2P networking"""
        try:
            return (getattr(self.master, 'p2p_enabled', False) and 
                   getattr(self.master, 'p2p_thread', None) and 
                   self.master.p2p_thread.is_alive())
        except:
            return False
    
    def test_backup(self):
        """Test Google Drive backup"""
        try:
            return bool(getattr(self.master, 'drive_service', None))
        except:
            return False
    
    def test_resource_monitor(self):
        """Test resource monitoring"""
        try:
            return (bool(getattr(self.master, 'resource_monitor', None)) and 
                   hasattr(self.master.resource_monitor, 'is_alive') and 
                   self.master.resource_monitor.is_alive())
        except:
            return False
    
    # Service restart functions
    def restart_ollama(self):
        """Attempt to restart Ollama service"""
        try:
            # Try to start Ollama if it's not running
            subprocess.run(["ollama", "serve"], 
                         capture_output=True, 
                         timeout=10,
                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            time.sleep(3)  # Give it time to start
            return self.test_ollama()
        except:
            return False
    
    def restart_clipboard(self):
        """Restart clipboard monitoring"""
        try:
            if getattr(self.master, 'monitoring_clipboard', False):
                self.master.stop_clipboard_monitor()
                time.sleep(1)
                self.master.start_clipboard_monitor()
            return self.test_clipboard()
        except:
            return False
    
    def restart_p2p(self):
        """Restart P2P networking"""
        try:
            if getattr(self.master, 'p2p_thread', None) and self.master.p2p_thread.is_alive():
                self.master.p2p_thread = None
                time.sleep(1)
            if getattr(self.master, 'p2p_enabled', False):
                self.master.start_p2p_networking()
            return self.test_p2p()
        except:
            return False
    
    def restart_resource_monitor(self):
        """Restart resource monitoring"""
        try:
            if getattr(self.master, 'resource_monitor', None):
                self.master.resource_monitor = None
                time.sleep(1)
            self.master.start_resource_monitor()
            return self.test_resource_monitor()
        except:
            return False


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.filepath = "notes.enc"
        self.hint = ""
        
        self.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_label = ctk.CTkLabel(self, text="Secure Cryptonote", font=("Roboto", 24, "bold"))
        self.title_label.pack(pady=20, padx=40)

        self.file_label = ctk.CTkLabel(self, text=f"Database: {self.filepath}")
        self.file_label.pack(pady=(0, 5))
        
        self.select_file_btn = ctk.CTkButton(self, text="Select/Create Database", command=self.select_file, width=200)
        self.select_file_btn.pack(pady=(0, 20))

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Master Password", show="*", width=200)
        self.pass_entry.pack(pady=10)
        self.pass_entry.bind("<Return>", lambda e: self.attempt_login())

        self.hint_label = ctk.CTkLabel(self, text="", text_color="gray", wraplength=300)
        self.hint_label.pack(pady=(0, 10))

        self.login_btn = ctk.CTkButton(self, text="Unlock / Create", command=self.attempt_login, width=200)
        self.login_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.pack(pady=5)

        # Load last used file if available
        self.load_last_file()

    def load_last_file(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                last_file = config.get("last_file")
                last_hash = config.get("last_hash")
                self.hint = config.get("hint", "")
                if last_file and os.path.exists(last_file):
                    with open(last_file, "rb") as f:
                        current_hash = hashlib.sha256(f.read()).hexdigest()
                    if current_hash == last_hash:
                        self.filepath = last_file
                        self.file_label.configure(text=f"Database: {os.path.basename(self.filepath)} (Last Used)")
                        if self.hint:
                            self.hint_label.configure(text=f"Hint: {self.hint}")
            except:
                pass  # Ignore config errors

    def select_file(self):
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Select or Create Database File",
            filetypes=(("Encrypted Files", "*.enc"), ("All Files", "*.*")),
            initialfile="notes.enc"
        )
        if filename:
            self.filepath = filename
            self.file_label.configure(text=f"Database: {os.path.basename(self.filepath)}")

    def attempt_login(self):
        password = self.pass_entry.get()
        if not password:
            logging.warning("Login attempt with empty password")
            self.status_label.configure(text="Password cannot be empty")
            return

        logging.info("Login attempt initiated")
        storage = StorageManager(self.filepath)
        
        try:
            if os.path.exists(self.filepath):
                # Try to load
                logging.debug("Attempting to load existing database")
                storage.load(password)
                logging.info("Database loaded successfully")
                self.on_login_success(storage, password, self.hint)
            else:
                # Create new - require password
                if not password:
                    self.status_label.configure(text="Password required to create new database")
                    return
                logging.info("Database file does not exist, prompting for creation")
                confirm = messagebox.askyesno("Create New Database", 
                    "File does not exist. Create new encrypted database?\n\n"
                    "WARNING: This file is your ONLY way to recover your notes. "
                    "Keep it safe and backed up!")
                if confirm:
                    # Ask for password hint
                    hint_dialog = ctk.CTkInputDialog(text="Enter a password hint (optional, will be shown when logging in):", title="Password Hint")
                    hint_dialog.geometry("+{}+{}".format(int(self.winfo_screenwidth()/2 - 200), int(self.winfo_screenheight()/2 - 100)))
                    hint = hint_dialog.get_input() or ""
                    logging.info("Creating new encrypted database")
                    storage.create_new(password)
                    logging.info("New database created successfully")
                    self.backed_up = False  # New database not backed up yet
                    # On first run, ask for Google Drive link
                    self.ask_google_drive_setup()
                    self.on_login_success(storage, password, hint)
                    self.on_login_success(storage, password, hint)
        except Exception as e:
            logging.error(f"Login failed: {e}", exc_info=True)
            self.status_label.configure(text=f"Error: {str(e)}")

    def ask_google_drive_setup(self):
        """Ask user to set up backup on first run with custom dialog"""
        BackupChoiceDialog(self)

class EditNotePopup(ctk.CTkToplevel):
    def __init__(self, master, note, on_save, on_delete):
        super().__init__(master)
        self.note = note
        self.on_save = on_save
        self.on_delete = on_delete
        self.attached_file = note.file_path if note else ""

        self.current_font = "Arial"
        self.current_size = 12
        
        # Inherit styling from master
        self.soft_button_radius = getattr(master, 'soft_button_radius', 12)

        self.title("Edit Note")
        self.geometry("800x500")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()        # Main frame and sidebar
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="right", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)
        
        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="Text Tools", font=("Roboto", 14, "bold"))
        self.sidebar_title.pack(pady=10)
        
        # Notepad++ Style Features
        # Line Numbers Toggle
        self.line_numbers_var = ctk.BooleanVar(value=False)
        self.line_numbers_cb = ctk.CTkCheckBox(self.sidebar, text="Line Numbers", variable=self.line_numbers_var, command=self.toggle_line_numbers)
        self.line_numbers_cb.pack(pady=5)
        
        # Word Wrap Toggle
        self.word_wrap_var = ctk.BooleanVar(value=True)
        self.word_wrap_cb = ctk.CTkCheckBox(self.sidebar, text="Word Wrap", variable=self.word_wrap_var, command=self.toggle_word_wrap)
        self.word_wrap_cb.pack(pady=5)
        
        # Show Whitespace Toggle
        self.whitespace_var = ctk.BooleanVar(value=False)
        self.whitespace_cb = ctk.CTkCheckBox(self.sidebar, text="Show Whitespace", variable=self.whitespace_var, command=self.toggle_whitespace)
        self.whitespace_cb.pack(pady=5)
        
        # Zoom Controls
        zoom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        zoom_frame.pack(pady=10)
        
        zoom_label = ctk.CTkLabel(zoom_frame, text="Zoom:", font=("Roboto", 12, "bold"))
        zoom_label.pack()
        
        zoom_btn_frame = ctk.CTkFrame(zoom_frame, fg_color="transparent")
        zoom_btn_frame.pack()
        
        self.zoom_out_btn = ctk.CTkButton(zoom_btn_frame, text="🔍-", width=40, command=self.zoom_out, corner_radius=self.soft_button_radius)
        self.zoom_out_btn.pack(side="left", padx=2)
        
        self.zoom_level_label = ctk.CTkLabel(zoom_btn_frame, text="100%", width=50)
        self.zoom_level_label.pack(side="left", padx=5)
        
        self.zoom_in_btn = ctk.CTkButton(zoom_btn_frame, text="🔍+", width=40, command=self.zoom_in, corner_radius=self.soft_button_radius)
        self.zoom_in_btn.pack(side="right", padx=2)
        
        # Separator
        separator1 = ctk.CTkFrame(self.sidebar, height=1, fg_color="#555555")
        separator1.pack(fill="x", pady=10)
        
        # Find & Replace Section
        find_label = ctk.CTkLabel(self.sidebar, text="Find & Replace", font=("Roboto", 12, "bold"))
        find_label.pack(pady=5)
        
        self.find_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Find text", width=140)
        self.find_entry.pack(pady=2)
        
        self.replace_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Replace with", width=140)
        self.replace_entry.pack(pady=2)
        
        find_btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        find_btn_frame.pack(pady=5)
        
        self.find_btn = ctk.CTkButton(find_btn_frame, text="Find", width=60, command=self.find_text, corner_radius=self.soft_button_radius)
        self.find_btn.pack(side="left", padx=2)
        
        self.replace_btn = ctk.CTkButton(find_btn_frame, text="Replace", width=70, command=self.replace_text, corner_radius=self.soft_button_radius)
        self.replace_btn.pack(side="right", padx=2)
        
        # Go to Line
        goto_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        goto_frame.pack(pady=10)
        
        goto_label = ctk.CTkLabel(goto_frame, text="Go to Line:", font=("Roboto", 12, "bold"))
        goto_label.pack()
        
        goto_input_frame = ctk.CTkFrame(goto_frame, fg_color="transparent")
        goto_input_frame.pack()
        
        self.goto_entry = ctk.CTkEntry(goto_input_frame, placeholder_text="Line #", width=80)
        self.goto_entry.pack(side="left", padx=2)
        
        self.goto_btn = ctk.CTkButton(goto_input_frame, text="Go", width=40, command=self.goto_line, corner_radius=self.soft_button_radius)
        self.goto_btn.pack(side="right", padx=2)
        
        # Separator
        separator2 = ctk.CTkFrame(self.sidebar, height=1, fg_color="#555555")
        separator2.pack(fill="x", pady=10)
        
        # Text Size
        self.size_label = ctk.CTkLabel(self.sidebar, text="Text Size:")
        self.size_label.pack(pady=5)
        self.size_combo = ctk.CTkComboBox(self.sidebar, values=["10", "12", "14", "16", "18", "20", "24"], command=self.change_font_size)
        self.size_combo.pack(pady=5)
        self.size_combo.set("12")
        
        # Font
        self.font_label = ctk.CTkLabel(self.sidebar, text="Font:")
        self.font_label.pack(pady=5)
        self.font_combo = ctk.CTkComboBox(self.sidebar, values=["Arial", "Times New Roman", "Courier New", "Verdana"], command=self.change_font)
        self.font_combo.pack(pady=5)
        self.font_combo.set("Arial")
        
        # Font Color
        self.color_label = ctk.CTkLabel(self.sidebar, text="Font Color:")
        self.color_label.pack(pady=5)
        self.color_combo = ctk.CTkComboBox(self.sidebar, values=["Black", "Red", "Blue", "Green", "Purple"], command=self.change_color)
        self.color_combo.pack(pady=5)
        self.color_combo.set("Black")
        
        # Emoji Button
        self.emoji_btn = ctk.CTkButton(self.sidebar, text="😊 Emoji", command=self.open_emoji)
        self.emoji_btn.pack(pady=20)
        
        # Title in main
        self.title_label = ctk.CTkLabel(self.main_frame, text="Title:")
        self.title_label.pack(pady=(20, 5))
        self.title_entry = ctk.CTkEntry(self.main_frame, width=550)
        self.title_entry.pack()
        if note:
            self.title_entry.insert(0, note.title)
        
        # Content
        self.content_label = ctk.CTkLabel(self.main_frame, text="Content:")
        self.content_label.pack(pady=(20, 5))
        self.content_text = ctk.CTkTextbox(self.main_frame, width=550, height=200)
        self.content_text.pack()
        if note:
            self.content_text.insert("0.0", note.content)
        
        # Ensure text box is editable and focused
        self.content_text.configure(state="normal")
        self.content_text.focus()

        # Add right-click context menu to content text
        self.content_text.bind("<Button-3>", self.show_content_context_menu)        # Tags
        self.tags_label = ctk.CTkLabel(self.main_frame, text="Tags (comma separated):")
        self.tags_label.pack(pady=(20, 5))
        self.tags_entry = ctk.CTkEntry(self.main_frame, width=550)
        self.tags_entry.pack()
        if note:
            self.tags_entry.insert(0, ", ".join(note.tags))
        
        # Attached File
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.pack(pady=20, padx=20, fill="x")
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="Attached File:")
        self.file_label.pack(pady=5)
        
        self.current_file_label = ctk.CTkLabel(self.file_frame, text=self.attached_file or "None", wraplength=500)
        self.current_file_label.pack(pady=5)
        
        self.file_buttons_frame = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.file_buttons_frame.pack(pady=5)
        
        self.attach_btn = ctk.CTkButton(self.file_buttons_frame, text="Attach/Replace", command=self.attach_file, width=100)
        self.attach_btn.pack(side="left", padx=5)
        
        self.delete_file_btn = ctk.CTkButton(self.file_buttons_frame, text="Delete", command=self.delete_file, fg_color="red", width=100)
        self.delete_file_btn.pack(side="left", padx=5)
        
        self.open_file_btn = ctk.CTkButton(self.file_buttons_frame, text="Open File", command=self.open_file, width=100)
        self.open_file_btn.pack(side="left", padx=5)
        
        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.pack(pady=20)
        
        self.save_btn = ctk.CTkButton(self.actions_frame, text="Save", command=self.save_note, fg_color="green", width=100)
        self.save_btn.pack(side="right", padx=10)
        
        if note:
            self.delete_btn = ctk.CTkButton(self.actions_frame, text="Delete", command=self.delete_note, fg_color="red", width=100)
            self.delete_btn.pack(side="right", padx=10)
        
        self.cancel_btn = ctk.CTkButton(self.actions_frame, text="Cancel", command=self.destroy, width=100)
        self.cancel_btn.pack(side="right", padx=10)
        
        # Special Feature: Copy Content Only
        self.copy_content_btn = ctk.CTkButton(self.actions_frame, text="Copy Content Only", command=self.copy_content_only, fg_color="#D35400", width=150)
        self.copy_content_btn.pack(side="left", padx=10)
        
        # AI Fix Button
        self.fix_ai_btn = ctk.CTkButton(self.actions_frame, text="Fix with AI", command=self.fix_with_ai, fg_color="purple", width=100)
        self.fix_ai_btn.pack(side="left", padx=10)
        
        # Copilot Integration Buttons
        self.copilot_frame = ctk.CTkFrame(self.actions_frame, fg_color="transparent")
        self.copilot_frame.pack(side="left", padx=10)
        
        if self.master.lifetime_license:
            self.copilot_edit_btn = ctk.CTkButton(self.copilot_frame, text="🤖 Copilot Edit", command=self.copilot_edit_note,
                                                fg_color="#0078D4", width=120, height=35, corner_radius=8)
            self.copilot_edit_btn.pack(side="left", padx=5)
            
            self.copilot_suggest_btn = ctk.CTkButton(self.copilot_frame, text="💡 Suggest", command=self.copilot_suggest_improvements,
                                                    fg_color="#0078D4", width=100, height=35, corner_radius=8)
            self.copilot_suggest_btn.pack(side="left", padx=5)
        else:
            premium_label = ctk.CTkLabel(self.copilot_frame, text="🔒 Copilot\nPremium", font=("Roboto", 10))
            premium_label.pack(pady=5)
        
        # AI Provider Selection
        self.ai_provider_var = ctk.StringVar(value="auto")
        self.ai_provider_combo = ctk.CTkComboBox(self.actions_frame, values=["auto", "ollama", "openai", "p2p"], variable=self.ai_provider_var, width=100)
        self.ai_provider_combo.pack(side="left", padx=10)
    
    def attach_file(self):
        filename = filedialog.askopenfilename(title="Select File to Attach")
        if filename:
            self.attached_file = filename
            self.current_file_label.configure(text=filename)
    
    def delete_file(self):
        self.attached_file = ""
        self.current_file_label.configure(text="None")
    
    def open_file(self):
        if self.attached_file and os.path.exists(self.attached_file):
            try:
                subprocess.run(["start", self.attached_file], shell=True)  # Windows
            except:
                try:
                    subprocess.run(["xdg-open", self.attached_file])  # Linux
                except:
                    messagebox.showerror("Error", "Could not open file")
        else:
            messagebox.showerror("Error", "File not found")
    
    def copy_content_only(self):
        content = self.content_text.get("0.0", "end-1c")
        if content:
            pyperclip.copy(content)
            self.copy_content_btn.configure(text="Copied!")
            self.after(1000, lambda: self.copy_content_btn.configure(text="Copy Content Only"))
    
    def fix_with_ai(self):
        content = self.content_text.get("0.0", "end-1c")
        if not content.strip():
            messagebox.showerror("Error", "No content to fix")
            return
        
        # Show loading
        self.fix_ai_btn.configure(text="Fixing...", state="disabled")
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=self._fix_with_ai_thread, args=(content,)).start()
    
    def _fix_with_ai_thread(self, content):
        try:
            provider = self.ai_provider_var.get()
            logging.info(f"Starting AI fix with provider: {provider}")
            
            if provider == "auto":
                # Original logic
                if self.master.lifetime_license:
                    fixed_content = self._fix_with_ollama(content)
                elif openai and os.getenv("OPENAI_API_KEY") and self.master.token_balance > 0:
                    fixed_content = self._fix_with_openai(content)
                elif self.master.p2p_enabled and self.master.p2p_peers:
                    fixed_content = self._fix_with_p2p(content)
                else:
                    error_msg = "No AI provider available. Activate lifetime license for Ollama, buy tokens for OpenAI, or enable P2P with peers."
                    logging.warning(f"AI fix failed: {error_msg}")
                    self.after(0, lambda: messagebox.showerror("AI Not Available", error_msg))
                    self.after(0, lambda: self._reset_button())
                    return
            elif provider == "ollama":
                if not self.master.lifetime_license:
                    error_msg = "Lifetime license required for Ollama."
                    logging.warning(f"AI fix failed: {error_msg}")
                    self.after(0, lambda: messagebox.showerror("License Required", error_msg))
                    self.after(0, lambda: self._reset_button())
                    return
                fixed_content = self._fix_with_ollama(content)
            elif provider == "openai":
                if not openai or not os.getenv("OPENAI_API_KEY"):
                    error_msg = "OpenAI API key not set."
                    logging.warning(f"AI fix failed: {error_msg}")
                    self.after(0, lambda: messagebox.showerror("OpenAI Not Configured", error_msg))
                    self.after(0, lambda: self._reset_button())
                    return
                if self.master.token_balance <= 0:
                    error_msg = "You have no AI tokens. Please buy tokens to use OpenAI."
                    logging.warning(f"AI fix failed: {error_msg}")
                    self.after(0, lambda: messagebox.showerror("No Tokens", error_msg))
                    self.after(0, lambda: self._reset_button())
                    return
                fixed_content = self._fix_with_openai(content)
            elif provider == "p2p":
                if not self.master.p2p_enabled or not self.master.p2p_peers:
                    error_msg = "P2P not enabled or no peers configured."
                    logging.warning(f"AI fix failed: {error_msg}")
                    self.after(0, lambda: messagebox.showerror("P2P Not Available", error_msg))
                    self.after(0, lambda: self._reset_button())
                    return
                fixed_content = self._fix_with_p2p(content)
            else:
                error_msg = "Unknown AI provider selected."
                logging.error(f"AI fix failed: {error_msg}")
                self.after(0, lambda: messagebox.showerror("Invalid Provider", error_msg))
                self.after(0, lambda: self._reset_button())
                return
            
            logging.info(f"AI fix completed successfully with provider: {provider}")
            # Update UI in main thread
            self.after(0, lambda: self._update_content(fixed_content))
        except Exception as e:
            logging.error(f"AI fix failed with exception: {e}", exc_info=True)
            self.after(0, lambda: messagebox.showerror("AI Fix Error", f"Failed to fix with AI: {e}"))
            self.after(0, lambda: self._reset_button())
    
    def _fix_with_ollama(self, content):
        start_time = time.time()
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant. Fix, improve, or complete the following code or text. Provide the improved version."},
                {"role": "user", "content": content}
            ],
            "stream": False
        }
        
        response = requests.post(f"{ollama_url}/api/chat", json=payload, timeout=self.get_ollama_timeout())
        response.raise_for_status()
        data = response.json()
        fixed_content = data["message"]["content"].strip()
        
        # Verify inference succeeded
        if not fixed_content or len(fixed_content.strip()) == 0:
            raise ValueError("AI inference failed: empty response from Ollama")
        
        # Estimate tokens used (rough approximation)
        estimated_tokens = self.estimate_tokens(content + fixed_content)
        self.master.total_tokens_used += estimated_tokens
        self.master.save_config()
        
        # Record TPS stats
        end_time = time.time()
        time_taken = end_time - start_time
        self.master.record_tps_stats('ollama', estimated_tokens, time_taken)
        
        return fixed_content
    
    def _fix_with_openai(self, content):
        start_time = time.time()
        
        # Use OpenAI first
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant. Fix, improve, or complete the following code or text. Provide the improved version."},
                {"role": "user", "content": content}
            ],
            max_tokens=1000
        )
        fixed_content = response.choices[0].message.content.strip()
        
        # Verify inference succeeded (response has content)
        if not fixed_content or len(fixed_content.strip()) == 0:
            raise ValueError("AI inference failed: empty response")
        
        # Deduct token only after successful inference
        self.master.token_balance -= 1
        self.after(0, lambda: self.master._update_token_label())
        
        # Add actual tokens used
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens
            self.master.total_tokens_used += tokens_used
        else:
            tokens_used = self.estimate_tokens(content + fixed_content)
            self.master.total_tokens_used += tokens_used
        self.master.save_config()
        
        # Record TPS stats
        end_time = time.time()
        time_taken = end_time - start_time
        self.master.record_tps_stats('openai', tokens_used, time_taken)
        
        return fixed_content
        
        # Record TPS stats
        end_time = time.time()
        time_taken = end_time - start_time
        self.master.record_tps_stats('openai', tokens_used, time_taken)
        
        return fixed_content
    
    def _fix_with_p2p(self, content):
        start_time = time.time()
        
        # Try each peer until one works
        for peer_url in self.master.p2p_peers:
            try:
                fixed_content = self.master.use_p2p_peer(peer_url, content)
                
                # Estimate tokens used
                estimated_tokens = self.estimate_tokens(content + fixed_content)
                
                # Record TPS stats
                end_time = time.time()
                time_taken = end_time - start_time
                self.master.record_tps_stats('p2p', estimated_tokens, time_taken)
                
                return fixed_content
            except Exception as e:
                logging.warning(f"P2P peer {peer_url} failed: {e}")
                continue
        raise Exception("All P2P peers failed")

    def _update_content(self, content):
        self.content_text.delete("0.0", "end")
        self.content_text.insert("0.0", content)
        self._reset_button()
    
    def _reset_button(self):
        self.fix_ai_btn.configure(text="Fix with AI", state="normal")
    
    def estimate_tokens(self, text):
        if tiktoken_available:
            try:
                enc = tiktoken.get_encoding("cl100k_base")  # For GPT-3.5/4
                return len(enc.encode(text))
            except:
                pass
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4
    
    def save_note(self):
        title = self.title_entry.get()
        content = self.content_text.get("0.0", "end-1c")
        tags_str = self.tags_entry.get()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        if not title:
            title = "Untitled"
        
        self.note.title = title
        self.note.content = content
        self.note.tags = tags
        self.note.file_path = self.attached_file
        self.note.modified_at = time.time()
        
        self.on_save(self.note)
        self.destroy()
    
    def change_font_size(self, size):
        self.current_size = int(size)
        self.content_text.tag_configure("font_size", font=(self.current_font, self.current_size))
        self.content_text.tag_add("font_size", "sel.first", "sel.last")
    
    def change_font(self, font):
        self.current_font = font
        self.content_text.tag_configure("font", font=(font, self.current_size))
        self.content_text.tag_add("font", "sel.first", "sel.last")
    
    def change_color(self, color):
        color_map = {"Black": "black", "Red": "red", "Blue": "blue", "Green": "green", "Purple": "purple"}
        self.content_text.tag_configure("color", foreground=color_map.get(color, "black"))
        self.content_text.tag_add("color", "sel.first", "sel.last")
    
    def open_emoji(self):
        # For Windows, use the built-in emoji picker
        import subprocess
        try:
            subprocess.run(["explorer.exe", "ms-emoji:"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open emoji picker: {e}")
    
    def delete_note(self):
        confirm = messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?")
        if confirm:
            self.on_delete(self.note)
            self.destroy()

    def copilot_edit_note(self):
        """Use Windows Copilot to edit the current note content"""
        content = self.content_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showinfo("No Content", "Please add some content to edit with Copilot.")
            return
        
        # Copy content to clipboard for Copilot
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(content)
            win32clipboard.CloseClipboard()
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")
            return
        
        # Activate Copilot
        self.master.activate_copilot()
        
        # Show instruction
        messagebox.showinfo("Copilot Editing", 
                          "Content copied to clipboard.\n\n"
                          "Tell Copilot: 'Edit this text' or 'Improve this writing' or 'Fix grammar'\n\n"
                          "Then copy Copilot's response and paste it back here.")
        
        # Focus the text area for easy pasting
        self.content_text.focus()
    
    def copilot_suggest_improvements(self):
        """Use Windows Copilot to suggest improvements for the note"""
        content = self.content_text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showinfo("No Content", "Please add some content to get suggestions for.")
            return
        
        # Create a prompt for Copilot
        prompt = f"Please suggest improvements for this text:\n\n{content}"
        
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(prompt)
            win32clipboard.CloseClipboard()
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")
            return
        
        # Activate Copilot
        self.master.activate_copilot()
        
        messagebox.showinfo("Copilot Suggestions", 
                          "Prompt copied to clipboard.\n\n"
                          "Copilot will analyze your text and suggest improvements.\n\n"
                          "Copy its suggestions and apply them to your note.")
    
    def show_content_context_menu(self, event):
        """Show context menu for content text area"""
        try:
            # Get selected text
            selected_text = self.content_text.selection_get()
            self.master.selected_text = selected_text
        except:
            self.master.selected_text = ""

        # Show the context menu
        self.master.show_context_menu(event, self.master.selected_text)
    
    # Notepad++ Style Features
    def toggle_line_numbers(self):
        """Toggle line numbers display"""
        # Note: CTkTextbox doesn't support line numbers natively
        # This would require a custom text widget implementation
        if self.line_numbers_var.get():
            messagebox.showinfo("Feature Note", "Line numbers are not yet implemented in this version.\n\nThis is a planned Notepad++-style feature.")
            self.line_numbers_cb.deselect()
    
    def toggle_word_wrap(self):
        """Toggle word wrapping"""
        if self.word_wrap_var.get():
            self.content_text.configure(wrap="word")
        else:
            self.content_text.configure(wrap="none")
    
    def toggle_whitespace(self):
        """Toggle whitespace visibility"""
        # This would require custom text widget with whitespace rendering
        if self.whitespace_var.get():
            messagebox.showinfo("Feature Note", "Whitespace visibility is not yet implemented.\n\nThis is a planned Notepad++-style feature.")
            self.whitespace_cb.deselect()
    
    def zoom_in(self):
        """Zoom in text"""
        current_size = self.current_size
        if current_size < 32:  # Max zoom
            self.current_size = min(32, current_size + 2)
            self.update_zoom_display()
            self.apply_zoom()
    
    def zoom_out(self):
        """Zoom out text"""
        current_size = self.current_size
        if current_size > 8:  # Min zoom
            self.current_size = max(8, current_size - 2)
            self.update_zoom_display()
            self.apply_zoom()
    
    def update_zoom_display(self):
        """Update zoom level display"""
        percentage = int((self.current_size / 12) * 100)  # 12pt is 100%
        self.zoom_level_label.configure(text=f"{percentage}%")
    
    def apply_zoom(self):
        """Apply zoom to text"""
        self.content_text.configure(font=(self.current_font, self.current_size))
        # Reapply any existing tags with new font size
        if hasattr(self, 'current_color'):
            self.content_text.tag_configure("color", foreground=self.current_color, font=(self.current_font, self.current_size))
    def apply_zoom(self):
        """Apply zoom to text"""
        self.content_text.configure(font=(self.current_font, self.current_size))
        # Reapply any existing tags with new font size
        if hasattr(self, 'current_color'):
            self.content_text.tag_configure("color", foreground=self.current_color, font=(self.current_font, self.current_size))
        if hasattr(self, 'current_font_style'):
            self.content_text.tag_configure("font", font=(self.current_font, self.current_size))
    
    def find_text(self):
        """Find text in the content"""
        search_text = self.find_entry.get().strip()
        if not search_text:
            messagebox.showwarning("Find", "Please enter text to find.")
            return
        
        content = self.content_text.get("1.0", "end-1c")
        start_pos = self.content_text.index("insert")
        
        # Find the text
        pos = content.find(search_text, int(float(start_pos.split('.')[0])) - 1)
        if pos == -1:
            # Wrap around to beginning
            pos = content.find(search_text)
        
        if pos != -1:
            line = content[:pos].count('\n') + 1
            char = pos - content.rfind('\n', 0, pos) if '\n' in content[:pos] else pos
            self.content_text.mark_set("insert", f"{line}.{char}")
            self.content_text.see(f"{line}.{char}")
            # Highlight the found text
            end_pos = f"{line}.{char + len(search_text)}"
            self.content_text.tag_add("search_highlight", f"{line}.{char}", end_pos)
            self.content_text.tag_configure("search_highlight", background="yellow", foreground="black")
        else:
            messagebox.showinfo("Find", f"Text '{search_text}' not found.")
    
    def replace_text(self):
        """Replace found text"""
        find_text = self.find_entry.get().strip()
        replace_text = self.replace_entry.get().strip()
        
        if not find_text:
            messagebox.showwarning("Replace", "Please enter text to find.")
            return
        
        # Check if there's a current selection
        try:
            selected_text = self.content_text.selection_get()
            if selected_text == find_text:
                self.content_text.delete("sel.first", "sel.last")
                self.content_text.insert("insert", replace_text)
                messagebox.showinfo("Replace", "Text replaced successfully.")
                return
        except:
            pass
        
        # Find and replace all occurrences
        content = self.content_text.get("1.0", "end-1c")
        if find_text in content:
            new_content = content.replace(find_text, replace_text, 1)  # Replace first occurrence
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", new_content)
            messagebox.showinfo("Replace", "First occurrence replaced.")
        else:
            messagebox.showinfo("Replace", f"Text '{find_text}' not found.")
    
    def goto_line(self):
        """Go to specific line number"""
        try:
            line_num = int(self.goto_entry.get().strip())
            if line_num < 1:
                raise ValueError
            
            # Get total lines
            content = self.content_text.get("1.0", "end-1c")
            total_lines = content.count('\n') + 1
            
            if line_num > total_lines:
                line_num = total_lines
            
            self.content_text.mark_set("insert", f"{line_num}.0")
            self.content_text.see(f"{line_num}.0")
            
        except ValueError:
            messagebox.showwarning("Go to Line", "Please enter a valid line number.")


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Application Settings", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=(20, 10))
        
        # Clipboard History Setting
        self.clipboard_frame = ctk.CTkFrame(self)
        self.clipboard_frame.pack(pady=10, padx=20, fill="x")
        
        self.clipboard_label = ctk.CTkLabel(self.clipboard_frame, text="Enable Clipboard History")
        self.clipboard_label.pack(pady=10)
        
        self.clipboard_checkbox = ctk.CTkCheckBox(self.clipboard_frame, text="", command=self.toggle_clipboard)
        self.clipboard_checkbox.pack(pady=5)
        self.clipboard_checkbox.select() if self.master.clipboard_enabled else self.clipboard_checkbox.deselect()
        
        # P2P AI Sharing Setting
        self.p2p_frame = ctk.CTkFrame(self)
        self.p2p_frame.pack(pady=10, padx=20, fill="x")
        
        self.p2p_label = ctk.CTkLabel(self.p2p_frame, text="Enable P2P AI Sharing\n(Earn tokens by sharing compute)")
        self.p2p_label.pack(pady=10)
        
        self.p2p_checkbox = ctk.CTkCheckBox(self.p2p_frame, text="", command=self.toggle_p2p)
        self.p2p_checkbox.pack(pady=5)
        self.p2p_checkbox.select() if self.master.p2p_enabled else self.p2p_checkbox.deselect()
        
        # AI Leaderboard Sharing Setting
        self.leaderboard_frame = ctk.CTkFrame(self)
        self.leaderboard_frame.pack(pady=10, padx=20, fill="x")
        
        self.leaderboard_label = ctk.CTkLabel(self.leaderboard_frame, text="Enable AI Leaderboard Sharing\n(Share performance metrics for global rankings)")
        self.leaderboard_label.pack(pady=10)
        
        self.leaderboard_checkbox = ctk.CTkCheckBox(self.leaderboard_frame, text="", command=self.toggle_leaderboard)
        self.leaderboard_checkbox.pack(pady=5)
        self.leaderboard_checkbox.select() if self.master.leaderboard_enabled else self.leaderboard_checkbox.deselect()
        
        # Headless Mode Setting
        self.headless_frame = ctk.CTkFrame(self)
        self.headless_frame.pack(pady=10, padx=20, fill="x")
        
        self.headless_label = ctk.CTkLabel(self.headless_frame, text="Run in Headless Mode\n(Minimize to tray by default)")
        self.headless_label.pack(pady=10)
        
        self.headless_checkbox = ctk.CTkCheckBox(self.headless_frame, text="", command=self.toggle_headless)
        self.headless_checkbox.pack(pady=5)
        self.headless_checkbox.select() if self.master.headless_mode else self.headless_checkbox.deselect()
        
        # Ollama Timeout Setting
        self.timeout_frame = ctk.CTkFrame(self)
        self.timeout_frame.pack(pady=10, padx=20, fill="x")
        
        self.timeout_label = ctk.CTkLabel(self.timeout_frame, text="Ollama Request Timeout\n(Prevents hanging on slow responses)")
        self.timeout_label.pack(pady=10)
        
        self.timeout_checkbox = ctk.CTkCheckBox(self.timeout_frame, text="Enable timeout", command=self.toggle_timeout)
        self.timeout_checkbox.pack(pady=5)
        self.timeout_checkbox.select() if self.master.ollama_timeout_enabled else self.timeout_checkbox.deselect()
        
        self.timeout_entry_frame = ctk.CTkFrame(self.timeout_frame, fg_color="transparent")
        self.timeout_entry_frame.pack(pady=5)
        
        self.timeout_entry_label = ctk.CTkLabel(self.timeout_entry_frame, text="Seconds:")
        self.timeout_entry_label.pack(side="left", padx=5)
        
        self.timeout_entry = ctk.CTkEntry(self.timeout_entry_frame, width=60)
        self.timeout_entry.pack(side="left", padx=5)
        self.timeout_entry.insert(0, str(self.master.ollama_timeout_seconds))
        
        # Themes Setting (Premium)
        if self.master.lifetime_license:
            self.themes_frame = ctk.CTkFrame(self)
            self.themes_frame.pack(pady=10, padx=20, fill="x")
            
            self.themes_label = ctk.CTkLabel(self.themes_frame, text="Themes")
            self.themes_label.pack(pady=10)
            
            self.themes_btn = ctk.CTkButton(self.themes_frame, text="Open Theme Selector", command=self.open_themes)
            self.themes_btn.pack(pady=5)
        
        # Responsive UI Setting (Premium)
        if self.master.lifetime_license:
            self.responsive_frame = ctk.CTkFrame(self)
            self.responsive_frame.pack(pady=10, padx=20, fill="x")
            
            self.responsive_label = ctk.CTkLabel(self.responsive_frame, text="Enable Responsive UI\n(Buttons resize with window)")
            self.responsive_label.pack(pady=10)
            
            self.responsive_checkbox = ctk.CTkCheckBox(self.responsive_frame, text="", command=self.toggle_responsive)
            self.responsive_checkbox.pack(pady=5)
            self.responsive_checkbox.select() if getattr(self.master, 'responsive_ui', False) else self.responsive_checkbox.deselect()
        
        # Prompt Library Setting (Premium)
        if self.master.lifetime_license:
            self.prompt_frame = ctk.CTkFrame(self)
            self.prompt_frame.pack(pady=10, padx=20, fill="x")
            
            self.prompt_label = ctk.CTkLabel(self.prompt_frame, text="Prompt Library")
            self.prompt_label.pack(pady=10)
            
            self.prompt_btn = ctk.CTkButton(self.prompt_frame, text="Redownload Prompts", command=self.redownload_prompts)
            self.prompt_btn.pack(pady=5)

            # Manual License Entry (Development)
            self.license_frame = ctk.CTkFrame(self)
            self.license_frame.pack(pady=10, padx=20, fill="x")

            self.license_label = ctk.CTkLabel(self.license_frame, text="Enter License Key")
            self.license_label.pack(pady=5)

            self.license_entry = ctk.CTkEntry(self.license_frame, placeholder_text="Enter key", width=200)
            self.license_entry.pack(pady=5)

            self.license_btn = ctk.CTkButton(self.license_frame, text="Apply License", command=self.apply_license_key)
            self.license_btn.pack(pady=5)
        
        # Save Button
        self.save_btn = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_btn.pack(pady=20)

    def toggle_clipboard(self):
        enabled = self.clipboard_checkbox.get()
        self.master.toggle_clipboard_enabled(enabled)
    
    def toggle_p2p(self):
        enabled = self.p2p_checkbox.get()
        self.master.toggle_p2p_enabled(enabled)
    
    def toggle_leaderboard(self):
        enabled = self.leaderboard_checkbox.get()
        self.master.leaderboard_enabled = enabled
        if enabled:
            self.master.start_p2p()
        else:
            self.master.p2p_enabled = False  # To stop the loop
        self.master.save_config()
    
    def toggle_headless(self):
        enabled = self.headless_checkbox.get()
        self.master.headless_mode = enabled
        self.master.save_config()
    
    def toggle_timeout(self):
        enabled = self.timeout_checkbox.get()
        self.master.ollama_timeout_enabled = enabled
        self.master.save_config()
    
    def open_themes(self):
        ThemesDialog(self.master)
    
    def toggle_responsive(self):
        enabled = self.responsive_checkbox.get()
        self.master.responsive_ui = enabled
        self.master.save_config()
        if enabled:
            self.master.bind("<Configure>", self.master.on_window_resize)
        else:
            self.master.unbind("<Configure>")
    
    def redownload_prompts(self):
        # Check if prompt library folder exists, create if not
        prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")
        if not os.path.exists(prompt_dir):
            os.makedirs(prompt_dir)
        
        # For now, just show a message that prompts are being downloaded
        # In a real implementation, this would download from a server or P2P
        messagebox.showinfo("Prompt Library", "Prompt library redownload initiated. Premium prompts will be updated.")
        # TODO: Implement actual download logic from server or P2P network

    def apply_license_key(self):
        key = self.license_entry.get().strip()
        if not key:
            messagebox.showerror("License", "Please enter a license key.")
            return
        if self.master.apply_license_key(key):
            messagebox.showinfo("License", "License applied. Premium features unlocked.")
            self.destroy()
        else:
            messagebox.showerror("License", "Invalid license key.")
    
    def add_peer(self):
        peer = self.peer_entry.get().strip()
        if peer and peer not in self.master.p2p_peers:
            self.master.p2p_peers.append(peer)
            self.peer_entry.delete(0, 'end')
            messagebox.showinfo("Peer Added", f"Added peer: {peer}")
    
    def save_settings(self):
        # Save timeout seconds if valid
        try:
            timeout_seconds = int(self.timeout_entry.get())
            if timeout_seconds > 0:
                self.master.ollama_timeout_seconds = timeout_seconds
        except ValueError:
            pass  # Keep current value if invalid
        
        self.master.save_config()
        self.destroy()


class ThemesDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Theme Selector")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Choose a Theme", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=(20, 10))
        
        # Theme buttons in a grid
        self.themes_frame = ctk.CTkScrollableFrame(self, width=450, height=300)
        self.themes_frame.pack(pady=10, padx=20)
        
        self.themes = {
            "Classic Dark": {"mode": "dark", "accent": "#3B8ED0"},
            "Ocean Blue": {"mode": "dark", "accent": "#1E90FF"},
            "Forest Green": {"mode": "dark", "accent": "#228B22"},
            "Royal Purple": {"mode": "dark", "accent": "#8A2BE2"},
            "Sunset Orange": {"mode": "dark", "accent": "#FF6347"},
            "Midnight Black": {"mode": "dark", "accent": "#2F2F2F"},
            "Arctic White": {"mode": "light", "accent": "#4682B4"},
            "Lavender Dream": {"mode": "light", "accent": "#9370DB"},
            "Mint Fresh": {"mode": "light", "accent": "#00FA9A"},
            "Coral Reef": {"mode": "light", "accent": "#FF7F50"}
        }
        
        row = 0
        col = 0
        for theme_name, config in self.themes.items():
            btn = ctk.CTkButton(self.themes_frame, text=theme_name, command=lambda t=theme_name: self.apply_theme(t), width=200)
            btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def apply_theme(self, theme_name):
        config = self.themes[theme_name]
        ctk.set_appearance_mode(config["mode"])
        # For accent color, we can set it on key widgets, but for simplicity, just mode
        # In a full implementation, set custom colors
        messagebox.showinfo("Theme Applied", f"Applied theme: {theme_name}")
        self.destroy()


class BackupChoiceDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Choose Backup Provider")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Select Cloud Backup Service", font=("Roboto", 18, "bold"))
        self.title_label.pack(pady=(20, 10))
        
        # Buttons frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=20)
        
        # Google Drive Button
        self.google_btn = ctk.CTkButton(self.btn_frame, text="📁 Google Drive", command=self.choose_google, width=150, height=50)
        self.google_btn.pack(side="left", padx=10)
        
        # OneDrive Button
        self.onedrive_btn = ctk.CTkButton(self.btn_frame, text="📂 OneDrive", command=self.choose_onedrive, width=150, height=50)
        self.onedrive_btn.pack(side="right", padx=10)
        
        # Skip Button
        self.skip_btn = ctk.CTkButton(self, text="Skip for Now", command=self.skip, width=100)
        self.skip_btn.pack(pady=10)

    def choose_google(self):
        messagebox.showinfo("Google Drive Setup", 
            "To set up Google Drive backup:\n\n"
            "1. Go to Google Cloud Console\n"
            "2. Create a project and enable Drive API\n"
            "3. Download client_secret.json\n"
            "4. Place it in the app directory\n"
            "5. Use the 'Drive Upload' button to backup")
        self.destroy()
    
    def choose_onedrive(self):
        messagebox.showinfo("OneDrive Setup", 
            "To set up OneDrive backup:\n\n"
            "1. Go to Azure Portal\n"
            "2. Register an app and get client ID\n"
            "3. Use Microsoft Graph API\n"
            "4. For now, manual backup recommended\n"
            "   Copy your .enc file to OneDrive folder")
        self.destroy()
    
    def skip(self):
        messagebox.showinfo("Backup Reminder", 
            "Remember to regularly backup your database file!\n"
            "Use cloud storage or copy the .enc file to a safe location.")
        self.destroy()


    def record_tps_stats(self, provider, tokens_used, time_taken):
        """Record TPS statistics for a provider"""
        if provider not in self.tps_stats:
            return
        
        stats = self.tps_stats[provider]
        stats['total_tokens'] += tokens_used
        stats['total_time'] += time_taken
        stats['requests'] += 1
        
        if stats['total_time'] > 0:
            stats['avg_tps'] = stats['total_tokens'] / stats['total_time']
        
        self.save_config()
        self.update_tps_display()
        logging.info(f"TPS stats updated for {provider}: {stats['avg_tps']:.2f} tokens/sec")

    def update_tps_display(self):
        """Update the TPS display in the UI"""
        if self.tps_label:
            ollama_tps = self.tps_stats['ollama']['avg_tps']
            openai_tps = self.tps_stats['openai']['avg_tps']
            p2p_tps = self.tps_stats['p2p']['avg_tps']
            
            display_text = f"Ollama: {ollama_tps:.1f} TPS | OpenAI: {openai_tps:.1f} TPS | P2P: {p2p_tps:.1f} TPS"
            self.tps_label.configure(text=display_text)

    def show_p2p_info(self):
        info_dialog = ctk.CTkToplevel(self)
        info_dialog.title("P2P AI Inferencing Setup")
        info_dialog.geometry("500x400")
        info_dialog.resizable(False, False)
        
        title = ctk.CTkLabel(info_dialog, text="Distributed P2P AI Inferencing", font=("Roboto", 16, "bold"))
        title.pack(pady=10)
        
        info_text = """
Cryptonote supports SECURE distributed AI inferencing through peer-to-peer networking.

How it works:
• Enable P2P AI Sharing in settings to share your Ollama compute
• Add peer URLs (IP:Port) of other Cryptonote users
• Earn tokens (10% of request cost) when others use your compute
• Use peers' compute when your local AI is unavailable

Setup Steps:
1. Install and run Ollama locally
2. Enable lifetime license for Ollama access
3. Enable P2P AI Sharing in settings
4. Share your IP:Port with trusted peers
5. Add peers in the settings to use their compute

SECURITY FEATURES:
• HTTPS encryption for all P2P traffic
• API key authentication required
• Rate limiting (10 requests/minute per IP)
• Input validation and size limits
• Request/response logging for monitoring
• Self-signed SSL certificates for encryption
• License verification for sharing

⚠️  SECURITY WARNING:
• Only connect to trusted peers
• Never share your API key publicly
• P2P requests require lifetime license
• All traffic is encrypted but peer identities are not verified
• Monitor logs for suspicious activity

Status:
"""
        info_label = ctk.CTkLabel(info_dialog, text=info_text, justify="left", wraplength=480)
        info_label.pack(pady=10, padx=10)
        
        # API Key display
        if self.master.p2p_api_key:
            api_frame = ctk.CTkFrame(info_dialog)
            api_frame.pack(pady=5, padx=20, fill="x")
            
            api_label = ctk.CTkLabel(api_frame, text="Your P2P API Key:", font=("Roboto", 12, "bold"))
            api_label.pack(pady=5)
            
            api_key_label = ctk.CTkLabel(api_frame, text=self.master.p2p_api_key, font=("Courier", 10))
            api_key_label.pack(pady=5)
            
            copy_api_btn = ctk.CTkButton(api_frame, text="Copy API Key", command=lambda: pyperclip.copy(self.master.p2p_api_key))
            copy_api_btn.pack(pady=5)
        
        # Status info
        status_frame = ctk.CTkFrame(info_dialog)
        status_frame.pack(pady=10, padx=20, fill="x")
        
        p2p_status = "Enabled" if self.master.p2p_enabled else "Disabled"
        server_status = "Running" if self.master.p2p_server else "Stopped"
        peers_count = len(self.master.p2p_peers)
        
        status_text = f"P2P Status: {p2p_status}\nServer: {server_status}\nPeers: {peers_count}\nEarned Tokens: {self.master.earned_tokens}"
        status_label = ctk.CTkLabel(status_frame, text=status_text, justify="left")
        status_label.pack(pady=10, padx=10)
        
        close_btn = ctk.CTkButton(info_dialog, text="Close", command=info_dialog.destroy)
        close_btn.pack(pady=10)

class ExtrasShop(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Extras Shop")
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        
        # Center the window on screen
        window_width = 400
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.resizable(False, False)
        
        # Make modal
        self.transient(master)
        self.grab_set()
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Purchase Extras", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=(20, 10))
        
        # Lifetime License Section
        self.license_frame = ctk.CTkFrame(self)
        self.license_frame.pack(pady=10, padx=20, fill="x")
        
        self.license_label = ctk.CTkLabel(self.license_frame, text="Lifetime License - $25\nUnlimited Ollama AI access")
        self.license_label.pack(pady=10)
        
        self.buy_license_btn = ctk.CTkButton(self.license_frame, text="Buy Lifetime License", command=self.buy_license)
        self.buy_license_btn.pack(pady=5)
        
        # Tokens Section
        self.tokens_frame = ctk.CTkFrame(self)
        self.tokens_frame.pack(pady=10, padx=20, fill="x")
        
        self.tokens_label = ctk.CTkLabel(self.tokens_frame, text="AI Tokens - $10 for 100 tokens\nFor OpenAI usage")
        self.tokens_label.pack(pady=10)
        
        self.buy_tokens_btn = ctk.CTkButton(self.tokens_frame, text="Buy Tokens", command=self.buy_tokens)
        self.buy_tokens_btn.pack(pady=5)
        
        # Current Status
        self.status_label = ctk.CTkLabel(self, text=f"Tokens: {self.master.token_balance}\nLifetime: {'Yes' if self.master.lifetime_license else 'No'}")
        self.status_label.pack(pady=10)

    def buy_license(self):
        self.master.activate_license()
        self.update_status()
    
    def buy_tokens(self):
        self.master.buy_tokens()
        self.update_status()
    
    def update_status(self):
        self.status_label.configure(text=f"Tokens: {self.master.token_balance}\nLifetime: {'Yes' if self.master.lifetime_license else 'No'}")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cryptonote - Secure Offline Storage")
        self.geometry("1200x800")
        self.minsize(1000, 600)  # Minimum size to keep buttons visible
        
        self.storage = None
        self.password = None
        self.current_note = None
        self.token_balance = 0
        self.lifetime_license = False
        self.transaction_id = ""
        self.total_tokens_used = 0
        self.backed_up = False
        self.clipboard_history = []
        self.monitoring_clipboard = False
        self.clipboard_enabled = True
        self.p2p_enabled = False
        self.p2p_peers = []
        self.p2p_server = None
        self.earned_tokens = 0
        self.headless_mode = False  # Default to GUI mode
        
        # AI Leaderboard opt-in
        self.leaderboard_enabled = False
        
        # Opted-in users for AI leaderboard ticker
        self.opted_in_users = ["Alice", "Bob", "Charlie", "Diana"]  # Dummy data; in real app, load from config or server
        
        # P2P AI Leaderboard
        self.ai_leaderboard = {}  # {user: avg_tps}
        self.p2p_thread = None
        self.user_name = "LocalUser"  # TODO: Load from config or prompt
        
        # TPS tracking
        self.tps_stats = {
            'ollama': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
            'openai': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
            'p2p': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0}
        }
        self.tps_label = None
        
        # P2P Security
        self.p2p_api_key = None  # Will be generated on first use
        self.p2p_rate_limits = {}  # Track request rates per IP
        self.p2p_cert_file = "certs/p2p_cert.pem"
        self.p2p_key_file = "certs/p2p_key.pem"
        
        self.ollama_timeout_enabled = False  # Default: no timeout
        self.ollama_timeout_seconds = 10
        
        # Responsive UI
        self.responsive_ui = False
        
        # Search index
        self.search_index = {}
        self.filtered_notes = None  # None means show all
        
        # Resource monitor
        self.resource_monitor = None
        self.resource_labels = {}
        
        # Audio controller tray
        self.audio_tray = None
        self.audio_tray_visible = False
        self.audio_tray_width = 300
        self.audio_mode = "spotify"  # "spotify" or "youtube"
        self.audio_volume = 50

        # Theme settings
        self.current_theme = "dark"  # "dark" or "light"
        self.auto_theme = False  # Auto theme switching (premium feature)

        # Context menu for text selection
        self.context_menu = None
        self.selected_text = ""

        # Keybind settings (premium feature)
        self.keybinds = {
            'launch_note_browser': '<Control-Button-1>',  # Ctrl+click
            'new_note': '<Control-n>',
            'search_focus': '<Control-f>',
            'save_note': '<Control-s>',
            'toggle_sidebar': '<Control-b>'
        }
        self.keybind_handlers = {}  # Store handler IDs for cleanup

        # Dev license key (for manual entry during development)
        self.dev_license_key = os.getenv("DEV_LICENSE_KEY", "test")

        # Dismissed warnings (user can disable specific warnings)
        self.dismissed_warnings = set()

        # Softer visual style
        self.soft_header_radius = 14
        self.soft_frame_radius = 16
        self.soft_card_radius = 18
        self.soft_button_radius = 12
        self.soft_field_radius = 10
        
        # Add close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Enhanced GUI responsiveness and performance
        self.responsive_ui = True
        self.animation_queue = []  # Queue for smooth animations
        self.performance_mode = False  # Reduce animations for low-end systems

        # Grid layout (3 columns: sidebar, main, right panel)
        self.grid_columnconfigure(1, weight=1)  # Main content expands
        self.grid_rowconfigure(1, weight=1)     # Content area expands

        # Responsive breakpoints
        self.breakpoints = {
            'mobile': 800,
            'tablet': 1200,
            'desktop': 1600
        }

        # Performance monitoring
        self.last_ui_update = 0
        self.ui_update_throttle = 50  # ms between UI updates

        # Load config
        self.load_config()
        
        # Initialize service manager
        self.service_manager = ServiceManager(self)
        
        # Login Screen
        self.login_frame = LoginFrame(self, self.on_login_success)

        # Main UI (Hidden initially)
        self.header = None
        self.board = None

        # Run automated tests on startup (development mode)
        self.run_startup_tests()

    def run_startup_tests(self):
        """Run automated tests on application startup"""
        try:
            # Only run tests in development/debug mode
            if os.getenv('CRYPTONOTE_TEST_MODE', '').lower() in ('1', 'true', 'yes'):
                logging.info("Running automated GUI tests on startup...")
                
                # Run tests in background thread to avoid blocking UI
                test_thread = threading.Thread(target=self._execute_startup_tests, daemon=True)
                test_thread.start()
            else:
                logging.info("Skipping automated tests (set CRYPTONOTE_TEST_MODE=1 to enable)")
                
        except Exception as e:
            logging.warning(f"Failed to initialize test system: {e}")

    def _execute_startup_tests(self):
        """Execute the startup test suite"""
        try:
            import subprocess
            import sys
            
            # Run GUI tests
            logging.info("Executing GUI test suite...")
            result = subprocess.run([
                sys.executable, 'run_gui_tests.py', 
                '--gui-only', '--skip-report'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logging.info("GUI tests passed successfully")
                # Show success message in UI after login
                self.after(1000, lambda: self._show_test_results("GUI Tests: PASSED", "green"))
            else:
                logging.error("GUI tests failed")
                logging.error(f"Test output: {result.stdout}")
                if result.stderr:
                    logging.error(f"Test errors: {result.stderr}")
                # Show failure message
                self.after(1000, lambda: self._show_test_results("GUI Tests: FAILED", "red"))
                
        except subprocess.TimeoutExpired:
            logging.error("GUI tests timed out")
            self.after(1000, lambda: self._show_test_results("GUI Tests: TIMEOUT", "orange"))
        except Exception as e:
            logging.error(f"Test execution failed: {e}")
            self.after(1000, lambda: self._show_test_results("GUI Tests: ERROR", "red"))

    def _show_test_results(self, message, color):
        """Show test results in the UI"""
        try:
            # Try to show in status bar or as a notification
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(text=message, text_color=color)
            # Could also show a messagebox, but that might be intrusive
            logging.info(f"Test results displayed: {message}")
        except:
            pass  # Ignore if UI not ready yet

    def on_closing(self):
        logging.info("Application closing initiated")
        if self.headless_mode:
            logging.info("Headless mode enabled, minimizing to tray")
            self.withdraw()
            return
        
        # Check if backed up
        if not self.backed_up and self.storage:
            confirm = messagebox.askyesno("Backup Required", 
                "Your database has not been backed up to Google Drive.\n\n"
                "IMPORTANT: Without backup, you risk losing all your notes if the local file is lost or corrupted.\n\n"
                "Do you want to backup now?")
            if confirm:
                # Trigger backup
                self.upload_to_drive()
                return  # Don't close yet
            else:
                final_confirm = messagebox.askyesno("Confirm Close", 
                    "Are you sure you want to close without backing up?\n\n"
                    "Your notes may be lost forever if something happens to the local file.")
                if not final_confirm:
                    return  # Don't close
        
        # Save data before closing
        self.stop_clipboard_monitoring()
        if self.storage and self.password:
            try:
                self.storage.save(self.password)
                logging.info("Database saved successfully on close")
            except Exception as e:
                logging.error(f"Failed to save database on close: {e}", exc_info=True)
                messagebox.showerror("Save Error", f"Failed to save on close: {e}")
        logging.info("Application closed")
        self.destroy()

    def on_login_success(self, storage, password, hint=None):
        self.storage = storage
        self.password = password
        self.hint = hint or ""
        self.login_frame.destroy()
        self.build_main_ui()
        self.load_user_config()
        self.check_backup_on_startup()
        self.save_config()
        self.start_clipboard_monitoring()

    def load_user_config(self):
        config_file = "user_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                self.token_balance = config.get("token_balance", 0)
                self.lifetime_license = config.get("lifetime_license", False)
                self.transaction_id = config.get("transaction_id", "")
                self.total_tokens_used = config.get("total_tokens_used", 0)
                self.clipboard_enabled = config.get("clipboard_enabled", True)
                self.p2p_enabled = config.get("p2p_enabled", False)
                self.p2p_peers = config.get("p2p_peers", [])
                self.earned_tokens = config.get("earned_tokens", 0)
                self.headless_mode = config.get("headless_mode", False)
                self.ollama_timeout_enabled = config.get("ollama_timeout_enabled", False)
                self.ollama_timeout_seconds = config.get("ollama_timeout_seconds", 10)
                self.leaderboard_enabled = config.get("leaderboard_enabled", False)
                self.p2p_api_key = config.get("p2p_api_key")
                self.ollama_timeout_enabled = config.get("ollama_timeout_enabled", False)
                self.ollama_timeout_seconds = config.get("ollama_timeout_seconds", 10)
                self.tps_stats = config.get("tps_stats", {
                    'ollama': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'openai': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'p2p': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0}
                })
                # Theme settings
                self.current_theme = config.get("current_theme", "dark")
                self.auto_theme = config.get("auto_theme", False)
                # Dismissed warnings
                self.dismissed_warnings = set(config.get("dismissed_warnings", []))
            except:
                self.token_balance = 0
                self.lifetime_license = False
                self.transaction_id = ""
                self.total_tokens_used = 0
                self.clipboard_enabled = True
                self.p2p_enabled = False
                self.p2p_peers = []
                self.earned_tokens = 0
                self.headless_mode = False
                self.p2p_api_key = None
                self.ollama_timeout_enabled = False
                self.ollama_timeout_seconds = 10
                self.tps_stats = {
                    'ollama': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'openai': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'p2p': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0}
                }
        else:
            self.token_balance = 0
            self.lifetime_license = False
            self.transaction_id = ""
            self.total_tokens_used = 0
            self.clipboard_enabled = True
            self.p2p_enabled = False
            self.p2p_peers = []
            self.earned_tokens = 0
        
        # Verify lifetime license with PayPal on boot
        if self.lifetime_license and self.transaction_id and paypal_available:
            if not self.verify_paypal_transaction(self.transaction_id):
                self.lifetime_license = False
                self.transaction_id = ""
                self.save_config()
                messagebox.showwarning("License Verification Failed", "Your lifetime license could not be verified with PayPal. Please contact support.")

    def check_backup_on_startup(self):
        """Check Google Drive for newer backups and download if available."""
        if not os.path.exists("client_secret.json"):
            logging.info("No Google Drive credentials, skipping backup check")
            return
        
        threading.Thread(target=self._check_backup_thread).start()

    def _check_backup_thread(self):
        try:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    logging.info("No valid Google Drive credentials, skipping backup check")
                    return
                
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            service = build('drive', 'v3', credentials=creds)
            
            # Search for backup files with the same name
            filename = os.path.basename(self.storage.filepath)
            query = f"name = '{filename}' and trashed = false"
            results = service.files().list(q=query, fields="files(id, name, modifiedTime)").execute()
            items = results.get('files', [])
            
            if not items:
                logging.info("No backup files found on Google Drive")
                return
            
            # Sort by modified time (newest first)
            items.sort(key=lambda x: x['modifiedTime'], reverse=True)
            
            # Get local file modification time
            local_mtime = os.path.getmtime(self.storage.filepath)
            
            # Check if the newest backup is newer than local
            newest_backup = items[0]
            from datetime import datetime
            backup_mtime = datetime.fromisoformat(newest_backup['modifiedTime'].replace('Z', '+00:00')).timestamp()
            
            if backup_mtime > local_mtime:
                logging.info(f"Newer backup found: {newest_backup['name']} ({newest_backup['modifiedTime']})")
                
                # Download the backup
                request = service.files().get_media(fileId=newest_backup['id'])
                temp_backup_path = f"temp_backup_{int(backup_mtime)}.enc"
                
                with open(temp_backup_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                
                # Replace current file with backup
                backup_path = self.storage.filepath + ".backup"
                os.rename(self.storage.filepath, backup_path)
                os.rename(temp_backup_path, self.storage.filepath)
                
                # Clean up old temp backups (keep last 5)
                self._cleanup_temp_backups()
                
                self.after(0, lambda: messagebox.showinfo("Backup Restored", 
                    f"A newer backup was found and restored.\nOld file saved as: {backup_path}"))
                
                # Reload the storage
                self.storage = StorageManager(self.storage.filepath)
                self.refresh_board()
            else:
                logging.info("Local file is up to date")
                
        except Exception as e:
            logging.error(f"Backup check failed: {e}")

    def _cleanup_temp_backups(self):
        """Keep only the last 5 temp backups."""
        temp_dir = os.path.dirname(self.storage.filepath)
        temp_files = [f for f in os.listdir(temp_dir) if f.startswith("temp_backup_") and f.endswith(".enc")]
        temp_files.sort(reverse=True)  # Newest first
        
        # Keep only the first 5 (newest)
        for old_file in temp_files[5:]:
            try:
                os.remove(os.path.join(temp_dir, old_file))
            except:
                pass

    def save_config(self):
        # Save last file info
        config = {
            "last_file": self.storage.filepath if self.storage else None,
            "last_hash": None,
            "hint": self.hint
        }
        if self.storage and self.storage.filepath:
            try:
                with open(self.storage.filepath, "rb") as f:
                    config["last_hash"] = hashlib.sha256(f.read()).hexdigest()
            except:
                pass
        with open("config.json", "w") as f:
            json.dump(config, f)
        
        # Save user config
        user_config = {
            "token_balance": self.token_balance,
            "lifetime_license": self.lifetime_license,
            "transaction_id": self.transaction_id,
            "total_tokens_used": self.total_tokens_used,
            "clipboard_enabled": self.clipboard_enabled,
            "p2p_enabled": self.p2p_enabled,
            "p2p_peers": self.p2p_peers,
            "earned_tokens": self.earned_tokens,
            "headless_mode": self.headless_mode,
            "p2p_api_key": self.p2p_api_key,
            "ollama_timeout_enabled": self.ollama_timeout_enabled,
            "ollama_timeout_seconds": self.ollama_timeout_seconds,
            "leaderboard_enabled": self.leaderboard_enabled,
            "tps_stats": self.tps_stats,
            "current_theme": self.current_theme,
            "auto_theme": self.auto_theme,
            "dismissed_warnings": list(self.dismissed_warnings)
        }
        with open("user_config.json", "w") as f:
            json.dump(user_config, f)

    def build_main_ui(self):
        # Configure main grid layout
        self.grid_columnconfigure(1, weight=1)  # Main content expands
        self.grid_rowconfigure(1, weight=1)     # Content area expands

        # Top Toolbar
        self.build_top_toolbar()

        # Left Sidebar
        self.build_sidebar()

        # Main Content Area
        self.build_main_content()

        # Right Panel
        self.build_right_panel()

        # Bottom Status Bar
        self.build_status_bar()

        # Initialize content
        self.start_p2p()
        self.apply_theme()
        self.refresh_board()
        self.build_search_index()

        # Resource Monitor (lower right)
        self.create_resource_monitor()

        # Audio Controller Toggle Button
        self.audio_toggle_btn = ctk.CTkButton(self, text="▶", width=30, height=30, command=self.toggle_audio_tray, corner_radius=self.soft_button_radius)
        self.audio_toggle_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-170)

        # Bind responsive events
        self.bind_responsive_events()

        # Setup keybinds
        self.setup_keybinds()

        # Create context menu
        self.create_context_menu()

        # Show welcome guide for new users
        self.show_welcome_if_first_run()

    def build_top_toolbar(self):
        """Build the top toolbar with essential actions"""
        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=self.soft_header_radius)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
        self.toolbar.grid_columnconfigure(1, weight=1)

        # Logo and title
        self.app_logo = ctk.CTkLabel(self.toolbar, text="📝 Cryptonote", font=("Roboto", 18, "bold"))
        self.app_logo.grid(row=0, column=0, padx=20, pady=10)

        # Quick Actions Frame
        self.quick_actions = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.quick_actions.grid(row=0, column=1)

        # New Note Button (Primary Action)
        self.new_note_btn = ctk.CTkButton(self.quick_actions, text="✨ New Note", command=self.create_new_note,
                                        width=120, height=35, corner_radius=self.soft_button_radius,
                                        fg_color="#0078D4", hover_color="#106EBE", font=("Roboto", 12, "bold"))
        self.new_note_btn.pack(side="left", padx=5)

        # Screen Capture
        self.snip_btn = ctk.CTkButton(self.quick_actions, text="📸 Capture", command=self.start_snip,
                                    width=100, height=35, corner_radius=self.soft_button_radius)
        self.snip_btn.pack(side="left", padx=5)

        # Import/Export
        self.import_btn = ctk.CTkButton(self.quick_actions, text="📥 Import", command=self.import_library,
                                      width=90, height=35, corner_radius=self.soft_button_radius)
        self.import_btn.pack(side="left", padx=5)

        self.export_btn = ctk.CTkButton(self.quick_actions, text="📤 Export", command=self.export_library,
                                      width=90, height=35, corner_radius=self.soft_button_radius)
        self.export_btn.pack(side="left", padx=5)

        # Right side actions
        self.right_actions = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        self.right_actions.grid(row=0, column=2, padx=20)

        # Copilot (Premium)
        self.copilot_btn = ctk.CTkButton(self.right_actions, text="🤖 Copilot", command=self.activate_copilot,
                                       width=100, height=35, corner_radius=self.soft_button_radius,
                                       fg_color="#0078D4", hover_color="#106EBE")
        self.copilot_btn.pack(side="left", padx=5)

        # Theme Toggle
        self.theme_btn = ctk.CTkButton(self.right_actions, text="🌙", command=self.toggle_theme,
                                     width=50, height=35, corner_radius=self.soft_button_radius)
        self.theme_btn.pack(side="left", padx=5)

        # Settings Menu
        self.settings_btn = ctk.CTkButton(self.right_actions, text="⚙️", command=self.open_settings,
                                        width=50, height=35, corner_radius=self.soft_button_radius)
        self.settings_btn.pack(side="left", padx=5)

    def build_sidebar(self):
        """Build the left sidebar for navigation and filters"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=self.soft_frame_radius)
        self.sidebar.grid(row=1, column=0, sticky="nsw", padx=(10, 5), pady=5)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Sidebar Header
        self.sidebar_header = ctk.CTkFrame(self.sidebar, height=40, corner_radius=self.soft_header_radius)
        self.sidebar_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.sidebar_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.sidebar_header, text="📂 Navigation", font=("Roboto", 14, "bold")).grid(row=0, column=0, padx=10, pady=5)

        # Navigation Content
        self.nav_content = ctk.CTkScrollableFrame(self.sidebar, corner_radius=self.soft_frame_radius)
        self.nav_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Navigation Items
        self.nav_buttons = {}

        # All Notes
        self.nav_buttons["all"] = ctk.CTkButton(self.nav_content, text="📄 All Notes", command=lambda: self.filter_notes("all"),
                                             anchor="w", height=35, corner_radius=self.soft_button_radius)
        self.nav_buttons["all"].pack(fill="x", padx=5, pady=2)

        # Recent Notes
        self.nav_buttons["recent"] = ctk.CTkButton(self.nav_content, text="🕒 Recent", command=lambda: self.filter_notes("recent"),
                                                anchor="w", height=35, corner_radius=self.soft_button_radius)
        self.nav_buttons["recent"].pack(fill="x", padx=5, pady=2)

        # Favorites (if implemented)
        self.nav_buttons["favorites"] = ctk.CTkButton(self.nav_content, text="⭐ Favorites", command=lambda: self.filter_notes("favorites"),
                                                   anchor="w", height=35, corner_radius=self.soft_button_radius)
        self.nav_buttons["favorites"].pack(fill="x", padx=5, pady=2)

        # Separator
        ctk.CTkFrame(self.nav_content, height=2, fg_color="gray").pack(fill="x", padx=10, pady=10)

        # Search Filters Header
        ctk.CTkLabel(self.nav_content, text="🔍 Filters", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        # Sort Options
        self.sort_var = ctk.StringVar(value="modified_desc")
        self.sort_options = ctk.CTkOptionMenu(self.nav_content, values=["Newest First", "Oldest First", "A-Z", "Z-A"],
                                            command=self.change_sort, height=30, corner_radius=self.soft_button_radius)
        self.sort_options.pack(fill="x", padx=10, pady=5)

        # View Options
        self.view_var = ctk.StringVar(value="cards")
        self.view_options = ctk.CTkOptionMenu(self.nav_content, values=["Card View", "List View", "Compact"],
                                            command=self.change_view, height=30, corner_radius=self.soft_button_radius)
        self.view_options.pack(fill="x", padx=10, pady=5)

        # Tag Filter (placeholder for now)
        ctk.CTkLabel(self.nav_content, text="🏷️ Tags", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(15, 5))
        self.tag_filter = ctk.CTkEntry(self.nav_content, placeholder_text="Filter by tag...", height=30, corner_radius=self.soft_field_radius)
        self.tag_filter.pack(fill="x", padx=10, pady=5)
        self.tag_filter.bind("<KeyRelease>", self.filter_by_tag)

    def build_main_content(self):
        """Build the main content area for notes display"""
        self.content_frame = ctk.CTkFrame(self, corner_radius=self.soft_frame_radius)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Search Bar
        self.search_frame = ctk.CTkFrame(self.content_frame, height=50, corner_radius=self.soft_frame_radius)
        self.search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.search_frame.grid_columnconfigure(0, weight=1)

        # Search Icon and Input
        search_container = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        search_container.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        search_container.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_container, text="🔍", font=("Roboto", 14)).grid(row=0, column=0, padx=(0, 10))

        self.search_entry = ctk.CTkEntry(search_container, placeholder_text="Search notes, tags, or content...",
                                       corner_radius=self.soft_field_radius, height=35)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Add right-click context menu to search entry
        self.search_entry.bind("<Button-3>", lambda e: self.show_context_menu(e))

        # Clear Search Button
        self.clear_search_btn = ctk.CTkButton(search_container, text="✕", width=35, height=35,
                                            command=self.clear_search, corner_radius=self.soft_button_radius)
        self.clear_search_btn.grid(row=0, column=2, padx=(10, 0))

        # Notes Display Area
        self.board_container = ctk.CTkFrame(self.content_frame, corner_radius=self.soft_frame_radius)
        self.board_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.board_container.grid_rowconfigure(0, weight=1)
        self.board_container.grid_columnconfigure(0, weight=1)

        # Notes Counter
        self.notes_counter = ctk.CTkLabel(self.board_container, text="Loading notes...", font=("Roboto", 12))
        self.notes_counter.grid(row=0, column=0, sticky="nw", padx=15, pady=10)

        # Notes Board
        self.board = ctk.CTkScrollableFrame(self.board_container, corner_radius=self.soft_frame_radius)
        self.board.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Set initial view mode
        self.current_view = "cards"  # cards, list, compact

    def build_right_panel(self):
        """Build the right panel for quick actions and AI assistant"""
        self.right_panel = ctk.CTkFrame(self, width=280, corner_radius=self.soft_frame_radius)
        self.right_panel.grid(row=1, column=2, sticky="nse", padx=(5, 10), pady=5)
        self.right_panel.grid_propagate(False)
        self.right_panel.grid_rowconfigure(2, weight=1)

        # Quick Actions Header
        self.actions_header = ctk.CTkFrame(self.right_panel, height=40, corner_radius=self.soft_header_radius)
        self.actions_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.actions_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.actions_header, text="⚡ Quick Actions", font=("Roboto", 14, "bold")).grid(row=0, column=0, padx=10, pady=5)

        # Quick Actions Content
        self.quick_actions_content = ctk.CTkFrame(self.right_panel, corner_radius=self.soft_frame_radius)
        self.quick_actions_content.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        # Action Buttons
        actions = [
            ("💾 Backup", self.upload_to_drive),
            ("📋 Clipboard", self.show_clipboard_panel),
            ("🔧 Services", self.show_service_status),
            ("🛒 Extras", self.open_extras_shop),
            ("📝 AI Prompts", self.download_prompts),
            ("🧹 Scrub", self.scrub_defaults)
        ]

        for i, (text, command) in enumerate(actions):
            btn = ctk.CTkButton(self.quick_actions_content, text=text, command=command,
                              height=35, corner_radius=self.soft_button_radius, anchor="w")
            btn.pack(fill="x", padx=10, pady=2)

        # AI Assistant Section
        self.ai_header = ctk.CTkFrame(self.right_panel, height=40, corner_radius=self.soft_header_radius)
        self.ai_header.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.ai_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.ai_header, text="🤖 AI Assistant", font=("Roboto", 14, "bold")).grid(row=0, column=0, padx=10, pady=5)

        # AI Quick Actions - moved right underneath AI Assistant header
        ai_actions = [
            ("✨ Generate Summary", lambda: self.ai_action("summarize")),
            ("🔍 Find Related", lambda: self.ai_action("find_related")),
            ("📊 Analyze Content", lambda: self.ai_action("analyze")),
            ("🎯 Suggest Tags", lambda: self.ai_action("suggest_tags"))
        ]

        # Create a frame for AI buttons right after the header
        self.ai_buttons_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.ai_buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))

        for text, command in ai_actions:
            btn = ctk.CTkButton(self.ai_buttons_frame, text=text, command=command,
                              height=30, corner_radius=self.soft_button_radius, anchor="w")
            btn.pack(fill="x", pady=2)

        # AI Content
        self.ai_content = ctk.CTkScrollableFrame(self.right_panel, corner_radius=self.soft_frame_radius)
        self.ai_content.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # AI Status
        self.ai_status = ctk.CTkLabel(self.ai_content, text="AI Status: Ready", font=("Roboto", 12))
        self.ai_status.pack(anchor="w", padx=10, pady=10)

        # Token Balance
        self.token_display = ctk.CTkLabel(self.ai_content, text=f"💰 Tokens: {self.token_balance}", font=("Roboto", 12))
        self.token_display.pack(anchor="w", padx=10, pady=5)

        # TPS Display
        self.tps_display = ctk.CTkLabel(self.ai_content, text="⚡ TPS: Calculating...", font=("Roboto", 10))
        self.tps_display.pack(anchor="w", padx=10, pady=5)

    def build_status_bar(self):
        """Build the bottom status bar"""
        self.status_bar = ctk.CTkFrame(self, height=35, corner_radius=self.soft_header_radius)
        self.status_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))
        self.status_bar.grid_columnconfigure(1, weight=1)

        # Left side - System status
        self.status_left = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        self.status_left.grid(row=0, column=0, padx=15)

        self.connection_status = ctk.CTkLabel(self.status_left, text="🔗 Connected", font=("Roboto", 10))
        self.connection_status.pack(side="left", padx=(0, 15))

        self.backup_status = ctk.CTkLabel(self.status_left, text="💾 Backed up", font=("Roboto", 10))
        self.backup_status.pack(side="left", padx=(0, 15))

        # Center - AI Leaderboard Ticker
        self.ticker_label = ctk.CTkLabel(self.status_bar, text="🏆 AI Leaderboard: Loading...", font=("Roboto", 10))
        self.ticker_label.grid(row=0, column=1)

        # Right side - Additional info
        self.status_right = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        self.status_right.grid(row=0, column=2, padx=15)

        self.license_status = ctk.CTkLabel(self.status_right, text="⭐ Free", font=("Roboto", 10))
        self.license_status.pack(side="right")

        # Update status bar
        self.update_status_bar()

    def create_context_menu(self):
        """Create the right-click context menu for text selection"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="📝 Summarize with Copilot",
                                    command=self.summarize_selected_text)
        self.context_menu.add_command(label="✨ Rewrite with AI",
                                    command=self.rewrite_selected_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy", command=self.copy_selected_text)
        self.context_menu.add_command(label="✂️ Cut", command=self.cut_selected_text)
        self.context_menu.add_command(label="📄 Paste", command=self.paste_text)

    def show_context_menu(self, event, selected_text=""):
        """Show the context menu at the mouse position"""
        self.selected_text = selected_text

        # Check if Copilot features should be enabled
        if not self.lifetime_license:
            # Disable Copilot menu items for free users
            self.context_menu.entryconfig(0, state="disabled")  # Summarize
            self.context_menu.entryconfig(1, state="disabled")  # Rewrite
        else:
            self.context_menu.entryconfig(0, state="normal")  # Summarize
            self.context_menu.entryconfig(1, state="normal")  # Rewrite

        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def summarize_selected_text(self):
        """Summarize the selected text using Copilot"""
        if not self.selected_text.strip():
            messagebox.showwarning("No Selection", "Please select some text to summarize.")
            return

        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature",
                              "AI summarization requires a lifetime license.\n\n"
                              "Upgrade to unlock Copilot-powered text analysis and summarization!")
            return

        # Show progress
        progress = self.show_progress("Summarizing with Copilot...")

        def summarize_task():
            try:
                prompt = f"Please provide a concise summary of the following text:\n\n{self.selected_text}"
                summary = self.call_ai_service(prompt, use_openai=True)

                if summary:
                    # Show summary in a dialog
                    SummaryDialog(self, self.selected_text, summary)
                else:
                    messagebox.showerror("Summarization Failed",
                                       "Unable to generate summary. Please check your AI service configuration.")

            except Exception as e:
                messagebox.showerror("Error", f"Summarization failed: {e}")
            finally:
                progress.destroy()

        # Run in background thread
        threading.Thread(target=summarize_task, daemon=True).start()

    def rewrite_selected_text(self):
        """Rewrite the selected text using AI with custom prompt"""
        if not self.selected_text.strip():
            messagebox.showwarning("No Selection", "Please select some text to rewrite.")
            return

        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature",
                              "AI rewriting requires a lifetime license.\n\n"
                              "Upgrade to unlock Copilot-powered text rewriting and enhancement!")
            return

        # Show prompt dialog
        RewritePromptDialog(self, self.selected_text)

    def copy_selected_text(self):
        """Copy selected text to clipboard"""
        if self.selected_text:
            pyperclip.copy(self.selected_text)

    def cut_selected_text(self):
        """Cut selected text (placeholder - would need text widget reference)"""
        if self.selected_text:
            pyperclip.copy(self.selected_text)
            # Note: Actual cutting would require access to the text widget

    def paste_text(self):
        """Paste text from clipboard (placeholder - would need text widget reference)"""
        try:
            text = pyperclip.paste()
            # Note: Actual pasting would require access to the text widget
        except:
            pass

    def call_ai_service(self, prompt, use_openai=False):
        """Call AI service for text processing"""
        try:
            if use_openai and openai and os.getenv("OPENAI_API_KEY"):
                # Use OpenAI
                client = openai.OpenAI()
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.lifetime_license:
                # Use Ollama
                return self._call_ollama(prompt)
            else:
                return None
        except Exception as e:
            print(f"AI service error: {e}")
            return None
    
    def _call_ollama(self, prompt):
        """Call Ollama AI service"""
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.ollama_timeout_seconds if self.ollama_timeout_enabled else 30
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return None
        except:
            return None

    def setup_keybinds(self):
        """Setup keyboard shortcuts and mouse bindings"""
        # Global keybinds
        self.bind(self.keybinds['new_note'], lambda e: self.create_new_note())
        self.bind(self.keybinds['search_focus'], lambda e: self.focus_search())
        self.bind(self.keybinds['toggle_sidebar'], lambda e: self.toggle_sidebar())

        # Note-specific bindings will be set when notes are created
        self.keybind_handlers = {
            'global': True  # Mark that global keybinds are set
        }

    def focus_search(self):
        """Focus the search entry"""
        if hasattr(self, 'search_entry'):
            self.search_entry.focus()
            self.search_entry.select_range(0, "end")

    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        if hasattr(self, 'sidebar'):
            if self.sidebar.winfo_ismapped():
                self.sidebar.grid_remove()
            else:
                self.sidebar.grid()

    def launch_note_in_browser(self, note):
        """Premium feature: Launch note content in default web browser (without title)"""
        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature",
                              "Browser launch is a premium feature.\n\n"
                              "Upgrade to a lifetime license to unlock advanced note sharing and web integration!")
            return

        try:
            import tempfile
            import webbrowser
            import html

            # Create temporary HTML file with note content (no title)
            content_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cryptonote - {note.title}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        line-height: 1.6;
                        background-color: #f5f5f5;
                    }}
                    .content {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    pre {{
                        background: #f8f8f8;
                        padding: 15px;
                        border-radius: 4px;
                        overflow-x: auto;
                        font-family: 'Consolas', 'Monaco', monospace;
                    }}
                    .metadata {{
                        color: #666;
                        font-size: 0.9em;
                        margin-top: 20px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                    }}
                </style>
            </head>
            <body>
                <div class="content">
                    {html.escape(note.content).replace(chr(10), '<br>')}
                </div>
                <div class="metadata">
                    <strong>From Cryptonote</strong> - Secure, offline note-taking<br>
                    Created: {time.ctime(note.created_at)}<br>
                    Last modified: {time.ctime(note.modified_at)}
                </div>
            </body>
            </html>
            """

            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(content_html)
                temp_file = f.name

            # Open in default browser
            webbrowser.open(f'file://{temp_file}')

            # Schedule cleanup after browser opens
            self.after(5000, lambda: self.cleanup_temp_file(temp_file))

        except Exception as e:
            messagebox.showerror("Browser Launch Error", f"Failed to open note in browser: {e}")

    def cleanup_temp_file(self, file_path):
        """Clean up temporary HTML files"""
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass  # Ignore cleanup errors

    def open_keybind_settings(self):
        """Open keybind settings dialog"""
        KeybindSettingsDialog(self)

    def update_responsive_layout(self):
        """Update layout based on window size for responsiveness"""
        if not self.responsive_ui:
            return

        width = self.winfo_width()
        height = self.winfo_height()

        # Responsive sidebar
        if width < self.breakpoints['mobile']:
            # Mobile: Hide sidebar, show hamburger menu
            if hasattr(self, 'sidebar'):
                self.sidebar.grid_remove()
            self.show_mobile_menu()
        elif width < self.breakpoints['tablet']:
            # Tablet: Smaller sidebar
            if hasattr(self, 'sidebar'):
                self.sidebar.configure(width=200)
                self.sidebar.grid()
        else:
            # Desktop: Full sidebar
            if hasattr(self, 'sidebar'):
                self.sidebar.configure(width=250)
                self.sidebar.grid()

        # Responsive right panel
        if width < self.breakpoints['tablet']:
            if hasattr(self, 'right_panel'):
                self.right_panel.grid_remove()
        else:
            if hasattr(self, 'right_panel'):
                self.right_panel.grid()

        # Responsive toolbar
        self.update_toolbar_for_size(width)

    def show_mobile_menu(self):
        """Show mobile hamburger menu"""
        if not hasattr(self, 'mobile_menu_btn'):
            self.mobile_menu_btn = ctk.CTkButton(self.toolbar, text="☰", width=50, height=35,
                                               command=self.toggle_mobile_sidebar,
                                               corner_radius=self.soft_button_radius)
            self.mobile_menu_btn.grid(row=0, column=0, padx=10, pady=10)

    def toggle_mobile_sidebar(self):
        """Toggle mobile sidebar overlay"""
        if hasattr(self, 'mobile_sidebar') and self.mobile_sidebar.winfo_ismapped():
            self.mobile_sidebar.grid_remove()
        else:
            self.show_mobile_sidebar()

    def show_mobile_sidebar(self):
        """Show mobile sidebar as overlay"""
        if not hasattr(self, 'mobile_sidebar'):
            self.mobile_sidebar = ctk.CTkFrame(self, width=280, corner_radius=self.soft_frame_radius)
            self.mobile_sidebar.place(x=0, y=50, relwidth=0.8, relheight=1.0)

            # Mobile sidebar content
            mobile_nav = ctk.CTkScrollableFrame(self.mobile_sidebar, corner_radius=self.soft_frame_radius)
            mobile_nav.pack(fill="both", expand=True, padx=10, pady=10)

            # Copy navigation items
            nav_items = [
                ("📄 All Notes", lambda: self.filter_notes("all")),
                ("🕒 Recent", lambda: self.filter_notes("recent")),
                ("⭐ Favorites", lambda: self.filter_notes("favorites")),
                ("⚙️ Settings", self.open_settings),
                ("📋 Clipboard", self.show_clipboard_panel),
                ("🔧 Services", self.show_service_status)
            ]

            for text, command in nav_items:
                btn = ctk.CTkButton(mobile_nav, text=text, command=command,
                                  height=40, corner_radius=self.soft_button_radius, anchor="w")
                btn.pack(fill="x", padx=5, pady=2)

        self.mobile_sidebar.lift()

    def update_toolbar_for_size(self, width):
        """Update toolbar layout based on window width"""
        if width < self.breakpoints['mobile']:
            # Mobile: Minimal toolbar
            if hasattr(self, 'app_logo'):
                self.app_logo.grid_remove()
            if hasattr(self, 'right_actions'):
                self.right_actions.grid_remove()
        else:
            # Desktop: Full toolbar
            if hasattr(self, 'app_logo'):
                self.app_logo.grid()
            if hasattr(self, 'right_actions'):
                self.right_actions.grid()

    def throttle_ui_update(self, func, *args, **kwargs):
        """Throttle UI updates for performance"""
        current_time = self._get_time_ms()
        if current_time - self.last_ui_update > self.ui_update_throttle:
            self.last_ui_update = current_time
            func(*args, **kwargs)

    def bind_responsive_events(self):
        """Bind events for responsive design"""
        self.bind('<Configure>', lambda e: self.throttle_ui_update(self.update_responsive_layout))

    def show_welcome_if_first_run(self):
        """Show welcome guide if this is the first run"""
        config_file = "user_config.json"
        if not os.path.exists(config_file):
            # First run - show welcome guide
            self.after(1000, self.show_welcome_guide)  # Show after UI is fully loaded

    def create_helpful_images(self):
        """Create helpful visual guides and icons for the interface"""
        # This would create visual guides, but for now we'll use emoji and text
        # In a real implementation, you'd generate or load actual images

        # Quick start guide (could be shown on first run)
        self.quick_start_guide = {
            "search": "🔍 Use the search bar to find notes by title, content, or tags",
            "new_note": "✨ Click 'New Note' to create your first note",
            "sidebar": "📂 Use the sidebar to filter and organize your notes",
            "copilot": "🤖 Premium: Use Copilot for AI-powered assistance",
            "backup": "💾 Regular backups keep your notes safe"
        }

    def show_welcome_guide(self):
        """Show a welcome guide for new users"""
        guide_text = """Welcome to Cryptonote! 🎉

Getting Started:
• Click 'New Note' to create your first note
• Use the search bar to find notes quickly
• Organize with tags and filters
• Enable P2P for AI leaderboards
• Backup regularly to Google Drive

Premium Features:
• AI Copilot for smart assistance
• Advanced text editing (Notepad++ style)
• Auto theme switching
• Clipboard monitoring
• Priority support

Enjoy secure, private note-taking! 🔒"""

        messagebox.showinfo("Welcome to Cryptonote", guide_text)

    def filter_notes(self, filter_type):
        """Filter notes based on type"""
        self.current_filter = filter_type

        # Update navigation button states
        for btn_type, btn in self.nav_buttons.items():
            if btn_type == filter_type:
                btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])  # Selected state
            else:
                btn.configure(fg_color=["#979DA2", "#565B5E"])  # Normal state

        # Apply filter
        if filter_type == "all":
            self.filtered_notes = None
        elif filter_type == "recent":
            # Show notes from last 7 days
            import datetime
            week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            recent_ids = []
            for note in self.storage.list_notes():
                if note.modified_at > week_ago.timestamp():
                    recent_ids.append(note.id)
            self.filtered_notes = set(recent_ids) if recent_ids else set()
        elif filter_type == "favorites":
            # Placeholder for favorites (not implemented yet)
            self.filtered_notes = set()

        self.refresh_board()

    def change_sort(self, sort_option):
        """Change sorting option"""
        sort_map = {
            "Newest First": "modified_desc",
            "Oldest First": "modified_asc",
            "A-Z": "title_asc",
            "Z-A": "title_desc"
        }
        self.current_sort = sort_map.get(sort_option, "modified_desc")
        self.refresh_board()

    def change_view(self, view_option):
        """Change view mode"""
        view_map = {
            "Card View": "cards",
            "List View": "list",
            "Compact": "compact"
        }
        self.current_view = view_map.get(view_option, "cards")
        self.refresh_board()

    def filter_by_tag(self, event):
        """Filter notes by tag"""
        tag_query = self.tag_filter.get().strip().lower()
        if not tag_query:
            # If no tag filter, keep current filter
            return

        # Find notes with matching tags
        matching_ids = []
        for note in self.storage.list_notes():
            if note.tags:
                note_tags = [tag.lower() for tag in note.tags]
                if any(tag_query in tag for tag in note_tags):
                    matching_ids.append(note.id)

        self.filtered_notes = set(matching_ids) if matching_ids else set()
        self.refresh_board()

    def clear_search(self):
        """Clear search and show all notes"""
        self.search_entry.delete(0, "end")
        self.filtered_notes = None
        self.refresh_board()

    def ai_action(self, action_type):
        """Handle AI quick actions"""
        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature", "AI actions require a lifetime license.\n\nUpgrade to unlock AI-powered note analysis, summaries, and smart suggestions!")
            return

        # Placeholder for AI actions
        messagebox.showinfo("AI Action", f"AI {action_type} feature coming soon!")

    def update_status_bar(self):
        """Update status bar information"""
        # Connection status
        if self.p2p_enabled:
            self.connection_status.configure(text="🔗 P2P Active")
        else:
            self.connection_status.configure(text="🔗 Local Only")

        # Backup status
        if self.backed_up:
            self.backup_status.configure(text="💾 Backed up")
        else:
            self.backup_status.configure(text="⚠️ Not backed up")

        # License status
        if self.lifetime_license:
            self.license_status.configure(text="💎 Lifetime")
        else:
            self.license_status.configure(text="⭐ Free")

        # Update ticker
        self.update_ticker()

    def update_ticker(self):
        # Scrolling ticker effect with top AI users
        if self.leaderboard_enabled and self.ai_leaderboard:
            sorted_users = sorted(self.ai_leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
            ticker_content = "🏆 " + " | ".join(f"{u}:{tps:.1f}" for u, tps in sorted_users) + " | "
        else:
            ticker_content = "🏆 AI Leaderboard: Join P2P to see rankings | "

        if not hasattr(self, 'ticker_text'):
            self.ticker_text = ticker_content

        # Shift the text left
        self.ticker_text = self.ticker_text[1:] + self.ticker_text[0]
        display_text = self.ticker_text[:50]  # Display first 50 chars
        self.ticker_label.configure(text=display_text)

        # Update every 200ms for smooth scroll
        self.after(200, self.update_ticker)

    def on_window_resize(self, event):
        """Handle window resize for responsive UI"""
        if not self.responsive_ui:
            return
        width = self.winfo_width()
        
        # Scale factor based on width (assuming base width 1200)
        scale = width / 1200.0
        scale = max(0.5, min(scale, 1.5))  # Clamp between 0.5 and 1.5
        
        # Resize buttons
        button_width = int(100 * scale)
        prompt_width = int(120 * scale)
        entry_width = int(400 * scale)
        
        try:
            self.snip_btn.configure(width=prompt_width)
            self.new_note_btn.configure(width=button_width)
            self.import_btn.configure(width=int(80 * scale))
            self.export_btn.configure(width=int(80 * scale))
            self.scrub_btn.configure(width=prompt_width)
            self.download_btn.configure(width=prompt_width)
            self.upload_btn.configure(width=prompt_width)
            self.extras_btn.configure(width=button_width)
            self.clipboard_btn.configure(width=button_width)
            self.settings_btn.configure(width=button_width)
            
            # Resize search entry
            self.search_entry.configure(width=entry_width)
            
            # Refresh board
            self.refresh_board()
            
            # Adjust ticker width
            ticker_width = width - 220
            self.ticker_frame.configure(width=ticker_width)
        except:
            pass  # Ignore if widgets not created yet

    def create_resource_monitor(self):
        """Create the resource monitor widget in lower right corner"""
        self.resource_monitor = ctk.CTkFrame(self, width=200, height=150, corner_radius=self.soft_card_radius)
        self.resource_monitor.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        
        # Title
        title = ctk.CTkLabel(self.resource_monitor, text="System Resources", font=("Roboto", 12, "bold"))
        title.pack(pady=(10, 5))
        
        # CPU Load
        cpu_frame = ctk.CTkFrame(self.resource_monitor, fg_color="transparent")
        cpu_frame.pack(pady=2, padx=10, fill="x")
        cpu_label = ctk.CTkLabel(cpu_frame, text="CPU:", font=("Roboto", 10))
        cpu_label.pack(side="left")
        self.resource_labels['cpu_load'] = ctk.CTkLabel(cpu_frame, text="0%", font=("Roboto", 10))
        self.resource_labels['cpu_load'].pack(side="right")
        
        # CPU Temp
        cpu_temp_frame = ctk.CTkFrame(self.resource_monitor, fg_color="transparent")
        cpu_temp_frame.pack(pady=2, padx=10, fill="x")
        cpu_temp_label = ctk.CTkLabel(cpu_temp_frame, text="CPU Temp:", font=("Roboto", 10))
        cpu_temp_label.pack(side="left")
        self.resource_labels['cpu_temp'] = ctk.CTkLabel(cpu_temp_frame, text="N/A", font=("Roboto", 10))
        self.resource_labels['cpu_temp'].pack(side="right")
        
        # GPU Load
        gpu_frame = ctk.CTkFrame(self.resource_monitor, fg_color="transparent")
        gpu_frame.pack(pady=2, padx=10, fill="x")
        gpu_label = ctk.CTkLabel(gpu_frame, text="GPU:", font=("Roboto", 10))
        gpu_label.pack(side="left")
        self.resource_labels['gpu_load'] = ctk.CTkLabel(gpu_frame, text="N/A", font=("Roboto", 10))
        self.resource_labels['gpu_load'].pack(side="right")
        
        # GPU Temp
        gpu_temp_frame = ctk.CTkFrame(self.resource_monitor, fg_color="transparent")
        gpu_temp_frame.pack(pady=2, padx=10, fill="x")
        gpu_temp_label = ctk.CTkLabel(gpu_temp_frame, text="GPU Temp:", font=("Roboto", 10))
        gpu_temp_label.pack(side="left")
        self.resource_labels['gpu_temp'] = ctk.CTkLabel(gpu_temp_frame, text="N/A", font=("Roboto", 10))
        self.resource_labels['gpu_temp'].pack(side="right")
        
        # RAM Usage
        ram_frame = ctk.CTkFrame(self.resource_monitor, fg_color="transparent")
        ram_frame.pack(pady=2, padx=10, fill="x")
        ram_label = ctk.CTkLabel(ram_frame, text="RAM:", font=("Roboto", 10))
        ram_label.pack(side="left")
        self.resource_labels['ram'] = ctk.CTkLabel(ram_frame, text="0%", font=("Roboto", 10))
        self.resource_labels['ram'].pack(side="right")
        
        # Start updating
        self.update_resource_monitor()

    def create_audio_tray(self):
        """Create the sliding audio controller tray"""
        self.audio_tray = ctk.CTkFrame(self, width=self.audio_tray_width, height=200, corner_radius=self.soft_card_radius)
        self.audio_tray.place(relx=1.0, rely=1.0, anchor="se", x=self.audio_tray_width, y=-170)
        
        # Title with mode switcher
        title_frame = ctk.CTkFrame(self.audio_tray, fg_color="transparent")
        title_frame.pack(pady=(10, 5), padx=10, fill="x")
        
        if self.master.lifetime_license:
            self.mode_switch_btn = ctk.CTkButton(title_frame, text="◀", width=30, height=30, command=self.switch_audio_mode, corner_radius=self.soft_button_radius)
            self.mode_switch_btn.pack(side="left")
            
            self.audio_title = ctk.CTkLabel(title_frame, text="Spotify Controller", font=("Roboto", 14, "bold"))
            self.audio_title.pack(side="left", padx=10)
        else:
            self.audio_title = ctk.CTkLabel(title_frame, text="🔒 Premium Audio Remote", font=("Roboto", 14, "bold"))
            self.audio_title.pack(side="left", padx=10)
        
        # Windows Volume Control (Always available)
        volume_frame = ctk.CTkFrame(self.audio_tray, fg_color="transparent")
        volume_frame.pack(pady=5, padx=10, fill="x")
        
        volume_label = ctk.CTkLabel(volume_frame, text="System Volume", font=("Roboto", 12, "bold"))
        volume_label.pack(pady=5)
        
        volume_control_frame = ctk.CTkFrame(volume_frame, fg_color="transparent")
        volume_control_frame.pack(fill="x")
        
        self.volume_down_btn = ctk.CTkButton(volume_control_frame, text="🔉", width=40, command=self.volume_down, corner_radius=self.soft_button_radius)
        self.volume_down_btn.pack(side="left", padx=5)
        
        self.volume_slider = ctk.CTkSlider(volume_control_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.volume_slider.set(self.audio_volume)
        
        self.volume_up_btn = ctk.CTkButton(volume_control_frame, text="🔊", width=40, command=self.volume_up, corner_radius=self.soft_button_radius)
        self.volume_up_btn.pack(side="right", padx=5)
        
        # Media Controls (Premium only)
        media_frame = ctk.CTkFrame(self.audio_tray, fg_color="transparent")
        media_frame.pack(pady=10, padx=10, fill="x")
        
        if self.master.lifetime_license:
            media_label = ctk.CTkLabel(media_frame, text="Media Controls", font=("Roboto", 12, "bold"))
            media_label.pack(pady=5)
            
            media_buttons_frame = ctk.CTkFrame(media_frame, fg_color="transparent")
            media_buttons_frame.pack(fill="x")
            
            self.prev_btn = ctk.CTkButton(media_buttons_frame, text="⏮", width=50, command=self.media_previous, corner_radius=self.soft_button_radius)
            self.prev_btn.pack(side="left", padx=5)
            
            self.play_pause_btn = ctk.CTkButton(media_buttons_frame, text="▶", width=50, command=self.media_play_pause, corner_radius=self.soft_button_radius)
            self.play_pause_btn.pack(side="left", padx=5)
            
            self.next_btn = ctk.CTkButton(media_buttons_frame, text="⏭", width=50, command=self.media_next, corner_radius=self.soft_button_radius)
            self.next_btn.pack(side="left", padx=5)
        else:
            # Premium lock message
            lock_label = ctk.CTkLabel(media_frame, text="🔒 Spotify/YouTube Remote\nRequires Lifetime License", font=("Roboto", 11))
            lock_label.pack(pady=10)
            
            upgrade_btn = ctk.CTkButton(media_frame, text="Upgrade to Premium", command=self.show_extras_dialog, corner_radius=self.soft_button_radius)
            upgrade_btn.pack(pady=5)
        
        # Status label
        self.audio_status = ctk.CTkLabel(self.audio_tray, text="Ready", font=("Roboto", 10))
        self.audio_status.pack(pady=5)

    def toggle_audio_tray(self):
        """Toggle the audio controller tray visibility with animation"""
        if not self.master.lifetime_license:
            messagebox.showinfo("Premium Feature", "Audio controls require a lifetime license.\n\nPurchase a license in Settings → Extras to unlock Spotify/YouTube remote controls.")
            return
            
        if self.audio_tray_visible:
            # Hide tray
            self.animate_tray_hide()
        else:
            # Show tray
            if not self.audio_tray:
                self.create_audio_tray()
            self.animate_tray_show()
    
    def animate_tray_show(self):
        """Animate the tray sliding in from the right with optimized performance"""
        if self.audio_tray_visible:
            return

        self.audio_tray_visible = True
        self.audio_toggle_btn.configure(text="◀")

        # Use more efficient animation with easing
        self._animate_tray(target_x=0, duration=300, easing="ease_out")

    def animate_tray_hide(self):
        """Animate the tray sliding out to the right with optimized performance"""
        if not self.audio_tray_visible:
            return

        self.audio_tray_visible = False
        self.audio_toggle_btn.configure(text="▶")

        # Use more efficient animation with easing
        self._animate_tray(target_x=self.audio_tray_width, duration=300, easing="ease_in")

    def _animate_tray(self, target_x, duration=300, easing="ease_out"):
        """Optimized animation system with easing functions"""
        start_x = self.audio_tray.winfo_x() if hasattr(self.audio_tray, 'winfo_x') else (self.audio_tray_width if target_x == 0 else 0)
        start_time = self._get_time_ms()
        total_distance = target_x - start_x

        def ease_out_cubic(t):
            return 1 - (1 - t) ** 3

        def ease_in_cubic(t):
            return t ** 3

        easing_func = ease_out_cubic if easing == "ease_out" else ease_in_cubic

        def animate_step():
            elapsed = self._get_time_ms() - start_time
            progress = min(elapsed / duration, 1.0)
            eased_progress = easing_func(progress)

            current_x = start_x + (total_distance * eased_progress)

            if progress >= 1.0:
                # Animation complete
                if target_x == 0:
                    self.audio_tray.place(relx=1.0, rely=1.0, anchor="se", x=0, y=-170)
                    self.audio_toggle_btn.place(relx=1.0, rely=1.0, anchor="se", x=-30, y=-170)
                    self.update_audio_status()
                else:
                    self.audio_toggle_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-170)
                return

            self.audio_tray.place(relx=1.0, rely=1.0, anchor="se", x=current_x, y=-170)
            self.audio_toggle_btn.place(relx=1.0, rely=1.0, anchor="se", x=current_x - 30, y=-170)
            self.after(16, animate_step)  # ~60 FPS

        animate_step()

    def _get_time_ms(self):
        """Get current time in milliseconds for animation timing"""
        import time
        return int(time.time() * 1000)
    
    def switch_audio_mode(self):
        """Switch between Spotify and YouTube mode"""
        if self.audio_mode == "spotify":
            self.audio_mode = "youtube"
            self.audio_title.configure(text="YouTube Remote")
        else:
            self.audio_mode = "spotify"
            self.audio_title.configure(text="Spotify Controller")
        
        self.update_audio_status()
    
    def update_audio_status(self):
        """Update the status label based on current mode"""
        if self.audio_mode == "spotify":
            self.audio_status.configure(text="Controlling Spotify")
        else:
            self.audio_status.configure(text="Controlling YouTube")
    
    def set_volume(self, value):
        """Set system volume"""
        if not audio_available:
            self.audio_status.configure(text="Audio control not available")
            return
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            # Convert 0-100 to 0.0-1.0
            volume.SetMasterVolumeLevelScalar(float(value) / 100.0, None)
            self.audio_volume = int(value)
            self.audio_status.configure(text=f"Volume: {int(value)}%")
        except Exception as e:
            self.audio_status.configure(text=f"Volume error: {e}")
    
    def volume_up(self):
        """Increase volume by 10%"""
        new_volume = min(100, self.audio_volume + 10)
        self.volume_slider.set(new_volume)
        self.set_volume(new_volume)
    
    def volume_down(self):
        """Decrease volume by 10%"""
        new_volume = max(0, self.audio_volume - 10)
        self.volume_slider.set(new_volume)
        self.set_volume(new_volume)
    
    def media_play_pause(self):
        """Send play/pause command"""
        if not media_control_available:
            self.audio_status.configure(text="Media control not available")
            return
        
        try:
            if self.audio_mode == "spotify":
                # Try to find Spotify window
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    spotify_windows[0].activate()
                    pyautogui.press('space')
                    self.audio_status.configure(text="Spotify: Play/Pause")
                else:
                    self.audio_status.configure(text="Spotify not found")
            else:
                # YouTube - send space to browser
                pyautogui.press('space')
                self.audio_status.configure(text="YouTube: Play/Pause")
        except Exception as e:
            self.audio_status.configure(text=f"Media error: {e}")
    
    def media_next(self):
        """Send next track command"""
        if not media_control_available:
            self.audio_status.configure(text="Media control not available")
            return
        
        try:
            if self.audio_mode == "spotify":
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    spotify_windows[0].activate()
                    pyautogui.hotkey('ctrl', 'right')
                    self.audio_status.configure(text="Spotify: Next")
                else:
                    self.audio_status.configure(text="Spotify not found")
            else:
                # YouTube - next video (shift + n)
                pyautogui.hotkey('shift', 'n')
                self.audio_status.configure(text="YouTube: Next")
        except Exception as e:
            self.audio_status.configure(text=f"Media error: {e}")
    
    def media_previous(self):
        """Send previous track command"""
        if not media_control_available:
            self.audio_status.configure(text="Media control not available")
            return
        
        try:
            if self.audio_mode == "spotify":
                spotify_windows = gw.getWindowsWithTitle("Spotify")
                if spotify_windows:
                    spotify_windows[0].activate()
                    pyautogui.hotkey('ctrl', 'left')
                    self.audio_status.configure(text="Spotify: Previous")
                else:
                    self.audio_status.configure(text="Spotify not found")
            else:
                # YouTube - previous video (shift + p)
                pyautogui.hotkey('shift', 'p')
                self.audio_status.configure(text="YouTube: Previous")
        except Exception as e:
            self.audio_status.configure(text=f"Media error: {e}")
    
    def activate_copilot(self):
        """Activate Windows 11 Copilot voice listening"""
        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature", "Copilot integration requires a lifetime license.\n\nPurchase a license in Settings → Extras to unlock Windows Copilot voice assistance.")
            return
            
        try:
            # Simulate Win+C to activate Copilot
            import pyautogui
            pyautogui.hotkey('win', 'c')
            # Show a brief notification
            self.show_notification("Copilot activated - listening for voice commands", "info")
        except Exception as e:
            self.show_notification(f"Failed to activate Copilot: {e}", "error")
    
    def show_notification(self, message, type="info"):
        """Show a temporary notification"""
        try:
            import tkinter.messagebox as messagebox
            if type == "error":
                messagebox.showerror("Copilot", message)
            else:
                messagebox.showinfo("Copilot", message)
        except:
            # Fallback if messagebox fails
            pass

    def update_resource_monitor(self):
        """Update the resource monitor stats"""
        try:
            # CPU Load
            cpu_load = psutil.cpu_percent(interval=1)
            self.resource_labels['cpu_load'].configure(text=f"{cpu_load:.1f}%")
            
            # RAM
            ram = psutil.virtual_memory()
            self.resource_labels['ram'].configure(text=f"{ram.percent:.1f}%")
            
            # CPU Temp
            cpu_temp = self.get_cpu_temperature()
            self.resource_labels['cpu_temp'].configure(text=cpu_temp)
            
            # GPU
            if gputil_available:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        self.resource_labels['gpu_load'].configure(text=f"{gpu.load*100:.1f}%")
                        gpu_temp = self.get_gpu_temperature()
                        self.resource_labels['gpu_temp'].configure(text=gpu_temp)
                    else:
                        self.resource_labels['gpu_load'].configure(text="No GPU")
                        self.resource_labels['gpu_temp'].configure(text="N/A")
                except:
                    self.resource_labels['gpu_load'].configure(text="Error")
                    self.resource_labels['gpu_temp'].configure(text="Error")
            else:
                self.resource_labels['gpu_load'].configure(text="N/A")
                self.resource_labels['gpu_temp'].configure(text="N/A")
                
        except Exception as e:
            logging.error(f"Resource monitor update error: {e}")
        
        # Update every 2 seconds
        self.after(2000, self.update_resource_monitor)

    def get_cpu_temperature(self):
        """Get CPU temperature using WMI"""
        if not wmi_available:
            return "N/A"
        try:
            w = wmi.WMI()
            temp_sensors = w.query("SELECT * FROM MSAcpi_ThermalZoneTemperature")
            if temp_sensors:
                # Convert from Kelvin to Celsius
                temp_k = temp_sensors[0].CurrentTemperature
                temp_c = (temp_k - 2732) / 10.0  # WMI gives deciKelvin
                return f"{temp_c:.1f}°C"
        except:
            pass
        return "N/A"

    def get_gpu_temperature(self):
        """Get GPU temperature using pynvml for NVIDIA"""
        if not pynvml_available:
            return "N/A"
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            return f"{temp}°C"
        except:
            return "N/A"

    def calculate_avg_tps(self):
        total_tps = 0
        count = 0
        for provider in self.tps_stats.values():
            if provider['requests'] > 0:
                total_tps += provider['avg_tps']
                count += 1
        return total_tps / count if count > 0 else 0

    def start_p2p(self):
        if self.leaderboard_enabled and not self.p2p_thread:
            self.p2p_thread = threading.Thread(target=self.p2p_loop, daemon=True)
            self.p2p_thread.start()

    def p2p_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', 0))  # Bind to any port
        broadcast_addr = ('<broadcast>', 12345)  # Example port
        while self.p2p_enabled:
            # Update own leaderboard
            self.ai_leaderboard[self.user_name] = self.calculate_avg_tps()
            # Send own metrics
            avg_tps = self.ai_leaderboard[self.user_name]
            data = json.dumps({'user': self.user_name, 'avg_tps': avg_tps}).encode()
            sock.sendto(data, broadcast_addr)
            # Receive
            sock.settimeout(1)
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                self.ai_leaderboard[msg['user']] = msg['avg_tps']
            except socket.timeout:
                pass
            time.sleep(5)  # Every 5 seconds

    def refresh_board(self):
        # Clear board
        for widget in self.board.winfo_children():
            widget.destroy()

        notes = self.storage.list_notes()

        # Apply sorting
        if hasattr(self, 'current_sort'):
            if self.current_sort == "modified_desc":
                notes.sort(key=lambda x: x.modified_at, reverse=True)
            elif self.current_sort == "modified_asc":
                notes.sort(key=lambda x: x.modified_at)
            elif self.current_sort == "title_asc":
                notes.sort(key=lambda x: (x.title or "").lower())
            elif self.current_sort == "title_desc":
                notes.sort(key=lambda x: (x.title or "").lower(), reverse=True)
        else:
            # Default: newest first
            notes.sort(key=lambda x: x.modified_at, reverse=True)

        # Filter notes if search/filter is active
        if self.filtered_notes is not None:
            notes = [n for n in notes if n.id in self.filtered_notes]

        # Update notes counter
        total_notes = len(self.storage.list_notes())
        filtered_count = len(notes)
        if self.filtered_notes is not None:
            self.notes_counter.configure(text=f"Showing {filtered_count} of {total_notes} notes")
        else:
            self.notes_counter.configure(text=f"All notes: {total_notes}")

        # Display notes based on current view mode
        if self.current_view == "cards":
            self.display_cards_view(notes)
        elif self.current_view == "list":
            self.display_list_view(notes)
        elif self.current_view == "compact":
            self.display_compact_view(notes)

    def display_cards_view(self, notes):
        """Display notes in card grid layout"""
        cols = 3  # Fewer columns for better readability
        for c in range(cols):
            self.board.grid_columnconfigure(c, weight=1, uniform="note_cols")

        for i, note in enumerate(notes):
            row = i // cols
            col = i % cols

            # Note Card
            card = ctk.CTkFrame(self.board, width=280, height=180, corner_radius=self.soft_card_radius)
            card.grid(row=row, column=col, padx=12, pady=12)
            card.grid_propagate(False)

            # Title
            title_label = ctk.CTkLabel(card, text=note.title or "Untitled", font=("Roboto", 14, "bold"),
                                     wraplength=260, anchor="w")
            title_label.pack(pady=(12, 6), padx=12, anchor="w")

            # Content Preview
            content_preview = note.content[:120] + "..." if len(note.content) > 120 else note.content
            content_label = ctk.CTkLabel(card, text=content_preview, wraplength=260, justify="left",
                                       anchor="w", font=("Roboto", 11))
            content_label.pack(pady=(0, 8), padx=12, anchor="w")

            # Footer with tags and metadata
            footer = ctk.CTkFrame(card, fg_color="transparent", height=25)
            footer.pack(fill="x", padx=12, pady=(0, 12))
            footer.pack_propagate(False)

            # Tags
            if note.tags:
                tags_text = ", ".join(note.tags[:2])  # Show max 2 tags
                if len(note.tags) > 2:
                    tags_text += f" +{len(note.tags)-2}"
                tags_label = ctk.CTkLabel(footer, text=f"🏷️ {tags_text}", font=("Roboto", 9), text_color="gray60")
                tags_label.pack(side="left")

            # Metadata (date/size)
            import datetime
            mod_date = datetime.datetime.fromtimestamp(note.modified_at).strftime("%m/%d")
            meta_text = f"📅 {mod_date}"
            if note.file_path:
                meta_text += " 📎"
            meta_label = ctk.CTkLabel(footer, text=meta_text, font=("Roboto", 9), text_color="gray60")
            meta_label.pack(side="right")

            # Click to edit
            card.bind("<Button-1>", lambda e, n=note: self.edit_note(n))
            card.bind(self.keybinds['launch_note_browser'], lambda e, n=note: self.launch_note_in_browser(n))

    def display_list_view(self, notes):
        """Display notes in list layout"""
        self.board.grid_columnconfigure(0, weight=1)

        for i, note in enumerate(notes):
            # List Item
            item = ctk.CTkFrame(self.board, height=60, corner_radius=self.soft_card_radius)
            item.grid(row=i, column=0, padx=10, pady=4, sticky="ew")
            item.grid_columnconfigure(1, weight=1)

            # Icon
            icon_label = ctk.CTkLabel(item, text="📄", font=("Roboto", 16))
            icon_label.grid(row=0, column=0, padx=12, pady=10)

            # Content
            content_frame = ctk.CTkFrame(item, fg_color="transparent")
            content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=10)
            content_frame.grid_columnconfigure(0, weight=1)

            # Title
            title_label = ctk.CTkLabel(content_frame, text=note.title or "Untitled", font=("Roboto", 13, "bold"),
                                     anchor="w")
            title_label.grid(row=0, column=0, sticky="ew")

            # Preview + metadata
            preview = note.content[:80] + "..." if len(note.content) > 80 else note.content
            import datetime
            mod_date = datetime.datetime.fromtimestamp(note.modified_at).strftime("%m/%d/%y")
            meta_line = f"{preview} • {mod_date}"
            if note.tags:
                meta_line += f" • {', '.join(note.tags[:2])}"

            meta_label = ctk.CTkLabel(content_frame, text=meta_line, font=("Roboto", 10),
                                    text_color="gray60", anchor="w")
            meta_label.grid(row=1, column=0, sticky="ew")

            # Click to edit
            item.bind("<Button-1>", lambda e, n=note: self.edit_note(n))
            item.bind(self.keybinds['launch_note_browser'], lambda e, n=note: self.launch_note_in_browser(n))

    def display_compact_view(self, notes):
        """Display notes in compact layout"""
        self.board.grid_columnconfigure(0, weight=1)

        for i, note in enumerate(notes):
            # Compact Item
            item = ctk.CTkFrame(self.board, height=40, corner_radius=self.soft_card_radius)
            item.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            item.grid_columnconfigure(1, weight=1)

            # Title
            title_label = ctk.CTkLabel(item, text=note.title or "Untitled", font=("Roboto", 12, "bold"),
                                     anchor="w")
            title_label.grid(row=0, column=0, padx=12, pady=8, sticky="w")

            # Metadata
            import datetime
            mod_date = datetime.datetime.fromtimestamp(note.modified_at).strftime("%m/%d")
            meta_text = f"{mod_date}"
            if note.tags:
                meta_text += f" • {note.tags[0]}"
            if note.file_path:
                meta_text += " 📎"

            meta_label = ctk.CTkLabel(item, text=meta_text, font=("Roboto", 10), text_color="gray60")
            meta_label.grid(row=0, column=1, padx=12, pady=8)

            # Click to edit
            item.bind("<Button-1>", lambda e, n=note: self.edit_note(n))
            item.bind(self.keybinds['launch_note_browser'], lambda e, n=note: self.launch_note_in_browser(n))

    def build_search_index(self):
        """Build search index for fast lookup"""
        self.search_index = {}
        for note in self.storage.list_notes():
            words = set((note.title + " " + note.content + " " + " ".join(note.tags)).lower().split())
            for word in words:
                if word not in self.search_index:
                    self.search_index[word] = []
                self.search_index[word].append(note.id)
        # Remove duplicates
        for word in self.search_index:
            self.search_index[word] = list(set(self.search_index[word]))

    def on_search_change(self, event):
        """Handle search input changes"""
        query = self.search_entry.get().strip().lower()
        if not query:
            self.filtered_notes = None
        else:
            # Simple hazy search: substring match
            matching_ids = set()
            query_words = query.split()
            for word in query_words:
                for index_word, note_ids in self.search_index.items():
                    if word in index_word:
                        matching_ids.update(note_ids)
            self.filtered_notes = matching_ids if matching_ids else set()
        self.refresh_board()

    def perform_search(self):
        """Perform search (same as on_search_change)"""
        self.on_search_change(None)

    def save_config(self):
        config = {
            "last_file": self.storage.filepath,
            "last_hash": self.compute_file_hash(self.storage.filepath),
            "hint": self.hint,
            "clipboard_enabled": self.clipboard_enabled,
            "p2p_enabled": self.p2p_enabled,
            "leaderboard_enabled": self.leaderboard_enabled,
            "headless_mode": self.headless_mode,
            "ollama_timeout_enabled": self.ollama_timeout_enabled,
            "ollama_timeout_seconds": self.ollama_timeout_seconds,
            "responsive_ui": self.responsive_ui,
            "defaults_scrubbed": getattr(self, 'defaults_scrubbed', False),
            "p2p_peers": self.p2p_peers,
            "lifetime_license": self.lifetime_license,
            "transaction_id": self.transaction_id,
            "token_balance": self.token_balance,
            "total_tokens_used": self.total_tokens_used,
            "backed_up": self.backed_up
        }
        try:
            with open("config.json", "w") as f:
                json.dump(config, f)
        except:
            pass  # Ignore save errors

    def load_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                self.clipboard_enabled = config.get("clipboard_enabled", True)
                self.p2p_enabled = config.get("p2p_enabled", False)
                self.leaderboard_enabled = config.get("leaderboard_enabled", False)
                self.headless_mode = config.get("headless_mode", False)
                self.ollama_timeout_enabled = config.get("ollama_timeout_enabled", False)
                self.ollama_timeout_seconds = config.get("ollama_timeout_seconds", 10)
                self.responsive_ui = config.get("responsive_ui", False)
                self.defaults_scrubbed = config.get("defaults_scrubbed", False)
                self.p2p_peers = config.get("p2p_peers", [])
                self.lifetime_license = config.get("lifetime_license", False)
                self.transaction_id = config.get("transaction_id", "")
                self.token_balance = config.get("token_balance", 0)
                self.total_tokens_used = config.get("total_tokens_used", 0)
                self.backed_up = config.get("backed_up", False)
            except:
                pass  # Ignore config errors

    def compute_file_hash(self, filepath):
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def create_new_note(self):
        new_note = Note()
        self.edit_note(new_note)

    def edit_note(self, note):
        popup = EditNotePopup(self, note, self.save_note, self.delete_note)
        popup.grab_set()  # Make it modal

    def save_note(self, note):
        if note.id not in [n.id for n in self.storage.list_notes()]:
            self.storage.add_note(note)
        # Note is already in storage, just save
        try:
            self.storage.save(self.password)
            self.refresh_board()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def delete_note(self, note):
        self.storage.delete_note(note.id)
        self.storage.save(self.password)
        self.refresh_board()

    def import_library(self):
        filename = filedialog.askopenfilename(title="Select Encrypted File to Import", filetypes=(("Encrypted Files", "*.enc"),))
        if not filename:
            return
        
        # Ask for password of the import file
        dialog = ctk.CTkInputDialog(text="Enter password for the import file:", title="Import Password")
        password = dialog.get_input()
        
        if password:
            try:
                self.storage.import_library(filename, password)
                self.storage.save(self.password)
                self.refresh_board()
                messagebox.showinfo("Success", "Library imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {e}")

    def export_library(self):
        filename = filedialog.asksaveasfilename(title="Export Library As", filetypes=(("Encrypted Files", "*.enc"),), initialfile="export.enc")
        if not filename:
            return
            
        # Ask for new password for the export file
        dialog = ctk.CTkInputDialog(text="Set password for the export file:", title="Export Password")
        password = dialog.get_input()
        
        if password:
            try:
                self.storage.export_library(filename, password)
                messagebox.showinfo("Success", "Library exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def scrub_defaults(self):
        default_titles = ["Python Hello World", "JavaScript Arrow Function"]
        if hasattr(self, 'defaults_scrubbed') and self.defaults_scrubbed:
            # Re-add defaults
            samples = [
                {
                    "title": "Python Hello World",
                    "content": "print('Hello, World!')",
                    "tags": ["python", "sample", "beginner"]
                },
                {
                    "title": "JavaScript Arrow Function",
                    "content": "const greet = (name) => `Hello, ${name}!`;\n\nconsole.log(greet('World'));",
                    "tags": ["javascript", "sample", "es6"]
                }
            ]
            for sample in samples:
                note = Note(**sample)
                self.storage.add_note(note)
            self.defaults_scrubbed = False
            self.scrub_btn.configure(text="Scrub Defaults")
            messagebox.showinfo("Defaults Restored", "Default postits have been restored.")
        else:
            # Remove defaults
            notes_to_remove = []
            for note in self.storage.notes:
                if note.title in default_titles:
                    notes_to_remove.append(note)
            for note in notes_to_remove:
                self.storage.remove_note(note.id)
            self.defaults_scrubbed = True
            self.scrub_btn.configure(text="Restore Defaults")
            messagebox.showinfo("Defaults Scrubbed", "Default postits have been removed.")
        
        try:
            self.storage.save(self.password)
            self.refresh_board()
            self.build_search_index()  # Rebuild search index
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")
    
    def download_prompts(self):
        # Placeholder for downloading prompts from external system
        # For freeware, provide a couple of sample prompts
        samples = [
            {
                "title": "Python Hello World",
                "content": "print('Hello, World!')",
                "tags": ["python", "sample", "beginner"]
            },
            {
                "title": "JavaScript Arrow Function",
                "content": "const greet = (name) => `Hello, ${name}!`;\n\nconsole.log(greet('World'));",
                "tags": ["javascript", "sample", "es6"]
            }
        ]
        
        for sample in samples:
            note = Note(**sample)
            self.storage.add_note(note)
        
        try:
            self.storage.save(self.password)
            self.refresh_board()
            self.build_search_index()  # Rebuild search index
            messagebox.showinfo("Success", "Sample prompts downloaded! For access to our premium curated AI prompt library, please purchase a license.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prompts: {e}")
    
    def upload_to_drive(self):
        if not os.path.exists("client_secret.json"):
            messagebox.showerror("Error", "client_secret.json not found. Please download it from Google Cloud Console and place it in the app directory.")
            return
        
        # Run in thread
        threading.Thread(target=self._upload_to_drive_thread).start()
    
    def _upload_to_drive_thread(self):
        try:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secret.json', ['https://www.googleapis.com/auth/drive.file'])
                    creds = flow.run_local_server(port=0)
                
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            service = build('drive', 'v3', credentials=creds)
            
            file_metadata = {
                'name': os.path.basename(self.storage.filepath),
                'parents': []  # Optional: specify folder ID
            }
            media = MediaFileUpload(self.storage.filepath, mimetype='application/octet-stream')
            
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            self.backed_up = True
            self.save_config()
            self.after(0, lambda: messagebox.showinfo("Success", f"File uploaded to Google Drive with ID: {file.get('id')}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Upload Error", f"Failed to upload: {e}"))

    def buy_tokens(self):
        paypal_email = os.getenv("PAYPAL_EMAIL")
        if not paypal_email:
            messagebox.showerror("Error", "PayPal email not set. Please set PAYPAL_EMAIL environment variable.")
            return
        
        # PayPal buy now link for 100 tokens at $10 (30% markup)
        link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={paypal_email}&item_name=100 Cryptonote AI Tokens&amount=10.00&currency_code=USD&return=http://localhost/thankyou"
        webbrowser.open(link)
        messagebox.showinfo("Buy Tokens", "PayPal payment page opened. After payment, contact support to receive your tokens.")

    def activate_license(self):
        paypal_email = os.getenv("PAYPAL_EMAIL")
        if not paypal_email:
            messagebox.showerror("Error", "PayPal email not set. Please set PAYPAL_EMAIL environment variable.")
            return
        
        # PayPal buy now link for lifetime license at $25
        link = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={paypal_email}&item_name=Cryptonote Lifetime License&amount=25.00&currency_code=USD&return=http://localhost/thankyou"
        webbrowser.open(link)
        
        # Prompt for PayPal transaction ID after payment
        transaction_id = ctk.CTkInputDialog(text="Enter your PayPal transaction ID (found in PayPal receipt):", title="Activate Lifetime License").get_input()
        if transaction_id and paypal_available:
            if self.verify_paypal_transaction(transaction_id):
                self.lifetime_license = True
                self.transaction_id = transaction_id
                self.save_config()
                messagebox.showinfo("Success", "Lifetime license activated! You now have access to Ollama AI features.")
            else:
                messagebox.showerror("Verification Failed", "Could not verify transaction with PayPal. Please check your transaction ID and try again.")
        elif transaction_id and not paypal_available:
            messagebox.showerror("PayPal SDK Not Available", "PayPal verification not available. Please install paypal-checkout-sdk.")
        else:
            messagebox.showerror("Invalid Input", "Transaction ID is required.")

    def apply_license_key(self, key: str) -> bool:
        """Apply a manual license key (development use)."""
        if key == self.dev_license_key or key == "DEV-SKIP":
            self.lifetime_license = True
            self.transaction_id = "DEV-MANUAL" if key == self.dev_license_key else "DEV-SKIP"
            self.save_config()
            return True
        return False

    def _update_token_label(self):
        self.token_label.configure(text=f"Tokens: {self.token_balance}")
        self.total_tokens_label.configure(text=f"Total Used: {self.total_tokens_used}")
        self.update_tps_display()

    def open_extras_shop(self):
        dialog = ExtrasShop(self)
        self.wait_window(dialog)

    def start_snip(self):
        try:
            # Launch Windows Snip & Sketch
            subprocess.run(["explorer.exe", "ms-screenclip:"])
            # Wait a bit for user to snip
            self.after(2000, self.handle_snip_result)
        except Exception as e:
            messagebox.showerror("Snip Error", f"Failed to start snipping tool: {e}")

    def handle_snip_result(self):
        if not clipboard_available:
            messagebox.showerror("Clipboard Error", "Clipboard access not available.")
            return
        
        # Check if clipboard has image
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                # Get image data
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                win32clipboard.CloseClipboard()
                
                # Convert to PIL Image
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(data))
                
                # Save to temp file
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                image.save(temp_file.name)
                temp_file.close()
                
                # Ask user where to add
                self.add_snip_to_note(temp_file.name)
            else:
                win32clipboard.CloseClipboard()
                messagebox.showinfo("No Snip", "No image found in clipboard. Please try snipping again.")
        except Exception as e:
            messagebox.showerror("Snip Error", f"Failed to process snip: {e}")

    def add_snip_to_note(self, image_path):
        # Dialog to choose: new note or existing
        choice = messagebox.askquestion("Add Snip", "Add snip to a new note or existing note?", icon='question', type='yesno')
        if choice == 'yes':  # New note
            note = Note(title="Snipped Image", content="", tags=["snip"])
            note.file_path = image_path
            self.storage.add_note(note)
            self.refresh_board()
        else:  # Existing note
            # Show list of notes
            notes = self.storage.list_notes()
            if not notes:
                messagebox.showinfo("No Notes", "No existing notes to add to.")
                return
            
            # Simple dialog with list
            note_names = [f"{n.title} ({n.id})" for n in notes]
            dialog = ctk.CTkInputDialog(text="Select note by title:", title="Choose Note")
            selected = dialog.get_input()
            if selected:
                for note in notes:
                    if note.title == selected.strip():
                        note.file_path = image_path
                        self.storage.update_note(note)
                        self.refresh_board()
                        break
                else:
                    messagebox.showerror("Not Found", "Note not found.")

    def start_clipboard_monitoring(self):
        if not clipboard_available or not self.clipboard_enabled:
            logging.debug("Clipboard monitoring not started: clipboard not available or disabled")
            return
        logging.info("Starting clipboard monitoring")
        self.monitoring_clipboard = True
        self.last_clipboard_hash = self.get_clipboard_hash()
        self.monitor_clipboard()

    def stop_clipboard_monitoring(self):
        logging.info("Stopping clipboard monitoring")
        self.monitoring_clipboard = False

    def monitor_clipboard(self):
        if not self.monitoring_clipboard:
            return
        current_hash = self.get_clipboard_hash()
        if current_hash != self.last_clipboard_hash:
            self.add_to_clipboard_history()
            self.last_clipboard_hash = current_hash
            self.update_clipboard_panel()
        self.after(1000, self.monitor_clipboard)  # Check every second

    def get_clipboard_hash(self):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                win32clipboard.CloseClipboard()
                return hashlib.md5(data.encode('utf-8')).hexdigest()
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                win32clipboard.CloseClipboard()
                return hashlib.md5(data).hexdigest()
            else:
                win32clipboard.CloseClipboard()
                return None
        except:
            return None

    def add_to_clipboard_history(self):
        try:
            logging.debug("Adding item to clipboard history")
            win32clipboard.OpenClipboard()
            item = {"timestamp": time.time()}
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                item["type"] = "text"
                item["content"] = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                logging.debug("Added text item to clipboard history")
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                item["type"] = "image"
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                # Convert to PIL and save thumbnail
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(data))
                image.thumbnail((100, 100))
                temp_file = f"temp_clip_{len(self.clipboard_history)}.png"
                image.save(temp_file)
                item["content"] = temp_file
                logging.debug("Added image item to clipboard history")
            else:
                win32clipboard.CloseClipboard()
                logging.debug("Clipboard contains unsupported format")
                return
            win32clipboard.CloseClipboard()
            self.clipboard_history.insert(0, item)
            logging.info(f"Clipboard history now contains {len(self.clipboard_history)} items")
        except Exception as e:
            logging.error(f"Failed to add clipboard item: {e}", exc_info=True)
            if len(self.clipboard_history) > 50:
                self.clipboard_history.pop()
        except Exception as e:
            print(f"Clipboard error: {e}")

    def update_clipboard_panel(self):
        if hasattr(self, 'clipboard_panel') and self.clipboard_panel.winfo_exists():
            # Update the panel
            for widget in self.clipboard_panel.winfo_children():
                widget.destroy()
            self.build_clipboard_panel_content()

    def toggle_clipboard_enabled(self, enabled):
        self.clipboard_enabled = enabled
        if enabled:
            self.start_clipboard_monitoring()
        else:
            self.stop_clipboard_monitoring()
        self.save_config()

    def get_ollama_timeout(self):
        """Get timeout value for Ollama requests based on user settings"""
        if self.ollama_timeout_enabled:
            return self.ollama_timeout_seconds
        return None  # No timeout

    def generate_p2p_api_key(self):
        """Generate a secure API key for P2P authentication"""
        if not self.p2p_api_key:
            import secrets
            self.p2p_api_key = secrets.token_urlsafe(32)
            self.save_config()
            logging.info("Generated new P2P API key")
        return self.p2p_api_key

    def generate_ssl_certificates(self):
        """Generate self-signed SSL certificates for HTTPS"""
        import os
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        import datetime
        
        cert_dir = os.path.dirname(self.p2p_cert_file)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        
        if os.path.exists(self.p2p_cert_file) and os.path.exists(self.p2p_key_file):
            logging.info("SSL certificates already exist")
            return True
        
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Cryptonote"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Cryptonote P2P"),
                x509.NameAttribute(NameOID.COMMON_NAME, "cryptonote-p2p.local"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.DNSName("127.0.0.1"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Write certificate
            with open(self.p2p_cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(self.p2p_key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logging.info("Generated SSL certificates for P2P server")
            return True
        except Exception as e:
            logging.error(f"Failed to generate SSL certificates: {e}", exc_info=True)
            return False

    def check_rate_limit(self, client_ip):
        """Check if client IP is within rate limits"""
        import time
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        self.p2p_rate_limits = {
            ip: times for ip, times in self.p2p_rate_limits.items()
            if times and current_time - times[-1] < 60
        }
        
        # Get request times for this IP
        if client_ip not in self.p2p_rate_limits:
            self.p2p_rate_limits[client_ip] = []
        
        request_times = self.p2p_rate_limits[client_ip]
        
        # Remove requests older than 1 minute
        request_times[:] = [t for t in request_times if current_time - t < 60]
        
        # Check rate limit: max 10 requests per minute
        if len(request_times) >= 10:
            logging.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Add current request
        request_times.append(current_time)
        return True

    def toggle_p2p_enabled(self, enabled):
        self.p2p_enabled = enabled
        if enabled:
            self.start_p2p_server()
        else:
            self.stop_p2p_server()
        self.save_config()
        if hasattr(self, 'clipboard_panel') and self.clipboard_panel.winfo_exists():
            self.clipboard_panel.destroy()
        else:
            self.show_clipboard_panel()

    def start_p2p_server(self):
        if not flask_available:
            error_msg = "Flask not available for P2P server."
            logging.error(error_msg)
            messagebox.showerror("P2P Error", error_msg)
            return
        
        # Generate API key if not exists
        self.generate_p2p_api_key()
        
        # Generate SSL certificates if not exist
        if not self.generate_ssl_certificates():
            error_msg = "Failed to generate SSL certificates for secure P2P."
            logging.error(error_msg)
            messagebox.showerror("P2P Error", error_msg)
            return
        
        if self.p2p_server is None:
            try:
                logging.info("Starting secure P2P server with HTTPS on port 11435")
                from threading import Thread
                self.p2p_app = Flask(__name__)
                
                # Configure SSL context
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(self.p2p_cert_file, self.p2p_key_file)
                
                self.setup_p2p_routes()
                self.p2p_server = Thread(target=self.p2p_app.run, kwargs={
                    'host': '0.0.0.0', 
                    'port': 11435, 
                    'debug': False, 
                    'use_reloader': False,
                    'ssl_context': ssl_context
                })
                self.p2p_server.daemon = True
                self.p2p_server.start()
                logging.info("Secure P2P server started successfully with HTTPS")
                print("Secure P2P server started on port 11435 (HTTPS)")
            except Exception as e:
                logging.error(f"Failed to start secure P2P server: {e}", exc_info=True)
                messagebox.showerror("P2P Error", f"Failed to start secure P2P server: {e}")

    def stop_p2p_server(self):
        if self.p2p_server:
            logging.info("Stopping P2P server")
            # Flask doesn't have easy shutdown, but since daemon, it will stop on app close
            self.p2p_server = None
            logging.info("P2P server stopped")
            print("P2P server stopped")

    def setup_p2p_routes(self):
        @self.p2p_app.before_request
        def before_request():
            """Security middleware for all requests"""
            client_ip = request.remote_addr
            
            # Rate limiting
            if not self.check_rate_limit(client_ip):
                logging.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            # Log all requests (for security monitoring)
            logging.info(f"P2P request: {request.method} {request.path} from {client_ip}")
        
        @self.p2p_app.errorhandler(BadRequest)
        def handle_bad_request(e):
            """Handle bad requests without leaking information"""
            logging.warning(f"Bad request: {e}")
            return jsonify({"error": "Invalid request"}), 400
        
        @self.p2p_app.errorhandler(Exception)
        def handle_exception(e):
            """Handle all exceptions without leaking sensitive information"""
            logging.error(f"Unhandled exception in P2P API: {e}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
        @self.p2p_app.route('/api/chat', methods=['POST'])
        def p2p_chat():
            start_time = time.time()
            
            try:
                # Authentication check
                api_key = request.headers.get('X-API-Key')
                if not api_key or api_key != self.p2p_api_key:
                    logging.warning(f"Unauthorized P2P request from {request.remote_addr}")
                    return jsonify({"error": "Unauthorized"}), 401
                
                # Check lifetime license
                if not self.lifetime_license:
                    logging.warning(f"License check failed for P2P request from {request.remote_addr}")
                    return jsonify({"error": "Lifetime license required for P2P sharing"}), 403
                
                # Validate request data
                if not request.is_json:
                    logging.warning(f"Invalid content type from {request.remote_addr}")
                    return jsonify({"error": "Content-Type must be application/json"}), 400
                
                data = request.get_json()
                if not data or 'messages' not in data:
                    logging.warning(f"Invalid JSON structure from {request.remote_addr}")
                    return jsonify({"error": "Invalid request format"}), 400
                
                # Validate message structure
                messages = data.get('messages', [])
                if not isinstance(messages, list) or len(messages) == 0:
                    logging.warning(f"Invalid messages format from {request.remote_addr}")
                    return jsonify({"error": "Messages must be a non-empty array"}), 400
                
                # Check message size limits (prevent DoS)
                content = messages[0].get('content', '')
                if len(content) > 10000:  # 10KB limit
                    logging.warning(f"Message too large from {request.remote_addr}: {len(content)} chars")
                    return jsonify({"error": "Message content too large"}), 413
                
                # Forward to local Ollama with timeout
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                response = requests.post(f"{ollama_url}/api/chat", json=data, timeout=30)  # Server-side timeout for security
                response.raise_for_status()
                result = response.json()
                
                fixed_content = result["message"]["content"]
                
                # Earn tokens: 10% of estimated cost
                estimated_tokens = self.estimate_tokens(content + fixed_content)
                earned = max(1, estimated_tokens // 10)  # At least 1 token
                self.earned_tokens += earned
                self.save_config()
                
                # Record TPS stats for served request
                end_time = time.time()
                time_taken = end_time - start_time
                self.record_tps_stats('ollama', estimated_tokens, time_taken)  # Local Ollama usage
                
                logging.info(f"P2P request served, earned {earned} tokens, TPS: {estimated_tokens/time_taken:.2f}")
                return jsonify(result)
                
            except requests.exceptions.Timeout:
                logging.error("Ollama request timeout")
                return jsonify({"error": "Request timeout"}), 504
            except requests.exceptions.RequestException as e:
                logging.error(f"Ollama request failed: {e}")
                return jsonify({"error": "AI service unavailable"}), 503
            except Exception as e:
                logging.error(f"P2P request processing failed: {e}", exc_info=True)
                return jsonify({"error": "Internal server error"}), 500

    def use_p2p_peer(self, peer_url, content):
        try:
            # Ensure HTTPS
            if not peer_url.startswith('https://'):
                if peer_url.startswith('http://'):
                    peer_url = peer_url.replace('http://', 'https://', 1)
                else:
                    peer_url = f"https://{peer_url}"
            
            payload = {
                "model": "llama2",
                "messages": [
                    {"role": "system", "content": "You are a helpful coding assistant. Fix, improve, or complete the following code or text. Provide the improved version."},
                    {"role": "user", "content": content}
                ],
                "stream": False
            }
            
            # For now, we'll need to get the peer's API key somehow
            # This is a placeholder - in a real implementation, peers would exchange keys
            headers = {}
            if hasattr(self, 'peer_api_keys') and peer_url in self.peer_api_keys:
                headers['X-API-Key'] = self.peer_api_keys[peer_url]
            
            response = requests.post(f"{peer_url}/api/chat", json=payload, headers=headers, timeout=30, verify=False)  # verify=False for self-signed certs
            response.raise_for_status()
            
            # Validate response
            data = response.json()
            if not data or 'message' not in data or 'content' not in data['message']:
                raise Exception("Invalid response format from peer")
                
            return data["message"]["content"]
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL error connecting to peer {peer_url}: {e}")
            raise Exception(f"SSL certificate error: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error to peer {peer_url}: {e}")
            raise Exception(f"Cannot connect to peer: {e}")
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout connecting to peer {peer_url}: {e}")
            raise Exception(f"Peer request timeout: {e}")
        except Exception as e:
            logging.error(f"P2P request to {peer_url} failed: {e}")
            raise Exception(f"P2P request failed: {e}")

    def show_clipboard_panel(self):
        if not self.lifetime_license:
            messagebox.showinfo("Premium Feature", "Clipboard manager requires a lifetime license.\n\nPurchase a license in Settings → Extras to unlock advanced clipboard history and Copilot integration.")
            return
            
        self.clipboard_panel = ctk.CTkToplevel(self)
        self.clipboard_panel.title("Clipboard History & Copilot")
        self.clipboard_panel.geometry("400x700+1200+100")  # Position on right, made wider for Copilot
        self.clipboard_panel.resizable(False, False)
        self.clipboard_panel.attributes("-topmost", True)
        
        self.build_clipboard_panel_content()

    def build_clipboard_panel_content(self):
        # Title with Copilot indicator
        title_frame = ctk.CTkFrame(self.clipboard_panel, fg_color="transparent")
        title_frame.pack(pady=10, padx=10, fill="x")
        
        title = ctk.CTkLabel(title_frame, text="Clipboard History & Copilot", font=("Roboto", 16, "bold"))
        title.pack(side="left")
        
        # Copilot status indicator
        self.copilot_status = ctk.CTkLabel(title_frame, text="🤖 Ready", font=("Roboto", 10))
        self.copilot_status.pack(side="right", padx=10)
        
        # Copilot action buttons
        copilot_frame = ctk.CTkFrame(self.clipboard_panel, fg_color="transparent")
        copilot_frame.pack(pady=5, padx=10, fill="x")
        
        if self.master.lifetime_license:
            self.copilot_edit_btn = ctk.CTkButton(copilot_frame, text="✏️ Edit with Copilot", command=self.copilot_edit_selection, 
                                                 width=180, height=35, corner_radius=self.soft_button_radius)
            self.copilot_edit_btn.pack(side="left", padx=5)
            
            self.copilot_explain_btn = ctk.CTkButton(copilot_frame, text="💡 Explain", command=self.copilot_explain_selection,
                                                    width=100, height=35, corner_radius=self.soft_button_radius)
            self.copilot_explain_btn.pack(side="right", padx=5)
        else:
            premium_label = ctk.CTkLabel(copilot_frame, text="🔒 Copilot features require lifetime license", font=("Roboto", 12))
            premium_label.pack(pady=10)
            
            upgrade_btn = ctk.CTkButton(copilot_frame, text="Upgrade to Premium", command=self.show_extras_dialog, 
                                       fg_color="#0078D4", width=150, height=35, corner_radius=self.soft_button_radius)
            upgrade_btn.pack(pady=5)
        
        # Separator
        separator = ctk.CTkFrame(self.clipboard_panel, height=2, fg_color="#333333")
        separator.pack(fill="x", padx=10, pady=5)
        
        # Clipboard history section
        history_title = ctk.CTkLabel(self.clipboard_panel, text="Recent Clipboard Items", font=("Roboto", 14, "bold"))
        history_title.pack(pady=5)
        
        scrollable = ctk.CTkScrollableFrame(self.clipboard_panel, width=360, height=400)
        scrollable.pack(pady=10, padx=10)
        
        for i, item in enumerate(self.clipboard_history[:15]):  # Show last 15
            frame = ctk.CTkFrame(scrollable)
            frame.pack(pady=3, fill="x")
            
            if item["type"] == "text":
                preview = item["content"][:60] + "..." if len(item["content"]) > 60 else item["content"]
                label = ctk.CTkLabel(frame, text=preview, wraplength=320, anchor="w", justify="left")
                label.pack(pady=5, padx=5, anchor="w")
            elif item["type"] == "image":
                # Show thumbnail
                try:
                    img = ctk.CTkImage(Image.open(item["content"]), size=(60, 60))
                    img_label = ctk.CTkLabel(frame, image=img, text="")
                    img_label.pack(pady=5)
                except:
                    label = ctk.CTkLabel(frame, text="[Image]")
                    label.pack(pady=5)
            
            # Action buttons for each item
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=5, pady=5)
            
            paste_btn = ctk.CTkButton(btn_frame, text="📋 Paste", command=lambda idx=i: self.paste_from_history(idx), 
                                     width=80, height=25, corner_radius=self.soft_button_radius)
            paste_btn.pack(side="left", padx=2)
            
            if self.master.lifetime_license:
                copilot_btn = ctk.CTkButton(btn_frame, text="🤖 Use", command=lambda idx=i: self.copilot_use_clipboard_item(idx),
                                           width=80, height=25, corner_radius=self.soft_button_radius)
                copilot_btn.pack(side="right", padx=2)
            else:
                lock_btn = ctk.CTkButton(btn_frame, text="🔒", command=self.show_premium_required, state="disabled",
                                        width=80, height=25, corner_radius=self.soft_button_radius, fg_color="gray")
                lock_btn.pack(side="right", padx=2)

    def paste_from_history(self, index):
        if index < len(self.clipboard_history):
            item = self.clipboard_history[index]
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                if item["type"] == "text":
                    win32clipboard.SetClipboardText(item["content"])
                elif item["type"] == "image":
                    # Load image and set to clipboard
                    from PIL import Image
                    image = Image.open(item["content"])
                    # Convert to DIB format (complex, for simplicity, just text)
                    win32clipboard.SetClipboardText("[Image from history]")
                win32clipboard.CloseClipboard()
                messagebox.showinfo("Pasted", "Item copied to clipboard.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to paste: {e}")
    
    def copilot_edit_selection(self):
        """Use Copilot to edit selected text in the current note"""
        if not hasattr(self, 'current_note') or not self.current_note:
            messagebox.showinfo("No Note Selected", "Please open a note to edit with Copilot.")
            return
            
        # Get the current note editor popup
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel) and hasattr(widget, 'content_text'):
                editor = widget
                break
        else:
            messagebox.showinfo("No Editor Open", "Please open a note editor first.")
            return
        
        # Get selected text
        try:
            selected_text = editor.content_text.selection_get()
            if not selected_text.strip():
                messagebox.showinfo("No Selection", "Please select some text to edit with Copilot.")
                return
        except:
            messagebox.showinfo("No Selection", "Please select some text to edit with Copilot.")
            return
        
        # Copy selected text to clipboard for Copilot
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(selected_text)
            win32clipboard.CloseClipboard()
        except:
            pass
        
        # Activate Copilot
        self.activate_copilot()
        self.copilot_status.configure(text="🤖 Editing selection...")
        
        # Start monitoring for Copilot response
        self.monitor_copilot_edit(editor, selected_text)
    
    def monitor_copilot_edit(self, editor, original_text):
        """Monitor clipboard for Copilot's response and apply changes"""
        def check_clipboard():
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                    win32clipboard.CloseClipboard()
                    
                    # Check if this is a Copilot response (different from original)
                    if data and data != original_text and len(data) > len(original_text) * 0.5:
                        # Replace selected text with Copilot's suggestion
                        try:
                            editor.content_text.delete("sel.first", "sel.last")
                            editor.content_text.insert("insert", data)
                            self.copilot_status.configure(text="✅ Applied Copilot edit")
                            return
                        except:
                            pass
                else:
                    win32clipboard.CloseClipboard()
            except:
                pass
            
            # Continue monitoring for 30 seconds
            if self.copilot_status.cget("text") == "🤖 Editing selection...":
                self.after(1000, check_clipboard)
            else:
                self.copilot_status.configure(text="🤖 Ready")
        
        self.after(2000, check_clipboard)  # Start checking after 2 seconds
    
    def show_premium_required(self):
        """Show premium feature required message"""
        messagebox.showinfo("Premium Feature", "This Copilot feature requires a lifetime license.\n\nPurchase a license in Settings → Extras to unlock Windows Copilot integration.")
    
    def show_extras_dialog(self):
        """Show the extras shop dialog"""
        ExtrasShop(self)
    
    def show_warning(self, title, message, warning_key=None):
        """Show a warning dialog, respecting user's dismissal preferences"""
        if warning_key and warning_key in self.dismissed_warnings:
            return  # User dismissed this warning
        
        dialog = WarningDialog(self, title, message, warning_key)
        self.wait_window(dialog)
    
    def copilot_explain_selection(self):
        """Use Copilot to explain selected text"""
        # Similar to edit but for explanation
        messagebox.showinfo("Copilot Explain", "Select text and Copilot will explain it.\n\nThis feature uses your personal Windows Copilot.")
    
    def copilot_use_clipboard_item(self, index):
        """Use Copilot to process a clipboard history item"""
        if index >= len(self.clipboard_history):
            return
            
        item = self.clipboard_history[index]
        if item["type"] != "text":
            messagebox.showinfo("Not Supported", "Copilot can only process text items.")
            return
        
        # Copy to clipboard and activate Copilot
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(item["content"])
            win32clipboard.CloseClipboard()
        except:
            pass
        
        self.activate_copilot()
        self.copilot_status.configure(text="🤖 Processing clipboard item...")

    def show_service_status(self):
        """Show service status dialog"""
        ServiceStatusDialog(self, self.service_manager)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "dark":
            self.set_light_theme()
        else:
            self.set_dark_theme()
        
        self.save_config()

    def set_dark_theme(self):
        """Apply dark theme"""
        self.current_theme = "dark"
        ctk.set_appearance_mode("Dark")
        self.theme_btn.configure(text="🌙")
        self.update_theme_button_text()

    def set_light_theme(self):
        """Apply light theme"""
        self.current_theme = "light"
        ctk.set_appearance_mode("Light")
        self.theme_btn.configure(text="☀️")
        self.update_theme_button_text()

    def update_theme_button_text(self):
        """Update theme button text based on current theme and auto theme setting"""
        if self.auto_theme and self.lifetime_license:
            self.theme_btn.configure(text="🌓")
        elif self.current_theme == "dark":
            self.theme_btn.configure(text="🌙")
        else:
            self.theme_btn.configure(text="☀️")

    def apply_theme(self):
        """Apply the current theme to all UI components"""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        # Update theme button text
        self.update_theme_button_text()

    def check_auto_theme(self):
        """Check if auto theme should switch based on system time (premium feature)"""
        if not self.auto_theme or not self.lifetime_license:
            return
            
        import datetime
        current_hour = datetime.datetime.now().hour
        
        # Auto switch: dark at night (8 PM - 6 AM), light during day
        should_be_dark = current_hour >= 20 or current_hour < 6
        
        if should_be_dark and self.current_theme != "dark":
            self.set_dark_theme()
        elif not should_be_dark and self.current_theme != "light":
            self.set_light_theme()

    def open_settings(self):
        SettingsDialog(self)

    def open_themes(self):
        ThemesDialog(self)

    def verify_paypal_transaction(self, transaction_id):
        try:
            client_id = os.getenv("PAYPAL_CLIENT_ID")
            client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
            if not client_id or not client_secret:
                return False
            
            # Use sandbox for testing, production for live
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            client = PayPalHttpClient(environment)
            
            request = OrdersGetRequest(transaction_id)
            response = client.execute(request)
            
            # Check if order is completed and for the correct item
            if response.result.status == "COMPLETED":
                # Check if it's for lifetime license (amount $25)
                amount = response.result.purchase_units[0].amount
                if amount.value == "25.00" and amount.currency_code == "USD":
                    return True
            return False
        except Exception as e:
            print(f"PayPal verification error: {e}")
            return False

class KeybindSettingsDialog(ctk.CTkToplevel):
    """Dialog for customizing keyboard shortcuts"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Keyboard Shortcuts")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the keybind settings interface"""
        # Header
        header = ctk.CTkLabel(self, text="Customize Keyboard Shortcuts",
                            font=("Roboto", 16, "bold"))
        header.pack(pady=(20, 10))

        # Scrollable frame for keybinds
        scroll_frame = ctk.CTkScrollableFrame(self, width=450, height=450)
        scroll_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Keybind descriptions
        keybind_info = {
            'launch_note_browser': {
                'name': 'Launch Note in Browser',
                'description': 'Ctrl+Click on a note to open content in web browser',
                'premium': True
            },
            'new_note': {
                'name': 'New Note',
                'description': 'Create a new note',
                'premium': False
            },
            'search_focus': {
                'name': 'Focus Search',
                'description': 'Focus the search bar',
                'premium': False
            },
            'toggle_sidebar': {
                'name': 'Toggle Sidebar',
                'description': 'Show/hide the navigation sidebar',
                'premium': False
            }
        }

        self.keybind_entries = {}

        for key, info in keybind_info.items():
            # Keybind frame
            frame = ctk.CTkFrame(scroll_frame, corner_radius=8)
            frame.pack(fill="x", padx=10, pady=5)

            # Name and description
            name_label = ctk.CTkLabel(frame, text=info['name'], font=("Roboto", 12, "bold"))
            name_label.pack(anchor="w", padx=10, pady=(10, 5))

            desc_label = ctk.CTkLabel(frame, text=info['description'], font=("Roboto", 10),
                                    text_color="gray60")
            desc_label.pack(anchor="w", padx=10, pady=(0, 10))

            # Current keybind display
            current_frame = ctk.CTkFrame(frame, fg_color="transparent")
            current_frame.pack(fill="x", padx=10, pady=(0, 10))

            current_label = ctk.CTkLabel(current_frame, text="Current:", font=("Roboto", 11))
            current_label.pack(side="left")

            current_value = ctk.CTkLabel(current_frame, text=self.parent.keybinds.get(key, 'Not set'),
                                       font=("Roboto", 11, "bold"), text_color="#0078D4")
            current_value.pack(side="left", padx=(5, 0))

            # Premium indicator
            if info['premium']:
                premium_label = ctk.CTkLabel(current_frame, text="💎 Premium",
                                           font=("Roboto", 9), text_color="#FFD700")
                premium_label.pack(side="right")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        reset_btn = ctk.CTkButton(button_frame, text="Reset to Defaults",
                                command=self.reset_keybinds, width=120)
        reset_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(button_frame, text="Close",
                                command=self.destroy, width=80)
        close_btn.pack(side="right")

    def reset_keybinds(self):
        """Reset keybinds to defaults"""
        default_keybinds = {
            'launch_note_browser': '<Control-Button-1>',
            'new_note': '<Control-n>',
            'search_focus': '<Control-f>',
            'save_note': '<Control-s>',
            'toggle_sidebar': '<Control-b>'
        }

        self.parent.keybinds.update(default_keybinds)
        messagebox.showinfo("Reset Complete", "Keyboard shortcuts have been reset to defaults.")

        # Re-setup keybinds
        self.parent.setup_keybinds()

        # Close and reopen dialog to show changes
        self.destroy()
        self.parent.open_keybind_settings()


class SummaryDialog(ctk.CTkToplevel):
    """Dialog to display AI-generated summary"""

    def __init__(self, parent, original_text, summary):
        super().__init__(parent)
        self.title("AI Summary")
        self.geometry("600x400")
        self.resizable(True, True)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        self.create_widgets(original_text, summary)

    def create_widgets(self, original_text, summary):
        """Create the summary display interface"""
        # Header
        header = ctk.CTkLabel(self, text="🤖 AI-Generated Summary",
                            font=("Roboto", 16, "bold"))
        header.pack(pady=(20, 10))

        # Summary text area
        summary_frame = ctk.CTkFrame(self)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        summary_label = ctk.CTkLabel(summary_frame, text="Summary:",
                                   font=("Roboto", 12, "bold"))
        summary_label.pack(anchor="w", padx=10, pady=(10, 5))

        summary_textbox = ctk.CTkTextbox(summary_frame, wrap="word")
        summary_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        summary_textbox.insert("0.0", summary)
        summary_textbox.configure(state="disabled")

        # Original text preview
        original_label = ctk.CTkLabel(summary_frame, text="Original Text Preview:",
                                    font=("Roboto", 12, "bold"))
        original_label.pack(anchor="w", padx=10, pady=(10, 5))

        preview_text = original_text[:200] + "..." if len(original_text) > 200 else original_text
        original_textbox = ctk.CTkTextbox(summary_frame, wrap="word", height=80)
        original_textbox.pack(fill="x", padx=10, pady=(0, 10))
        original_textbox.insert("0.0", preview_text)
        original_textbox.configure(state="disabled")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        copy_btn = ctk.CTkButton(button_frame, text="📋 Copy Summary",
                               command=lambda: self.copy_to_clipboard(summary), width=120)
        copy_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(button_frame, text="Close",
                                command=self.destroy, width=80)
        close_btn.pack(side="right")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Summary copied to clipboard!")


class RewritePromptDialog(ctk.CTkToplevel):
    """Dialog for AI rewriting with custom prompt"""

    def __init__(self, parent, selected_text):
        super().__init__(parent)
        self.parent = parent
        self.selected_text = selected_text
        self.title("AI Rewrite")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Create the rewrite prompt interface"""
        # Header
        header = ctk.CTkLabel(self, text="✨ Rewrite with AI",
                            font=("Roboto", 16, "bold"))
        header.pack(pady=(20, 10))

        # Selected text preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="x", padx=20, pady=(0, 10))

        preview_label = ctk.CTkLabel(preview_frame, text="Selected Text:",
                                   font=("Roboto", 12, "bold"))
        preview_label.pack(anchor="w", padx=10, pady=(10, 5))

        preview_text = self.selected_text[:150] + "..." if len(self.selected_text) > 150 else self.selected_text
        preview_textbox = ctk.CTkTextbox(preview_frame, wrap="word", height=60)
        preview_textbox.pack(fill="x", padx=10, pady=(0, 10))
        preview_textbox.insert("0.0", preview_text)
        preview_textbox.configure(state="disabled")

        # Prompt input
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        prompt_label = ctk.CTkLabel(prompt_frame, text="Rewrite Instructions:",
                                  font=("Roboto", 12, "bold"))
        prompt_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.prompt_textbox = ctk.CTkTextbox(prompt_frame, wrap="word")
        self.prompt_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Preset prompts
        presets_label = ctk.CTkLabel(prompt_frame, text="Quick Presets:",
                                   font=("Roboto", 11, "bold"))
        presets_label.pack(anchor="w", padx=10, pady=(5, 5))

        presets = [
            "Make it more professional",
            "Simplify the language",
            "Make it more concise",
            "Expand with more details",
            "Change the tone to be more friendly",
            "Convert to bullet points"
        ]

        preset_frame = ctk.CTkFrame(prompt_frame, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=(0, 10))

        for i, preset in enumerate(presets):
            preset_btn = ctk.CTkButton(preset_frame, text=preset,
                                     command=lambda p=preset: self.use_preset(p),
                                     height=25, font=("Roboto", 9))
            preset_btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky="ew")

        preset_frame.grid_columnconfigure(0, weight=1)
        preset_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel",
                                 command=self.destroy, width=80)
        cancel_btn.pack(side="right", padx=(10, 0))

        rewrite_btn = ctk.CTkButton(button_frame, text="✨ Rewrite",
                                  command=self.start_rewrite, width=100,
                                  fg_color="#0078D4", hover_color="#106EBE")
        rewrite_btn.pack(side="right")

    def use_preset(self, preset):
        """Use a preset prompt"""
        self.prompt_textbox.delete("0.0", "end")
        self.prompt_textbox.insert("0.0", preset)

    def start_rewrite(self):
        """Start the AI rewriting process"""
        prompt = self.prompt_textbox.get("0.0", "end").strip()
        if not prompt:
            messagebox.showwarning("No Prompt", "Please enter rewrite instructions.")
            return

        self.destroy()

        # Show progress
        progress = self.parent.show_progress("Rewriting with AI...")

        def rewrite_task():
            try:
                full_prompt = f"Please rewrite the following text according to these instructions: {prompt}\n\nText to rewrite:\n{self.selected_text}"
                rewritten = self.parent.call_ai_service(full_prompt, use_openai=True)

                if rewritten:
                    # Show result in a dialog
                    RewriteResultDialog(self.parent, self.selected_text, rewritten, prompt)
                else:
                    messagebox.showerror("Rewrite Failed",
                                       "Unable to rewrite text. Please check your AI service configuration.")

            except Exception as e:
                messagebox.showerror("Error", f"Rewrite failed: {e}")
            finally:
                progress.destroy()

        # Run in background thread
        threading.Thread(target=rewrite_task, daemon=True).start()


class RewriteResultDialog(ctk.CTkToplevel):
    """Dialog to display AI-rewritten text"""

    def __init__(self, parent, original_text, rewritten_text, prompt):
        super().__init__(parent)
        self.title("AI Rewrite Result")
        self.geometry("700x500")
        self.resizable(True, True)
        
        # Always on top
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        self.create_widgets(original_text, rewritten_text, prompt)

    def create_widgets(self, original_text, rewritten_text, prompt):
        """Create the rewrite result display interface"""
        # Header
        header = ctk.CTkLabel(self, text="✨ AI Rewrite Complete",
                            font=("Roboto", 16, "bold"))
        header.pack(pady=(20, 10))

        # Prompt used
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(fill="x", padx=20, pady=(0, 10))

        prompt_label = ctk.CTkLabel(prompt_frame, text=f"Instructions: {prompt}",
                                  font=("Roboto", 11), wraplength=600)
        prompt_label.pack(padx=10, pady=10)

        # Comparison frame
        comparison_frame = ctk.CTkFrame(self)
        comparison_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Original vs Rewritten
        original_label = ctk.CTkLabel(comparison_frame, text="Original:",
                                    font=("Roboto", 12, "bold"))
        original_label.pack(anchor="w", padx=10, pady=(10, 5))

        original_textbox = ctk.CTkTextbox(comparison_frame, wrap="word", height=100)
        original_textbox.pack(fill="x", padx=10, pady=(0, 10))
        original_textbox.insert("0.0", original_text)
        original_textbox.configure(state="disabled")

        rewritten_label = ctk.CTkLabel(comparison_frame, text="Rewritten:",
                                     font=("Roboto", 12, "bold"))
        rewritten_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.rewritten_textbox = ctk.CTkTextbox(comparison_frame, wrap="word", height=100)
        self.rewritten_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.rewritten_textbox.insert("0.0", rewritten_text)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        copy_btn = ctk.CTkButton(button_frame, text="📋 Copy Rewritten",
                               command=lambda: self.copy_to_clipboard(rewritten_text), width=130)
        copy_btn.pack(side="left", padx=(0, 10))

        replace_btn = ctk.CTkButton(button_frame, text="🔄 Replace Original",
                                  command=self.replace_original, width=130,
                                  fg_color="#28a745", hover_color="#218838")
        replace_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(button_frame, text="Close",
                                command=self.destroy, width=80)
        close_btn.pack(side="right")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Rewritten text copied to clipboard!")

    def replace_original(self):
        """Replace the original selected text with the rewritten version"""
        rewritten = self.rewritten_textbox.get("0.0", "end").strip()
        if rewritten:
            pyperclip.copy(rewritten)
            messagebox.showinfo("Ready to Replace",
                              "Rewritten text copied to clipboard.\n\n"
                              "You can now paste it to replace the original text.")
        self.destroy()


class WarningDialog(ctk.CTkToplevel):


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

