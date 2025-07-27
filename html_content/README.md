# NFC Object Display Templates

This directory contains HTML templates for displaying objects with 3D models when NFC chips are detected.


## Files

1. **zeus.html** - A complete example page for the Zeus object with two-row layout
3. **object_template.html** - A generic template that can be customized for any object
4. **models/** - Directory for storing 3D model files (GLTF/GLB format)
5. **images/** - Directory for storing reference images

## Using the Generic Template

To create a new object page using `object_template.html`:

1. Copy the template file and rename it (e.g., `athena.html`)
2. Replace the following placeholders:

### First Row (Main Content)
   - `{{OBJECT_NAME}}` - The main title (e.g., "Athena")
   - `{{OBJECT_SUBTITLE}}` - Subtitle or tagline (e.g., "Goddess of Wisdom and Warfare")
   - `{{MAIN_DESCRIPTION}}` - Main paragraph describing the object
   - `{{INFO_BOX_CONTENT}}` - Quick facts in the info box (use `<br>` for line breaks)
   - `{{SECTION_1_TITLE}}` - First section heading
   - `{{SECTION_1_CONTENT}}` - First section content
   - `{{SECTION_2_TITLE}}` - Second section heading
   - `{{SECTION_2_CONTENT}}` - Second section content
   - `{{TAG_1}}`, `{{TAG_2}}`, `{{TAG_3}}`, `{{TAG_4}}` - Metadata tags
   - `{{MODEL_FILENAME}}` - The filename of your 3D model (e.g., `athena.gltf`)

### Second Row (Image and Details)
   - `{{IMAGE_PATH}}` - Path to reference image (e.g., `images/athena-reference.jpg`)
   
   **Object Information (Middle Panel):**
   - `{{DATING}}` - Time period/date of the object
   - `{{ORIGIN}}` - Where the object is from
   - `{{MATERIAL}}` - What the object is made of
   - `{{DIMENSIONS}}` - Size of the object
   - `{{CONSERVATION_STATUS}}` - Current condition
   
   **Collection Metadata (Right Panel):**
   - `{{COLLECTION}}` - Which collection it belongs to
   - `{{INVENTORY_NUMBER}}` - Catalog/inventory number
   - `{{ACQUISITION}}` - How and when it was acquired
   - `{{DISPLAY_LOCATION}}` - Where it's currently displayed
   - `{{LAST_UPDATED}}` - When the information was last updated

## Adding 3D Models

1. Place your GLTF/GLB model files in the `models/` directory
2. Update the `MODEL_PATH` variable in the JavaScript section to point to your model
3. The template will automatically handle loading, centering, and scaling the model

## 3D Model Requirements

- **Format**: GLTF (.gltf) or GLB (.glb) files
- **Size**: Keep models under 10MB for best performance
- **Textures**: Embed textures or place them in the same directory as the model
- **Animations**: The template supports animated models automatically

## Reference Image Requirements

- **Location**: Place images in the `images/` directory
- **Format**: JPG, PNG, or WebP
- **Size**: Recommended max width of 800px for web performance
- **Naming**: Use descriptive names (e.g., `zeus-statue-front.jpg`)

## Features

- **Font Size Controls**: 
  - Two buttons in the top-left corner (small A and large A)
  - Adjustable from 70% to 150% of default size
  - Changes apply to current session only
- **Two-Row Layout**: 
  - First row: Text content and 3D model viewer
  - Second row: Reference image and split information panels
- **Three-Panel Second Row**:
  - Left: Reference image
  - Middle: Object Information (physical details)
  - Right: Collection Metadata (administrative details)
- **Responsive Design**: Works on desktop and mobile devices
- **3D Controls**: 
  - Mouse/touch rotation
  - Zoom in/out
  - Reset view button
  - Toggle auto-rotation
  - Wireframe mode
- **Professional Styling**: Clean, scientific presentation
- **Loading States**: Shows spinner while model loads
- **Fallback**: Shows placeholder if model fails to load
- **Scrollable**: Entire page scrolls for longer content

## Color Scheme

The template uses a professional, scientific dark theme with purple accents:
- Background: #0a0a0a (deep black)
- Header: #1a1a2e (dark blue-gray)
- Primary Accent: #667eea (purple)
- Text: #ffffff (white) and #e0e0e0 (light gray for body text)
- Cards: #1a1a2e with minimal borders (#2a2a3e)
- Buttons: Transparent with purple borders, purple fill on hover
- Info boxes: Black background with purple borders
- No shadows, gradients, or blur effects for a clean, professional look

## Example Info Box Format

```html
<strong>Domain:</strong> Music, Poetry, Prophecy<br>
<strong>Symbol:</strong> Lyre, Laurel Wreath<br>
<strong>Roman Name:</strong> Apollo<br>
<strong>Parents:</strong> Zeus and Leto
```

## Example Detail Items

The information is now split into two panels:

### Object Information Panel (Physical Details)
**For Archaeological Objects:**
- Dating: 5th century BCE
- Origin: Athens, Greece
- Material: Marble, Pentelic
- Dimensions: Height: 2.13m
- Conservation Status: Excellent condition

**For Modern Artworks:**
- Created: 2023
- Artist: John Doe
- Medium: Bronze and steel
- Dimensions: 150 x 80 x 60 cm
- Condition: Pristine

### Collection Metadata Panel (Administrative Details)
**Standard fields:**
- Collection: Haptic Collection
- Inventory Number: HC-2024-0042
- Acquisition: 2024, Private donation
- Display Location: Gallery 3, Section A
- Last Updated: January 2025

**Additional options:**
- Provenance: Previous ownership history
- Exhibition History: Past displays
- Publications: Referenced in catalogs
- Insurance Value: For internal use
- Access Restrictions: If applicable

## Tips

1. Keep descriptions concise but informative
2. Use the info box for quick reference facts
3. Add relevant metadata tags for categorization
4. Test your 3D models in a GLTF viewer before adding them
5. Optimize models for web use (reduce polygon count if needed)

## Troubleshooting

- **Model not loading**: Check the console for errors, verify the file path
- **Model too dark/bright**: Adjust the lighting values in the JavaScript
- **Performance issues**: Reduce model complexity or texture sizes
- **Model position**: The template auto-centers models, but you can adjust camera position if needed