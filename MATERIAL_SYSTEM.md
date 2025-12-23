# Material System Enhancement

## Overview

The Material System dramatically improves the visual quality of 3D models in Blender MCP by providing:

- **20+ PBR Material Presets**: Realistic materials for metals, glass, paint, wood, plastics, and more
- **Automatic Material Assignment**: AI-driven material suggestions based on object names
- **Procedural Textures**: Built-in procedural shaders for scratches, dirt, wood grain, and surface details
- **One-Command Enhancement**: Transform basic models into photorealistic objects instantly

## Why This Matters

AI-generated 3D models (from Hunyuan3D, Hyper3D Rodin) typically have:
- Basic or missing materials
- Flat, unrealistic surfaces
- No surface detail or imperfections
- Poor lighting response

The Material System fixes this by automatically applying realistic PBR materials with procedural details.

## Quick Start

### Auto-Enhance All Objects
```python
# Enhance all objects in the scene automatically
auto_enhance_materials()

# More dramatic enhancement with extra procedural details
auto_enhance_materials(aggressive=True)

# Enhance a specific object
auto_enhance_materials(object_name="telephone_booth")
```

### Apply Specific Materials
```python
# Get a suggestion for an object
suggest_material("window")  # Returns: "frosted_glass"

# Apply the suggested material
apply_material_preset("window", "frosted_glass")

# Override with custom color
apply_material_preset("car_body", "car_paint", color=[0.8, 0.1, 0.1])  # Red car paint
```

### Browse Available Materials
```python
# List all presets
list_material_presets()

# List by category
list_material_presets(category="metals")
list_material_presets(category="glass")
```

## Material Presets

### Metals
- **weathered_metal**: Aged metal with surface variation and rust
- **brushed_metal**: Anisotropic brushed finish (aluminum, steel)
- **rusted_metal**: Heavy oxidation and corrosion
- **chrome**: Mirror-like polished metal finish

### Glass & Transparency
- **clear_glass**: Crystal clear glass (windows, lenses)
- **frosted_glass**: Translucent with surface noise
- **tinted_glass**: Colored transparent glass

### Paint & Coatings
- **glossy_paint**: Shiny painted surface with clearcoat
- **matte_paint**: Flat, non-reflective paint
- **weathered_paint**: Aged paint with scratches and dirt
- **car_paint**: Automotive finish with metallic flakes and clearcoat

### Plastics
- **glossy_plastic**: Shiny ABS/polycarbonate finish
- **rubber**: Matte rubber with micro-bump detail

### Wood
- **polished_wood**: Smooth varnished wood with grain
- **rough_wood**: Unfinished wood with pronounced grain

### Stone & Concrete
- **concrete**: Industrial concrete with surface variation
- **stone**: Natural rock texture

### Fabric
- **fabric**: Woven textile material

### Special Effects
- **emission**: Glowing emissive material (lights, screens)
- **glow**: Soft luminous glow

## Custom Materials

Create materials with specific properties:

```python
create_custom_pbr_material(
    object_name="my_object",
    base_color=[0.8, 0.2, 0.1, 1.0],  # RGBA
    metallic=0.9,          # 0=dielectric, 1=metal
    roughness=0.3,         # 0=glossy, 1=rough
    transmission=0.0,      # 0=opaque, 1=transparent
    emission_strength=0.0, # Glow intensity
    clearcoat=0.5          # Extra glossy layer
)
```

## Smart Material Suggestions

The system analyzes object names to suggest appropriate materials:

| Object Name Contains | Suggested Material |
|---------------------|-------------------|
| window, glass, lens | frosted_glass |
| metal, steel, iron | brushed_metal |
| chrome, aluminum | chrome |
| car, vehicle | car_paint |
| wood, table, chair | polished_wood |
| concrete, cement | concrete |
| plastic, button | glossy_plastic |
| light, lamp, bulb | emission |

## Procedural Details

Materials can include procedural textures for realism:

### Noise Variation
Adds subtle surface imperfections to roughness
```python
"procedural": {
    "type": "noise",
    "scale": 15.0,
    "detail": 8.0,
    "roughness_variation": 0.3
}
```

### Scratches & Dirt
Layered scratches and dirt accumulation
```python
"procedural": {
    "type": "scratches_and_dirt",
    "scale": 20.0,
    "detail": 5.0
}
```

### Wood Grain
Realistic wood texture with rings
```python
"procedural": {
    "type": "wood_grain",
    "scale": 5.0,
    "detail": 8.0
}
```

### Concrete/Rock
Surface bump and variation
```python
"procedural": {
    "type": "concrete",
    "scale": 8.0,
    "detail": 4.0
}
```

## Workflow Integration

