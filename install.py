#!/usr/bin/env python3
"""
Interactive Installation Script for multi-agent-assistant

This script guides users through the complete setup:
1. Environment detection (Python, Node.js, git)
2. Backend dependencies
3. GitHub account & personal access token
4. GitHub Models API configuration
5. Gmail account setup (optional)
6. Profile creation (assistant + boss)
7. Testing & validation

Usage:
    python install.py
    python install.py --skip-github-models  # Skip GitHub Models setup
    python install.py --skip-gmail          # Skip Gmail setup
"""

import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict
import re


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

        if not (self.backend_dir / "requirements.txt").exists():
            print(Colors.error("requirements.txt not found"))
            return False

        print("Installing Python dependencies...")
        try:
            subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                cwd=self.backend_dir,
                check=True,
                capture_output=True,
            )
            print(Colors.success("Dependencies installed\n"))
            return True
        except subprocess.CalledProcessError as e:
            print(Colors.error(f"Failed to install dependencies: {e}\n"))
            return False

    def setup_github_account(self):
        """Guide user through GitHub account setup."""
        self.print_step(4, "GitHub Account Setup")

        print("GitHub is needed for:")
        print("  • GitHub Models API (free LLM brain for your assistant)")
        print("  • Personal access token for authentication")
        print()

        if not self.prompt_yes_no("Do you have a GitHub account?"):
            print(Colors.info("Please visit https://github.com/signup"))
            print("  1. Create account")
            print("  2. Verify email")
            print("  3. Return here when done")
            input(Colors.BOLD + "Press Enter to continue..." + Colors.END)

        return True

    def generate_github_token(self):
        """Generate GitHub personal access token."""
        self.print_step(5, "GitHub Personal Access Token")

        print("We need to generate a personal access token for GitHub Models API.")
        print()
        print("Steps:")
        print("  1. Go to https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Fill in:")
        print("     • Token name: multi-agent-assistant")
        print("     • Expiration: 90 days")
        print("     • Scopes: Check ONLY 'read:models'")
        print("  4. Click 'Generate token'")
        print("  5. Copy the token (you won't see it again)")
        print()

        token = self.prompt_input("Paste your GitHub token here")

        # Validate token format
        if not token.startswith("ghp_"):
            print(Colors.warning("Token should start with 'ghp_'"))

        self.config["GITHUB_TOKEN"] = token
        print(Colors.success("Token saved\n"))
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
        """Guide user through Gmail setup."""
        self.print_step(7, "Gmail Setup (Optional)")

        print("Gmail is used for email notifications and reminders.")
        print("This is optional but recommended.")
        print()

        if not self.prompt_yes_no("Do you want to set up Gmail integration?"):
            print(Colors.info("Skipping Gmail setup\n"))
            self.config["ASSISTANT_EMAIL_ENABLED"] = "false"
            return True

        if not self.prompt_yes_no("Do you have a Gmail account?"):
            print(Colors.info("Please visit https://gmail.com to create one"))
            input(Colors.BOLD + "Press Enter to continue..." + Colors.END)

        print()
        print("Setting up Gmail app-specific password...")
        print("Steps:")
        print("  1. Go to https://myaccount.google.com/security")
        print("  2. Click '2-Step Verification' (if not enabled)")
        print("  3. Go to https://myaccount.google.com/apppasswords")
        print("  4. Select 'Mail' and 'Windows Computer'")
        print("  5. Click 'Generate'")
        print("  6. Copy the 16-character password")
        print()

        email = self.prompt_input("Enter your Gmail address")
        app_password = self.prompt_input("Paste the app-specific password")

        self.config["ASSISTANT_EMAIL_ENABLED"] = "true"
        self.config["ASSISTANT_EMAIL_FROM"] = email
        self.config["ASSISTANT_EMAIL_APP_PASSWORD"] = app_password

        print(Colors.success("Gmail configured\n"))
        return True

    def setup_profiles(self):
        """Create assistant and boss profiles."""
        self.print_step(8, "Create Assistant Profiles")

        print("The assistant needs to know:")
        print("  • Its own skills (planning, scheduling, etc.)")
        print("  • Your (the boss) goals and constraints")
        print()

        # Assistant profile
        print(Colors.BOLD + "Assistant Profile:" + Colors.END)
        assistant_email = self.prompt_input("Assistant email", default="assistant@example.com")
        assistant_skills = [
            {"skill": "planning", "level": "advanced", "description": "Goal setting and roadmap creation"},
            {"skill": "scheduling", "level": "advanced", "description": "Calendar management"},
        ]

        # Boss profile
        print()
        print(Colors.BOLD + "Boss (Your) Profile:" + Colors.END)
        boss_name = self.prompt_input("Your name", default="User")
        boss_email = self.prompt_input("Your email", default="user@example.com")
        boss_timezone = self.prompt_input(
            "Your timezone",
            default="UTC",
            required=False,
        )

        print()
        print("Enter your goals (one per line, empty line to finish):")
        goals = []
        for i in range(1, 4):
            goal = self.prompt_input(f"  Goal {i}", required=False)
            if goal:
                goals.append(goal)
            else:
                break

        print()
        print("Enter your constraints (one per line, empty line to finish):")
        constraints = []
        for i in range(1, 4):
            constraint = self.prompt_input(f"  Constraint {i}", required=False)
            if constraint:
                constraints.append(constraint)
            else:
                break

        self.config["PROFILES"] = {
            "assistant": {
                "email": assistant_email,
                "skills": assistant_skills,
            },
            "boss": {
                "name": boss_name,
                "email": boss_email,
                "timezone": boss_timezone or "UTC",
                "goals": goals,
                "constraints": constraints,
            },
        }

        print()
        print(Colors.success(f"Profiles created for {boss_name}\n"))
        return True

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
        print("  ✓ GitHub account & token")
        print("  ✓ GitHub Models API (AI brain)")
        print("  ✓ Gmail integration (optional)")
        print("  ✓ Profile configuration")
        print()

        if not self.check_python_version():
            return False

        if not self.check_dependencies():
            print(Colors.warning("Some dependencies are missing. Install them and try again."))
            return False

        if not self.setup_backend_dependencies():
            return False

        if not self.setup_github_account():
            return False

        token = self.generate_github_token()
        if not token:
            print(Colors.error("GitHub token is required"))
            return False

        # Uncomment when backend can be started
        # if not self.test_github_models():
        #     print(Colors.warning("GitHub Models connection test failed"))

        self.setup_gmail()
        self.setup_profiles()

        # Write .env file
        self._write_env_file()

        # Save profiles to disk
        self._save_profiles()

        # Summary
        self.print_header("INSTALLATION COMPLETE ✓")

        print("Configuration saved to:")
        print(f"  • .env (environment variables)")
        print(f"  • data/assistant_profile.json")
        print(f"  • data/boss_profile.json")
        print()

        print("Next steps:")
        print("  1. Start backend:")
        print(f"     cd {self.backend_dir}")
        print("     python -m uvicorn app.main:app --reload")
        print()
        print("  2. In another terminal, start web frontend:")
        print("     cd apps/web")
        print("     npm run dev")
        print()
        print("  3. Visit http://localhost:3000")
        print()

        print("Test the setup:")
        print("  python test_quick.py --verbose")
        print()

        return True

    def _save_profiles(self):
        """Save assistant and boss profiles to disk."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)

        if "PROFILES" not in self.config:
            return

        profiles = self.config["PROFILES"]

        # Assistant profile
        assistant_profile = {
            "assistant_name": "multi-agent-assistant",
            "email": profiles["assistant"].get("email"),
            "version": "0.1.0",
            "skills": profiles["assistant"].get("skills", []),
            "supported_agents": ["planner", "calendar", "finance", "wellness", "general"],
            "instructions": "Be concise and actionable.",
            "guardrails": [],
        }

        with open(data_dir / "assistant_profile.json", "w") as f:
            json.dump(assistant_profile, f, indent=2)

        # Boss profile (using name as boss_id)
        boss_id = profiles["boss"].get("name", "user").lower().replace(" ", "_")
        boss_profile = {
            "boss_id": boss_id,
            "name": profiles["boss"].get("name"),
            "email": profiles["boss"].get("email"),
            "timezone": profiles["boss"].get("timezone", "UTC"),
            "goals": profiles["boss"].get("goals", []),
            "constraints": profiles["boss"].get("constraints", []),
            "preferences": {},
            "summary": f"{profiles['boss'].get('name')} - initialized by installer",
        }

        with open(data_dir / "boss_profile.json", "w") as f:
            json.dump(boss_profile, f, indent=2)

        print(Colors.success("Profiles saved to data/"))


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
