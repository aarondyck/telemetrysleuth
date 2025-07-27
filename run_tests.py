"""
This file has been moved to scripts/run_tests.py
"""

def main():
    """Run all tests."""
    print("Telemetry Sleuth Test Suite")
    print("=" * 60)
    
    tests = [
        ("SMDR Parser Unit Tests", run_parser_tests),
        ("Database Connection", test_database_connection),
        ("SMDR Parsing", test_smdr_parsing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())