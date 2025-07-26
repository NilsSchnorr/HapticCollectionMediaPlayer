# NFC Display System

The NFC Display System provides a seamless interactive experience where HTML content automatically appears when NFC chips are placed on the reader.

## Features

- **Home Base Screen**: Elegant welcome screen with animated NFC icon
- **Automatic Content Display**: Shows mapped HTML when chip is detected
- **Auto Return**: Returns to home base when chip is removed
- **Fullscreen Support**: Can run in kiosk mode for exhibitions
- **Real-time Detection**: Instant response to chip placement/removal

## Quick Start

### Simple Mode (Regular Browser Window)
```bash
chmod +x start_display_simple.sh
./start_display_simple.sh
```

### Kiosk Mode (Fullscreen - Raspberry Pi)
```bash
chmod +x start_display.sh
./start_display.sh
```

## How It Works

1. **Home Base**: Shows "Haptic Collection Media Player" with prompt to place object
2. **Chip Detected**: Automatically displays the mapped HTML content
3. **Chip Removed**: Returns to home base screen

## Display vs Management

This system has two separate interfaces:

### Management Interface (Port 5000)
- Create/delete NFC mappings
- View existing mappings
- Test NFC detection
- Run with: `./start_both.sh`

### Display Interface (Port 8080)
- Shows home base screen
- Displays content when chips detected
- Returns to home when chips removed
- Run with: `./start_display.sh`

## Full System Setup

1. **First Time - Create Mappings**:
   ```bash
   ./start_both.sh
   ```
   - Open http://localhost:5000
   - Map your NFC chips to HTML files
   - Close when done (mappings are saved)

2. **Daily Use - Display Only**:
   ```bash
   ./start_display.sh
   ```
   - Shows the interactive display
   - No management interface needed

## Customization

### Change Home Base Appearance
Edit the CSS in `nfc_display.py`:
- Colors: Modify the gradient backgrounds
- Animation: Adjust the pulse/shimmer effects
- Text: Change the title and prompt messages

### HTML Content
Place your HTML files in the `html_content/` directory. They will display in full screen when their mapped NFC chip is detected.

## Troubleshooting

- **Port 8080 in use**: Another program is using the port
- **No NFC detection**: Check that NFC reader is connected
- **Content not loading**: Verify HTML files exist in `html_content/`
- **Mappings not found**: Ensure `nfc_mappings.json` exists

## Exhibition/Installation Mode

For permanent installations:

1. Configure Raspberry Pi to auto-login
2. Add to autostart:
   ```bash
   @/home/pi/Documents/GitHub/HapticCollectionMediaPlayer/start_display.sh
   ```
3. System will start in fullscreen kiosk mode on boot

## Browser Compatibility

- **Best**: Chromium/Chrome (supports kiosk mode)
- **Good**: Firefox (supports kiosk mode)
- **Works**: Any modern browser (manual fullscreen with F11)
