#!/usr/bin/env python3
"""
Standalone TCP Listener for Telemetry Sleuth SMDR Data Capture.

This script starts the SMDR TCP listener service and can be run independently
for testing or as part of the containerized application.

Usage:
    python tcp_listener.py [--host HOST] [--port PORT]
"""

import argparse
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.tcp_listener import SMDRTCPListener
import logging

def main():
    """Main entry point for the standalone TCP listener."""
    parser = argparse.ArgumentParser(description='SMDR TCP Listener Service')
    parser.add_argument('--host', type=str, default=None,
                       help='Host IP address to bind to (default: from config)')
    parser.add_argument('--port', type=int, default=None,
                       help='Port number to listen on (default: from config)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('app.tcp_listener').setLevel(logging.DEBUG)
        logging.getLogger('app.parser').setLevel(logging.DEBUG)
    
    try:
        # Create and run the listener
        listener = SMDRTCPListener(host=args.host, port=args.port)
        
        print(f"Starting SMDR TCP Listener...")
        print(f"Host: {listener.host}")
        print(f"Port: {listener.port}")
        print(f"Press Ctrl+C to stop")
        print("-" * 50)
        
        listener.run_forever()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()