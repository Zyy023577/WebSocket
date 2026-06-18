"""WebSocket Connection Manager

Handles WebSocket connections, disconnections, and message broadcasting.
"""
import json
from typing import Dict, Set, Optional
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for the chat room"""
    
    def __init__(self):
        """Initialize connection manager"""
        # Dict of active connections: {username: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Set of connected usernames
        self.connected_users: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, username: str) -> None:
        """Accept and store a new WebSocket connection
        
        Args:
            websocket: The WebSocket connection
            username: The username of the connected client
        """
        await websocket.accept()
        self.active_connections[username] = websocket
        self.connected_users.add(username)
        print(f"✓ User '{username}' connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, username: str) -> None:
        """Close and remove a WebSocket connection
        
        Args:
            username: The username of the client to disconnect
        """
        if username in self.active_connections:
            websocket = self.active_connections.pop(username)
            self.connected_users.discard(username)
            try:
                await websocket.close()
            except:
                pass
            print(f"✗ User '{username}' disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict, exclude: Optional[str] = None) -> None:
        """Broadcast a message to all connected clients
        
        Args:
            message: The message dict to broadcast
            exclude: Optional username to exclude from broadcast
        """
        disconnected = []
        
        for username, websocket in self.active_connections.items():
            if exclude and username == exclude:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to {username}: {str(e)}")
                disconnected.append(username)
        
        # Clean up disconnected connections
        for username in disconnected:
            await self.disconnect(username)
    
    async def send_personal(self, username: str, message: dict) -> None:
        """Send a message to a specific user
        
        Args:
            username: The target username
            message: The message dict to send
        """
        if username in self.active_connections:
            try:
                await self.active_connections[username].send_json(message)
            except Exception as e:
                print(f"Error sending to {username}: {str(e)}")
                await self.disconnect(username)
    
    async def send_to_group(self, group_id: str, message: dict, 
                           users_in_group: Set[str]) -> None:
        """Send a message to users in a specific group
        
        Args:
            group_id: The group identifier
            message: The message dict to send
            users_in_group: Set of usernames in the group
        """
        for username in users_in_group:
            await self.send_personal(username, message)
    
    def get_connected_users(self) -> list:
        """Get list of all connected usernames
        
        Returns:
            List of connected usernames
        """
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def is_user_connected(self, username: str) -> bool:
        """Check if a user is currently connected
        
        Args:
            username: The username to check
            
        Returns:
            True if user is connected, False otherwise
        """
        return username in self.active_connections
    
    async def close_all_connections(self) -> None:
        """Close all active connections during shutdown"""
        for username in list(self.active_connections.keys()):
            await self.disconnect(username)
        print("All connections closed")
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics
        
        Returns:
            Dict with connection stats
        """
        return {
            "total_connections": self.get_connection_count(),
            "connected_users": self.get_connected_users(),
            "timestamp": datetime.now().isoformat()
        }
