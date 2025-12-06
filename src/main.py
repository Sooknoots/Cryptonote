import os
import sys
import time
import getpass
import pyperclip
from colorama import init, Fore, Style
from .models import Note
from .storage import StorageManager

# Initialize colorama
init()

class App:
    def __init__(self):
        self.storage = None
        self.filepath = "notes.enc" # Default file
        self.password = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        self.clear_screen()
        print(f"{Fore.CYAN}╔════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║           SECURE CRYPTONOTE            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"{Fore.BLACK}{Style.BRIGHT}Secure Offline Note Taking App{Style.RESET_ALL}\n")

    def main_menu(self):
        while True:
            self.print_header()
            if not self.storage or not self.storage.is_open:
                print(f"{Fore.YELLOW}1. Create New Database{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}2. Open Database{Style.RESET_ALL}")
                print(f"{Fore.RED}3. Exit{Style.RESET_ALL}")
                
                choice = input(f"\n{Fore.GREEN}Select option: {Style.RESET_ALL}")
                
                if choice == '1':
                    self.create_db()
                elif choice == '2':
                    self.open_db()
                elif choice == '3':
                    sys.exit()
            else:
                print(f"{Fore.BLUE}Database Open: {self.filepath}{Style.RESET_ALL}\n")
                print(f"{Fore.WHITE}1. List Notes{Style.RESET_ALL}")
                print(f"{Fore.WHITE}2. Add Note{Style.RESET_ALL}")
                print(f"{Fore.WHITE}3. Copy Note Content (No Title){Style.RESET_ALL}")
                print(f"{Fore.WHITE}4. Import Library{Style.RESET_ALL}")
                print(f"{Fore.WHITE}5. Export Library{Style.RESET_ALL}")
                print(f"{Fore.WHITE}6. Close Database{Style.RESET_ALL}")
                print(f"{Fore.RED}7. Exit{Style.RESET_ALL}")

                choice = input(f"\n{Fore.GREEN}Select option: {Style.RESET_ALL}")

                if choice == '1':
                    self.list_notes()
                elif choice == '2':
                    self.add_note()
                elif choice == '3':
                    self.copy_note_content()
                elif choice == '4':
                    self.import_lib()
                elif choice == '5':
                    self.export_lib()
                elif choice == '6':
                    self.storage = None
                    self.password = None
                elif choice == '7':
                    sys.exit()

    def create_db(self):
        path = input("Enter filename for new database (default: notes.enc): ") or "notes.enc"
        password = getpass.getpass("Set Master Password: ")
        confirm = getpass.getpass("Confirm Password: ")
        
        if password != confirm:
            print(f"{Fore.RED}Passwords do not match!{Style.RESET_ALL}")
            time.sleep(2)
            return

        self.filepath = path
        self.storage = StorageManager(path)
        try:
            self.storage.create_new(password)
            self.password = password
            print(f"{Fore.GREEN}Database created successfully!{Style.RESET_ALL}")
            time.sleep(1)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            time.sleep(2)

    def open_db(self):
        path = input("Enter database filename (default: notes.enc): ") or "notes.enc"
        if not os.path.exists(path):
            print(f"{Fore.RED}File not found!{Style.RESET_ALL}")
            time.sleep(2)
            return

        password = getpass.getpass("Enter Master Password: ")
        self.filepath = path
        self.storage = StorageManager(path)
        try:
            self.storage.load(password)
            self.password = password
            print(f"{Fore.GREEN}Database opened successfully!{Style.RESET_ALL}")
            time.sleep(1)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            time.sleep(2)

    def list_notes(self):
        self.print_header()
        notes = self.storage.list_notes()
        if not notes:
            print("No notes found.")
        else:
            print(f"{Fore.YELLOW}{'ID':<4} | {'Title':<30} | {'Tags'}{Style.RESET_ALL}")
            print("-" * 60)
            for i, note in enumerate(notes):
                tags = ", ".join(note.tags)
                print(f"{i+1:<4} | {note.title:<30} | {tags}")
        
        input(f"\n{Fore.GREEN}Press Enter to return...{Style.RESET_ALL}")

    def add_note(self):
        self.print_header()
        print("New Note")
        title = input("Title: ")
        print("Content (type END on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        content = "\n".join(lines)
        tags_input = input("Tags (comma separated): ")
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        note = Note(title=title, content=content, tags=tags)
        self.storage.add_note(note)
        self.storage.save(self.password)
        print(f"{Fore.GREEN}Note saved!{Style.RESET_ALL}")
        time.sleep(1)

    def copy_note_content(self):
        self.print_header()
        notes = self.storage.list_notes()
        if not notes:
            print("No notes to copy.")
            time.sleep(2)
            return

        for i, note in enumerate(notes):
            print(f"{i+1}. {note.title}")

        try:
            idx = int(input("\nSelect note number to copy content: ")) - 1
            if 0 <= idx < len(notes):
                note = notes[idx]
                pyperclip.copy(note.content)
                print(f"{Fore.GREEN}Content of '{note.title}' copied to clipboard!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
        
        time.sleep(2)

    def import_lib(self):
        path = input("Enter path to encrypted file to import: ")
        if not os.path.exists(path):
            print(f"{Fore.RED}File not found.{Style.RESET_ALL}")
            time.sleep(2)
            return
        
        password = getpass.getpass("Enter password for import file: ")
        try:
            self.storage.import_library(path, password)
            self.storage.save(self.password)
            print(f"{Fore.GREEN}Import successful!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Import failed: {e}{Style.RESET_ALL}")
        time.sleep(2)

    def export_lib(self):
        path = input("Enter filename for export: ")
        password = getpass.getpass("Set password for export file: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print(f"{Fore.RED}Passwords do not match.{Style.RESET_ALL}")
            time.sleep(2)
            return

        try:
            self.storage.export_library(path, password)
            print(f"{Fore.GREEN}Export successful!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Export failed: {e}{Style.RESET_ALL}")
        time.sleep(2)

if __name__ == "__main__":
    app = App()
    app.main_menu()
