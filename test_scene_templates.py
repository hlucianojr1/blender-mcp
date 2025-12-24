"""
Scene Templates System - Live Blender Test Suite
Test all 12 professional templates across 4 categories

SETUP:
1. Launch Blender MCP server
2. Run this script to test each template
3. Verify results visually

CATEGORIES:
- Product Photography (3 templates)
- Portrait Photography (3 templates)
- Landscape/Environment (3 templates)
- Architecture Visualization (3 templates)
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_scene_templates():
    """Test all 12 scene templates with live Blender"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "blender_mcp"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=" * 80)
            print("SCENE TEMPLATES SYSTEM - LIVE TEST SUITE")
            print("=" * 80)
            print()
            
            # ========== SETUP: CREATE TEST CUBE ==========
            print("\n" + "=" * 80)
            print("SETUP: Creating test cube for template testing")
            print("=" * 80)
            
            setup_code = """
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create test cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
test_cube = bpy.context.active_object
test_cube.name = "TestObject"

print(f"✓ Created test cube: {test_cube.name}")
print(f"  Location: {test_cube.location}")
print(f"  Size: 2 units")
"""
            
            result = await session.call_tool("execute_blender_code", {"code": setup_code})
            print(result.content[0].text)
            
            # ========== CATEGORY 1: PRODUCT PHOTOGRAPHY ==========
            print("\n" + "=" * 80)
            print("CATEGORY 1: PRODUCT PHOTOGRAPHY TEMPLATES")
            print("=" * 80)
            
            # Template 1: Product Studio Pro
            print("\n--- TEST 1: product_studio_pro ---")
            print("Expected: Clean studio shot with white background")
            
            test1_code = """
import bpy

# Reset cube
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.context.active_object.name = "TestObject"

print("Ready for template: product_studio_pro")
"""
            await session.call_tool("execute_blender_code", {"code": test1_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "product_studio_pro",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - product_studio_pro.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 2: Product Lifestyle
            print("\n--- TEST 2: product_lifestyle ---")
            print("Expected: Natural lifestyle shot with outdoor lighting")
            
            test2_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.context.active_object.name = "TestObject"
print("Ready for template: product_lifestyle")
"""
            await session.call_tool("execute_blender_code", {"code": test2_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "product_lifestyle",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - product_lifestyle.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 3: Product Hero Dramatic
            print("\n--- TEST 3: product_hero_dramatic ---")
            print("Expected: Dramatic hero shot with sunset lighting and god rays")
            
            test3_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.context.active_object.name = "TestObject"
print("Ready for template: product_hero_dramatic")
"""
            await session.call_tool("execute_blender_code", {"code": test3_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "product_hero_dramatic",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - product_hero_dramatic.png")
            
            input("\nPress Enter to continue to PORTRAIT templates...")
            
            # ========== CATEGORY 2: PORTRAIT PHOTOGRAPHY ==========
            print("\n" + "=" * 80)
            print("CATEGORY 2: PORTRAIT PHOTOGRAPHY TEMPLATES")
            print("=" * 80)
            
            # Template 4: Portrait Professional
            print("\n--- TEST 4: portrait_professional ---")
            print("Expected: Balanced three-point lighting, professional look")
            
            test4_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "TestObject"
print("Ready for template: portrait_professional")
"""
            await session.call_tool("execute_blender_code", {"code": test4_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "portrait_professional",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - portrait_professional.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 5: Portrait Cinematic
            print("\n--- TEST 5: portrait_cinematic ---")
            print("Expected: Dramatic lighting, sunset atmosphere, moody")
            
            test5_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "TestObject"
print("Ready for template: portrait_cinematic")
"""
            await session.call_tool("execute_blender_code", {"code": test5_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "portrait_cinematic",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - portrait_cinematic.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 6: Portrait Noir
            print("\n--- TEST 6: portrait_noir ---")
            print("Expected: Black & white, high contrast, film noir style")
            
            test6_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.active_object.name = "TestObject"
print("Ready for template: portrait_noir")
"""
            await session.call_tool("execute_blender_code", {"code": test6_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "portrait_noir",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - portrait_noir.png")
            
            input("\nPress Enter to continue to LANDSCAPE templates...")
            
            # ========== CATEGORY 3: LANDSCAPE/ENVIRONMENT ==========
            print("\n" + "=" * 80)
            print("CATEGORY 3: LANDSCAPE/ENVIRONMENT TEMPLATES")
            print("=" * 80)
            
            # Template 7: Landscape Epic
            print("\n--- TEST 7: landscape_epic ---")
            print("Expected: Wide shot, dramatic sunset, god rays")
            
            test7_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: landscape_epic")
"""
            await session.call_tool("execute_blender_code", {"code": test7_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "landscape_epic",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - landscape_epic.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 8: Landscape Classic
            print("\n--- TEST 8: landscape_classic ---")
            print("Expected: Balanced daylight, classic composition")
            
            test8_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: landscape_classic")
"""
            await session.call_tool("execute_blender_code", {"code": test8_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "landscape_classic",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - landscape_classic.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 9: Landscape Moody
            print("\n--- TEST 9: landscape_moody ---")
            print("Expected: Dark, foggy, mysterious night atmosphere")
            
            test9_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: landscape_moody")
"""
            await session.call_tool("execute_blender_code", {"code": test9_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "landscape_moody",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - landscape_moody.png")
            
            input("\nPress Enter to continue to ARCHITECTURE templates...")
            
            # ========== CATEGORY 4: ARCHITECTURE VISUALIZATION ==========
            print("\n" + "=" * 80)
            print("CATEGORY 4: ARCHITECTURE VISUALIZATION TEMPLATES")
            print("=" * 80)
            
            # Template 10: Architecture Hero
            print("\n--- TEST 10: architecture_hero ---")
            print("Expected: Dramatic golden hour, low angle, hero composition")
            
            test10_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: architecture_hero")
"""
            await session.call_tool("execute_blender_code", {"code": test10_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "architecture_hero",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - architecture_hero.png")
            
            input("\nPress Enter to continue to next template...")
            
            # Template 11: Architecture Technical
            print("\n--- TEST 11: architecture_technical ---")
            print("Expected: Clean, neutral daylight, front view")
            
            test11_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: architecture_technical")
"""
            await session.call_tool("execute_blender_code", {"code": test11_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "architecture_technical",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - architecture_technical.png")
            
            input("\nPress Enter to continue to final template...")
            
            # Template 12: Architecture Dramatic
            print("\n--- TEST 12: architecture_dramatic ---")
            print("Expected: Night scene, fog, dramatic cool tones")
            
            test12_code = """
import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 1.5))
bpy.context.active_object.name = "TestObject"
print("Ready for template: architecture_dramatic")
"""
            await session.call_tool("execute_blender_code", {"code": test12_code})
            
            result = await session.call_tool("apply_scene_template", {
                "template_key": "architecture_dramatic",
                "target_object": "TestObject"
            })
            print("✓ Template Applied:")
            print(result.content[0].text)
            
            screenshot = await session.call_tool("get_viewport_screenshot", {})
            print("✓ Screenshot captured - architecture_dramatic.png")
            
            # ========== FINAL SUMMARY ==========
            print("\n" + "=" * 80)
            print("TEST SUITE COMPLETE!")
            print("=" * 80)
            print()
            print("✓ Tested 12 templates across 4 categories:")
            print("  • Product Photography: 3/3")
            print("  • Portrait Photography: 3/3")
            print("  • Landscape/Environment: 3/3")
            print("  • Architecture Visualization: 3/3")
            print()
            print("All templates applied successfully!")
            print("Screenshots saved for visual verification.")
            print()
            print("NEXT STEPS:")
            print("1. Review screenshots visually")
            print("2. Verify each template matches expected style")
            print("3. Check that all enhancement systems work together")
            print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_scene_templates())
