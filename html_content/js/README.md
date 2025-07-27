# Three.js Library Files for Offline Use

To make the 3D viewer work offline, you need to download these Three.js library files and place them in the `js/` folder.

## Download Links

1. **three.min.js** (Main Three.js library)
   - Download from: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
   - Save as: `js/three.min.js`

2. **GLTFLoader.js** (For loading 3D models)
   - Download from: https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js
   - Save as: `js/GLTFLoader.js`

3. **OrbitControls.js** (For camera controls)
   - Download from: https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js
   - Save as: `js/OrbitControls.js`

## Quick Download Commands (macOS/Linux)

Run these commands from the `html_content` directory:

```bash
# Create js directory if it doesn't exist
mkdir -p js

# Download Three.js files
curl -o js/three.min.js https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js
curl -o js/GLTFLoader.js https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js
curl -o js/OrbitControls.js https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js
```

## Verification

After downloading, your directory structure should look like:
```
html_content/
├── js/
│   ├── three.min.js
│   ├── GLTFLoader.js
│   └── OrbitControls.js
├── models/
│   └── (your 3D model files)
└── zeus.html
```

Now your 3D viewer will work completely offline!
