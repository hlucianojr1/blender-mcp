# Composition System Guide

The Composition System provides intelligent camera framing and composition analysis using professional cinematography principles. It automatically positions cameras to create visually compelling shots following proven composition rules.

## Table of Contents
- [Quick Start](#quick-start)
- [Composition Rules](#composition-rules)
- [Shot Types](#shot-types)
- [API Reference](#api-reference)
- [Workflow Examples](#workflow-examples)
- [Presets](#presets)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

### Basic Auto-Framing (Recommended)
```python
# Automatic composition with smart defaults
auto_frame_with_composition(object_name="MyObject", purpose="general")

# For specific use cases
auto_frame_with_composition(object_name="Portrait", purpose="portrait")
auto_frame_with_composition(object_name="Product", purpose="product")
auto_frame_with_composition(object_name="Building", purpose="architecture")
```

### Using Composition Presets
```python
# Professional portrait setup
auto_frame_with_composition(object_name="Character", preset="portrait_pro")

# Cinematic product shot
auto_frame_with_composition(object_name="Watch", preset="product_hero")

# Dramatic architecture
auto_frame_with_composition(object_name="Tower", preset="architecture_dramatic")
```

### Manual Composition Control
```python
# Apply specific composition rule
apply_composition_rule(
    object_name="Cube",
    composition_rule="rule_of_thirds",
    camera_angle="three_quarter"
)

# Calculate shot framing
calculate_shot_framing(object_name="Statue", shot_type="medium_shot")
```

---

## Composition Rules

The system supports 6 classic composition rules, each optimized for different scenarios.

### 1. Rule of Thirds ⭐ (Most Common)
**When to use:** General purpose, portraits, landscapes, products

The frame is divided into a 3×3 grid. Subject is positioned at intersection points for visual balance.

```python
apply_composition_rule(object_name="Portrait", composition_rule="rule_of_thirds")
```

**Characteristics:**
- Grid points at 1/3 and 2/3 positions
- Creates dynamic, balanced compositions
- Professional standard for most content
- 15% headroom from top
- Subject at 55% horizontal position

**Ideal for:**
- Portraits and character shots
- Product photography
- Landscape photography
- General scenes

---

### 2. Golden Ratio (Phi Grid)
**When to use:** Fine art, architecture, nature photography

Uses phi (1.618) proportions for mathematically harmonious composition.

```python
apply_composition_rule(object_name="Sculpture", composition_rule="golden_ratio")
```

**Characteristics:**
- Grid points at 0.382 and 0.618 positions
- More refined than rule of thirds
- Creates elegant, natural-looking balance
- 12% headroom
- Subject at 61.8% (golden ratio) horizontal position

**Ideal for:**
- Fine art and gallery pieces
- Architectural photography
- Nature and organic subjects
- High-end product shots

---

### 3. Center Composition
**When to use:** Symmetrical subjects, minimalism, patterns

Subject centered for maximum impact and symmetry.

```python
apply_composition_rule(object_name="Mandala", composition_rule="center_composition")
```

**Characteristics:**
- Single center focus point
- Perfect symmetry
- Bold and direct
- Works with rotational symmetry

**Ideal for:**
- Symmetrical architecture
- Patterns and textures
- Minimalist designs
- Abstract art
- Mandalas and geometric forms

---

### 4. Diagonal Composition
**When to use:** Action scenes, dynamic tension, movement

Creates energy and dynamism through diagonal lines.

```python
apply_composition_rule(object_name="Athlete", composition_rule="diagonal")
```

**Characteristics:**
- Strong diagonal lines create movement
- Dynamic and energetic
- Adds visual tension
- Guides eye through frame

**Ideal for:**
- Action and sports
- Dynamic poses
- Tension-filled scenes
- Movement and flow

---

### 5. Frame Within Frame
**When to use:** Storytelling, adding depth and context

Uses environmental elements to create a natural frame around the subject.

```python
apply_composition_rule(object_name="Character", composition_rule="frame_within_frame")
```

**Characteristics:**
- Subject framed by scene elements
- Adds layers and depth
- Creates focus and context
- Strong sense of place

**Ideal for:**
- Storytelling shots
- Environmental portraits
- Adding context
- Creating depth

---

### 6. Leading Lines
**When to use:** Depth, perspective, architectural photography

Guides viewer's eye to the subject using converging lines.

```python
apply_composition_rule(object_name="Building", composition_rule="leading_lines")
```

**Characteristics:**
- Lines converge toward subject
- Creates strong sense of depth
- Guides viewer attention
- Works with perspective

**Ideal for:**
- Roads and pathways
- Architecture
- Perspective shots
- Creating visual flow

---

## Shot Types

Shot types control camera distance and framing. The system provides 7 standard shot types based on cinematography conventions.

### Shot Type Reference

| Shot Type | Frame Fill | Distance | Focal Length | Use Case |
|-----------|-----------|----------|--------------|----------|
| **Extreme Close-Up (ECU)** | 95% | 1.2× | 85mm | Details, textures, emotions |
| **Close-Up (CU)** | 75% | 1.8× | 85mm | Portraits, products, faces |
| **Medium Close-Up (MCU)** | 55% | 2.5× | 50mm | Interviews, product context |
| **Medium Shot (MS)** | 40% | 3.5× | 50mm | General, balanced framing |
| **Medium Wide (MWS)** | 25% | 5.0× | 35mm | Establishing, context |
| **Wide Shot (WS)** | 15% | 7.0× | 24mm | Landscapes, architecture |
| **Extreme Wide (EWS)** | 8% | 10.0× | 14mm | Epic vistas, scale |

### Shot Type Examples

```python
# Extreme close-up for detail work
calculate_shot_framing(object_name="Eye", shot_type="extreme_closeup")

# Standard close-up for portraits
calculate_shot_framing(object_name="Face", shot_type="closeup")

# Medium shot for balanced framing
calculate_shot_framing(object_name="Character", shot_type="medium_shot")

# Wide shot for environments
calculate_shot_framing(object_name="Landscape", shot_type="wide_shot")

# Epic establishing shot
calculate_shot_framing(object_name="Mountain", shot_type="extreme_wide")
```

### Automatic Shot Type Selection

The system automatically suggests shot types based on object size and purpose:

```python
# System analyzes object and chooses appropriate shot type
auto_frame_with_composition(object_name="Ring", purpose="detail")     # → extreme_closeup
auto_frame_with_composition(object_name="Portrait", purpose="portrait") # → closeup
auto_frame_with_composition(object_name="Scene", purpose="general")    # → medium_shot
auto_frame_with_composition(object_name="Vista", purpose="landscape")  # → wide_shot
```

---

## API Reference

### Core Functions

#### `auto_frame_with_composition()` ⭐ RECOMMENDED
Automatically set up optimal composition (all-in-one solution).

```python
auto_frame_with_composition(
    object_name: str,           # Object to frame
    purpose: str = "general",   # Purpose: detail, portrait, product, general, 
                                #          establishing, landscape, epic
    preset: str = None          # Optional preset override
) -> dict
```

**Returns:**
```json
{
  "success": true,
  "camera": "AutoFrame_Camera",
  "shot_type": "Close-Up (CU)",
  "composition_rule": "Rule of Thirds",
  "focal_length": 85,
  "fstop": 2.8,
  "position": [4.5, -4.5, 3.5],
  "distance": 5.2,
  "frame_fill": "75%"
}
```

**Example:**
```python
# Automatic portrait framing
auto_frame_with_composition(object_name="Character", purpose="portrait")

# Product hero shot
auto_frame_with_composition(object_name="Watch", purpose="product")

# Epic landscape
auto_frame_with_composition(object_name="Mountains", purpose="epic")
```

---

#### `apply_composition_rule()`
Apply specific composition rule with camera angle.

```python
apply_composition_rule(
    object_name: str,                    # Object to frame
    composition_rule: str = "rule_of_thirds",  # Composition rule
    camera_angle: str = "three_quarter"  # Camera angle preset
) -> dict
```

**Camera Angles:**
- `front` - Straight-on (0°)
- `three_quarter` - 45° angle (most common)
- `side` - 90° profile
- `top` - Top-down view (75° elevation)
- `low` - Low angle (5° elevation)
- `high` - High angle (35° elevation)

**Example:**
```python
# Rule of thirds with three-quarter view
apply_composition_rule(
    object_name="Statue",
    composition_rule="rule_of_thirds",
    camera_angle="three_quarter"
)

# Golden ratio with high angle
apply_composition_rule(
    object_name="Plaza",
    composition_rule="golden_ratio",
    camera_angle="high"
)
```

---

#### `calculate_shot_framing()`
Calculate camera position for specific shot type.

```python
calculate_shot_framing(
    object_name: str,
    shot_type: str = "medium_shot"
) -> dict
```

**Shot Types:**
- `extreme_closeup` - Extreme Close-Up (ECU)
- `closeup` - Close-Up (CU)
- `medium_closeup` - Medium Close-Up (MCU)
- `medium_shot` - Medium Shot (MS)
- `medium_wide` - Medium Wide Shot (MWS)
- `wide_shot` - Wide Shot (WS)
- `extreme_wide` - Extreme Wide Shot (EWS)

**Returns:**
```json
{
  "shot_type": "Close-Up (CU)",
  "description": "Subject fills frame with minimal background",
  "camera_position": [3.6, -3.6, 2.7],
  "focal_length": 85,
  "fstop": 2.8,
  "distance": 4.8,
  "frame_fill": "75%",
  "ideal_for": ["portraits", "products", "expressions"]
}
```

---

#### `analyze_scene_composition()`
Analyze current composition and get improvement suggestions.

```python
analyze_scene_composition(
    object_name: str = None,           # Object to analyze (or active)
    composition_rule: str = "rule_of_thirds"
) -> dict
```

**Returns:**
```json
{
  "object": "Cube",
  "camera": "Camera",
  "screen_position": {"x": 0.632, "y": 0.358},
  "composition_analysis": {
    "score": 87.3,
    "rule": "Rule of Thirds",
    "closest_point": [0.667, 0.333],
    "distance": 0.042,
    "recommendation": "Good composition. Minor adjustments could improve it.",
    "adjustments": {
      "horizontal_offset": 0.035,
      "vertical_offset": -0.025,
      "suggestions": ["Move camera slightly to the right"]
    }
  }
}
```

**Score Interpretation:**
- **90-100:** Excellent - Perfect alignment
- **70-89:** Good - Minor adjustments beneficial
- **50-69:** Acceptable - Repositioning recommended
- **30-49:** Weak - Significant improvement needed
- **0-29:** Poor - Major repositioning required

---

#### `suggest_composition()`
Get AI-powered composition recommendations.

```python
suggest_composition(
    object_name: str,
    scene_description: str = ""  # Optional context
) -> dict
```

**Returns:**
```json
{
  "object": "Portrait",
  "suggested_shot_type": "closeup",
  "suggested_composition_rule": "rule_of_thirds",
  "matching_presets": [
    {
      "name": "portrait_pro",
      "description": "Professional Portrait",
      "rule": "rule_of_thirds",
      "shot": "closeup"
    }
  ],
  "recommendation": "Use 'closeup' shot with 'rule_of_thirds' composition"
}
```

**Scene Description Keywords:**
- **Shot purpose:** `detail`, `macro`, `portrait`, `product`, `wide`, `landscape`, `epic`
- **Style:** `symmetrical`, `minimal`, `dynamic`, `dramatic`, `action`

**Example:**
```python
suggest_composition(object_name="Warrior", scene_description="dramatic action portrait")
# → Suggests: diagonal composition, closeup shot, dramatic preset

suggest_composition(object_name="Vase", scene_description="minimal product showcase")
# → Suggests: center composition, medium_closeup shot, product_hero preset
```

---

#### `list_composition_presets()`
List available composition options.

```python
list_composition_presets(category: str = "all") -> str
```

**Categories:**
- `all` - Everything
- `presets` - Quick setup presets
- `rules` - Composition rules
- `shots` - Shot types
- `framing` - Framing presets

---

## Presets

Composition presets are quick setups combining rule + shot type + camera angle.

### Portrait Presets

#### `portrait_pro` - Professional Portrait
Standard professional headshot.

```python
auto_frame_with_composition(object_name="Character", preset="portrait_pro")
```

- **Rule:** Rule of thirds
- **Shot:** Close-up (CU)
- **Angle:** 10° elevation, 45° azimuth
- **Use for:** Professional headshots, LinkedIn photos, character portraits

---

#### `portrait_cinematic` - Cinematic Portrait
Dramatic, film-quality portrait.

```python
auto_frame_with_composition(object_name="Hero", preset="portrait_cinematic")
```

- **Rule:** Golden ratio
- **Shot:** Medium close-up (MCU)
- **Angle:** 5° elevation, 30° azimuth
- **Use for:** Movie posters, dramatic characters, artistic portraits

---

### Product Presets

#### `product_hero` - Hero Product Shot
Centered, impactful product presentation.

```python
auto_frame_with_composition(object_name="Watch", preset="product_hero")
```

- **Rule:** Center composition
- **Shot:** Close-up (CU)
- **Angle:** 20° elevation, 45° azimuth
- **Use for:** E-commerce hero images, product launches, advertising

---

#### `product_lifestyle` - Lifestyle Product
Product in context with environment.

```python
auto_frame_with_composition(object_name="Phone", preset="product_lifestyle")
```

- **Rule:** Golden ratio
- **Shot:** Medium shot (MS)
- **Angle:** 15° elevation, 60° azimuth
- **Use for:** Lifestyle marketing, contextual product shots, in-use scenarios

---

### Architecture Presets

#### `architecture_hero` - Architecture Hero
Clean, professional architectural shot.

```python
auto_frame_with_composition(object_name="Building", preset="architecture_hero")
```

- **Rule:** Rule of thirds
- **Shot:** Wide shot (WS)
- **Angle:** 10° elevation, 30° azimuth
- **Use for:** Real estate, architectural portfolios, documentation

---

#### `architecture_dramatic` - Dramatic Architecture
Dynamic, eye-catching architectural composition.

```python
auto_frame_with_composition(object_name="Skyscraper", preset="architecture_dramatic")
```

- **Rule:** Diagonal composition
- **Shot:** Medium wide (MWS)
- **Angle:** 25° elevation, 45° azimuth
- **Use for:** Editorial, marketing, artistic architectural photography

---

### Landscape Presets

#### `landscape_classic` - Classic Landscape
Traditional landscape composition.

```python
auto_frame_with_composition(object_name="Mountains", preset="landscape_classic")
```

- **Rule:** Rule of thirds
- **Shot:** Wide shot (WS)
- **Angle:** 5° elevation, 0° azimuth (front)
- **Use for:** Nature photography, scenic vistas, travel

---

#### `landscape_epic` - Epic Landscape
Grand, sweeping landscape.

```python
auto_frame_with_composition(object_name="Valley", preset="landscape_epic")
```

- **Rule:** Golden ratio
- **Shot:** Extreme wide shot (EWS)
- **Angle:** 15° elevation, 0° azimuth
- **Use for:** Epic vistas, establishing shots, showcasing scale

---

## Workflow Examples

### Complete Enhancement Pipeline

Combine composition with geometry, materials, and lighting for professional results:

```python
# 1. Import model
import_generated_asset(name="character", task_uuid="xxx")

# 2. Enhance geometry
auto_enhance_geometry(object_name="character")

# 3. Enhance materials
auto_enhance_materials(object_name="character", aggressive=True)

# 4. Set up lighting
auto_setup_scene_lighting(
    scene_description="cinematic portrait lighting",
    target_object="character"
)

# 5. COMPOSITION - Frame the shot
auto_frame_with_composition(
    object_name="character",
    preset="portrait_cinematic"
)

# 6. Verify
get_viewport_screenshot()
```

---

### Product Photography Workflow

```python
# Import product model
download_sketchfab_model(uid="abc123")

# Enhance for product shot
auto_enhance_geometry(object_name="Product")
auto_enhance_materials(object_name="Product")

# Studio lighting
setup_hdri_lighting(preset="studio")
apply_lighting_rig(preset="studio", target_object="Product")

# Hero product composition
auto_frame_with_composition(object_name="Product", preset="product_hero")

# Configure high-quality render
configure_render_settings(preset="high")
```

---

### Architectural Visualization Workflow

```python
# Import building
download_polyhaven_asset(asset_id="modern_building", asset_type="models")

# Set up environment
setup_hdri_lighting(preset="outdoor_day")
apply_lighting_rig(preset="outdoor", target_object="Building")

# Dramatic architectural composition
auto_frame_with_composition(
    object_name="Building",
    preset="architecture_dramatic"
)

# Add atmosphere
add_atmospheric_fog(preset="haze")
```

---

### Portrait Studio Setup

```python
# Character model
import_generated_asset(name="portrait", task_uuid="xxx")

# Geometry enhancement
apply_enhancement_preset(object_name="portrait", preset="smooth")

# Portrait lighting
apply_lighting_rig(preset="portrait", target_object="portrait")

# Professional portrait framing
auto_frame_with_composition(
    object_name="portrait",
    preset="portrait_pro"
)

# Cinematic render settings
configure_render_settings(preset="cinematic")
```

---

## Advanced Usage

### Custom Camera Positioning

For fine-grained control, combine multiple tools:

```python
# 1. Get suggestions
suggestions = suggest_composition(
    object_name="Statue",
    scene_description="dramatic low angle hero shot"
)

# 2. Calculate framing
framing = calculate_shot_framing(
    object_name="Statue",
    shot_type="medium_closeup"
)

# 3. Apply with custom angle
apply_composition_rule(
    object_name="Statue",
    composition_rule="diagonal",
    camera_angle="low"  # Low angle for hero effect
)

# 4. Analyze result
analysis = analyze_scene_composition(
    object_name="Statue",
    composition_rule="diagonal"
)

# 5. Refine if needed
if analysis["composition_analysis"]["score"] < 70:
    # Try different rule or angle
    apply_composition_rule(
        object_name="Statue",
        composition_rule="rule_of_thirds",
        camera_angle="low"
    )
```

---

### Comparing Composition Rules

Test multiple rules to find the best:

```python
import json

rules_to_test = ["rule_of_thirds", "golden_ratio", "center_composition", "diagonal"]
results = []

for rule in rules_to_test:
    # Apply rule
    apply_composition_rule(
        object_name="Subject",
        composition_rule=rule,
        camera_angle="three_quarter"
    )
    
    # Analyze
    analysis = analyze_scene_composition(
        object_name="Subject",
        composition_rule=rule
    )
    
    results.append({
        "rule": rule,
        "score": analysis["composition_analysis"]["score"]
    })

# Find best
best = max(results, key=lambda x: x["score"])
print(f"Best composition: {best['rule']} (score: {best['score']})")
```

---

### Purpose-Driven Auto-Framing

Let the system choose everything based on purpose:

```python
# Detail/Macro work
auto_frame_with_composition(object_name="Gear", purpose="detail")
# → extreme_closeup or closeup, center composition

# Portrait work  
auto_frame_with_composition(object_name="Face", purpose="portrait")
# → closeup or medium_closeup, rule_of_thirds

# Product showcase
auto_frame_with_composition(object_name="Bottle", purpose="product")
# → closeup or medium_closeup, golden_ratio or center

# General scenes
auto_frame_with_composition(object_name="Scene", purpose="general")
# → medium_shot or medium_wide, rule_of_thirds or golden_ratio

# Establishing shots
auto_frame_with_composition(object_name="Cityscape", purpose="establishing")
# → wide_shot or extreme_wide, rule_of_thirds

# Epic landscapes
auto_frame_with_composition(object_name="Mountains", purpose="epic")
# → extreme_wide, golden_ratio
```

---

## Tips & Best Practices

### 1. **Start with Auto-Framing**
Use `auto_frame_with_composition()` first. It handles 90% of cases perfectly:
```python
auto_frame_with_composition(object_name="MyObject", purpose="general")
```

### 2. **Use Presets for Common Scenarios**
Presets are faster than manual setup:
```python
# Instead of manual setup...
auto_frame_with_composition(object_name="Product", preset="product_hero")

# ...which is equivalent to:
# - apply rule_of_thirds
# - set shot to closeup
# - configure 20° elevation, 45° azimuth
# - set DOF to f/2.8
```

### 3. **Combine with Lighting**
Composition works best with proper lighting:
```python
# 1. Set up lighting first
auto_setup_scene_lighting(scene_description="portrait", target_object="Character")

# 2. Then composition
auto_frame_with_composition(object_name="Character", preset="portrait_pro")
```

### 4. **Analyze Before Fine-Tuning**
Check composition score before manual adjustments:
```python
analysis = analyze_scene_composition(object_name="Subject")
if analysis["composition_analysis"]["score"] < 70:
    # Needs improvement
    auto_frame_with_composition(object_name="Subject", purpose="general")
```

### 5. **Match Shot Type to Subject Size**
- **Tiny objects** (< 1 unit): extreme_closeup, closeup
- **Small objects** (1-2 units): closeup, medium_closeup
- **Medium objects** (2-5 units): medium_shot, medium_wide
- **Large objects** (> 5 units): wide_shot, extreme_wide

### 6. **Choose Rule Based on Content**
- **Organic/Natural:** golden_ratio
- **Standard professional:** rule_of_thirds
- **Symmetrical:** center_composition
- **Dynamic/Action:** diagonal
- **Storytelling:** frame_within_frame, leading_lines

### 7. **Camera Angle Affects Mood**
- **Front (0°):** Neutral, documentary
- **Three-quarter (45°):** Natural, engaging (most common)
- **Side (90°):** Profile, silhouette
- **Top:** Bird's eye, overview
- **Low:** Heroic, powerful, dramatic
- **High:** Vulnerability, scale, context

---

## Troubleshooting

### Issue: "Object not found"
**Solution:** Ensure object name is exact (case-sensitive):
```python
# Check object names
scene_info = get_scene_info()
# Use exact name from scene_info
```

### Issue: Camera too close/far
**Solution:** Manually specify shot type:
```python
# Too close? Use wider shot
calculate_shot_framing(object_name="Object", shot_type="wide_shot")

# Too far? Use closer shot
calculate_shot_framing(object_name="Object", shot_type="closeup")
```

### Issue: Subject off-center when using center_composition
**Solution:** Center composition needs symmetrical subjects. Try rule_of_thirds:
```python
apply_composition_rule(object_name="Object", composition_rule="rule_of_thirds")
```

### Issue: Low composition score
**Solutions:**
1. Try different composition rule
2. Adjust camera angle
3. Use auto_frame_with_composition() for automatic optimization

```python
# Get suggestions
suggestions = suggest_composition(object_name="Object", scene_description="...")

# Apply suggested rule
apply_composition_rule(
    object_name="Object",
    composition_rule=suggestions["suggested_composition_rule"]
)
```

---

## Integration with Other Systems

The Composition System integrates seamlessly with Material, Post-Processing, and Lighting systems:

```python
# COMPLETE PROFESSIONAL WORKFLOW

# 1. Import Asset
download_sketchfab_model(uid="model_uid")

# 2. Geometry (Post-Processing System)
auto_enhance_geometry(object_name="Model")

# 3. Materials (Material System)
auto_enhance_materials(object_name="Model", aggressive=True)

# 4. Lighting (Lighting System)
auto_setup_scene_lighting(
    scene_description="cinematic product shot",
    target_object="Model"
)

# 5. Composition (Composition System) ⭐ NEW
auto_frame_with_composition(
    object_name="Model",
    preset="product_hero"
)

# 6. Verify
get_viewport_screenshot()

# 7. Render
configure_render_settings(preset="high")
```

This workflow transforms any model from basic import to production-ready render in seconds!

---

## Summary

**Quick Reference Card:**

| Task | Recommended Tool | Example |
|------|------------------|---------|
| **Quick auto-setup** | `auto_frame_with_composition()` | `auto_frame_with_composition("Object", purpose="general")` |
| **Use preset** | `auto_frame_with_composition()` | `auto_frame_with_composition("Object", preset="portrait_pro")` |
| **Specific rule** | `apply_composition_rule()` | `apply_composition_rule("Object", composition_rule="golden_ratio")` |
| **Specific shot** | `calculate_shot_framing()` | `calculate_shot_framing("Object", shot_type="closeup")` |
| **Get suggestions** | `suggest_composition()` | `suggest_composition("Object", scene_description="dramatic")` |
| **Check current** | `analyze_scene_composition()` | `analyze_scene_composition("Object")` |
| **List options** | `list_composition_presets()` | `list_composition_presets(category="presets")` |

**Most Common Workflows:**

1. **Portrait:** `auto_frame_with_composition(object_name="Character", preset="portrait_pro")`
2. **Product:** `auto_frame_with_composition(object_name="Product", preset="product_hero")`
3. **Architecture:** `auto_frame_with_composition(object_name="Building", preset="architecture_hero")`
4. **Landscape:** `auto_frame_with_composition(object_name="Scenery", preset="landscape_classic")`
5. **General:** `auto_frame_with_composition(object_name="Object", purpose="general")`

---

**Next Steps:**
- Combine with [Lighting System](LIGHTING_SYSTEM.md) for complete scene setup
- Use with [Material System](MATERIAL_SYSTEM.md) for realistic surfaces
- Enhance geometry with [Post-Processing](POST_PROCESSING.md) before composing shots

Happy framing! 📸
