#!/usr/bin/env python3
import unittest
import sys
import os

def run_tests():
    print("=" * 70)
    print("Running Email Monitor Discord Bot tests")
    print("=" * 70)
    
    # Discover and run all tests
    tests = unittest.defaultTestLoader.discover('tests')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    
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