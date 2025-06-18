"""
Conversation memory and context management.
"""

import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, max_history: int = 10, save_path: Optional[str] = None):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of exchanges to keep in memory
            save_path: Optional path to save conversation history
        """
        self.max_history = max_history
        self.save_path = save_path
        self.conversations: List[Dict] = []
        self.current_session: List[Dict] = []
        
        if save_path:
            self._load_history()
    
    def add_exchange(self, user_input: str, assistant_response: str) -> None:
        """
        Add a user-assistant exchange to memory.
        
        Args:
            user_input: User's message
            assistant_response: Assistant's response
        """
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'assistant': assistant_response
        }
        
        self.current_session.append(exchange)
        
        # Keep only the most recent exchanges
        if len(self.current_session) > self.max_history:
            self.current_session = self.current_session[-self.max_history:]
    
    def get_context(self, num_exchanges: int = 3) -> str:
        """
        Get conversation context for the model.
        
        Args:
            num_exchanges: Number of recent exchanges to include
            
        Returns:
            Formatted context string
        """
        if not self.current_session:
            return ""
        
        # Get the most recent exchanges
        recent_exchanges = self.current_session[-num_exchanges:]
        
        context_parts = []
        for exchange in recent_exchanges:
            context_parts.append(f"User: {exchange['user']}")
            context_parts.append(f"Assistant: {exchange['assistant']}")
        
        return "\n".join(context_parts)
    
    def get_full_history(self) -> List[Dict]:
        """
        Get the full conversation history.
        
        Returns:
            List of all exchanges in current session
        """
        return self.current_session.copy()
    
    def clear_session(self) -> None:
        """Clear the current conversation session."""
        if self.current_session:
            # Save current session before clearing
            session_summary = {
                'timestamp': datetime.now().isoformat(),
                'exchanges': len(self.current_session),
                'first_message': self.current_session[0]['user'][:100] + "..." if len(self.current_session[0]['user']) > 100 else self.current_session[0]['user']
            }
            self.conversations.append(session_summary)
            
            self.current_session = []
    
    def save_conversation(self, file_path: Optional[str] = None) -> None:
        """
        Save conversation to file.
        
        Args:
            file_path: Optional custom file path
        """
        if not self.current_session:
            return
        
        save_path = file_path or self.save_path
        if not save_path:
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"conversation_{timestamp}.json"
        
        conversation_data = {
            'timestamp': datetime.now().isoformat(),
            'exchanges': self.current_session,
            'summary': {
                'total_exchanges': len(self.current_session),
                'session_duration': self._calculate_session_duration()
            }
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save conversation: {e}")
    
    def load_conversation(self, file_path: str) -> bool:
        """
        Load conversation from file.
        
        Args:
            file_path: Path to conversation file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'exchanges' in data:
                self.current_session = data['exchanges']
                return True
            return False
        except Exception as e:
            print(f"Failed to load conversation: {e}")
            return False
    
    def _load_history(self) -> None:
        """Load conversation history from save path."""
        if not self.save_path or not Path(self.save_path).exists():
            return
        
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.conversations = data
            elif isinstance(data, dict) and 'conversations' in data:
                self.conversations = data['conversations']
        except Exception as e:
            print(f"Failed to load conversation history: {e}")
    
    def _save_history(self) -> None:
        """Save conversation history to file."""
        if not self.save_path:
            return
        
        try:
            data = {
                'conversations': self.conversations,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save conversation history: {e}")
    
    def _calculate_session_duration(self) -> Optional[str]:
        """Calculate the duration of the current session."""
        if len(self.current_session) < 2:
            return None
        
        try:
            start_time = datetime.fromisoformat(self.current_session[0]['timestamp'])
            end_time = datetime.fromisoformat(self.current_session[-1]['timestamp'])
            duration = end_time - start_time
            
            # Format duration
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except Exception:
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get conversation statistics.
        
        Returns:
            Dictionary with conversation statistics
        """
        total_exchanges = len(self.current_session)
        total_user_chars = sum(len(exchange['user']) for exchange in self.current_session)
        total_assistant_chars = sum(len(exchange['assistant']) for exchange in self.current_session)
        
        return {
            'total_exchanges': total_exchanges,
            'total_user_chars': total_user_chars,
            'total_assistant_chars': total_assistant_chars,
            'average_user_length': total_user_chars / max(total_exchanges, 1),
            'average_assistant_length': total_assistant_chars / max(total_exchanges, 1),
            'session_duration': self._calculate_session_duration()
        }
    
    def search_history(self, query: str) -> List[Dict]:
        """
        Search through conversation history.
        
        Args:
            query: Search query
            
        Returns:
            List of matching exchanges
        """
        if not query.strip():
            return []
        
        query_lower = query.lower()
        matches = []
        
        for exchange in self.current_session:
            if (query_lower in exchange['user'].lower() or 
                query_lower in exchange['assistant'].lower()):
                matches.append(exchange)
        
        return matches 