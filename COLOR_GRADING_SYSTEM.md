# Color Grading System Documentation

## Overview

The Color Grading System provides professional cinematic color grading capabilities for Blender renders. It combines LUTs (Look-Up Tables), tone mapping, and post-processing effects to transform renders from basic to cinematic quality.

**Key Features:**
- 10 LUT presets for lift/gamma/gain color control
- 6 tone mapping configurations
- 8 color effects (vignette, bloom, grain, etc.)
- 8 complete color grade presets combining all elements
- Automatic scene-based color grading
- Compositor node-based workflow

## Quick Start

### Automatic Color Grading (Recommended)

The fastest way to apply professional color grading:

```python
# Let AI choose the best color grade for your scene
auto_grade_scene(
    scene_description="dramatic product shot",
    lighting_type="outdoor"
)
```

### Apply Complete Presets

For specific looks, use complete color grade presets:

```python
# Hollywood blockbuster look (teal & orange)
apply_color_grade(preset="blockbuster")

# Product photography
apply_color_grade(preset="product_showcase")

# Film noir black and white
apply_color_grade(preset="noir_classic")

# Vintage faded film
apply_color_grade(preset="vintage_nostalgia")
```

### List All Options

```python
# See all available presets
list_color_presets(preset_type="all")

# See only LUTs
list_color_presets(preset_type="lut")

# See only effects
list_color_presets(preset_type="effects")
```

## Complete Color Grade Presets

These presets combine LUT + tone mapping + effects for one-step cinematic looks:

### 1. cinematic_standard
**Description:** Clean professional look with subtle enhancements  
**LUT:** cinematic_neutral  
**Tone Mapping:** filmic  
**Effects:** vignette_subtle, film_grain_light  
**Ideal for:** General, professional, cinematic work

**Example:**
```python
apply_color_grade(preset="cinematic_standard")
```

### 2. blockbuster
**Description:** Hollywood action movie look with teal shadows and orange highlights  
**LUT:** teal_orange  
**Tone Mapping:** filmic_high_contrast  
**Effects:** vignette_subtle, bloom_subtle  
**Ideal for:** Action, dramatic, commercial

**Example:**
```python
apply_color_grade(preset="blockbuster")
```

### 3. product_showcase
**Description:** Clean, vibrant look for product photography  
**LUT:** vibrant_pop  
**Tone Mapping:** filmic  
**Effects:** vignette_subtle  
**Ideal for:** Product, advertising, commercial

**Example:**
```python
apply_color_grade(preset="product_showcase")
```

### 4. moody_portrait
**Description:** Dark, atmospheric portrait look  
**LUT:** moody_dark  
**Tone Mapping:** filmic_high_contrast  
**Effects:** vignette_strong, film_grain_light  
**Ideal for:** Portrait, moody, dramatic

**Example:**
```python
apply_color_grade(preset="moody_portrait")
```

### 5. vintage_nostalgia
**Description:** Retro faded film aesthetic  
**LUT:** vintage_film  
**Tone Mapping:** filmic_low_contrast  
**Effects:** vignette_subtle, film_grain_heavy  
**Ideal for:** Vintage, retro, nostalgic

**Example:**
```python
apply_color_grade(preset="vintage_nostalgia")
```

### 6. noir_classic
**Description:** Classic film noir black and white  
**LUT:** film_noir  
**Tone Mapping:** filmic_high_contrast  
**Effects:** vignette_strong, film_grain_light  
**Ideal for:** Noir, black & white, dramatic

**Example:**
```python
apply_color_grade(preset="noir_classic")
```

### 7. dreamy_pastel
**Description:** Soft, ethereal pastel look  
**LUT:** muted_pastel  
**Tone Mapping:** filmic_low_contrast  
**Effects:** bloom_subtle  
**Ideal for:** Soft, dreamy, pastel

**Example:**
```python
apply_color_grade(preset="dreamy_pastel")
```

### 8. sci_fi_cool
**Description:** Cool futuristic tech aesthetic  
**LUT:** cinematic_cool  
**Tone Mapping:** filmic  
**Effects:** bloom_strong, chromatic_aberration  
**Ideal for:** Sci-fi, tech, futuristic

