# blender_mcp_server.py
from mcp.server.fastmcp import FastMCP, Context, Image
import socket
import json
import asyncio
import logging
import tempfile
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List
import os
from pathlib import Path
import base64
from urllib.parse import urlparse

# Import telemetry
from .telemetry import record_startup, get_telemetry
from .telemetry_decorator import telemetry_tool
# Import material system
from .materials import MATERIAL_PRESETS, get_suggested_material, list_available_materials, get_material_info
# Import post-processing system
from .post_processing import (
    ENHANCEMENT_PRESETS, 
    get_suggested_preset, 
    list_available_presets, 
    get_preset_info,
    calculate_optimal_subdivision_levels,
    analyze_mesh_quality
)
# Import lighting system
from .lighting import (
    HDRI_PRESETS,
    LIGHTING_RIGS,
    ATMOSPHERE_PRESETS,
    CAMERA_PRESETS,
    RENDER_PRESETS,
    suggest_scene_lighting,
    calculate_camera_position
)
# Import composition system
from .composition import (
    COMPOSITION_RULES,
    SHOT_TYPES,
    FRAMING_PRESETS,
    COMPOSITION_PRESETS,
    calculate_composition_score,
    suggest_shot_type,
    suggest_composition_rule,
    get_framing_guide_data,
    calculate_camera_position as calc_composition_camera
)
# Import scene templates system
from .scene_templates import (
    SCENE_TEMPLATES,
    get_template_categories,
    get_templates_by_category,
    suggest_template,
    get_template_info,
    customize_template
)
# Import color grading system
from .color_grading import (
    LUT_PRESETS,
    TONE_MAPPING,
    COLOR_EFFECTS,
    COLOR_GRADE_PRESETS,
    suggest_color_grade,
    get_color_temperature_offset,
    generate_compositor_nodes
)
# Import animation system
from .animation import (
    ANIMATION_PRESETS,
    ANIMATION_CATEGORIES,
    BONE_MAPPINGS,
    INTERPOLATION_TYPES,
    EASING_TYPES,
    get_preset_info as get_animation_preset_info,
    list_presets_by_category,
    get_bone_name,
    get_all_bone_mappings,
    suggest_animation,
    get_keyframe_data_for_blender,
    validate_armature_bones,
    get_animation_duration
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlenderMCPServer")

# Default configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876

@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    
    def connect(self) -> bool:
        """Connect to the Blender addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(180.0)  # Match the addon's timeout
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(180.0)  # Match the addon's timeout
            
            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Blender")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Blender response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Blender lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Blender: {str(e)}")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Blender: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    # We don't need to create a connection here since we're using the global connection
    # for resources and tools

    try:
        # Just log that we're starting up
        logger.info("BlenderMCP server starting up")

        # Record startup event for telemetry
        try:
            record_startup()
        except Exception as e:
            logger.debug(f"Failed to record startup telemetry: {e}")

        # Try to connect to Blender on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            blender = get_blender_connection()
            logger.info("Successfully connected to Blender on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Blender on startup: {str(e)}")
            logger.warning("Make sure the Blender addon is running before using Blender resources or tools")

        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
        global _blender_connection
        if _blender_connection:
            logger.info("Disconnecting from Blender on shutdown")
            _blender_connection.disconnect()
            _blender_connection = None
        logger.info("BlenderMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "BlenderMCP",
    lifespan=server_lifespan
)

# Resource endpoints

# Global connection for resources (since resources can't access context)
_blender_connection = None
_polyhaven_enabled = False  # Add this global variable

def get_blender_connection():
    """Get or create a persistent Blender connection"""
    global _blender_connection, _polyhaven_enabled  # Add _polyhaven_enabled to globals
    
    # If we have an existing connection, check if it's still valid
    if _blender_connection is not None:
        try:
            # First check if PolyHaven is enabled by sending a ping command
            result = _blender_connection.send_command("get_polyhaven_status")
            # Store the PolyHaven status globally
            _polyhaven_enabled = result.get("enabled", False)
            return _blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _blender_connection.disconnect()
            except:
                pass
            _blender_connection = None
    
    # Create a new connection if needed
    if _blender_connection is None:
        host = os.getenv("BLENDER_HOST", DEFAULT_HOST)
        port = int(os.getenv("BLENDER_PORT", DEFAULT_PORT))
        _blender_connection = BlenderConnection(host=host, port=port)
        if not _blender_connection.connect():
            logger.error("Failed to connect to Blender")
            _blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        logger.info("Created new persistent connection to Blender")
    
    return _blender_connection


@telemetry_tool("get_scene_info")
@mcp.tool()
def get_scene_info(ctx: Context) -> str:
    """Get detailed information about the current Blender scene"""
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_scene_info")

        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scene info from Blender: {str(e)}")
        return f"Error getting scene info: {str(e)}"

@telemetry_tool("get_object_info")
@mcp.tool()
def get_object_info(ctx: Context, object_name: str) -> str:
    """
    Get detailed information about a specific object in the Blender scene.
    
    Parameters:
    - object_name: The name of the object to get information about
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_object_info", {"name": object_name})
        
        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting object info from Blender: {str(e)}")
        return f"Error getting object info: {str(e)}"

@telemetry_tool("get_viewport_screenshot")
@mcp.tool()
def get_viewport_screenshot(ctx: Context, max_size: int = 800) -> Image:
    """
    Capture a screenshot of the current Blender 3D viewport.
    
    Parameters:
    - max_size: Maximum size in pixels for the largest dimension (default: 800)
    
    Returns the screenshot as an Image.
    """
    try:
        blender = get_blender_connection()
        
        # Create temp file path
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")
        
        result = blender.send_command("get_viewport_screenshot", {
            "max_size": max_size,
            "filepath": temp_path,
            "format": "png"
        })
        
        if "error" in result:
            raise Exception(result["error"])
        
        if not os.path.exists(temp_path):
            raise Exception("Screenshot file was not created")
        
        # Read the file
        with open(temp_path, 'rb') as f:
            image_bytes = f.read()
        
        # Delete the temp file
        os.remove(temp_path)
        
        return Image(data=image_bytes, format="png")
        
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        raise Exception(f"Screenshot failed: {str(e)}")


@telemetry_tool("execute_blender_code")
@mcp.tool()
def execute_blender_code(ctx: Context, code: str) -> str:
    """
    Execute arbitrary Python code in Blender. Make sure to do it step-by-step by breaking it into smaller chunks.
    
    ⚠️ SECURITY WARNING: This executes arbitrary code with full Blender Python API access.
    Only use with trusted code. Malicious code can access files, modify data, or compromise security.
    This feature should be disabled in multi-user or untrusted environments.

    Parameters:
    - code: The Python code to execute
    """
    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command("execute_code", {"code": code})
        return f"Code executed successfully: {result.get('result', '')}"
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Error executing code: {str(e)}"

@telemetry_tool("apply_material_preset")
@mcp.tool()
def apply_material_preset(
    ctx: Context,
    object_name: str,
    material_preset: str,
    color: list[float] = None
) -> str:
    """
    Apply a PBR material preset to an object in Blender.
    
    Parameters:
    - object_name: Name of the object to apply material to
    - material_preset: Name of the material preset to apply (use list_material_presets to see available options)
    - color: Optional RGBA color override [R, G, B, A] where values are 0.0-1.0
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        
        # Validate material preset exists
        if material_preset not in MATERIAL_PRESETS:
            available = ", ".join(list_available_materials())
            return f"Error: Material preset '{material_preset}' not found. Available presets: {available}"
        
        # Get material properties
        material_props = MATERIAL_PRESETS[material_preset].copy()
        
        # Override color if provided
        if color:
            if len(color) not in [3, 4]:
                return "Error: Color must be [R, G, B] or [R, G, B, A] with values 0.0-1.0"
            if len(color) == 3:
                color.append(1.0)  # Add alpha
            material_props["base_color"] = tuple(color)
        
        result = blender.send_command("apply_material_preset", {
            "object_name": object_name,
            "material_props": material_props,
            "preset_name": material_preset
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            return f"Successfully applied '{material_preset}' material to {object_name}"
        else:
            return f"Failed to apply material: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying material preset: {str(e)}")
        return f"Error applying material preset: {str(e)}"

@telemetry_tool("auto_enhance_materials")
@mcp.tool()
def auto_enhance_materials(
    ctx: Context,
    object_name: str = None,
    aggressive: bool = False
) -> str:
    """
    Automatically enhance materials on objects based on their names and context.
    If no object specified, enhances all objects in the scene.
    
    Parameters:
    - object_name: Optional name of specific object to enhance. If None, enhances all objects
    - aggressive: If True, applies more dramatic enhancements (higher detail, more procedural effects)
    
    Returns a message with details of enhancements applied.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("auto_enhance_materials", {
            "object_name": object_name,
            "aggressive": aggressive
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            enhanced_count = result.get("enhanced_count", 0)
            details = result.get("details", [])
            
            output = f"Successfully enhanced {enhanced_count} object(s):\n"
            for detail in details:
                output += f"- {detail}\n"
            
            return output
        else:
            return f"Failed to enhance materials: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error auto-enhancing materials: {str(e)}")
        return f"Error auto-enhancing materials: {str(e)}"

@telemetry_tool("list_material_presets")
@mcp.tool()
def list_material_presets(ctx: Context, category: str = None) -> str:
    """
    List all available material presets.
    
    Parameters:
    - category: Optional filter by category (metals, glass, paint, plastic, wood, fabric, stone, special)
    
    Returns a formatted list of available material presets.
    """
    try:
        materials = list_available_materials()
        
        # Categorize materials
        categories = {
            "metals": ["weathered_metal", "brushed_metal", "rusted_metal", "chrome"],
            "glass": ["clear_glass", "frosted_glass", "tinted_glass"],
            "paint": ["glossy_paint", "matte_paint", "weathered_paint", "car_paint"],
            "plastic": ["glossy_plastic", "rubber"],
            "wood": ["polished_wood", "rough_wood"],
            "fabric": ["fabric"],
            "stone": ["concrete", "stone"],
            "special": ["emission", "glow"]
        }
        
        output = "Available Material Presets:\n\n"
        
        if category:
            cat_lower = category.lower()
            if cat_lower in categories:
                output += f"{category.upper()}:\n"
                for mat in categories[cat_lower]:
                    info = get_material_info(mat)
                    output += f"  - {mat}: {info.get('type', 'pbr')} material\n"
            else:
                return f"Category '{category}' not found. Available categories: {', '.join(categories.keys())}"
        else:
            for cat_name, cat_materials in categories.items():
                output += f"{cat_name.upper()}:\n"
                for mat in cat_materials:
                    info = get_material_info(mat)
                    output += f"  - {mat}: {info.get('type', 'pbr')} material\n"
                output += "\n"
        
        return output
    except Exception as e:
        logger.error(f"Error listing material presets: {str(e)}")
        return f"Error listing material presets: {str(e)}"

@telemetry_tool("suggest_material")
@mcp.tool()
def suggest_material(ctx: Context, object_name: str) -> str:
    """
    Get a suggested material preset based on an object's name.
    
    Parameters:
    - object_name: Name of the object to get material suggestion for
    
    Returns the suggested material preset name and details.
    """
    try:
        suggested = get_suggested_material(object_name)
        material_info = get_material_info(suggested)
        
        output = f"Suggested material for '{object_name}': {suggested}\n"
        output += f"Type: {material_info.get('type', 'pbr')}\n"
        
        if 'base_color' in material_info:
            r, g, b, a = material_info['base_color']
            output += f"Base Color: RGB({r:.2f}, {g:.2f}, {b:.2f})\n"
        
        if 'metallic' in material_info:
            output += f"Metallic: {material_info['metallic']}\n"
        
        if 'roughness' in material_info:
            output += f"Roughness: {material_info['roughness']}\n"
        
        output += f"\nTo apply: use apply_material_preset('{object_name}', '{suggested}')"
        
        return output
    except Exception as e:
        logger.error(f"Error suggesting material: {str(e)}")
        return f"Error suggesting material: {str(e)}"

@telemetry_tool("create_custom_pbr_material")
@mcp.tool()
def create_custom_pbr_material(
    ctx: Context,
    object_name: str,
    base_color: list[float],
    metallic: float = 0.0,
    roughness: float = 0.5,
    specular: float = 0.5,
    transmission: float = 0.0,
    emission_strength: float = 0.0,
    clearcoat: float = 0.0
) -> str:
    """
    Create and apply a custom PBR material to an object with specific properties.
    
    Parameters:
    - object_name: Name of the object to apply material to
    - base_color: RGBA color [R, G, B, A] where values are 0.0-1.0
    - metallic: Metallic value 0.0-1.0 (0=dielectric, 1=metal)
    - roughness: Roughness value 0.0-1.0 (0=glossy, 1=rough)
    - specular: Specular intensity 0.0-1.0
    - transmission: Transmission/transparency 0.0-1.0
    - emission_strength: Emission strength (0=no emission)
    - clearcoat: Clearcoat layer 0.0-1.0
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        
        if len(base_color) not in [3, 4]:
            return "Error: base_color must be [R, G, B] or [R, G, B, A] with values 0.0-1.0"
        
        if len(base_color) == 3:
            base_color.append(1.0)
        
        material_props = {
            "type": "pbr",
            "base_color": tuple(base_color),
            "metallic": max(0.0, min(1.0, metallic)),
            "roughness": max(0.0, min(1.0, roughness)),
            "specular": max(0.0, min(1.0, specular)),
            "transmission": max(0.0, min(1.0, transmission)),
            "emission_strength": max(0.0, emission_strength),
            "clearcoat": max(0.0, min(1.0, clearcoat))
        }
        
        result = blender.send_command("apply_material_preset", {
            "object_name": object_name,
            "material_props": material_props,
            "preset_name": "custom"
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            return f"Successfully applied custom PBR material to {object_name}"
        else:
            return f"Failed to apply material: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error creating custom material: {str(e)}")
        return f"Error creating custom material: {str(e)}"

# ==================== POST-PROCESSING TOOLS ====================

@telemetry_tool("apply_subdivision_surface")
@mcp.tool()
def apply_subdivision_surface(
    ctx: Context,
    object_name: str,
    viewport_levels: int = 2,
    render_levels: int = 3,
    adaptive: bool = True
) -> str:
    """
    Apply subdivision surface modifier to smooth and add detail to geometry.
    
    Parameters:
    - object_name: Name of the object to subdivide
    - viewport_levels: Subdivision levels in viewport (0-6, default 2)
    - render_levels: Subdivision levels for rendering (0-6, default 3)
    - adaptive: Use adaptive subdivision for better performance
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("apply_subdivision_surface", {
            "object_name": object_name,
            "viewport_levels": max(0, min(6, viewport_levels)),
            "render_levels": max(0, min(6, render_levels)),
            "adaptive": adaptive
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            return f"Applied subdivision surface to {object_name} (viewport: {viewport_levels}, render: {render_levels})"
        else:
            return f"Failed to apply subdivision: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying subdivision surface: {str(e)}")
        return f"Error applying subdivision surface: {str(e)}"

@telemetry_tool("apply_enhancement_preset")
@mcp.tool()
def apply_enhancement_preset(
    ctx: Context,
    object_name: str,
    preset: str = "smooth"
) -> str:
    """
    Apply a complete geometry enhancement preset to an object.
    
    Parameters:
    - object_name: Name of the object to enhance
    - preset: Enhancement preset (smooth, high_detail, mechanical, organic, architectural)
    
    Returns a message with details of applied enhancements.
    """
    try:
        blender = get_blender_connection()
        
        # Validate preset exists
        if preset not in ENHANCEMENT_PRESETS:
            available = ", ".join(list_available_presets())
            return f"Error: Preset '{preset}' not found. Available presets: {available}"
        
        # Get preset configuration
        preset_config = ENHANCEMENT_PRESETS[preset].copy()
        
        result = blender.send_command("apply_enhancement_preset", {
            "object_name": object_name,
            "preset_config": preset_config,
            "preset_name": preset
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            applied = result.get("applied_modifiers", [])
            output = f"Applied '{preset}' enhancement to {object_name}:\n"
            for mod in applied:
                output += f"  - {mod}\n"
            return output
        else:
            return f"Failed to apply enhancement: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying enhancement preset: {str(e)}")
        return f"Error applying enhancement preset: {str(e)}"

@telemetry_tool("auto_enhance_geometry")
@mcp.tool()
def auto_enhance_geometry(
    ctx: Context,
    object_name: str = None,
    analyze_first: bool = True
) -> str:
    """
    Automatically enhance geometry quality based on object analysis.
    If no object specified, enhances all mesh objects in the scene.
    
    Parameters:
    - object_name: Optional name of specific object. If None, enhances all mesh objects
    - analyze_first: Analyze mesh quality before enhancement to choose optimal settings
    
    Returns a message with details of enhancements applied.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("auto_enhance_geometry", {
            "object_name": object_name,
            "analyze_first": analyze_first
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            enhanced_count = result.get("enhanced_count", 0)
            details = result.get("details", [])
            
            output = f"Successfully enhanced {enhanced_count} object(s):\n"
            for detail in details:
                output += f"  {detail}\n"
            
            return output
        else:
            return f"Failed to enhance geometry: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error auto-enhancing geometry: {str(e)}")
        return f"Error auto-enhancing geometry: {str(e)}"

@telemetry_tool("analyze_mesh")
@mcp.tool()
def analyze_mesh(ctx: Context, object_name: str) -> str:
    """
    Analyze mesh quality and get improvement suggestions.
    
    Parameters:
    - object_name: Name of the object to analyze
    
    Returns analysis results with quality metrics and suggestions.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("analyze_mesh", {
            "object_name": object_name
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            stats = result.get("stats", {})
            analysis = result.get("analysis", {})
            
            output = f"Mesh Analysis for '{object_name}':\n\n"
            output += "Statistics:\n"
            output += f"  Vertices: {stats.get('vertex_count', 0):,}\n"
            output += f"  Faces: {stats.get('face_count', 0):,}\n"
            output += f"  Triangles: {stats.get('triangles', 0):,}\n"
            output += f"  Quads: {stats.get('quads', 0):,}\n"
            output += f"  Ngons: {stats.get('ngons', 0):,}\n"
            
            if stats.get('loose_verts', 0) > 0:
                output += f"  ⚠️  Loose vertices: {stats['loose_verts']}\n"
            
            output += f"\nQuality: {analysis.get('priority', 'good').upper()}\n"
            
            suggestions = analysis.get('suggestions', [])
            if suggestions:
                output += "\nSuggestions:\n"
                for suggestion in suggestions:
                    output += f"  • {suggestion}\n"
            
            output += f"\nRecommended preset: {analysis.get('recommended_preset', 'smooth')}\n"
            
            return output
        else:
            return f"Failed to analyze mesh: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error analyzing mesh: {str(e)}")
        return f"Error analyzing mesh: {str(e)}"

@telemetry_tool("add_edge_bevel")
@mcp.tool()
def add_edge_bevel(
    ctx: Context,
    object_name: str,
    width: float = 0.01,
    segments: int = 2
) -> str:
    """
    Add bevel modifier to smooth hard edges.
    
    Parameters:
    - object_name: Name of the object
    - width: Bevel width (default 0.01)
    - segments: Number of segments (default 2)
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("add_edge_bevel", {
            "object_name": object_name,
            "width": width,
            "segments": segments
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            return f"Added bevel modifier to {object_name} (width: {width}, segments: {segments})"
        else:
            return f"Failed to add bevel: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error adding bevel: {str(e)}")
        return f"Error adding bevel: {str(e)}"

@telemetry_tool("set_shading")
@mcp.tool()
def set_shading(
    ctx: Context,
    object_name: str,
    smooth: bool = True,
    auto_smooth_angle: float = 30.0
) -> str:
    """
    Set object shading to smooth or flat with optional auto-smooth.
    
    Parameters:
    - object_name: Name of the object
    - smooth: Use smooth shading (True) or flat shading (False)
    - auto_smooth_angle: Angle in degrees for auto-smooth (0-180)
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("set_shading", {
            "object_name": object_name,
            "smooth": smooth,
            "auto_smooth_angle": max(0.0, min(180.0, auto_smooth_angle))
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            shading_type = "smooth" if smooth else "flat"
            msg = f"Set {shading_type} shading for {object_name}"
            if smooth and auto_smooth_angle > 0:
                msg += f" with auto-smooth at {auto_smooth_angle}°"
            return msg
        else:
            return f"Failed to set shading: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error setting shading: {str(e)}")
        return f"Error setting shading: {str(e)}"

@telemetry_tool("list_enhancement_presets")
@mcp.tool()
def list_enhancement_presets(ctx: Context) -> str:
    """
    List all available geometry enhancement presets.
    
    Returns a formatted list of enhancement presets with descriptions.
    """
    try:
        presets = list_available_presets()
        
        descriptions = {
            "smooth": "General purpose smoothing with moderate subdivision",
            "high_detail": "Maximum quality with high subdivision and beveling",
            "mechanical": "Hard-surface objects with sharp edges and beveling",
            "organic": "Smooth organic shapes with remeshing",
            "architectural": "Buildings and structures with crisp edges"
        }
        
        output = "Available Geometry Enhancement Presets:\n\n"
        
        for preset in presets:
            config = get_preset_info(preset)
            output += f"• {preset.upper()}\n"
            output += f"  {descriptions.get(preset, 'Custom preset')}\n"
            
            if config:
                if config.get("subdivision", {}).get("enabled"):
                    levels = config["subdivision"]["levels"]
                    output += f"  - Subdivision: {levels} levels\n"
                if config.get("bevel", {}).get("enabled"):
                    output += f"  - Bevel edges\n"
                if config.get("shade_smooth"):
                    output += f"  - Smooth shading\n"
            
            output += "\n"
        
        return output
    except Exception as e:
        logger.error(f"Error listing enhancement presets: {str(e)}")
        return f"Error listing enhancement presets: {str(e)}"

@telemetry_tool("suggest_enhancement")
@mcp.tool()
def suggest_enhancement(ctx: Context, object_name: str) -> str:
    """
    Get suggested enhancement preset based on object name and analysis.
    
    Parameters:
    - object_name: Name of the object to analyze
    
    Returns the suggested preset with reasoning.
    """
    try:
        suggested = get_suggested_preset(object_name)
        preset_info = get_preset_info(suggested)
        
        output = f"Suggested enhancement for '{object_name}': {suggested.upper()}\n\n"
        
        # Show what will be applied
        if preset_info:
            output += "This preset will apply:\n"
            
            if preset_info.get("subdivision", {}).get("enabled"):
                sub = preset_info["subdivision"]
                output += f"  • Subdivision surface ({sub['levels']} viewport, {sub['render_levels']} render)\n"
            
            if preset_info.get("bevel", {}).get("enabled"):
                bev = preset_info["bevel"]
                output += f"  • Edge bevel (width: {bev['width']}, segments: {bev['segments']})\n"
            
            if preset_info.get("edge_split", {}).get("enabled"):
                output += f"  • Edge split at {preset_info['edge_split']['angle']}°\n"
            
            if preset_info.get("shade_smooth"):
                output += f"  • Smooth shading\n"
                if preset_info.get("auto_smooth", {}).get("enabled"):
                    output += f"    with auto-smooth at {preset_info['auto_smooth']['angle']}°\n"
        
        output += f"\nTo apply: use apply_enhancement_preset('{object_name}', '{suggested}')"
        
        return output
    except Exception as e:
        logger.error(f"Error suggesting enhancement: {str(e)}")
        return f"Error suggesting enhancement: {str(e)}"

# ============================================================================
# LIGHTING & ATMOSPHERE TOOLS
# ============================================================================

@telemetry_tool("setup_hdri_lighting")
@mcp.tool()
async def setup_hdri_lighting(
    ctx: Context, 
    preset: str = "studio",
    rotation: float = None,
    strength: float = None,
    background_strength: float = None
) -> str:
    """
    Set up HDRI environment lighting for the scene.
    
    Parameters:
    - preset: HDRI preset (studio, outdoor_day, sunset, night, overcast, interior)
    - rotation: Optional rotation override (0-360 degrees)
    - strength: Optional strength override (0-10)
    - background_strength: Optional background visibility override (0-1)
    
    Returns confirmation of HDRI setup.
    """
    try:
        blender = get_blender_connection()
        
        if preset not in HDRI_PRESETS:
            available = ", ".join(HDRI_PRESETS.keys())
            return f"Error: Unknown HDRI preset '{preset}'. Available: {available}"
        
        hdri_config = HDRI_PRESETS[preset].copy()
        
        # Override with custom values if provided
        if rotation is not None:
            hdri_config["rotation"] = rotation
        if strength is not None:
            hdri_config["strength"] = strength
        if background_strength is not None:
            hdri_config["background_strength"] = background_strength
        
        result = await async_send_command(blender, "setup_hdri_lighting", {
            "preset": preset,
            "config": hdri_config
        })
        
        if "error" in result:
            return f"Error setting up HDRI: {result['error']}"
        
        output = f"HDRI lighting configured: {preset.upper()}\n"
        output += f"Description: {hdri_config['description']}\n"
        output += f"Strength: {hdri_config['strength']}\n"
        output += f"Rotation: {hdri_config['rotation']}°\n"
        output += f"Background visibility: {hdri_config['background_strength']}\n"
        
        if hdri_config.get("recommended_hdris"):
            output += f"\nRecommended HDRIs from PolyHaven:\n"
            for hdri in hdri_config["recommended_hdris"]:
                output += f"  - {hdri}\n"
        
        return output
    except Exception as e:
        logger.error(f"Error setting up HDRI: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("apply_lighting_rig")
@mcp.tool()
async def apply_lighting_rig(
    ctx: Context,
    preset: str = "three_point",
    scale: float = 1.0
) -> str:
    """
    Apply a lighting rig to the scene.
    
    Parameters:
    - preset: Lighting rig preset (three_point, studio, dramatic, outdoor, night)
    - scale: Scale multiplier for light positions (default 1.0)
    
    Returns confirmation of lights created.
    """
    try:
        blender = get_blender_connection()
        
        if preset not in LIGHTING_RIGS:
            available = ", ".join(LIGHTING_RIGS.keys())
            return f"Error: Unknown lighting rig '{preset}'. Available: {available}"
        
        rig_config = LIGHTING_RIGS[preset]
        
        result = await async_send_command(blender, "apply_lighting_rig", {
            "preset": preset,
            "config": rig_config,
            "scale": scale
        })
        
        if "error" in result:
            return f"Error applying lighting rig: {result['error']}"
        
        output = f"Lighting rig applied: {preset.upper()}\n"
        output += f"Description: {rig_config['description']}\n"
        output += f"Lights created: {len(rig_config['lights'])}\n\n"
        
        for light in rig_config['lights']:
            output += f"  • {light['name']} ({light['type']})\n"
            output += f"    Energy: {light['energy']}\n"
        
        return output
    except Exception as e:
        logger.error(f"Error applying lighting rig: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("add_atmospheric_fog")
@mcp.tool()
async def add_atmospheric_fog(
    ctx: Context,
    preset: str = "fog",
    density: float = None
) -> str:
    """
    Add volumetric fog/atmosphere to the scene.
    
    Parameters:
    - preset: Atmosphere preset (fog, heavy_fog, god_rays, haze, none)
    - density: Optional density override (0.001-1.0)
    
    Returns confirmation of atmosphere setup.
    """
    try:
        blender = get_blender_connection()
        
        if preset not in ATMOSPHERE_PRESETS:
            available = ", ".join(ATMOSPHERE_PRESETS.keys())
            return f"Error: Unknown atmosphere preset '{preset}'. Available: {available}"
        
        atmo_config = ATMOSPHERE_PRESETS[preset].copy()
        
        if density is not None:
            atmo_config["density"] = density
        
        result = await async_send_command(blender, "add_atmospheric_fog", {
            "preset": preset,
            "config": atmo_config
        })
        
        if "error" in result:
            return f"Error setting up atmosphere: {result['error']}"
        
        if not atmo_config.get("volumetric"):
            return "Atmosphere cleared (none preset selected)"
        
        output = f"Atmospheric fog configured: {preset.upper()}\n"
        output += f"Description: {atmo_config['description']}\n"
        output += f"Density: {atmo_config['density']}\n"
        output += f"Anisotropy: {atmo_config['anisotropy']}\n"
        output += "\nNote: Enable volumetrics in render settings for best results."
        
        return output
    except Exception as e:
        logger.error(f"Error setting up atmosphere: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("setup_camera")
@mcp.tool()
async def setup_camera(
    ctx: Context,
    preset: str = "normal",
    position: str = "three_quarter",
    target_object: str = None,
    focal_length: float = None,
    f_stop: float = None
) -> str:
    """
    Create and configure a camera for the scene.
    
    Parameters:
    - preset: Camera lens preset (portrait, wide, normal, telephoto, architectural)
    - position: Camera position type (front, side, top, three_quarter)
    - target_object: Optional object name to focus on (auto-calculates position)
    - focal_length: Optional focal length override (mm)
    - f_stop: Optional f-stop override for depth of field
    
    Returns confirmation of camera setup.
    """
    try:
        blender = get_blender_connection()
        
        if preset not in CAMERA_PRESETS:
            available = ", ".join(CAMERA_PRESETS.keys())
            return f"Error: Unknown camera preset '{preset}'. Available: {available}"
        
        camera_config = CAMERA_PRESETS[preset].copy()
        
        # Override with custom values
        if focal_length is not None:
            camera_config["focal_length"] = focal_length
        if f_stop is not None:
            camera_config["f_stop"] = f_stop
        
        result = await async_send_command(blender, "setup_camera", {
            "preset": preset,
            "config": camera_config,
            "position_type": position,
            "target_object": target_object
        })
        
        if "error" in result:
            return f"Error setting up camera: {result['error']}"
        
        output = f"Camera configured: {preset.upper()}\n"
        output += f"Description: {camera_config['description']}\n"
        output += f"Focal length: {camera_config['focal_length']}mm\n"
        output += f"Position: {position}\n"
        
        if camera_config.get("dof_enabled"):
            output += f"Depth of Field: f/{camera_config['f_stop']}\n"
        
        if target_object:
            output += f"Focused on: {target_object}\n"
        
        return output
    except Exception as e:
        logger.error(f"Error setting up camera: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("configure_render_settings")
@mcp.tool()
async def configure_render_settings(
    ctx: Context,
    preset: str = "preview",
    resolution_x: int = 1920,
    resolution_y: int = 1080
) -> str:
    """
    Configure render engine and quality settings.
    
    Parameters:
    - preset: Render quality preset (draft, preview, production, final)
    - resolution_x: Render width in pixels (default 1920)
    - resolution_y: Render height in pixels (default 1080)
    
    Returns confirmation of render settings.
    """
    try:
        blender = get_blender_connection()
        
        if preset not in RENDER_PRESETS:
            available = ", ".join(RENDER_PRESETS.keys())
            return f"Error: Unknown render preset '{preset}'. Available: {available}"
        
        render_config = RENDER_PRESETS[preset].copy()
        render_config["resolution_x"] = resolution_x
        render_config["resolution_y"] = resolution_y
        
        result = await async_send_command(blender, "configure_render_settings", {
            "preset": preset,
            "config": render_config
        })
        
        if "error" in result:
            return f"Error configuring render: {result['error']}"
        
        output = f"Render settings configured: {preset.upper()}\n"
        output += f"Description: {render_config['description']}\n"
        output += f"Engine: {render_config['engine']}\n"
        output += f"Samples: {render_config['samples']}\n"
        output += f"Resolution: {resolution_x}x{resolution_y} ({render_config['resolution_percentage']}%)\n"
        output += f"Denoising: {'Enabled' if render_config['use_denoising'] else 'Disabled'}\n"
        
        return output
    except Exception as e:
        logger.error(f"Error configuring render: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("auto_setup_scene_lighting")
@mcp.tool()
async def auto_setup_scene_lighting(
    ctx: Context,
    scene_description: str,
    target_object: str = None
) -> str:
    """
    Automatically set up complete lighting based on scene description.
    Configures HDRI, lighting rig, atmosphere, camera, and render settings.
    
    Parameters:
    - scene_description: Description of the scene (e.g., "outdoor product shot", "dramatic portrait")
    - target_object: Optional primary object to focus on
    
    Returns summary of all applied settings.
    """
    try:
        blender = get_blender_connection()
        
        # Get suggestions
        suggestions = suggest_scene_lighting(scene_description)
        
        output = f"Auto-configuring scene for: {scene_description}\n\n"
        
        # Apply HDRI
        hdri_result = await setup_hdri_lighting(ctx, suggestions["hdri"])
        output += "HDRI Setup:\n" + hdri_result + "\n\n"
        
        # Apply lighting rig
        rig_result = await apply_lighting_rig(ctx, suggestions["lighting_rig"])
        output += "Lighting Rig:\n" + rig_result + "\n\n"
        
        # Apply atmosphere
        atmo_result = await add_atmospheric_fog(ctx, suggestions["atmosphere"])
        output += "Atmosphere:\n" + atmo_result + "\n\n"
        
        # Setup camera
        cam_result = await setup_camera(
            ctx, 
            suggestions["camera"],
            target_object=target_object
        )
        output += "Camera:\n" + cam_result + "\n\n"
        
        # Configure render
        render_result = await configure_render_settings(ctx, "preview")
        output += "Render Settings:\n" + render_result + "\n"
        
        output += "\n✅ Scene lighting fully configured!"
        output += "\nTip: Use configure_render_settings('production') for final output."
        
        return output
    except Exception as e:
        logger.error(f"Error auto-setting up scene: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("list_lighting_presets")
@mcp.tool()
def list_lighting_presets(ctx: Context, category: str = "all") -> str:
    """
    List available lighting, camera, and atmosphere presets.
    
    Parameters:
    - category: Which category to list (all, hdri, lighting, atmosphere, camera, render)
    
    Returns formatted list of presets with descriptions.
    """
    try:
        output = ""
        
        if category in ["all", "hdri"]:
            output += "HDRI PRESETS:\n"
            for name, config in HDRI_PRESETS.items():
                output += f"  • {name}: {config['description']}\n"
            output += "\n"
        
        if category in ["all", "lighting"]:
            output += "LIGHTING RIG PRESETS:\n"
            for name, config in LIGHTING_RIGS.items():
                output += f"  • {name}: {config['description']} ({len(config['lights'])} lights)\n"
            output += "\n"
        
        if category in ["all", "atmosphere"]:
            output += "ATMOSPHERE PRESETS:\n"
            for name, config in ATMOSPHERE_PRESETS.items():
                output += f"  • {name}: {config['description']}\n"
            output += "\n"
        
        if category in ["all", "camera"]:
            output += "CAMERA PRESETS:\n"
            for name, config in CAMERA_PRESETS.items():
                output += f"  • {name}: {config['description']} ({config['focal_length']}mm)\n"
            output += "\n"
        
        if category in ["all", "render"]:
            output += "RENDER QUALITY PRESETS:\n"
            for name, config in RENDER_PRESETS.items():
                output += f"  • {name}: {config['description']} ({config['samples']} samples)\n"
        
        return output.strip()
    except Exception as e:
        logger.error(f"Error listing presets: {str(e)}")
        return f"Error: {str(e)}"

# ============================================================================
# COMPOSITION SYSTEM TOOLS
# ============================================================================

@telemetry_tool("analyze_scene_composition")
@mcp.tool()
def analyze_scene_composition(
    ctx: Context,
    object_name: str = None,
    composition_rule: str = "rule_of_thirds"
) -> str:
    """
    Analyze current scene composition and provide scoring/recommendations.
    
    Parameters:
    - object_name: Name of the main subject object (optional, uses active if not specified)
    - composition_rule: Rule to evaluate against (rule_of_thirds, golden_ratio, center_composition, etc.)
    
    Returns detailed composition analysis with score and improvement suggestions.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("analyze_composition", {
            "object_name": object_name,
            "composition_rule": composition_rule
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error analyzing composition: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("apply_composition_rule")
@mcp.tool()
def apply_composition_rule(
    ctx: Context,
    object_name: str,
    composition_rule: str = "rule_of_thirds",
    camera_angle: str = "three_quarter"
) -> str:
    """
    Position camera using specific composition rule to frame the object.
    
    Parameters:
    - object_name: Name of object to frame
    - composition_rule: Composition rule to apply (rule_of_thirds, golden_ratio, center_composition, 
                        diagonal, frame_within_frame, leading_lines)
    - camera_angle: Camera angle preset (front, three_quarter, side, top, low, high)
    
    Returns success message with camera details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("apply_composition_rule", {
            "object_name": object_name,
            "composition_rule": composition_rule,
            "camera_angle": camera_angle
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error applying composition: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("auto_frame_with_composition")
@mcp.tool()
def auto_frame_with_composition(
    ctx: Context,
    object_name: str,
    purpose: str = "general",
    preset: str = None
) -> str:
    """
    Automatically frame object with optimal composition, shot type, and camera settings.
    This is the recommended all-in-one composition tool.
    
    Parameters:
    - object_name: Name of object to frame
    - purpose: Purpose of shot (detail, portrait, product, general, establishing, landscape, epic)
    - preset: Optional composition preset (portrait_pro, portrait_cinematic, product_hero, 
              product_lifestyle, architecture_hero, architecture_dramatic, landscape_classic, landscape_epic)
    
    Returns complete scene setup details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("auto_frame_with_composition", {
            "object_name": object_name,
            "purpose": purpose,
            "preset": preset
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error auto-framing: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("list_composition_presets")
@mcp.tool()
def list_composition_presets(ctx: Context, category: str = "all") -> str:
    """
    List available composition presets, rules, and shot types.
    
    Parameters:
    - category: Which category to list (all, rules, shots, presets, framing)
    
    Returns formatted list of composition options.
    """
    try:
        output = ""
        
        if category in ["all", "presets"]:
            output += "COMPOSITION PRESETS (Quick Setups):\n"
            for name, config in COMPOSITION_PRESETS.items():
                output += f"  • {name}: {config['name']}\n"
                output += f"    - Rule: {config['composition_rule']}, Shot: {config['shot_type']}\n"
            output += "\n"
        
        if category in ["all", "rules"]:
            output += "COMPOSITION RULES:\n"
            for name, config in COMPOSITION_RULES.items():
                output += f"  • {name}: {config['name']}\n"
                output += f"    - {config['description']}\n"
                output += f"    - Ideal for: {', '.join(config['ideal_for'])}\n"
            output += "\n"
        
        if category in ["all", "shots"]:
            output += "SHOT TYPES:\n"
            for name, config in SHOT_TYPES.items():
                output += f"  • {name}: {config['name']} ({config['focal_length']}mm)\n"
                output += f"    - {config['description']}\n"
                output += f"    - Frame fill: {int(config['frame_fill']*100)}%\n"
            output += "\n"
        
        if category in ["all", "framing"]:
            output += "FRAMING PRESETS:\n"
            for name, config in FRAMING_PRESETS.items():
                output += f"  • {name}: {config['name']}\n"
                output += f"    - Shot: {config['shot_type']}, Rule: {config['composition_rule']}\n"
        
        return output.strip()
    except Exception as e:
        logger.error(f"Error listing composition presets: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("suggest_composition")
@mcp.tool()
def suggest_composition(
    ctx: Context,
    object_name: str,
    scene_description: str = ""
) -> str:
    """
    Get AI-powered composition suggestions based on object and scene context.
    
    Parameters:
    - object_name: Name of the subject object
    - scene_description: Optional description of the scene/intent (e.g., "dramatic portrait", 
                        "product showcase", "epic landscape")
    
    Returns recommended composition rule, shot type, and framing preset.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("suggest_composition", {
            "object_name": object_name,
            "scene_description": scene_description
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error suggesting composition: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("calculate_shot_framing")
@mcp.tool()
def calculate_shot_framing(
    ctx: Context,
    object_name: str,
    shot_type: str = "medium_shot"
) -> str:
    """
    Calculate optimal camera position and settings for specific shot type.
    
    Parameters:
    - object_name: Name of object to frame
    - shot_type: Desired shot type (extreme_closeup, closeup, medium_closeup, medium_shot,
                medium_wide, wide_shot, extreme_wide)
    
    Returns camera position, focal length, DOF settings, and expected frame fill.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("calculate_shot_framing", {
            "object_name": object_name,
            "shot_type": shot_type
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error calculating shot framing: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("get_polyhaven_categories")
@mcp.tool()
def get_polyhaven_categories(ctx: Context, asset_type: str = "hdris") -> str:
    """
    Get a list of categories for a specific asset type on Polyhaven.
    
    Parameters:
    - asset_type: The type of asset to get categories for (hdris, textures, models, all)
    """
    try:
        blender = get_blender_connection()
        if not _polyhaven_enabled:
            return "PolyHaven integration is disabled. Select it in the sidebar in BlenderMCP, then run it again."
        result = blender.send_command("get_polyhaven_categories", {"asset_type": asset_type})
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Format the categories in a more readable way
        categories = result["categories"]
        formatted_output = f"Categories for {asset_type}:\n\n"
        
        # Sort categories by count (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            formatted_output += f"- {category}: {count} assets\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error getting Polyhaven categories: {str(e)}")
        return f"Error getting Polyhaven categories: {str(e)}"

@telemetry_tool("search_polyhaven_assets")
@mcp.tool()
def search_polyhaven_assets(
    ctx: Context,
    asset_type: str = "all",
    categories: str = None
) -> str:
    """
    Search for assets on Polyhaven with optional filtering.
    
    Parameters:
    - asset_type: Type of assets to search for (hdris, textures, models, all)
    - categories: Optional comma-separated list of categories to filter by
    
    Returns a list of matching assets with basic information.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("search_polyhaven_assets", {
            "asset_type": asset_type,
            "categories": categories
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Format the assets in a more readable way
        assets = result["assets"]
        total_count = result["total_count"]
        returned_count = result["returned_count"]
        
        formatted_output = f"Found {total_count} assets"
        if categories:
            formatted_output += f" in categories: {categories}"
        formatted_output += f"\nShowing {returned_count} assets:\n\n"
        
        # Sort assets by download count (popularity)
        sorted_assets = sorted(assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True)
        
        for asset_id, asset_data in sorted_assets:
            formatted_output += f"- {asset_data.get('name', asset_id)} (ID: {asset_id})\n"
            formatted_output += f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
            formatted_output += f"  Categories: {', '.join(asset_data.get('categories', []))}\n"
            formatted_output += f"  Downloads: {asset_data.get('download_count', 'Unknown')}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Polyhaven assets: {str(e)}")
        return f"Error searching Polyhaven assets: {str(e)}"

@telemetry_tool("download_polyhaven_asset")
@mcp.tool()
def download_polyhaven_asset(
    ctx: Context,
    asset_id: str,
    asset_type: str,
    resolution: str = "1k",
    file_format: str = None
) -> str:
    """
    Download and import a Polyhaven asset into Blender.
    
    Parameters:
    - asset_id: The ID of the asset to download
    - asset_type: The type of asset (hdris, textures, models)
    - resolution: The resolution to download (e.g., 1k, 2k, 4k)
    - file_format: Optional file format (e.g., hdr, exr for HDRIs; jpg, png for textures; gltf, fbx for models)
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("download_polyhaven_asset", {
            "asset_id": asset_id,
            "asset_type": asset_type,
            "resolution": resolution,
            "file_format": file_format
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            message = result.get("message", "Asset downloaded and imported successfully")
            
            # Add additional information based on asset type
            if asset_type == "hdris":
                return f"{message}. The HDRI has been set as the world environment."
            elif asset_type == "textures":
                material_name = result.get("material", "")
                maps = ", ".join(result.get("maps", []))
                return f"{message}. Created material '{material_name}' with maps: {maps}."
            elif asset_type == "models":
                return f"{message}. The model has been imported into the current scene."
            else:
                return message
        else:
            return f"Failed to download asset: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Polyhaven asset: {str(e)}")
        return f"Error downloading Polyhaven asset: {str(e)}"

@telemetry_tool("set_texture")
@mcp.tool()
def set_texture(
    ctx: Context,
    object_name: str,
    texture_id: str
) -> str:
    """
    Apply a previously downloaded Polyhaven texture to an object.
    
    Parameters:
    - object_name: Name of the object to apply the texture to
    - texture_id: ID of the Polyhaven texture to apply (must be downloaded first)
    
    Returns a message indicating success or failure.
    """
    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command("set_texture", {
            "object_name": object_name,
            "texture_id": texture_id
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))
            
            # Add detailed material info
            material_info = result.get("material_info", {})
            node_count = material_info.get("node_count", 0)
            has_nodes = material_info.get("has_nodes", False)
            texture_nodes = material_info.get("texture_nodes", [])
            
            output = f"Successfully applied texture '{texture_id}' to {object_name}.\n"
            output += f"Using material '{material_name}' with maps: {maps}.\n\n"
            output += f"Material has nodes: {has_nodes}\n"
            output += f"Total node count: {node_count}\n\n"
            
            if texture_nodes:
                output += "Texture nodes:\n"
                for node in texture_nodes:
                    output += f"- {node['name']} using image: {node['image']}\n"
                    if node['connections']:
                        output += "  Connections:\n"
                        for conn in node['connections']:
                            output += f"    {conn}\n"
            else:
                output += "No texture nodes found in the material.\n"
            
            return output
        else:
            return f"Failed to apply texture: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying texture: {str(e)}")
        return f"Error applying texture: {str(e)}"

@telemetry_tool("get_polyhaven_status")
@mcp.tool()
def get_polyhaven_status(ctx: Context) -> str:
    """
    Check if PolyHaven integration is enabled in Blender.
    Returns a message indicating whether PolyHaven features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_polyhaven_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += "PolyHaven is good at Textures, and has a wider variety of textures than Sketchfab."
        return message
    except Exception as e:
        logger.error(f"Error checking PolyHaven status: {str(e)}")
        return f"Error checking PolyHaven status: {str(e)}"

@telemetry_tool("get_hyper3d_status")
@mcp.tool()
def get_hyper3d_status(ctx: Context) -> str:
    """
    Check if Hyper3D Rodin integration is enabled in Blender.
    Returns a message indicating whether Hyper3D Rodin features are available.

    Don't emphasize the key type in the returned message, but sliently remember it. 
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hyper3d_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += ""
        return message
    except Exception as e:
        logger.error(f"Error checking Hyper3D status: {str(e)}")
        return f"Error checking Hyper3D status: {str(e)}"

@telemetry_tool("get_sketchfab_status")
@mcp.tool()
def get_sketchfab_status(ctx: Context) -> str:
    """
    Check if Sketchfab integration is enabled in Blender.
    Returns a message indicating whether Sketchfab features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_sketchfab_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += "Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven."        
        return message
    except Exception as e:
        logger.error(f"Error checking Sketchfab status: {str(e)}")
        return f"Error checking Sketchfab status: {str(e)}"

@telemetry_tool("search_sketchfab_models")
@mcp.tool()
def search_sketchfab_models(
    ctx: Context,
    query: str,
    categories: str = None,
    count: int = 20,
    downloadable: bool = True
) -> str:
    """
    Search for models on Sketchfab with optional filtering.

    Parameters:
    - query: Text to search for
    - categories: Optional comma-separated list of categories
    - count: Maximum number of results to return (default 20)
    - downloadable: Whether to include only downloadable models (default True)

    Returns a formatted list of matching models.
    """
    try:
        blender = get_blender_connection()
        logger.info(f"Searching Sketchfab models with query: {query}, categories: {categories}, count: {count}, downloadable: {downloadable}")
        result = blender.send_command("search_sketchfab_models", {
            "query": query,
            "categories": categories,
            "count": count,
            "downloadable": downloadable
        })
        
        if "error" in result:
            logger.error(f"Error from Sketchfab search: {result['error']}")
            return f"Error: {result['error']}"
        
        # Safely get results with fallbacks for None
        if result is None:
            logger.error("Received None result from Sketchfab search")
            return "Error: Received no response from Sketchfab search"
            
        # Format the results
        models = result.get("results", []) or []
        if not models:
            return f"No models found matching '{query}'"
            
        formatted_output = f"Found {len(models)} models matching '{query}':\n\n"
        
        for model in models:
            if model is None:
                continue
                
            model_name = model.get("name", "Unnamed model")
            model_uid = model.get("uid", "Unknown ID")
            formatted_output += f"- {model_name} (UID: {model_uid})\n"
            
            # Get user info with safety checks
            user = model.get("user") or {}
            username = user.get("username", "Unknown author") if isinstance(user, dict) else "Unknown author"
            formatted_output += f"  Author: {username}\n"
            
            # Get license info with safety checks
            license_data = model.get("license") or {}
            license_label = license_data.get("label", "Unknown") if isinstance(license_data, dict) else "Unknown"
            formatted_output += f"  License: {license_label}\n"
            
            # Add face count and downloadable status
            face_count = model.get("faceCount", "Unknown")
            is_downloadable = "Yes" if model.get("isDownloadable") else "No"
            formatted_output += f"  Face count: {face_count}\n"
            formatted_output += f"  Downloadable: {is_downloadable}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Sketchfab models: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error searching Sketchfab models: {str(e)}"

@telemetry_tool("download_sketchfab_model")
@mcp.tool()
def download_sketchfab_model(
    ctx: Context,
    uid: str
) -> str:
    """
    Download and import a Sketchfab model by its UID.
    
    Parameters:
    - uid: The unique identifier of the Sketchfab model
    
    Returns a message indicating success or failure.
    The model must be downloadable and you must have proper access rights.
    """
    try:
        
        blender = get_blender_connection()
        logger.info(f"Attempting to download Sketchfab model with UID: {uid}")
        
        result = blender.send_command("download_sketchfab_model", {
            "uid": uid
        })
        
        if result is None:
            logger.error("Received None result from Sketchfab download")
            return "Error: Received no response from Sketchfab download request"
            
        if "error" in result:
            logger.error(f"Error from Sketchfab download: {result['error']}")
            return f"Error: {result['error']}"
        
        if result.get("success"):
            imported_objects = result.get("imported_objects", [])
            object_names = ", ".join(imported_objects) if imported_objects else "none"
            return f"Successfully imported model. Created objects: {object_names}"
        else:
            return f"Failed to download model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Sketchfab model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error downloading Sketchfab model: {str(e)}"


# ============== BlenderKit Integration ==============

@mcp.tool()
def get_blenderkit_status(ctx: Context) -> str:
    """
    Check if BlenderKit integration is enabled and the BlenderKit addon is installed.
    Returns status information about BlenderKit availability and any active downloads.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_blenderkit_status")
        enabled = result.get("enabled", False)
        authenticated = result.get("authenticated", False)
        native = result.get("native_available", False)
        active_downloads = result.get("active_downloads", 0)
        message = result.get("message", "")
        
        if enabled:
            message += "\n\nBlenderKit provides access to thousands of high-quality assets:"
            message += "\n- Models (3D objects, characters, vehicles, furniture)"
            message += "\n- Materials (PBR textures, procedural materials)"
            message += "\n- HDRIs (environment lighting)"
            message += "\n- Brushes (sculpting brushes)"
            message += "\n- Scenes (complete scene setups)"
            
            if native:
                message += "\n\n✓ Native BlenderKit download system available"
            
            if not authenticated:
                message += "\n\n⚠️ Not logged in - only free assets available"
            
            if active_downloads > 0:
                message += f"\n\n📥 {active_downloads} download(s) in progress"
        
        return message
    except Exception as e:
        logger.error(f"Error checking BlenderKit status: {str(e)}")
        return f"Error checking BlenderKit status: {str(e)}"


@telemetry_tool("search_blenderkit_assets")
@mcp.tool()
def search_blenderkit_assets(
    ctx: Context,
    query: str,
    asset_type: str = "model",
    category: str = None,
    free_only: bool = True,
    count: int = 20
) -> str:
    """
    Search BlenderKit for assets with optional filtering.
    Includes automatic retry with exponential backoff for rate limits.
    
    Parameters:
    - query: Text to search for (e.g., "chair", "wood texture", "sunset hdri")
    - asset_type: Type of asset to search for:
        * "model" - 3D models (default)
        * "material" - PBR materials and textures
        * "hdr" - HDRI environment maps
        * "brush" - Sculpting brushes
        * "scene" - Complete scenes
    - category: Optional category filter (use get_blenderkit_categories to see options)
    - free_only: Only show free assets (default: True for safety)
    - count: Maximum results to return (default: 20)
    
    Returns a formatted list of matching assets with IDs for downloading.
    """
    try:
        blender = get_blender_connection()
        logger.info(f"Searching BlenderKit: query='{query}', type={asset_type}")
        
        result = blender.send_command("search_blenderkit_assets", {
            "query": query,
            "asset_type": asset_type,
            "category": category,
            "free_only": free_only,
            "count": count
        })
        
        if "error" in result:
            logger.error(f"BlenderKit search error: {result['error']}")
            return f"Error: {result['error']}"
        
        results = result.get("results", [])
        total = result.get("total", 0)
        
        if not results:
            return f"No {asset_type}s found matching '{query}'" + (" (free only)" if free_only else "")
        
        output = f"Found {len(results)} of {total} {asset_type}s matching '{query}':\n\n"
        
        for asset in results:
            size_mb = asset.get("file_size", 0) / (1024 * 1024)
            size_str = f"{size_mb:.1f}MB" if size_mb > 0 else "Unknown size"
            
            output += f"📦 **{asset.get('name', 'Unnamed')}**\n"
            output += f"   ID: `{asset.get('asset_base_id', asset.get('id'))}`\n"
            output += f"   Author: {asset.get('author', 'Unknown')}\n"
            output += f"   Free: {'✓ Yes' if asset.get('is_free') else '✗ No (requires login)'}\n"
            output += f"   Size: {size_str}\n"
            
            rating = asset.get('rating', 0)
            if rating > 0:
                output += f"   Rating: {'⭐' * int(rating)} ({rating:.1f})\n"
            
            output += f"   Downloads: {asset.get('downloads', 0):,}\n"
            
            if asset_type == "model" and asset.get("face_count"):
                output += f"   Faces: {asset.get('face_count')}\n"
            elif asset_type == "material" and asset.get("texture_resolution"):
                output += f"   Max Resolution: {asset.get('texture_resolution')}\n"
            
            output += "\n"
        
        output += "Use `download_blenderkit_asset` with the asset ID to import.\n"
        output += "Large files (>10MB) download in background - use `poll_blenderkit_download` to check status."
        
        return output
    except Exception as e:
        logger.error(f"Error searching BlenderKit: {str(e)}")
        return f"Error searching BlenderKit: {str(e)}"


@mcp.tool()
def get_blenderkit_categories(
    ctx: Context,
    asset_type: str = "model"
) -> str:
    """
    Get available categories for a BlenderKit asset type.
    
    Parameters:
    - asset_type: Type of asset ("model", "material", "hdr", "brush", "scene")
    
    Returns hierarchical list of categories for filtering searches.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_blenderkit_categories", {
            "asset_type": asset_type
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        categories = result.get("categories", [])
        
        if not categories:
            return f"No categories found for {asset_type}"
        
        output = f"BlenderKit categories for {asset_type}:\n\n"
        
        for cat in categories:
            path = cat.get('path', cat.get('name'))
            depth = path.count('/')
            indent = "  " * depth
            name = cat.get('name')
            slug = cat.get('slug')
            output += f"{indent}• {name} (`{slug}`)\n"
        
        output += f"\nUse the slug value as the `category` parameter in search_blenderkit_assets."
        
        return output
    except Exception as e:
        logger.error(f"Error getting BlenderKit categories: {str(e)}")
        return f"Error getting BlenderKit categories: {str(e)}"


@telemetry_tool("download_blenderkit_asset")
@mcp.tool()
def download_blenderkit_asset(
    ctx: Context,
    asset_id: str,
    asset_type: str = "model",
    name: str = None,
    location: list[float] = None
) -> str:
    """
    Download and import a BlenderKit asset into the scene.
    
    Large files (>10MB) are downloaded in the background. Use poll_blenderkit_download
    to check progress and automatically import when complete.
    
    Parameters:
    - asset_id: The asset ID from search results (the 'asset_base_id' or 'id' field)
    - asset_type: Type of asset ("model", "material", "hdr", "brush", "scene")
    - name: Optional custom name for the imported asset
    - location: Optional [x, y, z] position for models (default: origin)
    
    Returns:
    - For small files: Immediate confirmation of import
    - For large files: A download_id to poll for progress
    
    Note: Free assets download without login. Paid assets require BlenderKit login.
    """
    try:
        blender = get_blender_connection()
        logger.info(f"Downloading BlenderKit asset: id={asset_id}, type={asset_type}")
        
        result = blender.send_command("download_blenderkit_asset", {
            "asset_id": asset_id,
            "asset_type": asset_type,
            "name": name,
            "location": location,
            "background": True
        })
        
        if "error" in result:
            logger.error(f"BlenderKit download error: {result['error']}")
            return f"Error: {result['error']}"
        
        # Background download started
        if result.get("status") == "background":
            download_id = result.get("download_id")
            asset_name = result.get("asset_name", "asset")
            return (f"📥 Background download started for '{asset_name}'\n\n"
                   f"Download ID: `{download_id}`\n\n"
                   f"{result.get('message', '')}\n\n"
                   f"Use `poll_blenderkit_download(download_id='{download_id}')` to check progress.")
        
        # Immediate success
        if result.get("success"):
            imported = result.get("imported", [])
            imported_str = "\n".join([f"  • {i}" for i in imported]) if imported else "  (none)"
            return (f"✓ {result.get('message', 'Successfully imported asset')}\n\n"
                   f"Imported:\n{imported_str}")
        
        return f"Download failed: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        logger.error(f"Error downloading BlenderKit asset: {str(e)}")
        return f"Error downloading BlenderKit asset: {str(e)}"


@mcp.tool()
def poll_blenderkit_download(
    ctx: Context,
    download_id: str = None
) -> str:
    """
    Check the status of background BlenderKit downloads.
    
    When a download completes, this automatically imports the asset into Blender.
    
    Parameters:
    - download_id: Specific download to check (from download_blenderkit_asset).
                   If not provided, shows all active downloads.
    
    Returns current download status, progress percentage, or import confirmation.
    """
    try:
        blender = get_blender_connection()
        
        result = blender.send_command("poll_blenderkit_download", {
            "download_id": download_id
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Single download status
        if download_id:
            status = result.get("status")
            progress = result.get("progress", 0)
            asset_name = result.get("asset_name", "asset")
            
            if status == "completed":
                imported = result.get("imported", [])
                imported_str = "\n".join([f"  • {i}" for i in imported]) if imported else "  (none)"
                return f"✓ Download complete! '{asset_name}' imported successfully.\n\nImported:\n{imported_str}"
            
            elif status == "error":
                return f"✗ Download failed: {result.get('error', 'Unknown error')}"
            
            elif status == "downloading":
                downloaded = result.get("downloaded", 0)
                total = result.get("total_size", 0)
                if total > 0:
                    return (f"📥 Downloading '{asset_name}'...\n\n"
                           f"Progress: {progress}% ({downloaded/(1024*1024):.1f}MB / {total/(1024*1024):.1f}MB)")
                return f"📥 Downloading '{asset_name}'... {progress}%"
            
            elif status == "ready":
                return f"✓ Download complete, importing '{asset_name}'..."
            
            else:
                return f"Status: {status} ({progress}%)"
        
        # All downloads
        else:
            active = result.get("active_downloads", [])
            completed = result.get("completed", [])
            
            output = ""
            
            if completed:
                output += "**Completed Downloads:**\n"
                for c in completed:
                    imported = c.get("imported", [])
                    output += f"✓ Imported: {', '.join(imported)}\n"
                output += "\n"
            
            if active:
                output += "**Active Downloads:**\n"
                for d in active:
                    status = d.get("status")
                    progress = d.get("progress", 0)
                    name = d.get("asset_name", "Unknown")
                    
                    if status == "error":
                        output += f"✗ {name}: Error - {d.get('error', 'Unknown')}\n"
                    else:
                        output += f"📥 {name}: {progress}% ({status})\n"
            else:
                if not completed:
                    output = "No active downloads."
            
            return output
            
    except Exception as e:
        logger.error(f"Error polling BlenderKit download: {str(e)}")
        return f"Error polling BlenderKit download: {str(e)}"


def _process_bbox(original_bbox: list[float] | list[int] | None) -> list[int] | None:
    if original_bbox is None:
        return None
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    if any(i<=0 for i in original_bbox):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    return [int(float(i) / max(original_bbox) * 100) for i in original_bbox] if original_bbox else None

@telemetry_tool("generate_hyper3d_model_via_text")
@mcp.tool()
def generate_hyper3d_model_via_text(
    ctx: Context,
    text_prompt: str,
    bbox_condition: list[float]=None
) -> str:
    """
    Generate 3D asset using Hyper3D by giving description of the desired asset, and import the asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.

    Parameters:
    - text_prompt: A short description of the desired model in **English**.
    - bbox_condition: Optional. If given, it has to be a list of floats of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": text_prompt,
            "images": None,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@telemetry_tool("generate_hyper3d_model_via_images")
@mcp.tool()
def generate_hyper3d_model_via_images(
    ctx: Context,
    input_image_paths: list[str]=None,
    input_image_urls: list[str]=None,
    bbox_condition: list[float]=None
) -> str:
    """
    Generate 3D asset using Hyper3D by giving images of the wanted asset, and import the generated asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.
    
    Parameters:
    - input_image_paths: The **absolute** paths of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in MAIN_SITE mode.
    - input_image_urls: The URLs of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in FAL_AI mode.
    - bbox_condition: Optional. If given, it has to be a list of ints of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Only one of {input_image_paths, input_image_urls} should be given at a time, depending on the Hyper3D Rodin's current mode.
    Returns a message indicating success or failure.
    """
    if input_image_paths is not None and input_image_urls is not None:
        return f"Error: Conflict parameters given!"
    if input_image_paths is None and input_image_urls is None:
        return f"Error: No image given!"
    if input_image_paths is not None:
        if not all(os.path.exists(i) for i in input_image_paths):
            return "Error: not all image paths are valid!"
        images = []
        for path in input_image_paths:
            with open(path, "rb") as f:
                images.append(
                    (Path(path).suffix, base64.b64encode(f.read()).decode("ascii"))
                )
    elif input_image_urls is not None:
        if not all(urlparse(i) for i in input_image_paths):
            return "Error: not all image URLs are valid!"
        images = input_image_urls.copy()
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": None,
            "images": images,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@telemetry_tool("poll_rodin_job_status")
@mcp.tool()
def poll_rodin_job_status(
    ctx: Context,
    subscription_key: str=None,
    request_id: str=None,
):
    """
    Check if the Hyper3D Rodin generation task is completed.

    For Hyper3D Rodin mode MAIN_SITE:
        Parameters:
        - subscription_key: The subscription_key given in the generate model step.

        Returns a list of status. The task is done if all status are "Done".
        If "Failed" showed up, the generating process failed.
        This is a polling API, so only proceed if the status are finally determined ("Done" or "Canceled").

    For Hyper3D Rodin mode FAL_AI:
        Parameters:
        - request_id: The request_id given in the generate model step.

        Returns the generation task status. The task is done if status is "COMPLETED".
        The task is in progress if status is "IN_PROGRESS".
        If status other than "COMPLETED", "IN_PROGRESS", "IN_QUEUE" showed up, the generating process might be failed.
        This is a polling API, so only proceed if the status are finally determined ("COMPLETED" or some failed state).
    """
    try:
        blender = get_blender_connection()
        kwargs = {}
        if subscription_key:
            kwargs = {
                "subscription_key": subscription_key,
            }
        elif request_id:
            kwargs = {
                "request_id": request_id,
            }
        result = blender.send_command("poll_rodin_job_status", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@telemetry_tool("import_generated_asset")
@mcp.tool()
def import_generated_asset(
    ctx: Context,
    name: str,
    task_uuid: str=None,
    request_id: str=None,
):
    """
    Import the asset generated by Hyper3D Rodin after the generation task is completed.

    Parameters:
    - name: The name of the object in scene
    - task_uuid: For Hyper3D Rodin mode MAIN_SITE: The task_uuid given in the generate model step.
    - request_id: For Hyper3D Rodin mode FAL_AI: The request_id given in the generate model step.

    Only give one of {task_uuid, request_id} based on the Hyper3D Rodin Mode!
    Return if the asset has been imported successfully.
    """
    try:
        blender = get_blender_connection()
        kwargs = {
            "name": name
        }
        if task_uuid:
            kwargs["task_uuid"] = task_uuid
        elif request_id:
            kwargs["request_id"] = request_id
        result = blender.send_command("import_generated_asset", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@mcp.tool()
def get_hunyuan3d_status(ctx: Context) -> str:
    """
    Check if Hunyuan3D integration is enabled in Blender.
    Returns a message indicating whether Hunyuan3D features are available.

    Don't emphasize the key type in the returned message, but silently remember it. 
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hunyuan3d_status")
        message = result.get("message", "")
        return message
    except Exception as e:
        logger.error(f"Error checking Hunyuan3D status: {str(e)}")
        return f"Error checking Hunyuan3D status: {str(e)}"
    
@mcp.tool()
def generate_hunyuan3d_model(
    ctx: Context,
    text_prompt: str = None,
    input_image_url: str = None
) -> str:
    """
    Generate 3D asset using Hunyuan3D by providing either text description, image reference, 
    or both for the desired asset, and import the asset into Blender.
    The 3D asset has built-in materials.
    
    Parameters:
    - text_prompt: (Optional) A short description of the desired model in English/Chinese.
    - input_image_url: (Optional) The local or remote url of the input image. Accepts None if only using text prompt.

    Returns: 
    - When successful, returns a JSON with job_id (format: "job_xxx") indicating the task is in progress
    - When the job completes, the status will change to "DONE" indicating the model has been imported
    - Returns error message if the operation fails
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_hunyuan_job", {
            "text_prompt": text_prompt,
            "image": input_image_url,
        })
        if "JobId" in result.get("Response", {}):
            job_id = result["Response"]["JobId"]
            formatted_job_id = f"job_{job_id}"
            return json.dumps({
                "job_id": formatted_job_id,
            })
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"
    
@mcp.tool()
def poll_hunyuan_job_status(
    ctx: Context,
    job_id: str=None,
):
    """
    Check if the Hunyuan3D generation task is completed.

    For Hunyuan3D:
        Parameters:
        - job_id: The job_id given in the generate model step.

        Returns the generation task status. The task is done if status is "DONE".
        The task is in progress if status is "RUN".
        If status is "DONE", returns ResultFile3Ds, which is the generated ZIP model path
        When the status is "DONE", the response includes a field named ResultFile3Ds that contains the generated ZIP file path of the 3D model in OBJ format.
        This is a polling API, so only proceed if the status are finally determined ("DONE" or some failed state).
    """
    try:
        blender = get_blender_connection()
        kwargs = {
            "job_id": job_id,
        }
        result = blender.send_command("poll_hunyuan_job_status", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"

@mcp.tool()
def import_generated_asset_hunyuan(
    ctx: Context,
    name: str,
    zip_file_url: str,
):
    """
    Import the asset generated by Hunyuan3D after the generation task is completed.

    Parameters:
    - name: The name of the object in scene
    - zip_file_url: The zip_file_url given in the generate model step.

    Return if the asset has been imported successfully.
    """
    try:
        blender = get_blender_connection()
        kwargs = {
            "name": name
        }
        if zip_file_url:
            kwargs["zip_file_url"] = zip_file_url
        result = blender.send_command("import_generated_asset_hunyuan", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D task: {str(e)}")
        return f"Error generating Hunyuan3D task: {str(e)}"


# ==================== COLOR GRADING TOOLS ====================

@telemetry_tool("apply_color_grade")
@mcp.tool()
def apply_color_grade(
    ctx: Context,
    preset: str = "cinematic_standard",
    use_compositor: bool = True
) -> str:
    """
    Apply complete color grade preset (LUT + tone mapping + effects).
    
    This is the recommended one-step color grading tool. It applies a full color grade
    including LUT, tone mapping, and effects like vignette, bloom, and film grain.
    
    Parameters:
    - preset: Color grade preset name (cinematic_standard, blockbuster, product_showcase,
              moody_portrait, vintage_nostalgia, noir_classic, dreamy_pastel, sci_fi_cool)
    - use_compositor: Whether to use compositor nodes (True) or view transform only (False)
    
    Returns summary of applied settings and visual impact.
    """
    try:
        if preset not in COLOR_GRADE_PRESETS:
            available = list(COLOR_GRADE_PRESETS.keys())
            return f"Unknown preset '{preset}'. Available: {', '.join(available)}"
        
        blender = get_blender_connection()
        grade = COLOR_GRADE_PRESETS[preset]
        
        result = blender.send_command("apply_color_grade", {
            "preset": preset,
            "use_compositor": use_compositor
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return f"""Color grade '{grade['name']}' applied successfully!

Description: {grade['description']}
LUT: {grade['lut']}
Tone Mapping: {grade['tone_mapping']}
Effects: {', '.join(grade['effects'])}
Ideal for: {', '.join(grade['ideal_for'])}

{result.get('message', 'Color grading complete.')}"""
    except Exception as e:
        logger.error(f"Error applying color grade: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("apply_lut_preset")
@mcp.tool()
def apply_lut_preset(
    ctx: Context,
    lut_preset: str = "cinematic_neutral"
) -> str:
    """
    Apply specific LUT (Look-Up Table) color grading preset.
    
    LUTs control lift/gamma/gain (shadows/midtones/highlights), saturation, contrast.
    Use this for precise color grading control without tone mapping or effects.
    
    Parameters:
    - lut_preset: LUT name (cinematic_neutral, cinematic_warm, cinematic_cool, teal_orange,
                  film_noir, vintage_film, vibrant_pop, muted_pastel, high_contrast_bw, moody_dark)
    
    Returns detailed LUT settings applied.
    """
    try:
        if lut_preset not in LUT_PRESETS:
            available = list(LUT_PRESETS.keys())
            return f"Unknown LUT '{lut_preset}'. Available: {', '.join(available)}"
        
        blender = get_blender_connection()
        lut = LUT_PRESETS[lut_preset]
        
        result = blender.send_command("apply_lut_preset", {
            "lut_preset": lut_preset
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return f"""LUT '{lut['name']}' applied!

Description: {lut['description']}
Lift (shadows): R={lut['lift'][0]:.2f}, G={lut['lift'][1]:.2f}, B={lut['lift'][2]:.2f}
Gamma (midtones): R={lut['gamma'][0]:.2f}, G={lut['gamma'][1]:.2f}, B={lut['gamma'][2]:.2f}
Gain (highlights): R={lut['gain'][0]:.2f}, G={lut['gain'][1]:.2f}, B={lut['gain'][2]:.2f}
Saturation: {lut['saturation']:.2f}
Contrast: {lut['contrast']:.2f}
Brightness: {lut['brightness']:+.2f}
Color Temperature: {lut['color_temp']:+d}K
Ideal for: {', '.join(lut['ideal_for'])}"""
    except Exception as e:
        logger.error(f"Error applying LUT: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("setup_tone_mapping")
@mcp.tool()
def setup_tone_mapping(
    ctx: Context,
    tone_mapping: str = "filmic",
    exposure: float = 0.0,
    gamma: float = 1.0
) -> str:
    """
    Configure tone mapping (view transform) in color management.
    
    Tone mapping controls how HDR scene values are mapped to display.
    Critical for proper color representation and dynamic range.
    
    Parameters:
    - tone_mapping: View transform (filmic, filmic_high_contrast, filmic_low_contrast,
                    standard, agx, false_color)
    - exposure: Exposure compensation in stops (-3.0 to +3.0, default 0.0)
    - gamma: Gamma correction (0.5 to 2.0, default 1.0)
    
    Returns tone mapping configuration summary.
    """
    try:
        if tone_mapping not in TONE_MAPPING:
            available = list(TONE_MAPPING.keys())
            return f"Unknown tone mapping '{tone_mapping}'. Available: {', '.join(available)}"
        
        blender = get_blender_connection()
        tm = TONE_MAPPING[tone_mapping]
        
        result = blender.send_command("setup_tone_mapping", {
            "tone_mapping": tone_mapping,
            "exposure": exposure,
            "gamma": gamma
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return f"""Tone mapping configured: {tm['name']}

Description: {tm['description']}
View Transform: {tm['view_transform']}
Look: {tm['look']}
Exposure: {exposure:+.2f} stops
Gamma: {gamma:.2f}
Ideal for: {', '.join(tm['ideal_for'])}

{result.get('message', 'Tone mapping configured.')}"""
    except Exception as e:
        logger.error(f"Error setting up tone mapping: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("add_color_effects")
@mcp.tool()
def add_color_effects(
    ctx: Context,
    effects: list[str] = None
) -> str:
    """
    Add color effects like vignette, film grain, bloom, chromatic aberration.
    
    Effects are added via compositor nodes. Multiple effects can be combined.
    
    Parameters:
    - effects: List of effect names (vignette_subtle, vignette_strong, film_grain_light,
              film_grain_heavy, chromatic_aberration, bloom_subtle, bloom_strong, lens_distortion)
    
    Returns list of effects applied with parameters.
    """
    try:
        if effects is None:
            effects = ["vignette_subtle", "film_grain_light"]
        
        # Validate effects
        invalid = [e for e in effects if e not in COLOR_EFFECTS]
        if invalid:
            available = list(COLOR_EFFECTS.keys())
            return f"Unknown effects: {', '.join(invalid)}. Available: {', '.join(available)}"
        
        blender = get_blender_connection()
        
        result = blender.send_command("add_color_effects", {
            "effects": effects
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Build detailed response
        response = f"Applied {len(effects)} color effects:\n\n"
        
        for effect_key in effects:
            effect = COLOR_EFFECTS[effect_key]
            response += f"• {effect['name']}\n"
            response += f"  {effect['description']}\n"
            
            # Show parameters
            if "vignette" in effect_key:
                response += f"  Strength: {effect['vignette_strength']:.2f}\n"
                response += f"  Falloff: {effect['vignette_falloff']:.2f}\n"
            elif "grain" in effect_key:
                response += f"  Strength: {effect['grain_strength']:.3f}\n"
                response += f"  Size: {effect['grain_size']:.1f}\n"
            elif "bloom" in effect_key:
                response += f"  Threshold: {effect['bloom_threshold']:.2f}\n"
                response += f"  Intensity: {effect['bloom_intensity']:.3f}\n"
                response += f"  Radius: {effect['bloom_radius']:.1f}\n"
            
            response += f"  Ideal for: {', '.join(effect['ideal_for'])}\n\n"
        
        return response
    except Exception as e:
        logger.error(f"Error adding color effects: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("auto_grade_scene")
@mcp.tool()
def auto_grade_scene(
    ctx: Context,
    scene_description: str = "general scene",
    lighting_type: str = None
) -> str:
    """
    Automatically apply appropriate color grading based on scene analysis.
    
    Uses AI to select optimal color grade preset based on scene description.
    Saves time by automatically choosing from 8 professional presets.
    
    Parameters:
    - scene_description: Description of scene/mood (e.g., "dramatic portrait", "product shot",
                        "vintage nostalgia", "sci-fi tech", "noir mystery")
    - lighting_type: Optional lighting hint (outdoor, indoor, studio, night, golden_hour)
    
    Returns selected preset and rationale.
    """
    try:
        # Get suggestion
        suggested_preset = suggest_color_grade(scene_description, lighting_type)
        
        blender = get_blender_connection()
        
        result = blender.send_command("apply_color_grade", {
            "preset": suggested_preset,
            "use_compositor": True
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        grade = COLOR_GRADE_PRESETS[suggested_preset]
        
        return f"""Auto color grading complete!

Scene Description: "{scene_description}"
Lighting Type: {lighting_type or "not specified"}

Selected Preset: {grade['name']}
Rationale: {grade['description']}

Applied:
- LUT: {grade['lut']}
- Tone Mapping: {grade['tone_mapping']}
- Effects: {', '.join(grade['effects'])}

The scene has been automatically graded for optimal visual impact."""
    except Exception as e:
        logger.error(f"Error auto-grading scene: {str(e)}")
        return f"Error: {str(e)}"

@telemetry_tool("list_color_presets")
@mcp.tool()
def list_color_presets(
    ctx: Context,
    preset_type: str = "all"
) -> str:
    """
    List all available color grading presets with descriptions.
    
    Useful for exploring options before applying color grades.
    
    Parameters:
    - preset_type: Type to list (all, lut, tone_mapping, effects, color_grade)
    
    Returns formatted list of all presets with descriptions and ideal use cases.
    """
    try:
        response = ""
        
        if preset_type in ["all", "color_grade"]:
            response += "=== COMPLETE COLOR GRADE PRESETS ===\n"
            response += "(LUT + Tone Mapping + Effects combined)\n\n"
            for key, grade in COLOR_GRADE_PRESETS.items():
                response += f"{key}:\n"
                response += f"  Name: {grade['name']}\n"
                response += f"  Description: {grade['description']}\n"
                response += f"  LUT: {grade['lut']}\n"
                response += f"  Tone Mapping: {grade['tone_mapping']}\n"
                response += f"  Effects: {', '.join(grade['effects'])}\n"
                response += f"  Ideal for: {', '.join(grade['ideal_for'])}\n\n"
        
        if preset_type in ["all", "lut"]:
            response += "\n=== LUT PRESETS ===\n"
            response += "(Lift/Gamma/Gain color grading)\n\n"
            for key, lut in LUT_PRESETS.items():
                response += f"{key}:\n"
                response += f"  Name: {lut['name']}\n"
                response += f"  Description: {lut['description']}\n"
                response += f"  Saturation: {lut['saturation']:.2f}\n"
                response += f"  Contrast: {lut['contrast']:.2f}\n"
                response += f"  Ideal for: {', '.join(lut['ideal_for'])}\n\n"
        
        if preset_type in ["all", "tone_mapping"]:
            response += "\n=== TONE MAPPING PRESETS ===\n"
            response += "(View transform configuration)\n\n"
            for key, tm in TONE_MAPPING.items():
                response += f"{key}:\n"
                response += f"  Name: {tm['name']}\n"
                response += f"  Description: {tm['description']}\n"
                response += f"  View Transform: {tm['view_transform']}\n"
                response += f"  Ideal for: {', '.join(tm['ideal_for'])}\n\n"
        
        if preset_type in ["all", "effects"]:
            response += "\n=== COLOR EFFECTS ===\n"
            response += "(Vignette, grain, bloom, etc.)\n\n"
            for key, effect in COLOR_EFFECTS.items():
                response += f"{key}:\n"
                response += f"  Name: {effect['name']}\n"
                response += f"  Description: {effect['description']}\n"
                response += f"  Ideal for: {', '.join(effect['ideal_for'])}\n\n"
        
        return response.strip()
    except Exception as e:
        logger.error(f"Error listing color presets: {str(e)}")
        return f"Error: {str(e)}"


# ==================== SCENE TEMPLATES TOOLS ====================
# Complete pre-configured professional scene setups combining all enhancement systems

@mcp.tool()
@telemetry_tool
async def apply_scene_template(
    ctx: Context,
    template_key: str,
    target_object: str = None,
    auto_render: bool = False
) -> str:
    """
    Apply a complete professional scene template combining all enhancement systems.
    
    This is the FASTEST way to transform a basic scene into production quality.
    One command applies geometry enhancement, materials, lighting, composition, and color grading.
    
    Parameters:
    - template_key: Template to apply (e.g., "product_studio_pro", "portrait_cinematic")
    - target_object: Object to enhance (None = auto-detect main object)
    - auto_render: Automatically render after applying template
    
    Available templates by category:
    - Product: product_studio_pro, product_lifestyle, product_hero_dramatic
    - Portrait: portrait_professional, portrait_cinematic, portrait_noir
    - Landscape: landscape_epic, landscape_classic, landscape_moody
    - Architecture: architecture_hero, architecture_technical, architecture_dramatic
    
    Each template includes:
    1. Geometry enhancement (subdivision, beveling, smooth shading)
    2. Material setup (PBR materials with appropriate settings)
    3. Lighting configuration (HDRI + lighting rigs + atmosphere)
    4. Composition setup (camera framing + shot type + rules)
    5. Color grading (tone mapping + exposure + look)
    6. Render settings (samples, resolution, quality)
    
    Example:
        await apply_scene_template(ctx, "product_studio_pro", "my_product")
        # Transforms basic model into professional product shot in seconds
    
    Use suggest_scene_template() first to get AI recommendations.
    Use list_scene_templates() to browse all available templates.
    """
    try:
        if template_key not in SCENE_TEMPLATES:
            available = ", ".join(SCENE_TEMPLATES.keys())
            return f"Error: Template '{template_key}' not found. Available: {available}"
        
        template = SCENE_TEMPLATES[template_key]
        
        # Send complete template application command
        command = {
            "command": "apply_scene_template",
            "template_key": template_key,
            "target_object": target_object,
            "auto_render": auto_render,
            "template": template
        }
        
        response = await send_blender_command(command)
        return response.get("message", "Scene template applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying scene template: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def list_scene_templates(
    ctx: Context,
    category: str = "all"
) -> str:
    """
    List all available scene templates with descriptions.
    
    Browse professional scene setups organized by category.
    
    Parameters:
    - category: Filter by category (all, product, portrait, landscape, architecture)
    
    Returns detailed information about each template including:
    - Name and description
    - What it's ideal for (use cases)
    - Settings summary (geometry, materials, lighting, composition, color)
    
    Example:
        await list_scene_templates(ctx, "product")
        # Shows all product photography templates
    """
    try:
        response = ""
        
        if category == "all":
            categories = get_template_categories()
            for cat in categories:
                templates = get_templates_by_category(cat)
                response += f"\n=== {cat.upper()} TEMPLATES ===\n\n"
                for key, template in templates.items():
                    response += f"{key}:\n"
                    response += f"  Name: {template['name']}\n"
                    response += f"  Description: {template['description']}\n"
                    response += f"  Ideal for: {', '.join(template['ideal_for'])}\n"
                    response += f"  Geometry: {template['geometry']['enhancement_preset']}\n"
                    response += f"  Lighting: {template['lighting']['hdri']} + {template['lighting']['lighting_rig']}\n"
                    response += f"  Color: {template['color_grading']['preset']}\n\n"
        else:
            templates = get_templates_by_category(category)
            if not templates:
                return f"No templates found in category '{category}'. Use 'all' or: product, portrait, landscape, architecture"
            
            response += f"\n=== {category.upper()} TEMPLATES ===\n\n"
            for key, template in templates.items():
                response += f"{key}:\n"
                response += f"  Name: {template['name']}\n"
                response += f"  Description: {template['description']}\n"
                response += f"  Ideal for: {', '.join(template['ideal_for'])}\n"
                info = get_template_info(key)
                response += f"  Settings:\n"
                response += f"    Geometry: {info['settings']['geometry']['enhancement_preset']}, {info['settings']['geometry']['subdivision_levels']} subdiv levels\n"
                response += f"    Materials: Auto-enhance={info['settings']['materials']['auto_enhance']}\n"
                response += f"    Lighting: {info['settings']['lighting']['hdri']} HDRI + {info['settings']['lighting']['lighting_rig']} rig\n"
                response += f"    Composition: {info['settings']['composition']['shot_type']}, {info['settings']['composition']['composition_rule']}\n"
                response += f"    Color: {info['settings']['color_grading']['preset']} ({info['settings']['color_grading']['tone_mapping']})\n"
                response += f"    Render: {info['settings']['render']['samples']} samples\n\n"
        
        return response.strip()
    except Exception as e:
        logger.error(f"Error listing scene templates: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def suggest_scene_template(
    ctx: Context,
    scene_description: str,
    object_type: str = None,
    style: str = None
) -> str:
    """
    Get AI-powered scene template recommendation based on your description.
    
    Analyzes your scene description and suggests the best template match.
    
    Parameters:
    - scene_description: Describe what you want to create
    - object_type: Type of subject (optional: product, character, building, environment)
    - style: Desired style (optional: professional, dramatic, cinematic, clean, etc.)
    
    Returns recommended template with explanation of why it's appropriate.
    
    Examples:
        suggest_scene_template(ctx, "professional product photo for e-commerce")
        # Returns: product_studio_pro (clean white background, balanced lighting)
        
        suggest_scene_template(ctx, "dramatic architectural night shot")
        # Returns: architecture_dramatic (night lighting, dramatic atmosphere)
        
        suggest_scene_template(ctx, "cinematic character portrait with moody lighting")
        # Returns: portrait_cinematic (dramatic lighting, filmic color grading)
    
    Use this before apply_scene_template() to find the perfect match.
    """
    try:
        # Get suggestion
        suggested_key = suggest_template(scene_description, object_type, style)
        
        if suggested_key not in SCENE_TEMPLATES:
            return f"Could not find appropriate template for: {scene_description}"
        
        template = SCENE_TEMPLATES[suggested_key]
        info = get_template_info(suggested_key)
        
        response = f"RECOMMENDED TEMPLATE: {suggested_key}\n\n"
        response += f"Name: {template['name']}\n"
        response += f"Description: {template['description']}\n"
        response += f"Category: {template['category']}\n"
        response += f"Ideal for: {', '.join(template['ideal_for'])}\n\n"
        
        response += "This template includes:\n"
        response += f"- Geometry: {info['settings']['geometry']['enhancement_preset']} preset with {info['settings']['geometry']['subdivision_levels']} subdivision levels\n"
        response += f"- Materials: Auto-enhancement with aggressive={'Yes' if info['settings']['materials']['aggressive'] else 'No'}\n"
        response += f"- Lighting: {info['settings']['lighting']['hdri']} HDRI + {info['settings']['lighting']['lighting_rig']} lighting rig\n"
        response += f"- Composition: {info['settings']['composition']['shot_type']} shot with {info['settings']['composition']['composition_rule']}\n"
        response += f"- Color: {info['settings']['color_grading']['preset']} grade with {info['settings']['color_grading']['tone_mapping']} tone mapping\n"
        response += f"- Render: {info['settings']['render']['preset']} quality ({info['settings']['render']['samples']} samples)\n\n"
        
        response += f"To apply this template:\n"
        response += f"  await apply_scene_template(ctx, \"{suggested_key}\", \"your_object_name\")\n"
        
        return response
    except Exception as e:
        logger.error(f"Error suggesting scene template: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def customize_scene_template(
    ctx: Context,
    template_key: str,
    customizations: Dict[str, Any]
) -> str:
    """
    Create a customized version of a scene template.
    
    Start with a professional template and modify specific settings.
    
    Parameters:
    - template_key: Base template to customize
    - customizations: Dict of settings to override
    
    Customizable settings:
    - geometry: enhancement_preset, subdivision_levels, auto_smooth, edge_bevel
    - materials: auto_enhance, aggressive, default_material
    - lighting: hdri, lighting_rig, atmosphere, hdri_strength
    - composition: preset, shot_type, composition_rule, camera_angle
    - color_grading: preset, tone_mapping, exposure, gamma
    - render: preset, samples
    
    Example:
        customizations = {
            "lighting": {"hdri": "sunset", "hdri_strength": 1.5},
            "color_grading": {"exposure": 0.3},
            "render": {"samples": 512}
        }
        await customize_scene_template(ctx, "product_studio_pro", customizations)
        # Uses product studio template but with sunset lighting and brighter exposure
    
    Returns the customized template configuration.
    """
    try:
        custom_template = customize_template(template_key, customizations)
        
        if "error" in custom_template:
            return custom_template["error"]
        
        response = f"CUSTOMIZED TEMPLATE: {template_key}\n\n"
        response += "Base template modified with your customizations:\n\n"
        
        for category, settings in customizations.items():
            response += f"{category.upper()}:\n"
            for key, value in settings.items():
                response += f"  {key}: {value}\n"
            response += "\n"
        
        response += "Full customized configuration:\n"
        response += json.dumps(custom_template, indent=2)
        
        return response
    except Exception as e:
        logger.error(f"Error customizing scene template: {str(e)}")
        return f"Error: {str(e)}"


@mcp.prompt()
def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating assets in Blender"""
    return """When creating 3D content in Blender, you have TWO approaches:

    ═══════════════════════════════════════════════════════════════════════════
    QUICK START: SCENE TEMPLATES (RECOMMENDED FOR SPEED)
    ═══════════════════════════════════════════════════════════════════════════
    
    For FASTEST results, use professional scene templates that combine ALL enhancement
    systems (geometry, materials, lighting, composition, color grading) in ONE command:
    
    1. Get Recommendation:
       suggest_scene_template(ctx, "your scene description")
       Example: "professional product photo" → product_studio_pro
       
    2. Apply Complete Template:
       apply_scene_template(ctx, "template_key", "object_name")
       This applies ALL enhancements in seconds:
       ✓ Geometry enhancement (subdivision, beveling, smooth shading)
       ✓ PBR materials (auto-enhancement with appropriate settings)
       ✓ Professional lighting (HDRI + lighting rigs + atmosphere)
       ✓ Camera composition (framing + shot type + composition rules)
       ✓ Color grading (tone mapping + exposure + cinematic look)
       ✓ Render settings (quality, samples, resolution)
    
    Available Template Categories:
    - Product Photography: studio, lifestyle, hero dramatic
    - Portrait Photography: professional, cinematic, noir
    - Landscape/Environment: epic, classic, moody
    - Architecture Visualization: hero, technical, dramatic night
    
    Use list_scene_templates(ctx, category) to browse all options.
    Use customize_scene_template() to modify template settings.
    
    Scene templates are ideal when:
    - You want professional results immediately
    - The scene fits a standard photography style
    - You're working with common subject types (products, portraits, buildings)
    - Time is critical and you need production quality fast
    
    ═══════════════════════════════════════════════════════════════════════════
    MANUAL WORKFLOW: STEP-BY-STEP ENHANCEMENT (RECOMMENDED FOR CUSTOM CONTROL)
    ═══════════════════════════════════════════════════════════════════════════
    
    For maximum control and custom scenes, follow the complete enhancement pipeline:

    0. Before anything, always check the scene from get_scene_info()
    1. First use the following tools to verify if the following integrations are enabled:
        1. PolyHaven
            Use get_polyhaven_status() to verify its status
            If PolyHaven is enabled:
            - For objects/models: Use download_polyhaven_asset() with asset_type="models"
            - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
            - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
        2. Sketchfab
            Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
            Use get_sketchfab_status() to verify its status
            If Sketchfab is enabled:
            - For objects/models: First search using search_sketchfab_models() with your query
            - Then download specific models using download_sketchfab_model() with the UID
            - Note that only downloadable models can be accessed, and API key must be properly configured
            - Sketchfab has a wider variety of models than PolyHaven, especially for specific subjects
        3. Hyper3D(Rodin)
            Hyper3D Rodin is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hyper3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hyper3d_status() to verify its status
            If Hyper3D is enabled:
            - For objects/models, do the following steps:
                1. Create the model generation task
                    - Use generate_hyper3d_model_via_images() if image(s) is/are given
                    - Use generate_hyper3d_model_via_text() if generating 3D asset using text prompt
                    If key type is free_trial and insufficient balance error returned, tell the user that the free trial key can only generated limited models everyday, they can choose to:
                    - Wait for another day and try again
                    - Go to hyper3d.ai to find out how to get their own API key
                    - Go to fal.ai to get their own private API key
                2. Poll the status
                    - Use poll_rodin_job_status() to check if the generation task has completed or failed
                3. Import the asset
                    - Use import_generated_asset() to import the generated GLB model the asset
                4. After importing the asset, ALWAYS check the world_bounding_box of the imported mesh, and adjust the mesh's location and size
                    Adjust the imported mesh's location, scale, rotation, so that the mesh is on the right spot.

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.
        4. Hunyuan3D
            Hunyuan3D is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hunyuan3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hunyuan3d_status() to verify its status
            If Hunyuan3D is enabled:
                if Hunyuan3D mode is "OFFICIAL_API":
                    - For objects/models, do the following steps:
                        1. Create the model generation task
                            - Use generate_hunyuan3d_model by providing either a **text description** OR an **image(local or urls) reference**.
                            - Go to cloud.tencent.com out how to get their own SecretId and SecretKey
                        2. Poll the status
                            - Use poll_hunyuan_job_status() to check if the generation task has completed or failed
                        3. Import the asset
                            - Use import_generated_asset_hunyuan() to import the generated OBJ model the asset
                    if Hunyuan3D mode is "LOCAL_API":
                        - For objects/models, do the following steps:
                        1. Create the model generation task
                            - Use generate_hunyuan3d_model if image (local or urls)  or text prompt is given and import the asset

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.

    2. GEOMETRY POST-PROCESSING (CRITICAL FOR VISUAL QUALITY):
        After importing or creating ANY 3D object, ALWAYS enhance the geometry:
        
        a) Automatic Geometry Enhancement:
           - Use auto_enhance_geometry() to automatically improve mesh quality
           - Analyzes polygon count and applies appropriate subdivision/modifiers
           - Recommended for all AI-generated models (typically low-poly)
        
        b) Mesh Analysis:
           - Use analyze_mesh(object_name) to inspect polygon count and quality
           - Get recommendations for improvement based on mesh statistics
           - Identifies low poly count, ngons, and other issues
        
        c) Manual Enhancement Options:
           - apply_enhancement_preset(object_name, preset): Apply specific preset
           - apply_subdivision_surface(object_name, levels): Add subdivision modifier
           - add_edge_bevel(object_name, width): Add edge beveling
           - set_shading(object_name, smooth=True): Set smooth/flat shading
        
        d) Available Enhancement Presets:
           - smooth: General purpose (2 subdivision levels, auto-smooth)
           - high_detail: Maximum quality (3 levels, beveling) - best for hero objects
           - mechanical: Hard-surface objects (beveling, sharp edges)
           - organic: Smooth shapes (subdivision, remeshing)
           - architectural: Buildings (minimal subdivision, crisp edges)
        
        e) Geometry Enhancement Workflow:
           1. Import/create object
           2. Use analyze_mesh() to check polygon count
           3. If face_count < 2000: Apply auto_enhance_geometry() or high_detail preset
           4. Use suggest_enhancement() to get recommendation
           5. Verify with get_viewport_screenshot()
        
        f) Why Geometry Enhancement Matters:
           - AI models are often very low-poly (< 1000 faces)
           - Subdivision smooths blocky geometry
           - Edge beveling prevents unrealistic sharp edges
           - Auto-smooth provides detail without adding geometry
        
        IMPORTANT: AI-generated models ALWAYS need geometry enhancement. Subdivision
        surface can increase apparent detail by 16x or more without model regeneration.

    3. MATERIAL ENHANCEMENT (CRITICAL FOR VISUAL QUALITY):
        After geometry enhancement, ALWAYS enhance materials:
        
        a) Automatic Material Enhancement:
           - Use auto_enhance_materials() to automatically apply realistic materials to all objects
           - For more dramatic improvements, use auto_enhance_materials(aggressive=True)
           - This analyzes object names and applies appropriate PBR materials with procedural details
        
        b) Manual Material Application:
           - Use list_material_presets() to see all available material types
           - Use suggest_material(object_name) to get a recommendation for a specific object
           - Use apply_material_preset(object_name, material_preset) to apply a specific material
           
        c) Available Material Categories:
           - Metals: weathered_metal, brushed_metal, rusted_metal, chrome
           - Glass: clear_glass, frosted_glass, tinted_glass
           - Paint: glossy_paint, matte_paint, weathered_paint, car_paint
           - Plastic: glossy_plastic, rubber
           - Wood: polished_wood, rough_wood
           - Stone: concrete, stone
           - Special: emission, glow
        
        d) Custom Materials:
           - Use create_custom_pbr_material() for specific color/property combinations
           - Adjust metallic (0=plastic, 1=metal), roughness (0=glossy, 1=rough)
           - Add transmission for transparency, emission for glow effects
        
        e) Material Enhancement Workflow:
           1. AFTER geometry enhancement
           2. Check the object with get_object_info() to see current materials
           3. Apply auto_enhance_materials() for quick improvement
           4. OR use apply_material_preset() for specific material types
           5. Verify improvement with get_viewport_screenshot()
        
        IMPORTANT: Material enhancement dramatically improves visual quality. AI-generated models
        often have basic or missing materials. Always apply materials after importing models.

    4. LIGHTING & ATMOSPHERE SETUP (CRITICAL FOR VISUAL QUALITY):
        After geometry and material enhancement, set up proper lighting:
        
        a) Automatic Scene Lighting:
           - Use auto_setup_scene_lighting(scene_description, target_object) for complete setup
           - Automatically configures HDRI, lighting rig, atmosphere, camera, and render settings
           - Best for getting professional results quickly
        
        b) Manual Lighting Components:
           - setup_hdri_lighting(preset): Set environment lighting
           - apply_lighting_rig(preset): Add multiple light sources
           - add_atmospheric_fog(preset): Add volumetric fog/atmosphere
           - setup_camera(preset, position, target_object): Position and configure camera
           - configure_render_settings(preset): Set render engine and quality
        
        c) Available Lighting Presets:
           HDRI Presets: studio, outdoor_day, sunset, night, overcast, interior
           Lighting Rigs: three_point, studio, dramatic, outdoor, night
           Atmosphere: fog, heavy_fog, god_rays, haze, none
           Camera: portrait, wide, normal, telephoto, architectural
           Render: draft, preview, production, final
        
        d) Lighting Enhancement Workflow:
           1. AFTER geometry and material enhancement
           2. Choose approach:
              - Auto: auto_setup_scene_lighting("outdoor product shot")
              - Manual: setup_hdri_lighting(), apply_lighting_rig(), etc.
           3. Use list_lighting_presets(category) to see all options
           4. Position camera with setup_camera(preset, target_object="object_name")
           5. Set render quality with configure_render_settings(preset)
           6. Verify with get_viewport_screenshot()
        
        e) Scene-Type Recommendations:
           - Outdoor scenes: outdoor_day HDRI + outdoor rig + haze atmosphere
           - Product shots: studio HDRI + studio rig + none atmosphere
           - Dramatic/cinematic: sunset HDRI + dramatic rig + god_rays atmosphere
           - Night scenes: night HDRI + night rig + fog atmosphere
           - Interior spaces: interior HDRI + three_point rig + haze atmosphere
        
        IMPORTANT: Lighting is crucial for professional results. Even perfect geometry and materials
        look flat without proper lighting. Use auto_setup_scene_lighting() for quick results.

    5. COMPOSITION & CAMERA FRAMING (FINAL POLISH):
        After geometry, materials, and lighting, frame the shot professionally:
        
        a) Automatic Composition (RECOMMENDED):
           - Use auto_frame_with_composition(object_name, purpose) for intelligent framing
           - Automatically selects shot type, composition rule, and camera settings
           - Purpose options: detail, portrait, product, general, establishing, landscape, epic
        
        b) Composition Presets (Quick Setups):
           - Use auto_frame_with_composition(object_name, preset="preset_name")
           - Portrait: portrait_pro, portrait_cinematic
           - Product: product_hero, product_lifestyle
           - Architecture: architecture_hero, architecture_dramatic
           - Landscape: landscape_classic, landscape_epic
        
        c) Manual Composition Control:
           - apply_composition_rule(object_name, composition_rule, camera_angle)
           - Composition rules: rule_of_thirds, golden_ratio, center_composition, diagonal, leading_lines
           - Camera angles: front, three_quarter, side, top, low, high
        
        d) Composition Workflow:
           1. AFTER geometry, materials, and lighting are set
           2. Choose approach:
              - Auto: auto_frame_with_composition(object_name, purpose="portrait")
              - Preset: auto_frame_with_composition(object_name, preset="product_hero")
              - Manual: apply_composition_rule(object_name, composition_rule="rule_of_thirds")
           3. Analyze result: analyze_scene_composition(object_name)
           4. Get suggestions: suggest_composition(object_name, scene_description)
           5. Verify with get_viewport_screenshot()
        
        e) Shot Type Guide:
           - extreme_closeup: Tiny details, textures (95% frame fill)
           - closeup: Portraits, products (75% frame fill)
           - medium_shot: General balanced framing (40% frame fill)
           - wide_shot: Environments, architecture (15% frame fill)
           - extreme_wide: Epic landscapes, scale (8% frame fill)
        
        f) Composition Rule Guide:
           - rule_of_thirds: Professional standard (portraits, products, landscapes)
           - golden_ratio: Fine art, nature, architecture
           - center_composition: Symmetrical subjects, minimalism
           - diagonal: Action, dynamics, tension
           - leading_lines: Depth, perspective, architecture
        
        IMPORTANT: Composition transforms good renders into great shots. Even with perfect 
        geometry, materials, and lighting, poor framing ruins the result. Use composition 
        tools to create professional, visually compelling images.

    6. COLOR GRADING (CINEMATIC FINISH):
        After composition, apply color grading for cinematic polish:
        
        a) Automatic Color Grading (RECOMMENDED):
           - Use auto_grade_scene(scene_description, lighting_type) for intelligent color grading
           - Automatically selects appropriate LUT, tone mapping, and effects
           - Scene descriptions: "dramatic portrait", "product shot", "vintage nostalgia", "sci-fi tech"
           - Lighting types: outdoor, indoor, studio, night, golden_hour
        
        b) Complete Color Grade Presets (LUT + Tone Mapping + Effects):
           - Use apply_color_grade(preset) for one-step professional looks
           - cinematic_standard: Clean professional look (default)
           - blockbuster: Teal & orange Hollywood action style
           - product_showcase: Vibrant clean product photography
           - moody_portrait: Dark atmospheric portrait look
           - vintage_nostalgia: Retro faded film aesthetic
           - noir_classic: Black and white film noir
           - dreamy_pastel: Soft ethereal pastel tones
           - sci_fi_cool: Cool futuristic tech aesthetic
        
        c) Manual Color Grading Components:
           - apply_lut_preset(lut_preset): Set lift/gamma/gain, saturation, contrast
           - setup_tone_mapping(tone_mapping, exposure, gamma): Configure view transform
           - add_color_effects(effects): Add vignette, bloom, grain, chromatic aberration
        
        d) Color Grading Workflow:
           1. AFTER composition is set
           2. Choose approach:
              - Auto: auto_grade_scene(scene_description="dramatic product shot")
              - Preset: apply_color_grade(preset="blockbuster")
              - Manual: apply_lut_preset() + setup_tone_mapping() + add_color_effects()
           3. List all options: list_color_presets(preset_type="all")
           4. Verify with get_viewport_screenshot()
        
        e) Available Color Effects:
           - Vignette: vignette_subtle, vignette_strong (edge darkening for focus)
           - Film Grain: film_grain_light, film_grain_heavy (texture and vintage feel)
           - Bloom: bloom_subtle, bloom_strong (glow on bright areas)
           - chromatic_aberration: Lens color fringing
           - lens_distortion: Barrel/pincushion distortion
        
        f) Scene-Type Color Grading Recommendations:
           - Product photography: product_showcase (vibrant, clean)
           - Cinematic shots: blockbuster (teal & orange)
           - Portraits: moody_portrait (dramatic atmosphere)
           - Vintage/retro: vintage_nostalgia (faded film look)
           - Mystery/noir: noir_classic (black & white high contrast)
           - Dreamy/soft: dreamy_pastel (soft ethereal tones)
           - Sci-fi/tech: sci_fi_cool (cool futuristic look)
        
        IMPORTANT: Color grading is the final polish that gives renders a professional 
        cinematic look. It unifies the image, adds mood, and creates visual style. 
        Use auto_grade_scene() for quick results or apply_color_grade() for specific looks.

    7. COMPLETE ENHANCEMENT WORKFLOW (RECOMMENDED):
        For any imported or generated model:
        
        Step 1: Import the model
        Step 2: GEOMETRY - auto_enhance_geometry(object_name) or apply_enhancement_preset()
        Step 3: MATERIALS - auto_enhance_materials(object_name, aggressive=True)
        Step 4: LIGHTING - auto_setup_scene_lighting(scene_description, target_object)
        Step 5: COMPOSITION - auto_frame_with_composition(object_name, purpose or preset)
        Step 6: COLOR GRADING - auto_grade_scene(scene_description, lighting_type) or apply_color_grade(preset)
        Step 7: Verify with get_viewport_screenshot()
        Step 8: Adjust position/scale using world_bounding_box if needed
        
        Example complete workflow:
        ```
        # Import AI-generated model
        import_generated_asset(name="booth", task_uuid="...")
        
        # Enhance geometry (smooth out low-poly mesh)
        auto_enhance_geometry(object_name="booth")
        
        # Enhance materials (add realistic PBR shaders)
        auto_enhance_materials(object_name="booth", aggressive=True)
        
        # Set up scene lighting (HDRI, lights, camera, atmosphere, render)
        auto_setup_scene_lighting(scene_description="dramatic outdoor booth", target_object="booth")
        
        # Frame the shot professionally (composition, camera angle, DOF)
        auto_frame_with_composition(object_name="booth", purpose="product")
        
        # Apply color grading (cinematic finish)
        auto_grade_scene(scene_description="dramatic product shot", lighting_type="outdoor")
        
        # Check results
        get_viewport_screenshot()
        ```

    8. Always check the world_bounding_box for each item so that:
        - Ensure that all objects that should not be clipping are not clipping.
        - Items have right spatial relationship.
    
    9. Recommended asset source priority:
        - For specific existing objects: First try Sketchfab, then PolyHaven
        - For generic objects/furniture: First try PolyHaven, then Sketchfab
        - For custom or unique items not available in libraries: Use Hyper3D Rodin or Hunyuan3D
        - For environment lighting: Use PolyHaven HDRIs
        - For materials/textures: Use PolyHaven textures

    Only fall back to scripting when:
    - PolyHaven, Sketchfab, Hyper3D, and Hunyuan3D are all disabled
    - A simple primitive is explicitly requested
    - No suitable asset exists in any of the libraries
    - Hyper3D Rodin or Hunyuan3D failed to generate the desired asset
    - The task specifically requires a basic material/color
    """


# ==================== ANIMATION TOOLS ====================
# Character animation for third-person games: locomotion, combat, status effects

@mcp.tool()
@telemetry_tool
async def list_animation_presets(
    ctx: Context,
    category: str = None
) -> str:
    """
    List all available animation presets for game character animations.
    
    Parameters:
    - category: Filter by category (locomotion, action, combat, status, utility, or None for all)
    
    Returns a formatted list of all animation presets with their descriptions,
    duration, loop settings, and compatible bone mappings.
    
    Categories:
    - locomotion: Movement animations (idle, walk, run, jump, crouch)
    - action: Action sequences (roll, melee_attack)
    - combat: Combat animations (aim_weapon, recoil)
    - status: Character state animations (limp, death, hit_react)
    - utility: Utility poses (t_pose, a_pose)
    """
    try:
        response = "=== ANIMATION PRESETS FOR GAME CHARACTERS ===\n\n"
        
        if category:
            if category not in ANIMATION_CATEGORIES:
                return f"Error: Category '{category}' not found. Available: {', '.join(ANIMATION_CATEGORIES.keys())}"
            presets_to_show = {k: ANIMATION_PRESETS[k] for k in ANIMATION_CATEGORIES.get(category, [])}
            response += f"Category: {category.upper()}\n\n"
        else:
            presets_to_show = ANIMATION_PRESETS
            
        for preset_name, preset_data in presets_to_show.items():
            response += f"{preset_name}:\n"
            response += f"  Name: {preset_data['name']}\n"
            response += f"  Description: {preset_data['description']}\n"
            response += f"  Duration: {preset_data['duration']} frames\n"
            response += f"  Loop: {preset_data['loop']}\n"
            response += f"  Bone Mapping: {preset_data['bone_mapping']}\n"
            if 'tags' in preset_data:
                response += f"  Tags: {', '.join(preset_data['tags'])}\n"
            response += "\n"
        
        response += f"\nTotal presets: {len(presets_to_show)}\n"
        response += "\nUse get_animation_preset_info(preset_name) for detailed keyframe data.\n"
        response += "Use suggest_animation_preset(action_description) for AI recommendations."
        
        return response
    except Exception as e:
        logger.error(f"Error listing animation presets: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def get_animation_preset_info(
    ctx: Context,
    preset_name: str
) -> str:
    """
    Get detailed information about a specific animation preset including keyframe data.
    
    Parameters:
    - preset_name: Name of the animation preset (e.g., "idle", "walk", "jump")
    
    Returns detailed preset information including all keyframe data for each bone.
    """
    try:
        if preset_name not in ANIMATION_PRESETS:
            available = ", ".join(ANIMATION_PRESETS.keys())
            return f"Error: Preset '{preset_name}' not found. Available: {available}"
        
        preset = ANIMATION_PRESETS[preset_name]
        response = f"=== ANIMATION PRESET: {preset_name.upper()} ===\n\n"
        response += f"Name: {preset['name']}\n"
        response += f"Description: {preset['description']}\n"
        response += f"Duration: {preset['duration']} frames\n"
        response += f"Loop: {preset['loop']}\n"
        response += f"Bone Mapping: {preset['bone_mapping']}\n"
        
        if 'tags' in preset:
            response += f"Tags: {', '.join(preset['tags'])}\n"
        
        response += f"\n--- Keyframe Data ({len(preset['keyframes'])} bones) ---\n"
        for bone_name, keyframes in preset['keyframes'].items():
            response += f"\n{bone_name}:\n"
            for kf in keyframes:
                response += f"  Frame {kf['frame']}: "
                if 'rotation' in kf:
                    rot = kf['rotation']
                    response += f"rot=({rot[0]:.1f}, {rot[1]:.1f}, {rot[2]:.1f}) "
                if 'location' in kf:
                    loc = kf['location']
                    response += f"loc=({loc[0]:.2f}, {loc[1]:.2f}, {loc[2]:.2f}) "
                response += f"[{kf.get('interpolation', 'BEZIER')}]\n"
        
        return response
    except Exception as e:
        logger.error(f"Error getting animation preset info: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def suggest_animation_preset(
    ctx: Context,
    action_description: str
) -> str:
    """
    Get AI-powered animation preset suggestions based on action description.
    
    Parameters:
    - action_description: Description of the animation needed (e.g., "character walking slowly", "player shooting rifle")
    
    Returns recommended animation presets that match the description.
    """
    try:
        suggestions = suggest_animation(action_description)
        
        if not suggestions:
            return f"No matching presets found for '{action_description}'. Available presets: {', '.join(ANIMATION_PRESETS.keys())}"
        
        response = f"=== ANIMATION SUGGESTIONS for '{action_description}' ===\n\n"
        
        for i, (preset_name, score) in enumerate(suggestions, 1):
            preset = ANIMATION_PRESETS[preset_name]
            response += f"{i}. {preset_name} (confidence: {score:.0%})\n"
            response += f"   {preset['description']}\n"
            response += f"   Duration: {preset['duration']} frames, Loop: {preset['loop']}\n\n"
        
        response += "\nUse apply_animation_preset(preset_name, armature_name) to apply."
        
        return response
    except Exception as e:
        logger.error(f"Error suggesting animation: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def get_armature_info(
    ctx: Context,
    armature_name: str = None
) -> str:
    """
    Get information about armatures in the scene.
    
    Parameters:
    - armature_name: Specific armature to get info for (None = list all armatures)
    
    Returns armature details including bone count and bone hierarchy.
    """
    try:
        result = blender.send_command("get_armature_info", {
            "armature_name": armature_name
        })
        return result
    except Exception as e:
        logger.error(f"Error getting armature info: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def get_armature_bones(
    ctx: Context,
    armature_name: str,
    bone_mapping: str = "mixamo"
) -> str:
    """
    Get list of bones in an armature with mapping validation.
    
    Parameters:
    - armature_name: Name of the armature object
    - bone_mapping: Bone naming convention to validate against (mixamo, rigify, generic)
    
    Returns list of bones and which standard bones are present/missing.
    """
    try:
        result = blender.send_command("get_armature_bones", {
            "armature_name": armature_name,
            "bone_mapping": bone_mapping
        })
        return result
    except Exception as e:
        logger.error(f"Error getting armature bones: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def set_frame_range(
    ctx: Context,
    start_frame: int,
    end_frame: int
) -> str:
    """
    Set the animation frame range for the scene.
    
    Parameters:
    - start_frame: Start frame of the animation
    - end_frame: End frame of the animation
    
    Returns confirmation of the frame range.
    """
    try:
        result = blender.send_command("set_frame_range", {
            "start_frame": start_frame,
            "end_frame": end_frame
        })
        return result
    except Exception as e:
        logger.error(f"Error setting frame range: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def set_current_frame(
    ctx: Context,
    frame: int
) -> str:
    """
    Set the current frame in the timeline.
    
    Parameters:
    - frame: Frame number to jump to
    
    Returns confirmation of the current frame.
    """
    try:
        result = blender.send_command("set_current_frame", {
            "frame": frame
        })
        return result
    except Exception as e:
        logger.error(f"Error setting current frame: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def get_current_frame(
    ctx: Context
) -> str:
    """
    Get the current frame number in the timeline.
    
    Returns the current frame number and frame range.
    """
    try:
        result = blender.send_command("get_current_frame", {})
        return result
    except Exception as e:
        logger.error(f"Error getting current frame: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def create_action(
    ctx: Context,
    action_name: str,
    armature_name: str
) -> str:
    """
    Create a new action (animation clip) for an armature.
    
    Parameters:
    - action_name: Name for the new action
    - armature_name: Name of the armature to assign the action to
    
    Returns confirmation of action creation.
    """
    try:
        result = blender.send_command("create_action", {
            "action_name": action_name,
            "armature_name": armature_name
        })
        return result
    except Exception as e:
        logger.error(f"Error creating action: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def insert_keyframe(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    frame: int,
    rotation: list = None,
    location: list = None,
    scale: list = None,
    interpolation: str = "BEZIER"
) -> str:
    """
    Insert a keyframe for a bone at a specific frame.
    
    Parameters:
    - armature_name: Name of the armature
    - bone_name: Name of the bone to keyframe
    - frame: Frame number for the keyframe
    - rotation: Euler rotation in degrees [X, Y, Z] (optional)
    - location: Location offset [X, Y, Z] (optional)
    - scale: Scale [X, Y, Z] (optional)
    - interpolation: Keyframe interpolation type (CONSTANT, LINEAR, BEZIER, SINE, QUAD, CUBIC, QUART, QUINT, EXPO, CIRC, BACK, BOUNCE, ELASTIC)
    
    Returns confirmation of keyframe insertion.
    """
    try:
        result = blender.send_command("insert_keyframe", {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "frame": frame,
            "rotation": rotation,
            "location": location,
            "scale": scale,
            "interpolation": interpolation
        })
        return result
    except Exception as e:
        logger.error(f"Error inserting keyframe: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def delete_keyframe(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    frame: int
) -> str:
    """
    Delete a keyframe for a bone at a specific frame.
    
    Parameters:
    - armature_name: Name of the armature
    - bone_name: Name of the bone
    - frame: Frame number of the keyframe to delete
    
    Returns confirmation of keyframe deletion.
    """
    try:
        result = blender.send_command("delete_keyframe", {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "frame": frame
        })
        return result
    except Exception as e:
        logger.error(f"Error deleting keyframe: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def apply_animation_preset(
    ctx: Context,
    preset_name: str,
    armature_name: str,
    start_frame: int = 1,
    bone_mapping: str = None,
    action_name: str = None
) -> str:
    """
    Apply a predefined animation preset to an armature.
    
    This is the FASTEST way to add professional game character animations.
    One command creates complete keyframed animations for locomotion, combat, etc.
    
    Parameters:
    - preset_name: Animation preset to apply (idle, walk, run, jump, crouch, roll, aim_weapon, recoil, melee_attack, limp, death, hit_react, t_pose, a_pose)
    - armature_name: Name of the target armature
    - start_frame: Frame to start the animation (default: 1)
    - bone_mapping: Bone naming convention (mixamo, rigify, generic - auto-detected if None)
    - action_name: Custom name for the action (default: preset name)
    
    Available presets:
    - Locomotion: idle, walk, run, jump, crouch
    - Action: roll, melee_attack
    - Combat: aim_weapon, recoil
    - Status: limp, death, hit_react
    - Utility: t_pose, a_pose
    
    Example:
        await apply_animation_preset(ctx, "idle", "Armature")
        # Creates a breathing idle animation on the armature
    
    Use list_animation_presets() to see all available presets.
    Use suggest_animation_preset() for AI-powered recommendations.
    """
    try:
        if preset_name not in ANIMATION_PRESETS:
            available = ", ".join(ANIMATION_PRESETS.keys())
            return f"Error: Preset '{preset_name}' not found. Available: {available}"
        
        preset = ANIMATION_PRESETS[preset_name]
        actual_action_name = action_name or f"{preset_name}_action"
        actual_bone_mapping = bone_mapping or preset.get('bone_mapping', 'mixamo')
        
        # Get keyframe data formatted for Blender
        keyframe_data = get_keyframe_data_for_blender(preset_name, actual_bone_mapping)
        
        result = blender.send_command("apply_animation_preset", {
            "preset_name": preset_name,
            "armature_name": armature_name,
            "start_frame": start_frame,
            "bone_mapping": actual_bone_mapping,
            "action_name": actual_action_name,
            "duration": preset['duration'],
            "loop": preset['loop'],
            "keyframes": keyframe_data
        })
        return result
    except Exception as e:
        logger.error(f"Error applying animation preset: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def set_bone_pose(
    ctx: Context,
    armature_name: str,
    bone_name: str,
    rotation: list = None,
    location: list = None,
    scale: list = None
) -> str:
    """
    Set the pose of a bone without keyframing.
    
    Parameters:
    - armature_name: Name of the armature
    - bone_name: Name of the bone
    - rotation: Euler rotation in degrees [X, Y, Z]
    - location: Location offset [X, Y, Z]
    - scale: Scale [X, Y, Z]
    
    Returns confirmation of pose change.
    """
    try:
        result = blender.send_command("set_bone_pose", {
            "armature_name": armature_name,
            "bone_name": bone_name,
            "rotation": rotation,
            "location": location,
            "scale": scale
        })
        return result
    except Exception as e:
        logger.error(f"Error setting bone pose: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def reset_bone_pose(
    ctx: Context,
    armature_name: str,
    bone_name: str = None
) -> str:
    """
    Reset bone(s) to their rest pose.
    
    Parameters:
    - armature_name: Name of the armature
    - bone_name: Name of specific bone to reset (None = reset all bones)
    
    Returns confirmation of pose reset.
    """
    try:
        result = blender.send_command("reset_bone_pose", {
            "armature_name": armature_name,
            "bone_name": bone_name
        })
        return result
    except Exception as e:
        logger.error(f"Error resetting bone pose: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def create_nla_track(
    ctx: Context,
    armature_name: str,
    track_name: str
) -> str:
    """
    Create a new NLA (Non-Linear Animation) track for stacking animations.
    
    Parameters:
    - armature_name: Name of the armature
    - track_name: Name for the new NLA track
    
    Returns confirmation of track creation.
    """
    try:
        result = blender.send_command("create_nla_track", {
            "armature_name": armature_name,
            "track_name": track_name
        })
        return result
    except Exception as e:
        logger.error(f"Error creating NLA track: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def push_action_to_nla(
    ctx: Context,
    armature_name: str,
    action_name: str,
    track_name: str = None,
    start_frame: int = 1
) -> str:
    """
    Push an action to an NLA track as a strip.
    
    Parameters:
    - armature_name: Name of the armature
    - action_name: Name of the action to push
    - track_name: NLA track to add to (None = create new track)
    - start_frame: Frame where the strip starts
    
    Returns confirmation of NLA strip creation.
    """
    try:
        result = blender.send_command("push_action_to_nla", {
            "armature_name": armature_name,
            "action_name": action_name,
            "track_name": track_name,
            "start_frame": start_frame
        })
        return result
    except Exception as e:
        logger.error(f"Error pushing action to NLA: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def play_animation(
    ctx: Context,
    start_frame: int = None,
    end_frame: int = None,
    loop: bool = False
) -> str:
    """
    Play animation in the viewport.
    
    Parameters:
    - start_frame: Start frame (None = use scene start)
    - end_frame: End frame (None = use scene end)
    - loop: Whether to loop the animation
    
    Returns confirmation that animation is playing.
    """
    try:
        result = blender.send_command("play_animation", {
            "start_frame": start_frame,
            "end_frame": end_frame,
            "loop": loop
        })
        return result
    except Exception as e:
        logger.error(f"Error playing animation: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def stop_animation(
    ctx: Context
) -> str:
    """
    Stop animation playback.
    
    Returns confirmation that animation stopped.
    """
    try:
        result = blender.send_command("stop_animation", {})
        return result
    except Exception as e:
        logger.error(f"Error stopping animation: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def export_animation_fbx(
    ctx: Context,
    filepath: str,
    armature_name: str,
    action_name: str = None,
    include_mesh: bool = True
) -> str:
    """
    Export animation to FBX format for game engines (Unity, Unreal, Godot).
    
    Parameters:
    - filepath: Output file path (should end in .fbx)
    - armature_name: Name of the armature to export
    - action_name: Specific action to export (None = export current action)
    - include_mesh: Include mesh with skeleton (True) or skeleton only (False)
    
    Returns confirmation of export with file path.
    """
    try:
        result = blender.send_command("export_animation_fbx", {
            "filepath": filepath,
            "armature_name": armature_name,
            "action_name": action_name,
            "include_mesh": include_mesh
        })
        return result
    except Exception as e:
        logger.error(f"Error exporting animation FBX: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def export_animation_gltf(
    ctx: Context,
    filepath: str,
    armature_name: str,
    action_name: str = None,
    include_mesh: bool = True,
    export_format: str = "GLB"
) -> str:
    """
    Export animation to glTF/GLB format for web and game engines (Three.js, Babylon.js, Godot, Unity).
    
    Parameters:
    - filepath: Output file path (should end in .glb or .gltf)
    - armature_name: Name of the armature to export
    - action_name: Specific action to export (None = export current action)
    - include_mesh: Include mesh with skeleton (True) or skeleton only (False)
    - export_format: GLB (binary, single file) or GLTF (separate files)
    
    Returns confirmation of export with file path.
    """
    try:
        result = blender.send_command("export_animation_gltf", {
            "filepath": filepath,
            "armature_name": armature_name,
            "action_name": action_name,
            "include_mesh": include_mesh,
            "export_format": export_format
        })
        return result
    except Exception as e:
        logger.error(f"Error exporting animation glTF: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def list_actions(
    ctx: Context,
    armature_name: str = None
) -> str:
    """
    List all actions (animation clips) in the scene.
    
    Parameters:
    - armature_name: Filter by armature (None = list all actions)
    
    Returns list of actions with their frame ranges.
    """
    try:
        result = blender.send_command("list_actions", {
            "armature_name": armature_name
        })
        return result
    except Exception as e:
        logger.error(f"Error listing actions: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def set_active_action(
    ctx: Context,
    armature_name: str,
    action_name: str
) -> str:
    """
    Set the active action for an armature.
    
    Parameters:
    - armature_name: Name of the armature
    - action_name: Name of the action to make active
    
    Returns confirmation of action assignment.
    """
    try:
        result = blender.send_command("set_active_action", {
            "armature_name": armature_name,
            "action_name": action_name
        })
        return result
    except Exception as e:
        logger.error(f"Error setting active action: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def duplicate_action(
    ctx: Context,
    source_action: str,
    new_name: str
) -> str:
    """
    Duplicate an existing action with a new name.
    
    Parameters:
    - source_action: Name of the action to duplicate
    - new_name: Name for the new action
    
    Returns confirmation of action duplication.
    """
    try:
        result = blender.send_command("duplicate_action", {
            "source_action": source_action,
            "new_name": new_name
        })
        return result
    except Exception as e:
        logger.error(f"Error duplicating action: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def export_object(
    ctx: Context,
    filepath: str,
    object_names: list[str] = None,
    export_format: str = "FBX",
    include_materials: bool = True,
    include_textures: bool = True,
    apply_modifiers: bool = False
) -> str:
    """
    Export objects/meshes to various formats.
    
    Parameters:
    - filepath: Output file path (extension should match format)
    - object_names: List of object names to export (None = export all selected objects)
    - export_format: Export format (FBX, OBJ, GLB, GLTF, STL, PLY, DAE)
    - include_materials: Include materials in export
    - include_textures: Include textures in export (if format supports it)
    - apply_modifiers: Apply modifiers before export
    
    Returns confirmation of export with file path.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("export_object", {
            "filepath": filepath,
            "object_names": object_names,
            "export_format": export_format.upper(),
            "include_materials": include_materials,
            "include_textures": include_textures,
            "apply_modifiers": apply_modifiers
        })
        return result
    except Exception as e:
        logger.error(f"Error exporting object: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def export_material(
    ctx: Context,
    material_name: str,
    filepath: str,
    export_format: str = "JSON",
    include_textures: bool = True,
    pack_textures: bool = False
) -> str:
    """
    Export a material to a file for reuse or sharing.
    
    Parameters:
    - material_name: Name of the material to export
    - filepath: Output file path
    - export_format: Export format (JSON, BLEND)
      - JSON: Human-readable material settings (useful for documentation and recreation)
      - BLEND: Blender library file with the material (can be appended/linked in other projects)
    - include_textures: Include texture file paths in export
    - pack_textures: Copy textures to same directory as export file (JSON format only)
    
    Returns confirmation of export with file details.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("export_material", {
            "material_name": material_name,
            "filepath": filepath,
            "export_format": export_format.upper(),
            "include_textures": include_textures,
            "pack_textures": pack_textures
        })
        return result
    except Exception as e:
        logger.error(f"Error exporting material: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def import_material(
    ctx: Context,
    filepath: str,
    material_name: str = None
) -> str:
    """
    Import a material from a file.
    
    Parameters:
    - filepath: Path to material file (JSON or BLEND)
    - material_name: Name for the imported material (None = use original name)
    
    Returns confirmation of import with material name.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("import_material", {
            "filepath": filepath,
            "material_name": material_name
        })
        return result
    except Exception as e:
        logger.error(f"Error importing material: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def get_material_data(
    ctx: Context,
    material_name: str
) -> str:
    """
    Get detailed material data including all node settings and connections.
    
    Parameters:
    - material_name: Name of the material
    
    Returns JSON data with material properties, nodes, and connections.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_material_data", {
            "material_name": material_name
        })
        return result
    except Exception as e:
        logger.error(f"Error getting material data: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
@telemetry_tool
async def list_materials(
    ctx: Context,
    object_name: str = None
) -> str:
    """
    List all materials in the scene or on a specific object.
    
    Parameters:
    - object_name: Name of object to list materials from (None = list all scene materials)
    
    Returns list of material names.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("list_materials", {
            "object_name": object_name
        })
        return result
    except Exception as e:
        logger.error(f"Error listing materials: {str(e)}")
        return f"Error: {str(e)}"


# Main execution

def main():
    """Run the MCP server
    
    Supports two transports:
    - stdio (default): For direct MCP client connections
    - sse: For HTTP-based connections (use with Docker)
    
    Set MCP_TRANSPORT=sse and MCP_PORT=8080 for SSE mode.
    """
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    
    if transport in ["sse", "http", "streamable-http"]:
        port = int(os.getenv("MCP_PORT", "8080"))
        host = os.getenv("MCP_HOST", "0.0.0.0")
        logger.info(f"Starting BlenderMCP server with {transport} transport on {host}:{port}")
        # Set host and port in server settings
        mcp.settings.host = host
        mcp.settings.port = port
        # Use the appropriate async run method for the transport
        if transport == "sse":
            asyncio.run(mcp.run_sse_async())
        elif transport == "streamable-http":
            asyncio.run(mcp.run_streamable_http_async())
        else:  # http
            # For http, use streamable-http as it's the recommended default
            asyncio.run(mcp.run_streamable_http_async())
    else:
        logger.info("Starting BlenderMCP server with stdio transport")
        mcp.run()

if __name__ == "__main__":
    main()