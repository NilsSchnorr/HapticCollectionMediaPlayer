# Quick Test Guide

## Test Files Created

I've added three test HTML files to quickly verify your system is working:

1. **test1.html** - Shows "TEST 1" on a blue background
2. **test2.html** - Shows "TEST 2" on a red background
3. **test_interactive.html** - Interactive counter with buttons (green background)

## Testing Steps

### 1. Quick Manual Test (No NFC tag needed)

Open the test files directly in your browser to verify they work:
```bash
cd /Users/nilsschnorr/Documents/GitHub/HapticCollectionMediaPlayer
open html/test1.html
open html/test2.html
```

### 2. Test with Web Interface

1. Start the web interface:
   ```bash
   ./start_web_interface.sh
   ```

2. Open http://localhost:5000 in your browser

3. Place any NFC tag on the reader

4. When detected, assign it to `test1.html` or `test2.html`

5. Save the tag

### 3. Test the Full System

1. Start the main display system:
   ```bash
   ./start_nfc_display.sh
   ```

2. You should see the home base page

3. Place your configured NFC tag on the reader

4. You should see either "TEST 1" (blue) or "TEST 2" (red)

5. Remove the tag - system should return to home base

## Expected Behavior

- **No tag**: Shows home_base.html (gradient background with "Ready to Scan")
- **Tag with test1.html**: Shows "TEST 1" on blue background
- **Tag with test2.html**: Shows "TEST 2" on red background
- **Unknown tag**: Shows unknown_tag.html (error message)

## Visual Confirmation

The test pages use distinctive colors:
- **Test 1**: Blue background (#3498db)
- **Test 2**: Red background (#e74c3c)
- **Interactive Test**: Green background (#27ae60) with counter
- **Home Base**: Purple gradient
- **Unknown Tag**: Orange/yellow gradient

This makes it easy to confirm the system is switching pages correctly!

## Testing Page Persistence

The interactive test page is perfect for verifying that:
1. The page stays active while the tag is on the reader
2. JavaScript continues to work (counter maintains its value)
3. The page doesn't refresh as long as the tag remains present
4. Removing the tag returns to home base (counter resets)
