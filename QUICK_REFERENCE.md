# Quick Reference: Complete Enhancement Pipeline

## One-Command Enhancement

```python
# Generate AI model
generate_hyper3d_model_via_text(text_prompt="vintage telephone booth")
import_generated_asset(name="booth", task_uuid="...")

# Enhance everything (geometry + materials + lighting)
auto_enhance_geometry("booth")
auto_enhance_materials("booth", aggressive=True)
auto_setup_scene_lighting("dramatic outdoor booth", "booth")

# Done!
get_viewport_screenshot()
```

---

## System Quick Reference

### 1. Material System

```python
# Auto-apply materials to all objects
auto_enhance_materials()

# Aggressive mode for maximum improvement
auto_enhance_materials(aggressive=True)

# Apply specific material to object
apply_material_preset("MyObject", "weathered_metal")

# Get suggestion
suggest_material("MyObject")

# List all materials
list_material_presets()
```

**Popular Materials**: weathered_metal, brushed_metal, clear_glass, glossy_paint, polished_wood, chrome, concrete

---

### 2. Post-Processing System

```python
# Auto-enhance geometry for all objects
auto_enhance_geometry()

# Apply specific preset
apply_enhancement_preset("MyObject", "high_detail")

# Analyze mesh first
analyze_mesh("MyObject")

# Get suggestion
suggest_enhancement("MyObject")

# List all presets
list_enhancement_presets()
```

**Popular Presets**: high_detail (hero objects), smooth (general), mechanical (hard surface), organic (characters)

---

### 3. Lighting System

```python
# Complete auto-setup (easiest)
auto_setup_scene_lighting("dramatic outdoor", "MyObject")

# Or manual setup:
setup_hdri_lighting("sunset")
apply_lighting_rig("three_point")
add_atmospheric_fog("god_rays")
setup_camera("portrait", target_object="MyObject")
configure_render_settings("production")

# List options
list_lighting_presets("all")
```

**Popular Combinations**:
- Product: studio HDRI + studio rig + no atmosphere
- Outdoor: outdoor_day HDRI + outdoor rig + haze
- Dramatic: sunset HDRI + dramatic rig + god_rays
- Night: night HDRI + night rig + fog

---

## Complete Workflow Examples

### Example 1: Product Shot

```python
# Import
download_polyhaven_asset("watch_model", "models", "2k")

# Enhance
auto_enhance_geometry("watch_model")
apply_material_preset("watch_model", "brushed_metal")
setup_hdri_lighting("studio")
apply_lighting_rig("studio")
setup_camera("normal", target_object="watch_model")
configure_render_settings("production")

get_viewport_screenshot()
```

### Example 2: Dramatic Scene

```python
# Generate
generate_hyper3d_model_via_text(text_prompt="old rusty telephone booth")
import_generated_asset(name="booth", task_uuid="...")

# Enhance (all-in-one)
auto_enhance_geometry("booth")
auto_enhance_materials("booth", aggressive=True)
auto_setup_scene_lighting("dramatic sunset outdoor", "booth")

get_viewport_screenshot()
```

### Example 3: Night Scene

```python
# Import
download_sketchfab_model(uid="abc123")

# Enhance
apply_enhancement_preset("Sketchfab_model", "high_detail")
auto_enhance_materials("Sketchfab_model")
setup_hdri_lighting("night", strength=0.3)
apply_lighting_rig("night", scale=1.5)
add_atmospheric_fog("fog", density=0.08)
setup_camera("wide", target_object="Sketchfab_model")
configure_render_settings("production")

get_viewport_screenshot()
```

---

## Preset Quick Reference

### Materials (20+)
```
METALS          GLASS           PAINT           WOOD
weathered_metal clear_glass     glossy_paint    polished_wood
brushed_metal   frosted_glass   matte_paint     rough_wood
rusted_metal    tinted_glass    weathered_paint
chrome                          car_paint       STONE
                                                concrete
PLASTIC         SPECIAL         stone
glossy_plastic  emission
rubber          glow
```

### Enhancement Presets (5)
```
smooth       - General purpose (2 levels, auto-smooth)
high_detail  - Maximum quality (3 levels, beveling)
mechanical   - Hard surfaces (beveling, sharp edges)
organic      - Smooth shapes (subdivision, remeshing)
architectural- Buildings (minimal subdivision)
```

### HDRI Presets (6)
```
studio      - Neutral studio (strength: 1.0)
outdoor_day - Bright daylight (strength: 1.0)
sunset      - Golden hour (strength: 0.8)
night       - Moonlight (strength: 0.3)
overcast    - Soft sky (strength: 0.9)
interior    - Indoor ambient (strength: 0.7)
```

### Lighting Rigs (5)
```
three_point - Key + fill + rim (3 lights)
studio      - Product photography (4 lights)
dramatic    - High contrast (2 lights)
outdoor     - Sun + sky (2 lights)
night       - Street lights (3 lights)
```

### Atmosphere (5)
```
fog        - Volumetric fog (density: 0.05)
heavy_fog  - Dense fog (density: 0.15)
god_rays   - Light shafts (density: 0.03, anisotropy: 0.5)
haze       - Subtle haze (density: 0.01)
none       - Clear
```

### Camera (5)
```
portrait      - 85mm, f/2.8 (DOF enabled)
wide          - 24mm, f/8.0 (no DOF)
normal        - 50mm, f/5.6 (DOF enabled)
telephoto     - 135mm, f/2.0 (DOF enabled)
architectural - 35mm, f/11.0 (no DOF)
```

