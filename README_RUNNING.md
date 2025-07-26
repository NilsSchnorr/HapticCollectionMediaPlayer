# Running the NFC Player Continuously

Now that you've mapped your NFC chips, you need to keep the NFC Player running to detect chips and open HTML files.

## Quick Options:

### 1. Simple Background (Survives terminal close)
```bash
./start_player_background.sh
```
- Runs in background
- Logs to `nfc_player.log`
- Survives terminal closure
- Stop with: `pkill -f nfc_player.py`

### 2. System Service (Starts on boot) - RECOMMENDED
```bash
chmod +x install_service.sh
./install_service.sh
```
- Runs as system service
- Starts automatically on boot
- Professional solution
- Control with: `sudo systemctl start/stop/status nfc-player`

### 3. Screen Session (Can reattach later)
```bash
screen -S nfc-player
python3 nfc_player.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r nfc-player
```

## What You Can Close:

✅ **CAN CLOSE:**
- Web browser (http://localhost:5000) - mappings are saved
- Web server terminal (if only doing playback)

❌ **CANNOT CLOSE (unless using option 1 or 2 above):**
- NFC Player terminal - needs to run for chip detection

## Check What's Running:
```bash
./check_status.sh
```

## Your Mappings:
- Saved in `nfc_mappings.json`
- Will persist across restarts
- Can add more anytime via web interface
