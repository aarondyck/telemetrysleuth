#!/usr/bin/env python3
"""
SMDR Test Data Sender for Telemetry Sleuth.

This script sends sample SMDR data to the TCP listener for testing purposes.
It simulates an Avaya IP Office system sending SMDR records.

Usage:
    python test_smdr_sender.py [--host HOST] [--port PORT] [--count COUNT]
"""

import socket
import time
import argparse
import sys
from datetime import datetime, timedelta


class SMDRTestSender:
    """Test sender for SMDR data."""
    
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        
    def create_sample_records(self, count=5):
        """Create sample SMDR records for testing."""
        records = []
        base_time = datetime.now()
        
        sample_data = [
            # Outbound call
            {
                'caller': '2001',
                'called': '5551234567',
                'direction': 'O',
                'is_internal': '0',
                'party1_device': 'E2001',
                'party1_name': 'John Smith',
                'connected_time': '00:02:35'
            },
            # Inbound call
            {
                'caller': '5559876543',
                'called': '2002',
                'direction': 'I',
                'is_internal': '0',
                'party1_device': 'T9001',
                'party2_device': 'E2002',
                'party2_name': 'Jane Doe',
                'connected_time': '00:01:45'
            },
            # Internal call
            {
                'caller': '2001',
                'called': '2003',
                'direction': 'O',
                'is_internal': '1',
                'party1_device': 'E2001',
                'party1_name': 'John Smith',
                'party2_device': 'E2003',
                'party2_name': 'Bob Johnson',
                'connected_time': '00:00:30'
            },
            # Voicemail call
            {
                'caller': '2002',
                'called': '2002',
                'direction': 'O',
                'is_internal': '1',
                'party1_device': 'E2002',
                'party1_name': 'Jane Doe',
                'party2_device': 'V9501',
                'party2_name': 'VM Channel 1',
                'connected_time': '00:00:15'
            },
            # Failed call (no connection)
            {
                'caller': '2001',
                'called': '5551111111',
                'direction': 'O',
                'is_internal': '0',
                'party1_device': 'E2001',
                'party1_name': 'John Smith',
                'connected_time': '00:00:00',
                'ring_time': '30'
            }
        ]
        
        for i in range(count):
            sample = sample_data[i % len(sample_data)]
            call_time = base_time - timedelta(minutes=i*5)
            call_id = 1000000 + i
            
            # Build the 37-field CSV record
            record_fields = [
                call_time.strftime('%Y/%m/%d %H:%M:%S'),  # 1: Call Start Time
                sample.get('connected_time', '00:00:00'),  # 2: Connected Time
                sample.get('ring_time', '5'),              # 3: Ring Time
                sample.get('caller', ''),                  # 4: Caller
                sample.get('direction', 'O'),              # 5: Direction
                sample.get('called', ''),                  # 6: Called Number
                sample.get('called', ''),                  # 7: Dialed Number (same as called for this test)
                '',                                        # 8: Account Code
                sample.get('is_internal', '0'),            # 9: Is Internal
                str(call_id),                             # 10: Call ID
                '0',                                      # 11: Continuation
                sample.get('party1_device', ''),          # 12: Party1 Device
                sample.get('party1_name', ''),            # 13: Party1 Name
                sample.get('party2_device', ''),          # 14: Party2 Device
                sample.get('party2_name', ''),            # 15: Party2 Name
                '0',                                      # 16: Hold Time
                '0',                                      # 17: Park Time
                '',                                       # 18: Authorization Valid
                '',                                       # 19: Authorization Code
                '',                                       # 20: User Charged
                '',                                       # 21: Call Charge
                '',                                       # 22: Currency
                '',                                       # 23: Amount at Last User Change
                '',                                       # 24: Call Units
                '',                                       # 25: Units at Last User Change
                '',                                       # 26: Cost per Unit
                '',                                       # 27: Mark Up
                '',                                       # 28: External Targeting Cause
                '',                                       # 29: External Targeter ID
                '',                                       # 30: External Targeted Number
                '',                                       # 31: Calling Party Server IP
                '',                                       # 32: Unique Call ID Caller
                '',                                       # 33: Called Party Server IP
                '',                                       # 34: Unique Call ID Called
                call_time.strftime('%Y/%m/%d %H:%M:%S'),  # 35: SMDR Record Time
                '0',                                      # 36: Caller Consent Directive
                ''                                        # 37: Calling Number Verification
            ]
            
            record = ','.join(record_fields) + '\r\n'
            records.append(record)
            
        return records
    
    def send_records(self, records, delay=1.0):
        """Send SMDR records to the TCP listener."""
        try:
            print(f"Connecting to {self.host}:{self.port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            print("Connected successfully!")
            
            for i, record in enumerate(records, 1):
                print(f"Sending record {i}/{len(records)}...")
                print(f"  Data: {record.strip()}")
                
                # Send the record
                sock.send(record.encode('utf-8'))
                
                # Wait before sending next record
                if i < len(records):
                    time.sleep(delay)
            
            print("All records sent successfully!")
            
        except ConnectionRefusedError:
            print(f"Error: Could not connect to {self.host}:{self.port}")
            print("Make sure the SMDR TCP listener is running.")
            return False
        except Exception as e:
            print(f"Error sending data: {e}")
            return False
        finally:
            try:
                sock.close()
            except:
                pass
        
        return True


def main():
    """Main entry point for the test sender."""
    parser = argparse.ArgumentParser(description='SMDR Test Data Sender')
    parser.add_argument('--host', type=str, default='localhost',
                       help='Host to connect to (default: localhost)')
    parser.add_argument('--port', type=int, default=9000,
                       help='Port to connect to (default: 9000)')
    parser.add_argument('--count', type=int, default=5,
                       help='Number of test records to send (default: 5)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between records in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Create sender and generate test data
    sender = SMDRTestSender(args.host, args.port)
    records = sender.create_sample_records(args.count)
    
    print("SMDR Test Data Sender")
    print("=" * 40)
    print(f"Target: {args.host}:{args.port}")
    print(f"Records to send: {args.count}")
    print(f"Delay between records: {args.delay}s")
    print()
    
    # Send the records
    success = sender.send_records(records, args.delay)
    
    if success:
        print("\nTest completed successfully!")
        sys.exit(0)
    else:
        print("\nTest failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()