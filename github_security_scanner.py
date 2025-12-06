# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: cef7389f6b74088e
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

# Cryptonote GitHub Security Scanner
# Scans GitHub repository after commits to detect accidentally uploaded sensitive files
# Automatically alerts and provides removal instructions

import os
import requests
import json
import re
from pathlib import Path
from typing import List, Dict, Set
import time

class GitHubSecurityScanner:
    """
    Post-commit GitHub security scanner.
    Monitors repository for accidentally committed sensitive files.
    """

    # Files that should NEVER be on GitHub
    CRITICAL_FORBIDDEN = {
        'private keys': ['*.pem', '*.key', '*.p12', '*.pfx'],
        'certificates': ['*.crt', 'server.crt', 'ca.crt'],
        'api secrets': ['secrets.json', '*_secret*', '*_key*'],
        'encrypted data': ['*.enc', 'notes.enc'],
        'user configs': ['user_config.json', 'local_config.json'],
        'databases': ['*.db', '*.sqlite', '*.sqlite3'],
        'logs': ['*.log', 'logs/'],
        'temp files': ['*.tmp', 'temp/', 'tmp/'],
    }

    def __init__(self, repo_owner: str = None, repo_name: str = None, token: str = None):
        self.repo_owner = repo_owner or os.environ.get('GITHUB_REPOSITORY_OWNER', 'Sooknoots')
        self.repo_name = repo_name or os.environ.get('GITHUB_REPOSITORY', 'Cryptonote').split('/')[-1]
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.api_base = "https://api.github.com"

        if not all([self.repo_owner, self.repo_name]):
            print("❌ GitHub repository information not available")
            print("Set GITHUB_REPOSITORY_OWNER and GITHUB_REPOSITORY environment variables")
            return

    def get_recent_commits(self, limit: int = 5) -> List[Dict]:
        """Get recent commits from the repository."""
        if not self.token:
            print("⚠️  No GitHub token available - limited API access")
            return []

        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/commits?per_page={limit}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Failed to fetch commits: {e}")
            return []

    def get_commit_files(self, commit_sha: str) -> List[Dict]:
        """Get files changed in a specific commit."""
        if not self.token:
            return []

        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/commits/{commit_sha}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commit_data = response.json()
            return commit_data.get('files', [])
        except requests.RequestException as e:
            print(f"❌ Failed to fetch commit files: {e}")
            return []

    def scan_commit_for_violations(self, commit_sha: str) -> Dict[str, List[str]]:
        """Scan a commit for security violations."""
        violations = {
            'critical': [],  # Must be removed immediately
            'warning': [],   # Should be reviewed
            'suspicious': [] # May be false positives
        }

        files = self.get_commit_files(commit_sha)

        for file_info in files:
            filename = file_info['filename']

            # Check against critical forbidden patterns
            for category, patterns in self.CRITICAL_FORBIDDEN.items():
                for pattern in patterns:
                    if self._matches_pattern(filename, pattern):
                        violations['critical'].append(f"{filename} ({category})")
                        break

            # Check for suspicious file extensions
            suspicious_ext = ['.key', '.pem', '.crt', '.p12', '.pfx', '.enc']
            if any(filename.endswith(ext) for ext in suspicious_ext):
                if filename not in violations['critical']:
                    violations['warning'].append(f"{filename} (suspicious extension)")

            # Check for sensitive filenames
            sensitive_names = ['secret', 'key', 'private', 'config', 'auth']
            if any(name in filename.lower() for name in sensitive_names):
                if filename not in violations['critical'] and filename not in violations['warning']:
                    violations['suspicious'].append(f"{filename} (sensitive name)")

        return violations

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern."""
        if pattern.startswith('*.'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        elif '*' in pattern:
            # Handle patterns like '*_secret*'
            pattern = pattern.replace('*', '.*')
            return bool(re.match(pattern, filename, re.IGNORECASE))
        else:
            return filename == pattern

    def scan_recent_commits(self) -> bool:
        """Scan recent commits for security violations."""
        print("🔍 Scanning recent GitHub commits for security violations...")
        print("=" * 60)

        commits = self.get_recent_commits()

        if not commits:
            print("❌ Could not retrieve commit information")
            return False

        all_violations = {
            'critical': set(),
            'warning': set(),
            'suspicious': set()
        }

        for commit in commits[:3]:  # Check last 3 commits
            sha = commit['sha'][:8]
            message = commit['commit']['message'][:50]

            print(f"📋 Checking commit {sha}: {message}...")

            violations = self.scan_commit_for_violations(commit['sha'])

            for level, files in violations.items():
                all_violations[level].update(files)

        # Report findings
        has_violations = False

        if all_violations['critical']:
            has_violations = True
            print("\n🚨 CRITICAL SECURITY VIOLATIONS DETECTED!")
            print("These files MUST be removed from GitHub immediately:")
            for violation in sorted(all_violations['critical']):
                print(f"  ❌ {violation}")

        if all_violations['warning']:
            print("\n⚠️  WARNING: Potentially sensitive files detected:")
            for violation in sorted(all_violations['warning']):
                print(f"  ⚠️  {violation}")

        if all_violations['suspicious']:
            print("\n🤔 SUSPICIOUS: Files that should be reviewed:")
            for violation in sorted(all_violations['suspicious']):
                print(f"  🤔 {violation}")

        if not has_violations:
            print("\n✅ No security violations detected in recent commits")
            return True

        # Provide removal instructions
        self._print_removal_instructions(list(all_violations['critical']))
        return False

    def _print_removal_instructions(self, critical_files: List[str]):
        """Print instructions for removing critical files."""
        if not critical_files:
            return

        print("\n🛠️  EMERGENCY REMOVAL INSTRUCTIONS:")
        print("=" * 50)
        print("1. IMMEDIATELY revoke any exposed credentials/API keys")
        print("2. Run these commands to remove files from Git history:")
        print()
        print("   # Remove files from git history (rewrites history)")
        for file in critical_files:
            print(f"   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch {file}' --prune-empty --tag-name-filter cat -- --all")
        print()
        print("   # Force push the cleaned history")
        print("   git push origin --force --all")
        print()
        print("   # Clear git cache and force garbage collection")
        print("   git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin")
        print("   git reflog expire --expire=now --all")
        print("   git gc --prune=now")
        print()
        print("3. Change all passwords and API keys that may have been exposed")
        print("4. Notify team members to re-clone the repository")
        print("5. Consider enabling branch protection rules")

    def generate_security_audit_report(self) -> str:
        """Generate a comprehensive security audit report."""
        report = []
        report.append("# 🔒 Cryptonote GitHub Security Audit Report")
        report.append(f"Repository: {self.repo_owner}/{self.repo_name}")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Scan results
        success = self.scan_recent_commits()

        report.append("## 📊 Scan Results")
        if success:
            report.append("✅ No security violations detected")
        else:
            report.append("❌ Security violations found - see above for details")

        report.append("")
        report.append("## 🔍 Security Policies")
        report.append("- Private keys, certificates, and API secrets are NEVER committed")
        report.append("- All commits are scanned for sensitive file patterns")
        report.append("- Pre-build security validation prevents unsafe releases")
        report.append("- Regular security audits ensure ongoing compliance")

        return "\n".join(report)

def main():
    """Main GitHub security scanning function."""
    scanner = GitHubSecurityScanner()

    print("🔒 Cryptonote GitHub Security Scanner")
    print("Checking repository for accidentally committed sensitive files...")
    print()

    success = scanner.scan_recent_commits()

    if not success:
        print("\n❌ SECURITY ISSUES DETECTED!")
        print("Review and fix violations before proceeding")
        return False

    print("\n✅ GitHub security scan completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)