### After AI Model Generation
```python
# 1. Generate model
generate_hyper3d_model_via_text(text_prompt="vintage telephone booth")

# 2. Wait for completion
poll_rodin_job_status(subscription_key="...")

# 3. Import
import_generated_asset(name="booth", task_uuid="...")

# 4. ENHANCE MATERIALS (NEW!)
auto_enhance_materials(object_name="booth", aggressive=True)

# 5. Verify with screenshot
get_viewport_screenshot()
```

### Scene-Wide Enhancement
```python
# Get scene info
scene = get_scene_info()

# Import multiple models...

# Enhance everything at once
auto_enhance_materials()  # Enhances all mesh objects

# Check results
get_viewport_screenshot()
```

## Advanced Usage

### Target Specific Object Types

The auto-enhancement recognizes object name patterns:

- Objects with "window" → frosted_glass
- Objects with "metal" → brushed_metal  
- Objects with "door" → weathered_paint
- Objects with "light" → emission
- Objects with "wood" → polished_wood

### Progressive Enhancement

```python
# Basic enhancement
apply_material_preset("object", "matte_paint")

# Add procedural details manually via code
execute_blender_code("""
import bpy
mat = bpy.data.materials.get("matte_paint_object")
if mat:
    nodes = mat.node_tree.nodes
    # Add custom procedural nodes...
""")
```

## API Reference

### auto_enhance_materials(object_name=None, aggressive=False)
Automatically enhance materials on objects based on name analysis.

**Parameters:**
- `object_name` (str, optional): Specific object to enhance. If None, enhances all mesh objects
- `aggressive` (bool): Add extra procedural details for more dramatic enhancement

**Returns:** Success message with list of enhanced objects

---

### apply_material_preset(object_name, material_preset, color=None)
Apply a specific material preset to an object.

**Parameters:**
- `object_name` (str): Name of target object
- `material_preset` (str): Name of preset (see list_material_presets)
- `color` (list, optional): Override color [R, G, B, A] (0.0-1.0)

**Returns:** Success/error message

---

### list_material_presets(category=None)
List available material presets.

**Parameters:**
- `category` (str, optional): Filter by category (metals, glass, paint, plastic, wood, fabric, stone, special)

**Returns:** Formatted list of materials

---

### suggest_material(object_name)
Get material suggestion based on object name.

**Parameters:**
- `object_name` (str): Name of object to analyze

**Returns:** Suggested material name and properties

---

### create_custom_pbr_material(...)
Create custom PBR material with specific properties.

**Parameters:**
- `object_name` (str): Target object
- `base_color` (list): RGBA color [0.0-1.0]
- `metallic` (float): 0.0-1.0
- `roughness` (float): 0.0-1.0
- `specular` (float): 0.0-1.0
- `transmission` (float): 0.0-1.0
- `emission_strength` (float): 0.0+
- `clearcoat` (float): 0.0-1.0

**Returns:** Success/error message

## Technical Details

### Implementation
- **Server**: New tools in `src/blender_mcp/server.py`
- **Materials Module**: Presets and logic in `src/blender_mcp/materials.py`
- **Addon Integration**: Command handlers in `addon.py`
- **Shader Generation**: Procedural node creation in Blender's shader graph

### Blender Node System
The system creates Principled BSDF shaders with:
- Base color and PBR properties
- Procedural texture nodes (Noise, Wave, etc.)
- Mix and ColorRamp nodes for layering
- Bump nodes for surface detail
- Proper linking to Material Output

### Performance
- Lightweight: Procedural textures use minimal memory
- Fast: Materials created instantly
- Scalable: Can enhance entire scenes at once

## Best Practices

1. **Always enhance after import**: AI models need material improvement
2. **Use auto-enhance first**: Let the system suggest materials automatically
3. **Check with screenshots**: Verify materials look good before proceeding
4. **Aggressive mode for hero objects**: Use `aggressive=True` for main subjects
5. **Custom colors**: Override colors while keeping material properties
6. **Scene consistency**: Apply similar material styles across related objects

## Troubleshooting

### Materials look too dark
- Increase emission_strength for glowing parts
- Reduce roughness for shinier surfaces
- Check scene lighting (add HDRI)

### Materials look too simple
- Use `aggressive=True` mode
- Manually apply materials with procedural details
- Check that procedural scale matches object size

### Wrong material applied
- Use `suggest_material()` to see what was chosen
- Manually apply correct preset with `apply_material_preset()`
- Check object naming for keyword matches

## Future Enhancements

Planned improvements:
- Image-based material extraction
- Material libraries from reference photos
- Automatic UV unwrapping for complex models
- Advanced procedural systems (Substance-like)
- Material blending and layering
- Export material presets

## Examples

See the telephone booth example:
- Before: Basic geometry with flat colors
- After: Weathered blue paint, frosted glass windows, brushed metal details

```python
# Complete telephone booth enhancement
auto_enhance_materials(object_name="booth", aggressive=True)
apply_material_preset("booth_windows", "frosted_glass")
apply_material_preset("booth_phone", "chrome")
apply_material_preset("booth_frame", "weathered_metal")
```
