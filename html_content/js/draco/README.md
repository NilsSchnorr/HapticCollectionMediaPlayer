# Draco decoder (offline) — for the HCMP Medienstation

These are the Draco decoder files that THREE.DRACOLoader loads locally so that
Draco-compressed glTF/GLB models display **offline** on the Raspberry Pi
(no CDN access needed).

- Source: three.js **r128**, `examples/js/libs/draco/gltf/`
- Variant: **glTF** build, targeted at the `KHR_draco_mesh_compression`
  extension (i.e. exactly the compression used by our .glb/.gltf models).
  Smaller than the "default" build, which is better for the Pi.
- Draco license: Apache License 2.0 (Google) — https://github.com/google/draco

Files:
- `draco_decoder.wasm`      — WebAssembly decoder (used by default; fast on the Pi)
- `draco_wasm_wrapper.js`   — JS wrapper that loads the WASM decoder
- `draco_decoder.js`        — pure-JS fallback (used only if WASM is unavailable)

## How it is wired up (recommended: central, one-time)
Include these scripts in each model page, in this order:

```html
<script src="js/three.min.js"></script>
<script src="js/GLTFLoader.js"></script>
<script src="js/DRACOLoader.js"></script>
<script src="js/draco-setup.js"></script>
```

`js/draco-setup.js` attaches a shared DRACOLoader (pointing at this folder) to
every GLTFLoader automatically, so no per-page JavaScript is needed. Just call
`loader.load('models/xxx.glb', ...)` as usual.

## Alternative (manual, per loader)
If you prefer to wire it up explicitly instead of using draco-setup.js:

```js
const loader = new THREE.GLTFLoader();
const dracoLoader = new THREE.DRACOLoader();
dracoLoader.setDecoderPath('js/draco/');   // <- this folder
loader.setDRACOLoader(dracoLoader);
```

## Updating later
If three.js is ever upgraded, replace these files with the matching
`examples/js/libs/draco/gltf/` files from the same three.js release, and
replace `js/DRACOLoader.js` with that release's `examples/js/loaders/DRACOLoader.js`.
