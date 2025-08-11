"""State Manager for AI Job Agent Recovery System

Provides SQLite-based state persistence and recovery functionality.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path


class StateManager:
    """Manages application state with SQLite persistence."""
    
    def __init__(self, db_path: str = "ai_job_agent_state.db"):
        """Initialize state manager with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS application_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_search_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_id TEXT UNIQUE NOT NULL,
                    query TEXT NOT NULL,
                    results TEXT,
                    status TEXT DEFAULT 'pending',
                    error_count INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recovery_checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id TEXT UNIQUE NOT NULL,
                    operation TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    def save_state(self, key: str, value: Any) -> None:
        """Save application state to database.
        
        Args:
            key: State key identifier
            value: State value to save
        """
        data_type = type(value).__name__
        
        # Serialize complex objects to JSON
        if isinstance(value, (dict, list, tuple)):
            serialized_value = json.dumps(value)
            data_type = 'json'
        else:
            serialized_value = str(value)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO application_state 
                    (key, value, data_type, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (key, serialized_value, data_type))
                conn.commit()
                self.logger.debug(f"Saved state for key: {key}")
        except Exception as e:
            self.logger.error(f"Failed to save state for key {key}: {e}")
            raise
    
    def load_state(self, key: str, default: Any = None) -> Any:
        """Load application state from database.
        
        Args:
            key: State key identifier
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value, data_type FROM application_state WHERE key = ?",
                    (key,)
                )
                result = cursor.fetchone()
                
                if result is None:
                    return default
                
                value, data_type = result
                
                # Deserialize based on data type
                if data_type == 'json':
                    return json.loads(value)
                elif data_type == 'int':
                    return int(value)
                elif data_type == 'float':
                    return float(value)
                elif data_type == 'bool':
                    return value.lower() == 'true'
                else:
                    return value
                    
        except Exception as e:
            self.logger.error(f"Failed to load state for key {key}: {e}")
            return default
    
    def delete_state(self, key: str) -> bool:
        """Delete state entry from database.
        
        Args:
            key: State key to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM application_state WHERE key = ?",
                    (key,)
                )
                conn.commit()
                deleted = cursor.rowcount > 0
                if deleted:
                    self.logger.debug(f"Deleted state for key: {key}")
                return deleted
        except Exception as e:
            self.logger.error(f"Failed to delete state for key {key}: {e}")
            return False
    
    def save_job_search_state(self, search_id: str, query: str, 
                            results: Optional[List[Dict]] = None,
                            status: str = 'pending',
                            error_count: int = 0,
                            last_error: Optional[str] = None) -> None:
        """Save job search specific state.
        
        Args:
            search_id: Unique identifier for the search
            query: Search query
            results: Search results if available
            status: Current status of the search
            error_count: Number of errors encountered
            last_error: Last error message if any
        """
        results_json = json.dumps(results) if results else None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO job_search_state 
                    (search_id, query, results, status, error_count, last_error, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (search_id, query, results_json, status, error_count, last_error))
                conn.commit()
                self.logger.debug(f"Saved job search state for: {search_id}")
        except Exception as e:
            self.logger.error(f"Failed to save job search state: {e}")
            raise
    
    def load_job_search_state(self, search_id: str) -> Optional[Dict]:
        """Load job search state by ID.
        
        Args:
            search_id: Search identifier
            
        Returns:
            Job search state dict or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM job_search_state WHERE search_id = ?",
                    (search_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    state = dict(result)
                    if state['results']:
                        state['results'] = json.loads(state['results'])
                    return state
                return None
        except Exception as e:
            self.logger.error(f"Failed to load job search state: {e}")
            return None
    
    def create_checkpoint(self, checkpoint_id: str, operation: str, 
                         state_data: Dict) -> None:
        """Create a recovery checkpoint.
        
        Args:
            checkpoint_id: Unique checkpoint identifier
            operation: Operation being performed
            state_data: Current state data
        """
        state_json = json.dumps(state_data)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO recovery_checkpoints 
                    (checkpoint_id, operation, state_data)
                    VALUES (?, ?, ?)
                """, (checkpoint_id, operation, state_json))
                conn.commit()
                self.logger.info(f"Created checkpoint: {checkpoint_id}")
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint: {e}")
            raise
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Load recovery checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Returns:
            Checkpoint data or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT operation, state_data FROM recovery_checkpoints WHERE checkpoint_id = ?",
                    (checkpoint_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    operation, state_data = result
                    return {
                        'operation': operation,
                        'state_data': json.loads(state_data)
                    }
                return None
        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get all application states.
        
        Returns:
            Dictionary of all states
        """
        states = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT key, value, data_type FROM application_state"
                )
                
                for key, value, data_type in cursor.fetchall():
                    if data_type == 'json':
                        states[key] = json.loads(value)
                    elif data_type == 'int':
                        states[key] = int(value)
                    elif data_type == 'float':
                        states[key] = float(value)
                    elif data_type == 'bool':
                        states[key] = value.lower() == 'true'
                    else:
                        states[key] = value
        except Exception as e:
            self.logger.error(f"Failed to get all states: {e}")
        
        return states
    
    def clear_all_states(self) -> bool:
        """Clear all application states.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM application_state")
                conn.execute("DELETE FROM job_search_state")
                conn.execute("DELETE FROM recovery_checkpoints")
                conn.commit()
                self.logger.info("Cleared all states")
                return True
        except Exception as e:
            self.logger.error(f"Failed to clear states: {e}")
            return False
    
    def close(self) -> None:
        """Close database connection and cleanup."""
        # SQLite connections are closed automatically with context managers
        self.logger.info("State manager closed")
