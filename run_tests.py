#!/usr/bin/env python3
"""
Test runner script for Email Monitor Discord Bot.
Discovers and runs all tests in the tests directory.
"""

import unittest
import sys
import os
import warnings

def run_tests():
    """Discover and run all tests, return True if all tests pass."""
    # Suppress warnings about coroutines not being awaited
    warnings.filterwarnings("ignore", message="coroutine '.*' was never awaited")
    
    # Print test information
    print("=" * 70)
    print("Running Email Monitor Discord Bot tests")
    print("=" * 70)
    
    # Discover tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    # Return exit code based on result
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests()) 