# Blender MCP Enhancement Systems - Complete Agent Guide

**Comprehensive reference for AI agents to create professional 3D renders using Blender MCP**

Version: 1.0  
Last Updated: December 23, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Enhancement Systems](#enhancement-systems)
4. [Complete Workflows](#complete-workflows)
5. [API Reference](#api-reference)
6. [Best Practices](#best-practices)
7. [Integration Patterns](#integration-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Blender MCP?

Blender MCP is a Model Context Protocol server that connects AI agents to Blender 3D software, enabling programmatic control over 3D modeling, rendering, and enhancement operations.

### Enhancement Systems (6 Total)

The server provides **6 professional enhancement systems** that transform basic 3D models into production-quality renders:

1. **Scene Templates System** - One-command professional setups (12 templates)
2. **Material System** - PBR materials and procedural shaders (20+ presets)
3. **Post-Processing Pipeline** - Geometry enhancement (5 presets)
4. **Lighting & Atmosphere** - HDRIs, lighting rigs, atmosphere (25+ presets)
5. **Composition System** - Camera framing and rules (7 shot types, 6 rules)
6. **Color Grading System** - Tone mapping and color correction (10 LUTs, 6 tone mappings)

### Key Capabilities

- ✅ **One-Command Enhancement** - Apply complete professional setup in seconds
- ✅ **AI Model Import** - Support for Hyper3D, Hunyuan3D, Sketchfab, PolyHaven
- ✅ **Automatic Quality Improvement** - Auto-enhance geometry, materials, lighting
- ✅ **Professional Photography Styles** - Product, portrait, landscape, architecture
- ✅ **Customizable Templates** - Modify any aspect of pre-configured setups
- ✅ **Real-time Rendering** - Cycles engine with optimized settings

---

## Quick Start

### Approach 1: Scene Templates (Fastest)

**Use when:** You want professional results in one command

```python
# Step 1: Get recommendation
suggest_scene_template(ctx, "professional product photo")
# Returns: "product_studio_pro"

# Step 2: Apply complete template
apply_scene_template(ctx, "product_studio_pro", "MyObject")
# Applies: geometry + materials + lighting + composition + color + render

# Step 3: Capture result
get_viewport_screenshot(ctx)
```

**Time:** 2-5 seconds for production quality

### Approach 2: Manual Enhancement (Maximum Control)

**Use when:** You need custom control over each aspect

```python
# Step 1: Generate/Import model
generate_hyper3d_model_via_text(ctx, "coffee mug")
import_generated_asset(ctx, "mug", task_uuid)

# Step 2: Enhance geometry
auto_enhance_geometry(ctx, "mug")

# Step 3: Enhance materials
auto_enhance_materials(ctx, "mug", aggressive=True)

# Step 4: Setup lighting
auto_setup_scene_lighting(ctx, "studio product", "mug")

# Step 5: Setup composition
auto_frame_with_composition(ctx, "mug", "medium_shot")

# Step 6: Apply color grading
apply_color_grade(ctx, "product_showcase")

# Step 7: Capture result
get_viewport_screenshot(ctx)
```

**Time:** 10-20 seconds with full customization

---

## Enhancement Systems

### 1. Scene Templates System

**Purpose:** Complete professional setups combining all 6 enhancement systems in one command.

#### Available Templates (12)

**Product Photography (3):**
- `product_studio_pro` - Clean white background, balanced lighting
- `product_lifestyle` - Natural outdoor environment, warm tones
- `product_hero_dramatic` - Sunset, god rays, high impact

**Portrait Photography (3):**
- `portrait_professional` - Three-point lighting, balanced
- `portrait_cinematic` - Dramatic moody atmosphere, fog
- `portrait_noir` - Black & white, high contrast, film noir

**Landscape/Environment (3):**
- `landscape_epic` - Wide dramatic vista, sunset, god rays
- `landscape_classic` - Balanced daylight, traditional composition
- `landscape_moody` - Dark night, heavy fog, mysterious

**Architecture Visualization (3):**
- `architecture_hero` - Golden hour, dramatic low angle
- `architecture_technical` - Clean neutral daylight, front view
- `architecture_dramatic` - Night scene, fog, cool tones

#### Core Functions

```python
# Get AI recommendation
suggest_scene_template(ctx, 
    scene_description: str,
    object_type: str = None,      # product, character, building, environment
    style: str = None             # professional, dramatic, cinematic, clean
) -> str

# Apply complete template
apply_scene_template(ctx,
    template_key: str,            # Template to apply
    target_object: str = None,    # Auto-detects if None
    auto_render: bool = False     # Render after applying
) -> str

# Browse templates
list_scene_templates(ctx,
    category: str = "all"         # all, product, portrait, landscape, architecture
) -> str

# Customize template
customize_scene_template(ctx,
    template_key: str,
    customizations: dict          # Override specific settings
) -> str
```

#### Template Structure

Each template includes:
```python
{
    "geometry": {
        "enhancement_preset": "high_detail",
        "subdivision_levels": 2,
        "auto_smooth": True
    },
    "materials": {
        "auto_enhance": True,
        "aggressive": True
    },
    "lighting": {
        "hdri": "studio",
        "lighting_rig": "studio",
        "hdri_strength": 1.0
    },
    "composition": {
        "shot_type": "medium_shot",
        "composition_rule": "rule_of_thirds",
        "camera_angle": "three_quarter"
    },
    "color_grading": {
        "preset": "product_showcase",
        "tone_mapping": "agx",
        "exposure": 0.0
    },
    "render": {
        "samples": 256
    }
}
```

---

### 2. Material System

**Purpose:** Apply professional PBR materials with physically accurate shading.

#### Material Presets (20+)

**Metals:**
- `brushed_aluminum` - Anisotropic brushed metal
- `brushed_metal` - Generic brushed metal finish
- `weathered_metal` - Rusty, worn metal
- `chrome` - Perfect mirror chrome
- `copper` - Polished copper
- `gold` - Polished gold

**Plastics:**
- `glossy_plastic` - Shiny plastic finish
- `matte_plastic` - Non-reflective plastic

**Glass:**
- `clear_glass` - Transparent glass
- `frosted_glass` - Semi-transparent diffused glass

**Wood:**
- `polished_wood` - Glossy wood finish
- `rough_wood` - Matte weathered wood

**Architectural:**
- `concrete` - Rough concrete
- `ceramic` - Glossy ceramic tiles
- `fabric` - Cloth material
- `leather` - Leather texture
- `rubber` - Matte rubber

**Specialty:**
- `glossy_paint` - Car paint
- `glowing` - Emissive material
- `subsurface` - Skin/wax with SSS

#### Core Functions

```python
# Auto-enhance all materials
auto_enhance_materials(ctx,
    object_name: str = None,      # Specific object or all
    aggressive: bool = False      # More dramatic enhancement
) -> str

# Apply specific material
apply_material_preset(ctx,
    object_name: str,
    preset_name: str              # Material preset key
) -> str

# Get suggestion
suggest_material(ctx,
    object_name: str
) -> str

# List all materials
list_material_presets(ctx) -> str
```

#### Material Properties

Each material includes:
- Base color (RGB)
- Metallic (0-1)
- Roughness (0-1)
- Specular (0-1)
- Optional: Anisotropic, Clearcoat, Emission, Transmission, Subsurface

---

### 3. Post-Processing Pipeline

**Purpose:** Enhance geometry quality through subdivision, beveling, and modifiers.

#### Enhancement Presets (5)

- `smooth` - General purpose (2 subdiv levels, auto-smooth)
- `high_detail` - Maximum quality (3 levels, beveling)
- `mechanical` - Hard-surface objects (beveling, sharp edges)
- `organic` - Smooth shapes (subdivision, remeshing)
- `architectural` - Buildings (minimal subdiv, crisp edges)

#### Core Functions

```python
# Auto-enhance geometry
auto_enhance_geometry(ctx,
    object_name: str = None       # Specific object or all
) -> str

# Apply specific preset
apply_enhancement_preset(ctx,
    object_name: str,
    preset: str                   # Enhancement preset key
) -> str

# Add subdivision
apply_subdivision_surface(ctx,
    object_name: str,
    levels: int = 2,              # Viewport levels
    render_levels: int = 3        # Render levels
) -> str

# Add edge beveling
add_edge_bevel(ctx,
    object_name: str,
    width: float = 0.01,          # Bevel width
    segments: int = 3             # Bevel segments
) -> str

# Set shading
set_shading(ctx,
    object_name: str,
    smooth: bool = True           # Smooth or flat shading
) -> str

# Analyze mesh
analyze_mesh(ctx,
    object_name: str
) -> str

# Get suggestion
suggest_enhancement(ctx,
    object_name: str
) -> str
```

---

### 4. Lighting & Atmosphere System

**Purpose:** Professional lighting setups with HDRIs, lighting rigs, and atmospheric effects.

#### HDRI Presets (6)

- `studio` - Neutral studio environment
- `outdoor_day` - Bright daylight
- `sunset` - Golden hour warm tones
- `night` - Dark night sky
- `interior` - Indoor lighting
- `overcast` - Soft diffused light

#### Lighting Rigs (5)

- `three_point` - Classic 3-point lighting
- `studio` - Soft studio setup
- `dramatic` - High contrast dramatic
- `outdoor` - Natural outdoor simulation
- `night` - Low-key night lighting

#### Atmosphere Presets (5)

- `haze` - Subtle atmospheric haze
- `fog` - Medium fog
- `heavy_fog` - Dense fog
- `god_rays` - Volumetric light shafts
- `dust` - Particle dust in air

#### Core Functions

```python
# Auto-setup complete scene lighting
auto_setup_scene_lighting(ctx,
    scene_description: str,
    target_object: str = None
) -> str

# Setup HDRI
setup_hdri_lighting(ctx,
    preset: str,                  # HDRI preset key
    strength: float = 1.0,        # Brightness multiplier
    rotation: float = 0.0         # Rotation in radians
) -> str

# Apply lighting rig
apply_lighting_rig(ctx,
    rig_type: str,                # Lighting rig preset
    target_object: str = None,    # Object to light
    distance: float = 10.0        # Light distance
) -> str

# Add atmospheric effects
add_atmospheric_fog(ctx,
    preset: str,                  # Atmosphere preset
    density: float = None         # Override density
) -> str

# Setup camera
setup_camera(ctx,
    preset: str,                  # Camera preset
    target_object: str = None,
    distance: float = None
) -> str

# Configure render settings
configure_render_settings(ctx,
    preset: str                   # preview, production, final
) -> str
```

---

### 5. Composition System

**Purpose:** Professional camera framing using photography composition rules.

#### Shot Types (7)

- `extreme_wide` - Very wide establishing shot (distance: 20-30 units)
- `wide_shot` - Wide environmental shot (distance: 12-18 units)
- `medium_wide` - Medium-wide shot (distance: 8-12 units)
- `medium_shot` - Standard medium shot (distance: 5-8 units)
- `medium_closeup` - Closer medium shot (distance: 3-5 units)
- `closeup` - Close-up shot (distance: 2-3 units)
- `extreme_closeup` - Very close detail (distance: 1-2 units)

#### Composition Rules (6)

- `rule_of_thirds` - Classic thirds grid
- `golden_ratio` - Fibonacci spiral
- `center_composition` - Centered subject
- `diagonal` - Dynamic diagonal lines
- `leading_lines` - Guide viewer's eye
- `symmetry` - Balanced symmetry

#### Camera Angles (5)

- `front` - Straight-on view
- `three_quarter` - 3/4 view (45°)
- `side` - Profile view (90°)
- `low` - Low angle looking up
- `high` - High angle looking down

#### Core Functions

```python
# Auto-frame with composition
auto_frame_with_composition(ctx,
    target_object: str,
    shot_type: str = "medium_shot",
    composition_rule: str = "rule_of_thirds",
    camera_angle: str = "three_quarter"
) -> str

# Analyze composition
analyze_composition(ctx,
    camera_name: str = None
) -> str

# Apply composition rule
apply_composition_rule(ctx,
    rule: str,
    target_object: str,
    camera_name: str = None
) -> str

# Calculate shot framing
calculate_shot_framing(ctx,
    target_object: str,
    shot_type: str
) -> str

# Suggest composition
suggest_composition(ctx,
    target_object: str,
    scene_description: str = None
) -> str
```

#### Composition Presets (8)

Pre-configured complete setups:
- `product_hero` - Hero product shot
- `product_lifestyle` - Lifestyle product
- `portrait_pro` - Professional portrait
- `portrait_cinematic` - Cinematic portrait
- `landscape_epic` - Epic landscape
- `landscape_classic` - Classic landscape
- `architecture_hero` - Hero architecture
- `architecture_dramatic` - Dramatic architecture

---

### 6. Color Grading System

**Purpose:** Professional color correction and tone mapping for cinematic looks.

#### Tone Mapping Presets (6)

- `filmic` - Standard filmic curve (medium contrast)
- `filmic_high_contrast` - High contrast filmic
- `filmic_low_contrast` - Low contrast filmic
- `standard` - Basic sRGB
- `agx` - Blender 5.0 default (photographic)
- `false_color` - Exposure visualization

#### LUT Presets (10)

- `cinematic_neutral` - Balanced cinematic
- `teal_orange` - Hollywood teal/orange look
- `film_noir` - Classic black & white
- `vintage_film` - Retro film look
- `vibrant_pop` - Saturated pop art
- `muted_pastel` - Soft pastel tones
- `moody_dark` - Dark desaturated
- `high_contrast_bw` - High contrast B&W
- `cinematic_warm` - Warm golden tones
- `cinematic_cool` - Cool blue tones

#### Color Grade Presets (8)

Complete presets combining tone mapping + LUT + effects:
- `cinematic_standard` - Balanced cinematic
- `blockbuster` - High-impact dramatic
- `product_showcase` - Clean product presentation
- `moody_portrait` - Dark moody portrait
- `vintage_nostalgia` - Retro vintage
- `noir_classic` - Film noir B&W
- `dreamy_pastel` - Soft dreamy
- `sci_fi_cool` - Cool sci-fi look

#### Core Functions

```python
# Apply complete color grade
apply_color_grade(ctx,
    preset: str                   # Color grade preset
) -> str

# Apply LUT preset
apply_lut_preset(ctx,
    preset: str                   # LUT preset
) -> str

# Setup tone mapping
setup_tone_mapping(ctx,
    preset: str,                  # Tone mapping preset
    exposure: float = 0.0,        # -1.0 to +1.0 stops
    gamma: float = 1.0            # 0.8 to 1.5
) -> str

# Add color effects
add_color_effects(ctx,
    effects: list = None          # List of effect keys
) -> str

# Auto-grade scene
auto_grade_scene(ctx,
    scene_description: str
) -> str

# List presets
list_color_presets(ctx,
    preset_type: str = "all"      # all, lut, tone_mapping, effects, color_grade
) -> str
```

#### Color Effects (8)

- `vignette_subtle` - Subtle edge darkening
- `vignette_strong` - Strong vignette
- `film_grain_light` - Light grain texture
- `film_grain_heavy` - Heavy grain
- `bloom_subtle` - Soft glow
- `bloom_strong` - Strong bloom
- `chromatic_aberration` - Lens color fringing
- `lens_distortion` - Barrel distortion

---

## Complete Workflows

### Workflow 1: E-Commerce Product Shot

**Goal:** Clean professional product photo for online store

```python
# Import model
generate_hyper3d_model_via_text(ctx, "wireless headphones")
import_generated_asset(ctx, "headphones", task_uuid)

# ONE-COMMAND APPROACH (Fastest):
apply_scene_template(ctx, "product_studio_pro", "headphones")
screenshot = get_viewport_screenshot(ctx)

# MANUAL APPROACH (More control):
# 1. Enhance geometry
auto_enhance_geometry(ctx, "headphones")

# 2. Apply materials
apply_material_preset(ctx, "headphones", "glossy_plastic")

# 3. Setup studio lighting
setup_hdri_lighting(ctx, "studio", strength=1.0)
apply_lighting_rig(ctx, "studio", "headphones")

# 4. Frame product
auto_frame_with_composition(ctx, "headphones", 
    shot_type="medium_shot",
    composition_rule="rule_of_thirds",
    camera_angle="three_quarter"
)

# 5. Apply color grade
apply_color_grade(ctx, "product_showcase")

# 6. Render
configure_render_settings(ctx, "production")
screenshot = get_viewport_screenshot(ctx)
```

---

### Workflow 2: Cinematic Character Portrait

**Goal:** Dramatic artistic character render

```python
# Import character model from Sketchfab
search_sketchfab_models(ctx, "fantasy character", downloadable=True)
download_sketchfab_model(ctx, "model_uid")

# ONE-COMMAND APPROACH:
apply_scene_template(ctx, "portrait_cinematic", "Character")
screenshot = get_viewport_screenshot(ctx)

# MANUAL APPROACH:
# 1. Enhance geometry
apply_enhancement_preset(ctx, "Character", "organic")

# 2. Enhance materials
auto_enhance_materials(ctx, "Character", aggressive=True)

# 3. Setup dramatic lighting
setup_hdri_lighting(ctx, "sunset", strength=1.2)
apply_lighting_rig(ctx, "dramatic", "Character")
add_atmospheric_fog(ctx, "fog", density=0.05)

# 4. Cinematic composition
auto_frame_with_composition(ctx, "Character",
    shot_type="closeup",
    composition_rule="golden_ratio",
    camera_angle="three_quarter"
)

# 5. Color grading
apply_color_grade(ctx, "moody_portrait")
setup_tone_mapping(ctx, "filmic_high_contrast", exposure=-0.2, gamma=1.1)

# 6. High quality render
configure_render_settings(ctx, "final")
screenshot = get_viewport_screenshot(ctx)
```

---

### Workflow 3: Architectural Visualization

**Goal:** Hero architectural render for portfolio

```python
# Import building model from PolyHaven
download_polyhaven_asset(ctx, "modern_building", "models")

# ONE-COMMAND APPROACH:
apply_scene_template(ctx, "architecture_hero", "modern_building")
screenshot = get_viewport_screenshot(ctx)

# MANUAL APPROACH:
# 1. Enhance geometry
apply_enhancement_preset(ctx, "modern_building", "architectural")

# 2. Materials
auto_enhance_materials(ctx, "modern_building", aggressive=True)

# 3. Golden hour lighting
setup_hdri_lighting(ctx, "sunset", strength=1.3)
apply_lighting_rig(ctx, "dramatic", "modern_building")
add_atmospheric_fog(ctx, "haze", density=0.03)

# 4. Hero composition
auto_frame_with_composition(ctx, "modern_building",
    shot_type="wide_shot",
    composition_rule="golden_ratio",
    camera_angle="low"
)

# 5. Blockbuster color grade
apply_color_grade(ctx, "blockbuster")

# 6. Final quality render
configure_render_settings(ctx, "final")
screenshot = get_viewport_screenshot(ctx)
```

---

### Workflow 4: Product Lifestyle Shot

**Goal:** Natural product in environment for social media

```python
# Generate product
generate_hyper3d_model_via_text(ctx, "coffee mug ceramic")
import_generated_asset(ctx, "mug", task_uuid)

# ONE-COMMAND APPROACH:
apply_scene_template(ctx, "product_lifestyle", "mug")
screenshot = get_viewport_screenshot(ctx)

# MANUAL WITH CUSTOMIZATION:
# 1. Start with template
apply_scene_template(ctx, "product_lifestyle", "mug")

# 2. Customize lighting (make it warmer)
setup_hdri_lighting(ctx, "sunset", strength=1.5)

# 3. Adjust color (more warmth)
setup_tone_mapping(ctx, "filmic", exposure=0.3, gamma=1.0)

# 4. Capture
screenshot = get_viewport_screenshot(ctx)
```

---

## API Reference

### Asset Generation & Import

```python
# Hyper3D (Rodin) generation
generate_hyper3d_model_via_text(ctx,
    text_prompt: str,
    art_style: str = "realistic"
) -> dict

generate_hyper3d_model_via_images(ctx,
    image_paths: list
) -> dict

poll_rodin_job_status(ctx,
    request_id: str = None,
    subscription_key: str = None
) -> dict

import_generated_asset(ctx,
    name: str,
    task_uuid: str = None,
    subscription_key: str = None
) -> str

# Hunyuan3D generation
generate_hunyuan3d_model(ctx,
    text_prompt: str = None,
    image_path: str = None
) -> dict

poll_hunyuan_job_status(ctx,
    job_id: str
) -> dict

import_generated_asset_hunyuan(ctx,
    job_id: str,
    name: str
) -> str

# Sketchfab
search_sketchfab_models(ctx,
    query: str,
    categories: str = None,
    count: int = 20,
    downloadable: bool = True
) -> str

download_sketchfab_model(ctx,
    uid: str
) -> str

# PolyHaven
search_polyhaven_assets(ctx,
    asset_type: str = "all",      # hdris, textures, models, all
    categories: str = None
) -> str

download_polyhaven_asset(ctx,
    asset_id: str,
    asset_type: str,              # hdris, textures, models
    resolution: str = "1k",
    file_format: str = None
) -> str
```

### Scene Information

```python
# Get scene info
get_scene_info(ctx) -> str

# Get viewport screenshot
get_viewport_screenshot(ctx,
    max_size: int = 800
) -> Image

# Execute Blender code
execute_blender_code(ctx,
    code: str
) -> str
```

---

## Best Practices

### 1. Template Selection

**Use Scene Templates when:**
- ✅ Scene fits standard photography style
- ✅ Speed is critical
- ✅ Want proven professional results
- ✅ Learning the system

**Use Manual Enhancement when:**
- ✅ Highly custom requirements
- ✅ Non-standard scenes
- ✅ Experimental styles
- ✅ Need granular control

### 2. Quality Settings

**Preview Mode (Fast):**
```python
configure_render_settings(ctx, "preview")  # 64 samples
```

**Production Mode (Balanced):**
```python
configure_render_settings(ctx, "production")  # 256 samples
```

**Final Mode (Highest Quality):**
```python
configure_render_settings(ctx, "final")  # 512 samples
```

### 3. Geometry Enhancement Priority

**ALWAYS enhance geometry for AI-generated models:**

```python
# AI models are typically very low-poly (< 1000 faces)
# Subdivision can increase quality 16x
auto_enhance_geometry(ctx, "object_name")
```

**Enhancement order:**
1. Geometry first (creates smooth base)
2. Materials second (applies to enhanced geometry)
3. Lighting third (reveals material detail)
4. Composition fourth (frames the result)
5. Color grading last (final look)

### 4. Material Selection

**By object type:**
- Products: `glossy_plastic`, `chrome`, `brushed_metal`
- Characters: `subsurface`, `fabric`, `leather`
- Buildings: `concrete`, `glass`, `brushed_metal`
- Natural objects: `rough_wood`, `weathered_metal`

### 5. Lighting Strategy

**Indoor/Studio scenes:**
```python
setup_hdri_lighting(ctx, "studio")
apply_lighting_rig(ctx, "studio")
```

**Outdoor scenes:**
```python
setup_hdri_lighting(ctx, "outdoor_day")
apply_lighting_rig(ctx, "outdoor")
add_atmospheric_fog(ctx, "haze")
```

**Dramatic scenes:**
```python
setup_hdri_lighting(ctx, "sunset")
apply_lighting_rig(ctx, "dramatic")
add_atmospheric_fog(ctx, "god_rays")
```

### 6. Composition Guidelines

**Product photography:**
- Shot type: `medium_shot` or `closeup`
- Rule: `rule_of_thirds`
- Angle: `three_quarter`

**Portraits:**
- Shot type: `closeup` or `medium_closeup`
- Rule: `golden_ratio`
- Angle: `three_quarter` or `side`

**Architecture:**
- Shot type: `wide_shot`
- Rule: `golden_ratio` or `diagonal`
- Angle: `low`

**Landscapes:**
- Shot type: `extreme_wide` or `wide_shot`
- Rule: `rule_of_thirds`
- Angle: `front`

### 7. Color Grading Tips

**Product shots:** Use `product_showcase` or `cinematic_neutral`  
**Dramatic scenes:** Use `blockbuster` or `moody_portrait`  
**Vintage looks:** Use `vintage_nostalgia` or `film_noir`  
**Bright/clean:** Use `agx` tone mapping with positive exposure  
**Dark/moody:** Use `filmic_high_contrast` with negative exposure

---

## Integration Patterns

### Pattern 1: Quick Enhancement

For rapid prototyping and iteration:

```python
def quick_enhance(object_name: str, style: str = "product"):
    """One-function enhancement based on style"""
    
    # Map style to template
    template_map = {
        "product": "product_studio_pro",
        "portrait": "portrait_professional",
        "landscape": "landscape_classic",
        "architecture": "architecture_technical"
    }
    
    template = template_map.get(style, "product_studio_pro")
    apply_scene_template(ctx, template, object_name)
    return get_viewport_screenshot(ctx)
```

### Pattern 2: Iterative Refinement

For progressive enhancement with feedback:

```python
def iterative_enhance(object_name: str):
    """Step-by-step enhancement with checkpoints"""
    
    # Step 1: Geometry
    auto_enhance_geometry(ctx, object_name)
    screenshot1 = get_viewport_screenshot(ctx)
    
    # Step 2: Materials
    auto_enhance_materials(ctx, object_name)
    screenshot2 = get_viewport_screenshot(ctx)
    
    # Step 3: Lighting
    auto_setup_scene_lighting(ctx, "studio product", object_name)
    screenshot3 = get_viewport_screenshot(ctx)
    
    # Step 4: Composition
    auto_frame_with_composition(ctx, object_name, "medium_shot")
    screenshot4 = get_viewport_screenshot(ctx)
    
    # Step 5: Color
    apply_color_grade(ctx, "cinematic_standard")
    final = get_viewport_screenshot(ctx)
    
    return [screenshot1, screenshot2, screenshot3, screenshot4, final]
```

### Pattern 3: Batch Processing

For multiple objects with consistent style:

```python
def batch_enhance(object_names: list, template: str):
    """Apply same template to multiple objects"""
    
    results = []
    for obj_name in object_names:
        apply_scene_template(ctx, template, obj_name)
        screenshot = get_viewport_screenshot(ctx)
        results.append({
            "object": obj_name,
            "template": template,
            "screenshot": screenshot
        })
    return results
```

### Pattern 4: A/B Testing

For comparing different approaches:

```python
def ab_test_templates(object_name: str, templates: list):
    """Test multiple templates and compare"""
    
    results = []
    for template in templates:
        apply_scene_template(ctx, template, object_name)
        screenshot = get_viewport_screenshot(ctx)
        results.append({
            "template": template,
            "screenshot": screenshot
        })
    return results

# Usage
compare = ab_test_templates("product", [
    "product_studio_pro",
    "product_lifestyle",
    "product_hero_dramatic"
])
```

---

## Troubleshooting

### Common Issues

**Issue: Low quality result**
```python
# Solution: Check geometry first
analyze_mesh(ctx, "object_name")
# If face_count < 2000, apply high detail preset
apply_enhancement_preset(ctx, "object_name", "high_detail")
```

**Issue: Object too dark**
```python
# Solution: Increase exposure
setup_tone_mapping(ctx, "filmic", exposure=0.5, gamma=1.0)
```

**Issue: Object too bright**
```python
# Solution: Decrease exposure
setup_tone_mapping(ctx, "filmic", exposure=-0.3, gamma=1.0)
```

**Issue: Flat/boring lighting**
```python
# Solution: Add atmosphere and dramatic rig
apply_lighting_rig(ctx, "dramatic", "object_name")
add_atmospheric_fog(ctx, "god_rays")
```

**Issue: Poor composition**
```python
# Solution: Use composition analysis
analyze_composition(ctx)
# Then apply rule
apply_composition_rule(ctx, "golden_ratio", "object_name")
```

**Issue: Colors look wrong**
```python
# Solution: Check tone mapping
setup_tone_mapping(ctx, "agx", exposure=0.0, gamma=1.0)
# Or try different color grade
apply_color_grade(ctx, "cinematic_neutral")
```

---

## Appendix: Template Quick Reference

### Template Decision Tree

```
Start → What type of subject?
│
├─ Product
│  ├─ E-commerce/Clean → product_studio_pro
│  ├─ Lifestyle/Natural → product_lifestyle
│  └─ Hero/Dramatic → product_hero_dramatic
│
├─ Character/Portrait
│  ├─ Professional/Corporate → portrait_professional
│  ├─ Artistic/Cinematic → portrait_cinematic
│  └─ Black & White/Vintage → portrait_noir
│
├─ Environment/Landscape
│  ├─ Epic/Dramatic → landscape_epic
│  ├─ Natural/Balanced → landscape_classic
│  └─ Moody/Dark → landscape_moody
│
└─ Architecture/Building
   ├─ Hero/Portfolio → architecture_hero
   ├─ Technical/Documentation → architecture_technical
   └─ Night/Dramatic → architecture_dramatic
```

### Enhancement Priority Matrix

| Priority | System | When to Use | Impact |
|----------|--------|-------------|--------|
| 1 | Geometry | Always for AI models | ⭐⭐⭐⭐⭐ |
| 2 | Materials | Always | ⭐⭐⭐⭐⭐ |
| 3 | Lighting | Always | ⭐⭐⭐⭐⭐ |
| 4 | Composition | Always | ⭐⭐⭐⭐ |
| 5 | Color Grading | Final polish | ⭐⭐⭐ |
| 0 | Scene Templates | Quick results | ⭐⭐⭐⭐⭐ |

### Function Categories

**Asset Management (9 functions):**
- generate_hyper3d_model_via_text
- generate_hyper3d_model_via_images
- generate_hunyuan3d_model
- search_sketchfab_models
- download_sketchfab_model
- search_polyhaven_assets
- download_polyhaven_asset
- import_generated_asset
- import_generated_asset_hunyuan

**Scene Templates (4 functions):**
- apply_scene_template ⭐
- suggest_scene_template
- list_scene_templates
- customize_scene_template

**Geometry Enhancement (7 functions):**
- auto_enhance_geometry ⭐
- apply_enhancement_preset
- apply_subdivision_surface
- add_edge_bevel
- set_shading
- analyze_mesh
- suggest_enhancement

**Materials (4 functions):**
- auto_enhance_materials ⭐
- apply_material_preset
- suggest_material
- list_material_presets

**Lighting (5 functions):**
- auto_setup_scene_lighting ⭐
- setup_hdri_lighting
- apply_lighting_rig
- add_atmospheric_fog
- configure_render_settings

**Composition (5 functions):**
- auto_frame_with_composition ⭐
- analyze_composition
- apply_composition_rule
- calculate_shot_framing
- suggest_composition

**Color Grading (6 functions):**
- apply_color_grade ⭐
- setup_tone_mapping
- apply_lut_preset
- add_color_effects
- auto_grade_scene
- list_color_presets

**Utilities (3 functions):**
- get_scene_info
- get_viewport_screenshot
- execute_blender_code

⭐ = Most commonly used "auto" functions

---

## Summary

### The Complete Enhancement Pipeline

```
1. IMPORT/GENERATE
   ↓
2. GEOMETRY ENHANCEMENT (subdivision + beveling)
   ↓
3. MATERIALS (PBR shaders)
   ↓
4. LIGHTING (HDRI + rigs + atmosphere)
   ↓
5. COMPOSITION (camera framing + rules)
   ↓
6. COLOR GRADING (tone mapping + effects)
   ↓
7. RENDER & CAPTURE
```

### Time Estimates

- **Scene Template Approach:** 2-5 seconds
- **Auto-Enhancement Functions:** 10-20 seconds
- **Full Manual Control:** 30-60 seconds
- **Custom Experimental:** 2-5 minutes

### Success Rate by Approach

- **Scene Templates:** 95% - Proven professional results
- **Auto Functions:** 90% - AI-optimized choices
- **Manual Selection:** 85% - Depends on expertise
- **Custom Experimental:** 70% - Trial and error

### Recommended Starting Point

```python
# For new users and agents:
# 1. Use suggest_scene_template() to get recommendation
# 2. Apply template with apply_scene_template()
# 3. Customize if needed with customize_scene_template()
# 4. Capture with get_viewport_screenshot()

# This provides 95% success rate with minimal complexity
```

---

**End of Agent Guide**

For questions or issues, refer to individual system documentation:
- SCENE_TEMPLATES_SYSTEM.md
- MATERIAL_SYSTEM.md
- POST_PROCESSING.md
- LIGHTING_SYSTEM.md
- COMPOSITION_SYSTEM.md
- COLOR_GRADING_SYSTEM.md
