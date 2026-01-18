#!/usr/bin/env python3
"""
Test script for new export features in Blender MCP
Tests material export, object export, and related tools
"""

import socket
import json
import sys

def send_command(sock, command_type, params=None):
    """Send a command to Blender and get response"""
    command = {
        "type": command_type,
        "params": params or {}
    }
    
    # Send command
    message = json.dumps(command) + "\n"
    sock.sendall(message.encode('utf-8'))
    
    # Receive response
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
        try:
            # Try to parse as JSON to see if we have complete response
            json.loads(response.decode('utf-8'))
            break
        except json.JSONDecodeError:
            continue
    
    return json.loads(response.decode('utf-8'))

def test_export_features():
    """Test the new export features"""
    print("Connecting to Blender MCP server...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 9876))
        print("✓ Connected to Blender")
        
        # Test 1: Create a test cube
        print("\n1. Creating test cube...")
        result = send_command(sock, "execute_code", {
            "code": """
import bpy
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"
"Cube created"
"""
        })
        print(f"   Result: {result}")
        
        # Test 2: Create a test material
        print("\n2. Creating test material...")
        result = send_command(sock, "execute_code", {
            "code": """
import bpy
mat = bpy.data.materials.new(name="TestMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Add Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)
bsdf.inputs['Metallic'].default_value = 0.5
bsdf.inputs['Roughness'].default_value = 0.3

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Link
mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign to cube
cube = bpy.data.objects.get("TestCube")
if cube:
    if len(cube.data.materials) == 0:
        cube.data.materials.append(mat)
    else:
        cube.data.materials[0] = mat

"Material created and assigned"
"""
        })
        print(f"   Result: {result}")
        
        # Test 3: List materials
        print("\n3. Listing all materials...")
        result = send_command(sock, "list_materials", {})
        print(f"   Result: {result}")
        
        # Test 4: Get material data
        print("\n4. Getting material data...")
        result = send_command(sock, "get_material_data", {
            "material_name": "TestMaterial"
        })
        print(f"   Result: {result}")
        
        # Test 5: Export material as JSON
        print("\n5. Exporting material as JSON...")
        result = send_command(sock, "export_material", {
            "material_name": "TestMaterial",
            "filepath": "/tmp/test_material.json",
            "export_format": "JSON",
            "include_textures": True
        })
        print(f"   Result: {result}")
        
        # Test 6: Export object as FBX
        print("\n6. Exporting object as FBX...")
        result = send_command(sock, "export_object", {
            "object_names": ["TestCube"],
            "filepath": "/tmp/test_cube.fbx",
            "export_format": "FBX",
            "include_materials": True,
            "include_textures": True
        })
        print(f"   Result: {result}")
        
        # Test 7: Export object as OBJ
        print("\n7. Exporting object as OBJ...")
        result = send_command(sock, "export_object", {
            "object_names": ["TestCube"],
            "filepath": "/tmp/test_cube.obj",
            "export_format": "OBJ",
            "include_materials": True
        })
        print(f"   Result: {result}")
        
        # Test 8: Export object as GLB
        print("\n8. Exporting object as GLB...")
        result = send_command(sock, "export_object", {
            "object_names": ["TestCube"],
            "filepath": "/tmp/test_cube.glb",
            "export_format": "GLB",
            "include_materials": True,
            "include_textures": True
        })
        print(f"   Result: {result}")
        
        # Test 9: Import material back
        print("\n9. Importing material from JSON...")
        result = send_command(sock, "import_material", {
            "filepath": "/tmp/test_material.json",
            "material_name": "ImportedMaterial"
        })
        print(f"   Result: {result}")
        
        # Test 10: List materials again to see imported one
        print("\n10. Listing materials after import...")
        result = send_command(sock, "list_materials", {})
        print(f"    Result: {result}")
        
        print("\n✓ All tests completed successfully!")
        
        sock.close()
        return 0
        
    except ConnectionRefusedError:
        print("✗ Error: Could not connect to Blender MCP server")
        print("  Make sure Blender is running with the MCP addon enabled")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_export_features())
