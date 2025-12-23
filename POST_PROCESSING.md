# Post-Processing Pipeline

## Overview

The Post-Processing Pipeline dramatically improves the geometric quality of AI-generated 3D models by providing:

- **5 Enhancement Presets**: Pre-configured modifier stacks for different object types
- **Automatic Mesh Analysis**: Intelligent quality assessment and recommendations
- **Subdivision Surface**: Smooth low-poly geometry without regeneration
- **Edge Beveling**: Realistic edge softening for hard-surface models
- **Smart Shading**: Auto-smooth for optimal lighting response
- **One-Command Enhancement**: `auto_enhance_geometry()` applies optimal settings automatically

## Why This Matters

AI-generated 3D models typically suffer from:
- **Very low polygon counts** (often < 1000 faces) resulting in blocky appearance
- **No edge beveling** causing unrealistic sharp corners
- **Flat shading** making surfaces look faceted
- **Poor subdivision topology** limiting refinement options

The Post-Processing Pipeline fixes these issues by applying industry-standard modifiers and techniques.

## Quick Start

### Auto-Enhance (Recommended)
```python
# Enhance geometry automatically based on analysis
auto_enhance_geometry(object_name="telephone_booth")

# Enhance all mesh objects in scene
auto_enhance_geometry()
```

### Apply Specific Preset
```python
# High detail for hero objects (telephone booth, vehicles, props)
apply_enhancement_preset("telephone_booth", "high_detail")

# Mechanical for hard-surface objects (robots, machines)
apply_enhancement_preset("robot_arm", "mechanical")

# Smooth for general objects
apply_enhancement_preset("furniture", "smooth")

# Organic for characters and natural forms
apply_enhancement_preset("tree", "organic")

# Architectural for buildings
apply_enhancement_preset("building", "architectural")
```

### Analyze Before Enhancement
```python
# Get detailed mesh analysis
analyze_mesh("imported_model")

# Returns:
# - Polygon count (vertices, faces, tris, quads, ngons)
# - Quality assessment (low/medium/high priority)
# - Specific suggestions for improvement
# - Recommended preset
```

## Enhancement Presets

### 1. **smooth** (Default)
Best for: General purpose objects, furniture, props

**Applied Modifiers:**
- Subdivision Surface: 2 viewport / 3 render levels
- Edge Split: 30° angle
- Smooth Shading with Auto-Smooth (30°)

**Effect:** Balanced quality improvement with moderate performance impact

---

### 2. **high_detail** (Maximum Quality)
Best for: Hero objects, close-up shots, telephone booths, vehicles, jewelry

**Applied Modifiers:**
- Subdivision Surface: 3 viewport / 4 render levels
- Edge Split: 20° angle (preserves more details)
- Edge Bevel: 0.01 width, 2 segments
- Smooth Shading with Auto-Smooth (20°)

**Effect:** Maximum quality with significant geometry increase (up to 256x faces at render)

---

### 3. **mechanical** (Hard Surface)
Best for: Robots, machines, tools, weapons, manufactured objects

**Applied Modifiers:**
- Edge Bevel: 0.02 width, 3 segments (larger, softer bevels)
- Edge Split: 45° angle (maintains hard edges)
- Smooth Shading with Auto-Smooth (45°)
- No Subdivision (preserves hard edges)

**Effect:** Clean, manufactured look with realistic edge wear

---

### 4. **organic** (Natural Forms)
Best for: Characters, creatures, trees, terrain

**Applied Modifiers:**
- Subdivision Surface: 2 viewport / 3 render levels (no creases)
- Remesh: Smooth mode, octree depth 6
- Smooth Shading (no auto-smooth)

**Effect:** Smooth, natural forms with even geometry distribution

---

### 5. **architectural** (Buildings & Structures)
Best for: Buildings, walls, floors, architectural elements

**Applied Modifiers:**
- Subdivision Surface: 1 viewport / 2 render levels
- Edge Split: 30° angle
- Edge Bevel: 0.005 width, 2 segments (subtle)
- Flat Shading (crisp surfaces)

**Effect:** Clean architectural look with crisp edges and flat surfaces

## Individual Tools

### Subdivision Surface
```python
apply_subdivision_surface(
    object_name="model",
    viewport_levels=2,    # 0-6
    render_levels=3,      # 0-6
    adaptive=True         # Better performance
)
```

**Impact:** Each level quadruples face count
- Level 1: 4x faces
- Level 2: 16x faces
- Level 3: 64x faces
- Level 4: 256x faces

### Edge Beveling
```python
add_edge_bevel(
    object_name="model",
    width=0.01,    # Distance from edge
    segments=2     # Bevel smoothness
)
```

**Use Cases:**
- Realistic edge wear
- Prevent unrealistic sharp corners
- Catch and reflect light properly

