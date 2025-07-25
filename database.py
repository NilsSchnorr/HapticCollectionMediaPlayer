#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import os

class NFCDatabase:
    def __init__(self, db_path='data/nfc_tags.db'):
        self.db_path = db_path
        
    def get_html_file(self, tag_uid):
        """Get HTML file associated with a tag UID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get HTML file for tag
            cursor.execute('''
            SELECT html_file, tag_name FROM nfc_tags WHERE tag_uid = ?
            ''', (tag_uid,))
            
            result = cursor.fetchone()
            
            if result:
                html_file, tag_name = result
                
                # Update last accessed time
                cursor.execute('''
                UPDATE nfc_tags SET last_accessed = ? WHERE tag_uid = ?
                ''', (datetime.now(), tag_uid))
                
                # Log access
                cursor.execute('''
                INSERT INTO access_log (tag_uid) VALUES (?)
                ''', (tag_uid,))
                
                conn.commit()
                return html_file, tag_name
            else:
                return None, None
                
        finally:
            conn.close()
    
    def add_tag(self, tag_uid, tag_name, html_file, description=""):
        """Add a new tag to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO nfc_tags (tag_uid, tag_name, html_file, description)
            VALUES (?, ?, ?, ?)
            ''', (tag_uid, tag_name, html_file, description))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def list_tags(self):
        """List all registered tags"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT tag_uid, tag_name, html_file, last_accessed FROM nfc_tags
        ORDER BY created_at DESC
        ''')
        
        tags = cursor.fetchall()
        conn.close()
        
        return tags
    
    def get_access_log(self, tag_uid=None, limit=100):
        """Get access log, optionally filtered by tag UID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if tag_uid:
            cursor.execute('''
            SELECT a.tag_uid, t.tag_name, a.accessed_at 
            FROM access_log a
            JOIN nfc_tags t ON a.tag_uid = t.tag_uid
            WHERE a.tag_uid = ?
            ORDER BY a.accessed_at DESC
            LIMIT ?
            ''', (tag_uid, limit))
        else:
            cursor.execute('''
            SELECT a.tag_uid, t.tag_name, a.accessed_at 
            FROM access_log a
            JOIN nfc_tags t ON a.tag_uid = t.tag_uid
            ORDER BY a.accessed_at DESC
            LIMIT ?
            ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return logs
