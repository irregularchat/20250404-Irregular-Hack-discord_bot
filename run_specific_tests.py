#!/usr/bin/env python3
"""
Test runner script for specific modules of the Email Monitor Discord Bot.
"""

import unittest
import sys
import os
import warnings

def run_tests(test_module):
    """Discover and run tests for a specific module."""
    # Suppress warnings about coroutines not being awaited
    warnings.filterwarnings("ignore", message="coroutine '.*' was never awaited")
    
    # Print test information
    print("=" * 70)
    print(f"Running tests for module: {test_module}")
    print("=" * 70)
    
    # Run tests
    test_loader = unittest.TestLoader()
    
    # Load tests from specific module
    try:
        test_suite = test_loader.loadTestsFromName(f"tests.{test_module}")
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
    except (ImportError, AttributeError) as e:
        print(f"Error: Could not load tests for module '{test_module}': {e}")
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_specific_tests.py <test_module_name>")
        print("Example: python run_specific_tests.py test_discord_notifier")
        sys.exit(1)
    
    test_module = sys.argv[1]
    sys.exit(run_tests(test_module)) 