**Example:**
```python
apply_color_grade(preset="sci_fi_cool")
```

## LUT Presets

LUTs control lift/gamma/gain (shadows/midtones/highlights), saturation, and contrast:

### Color LUTs

**cinematic_neutral** - Clean cinematic look with subtle contrast boost
```python
apply_lut_preset(lut_preset="cinematic_neutral")
```

**cinematic_warm** - Warm, inviting look for sunset/golden hour scenes
```python
apply_lut_preset(lut_preset="cinematic_warm")
```

**cinematic_cool** - Cool, modern look for tech/sci-fi scenes
```python
apply_lut_preset(lut_preset="cinematic_cool")
```

**teal_orange** - Hollywood blockbuster look (teal shadows, orange highlights)
```python
apply_lut_preset(lut_preset="teal_orange")
```

**vintage_film** - Faded film look with reduced contrast
```python
apply_lut_preset(lut_preset="vintage_film")
```

**vibrant_pop** - High saturation, punchy colors for advertising
```python
apply_lut_preset(lut_preset="vibrant_pop")
```

**muted_pastel** - Soft, desaturated pastel tones
```python
apply_lut_preset(lut_preset="muted_pastel")
```

**moody_dark** - Dark, moody look for horror/thriller
```python
apply_lut_preset(lut_preset="moody_dark")
```

### Black & White LUTs

**film_noir** - Classic black and white high-contrast noir look
```python
apply_lut_preset(lut_preset="film_noir")
```

**high_contrast_bw** - Dramatic black and white with deep blacks
```python
apply_lut_preset(lut_preset="high_contrast_bw")
```

## Tone Mapping Presets

Tone mapping controls how HDR scene values are mapped to display:

**filmic** - Blender's Filmic color management (cinematic HDR)
```python
setup_tone_mapping(tone_mapping="filmic")
```

**filmic_high_contrast** - Filmic with punchy contrast
```python
setup_tone_mapping(tone_mapping="filmic_high_contrast")
```

**filmic_low_contrast** - Filmic with softer contrast
```python
setup_tone_mapping(tone_mapping="filmic_low_contrast")
```

**standard** - Standard sRGB display (no tone mapping)
```python
setup_tone_mapping(tone_mapping="standard")
```

**agx** - AgX tone mapper (Blender 4.0+, highly recommended)
```python
setup_tone_mapping(tone_mapping="agx")
```

**false_color** - Exposure visualization tool
```python
setup_tone_mapping(tone_mapping="false_color")
```

### Custom Exposure and Gamma

```python
# Brighten the image
setup_tone_mapping(
    tone_mapping="filmic",
    exposure=1.0,  # +1 stop brighter
    gamma=1.0
)

# Darken the image
setup_tone_mapping(
    tone_mapping="filmic",
    exposure=-0.5,  # -0.5 stop darker
    gamma=1.0
)

# Adjust gamma (contrast in midtones)
setup_tone_mapping(
    tone_mapping="filmic",
    exposure=0.0,
    gamma=1.2  # Slightly brighter midtones
)
```

## Color Effects

Effects are added via compositor nodes:

### Vignette

**vignette_subtle** - Gentle darkening at edges
```python
add_color_effects(effects=["vignette_subtle"])
```

**vignette_strong** - Dramatic edge darkening for focus
```python
add_color_effects(effects=["vignette_strong"])
```

### Film Grain

**film_grain_light** - Subtle grain for film texture
```python
add_color_effects(effects=["film_grain_light"])
```

**film_grain_heavy** - Strong grain for vintage film look
```python
add_color_effects(effects=["film_grain_heavy"])
```

### Bloom/Glow

**bloom_subtle** - Gentle glow on bright areas
```python
add_color_effects(effects=["bloom_subtle"])
```

**bloom_strong** - Dramatic glow effect
```python
add_color_effects(effects=["bloom_strong"])
```

### Lens Effects

**chromatic_aberration** - Lens color fringing effect
```python
add_color_effects(effects=["chromatic_aberration"])
```

