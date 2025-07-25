# Setup Instructions for Desktop Installation

When your repository is saved on the Raspberry Pi's Desktop, follow these instructions:

## 1. Navigate to the Project

```bash
cd ~/Desktop/HapticCollectionMediaPlayer
```

## 2. Make Scripts Executable

```bash
chmod +x *.sh
```

## 3. Update Service File Paths (IMPORTANT!)

Before running setup, update the service files with your actual path:

```bash
./update_paths.sh
```

This script automatically updates the systemd service files with your current directory path.

## 4. Run the Setup

```bash
./setup.sh
```

When prompted:
- Choose **1** for PN532 NFC HAT
- Choose **Y** for auto-start if desired

## 5. Initialize Database

```bash
source venv/bin/activate
python3 setup_db.py
```

## Complete Path Reference

All paths will be relative to:
```
/home/pi/Desktop/HapticCollectionMediaPlayer/
```

### Service Files
If you enable auto-start, the services will use:
- Working Directory: `/home/pi/Desktop/HapticCollectionMediaPlayer`
- Python: `/home/pi/Desktop/HapticCollectionMediaPlayer/venv/bin/python`
- Scripts: `/home/pi/Desktop/HapticCollectionMediaPlayer/main.py`

### Manual Commands
Always run from the project directory:
```bash
cd ~/Desktop/HapticCollectionMediaPlayer
./start_web_interface.sh
./start_nfc_display.sh
```

## Quick Start After Setup

1. **Test the NFC reader**:
   ```bash
   cd ~/Desktop/HapticCollectionMediaPlayer
   source venv/bin/activate
   python3 test_presence.py
   ```

2. **Configure tags**:
   ```bash
   cd ~/Desktop/HapticCollectionMediaPlayer
   ./start_web_interface.sh
   ```

3. **Run the display**:
   ```bash
   cd ~/Desktop/HapticCollectionMediaPlayer
   ./start_nfc_display.sh
   ```

## Notes

- The `setup.sh` script now uses the current directory instead of creating a new one
- All launcher scripts use relative paths (`cd "$(dirname "$0")"`)
- The virtual environment is created within the project folder
- Database and logs folders are created in the project directory

## If You Move the Project

If you ever move the project to a different location:
1. Run `./update_paths.sh` again
2. Reinstall the systemd services if using auto-start

That's it! The system will work perfectly from your Desktop location.
