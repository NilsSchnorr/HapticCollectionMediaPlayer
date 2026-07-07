# Haptic Collection Media Player
By Lucas Latzel and Nils Schnorr

An interactive NFC-based media display system that presents HTML content when physical objects are placed on a reader. Perfect for museums, exhibitions, interactive art installations, and educational displays.

## 🌟 Overview

This system allows you to:
- **Map NFC chips to HTML content** using a web interface
- **Display content automatically** when objects are placed on the reader
- **Return to home screen** when objects are removed
- **Boot straight into kiosk mode** for unattended public exhibitions — the Pi survives daily power cuts without any manual intervention

**How it works in the exhibition:** A visitor places a tagged object on the reader. The PN532 NFC HAT reads the chip's UID, the backend looks it up in `nfc_mappings.json`, and Chromium (running fullscreen in kiosk mode) instantly displays the mapped HTML page. When the object is removed, the display returns to the home screen.

## 🧰 Hardware

### Parts

- Raspberry Pi 4 (Pi 3 also works)
- **Waveshare PN532 NFC HAT** (mounted on the Pi's 40-pin GPIO header)
- NFC tags/chips (NTAG, Mifare, etc.) — one per exhibit object
- HDMI display
- microSD card with Raspberry Pi OS (with desktop)

### Configuring the Waveshare PN532 NFC HAT (UART mode)

The software communicates with the PN532 via **UART on `/dev/ttyS0`**, so the HAT must be physically configured for UART mode. **Always power off before changing switches or jumpers.**

**1. Chip mode jumpers (I0 / I1):** set both to **L**

| Jumper | Position |
|--------|----------|
| I0 | **L** |
| I1 | **L** |

**2. DIP switch block:** only **RX** and **TX** ON, everything else OFF

| SCK | MISO | MOSI | NSS | SCL | SDA | RX | TX |
|-----|------|------|-----|-----|-----|-----|-----|
| OFF | OFF | OFF | OFF | OFF | OFF | **ON** | **ON** |

Never set all DIP switches to ON at the same time — the HAT will not communicate correctly.

**3. Reset jumper:** connect **RSTPDN → D20** with a jumper cap. The software pulses GPIO 20 to hardware-reset the PN532 on startup (`reset=20` in the code), which makes recovery from a hung reader reliable.

**4. Not needed for UART:** the INT0 → D16 jumper (only relevant for I2C mode). Leave it off.

**5. Antenna:** the PCB antenna is integrated — nothing to attach. Keep the coil area clear of metal.

Then seat the HAT firmly on all 40 GPIO pins. The connections are made automatically through the header:

| PN532 HAT | Raspberry Pi |
|-----------|--------------|
| 3V3 | 3.3V |
| GND | GND |
| TXD | RXD (GPIO 15, physical pin 10) |
| RXD | TXD (GPIO 14, physical pin 8) |

(If you ever wire a PN532 board manually instead of using the HAT, note that TX and RX cross: reader TX → Pi RX and vice versa.)

## 🐣 Raspberry Pi Setup — Fresh Install, Step by Step

> ⚠️ **Offline deployment note:** In the exhibition, the Pi typically has **no internet**. Steps 4–6 require a connection — complete them (and test everything) before the Pi is deployed.

### Step 1: Flash the OS

Flash **Raspberry Pi OS (with desktop)** using Raspberry Pi Imager. In the imager settings, set the hostname (e.g. `hcmp-pi`), username (e.g. `hcmp`), and Wi-Fi credentials. Boot the Pi with the configured HAT mounted.

### Step 2: Enable UART, disable the serial console

```bash
sudo raspi-config
```

Navigate to **Interface Options → Serial Port** and answer:

1. *"Would you like a login shell to be accessible over serial?"* → **No**
2. *"Would you like the serial port hardware to be enabled?"* → **Yes**

This exact combination is critical. A login shell bound to the serial port is the single most common reason the PN532 stays silent.

Before rebooting, verify (paths are `/boot/firmware/` on current OS versions, `/boot/` on older ones):

```bash
grep enable_uart /boot/firmware/config.txt   # must show: enable_uart=1
cat /boot/firmware/cmdline.txt               # must NOT contain: console=serial0,115200
```

Then reboot:

```bash
sudo reboot
```

### Step 3: Verify the serial device

```bash
ls -l /dev/ttyS0 /dev/serial0
```

`/dev/ttyS0` should exist, with `/dev/serial0` symlinked to it. Also confirm your user is in the `dialout` group (`groups` — it is by default on Raspberry Pi OS).

### Step 4: Clone the repository

```bash
mkdir -p ~/Documents/Github
cd ~/Documents/Github
git clone https://github.com/NilsSchnorr/HapticCollectionMediaPlayer.git
cd HapticCollectionMediaPlayer
```

### Step 5: Copy the files git doesn't bring

Two kinds of files are **gitignored** and must be copied from an existing unit (or your development machine), e.g. via `scp` or USB stick:

- `nfc_mappings.json` — the chip-to-content mappings (skip if this unit gets freshly mapped chips)
- Large media files, e.g. videos in `html_content/videos/`

Example from another machine on the same network:

```bash
scp /path/to/nfc_mappings.json hcmp@hcmp-pi.local:~/Documents/Github/HapticCollectionMediaPlayer/
```

### Step 6: Install dependencies

```bash
chmod +x make_executable.sh && ./make_executable.sh
./setup_system_packages.sh
```

This installs `xdotool` plus all Python packages from `requirements-rpi.txt` into the **system Python**.

> ⚠️ Do **not** use a virtual environment on the Pi. The autostart service runs `/usr/bin/python3` — dependencies installed only in a venv will fail at boot. (`requirements.txt` without the `-rpi` suffix is for development machines and lacks the Pi-specific packages.)

### Step 7: Test the NFC hardware

```bash
cd python
python3 example_get_uid.py
```

Place a tag on the HAT — its UID should print. If not, see [Troubleshooting](#%EF%B8%8F-troubleshooting) before continuing. Return to the repo root afterwards (`cd ..`).

### Step 8: Map your NFC chips (if needed)

If you copied a valid `nfc_mappings.json` for the same physical objects in Step 5, skip this. For new chips:

```bash
python3 nfc_web_server.py
```

Open http://localhost:5000, place each chip on the reader, assign an HTML file, save. Stop with Ctrl+C when done. (See [Tag Management Interface](#tag-management-interface) for details.)

### Step 9: Install autostart

```bash
./install_autostart.sh
```

Sets up everything for unattended operation (see [Autostart](#-autostart-museum--exhibition-mode)). Accept the reboot at the end.

### Step 10: The acceptance test

After the reboot the Pi should come up on its own: auto-login → backend starts → Chromium opens fullscreen showing the home screen. Then the real museum test: **pull the power plug, plug it back in**, and confirm the whole chain comes up again without touching anything. If that works, the unit is deployment-ready.

## 📖 User Guide

### Tag Management Interface

The mapping interface links NFC chip UIDs to HTML files.

**If autostart is installed, stop the display backend first** — it holds the NFC serial port exclusively:

```bash
sudo systemctl stop hcmp-display
```

Then start the interface:

```bash
python3 nfc_web_server.py
```

Open http://localhost:5000 in a browser:

1. **Place an NFC chip** on the reader — its UID appears in the form automatically
2. **Select an HTML file** from the dropdown
3. **Add a description** (optional)
4. Click **Save Mapping**

You can also view all mappings, delete mappings, and test with a random UID for development. Mappings are saved in `nfc_mappings.json` and persist across restarts. **Back this file up** — it is gitignored and exists only on the device.

When you're done, Ctrl+C the interface and restart the display backend (or just reboot):

```bash
sudo systemctl start hcmp-display
```

### Display System

**Normal operation is autostart** — the Pi boots straight into display mode with no interaction (see below).

**Manual operation** (during setup, or with autostart uninstalled):

```bash
python3 nfc_display.py    # backend, in one terminal
./kiosk.sh                # fullscreen kiosk browser, in another
```

**Windowed mode for development** (easy to close):

```bash
./start_display_simple.sh
```

**Demo mode — no NFC hardware needed** (e.g. for previewing content on a laptop):

```bash
./start_demo.sh
```

Use the on-screen buttons or keys 1–3 to simulate chips, 0/ESC to simulate removal.

#### How it works

1. **Home screen** shows the animated "place an object" prompt
2. **Chip detected** → the mapped HTML content displays instantly, edge to edge
3. **Chip removed** → back to the home screen
4. **Unknown chip** → "Unknown chip" message with the UID (useful for finding unmapped tags)

#### Exiting kiosk mode

- **Alt + F4** — close the browser window
- **Ctrl + C** in the terminal (manual mode) — stop the backend

### Adding Content

- Place HTML files in the `html_content/` directory — full HTML/CSS/JavaScript support
- Put shared assets (images, videos, JS, 3D models) in subdirectories, e.g. `html_content/images/`, `html_content/videos/`
- Content displays edge-to-edge in an iframe served from `http://localhost:8080/content/<file>`
- Map new files to chips via the Tag Management Interface

## 🚀 Autostart (Museum / Exhibition Mode)

For unattended installations where staff simply turn on the power each morning.

### What `install_autostart.sh` does

1. **Installs a systemd service** (`hcmp-display`) that starts the NFC display backend (`nfc_display.py`) at boot — this is the Python server that talks to the reader and serves content on port 8080
2. **Registers the kiosk launcher** (`kiosk.sh`) in three autostart mechanisms — LXDE, XDG, and labwc — so it works on both X11 desktops and newer Wayland-based Raspberry Pi OS images. A file lock inside `kiosk.sh` guarantees only one kiosk instance ever launches, no matter how many mechanisms fire
3. **Disables screen blanking** (via raspi-config and `xset`)
4. **Enables desktop auto-login**

`kiosk.sh` itself waits for the backend to respond (up to 60 s), picks the right Chromium binary, launches it fullscreen, and — via `xdotool` — sends a single automatic F5 shortly after launch to work around Chromium's blank first paint on cold boot.

The installer is **safe to re-run** at any time (e.g. after a `git pull`): it replaces its own entries between `# --- HCMP START/END ---` markers without duplicating anything.

### Boot sequence after installation

1. Pi powers on and boots the OS
2. Auto-login to the desktop (no password prompt)
3. systemd starts the NFC display backend
4. Chromium opens in fullscreen kiosk mode
5. The home screen appears — ready for visitors

### Making changes while autostart is active

No need to uninstall anything. Open a terminal and stop the service:

```bash
sudo systemctl stop hcmp-display
```

Close Chromium (Alt+F4), do your work (map chips, edit HTML, `git pull`, …), then reboot — or restart manually with `sudo systemctl start hcmp-display`.

### Removing autostart

```bash
./uninstall_autostart.sh
```

Removes the service and all three kiosk autostart entries. Auto-login and screen blanking settings are left as-is (adjust via `sudo raspi-config` if needed).

### Useful commands

```bash
sudo systemctl stop hcmp-display      # Stop the display backend
sudo systemctl start hcmp-display     # Start the display backend
sudo systemctl status hcmp-display    # Check if it's running
sudo journalctl -u hcmp-display -f    # View live logs
./check_status.sh                     # Overview of everything
./kiosk.sh                            # Launch the kiosk manually
```

## 🎨 Customization

### Home screen appearance

Edit `nfc_display.py` to customize the title text, colors and gradients, animations, and the NFC icon.

### Example content structure

```
html_content/
├── hundekopf_video.html   # Exhibit page (video)
├── zeus.html              # Exhibit page
├── template_object.html   # Reusable templates
├── images/                # Shared images
├── videos/                # Video files (gitignored — copy manually)
├── models/                # 3D models
└── js/                    # Shared scripts
```

## 🛠️ Troubleshooting

### Check system status

```bash
./check_status.sh
```

Shows the service state, running processes, ports, and mappings file.

### NFC not detecting

Work through these in order — they cover the failure modes by frequency:

1. **Serial console still active** — re-check Step 2 of the setup: the login shell over serial must be **disabled** and `console=serial0,115200` must be gone from `cmdline.txt`. This is the #1 cause on a fresh Pi.
2. **HAT switches** — DIP switch must be exactly `RX ON, TX ON, all others OFF`; jumpers I0 and I1 both on **L**; RSTPDN→D20 jumper cap in place. Power off before correcting.
3. **Serial port held by another process** — the display backend (`hcmp-display` service) holds `/dev/ttyS0` exclusively. Stop it before running `nfc_web_server.py` or any test script: `sudo systemctl stop hcmp-display`
4. **Verify in isolation:** `cd python && python3 example_get_uid.py`
5. **Leftover port lock after an unclean shutdown** — both main scripts flush the serial port on startup, but if the reader still won't respond, a reboot always resolves it.

### Garbled or intermittent NFC data

The mini UART's baud rate depends on the core clock. `enable_uart=1` normally pins it, but if you see corruption at 115200, add `core_freq=250` to `config.txt` and reboot.

### White screen after boot

Chromium's first paint can race the desktop compositor on cold boot. `kiosk.sh` fixes this automatically by sending one F5 via `xdotool` a few seconds after launch. If you see a lasting white screen, `xdotool` is probably missing — press F5 once, and install it for next time (`sudo apt install xdotool`, requires internet).

### Screen goes black after a while

Screen blanking must be off. `install_autostart.sh` handles this, but to check manually: `sudo raspi-config` → **Display Options → Screen Blanking → No**.

### Port already in use

- Mapping interface: port **5000**
- Display system: port **8080**

`./check_status.sh` shows what's holding them.

### View logs

```bash
sudo journalctl -u hcmp-display -f
```

## 📁 Project Structure

```
HapticCollectionMediaPlayer/
├── Core System
│   ├── nfc_display.py            # Display backend (port 8080)
│   ├── nfc_web_server.py         # Tag mapping interface (port 5000)
│   └── web_interface/            # Mapping interface UI files
│
├── Setup
│   ├── setup_system_packages.sh  # Dependency installer (system Python)
│   ├── requirements-rpi.txt      # Python packages (Raspberry Pi)
│   ├── requirements.txt          # Python packages (development machines)
│   └── make_executable.sh        # chmod helper
│
├── Autostart
│   ├── install_autostart.sh      # Set up boot-to-display
│   ├── uninstall_autostart.sh    # Remove autostart
│   ├── kiosk.sh                  # Chromium kiosk launcher
│   └── hcmp-display.service      # systemd service template
│
├── Development Helpers
│   ├── start_display_simple.sh   # Windowed mode
│   ├── start_demo.sh             # Demo mode (no NFC hardware)
│   ├── nfc_display_demo.py       # Demo backend
│   └── check_status.sh           # System status overview
│
├── Content & Data
│   ├── html_content/             # Your HTML files and assets
│   └── nfc_mappings.json         # Saved mappings (gitignored!)
│
└── Libraries
    └── python/                   # PN532 drivers + hardware test scripts
```

## 💡 Tips

- **Back up `nfc_mappings.json`** — it is gitignored and lives only on the device
- **Test content first** with demo mode (`./start_demo.sh`) — works on any machine, no hardware needed
- **Optimize for your display** — design HTML for the exhibition screen's resolution
- **Deploying multiple units?** Cloning the SD card of a working Pi is the fastest and safest path
- **Everything internet-dependent happens before deployment** — clone, dependencies, xdotool; the exhibition Pi is offline
- **The reader works through thin materials** — it can be hidden under a surface

## 🔒 Security Note

This system is designed for local networks and trusted environments. For public installations:
- Run on an isolated network
- Restrict file system access
- Use a read-only file system
- Disable unnecessary services

## 📄 License

This project is licensed under a Modified MIT License (Non-Commercial) - see the [LICENSE.txt](LICENSE.txt) file for details.

**Key points:**
- ✅ Free to use, modify, and share for non-commercial purposes
- ✅ Attribution required (Lucas Latzel and Nils Schnorr)
- ❌ Commercial use prohibited
- 📚 Please cite our work if used in research (see LICENSE.txt)

## Acknowledgments

Built with:
- Flask web framework
- PN532 NFC library by Waveshare/Yehui ([Wiki](https://www.waveshare.com/wiki/PN532_NFC_HAT))
- Threejs-gltf-import from dgreenheck (https://github.com/dgreenheck/threejs-gltf-import/tree/main)

**Special thanks to:**
- Jürgen Schnorr for providing us with the required hardware and helping us with the first iteration of code

---

**Repository:** https://github.com/NilsSchnorr/HapticCollectionMediaPlayer

For issues, questions, or contributions, please visit the project repository.
