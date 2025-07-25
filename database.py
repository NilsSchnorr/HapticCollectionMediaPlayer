#!/usr/bin/env python3
"""
NFC Tag Database Management
Handles SQLite database for NFC tag to HTML file mapping
"""

import sqlite3
import logging
import os
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

class NFCDatabase:
    def __init__(self, db_path: str):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tags table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS nfc_tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_uid TEXT UNIQUE NOT NULL,
                        tag_name TEXT NOT NULL,
                        html_file TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create usage log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usage_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag_uid TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tag_uid) REFERENCES nfc_tags (tag_uid)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_tag(self, tag_uid: str, tag_name: str, html_file: str) -> bool:
        """Add a new NFC tag to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO nfc_tags (tag_uid, tag_name, html_file)
                    VALUES (?, ?, ?)
                ''', (tag_uid, tag_name, html_file))
                conn.commit()
                logger.info(f"Added tag: {tag_name} ({tag_uid}) -> {html_file}")
                return True
        except Exception as e:
            logger.error(f"Error adding tag: {e}")
            return False
    
    def get_html_file(self, tag_uid: str) -> Tuple[Optional[str], Optional[str]]:
        """Get HTML file and tag name for a given UID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT html_file, tag_name FROM nfc_tags WHERE tag_uid = ?
                ''', (tag_uid,))
                result = cursor.fetchone()
                
                if result:
                    # Update last used timestamp
                    cursor.execute('''
                        UPDATE nfc_tags SET last_used = CURRENT_TIMESTAMP WHERE tag_uid = ?
                    ''', (tag_uid,))
                    
                    # Log usage
                    cursor.execute('''
                        INSERT INTO usage_log (tag_uid) VALUES (?)
                    ''', (tag_uid,))
                    
                    conn.commit()
                    return result[0], result[1]  # html_file, tag_name
                else:
                    logger.info(f"Unknown tag: {tag_uid}")
                    return None, None
                    
        except Exception as e:
            logger.error(f"Error getting HTML file for tag {tag_uid}: {e}")
            return None, None
    
    def get_all_tags(self) -> List[Tuple]:
        """Get all tags from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT tag_uid, tag_name, html_file, created_at, last_used 
                    FROM nfc_tags ORDER BY tag_name
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            return []
    
    def delete_tag(self, tag_uid: str) -> bool:
        """Delete a tag from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM nfc_tags WHERE tag_uid = ?', (tag_uid,))
                cursor.execute('DELETE FROM usage_log WHERE tag_uid = ?', (tag_uid,))
                conn.commit()
                logger.info(f"Deleted tag: {tag_uid}")
                return True
        except Exception as e:
            logger.error(f"Error deleting tag: {e}")
            return False
    
    def get_usage_stats(self) -> List[Tuple]:
        """Get usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.tag_name, t.tag_uid, COUNT(u.id) as usage_count,
                           MAX(u.timestamp) as last_used
                    FROM nfc_tags t
                    LEFT JOIN usage_log u ON t.tag_uid = u.tag_uid
                    GROUP BY t.tag_uid
                    ORDER BY usage_count DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return []
