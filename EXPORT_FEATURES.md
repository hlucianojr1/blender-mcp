# Export Features Documentation

This document describes the new export features added to Blender MCP server.

## New Tools Added

### 1. `export_object` - Export Objects/Meshes

Export one or more objects to various file formats.

**Parameters:**
- `filepath` (string, required): Output file path (extension should match format)
- `object_names` (list[string], optional): List of object names to export (None = export all selected objects)
- `export_format` (string, default: "FBX"): Export format
  - `FBX` - Autodesk FBX (widely supported, good for game engines)
  - `OBJ` - Wavefront OBJ (simple, widely compatible)
  - `GLB` - Binary glTF (modern, web-friendly, single file)
  - `GLTF` - glTF separate files (modern, web-friendly)
  - `STL` - Stereolithography (3D printing)
  - `PLY` - Polygon File Format (point clouds, 3D scanning)
  - `DAE` - Collada (game engines, 3D apps)
- `include_materials` (boolean, default: true): Include materials in export
- `include_textures` (boolean, default: true): Include textures in export (if format supports it)
- `apply_modifiers` (boolean, default: false): Apply modifiers before export

**Example:**
```python
# Export multiple objects as FBX
export_object(
    object_names=["Cube", "Sphere", "Cylinder"],
    filepath="/path/to/scene.fbx",
    export_format="FBX",
    include_materials=True,
    include_textures=True
)

# Export single object as GLB for web
export_object(
    object_names=["MyModel"],
    filepath="/path/to/model.glb",
    export_format="GLB"
)

# Export for 3D printing (no materials needed)
export_object(
    object_names=["PrintModel"],
    filepath="/path/to/model.stl",
    export_format="STL"
)
```

---

### 2. `export_material` - Export Material to File

Export a material for reuse or sharing.

**Parameters:**
- `material_name` (string, required): Name of the material to export
- `filepath` (string, required): Output file path
- `export_format` (string, default: "JSON"): Export format
  - `JSON` - Human-readable material settings (useful for documentation and recreation)
  - `BLEND` - Blender library file with the material (can be appended/linked in other projects)
- `include_textures` (boolean, default: true): Include texture file paths in export
- `pack_textures` (boolean, default: false): Copy textures to same directory as export file (JSON format only)

**Example:**
```python
# Export as JSON (readable, portable)
export_material(
    material_name="MyAwesomeMaterial",
    filepath="/path/to/material.json",
    export_format="JSON",
    include_textures=True,
    pack_textures=True  # Copy texture files too
)

# Export as Blender library file
export_material(
    material_name="MyAwesomeMaterial",
    filepath="/path/to/material.blend",
    export_format="BLEND"
)
```

**JSON Format Example:**
```json
{
  "name": "MyMaterial",
  "use_nodes": true,
  "diffuse_color": [0.8, 0.2, 0.1, 1.0],
  "metallic": 0.5,
  "roughness": 0.3,
  "nodes": [
    {
      "name": "Principled BSDF",
      "type": "ShaderNodeBsdfPrincipled",
      "location": [0, 0],
      "inputs": {
        "Base Color": [0.8, 0.2, 0.1, 1.0],
        "Metallic": 0.5,
        "Roughness": 0.3
      }
    }
  ],
  "links": [...]
}
```

---

### 3. `import_material` - Import Material from File

Import a material from a JSON or BLEND file.

**Parameters:**
- `filepath` (string, required): Path to material file (JSON or BLEND)
- `material_name` (string, optional): Name for the imported material (None = use original name)

**Example:**
```python
# Import from JSON
import_material(
    filepath="/path/to/material.json",
    material_name="ImportedMaterial"
)

# Import from BLEND library
import_material(
    filepath="/path/to/materials.blend",
    material_name="SpecificMaterial"  # Optional: specify which material
)
```

---

### 4. `get_material_data` - Get Material Details

Get detailed material data including all node settings and connections.

**Parameters:**
- `material_name` (string, required): Name of the material

**Returns:**
JSON data with material properties, nodes, and connections.

**Example:**
```python
data = get_material_data(material_name="MyMaterial")
# Returns:
# {
#   "name": "MyMaterial",
#   "use_nodes": true,
#   "diffuse_color": [0.8, 0.8, 0.8, 1.0],
#   "metallic": 0.0,
#   "roughness": 0.5,
#   "node_count": 2,
#   "link_count": 1,
#   "nodes": [
#     {"name": "Principled BSDF", "type": "ShaderNodeBsdfPrincipled"},
#     {"name": "Material Output", "type": "ShaderNodeOutputMaterial"}
#   ]
# }
```

---

### 5. `list_materials` - List Materials

List all materials in the scene or on a specific object.

**Parameters:**
- `object_name` (string, optional): Name of object to list materials from (None = list all scene materials)

**Example:**
```python
# List all materials in scene
all_materials = list_materials()
# Returns: {"materials": ["Material.001", "MyMaterial", ...], "count": 5}

# List materials on specific object
object_materials = list_materials(object_name="Cube")
# Returns: {"materials": ["Material.001"], "count": 1}
```

---

## Use Cases

### Workflow 1: Share Materials Between Projects
```python
# In Project A: Export your custom material
export_material(
    material_name="CustomWood",
    filepath="/shared/materials/custom_wood.json",
    pack_textures=True
)

# In Project B: Import the material
import_material(
    filepath="/shared/materials/custom_wood.json"
)
```

### Workflow 2: Export Model for Game Engine
```python
# Export character with animations and materials
export_object(
    object_names=["CharacterMesh", "Weapon", "Armor"],
    filepath="/game/assets/character.fbx",
    export_format="FBX",
    include_materials=True,
    include_textures=True,
    apply_modifiers=True
)
```

### Workflow 3: Export for Web (Three.js, Babylon.js)
```python
# Export as GLB for web
export_object(
    object_names=["Building"],
    filepath="/web/assets/building.glb",
    export_format="GLB",
    include_materials=True,
    include_textures=True
)
```

### Workflow 4: Material Library Management
```python
# List all materials
materials = list_materials()

# Export each material
for mat_name in materials["materials"]:
    export_material(
        material_name=mat_name,
        filepath=f"/library/{mat_name}.json",
        pack_textures=True
    )
```

### Workflow 5: Automated Export Pipeline
```python
# Get scene info
scene = get_scene_info()

# Export all mesh objects
for obj in scene["objects"]:
    if obj["type"] == "MESH":
        export_object(
            object_names=[obj["name"]],
            filepath=f"/exports/{obj['name']}.glb",
            export_format="GLB"
        )
```

---

## Testing

Run the test script to verify all features work:

```bash
# Make sure Blender is running with MCP addon enabled
python test_export_features.py
```

The test script will:
1. Create a test cube
2. Create a test material with nodes
3. List materials
4. Get material data
5. Export material as JSON
6. Export object as FBX, OBJ, and GLB
7. Import material back
8. Verify the import

---

## Notes

- All export paths should be absolute paths
- Supported formats vary by Blender version (tested with Blender 3.0+)
- Material export to JSON is custom format (not a Blender standard)
- Material export to BLEND creates a library file that can be linked/appended in other Blender projects
- When exporting materials with textures, ensure texture paths are accessible
- Use `pack_textures=True` to copy texture files alongside the material JSON for portability
