#!/usr/bin/env python3
"""
NFC Display System Configuration
Optimized for fresh Raspberry Pi setup
"""

# Reader Configuration - Using working approach
READER_TYPE = "PN532_WORKING"  # Uses working NFC-Player approach

# PN532 Configuration - Based on working player
PN532_UART_PORT = '/dev/ttyS0'      # Working player uses ttyS0, not ttyAMA0
PN532_UART_BAUDRATE = 115200        # Standard baud rate
PN532_RESET_PIN = 20               # GPIO pin for reset (RSTPDN -> D20)

# Display Configuration
HOME_BASE_PAGE = "home_base.html"    # Page shown when no tag is present
UNKNOWN_TAG_PAGE = "unknown_tag.html"  # Page shown for unregistered tags

# Tag Detection Settings
NO_TAG_THRESHOLD = 3    # Number of failed reads before considering tag removed
READ_INTERVAL = 0.1     # Seconds between tag reads

# Browser Configuration
BROWSER_COMMAND = [
    'chromium-browser',
    '--kiosk',
    '--noerrdialogs',
    '--disable-infobars',
    '--disable-session-crashed-bubble',
    '--disable-translate',
    '--disable-features=TranslateUI',
    '--check-for-update-interval=31536000',
    '--disable-component-update',
]

# For development/testing without fullscreen
BROWSER_COMMAND_DEV = [
    'chromium-browser',
    '--app={url}',
    '--window-size=800,600',
    '--window-position=100,100',
    '--disable-infobars',
]

# Use development mode browser?
DEV_MODE = False

# Database Configuration
DATABASE_PATH = "data/nfc_tags.db"

# Logging Configuration
ENABLE_LOGGING = True
LOG_FILE = "logs/nfc_display.log"
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

# Auto-add unknown tags
AUTO_ADD_UNKNOWN_TAGS = False

# Display timeout (optional)
DISPLAY_TIMEOUT = None  # e.g., 300 for 5 minutes

# Performance Settings
CACHE_HTML = True  # Cache HTML files in memory for faster loading

# Network Features
ENABLE_WEB_SERVER = True   # Enable web interface for tag management
WEB_SERVER_PORT = 5000
WEB_SERVER_HOST = "0.0.0.0"
