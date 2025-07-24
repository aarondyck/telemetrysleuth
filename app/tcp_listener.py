"""
TCP Listener Service for Telemetry Sleuth SMDR Data Capture.

This module implements a robust TCP server that listens for incoming SMDR data
from Avaya IP Office systems. It handles byte streams, decodes them to strings,
and splits records based on the \r\n terminator.
"""

import socket
import socketserver
import threading
import logging
import sys
from datetime import datetime
from typing import Optional

from .config import Config
from .models import init_database, get_db_context, CallRecord
from .parser import SMDRParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('smdr_listener.log')
    ]
)
logger = logging.getLogger(__name__)


class SMDRHandler(socketserver.StreamRequestHandler):
    """
    Handler for individual SMDR client connections.
    
    Processes incoming byte streams, decodes them, and splits records
    based on \r\n terminators.
    """
    
    def __init__(self, request, client_address, server):
        self.parser = SMDRParser()
        super().__init__(request, client_address, server)
    
    def handle(self):
        """Handle incoming SMDR data from a client connection."""
        client_ip = self.client_address[0]
        client_port = self.client_address[1]
        
        logger.info(f"New SMDR connection from {client_ip}:{client_port}")
        
        # Buffer for incomplete records
        buffer = ""
        
        try:
            while True:
                # Read data from the client
                data = self.request.recv(4096)
                
                if not data:
                    logger.info(f"Client {client_ip}:{client_port} disconnected")
                    break
                
                # Decode bytes to string
                try:
                    decoded_data = data.decode('utf-8', errors='replace')
                except UnicodeDecodeError as e:
                    logger.error(f"Unicode decode error from {client_ip}: {e}")
                    continue
                
                # Add to buffer
                buffer += decoded_data
                
                # Process complete records (terminated by \r\n)
                while '\r\n' in buffer:
                    # Find the first complete record
                    record_end = buffer.find('\r\n')
                    raw_record = buffer[:record_end]
                    
                    # Remove processed record from buffer
                    buffer = buffer[record_end + 2:]
                    
                    # Skip empty records
                    if not raw_record.strip():
                        continue
                    
                    # Process the SMDR record
                    self.process_smdr_record(raw_record, client_ip)
                    
        except ConnectionResetError:
            logger.info(f"Connection reset by client {client_ip}:{client_port}")
        except Exception as e:
            logger.error(f"Error handling client {client_ip}:{client_port}: {e}")
        finally:
            logger.info(f"Closing connection to {client_ip}:{client_port}")
    
    def process_smdr_record(self, raw_record: str, client_ip: str):
        """
        Process a single SMDR record.
        
        Args:
            raw_record: The raw SMDR record string
            client_ip: IP address of the client that sent the record
        """
        try:
            logger.debug(f"Processing SMDR record from {client_ip}: {raw_record}")
            
            # Parse the SMDR record
            call_record = self.parser.parse_record(raw_record)
            
            if call_record:
                # Save to database
                with get_db_context() as session:
                    session.add(call_record)
                    
                logger.info(f"Saved SMDR record - Call ID: {call_record.call_id}, "
                           f"Caller: {call_record.caller}, "
                           f"Called: {call_record.called_number}")
            else:
                logger.warning(f"Failed to parse SMDR record from {client_ip}: {raw_record}")
                
        except Exception as e:
            logger.error(f"Error processing SMDR record from {client_ip}: {e}")
            logger.error(f"Raw record: {raw_record}")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Threaded TCP Server for handling multiple SMDR connections simultaneously.
    """
    allow_reuse_address = True
    daemon_threads = True
    
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        logger.info(f"SMDR TCP Server initialized on {server_address[0]}:{server_address[1]}")


class SMDRTCPListener:
    """
    Main SMDR TCP Listener service.
    
    Manages the TCP server lifecycle and handles graceful shutdown.
    """
    
    def __init__(self, host: str = None, port: int = None):
        self.config = Config()
        self.host = host or self.config.TCP_HOST
        self.port = port or self.config.TCP_PORT
        self.server: Optional[ThreadedTCPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Initialize database
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def start(self):
        """Start the SMDR TCP listener service."""
        try:
            # Create and start the server
            self.server = ThreadedTCPServer((self.host, self.port), SMDRHandler)
            
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            logger.info(f"SMDR TCP Listener started on {self.host}:{self.port}")
            logger.info("Waiting for SMDR connections...")
            
        except Exception as e:
            logger.error(f"Failed to start SMDR TCP Listener: {e}")
            raise
    
    def stop(self):
        """Stop the SMDR TCP listener service."""
        if self.server and self.running:
            logger.info("Stopping SMDR TCP Listener...")
            self.server.shutdown()
            self.server.server_close()
            
            if self.server_thread:
                self.server_thread.join(timeout=5)
            
            self.running = False
            logger.info("SMDR TCP Listener stopped")
    
    def run_forever(self):
        """Run the service until interrupted."""
        try:
            self.start()
            
            # Keep the main thread alive
            while self.running:
                threading.Event().wait(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop()


def main():
    """Main entry point for the SMDR TCP Listener."""
    try:
        # Create and run the listener
        listener = SMDRTCPListener()
        listener.run_forever()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()