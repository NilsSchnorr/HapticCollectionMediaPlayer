#!/usr/bin/env python3
"""
Web-based NFC Tag Management Interface
"""
import os
import sys
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from database import NFCDatabase
from config import READER_TYPE, DATABASE_PATH, PN532_INTERFACE, PN532_I2C_BUS, PN532_I2C_ADDRESS

# Import reader libraries based on configuration
if READER_TYPE == "PN532":
    import nfc
else:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nfc-management-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
current_tag = None
tag_reader_thread = None
stop_reading = False
db = NFCDatabase(DATABASE_PATH)

class NFCReader:
    def __init__(self):
        self.current_tag = None
        self.last_tag = None
        if READER_TYPE == "PN532":
            self.init_pn532()
        else:
            self.init_rc522()
    
    def init_pn532(self):
        """Initialize PN532 NFC reader"""
        try:
            # Connection string based on interface type
            if PN532_INTERFACE == 'i2c':
                # For PN532 NFC HAT using I2C
                connection_string = f'i2c:{PN532_I2C_BUS}:{PN532_I2C_ADDRESS}'
            elif PN532_INTERFACE == 'spi':
                connection_string = 'spi:0:0'
            elif PN532_INTERFACE == 'uart':
                connection_string = 'tty:serial0:115200'
            else:  # usb
                connection_string = 'usb'
            
            print(f"Initializing PN532 NFC HAT with {PN532_INTERFACE} interface...")
            self.clf = nfc.ContactlessFrontend(connection_string)
            if not self.clf:
                print("No NFC device found!")
                print("Please check:")
                print("1. I2C is enabled (sudo raspi-config -> Interface Options -> I2C)")
                print("2. PN532 HAT is properly connected")
                print("3. Try: sudo i2cdetect -y 1")
                sys.exit(1)
            print("PN532 NFC HAT initialized successfully")
        except Exception as e:
            print(f"Error initializing PN532: {e}")
            print("\nTroubleshooting steps:")
            print("1. Enable I2C: sudo raspi-config -> Interface Options -> I2C")
            print("2. Check connections on the PN532 HAT")
            print("3. Verify with: sudo i2cdetect -y 1")
            print("4. You might need to run with sudo if permission errors occur")
            sys.exit(1)
    
    def init_rc522(self):
        """Initialize RC522 NFC reader"""
        self.reader = SimpleMFRC522()
    
    def read_tag(self):
        """Read tag and return UID or None"""
        if READER_TYPE == "PN532":
            try:
                tag = self.clf.connect(rdwr={'on-connect': lambda tag: False}, terminate=lambda: True, timeout=0.5)
                if tag:
                    return tag.identifier.hex()
            except:
                pass
        else:
            try:
                id, text = self.reader.read_no_block()
                if id:
                    return hex(id)[2:].upper()
            except:
                pass
        return None
    
    def format_tag_uid(self, uid):
        """Format tag UID to standard format"""
        uid = uid.upper()
        return ':'.join([uid[i:i+2] for i in range(0, len(uid), 2)])
    
    def close(self):
        """Clean up reader resources"""
        if READER_TYPE == "PN532":
            try:
                self.clf.close()
            except:
                pass
        else:
            GPIO.cleanup()

# Initialize NFC reader
nfc_reader = NFCReader()

def read_tags_continuously():
    """Background thread to continuously read NFC tags"""
    global current_tag, stop_reading
    
    while not stop_reading:
        try:
            tag_uid = nfc_reader.read_tag()
            
            if tag_uid:
                formatted_uid = nfc_reader.format_tag_uid(tag_uid)
                
                if formatted_uid != current_tag:
                    current_tag = formatted_uid
                    
                    # Get tag info from database
                    tags = db.list_tags()
                    tag_info = None
                    for tag in tags:
                        if tag[0] == formatted_uid:
                            tag_info = {
                                'uid': tag[0],
                                'name': tag[1],
                                'html_file': tag[2],
                                'last_accessed': tag[3]
                            }
                            break
                    
                    if not tag_info:
                        tag_info = {
                            'uid': formatted_uid,
                            'name': 'Unregistered Tag',
                            'html_file': '',
                            'last_accessed': None
                        }
                    
                    # Emit tag detected event
                    socketio.emit('tag_detected', tag_info)
            else:
                if current_tag:
                    current_tag = None
                    socketio.emit('tag_removed')
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Error reading tag: {e}")
            time.sleep(1)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/tags')
