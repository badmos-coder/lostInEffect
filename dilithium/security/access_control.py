from dilithium.config import SecurityConfig
from typing import List, Dict, Optional
import jwt
from datetime import datetime, timedelta
import hashlib
import sqlite3

class AccessControl:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.session_cache = {}
        self.db_conn = self._init_database()
        
    def _init_database(self) -> sqlite3.Connection:
        conn = sqlite3.connect('access.db', check_same_thread=False)
        conn.execute('''CREATE TABLE IF NOT EXISTS roles
                       (role_id TEXT PRIMARY KEY, permissions TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS user_roles
                       (user_id TEXT, role_id TEXT,
                        FOREIGN KEY(role_id) REFERENCES roles(role_id))''')
        return conn
        
    def verify_access(self, token: str, required_permission: str) -> bool:
        """Verify user access rights"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=['HS256'])
            user_id = payload['sub']
            
            if user_id in self.session_cache:
                permissions = self.session_cache[user_id]
            else:
                permissions = self._load_permissions(user_id)
                
            return required_permission in permissions
            
        except jwt.InvalidTokenError:
            return False
            
    def _load_permissions(self, user_id: str) -> List[str]:
        """Load user permissions from database"""
        cursor = self.db_conn.cursor()
        cursor.execute('''
            SELECT r.permissions
            FROM roles r
            JOIN user_roles ur ON r.role_id = ur.role_id
            WHERE ur.user_id = ?
        ''', (user_id,))
        
        permissions = []
        for row in cursor.fetchall():
            permissions.extend(row[0].split(','))
        
        self.session_cache[user_id] = permissions
        return permissions 