### Render (4)
```
draft      - Eevee, 64 samples, 50% res (fast preview)
preview    - Cycles, 128 samples, 75% res (quality check)
production - Cycles, 512 samples, 100% res (final)
final      - Cycles, 2048 samples, 100% res (max quality)
```

---

## Decision Tree

### What Material?
- **Metal object** → weathered_metal, brushed_metal, or chrome
- **Transparent** → clear_glass or frosted_glass
- **Painted** → glossy_paint or car_paint
- **Wood** → polished_wood or rough_wood
- **Plastic** → glossy_plastic or rubber
- **Stone/Concrete** → concrete or stone
- **Glowing** → emission or glow

### What Enhancement Preset?
- **Polygon count < 1000** → high_detail
- **Character/organic** → organic
- **Vehicle/product** → mechanical or smooth
- **Building** → architectural
- **General object** → smooth

### What Lighting Setup?
- **Product photo** → studio HDRI + studio rig
- **Outdoor day** → outdoor_day HDRI + outdoor rig + haze
- **Dramatic/cinematic** → sunset HDRI + dramatic rig + god_rays
- **Night scene** → night HDRI + night rig + fog
- **Interior** → interior HDRI + three_point rig + haze

### What Camera?
- **Portrait/character** → portrait (85mm, shallow DOF)
- **Product** → normal (50mm)
- **Architecture** → architectural (35mm, no DOF)
- **Wide scene** → wide (24mm)
- **Compressed perspective** → telephoto (135mm)

### What Render Quality?
- **First preview** → draft (Eevee, fast)
- **Iterating** → preview (Cycles, moderate)
- **Final check** → production (Cycles, high quality)
- **Publication** → final (Cycles, maximum)

---

## Common Patterns

### Pattern 1: AI Model → Production Quality
```python
# Import AI-generated low-poly model
import_generated_asset(name="object", task_uuid="...")

# Triple enhancement
auto_enhance_geometry("object")           # Fix low-poly
auto_enhance_materials("object", True)    # Add realistic materials
auto_setup_scene_lighting("scene", "object")  # Professional lighting
```

### Pattern 2: Library Asset → Customized
```python
# Import from library
download_polyhaven_asset("asset_id", "models")

# Customize
apply_enhancement_preset("asset_id", "high_detail")
apply_material_preset("asset_id", "custom_material")
setup_hdri_lighting("custom_hdri", rotation=45, strength=1.2)
```

### Pattern 3: Rapid Iteration
```python
# Fast preview mode
configure_render_settings("draft")

# Try different looks quickly
apply_material_preset("obj", "chrome")
get_viewport_screenshot()

apply_material_preset("obj", "weathered_metal")
get_viewport_screenshot()

apply_material_preset("obj", "brushed_metal")
get_viewport_screenshot()

# Pick winner, upgrade to production
configure_render_settings("production")
```

---

## Troubleshooting

### Object looks blocky
**Fix**: Apply geometry enhancement
```python
auto_enhance_geometry("MyObject")
# or
apply_enhancement_preset("MyObject", "high_detail")
```

### Materials look flat
**Fix**: Apply material enhancement
```python
auto_enhance_materials("MyObject", aggressive=True)
# or
apply_material_preset("MyObject", "weathered_metal")
```

### Scene too dark
**Fix**: Increase lighting
```python
setup_hdri_lighting("studio", strength=1.5)
apply_lighting_rig("studio", scale=1.2)
```

### Fog not visible
**Fix**: Check engine and increase density
```python
configure_render_settings("production")  # Use Cycles
add_atmospheric_fog("fog", density=0.1)
```

### Camera not framing correctly
**Fix**: Specify target object
```python
setup_camera("normal", target_object="MyObject")
```

---

## Performance Tips

1. **Start with draft renders** while setting up
2. **Use preview for quality checks** (75% resolution)
3. **Switch to production only when ready** for final output
4. **Limit fog density** if render is slow (< 0.1)
5. **Use Eevee for iteration**, Cycles for final
6. **Apply enhancements to visible objects only**
7. **Scale lighting rigs** if scene is large/small

---

## Keyboard Commands (in Blender)

While working in Blender viewport:
- `Z` → Shading menu (switch to Rendered/Material Preview)
- `Numpad 0` → Camera view
- `Shift + A` → Add menu
- `G` → Move, `R` → Rotate, `S` → Scale
- `Tab` → Edit mode
- `F12` → Render

---

## Best Practice Checklist

For every AI-generated model:

- [ ] Import model
- [ ] Run `analyze_mesh()` to check polygon count
- [ ] Apply `auto_enhance_geometry()` if faces < 2000
- [ ] Check `get_object_info()` for materials
- [ ] Apply `auto_enhance_materials(aggressive=True)`
- [ ] Use `auto_setup_scene_lighting()` with description
- [ ] Verify with `get_viewport_screenshot()`
- [ ] Adjust individual elements as needed
- [ ] Set production render settings
- [ ] Final render

---

## Integration with Blender Workflow

These systems are designed to work with existing Blender features:

**After Enhancement, you can**:
- Manually adjust materials in Shader Editor
- Fine-tune light positions in 3D Viewport
- Edit geometry in Edit Mode
- Adjust camera in Camera Properties
- Modify render settings in Render Properties
- Add additional effects (compositing, etc.)

The enhancement systems provide a **professional starting point**, not a restriction.

---

For detailed information, see:
- [MATERIAL_SYSTEM.md](MATERIAL_SYSTEM.md)
- [POST_PROCESSING.md](POST_PROCESSING.md)
- [LIGHTING_SYSTEM.md](LIGHTING_SYSTEM.md)
- [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md)
