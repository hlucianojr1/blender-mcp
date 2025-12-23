# Manual Test Guide - Enhancement Pipeline

This guide walks you through manually testing all three enhancement systems together.

## Prerequisites

1. ✅ Blender is running (3.0+)
2. ✅ BlenderMCP addon is installed and enabled
3. ✅ BlenderMCP server is started in the addon panel
4. ✅ Claude Desktop is connected via MCP

## Test Procedure

### Step 1: Prepare Blender Scene

In Blender:
1. Clear the default scene: Select all (`A`), Delete (`X`)
2. Keep the addon panel open
3. Switch viewport shading to "Material Preview" (`Z` → Material Preview)

### Step 2: Import a Test Object

Choose ONE of these options:

**Option A: Use Sketchfab (Best for realistic test)**
```
Ask Claude:
"Search Sketchfab for 'vintage telephone' models and download the first downloadable one"
```

**Option B: Use PolyHaven**
```
Ask Claude:
"Download the barrel_01 model from PolyHaven"
```

**Option C: Create a simple test object**
```
Ask Claude:
"Create a test cube named TestCube at location (0, 0, 1) with size 2"
```

### Step 3: Capture BEFORE State

```
Ask Claude:
"Take a screenshot of the current viewport"
```

**Expected**: Basic object with flat lighting, simple/no materials

### Step 4: Apply Complete Enhancement Pipeline

Now apply all three enhancement systems with a single prompt:

```
Ask Claude:
"Apply the complete enhancement pipeline to [ObjectName]:
1. Run auto_enhance_geometry() 
2. Run auto_enhance_materials() with aggressive=True
3. Run auto_setup_scene_lighting() with scene description 'dramatic outdoor product shot' targeting [ObjectName]
4. Take a screenshot"
```

Replace `[ObjectName]` with your object's name (e.g., "TestCube", "Sketchfab_model", "barrel_01")

### Step 5: Verify Each System

#### Geometry Enhancement (Post-Processing)
```
Ask Claude:
"Analyze the mesh for [ObjectName] and show me what modifiers were applied"
```

**Expected output:**
- Subdivision Surface modifier (level 2-3)
- Possibly edge bevel modifier
- Higher apparent polygon count
- Smoother silhouette

**Visual check in Blender:**
- Object should look smoother
- Check Modifiers panel - should see "Subdivision Surface"
- Viewport should show increased geometry detail

#### Material Enhancement
```
Ask Claude:
"Get object info for [ObjectName] and tell me what materials were applied"
```

**Expected output:**
- PBR material applied (e.g., weathered_metal, brushed_metal, etc.)
- Material with Principled BSDF nodes
- Possibly procedural texture nodes (noise, scratches, etc.)

**Visual check in Blender:**
- Open Shading workspace
- Select object
- Should see complex node tree in Shader Editor
- Material should have realistic properties (metallic, roughness, etc.)

#### Lighting & Atmosphere
```
Ask Claude:
"List all lights in the scene and describe the camera setup"
```

**Expected output:**
- 3-4 lights created (Key_Light, Fill_Light, etc.)
- Camera positioned and aimed at object
- HDRI environment set up
- Volumetric atmosphere configured

**Visual check in Blender:**
- Switch to "Rendered" viewport shading (`Z` → Rendered)
- Should see professional lighting with multiple light sources
- Possible fog/atmosphere visible
- Camera view (`Numpad 0`) should frame object nicely

### Step 6: Compare BEFORE vs AFTER

View both screenshots side by side:

**BEFORE:**
- ❌ Low polygon count (blocky/faceted)
- ❌ Flat single-color material
- ❌ Basic default lighting
- ❌ No atmosphere
- ❌ Generic camera angle

**AFTER:**
- ✅ Smooth, high-detail geometry
- ✅ Realistic PBR material with surface details
- ✅ Professional multi-light setup
- ✅ HDRI environment lighting
- ✅ Volumetric atmosphere (fog/haze)
- ✅ Properly framed camera
- ✅ Production render settings

### Step 7: Test Individual System Controls

Test that you can adjust each system independently:

**Geometry:**
```
Ask Claude:
"Apply the high_detail enhancement preset to [ObjectName]"
```

**Materials:**
```
Ask Claude:
"Apply the chrome material to [ObjectName]"
```

**Lighting:**
```
Ask Claude:
"Change the HDRI to sunset preset with rotation 90 degrees"
```

**Camera:**
```
Ask Claude:
"Setup a portrait camera with telephoto lens targeting [ObjectName]"
```

**Render:**
```
Ask Claude:
"Configure render settings to production quality"
```

### Step 8: Test Workflow Integration

Test the complete workflow with a fresh object:

```
Ask Claude:
"Create a new test sphere named TestSphere, then immediately apply:
1. High detail geometry enhancement
2. Brushed metal material  
3. Studio lighting setup
Then take a screenshot"
```

This tests that the systems work in sequence without manual intervention.

## Success Criteria

✅ **Geometry System:**
- Subdivision modifiers apply correctly
- Mesh analysis works
- Different presets produce different results

✅ **Material System:**
- Materials apply with proper PBR properties
- Procedural textures visible in shader nodes
- Auto-enhancement selects appropriate materials

✅ **Lighting System:**
- HDRI world setup works
- Multiple lights created and positioned
- Camera frames object correctly
- Render settings configured

✅ **Integration:**
- All three systems can be applied in sequence
- No conflicts between systems
- Complete pipeline produces professional results

## Troubleshooting

### "Object not found" errors
- Verify object name exactly (case-sensitive)
- List objects: "Show me all objects in the scene"

### Geometry looks the same after enhancement
- Check Modifiers panel in Blender
- Try: "Show modifiers on [ObjectName]"
- May need higher subdivision: "Apply subdivision with 3 levels"

### Materials look flat
- Ensure viewport is in Material Preview or Rendered mode
- Check: "List all materials in the scene"
- Try aggressive mode: "Apply materials with aggressive=True"

### Lighting not visible
- Switch to Rendered viewport shading
- Check: "List all lights in the scene"
- Increase HDRI strength: "Set HDRI strength to 1.5"

### Fog/atmosphere not visible
- Must use Rendered viewport shading
- Check render engine: "What render engine is active?"
- Increase density: "Add fog with density 0.1"

## Performance Notes

- **Draft quality** (Eevee, fast): Use for testing and iteration
- **Preview quality** (Cycles, medium): Use for quality checks
- **Production quality** (Cycles, slow): Use for final output only

Switch quality: "Configure render settings to [draft/preview/production/final]"

## Next Steps After Testing

If all tests pass:
1. Document any issues found
2. Test with different object types (organic vs mechanical)
3. Test with AI-generated models (Hyper3D/Hunyuan3D)
4. Test different lighting scenarios (night, interior, etc.)
5. Create example presets for common use cases

## Example Complete Test Session

Here's a full test you can copy/paste to Claude:

```
1. "Create a test cube named TestCube at (0,0,1) with size 2"

2. "Take a screenshot and save it as 'before'"

3. "Analyze the mesh for TestCube"

4. "Apply complete enhancement: auto_enhance_geometry on TestCube, auto_enhance_materials with aggressive=True on TestCube, and auto_setup_scene_lighting for 'dramatic outdoor product' targeting TestCube"

5. "Take a screenshot and save it as 'after'"

6. "List all modifiers on TestCube"

7. "Get object info for TestCube and show materials"

8. "List all lights in the scene"

9. "Show camera settings"
```

Compare the before/after screenshots to verify the transformation!
