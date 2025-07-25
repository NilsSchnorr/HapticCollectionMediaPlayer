# Web Interface User Guide

The NFC Tag Management Web Interface provides an easy way to manage your NFC tags without using the command line.

## Starting the Web Interface

1. **On the Raspberry Pi:**
   ```bash
   ./start_web_interface.sh
   ```

2. **Access from a browser:**
   - Local: http://localhost:5000
   - Network: http://[your-pi-ip-address]:5000

## Using the Interface

### Main Dashboard

The interface shows three main sections:

1. **Tag Scanner** - Real-time tag detection
2. **Quick Actions** - Refresh controls
3. **Registered Tags** - List of all configured tags

### Managing Tags

#### Adding a New Tag

1. Place an unregistered NFC tag on the reader
2. The scanner will detect it and show "New tag detected!"
3. Fill in the form:
   - **Tag Name**: A friendly name (e.g., "Meeting Room Schedule")
   - **HTML File**: Select from the dropdown of available HTML files
   - **Description**: Optional notes about the tag
4. Click "Save Tag"

#### Editing an Existing Tag

1. **Method 1**: Place the tag on the reader - its current settings will appear
2. **Method 2**: Click "Edit" next to any tag in the list
3. Update the settings and click "Save Tag"

#### Deleting a Tag

1. Click "Delete" next to the tag in the list
2. Confirm the deletion

### Viewing Access Logs

Click "Logs" next to any tag to see when it was scanned.

## Tips

- **Real-time Updates**: The interface updates automatically when tags are detected
- **Multiple Browsers**: You can open the interface on multiple devices simultaneously
- **HTML Files**: Add new HTML files to the `html/` directory and click "Refresh HTML Files"

## Running as a Service

To run the web interface automatically on boot:

```bash
sudo cp nfc-web-interface.service /etc/systemd/system/
sudo systemctl enable nfc-web-interface.service
sudo systemctl start nfc-web-interface.service
```

## Troubleshooting

- **Connection Failed**: Ensure the web interface is running and check the IP address
- **Tag Not Detected**: Check that the main NFC reader service has permissions
- **No HTML Files**: Ensure HTML files are in the correct directory (`html/`)
