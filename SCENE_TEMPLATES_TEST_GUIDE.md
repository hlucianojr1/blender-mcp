# Scene Templates Test Guide

## Quick Manual Test (Recommended)

The easiest way to test all templates is manually through the MCP interface:

### Setup
1. Start Blender in background:
   ```bash
   /Applications/Blender.app/Contents/MacOS/Blender --background --python addon.py &
   sleep 8
   ```

2. Connect via MCP and test each template

### Test Each Category

#### PRODUCT TEMPLATES (3)

**Test 1: product_studio_pro**
```python
# Create test object
bpy.ops.mesh.primitive_cube_add(size=2)
bpy.context.active_object.name = "Product"

# Apply template
apply_scene_template("product_studio_pro", "Product")

# Expected: Clean white studio, balanced lighting, professional
```

**Test 2: product_lifestyle**
```python
# Create test object
bpy.ops.mesh.primitive_cube_add(size=2)
bpy.context.active_object.name = "Product"

# Apply template
apply_scene_template("product_lifestyle", "Product")

# Expected: Outdoor daylight, haze atmosphere, warm tones
```

**Test 3: product_hero_dramatic**
```python
# Create test object
bpy.ops.mesh.primitive_cube_add(size=2)
bpy.context.active_object.name = "Product"

# Apply template
apply_scene_template("product_hero_dramatic", "Product")

# Expected: Sunset, god rays, dramatic lighting, high contrast
```

---

#### PORTRAIT TEMPLATES (3)

**Test 4: portrait_professional**
```python
# Create test object (sphere for portrait)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "Portrait"

# Apply template
apply_scene_template("portrait_professional", "Portrait")

# Expected: Three-point lighting, balanced, professional
```

**Test 5: portrait_cinematic**
```python
# Create test object
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "Portrait"

# Apply template
apply_scene_template("portrait_cinematic", "Portrait")

# Expected: Dramatic sunset, fog, moody high contrast
```

**Test 6: portrait_noir**
```python
# Create test object
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "Portrait"

# Apply template
apply_scene_template("portrait_noir", "Portrait")

# Expected: Black & white, high contrast, dramatic side lighting
```

---

#### LANDSCAPE TEMPLATES (3)

**Test 7: landscape_epic**
```python
# Create test scene
bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "Landscape"

# Apply template
apply_scene_template("landscape_epic", "Landscape")

# Expected: Wide shot, sunset, god rays, dramatic
```

**Test 8: landscape_classic**
```python
# Create test scene
bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "Landscape"

# Apply template
apply_scene_template("landscape_classic", "Landscape")

# Expected: Balanced daylight, haze, classic composition
```

**Test 9: landscape_moody**
```python
# Create test scene
bpy.ops.mesh.primitive_plane_add(size=10)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "Landscape"

# Apply template
apply_scene_template("landscape_moody", "Landscape")

# Expected: Dark night, heavy fog, low exposure, mysterious
```

---

#### ARCHITECTURE TEMPLATES (3)

**Test 10: architecture_hero**
```python
# Create test building
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "Building"

# Apply template
apply_scene_template("architecture_hero", "Building")

# Expected: Sunset, haze, low angle, golden hour
```

**Test 11: architecture_technical**
```python
# Create test building
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "Building"

# Apply template
apply_scene_template("architecture_technical", "Building")

# Expected: Clean daylight, front view, neutral colors
```

**Test 12: architecture_dramatic**
```python
# Create test building
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "Building"

# Apply template
apply_scene_template("architecture_dramatic", "Building")

# Expected: Night, fog, cool tones, low angle, dramatic
```

---

## Verification Checklist

For each template, verify:

### ✓ Geometry Enhancement
- [ ] Subdivision applied (check smooth surface)
- [ ] Beveled edges (check rounded corners)
- [ ] Smooth shading enabled

### ✓ Materials
- [ ] Materials auto-enhanced
- [ ] Appropriate shininess/roughness
- [ ] PBR materials visible

### ✓ Lighting
- [ ] HDRI environment visible
- [ ] Lighting rig lights positioned
- [ ] Atmosphere effects (fog/haze/god rays) visible

### ✓ Composition
- [ ] Camera positioned correctly
- [ ] Object framed according to shot type
- [ ] Composition rule applied

### ✓ Color Grading
- [ ] Tone mapping applied
- [ ] Exposure adjusted
- [ ] Color look matches template style

### ✓ Render Settings
- [ ] Appropriate sample count
- [ ] Cycles engine enabled
- [ ] Quality settings correct

---

## Expected Visual Results

### Product Templates
- **studio_pro**: Clean, bright, professional white background
- **lifestyle**: Natural outdoor look, warm tones, environmental
- **hero_dramatic**: Bold sunset, dramatic shadows, high impact

### Portrait Templates
- **professional**: Balanced, clean, corporate look
- **cinematic**: Moody, dramatic, filmic atmosphere
- **noir**: Black & white, high contrast, classic film

### Landscape Templates
- **epic**: Wide dramatic vista, sunset sky, epic scale
- **classic**: Balanced daylight, natural, traditional
- **moody**: Dark, foggy, mysterious, low light

### Architecture Templates
- **hero**: Golden hour, dramatic low angle, showcase
- **technical**: Clean, neutral, front view, documentation
- **dramatic**: Night scene, fog, cool tones, atmosphere

---

## Automated Test Script

Run the full automated test:

```bash
python test_scene_templates.py
```

This will:
1. Test all 12 templates sequentially
2. Capture screenshots for each
3. Generate test report
4. Pause between tests for visual verification

---

## Quick One-Template Test

To test just one template quickly:

```python
import bpy

# Setup
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=2)
bpy.context.active_object.name = "Test"

# Apply template (via MCP)
# apply_scene_template("product_studio_pro", "Test")

# Capture result
# get_viewport_screenshot()
```

---

## Success Criteria

All 12 templates should:
1. Apply without errors
2. Produce visually distinct results
3. Match their described style
4. Combine all 6 enhancement systems
5. Complete in 2-5 seconds each

---

## Troubleshooting

**Template fails to apply:**
- Check object exists
- Verify object name is correct
- Ensure scene is not empty

**Visual results don't match expected:**
- Verify Blender is in Material Preview or Rendered view
- Check viewport shading settings
- Ensure HDRI is visible in viewport

**Performance issues:**
- Reduce render samples for testing
- Use preview quality initially
- Test one category at a time