**lens_distortion** - Barrel/pincushion distortion
```python
add_color_effects(effects=["lens_distortion"])
```

### Combining Effects

```python
# Multiple effects at once
add_color_effects(effects=[
    "vignette_subtle",
    "film_grain_light",
    "bloom_subtle"
])
```

## Complete Workflows

### Workflow 1: Automatic (Fastest)

Let the system choose everything:

```python
# 1. Import/create your scene
# 2. Apply automatic color grading
auto_grade_scene(
    scene_description="dramatic product shot",
    lighting_type="outdoor"
)
# 3. Verify
get_viewport_screenshot()
```

### Workflow 2: Preset-Based

Use a specific preset:

```python
# 1. List available presets
list_color_presets(preset_type="color_grade")

# 2. Apply desired preset
apply_color_grade(preset="blockbuster")

# 3. Verify
get_viewport_screenshot()
```

### Workflow 3: Manual Control

Build your own look:

```python
# 1. Apply LUT
apply_lut_preset(lut_preset="cinematic_warm")

# 2. Configure tone mapping
setup_tone_mapping(
    tone_mapping="filmic_high_contrast",
    exposure=0.5
)

# 3. Add effects
add_color_effects(effects=[
    "vignette_subtle",
    "bloom_subtle"
])

# 4. Verify
get_viewport_screenshot()
```

### Workflow 4: Complete Enhancement Pipeline

Full 6-step workflow from import to final render:

```python
# Step 1: Import model
import_generated_asset(name="product", task_uuid="...")

# Step 2: Enhance geometry
auto_enhance_geometry(object_name="product")

# Step 3: Enhance materials
auto_enhance_materials(object_name="product", aggressive=True)

# Step 4: Set up lighting
auto_setup_scene_lighting(
    scene_description="dramatic product shot",
    target_object="product"
)

# Step 5: Frame the shot
auto_frame_with_composition(
    object_name="product",
    purpose="product"
)

# Step 6: Apply color grading (FINAL POLISH)
auto_grade_scene(
    scene_description="dramatic product shot",
    lighting_type="outdoor"
)

# Verify results
get_viewport_screenshot()
```

## Scene-Type Recommendations

### Product Photography

**Best preset:** `product_showcase`

```python
apply_color_grade(preset="product_showcase")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="vibrant_pop")
setup_tone_mapping(tone_mapping="filmic")
add_color_effects(effects=["vignette_subtle"])
```

### Cinematic/Action Shots

**Best preset:** `blockbuster`

```python
apply_color_grade(preset="blockbuster")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="teal_orange")
setup_tone_mapping(tone_mapping="filmic_high_contrast")
add_color_effects(effects=["vignette_subtle", "bloom_subtle"])
```

### Portrait Photography

**Best preset:** `moody_portrait`

```python
apply_color_grade(preset="moody_portrait")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="moody_dark")
setup_tone_mapping(tone_mapping="filmic_high_contrast")
add_color_effects(effects=["vignette_strong", "film_grain_light"])
```

### Vintage/Retro

**Best preset:** `vintage_nostalgia`

```python
apply_color_grade(preset="vintage_nostalgia")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="vintage_film")
setup_tone_mapping(tone_mapping="filmic_low_contrast")
add_color_effects(effects=["vignette_subtle", "film_grain_heavy"])
```

### Black & White/Noir

**Best preset:** `noir_classic`

```python
apply_color_grade(preset="noir_classic")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="film_noir")
setup_tone_mapping(tone_mapping="filmic_high_contrast")
add_color_effects(effects=["vignette_strong", "film_grain_light"])
```

### Dreamy/Soft

**Best preset:** `dreamy_pastel`

```python
apply_color_grade(preset="dreamy_pastel")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="muted_pastel")
setup_tone_mapping(tone_mapping="filmic_low_contrast")
add_color_effects(effects=["bloom_subtle"])
```

### Sci-Fi/Tech

**Best preset:** `sci_fi_cool`

```python
apply_color_grade(preset="sci_fi_cool")
```

