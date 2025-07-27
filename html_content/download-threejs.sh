#!/bin/bash
# Download Three.js libraries for offline use
# Three.js is used under the MIT License - see js/LICENSE for details

echo "Downloading Three.js libraries for offline use..."
echo "Three.js is distributed under the MIT License"

# Create js directory if it doesn't exist
mkdir -p js

# Download Three.js core library
echo "Downloading three.min.js..."
curl -o js/three.min.js https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js

# Download GLTFLoader
echo "Downloading GLTFLoader.js..."
curl -o js/GLTFLoader.js https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js

# Download OrbitControls
echo "Downloading OrbitControls.js..."
curl -o js/OrbitControls.js https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js

echo "Done! Three.js libraries downloaded to js/ folder"
echo "Your 3D viewer will now work offline."
