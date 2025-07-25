# PN532 NFC HAT Setup Guide

This guide specifically covers the setup and configuration of the PN532 NFC HAT for Raspberry Pi.

## Hardware Setup

1. **Install the HAT**:
   - Power off your Raspberry Pi
   - Carefully align the HAT with the GPIO pins
   - Press down firmly until the HAT sits flush on the GPIO header
   - The HAT should cover all 40 GPIO pins

2. **Check Jumper Settings**:
   The PN532 HAT has jumpers to select the communication interface:
   - **I2C** (default): Both jumpers in I2C position
   - **SPI**: Both jumpers in SPI position
   - **UART**: Both jumpers in UART position

## Software Setup

### Automatic Setup

Run the setup script and choose option 1:
```bash
./setup.sh
# Choose: 1) PN532 NFC HAT
```

This will:
- Enable I2C interface
- Install required Python libraries
- Configure the system for the PN532 HAT

### Manual Setup

1. **Enable I2C**:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → I2C → Enable
   ```

2. **Install I2C tools**:
   ```bash
   sudo apt-get update
   sudo apt-get install i2c-tools
   ```

3. **Add user to i2c group**:
   ```bash
   sudo usermod -a -G i2c $USER
   # Log out and back in for changes to take effect
   ```

4. **Verify I2C connection**:
   ```bash
   sudo i2cdetect -y 1
   ```
   You should see a device at address `24`.

## Configuration

The system is pre-configured for I2C interface. If you need to change it, edit `config.py`:

```python
# For I2C (default for HAT)
PN532_INTERFACE = 'i2c'

# For SPI (if jumpers set to SPI)
PN532_INTERFACE = 'spi'

# For UART (if jumpers set to UART)
PN532_INTERFACE = 'uart'
```

## Troubleshooting

### HAT Not Detected

1. **Check physical connection**:
   - Ensure HAT is properly seated
   - No bent pins
   - HAT is powered (LED indicators)

2. **Verify I2C is enabled**:
   ```bash
   ls /dev/i2c*
   # Should show /dev/i2c-1
   ```

3. **Check I2C detection**:
   ```bash
   sudo i2cdetect -y 1
   ```

4. **Permission issues**:
   ```bash
   # Run with sudo if needed
   sudo python3 main.py
   
   # Or ensure user is in i2c group
   groups $USER
   ```

### Switching Interfaces

If I2C doesn't work, try SPI:

1. **Move jumpers to SPI position**
2. **Enable SPI**:
   ```bash
   sudo raspi-config
   # Interface Options → SPI → Enable
   ```
3. **Edit config.py**:
   ```python
   PN532_INTERFACE = 'spi'
   ```

## LED Indicators

The PN532 HAT has LEDs that indicate status:
- **Power LED**: Should be on when powered
- **Activity LED**: Blinks during NFC operations

## Compatible NFC Tags

The PN532 HAT supports:
- ISO14443A (Mifare Classic, Mifare Ultralight)
- ISO14443B
- FeliCa
- ISO18092 (NFC peer-to-peer)

Most common NFC tags and cards will work perfectly.

## Performance Tips

1. **Tag Detection Range**: 
   - Optimal: 0-5cm
   - Maximum: ~10cm (depends on tag size)

2. **Tag Placement**:
   - Place tags parallel to the antenna
   - Center the tag over the antenna area
   - Remove metal objects nearby

3. **Read Speed**:
   - The system polls every 100ms by default
   - Adjust `READ_INTERVAL` in `config.py` if needed

## Next Steps

Once the HAT is working:
1. Test with `python3 test_presence.py`
2. Configure tags using the web interface
3. Run the main display system

Remember: The PN532 HAT is more reliable than USB adapters and provides better integration with the Raspberry Pi!