**Manual setup:**
```python
apply_lut_preset(lut_preset="cinematic_cool")
setup_tone_mapping(tone_mapping="filmic")
add_color_effects(effects=["bloom_strong", "chromatic_aberration"])
```

## API Reference

### apply_color_grade()

Apply complete color grade preset (LUT + tone mapping + effects).

**Parameters:**
- `preset` (str): Color grade preset name
  - Options: cinematic_standard, blockbuster, product_showcase, moody_portrait, vintage_nostalgia, noir_classic, dreamy_pastel, sci_fi_cool
- `use_compositor` (bool): Whether to use compositor nodes (default: True)

**Returns:** Summary of applied settings

**Example:**
```python
apply_color_grade(preset="blockbuster", use_compositor=True)
```

### apply_lut_preset()

Apply specific LUT (Look-Up Table) color grading preset.

**Parameters:**
- `lut_preset` (str): LUT name
  - Options: cinematic_neutral, cinematic_warm, cinematic_cool, teal_orange, film_noir, vintage_film, vibrant_pop, muted_pastel, high_contrast_bw, moody_dark

**Returns:** Detailed LUT settings

**Example:**
```python
apply_lut_preset(lut_preset="teal_orange")
```

### setup_tone_mapping()

Configure tone mapping (view transform) in color management.

**Parameters:**
- `tone_mapping` (str): View transform
  - Options: filmic, filmic_high_contrast, filmic_low_contrast, standard, agx, false_color
- `exposure` (float): Exposure compensation in stops (-3.0 to +3.0, default: 0.0)
- `gamma` (float): Gamma correction (0.5 to 2.0, default: 1.0)

**Returns:** Tone mapping configuration summary

**Example:**
```python
setup_tone_mapping(
    tone_mapping="filmic_high_contrast",
    exposure=0.5,
    gamma=1.0
)
```

### add_color_effects()

Add color effects like vignette, film grain, bloom, chromatic aberration.

**Parameters:**
- `effects` (list[str]): List of effect names
  - Options: vignette_subtle, vignette_strong, film_grain_light, film_grain_heavy, chromatic_aberration, bloom_subtle, bloom_strong, lens_distortion

**Returns:** List of effects applied with parameters

**Example:**
```python
add_color_effects(effects=[
    "vignette_subtle",
    "film_grain_light",
    "bloom_subtle"
])
```

### auto_grade_scene()

Automatically apply appropriate color grading based on scene analysis.

**Parameters:**
- `scene_description` (str): Description of scene/mood
  - Examples: "dramatic portrait", "product shot", "vintage nostalgia", "sci-fi tech"
- `lighting_type` (str, optional): Lighting hint
  - Options: outdoor, indoor, studio, night, golden_hour

**Returns:** Selected preset and rationale

**Example:**
```python
auto_grade_scene(
    scene_description="dramatic product shot",
    lighting_type="outdoor"
)
```

### list_color_presets()

List all available color grading presets with descriptions.

**Parameters:**
- `preset_type` (str): Type to list
  - Options: all, lut, tone_mapping, effects, color_grade

**Returns:** Formatted list of presets with descriptions

**Example:**
```python
list_color_presets(preset_type="all")
```

## Technical Details

### Compositor Node Structure

The color grading system uses Blender's compositor:

```
Render Layers → Color Balance (LUT) → Hue/Saturation → Bright/Contrast → Effects → Composite
```

**LUT Nodes:**
- Color Balance: Lift/Gamma/Gain control
- Hue/Saturation: Saturation control
- Bright/Contrast: Brightness and contrast

**Effect Nodes:**
- Ellipse Mask + Blur: Vignette
- RGB Curves: Film grain
- Glare (Fog Glow): Bloom
- Lens Distortion: Chromatic aberration, lens distortion

### Color Management

Tone mapping is applied through Blender's color management:

```
Scene → View Settings → View Transform / Look / Exposure / Gamma
```

### LUT Parameters

