#!/usr/bin/env python3
"""
Service Startup Script for Telemetry Sleuth.

This script provides easy management of all Telemetry Sleuth services
including the TCP listener, web interface, and database initialization.
"""

import sys
import os
import subprocess
import time
import signal
import argparse
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.config import Config

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.config = Config()
        
    def init_database(self):
        """Initialize the database."""
        print("Initializing database...")
        try:
            from app.models import init_database
            init_database()
            print("✓ Database initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            return False
    
    def start_tcp_listener(self):
        """Start the TCP listener service."""
        print(f"Starting TCP listener on {self.config.TCP_HOST}:{self.config.TCP_PORT}...")
        try:
            process = subprocess.Popen([
                sys.executable, "tcp_listener.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['tcp_listener'] = process
            time.sleep(2)  # Give it time to start
            
            if process.poll() is None:
                print("✓ TCP listener started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"✗ TCP listener failed to start:")
                if stderr:
                    print(f"  Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to start TCP listener: {e}")
            return False
    
    def start_web_app(self):
        """Start the Flask web application."""
        print("Starting Flask web application on port 5000...")
        try:
            process = subprocess.Popen([
                sys.executable, "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['web_app'] = process
            time.sleep(3)  # Give it time to start
            
            if process.poll() is None:
                print("✓ Web application started successfully")
                print("  Access the web interface at: http://localhost:5000")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"✗ Web application failed to start:")
                if stderr:
                    print(f"  Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to start web application: {e}")
            return False
    
    def check_service_status(self):
        """Check the status of all services."""
        print("\nService Status:")
        print("-" * 40)
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                print(f"✓ {service_name}: Running (PID: {process.pid})")
            else:
                print(f"✗ {service_name}: Stopped")
    
    def stop_all_services(self):
        """Stop all running services."""
        print("\nStopping all services...")
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                print(f"Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print(f"✓ {service_name} stopped")
                except subprocess.TimeoutExpired:
                    print(f"Force killing {service_name}...")
                    process.kill()
                    process.wait()
                    print(f"✓ {service_name} force stopped")
            else:
                print(f"✓ {service_name} already stopped")
    
    def run_tests(self):
        """Run the test suite."""
        print("Running test suite...")
        try:
            result = subprocess.run([
                sys.executable, "test_web_app.py"
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"✗ Test suite failed: {e}")
            return False
    
    def send_test_data(self, count=10):
        """Send test SMDR data to the TCP listener."""
        print(f"Sending {count} test SMDR records...")
        try:
            result = subprocess.run([
                sys.executable, "tests/test_smdr_sender.py", "--count", str(count)
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"✗ Failed to send test data: {e}")
            return False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nReceived interrupt signal. Shutting down...")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.stop_all_services()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Telemetry Sleuth Service Manager")
    parser.add_argument("command", choices=[
        "start", "stop", "status", "restart", "test", "init-db", "send-test-data"
    ], help="Command to execute")
    parser.add_argument("--service", choices=["tcp", "web", "all"], default="all",
                       help="Specific service to control (default: all)")
    parser.add_argument("--test-records", type=int, default=10,
                       help="Number of test records to send (default: 10)")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    signal_handler.manager = manager  # Make manager available to signal handler
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("Telemetry Sleuth Service Manager")
    print("=" * 60)
    print(f"Command: {args.command}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if args.command == "init-db":
        success = manager.init_database()
        sys.exit(0 if success else 1)
    
    elif args.command == "start":
        # Initialize database first
        if not manager.init_database():
            sys.exit(1)
        
        success = True
        
        if args.service in ["tcp", "all"]:
            success &= manager.start_tcp_listener()
        
        if args.service in ["web", "all"]:
            success &= manager.start_web_app()
        
        if success:
            print("\n🎉 All services started successfully!")
            manager.check_service_status()
            
            if args.service == "all":
                print("\n" + "=" * 60)
                print("Services are now running. Press Ctrl+C to stop all services.")
                print("=" * 60)
                
                try:
                    # Keep the script running
                    while True:
                        time.sleep(1)
                        
                        # Check if any service died
                        for service_name, process in manager.processes.items():
                            if process.poll() is not None:
                                print(f"\n⚠️  Service {service_name} has stopped unexpectedly!")
                                manager.check_service_status()
                                break
                                
                except KeyboardInterrupt:
                    pass
        else:
            print("\n❌ Failed to start some services")
            sys.exit(1)
    
    elif args.command == "stop":
        manager.stop_all_services()
    
    elif args.command == "status":
        manager.check_service_status()
    
    elif args.command == "restart":
        manager.stop_all_services()
        time.sleep(2)
        
        if not manager.init_database():
            sys.exit(1)
        
        success = True
        if args.service in ["tcp", "all"]:
            success &= manager.start_tcp_listener()
        
        if args.service in ["web", "all"]:
            success &= manager.start_web_app()
        
        if success:
            print("\n🎉 All services restarted successfully!")
            manager.check_service_status()
        else:
            sys.exit(1)
    
    elif args.command == "test":
        success = manager.run_tests()
        sys.exit(0 if success else 1)
    
    elif args.command == "send-test-data":
        success = manager.send_test_data(args.test_records)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()