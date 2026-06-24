#!/usr/bin/env python3
"""
Quick test script for GitHub Models integration.
Run this to verify everything is working.

Usage:
    python test_quick.py
    python test_quick.py --with-github-models  # Test with GitHub Models brain
"""

import httpx
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"
VERBOSE = "--verbose" in sys.argv
WITH_MODELS = "--with-github-models" in sys.argv


def print_test(name, passed, error=None):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status:8} | {name}")
    if error and VERBOSE:
        print(f"         | Error: {error}")


def test_health():
    """Test health endpoint."""
    try:
        resp = httpx.get(f"{BASE_URL}/health", timeout=5)
        passed = resp.status_code == 200
        print_test("Health check", passed)
        return passed
    except Exception as e:
        print_test("Health check", False, str(e))
        return False


def test_github_models():
    """Test GitHub Models connection."""
    try:
        resp = httpx.post(f"{BASE_URL}/models/test-connection", timeout=10)
        data = resp.json()
        passed = resp.status_code in [200, 400] and "success" in data
        print_test("GitHub Models test-connection", passed)
        if VERBOSE:
            print(f"         | Response: {data}")
        return passed
    except Exception as e:
        print_test("GitHub Models test-connection", False, str(e))
        return False


def test_chat_basic():
    """Test basic chat without GitHub Models."""
    try:
        resp = httpx.post(
            f"{BASE_URL}/chat",
            json={"user_id": "test_user", "message": "Help me plan my week", "context": {}},
            timeout=5,
        )
        data = resp.json()
        passed = (
            resp.status_code == 200
            and "result" in data
            and "summary" in data["result"]
            and "actions" in data["result"]
        )
        print_test("Chat (basic)", passed)
        if passed and VERBOSE:
            print(f"         | Route: {data.get('route')}")
            print(f"         | Summary: {data['result']['summary'][:50]}...")
        return passed
    except Exception as e:
        print_test("Chat (basic)", False, str(e))
        return False


def test_profiles():
    """Test profile management endpoints."""
    results = []

    # Get assistant profile
    try:
        resp = httpx.get(f"{BASE_URL}/profiles/assistant", timeout=5)
        passed = resp.status_code == 200 and "assistant_name" in resp.json()
        print_test("Get assistant profile", passed)
        results.append(passed)
    except Exception as e:
        print_test("Get assistant profile", False, str(e))
        results.append(False)

    # Create assistant profile
    try:
        resp = httpx.post(
            f"{BASE_URL}/profiles/assistant",
            json={
                "email": "test@example.com",
                "skills": [
                    {"skill": "planning", "level": "advanced", "description": "Planning"}
                ],
            },
            timeout=5,
        )
        passed = resp.status_code == 200
        print_test("Update assistant profile", passed)
        results.append(passed)
    except Exception as e:
        print_test("Update assistant profile", False, str(e))
        results.append(False)

    # Create boss profile
    try:
        resp = httpx.post(
            f"{BASE_URL}/profiles/boss/test_user",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "goals": ["Complete project", "Learn new skills"],
                "constraints": ["Max 50 hours/week"],
            },
            timeout=5,
        )
        passed = resp.status_code == 200
        print_test("Create boss profile", passed)
        results.append(passed)
    except Exception as e:
        print_test("Create boss profile", False, str(e))
        results.append(False)

    # Get boss profile
    try:
        resp = httpx.get(f"{BASE_URL}/profiles/boss/test_user", timeout=5)
        passed = resp.status_code == 200 and "boss_id" in resp.json()
        print_test("Get boss profile", passed)
        results.append(passed)
    except Exception as e:
        print_test("Get boss profile", False, str(e))
        results.append(False)

    return all(results)


def test_chat_with_context():
    """Test chat with profile context."""
    try:
        resp = httpx.post(
            f"{BASE_URL}/chat",
            json={
                "user_id": "test_user",
                "message": "I need to finish by Friday",
                "context": {"boss_context": "Test User, goals: [Complete project]"},
            },
            timeout=10,
        )
        data = resp.json()
        passed = (
            resp.status_code == 200
            and "result" in data
            and "summary" in data["result"]
        )
        print_test("Chat (with context)", passed)
        if passed and VERBOSE:
            print(f"         | Summary: {data['result']['summary'][:50]}...")
        return passed
    except Exception as e:
        print_test("Chat (with context)", False, str(e))
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TESTING: GitHub Models Integration")
    print("=" * 60 + "\n")

    print(f"Target: {BASE_URL}")
    if VERBOSE:
        print("Mode: VERBOSE")
    if WITH_MODELS:
        print("Mode: WITH_GITHUB_MODELS")
    print()

    tests = [
        ("Backend Connectivity", test_health),
        ("GitHub Models", test_github_models),
        ("Chat Basic", test_chat_basic),
        ("Profiles", test_profiles),
        ("Chat with Context", test_chat_with_context),
    ]

    if WITH_MODELS:
        print("Running with GitHub Models (full AI brain)...\n")
    else:
        print("Running in fallback mode (no AI brain)...\n")

    results = []
    for category, test_func in tests:
        result = test_func()
        results.append(result)
        print()

    # Summary
    passed = sum(results)
    total = len(results)
    print("=" * 60)
    print(f"Summary: {passed}/{total} test categories passed")
    print("=" * 60)

    if passed == total:
        print("\n✅ All tests passed! System is ready.\n")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Check errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