### Shading Control
```python
set_shading(
    object_name="model",
    smooth=True,              # True=smooth, False=flat
    auto_smooth_angle=30.0    # Degrees (0-180)
)
```

**Auto-Smooth:** Automatically shades angles above threshold as sharp

## Mesh Analysis

### Get Detailed Statistics
```python
analyze_mesh("my_object")
```

**Returns:**
```
Mesh Analysis for 'my_object':

Statistics:
  Vertices: 542
  Faces: 486
  Triangles: 124
  Quads: 362
  Ngons: 0

Quality: HIGH

Suggestions:
  • Very low polygon count - consider subdivision
  • Recommended preset: high_detail
```

### Quality Indicators

| Face Count | Quality | Recommendation |
|-----------|---------|----------------|
| < 500 | High Priority | Apply high_detail preset |
| 500-2000 | Medium Priority | Apply smooth or subdivision |
| 2000-20000 | Good | Optional enhancement |
| > 20000 | Excellent | Minimal or no enhancement |

## Workflow Integration

### Complete Enhancement Workflow
```python
# 1. Import AI-generated model
import_generated_asset(name="booth", task_uuid="...")

# 2. ANALYZE the mesh
stats = analyze_mesh("booth")
# Shows: 842 faces → "HIGH priority - very low poly"

# 3. ENHANCE GEOMETRY
auto_enhance_geometry("booth")
# Applies high_detail preset automatically
# Result: ~13,000 faces viewport, ~200,000 faces render

# 4. ENHANCE MATERIALS
auto_enhance_materials("booth", aggressive=True)
# Applies weathered_paint, frosted_glass, etc.

# 5. VERIFY
get_viewport_screenshot()
# Visual confirmation of improvements
```

### Suggested Enhancement
```python
# Get smart recommendation
suggest_enhancement("telephone_booth")
```

**Returns:**
```
Suggested enhancement for 'telephone_booth': HIGH_DETAIL

This preset will apply:
  • Subdivision surface (3 viewport, 4 render)
  • Edge bevel (width: 0.01, segments: 2)
  • Edge split at 20°
  • Smooth shading with auto-smooth at 20°

To apply: use apply_enhancement_preset('telephone_booth', 'high_detail')
```

## Performance Considerations

### Viewport vs Render Levels
- **Viewport levels**: Lower for interactive performance
- **Render levels**: Higher for final quality
- Difference allows smooth editing with high-quality renders

### Adaptive Subdivision
- Subdivides more near edges
- Less in flat areas
- Better performance with similar quality

### When to Skip Enhancement
- Models already high-poly (> 20,000 faces)
- Real-time rendering requirements
- Simple placeholder geometry

## Advanced Usage

### Custom Enhancement Stack
```python
# Manual modifier stack
apply_subdivision_surface("object", viewport_levels=3, render_levels=4)
add_edge_bevel("object", width=0.015, segments=3)
set_shading("object", smooth=True, auto_smooth_angle=25.0)
```

### Conditional Enhancement
```python
# Only enhance if low-poly
stats = analyze_mesh("object")
if stats["stats"]["face_count"] < 2000:
    apply_enhancement_preset("object", "high_detail")
```

### Scene-Wide Processing
```python
# Enhance everything at once
auto_enhance_geometry()  # All mesh objects

# Then materials
auto_enhance_materials()
```

## Visual Quality Impact

### Before Enhancement
- **Faces**: 842 (very low-poly)
- **Appearance**: Blocky, faceted
- **Edges**: Unrealistically sharp
- **Shading**: Flat or incorrect normals

### After Enhancement (high_detail preset)
- **Faces**: 13,472 viewport / ~200,000 render
- **Appearance**: Smooth, professional
- **Edges**: Realistic beveling
- **Shading**: Proper smooth shading with auto-smooth

**Result**: 16-256x quality improvement without model regeneration!

## Object Type Detection

The system automatically suggests presets based on object names:

| Object Name Contains | Suggested Preset |
|---------------------|------------------|
| phone, telephone, booth | high_detail |
| vehicle, car, watch | high_detail |
| robot, machine, gear | mechanical |
| building, wall, door | architectural |
| character, creature | organic |
| (default) | smooth |

## API Reference

### auto_enhance_geometry(object_name=None, analyze_first=True)
Automatically enhance geometry based on intelligent analysis.

**Parameters:**
- `object_name` (str, optional): Specific object to enhance. If None, enhances all mesh objects
- `analyze_first` (bool): Analyze mesh quality to determine optimal settings

**Returns:** Success message with list of enhanced objects and applied modifiers

---

### apply_enhancement_preset(object_name, preset)
Apply a complete enhancement preset.

**Parameters:**
- `object_name` (str): Name of target object
- `preset` (str): Preset name (smooth, high_detail, mechanical, organic, architectural)

