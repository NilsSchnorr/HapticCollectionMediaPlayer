// js/draco-setup.js
// -----------------------------------------------------------------------------
// Enables OFFLINE Draco decoding for the HCMP Medienstation — centrally, so the
// DRACOLoader does NOT have to be wired up in every single page.
//
// Include this AFTER three.min.js, GLTFLoader.js and DRACOLoader.js, e.g.:
//     <script src="js/three.min.js"></script>
//     <script src="js/GLTFLoader.js"></script>
//     <script src="js/DRACOLoader.js"></script>
//     <script src="js/draco-setup.js"></script>
//
// From then on, every THREE.GLTFLoader created on the page automatically gets a
// shared DRACOLoader (decoder files expected in js/draco/). You can just call
// loader.load('models/foo.glb', ...) as usual — Draco-compressed models will
// decode locally, no internet / CDN needed.
//
// Non-Draco models are unaffected: the decoder is only invoked when a model
// actually uses the KHR_draco_mesh_compression extension.
// -----------------------------------------------------------------------------
(function () {
  if (typeof THREE === 'undefined' || !THREE.GLTFLoader || !THREE.DRACOLoader) {
    console.warn('[draco-setup] THREE.GLTFLoader or THREE.DRACOLoader not found — ' +
                 'load three.min.js, GLTFLoader.js and DRACOLoader.js before draco-setup.js.');
    return;
  }

  // One shared decoder instance for the whole page (it manages its own worker).
  var dracoLoader = new THREE.DRACOLoader();
  dracoLoader.setDecoderPath('js/draco/');

  // Auto-attach the shared DRACOLoader to every GLTFLoader instance the first
  // time it loads something, unless one was already set manually.
  var originalLoad = THREE.GLTFLoader.prototype.load;
  THREE.GLTFLoader.prototype.load = function () {
    if (!this.dracoLoader) {
      this.setDRACOLoader(dracoLoader);
    }
    return originalLoad.apply(this, arguments);
  };
})();
