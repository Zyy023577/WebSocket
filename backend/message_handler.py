"""Message Handler and Storage

Handles message creation, storage, and retrieval.
"""
from typing import List, Optional, Dict
from datetime import datetime
from collections import deque
import json


class MessageHandler:
    """Handles message creation and storage"""
    
    def __init__(self, max_stored_messages: int = 500):
        """Initialize message handler
        
        Args:
            max_stored_messages: Maximum messages to keep in memory
        """
        # Use deque for efficient append and popleft
        self.messages: deque = deque(maxlen=max_stored_messages)
        self.max_stored_messages = max_stored_messages
    
    def create_message(self, username: str, content: str, msg_type: str = "message",
                      target_user: Optional[str] = None, group_id: Optional[str] = None) -> dict:
        """Create a message object
        
        Args:
            username: The sender username
            content: The message content
            msg_type: Type of message (message, private_message, login, logout, etc.)
            target_user: For private messages, the target user
            group_id: For group messages, the group ID
            
        Returns:
            Message dict
        """
        message = {
            "type": msg_type,
            "username": username,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "message_id": self._generate_message_id()
        }
        
        if target_user:
            message["target_user"] = target_user
        
        if group_id:
            message["group_id"] = group_id
        
        # Store regular messages and system messages
        if msg_type in ["message", "private_message", "login", "logout"]:
            self.messages.append(message)
        
        return message
    
    def get_recent_messages(self, limit: int = 50) -> List[dict]:
        """Get recent messages
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of recent messages
        """
        # Convert deque to list and get the last 'limit' messages
        all_messages = list(self.messages)
        return all_messages[-limit:]
    
    def get_messages_for_user(self, username: str, limit: int = 50) -> List[dict]:
        """Get recent messages involving a specific user (sent by or to them)
        
        Args:
            username: The username to filter for
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        user_messages = [
            msg for msg in self.messages
            if msg.get("username") == username or msg.get("target_user") == username
        ]
        return user_messages[-limit:]
    
    def get_group_messages(self, group_id: str, limit: int = 50) -> List[dict]:
        """Get messages for a specific group
        
        Args:
            group_id: The group ID to filter for
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of group messages
        """
        group_messages = [
            msg for msg in self.messages
            if msg.get("group_id") == group_id
        ]
        return group_messages[-limit:]
    
    def get_private_messages(self, user1: str, user2: str, limit: int = 50) -> List[dict]:
        """Get private messages between two users
        
        Args:
            user1: First username
            user2: Second username
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of private messages between the two users
        """
        private_messages = [
            msg for msg in self.messages
            if msg.get("type") == "private_message" and (
                (msg.get("username") == user1 and msg.get("target_user") == user2) or
                (msg.get("username") == user2 and msg.get("target_user") == user1)
            )
        ]
        return private_messages[-limit:]
    
    def search_messages(self, keyword: str, limit: int = 50) -> List[dict]:
        """Search messages by keyword
        
        Args:
            keyword: The search keyword
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        keyword_lower = keyword.lower()
        results = [
            msg for msg in self.messages
            if keyword_lower in msg.get("content", "").lower()
        ]
        return results[-limit:]
    
    def get_message_stats(self) -> dict:
        """Get message statistics
        
        Returns:
            Dict with message stats
        """
        total_messages = len(self.messages)
        message_types = {}
        
        for msg in self.messages:
            msg_type = msg.get("type", "unknown")
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            "total_messages": total_messages,
            "max_capacity": self.max_stored_messages,
            "usage_percent": (total_messages / self.max_stored_messages) * 100,
            "message_types": message_types,
            "timestamp": datetime.now().isoformat()
        }
    
    def export_messages(self, format: str = "json") -> str:
        """Export all stored messages
        
        Args:
            format: Export format ('json', 'csv')
            
        Returns:
            Exported messages as string
        """
        if format == "json":
            return json.dumps(list(self.messages), indent=2)
        elif format == "csv":
            # Simple CSV export
            lines = ["timestamp,username,type,content"]
            for msg in self.messages:
                lines.append(
                    f"{msg.get('timestamp')},"
                    f"{msg.get('username')},"
                    f"{msg.get('type')},"
                    f"{msg.get('content')}"
                )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_messages(self) -> None:
        """Clear all stored messages (for testing)"""
        self.messages.clear()
        print("🗑️ All messages cleared")
    
    @staticmethod
    def _generate_message_id() -> str:
        """Generate a unique message ID
        
        Returns:
            Unique message ID
        """
        import uuid
        return str(uuid.uuid4())[:8]