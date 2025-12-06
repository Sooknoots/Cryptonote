# Cryptonote Releases

This folder contains all commercial distribution releases of Cryptonote.

## Release Structure

Each release follows this naming convention:
`Cryptonote_[Type]_v[Version]_[Date]`

### Release Types
- `Offline` - Complete offline package with all dependencies
- `Standard` - Basic executable only
- `Pro` - Obfuscated version with maximum security

## Current Release: Cryptonote_Offline_v1.0.0

### What's Included
- `Cryptonote.exe` - Main application executable
- `BuildReqs/` - Complete build and setup resources
- `certs/` - SSL certificates for secure P2P
- `logs/` - Application logs directory
- `user_config.json` - Default configuration
- `README.md` - Offline usage guide
- `Run_Offline.bat` - Simple launcher script

### Offline Capabilities
✅ All features work without internet:
- Encrypted note storage
- Local AI via Ollama
- P2P server for distributed computing
- SSL-secured peer communication
- Complete offline setup scripts

### System Requirements
- Windows 10/11
- 4GB RAM minimum (8GB recommended for AI)
- 2GB free disk space
- Ollama (for AI features) - https://ollama.ai/download

## Distribution Checklist

### Pre-Release
- [x] Executable builds successfully
- [x] All dependencies bundled
- [x] SSL certificates generated
- [x] Offline setup scripts tested
- [x] Documentation complete
- [x] File size optimized (< 100MB)

### Testing
- [x] Basic functionality works
- [x] Encryption/decryption tested
- [x] AI features work with Ollama
- [x] P2P server starts correctly
- [x] No sensitive data in executable

### Security
- [x] Source code protected (PyInstaller bundling)
- [x] SSL certificates for secure communication
- [x] API key authentication for P2P
- [x] Rate limiting implemented
- [x] Input validation active

## Release Process

1. **Update Version**: Modify version numbers in relevant files
2. **Run Build**: Execute `build_master.bat` and select option 1
3. **Test Package**: Extract and test the offline package
4. **Create Archive**: Zip the release folder
5. **Upload**: Add to GitHub releases with changelog
6. **Update Docs**: Update this README with new version info

## Future Releases

### Planned Improvements
- Automatic Ollama installation bundling
- Multiple AI model options
- Enhanced P2P discovery
- Mobile app companion
- Cloud sync options (optional)

### Version History
- **v1.0.0** - Initial offline release
  - Complete offline functionality
  - Local AI integration
  - Secure P2P networking
  - Military-grade encryption