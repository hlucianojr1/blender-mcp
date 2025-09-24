#!/usr/bin/env python3
"""
Create a cube with light blue material in Blender via socket connection.
This script demonstrates how to create 3D objects and materials using the Blender addon.
"""

import socket
import json
import time

def send_blender_command(host, port, command_type, params=None):
    """Send a command to Blender and return the response."""
    command = {
        "type": command_type,
        "params": params or {}
    }
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((host, port))
            
            # Send command
            message = json.dumps(command).encode('utf-8')
            sock.sendall(message)
            
            # Receive response
            response_data = sock.recv(8192)
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get("status") == "error":
                raise Exception(response.get("message", "Unknown error"))
            
            return response.get("result", {})
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_cube_with_light_blue_material():
    """Create a cube with light blue material in Blender."""
    host = "localhost"
    port = 9876
    
    print("🔷 Creating cube with light blue material in Blender...")
    
    # Step 1: Get current scene info
    print("\n📋 Step 1: Getting current scene info...")
    scene_info = send_blender_command(host, port, "get_scene_info")
    if scene_info:
        print(f"   Current scene: {scene_info.get('name')}")
        print(f"   Objects: {len(scene_info.get('objects', []))}")
    
    # Step 2: Create the cube and light blue material using Python code
    print("\n🔵 Step 2: Creating cube with light blue material...")
    
    create_cube_code = """
import bpy
import bmesh

# Clear existing mesh objects (optional - you can remove this if you want to keep existing objects)
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False, confirm=False)

# Create a new cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "LightBlueCube"

# Create a new material
material = bpy.data.materials.new(name="LightBlueMaterial")
material.use_nodes = True

# Get the material nodes
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear existing nodes
nodes.clear()

# Add Principled BSDF shader
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)

# Add Material Output
material_output = nodes.new(type='ShaderNodeOutputMaterial')
material_output.location = (400, 0)

# Link BSDF to Material Output
links.new(bsdf.outputs[0], material_output.inputs[0])

# Set the base color to light blue (RGB: 0.5, 0.7, 1.0)
bsdf.inputs['Base Color'].default_value = (0.5, 0.7, 1.0, 1.0)  # Light blue color

# Make it slightly metallic and adjust roughness for a nice appearance
bsdf.inputs['Metallic'].default_value = 0.2  # Metallic
bsdf.inputs['Roughness'].default_value = 0.3  # Roughness

# Assign material to cube
if cube.data.materials:
    cube.data.materials[0] = material
else:
    cube.data.materials.append(material)

# Switch to Material shading mode to see the material
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

print("Created light blue cube successfully!")
"""
    
    result = send_blender_command(host, port, "execute_code", {"code": create_cube_code})
    if result:
        print("   ✅ Cube created successfully!")
    else:
        print("   ❌ Failed to create cube")
        return
    
    # Step 3: Get updated scene info to confirm creation
    print("\n📋 Step 3: Verifying cube creation...")
    scene_info = send_blender_command(host, port, "get_scene_info")
    if scene_info:
        objects = scene_info.get('objects', [])
        cube_found = any(obj.get('name') == 'LightBlueCube' for obj in objects)
        if cube_found:
            print("   ✅ Light blue cube found in scene!")
            for obj in objects:
                if obj.get('name') == 'LightBlueCube':
                    print(f"   📦 Cube location: {obj.get('location')}")
                    print(f"   📦 Cube type: {obj.get('type')}")
        else:
            print("   ⚠️  Cube not found by name, but operation may have succeeded")
    
    # Step 4: Get viewport screenshot to see the result
    print("\n📸 Step 4: Taking screenshot of the result...")
    try:
        import tempfile
        import os
        
        # Create temp file path
        temp_dir = tempfile.gettempdir()
        screenshot_path = os.path.join(temp_dir, "blender_cube_screenshot.png")
        
        screenshot_result = send_blender_command(host, port, "get_viewport_screenshot", {
            "max_size": 800,
            "filepath": screenshot_path,
            "format": "png"
        })
        
        if screenshot_result and os.path.exists(screenshot_path):
            print(f"   📸 Screenshot saved to: {screenshot_path}")
            print("   🖼️  Open the file to see your light blue cube!")
        else:
            print("   ⚠️  Screenshot not available")
    except Exception as e:
        print(f"   ⚠️  Screenshot failed: {e}")
    
    print("\n🎉 Cube creation complete!")
    print("💡 Tips:")
    print("   - In Blender, press '5' for orthographic view")
    print("   - Press '7' for top view")
    print("   - Press 'Z' and select 'Material Preview' to see the material")
    print("   - Use mouse wheel to zoom in/out")

def main():
    """Main function."""
    print("🚀 Blender Cube Creator")
    print("=" * 50)
    
    try:
        create_cube_with_light_blue_material()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Blender is running")
        print("   2. Ensure BlenderMCP addon is enabled") 
        print("   3. Click 'Connect to Claude' in Blender")
        print("   4. Check that port 9876 is not blocked")

if __name__ == "__main__":
    main()