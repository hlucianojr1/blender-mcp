# Composition System - Quick Reference

## ⚡ Quick Commands

### Auto-Frame (Most Common)
```python
# General purpose
auto_frame_with_composition(object_name="Object", purpose="general")

# Portrait
auto_frame_with_composition(object_name="Character", purpose="portrait")

# Product
auto_frame_with_composition(object_name="Product", purpose="product")

# Architecture
auto_frame_with_composition(object_name="Building", purpose="architecture")

# Landscape
auto_frame_with_composition(object_name="Mountains", purpose="landscape")
```

### Presets (Quick Setups)
```python
# Portrait
auto_frame_with_composition(object_name="Character", preset="portrait_pro")
auto_frame_with_composition(object_name="Hero", preset="portrait_cinematic")

# Product
auto_frame_with_composition(object_name="Watch", preset="product_hero")
auto_frame_with_composition(object_name="Phone", preset="product_lifestyle")

# Architecture
auto_frame_with_composition(object_name="Building", preset="architecture_hero")
auto_frame_with_composition(object_name="Tower", preset="architecture_dramatic")

# Landscape
auto_frame_with_composition(object_name="Vista", preset="landscape_classic")
auto_frame_with_composition(object_name="Valley", preset="landscape_epic")
```

## 📐 Composition Rules

| Rule | Use For | Example |
|------|---------|---------|
| **rule_of_thirds** | General, portraits, products | Professional standard |
| **golden_ratio** | Fine art, nature, architecture | Elegant balance |
| **center_composition** | Symmetry, patterns, minimalism | Bold impact |
| **diagonal** | Action, dynamics, movement | Energetic |
| **leading_lines** | Depth, perspective | Architectural |
| **frame_within_frame** | Storytelling, context | Layered |

## 🎥 Shot Types

| Shot | Frame Fill | Use Case |
|------|-----------|----------|
| **extreme_closeup** | 95% | Details, textures, macro |
| **closeup** | 75% | Portraits, products |
| **medium_closeup** | 55% | Interviews, context |
| **medium_shot** | 40% | General balanced |
| **medium_wide** | 25% | Establishing, setting |
| **wide_shot** | 15% | Landscapes, architecture |
| **extreme_wide** | 8% | Epic vistas, scale |

## 🔧 Manual Control

```python
# Specific composition rule
apply_composition_rule(
    object_name="Cube",
    composition_rule="rule_of_thirds",
    camera_angle="three_quarter"
)

# Specific shot type
calculate_shot_framing(
    object_name="Statue",
    shot_type="medium_shot"
)

# Get suggestions
suggest_composition(
    object_name="Object",
    scene_description="dramatic portrait"
)

# Analyze current composition
analyze_scene_composition(
    object_name="Object",
    composition_rule="rule_of_thirds"
)

# List all options
list_composition_presets(category="presets")
```

## 📸 Camera Angles

- `front` - Straight-on (0°)
- `three_quarter` - 45° angle (most common)
- `side` - 90° profile
- `top` - Top-down view
- `low` - Low angle (heroic)
- `high` - High angle (scale)

## 🎯 Complete Workflow

```python
# 1. Import
download_sketchfab_model(uid="abc123")

# 2. Geometry
auto_enhance_geometry(object_name="Model")

# 3. Materials
auto_enhance_materials(object_name="Model", aggressive=True)

# 4. Lighting
auto_setup_scene_lighting(
    scene_description="cinematic product",
    target_object="Model"
)

# 5. COMPOSITION ⭐ NEW
auto_frame_with_composition(
    object_name="Model",
    preset="product_hero"
)

# 6. Verify
get_viewport_screenshot()
```

## 💡 Tips

1. **Start with auto_frame_with_composition()** - handles 90% of cases
2. **Use presets for speed** - pre-configured professional setups
3. **Combine with lighting** - composition needs good lighting to shine
4. **Analyze before tweaking** - check score first
5. **Match shot to subject size** - tiny objects need closeups, large objects need wide shots

## 📊 Composition Score Interpretation

- **90-100:** ✅ Excellent - Perfect alignment
- **70-89:** ✅ Good - Minor adjustments beneficial
- **50-69:** ⚠️ Acceptable - Repositioning recommended
- **30-49:** ⚠️ Weak - Significant improvement needed
- **0-29:** ❌ Poor - Major repositioning required

## 🔗 Integration

Works seamlessly with:
- **Material System** - Realistic surfaces
- **Post-Processing** - Smooth geometry
- **Lighting System** - Professional lighting

See [COMPOSITION_SYSTEM.md](COMPOSITION_SYSTEM.md) for complete documentation.
