#!/usr/bin/env python3
"""
Unit tests for the SMDR Parser.

This module contains tests to validate the SMDR parser functionality
using sample data including malformed records and records with empty fields.
"""

import unittest
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.parser import SMDRParser, validate_smdr_record


class TestSMDRParser(unittest.TestCase):
    """Test cases for the SMDR Parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = SMDRParser()
    
    def test_complete_record_parsing(self):
        """Test parsing a complete SMDR record with all fields."""
        sample_record = (
            "2024/01/15 14:30:25,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0,"
            "E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 14:33:00,0,"
        )
        
        result = self.parser.parse_record(sample_record)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.caller, "2001")
        self.assertEqual(result.called_number, "5551234567")
        self.assertEqual(result.direction, "O")
        self.assertEqual(result.connected_time, 155)  # 2:35 = 155 seconds
        self.assertEqual(result.ring_time, 5)
        self.assertEqual(result.call_id, 1000001)
        self.assertFalse(result.is_internal)
        self.assertEqual(result.party1_device, "E2001")
        self.assertEqual(result.party1_name, "John Smith")
    
    def test_internal_call_parsing(self):
        """Test parsing an internal call record."""
        sample_record = (
            "2024/01/15 15:45:12,00:01:30,3,2001,O,2002,2002,,1,1000002,0,"
            "E2001,John Smith,E2002,Jane Doe,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 15:46:42,0,"
        )
        
        result = self.parser.parse_record(sample_record)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.caller, "2001")
        self.assertEqual(result.called_number, "2002")
        self.assertEqual(result.direction, "O")
        self.assertTrue(result.is_internal)
        self.assertEqual(result.connected_time, 90)  # 1:30 = 90 seconds
    
    def test_inbound_call_parsing(self):
        """Test parsing an inbound call record."""
        sample_record = (
            "2024/01/15 16:20:00,00:03:45,8,5559876543,I,2003,2003,,0,1000003,0,"
            "T9002,Line 2,E2003,Bob Johnson,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 16:23:45,0,"
        )
        
        result = self.parser.parse_record(sample_record)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.caller, "5559876543")
        self.assertEqual(result.called_number, "2003")
        self.assertEqual(result.direction, "I")
        self.assertFalse(result.is_internal)
        self.assertEqual(result.connected_time, 225)  # 3:45 = 225 seconds
    
    def test_empty_fields_handling(self):
        """Test handling of records with empty fields."""
        sample_record = (
            "2024/01/15 17:00:00,00:00:00,0,,O,,,,,1000004,0,"
            ",,,,0,0,,,,,,,,,,,,,,,,,,"
            ",0,"
        )
        
        result = self.parser.parse_record(sample_record)
        
        self.assertIsNotNone(result)
        self.assertIsNone(result.caller)
        self.assertIsNone(result.called_number)
        self.assertEqual(result.direction, "O")
        self.assertEqual(result.connected_time, 0)
        self.assertEqual(result.call_id, 1000004)
    
    def test_malformed_record_handling(self):
        """Test handling of malformed records."""
        # Too few fields
        malformed_record1 = "2024/01/15 14:30:25,00:02:35,5"
        result1 = self.parser.parse_record(malformed_record1)
        self.assertIsNotNone(result1)  # Should still parse with padding
        
        # Invalid datetime format
        malformed_record2 = (
            "invalid-date,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0,"
            "E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 14:33:00,0,"
        )
        result2 = self.parser.parse_record(malformed_record2)
        self.assertIsNotNone(result2)
        self.assertIsNone(result2.call_start_time)  # Should handle invalid datetime gracefully
        
        # Invalid duration format
        malformed_record3 = (
            "2024/01/15 14:30:25,invalid-duration,5,2001,O,5551234567,5551234567,,0,1000001,0,"
            "E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 14:33:00,0,"
        )
        result3 = self.parser.parse_record(malformed_record3)
        self.assertIsNotNone(result3)
        self.assertIsNone(result3.connected_time)  # Should handle invalid duration gracefully
    
    def test_datetime_parsing(self):
        """Test datetime parsing functionality."""
        # Valid datetime
        dt1 = self.parser._parse_datetime("2024/01/15 14:30:25")
        self.assertEqual(dt1, datetime(2024, 1, 15, 14, 30, 25))
        
        # Valid datetime without seconds
        dt2 = self.parser._parse_datetime("2024/01/15 14:30")
        self.assertEqual(dt2, datetime(2024, 1, 15, 14, 30, 0))
        
        # Empty string
        dt3 = self.parser._parse_datetime("")
        self.assertIsNone(dt3)
        
        # Invalid format
        dt4 = self.parser._parse_datetime("invalid-date")
        self.assertIsNone(dt4)
    
    def test_duration_parsing(self):
        """Test duration parsing to seconds."""
        # HH:MM:SS format
        dur1 = self.parser._parse_duration_to_seconds("01:30:45")
        self.assertEqual(dur1, 5445)  # 1*3600 + 30*60 + 45
        
        # MM:SS format
        dur2 = self.parser._parse_duration_to_seconds("05:30")
        self.assertEqual(dur2, 330)  # 5*60 + 30
        
        # Just seconds
        dur3 = self.parser._parse_duration_to_seconds("45")
        self.assertEqual(dur3, 45)
        
        # Empty string
        dur4 = self.parser._parse_duration_to_seconds("")
        self.assertIsNone(dur4)
        
        # Invalid format
        dur5 = self.parser._parse_duration_to_seconds("invalid")
        self.assertIsNone(dur5)
    
    def test_boolean_parsing(self):
        """Test boolean field parsing."""
        # Valid boolean values
        self.assertTrue(self.parser._parse_boolean("1"))
        self.assertFalse(self.parser._parse_boolean("0"))
        
        # Empty value
        self.assertIsNone(self.parser._parse_boolean(""))
        
        # Invalid value
        self.assertIsNone(self.parser._parse_boolean("invalid"))
    
    def test_record_validation(self):
        """Test SMDR record validation."""
        # Create a valid record
        sample_record = (
            "2024/01/15 14:30:25,00:02:35,5,2001,O,5551234567,5551234567,,0,1000001,0,"
            "E2001,John Smith,T9001,Line 1,0,0,,,,,,,,,,,,,,,,,,"
            "2024/01/15 14:33:00,0,"
        )
        
        parsed_record = self.parser.parse_record(sample_record)
        self.assertTrue(validate_smdr_record(parsed_record))
        
        # Test invalid direction
        parsed_record.direction = "X"
        self.assertFalse(validate_smdr_record(parsed_record))
        
        # Test missing call start time
        parsed_record.direction = "O"
        parsed_record.call_start_time = None
        self.assertFalse(validate_smdr_record(parsed_record))


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)