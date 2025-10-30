#!/usr/bin/env python3
"""
WebSocket Server for Real-Time Collaborative Code Editing
Supports bidirectional communication, user presence, and cursor tracking
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Set, Dict
import signal
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
CONNECTED_CLIENTS: Set = set()
USER_INFO: Dict[str, dict] = {}  # websocket id -> user info

# Dual-mode document state
# Web-Edit state (legacy for CSS/JS/HTML quadrants)
WEBEDIT_STATE = {
    'css': '',
    'javascript': '',
    'html': ''
}

# File-based state for Code Editor
FILE_STATE: Dict[str, str] = {}  # file_path -> content
FILE_USERS: Dict[str, Set[str]] = {}  # file_path -> set of user_ids who have it open
USER_FILES: Dict[str, Set[str]] = {}  # user_id -> set of file_paths they have open

USER_CURSORS: Dict[str, dict] = {}  # user_id -> cursor position


class CollaborationServer:
    """WebSocket server for real-time collaborative editing"""
    
    def __init__(self, host='0.0.0.0', port=8001):
        self.host = host
        self.port = port
        self.server = None
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        CONNECTED_CLIENTS.add(websocket)
        client_id = id(websocket)
        
        # Generate user info
        user_id = f"user_{len(USER_INFO) + 1}"
        USER_INFO[client_id] = {
            'user_id': user_id,
            'connected_at': datetime.now().isoformat(),
            'remote_address': websocket.remote_address[0] if websocket.remote_address else 'unknown'
        }
        
        logger.info(f"Client connected: {user_id} from {USER_INFO[client_id]['remote_address']}")
        logger.info(f"Total connected clients: {len(CONNECTED_CLIENTS)}")
        
        # Initialize user's file tracking
        USER_FILES[user_id] = set()
        
        # Send initial state to new client
        await websocket.send(json.dumps({
            'type': 'init',
            'user_id': user_id,
            'webedit': WEBEDIT_STATE,  # Web-Edit quadrants
            'files': FILE_STATE,  # All open files
            'users': list(USER_INFO.values()),
            'cursors': USER_CURSORS,
            'file_users': {path: list(users) for path, users in FILE_USERS.items()}
        }))
        
        # Notify all other clients about new user
        await self.broadcast({
            'type': 'user_joined',
            'user': USER_INFO[client_id],
            'total_users': len(CONNECTED_CLIENTS)
        }, exclude=websocket)
        
    async def unregister_client(self, websocket):
        """Unregister a disconnected client"""
        CONNECTED_CLIENTS.discard(websocket)
        client_id = id(websocket)
        
        if client_id in USER_INFO:
            user_info = USER_INFO.pop(client_id)
            user_id = user_info['user_id']
            
            # Remove user's cursor
            USER_CURSORS.pop(user_id, None)
            
            # Clean up file tracking
            if user_id in USER_FILES:
                files = USER_FILES.pop(user_id)
                for file_path in files:
                    if file_path in FILE_USERS:
                        FILE_USERS[file_path].discard(user_id)
                        if not FILE_USERS[file_path]:
                            # No one has this file open anymore
                            FILE_USERS.pop(file_path, None)
            
            logger.info(f"Client disconnected: {user_id}")
            logger.info(f"Total connected clients: {len(CONNECTED_CLIENTS)}")
            
            # Notify remaining clients
            await self.broadcast({
                'type': 'user_left',
                'user_id': user_id,
                'total_users': len(CONNECTED_CLIENTS)
            })
    
    async def broadcast(self, message: dict, exclude=None):
        """Broadcast message to all connected clients except excluded one"""
        if not CONNECTED_CLIENTS:
            return
            
        message_str = json.dumps(message)
        
        # Send to all clients (exceptions are handled automatically)
        tasks = []
        for client in CONNECTED_CLIENTS:
            if client != exclude:
                tasks.append(client.send(message_str))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def handle_message(self, websocket, message_str: str):
        """Handle incoming message from client"""
        try:
            message = json.loads(message_str)
            message_type = message.get('type')
            client_id = id(websocket)
            user_id = USER_INFO.get(client_id, {}).get('user_id', 'unknown')
            
            if message_type == 'code_update':
                # Update Web-Edit quadrant state (CSS/JS/HTML)
                field = message.get('field')  # 'css', 'javascript', or 'html'
                value = message.get('value', '')
                
                if field in WEBEDIT_STATE:
                    WEBEDIT_STATE[field] = value
                    
                    # Broadcast to all other clients
                    await self.broadcast({
                        'type': 'code_update',
                        'field': field,
                        'value': value,
                        'user_id': user_id,
                        'timestamp': datetime.now().isoformat()
                    }, exclude=websocket)
                    
                    logger.debug(f"Code update from {user_id} in {field}: {len(value)} chars")
            
            elif message_type == 'file_open':
                # User opened a file in Code Editor
                file_path = message.get('file_path')
                initial_content = message.get('content', '')
                
                if file_path:
                    # Track this user as having the file open
                    if file_path not in FILE_USERS:
                        FILE_USERS[file_path] = set()
                    FILE_USERS[file_path].add(user_id)
                    USER_FILES[user_id].add(file_path)
                    
                    # Initialize file state if not exists
                    if file_path not in FILE_STATE:
                        FILE_STATE[file_path] = initial_content
                    
                    # Notify other users that this user opened the file
                    await self.broadcast({
                        'type': 'file_opened',
                        'file_path': file_path,
                        'user_id': user_id,
                        'users_editing': list(FILE_USERS[file_path]),
                        'timestamp': datetime.now().isoformat()
                    }, exclude=websocket)
                    
                    logger.info(f"{user_id} opened file: {file_path}")
            
            elif message_type == 'file_close':
                # User closed a file
                file_path = message.get('file_path')
                
                if file_path and user_id in USER_FILES:
                    USER_FILES[user_id].discard(file_path)
                    if file_path in FILE_USERS:
                        FILE_USERS[file_path].discard(user_id)
                        
                        # Notify other users
                        await self.broadcast({
                            'type': 'file_closed',
                            'file_path': file_path,
                            'user_id': user_id,
                            'users_editing': list(FILE_USERS.get(file_path, [])),
                            'timestamp': datetime.now().isoformat()
                        }, exclude=websocket)
                    
                    logger.info(f"{user_id} closed file: {file_path}")
            
            elif message_type == 'file_update':
                # User edited a file
                file_path = message.get('file_path')
                content = message.get('content', '')
                
                if file_path:
                    # Update file state
                    FILE_STATE[file_path] = content
                    
                    # Broadcast to other users who have this file open
                    broadcast_msg = {
                        'type': 'file_update',
                        'file_path': file_path,
                        'content': content,
                        'user_id': user_id,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Send to all clients except sender
                    await self.broadcast(broadcast_msg, exclude=websocket)
                    
                    logger.debug(f"File update from {user_id} in {file_path}: {len(content)} chars")
            
            elif message_type == 'cursor_update':
                # Update cursor position
                cursor_data = {
                    'field': message.get('field'),
                    'line': message.get('line'),
                    'column': message.get('column'),
                    'timestamp': datetime.now().isoformat()
                }
                USER_CURSORS[user_id] = cursor_data
                
                # Broadcast to all other clients
                await self.broadcast({
                    'type': 'cursor_update',
                    'user_id': user_id,
                    'cursor': cursor_data
                }, exclude=websocket)
            
            elif message_type == 'chat_message':
                # Handle chat messages
                chat_message = message.get('message', '')
                
                await self.broadcast({
                    'type': 'chat_message',
                    'user_id': user_id,
                    'message': chat_message,
                    'timestamp': datetime.now().isoformat()
                }, exclude=websocket)
                
                logger.info(f"Chat from {user_id}: {chat_message}")
            
            elif message_type == 'ping':
                # Respond to ping with pong
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message_str}")
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def handler(self, websocket):
        """Main WebSocket connection handler"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Connection closed normally")
        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)
        finally:
            await self.unregister_client(websocket)
    
    async def start(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        self.server = await websockets.serve(
            self.handler,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        logger.info(f"✓ WebSocket server running on ws://{self.host}:{self.port}")
        logger.info("Ready for collaborative editing connections...")
        
    async def stop(self):
        """Stop the WebSocket server"""
        if self.server:
            logger.info("Shutting down WebSocket server...")
            self.server.close()
            await self.server.wait_closed()
            logger.info("Server stopped")


async def main():
    """Main entry point"""
    server = CollaborationServer(host='0.0.0.0', port=8001)
    
    # Handle graceful shutdown
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    await server.start()
    
    # Keep server running
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
