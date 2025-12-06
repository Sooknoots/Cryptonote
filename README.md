# 🔒 Cryptonote - Secure, Offline AI-Powered Note Taking

<div align="center">

![Cryptonote Logo](https://img.shields.io/badge/Cryptonote-v1.0.0-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDMTMuMSAyIDE0IDIuOSAxNCA0VjE2QzE0IDE3LjEgMTMuMSAxOCA5LjUgMTJDOS41IDExLjEgOS41IDEwLjEgOS41IDEwSDE0VjE0SDE2VjRIMTJDMTEuNCAyIDEwLjYgMiAxMCAySDRDMi40IDIgMiAzLjQgMiA2VjE4QzIgMTkuNiAzLjQgMjEgNiAyMkgxOFYyMEgxOFoiIGZpbGw9IiM2MzY2ZjEiLz4KPC9zdmc+)

**Military-Grade Security Meets AI Intelligence**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: AES-256-GCM](https://img.shields.io/badge/security-AES--256--GCM-red.svg)](https://en.wikipedia.org/wiki/Galois/Counter_Mode)
[![Offline First](https://img.shields.io/badge/offline-first-green.svg)](https://offlinefirst.org/)

*Take secure notes with AI assistance - completely offline, forever.*

[📥 Download Latest Release](#-download) • [📖 Documentation](#-documentation) • [🔐 Security](#-security) • [🤖 AI Features](#-ai-features)

</div>

---

## 🌟 What is Cryptonote?

**Cryptonote** is a revolutionary note-taking application that combines **military-grade encryption** with **artificial intelligence**, designed for professionals who demand both security and productivity. Unlike cloud-based alternatives, Cryptonote works completely offline - no internet connection required, no data leaks possible.

### 🎯 Perfect For:
- **🔒 Security Professionals** - Journalists, lawyers, researchers
- **💼 Business Users** - Secure client notes, sensitive documentation
- **🎓 Students & Academics** - Private research notes with AI assistance
- **🛡️ Privacy Advocates** - Zero-trust, offline-first approach
- **💻 Developers** - Code snippets, documentation, secure knowledge base

---

## ✨ Key Features

### 🔐 Uncompromising Security
- **AES-256-GCM Encryption** - Military-grade authenticated encryption
- **Argon2id Key Derivation** - Industry-standard password hashing
- **Zero-Knowledge Architecture** - Encryption keys never leave your device
- **Single Encrypted Database** - All data in one secure `notes.enc` file

### 🤖 AI-Powered Intelligence
- **Local AI Processing** - Ollama integration for offline AI assistance
- **Cloud AI Support** - OpenAI API integration when needed
- **Smart Writing Assistance** - Grammar, style, and content suggestions
- **Context-Aware Prompts** - AI understands your notes and writing style

### 💻 User Experience
### 💻 Modern Interface Redesign
- **3-Panel Layout**: Navigation sidebar, main content, and quick actions panel
- **Smart Search**: Real-time search with advanced filtering
- **Multiple View Modes**: Card view, List view, and Compact view for different use cases
- **Theme System**: Light/Dark themes with premium auto-switching
- **Responsive Design**: Adapts to different screen sizes and resolutions
- **Intuitive Navigation**: Sidebar with quick filters and organization tools
- **Status Bar**: System status, AI leaderboard ticker, and license information
- **Welcome Guide**: Built-in onboarding for new users

### 🏆 AI Competition Features
- **P2P Leaderboard** - Compete with peers on AI inference speed
- **Opt-in Sharing** - Privacy-first metric sharing with user consent
- **Live Rankings** - Animated ticker showing top 10 performers
- **Performance Tracking** - TPS statistics for all AI providers

### 🌐 Offline-First Design
- **Zero Internet Dependency** - Works anywhere, anytime
- **No Auto-Updates** - You control when and what gets updated
- **Portable Application** - Single executable file
- **Cross-Platform Ready** - Windows, macOS, Linux support

### ☁️ Automatic Backup Management
- **Google Drive Integration** - Secure cloud backup with OAuth2 authentication
- **Automatic Sync** - Checks for newer backups on startup and downloads automatically
- **Version Control** - Keeps last 5 backup versions in temporary storage
- **Conflict Resolution** - Always uses the most recent version across devices
- **Offline Fallback** - Works without internet, syncs when connection available

### 💳 Premium Features & Licensing
- **PayPal Integration** - Secure payment processing for AI tokens and licenses
- **Manual License Keys** - Direct license key entry for development and testing
- **Token Management** - Purchase and track AI usage tokens
- **Lifetime Licenses** - One-time payments for permanent access
- **Advanced Clipboard Manager** - Premium clipboard history with Copilot integration
- **Copilot Note Editing** - Use Windows Copilot to modify and improve notes
- **Smart Text Suggestions** - AI-powered writing assistance and improvements
- **Windows Copilot Integration** - Voice-activated AI assistance (premium)

---

## 🚀 Quick Start

### Option 1: Download & Run (Recommended)

1. **Download** the latest release from [GitHub Releases](https://github.com/Sooknoots/Cryptonote/releases)
2. **Extract** the ZIP file to your preferred location
3. **Run** `Cryptonote.exe` (Windows) or the appropriate executable for your platform
4. **Create** your master password and start taking secure notes!

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/Sooknoots/Cryptonote.git
cd Cryptonote

# Install dependencies
pip install -r requirements.txt

# Run the application
python Gui.py
```

---

## 🔑 Security Deep Dive

### Encryption Specifications

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **Cipher** | AES-256-GCM | Authenticated encryption with integrity |
| **Key Derivation** | Argon2id | Memory-hard password hashing |
| **Memory Cost** | 64 MB | Protection against brute force |
| **Time Cost** | 2 iterations | Computational difficulty |
| **Parallelism** | 2 threads | Multi-threading support |
| **Salt Length** | 16 bytes | Random salt per file |
| **Nonce Length** | 12 bytes | Unique per encryption |

### Zero-Trust Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Argon2id KDF   │───▶│   AES-256-GCM   │
│ (Master Password)│    │  (Key Derivation) │    │   Encryption    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐             │
│   Encrypted     │◀───│   notes.enc     │◀────────────┘
│   Plaintext     │    │   Database      │
│   (Your Notes)  │    └─────────────────┘
└─────────────────┘
```

**Your data is encrypted before it even touches the disk.**

---

## 🤖 AI Features & Capabilities

### Local AI Processing (Ollama)
- **Lifetime License**: One-time purchase for unlimited local AI
- **Privacy First**: All processing happens on your device
- **No Data Leakage**: Conversations never leave your computer
- **Model Flexibility**: Choose from various open-source models

### Cloud AI Support (OpenAI)
- **Token-Based**: Pay only for what you use
- **Premium Models**: Access to GPT-4 and other advanced models
- **Secure Integration**: API keys stored locally and encrypted
- **Fallback Support**: Works when local AI isn't available

### AI Writing Assistance
- **Grammar & Style**: Professional writing enhancement
- **Content Suggestions**: Smart recommendations based on context
- **Code Assistance**: Programming help and code review
- **Research Support**: Summarization and analysis tools

### Token Verification System
- **Fair Usage**: Tokens only deducted after successful AI inference
- **Error Protection**: No charges for failed API calls or empty responses
- **Transparent Tracking**: Real-time token balance and usage statistics
- **Multi-Provider Support**: Consistent verification across Ollama and OpenAI

### P2P AI Leaderboard
- **Performance Competition**: Compete with other users on AI inference speed
- **Opt-in Privacy**: Share metrics only with explicit permission
- **Real-time Rankings**: Live updates of top 10 fastest users
- **Network Discovery**: Automatic peer discovery on local networks
- **Background Service**: Runs silently when enabled, no impact on performance

---

## 🎨 Interface Guide

### Layout Overview
```
┌─────────────────────────────────────────────────┐
│ [📝 Cryptonote] [✨ New Note] [📸 Capture] ...    │ ← Top Toolbar
├─────────────┬───────────────────────────────────┬─────────────┐
│             │                                   │             │
│  📂 Nav     │        📄 Notes Display           │  ⚡ Actions  │
│  🔍 Filters │        🔍 Search Bar              │  🤖 AI       │
│             │        [Card/List/Compact View]   │             │
│             │                                   │             │
├─────────────┴───────────────────────────────────┴─────────────┤
│ 🔗 Connected 💾 Backed up [🏆 Leaderboard] ⭐ Free │ ← Status Bar
└─────────────────────────────────────────────────┘
```

### Navigation Sidebar
- **📄 All Notes**: View complete note collection
- **🕒 Recent**: Notes modified in the last 7 days
- **⭐ Favorites**: Important starred notes
- **🔍 Smart Search**: Real-time content filtering
- **🏷️ Tag Filter**: Filter by specific tags
- **📊 Sort Options**: Newest/Oldest, Alphabetical
- **👁️ View Modes**: Card, List, or Compact display

### Search & Discovery
- **Instant Results**: Search updates as you type
- **Multi-Field Search**: Title, content, and tags
- **Tag-Based Filtering**: Sidebar tag filter
- **Advanced Queries**: Complex search patterns supported

### View Modes
- **Card View**: Visual grid with previews and metadata
- **List View**: Compact list with inline previews
- **Compact View**: Minimal space usage for large collections

### Quick Actions Panel
- **💾 Backup**: Google Drive synchronization
- **📋 Clipboard**: Content capture and history
- **🔧 Services**: System status monitoring
- **🤖 AI Actions**: Premium AI-powered features
- **📝 Prompts**: AI prompt library access

---

## 📊 Technical Specifications

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 | Windows 10/11 |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 200 MB | 500 MB |
| **Python** | 3.10+ | 3.11+ |
| **Display** | 1366x768 | 1920x1080 |

### Dependencies

```txt
customtkinter>=5.2.0      # Modern UI framework
cryptography>=41.0.0      # Encryption library
argon2-cffi>=23.1.0       # Password hashing
pyperclip>=1.8.0          # Clipboard management
pillow>=10.0.0           # Image processing
requests>=2.31.0         # HTTP client
pywin32>=306             # Windows integration
```

### File Structure

```
Cryptonote/
├── Cryptonote.exe          # Main executable
├── notes.enc              # Encrypted database
├── user_config.json       # User preferences
├── logs/                  # Application logs
├── certs/                 # SSL certificates (offline P2P)
└── docs/                  # Documentation
```

---

## 💰 Licensing & Monetization

### Software License
**Cryptonote Core**: Free and open-source (MIT License)
- Full source code available on GitHub
- Community-driven development
- No restrictions on personal use

### AI Features
- **Local AI (Ollama)**: Lifetime license - $25 one-time
- **Cloud AI Tokens**: $0.10 per 1K tokens (OpenAI pricing)
- **Premium Prompts**: Curated prompt libraries - $10/year

### Business Model
- **Transparent Pricing**: Pay only for AI features you use
- **No Subscriptions**: Lifetime licenses, no recurring fees
- **Token System**: Fair usage-based pricing
- **Open Source Core**: Build trust through transparency

---

## 🔧 Advanced Configuration

### AI Setup

#### Local AI (Ollama)
```bash
# Install Ollama
# Visit: https://ollama.ai/download

# Pull a model
ollama pull llama2

# Activate in Cryptonote
# Settings → AI → Enable Local AI → Select Model
```

#### Cloud AI (OpenAI)
```bash
# Get API key from https://platform.openai.com/api-keys

# Configure in Cryptonote
# Settings → AI → OpenAI API Key → Enter Key
# Purchase tokens via integrated PayPal
```

### Backup Setup

#### Google Drive Integration
```bash
# 1. Create Google Cloud Project
# Visit: https://console.cloud.google.com/
# Create new project → APIs & Services → Credentials

# 2. Enable Google Drive API
# APIs & Services → Library → Search "Google Drive API" → Enable

# 3. Create OAuth2 Credentials
# Credentials → Create Credentials → OAuth 2.0 Client IDs
# Application type: Desktop application
# Download JSON file as 'client_secret.json'

# 4. Configure in Cryptonote
# Place 'client_secret.json' in application directory
# Settings → Backup → Upload to Drive (first time will prompt OAuth)

# 5. Automatic Features
# - Checks for newer backups on startup
# - Downloads latest version automatically
# - Keeps last 5 backup versions locally
# - Syncs across multiple devices
```

#### Audio Controls Setup
```bash
# Volume Control (Free)
# Always available - system volume slider and buttons in the sliding tray

# Media Remote Controls (Premium)
# Spotify/YouTube remote controls require a lifetime license
# Access via the sliding tray at the bottom-right of the main window
# Switch between Spotify and YouTube modes with the ◀ button
# Features:
# - Previous/Play-Pause/Next track buttons
# - Automatic media window detection and control
# - Visual feedback for current status

# Windows Copilot Integration
# Big blue "🤖 Copilot" button in the header activates Windows 11 Copilot
# Functions like "Hey Copilot" voice activation
# Requires Windows 11 with Copilot enabled
```

#### Licensing & Payments
```bash
# PayPal Integration (Production)
# Set environment variables:
# PAYPAL_CLIENT_ID=your_production_client_id
# PAYPAL_CLIENT_SECRET=your_production_client_secret
# PAYPAL_ENVIRONMENT=production

# For Development/Testing:
# PAYPAL_ENVIRONMENT=sandbox
# Use PayPal sandbox credentials

# Manual License Keys:
# Enter license keys directly in Settings → Licensing
# Supports both lifetime licenses and token purchases
```

### Security Settings

```json
{
  "encryption": {
    "cipher": "AES-256-GCM",
    "kdf": "Argon2id",
    "memory_cost": 65536,
    "time_cost": 2,
    "parallelism": 2
  },
  "ai": {
    "local_enabled": true,
    "cloud_enabled": false,
    "ollama_model": "llama2"
  },
  "ui": {
    "theme": "dark",
    "clipboard_history": true,
    "auto_save": true
  }
}
```

---

## 🛠️ Development

### Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests: `python run_tests.py`
4. Submit a pull request

### Building from Source

```bash
# Install build dependencies
pip install pyinstaller

# Run security validation
python security_validator.py

# Build executable
python BuildReqs/scripts/build_offline_complete.bat
```

### Testing

```bash
# Run all tests
python run_tests.py

# Run specific test category
python -m pytest tests/test_crypto.py -v
```

---

## 📚 Documentation

- **[User Guide](docs/User_Guide.md)** - Complete usage instructions
- **[Security Overview](docs/Security_Overview.md)** - Technical security details
- **[API Reference](docs/API_Reference.md)** - Developer documentation
- **[Build Guide](docs/Build_Guide.md)** - Compilation instructions

---

## 🤝 Community & Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/Sooknoots/Cryptonote/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sooknoots/Cryptonote/discussions)
- **Security**: For security concerns, email: security@cryptonote.app

### Roadmap
- [ ] Mobile applications (iOS/Android)
- [ ] Web-based interface
- [ ] Plugin ecosystem
- [ ] Advanced collaboration features
- [ ] Multi-language support

---

## ⚖️ Legal & Compliance

### Data Protection
- **GDPR Compliant**: Your data never leaves your device
- **Zero Data Collection**: No telemetry or analytics
- **Open Source Transparency**: Audit our code for security

### Warrant Canary
*As of December 6, 2025, Cryptonote has not received any national security letters, gag orders, or requests for user data from any government agency.*

### Responsible Disclosure
We take security seriously. If you discover a vulnerability, please email security@cryptonote.app with full details.

---

## 🙏 Acknowledgments

- **Ollama** - For making local AI accessible
- **OpenAI** - For powerful AI capabilities
- **Python Cryptography** - For robust encryption libraries
- **CustomTkinter** - For beautiful UI components

---

<div align="center">

**Made with ❤️ for privacy and productivity**

*Download today and take control of your digital notes!*

[📥 Download Now](https://github.com/Sooknoots/Cryptonote/releases/latest) • [🌟 Star on GitHub](https://github.com/Sooknoots/Cryptonote) • [📖 Read the Docs](docs/)

---

*Cryptonote v1.0.0 - Secure your thoughts, amplify your productivity.*

</div>
