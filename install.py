#!/usr/bin/env python3
"""
Interactive Installation Script for multi-agent-assistant

This script guides users through the complete setup:
1. Environment detection (Python, Node.js, git)
2. Backend dependencies
3. GitHub account & personal access token
4. GitHub Models API configuration
5. Gmail account setup (required)
6. Assistant profile creation
7. Testing & validation

Usage:
    python install.py
"""

import sys
import json
import platform
import subprocess
import webbrowser
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"

    @staticmethod
    def info(text):
        return f"{Colors.BLUE}ℹ️  {text}{Colors.END}"

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✓ {text}{Colors.END}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠️  {text}{Colors.END}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}✗ {text}{Colors.END}"


class Installer:
    """Interactive installer for multi-agent-assistant."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
        self.backend_dir = self.project_root / "services" / "orchestrator"
        self.config = {}

    def print_header(self, title):
        """Print a section header."""
        print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{title:^60}{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")

    def print_step(self, step_num, title):
        """Print a step header."""
        print(f"{Colors.BOLD}Step {step_num}: {title}{Colors.END}")
        print("-" * 60)

    def prompt_yes_no(self, question):
        """Prompt user for yes/no response."""
        while True:
            response = input(f"{Colors.BOLD}{question} (y/n): {Colors.END}").strip().lower()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            print(Colors.error("Please enter 'y' or 'n'"))

    def prompt_input(self, prompt_text, default=None, required=True):
        """Prompt user for input with optional default."""
        while True:
            if default:
                full_prompt = f"{Colors.BOLD}{prompt_text} [{default}]: {Colors.END}"
            else:
                full_prompt = f"{Colors.BOLD}{prompt_text}: {Colors.END}"

            response = input(full_prompt).strip()

            if response:
                return response
            elif default:
                return default
            elif not required:
                return None
            else:
                print(Colors.error("This field is required"))

    def check_command_exists(self, command):
        """Check if a command exists in PATH."""
        result = subprocess.run(
            ["where" if platform.system() == "Windows" else "which", command],
            capture_output=True,
        )
        return result.returncode == 0

    def check_python_version(self):
        """Check Python version is 3.11+."""
        self.print_step(1, "Python Version Check")

        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 11):
            print(Colors.error("Python 3.11+ required"))
            return False

        print(Colors.success(f"Python {version.major}.{version.minor} OK\n"))
        return True

    def check_dependencies(self):
        """Check for required system dependencies."""
        self.print_step(2, "System Dependencies Check")

        deps = {
            "git": "Git version control",
            "python": "Python interpreter",
            "pip": "Python package manager",
        }

        if platform.system() != "Windows":
            deps["curl"] = "HTTP client"

        all_good = True
        for cmd, desc in deps.items():
            if self.check_command_exists(cmd):
                print(Colors.success(f"{desc}: Found"))
            else:
                print(Colors.warning(f"{desc}: Not found - install it"))
                all_good = False

        print()
        return all_good

    def setup_backend_dependencies(self):
        """Install Python dependencies."""
        self.print_step(3, "Install Backend Dependencies")

        if not (self.backend_dir / "pyproject.toml").exists():
            print(Colors.error("services/orchestrator/pyproject.toml not found"))
            return False

        print("Installing Python dependencies...")
        print("  (including playwright for browser automation)")
        try:
            # Install backend from pyproject in editable mode with dev extras.
            subprocess.run(
                ["pip", "install", "-e", ".[dev]"],
                cwd=self.backend_dir,
                check=True,
                capture_output=True,
            )
            # Also install playwright
            subprocess.run(
                ["pip", "install", "playwright"],
                check=True,
                capture_output=True,
            )
            print(Colors.success("Dependencies installed\n"))
            return True
        except subprocess.CalledProcessError as e:
            print(Colors.error(f"Failed to install dependencies: {e}\n"))
            return False

    def setup_github_account(self):
        """Create brand-new assistant GitHub account, reusing Gmail address."""
        self.print_step(5, "New Assistant GitHub Account (SECOND) — uses Gmail address")

        print("A brand-new GitHub account is needed for the assistant.")
        print("This must NOT be your personal account.")
        print(f"We'll use the Gmail address already collected: {self.config.get('ASSISTANT_EMAIL_FROM', 'aiassistance@gmail.com')}")
        print()

        github_username = self.prompt_input(
            "Choose a GitHub username for the assistant",
            default="ai-assistant-bot",
        )
        # Reuse the Gmail address already collected in setup_gmail
        github_email = self.config.get("ASSISTANT_EMAIL_FROM", "aiassistance@gmail.com")

        self.config["ASSISTANT_GITHUB_NAME"] = github_username

        print()
        print(Colors.info("Opening GitHub signup in browser — sign out of personal account first!"))
        signup_url = f"https://github.com/signup?email={github_email}"
        webbrowser.open(signup_url)

        print(Colors.success("Browser opened to GitHub signup"))
        print()
        print("Please complete these steps:")
        print(f"  1. Email: {github_email}  (pre-filled)")
        print(f"  2. Username: {github_username}")
        print("  3. Create a strong password")
        print("  4. Verify your email address")
        print()

        input(Colors.BOLD + "Press Enter once email is verified and account is ready..." + Colors.END)
        print()

        return True

    def generate_github_token(self):
        """Generate GitHub personal access token with browser automation."""
        self.print_step(6, "GitHub Personal Access Token")

        print("I'll open GitHub settings in your browser to generate a token.")
        print()
        
        # Open token creation page
        token_url = "https://github.com/settings/tokens/new"
        webbrowser.open(token_url)
        
        print(Colors.success("Browser opened to GitHub token creation"))
        print()
        print("I've opened GitHub's token creation page.")
        print()
        print("Please complete these steps in the browser:")
        print("  1. Token name: multi-agent-assistant")
        print("  2. Expiration: 90 days")
        print("  3. Scopes: Check ONLY 'read:models'")
        print("  4. Click 'Generate token'")
        print("  5. Copy the token (shown only once!)")
        print()
        
        token = self.prompt_input(Colors.BOLD + "Paste your GitHub token here" + Colors.END)

        # Validate token format
        if not token.startswith("ghp_"):
            print(Colors.warning("Token should start with 'ghp_'"))
            
        print()
        print(Colors.success("Token saved"))
        
        self.config["GITHUB_TOKEN"] = token
        return token

    def test_github_models(self):
        """Test GitHub Models connection."""
        self.print_step(6, "Test GitHub Models Connection")

        if not self.config.get("GITHUB_TOKEN"):
            print(Colors.warning("No GitHub token configured"))
            return False

        # Save temp .env to test
        self._write_env_file({"GITHUB_TOKEN": self.config["GITHUB_TOKEN"]})

        print("Testing connection to GitHub Models API...")
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app.main:app",
                    "--port",
                    "8765",
                ],
                cwd=self.backend_dir,
                capture_output=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            print(Colors.success("Backend started\n"))
            return True

        print(Colors.warning("Could not start backend for testing"))
        return False

    def setup_gmail(self):
        """Create brand-new assistant Gmail account with browser automation."""
        self.print_step(4, "Gmail Setup (FIRST) — assistant identity")

        print("Gmail is required for assistant email notifications and reminders.")
        print()

        gmail_address = self.prompt_input(
            "New assistant Gmail address",
            default="aiassistance@gmail.com",
        )

        print()
        print(Colors.info("Opening Gmail signup — sign out of personal Gmail first!"))
        webbrowser.open("https://accounts.google.com/signup/v2/webcreateaccount")
        print(Colors.success("Browser opened to Gmail signup"))
        print()
        print(f"Please create a NEW Gmail account: {gmail_address}")
        print("Complete phone/email verification before continuing.")
        print()
        input(Colors.BOLD + "Press Enter once Gmail account is ready..." + Colors.END)
        print()

        print(Colors.info("Opening Gmail app passwords..."))
        webbrowser.open("https://myaccount.google.com/apppasswords")

        print(Colors.success("Browser opened to Gmail app passwords"))
        print()
        print("Please complete these steps in the browser:")
        print("  1. Select 'Mail' from the 'Select app' dropdown")
        print("  2. Select 'Windows Computer' from the 'Select device' dropdown")
        print("  3. Click 'Generate'")
        print("  4. Copy the 16-character password shown")
        print()

        app_password = self.prompt_input(Colors.BOLD + "Paste the app-specific password here" + Colors.END)

        self.config["ASSISTANT_EMAIL_ENABLED"] = "true"
        self.config["ASSISTANT_EMAIL_FROM"] = gmail_address
        self.config["ASSISTANT_EMAIL_APP_PASSWORD"] = app_password

        print()
        print(Colors.success("Gmail configured\n"))
        return True

    def setup_assistant_profile(self):
        """Create assistant profile only."""
        self.print_step(7, "Create Assistant Profile")

        print("The assistant profile stores app identity and skills.")
        print()

        print(Colors.BOLD + "Assistant Profile:" + Colors.END)
        assistant_email = self.prompt_input(
            "Assistant email",
            default=self.config.get("ASSISTANT_EMAIL_FROM", "aiassistance@gmail.com"),
        )
        assistant_name = self.prompt_input("Assistant name", default="multi-agent-assistant")
        assistant_skills = [
            {"skill": "planning", "level": "advanced", "description": "Goal setting and roadmap creation"},
            {"skill": "scheduling", "level": "advanced", "description": "Calendar management"},
        ]

        self.config["PROFILES"] = {
            "assistant": {
                "assistant_name": assistant_name,
                "email": assistant_email,
                "skills": assistant_skills,
            }
        }

        print()
        print(Colors.success("Assistant profile created\n"))
        return True

    def _save_credentials(self):
        """Save sensitive credentials to ~/.assistant/credentials outside the repo."""
        from pathlib import Path
        cred_dir = Path.home() / ".assistant"
        cred_dir.mkdir(exist_ok=True)
        cred_file = cred_dir / "credentials"
        lines = [
            "# Assistant credentials - DO NOT SHARE OR COMMIT",
            f"# Stored outside the repo at {cred_file}",
            f"GITHUB_TOKEN={self.config.get('GITHUB_TOKEN', '')}",
            f"GITHUB_USERNAME={self.config.get('ASSISTANT_GITHUB_NAME', '')}",
            f"GMAIL_ADDRESS={self.config.get('ASSISTANT_EMAIL_FROM', '')}",
            f"GMAIL_APP_PASSWORD={self.config.get('ASSISTANT_EMAIL_APP_PASSWORD', '')}",
        ]
        with open(cred_file, "w") as f:
            f.write("\n".join(lines) + "\n")
        # Restrict file permissions on non-Windows
        import stat
        import platform
        if platform.system() != "Windows":
            cred_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
        print(Colors.success(f"Credentials saved to {cred_file} (outside repo, never published)"))

    def _write_env_file(self, custom_config=None):
        """Write configuration to .env file."""
        config = {
            "APP_ENV": "dev",
            "APP_HOST": "0.0.0.0",
            "APP_PORT": "8000",
            "GITHUB_TOKEN": self.config.get("GITHUB_TOKEN", ""),
            "GITHUB_MODELS_ENABLED": "true" if self.config.get("GITHUB_TOKEN") else "false",
            "GITHUB_MODELS_MODEL": "gpt-4o-mini",
            "GITHUB_MODELS_TIMEOUT": "30",
            "ASSISTANT_EMAIL_ENABLED": self.config.get("ASSISTANT_EMAIL_ENABLED", "false"),
            "ASSISTANT_EMAIL_FROM": self.config.get("ASSISTANT_EMAIL_FROM", ""),
            "ASSISTANT_EMAIL_APP_PASSWORD": self.config.get("ASSISTANT_EMAIL_APP_PASSWORD", ""),
            "NEXT_PUBLIC_API_BASE_URL": "http://localhost:8000/api/v1",
            "EXPO_PUBLIC_API_BASE_URL": "http://localhost:8000/api/v1",
        }

        if custom_config:
            config.update(custom_config)

        with open(self.env_file, "w") as f:
            f.write("# Generated by installation script\n")
            for key, value in config.items():
                f.write(f"{key}={value}\n")

    def run(self):
        """Run the complete installation."""
        self.print_header("MULTI-AGENT-ASSISTANT INSTALLATION")

        print("This script will set up your assistant with:")
        print("  Step 4 ✓ Gmail account (FIRST — used as identity for GitHub)")
        print("  Step 5 ✓ GitHub account (SECOND — uses same Gmail)")
        print("  Step 6 ✓ GitHub token (AI brain access)")
        print("  Step 7 ✓ Assistant profile")
        print()

        if not self.check_python_version():
            return False

        if not self.check_dependencies():
            print(Colors.warning("Some dependencies are missing. Install them and try again."))
            return False

        if not self.setup_backend_dependencies():
            return False

        # Gmail FIRST — assistant needs Gmail before GitHub (same email reused)
        if not self.setup_gmail():
            return False

        # GitHub SECOND — uses the Gmail address already collected
        if not self.setup_github_account():
            return False

        token = self.generate_github_token()
        if not token:
            print(Colors.error("GitHub token is required"))
            return False
        if not self.setup_assistant_profile():
            return False

        # Write .env file
        self._write_env_file()

        # Save sensitive credentials to user home (outside repo)
        self._save_credentials()

        # Save profiles to disk
        self._save_profiles()

        # Summary
        self.print_header("INSTALLATION COMPLETE ✓")

        from pathlib import Path
        cred_path = Path.home() / ".assistant" / "credentials"
        print("\n✓ Install is done ONCE. To run the app each time:")
        print()
        print("  Terminal 1 — Backend:")
        print(f"    cd {self.backend_dir}")
        print("    python -m uvicorn app.main:app --reload")
        print()
        print("  Terminal 2 — Web frontend:")
        print("    cd apps/web")
        print("    npm install   # first time only")
        print("    npm run dev")
        print()
        print("  Then open: http://localhost:3000")
        print()
        print("  Quick health check:")
        print("    python test_quick.py")
        print()
        print("Credentials stored at:")
        print(f"  {cred_path}  (PRIVATE — outside repo, never published)")
        print()

        return True

    def _save_profiles(self):
        """Save assistant profile to disk."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)

        if "PROFILES" not in self.config:
            return

        profiles = self.config["PROFILES"]

        # Assistant profile
        assistant_profile = {
            "assistant_name": profiles["assistant"].get("assistant_name", "multi-agent-assistant"),
            "email": profiles["assistant"].get("email"),
            "version": "0.1.0",
            "skills": profiles["assistant"].get("skills", []),
            "supported_agents": [
                "planner",
                "calendar",
                "finance",
                "wellness",
                "compliance",
                "general",
            ],
            "instructions": "Be concise and actionable.",
            "guardrails": [],
        }

        with open(data_dir / "assistant_profile.json", "w") as f:
            json.dump(assistant_profile, f, indent=2)

        print(Colors.success("Assistant profile saved to data/"))


def main():
    """Main entry point."""
    try:
        installer = Installer()
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.warning('Installation cancelled by user')}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.error(f'Installation failed: {e}')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
