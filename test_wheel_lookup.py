#!/usr/bin/env python3
"""Quick integration test for ancestor wheel lookup."""

import sys
import os

# Add the pipeline_generator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'buildkite', 'pipeline_generator'))

from utils_lib.wheel_utils import check_wheel_exists, find_nearest_wheel_commit
from utils_lib.git_utils import get_ancestors, has_cpp_changes_between

def test_check_wheel_exists():
    """Test checking if a wheel exists."""
    # This is a known commit with a wheel (from the plan)
    commit = "bcd2f74c0d1e85a2da4dcb41849ad75a7e3fdaf4"
    result = check_wheel_exists(commit)
    print(f"Wheel exists for {commit}: {result}")
    return result

def test_find_nearest_wheel():
    """Test finding the nearest wheel commit."""
    # Use a recent commit that should have ancestors with wheels
    commit = "bcd2f74c0d1e85a2da4dcb41849ad75a7e3fdaf4"
    result = find_nearest_wheel_commit(commit, max_ancestors=10)
    print(f"Nearest wheel commit for {commit}: {result}")
    return result is not None

def test_get_ancestors():
    """Test getting ancestor commits."""
    # Need to be in a git repo for this to work
    try:
        os.chdir('/home/hdds/480ssd/codebase/ci-infra')
        commit = "HEAD"
        ancestors = get_ancestors(commit, max_count=5)
        print(f"First 5 ancestors from HEAD: {ancestors[:5]}")
        return len(ancestors) > 0
    except Exception as e:
        print(f"Error getting ancestors: {e}")
        return False

def test_has_cpp_changes():
    """Test checking for C++ changes between commits."""
    try:
        os.chdir('/home/hdds/480ssd/codebase/ci-infra')
        # Compare HEAD with HEAD~1
        result = has_cpp_changes_between("HEAD~1", "HEAD")
        print(f"C++ changes between HEAD~1 and HEAD: {result}")
        return True  # Just return True if it doesn't crash
    except Exception as e:
        print(f"Error checking C++ changes: {e}")
        return False

if __name__ == "__main__":
    print("Testing wheel lookup functionality...\n")

    tests = [
        ("check_wheel_exists", test_check_wheel_exists),
        ("find_nearest_wheel", test_find_nearest_wheel),
        ("get_ancestors", test_get_ancestors),
        ("has_cpp_changes", test_has_cpp_changes),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n--- Testing {name} ---")
        try:
            result = test_func()
            results.append((name, result))
            print(f"Result: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"EXCEPTION: {e}")
            results.append((name, False))

    print("\n\n=== Summary ===")
    for name, result in results:
        print(f"{name}: {'PASS' if result else 'FAIL'}")

    all_passed = all(r[1] for r in results)
    sys.exit(0 if all_passed else 1)
