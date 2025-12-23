# Lighting & Atmosphere System

The Lighting & Atmosphere System provides professional-quality cinematic lighting for your Blender scenes through HDRI environments, multi-light rigs, volumetric atmosphere, camera configuration, and render settings.

## Table of Contents
- [Quick Start](#quick-start)
- [HDRI Lighting](#hdri-lighting)
- [Lighting Rigs](#lighting-rigs)
- [Atmospheric Effects](#atmospheric-effects)
- [Camera Setup](#camera-setup)
- [Render Configuration](#render-configuration)
- [Auto Scene Setup](#auto-scene-setup)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)

## Quick Start

### Auto Setup (Recommended)
The fastest way to get professional lighting:

```python
# Automatically configure everything based on scene description
auto_setup_scene_lighting(
    scene_description="outdoor product shot",
    target_object="MyObject"
)
```

This single command sets up:
- ✅ HDRI environment lighting
- ✅ Multi-light rig
- ✅ Volumetric atmosphere
- ✅ Camera with proper framing
- ✅ Render engine and quality settings

### Manual Setup
For more control:

```python
# 1. Set up HDRI environment
setup_hdri_lighting(preset="studio")

# 2. Add lighting rig
apply_lighting_rig(preset="three_point")

# 3. Add atmosphere
add_atmospheric_fog(preset="fog")

# 4. Position camera
setup_camera(preset="normal", target_object="MyObject")

# 5. Configure rendering
configure_render_settings(preset="preview")
```

## HDRI Lighting

HDRI (High Dynamic Range Imaging) provides realistic environment lighting.

### Available HDRI Presets

#### studio
Neutral studio lighting with soft shadows
- **Use for**: Product photography, commercial renders
- **Strength**: 1.0
- **Background**: Hidden
- **Recommended HDRIs**: studio_small_03, photo_studio_01, industrial_sunset

#### outdoor_day
Bright outdoor daylight
- **Use for**: Outdoor scenes, architecture, vehicles
- **Strength**: 1.0
- **Background**: Visible
- **Recommended HDRIs**: kloppenheim_02, venice_sunset, syferfontein_18d

#### sunset
Warm golden hour lighting
- **Use for**: Dramatic scenes, portraits, cinematic shots
- **Strength**: 0.8
- **Background**: Visible
- **Recommended HDRIs**: venice_sunset, artist_workshop, kiara_1_dawn

#### night
Night city or moonlight
- **Use for**: Night scenes, urban environments
- **Strength**: 0.3
- **Background**: Visible
- **Recommended HDRIs**: night_street, moonlit_golf, starmap_2020

#### overcast
Soft overcast sky
- **Use for**: Even lighting, diffused shadows
- **Strength**: 0.9
- **Background**: Visible
- **Recommended HDRIs**: kloofendal_43d_clear, cloudy_vondelpark, kloppenheim_06

#### interior
Interior ambient lighting
- **Use for**: Indoor scenes, rooms
- **Strength**: 0.7
- **Background**: Hidden
- **Recommended HDRIs**: leadenhall_market, St_Peters_Square, wooden_lounge

### Usage Examples

```python
# Basic HDRI setup
setup_hdri_lighting(preset="studio")

# Custom parameters
setup_hdri_lighting(
    preset="sunset",
    rotation=45.0,        # Rotate environment
    strength=1.2,         # Increase brightness
    background_strength=0.5  # Semi-transparent background
)
```

### Downloading HDRIs from PolyHaven

The system works with PolyHaven HDRIs. To download and use:

```python
# Download HDRI from PolyHaven
download_polyhaven_asset(
    asset_id="venice_sunset",
    asset_type="hdris",
    resolution="2k"
)

# Then apply HDRI preset
setup_hdri_lighting(preset="sunset")
```

## Lighting Rigs

Lighting rigs add multiple positioned lights to create depth and dimension.

### Available Lighting Rigs

#### three_point
Classic 3-point lighting (key, fill, rim)
- **Lights**: 3 area lights
- **Use for**: General purpose, portraits, product shots
- **Key Light**: 500W at 45° (warm)
- **Fill Light**: 200W opposite side (cool)
- **Rim Light**: 300W from behind

#### studio
Studio product photography lighting
- **Lights**: 4 area lights
- **Use for**: Commercial photography, clean product shots
- **Main Light**: 400W front-side
- **Side Fill**: 250W side
- **Back Light**: 200W rear
- **Top Light**: 150W overhead

#### dramatic
High contrast dramatic lighting
- **Lights**: 2 lights (spot + area)
- **Use for**: Cinematic, moody, high-contrast scenes
- **Key Light**: 1000W spotlight (warm)
- **Fill Light**: 50W subtle fill (cool)

#### outdoor
Natural outdoor lighting simulation
- **Lights**: 2 lights (sun + sky)
- **Use for**: Outdoor scenes, natural lighting
- **Sun**: Directional sun light
- **Sky Fill**: Large area light (blue tint)

#### night
Night scene with street lights
- **Lights**: 3 area lights
- **Use for**: Night urban scenes
- **Street Lights**: 2x 400W (warm orange)
- **Moon Fill**: 50W large area (cool blue)

### Usage Examples

```python
# Apply standard rig
apply_lighting_rig(preset="three_point")

# Scale rig for larger scenes
apply_lighting_rig(
    preset="studio",
    scale=2.0  # 2x distance from origin
)
```

## Atmospheric Effects

Volumetric atmosphere adds depth, fog, and light scattering.

### Available Atmosphere Presets

#### fog
Volumetric fog for depth and atmosphere
- **Density**: 0.05
- **Anisotropy**: 0.1
- **Color**: Cool grey-blue
- **Use for**: Moody scenes, depth

#### heavy_fog
Dense fog for moody scenes
- **Density**: 0.15
- **Anisotropy**: 0.2
- **Color**: Dense grey
- **Use for**: Horror, mystery, dramatic scenes

#### god_rays
Light shafts through atmosphere
- **Density**: 0.03
- **Anisotropy**: 0.5 (high for visible rays)
- **Color**: Warm
- **Use for**: Dramatic lighting, forest scenes, church interiors

#### haze
Subtle atmospheric haze
- **Density**: 0.01
- **Anisotropy**: 0.05
- **Color**: Very subtle blue tint
- **Use for**: Outdoor scenes, subtle depth

#### none
Clear atmosphere
- **Use for**: Studio shots, clear visibility

### Usage Examples

```python
# Add fog
add_atmospheric_fog(preset="fog")

# Custom density
add_atmospheric_fog(
    preset="god_rays",
    density=0.05  # Override preset density
)

# Clear atmosphere
add_atmospheric_fog(preset="none")
```

### Render Settings for Volumetrics

Volumetric effects require proper render settings:

```python
# Cycles (recommended for volumetrics)
configure_render_settings(preset="production")  # Enables volumetrics

# Eevee (faster but less accurate)
configure_render_settings(preset="preview")  # Also enables volumetrics
```

## Camera Setup

Professional camera configuration with focal length and depth of field.

### Available Camera Presets

#### portrait
Portrait focal length (85mm equivalent)
- **Focal Length**: 85mm
- **DOF**: Enabled (f/2.8)
- **Use for**: Character shots, portraits, hero objects

#### wide
Wide angle (24mm equivalent)
- **Focal Length**: 24mm
- **DOF**: Disabled (f/8.0)
- **Use for**: Architecture, interiors, landscapes

#### normal
Normal view (50mm equivalent)
- **Focal Length**: 50mm
- **DOF**: Enabled (f/5.6)
- **Use for**: General purpose, product shots

#### telephoto
Telephoto (135mm equivalent)
- **Focal Length**: 135mm
- **DOF**: Enabled (f/2.0)
- **Use for**: Compressed perspective, shallow DOF

#### architectural
Architectural (35mm, no distortion)
- **Focal Length**: 35mm
- **DOF**: Disabled (f/11.0)
- **Use for**: Architecture, technical renders

### Camera Positions

- **three_quarter**: 45° angle (default, most cinematic)
- **front**: Straight on
- **side**: 90° side view
- **top**: Top-down orthographic-style

### Usage Examples

```python
# Auto-position camera on object
setup_camera(
    preset="portrait",
    position="three_quarter",
    target_object="Character"
)

# Custom camera settings
setup_camera(
    preset="normal",
    focal_length=75,    # Override focal length
    f_stop=1.8,         # Shallow depth of field
    target_object="Product"
)
```

### Camera Framing

The system automatically frames the camera based on the target object's bounding box:
- Calculates optimal distance based on object size
- Points camera at object center
- Applies depth of field focus to target

## Render Configuration

Configure render engine and quality settings.

### Available Render Presets

#### draft
Fast preview render
- **Engine**: Eevee
- **Samples**: 64
- **Resolution**: 50%
- **Denoising**: Enabled
- **Use for**: Quick previews, iteration

#### preview
Quick quality check
- **Engine**: Cycles
- **Samples**: 128
- **Resolution**: 75%
- **Denoising**: Enabled
- **Use for**: Quality checks, work-in-progress

#### production
High quality for final output
- **Engine**: Cycles
- **Samples**: 512
- **Resolution**: 100%
- **Denoising**: Enabled
- **Use for**: Final renders, presentations

#### final
Maximum quality
- **Engine**: Cycles
- **Samples**: 2048
- **Resolution**: 100%
- **Denoising**: Disabled
- **Use for**: Publication, print, portfolio

### Usage Examples

```python
# Set render quality
configure_render_settings(preset="production")

# Custom resolution
configure_render_settings(
    preset="preview",
    resolution_x=2560,
    resolution_y=1440
)
```

### Render Engine Comparison

**Cycles (Ray Tracing)**
- More realistic
- Better volumetrics
- Slower
- Recommended for final output

**Eevee (Rasterization)**
- Faster
- Real-time preview
- Good for iteration
- Recommended for drafts

## Auto Scene Setup

The `auto_setup_scene_lighting()` function automatically configures all lighting aspects based on scene description.

### How It Works

1. Analyzes scene description for keywords
2. Selects appropriate presets for each component
3. Applies HDRI, lights, atmosphere, camera, render settings
4. Returns complete summary

### Scene Type Detection

The system automatically detects scene type from description:

| Keywords | Scene Type | HDRI | Lighting Rig | Atmosphere | Camera |
|----------|------------|------|--------------|------------|--------|
| outdoor, street, city | Outdoor | outdoor_day | outdoor | haze | normal |
| night, evening, dark | Night | night | night | fog | normal |
| studio, product | Product | studio | studio | none | portrait |
| dramatic, cinematic | Dramatic | sunset | dramatic | god_rays | portrait |
| interior, room, indoor | Interior | interior | three_point | haze | wide |

### Usage Examples

```python
# Outdoor scene
auto_setup_scene_lighting(
    scene_description="outdoor product shot in daylight",
    target_object="Product"
)

# Dramatic portrait
auto_setup_scene_lighting(
    scene_description="dramatic cinematic portrait",
    target_object="Character"
)

# Night scene
auto_setup_scene_lighting(
    scene_description="night street scene with fog",
    target_object="Building"
)

# Studio product
auto_setup_scene_lighting(
    scene_description="studio product photography",
    target_object="Watch"
)
```

## API Reference

### MCP Tools

#### setup_hdri_lighting()
```python
setup_hdri_lighting(
    preset: str = "studio",
    rotation: float = None,
    strength: float = None,
    background_strength: float = None
) -> str
```

#### apply_lighting_rig()
```python
apply_lighting_rig(
    preset: str = "three_point",
    scale: float = 1.0
) -> str
```

#### add_atmospheric_fog()
```python
add_atmospheric_fog(
    preset: str = "fog",
    density: float = None
) -> str
```

#### setup_camera()
```python
setup_camera(
    preset: str = "normal",
    position: str = "three_quarter",
    target_object: str = None,
    focal_length: float = None,
    f_stop: float = None
) -> str
```

#### configure_render_settings()
```python
configure_render_settings(
    preset: str = "preview",
    resolution_x: int = 1920,
    resolution_y: int = 1080
) -> str
```

#### auto_setup_scene_lighting()
```python
auto_setup_scene_lighting(
    scene_description: str,
    target_object: str = None
) -> str
```

#### list_lighting_presets()
```python
list_lighting_presets(
    category: str = "all"  # all, hdri, lighting, atmosphere, camera, render
) -> str
```

## Best Practices

### 1. Complete Workflow Integration

Always apply lighting AFTER geometry and materials:

```python
# 1. Import model
import_generated_asset(name="object", ...)

# 2. Enhance geometry
auto_enhance_geometry(object_name="object")

# 3. Enhance materials
auto_enhance_materials(object_name="object")

# 4. Set up lighting ← THIS STEP
auto_setup_scene_lighting(
    scene_description="dramatic product shot",
    target_object="object"
)

# 5. Verify
get_viewport_screenshot()
```

### 2. Scene-Appropriate Lighting

Choose lighting that matches your subject:

- **Product Photography**: studio HDRI + studio rig + none atmosphere
- **Outdoor Scenes**: outdoor_day HDRI + outdoor rig + haze atmosphere
- **Dramatic/Cinematic**: sunset HDRI + dramatic rig + god_rays atmosphere
- **Night Scenes**: night HDRI + night rig + fog atmosphere
- **Character Portraits**: studio/sunset HDRI + three_point rig + haze atmosphere

### 3. Render Quality Progression

Start fast, increase quality incrementally:

1. **Draft** (Eevee, 64 samples): Initial setup and positioning
2. **Preview** (Cycles, 128 samples): Check lighting and composition
3. **Production** (Cycles, 512 samples): Final review
4. **Final** (Cycles, 2048 samples): Only when completely satisfied

### 4. Camera Framing

- Use `target_object` parameter to auto-frame on your subject
- `three_quarter` position is most cinematic for products
- `wide` lens for architecture and interiors
- `portrait` or `telephoto` lens for shallow depth of field

### 5. Atmospheric Effects

- Start subtle (haze) and increase if needed
- god_rays require strong directional light
- Heavy fog reduces visibility - use sparingly
- Volumetrics increase render time significantly

### 6. HDRI + Light Rigs

Combine for best results:
- HDRI provides ambient environment lighting
- Light rigs add controlled directional light
- Together they create depth and dimension

### 7. Custom Adjustments

After auto-setup, fine-tune individual elements:

```python
# Auto setup as starting point
auto_setup_scene_lighting("outdoor product", "Product")

# Then adjust specific elements
setup_hdri_lighting(preset="sunset", rotation=90)  # Adjust HDRI rotation
add_atmospheric_fog(preset="haze", density=0.02)   # Reduce fog density
```

## Troubleshooting

### Viewport shows black

**Solution**: Enable viewport shading
- Press `Z` in Blender, select "Rendered" or "Material Preview"

### Fog not visible

**Solution**: 
1. Check render engine supports volumetrics (use Cycles or Eevee)
2. Increase fog density: `add_atmospheric_fog(preset="fog", density=0.1)`
3. In Blender: World Properties → Volume → Ensure Volume Scatter node exists

### Camera not framing object correctly

**Solution**:
1. Ensure `target_object` parameter is correct object name
2. Check object has reasonable bounding box with `get_object_info()`
3. Try different position: `setup_camera(preset="normal", position="front")`

### Render is too dark/bright

**Solution**:
1. Adjust HDRI strength: `setup_hdri_lighting(preset="studio", strength=1.5)`
2. Adjust light rig scale: `apply_lighting_rig(preset="three_point", scale=0.8)`
3. In Blender: Render Properties → Film → Exposure

### Render takes too long

**Solution**:
1. Use lower quality preset: `configure_render_settings(preset="draft")`
2. Reduce resolution: `configure_render_settings(preset="preview", resolution_x=1280, resolution_y=720)`
3. Simplify volumetrics: `add_atmospheric_fog(preset="haze")` instead of heavy_fog

## Examples

### Example 1: Product Photography

```python
# Generate product
generate_hyper3d_model_via_text(text_prompt="modern watch")
import_generated_asset(name="watch", task_uuid="...")

# Enhance
auto_enhance_geometry("watch")
auto_enhance_materials("watch", aggressive=True)

# Studio lighting setup
setup_hdri_lighting(preset="studio")
apply_lighting_rig(preset="studio")
setup_camera(preset="normal", target_object="watch")
configure_render_settings(preset="production")

get_viewport_screenshot()
```

### Example 2: Dramatic Outdoor Scene

```python
# Import model
download_sketchfab_model(uid="abc123")

# Enhance
auto_enhance_geometry("Sketchfab_model")
auto_enhance_materials("Sketchfab_model")

# Dramatic lighting
auto_setup_scene_lighting(
    scene_description="dramatic sunset outdoor scene",
    target_object="Sketchfab_model"
)

# Adjust camera for cinematic framing
setup_camera(
    preset="portrait",
    position="three_quarter",
    target_object="Sketchfab_model",
    f_stop=2.0  # Shallow DOF
)

get_viewport_screenshot()
```

### Example 3: Night Scene

```python
# Generate scene
generate_hyper3d_model_via_images(
    image_urls=["night_street.jpg"]
)
import_generated_asset(name="street", task_uuid="...")

# Enhance
auto_enhance_geometry("street")
auto_enhance_materials("street")

# Night lighting
setup_hdri_lighting(preset="night", strength=0.2)
apply_lighting_rig(preset="night", scale=1.5)
add_atmospheric_fog(preset="fog", density=0.08)
setup_camera(preset="wide", target_object="street")
configure_render_settings(preset="production")

get_viewport_screenshot()
```

## Integration with Other Systems

The Lighting System works seamlessly with Material and Post-Processing systems:

```python
# Complete enhancement pipeline
def enhance_model(object_name, scene_type):
    # 1. Geometry
    auto_enhance_geometry(object_name)
    
    # 2. Materials
    auto_enhance_materials(object_name, aggressive=True)
    
    # 3. Lighting
    auto_setup_scene_lighting(scene_type, object_name)
    
    # 4. Verify
    return get_viewport_screenshot()

# Usage
enhance_model("MyObject", "dramatic outdoor product")
```

---

**Next Steps**:
- Review [MATERIAL_SYSTEM.md](MATERIAL_SYSTEM.md) for material presets
- Review [POST_PROCESSING.md](POST_PROCESSING.md) for geometry enhancement
- Experiment with different preset combinations
- Use `list_lighting_presets()` to explore all options
