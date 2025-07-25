#!/usr/bin/env python3
"""
NFC Display System Configuration
"""

# Reader Configuration
READER_TYPE = "PN532"  # Options: "PN532" or "RC522"

# PN532 NFC HAT Configuration
# The PN532 NFC HAT can use different interfaces:
# - 'i2c': Most common for HATs (uses I2C bus)
# - 'spi': Alternative interface
# - 'uart': Serial interface
# - 'usb': For USB-based readers
PN532_INTERFACE = 'i2c'  # For PN532 NFC HAT, use 'i2c'

# I2C Configuration for PN532 HAT
PN532_I2C_BUS = 1  # Raspberry Pi typically uses bus 1
PN532_I2C_ADDRESS = 0x24  # Default I2C address for PN532

# Display Configuration
HOME_BASE_PAGE = "home_base.html"  # Page shown when no tag is present
UNKNOWN_TAG_PAGE = "unknown_tag.html"  # Page shown for unregistered tags

# Tag Detection Settings
NO_TAG_THRESHOLD = 3  # Number of failed reads before considering tag removed
READ_INTERVAL = 0.1  # Seconds between tag reads

# Browser Configuration
BROWSER_COMMAND = [
    'chromium-browser',
    '--kiosk',
    '--noerrdialogs',
    '--disable-infobars',
    '--disable-session-crashed-bubble',
    '--disable-translate',
    '--disable-features=TranslateUI',
    '--check-for-update-interval=31536000',  # Disable update checks
    '--disable-component-update',
]

# For development/testing without fullscreen
BROWSER_COMMAND_DEV = [
    'chromium-browser',
    '--app={url}',  # {url} will be replaced with actual URL
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
AUTO_ADD_UNKNOWN_TAGS = False  # If True, unknown tags will be automatically added to the database

# Display timeout (optional)
# Set to None to disable, or number of seconds to return to home after no interaction
DISPLAY_TIMEOUT = None  # e.g., 300 for 5 minutes

# GPIO Pin Configuration (for RC522)
RC522_RST_PIN = 22  # GPIO pin for RST
RC522_SPI_ID = 0    # SPI bus ID
RC522_SPI_CE = 0    # SPI chip enable

# PN532 Configuration
PN532_INTERFACE = 'usb'  # Options: 'usb', 'uart', 'i2c'

# Performance Settings
CACHE_HTML = True  # Cache HTML files in memory for faster loading

# Network Features (future expansion)
ENABLE_WEB_SERVER = False  # Enable web interface for remote management
WEB_SERVER_PORT = 8080
WEB_SERVER_HOST = "0.0.0.0"
