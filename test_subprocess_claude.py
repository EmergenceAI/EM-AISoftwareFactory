#!/usr/bin/env python3
"""
Test script to diagnose subprocess claude issue
"""
import subprocess
import os
import tempfile
from pathlib import Path

print("=" * 60)
print("Testing subprocess call to claude CLI")
print("=" * 60)

# Test 1: which claude
print("\n1. Testing 'which claude'...")
result = subprocess.run(['which', 'claude'], capture_output=True, text=True, env=os.environ.copy())
print(f"   Result: {result.stdout.strip()}")
print(f"   Return code: {result.returncode}")

# Test 2: claude --version
print("\n2. Testing 'claude --version'...")
try:
    result = subprocess.run(
        ['claude', '--version'],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=5
    )
    print(f"   Result: {result.stdout.strip()}")
    print(f"   Return code: {result.returncode}")
except FileNotFoundError as e:
    print(f"   ERROR: {e}")
except subprocess.TimeoutExpired:
    print("   ERROR: Timeout")

# Test 3: claude with message file (similar to orchestrator)
print("\n3. Testing 'claude --message-file'...")
message = "Hello, this is a test message"
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write(message)
    message_file = Path(f.name)

try:
    result = subprocess.run(
        ['claude', '--message-file', str(message_file)],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=5
    )
    print(f"   Return code: {result.returncode}")
    print(f"   Stdout length: {len(result.stdout)}")
    print(f"   Stderr: {result.stderr[:200] if result.stderr else 'None'}")
except FileNotFoundError as e:
    print(f"   ERROR FileNotFoundError: {e}")
except subprocess.TimeoutExpired:
    print("   ERROR: Timeout (expected for interactive command)")
finally:
    message_file.unlink()

# Test 4: Check PATH
print("\n4. Current PATH:")
path_parts = os.environ.get('PATH', '').split(':')
for i, p in enumerate(path_parts[:10], 1):  # First 10 entries
    print(f"   {i}. {p}")

# Test 5: Check if /opt/homebrew/bin/claude exists
claude_path = Path('/opt/homebrew/bin/claude')
print(f"\n5. {claude_path} exists: {claude_path.exists()}")
if claude_path.exists():
    print(f"   Is executable: {os.access(claude_path, os.X_OK)}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
