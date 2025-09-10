"""
Dexter Simple v2 - Brain System
Simplified but functional memory system for local setup
"""

import json
import sqlite3
import time
from pathlib import Path
from collections import deque

class BrainManager:
    """Simplified brain manager for local setup"""
    
    def __init__(self, config_path="dexter_simple_config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        
        # Create data directory
        Path("./data").mkdir(exist_ok=True)
        
        # Simple in-memory storage
        self.short_term = deque(maxlen=100)
        
        # Initialize SQLite for long-term storage
        self.db = sqlite3.connect("./data/brain.db", check_same_thread=False)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                user_input TEXT,
                ai_response TEXT,
                ai_name TEXT
            )
        """)
        self.db.commit()
    
    def get_context(self, user_input=""):
        """Get context for conversation"""
        if len(self.short_term) == 0:
            return "No previous conversation context."
        
        # Return last few interactions
        recent = list(self.short_term)[-3:]
        context_parts = []
        for item in recent:
            context_parts.append(f"User: {item['user']}")
            context_parts.append(f"AI: {item['ai']}")
        
        return "\n".join(context_parts)
    
    def process_conversation(self, user_input, ai_response, ai_name="dexter"):
        """Store conversation"""
        timestamp = time.time()
        
        # Add to short-term memory
        self.short_term.append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': timestamp
        })
        
        # Add to long-term storage
        try:
            self.db.execute(
                "INSERT INTO conversations (timestamp, user_input, ai_response, ai_name) VALUES (?, ?, ?, ?)",
                (timestamp, user_input, ai_response, ai_name)
            )
            self.db.commit()
        except:
            pass  # Ignore database errors for now