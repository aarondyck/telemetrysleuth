"""
SMDR Parser for Telemetry Sleuth.

This module handles parsing of raw SMDR record strings into CallRecord objects.
It performs data validation and type conversion for each of the 37 fields.
"""

import logging
from datetime import datetime
from typing import Optional, List

from .models import CallRecord

logger = logging.getLogger(__name__)


class SMDRParser:
    """
    Parser for Avaya IP Office SMDR records.
    
    Converts comma-separated SMDR strings into CallRecord database objects
    with proper data validation and type conversion.
    """
    
    def __init__(self):
        self.expected_field_count = 37
    
    def parse_record(self, raw_record: str) -> Optional[CallRecord]:
        """
        Parse a raw SMDR record string into a CallRecord object.
        
        Args:
            raw_record: The raw comma-separated SMDR record
            
        Returns:
            CallRecord object if parsing successful, None otherwise
        """
        try:
            # Split by commas to get individual fields
            fields = raw_record.split(',')
            
            # Log field count for debugging
            if len(fields) != self.expected_field_count:
                logger.warning(f"Expected {self.expected_field_count} fields, got {len(fields)}. "
                              f"Record: {raw_record}")
            
            # Pad with empty strings if we have fewer fields than expected
            while len(fields) < self.expected_field_count:
                fields.append('')
            
            # Create CallRecord with parsed fields
            call_record = CallRecord(
                # Field 1: Call Start Time (YYYY/MM/DD HH:MM:SS)
                call_start_time=self._parse_datetime(fields[0]),
                
                # Field 2: Connected Time (HH:MM:SS -> seconds)
                connected_time=self._parse_duration_to_seconds(fields[1]),
                
                # Field 3: Ring Time (seconds)
                ring_time=self._parse_integer(fields[2]),
                
                # Field 4: Caller
                caller=self._parse_string(fields[3]),
                
                # Field 5: Direction (I/O)
                direction=self._parse_string(fields[4]),
                
                # Field 6: Called Number
                called_number=self._parse_string(fields[5]),
                
                # Field 7: Dialed Number
                dialed_number=self._parse_string(fields[6]),
                
                # Field 8: Account Code
                account_code=self._parse_string(fields[7]),
                
                # Field 9: Is Internal (0/1)
                is_internal=self._parse_boolean(fields[8]),
                
                # Field 10: Call ID
                call_id=self._parse_integer(fields[9]),
                
                # Field 11: Continuation (0/1)
                continuation=self._parse_boolean(fields[10]),
                
                # Field 12: Party1 Device
                party1_device=self._parse_string(fields[11]),
                
                # Field 13: Party1 Name
                party1_name=self._parse_string(fields[12]),
                
                # Field 14: Party2 Device
                party2_device=self._parse_string(fields[13]),
                
                # Field 15: Party2 Name
                party2_name=self._parse_string(fields[14]),
                
                # Field 16: Hold Time (seconds)
                hold_time=self._parse_integer(fields[15]),
                
                # Field 17: Park Time (seconds)
                park_time=self._parse_integer(fields[16]),
                
                # Field 18: Authorization Valid (0/1)
                authorization_valid=self._parse_boolean(fields[17]),
                
                # Field 19: Authorization Code
                authorization_code=self._parse_string(fields[18]),
                
                # Field 20: User Charged
                user_charged=self._parse_string(fields[19]),
                
                # Field 21: Call Charge
                call_charge=self._parse_string(fields[20]),
                
                # Field 22: Currency
                currency=self._parse_string(fields[21]),
                
                # Field 23: Amount at Last User Change
                amount_at_last_user_change=self._parse_string(fields[22]),
                
                # Field 24: Call Units
                call_units=self._parse_integer(fields[23]),
                
                # Field 25: Units at Last User Change
                units_at_last_user_change=self._parse_integer(fields[24]),
                
                # Field 26: Cost per Unit
                cost_per_unit=self._parse_integer(fields[25]),
                
                # Field 27: Mark Up
                mark_up=self._parse_integer(fields[26]),
                
                # Field 28: External Targeting Cause
                external_targeting_cause=self._parse_string(fields[27]),
                
                # Field 29: External Targeter ID
                external_targeter_id=self._parse_string(fields[28]),
                
                # Field 30: External Targeted Number
                external_targeted_number=self._parse_string(fields[29]),
                
                # Field 31: Calling Party Server IP
                calling_party_server_ip=self._parse_string(fields[30]),
                
                # Field 32: Unique Call ID for Caller
                unique_call_id_caller=self._parse_string(fields[31]),
                
                # Field 33: Called Party Server IP
                called_party_server_ip=self._parse_string(fields[32]),
                
                # Field 34: Unique Call ID for Called
                unique_call_id_called=self._parse_string(fields[33]),
                
                # Field 35: SMDR Record Time (YYYY/MM/DD HH:MM:SS)
                smdr_record_time=self._parse_datetime(fields[34]),
                
                # Field 36: Caller Consent Directive (0/2/6)
                caller_consent_directive=self._parse_integer(fields[35]),
                
                # Field 37: Calling Number Verification (A/B/C/N/A)
                calling_number_verification=self._parse_string(fields[36]),
                
                # Store raw data for debugging
                raw_data=raw_record
            )
            
            return call_record
            
        except Exception as e:
            logger.error(f"Error parsing SMDR record: {e}")
            logger.error(f"Raw record: {raw_record}")
            return None
    
    def _parse_string(self, value: str) -> Optional[str]:
        """Parse a string field, returning None for empty values."""
        if not value or value.strip() == '':
            return None
        return value.strip()
    
    def _parse_integer(self, value: str) -> Optional[int]:
        """Parse an integer field, returning None for empty/invalid values."""
        if not value or value.strip() == '':
            return None
        try:
            return int(value.strip())
        except ValueError:
            logger.warning(f"Could not parse integer: '{value}'")
            return None
    
    def _parse_boolean(self, value: str) -> Optional[bool]:
        """Parse a boolean field (0/1), returning None for empty values."""
        if not value or value.strip() == '':
            return None
        try:
            int_val = int(value.strip())
            return bool(int_val)
        except ValueError:
            logger.warning(f"Could not parse boolean: '{value}'")
            return None
    
    def _parse_datetime(self, value: str) -> Optional[datetime]:
        """
        Parse a datetime field in YYYY/MM/DD HH:MM:SS format.
        
        Args:
            value: DateTime string in YYYY/MM/DD HH:MM:SS format
            
        Returns:
            datetime object or None if parsing fails
        """
        if not value or value.strip() == '':
            return None
        
        try:
            # Expected format: YYYY/MM/DD HH:MM:SS
            return datetime.strptime(value.strip(), '%Y/%m/%d %H:%M:%S')
        except ValueError:
            try:
                # Try alternative format without seconds
                return datetime.strptime(value.strip(), '%Y/%m/%d %H:%M')
            except ValueError:
                logger.warning(f"Could not parse datetime: '{value}'")
                return None
    
    def _parse_duration_to_seconds(self, value: str) -> Optional[int]:
        """
        Parse a duration field in HH:MM:SS format to total seconds.
        
        Args:
            value: Duration string in HH:MM:SS format
            
        Returns:
            Total seconds as integer, or None if parsing fails
        """
        if not value or value.strip() == '':
            return None
        
        try:
            # Expected format: HH:MM:SS
            time_parts = value.strip().split(':')
            
            if len(time_parts) == 3:
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(time_parts) == 2:
                # MM:SS format
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])
                return minutes * 60 + seconds
            else:
                # Assume it's just seconds
                return int(value.strip())
                
        except (ValueError, IndexError):
            logger.warning(f"Could not parse duration: '{value}'")
            return None


def validate_smdr_record(record: CallRecord) -> bool:
    """
    Validate a parsed SMDR record for basic consistency.
    
    Args:
        record: The CallRecord to validate
        
    Returns:
        True if record appears valid, False otherwise
    """
    # Basic validation rules
    if not record.call_start_time:
        logger.warning("Invalid record: missing call start time")
        return False
    
    if record.direction and record.direction not in ['I', 'O']:
        logger.warning(f"Invalid direction: {record.direction}")
        return False
    
    if record.caller_consent_directive is not None:
        if record.caller_consent_directive not in [0, 2, 6]:
            logger.warning(f"Invalid caller consent directive: {record.caller_consent_directive}")
            return False
    
    return True