"""
This file has been moved to scripts/test_web_app.py
"""
                    'outbound_today', 'internal_today', 'external_today',
                    'avg_duration'
                ]
                
                passed = all(field in data for field in expected_fields)
                print(f"✓ API Stats working" if passed else "✗ API Stats missing fields")
                if passed:
                    print(f"  Total Records: {data.get('total_records', 0)}")
                    print(f"  Today's Calls: {data.get('today_records', 0)}")
                return passed
            else:
                print(f"✗ API Stats returned status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ API Stats test failed: {e}")
            return False
    
    def test_api_recent(self):
        """Test the recent records API endpoint."""
        print("Testing API Recent Records...")
        try:
            response = self.session.get(f"{self.base_url}/api/recent?limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✓ API Recent Records working - returned {len(data)} records")
                    return True
                else:
                    print("✗ API Recent Records returned non-list data")
                    return False
            else:
                print(f"✗ API Recent Records returned status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ API Recent Records test failed: {e}")
            return False
    
    def test_search_functionality(self):
        """Test search functionality with various parameters."""
        print("Testing Search Functionality...")
        try:
            # Test search with direction filter
            response = self.session.get(f"{self.base_url}/search?direction=I")
            if response.status_code != 200:
                print("✗ Search with direction filter failed")
                return False
            
            # Test search with date range
            today = datetime.now().strftime('%Y-%m-%d')
            response = self.session.get(f"{self.base_url}/search?date_from={today}")
            if response.status_code != 200:
                print("✗ Search with date filter failed")
                return False
            
            # Test search with phone number
            response = self.session.get(f"{self.base_url}/search?caller=1234")
            if response.status_code != 200:
                print("✗ Search with caller filter failed")
                return False
            
            print("✓ Search functionality working")
            return True
            
        except Exception as e:
            print(f"✗ Search functionality test failed: {e}")
            return False
    
    def test_record_detail(self):
        """Test record detail page (if records exist)."""
        print("Testing Record Detail Page...")
        try:
            # First check if we have any records
            with get_db_context() as session:
                record = session.query(CallRecord).first()
                
                if record:
                    response = self.session.get(f"{self.base_url}/record/{record.id}")
                    if response.status_code == 200:
                        content = response.text
                        checks = [
                            "Call Record Details" in content,
                            "Call Summary" in content,
                            "Technical Details" in content
                        ]
                        
                        passed = all(checks)
                        print(f"✓ Record detail page working" if passed else "✗ Record detail missing elements")
                        return passed
                    else:
                        print(f"✗ Record detail returned status code {response.status_code}")
                        return False
                else:
                    print("ℹ No records found - skipping record detail test")
                    return True
                    
        except Exception as e:
            print(f"✗ Record detail test failed: {e}")
            return False
    
    def create_test_data(self):
        """Create some test SMDR data for testing."""
        print("Creating test data...")
        try:
            parser = SMDRParser()
            
            # Sample SMDR records
            test_records = [
                "2024/01/15 14:30:25,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0,E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,2024/01/15 14:33:00,0,",
                "2024/01/15 15:45:12,00:01:20,3,2002,I,5559876543,2002,5559876543,0,1000002,0,E2002,Jane Doe,T9002,Line 2,0,0,,,,,,,,,,,,,,,,,2024/01/15 15:46:32,0,",
                "2024/01/15 16:20:45,00:03:45,8,2003,O,5555551234,5555551234,,1,1000003,0,E2003,Bob Wilson,T9003,Line 3,0,0,,,,,,,,,,,,,,,,,2024/01/15 16:24:30,0,",
            ]
            
            with get_db_context() as session:
                for record_data in test_records:
                    parsed_record = parser.parse_record(record_data)
                    if parsed_record:
                        session.add(parsed_record)
                
                session.commit()
                count = session.query(CallRecord).count()
                
            print(f"✓ Created {len(test_records)} test records (Total: {count})")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create test data: {e}")
            return False

def run_all_tests():
    """Run all web application tests."""
    print("=" * 60)
    print("Telemetry Sleuth Web Application Test Suite")
    print("=" * 60)
    
    # Initialize database first
    try:
        init_database()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    tester = WebAppTester()
    
    # Check if web app is running
    print("\nChecking web application connectivity...")
    if not tester.test_connection():
        print("✗ Web application is not running!")
        print("Please start the web app with: python app.py")
        return False
    
    print("✓ Web application is running")
    
    # Create test data
    tester.create_test_data()
    
    # Run tests
    tests = [
        ("Dashboard Page", tester.test_dashboard),
        ("Search Page", tester.test_search_page),
        ("API Stats Endpoint", tester.test_api_stats),
        ("API Recent Records", tester.test_api_recent),
        ("Search Functionality", tester.test_search_functionality),
        ("Record Detail Page", tester.test_record_detail),
    ]
    
    results = {}
    
    print("\n" + "=" * 60)
    print("Running Web Application Tests")
    print("=" * 60)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results[test_name] = False
        
        time.sleep(0.5)  # Brief pause between tests
    
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
        print("🎉 All web application tests passed!")
        print("\nYour Flask web interface is working correctly!")
        print(f"Access it at: http://localhost:5000")
        return True
    else:
        print("❌ Some web application tests failed!")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Telemetry Sleuth Web Application")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL of the web application")
    parser.add_argument("--create-data", action="store_true", help="Only create test data")
    
    args = parser.parse_args()
    
    if args.create_data:
        tester = WebAppTester(args.url)
        tester.create_test_data()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)