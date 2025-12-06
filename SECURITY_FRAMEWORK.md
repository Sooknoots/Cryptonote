# 🔒 Cryptonote Security Framework - PERMANENT RULES

## 🚨 CRITICAL SECURITY DIRECTIVE

**PERMANENT RULE**: I will NEVER push files marked as unsafe for users to see, including:
- Source code containing private keys, secrets, or sensitive APIs
- Application binaries with embedded credentials
- Configuration files with API keys or personal data
- Any encrypted data or certificates

**ALL PUBLIC RELEASES MUST BE CHECKED** before building and pushing. Every single time.

## 🛡️ Security System Components

### 1. Pre-Build Security Validation (`prebuild_security_check.bat`)
- **Runs automatically** before any build process
- **Blocks builds** if security violations detected
- **Scans for** forbidden file patterns and embedded secrets
- **Checks git status** to ensure only safe files are staged

### 2. Comprehensive Security Validator (`security_validator.py`)
- **Forbidden Files Detection**: Identifies private keys, certificates, API secrets
- **Content Analysis**: Scans for embedded secrets and sensitive patterns
- **Git Integration**: Only flags files that would actually be committed
- **Security Reports**: Generates detailed audit reports

### 3. Post-Commit GitHub Scanner (`github_security_scanner.py`)
- **Automatic Monitoring**: Runs after every commit via git hooks
- **GitHub API Integration**: Scans repository for accidentally uploaded files
- **Emergency Removal**: Provides step-by-step instructions for data cleanup
- **Continuous Vigilance**: Monitors all future commits

### 4. Security Markers System (`add_security_markers.py`)
- **File Validation**: Adds security markers to all Python files
- **SHA256 Hashing**: Tracks file integrity
- **Audit Trail**: Proves files passed security validation
- **Automated Process**: Can be run before any release

### 5. Enhanced .gitignore
- **Comprehensive Coverage**: Blocks all sensitive file types
- **Pattern Matching**: Prevents accidental inclusion of secrets
- **Build Artifacts**: Excludes compiled binaries and temporary files
- **IDE Files**: Removes development-specific files

## 🔐 Security Validation Process

### Before Any Build/Release:
1. **Run Security Validator**: `python security_validator.py`
2. **Add Security Markers**: `python add_security_markers.py`
3. **Verify Git Status**: Ensure no sensitive files are staged
4. **Build Only If Passed**: All checks must pass before proceeding

### After Every Commit:
1. **GitHub Scan**: Automatically checks repository for violations
2. **Alert on Detection**: Immediate notification of security issues
3. **Emergency Cleanup**: Step-by-step removal instructions provided

### File Security Markers:
```
# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ /path/to/project
# SHA256: [hash]
# NEVER REMOVE THIS MARKER - Indicates file passed security validation
```

## 🚫 Forbidden File Categories

### NEVER Commit These:
- **Private Keys**: `*.pem`, `*.key`, `*.p12`, `*.pfx`
- **Certificates**: `*.crt`, `server.crt`, `ca.crt`
- **API Secrets**: `secrets.json`, `*_secret*`, `*_key*`
- **Encrypted Data**: `*.enc`, `notes.enc`
- **User Configs**: `user_config.json`, `local_config.json`
- **Databases**: `*.db`, `*.sqlite`, `*.sqlite3`
- **Logs**: `*.log`, `logs/`
- **Executables**: `*.exe`, `*.dll` (except in controlled releases)

### Pattern-Based Detection:
- Google API Keys: `AIza[0-9A-Za-z-_]{35}`
- OpenAI Keys: `sk-[a-zA-Z0-9]{48}`
- Slack Tokens: `xoxb-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}`
- GitHub Tokens: `ghp_[a-zA-Z0-9]{36}`

## 🚨 Emergency Response Protocol

### If Sensitive Files Are Detected:

1. **IMMEDIATE ACTION**: Stop all development
2. **Revoke Credentials**: Change all passwords and API keys
3. **Remove from Git History**:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch SENSITIVE_FILE' --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
4. **Clean Repository**:
   ```bash
   git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
   git reflog expire --expire=now --all
   git gc --prune=now
   ```
5. **Notify Team**: Inform all contributors to re-clone

## 📊 Security Audit Trail

- **Pre-build validation** logs all security checks
- **Security markers** prove file validation
- **GitHub scanning** monitors post-commit status
- **Security reports** document all findings

## 🔄 Continuous Security Process

1. **Daily Validation**: Run security checks before any work
2. **Pre-commit Checks**: Validate before committing changes
3. **Post-commit Monitoring**: GitHub scanner runs automatically
4. **Release Validation**: Full security audit before releases
5. **Regular Audits**: Periodic comprehensive security reviews

## ⚡ Quick Security Commands

```bash
# Validate security before build
python security_validator.py

# Add security markers to all files
python add_security_markers.py

# Check GitHub for violations
python github_security_scanner.py

# Run pre-build security check
prebuild_security_check.bat
```

## 🎯 Security Success Metrics

- ✅ **Zero Sensitive Files** in public repositories
- ✅ **100% Pre-build Validation** pass rate
- ✅ **Automatic Detection** of security violations
- ✅ **Immediate Response** to detected issues
- ✅ **Comprehensive Audit Trail** for all security actions

---

**PERMANENT RULE**: Security validation is mandatory for all builds and releases. This system ensures Cryptonote maintains the highest security standards and never exposes sensitive information to the public.

**Last Updated**: December 6, 2025
**Security Framework Version**: 1.0