**Returns:** Success message with list of applied modifiers

---

### analyze_mesh(object_name)
Analyze mesh quality and get recommendations.

**Parameters:**
- `object_name` (str): Name of object to analyze

**Returns:** Detailed statistics, quality assessment, and suggestions

---

### apply_subdivision_surface(object_name, viewport_levels, render_levels, adaptive)
Apply subdivision surface modifier.

**Parameters:**
- `object_name` (str): Target object
- `viewport_levels` (int): Subdivision levels in viewport (0-6)
- `render_levels` (int): Subdivision levels for rendering (0-6)
- `adaptive` (bool): Use adaptive subdivision

**Returns:** Success/error message

---

### add_edge_bevel(object_name, width, segments)
Add bevel modifier to edges.

**Parameters:**
- `object_name` (str): Target object
- `width` (float): Bevel width
- `segments` (int): Number of segments for smoothness

**Returns:** Success/error message

---

### set_shading(object_name, smooth, auto_smooth_angle)
Set object shading mode.

**Parameters:**
- `object_name` (str): Target object
- `smooth` (bool): Smooth (True) or flat (False) shading
- `auto_smooth_angle` (float): Angle threshold for auto-smooth (0-180°)

**Returns:** Success/error message

---

### list_enhancement_presets()
List all available enhancement presets with descriptions.

**Returns:** Formatted list of presets

---

### suggest_enhancement(object_name)
Get suggested enhancement preset based on object analysis.

**Parameters:**
- `object_name` (str): Object to analyze

**Returns:** Suggested preset with detailed explanation

## Best Practices

1. **Always enhance AI-generated models**: They're typically very low-poly
2. **Analyze first**: Use `analyze_mesh()` to understand what's needed
3. **Use auto_enhance_geometry()**: Let the system choose optimal settings
4. **High detail for hero objects**: Use `high_detail` preset for main subjects
5. **Check viewport performance**: Reduce viewport levels if sluggish
6. **Combine with materials**: Post-processing + materials = dramatic improvement
7. **Screenshot verification**: Always check results visually

## Troubleshooting

### Viewport is slow after enhancement
- Reduce viewport_levels: `apply_subdivision_surface("object", viewport_levels=1)`
- Render levels can stay high for final output

### Edges still look sharp
- Increase bevel width: `add_edge_bevel("object", width=0.02)`
- Lower auto-smooth angle: `set_shading("object", auto_smooth_angle=20.0)`

### Surface looks faceted despite smooth shading
- Apply subdivision: `apply_subdivision_surface("object")`
- Or use auto_enhance with high_detail preset

### Modifiers not having desired effect
- Check modifier order in Blender (subdivision should be early)
- Ensure mesh has enough geometry for bevel to work
- Use analyze_mesh() to check for topology issues

## Technical Details

### Implementation
- **Server**: New tools in `src/blender_mcp/server.py`
- **Post-Processing Module**: Logic in `src/blender_mcp/post_processing.py`
- **Addon Integration**: Handlers in `addon.py`
- **Modifier System**: Uses Blender's native modifier stack

### Modifier Order
Optimal order (automatically applied):
1. Remesh (if organic)
2. Edge Split
3. Subdivision Surface
4. Bevel
5. (Shading applied separately)

### Subdivision Algorithm
- Uses Catmull-Clark subdivision
- Preserves UV maps and vertex colors
- Respects edge creases when enabled

## Examples

### Telephone Booth Enhancement
```python
# Import AI-generated booth
generate_hyper3d_model_via_text("vintage telephone booth")
# ... wait and import ...

# Analyze - likely < 1000 faces
analyze_mesh("booth")  # → "HIGH priority"

# Enhance geometry
auto_enhance_geometry("booth")
# Applies high_detail: subdivision + bevel + smooth shading

# Result: Smooth surfaces, realistic edges
get_viewport_screenshot()
```

### Scene Enhancement
```python
# Multiple objects imported from different sources
# Sketchfab model (5000 faces)
# AI-generated prop (800 faces)
# PolyHaven asset (already high quality)

# Enhance entire scene intelligently
auto_enhance_geometry()
# Each object gets appropriate treatment based on analysis

# Verify
get_viewport_screenshot()
```

## Future Enhancements

Planned improvements:
- Normal map baking from high-to-low poly
- Displacement map generation
- Geometry nodes integration
- Smart retopology for difficult meshes
- Automated UV unwrapping
- LOD (Level of Detail) generation

## Comparison with Material System

Both systems work together:

| System | Purpose | Impact |
|--------|---------|--------|
| Post-Processing | Geometry quality | Smoothness, edge detail |
| Material System | Surface appearance | Color, reflections, textures |

**Best Results**: Use both together
1. Enhance geometry first (better topology for shaders)
2. Then enhance materials (realistic PBR on smooth geometry)
