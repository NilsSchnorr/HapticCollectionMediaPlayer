#!/usr/bin/env python3
import sqlite3
import os

def create_database():
    """Create the NFC database and tables"""
    # Create database directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('data/nfc_tags.db')
    cursor = conn.cursor()
    
    # Create tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nfc_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_uid TEXT UNIQUE NOT NULL,
        tag_name TEXT,
        html_file TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP
    )
    ''')
    
    # Create access log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_uid TEXT NOT NULL,
        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tag_uid) REFERENCES nfc_tags(tag_uid)
    )
    ''')
    
    # Insert some example data
    example_tags = [
        ('04:5C:7B:2A:6C:50:80', 'Welcome Tag', 'welcome.html', 'Main welcome page'),
        ('04:5D:7B:2A:6C:50:80', 'Product Info', 'product1.html', 'Product information page'),
        ('04:5E:7B:2A:6C:50:80', 'Contact Info', 'contact.html', 'Contact information page'),
        ('04:5F:7B:2A:6C:50:80', 'Test Tag 1', 'test1.html', 'Test page 1 - Blue background'),
        ('04:60:7B:2A:6C:50:80', 'Test Tag 2', 'test2.html', 'Test page 2 - Red background')
    ]
    
    for tag in example_tags:
        try:
            cursor.execute('''
            INSERT INTO nfc_tags (tag_uid, tag_name, html_file, description)
            VALUES (?, ?, ?, ?)
            ''', tag)
        except sqlite3.IntegrityError:
            print(f"Tag {tag[0]} already exists, skipping...")
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
