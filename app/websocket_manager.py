#!/usr/bin/env python3
"""
WebSocket Manager for Real-time Updates.

This module handles WebSocket connections and broadcasts real-time updates
to connected clients when new SMDR records are received.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Set, Dict, Any, Optional
import websockets
from websockets.server import WebSocketServerProtocol
from threading import Thread, Lock
import queue
import time

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time updates."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.client_subscriptions: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        self.message_queue = queue.Queue()
        self.running = False
        self.server = None
        self.clients_lock = Lock()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'start_time': None
        }
    
    async def register_client(self, websocket: WebSocketServerProtocol, path: str):
        """Register a new WebSocket client."""
        with self.clients_lock:
            self.clients.add(websocket)
            self.client_subscriptions[websocket] = {
                'subscribed_at': datetime.now(),
                'filters': {},
                'last_ping': datetime.now()
            }
            self.stats['total_connections'] += 1
            self.stats['active_connections'] = len(self.clients)
        
        logger.info(f"Client connected from {websocket.remote_address}. Total clients: {len(self.clients)}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            'type': 'welcome',
            'message': 'Connected to Telemetry Sleuth WebSocket',
            'timestamp': datetime.now().isoformat(),
            'client_id': id(websocket)
        })
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket client."""
        with self.clients_lock:
            self.clients.discard(websocket)
            self.client_subscriptions.pop(websocket, None)
            self.stats['active_connections'] = len(self.clients)
        
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                await self.handle_subscription(websocket, data)
            elif message_type == 'unsubscribe':
                await self.handle_unsubscription(websocket, data)
            elif message_type == 'ping':
                await self.handle_ping(websocket, data)
            elif message_type == 'get_stats':
                await self.send_stats(websocket)
            else:
                await self.send_to_client(websocket, {
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
        
        except json.JSONDecodeError:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Invalid JSON message'
            })
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Internal server error'
            })
    
    async def handle_subscription(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle client subscription requests."""
        filters = data.get('filters', {})
        
        with self.clients_lock:
            if websocket in self.client_subscriptions:
                self.client_subscriptions[websocket]['filters'] = filters
        
        await self.send_to_client(websocket, {
            'type': 'subscription_confirmed',
            'filters': filters,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Client {id(websocket)} subscribed with filters: {filters}")
    
    async def handle_unsubscription(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle client unsubscription requests."""
        with self.clients_lock:
            if websocket in self.client_subscriptions:
                self.client_subscriptions[websocket]['filters'] = {}
        
        await self.send_to_client(websocket, {
            'type': 'unsubscription_confirmed',
            'timestamp': datetime.now().isoformat()
        })
    
    async def handle_ping(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle ping messages from clients."""
        with self.clients_lock:
            if websocket in self.client_subscriptions:
                self.client_subscriptions[websocket]['last_ping'] = datetime.now()
        
        await self.send_to_client(websocket, {
            'type': 'pong',
            'timestamp': datetime.now().isoformat(),
            'client_timestamp': data.get('timestamp')
        })
    
    async def send_stats(self, websocket: WebSocketServerProtocol):
        """Send server statistics to client."""
        current_stats = self.stats.copy()
        current_stats['uptime'] = (
            (datetime.now() - self.stats['start_time']).total_seconds()
            if self.stats['start_time'] else 0
        )
        
        await self.send_to_client(websocket, {
            'type': 'stats',
            'data': current_stats,
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Send a message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
            self.stats['messages_sent'] += 1
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")
            await self.unregister_client(websocket)
    
    async def broadcast_message(self, message: Dict[str, Any], filters: Optional[Dict[str, Any]] = None):
        """Broadcast a message to all connected clients (with optional filtering)."""
        if not self.clients:
            return
        
        disconnected_clients = set()
        
        for websocket in self.clients.copy():
            try:
                # Check if client matches filters
                if filters and not self.client_matches_filters(websocket, filters):
                    continue
                
                await self.send_to_client(websocket, message)
            
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected_clients:
            await self.unregister_client(websocket)
    
    def client_matches_filters(self, websocket: WebSocketServerProtocol, message_filters: Dict[str, Any]) -> bool:
        """Check if a client's subscription filters match the message filters."""
        with self.clients_lock:
            client_filters = self.client_subscriptions.get(websocket, {}).get('filters', {})
        
        if not client_filters:
            return True  # No filters means receive all messages
        
        # Check each filter criterion
        for key, value in client_filters.items():
            if key in message_filters and message_filters[key] != value:
                return False
        
        return True
    
    async def websocket_handler(self, websocket: WebSocketServerProtocol, path: str):
        """Main WebSocket connection handler."""
        await self.register_client(websocket, path)
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            await self.unregister_client(websocket)
    
    def start_server(self):
        """Start the WebSocket server."""
        if self.running:
            logger.warning("WebSocket server is already running")
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Start the server in a separate thread
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            start_server = websockets.serve(
                self.websocket_handler,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            self.server = loop.run_until_complete(start_server)
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                logger.info("WebSocket server stopped by user")
            finally:
                self.server.close()
                loop.run_until_complete(self.server.wait_closed())
                loop.close()
        
        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Start message processor
        self.processor_thread = Thread(target=self.process_messages, daemon=True)
        self.processor_thread.start()
    
    def stop_server(self):
        """Stop the WebSocket server."""
        if not self.running:
            return
        
        self.running = False
        
        if self.server:
            self.server.close()
        
        logger.info("WebSocket server stopped")
    
    def process_messages(self):
        """Process queued messages for broadcasting."""
        while self.running:
            try:
                # Get message from queue with timeout
                message = self.message_queue.get(timeout=1.0)
                
                # Create event loop for this thread if it doesn't exist
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Broadcast the message
                loop.run_until_complete(self.broadcast_message(message))
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def queue_message(self, message: Dict[str, Any]):
        """Queue a message for broadcasting."""
        try:
            self.message_queue.put_nowait(message)
        except queue.Full:
            logger.warning("Message queue is full, dropping message")
    
    def broadcast_new_record(self, record_data: Dict[str, Any]):
        """Broadcast a new call record to connected clients."""
        message = {
            'type': 'new_record',
            'data': record_data,
            'timestamp': datetime.now().isoformat()
        }
        self.queue_message(message)
    
    def broadcast_stats_update(self, stats_data: Dict[str, Any]):
        """Broadcast updated statistics to connected clients."""
        message = {
            'type': 'stats_update',
            'data': stats_data,
            'timestamp': datetime.now().isoformat()
        }
        self.queue_message(message)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current server status."""
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'stats': self.stats.copy()
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


def start_websocket_server(host: str = '0.0.0.0', port: int = 8765):
    """Start the WebSocket server."""
    global websocket_manager
    websocket_manager.host = host
    websocket_manager.port = port
    websocket_manager.start_server()
    return websocket_manager


def stop_websocket_server():
    """Stop the WebSocket server."""
    global websocket_manager
    websocket_manager.stop_server()


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    return websocket_manager