# NFC Display System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi                             │
│                                                              │
│  ┌─────────────────┐         ┌──────────────────┐          │
│  │   NFC Reader    │         │  SQLite Database │          │
│  │  (PN532/RC522)  │◄────────┤                  │          │
│  └────────┬────────┘         │  • Tag mappings  │          │
│           │                  │  • Access logs   │          │
│           ▼                  └──────────────────┘          │
│  ┌─────────────────┐                  ▲                     │
│  │    main.py      │                  │                     │
│  │                 │──────────────────┘                     │
│  │ • Tag detection │                                        │
│  │ • Page display  │         ┌──────────────────┐          │
│  └────────┬────────┘         │   HTML Files     │          │
│           │                  │                  │          │
│           ▼                  │ • home_base.html │          │
│  ┌─────────────────┐         │ • product1.html  │          │
│  │ Chromium Browser│◄────────┤ • welcome.html   │          │
│  │  (Kiosk Mode)   │         │ • ...            │          │
│  └─────────────────┘         └──────────────────┘          │
│                                                              │
│  ┌─────────────────────────────────────────────┐           │
│  │        Web Management Interface              │           │
│  │                                              │           │
│  │  ┌─────────────┐    ┌─────────────────┐    │           │
│  │  │web_interface│    │   Browser UI     │    │           │
│  │  │    .py      │◄───┤                 │    │           │
│  │  │             │    │ • Tag detection │    │           │
│  │  │ Flask Server│    │ • Configuration │    │           │
│  │  └─────────────┘    │ • Access logs   │    │           │
│  │         ▲           └─────────────────┘    │           │
│  │         │                                   │           │
│  │         └───────── WebSocket ───────────    │           │
│  │                                              │           │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘

## Data Flow

1. **Tag Detection**: NFC reader detects tag UID
2. **Database Lookup**: System queries SQLite for associated HTML file
3. **Display Update**: 
   - Tag present → Show tag's HTML page
   - Tag removed → Return to home_base.html
4. **Web Interface**: Real-time tag management via browser

## Key Components

- **main.py**: Core display logic with tag presence detection
- **web_interface.py**: Flask-based management interface
- **database.py**: SQLite database operations
- **config.py**: System configuration
