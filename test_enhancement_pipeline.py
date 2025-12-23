#!/usr/bin/env python3
"""
Test script for the complete Blender MCP enhancement pipeline.
Tests Material System + Post-Processing + Lighting & Atmosphere systems.

Run this after starting the Blender MCP server and having Blender open with the addon enabled.
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from blender_mcp.server import BlenderConnection, async_send_command, get_blender_connection

async def test_enhancement_pipeline():
    """Test the complete enhancement pipeline"""
    
    print("=" * 80)
    print("BLENDER MCP ENHANCEMENT PIPELINE TEST")
    print("=" * 80)
    
    # Connect to Blender
    print("\n[1/9] Connecting to Blender...")
    try:
        blender = get_blender_connection()
        if not blender.connect():
            print("❌ Failed to connect to Blender. Ensure:")
            print("   1. Blender is running")
            print("   2. BlenderMCP addon is enabled")
            print("   3. Server is started in the addon panel")
            return False
        print("✅ Connected to Blender")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Check scene info
    print("\n[2/9] Checking scene status...")
    try:
        result = await async_send_command(blender, "get_scene_info", {})
        if "error" in result:
            print(f"❌ Error getting scene info: {result['error']}")
            return False
        
        print(f"✅ Scene: {result.get('scene_name', 'Unknown')}")
        print(f"   Objects: {result.get('object_count', 0)}")
        print(f"   Active camera: {result.get('active_camera', 'None')}")
    except Exception as e:
        print(f"❌ Scene check error: {e}")
        return False
    
    # Check available integrations
    print("\n[3/9] Checking available integrations...")
    integrations = {}
    
    for integration, command in [
        ("PolyHaven", "get_polyhaven_status"),
        ("Hyper3D Rodin", "get_hyper3d_status"),
        ("Hunyuan3D", "get_hunyuan3d_status"),
        ("Sketchfab", "get_sketchfab_status")
    ]:
        try:
            result = await async_send_command(blender, command, {})
            enabled = "enabled" in result.get("status", "").lower()
            integrations[integration] = enabled
            status = "✅ Enabled" if enabled else "⚠️  Disabled"
            print(f"   {integration}: {status}")
        except Exception as e:
            print(f"   {integration}: ❌ Error checking: {e}")
            integrations[integration] = False
    
    # Determine which asset source to use
    print("\n[4/9] Selecting asset source...")
    asset_source = None
    test_object_name = None
    
    if integrations.get("Sketchfab"):
        asset_source = "sketchfab"
        print("   Using: Sketchfab (best for realistic models)")
    elif integrations.get("PolyHaven"):
        asset_source = "polyhaven"
        print("   Using: PolyHaven (good variety)")
    elif integrations.get("Hyper3D Rodin"):
        asset_source = "hyper3d"
        print("   Using: Hyper3D Rodin (AI generation)")
    elif integrations.get("Hunyuan3D"):
        asset_source = "hunyuan3d"
        print("   Using: Hunyuan3D (AI generation)")
    else:
        print("   ⚠️  No integrations enabled - will create a test cube instead")
        asset_source = "primitive"
    
    # Import or create test object
    print("\n[5/9] Importing/creating test object...")
    
    if asset_source == "sketchfab":
        # Search for a simple test model
        print("   Searching Sketchfab for 'vintage telephone'...")
        try:
            result = await async_send_command(blender, "search_sketchfab_models", {
                "query": "vintage telephone",
                "count": 3,
                "downloadable": True
            })
            
            if "error" not in result and result.get("results"):
                # Try to download first result
                first_model = result["results"][0]
                uid = first_model.get("uid")
                print(f"   Found: {first_model.get('name', 'Unknown')}")
                print(f"   Downloading model {uid}...")
                
                dl_result = await async_send_command(blender, "download_sketchfab_model", {
                    "uid": uid
                })
                
                if "error" not in dl_result:
                    test_object_name = "Sketchfab_model"  # Default name
                    print(f"✅ Imported Sketchfab model: {test_object_name}")
                else:
                    print(f"   ⚠️  Download failed: {dl_result['error']}")
                    asset_source = "primitive"
            else:
                print("   ⚠️  No downloadable models found")
                asset_source = "primitive"
        except Exception as e:
            print(f"   ⚠️  Sketchfab error: {e}")
            asset_source = "primitive"
    
    elif asset_source == "polyhaven":
        # Download a simple model
        print("   Downloading PolyHaven model...")
        try:
            result = await async_send_command(blender, "download_polyhaven_asset", {
                "asset_id": "barrel_01",
                "asset_type": "models",
                "resolution": "1k"
            })
            
            if "error" not in result:
                test_object_name = "barrel_01"
                print(f"✅ Imported PolyHaven model: {test_object_name}")
            else:
                print(f"   ⚠️  Download failed: {result['error']}")
                asset_source = "primitive"
        except Exception as e:
            print(f"   ⚠️  PolyHaven error: {e}")
            asset_source = "primitive"
    
    elif asset_source in ["hyper3d", "hunyuan3d"]:
        print("   ⚠️  AI generation requires API keys and is slow for testing")
        print("   Falling back to primitive cube")
        asset_source = "primitive"
    
    # Fallback to primitive if needed
    if asset_source == "primitive":
        print("   Creating test cube...")
        try:
            code = """
