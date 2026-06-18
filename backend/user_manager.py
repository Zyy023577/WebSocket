"""User Session Manager

Manages user sessions, tracking online users and their metadata.
"""
from typing import Dict, Optional, List
from datetime import datetime


class UserManager:
    """Manages user sessions in the chat room"""
    
    def __init__(self):
        """Initialize user manager"""
        # Dict of user info: {username: user_data}
        self.users: Dict[str, dict] = {}
    
    def add_user(self, username: str, user_data: Optional[dict] = None) -> bool:
        """Add a new user to the session
        
        Args:
            username: The username
            user_data: Optional user metadata
            
        Returns:
            True if user added successfully, False if already exists
        """
        if username in self.users:
            return False
        
        self.users[username] = {
            "username": username,
            "login_time": datetime.now().isoformat(),
            "messages_count": 0,
            "status": "online",
            **(user_data or {})
        }
        print(f"📝 User '{username}' added to session")
        return True
    
    def remove_user(self, username: str) -> bool:
        """Remove a user from the session
        
        Args:
            username: The username to remove
            
        Returns:
            True if user was removed, False if not found
        """
        if username in self.users:
            del self.users[username]
            print(f"🗑️ User '{username}' removed from session")
            return True
        return False
    
    def get_user(self, username: str) -> Optional[dict]:
        """Get user information
        
        Args:
            username: The username to retrieve
            
        Returns:
            User data dict if found, None otherwise
        """
        return self.users.get(username)
    
    def get_all_users(self) -> List[str]:
        """Get list of all online users
        
        Returns:
            List of usernames
        """
        return list(self.users.keys())
    
    def is_user_online(self, username: str) -> bool:
        """Check if a user is online
        
        Args:
            username: The username to check
            
        Returns:
            True if user is online, False otherwise
        """
        return username in self.users
    
    def increment_message_count(self, username: str) -> None:
        """Increment message count for a user
        
        Args:
            username: The username
        """
        if username in self.users:
            self.users[username]["messages_count"] += 1
    
    def update_user_status(self, username: str, status: str) -> bool:
        """Update user status
        
        Args:
            username: The username
            status: The new status (e.g., 'online', 'away', 'busy')
            
        Returns:
            True if status updated, False if user not found
        """
        if username in self.users:
            self.users[username]["status"] = status
            self.users[username]["status_update_time"] = datetime.now().isoformat()
            return True
        return False
    
    def get_user_count(self) -> int:
        """Get total number of online users
        
        Returns:
            Number of online users
        """
        return len(self.users)
    
    def get_session_stats(self) -> dict:
        """Get session statistics
        
        Returns:
            Dict with session stats
        """
        total_messages = sum(u.get("messages_count", 0) for u in self.users.values())
        
        return {
            "total_users": self.get_user_count(),
            "online_users": self.get_all_users(),
            "total_messages": total_messages,
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_all_users(self) -> None:
        """Clear all user sessions (for testing/cleanup)"""
        self.users.clear()
        print("🧹 All user sessions cleared")
