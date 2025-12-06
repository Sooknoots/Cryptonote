# Cryptonote Security Framework
# PERMANENT RULE: Never push unsafe files to public repositories
# This file contains the security validation system

import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Set
import re

class SecurityValidator:
    """
    Comprehensive security validation system for Cryptonote.
    Ensures no sensitive files are ever exposed in public releases.
    """

    # CRITICAL: Files that MUST NEVER be committed or released
    FORBIDDEN_FILES = {
        # Private keys and certificates
        '*.pem', '*.key', '*.crt', '*.p12', '*.pfx',
        'server.key', 'server.crt', 'ca.crt', 'private.key',

        # API keys and secrets
        '*_secret*', '*_key*', '*.env', 'secrets.json',
        'config/secrets/', 'secrets/',

        # Encrypted data
        '*.enc', 'notes.enc', 'encrypted_data/',

        # User-specific configurations
        'user_config.json', 'local_config.json',

        # Database files
        '*.db', '*.sqlite', '*.sqlite3',

        # Compiled binaries (except in releases)
        '*.exe', '*.dll', '*.so', '*.dylib',

        # IDE and OS files
        '.vscode/', '.idea/', '*.swp', '*.swo', 'Thumbs.db',
        '.DS_Store', '._*', 'ehthumbs.db',

        # Logs and temporary files
        '*.log', 'logs/', 'temp/', 'tmp/', '*.tmp',
    }

    # SENSITIVE PATTERNS: Content that should never be in committed files
    SENSITIVE_PATTERNS = [
        r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
        r'-----BEGIN\s+ENCRYPTED\s+PRIVATE\s+KEY-----',
        r'-----BEGIN\s+CERTIFICATE-----',
        r'AIza[0-9A-Za-z-_]{35}',  # Google API keys
        r'sk-[a-zA-Z0-9]{48}',     # OpenAI API keys
        r'xoxb-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}',  # Slack tokens
        r'ghp_[a-zA-Z0-9]{36}',    # GitHub tokens
        r'[a-zA-Z0-9]{32}',        # Generic 32-char keys (potential secrets)
    ]

    # ALLOWED RELEASE FILES: Only these can be in public releases
    ALLOWED_RELEASE_FILES = {
        'README.md', 'LICENSE', 'CHANGELOG.md',
        'requirements.txt', 'setup.py', 'pyproject.toml',
        'MANIFEST.in', '.gitignore',
    }

    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or os.getcwd())
        self.security_log = []
        self.scan_results = {}

    def scan_for_forbidden_files(self, path: Path = None) -> Dict[str, List[str]]:
        """Scan for forbidden files that should never be committed."""
        if path is None:
            path = self.root_path

        forbidden_found = {
            'critical': [],    # Must never exist
            'warning': [],     # Should be reviewed
            'info': []         # Not recommended
        }

        for root, dirs, files in os.walk(path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_path = Path(root) / file

                # Check against forbidden patterns
                for pattern in self.FORBIDDEN_FILES:
                    if pattern.startswith('*') and pattern.endswith('*'):
                        if pattern[1:-1] in str(file_path):
                            forbidden_found['critical'].append(str(file_path))
                    elif pattern.startswith('*.'):
                        if file_path.suffix == pattern[1:]:
                            forbidden_found['critical'].append(str(file_path))
                    elif pattern.endswith('/'):
                        if pattern[:-1] in str(file_path):
                            forbidden_found['critical'].append(str(file_path))
                    elif file == pattern:
                        forbidden_found['critical'].append(str(file_path))

        return forbidden_found

    def scan_file_content_for_secrets(self, file_path: Path) -> List[str]:
        """Scan file content for potential secrets and sensitive patterns."""
        sensitive_findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                for pattern in self.SENSITIVE_PATTERNS:
                    matches = re.findall(pattern, content)
                    if matches:
                        sensitive_findings.extend(matches[:3])  # Limit to first 3 matches

        except (UnicodeDecodeError, PermissionError):
            # Binary files or permission issues - skip content scan
            pass

        return sensitive_findings

    def validate_build_safety(self) -> bool:
        """Validate that it's safe to proceed with build/release."""
        print("🔒 SECURITY VALIDATION: Checking build safety...")

        # Check git status to see what would be committed
        import subprocess
        try:
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True, cwd=self.root_path)
            if result.returncode == 0:
                staged_files = []
                unstaged_files = []

                for line in result.stdout.split('\n'):
                    if line.strip():
                        status = line[:2]
                        filename = line[3:]
                        if status[0] in ['A', 'M', 'R']:  # Added, Modified, Renamed
                            staged_files.append(filename)
                        elif status[1] != ' ':  # Unstaged changes
                            unstaged_files.append(filename)

                # Check staged files for forbidden content
                for file in staged_files:
                    file_path = self.root_path / file
                    if file_path.exists():
                        # Check if it's a forbidden file type
                        for pattern in self.FORBIDDEN_FILES:
                            if self._matches_forbidden_pattern(file, pattern):
                                print(f"❌ CRITICAL: Staged file '{file}' matches forbidden pattern '{pattern}'")
                                return False

                        # Check file content for secrets
                        secrets = self.scan_file_content_for_secrets(file_path)
                        if secrets:
                            print(f"❌ CRITICAL: Staged file '{file}' contains potential secrets")
                            return False

                print("✅ Staged files passed security validation")
            else:
                print("⚠️  Could not check git status - proceeding with file system scan")

        except Exception as e:
            print(f"⚠️  Git status check failed: {e} - proceeding with file system scan")

        # Fallback: Scan for forbidden files in the working directory
        # But exclude files that are properly gitignored
        forbidden = self.scan_for_forbidden_files()
        critical_issues = []

        for file in forbidden['critical']:
            file_path = Path(file)
            # Check if this file would be ignored by git
            try:
                result = subprocess.run(['git', 'check-ignore', str(file_path)],
                                      capture_output=True, cwd=self.root_path)
                if result.returncode != 0:  # File is not ignored
                    critical_issues.append(file)
            except:
                # If git check fails, assume file is problematic
                critical_issues.append(file)

        if critical_issues:
            print("❌ CRITICAL SECURITY VIOLATION!")
            print("Files that must never be released (not properly gitignored):")
            for file in critical_issues:
                print(f"  🚫 {file}")
            return False

        print("✅ SECURITY CHECK PASSED: Safe to proceed with build")
        return True

    def _matches_forbidden_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a forbidden pattern."""
        if pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in filename
        elif pattern.startswith('*.'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('/'):
            return pattern[:-1] in filename
        else:
            return filename == pattern

    def generate_security_report(self) -> str:
        """Generate a comprehensive security report."""
        report = []
        report.append("# [LOCK] Cryptonote Security Report")
        report.append(f"Generated: {os.environ.get('USER', 'Unknown')} @ {Path.cwd()}")
        report.append("")

        # Scan results
        forbidden = self.scan_for_forbidden_files()

        report.append("## [FORBIDDEN] Forbidden Files Check")
        if forbidden['critical']:
            report.append("### CRITICAL VIOLATIONS (Must Fix)")
            for file in forbidden['critical']:
                report.append(f"- [X] {file}")
        else:
            report.append("[OK] No critical violations found")

        if forbidden['warning']:
            report.append("### Warnings (Review Recommended)")
            for file in forbidden['warning']:
                report.append(f"- ⚠️ {file}")

        report.append("")
        report.append("## [SEARCH] Content Security Scan")
        report.append("Scanning for embedded secrets and sensitive patterns...")

        sensitive_count = 0
        for root, dirs, files in os.walk(self.root_path):
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_path = Path(root) / file
                secrets = self.scan_file_content_for_secrets(file_path)
                if secrets:
                    report.append(f"### {file_path}")
                    for secret in secrets[:5]:  # Show first 5
                        report.append(f"- [KEY] `{secret[:20]}...`")
                    sensitive_count += 1

        if sensitive_count == 0:
            report.append("[OK] No sensitive content detected")

        report.append("")
        report.append("## [INFO] Security Recommendations")
        report.append("1. Never commit private keys, certificates, or API secrets")
        report.append("2. Use environment variables for sensitive configuration")
        report.append("3. Regularly audit committed files for accidental exposure")
        report.append("4. Use .gitignore to prevent sensitive files from being tracked")

        return "\n".join(report)

    def create_security_marker(self, file_path: str) -> None:
        """Add security validation marker to a file."""
        marker = f"""
# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: {os.environ.get('USER', 'Unknown')} @ {Path.cwd()}
# SHA256: {hashlib.sha256(open(file_path, 'rb').read()).hexdigest()[:16]}
# NEVER REMOVE THIS MARKER - Indicates file passed security validation
"""

        with open(file_path, 'r+') as f:
            content = f.read()
            if "# SECURITY MARKER:" not in content:
                f.seek(0)
                f.write(marker + "\n" + content)

def main():
    """Main security validation function."""
    validator = SecurityValidator()

    print("🔒 Cryptonote Security Validation System")
    print("=" * 50)

    # Run comprehensive security check
    if validator.validate_build_safety():
        print("\n✅ ALL SECURITY CHECKS PASSED")
        print("Safe to proceed with build/release")

        # Generate security report
        report = validator.generate_security_report()
        with open("SECURITY_REPORT.md", "w") as f:
            f.write(report)
        print("📄 Security report saved to SECURITY_REPORT.md")

        return True
    else:
        print("\n❌ SECURITY VIOLATIONS DETECTED")
        print("Build/release ABORTED for security reasons")
        print("Fix violations before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)