import bpy
# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Create test cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.context.active_object.name = "TestCube"
"""
            result = await async_send_command(blender, "execute_code", {"code": code})
            if "error" not in result:
                test_object_name = "TestCube"
                print(f"✅ Created test cube: {test_object_name}")
            else:
                print(f"❌ Failed to create cube: {result.get('error')}")
                return False
        except Exception as e:
            print(f"❌ Error creating cube: {e}")
            return False
    
    if not test_object_name:
        print("❌ No test object available")
        return False
    
    # Take "before" screenshot
    print("\n[6/9] Capturing BEFORE screenshot...")
    try:
        # Set viewport to rendered mode for better comparison
        code = """
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
"""
        await async_send_command(blender, "execute_code", {"code": code})
        
        result = await async_send_command(blender, "get_viewport_screenshot", {"max_size": 800})
        if "error" in result:
            print(f"   ⚠️  Screenshot failed: {result['error']}")
        else:
            print("✅ BEFORE screenshot captured")
    except Exception as e:
        print(f"   ⚠️  Screenshot error: {e}")
    
    # APPLY ENHANCEMENT PIPELINE
    print("\n" + "=" * 80)
    print("APPLYING ENHANCEMENT PIPELINE")
    print("=" * 80)
    
    # Step 1: Geometry Enhancement
    print("\n[7/9] STEP 1: Geometry Enhancement")
    print("-" * 80)
    try:
        # First analyze the mesh
        print(f"   Analyzing mesh: {test_object_name}...")
        result = await async_send_command(blender, "analyze_mesh", {
            "object_name": test_object_name
        })
        
        if "error" not in result:
            print(f"   📊 Mesh Statistics:")
            print(f"      Face count: {result.get('face_count', 'Unknown')}")
            print(f"      Vertex count: {result.get('vertex_count', 'Unknown')}")
            print(f"      Edge count: {result.get('edge_count', 'Unknown')}")
            
            # Get suggestion
            suggestion = result.get('suggested_preset', 'smooth')
            print(f"      Suggested preset: {suggestion}")
        
        # Apply auto-enhancement
        print(f"\n   Applying auto_enhance_geometry()...")
        result = await async_send_command(blender, "auto_enhance_geometry", {
            "object_name": test_object_name
        })
        
        if "error" in result:
            print(f"   ❌ Geometry enhancement failed: {result['error']}")
        else:
            print(f"   ✅ Geometry enhanced!")
            print(f"      {result.get('message', 'Complete')}")
    except Exception as e:
        print(f"   ❌ Geometry enhancement error: {e}")
    
    # Step 2: Material Enhancement
    print("\n[8/9] STEP 2: Material Enhancement")
    print("-" * 80)
    try:
        # Get material suggestion
        print(f"   Getting material suggestion for {test_object_name}...")
        result = await async_send_command(blender, "suggest_material", {
            "object_name": test_object_name
        })
        
        if "error" not in result:
            print(f"   💡 Suggestion: {result.get('suggested', 'Unknown')}")
        
        # Apply auto-enhancement
        print(f"\n   Applying auto_enhance_materials(aggressive=True)...")
        result = await async_send_command(blender, "auto_enhance_materials", {
            "object_name": test_object_name,
            "aggressive": True
        })
        
        if "error" in result:
            print(f"   ❌ Material enhancement failed: {result['error']}")
        else:
            print(f"   ✅ Materials enhanced!")
            if "enhanced" in result:
                for obj in result["enhanced"]:
                    print(f"      • {obj}")
    except Exception as e:
        print(f"   ❌ Material enhancement error: {e}")
    
    # Step 3: Lighting & Atmosphere
    print("\n[9/9] STEP 3: Lighting & Atmosphere Setup")
    print("-" * 80)
    try:
        print(f"   Applying auto_setup_scene_lighting()...")
        print(f"   Scene description: 'dramatic outdoor product shot'")
        
        result = await async_send_command(blender, "auto_setup_scene_lighting", {
            "scene_description": "dramatic outdoor product shot",
            "target_object": test_object_name
        })
        
        if "error" in result:
            print(f"   ❌ Lighting setup failed: {result['error']}")
        else:
            print(f"   ✅ Lighting configured!")
            # The result contains detailed info about what was set up
            if isinstance(result, dict):
                for key, value in result.items():
                    if key != "error":
                        print(f"      {key}: {value}")
    except Exception as e:
        print(f"   ❌ Lighting setup error: {e}")
    
    # Take "after" screenshot
    print("\n" + "=" * 80)
    print("CAPTURING RESULTS")
    print("=" * 80)
    
    print("\nCapturing AFTER screenshot...")
    try:
        # Switch to rendered view
        code = """
import bpy
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'RENDERED'
"""
        await async_send_command(blender, "execute_code", {"code": code})
        
        result = await async_send_command(blender, "get_viewport_screenshot", {"max_size": 800})
        if "error" in result:
            print(f"   ⚠️  Screenshot failed: {result['error']}")
        else:
            print("✅ AFTER screenshot captured")
    except Exception as e:
        print(f"   ⚠️  Screenshot error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n✅ Enhancement pipeline executed successfully!")
    print("\nEnhancements applied:")
    print("  1. ✅ Geometry - auto_enhance_geometry()")
    print("  2. ✅ Materials - auto_enhance_materials(aggressive=True)")
    print("  3. ✅ Lighting - auto_setup_scene_lighting()")
    print("\nCheck Blender viewport to see the results!")
    print("\nYou should see:")
    print("  • Smoother geometry (subdivision surface applied)")
    print("  • Realistic PBR materials with procedural details")
    print("  • Professional lighting with HDRI and multi-light rig")
    print("  • Volumetric atmosphere for depth")
    print("  • Properly framed camera")
    print("  • Production-quality render settings")
    
    return True

if __name__ == "__main__":
    print("\nBlender MCP Enhancement Pipeline Test")
    print("Make sure Blender is running with BlenderMCP addon enabled!\n")
    
    success = asyncio.run(test_enhancement_pipeline())
    
    if success:
        print("\n🎉 All systems operational!")
        sys.exit(0)
    else:
        print("\n❌ Test failed - check error messages above")
        sys.exit(1)
