#!/usr/bin/env python3
"""
Test runner for Telemetry Sleuth.

This script runs various tests to validate the SMDR parsing and database functionality.
"""

import sys
import os
import subprocess
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_parser_tests():
    """Run the parser unit tests."""
    print("=" * 60)
    print("Running SMDR Parser Tests")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_parser.py')
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running parser tests: {e}")
        return False

def test_database_connection():
    """Test database connection and model creation."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        from app.models import init_database, get_db_context, CallRecord
        from app.config import Config
        
        config = Config()
        print(f"Database URL: {config.DATABASE_URL}")
        
        # Initialize database
        engine, session_factory = init_database()
        print("✓ Database connection established")
        print("✓ Tables created successfully")
        
        # Test session creation
        with get_db_context() as session:
            # Try to query the table (should be empty)
            count = session.query(CallRecord).count()
            print(f"✓ Database query successful - {count} records found")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_smdr_parsing():
    """Test SMDR parsing with sample data."""
    print("=" * 60)
    print("Testing SMDR Parsing")
    print("=" * 60)
    
    try:
        from app.parser import SMDRParser
        
        parser = SMDRParser()
        
        # Test sample record
        sample_record = (
            "2024/01/15 14:30:25,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0," \
            "E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,," \
            "2024/01/15 14:33:00,0,"
        )
        
        result = parser.parse_record(sample_record)
        
        if result:
            print("✓ Sample record parsed successfully")
            print(f"  Caller: {result.caller}")
            print(f"  Called: {result.called_number}")
            print(f"  Direction: {result.direction}")
            print(f"  Connected Time: {result.connected_time} seconds")
            print(f"  Call ID: {result.call_id}")
            return True
        else:
            print("✗ Failed to parse sample record")
            return False
            
    except Exception as e:
        print(f"✗ SMDR parsing test failed: {e}")
        return False
