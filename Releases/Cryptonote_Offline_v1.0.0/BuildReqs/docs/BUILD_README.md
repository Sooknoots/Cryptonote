# Cryptonote - Secure Distributed Note Taking

A military-grade encrypted note-taking application with AI assistance and distributed P2P computing capabilities.

## 🚀 Quick Start

### For Users
1. Download `Cryptonote.exe` from the releases
2. Run the executable (no installation required)
3. Create your first encrypted database

### For Developers
```bash
# Clone the repository
git clone https://github.com/yourusername/cryptonote.git
cd cryptonote

# Install dependencies
pip install -r requirements.txt

# Run the application
python Gui.py
```

## 🔒 Security Features

- **AES-256-GCM Encryption**: Military-grade encryption for all data
- **Argon2id Key Derivation**: Secure password hashing
- **P2P HTTPS**: Encrypted peer-to-peer AI computing
- **API Key Authentication**: Secure P2P access control
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive request validation

## 🏗️ Building Executables

### Standard Build (Recommended)
```bash
# Run the standard build script
build_exe.bat
```
Creates `dist/Cryptonote.exe` - source code is embedded but not easily extractable.

### Obfuscated Build (Maximum Security)
```bash
# Run the obfuscated build script (requires PyArmor)
build_obfuscated.bat
```
Creates `dist/Cryptonote_Pro.exe` with:
- Source code obfuscated with PyArmor
- Function names encrypted
- Control flow obfuscated
- String literals encrypted
- Extremely difficult to reverse engineer

### Manual Build
```bash
# Using PyInstaller spec file
pyinstaller cryptonote.spec
```

## 📋 Build Requirements

- Python 3.8+
- PyInstaller
- PyArmor (for obfuscated builds)
- All dependencies from `requirements.txt`

## 🔐 Distribution Security

### GitHub Releases Checklist
- [x] Test executable on clean Windows system
- [x] Verify no sensitive data in executable
- [x] Check file size is reasonable (78MB)
- [x] Test all features work
- [x] Verify encryption/decryption works
- [x] Test P2P features (if applicable)
- [x] Check logs don't contain sensitive information

### Security Notes
- **Source Code Protection**: Executables created with PyInstaller embed Python bytecode, but source code is not directly extractable
- **Obfuscation**: For maximum protection, use the obfuscated build with PyArmor
- **Dependencies**: All required libraries are bundled in the executable
- **No External Dependencies**: Executable runs standalone on Windows

## 🛠️ Development

### Project Structure
```
cryptonote/
├── Gui.py                 # Main application
├── src/
│   ├── crypto.py         # Encryption utilities
│   ├── storage.py        # Data persistence
│   └── models.py         # Data models
├── tests/                # Unit tests
├── logs/                 # Application logs
├── certs/                # SSL certificates (generated)
├── build_exe.bat         # Standard build script
├── build_obfuscated.bat  # Obfuscated build script
├── cryptonote.spec       # PyInstaller spec file
└── requirements.txt      # Python dependencies
```

### Key Technologies
- **GUI**: CustomTkinter (modern dark theme)
- **Encryption**: Cryptography library (AES-256-GCM + Argon2id)
- **P2P**: Flask with SSL/TLS
- **AI**: Ollama (local) + OpenAI (API)
- **Build**: PyInstaller + PyArmor

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines]

## 📞 Support

[Add support information]