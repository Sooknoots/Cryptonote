# Cryptonote - Complete Offline Setup Guide

## Overview
Cryptonote is designed to work completely offline once properly configured. This guide explains how to set up and use all features without internet connectivity.

## Prerequisites
- Windows 10/11
- Cryptonote executable
- Ollama (for local AI) - Download from https://ollama.ai/download

## Initial Setup (One-time)

### 1. Run Offline Setup
Execute `BuildReqs\scripts\setup_offline.bat` to:
- Generate SSL certificates for secure P2P communication
- Create default configuration files
- Initialize logging system

### 2. Install Ollama for Local AI
```bash
# Download and install Ollama from https://ollama.ai/download
# After installation, pull the default model:
ollama pull llama2
```

### 3. Start Ollama Service
```bash
ollama serve
```
Keep this running in the background for AI functionality.

## Offline Features Available

### ✅ Core Functionality (Always Works Offline)
- Create, edit, and delete encrypted notes
- File attachments and clipboard monitoring
- Local database storage with AES-256-GCM encryption
- Search and organize notes
- Export/import notes

### ✅ AI Features (With Ollama)
- Grammar and style corrections
- Content suggestions
- Note summarization
- Smart categorization
- TPS (Tokens Per Second) performance tracking

### ✅ P2P Features (Local Network Only)
- Share AI processing power with other Cryptonote users
- Secure peer-to-peer communication via HTTPS
- API key authentication
- Rate limiting and request logging

### ❌ Online-Only Features
- OpenAI API integration (requires internet)
- Google Drive backup/sync (requires internet)
- PayPal payments (requires internet)

## Directory Structure for Offline Distribution

```
Cryptonote_Offline/
├── Cryptonote.exe          # Main application
├── BuildReqs/             # Offline setup resources
│   ├── scripts/
│   │   ├── setup_offline.bat
│   │   └── generate_ssl_certs.bat
│   ├── configs/
│   │   └── default_config.json
│   └── docs/
│       └── offline_guide.md
├── certs/                 # SSL certificates (generated)
├── logs/                  # Application logs
├── user_config.json       # User configuration
└── README.md             # This file
```

## Configuration for Offline Use

The default configuration enables all offline features:

```json
{
  "ai_providers": {
    "ollama": {
      "enabled": true,
      "url": "http://localhost:11434"
    },
    "p2p": {
      "enabled": true,
      "port": 5000
    }
  },
  "p2p_server": {
    "enabled": true,
    "ssl_enabled": true
  }
}
```

## Running the Application

1. **Start Ollama** (if using AI features):
   ```bash
   ollama serve
   ```

2. **Run Cryptonote**:
   - Double-click `Cryptonote.exe`
   - Or run from command line: `Cryptonote.exe`

3. **Enable P2P Server** (optional):
   - In the application, go to Settings
   - Enable "P2P Server" to share AI processing power

## Troubleshooting Offline Issues

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if port 11434 is available
- Verify model is downloaded: `ollama list`

### P2P Server Issues
- Check if ports 5000 are available
- Verify SSL certificates exist in `certs/` folder
- Check logs in `logs/cryptonote.log`

### SSL Certificate Issues
- Run `BuildReqs\scripts\generate_ssl_certs.bat` to regenerate certificates
- Ensure OpenSSL is installed (usually comes with Git)

## Performance Optimization

### For Better AI Performance
- Use SSD storage for Ollama models
- Allocate more RAM to Ollama if possible
- Use smaller models for faster responses: `ollama pull llama2:7b`

### For Better P2P Performance
- Ensure stable local network connection
- Configure appropriate rate limits in settings
- Monitor logs for performance metrics

## Security Notes

- All data is encrypted locally using AES-256-GCM
- P2P communication uses SSL/TLS encryption
- API keys are required for P2P access
- No data is sent to external servers in offline mode

## Updating Offline Installation

To update to a new version:
1. Download new `Cryptonote.exe`
2. Replace the old executable
3. Run `BuildReqs\scripts\setup_offline.bat` if needed
4. Your encrypted notes and configuration will be preserved

## Support

For offline usage issues:
1. Check the logs in `logs/cryptonote.log`
2. Verify Ollama is running and accessible
3. Ensure all required files are present
4. Try regenerating SSL certificates

The application is designed to be fully functional offline once properly set up.