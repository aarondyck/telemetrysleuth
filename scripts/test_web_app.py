#!/usr/bin/env python3
"""
Test script for the Flask Web Application.

This script tests all web routes, API endpoints, and functionality
of the Telemetry Sleuth web interface.
"""

import sys
import os
import requests
import time
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import Config
from app.models import init_database, get_db_context, CallRecord
from app.parser import SMDRParser

class WebAppTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_connection(self):
        """Test if the web app is running."""
        try:
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def test_dashboard(self):
        """Test the main dashboard page."""
        print("Testing Dashboard...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                content = response.text
                # Check for expected elements
                checks = [
                    "Dashboard" in content,
                    "Total Records" in content,
                    "Today's Calls" in content,
                    "Recent Call Records" in content,
                    "bootstrap" in content.lower()
                ]
                
                passed = all(checks)
                print(f"✓ Dashboard loaded successfully" if passed else "✗ Dashboard missing elements")
                return passed
            else:
                print(f"✗ Dashboard returned status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Dashboard test failed: {e}")
            return False
    
    def test_search_page(self):
        """Test the search page."""
        print("Testing Search Page...")
        try:
            response = self.session.get(f"{self.base_url}/search")
            if response.status_code == 200:
                content = response.text
                # Check for search form elements
                checks = [
                    "Search Records" in content,
                    "date_from" in content,
                    "date_to" in content,
                    "direction" in content,
                    "caller" in content,
                    "called" in content
                ]
                
                passed = all(checks)
                print(f"✓ Search page loaded successfully" if passed else "✗ Search page missing elements")
                return passed
            else:
                print(f"✗ Search page returned status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Search page test failed: {e}")
            return False
    
    def test_api_stats(self):
        """Test the stats API endpoint."""
        print("Testing API Stats Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                data = response.json()
                # Check for expected fields
                expected_fields = [
                    'total_records', 'today_records', 'inbound_today',
                    'outbound_today', 'missed_today', 'recent_records'
                ]
                # Check that all expected fields are present
                passed = all(field in data for field in expected_fields)
                print(f"✓ API stats endpoint returned expected fields" if passed else "✗ API stats endpoint missing fields")
                return passed
            else:
                print(f"✗ API stats endpoint returned status code {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ API stats test failed: {e}")
            return False
    
    def test_api_call_records(self, limit=5):
        """Test the call records API endpoint."""
        print("Testing API Call Records Endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/call_records?limit={limit}")
            if response.status_code == 200:
                data = response.json()
                # Check that we received the correct number of records
                if len(data) == limit:
                    print("✓ API call records endpoint returned the correct number of records")
                else:
                    print(f"✗ API call records endpoint returned {len(data)} records, expected {limit}")
                
                # Check that each record has the expected fields
                expected_fields = ['id', 'caller', 'called', 'start_time', 'duration', 'direction', 'status']
                for record in data:
                    passed = all(field in record for field in expected_fields)
                    if not passed:
                        print(f"✗ Record {record.get('id')} is missing fields")
                
                return True
            else:
                print(f"✗ API call records endpoint returned status code {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ API call records test failed: {e}")
            return False
    
    def test_upload_smdr(self, file_path):
        """Test uploading an SMDR file."""
        print(f"Testing SMDR Upload with file {file_path}...")
        try:
            with open(file_path, 'rb') as f:
                response = self.session.post(f"{self.base_url}/upload_smdr", files={"file": f})
                if response.status_code == 200:
                    print("✓ SMDR file uploaded successfully")
                    return True
                else:
                    print(f"✗ SMDR upload failed with status code {response.status_code}")
                    return False
        except Exception as e:
            print(f"✗ SMDR upload test failed: {e}")
            return False
    
    def test_parse_smdr(self, file_path):
        """Test parsing an SMDR file."""
        print(f"Testing SMDR Parse with file {file_path}...")
        try:
            with open(file_path, 'r') as f:
                smdr_data = f.read()
                parser = SMDRParser(smdr_data)
                records = parser.parse()
                
                # Check that records were created
                if records:
                    print(f"✓ Parsed SMDR file and created {len(records)} records")
                    return True
                else:
                    print("✗ No records created from SMDR file")
                    return False
        except Exception as e:
            print(f"✗ SMDR parse test failed: {e}")
            return False
    
    def test_database_integration(self):
        """Test the database integration."""
        print("Testing Database Integration...")
        try:
            # Initialize the database
            init_db_result = init_database()
            if init_db_result:
                print("✓ Database initialized successfully")
            else:
                print("✗ Database initialization failed")
            
            # Test database context manager
            with get_db_context() as db:
                # Query the count of call records
                record_count = db.session.query(CallRecord).count()
                print(f"✓ Found {record_count} call records in the database")
                
                # Add a test record
                test_record = CallRecord(
                    caller="Test Caller",
                    called="Test Called",
                    start_time=datetime.now(),
                    duration=3600,
                    direction="inbound",
                    status="completed"
                )
                db.session.add(test_record)
                db.session.commit()
                print("✓ Test record added to the database")
                
                # Query the test record
                added_record = db.session.query(CallRecord).filter_by(caller="Test Caller").first()
                if added_record:
                    print(f"✓ Found added test record: {added_record}")
                else:
                    print("✗ Test record not found in the database")
                
                # Clean up - remove the test record
                db.session.delete(added_record)
                db.session.commit()
                print("✓ Test record removed from the database")
            
            return True
        except Exception as e:
            print(f"✗ Database integration test failed: {e}")
            return False

def run_tests():
    tester = WebAppTester()
    
    # Test connection to the web app
    if not tester.test_connection():
        print("✗ Unable to connect to the web app. Is it running?")
        return
    
    # Test dashboard
    tester.test_dashboard()
    
    # Test search page
    tester.test_search_page()
    
    # Test API endpoints
    tester.test_api_stats()
    tester.test_api_call_records()
    
    # Test SMDR upload and parsing
    test_smdr_file = os.path.join(os.path.dirname(__file__), 'test_data', 'sample.smdr')
    tester.test_upload_smdr(test_smdr_file)
    tester.test_parse_smdr(test_smdr_file)
    
    # Test database integration
    tester.test_database_integration()

if __name__ == "__main__":
    run_tests()