def get_tags():
    """Get all registered tags"""
    tags = db.list_tags()
    tag_list = []
    for tag in tags:
        tag_list.append({
            'uid': tag[0],
            'name': tag[1],
            'html_file': tag[2],
            'last_accessed': tag[3]
        })
    return jsonify(tag_list)

@app.route('/api/html_files')
def get_html_files():
    """Get list of available HTML files"""
    html_dir = os.path.join(os.path.dirname(__file__), 'html')
    files = []
    
    if os.path.exists(html_dir):
        for file in os.listdir(html_dir):
            if file.endswith('.html'):
                files.append(file)
    
    return jsonify(sorted(files))

@app.route('/api/tag/<uid>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_tag(uid):
    """Manage a specific tag"""
    if request.method == 'GET':
        # Get tag info
        tags = db.list_tags()
        for tag in tags:
            if tag[0] == uid:
                return jsonify({
                    'uid': tag[0],
                    'name': tag[1],
                    'html_file': tag[2],
                    'last_accessed': tag[3]
                })
        return jsonify({'error': 'Tag not found'}), 404
    
    elif request.method == 'POST' or request.method == 'PUT':
        # Add or update tag
        data = request.json
        name = data.get('name', 'Unnamed Tag')
        html_file = data.get('html_file', '')
        description = data.get('description', '')
        
        # Check if tag exists
        tags = db.list_tags()
        exists = any(tag[0] == uid for tag in tags)
        
        if exists:
            # Update existing tag (delete and re-add)
            # Note: In a real implementation, we'd add an update method to the database class
            conn = db.db_path
            import sqlite3
            connection = sqlite3.connect(conn)
            cursor = connection.cursor()
            cursor.execute('UPDATE nfc_tags SET tag_name = ?, html_file = ?, description = ? WHERE tag_uid = ?',
                         (name, html_file, description, uid))
            connection.commit()
            connection.close()
            return jsonify({'message': 'Tag updated successfully'})
        else:
            # Add new tag
            success = db.add_tag(uid, name, html_file, description)
            if success:
                return jsonify({'message': 'Tag added successfully'})
            else:
                return jsonify({'error': 'Failed to add tag'}), 400
    
    elif request.method == 'DELETE':
        # Delete tag
        # Note: In a real implementation, we'd add a delete method to the database class
        conn = db.db_path
        import sqlite3
        connection = sqlite3.connect(conn)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM nfc_tags WHERE tag_uid = ?', (uid,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Tag deleted successfully'})

@app.route('/api/logs/<uid>')
def get_tag_logs(uid):
    """Get access logs for a specific tag"""
    logs = db.get_access_log(uid, limit=50)
    log_list = []
    for log in logs:
        log_list.append({
            'uid': log[0],
            'name': log[1],
            'accessed_at': log[2]
        })
    return jsonify(log_list)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    
    # Send current tag if any
    if current_tag:
        tags = db.list_tags()
        tag_info = None
        for tag in tags:
            if tag[0] == current_tag:
                tag_info = {
                    'uid': tag[0],
                    'name': tag[1],
                    'html_file': tag[2],
                    'last_accessed': tag[3]
                }
                break
        
        if not tag_info:
            tag_info = {
                'uid': current_tag,
                'name': 'Unregistered Tag',
                'html_file': '',
                'last_accessed': None
            }
        
        emit('tag_detected', tag_info)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Start tag reader thread
    tag_reader_thread = threading.Thread(target=read_tags_continuously, daemon=True)
    tag_reader_thread.start()
    
    try:
        # Run the web server
        print("Starting NFC Management Interface...")
        print("Open http://localhost:5000 in your browser")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
        stop_reading = True
        nfc_reader.close()