Each LUT preset defines:
- `lift`: RGB multipliers for shadows (0.0-2.0)
- `gamma`: RGB multipliers for midtones (0.0-2.0)
- `gain`: RGB multipliers for highlights (0.0-2.0)
- `saturation`: Saturation multiplier (0.0-2.0, 0=grayscale, 1=normal)
- `contrast`: Contrast multiplier (0.0-2.0, 1=normal)
- `brightness`: Brightness offset (-1.0 to +1.0, 0=normal)
- `color_temp`: Color temperature offset in Kelvin (-500 to +500)

## Tips and Best Practices

### 1. Color Grading is the Final Step

Always apply color grading AFTER:
- Geometry enhancement
- Material application
- Lighting setup
- Composition/framing

Color grading unifies the entire image and should be the last step.

### 2. Start with Auto or Presets

Use `auto_grade_scene()` or `apply_color_grade(preset=...)` first. Only go manual if you need specific adjustments.

### 3. Match Color Grade to Scene Mood

- **Dramatic:** Use high-contrast LUTs (film_noir, moody_dark, teal_orange)
- **Soft:** Use low-contrast LUTs (muted_pastel, vintage_film)
- **Clean:** Use neutral LUTs (cinematic_neutral, vibrant_pop)
- **Stylized:** Use teal_orange for action, moody_dark for thriller

### 4. Effects Add Polish

- **Vignette:** Draws attention to center, universal enhancement
- **Film Grain:** Adds texture, hides banding, vintage feel
- **Bloom:** Adds magic/glow, good for sci-fi and dreamy looks
- **Chromatic Aberration:** Subtle realism, lens simulation

### 5. Tone Mapping Matters

- **Filmic:** Best for most scenes (HDR-aware)
- **AgX:** Blender 4.0+ (most accurate)
- **Standard:** Use only for web graphics (sRGB)
- **False Color:** Use to check exposure (not for final renders)

### 6. Combine with Lighting

Color grading works best with proper lighting:
- Match warm LUTs with warm lighting
- Match cool LUTs with cool lighting
- Use color grading to enhance, not fix bad lighting

### 7. Test on Final Render

View transforms look different in viewport vs render. Always check final render output.

## Troubleshooting

### Problem: Color grading has no visible effect

**Solution:**
1. Check if compositor is enabled: `scene.use_nodes = True`
2. Verify view transform is set correctly
3. Make sure you're viewing in rendered/material preview mode
4. Check if effects are too subtle - try stronger presets

### Problem: Colors look wrong/oversaturated

**Solution:**
1. Reduce saturation: Use a different LUT with lower saturation
2. Check tone mapping: Try filmic instead of standard
3. Reduce effect strength: Use subtle instead of strong variants

### Problem: Image too dark/bright

**Solution:**
1. Adjust exposure in `setup_tone_mapping(exposure=...)`
2. Adjust brightness in LUT (not recommended, use exposure instead)
3. Check lighting setup - color grading won't fix underlit scenes

### Problem: Compositor is slow

**Solution:**
1. Reduce bloom quality/radius
2. Remove heavy grain effects
3. Use fewer effects overall
4. Disable compositor for preview (`use_compositor=False`)

## Integration with Other Systems

Color grading integrates with all enhancement systems:

1. **Geometry System:** Color grading highlights mesh detail
2. **Material System:** LUTs enhance PBR material appearance
3. **Lighting System:** Color grading complements lighting mood
4. **Composition System:** Vignette reinforces composition rules

**Complete Pipeline:**
```
Geometry → Materials → Lighting → Composition → Color Grading → Final Render
```

## Conclusion

The Color Grading System transforms renders from basic to cinematic. Use `auto_grade_scene()` for quick results or build custom looks with LUTs, tone mapping, and effects.

**Key Takeaways:**
- Color grading is the final polish (step 6 of 6)
- Start with auto or presets, customize if needed
- Match color grade to scene mood and lighting
- Effects add professional polish
- Always verify with `get_viewport_screenshot()`

For more information, see:
- MATERIAL_SYSTEM.md
- POST_PROCESSING.md
- LIGHTING_SYSTEM.md
- COMPOSITION_SYSTEM.md
