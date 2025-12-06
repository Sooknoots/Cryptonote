import customtkinter as ctk
import os
import sys
import threading
import pyperclip
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
    from googleapiclient.http import MediaFileUpload
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
                # Create new
                logging.info("Database file does not exist, prompting for creation")
                confirm = messagebox.askyesno("Create New Database", "File does not exist. Create new encrypted database?")
                if confirm:
                    # Ask for password hint
                    hint_dialog = ctk.CTkInputDialog(text="Enter a password hint (optional, will be shown when logging in):", title="Password Hint")
                    hint = hint_dialog.get_input() or ""
                    logging.info("Creating new encrypted database")
                    storage.create_new(password)
                    logging.info("New database created successfully")
                    self.on_login_success(storage, password, hint)
        except Exception as e:
            logging.error(f"Login failed: {e}", exc_info=True)
            self.status_label.configure(text=f"Error: {str(e)}")

class EditNotePopup(ctk.CTkToplevel):
    def __init__(self, master, note, on_save, on_delete):
        super().__init__(master)
        self.note = note
        self.on_save = on_save
        self.on_delete = on_delete
        self.attached_file = note.file_path if note else ""
        
        self.title("Edit Note")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Title
        self.title_label = ctk.CTkLabel(self, text="Title:")
        self.title_label.pack(pady=(20, 5))
        self.title_entry = ctk.CTkEntry(self, width=550)
        self.title_entry.pack()
        if note:
            self.title_entry.insert(0, note.title)
        
        # Content
        self.content_label = ctk.CTkLabel(self, text="Content:")
        self.content_label.pack(pady=(20, 5))
        self.content_text = ctk.CTkTextbox(self, width=550, height=200)
        self.content_text.pack()
        if note:
            self.content_text.insert("0.0", note.content)
        
        # Tags
        self.tags_label = ctk.CTkLabel(self, text="Tags (comma separated):")
        self.tags_label.pack(pady=(20, 5))
        self.tags_entry = ctk.CTkEntry(self, width=550)
        self.tags_entry.pack()
        if note:
            self.tags_entry.insert(0, ", ".join(note.tags))
        
        # Attached File
        self.file_frame = ctk.CTkFrame(self)
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
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
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
        
        # Deduct token
        self.master.token_balance -= 1
        self.after(0, lambda: self.master._update_token_label())
        self.master.save_config()
        
        # Use OpenAI
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
        
        # Add actual tokens used
        if hasattr(response, 'usage') and response.usage:
            tokens_used = response.usage.total_tokens
            self.master.total_tokens_used += tokens_used
            self.master.save_config()
        else:
            tokens_used = self.estimate_tokens(content + fixed_content)
            self.master.total_tokens_used += tokens_used
            self.master.save_config()
        
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
    
    def delete_note(self):
        confirm = messagebox.askyesno("Delete Note", "Are you sure you want to delete this note?")
        if confirm:
            self.on_delete(self.note)
            self.destroy()

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.geometry("400x300")
        self.resizable(False, False)
        
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
        
        # Peer Management
        self.peer_frame = ctk.CTkFrame(self)
        self.peer_frame.pack(pady=10, padx=20, fill="x")
        
        self.peer_label = ctk.CTkLabel(self.peer_frame, text="P2P Peers")
        self.peer_label.pack(pady=5)
        
        self.peer_entry = ctk.CTkEntry(self.peer_frame, placeholder_text="Peer IP:Port")
        self.peer_entry.pack(pady=5)
        
        self.add_peer_btn = ctk.CTkButton(self.peer_frame, text="Add Peer", command=self.add_peer)
        self.add_peer_btn.pack(pady=5)
        
        self.p2p_info_btn = ctk.CTkButton(self.peer_frame, text="P2P Setup Info", command=self.show_p2p_info)
        self.p2p_info_btn.pack(pady=5)
        
        # Save Button
        self.save_btn = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_btn.pack(pady=20)

    def toggle_clipboard(self):
        enabled = self.clipboard_checkbox.get()
        self.master.toggle_clipboard_enabled(enabled)
    
    def toggle_p2p(self):
        enabled = self.p2p_checkbox.get()
        self.master.toggle_p2p_enabled(enabled)
    
    def toggle_headless(self):
        enabled = self.headless_checkbox.get()
        self.master.headless_mode = enabled
        self.master.save_config()
    
    def toggle_timeout(self):
        enabled = self.timeout_checkbox.get()
        self.master.ollama_timeout_enabled = enabled
        self.master.save_config()
    
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
        self.geometry("400x300")
        self.resizable(False, False)
        
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
        
        self.storage = None
        self.password = None
        self.current_note = None
        self.token_balance = 0
        self.lifetime_license = False
        self.transaction_id = ""
        self.total_tokens_used = 0
        self.clipboard_history = []
        self.monitoring_clipboard = False
        self.clipboard_enabled = True
        self.p2p_enabled = False
        self.p2p_peers = []
        self.p2p_server = None
        self.earned_tokens = 0
        self.headless_mode = False  # Default to GUI mode
        
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
        
        # Ollama timeout setting
        self.ollama_timeout_enabled = False  # Default: no timeout
        self.ollama_timeout_seconds = 10
        
        # Add close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Login Screen
        self.login_frame = LoginFrame(self, self.on_login_success)

        # Main UI (Hidden initially)
        self.header = None
        self.board = None

    def on_closing(self):
        logging.info("Application closing initiated")
        if self.headless_mode:
            logging.info("Headless mode enabled, minimizing to tray")
            self.withdraw()
            return
        
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
                self.p2p_api_key = config.get("p2p_api_key")
                self.ollama_timeout_enabled = config.get("ollama_timeout_enabled", False)
                self.ollama_timeout_seconds = config.get("ollama_timeout_seconds", 10)
                self.tps_stats = config.get("tps_stats", {
                    'ollama': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'openai': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0},
                    'p2p': {'total_tokens': 0, 'total_time': 0.0, 'requests': 0, 'avg_tps': 0.0}
                })
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
            "tps_stats": self.tps_stats
        }
        with open("user_config.json", "w") as f:
            json.dump(user_config, f)

    def build_main_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(4, weight=1)
        
        self.app_logo = ctk.CTkLabel(self.header, text="Cryptonote", font=("Roboto", 20, "bold"))
        self.app_logo.grid(row=0, column=0, padx=20, pady=10)
        
        # Snip Button (centered)
        self.snip_btn = ctk.CTkButton(self.header, text="📷 Snip", command=self.start_snip, width=80)
        self.snip_btn.grid(row=0, column=1, padx=20, pady=10)
        
        self.new_note_btn = ctk.CTkButton(self.header, text="New Note", command=self.create_new_note, width=100)
        self.new_note_btn.grid(row=0, column=2, padx=20, pady=10)
        
        # Import/Export Buttons
        self.io_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.io_frame.grid(row=0, column=4, padx=20, pady=10)
        
        self.import_btn = ctk.CTkButton(self.io_frame, text="Import", width=80, command=self.import_library)
        self.import_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(self.io_frame, text="Export", width=80, command=self.export_library)
        self.export_btn.pack(side="right", padx=5)

        # Download Prompts Button
        self.download_btn = ctk.CTkButton(self.header, text="Download Prompts", command=self.download_prompts, width=120)
        self.download_btn.grid(row=0, column=5, padx=20, pady=10)

        # Upload to Google Drive Button
        self.upload_btn = ctk.CTkButton(self.header, text="Upload to Drive", command=self.upload_to_drive, width=120)
        self.upload_btn.grid(row=0, column=6, padx=20, pady=10)

        # Token Balance Label
        self.token_label = ctk.CTkLabel(self.header, text=f"Tokens: {self.token_balance}")
        self.token_label.grid(row=0, column=7, padx=20, pady=10)

        # Total Tokens Used Label
        self.total_tokens_label = ctk.CTkLabel(self.header, text=f"Total Used: {self.total_tokens_used}")
        self.total_tokens_label.grid(row=0, column=8, padx=20, pady=10)

        # TPS Stats Label
        self.tps_label = ctk.CTkLabel(self.header, text="Ollama: 0.0 TPS | OpenAI: 0.0 TPS | P2P: 0.0 TPS", font=("Roboto", 10))
        self.tps_label.grid(row=0, column=9, padx=20, pady=10)

        # Extras Button
        self.extras_btn = ctk.CTkButton(self.header, text="Extras", command=self.open_extras_shop, width=100)
        self.extras_btn.grid(row=0, column=9, padx=20, pady=10)

        # Clipboard Button
        self.clipboard_btn = ctk.CTkButton(self.header, text="📋 Clipboard", command=self.toggle_clipboard_panel, width=100)
        self.clipboard_btn.grid(row=0, column=10, padx=20, pady=10)

        # Settings Button
        self.settings_btn = ctk.CTkButton(self.header, text="⚙️ Settings", command=self.open_settings, width=100)
        self.settings_btn.grid(row=0, column=11, padx=20, pady=10)

        # Board
        self.board = ctk.CTkScrollableFrame(self, label_text="Your Notes")
        self.board.grid(row=1, column=0, sticky="nsew")
        
        self.refresh_board()

    def refresh_board(self):
        # Clear board
        for widget in self.board.winfo_children():
            widget.destroy()

        notes = self.storage.list_notes()
        # Sort by modified time desc
        notes.sort(key=lambda x: x.modified_at, reverse=True)

        # Grid layout: 4 columns
        cols = 4
        for i, note in enumerate(notes):
            row = i // cols
            col = i % cols
            
            # Note Card
            card = ctk.CTkFrame(self.board, width=250, height=150, corner_radius=10)
            card.grid(row=row, column=col, padx=10, pady=10)
            card.grid_propagate(False)
            
            # Title
            title_label = ctk.CTkLabel(card, text=note.title or "Untitled", font=("Roboto", 14, "bold"), wraplength=230)
            title_label.pack(pady=(10, 5), padx=10, anchor="w")
            
            # Content Preview
            content_preview = note.content[:100] + "..." if len(note.content) > 100 else note.content
            content_label = ctk.CTkLabel(card, text=content_preview, wraplength=230, justify="left", anchor="w")
            content_label.pack(pady=(0, 5), padx=10, anchor="w")
            
            # Tags
            if note.tags:
                tags_text = ", ".join(note.tags)
                tags_label = ctk.CTkLabel(card, text=f"Tags: {tags_text}", font=("Roboto", 10), text_color="gray")
                tags_label.pack(pady=(0, 5), padx=10, anchor="w")
            
            # Attachment Indicator
            if note.file_path:
                attach_label = ctk.CTkLabel(card, text="📎 Attached", font=("Roboto", 10), text_color="orange")
                attach_label.pack(pady=(0, 10), padx=10, anchor="w")
            
            # Click to edit
            card.bind("<Button-1>", lambda e, n=note: self.edit_note(n))

    def save_config(self):
        config = {
            "last_file": self.storage.filepath,
            "last_hash": self.compute_file_hash(self.storage.filepath),
            "hint": self.hint
        }
        try:
            with open("config.json", "w") as f:
                json.dump(config, f)
        except:
            pass  # Ignore save errors

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

    def _update_token_label(self):
        self.token_label.configure(text=f"Tokens: {self.token_balance}")
        self.total_tokens_label.configure(text=f"Total Used: {self.total_tokens_used}")
        self.update_tps_display()

    def open_extras_shop(self):
        ExtrasShop(self)

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
        self.clipboard_panel = ctk.CTkToplevel(self)
        self.clipboard_panel.title("Clipboard History")
        self.clipboard_panel.geometry("300x600+1200+100")  # Position on right
        self.clipboard_panel.resizable(False, False)
        self.clipboard_panel.attributes("-topmost", True)
        
        self.build_clipboard_panel_content()

    def build_clipboard_panel_content(self):
        title = ctk.CTkLabel(self.clipboard_panel, text="Clipboard History", font=("Roboto", 16, "bold"))
        title.pack(pady=10)
        
        scrollable = ctk.CTkScrollableFrame(self.clipboard_panel, width=280, height=500)
        scrollable.pack(pady=10, padx=10)
        
        for i, item in enumerate(self.clipboard_history[:20]):  # Show last 20
            frame = ctk.CTkFrame(scrollable)
            frame.pack(pady=5, fill="x")
            
            if item["type"] == "text":
                preview = item["content"][:50] + "..." if len(item["content"]) > 50 else item["content"]
                label = ctk.CTkLabel(frame, text=preview, wraplength=250)
                label.pack(pady=5)
            elif item["type"] == "image":
                # Show thumbnail
                try:
                    img = ctk.CTkImage(Image.open(item["content"]), size=(80, 80))
                    img_label = ctk.CTkLabel(frame, image=img, text="")
                    img_label.pack(pady=5)
                except:
                    label = ctk.CTkLabel(frame, text="[Image]")
                    label.pack(pady=5)
            
            btn = ctk.CTkButton(frame, text="Paste", command=lambda idx=i: self.paste_from_history(idx), width=50)
            btn.pack(pady=5)

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

    def open_settings(self):
        SettingsDialog(self)

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

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

