# Code created by Siddharth Ahuja: www.github.com/ahujasid © 2025

import re
import bpy
import mathutils
import json
import threading
import socket
import time
import requests
import tempfile
import traceback
import os
import shutil
import zipfile
from bpy.props import IntProperty
import io
from datetime import datetime
import hashlib, hmac, base64
import os.path as osp
from contextlib import redirect_stdout, suppress

bl_info = {
    "name": "Blender MCP",
    "author": "BlenderMCP",
    "version": (1, 2),
    "blender": (3, 0, 0),  # Minimum version; tested up to 5.0
    "location": "View3D > Sidebar > BlenderMCP",
    "description": "Connect Blender to Claude via MCP",
    "category": "Interface",
}

# SECURITY WARNING: Do not commit API keys to version control
# The free trial key has been removed for security reasons.
# Users should obtain their own API key from hyper3d.ai or fal.ai
# and enter it in the BlenderMCP addon settings panel.
RODIN_FREE_TRIAL_KEY = ""  # Removed for security - get your own key from hyper3d.ai

# Add User-Agent as required by Poly Haven API
REQ_HEADERS = requests.utils.default_headers()
REQ_HEADERS.update({"User-Agent": "blender-mcp"})

class BlenderMCPServer:
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None

    def start(self):
        if self.running:
            print("Server is already running")
            return

        self.running = True

        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)

            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"BlenderMCP server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    def stop(self):
        self.running = False

        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        # Wait for thread to finish
        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except:
                pass
            self.server_thread = None

        print("BlenderMCP server stopped")

    def _server_loop(self):
        """Main server loop in a separate thread"""
        print("Server thread started")
        self.socket.settimeout(1.0)  # Timeout to allow for stopping

        while self.running:
            try:
                # Accept new connection
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")

                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # Just check running condition
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {str(e)}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in server loop: {str(e)}")
                if not self.running:
                    break
                time.sleep(0.5)

        print("Server thread stopped")

    def _handle_client(self, client):
        """Handle connected client"""
        print("Client handler started")
        client.settimeout(None)  # No timeout
        buffer = b''

        try:
            while self.running:
                # Receive data
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break

                    buffer += data
                    try:
                        # Try to parse command
                        command = json.loads(buffer.decode('utf-8'))
                        buffer = b''

                        # Execute command in Blender's main thread
                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode('utf-8'))
                                except:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                traceback.print_exc()
                                try:
                                    error_response = {
                                        "status": "error",
                                        "message": str(e)
                                    }
                                    client.sendall(json.dumps(error_response).encode('utf-8'))
                                except:
                                    pass
                            return None

                        # Schedule execution in main thread
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        # Incomplete data, wait for more
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass
            print("Client handler stopped")

    def execute_command(self, command):
        """Execute a command in the main Blender thread"""
        try:
            return self._execute_command_internal(command)

        except Exception as e:
            print(f"Error executing command: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def _execute_command_internal(self, command):
        """Internal command execution with proper context"""
        cmd_type = command.get("type")
        params = command.get("params", {})

        # Add a handler for checking PolyHaven status
        if cmd_type == "get_polyhaven_status":
            return {"status": "success", "result": self.get_polyhaven_status()}

        # Base handlers that are always available
        handlers = {
            "get_scene_info": self.get_scene_info,
            "get_object_info": self.get_object_info,
            "get_viewport_screenshot": self.get_viewport_screenshot,
            "execute_code": self.execute_code,
            "get_polyhaven_status": self.get_polyhaven_status,
            "get_hyper3d_status": self.get_hyper3d_status,
            "get_sketchfab_status": self.get_sketchfab_status,
            "get_hunyuan3d_status": self.get_hunyuan3d_status,
            # Material system handlers (always available)
            "apply_material_preset": self.apply_material_preset,
            "auto_enhance_materials": self.auto_enhance_materials,
            # Post-processing handlers (always available)
            "apply_subdivision_surface": self.apply_subdivision_surface,
            "apply_enhancement_preset": self.apply_enhancement_preset,
            "auto_enhance_geometry": self.auto_enhance_geometry,
            "analyze_mesh": self.analyze_mesh,
            "add_edge_bevel": self.add_edge_bevel,
            "set_shading": self.set_shading,
            # Lighting & atmosphere handlers (always available)
            "setup_hdri_lighting": self.setup_hdri_lighting,
            "apply_lighting_rig": self.apply_lighting_rig,
            "add_atmospheric_fog": self.add_atmospheric_fog,
            "setup_camera": self.setup_camera,
            "configure_render_settings": self.configure_render_settings,
            # Composition system handlers (always available)
            "analyze_composition": self.analyze_composition,
            "apply_composition_rule": self.apply_composition_rule,
            "auto_frame_with_composition": self.auto_frame_with_composition,
            "suggest_composition": self.suggest_composition,
            "calculate_shot_framing": self.calculate_shot_framing,
            # Color grading system handlers (always available)
            "apply_color_grade": self.apply_color_grade,
            "apply_lut_preset": self.apply_lut_preset,
            "setup_tone_mapping": self.setup_tone_mapping,
            "add_color_effects": self.add_color_effects,
            # Scene templates system handlers (always available)
            "apply_scene_template": self.apply_scene_template,
            # Animation system handlers (always available)
            "get_armature_info": self.get_armature_info,
            "get_armature_bones": self.get_armature_bones,
            "set_frame_range": self.set_frame_range,
            "set_current_frame": self.set_current_frame,
            "get_current_frame": self.get_current_frame,
            "create_action": self.create_action,
            "insert_keyframe": self.insert_keyframe,
            "delete_keyframe": self.delete_keyframe,
            "apply_animation_preset": self.apply_animation_preset,
            "set_bone_pose": self.set_bone_pose,
            "reset_bone_pose": self.reset_bone_pose,
            "create_nla_track": self.create_nla_track,
            "push_action_to_nla": self.push_action_to_nla,
            "play_animation": self.play_animation,
            "stop_animation": self.stop_animation,
            "export_animation_fbx": self.export_animation_fbx,
            "export_animation_gltf": self.export_animation_gltf,
            "list_actions": self.list_actions,
            "set_active_action": self.set_active_action,
            "duplicate_action": self.duplicate_action,
        }

        # Add Polyhaven handlers only if enabled
        if bpy.context.scene.blendermcp_use_polyhaven:
            polyhaven_handlers = {
                "get_polyhaven_categories": self.get_polyhaven_categories,
                "search_polyhaven_assets": self.search_polyhaven_assets,
                "download_polyhaven_asset": self.download_polyhaven_asset,
                "set_texture": self.set_texture,
            }
            handlers.update(polyhaven_handlers)

        # Add Hyper3d handlers only if enabled
        if bpy.context.scene.blendermcp_use_hyper3d:
            polyhaven_handlers = {
                "create_rodin_job": self.create_rodin_job,
                "poll_rodin_job_status": self.poll_rodin_job_status,
                "import_generated_asset": self.import_generated_asset,
            }
            handlers.update(polyhaven_handlers)

        # Add Sketchfab handlers only if enabled
        if bpy.context.scene.blendermcp_use_sketchfab:
            sketchfab_handlers = {
                "search_sketchfab_models": self.search_sketchfab_models,
                "download_sketchfab_model": self.download_sketchfab_model,
            }
            handlers.update(sketchfab_handlers)
        
        # Add Hunyuan3d handlers only if enabled
        if bpy.context.scene.blendermcp_use_hunyuan3d:
            hunyuan_handlers = {
                "create_hunyuan_job": self.create_hunyuan_job,
                "poll_hunyuan_job_status": self.poll_hunyuan_job_status,
                "import_generated_asset_hunyuan": self.import_generated_asset_hunyuan
            }
            handlers.update(hunyuan_handlers)

        handler = handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print(f"Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}



    def get_scene_info(self):
        """Get information about the current Blender scene"""
        try:
            print("Getting scene info...")
            # Simplify the scene info to reduce data size
            scene_info = {
                "name": bpy.context.scene.name,
                "object_count": len(bpy.context.scene.objects),
                "objects": [],
                "materials_count": len(bpy.data.materials),
            }

            # Collect minimal object information (limit to first 10 objects)
            for i, obj in enumerate(bpy.context.scene.objects):
                if i >= 10:  # Reduced from 20 to 10
                    break

                obj_info = {
                    "name": obj.name,
                    "type": obj.type,
                    # Only include basic location data
                    "location": [round(float(obj.location.x), 2),
                                round(float(obj.location.y), 2),
                                round(float(obj.location.z), 2)],
                }
                scene_info["objects"].append(obj_info)

            print(f"Scene info collected: {len(scene_info['objects'])} objects")
            return scene_info
        except Exception as e:
            print(f"Error in get_scene_info: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}

    @staticmethod
    def _get_aabb(obj):
        """ Returns the world-space axis-aligned bounding box (AABB) of an object. """
        if obj.type != 'MESH':
            raise TypeError("Object must be a mesh")

        # Get the bounding box corners in local space
        local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]

        # Convert to world coordinates
        world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

        # Compute axis-aligned min/max coordinates
        min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
        max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

        return [
            [*min_corner], [*max_corner]
        ]



    def get_object_info(self, name):
        """Get detailed information about a specific object"""
        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")

        # Basic object info
        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "location": [obj.location.x, obj.location.y, obj.location.z],
            "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
            "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            "visible": obj.visible_get(),
            "materials": [],
        }

        if obj.type == "MESH":
            bounding_box = self._get_aabb(obj)
            obj_info["world_bounding_box"] = bounding_box

        # Add material slots
        for slot in obj.material_slots:
            if slot.material:
                obj_info["materials"].append(slot.material.name)

        # Add mesh data if applicable
        if obj.type == 'MESH' and obj.data:
            mesh = obj.data
            obj_info["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
            }

        return obj_info

    def get_viewport_screenshot(self, max_size=800, filepath=None, format="png"):
        """
        Capture a screenshot of the current 3D viewport and save it to the specified path.

        Parameters:
        - max_size: Maximum size in pixels for the largest dimension of the image
        - filepath: Path where to save the screenshot file
        - format: Image format (png, jpg, etc.)

        Returns success/error status
        """
        try:
            if not filepath:
                return {"error": "No filepath provided"}

            # Find the active 3D viewport
            area = None
            for a in bpy.context.screen.areas:
                if a.type == 'VIEW_3D':
                    area = a
                    break

            if not area:
                return {"error": "No 3D viewport found"}

            # Take screenshot with proper context override
            with bpy.context.temp_override(area=area):
                bpy.ops.screen.screenshot_area(filepath=filepath)

            # Load and resize if needed
            img = bpy.data.images.load(filepath)
            width, height = img.size

            if max(width, height) > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img.scale(new_width, new_height)

                # Set format and save
                img.file_format = format.upper()
                img.save()
                width, height = new_width, new_height

            # Cleanup Blender image data
            bpy.data.images.remove(img)

            return {
                "success": True,
                "width": width,
                "height": height,
                "filepath": filepath
            }

        except Exception as e:
            return {"error": str(e)}

    def execute_code(self, code):
        """Execute arbitrary Blender Python code
        
        SECURITY WARNING: This function executes arbitrary Python code in Blender.
        Only use with trusted code from trusted sources. Malicious code can:
        - Access the file system
        - Modify or delete Blender data
        - Execute system commands
        - Potentially compromise system security
        
        This feature should be used with extreme caution in production environments.
        """
        # SECURITY: This is powerful but potentially dangerous - use with caution
        try:
            # Create a local namespace for execution
            namespace = {"bpy": bpy}

            # Capture stdout during execution, and return it as result
            capture_buffer = io.StringIO()
            with redirect_stdout(capture_buffer):
                exec(code, namespace)

            captured_output = capture_buffer.getvalue()
            return {"executed": True, "result": captured_output}
        except Exception as e:
            raise Exception(f"Code execution error: {str(e)}")

    def apply_material_preset(self, object_name, material_props, preset_name="custom"):
        """Apply a PBR material preset to an object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            # Create or get material
            mat_name = f"{preset_name}_{object_name}"
            mat = bpy.data.materials.get(mat_name)
            if not mat:
                mat = bpy.data.materials.new(name=mat_name)
            
            # Enable nodes
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create output node
            output = nodes.new('ShaderNodeOutputMaterial')
            output.location = (300, 0)
            
            material_type = material_props.get('type', 'pbr')
            
            if material_type == 'glass':
                # Create glass shader
                glass = nodes.new('ShaderNodeBsdfGlass')
                glass.location = (0, 0)
                
                # Set properties
                if 'base_color' in material_props:
                    glass.inputs['Color'].default_value = material_props['base_color']
                if 'roughness' in material_props:
                    glass.inputs['Roughness'].default_value = material_props['roughness']
                if 'ior' in material_props:
                    glass.inputs['IOR'].default_value = material_props['ior']
                
                links.new(glass.outputs['BSDF'], output.inputs['Surface'])
                
            elif material_type == 'emission':
                # Create emission shader
                emission = nodes.new('ShaderNodeEmission')
                emission.location = (0, 0)
                
                if 'base_color' in material_props:
                    emission.inputs['Color'].default_value = material_props['base_color']
                if 'emission_strength' in material_props:
                    emission.inputs['Strength'].default_value = material_props['emission_strength']
                
                links.new(emission.outputs['Emission'], output.inputs['Surface'])
                
            else:  # PBR material
                # Create Principled BSDF
                bsdf = nodes.new('ShaderNodeBsdfPrincipled')
                bsdf.location = (0, 0)
                
                # Set base properties
                if 'base_color' in material_props:
                    bsdf.inputs['Base Color'].default_value = material_props['base_color']
                if 'metallic' in material_props:
                    bsdf.inputs['Metallic'].default_value = material_props['metallic']
                if 'roughness' in material_props:
                    bsdf.inputs['Roughness'].default_value = material_props['roughness']
                if 'specular' in material_props:
                    bsdf.inputs['Specular IOR Level'].default_value = material_props['specular']
                if 'transmission' in material_props:
                    bsdf.inputs['Transmission Weight'].default_value = material_props['transmission']
                if 'emission_strength' in material_props:
                    bsdf.inputs['Emission Strength'].default_value = material_props['emission_strength']
                    if 'base_color' in material_props:
                        bsdf.inputs['Emission Color'].default_value = material_props['base_color']
                if 'clearcoat' in material_props:
                    bsdf.inputs['Coat Weight'].default_value = material_props['clearcoat']
                    if 'clearcoat_roughness' in material_props:
                        bsdf.inputs['Coat Roughness'].default_value = material_props['clearcoat_roughness']
                
                # Add procedural textures if specified
                if 'procedural' in material_props:
                    proc = material_props['procedural']
                    proc_type = proc.get('type', 'noise')
                    
                    if proc_type == 'noise':
                        self._add_noise_procedural(nodes, links, bsdf, proc)
                    elif proc_type in ['scratches_and_dirt', 'scratch', 'rust']:
                        self._add_scratches_procedural(nodes, links, bsdf, proc)
                    elif proc_type == 'wood_grain':
                        self._add_wood_grain_procedural(nodes, links, bsdf, proc)
                    elif proc_type == 'concrete' or proc_type == 'rock':
                        self._add_concrete_procedural(nodes, links, bsdf, proc)
                    elif proc_type == 'bump':
                        self._add_bump_procedural(nodes, links, bsdf, proc)
                
                links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
            
            # Assign material to object
            if len(obj.data.materials):
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)
            
            return {"success": True, "material_name": mat_name}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _add_noise_procedural(self, nodes, links, bsdf, proc):
        """Add noise-based procedural texture"""
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = proc.get('scale', 15.0)
        noise.inputs['Detail'].default_value = proc.get('detail', 8.0)
        noise.location = (-400, -200)
        
        # Mix with base roughness
        if 'roughness_variation' in proc:
            mix = nodes.new('ShaderNodeMixRGB')
            mix.blend_type = 'MIX'
            mix.inputs[0].default_value = proc['roughness_variation']
            mix.location = (-200, -200)
            links.new(noise.outputs['Fac'], mix.inputs[2])
            links.new(mix.outputs[0], bsdf.inputs['Roughness'])
    
    def _add_scratches_procedural(self, nodes, links, bsdf, proc):
        """Add scratches and dirt procedural texture"""
        scale = proc.get('scale', 20.0)
        detail = proc.get('detail', 5.0)
        
        # Scratch noise
        scratch_noise = nodes.new('ShaderNodeTexNoise')
        scratch_noise.inputs['Scale'].default_value = scale
        scratch_noise.inputs['Detail'].default_value = detail
        scratch_noise.location = (-600, -200)
        
        # Dirt noise
        dirt_noise = nodes.new('ShaderNodeTexNoise')
        dirt_noise.inputs['Scale'].default_value = scale * 0.5
        dirt_noise.location = (-600, -400)
        
        # Mix
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = 0.5
        mix.location = (-400, -300)
        
        # Color ramp
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.4
        ramp.color_ramp.elements[1].position = 0.6
        ramp.location = (-200, -300)
        
        links.new(scratch_noise.outputs['Fac'], mix.inputs[6])
        links.new(dirt_noise.outputs['Fac'], mix.inputs[7])
        links.new(mix.outputs[2], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])
        
        # Add bump
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.3
        bump.location = (-200, -500)
        links.new(ramp.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    def _add_wood_grain_procedural(self, nodes, links, bsdf, proc):
        """Add wood grain procedural texture"""
        scale = proc.get('scale', 5.0)
        detail = proc.get('detail', 8.0)
        
        # Wave texture
        wave = nodes.new('ShaderNodeTexWave')
        wave.wave_type = 'RINGS'
        wave.inputs['Scale'].default_value = scale
        wave.inputs['Distortion'].default_value = 2.0
        wave.inputs['Detail'].default_value = detail
        wave.location = (-600, 0)
        
        # Noise for variation
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = scale * 3
        noise.location = (-600, -200)
        
        # Mix
        mix = nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.blend_type = 'MULTIPLY'
        mix.inputs[0].default_value = 0.3
        mix.location = (-400, -100)
        
        # Color ramp
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.location = (-200, -100)
        
        links.new(wave.outputs['Color'], mix.inputs[6])
        links.new(noise.outputs['Fac'], mix.inputs[7])
        links.new(mix.outputs[2], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        
        # Bump
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.1
        bump.location = (-200, -300)
        links.new(ramp.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    def _add_concrete_procedural(self, nodes, links, bsdf, proc):
        """Add concrete/rock procedural texture"""
        scale = proc.get('scale', 8.0)
        detail = proc.get('detail', 4.0)
        
        # Noise texture
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = scale
        noise.inputs['Detail'].default_value = detail
        noise.location = (-400, -200)
        
        # Bump for surface variation
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.5
        bump.location = (-200, -200)
        
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        
        # Add to roughness for variation
        links.new(noise.outputs['Fac'], bsdf.inputs['Roughness'])
    
    def _add_bump_procedural(self, nodes, links, bsdf, proc):
        """Add simple bump map"""
        scale = proc.get('scale', 200.0)
        
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = scale
        noise.location = (-400, -200)
        
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.2
        bump.location = (-200, -200)
        
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    def auto_enhance_materials(self, object_name=None, aggressive=False):
        """Automatically enhance materials on objects"""
        try:
            # Import material suggestions
            from .materials import get_suggested_material, MATERIAL_PRESETS
            
            enhanced = []
            objects_to_enhance = []
            
            if object_name:
                obj = bpy.data.objects.get(object_name)
                if obj:
                    objects_to_enhance = [obj]
                else:
                    return {"error": f"Object '{object_name}' not found"}
            else:
                # Enhance all mesh objects in scene
                objects_to_enhance = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            
            for obj in objects_to_enhance:
                # Get suggested material
                suggested = get_suggested_material(obj.name)
                material_props = MATERIAL_PRESETS[suggested].copy()
                
                # If aggressive, add more procedural detail
                if aggressive and 'procedural' not in material_props:
                    # Add procedural detail based on material type
                    if 'metal' in suggested:
                        material_props['procedural'] = {
                            'type': 'scratches_and_dirt',
                            'scale': 15.0,
                            'detail': 6.0,
                            'roughness_variation': 0.4
                        }
                    elif 'paint' in suggested:
                        material_props['procedural'] = {
                            'type': 'scratches_and_dirt',
                            'scale': 25.0,
                            'detail': 5.0
                        }
                
                # Apply the material
                result = self.apply_material_preset(obj.name, material_props, suggested)
                
                if result.get("success"):
                    enhanced.append(f"{obj.name} -> {suggested}")
            
            return {
                "success": True,
                "enhanced_count": len(enhanced),
                "details": enhanced
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== POST-PROCESSING METHODS ====================
    
    def apply_subdivision_surface(self, object_name, viewport_levels=2, render_levels=3, adaptive=True):
        """Apply subdivision surface modifier to an object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            if obj.type != 'MESH':
                return {"error": f"Object '{object_name}' is not a mesh"}
            
            # Check if subdivision modifier already exists
            subsurf = None
            for mod in obj.modifiers:
                if mod.type == 'SUBSURF':
                    subsurf = mod
                    break
            
            # Create new modifier if it doesn't exist
            if not subsurf:
                subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            
            # Set properties
            subsurf.levels = viewport_levels
            subsurf.render_levels = render_levels
            
            # Set subdivision algorithm
            if adaptive:
                subsurf.subdivision_type = 'CATMULL_CLARK'
            
            return {"success": True, "modifier": "Subdivision Surface"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def apply_enhancement_preset(self, object_name, preset_config, preset_name="custom"):
        """Apply a complete enhancement preset to an object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            if obj.type != 'MESH':
                return {"error": f"Object '{object_name}' is not a mesh"}
            
            applied_modifiers = []
            
            # Apply subdivision surface
            if preset_config.get('subdivision', {}).get('enabled'):
                sub = preset_config['subdivision']
                result = self.apply_subdivision_surface(
                    object_name,
                    viewport_levels=sub.get('levels', 2),
                    render_levels=sub.get('render_levels', 3),
                    adaptive=sub.get('adaptive', True)
                )
                if result.get('success'):
                    applied_modifiers.append("Subdivision Surface")
                    
                    # Set use_creases if specified
                    if sub.get('use_creases', False):
                        for mod in obj.modifiers:
                            if mod.type == 'SUBSURF':
                                mod.use_creases = True
            
            # Apply edge split
            if preset_config.get('edge_split', {}).get('enabled'):
                edge_split = obj.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
                edge_split.split_angle = preset_config['edge_split']['angle'] * 0.0174533  # Convert to radians
                applied_modifiers.append("Edge Split")
            
            # Apply bevel
            if preset_config.get('bevel', {}).get('enabled'):
                bev = preset_config['bevel']
                bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
                bevel.width = bev.get('width', 0.01)
                bevel.segments = bev.get('segments', 2)
                if 'only_vertices' in bev:
                    bevel.affect = 'VERTICES' if bev['only_vertices'] else 'EDGES'
                applied_modifiers.append("Bevel")
            
            # Apply remesh (for organic)
            if preset_config.get('remesh', {}).get('enabled'):
                rem = preset_config['remesh']
                remesh = obj.modifiers.new(name="Remesh", type='REMESH')
                remesh.mode = rem.get('mode', 'SMOOTH')
                remesh.octree_depth = rem.get('octree_depth', 6)
                applied_modifiers.append("Remesh")
            
            # Set shading
            if preset_config.get('shade_smooth'):
                # Smooth shading
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.shade_smooth()
                applied_modifiers.append("Smooth Shading")
                
                # Auto smooth
                if preset_config.get('auto_smooth', {}).get('enabled'):
                    obj.data.use_auto_smooth = True
                    obj.data.auto_smooth_angle = preset_config['auto_smooth']['angle'] * 0.0174533
                    applied_modifiers.append("Auto Smooth")
            else:
                # Flat shading
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.shade_flat()
                applied_modifiers.append("Flat Shading")
            
            return {
                "success": True,
                "applied_modifiers": applied_modifiers
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def auto_enhance_geometry(self, object_name=None, analyze_first=True):
        """Automatically enhance geometry quality"""
        try:
            from .post_processing import get_suggested_preset, ENHANCEMENT_PRESETS
            
            enhanced = []
            objects_to_enhance = []
            
            if object_name:
                obj = bpy.data.objects.get(object_name)
                if obj:
                    objects_to_enhance = [obj]
                else:
                    return {"error": f"Object '{object_name}' not found"}
            else:
                # Enhance all mesh objects
                objects_to_enhance = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            
            for obj in objects_to_enhance:
                # Analyze mesh if requested
                if analyze_first:
                    stats = self._get_mesh_stats(obj)
                    
                    # Use analysis to determine preset
                    face_count = stats.get('face_count', 0)
                    if face_count < 1000:
                        suggested = "high_detail"
                    elif "vehicle" in obj.name.lower() or "car" in obj.name.lower():
                        suggested = "mechanical"
                    elif "building" in obj.name.lower() or "wall" in obj.name.lower():
                        suggested = "architectural"
                    else:
                        suggested = get_suggested_preset(obj.name)
                else:
                    suggested = get_suggested_preset(obj.name)
                
                preset_config = ENHANCEMENT_PRESETS[suggested].copy()
                
                # Adjust subdivision levels based on poly count if analyzing
                if analyze_first and 'subdivision' in preset_config and preset_config['subdivision'].get('enabled'):
                    stats = self._get_mesh_stats(obj)
                    face_count = stats.get('face_count', 0)
                    
                    if face_count < 500:
                        preset_config['subdivision']['levels'] = 3
                        preset_config['subdivision']['render_levels'] = 4
                    elif face_count > 20000:
                        preset_config['subdivision']['levels'] = 1
                        preset_config['subdivision']['render_levels'] = 2
                
                # Apply the preset
                result = self.apply_enhancement_preset(obj.name, preset_config, suggested)
                
                if result.get("success"):
                    mods = ", ".join(result.get("applied_modifiers", []))
                    enhanced.append(f"{obj.name} -> {suggested} ({mods})")
            
            return {
                "success": True,
                "enhanced_count": len(enhanced),
                "details": enhanced
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _get_mesh_stats(self, obj):
        """Get mesh statistics for an object"""
        if obj.type != 'MESH':
            return {}
        
        mesh = obj.data
        
        stats = {
            "vertex_count": len(mesh.vertices),
            "face_count": len(mesh.polygons),
            "edge_count": len(mesh.edges),
            "triangles": sum(1 for poly in mesh.polygons if len(poly.vertices) == 3),
            "quads": sum(1 for poly in mesh.polygons if len(poly.vertices) == 4),
            "ngons": sum(1 for poly in mesh.polygons if len(poly.vertices) > 4),
        }
        
        return stats
    
    def analyze_mesh(self, object_name):
        """Analyze mesh quality and provide suggestions"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            if obj.type != 'MESH':
                return {"error": f"Object '{object_name}' is not a mesh"}
            
            stats = self._get_mesh_stats(obj)
            
            # Analyze quality
            from .post_processing import analyze_mesh_quality
            analysis = analyze_mesh_quality(stats)
            
            return {
                "success": True,
                "stats": stats,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def add_edge_bevel(self, object_name, width=0.01, segments=2):
        """Add bevel modifier to an object"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            if obj.type != 'MESH':
                return {"error": f"Object '{object_name}' is not a mesh"}
            
            # Add bevel modifier
            bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
            bevel.width = width
            bevel.segments = segments
            
            return {"success": True}
            
        except Exception as e:
            return {"error": str(e)}
    
    def set_shading(self, object_name, smooth=True, auto_smooth_angle=30.0):
        """Set object shading"""
        try:
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            if obj.type != 'MESH':
                return {"error": f"Object '{object_name}' is not a mesh"}
            
            # Set active and select
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            
            # Apply shading
            if smooth:
                bpy.ops.object.shade_smooth()
                if auto_smooth_angle > 0:
                    obj.data.use_auto_smooth = True
                    obj.data.auto_smooth_angle = auto_smooth_angle * 0.0174533  # Convert to radians
            else:
                bpy.ops.object.shade_flat()
            
            return {"success": True}
            
        except Exception as e:
            return {"error": str(e)}

    # ========================================================================
    # LIGHTING & ATMOSPHERE COMMANDS
    # ========================================================================

    def setup_hdri_lighting(self, preset, config):
        """Set up HDRI environment lighting"""
        try:
            # Get or create world
            if not bpy.context.scene.world:
                bpy.context.scene.world = bpy.data.worlds.new("World")
            
            world = bpy.context.scene.world
            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Create nodes
            output_node = nodes.new('ShaderNodeOutputWorld')
            background_node = nodes.new('ShaderNodeBackground')
            env_texture = nodes.new('ShaderNodeTexEnvironment')
            mapping = nodes.new('ShaderNodeMapping')
            tex_coord = nodes.new('ShaderNodeTexCoord')
            
            # Position nodes
            tex_coord.location = (-800, 0)
            mapping.location = (-600, 0)
            env_texture.location = (-300, 0)
            background_node.location = (0, 0)
            output_node.location = (200, 0)
            
            # Connect nodes
            links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], env_texture.inputs['Vector'])
            links.new(env_texture.outputs['Color'], background_node.inputs['Color'])
            links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
            
            # Set rotation (convert degrees to radians)
            import math
            mapping.inputs['Rotation'].default_value[2] = math.radians(config.get('rotation', 0.0))
            
            # Set strength
            background_node.inputs['Strength'].default_value = config.get('strength', 1.0)
            
            # Note: Actual HDRI file loading would require the file path
            # For now, we set up the node structure and user can load HDRI manually
            # or via download_polyhaven_asset
            
            return {
                "success": True,
                "message": f"HDRI node setup complete. Load an HDRI texture or use PolyHaven: {config.get('recommended_hdris', [])}"
            }
            
        except Exception as e:
            return {"error": str(e)}

    def apply_lighting_rig(self, preset, config, scale=1.0):
        """Create a lighting rig with multiple lights"""
        try:
            created_lights = []
            
            for light_config in config.get('lights', []):
                # Create light data
                light_data = bpy.data.lights.new(
                    name=light_config['name'],
                    type=light_config['type']
                )
                
                # Set light properties
                light_data.energy = light_config['energy']
                light_data.color = light_config['color']
                
                # Type-specific properties
                if light_config['type'] == 'AREA':
                    light_data.size = light_config.get('size', 1.0)
                elif light_config['type'] == 'SPOT':
                    light_data.spot_size = light_config.get('spot_size', 0.785)
                    light_data.spot_blend = light_config.get('spot_blend', 0.15)
                elif light_config['type'] == 'SUN':
                    light_data.angle = light_config.get('angle', 0.00918)
                
                # Create light object
                light_obj = bpy.data.objects.new(light_config['name'], light_data)
                bpy.context.collection.objects.link(light_obj)
                
                # Set location (scaled)
                loc = light_config['location']
                light_obj.location = (loc[0] * scale, loc[1] * scale, loc[2] * scale)
                
                # Set rotation (convert to radians)
                import math
                rot = light_config['rotation']
                light_obj.rotation_euler = (rot[0], rot[1], rot[2])
                
                created_lights.append(light_config['name'])
            
            return {
                "success": True,
                "lights_created": created_lights,
                "count": len(created_lights)
            }
            
        except Exception as e:
            return {"error": str(e)}

    def add_atmospheric_fog(self, preset, config):
        """Add volumetric fog to the scene"""
        try:
            if not config.get('volumetric'):
                # Clear volumetrics
                if bpy.context.scene.world:
                    world = bpy.context.scene.world
                    if world.use_nodes:
                        # Remove volume shader if exists
                        nodes = world.node_tree.nodes
                        for node in nodes:
                            if node.type == 'VOLUME_SCATTER':
                                nodes.remove(node)
                return {"success": True, "message": "Volumetrics cleared"}
            
            # Get or create world
            if not bpy.context.scene.world:
                bpy.context.scene.world = bpy.data.worlds.new("World")
            
            world = bpy.context.scene.world
            world.use_nodes = True
            nodes = world.node_tree.nodes
            links = world.node_tree.links
            
            # Find or create output node
            output_node = None
            for node in nodes:
                if node.type == 'OUTPUT_WORLD':
                    output_node = node
                    break
            
            if not output_node:
                output_node = nodes.new('ShaderNodeOutputWorld')
                output_node.location = (200, 0)
            
            # Create volume scatter node
            volume_scatter = nodes.new('ShaderNodeVolumeScatter')
            volume_scatter.location = (0, -200)
            
            # Set properties
            volume_scatter.inputs['Density'].default_value = config.get('density', 0.05)
            volume_scatter.inputs['Anisotropy'].default_value = config.get('anisotropy', 0.1)
            volume_scatter.inputs['Color'].default_value = list(config.get('color', (0.8, 0.85, 0.9))) + [1.0]
            
            # Create volume absorption if specified
            if 'absorption_color' in config:
                volume_abs = nodes.new('ShaderNodeVolumeAbsorption')
                volume_abs.location = (0, -350)
                volume_abs.inputs['Color'].default_value = list(config['absorption_color']) + [1.0]
                
                # Mix volumes
                add_shader = nodes.new('ShaderNodeAddShader')
                add_shader.location = (200, -250)
                links.new(volume_scatter.outputs['Volume'], add_shader.inputs[0])
                links.new(volume_abs.outputs['Volume'], add_shader.inputs[1])
                links.new(add_shader.outputs['Shader'], output_node.inputs['Volume'])
            else:
                # Direct connection
                links.new(volume_scatter.outputs['Volume'], output_node.inputs['Volume'])
            
            return {
                "success": True,
                "message": f"Volumetric atmosphere added: {preset}"
            }
            
        except Exception as e:
            return {"error": str(e)}

    def setup_camera(self, preset, config, position_type="three_quarter", target_object=None):
        """Create and configure a camera"""
        try:
            import math
            from .lighting import calculate_camera_position
            
            # Create camera
            camera_data = bpy.data.cameras.new("Camera")
            camera_obj = bpy.data.objects.new("Camera", camera_data)
            bpy.context.collection.objects.link(camera_obj)
            
            # Set camera properties
            camera_data.lens = config.get('focal_length', 50)
            camera_data.sensor_width = config.get('sensor_width', 36)
            
            # Depth of field
            if config.get('dof_enabled'):
                camera_data.dof.use_dof = True
                camera_data.dof.aperture_fstop = config.get('f_stop', 5.6)
                
                # If target object specified, focus on it
                if target_object:
                    target_obj = bpy.data.objects.get(target_object)
                    if target_obj:
                        camera_data.dof.focus_object = target_obj
            
            # Calculate camera position
            if target_object:
                target_obj = bpy.data.objects.get(target_object)
                if target_obj:
                    # Get bounding box
                    bbox_corners = [target_obj.matrix_world @ mathutils.Vector(corner) for corner in target_obj.bound_box]
                    min_corner = [min(c[i] for c in bbox_corners) for i in range(3)]
                    max_corner = [max(c[i] for c in bbox_corners) for i in range(3)]
                    
                    cam_pos = calculate_camera_position([min_corner, max_corner], position_type)
                    camera_obj.location = cam_pos['location']
                    camera_obj.rotation_euler = [math.radians(r) for r in cam_pos['rotation']]
                    
                    # Point camera at target
                    direction = mathutils.Vector(cam_pos['target']) - mathutils.Vector(cam_pos['location'])
                    rot_quat = direction.to_track_quat('-Z', 'Y')
                    camera_obj.rotation_euler = rot_quat.to_euler()
            else:
                # Default position
                default_pos = calculate_camera_position(None, position_type)
                camera_obj.location = default_pos['location']
                camera_obj.rotation_euler = [math.radians(r) for r in default_pos['rotation']]
            
            # Make this the active camera
            bpy.context.scene.camera = camera_obj
            
            return {
                "success": True,
                "camera_name": camera_obj.name,
                "focal_length": camera_data.lens,
                "dof_enabled": config.get('dof_enabled', False)
            }
            
        except Exception as e:
            return {"error": str(e)}

    def configure_render_settings(self, preset, config):
        """Configure render engine and quality settings"""
        try:
            scene = bpy.context.scene
            
            # Set render engine
            engine = config.get('engine', 'CYCLES')
            scene.render.engine = engine
            
            # Set resolution
            scene.render.resolution_x = config.get('resolution_x', 1920)
            scene.render.resolution_y = config.get('resolution_y', 1080)
            scene.render.resolution_percentage = config.get('resolution_percentage', 100)
            
            # Engine-specific settings
            if engine == 'CYCLES':
                scene.cycles.samples = config.get('samples', 128)
                scene.cycles.use_denoising = config.get('use_denoising', True)
                
                # Enable volumetrics for better fog/atmosphere
                scene.cycles.volume_bounces = 2
                scene.cycles.transparent_max_bounces = 8
                
            elif engine == 'BLENDER_EEVEE':
                scene.eevee.taa_render_samples = config.get('samples', 64)
                scene.eevee.use_gtao = True
                scene.eevee.use_bloom = True
                scene.eevee.use_ssr = True
                
                # Enable volumetrics
                scene.eevee.use_volumetric_lights = True
                scene.eevee.use_volumetric_shadows = True
            
            return {
                "success": True,
                "engine": engine,
                "samples": config.get('samples'),
                "resolution": f"{scene.render.resolution_x}x{scene.render.resolution_y}"
            }
            
        except Exception as e:
            return {"error": str(e)}

    # ============================================================================
    # COMPOSITION SYSTEM HANDLERS
    # ============================================================================

    def analyze_composition(self, object_name=None, composition_rule="rule_of_thirds"):
        """Analyze current scene composition"""
        try:
            import mathutils
            from .composition import calculate_composition_score, COMPOSITION_RULES
            
            # Get the object
            if object_name:
                obj = bpy.data.objects.get(object_name)
                if not obj:
                    return {"error": f"Object '{object_name}' not found"}
            else:
                obj = bpy.context.active_object
                if not obj:
                    return {"error": "No active object"}
            
            # Get active camera
            camera = bpy.context.scene.camera
            if not camera:
                return {"error": "No active camera in scene"}
            
            # Calculate object position in screen space
            scene = bpy.context.scene
            render = scene.render
            
            # Project object center to screen space
            co_2d = bpy_extras.object_utils.world_to_camera_view(scene, camera, obj.location)
            
            # Normalize to 0-1 range
            screen_x = co_2d.x
            screen_y = 1.0 - co_2d.y  # Flip Y axis
            
            # Calculate composition score
            score_result = calculate_composition_score((screen_x, screen_y), composition_rule)
            
            return {
                "object": obj.name,
                "camera": camera.name,
                "screen_position": {"x": round(screen_x, 3), "y": round(screen_y, 3)},
                "composition_analysis": score_result
            }
            
        except Exception as e:
            return {"error": str(e)}

    def apply_composition_rule(self, object_name, composition_rule="rule_of_thirds", camera_angle="three_quarter"):
        """Position camera using composition rule"""
        try:
            import mathutils
            import math
            from .composition import COMPOSITION_RULES, calc_composition_camera as calculate_camera_position
            
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            # Calculate object bounds
            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            min_x = min(v.x for v in bbox)
            max_x = max(v.x for v in bbox)
            min_y = min(v.y for v in bbox)
            max_y = max(v.y for v in bbox)
            min_z = min(v.z for v in bbox)
            max_z = max(v.z for v in bbox)
            
            object_bounds = {
                'width': max_x - min_x,
                'height': max_z - min_z,
                'depth': max_y - min_y
            }
            
            # Define camera angles
            angle_presets = {
                "front": (15, 0),
                "three_quarter": (15, 45),
                "side": (15, 90),
                "top": (75, 45),
                "low": (5, 45),
                "high": (35, 45),
            }
            
            camera_angle_degrees = angle_presets.get(camera_angle, (15, 45))
            
            # Calculate camera position
            camera_data = calculate_camera_position(
                object_center=tuple(obj.location),
                object_bounds=object_bounds,
                shot_type="medium_shot",  # Default
                composition_rule=composition_rule,
                camera_angle=camera_angle_degrees
            )
            
            # Create or get camera
            camera_name = f"Composition_Camera"
            if camera_name in bpy.data.cameras:
                camera_data_block = bpy.data.cameras[camera_name]
            else:
                camera_data_block = bpy.data.cameras.new(camera_name)
            
            if camera_name in bpy.data.objects:
                camera_obj = bpy.data.objects[camera_name]
            else:
                camera_obj = bpy.data.objects.new(camera_name, camera_data_block)
                bpy.context.scene.collection.objects.link(camera_obj)
            
            # Set camera position and rotation
            camera_obj.location = camera_data['position']
            
            # Point camera at object
            direction = mathutils.Vector(camera_data['target']) - mathutils.Vector(camera_data['position'])
            rot_quat = direction.to_track_quat('-Z', 'Y')
            camera_obj.rotation_euler = rot_quat.to_euler()
            
            # Set camera as active
            bpy.context.scene.camera = camera_obj
            
            return {
                "success": True,
                "camera": camera_name,
                "position": camera_data['position'],
                "composition_rule": camera_data['composition_rule'],
                "focal_length": camera_data['focal_length']
            }
            
        except Exception as e:
            return {"error": str(e)}

    def auto_frame_with_composition(self, object_name, purpose="general", preset=None):
        """Automatically frame object with optimal composition"""
        try:
            import mathutils
            import math
            from .composition import (
                suggest_shot_type, 
                suggest_composition_rule, 
                COMPOSITION_PRESETS,
                SHOT_TYPES,
                calc_composition_camera as calculate_camera_position
            )
            
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            # Calculate object bounds
            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            min_x = min(v.x for v in bbox)
            max_x = max(v.x for v in bbox)
            min_y = min(v.y for v in bbox)
            max_y = max(v.y for v in bbox)
            min_z = min(v.z for v in bbox)
            max_z = max(v.z for v in bbox)
            
            object_bounds = {
                'width': max_x - min_x,
                'height': max_z - min_z,
                'depth': max_y - min_y
            }
            
            # Use preset if provided
            if preset and preset in COMPOSITION_PRESETS:
                preset_config = COMPOSITION_PRESETS[preset]
                composition_rule = preset_config['composition_rule']
                shot_type = preset_config['shot_type']
                camera_angle = preset_config['camera_angle']
            else:
                # Auto-suggest
                shot_type = suggest_shot_type(object_bounds, purpose)
                
                # Determine object type from name or purpose
                object_type = purpose if purpose in ['portrait', 'product', 'architecture'] else 'general'
                composition_rule = suggest_composition_rule(object_type, 'neutral')
                camera_angle = (15, 45)  # Default three-quarter view
            
            # Calculate camera position
            camera_data = calculate_camera_position(
                object_center=tuple(obj.location),
                object_bounds=object_bounds,
                shot_type=shot_type,
                composition_rule=composition_rule,
                camera_angle=camera_angle
            )
            
            # Create or update camera
            camera_name = f"AutoFrame_Camera"
            if camera_name in bpy.data.cameras:
                camera_data_block = bpy.data.cameras[camera_name]
            else:
                camera_data_block = bpy.data.cameras.new(camera_name)
            
            if camera_name in bpy.data.objects:
                camera_obj = bpy.data.objects[camera_name]
            else:
                camera_obj = bpy.data.objects.new(camera_name, camera_data_block)
                bpy.context.scene.collection.objects.link(camera_obj)
            
            # Set camera properties
            camera_obj.location = camera_data['position']
            camera_data_block.lens = camera_data['focal_length']
            
            # Enable DOF
            camera_data_block.dof.use_dof = True
            camera_data_block.dof.aperture_fstop = camera_data['fstop']
            
            # Point camera at object
            direction = mathutils.Vector(camera_data['target']) - mathutils.Vector(camera_data['position'])
            rot_quat = direction.to_track_quat('-Z', 'Y')
            camera_obj.rotation_euler = rot_quat.to_euler()
            
            # Set focus distance
            focus_distance = (mathutils.Vector(camera_data['position']) - mathutils.Vector(camera_data['target'])).length
            camera_data_block.dof.focus_distance = focus_distance
            
            # Set as active camera
            bpy.context.scene.camera = camera_obj
            
            return {
                "success": True,
                "camera": camera_name,
                "shot_type": camera_data['shot_type'],
                "composition_rule": camera_data['composition_rule'],
                "focal_length": camera_data['focal_length'],
                "fstop": camera_data['fstop'],
                "position": camera_data['position'],
                "distance": camera_data['distance'],
                "frame_fill": f"{int(camera_data['frame_fill'] * 100)}%"
            }
            
        except Exception as e:
            return {"error": str(e)}

    def suggest_composition(self, object_name, scene_description=""):
        """Get composition suggestions for object"""
        try:
            import mathutils
            from .composition import (
                suggest_shot_type,
                suggest_composition_rule,
                COMPOSITION_PRESETS
            )
            
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            # Calculate object bounds
            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            object_bounds = {
                'width': max(v.x for v in bbox) - min(v.x for v in bbox),
                'height': max(v.z for v in bbox) - min(v.z for v in bbox),
                'depth': max(v.y for v in bbox) - min(v.y for v in bbox)
            }
            
            # Parse scene description for keywords
            desc_lower = scene_description.lower()
            
            # Determine purpose from description
            if any(word in desc_lower for word in ['detail', 'macro', 'close']):
                purpose = 'detail'
            elif any(word in desc_lower for word in ['portrait', 'face']):
                purpose = 'portrait'
            elif any(word in desc_lower for word in ['product', 'showcase']):
                purpose = 'product'
            elif any(word in desc_lower for word in ['wide', 'landscape', 'epic', 'grand']):
                purpose = 'landscape'
            else:
                purpose = 'general'
            
            # Determine context from description
            if any(word in desc_lower for word in ['symmetrical', 'symmetric', 'minimal']):
                context = 'symmetrical'
            elif any(word in desc_lower for word in ['dynamic', 'action', 'dramatic']):
                context = 'dynamic'
            else:
                context = 'neutral'
            
            # Get suggestions
            suggested_shot = suggest_shot_type(object_bounds, purpose)
            suggested_rule = suggest_composition_rule(purpose, context)
            
            # Find matching presets
            matching_presets = []
            for preset_name, preset_config in COMPOSITION_PRESETS.items():
                if (preset_config['composition_rule'] == suggested_rule or 
                    preset_config['shot_type'] == suggested_shot):
                    matching_presets.append({
                        "name": preset_name,
                        "description": preset_config['name'],
                        "rule": preset_config['composition_rule'],
                        "shot": preset_config['shot_type']
                    })
            
            return {
                "object": object_name,
                "suggested_shot_type": suggested_shot,
                "suggested_composition_rule": suggested_rule,
                "matching_presets": matching_presets[:3],  # Top 3
                "recommendation": f"Use '{suggested_shot}' shot with '{suggested_rule}' composition"
            }
            
        except Exception as e:
            return {"error": str(e)}

    def calculate_shot_framing(self, object_name, shot_type="medium_shot"):
        """Calculate optimal camera position for shot type"""
        try:
            import mathutils
            from .composition import SHOT_TYPES, calc_composition_camera as calculate_camera_position
            
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object '{object_name}' not found"}
            
            # Validate shot type
            if shot_type not in SHOT_TYPES:
                return {"error": f"Unknown shot type '{shot_type}'. Valid types: {', '.join(SHOT_TYPES.keys())}"}
            
            # Calculate object bounds
            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            object_bounds = {
                'width': max(v.x for v in bbox) - min(v.x for v in bbox),
                'height': max(v.z for v in bbox) - min(v.z for v in bbox),
                'depth': max(v.y for v in bbox) - min(v.y for v in bbox)
            }
            
            # Calculate camera position
            camera_data = calculate_camera_position(
                object_center=tuple(obj.location),
                object_bounds=object_bounds,
                shot_type=shot_type,
                composition_rule="rule_of_thirds",
                camera_angle=(15, 45)
            )
            
            shot_info = SHOT_TYPES[shot_type]
            
            return {
                "shot_type": shot_info['name'],
                "description": shot_info['description'],
                "camera_position": camera_data['position'],
                "focal_length": camera_data['focal_length'],
                "fstop": camera_data['fstop'],
                "distance": camera_data['distance'],
                "frame_fill": f"{int(camera_data['frame_fill'] * 100)}%",
                "ideal_for": shot_info['ideal_for']
            }
            
        except Exception as e:
            return {"error": str(e)}

    # ==================== COLOR GRADING HANDLERS ====================

    def apply_color_grade(self, preset="cinematic_standard", use_compositor=True):
        """Apply complete color grade preset (LUT + tone mapping + effects)"""
        try:
            from .color_grading import COLOR_GRADE_PRESETS, LUT_PRESETS, TONE_MAPPING
            
            if preset not in COLOR_GRADE_PRESETS:
                return {"error": f"Unknown preset '{preset}'"}
            
            grade = COLOR_GRADE_PRESETS[preset]
            
            # Apply LUT
            lut_result = self.apply_lut_preset(grade["lut"])
            if "error" in lut_result:
                return lut_result
            
            # Apply tone mapping
            tone_mapping_result = self.setup_tone_mapping(grade["tone_mapping"])
            if "error" in tone_mapping_result:
                return tone_mapping_result
            
            # Apply effects if compositor is enabled
            if use_compositor and grade["effects"]:
                effects_result = self.add_color_effects(grade["effects"])
                if "error" in effects_result:
                    return effects_result
            
            return {
                "message": f"Applied color grade '{grade['name']}'",
                "preset": preset,
                "lut": grade["lut"],
                "tone_mapping": grade["tone_mapping"],
                "effects": grade["effects"] if use_compositor else []
            }
            
        except Exception as e:
            return {"error": str(e)}

    def apply_lut_preset(self, lut_preset="cinematic_neutral"):
        """Apply LUT (Look-Up Table) color grading preset"""
        try:
            from .color_grading import LUT_PRESETS, get_color_temperature_offset
            
            if lut_preset not in LUT_PRESETS:
                return {"error": f"Unknown LUT preset '{lut_preset}'"}
            
            lut = LUT_PRESETS[lut_preset]
            
            # Enable compositor for color grading
            scene = bpy.context.scene
            scene.use_nodes = True
            tree = scene.node_tree
            
            # Clear existing nodes (except render layers and composite)
            for node in tree.nodes:
                if node.type not in ['R_LAYERS', 'COMPOSITE']:
                    tree.nodes.remove(node)
            
            # Get or create render layers and composite nodes
            render_layers = None
            composite = None
            for node in tree.nodes:
                if node.type == 'R_LAYERS':
                    render_layers = node
                elif node.type == 'COMPOSITE':
                    composite = node
            
            if not render_layers:
                render_layers = tree.nodes.new('CompositorNodeRLayers')
                render_layers.location = (0, 0)
            
            if not composite:
                composite = tree.nodes.new('CompositorNodeComposite')
                composite.location = (800, 0)
            
            # Create color balance node for LUT
            color_balance = tree.nodes.new('CompositorNodeColorBalance')
            color_balance.name = f"LUT_{lut_preset}"
            color_balance.location = (200, 0)
            color_balance.lift = lut["lift"]
            color_balance.gamma = lut["gamma"]
            color_balance.gain = lut["gain"]
            
            # Create hue/saturation node
            hue_sat = tree.nodes.new('CompositorNodeHueSat')
            hue_sat.name = f"Saturation_{lut_preset}"
            hue_sat.location = (400, 0)
            hue_sat.inputs['Saturation'].default_value = lut["saturation"]
            
            # Create bright/contrast node
            bright_contrast = tree.nodes.new('CompositorNodeBrightContrast')
            bright_contrast.name = f"Contrast_{lut_preset}"
            bright_contrast.location = (600, 0)
            bright_contrast.inputs['Bright'].default_value = lut["brightness"]
            bright_contrast.inputs['Contrast'].default_value = lut["contrast"] - 1.0
            
            # Link nodes
            tree.links.new(render_layers.outputs['Image'], color_balance.inputs['Image'])
            tree.links.new(color_balance.outputs['Image'], hue_sat.inputs['Image'])
            tree.links.new(hue_sat.outputs['Image'], bright_contrast.inputs['Image'])
            tree.links.new(bright_contrast.outputs['Image'], composite.inputs['Image'])
            
            return {"message": f"Applied LUT '{lut['name']}'"}
            
        except Exception as e:
            return {"error": str(e)}

    def setup_tone_mapping(self, tone_mapping="filmic", exposure=0.0, gamma=1.0):
        """Configure tone mapping (view transform) in color management"""
        try:
            from .color_grading import TONE_MAPPING
            
            if tone_mapping not in TONE_MAPPING:
                return {"error": f"Unknown tone mapping '{tone_mapping}'"}
            
            tm = TONE_MAPPING[tone_mapping]
            scene = bpy.context.scene
            
            # Set view transform
            scene.view_settings.view_transform = tm["view_transform"]
            
            # Set look if available
            if tm["look"] != "None":
                try:
                    scene.view_settings.look = tm["look"]
                except:
                    pass  # Look might not be available for all view transforms
            
            # Set exposure and gamma
            scene.view_settings.exposure = exposure
            scene.view_settings.gamma = gamma
            
            return {"message": f"Configured tone mapping '{tm['name']}'"}
            
        except Exception as e:
            return {"error": str(e)}

    def add_color_effects(self, effects=None):
        """Add color effects like vignette, bloom, grain, etc."""
        try:
            from .color_grading import COLOR_EFFECTS
            
            if effects is None:
                effects = ["vignette_subtle", "film_grain_light"]
            
            scene = bpy.context.scene
            scene.use_nodes = True
            tree = scene.node_tree
            
            # Find the last node before composite
            composite = None
            last_node = None
            for node in tree.nodes:
                if node.type == 'COMPOSITE':
                    composite = node
                elif node.location.x > (last_node.location.x if last_node else -1000):
                    if node.type != 'COMPOSITE':
                        last_node = node
            
            if not composite:
                return {"error": "Compositor not set up"}
            
            if not last_node:
                # Find render layers as fallback
                for node in tree.nodes:
                    if node.type == 'R_LAYERS':
                        last_node = node
                        break
            
            current_node = last_node
            current_x = last_node.location.x + 200 if last_node else 200
            
            # Add each effect
            for effect_key in effects:
                if effect_key not in COLOR_EFFECTS:
                    continue
                
                effect = COLOR_EFFECTS[effect_key]
                
                # Vignette
                if "vignette" in effect_key:
                    # Create ellipse mask for vignette
                    ellipse = tree.nodes.new('CompositorNodeEllipseMask')
                    ellipse.name = f"Vignette_{effect_key}"
                    ellipse.location = (current_x, -200)
                    ellipse.width = 0.8
                    ellipse.height = 0.8
                    
                    # Blur the mask
                    blur = tree.nodes.new('CompositorNodeBlur')
                    blur.location = (current_x + 150, -200)
                    blur.size_x = int(effect["vignette_falloff"] * 50)
                    blur.size_y = int(effect["vignette_falloff"] * 50)
                    
                    # Mix with image
                    mix = tree.nodes.new('CompositorNodeMixRGB')
                    mix.location = (current_x + 300, 0)
                    mix.blend_type = 'MULTIPLY'
                    mix.inputs['Fac'].default_value = effect["vignette_strength"]
                    
                    # Link
                    tree.links.new(ellipse.outputs['Mask'], blur.inputs['Image'])
                    tree.links.new(current_node.outputs['Image'], mix.inputs[1])
                    tree.links.new(blur.outputs['Image'], mix.inputs[2])
                    
                    current_node = mix
                    current_x += 350
                
                # Film Grain
                elif "grain" in effect_key:
                    # Create noise texture (requires texture nodes)
                    # Simplified: use RGB curves to simulate grain
                    rgb_curves = tree.nodes.new('CompositorNodeCurveRGB')
                    rgb_curves.name = f"Grain_{effect_key}"
                    rgb_curves.location = (current_x, 0)
                    
                    # Add slight variation to all channels
                    for curve in [rgb_curves.mapping.curves[i] for i in range(3)]:
                        curve.points.new(0.5, 0.5 + effect["grain_strength"])
                    
                    tree.links.new(current_node.outputs['Image'], rgb_curves.inputs['Image'])
                    current_node = rgb_curves
                    current_x += 200
                
                # Bloom/Glare
                elif "bloom" in effect_key:
                    glare = tree.nodes.new('CompositorNodeGlare')
                    glare.name = f"Bloom_{effect_key}"
                    glare.location = (current_x, 0)
                    glare.glare_type = 'FOG_GLOW'
                    glare.quality = 'HIGH'
                    glare.threshold = effect.get("bloom_threshold", 1.0)
                    glare.size = int(effect.get("bloom_radius", 6.5))
                    glare.mix = effect.get("bloom_intensity", 0.1) * -1
                    
                    tree.links.new(current_node.outputs['Image'], glare.inputs['Image'])
                    current_node = glare
                    current_x += 200
                
                # Chromatic Aberration
                elif "chromatic_aberration" in effect_key:
                    # Use lens distortion node
                    lens_distort = tree.nodes.new('CompositorNodeLensdist')
                    lens_distort.name = f"CA_{effect_key}"
                    lens_distort.location = (current_x, 0)
                    lens_distort.inputs['Dispersion'].default_value = effect.get("ca_strength", 0.003)
                    
                    tree.links.new(current_node.outputs['Image'], lens_distort.inputs['Image'])
                    current_node = lens_distort
                    current_x += 200
                
                # Lens Distortion
                elif "lens_distortion" in effect_key:
                    lens_distort = tree.nodes.new('CompositorNodeLensdist')
                    lens_distort.name = f"Distortion_{effect_key}"
                    lens_distort.location = (current_x, 0)
                    lens_distort.inputs['Distort'].default_value = effect.get("distortion", 0.02)
                    lens_distort.inputs['Dispersion'].default_value = effect.get("dispersion", 0.01)
                    
                    tree.links.new(current_node.outputs['Image'], lens_distort.inputs['Image'])
                    current_node = lens_distort
                    current_x += 200
            
            # Link final node to composite
            composite.location = (current_x, 0)
            tree.links.new(current_node.outputs['Image'], composite.inputs['Image'])
            
            return {
                "message": f"Applied {len(effects)} color effects",
                "effects": effects
            }
            
        except Exception as e:
            return {"error": str(e)}

    # ==================== COLOR GRADING HANDLERS ====================

    def apply_color_grade(self, preset="cinematic_standard", use_compositor=True):
        """Apply complete color grade preset (LUT + tone mapping + effects)"""
        try:
            from .color_grading import COLOR_GRADE_PRESETS
            
            if preset not in COLOR_GRADE_PRESETS:
                return {"error": f"Unknown preset '{preset}'. Available: {', '.join(COLOR_GRADE_PRESETS.keys())}"}
            
            grade = COLOR_GRADE_PRESETS[preset]
            
            # Apply LUT
            self.apply_lut_preset(lut_preset=grade["lut"])
            
            # Apply tone mapping
            self.setup_tone_mapping(tone_mapping=grade["tone_mapping"])
            
            # Apply effects
            if use_compositor and grade["effects"]:
                self.add_color_effects(effects=grade["effects"])
            
            return {
                "message": f"Color grade '{grade['name']}' applied successfully",
                "preset": preset,
                "lut": grade["lut"],
                "tone_mapping": grade["tone_mapping"],
                "effects": grade["effects"]
            }
            
        except Exception as e:
            return {"error": str(e)}

    def apply_lut_preset(self, lut_preset="cinematic_neutral"):
        """Apply LUT (Look-Up Table) color grading preset"""
        try:
            from .color_grading import LUT_PRESETS
            
            if lut_preset not in LUT_PRESETS:
                return {"error": f"Unknown LUT '{lut_preset}'. Available: {', '.join(LUT_PRESETS.keys())}"}
            
            lut = LUT_PRESETS[lut_preset]
            
            # Enable compositor
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            nodes = tree.nodes
            
            # Clear existing color grading nodes
            for node in nodes:
                if node.name.startswith("LUT_") or node.name.startswith("Saturation_") or node.name.startswith("Contrast_"):
                    nodes.remove(node)
            
            # Get or create render layers node
            render_layers = None
            for node in nodes:
                if node.type == 'R_LAYERS':
                    render_layers = node
                    break
            
            if not render_layers:
                render_layers = nodes.new('CompositorNodeRLayers')
                render_layers.location = (0, 0)
            
            # Get or create composite node
            composite = None
            for node in nodes:
                if node.type == 'COMPOSITE':
                    composite = node
                    break
            
            if not composite:
                composite = nodes.new('CompositorNodeComposite')
                composite.location = (800, 0)
            
            # Create color balance node (LUT)
            color_balance = nodes.new('CompositorNodeColorBalance')
            color_balance.name = f"LUT_{lut_preset}"
            color_balance.location = (200, 0)
            color_balance.lift = lut["lift"]
            color_balance.gamma = lut["gamma"]
            color_balance.gain = lut["gain"]
            
            # Create hue/saturation node
            hue_sat = nodes.new('CompositorNodeHueSat')
            hue_sat.name = f"Saturation_{lut_preset}"
            hue_sat.location = (400, 0)
            hue_sat.inputs['Saturation'].default_value = lut["saturation"]
            
            # Create bright/contrast node
            bright_contrast = nodes.new('CompositorNodeBrightContrast')
            bright_contrast.name = f"Contrast_{lut_preset}"
            bright_contrast.location = (600, 0)
            bright_contrast.inputs['Bright'].default_value = lut["brightness"]
            bright_contrast.inputs['Contrast'].default_value = lut["contrast"] - 1.0
            
            # Link nodes
            links = tree.links
            
            # Clear existing links to composite
            for link in composite.inputs['Image'].links:
                links.remove(link)
            
            # Create new links
            links.new(render_layers.outputs['Image'], color_balance.inputs['Image'])
            links.new(color_balance.outputs['Image'], hue_sat.inputs['Image'])
            links.new(hue_sat.outputs['Image'], bright_contrast.inputs['Image'])
            links.new(bright_contrast.outputs['Image'], composite.inputs['Image'])
            
            return {
                "message": f"LUT '{lut['name']}' applied",
                "lut": lut_preset
            }
            
        except Exception as e:
            return {"error": str(e)}

    def setup_tone_mapping(self, tone_mapping="filmic", exposure=0.0, gamma=1.0):
        """Configure tone mapping (view transform) in color management"""
        try:
            from .color_grading import TONE_MAPPING
            
            if tone_mapping not in TONE_MAPPING:
                return {"error": f"Unknown tone mapping '{tone_mapping}'. Available: {', '.join(TONE_MAPPING.keys())}"}
            
            tm = TONE_MAPPING[tone_mapping]
            
            # Set view transform
            scene = bpy.context.scene
            scene.view_settings.view_transform = tm["view_transform"]
            scene.view_settings.look = tm["look"]
            scene.view_settings.exposure = exposure
            scene.view_settings.gamma = gamma
            
            return {
                "message": f"Tone mapping '{tm['name']}' configured",
                "view_transform": tm["view_transform"],
                "look": tm["look"],
                "exposure": exposure,
                "gamma": gamma
            }
            
        except Exception as e:
            return {"error": str(e)}

    def add_color_effects(self, effects=None):
        """Add color effects via compositor nodes"""
        try:
            from .color_grading import COLOR_EFFECTS
            
            if effects is None:
                effects = ["vignette_subtle", "film_grain_light"]
            
            # Validate effects
            invalid = [e for e in effects if e not in COLOR_EFFECTS]
            if invalid:
                return {"error": f"Unknown effects: {', '.join(invalid)}. Available: {', '.join(COLOR_EFFECTS.keys())}"}
            
            # Enable compositor
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            nodes = tree.nodes
            links = tree.links
            
            # Find the last node before composite (should be contrast node from LUT)
            composite = None
            for node in nodes:
                if node.type == 'COMPOSITE':
                    composite = node
                    break
            
            if not composite:
                composite = nodes.new('CompositorNodeComposite')
                composite.location = (1200, 0)
            
            # Find input to composite
            current_node = None
            current_output = None
            if composite.inputs['Image'].links:
                link = composite.inputs['Image'].links[0]
                current_node = link.from_node
                current_output = link.from_socket
            else:
                # Find render layers
                for node in nodes:
                    if node.type == 'R_LAYERS':
                        current_node = node
                        current_output = node.outputs['Image']
                        break
            
            if not current_node:
                return {"error": "No input found for compositor"}
            
            # Disconnect composite input
            for link in composite.inputs['Image'].links:
                links.remove(link)
            
            x_offset = current_node.location[0] + 200
            y_offset = 0
            
            # Add each effect
            for effect_key in effects:
                effect = COLOR_EFFECTS[effect_key]
                
                if "vignette" in effect_key:
                    # Create vignette using ellipse mask
                    ellipse = nodes.new('CompositorNodeEllipseMask')
                    ellipse.name = f"Vignette_Mask_{effect_key}"
                    ellipse.location = (x_offset, y_offset - 200)
                    ellipse.width = 0.8
                    ellipse.height = 0.8
                    
                    blur = nodes.new('CompositorNodeBlur')
                    blur.name = f"Vignette_Blur_{effect_key}"
                    blur.location = (x_offset + 150, y_offset - 200)
                    blur.size_x = 100
                    blur.size_y = 100
                    blur.filter_type = 'GAUSS'
                    
                    mix = nodes.new('CompositorNodeMixRGB')
                    mix.name = f"Vignette_{effect_key}"
                    mix.location = (x_offset + 300, y_offset)
                    mix.blend_type = 'MULTIPLY'
                    mix.inputs['Fac'].default_value = effect["vignette_strength"]
                    mix.inputs['Color2'].default_value = (0, 0, 0, 1)
                    
                    # Link vignette nodes
                    links.new(ellipse.outputs['Mask'], blur.inputs['Image'])
                    links.new(blur.outputs['Image'], mix.inputs['Fac'])
                    links.new(current_output, mix.inputs['Image'])
                    
                    current_node = mix
                    current_output = mix.outputs['Image']
                    x_offset += 350
                
                elif "grain" in effect_key:
                    # Create film grain using noise texture
                    mix = nodes.new('CompositorNodeMixRGB')
                    mix.name = f"Grain_{effect_key}"
                    mix.location = (x_offset, y_offset)
                    mix.blend_type = 'OVERLAY'
                    mix.inputs['Fac'].default_value = effect["grain_strength"]
                    
                    # Note: Actual grain requires render or texture input
                    # This is a placeholder - would need noise texture in practice
                    links.new(current_output, mix.inputs['Image'])
                    
                    current_node = mix
                    current_output = mix.outputs['Image']
                    x_offset += 200
                
                elif "bloom" in effect_key:
                    # Create bloom using glare node
                    glare = nodes.new('CompositorNodeGlare')
                    glare.name = f"Bloom_{effect_key}"
                    glare.location = (x_offset, y_offset)
                    glare.glare_type = 'FOG_GLOW'
                    glare.quality = 'HIGH'
                    glare.threshold = effect.get("bloom_threshold", 1.0)
                    glare.size = int(effect.get("bloom_radius", 6.5))
                    glare.mix = effect.get("bloom_intensity", 0.1) * -1
                    
                    links.new(current_output, glare.inputs['Image'])
                    
                    current_node = glare
                    current_output = glare.outputs['Image']
                    x_offset += 200
                
                elif "chromatic_aberration" in effect_key or "lens_distortion" in effect_key:
                    # Create lens distortion
                    lens = nodes.new('CompositorNodeLensdist')
                    lens.name = f"Lens_{effect_key}"
                    lens.location = (x_offset, y_offset)
                    
                    if "chromatic" in effect_key:
                        lens.inputs['Dispersion'].default_value = effect.get("ca_strength", 0.003)
                    else:
                        lens.inputs['Distort'].default_value = effect.get("distortion", 0.02)
                        lens.inputs['Dispersion'].default_value = effect.get("dispersion", 0.01)
                    
                    links.new(current_output, lens.inputs['Image'])
                    
                    current_node = lens
                    current_output = lens.outputs['Image']
                    x_offset += 200
            
            # Connect final output to composite
            links.new(current_output, composite.inputs['Image'])
            composite.location = (x_offset + 100, 0)
            
            return {
                "message": f"Applied {len(effects)} color effects",
                "effects": effects
            }
            
        except Exception as e:
            return {"error": str(e)}

    def get_polyhaven_categories(self, asset_type):
        """Get categories for a specific asset type from Polyhaven"""
        try:
            if asset_type not in ["hdris", "textures", "models", "all"]:
                return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}

            response = requests.get(f"https://api.polyhaven.com/categories/{asset_type}", headers=REQ_HEADERS)
            if response.status_code == 200:
                return {"categories": response.json()}
            else:
                return {"error": f"API request failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def apply_scene_template(self, template_key, target_object=None, auto_render=False, template=None):
        """
        Apply a complete professional scene template combining all enhancement systems.
        This is the master function that orchestrates the entire enhancement pipeline.
        """
        try:
            import scene_templates_data
            SCENE_TEMPLATES = scene_templates_data.SCENE_TEMPLATES
            
            # Get template
            if template is None:
                if template_key not in SCENE_TEMPLATES:
                    return {"error": f"Template '{template_key}' not found"}
                template = SCENE_TEMPLATES[template_key]
            
            # Track results
            results = {
                "template_name": template["name"],
                "template_key": template_key,
                "steps": {}
            }
            
            # Determine target object
            if target_object is None:
                # Auto-detect: Use selected object or find largest mesh object
                if bpy.context.selected_objects:
                    target_object = bpy.context.selected_objects[0].name
                else:
                    # Find largest mesh object
                    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
                    if mesh_objects:
                        target_object = max(mesh_objects, key=lambda o: len(o.data.vertices)).name
                    else:
                        return {"error": "No mesh objects found in scene"}
            
            # Store object name for later steps
            obj_name = target_object
            
            # ========== STEP 1: GEOMETRY ENHANCEMENT ==========
            geom_settings = template["geometry"]
            try:
                # Apply enhancement preset
                preset = geom_settings["enhancement_preset"]
                result = self.apply_enhancement_preset(obj_name, preset)
                
                # Apply additional settings if specified
                if "subdivision_levels" in geom_settings:
                    self.apply_subdivision_surface(obj_name, geom_settings["subdivision_levels"])
                
                if "edge_bevel" in geom_settings:
                    self.add_edge_bevel(obj_name, geom_settings["edge_bevel"])
                
                if "auto_smooth" in geom_settings:
                    self.set_shading(obj_name, smooth=geom_settings["auto_smooth"])
                
                results["steps"]["geometry"] = "success"
            except Exception as e:
                results["steps"]["geometry"] = f"error: {str(e)}"
            
            # ========== STEP 2: MATERIALS ==========
            mat_settings = template["materials"]
            try:
                # Auto-enhance materials
                if mat_settings.get("auto_enhance", True):
                    result = self.auto_enhance_materials(
                        obj_name, 
                        aggressive=mat_settings.get("aggressive", False)
                    )
                
                # Apply default material if specified
                if "default_material" in mat_settings:
                    self.apply_material_preset(
                        obj_name,
                        mat_settings["default_material"]
                    )
                
                results["steps"]["materials"] = "success"
            except Exception as e:
                results["steps"]["materials"] = f"error: {str(e)}"
            
            # ========== STEP 3: LIGHTING ==========
            light_settings = template["lighting"]
            try:
                # Setup HDRI
                if light_settings.get("hdri"):
                    self.setup_hdri_lighting(
                        light_settings["hdri"],
                        strength=light_settings.get("hdri_strength", 1.0)
                    )
                
                # Apply lighting rig
                if light_settings.get("lighting_rig"):
                    self.apply_lighting_rig(
                        light_settings["lighting_rig"],
                        target_object=obj_name
                    )
                
                # Add atmosphere
                if light_settings.get("atmosphere"):
                    self.add_atmospheric_fog(light_settings["atmosphere"])
                
                results["steps"]["lighting"] = "success"
            except Exception as e:
                results["steps"]["lighting"] = f"error: {str(e)}"
            
            # ========== STEP 4: COMPOSITION ==========
            comp_settings = template["composition"]
            try:
                # Setup camera with composition
                self.auto_frame_with_composition(
                    target_object=obj_name,
                    shot_type=comp_settings.get("shot_type", "medium_shot"),
                    composition_rule=comp_settings.get("composition_rule", "rule_of_thirds"),
                    camera_angle=comp_settings.get("camera_angle", "front")
                )
                
                results["steps"]["composition"] = "success"
            except Exception as e:
                results["steps"]["composition"] = f"error: {str(e)}"
            
            # ========== STEP 5: COLOR GRADING ==========
            color_settings = template["color_grading"]
            try:
                # Apply complete color grade
                self.apply_color_grade(
                    color_settings.get("preset", "cinematic_standard")
                )
                
                # Or apply individual settings
                if "tone_mapping" in color_settings:
                    self.setup_tone_mapping(
                        color_settings["tone_mapping"],
                        exposure=color_settings.get("exposure", 0.0),
                        gamma=color_settings.get("gamma", 1.0)
                    )
                
                results["steps"]["color_grading"] = "success"
            except Exception as e:
                results["steps"]["color_grading"] = f"error: {str(e)}"
            
            # ========== STEP 6: RENDER SETTINGS ==========
            render_settings = template["render"]
            try:
                # Apply render preset if available
                if "preset" in render_settings:
                    self.configure_render_settings(render_settings["preset"])
                
                # Override samples if specified
                if "samples" in render_settings:
                    bpy.context.scene.cycles.samples = render_settings["samples"]
                
                results["steps"]["render_settings"] = "success"
            except Exception as e:
                results["steps"]["render_settings"] = f"error: {str(e)}"
            
            # ========== OPTIONAL: AUTO RENDER ==========
            if auto_render:
                try:
                    bpy.ops.render.render(write_still=False)
                    results["rendered"] = True
                except Exception as e:
                    results["render_error"] = str(e)
            
            # Format success message
            successful_steps = [step for step, status in results["steps"].items() if status == "success"]
            failed_steps = [step for step, status in results["steps"].items() if status != "success"]
            
            message = f"Scene template '{template['name']}' applied successfully!\n"
            message += f"✓ Completed steps: {', '.join(successful_steps)}\n"
            if failed_steps:
                message += f"⚠ Failed steps: {', '.join(failed_steps)}\n"
            
            results["message"] = message
            return results
            
        except Exception as e:
            return {"error": f"Scene template application failed: {str(e)}"}

    # ==================== ANIMATION SYSTEM HANDLERS ====================
    
    def get_armature_info(self, armature_name=None):
        """Get information about armatures in the scene"""
        try:
            if armature_name:
                armature = bpy.data.objects.get(armature_name)
                if not armature:
                    return {"error": f"Armature '{armature_name}' not found"}
                if armature.type != 'ARMATURE':
                    return {"error": f"Object '{armature_name}' is not an armature"}
                
                bones = []
                for bone in armature.data.bones:
                    bone_info = {
                        "name": bone.name,
                        "parent": bone.parent.name if bone.parent else None,
                        "children": [child.name for child in bone.children],
                        "head": [round(x, 4) for x in bone.head_local],
                        "tail": [round(x, 4) for x in bone.tail_local],
                    }
                    bones.append(bone_info)
                
                return {
                    "name": armature.name,
                    "bone_count": len(armature.data.bones),
                    "bones": bones,
                    "active_action": armature.animation_data.action.name if armature.animation_data and armature.animation_data.action else None
                }
            else:
                armatures = [obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE']
                return {
                    "armature_count": len(armatures),
                    "armatures": [{"name": a.name, "bone_count": len(a.data.bones)} for a in armatures]
                }
        except Exception as e:
            return {"error": str(e)}

    def get_armature_bones(self, armature_name, bone_mapping="mixamo"):
        """Get list of bones in an armature with mapping validation"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            # Standard bone names for different mappings
            BONE_MAPPINGS = {
                "mixamo": {
                    "hips": "mixamorig:Hips",
                    "spine": "mixamorig:Spine",
                    "spine1": "mixamorig:Spine1",
                    "spine2": "mixamorig:Spine2",
                    "neck": "mixamorig:Neck",
                    "head": "mixamorig:Head",
                    "left_shoulder": "mixamorig:LeftShoulder",
                    "left_arm": "mixamorig:LeftArm",
                    "left_forearm": "mixamorig:LeftForeArm",
                    "left_hand": "mixamorig:LeftHand",
                    "right_shoulder": "mixamorig:RightShoulder",
                    "right_arm": "mixamorig:RightArm",
                    "right_forearm": "mixamorig:RightForeArm",
                    "right_hand": "mixamorig:RightHand",
                    "left_upleg": "mixamorig:LeftUpLeg",
                    "left_leg": "mixamorig:LeftLeg",
                    "left_foot": "mixamorig:LeftFoot",
                    "right_upleg": "mixamorig:RightUpLeg",
                    "right_leg": "mixamorig:RightLeg",
                    "right_foot": "mixamorig:RightFoot",
                },
                "rigify": {
                    "hips": "spine",
                    "spine": "spine.001",
                    "spine1": "spine.002",
                    "spine2": "spine.003",
                    "neck": "spine.004",
                    "head": "spine.006",
                    "left_shoulder": "shoulder.L",
                    "left_arm": "upper_arm.L",
                    "left_forearm": "forearm.L",
                    "left_hand": "hand.L",
                    "right_shoulder": "shoulder.R",
                    "right_arm": "upper_arm.R",
                    "right_forearm": "forearm.R",
                    "right_hand": "hand.R",
                    "left_upleg": "thigh.L",
                    "left_leg": "shin.L",
                    "left_foot": "foot.L",
                    "right_upleg": "thigh.R",
                    "right_leg": "shin.R",
                    "right_foot": "foot.R",
                },
                "generic": {
                    "hips": "Hips",
                    "spine": "Spine",
                    "spine1": "Spine1",
                    "spine2": "Spine2",
                    "neck": "Neck",
                    "head": "Head",
                    "left_shoulder": "LeftShoulder",
                    "left_arm": "LeftArm",
                    "left_forearm": "LeftForeArm",
                    "left_hand": "LeftHand",
                    "right_shoulder": "RightShoulder",
                    "right_arm": "RightArm",
                    "right_forearm": "RightForeArm",
                    "right_hand": "RightHand",
                    "left_upleg": "LeftUpLeg",
                    "left_leg": "LeftLeg",
                    "left_foot": "LeftFoot",
                    "right_upleg": "RightUpLeg",
                    "right_leg": "RightLeg",
                    "right_foot": "RightFoot",
                }
            }
            
            mapping = BONE_MAPPINGS.get(bone_mapping, BONE_MAPPINGS["mixamo"])
            bone_names = [bone.name for bone in armature.data.bones]
            
            found = {}
            missing = []
            
            for standard_name, mapped_name in mapping.items():
                if mapped_name in bone_names:
                    found[standard_name] = mapped_name
                else:
                    missing.append(standard_name)
            
            return {
                "armature": armature_name,
                "total_bones": len(bone_names),
                "bone_names": bone_names,
                "bone_mapping": bone_mapping,
                "mapped_bones": found,
                "missing_bones": missing,
                "mapping_coverage": f"{len(found)}/{len(mapping)}"
            }
        except Exception as e:
            return {"error": str(e)}

    def set_frame_range(self, start_frame, end_frame):
        """Set the animation frame range"""
        try:
            bpy.context.scene.frame_start = start_frame
            bpy.context.scene.frame_end = end_frame
            return {"message": f"Frame range set to {start_frame} - {end_frame}"}
        except Exception as e:
            return {"error": str(e)}

    def set_current_frame(self, frame):
        """Set the current frame"""
        try:
            bpy.context.scene.frame_set(frame)
            return {"message": f"Current frame set to {frame}"}
        except Exception as e:
            return {"error": str(e)}

    def get_current_frame(self):
        """Get the current frame"""
        try:
            return {
                "current_frame": bpy.context.scene.frame_current,
                "frame_start": bpy.context.scene.frame_start,
                "frame_end": bpy.context.scene.frame_end,
                "fps": bpy.context.scene.render.fps
            }
        except Exception as e:
            return {"error": str(e)}

    def create_action(self, action_name, armature_name):
        """Create a new action for an armature"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            # Create action
            action = bpy.data.actions.new(name=action_name)
            
            # Ensure armature has animation data
            if not armature.animation_data:
                armature.animation_data_create()
            
            # Assign action
            armature.animation_data.action = action
            
            return {"message": f"Action '{action_name}' created and assigned to '{armature_name}'"}
        except Exception as e:
            return {"error": str(e)}

    def insert_keyframe(self, armature_name, bone_name, frame, rotation=None, location=None, scale=None, interpolation="BEZIER"):
        """Insert a keyframe for a bone"""
        try:
            import math
            
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            # Enter pose mode
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            pose_bone = armature.pose.bones.get(bone_name)
            if not pose_bone:
                bpy.ops.object.mode_set(mode='OBJECT')
                return {"error": f"Bone '{bone_name}' not found in armature"}
            
            bpy.context.scene.frame_set(frame)
            
            keyframed = []
            
            if rotation is not None:
                pose_bone.rotation_mode = 'XYZ'
                pose_bone.rotation_euler = [math.radians(r) for r in rotation]
                pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
                keyframed.append("rotation")
                
                # Set interpolation
                if armature.animation_data and armature.animation_data.action:
                    for fcurve in armature.animation_data.action.fcurves:
                        if bone_name in fcurve.data_path and "rotation" in fcurve.data_path:
                            for kf in fcurve.keyframe_points:
                                if abs(kf.co[0] - frame) < 0.5:
                                    kf.interpolation = interpolation
            
            if location is not None:
                pose_bone.location = location
                pose_bone.keyframe_insert(data_path="location", frame=frame)
                keyframed.append("location")
                
                if armature.animation_data and armature.animation_data.action:
                    for fcurve in armature.animation_data.action.fcurves:
                        if bone_name in fcurve.data_path and "location" in fcurve.data_path:
                            for kf in fcurve.keyframe_points:
                                if abs(kf.co[0] - frame) < 0.5:
                                    kf.interpolation = interpolation
            
            if scale is not None:
                pose_bone.scale = scale
                pose_bone.keyframe_insert(data_path="scale", frame=frame)
                keyframed.append("scale")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            return {"message": f"Keyframe inserted at frame {frame} for bone '{bone_name}': {', '.join(keyframed)}"}
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return {"error": str(e)}

    def delete_keyframe(self, armature_name, bone_name, frame):
        """Delete a keyframe for a bone"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if not armature.animation_data or not armature.animation_data.action:
                return {"error": "No action on armature"}
            
            action = armature.animation_data.action
            deleted = 0
            
            for fcurve in action.fcurves:
                if bone_name in fcurve.data_path:
                    for i, kf in enumerate(fcurve.keyframe_points):
                        if abs(kf.co[0] - frame) < 0.5:
                            fcurve.keyframe_points.remove(fcurve.keyframe_points[i])
                            deleted += 1
                            break
            
            return {"message": f"Deleted {deleted} keyframes at frame {frame} for bone '{bone_name}'"}
        except Exception as e:
            return {"error": str(e)}

    def apply_animation_preset(self, preset_name, armature_name, start_frame=1, bone_mapping="mixamo", 
                               action_name=None, duration=60, loop=False, keyframes=None):
        """Apply an animation preset to an armature"""
        try:
            import math
            
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            if not keyframes:
                return {"error": "No keyframe data provided"}
            
            # Create action
            final_action_name = action_name or f"{preset_name}_action"
            action = bpy.data.actions.new(name=final_action_name)
            
            # Ensure armature has animation data
            if not armature.animation_data:
                armature.animation_data_create()
            
            armature.animation_data.action = action
            
            # Enter pose mode
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            keyframed_bones = 0
            
            for bone_name, bone_keyframes in keyframes.items():
                pose_bone = armature.pose.bones.get(bone_name)
                if not pose_bone:
                    continue
                
                keyframed_bones += 1
                pose_bone.rotation_mode = 'XYZ'
                
                for kf in bone_keyframes:
                    frame = start_frame + kf.get("frame", 0)
                    bpy.context.scene.frame_set(frame)
                    
                    if "rotation" in kf:
                        rot = kf["rotation"]
                        pose_bone.rotation_euler = [math.radians(r) for r in rot]
                        pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
                    
                    if "location" in kf:
                        pose_bone.location = kf["location"]
                        pose_bone.keyframe_insert(data_path="location", frame=frame)
                    
                    if "scale" in kf:
                        pose_bone.scale = kf["scale"]
                        pose_bone.keyframe_insert(data_path="scale", frame=frame)
                    
                    # Set interpolation
                    interp = kf.get("interpolation", "BEZIER")
                    for fcurve in action.fcurves:
                        if bone_name in fcurve.data_path:
                            for keyframe in fcurve.keyframe_points:
                                if abs(keyframe.co[0] - frame) < 0.5:
                                    keyframe.interpolation = interp
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Set frame range
            end_frame = start_frame + duration - 1
            bpy.context.scene.frame_start = start_frame
            bpy.context.scene.frame_end = end_frame
            bpy.context.scene.frame_set(start_frame)
            
            return {
                "message": f"Animation preset '{preset_name}' applied to '{armature_name}'",
                "action_name": final_action_name,
                "keyframed_bones": keyframed_bones,
                "frame_range": f"{start_frame} - {end_frame}",
                "loop": loop
            }
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return {"error": str(e)}

    def set_bone_pose(self, armature_name, bone_name, rotation=None, location=None, scale=None):
        """Set the pose of a bone without keyframing"""
        try:
            import math
            
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            pose_bone = armature.pose.bones.get(bone_name)
            if not pose_bone:
                bpy.ops.object.mode_set(mode='OBJECT')
                return {"error": f"Bone '{bone_name}' not found"}
            
            changes = []
            if rotation is not None:
                pose_bone.rotation_mode = 'XYZ'
                pose_bone.rotation_euler = [math.radians(r) for r in rotation]
                changes.append("rotation")
            
            if location is not None:
                pose_bone.location = location
                changes.append("location")
            
            if scale is not None:
                pose_bone.scale = scale
                changes.append("scale")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            return {"message": f"Bone '{bone_name}' pose updated: {', '.join(changes)}"}
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return {"error": str(e)}

    def reset_bone_pose(self, armature_name, bone_name=None):
        """Reset bone(s) to rest pose"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            if armature.type != 'ARMATURE':
                return {"error": f"Object '{armature_name}' is not an armature"}
            
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')
            
            if bone_name:
                pose_bone = armature.pose.bones.get(bone_name)
                if not pose_bone:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    return {"error": f"Bone '{bone_name}' not found"}
                
                pose_bone.location = (0, 0, 0)
                pose_bone.rotation_quaternion = (1, 0, 0, 0)
                pose_bone.rotation_euler = (0, 0, 0)
                pose_bone.scale = (1, 1, 1)
                message = f"Bone '{bone_name}' reset to rest pose"
            else:
                for pose_bone in armature.pose.bones:
                    pose_bone.location = (0, 0, 0)
                    pose_bone.rotation_quaternion = (1, 0, 0, 0)
                    pose_bone.rotation_euler = (0, 0, 0)
                    pose_bone.scale = (1, 1, 1)
                message = f"All bones reset to rest pose"
            
            bpy.ops.object.mode_set(mode='OBJECT')
            return {"message": message}
        except Exception as e:
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            return {"error": str(e)}

    def create_nla_track(self, armature_name, track_name):
        """Create a new NLA track"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            
            if not armature.animation_data:
                armature.animation_data_create()
            
            track = armature.animation_data.nla_tracks.new()
            track.name = track_name
            
            return {"message": f"NLA track '{track_name}' created on '{armature_name}'"}
        except Exception as e:
            return {"error": str(e)}

    def push_action_to_nla(self, armature_name, action_name, track_name=None, start_frame=1):
        """Push an action to an NLA track"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            
            action = bpy.data.actions.get(action_name)
            if not action:
                return {"error": f"Action '{action_name}' not found"}
            
            if not armature.animation_data:
                armature.animation_data_create()
            
            # Get or create track
            if track_name:
                track = None
                for t in armature.animation_data.nla_tracks:
                    if t.name == track_name:
                        track = t
                        break
                if not track:
                    track = armature.animation_data.nla_tracks.new()
                    track.name = track_name
            else:
                track = armature.animation_data.nla_tracks.new()
                track.name = f"{action_name}_track"
            
            # Create strip
            strip = track.strips.new(action_name, start_frame, action)
            
            return {
                "message": f"Action '{action_name}' pushed to NLA track '{track.name}'",
                "strip_name": strip.name,
                "start_frame": start_frame,
                "end_frame": int(strip.frame_end)
            }
        except Exception as e:
            return {"error": str(e)}

    def play_animation(self, start_frame=None, end_frame=None, loop=False):
        """Play animation in viewport"""
        try:
            if start_frame is not None:
                bpy.context.scene.frame_start = start_frame
            if end_frame is not None:
                bpy.context.scene.frame_end = end_frame
            
            bpy.context.scene.frame_set(bpy.context.scene.frame_start)
            bpy.ops.screen.animation_play()
            
            return {
                "message": "Animation playing",
                "frame_range": f"{bpy.context.scene.frame_start} - {bpy.context.scene.frame_end}"
            }
        except Exception as e:
            return {"error": str(e)}

    def stop_animation(self):
        """Stop animation playback"""
        try:
            bpy.ops.screen.animation_cancel()
            return {"message": "Animation stopped"}
        except Exception as e:
            return {"error": str(e)}

    def export_animation_fbx(self, filepath, armature_name, action_name=None, include_mesh=True):
        """Export animation to FBX"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            
            # Set action if specified
            if action_name:
                action = bpy.data.actions.get(action_name)
                if not action:
                    return {"error": f"Action '{action_name}' not found"}
                if armature.animation_data:
                    armature.animation_data.action = action
            
            # Select armature and optionally mesh children
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            
            if include_mesh:
                for child in armature.children:
                    if child.type == 'MESH':
                        child.select_set(True)
            
            bpy.context.view_layer.objects.active = armature
            
            # Export
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                bake_anim=True,
                bake_anim_use_all_actions=False if action_name else True,
                bake_anim_force_startend_keying=True,
                add_leaf_bones=False,
                path_mode='AUTO'
            )
            
            return {"message": f"Animation exported to '{filepath}'"}
        except Exception as e:
            return {"error": str(e)}

    def export_animation_gltf(self, filepath, armature_name, action_name=None, include_mesh=True, export_format="GLB"):
        """Export animation to glTF/GLB format"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            
            # Set action if specified
            if action_name:
                action = bpy.data.actions.get(action_name)
                if not action:
                    return {"error": f"Action '{action_name}' not found"}
                if armature.animation_data:
                    armature.animation_data.action = action
            
            # Select armature and optionally mesh children
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            
            if include_mesh:
                for child in armature.children:
                    if child.type == 'MESH':
                        child.select_set(True)
            
            bpy.context.view_layer.objects.active = armature
            
            # Determine export format
            export_fmt = export_format.upper()
            if export_fmt not in ["GLB", "GLTF_SEPARATE", "GLTF_EMBEDDED"]:
                export_fmt = "GLB"
            
            # Export
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                use_selection=True,
                export_format=export_fmt,
                export_animations=True,
                export_animation_mode='ACTIONS' if action_name else 'ACTIVE_ACTIONS',
                export_nla_strips=False if action_name else True,
                export_skins=True,
                export_morph=True,
                export_apply=False
            )
            
            return {"message": f"Animation exported to '{filepath}' (format: {export_fmt})"}
        except Exception as e:
            return {"error": str(e)}

    def list_actions(self, armature_name=None):
        """List all actions"""
        try:
            actions = []
            for action in bpy.data.actions:
                action_info = {
                    "name": action.name,
                    "frame_range": [int(action.frame_range[0]), int(action.frame_range[1])],
                    "fcurve_count": len(action.fcurves)
                }
                actions.append(action_info)
            
            return {"action_count": len(actions), "actions": actions}
        except Exception as e:
            return {"error": str(e)}

    def set_active_action(self, armature_name, action_name):
        """Set the active action for an armature"""
        try:
            armature = bpy.data.objects.get(armature_name)
            if not armature:
                return {"error": f"Armature '{armature_name}' not found"}
            
            action = bpy.data.actions.get(action_name)
            if not action:
                return {"error": f"Action '{action_name}' not found"}
            
            if not armature.animation_data:
                armature.animation_data_create()
            
            armature.animation_data.action = action
            
            return {"message": f"Action '{action_name}' set as active on '{armature_name}'"}
        except Exception as e:
            return {"error": str(e)}

    def duplicate_action(self, source_action, new_name):
        """Duplicate an action"""
        try:
            action = bpy.data.actions.get(source_action)
            if not action:
                return {"error": f"Action '{source_action}' not found"}
            
            new_action = action.copy()
            new_action.name = new_name
            
            return {"message": f"Action '{source_action}' duplicated as '{new_action.name}'"}
        except Exception as e:
            return {"error": str(e)}

    def search_polyhaven_assets(self, asset_type=None, categories=None):
        """Search for assets from Polyhaven with optional filtering"""
        try:
            url = "https://api.polyhaven.com/assets"
            params = {}

            if asset_type and asset_type != "all":
                if asset_type not in ["hdris", "textures", "models"]:
                    return {"error": f"Invalid asset type: {asset_type}. Must be one of: hdris, textures, models, all"}
                params["type"] = asset_type

            if categories:
                params["categories"] = categories

            response = requests.get(url, params=params, headers=REQ_HEADERS)
            if response.status_code == 200:
                # Limit the response size to avoid overwhelming Blender
                assets = response.json()
                # Return only the first 20 assets to keep response size manageable
                limited_assets = {}
                for i, (key, value) in enumerate(assets.items()):
                    if i >= 20:  # Limit to 20 assets
                        break
                    limited_assets[key] = value

                return {"assets": limited_assets, "total_count": len(assets), "returned_count": len(limited_assets)}
            else:
                return {"error": f"API request failed with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def download_polyhaven_asset(self, asset_id, asset_type, resolution="1k", file_format=None):
        try:
            # First get the files information
            files_response = requests.get(f"https://api.polyhaven.com/files/{asset_id}", headers=REQ_HEADERS)
            if files_response.status_code != 200:
                return {"error": f"Failed to get asset files: {files_response.status_code}"}

            files_data = files_response.json()

            # Handle different asset types
            if asset_type == "hdris":
                # For HDRIs, download the .hdr or .exr file
                if not file_format:
                    file_format = "hdr"  # Default format for HDRIs

                if "hdri" in files_data and resolution in files_data["hdri"] and file_format in files_data["hdri"][resolution]:
                    file_info = files_data["hdri"][resolution][file_format]
                    file_url = file_info["url"]

                    # For HDRIs, we need to save to a temporary file first
                    # since Blender can't properly load HDR data directly from memory
                    with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp_file:
                        # Download the file
                        response = requests.get(file_url, headers=REQ_HEADERS)
                        if response.status_code != 200:
                            return {"error": f"Failed to download HDRI: {response.status_code}"}

                        tmp_file.write(response.content)
                        tmp_path = tmp_file.name

                    try:
                        # Create a new world if none exists
                        if not bpy.data.worlds:
                            bpy.data.worlds.new("World")

                        world = bpy.data.worlds[0]
                        world.use_nodes = True
                        node_tree = world.node_tree

                        # Clear existing nodes
                        for node in node_tree.nodes:
                            node_tree.nodes.remove(node)

                        # Create nodes
                        tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
                        tex_coord.location = (-800, 0)

                        mapping = node_tree.nodes.new(type='ShaderNodeMapping')
                        mapping.location = (-600, 0)

                        # Load the image from the temporary file
                        env_tex = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
                        env_tex.location = (-400, 0)
                        env_tex.image = bpy.data.images.load(tmp_path)

                        # Use a color space that exists in all Blender versions
                        if file_format.lower() == 'exr':
                            # Try to use Linear color space for EXR files
                            try:
                                env_tex.image.colorspace_settings.name = 'Linear'
                            except:
                                # Fallback to Non-Color if Linear isn't available
                                env_tex.image.colorspace_settings.name = 'Non-Color'
                        else:  # hdr
                            # For HDR files, try these options in order
                            for color_space in ['Linear', 'Linear Rec.709', 'Non-Color']:
                                try:
                                    env_tex.image.colorspace_settings.name = color_space
                                    break  # Stop if we successfully set a color space
                                except:
                                    continue

                        background = node_tree.nodes.new(type='ShaderNodeBackground')
                        background.location = (-200, 0)

                        output = node_tree.nodes.new(type='ShaderNodeOutputWorld')
                        output.location = (0, 0)

                        # Connect nodes
                        node_tree.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
                        node_tree.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
                        node_tree.links.new(env_tex.outputs['Color'], background.inputs['Color'])
                        node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])

                        # Set as active world
                        bpy.context.scene.world = world

                        # Clean up temporary file
                        try:
                            tempfile._cleanup()  # This will clean up all temporary files
                        except:
                            pass

                        return {
                            "success": True,
                            "message": f"HDRI {asset_id} imported successfully",
                            "image_name": env_tex.image.name
                        }
                    except Exception as e:
                        return {"error": f"Failed to set up HDRI in Blender: {str(e)}"}
                else:
                    return {"error": f"Requested resolution or format not available for this HDRI"}

            elif asset_type == "textures":
                if not file_format:
                    file_format = "jpg"  # Default format for textures

                downloaded_maps = {}

                try:
                    for map_type in files_data:
                        if map_type not in ["blend", "gltf"]:  # Skip non-texture files
                            if resolution in files_data[map_type] and file_format in files_data[map_type][resolution]:
                                file_info = files_data[map_type][resolution][file_format]
                                file_url = file_info["url"]

                                # Use NamedTemporaryFile like we do for HDRIs
                                with tempfile.NamedTemporaryFile(suffix=f".{file_format}", delete=False) as tmp_file:
                                    # Download the file
                                    response = requests.get(file_url, headers=REQ_HEADERS)
                                    if response.status_code == 200:
                                        tmp_file.write(response.content)
                                        tmp_path = tmp_file.name

                                        # Load image from temporary file
                                        image = bpy.data.images.load(tmp_path)
                                        image.name = f"{asset_id}_{map_type}.{file_format}"

                                        # Pack the image into .blend file
                                        image.pack()

                                        # Set color space based on map type
                                        if map_type in ['color', 'diffuse', 'albedo']:
                                            try:
                                                image.colorspace_settings.name = 'sRGB'
                                            except:
                                                pass
                                        else:
                                            try:
                                                image.colorspace_settings.name = 'Non-Color'
                                            except:
                                                pass

                                        downloaded_maps[map_type] = image

                                        # Clean up temporary file
                                        try:
                                            os.unlink(tmp_path)
                                        except:
                                            pass

                    if not downloaded_maps:
                        return {"error": f"No texture maps found for the requested resolution and format"}

                    # Create a new material with the downloaded textures
                    mat = bpy.data.materials.new(name=asset_id)
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links

                    # Clear default nodes
                    for node in nodes:
                        nodes.remove(node)

                    # Create output node
                    output = nodes.new(type='ShaderNodeOutputMaterial')
                    output.location = (300, 0)

                    # Create principled BSDF node
                    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
                    principled.location = (0, 0)
                    links.new(principled.outputs[0], output.inputs[0])

                    # Add texture nodes based on available maps
                    tex_coord = nodes.new(type='ShaderNodeTexCoord')
                    tex_coord.location = (-800, 0)

                    mapping = nodes.new(type='ShaderNodeMapping')
                    mapping.location = (-600, 0)
                    mapping.vector_type = 'TEXTURE'  # Changed from default 'POINT' to 'TEXTURE'
                    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

                    # Position offset for texture nodes
                    x_pos = -400
                    y_pos = 300

                    # Connect different texture maps
                    for map_type, image in downloaded_maps.items():
                        tex_node = nodes.new(type='ShaderNodeTexImage')
                        tex_node.location = (x_pos, y_pos)
                        tex_node.image = image

                        # Set color space based on map type
                        if map_type.lower() in ['color', 'diffuse', 'albedo']:
                            try:
                                tex_node.image.colorspace_settings.name = 'sRGB'
                            except:
                                pass  # Use default if sRGB not available
                        else:
                            try:
                                tex_node.image.colorspace_settings.name = 'Non-Color'
                            except:
                                pass  # Use default if Non-Color not available

                        links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])

                        # Connect to appropriate input on Principled BSDF
                        if map_type.lower() in ['color', 'diffuse', 'albedo']:
                            links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
                        elif map_type.lower() in ['roughness', 'rough']:
                            links.new(tex_node.outputs['Color'], principled.inputs['Roughness'])
                        elif map_type.lower() in ['metallic', 'metalness', 'metal']:
                            links.new(tex_node.outputs['Color'], principled.inputs['Metallic'])
                        elif map_type.lower() in ['normal', 'nor']:
                            # Add normal map node
                            normal_map = nodes.new(type='ShaderNodeNormalMap')
                            normal_map.location = (x_pos + 200, y_pos)
                            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                            links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
                        elif map_type in ['displacement', 'disp', 'height']:
                            # Add displacement node
                            disp_node = nodes.new(type='ShaderNodeDisplacement')
                            disp_node.location = (x_pos + 200, y_pos - 200)
                            links.new(tex_node.outputs['Color'], disp_node.inputs['Height'])
                            links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])

                        y_pos -= 250

                    return {
                        "success": True,
                        "message": f"Texture {asset_id} imported as material",
                        "material": mat.name,
                        "maps": list(downloaded_maps.keys())
                    }

                except Exception as e:
                    return {"error": f"Failed to process textures: {str(e)}"}

            elif asset_type == "models":
                # For models, prefer glTF format if available
                if not file_format:
                    file_format = "gltf"  # Default format for models

                if file_format in files_data and resolution in files_data[file_format]:
                    file_info = files_data[file_format][resolution][file_format]
                    file_url = file_info["url"]

                    # Create a temporary directory to store the model and its dependencies
                    temp_dir = tempfile.mkdtemp()
                    main_file_path = ""

                    try:
                        # Download the main model file
                        main_file_name = file_url.split("/")[-1]
                        main_file_path = os.path.join(temp_dir, main_file_name)

                        response = requests.get(file_url, headers=REQ_HEADERS)
                        if response.status_code != 200:
                            return {"error": f"Failed to download model: {response.status_code}"}

                        with open(main_file_path, "wb") as f:
                            f.write(response.content)

                        # Check for included files and download them
                        if "include" in file_info and file_info["include"]:
                            for include_path, include_info in file_info["include"].items():
                                # Get the URL for the included file - this is the fix
                                include_url = include_info["url"]

                                # Create the directory structure for the included file
                                include_file_path = os.path.join(temp_dir, include_path)
                                os.makedirs(os.path.dirname(include_file_path), exist_ok=True)

                                # Download the included file
                                include_response = requests.get(include_url, headers=REQ_HEADERS)
                                if include_response.status_code == 200:
                                    with open(include_file_path, "wb") as f:
                                        f.write(include_response.content)
                                else:
                                    print(f"Failed to download included file: {include_path}")

                        # Import the model into Blender
                        if file_format == "gltf" or file_format == "glb":
                            bpy.ops.import_scene.gltf(filepath=main_file_path)
                        elif file_format == "fbx":
                            bpy.ops.import_scene.fbx(filepath=main_file_path)
                        elif file_format == "obj":
                            bpy.ops.import_scene.obj(filepath=main_file_path)
                        elif file_format == "blend":
                            # For blend files, we need to append or link
                            with bpy.data.libraries.load(main_file_path, link=False) as (data_from, data_to):
                                data_to.objects = data_from.objects

                            # Link the objects to the scene
                            for obj in data_to.objects:
                                if obj is not None:
                                    bpy.context.collection.objects.link(obj)
                        else:
                            return {"error": f"Unsupported model format: {file_format}"}

                        # Get the names of imported objects
                        imported_objects = [obj.name for obj in bpy.context.selected_objects]

                        return {
                            "success": True,
                            "message": f"Model {asset_id} imported successfully",
                            "imported_objects": imported_objects
                        }
                    except Exception as e:
                        return {"error": f"Failed to import model: {str(e)}"}
                    finally:
                        # Clean up temporary directory
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                else:
                    return {"error": f"Requested format or resolution not available for this model"}

            else:
                return {"error": f"Unsupported asset type: {asset_type}"}

        except Exception as e:
            return {"error": f"Failed to download asset: {str(e)}"}

    def set_texture(self, object_name, texture_id):
        """Apply a previously downloaded Polyhaven texture to an object by creating a new material"""
        try:
            # Get the object
            obj = bpy.data.objects.get(object_name)
            if not obj:
                return {"error": f"Object not found: {object_name}"}

            # Make sure object can accept materials
            if not hasattr(obj, 'data') or not hasattr(obj.data, 'materials'):
                return {"error": f"Object {object_name} cannot accept materials"}

            # Find all images related to this texture and ensure they're properly loaded
            texture_images = {}
            for img in bpy.data.images:
                if img.name.startswith(texture_id + "_"):
                    # Extract the map type from the image name
                    map_type = img.name.split('_')[-1].split('.')[0]

                    # Force a reload of the image
                    img.reload()

                    # Ensure proper color space
                    if map_type.lower() in ['color', 'diffuse', 'albedo']:
                        try:
                            img.colorspace_settings.name = 'sRGB'
                        except:
                            pass
                    else:
                        try:
                            img.colorspace_settings.name = 'Non-Color'
                        except:
                            pass

                    # Ensure the image is packed
                    if not img.packed_file:
                        img.pack()

                    texture_images[map_type] = img
                    print(f"Loaded texture map: {map_type} - {img.name}")

                    # Debug info
                    print(f"Image size: {img.size[0]}x{img.size[1]}")
                    print(f"Color space: {img.colorspace_settings.name}")
                    print(f"File format: {img.file_format}")
                    print(f"Is packed: {bool(img.packed_file)}")

            if not texture_images:
                return {"error": f"No texture images found for: {texture_id}. Please download the texture first."}

            # Create a new material
            new_mat_name = f"{texture_id}_material_{object_name}"

            # Remove any existing material with this name to avoid conflicts
            existing_mat = bpy.data.materials.get(new_mat_name)
            if existing_mat:
                bpy.data.materials.remove(existing_mat)

            new_mat = bpy.data.materials.new(name=new_mat_name)
            new_mat.use_nodes = True

            # Set up the material nodes
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            # Clear default nodes
            nodes.clear()

            # Create output node
            output = nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (600, 0)

            # Create principled BSDF node
            principled = nodes.new(type='ShaderNodeBsdfPrincipled')
            principled.location = (300, 0)
            links.new(principled.outputs[0], output.inputs[0])

            # Add texture nodes based on available maps
            tex_coord = nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-800, 0)

            mapping = nodes.new(type='ShaderNodeMapping')
            mapping.location = (-600, 0)
            mapping.vector_type = 'TEXTURE'  # Changed from default 'POINT' to 'TEXTURE'
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

            # Position offset for texture nodes
            x_pos = -400
            y_pos = 300

            # Connect different texture maps
            for map_type, image in texture_images.items():
                tex_node = nodes.new(type='ShaderNodeTexImage')
                tex_node.location = (x_pos, y_pos)
                tex_node.image = image

                # Set color space based on map type
                if map_type.lower() in ['color', 'diffuse', 'albedo']:
                    try:
                        tex_node.image.colorspace_settings.name = 'sRGB'
                    except:
                        pass  # Use default if sRGB not available
                else:
                    try:
                        tex_node.image.colorspace_settings.name = 'Non-Color'
                    except:
                        pass  # Use default if Non-Color not available

                links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])

                # Connect to appropriate input on Principled BSDF
                if map_type.lower() in ['color', 'diffuse', 'albedo']:
                    links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
                elif map_type.lower() in ['roughness', 'rough']:
                    links.new(tex_node.outputs['Color'], principled.inputs['Roughness'])
                elif map_type.lower() in ['metallic', 'metalness', 'metal']:
                    links.new(tex_node.outputs['Color'], principled.inputs['Metallic'])
                elif map_type.lower() in ['normal', 'nor', 'dx', 'gl']:
                    # Add normal map node
                    normal_map = nodes.new(type='ShaderNodeNormalMap')
                    normal_map.location = (x_pos + 200, y_pos)
                    links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                    links.new(normal_map.outputs['Normal'], principled.inputs['Normal'])
                elif map_type.lower() in ['displacement', 'disp', 'height']:
                    # Add displacement node
                    disp_node = nodes.new(type='ShaderNodeDisplacement')
                    disp_node.location = (x_pos + 200, y_pos - 200)
                    disp_node.inputs['Scale'].default_value = 0.1  # Reduce displacement strength
                    links.new(tex_node.outputs['Color'], disp_node.inputs['Height'])
                    links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])

                y_pos -= 250

            # Second pass: Connect nodes with proper handling for special cases
            texture_nodes = {}

            # First find all texture nodes and store them by map type
            for node in nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    for map_type, image in texture_images.items():
                        if node.image == image:
                            texture_nodes[map_type] = node
                            break

            # Now connect everything using the nodes instead of images
            # Handle base color (diffuse)
            for map_name in ['color', 'diffuse', 'albedo']:
                if map_name in texture_nodes:
                    links.new(texture_nodes[map_name].outputs['Color'], principled.inputs['Base Color'])
                    print(f"Connected {map_name} to Base Color")
                    break

            # Handle roughness
            for map_name in ['roughness', 'rough']:
                if map_name in texture_nodes:
                    links.new(texture_nodes[map_name].outputs['Color'], principled.inputs['Roughness'])
                    print(f"Connected {map_name} to Roughness")
                    break

            # Handle metallic
            for map_name in ['metallic', 'metalness', 'metal']:
                if map_name in texture_nodes:
                    links.new(texture_nodes[map_name].outputs['Color'], principled.inputs['Metallic'])
                    print(f"Connected {map_name} to Metallic")
                    break

            # Handle normal maps
            for map_name in ['gl', 'dx', 'nor']:
                if map_name in texture_nodes:
                    normal_map_node = nodes.new(type='ShaderNodeNormalMap')
                    normal_map_node.location = (100, 100)
                    links.new(texture_nodes[map_name].outputs['Color'], normal_map_node.inputs['Color'])
                    links.new(normal_map_node.outputs['Normal'], principled.inputs['Normal'])
                    print(f"Connected {map_name} to Normal")
                    break

            # Handle displacement
            for map_name in ['displacement', 'disp', 'height']:
                if map_name in texture_nodes:
                    disp_node = nodes.new(type='ShaderNodeDisplacement')
                    disp_node.location = (300, -200)
                    disp_node.inputs['Scale'].default_value = 0.1  # Reduce displacement strength
                    links.new(texture_nodes[map_name].outputs['Color'], disp_node.inputs['Height'])
                    links.new(disp_node.outputs['Displacement'], output.inputs['Displacement'])
                    print(f"Connected {map_name} to Displacement")
                    break

            # Handle ARM texture (Ambient Occlusion, Roughness, Metallic)
            if 'arm' in texture_nodes:
                separate_rgb = nodes.new(type='ShaderNodeSeparateRGB')
                separate_rgb.location = (-200, -100)
                links.new(texture_nodes['arm'].outputs['Color'], separate_rgb.inputs['Image'])

                # Connect Roughness (G) if no dedicated roughness map
                if not any(map_name in texture_nodes for map_name in ['roughness', 'rough']):
                    links.new(separate_rgb.outputs['G'], principled.inputs['Roughness'])
                    print("Connected ARM.G to Roughness")

                # Connect Metallic (B) if no dedicated metallic map
                if not any(map_name in texture_nodes for map_name in ['metallic', 'metalness', 'metal']):
                    links.new(separate_rgb.outputs['B'], principled.inputs['Metallic'])
                    print("Connected ARM.B to Metallic")

                # For AO (R channel), multiply with base color if we have one
                base_color_node = None
                for map_name in ['color', 'diffuse', 'albedo']:
                    if map_name in texture_nodes:
                        base_color_node = texture_nodes[map_name]
                        break

                if base_color_node:
                    mix_node = nodes.new(type='ShaderNodeMixRGB')
                    mix_node.location = (100, 200)
                    mix_node.blend_type = 'MULTIPLY'
                    mix_node.inputs['Fac'].default_value = 0.8  # 80% influence

                    # Disconnect direct connection to base color
                    for link in base_color_node.outputs['Color'].links:
                        if link.to_socket == principled.inputs['Base Color']:
                            links.remove(link)

                    # Connect through the mix node
                    links.new(base_color_node.outputs['Color'], mix_node.inputs[1])
                    links.new(separate_rgb.outputs['R'], mix_node.inputs[2])
                    links.new(mix_node.outputs['Color'], principled.inputs['Base Color'])
                    print("Connected ARM.R to AO mix with Base Color")

            # Handle AO (Ambient Occlusion) if separate
            if 'ao' in texture_nodes:
                base_color_node = None
                for map_name in ['color', 'diffuse', 'albedo']:
                    if map_name in texture_nodes:
                        base_color_node = texture_nodes[map_name]
                        break

                if base_color_node:
                    mix_node = nodes.new(type='ShaderNodeMixRGB')
                    mix_node.location = (100, 200)
                    mix_node.blend_type = 'MULTIPLY'
                    mix_node.inputs['Fac'].default_value = 0.8  # 80% influence

                    # Disconnect direct connection to base color
                    for link in base_color_node.outputs['Color'].links:
                        if link.to_socket == principled.inputs['Base Color']:
                            links.remove(link)

                    # Connect through the mix node
                    links.new(base_color_node.outputs['Color'], mix_node.inputs[1])
                    links.new(texture_nodes['ao'].outputs['Color'], mix_node.inputs[2])
                    links.new(mix_node.outputs['Color'], principled.inputs['Base Color'])
                    print("Connected AO to mix with Base Color")

            # CRITICAL: Make sure to clear all existing materials from the object
            while len(obj.data.materials) > 0:
                obj.data.materials.pop(index=0)

            # Assign the new material to the object
            obj.data.materials.append(new_mat)

            # CRITICAL: Make the object active and select it
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

            # CRITICAL: Force Blender to update the material
            bpy.context.view_layer.update()

            # Get the list of texture maps
            texture_maps = list(texture_images.keys())

            # Get info about texture nodes for debugging
            material_info = {
                "name": new_mat.name,
                "has_nodes": new_mat.use_nodes,
                "node_count": len(new_mat.node_tree.nodes),
                "texture_nodes": []
            }

            for node in new_mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    connections = []
                    for output in node.outputs:
                        for link in output.links:
                            connections.append(f"{output.name} → {link.to_node.name}.{link.to_socket.name}")

                    material_info["texture_nodes"].append({
                        "name": node.name,
                        "image": node.image.name,
                        "colorspace": node.image.colorspace_settings.name,
                        "connections": connections
                    })

            return {
                "success": True,
                "message": f"Created new material and applied texture {texture_id} to {object_name}",
                "material": new_mat.name,
                "maps": texture_maps,
                "material_info": material_info
            }

        except Exception as e:
            print(f"Error in set_texture: {str(e)}")
            traceback.print_exc()
            return {"error": f"Failed to apply texture: {str(e)}"}

    def get_polyhaven_status(self):
        """Get the current status of PolyHaven integration"""
        enabled = bpy.context.scene.blendermcp_use_polyhaven
        if enabled:
            return {"enabled": True, "message": "PolyHaven integration is enabled and ready to use."}
        else:
            return {
                "enabled": False,
                "message": """PolyHaven integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Check the 'Use assets from Poly Haven' checkbox
                            3. Restart the connection to Claude"""
        }

    #region Hyper3D
    def get_hyper3d_status(self):
        """Get the current status of Hyper3D Rodin integration"""
        enabled = bpy.context.scene.blendermcp_use_hyper3d
        if enabled:
            if not bpy.context.scene.blendermcp_hyper3d_api_key:
                return {
                    "enabled": False,
                    "message": """Hyper3D Rodin integration is currently enabled, but API key is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Hyper3D Rodin 3D model generation' checkbox checked
                                3. Choose the right plaform and fill in the API Key
                                4. Restart the connection to Claude"""
                }
            mode = bpy.context.scene.blendermcp_hyper3d_mode
            message = f"Hyper3D Rodin integration is enabled and ready to use. Mode: {mode}. " + \
                f"Key type: {'private' if bpy.context.scene.blendermcp_hyper3d_api_key != RODIN_FREE_TRIAL_KEY else 'free_trial'}"
            return {
                "enabled": True,
                "message": message
            }
        else:
            return {
                "enabled": False,
                "message": """Hyper3D Rodin integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Check the 'Use Hyper3D Rodin 3D model generation' checkbox
                            3. Restart the connection to Claude"""
            }

    def create_rodin_job(self, *args, **kwargs):
        match bpy.context.scene.blendermcp_hyper3d_mode:
            case "MAIN_SITE":
                return self.create_rodin_job_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.create_rodin_job_fal_ai(*args, **kwargs)
            case _:
                return f"Error: Unknown Hyper3D Rodin mode!"

    def create_rodin_job_main_site(
            self,
            text_prompt: str=None,
            images: list[tuple[str, str]]=None,
            bbox_condition=None
        ):
        try:
            if images is None:
                images = []
            """Call Rodin API, get the job uuid and subscription key"""
            files = [
                *[("images", (f"{i:04d}{img_suffix}", img)) for i, (img_suffix, img) in enumerate(images)],
                ("tier", (None, "Sketch")),
                ("mesh_mode", (None, "Raw")),
            ]
            if text_prompt:
                files.append(("prompt", (None, text_prompt)))
            if bbox_condition:
                files.append(("bbox_condition", (None, json.dumps(bbox_condition))))
            response = requests.post(
                "https://hyperhuman.deemos.com/api/v2/rodin",
                headers={
                    "Authorization": f"Bearer {bpy.context.scene.blendermcp_hyper3d_api_key}",
                },
                files=files
            )
            data = response.json()
            return data
        except Exception as e:
            return {"error": str(e)}

    def create_rodin_job_fal_ai(
            self,
            text_prompt: str=None,
            images: list[tuple[str, str]]=None,
            bbox_condition=None
        ):
        try:
            req_data = {
                "tier": "Sketch",
            }
            if images:
                req_data["input_image_urls"] = images
            if text_prompt:
                req_data["prompt"] = text_prompt
            if bbox_condition:
                req_data["bbox_condition"] = bbox_condition
            response = requests.post(
                "https://queue.fal.run/fal-ai/hyper3d/rodin",
                headers={
                    "Authorization": f"Key {bpy.context.scene.blendermcp_hyper3d_api_key}",
                    "Content-Type": "application/json",
                },
                json=req_data
            )
            data = response.json()
            return data
        except Exception as e:
            return {"error": str(e)}

    def poll_rodin_job_status(self, *args, **kwargs):
        match bpy.context.scene.blendermcp_hyper3d_mode:
            case "MAIN_SITE":
                return self.poll_rodin_job_status_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.poll_rodin_job_status_fal_ai(*args, **kwargs)
            case _:
                return f"Error: Unknown Hyper3D Rodin mode!"

    def poll_rodin_job_status_main_site(self, subscription_key: str):
        """Call the job status API to get the job status"""
        response = requests.post(
            "https://hyperhuman.deemos.com/api/v2/status",
            headers={
                "Authorization": f"Bearer {bpy.context.scene.blendermcp_hyper3d_api_key}",
            },
            json={
                "subscription_key": subscription_key,
            },
        )
        data = response.json()
        return {
            "status_list": [i["status"] for i in data["jobs"]]
        }

    def poll_rodin_job_status_fal_ai(self, request_id: str):
        """Call the job status API to get the job status"""
        response = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}/status",
            headers={
                "Authorization": f"KEY {bpy.context.scene.blendermcp_hyper3d_api_key}",
            },
        )
        data = response.json()
        return data

    @staticmethod
    def _clean_imported_glb(filepath, mesh_name=None):
        # Get the set of existing objects before import
        existing_objects = set(bpy.data.objects)

        # Import the GLB file
        bpy.ops.import_scene.gltf(filepath=filepath)

        # Ensure the context is updated
        bpy.context.view_layer.update()

        # Get all imported objects
        imported_objects = list(set(bpy.data.objects) - existing_objects)
        # imported_objects = [obj for obj in bpy.context.view_layer.objects if obj.select_get()]

        if not imported_objects:
            print("Error: No objects were imported.")
            return

        # Identify the mesh object
        mesh_obj = None

        if len(imported_objects) == 1 and imported_objects[0].type == 'MESH':
            mesh_obj = imported_objects[0]
            print("Single mesh imported, no cleanup needed.")
        else:
            if len(imported_objects) == 2:
                empty_objs = [i for i in imported_objects if i.type == "EMPTY"]
                if len(empty_objs) != 1:
                    print("Error: Expected an empty node with one mesh child or a single mesh object.")
                    return
                parent_obj = empty_objs.pop()
                if len(parent_obj.children) == 1:
                    potential_mesh = parent_obj.children[0]
                    if potential_mesh.type == 'MESH':
                        print("GLB structure confirmed: Empty node with one mesh child.")

                        # Unparent the mesh from the empty node
                        potential_mesh.parent = None

                        # Remove the empty node
                        bpy.data.objects.remove(parent_obj)
                        print("Removed empty node, keeping only the mesh.")

                        mesh_obj = potential_mesh
                    else:
                        print("Error: Child is not a mesh object.")
                        return
                else:
                    print("Error: Expected an empty node with one mesh child or a single mesh object.")
                    return
            else:
                print("Error: Expected an empty node with one mesh child or a single mesh object.")
                return

        # Rename the mesh if needed
        try:
            if mesh_obj and mesh_obj.name is not None and mesh_name:
                mesh_obj.name = mesh_name
                if mesh_obj.data.name is not None:
                    mesh_obj.data.name = mesh_name
                print(f"Mesh renamed to: {mesh_name}")
        except Exception as e:
            print("Having issue with renaming, give up renaming.")

        return mesh_obj

    def import_generated_asset(self, *args, **kwargs):
        match bpy.context.scene.blendermcp_hyper3d_mode:
            case "MAIN_SITE":
                return self.import_generated_asset_main_site(*args, **kwargs)
            case "FAL_AI":
                return self.import_generated_asset_fal_ai(*args, **kwargs)
            case _:
                return f"Error: Unknown Hyper3D Rodin mode!"

    def import_generated_asset_main_site(self, task_uuid: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.post(
            "https://hyperhuman.deemos.com/api/v2/download",
            headers={
                "Authorization": f"Bearer {bpy.context.scene.blendermcp_hyper3d_api_key}",
            },
            json={
                'task_uuid': task_uuid
            }
        )
        data_ = response.json()
        temp_file = None
        for i in data_["list"]:
            if i["name"].endswith(".glb"):
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    prefix=task_uuid,
                    suffix=".glb",
                )

                try:
                    # Download the content
                    response = requests.get(i["url"], stream=True)
                    response.raise_for_status()  # Raise an exception for HTTP errors

                    # Write the content to the temporary file
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)

                    # Close the file
                    temp_file.close()

                except Exception as e:
                    # Clean up the file if there's an error
                    temp_file.close()
                    os.unlink(temp_file.name)
                    return {"succeed": False, "error": str(e)}

                break
        else:
            return {"succeed": False, "error": "Generation failed. Please first make sure that all jobs of the task are done and then try again later."}

        try:
            obj = self._clean_imported_glb(
                filepath=temp_file.name,
                mesh_name=name
            )
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {
                "succeed": True, **result
            }
        except Exception as e:
            return {"succeed": False, "error": str(e)}

    def import_generated_asset_fal_ai(self, request_id: str, name: str):
        """Fetch the generated asset, import into blender"""
        response = requests.get(
            f"https://queue.fal.run/fal-ai/hyper3d/requests/{request_id}",
            headers={
                "Authorization": f"Key {bpy.context.scene.blendermcp_hyper3d_api_key}",
            }
        )
        data_ = response.json()
        temp_file = None

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            prefix=request_id,
            suffix=".glb",
        )

        try:
            # Download the content
            response = requests.get(data_["model_mesh"]["url"], stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Write the content to the temporary file
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)

            # Close the file
            temp_file.close()

        except Exception as e:
            # Clean up the file if there's an error
            temp_file.close()
            os.unlink(temp_file.name)
            return {"succeed": False, "error": str(e)}

        try:
            obj = self._clean_imported_glb(
                filepath=temp_file.name,
                mesh_name=name
            )
            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {
                "succeed": True, **result
            }
        except Exception as e:
            return {"succeed": False, "error": str(e)}
    #endregion
 
    #region Sketchfab API
    def get_sketchfab_status(self):
        """Get the current status of Sketchfab integration"""
        enabled = bpy.context.scene.blendermcp_use_sketchfab
        api_key = bpy.context.scene.blendermcp_sketchfab_api_key

        # Test the API key if present
        if api_key:
            try:
                headers = {
                    "Authorization": f"Token {api_key}"
                }

                response = requests.get(
                    "https://api.sketchfab.com/v3/me",
                    headers=headers,
                    timeout=30  # Add timeout of 30 seconds
                )

                if response.status_code == 200:
                    user_data = response.json()
                    username = user_data.get("username", "Unknown user")
                    return {
                        "enabled": True,
                        "message": f"Sketchfab integration is enabled and ready to use. Logged in as: {username}"
                    }
                else:
                    return {
                        "enabled": False,
                        "message": f"Sketchfab API key seems invalid. Status code: {response.status_code}"
                    }
            except requests.exceptions.Timeout:
                return {
                    "enabled": False,
                    "message": "Timeout connecting to Sketchfab API. Check your internet connection."
                }
            except Exception as e:
                return {
                    "enabled": False,
                    "message": f"Error testing Sketchfab API key: {str(e)}"
                }

        if enabled and api_key:
            return {"enabled": True, "message": "Sketchfab integration is enabled and ready to use."}
        elif enabled and not api_key:
            return {
                "enabled": False,
                "message": """Sketchfab integration is currently enabled, but API key is not given. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Keep the 'Use Sketchfab' checkbox checked
                            3. Enter your Sketchfab API Key
                            4. Restart the connection to Claude"""
            }
        else:
            return {
                "enabled": False,
                "message": """Sketchfab integration is currently disabled. To enable it:
                            1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                            2. Check the 'Use assets from Sketchfab' checkbox
                            3. Enter your Sketchfab API Key
                            4. Restart the connection to Claude"""
            }

    def search_sketchfab_models(self, query, categories=None, count=20, downloadable=True):
        """Search for models on Sketchfab based on query and optional filters"""
        try:
            api_key = bpy.context.scene.blendermcp_sketchfab_api_key
            if not api_key:
                return {"error": "Sketchfab API key is not configured"}

            # Build search parameters with exact fields from Sketchfab API docs
            params = {
                "type": "models",
                "q": query,
                "count": count,
                "downloadable": downloadable,
                "archives_flavours": False
            }

            if categories:
                params["categories"] = categories

            # Make API request to Sketchfab search endpoint
            # The proper format according to Sketchfab API docs for API key auth
            headers = {
                "Authorization": f"Token {api_key}"
            }


            # Use the search endpoint as specified in the API documentation
            response = requests.get(
                "https://api.sketchfab.com/v3/search",
                headers=headers,
                params=params,
                timeout=30  # Add timeout of 30 seconds
            )

            if response.status_code == 401:
                return {"error": "Authentication failed (401). Check your API key."}

            if response.status_code != 200:
                return {"error": f"API request failed with status code {response.status_code}"}

            response_data = response.json()

            # Safety check on the response structure
            if response_data is None:
                return {"error": "Received empty response from Sketchfab API"}

            # Handle 'results' potentially missing from response
            results = response_data.get("results", [])
            if not isinstance(results, list):
                return {"error": f"Unexpected response format from Sketchfab API: {response_data}"}

            return response_data

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Check your internet connection."}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response from Sketchfab API: {str(e)}"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    def download_sketchfab_model(self, uid):
        """Download a model from Sketchfab by its UID"""
        try:
            api_key = bpy.context.scene.blendermcp_sketchfab_api_key
            if not api_key:
                return {"error": "Sketchfab API key is not configured"}

            # Use proper authorization header for API key auth
            headers = {
                "Authorization": f"Token {api_key}"
            }

            # Request download URL using the exact endpoint from the documentation
            download_endpoint = f"https://api.sketchfab.com/v3/models/{uid}/download"

            response = requests.get(
                download_endpoint,
                headers=headers,
                timeout=30  # Add timeout of 30 seconds
            )

            if response.status_code == 401:
                return {"error": "Authentication failed (401). Check your API key."}

            if response.status_code != 200:
                return {"error": f"Download request failed with status code {response.status_code}"}

            data = response.json()

            # Safety check for None data
            if data is None:
                return {"error": "Received empty response from Sketchfab API for download request"}

            # Extract download URL with safety checks
            gltf_data = data.get("gltf")
            if not gltf_data:
                return {"error": "No gltf download URL available for this model. Response: " + str(data)}

            download_url = gltf_data.get("url")
            if not download_url:
                return {"error": "No download URL available for this model. Make sure the model is downloadable and you have access."}

            # Download the model (already has timeout)
            model_response = requests.get(download_url, timeout=60)  # 60 second timeout

            if model_response.status_code != 200:
                return {"error": f"Model download failed with status code {model_response.status_code}"}

            # Save to temporary file
            temp_dir = tempfile.mkdtemp()
            zip_file_path = os.path.join(temp_dir, f"{uid}.zip")

            with open(zip_file_path, "wb") as f:
                f.write(model_response.content)

            # Extract the zip file with enhanced security
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # More secure zip slip prevention
                for file_info in zip_ref.infolist():
                    # Get the path of the file
                    file_path = file_info.filename

                    # Convert directory separators to the current OS style
                    # This handles both / and \ in zip entries
                    target_path = os.path.join(temp_dir, os.path.normpath(file_path))

                    # Get absolute paths for comparison
                    abs_temp_dir = os.path.abspath(temp_dir)
                    abs_target_path = os.path.abspath(target_path)

                    # Ensure the normalized path doesn't escape the target directory
                    if not abs_target_path.startswith(abs_temp_dir):
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                        return {"error": "Security issue: Zip contains files with path traversal attempt"}

                    # Additional explicit check for directory traversal
                    if ".." in file_path:
                        with suppress(Exception):
                            shutil.rmtree(temp_dir)
                        return {"error": "Security issue: Zip contains files with directory traversal sequence"}

                # If all files passed security checks, extract them
                zip_ref.extractall(temp_dir)

            # Find the main glTF file
            gltf_files = [f for f in os.listdir(temp_dir) if f.endswith('.gltf') or f.endswith('.glb')]

            if not gltf_files:
                with suppress(Exception):
                    shutil.rmtree(temp_dir)
                return {"error": "No glTF file found in the downloaded model"}

            main_file = os.path.join(temp_dir, gltf_files[0])

            # Import the model
            bpy.ops.import_scene.gltf(filepath=main_file)

            # Get the names of imported objects
            imported_objects = [obj.name for obj in bpy.context.selected_objects]

            # Clean up temporary files
            with suppress(Exception):
                shutil.rmtree(temp_dir)

            return {
                "success": True,
                "message": "Model imported successfully",
                "imported_objects": imported_objects
            }

        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Check your internet connection and try again with a simpler model."}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response from Sketchfab API: {str(e)}"}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to download model: {str(e)}"}
    #endregion

    #region Hunyuan3D
    def get_hunyuan3d_status(self):
        """Get the current status of Hunyuan3D integration"""
        enabled = bpy.context.scene.blendermcp_use_hunyuan3d
        hunyuan3d_mode = bpy.context.scene.blendermcp_hunyuan3d_mode
        if enabled:
            match hunyuan3d_mode:
                case "OFFICIAL_API":
                    if not bpy.context.scene.blendermcp_hunyuan3d_secret_id or not bpy.context.scene.blendermcp_hunyuan3d_secret_key:
                        return {
                            "enabled": False, 
                            "mode": hunyuan3d_mode, 
                            "message": """Hunyuan3D integration is currently enabled, but SecretId or SecretKey is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Tencent Hunyuan 3D model generation' checkbox checked
                                3. Choose the right platform and fill in the SecretId and SecretKey
                                4. Restart the connection to Claude"""
                        }
                case "LOCAL_API":
                    if not bpy.context.scene.blendermcp_hunyuan3d_api_url:
                        return {
                            "enabled": False, 
                            "mode": hunyuan3d_mode, 
                            "message": """Hunyuan3D integration is currently enabled, but API URL  is not given. To enable it:
                                1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                                2. Keep the 'Use Tencent Hunyuan 3D model generation' checkbox checked
                                3. Choose the right platform and fill in the API URL
                                4. Restart the connection to Claude"""
                        }
                case _:
                    return {
                        "enabled": False, 
                        "message": "Hunyuan3D integration is enabled and mode is not supported."
                    }
            return {
                "enabled": True, 
                "mode": hunyuan3d_mode,
                "message": "Hunyuan3D integration is enabled and ready to use."
            }
        return {
            "enabled": False, 
            "message": """Hunyuan3D integration is currently disabled. To enable it:
                        1. In the 3D Viewport, find the BlenderMCP panel in the sidebar (press N if hidden)
                        2. Check the 'Use Tencent Hunyuan 3D model generation' checkbox
                        3. Restart the connection to Claude"""
        }
    
    @staticmethod
    def get_tencent_cloud_sign_headers(
        method: str,
        path: str,
        headParams: dict,
        data: dict,
        service: str,
        region: str,
        secret_id: str,
        secret_key: str,
        host: str = None
    ):
        """Generate the signature header required for Tencent Cloud API requests headers"""
        # Generate timestamp
        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        # If host is not provided, it is generated based on service and region.
        if not host:
            host = f"{service}.tencentcloudapi.com"
        
        endpoint = f"https://{host}"
        
        # Constructing the request body
        payload_str = json.dumps(data)
        
        # ************* Step 1: Concatenate the canonical request string *************
        canonical_uri = path
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = f"content-type:{ct}\nhost:{host}\nx-tc-action:{headParams.get('Action', '').lower()}\n"
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        
        canonical_request = (method + "\n" +
                            canonical_uri + "\n" +
                            canonical_querystring + "\n" +
                            canonical_headers + "\n" +
                            signed_headers + "\n" +
                            hashed_request_payload)

        # ************* Step 2: Construct the reception signature string *************
        credential_scope = f"{date}/{service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = ("TC3-HMAC-SHA256" + "\n" +
                        str(timestamp) + "\n" +
                        credential_scope + "\n" +
                        hashed_canonical_request)

        # ************* Step 3: Calculate the signature *************
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
        secret_service = sign(secret_date, service)
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(
            secret_signing, 
            string_to_sign.encode("utf-8"), 
            hashlib.sha256
        ).hexdigest()

        # ************* Step 4: Connect Authorization *************
        authorization = ("TC3-HMAC-SHA256" + " " +
                        "Credential=" + secret_id + "/" + credential_scope + ", " +
                        "SignedHeaders=" + signed_headers + ", " +
                        "Signature=" + signature)

        # Constructing request headers
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host,
            "X-TC-Action": headParams.get("Action", ""),
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": headParams.get("Version", ""),
            "X-TC-Region": region
        }

        return headers, endpoint

    def create_hunyuan_job(self, *args, **kwargs):
        match bpy.context.scene.blendermcp_hunyuan3d_mode:
            case "OFFICIAL_API":
                return self.create_hunyuan_job_main_site(*args, **kwargs)
            case "LOCAL_API":
                return self.create_hunyuan_job_local_site(*args, **kwargs)
            case _:
                return f"Error: Unknown Hunyuan3D mode!"

    def create_hunyuan_job_main_site(
        self,
        text_prompt: str = None,
        image: str = None
    ):
        try:
            secret_id = bpy.context.scene.blendermcp_hunyuan3d_secret_id
            secret_key = bpy.context.scene.blendermcp_hunyuan3d_secret_key

            if not secret_id or not secret_key:
                return {"error": "SecretId or SecretKey is not given"}

            # Parameter verification
            if not text_prompt and not image:
                return {"error": "Prompt or Image is required"}
            if text_prompt and image:
                return {"error": "Prompt and Image cannot be provided simultaneously"}
            # Fixed parameter configuration
            service = "hunyuan"
            action = "SubmitHunyuanTo3DJob"
            version = "2023-09-01"
            region = "ap-guangzhou"

            headParams={
                "Action": action,
                "Version": version,
                "Region": region,
            }

            # Constructing request parameters
            data = {
                "Num": 1  # The current API limit is only 1
            }

            # Handling text prompts
            if text_prompt:
                if len(text_prompt) > 200:
                    return {"error": "Prompt exceeds 200 characters limit"}
                data["Prompt"] = text_prompt

            # Handling image
            if image:
                if re.match(r'^https?://', image, re.IGNORECASE) is not None:
                    data["ImageUrl"] = image
                else:
                    try:
                        # Convert to Base64 format
                        with open(image, "rb") as f:
                            image_base64 = base64.b64encode(f.read()).decode("ascii")
                        data["ImageBase64"] = image_base64
                    except Exception as e:
                        return {"error": f"Image encoding failed: {str(e)}"}
            
            # Get signed headers
            headers, endpoint = self.get_tencent_cloud_sign_headers("POST", "/", headParams, data, service, region, secret_id, secret_key)

            response = requests.post(
                endpoint,
                headers = headers,
                data = json.dumps(data)
            )

            if response.status_code == 200:
                return response.json()
            return {
                "error": f"API request failed with status {response.status_code}: {response}"
            }
        except Exception as e:
            return {"error": str(e)}

    def create_hunyuan_job_local_site(
        self,
        text_prompt: str = None,
        image: str = None):
        try:
            base_url = bpy.context.scene.blendermcp_hunyuan3d_api_url.rstrip('/')
            octree_resolution = bpy.context.scene.blendermcp_hunyuan3d_octree_resolution
            num_inference_steps = bpy.context.scene.blendermcp_hunyuan3d_num_inference_steps
            guidance_scale = bpy.context.scene.blendermcp_hunyuan3d_guidance_scale
            texture = bpy.context.scene.blendermcp_hunyuan3d_texture

            if not base_url:
                return {"error": "API URL is not given"}
            # Parameter verification
            if not text_prompt and not image:
                return {"error": "Prompt or Image is required"}

            # Constructing request parameters
            data = {
                "octree_resolution": octree_resolution,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "texture": texture,
            }

            # Handling text prompts
            if text_prompt:
                data["text"] = text_prompt

            # Handling image
            if image:
                if re.match(r'^https?://', image, re.IGNORECASE) is not None:
                    try:
                        resImg = requests.get(image)
                        resImg.raise_for_status()
                        image_base64 = base64.b64encode(resImg.content).decode("ascii")
                        data["image"] = image_base64
                    except Exception as e:
                        return {"error": f"Failed to download or encode image: {str(e)}"} 
                else:
                    try:
                        # Convert to Base64 format
                        with open(image, "rb") as f:
                            image_base64 = base64.b64encode(f.read()).decode("ascii")
                        data["image"] = image_base64
                    except Exception as e:
                        return {"error": f"Image encoding failed: {str(e)}"}

            response = requests.post(
                f"{base_url}/generate",
                json = data,
            )

            if response.status_code != 200:
                return {
                    "error": f"Generation failed: {response.text}"
                }
        
            # Decode base64 and save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".glb") as temp_file:
                temp_file.write(response.content)
                temp_file_name = temp_file.name

            # Import the GLB file in the main thread
            def import_handler():
                bpy.ops.import_scene.gltf(filepath=temp_file_name)
                os.unlink(temp_file.name)
                return None
            
            bpy.app.timers.register(import_handler)

            return {
                "status": "DONE",
                "message": "Generation and Import glb succeeded"
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"error": str(e)}
        
    
    def poll_hunyuan_job_status(self, *args, **kwargs):
        return self.poll_hunyuan_job_status_ai(*args, **kwargs)
    
    def poll_hunyuan_job_status_ai(self, job_id: str):
        """Call the job status API to get the job status"""
        print(job_id)
        try:
            secret_id = bpy.context.scene.blendermcp_hunyuan3d_secret_id
            secret_key = bpy.context.scene.blendermcp_hunyuan3d_secret_key

            if not secret_id or not secret_key:
                return {"error": "SecretId or SecretKey is not given"}
            if not job_id:
                return {"error": "JobId is required"}
            
            service = "hunyuan"
            action = "QueryHunyuanTo3DJob"
            version = "2023-09-01"
            region = "ap-guangzhou"

            headParams={
                "Action": action,
                "Version": version,
                "Region": region,
            }

            clean_job_id = job_id.removeprefix("job_")
            data = {
                "JobId": clean_job_id
            }

            headers, endpoint = self.get_tencent_cloud_sign_headers("POST", "/", headParams, data, service, region, secret_id, secret_key)

            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(data)
            )

            if response.status_code == 200:
                return response.json()
            return {
                "error": f"API request failed with status {response.status_code}: {response}"
            }
        except Exception as e:
            return {"error": str(e)}

    def import_generated_asset_hunyuan(self, *args, **kwargs):
        return self.import_generated_asset_hunyuan_ai(*args, **kwargs)
            
    def import_generated_asset_hunyuan_ai(self, name: str , zip_file_url: str):
        if not zip_file_url:
            return {"error": "Zip file not found"}
        
        # Validate URL
        if not re.match(r'^https?://', zip_file_url, re.IGNORECASE):
            return {"error": "Invalid URL format. Must start with http:// or https://"}
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="tencent_obj_")
        zip_file_path = osp.join(temp_dir, "model.zip")
        obj_file_path = osp.join(temp_dir, "model.obj")
        mtl_file_path = osp.join(temp_dir, "model.mtl")

        try:
            # Download ZIP file
            zip_response = requests.get(zip_file_url, stream=True)
            zip_response.raise_for_status()
            with open(zip_file_path, "wb") as f:
                for chunk in zip_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Unzip the ZIP
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the .obj file (there may be multiple, assuming the main file is model.obj)
            for file in os.listdir(temp_dir):
                if file.endswith(".obj"):
                    obj_file_path = osp.join(temp_dir, file)

            if not osp.exists(obj_file_path):
                return {"succeed": False, "error": "OBJ file not found after extraction"}

            # Import obj file
            if bpy.app.version>=(4, 0, 0):
                bpy.ops.wm.obj_import(filepath=obj_file_path)
            else:
                bpy.ops.import_scene.obj(filepath=obj_file_path)

            imported_objs = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
            if not imported_objs:
                return {"succeed": False, "error": "No mesh objects imported"}

            obj = imported_objs[0]
            if name:
                obj.name = name

            result = {
                "name": obj.name,
                "type": obj.type,
                "location": [obj.location.x, obj.location.y, obj.location.z],
                "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
            }

            if obj.type == "MESH":
                bounding_box = self._get_aabb(obj)
                result["world_bounding_box"] = bounding_box

            return {"succeed": True, **result}
        except Exception as e:
            return {"succeed": False, "error": str(e)}
        finally:
            #  Clean up temporary zip and obj, save texture and mtl
            try:
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path) 
                if os.path.exists(obj_file_path):
                    os.remove(obj_file_path)
            except Exception as e:
                print(f"Failed to clean up temporary directory {temp_dir}: {e}")
    #endregion

# Blender UI Panel
class BLENDERMCP_PT_Panel(bpy.types.Panel):
    bl_label = "Blender MCP"
    bl_idname = "BLENDERMCP_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderMCP'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "blendermcp_port")
        layout.prop(scene, "blendermcp_use_polyhaven", text="Use assets from Poly Haven")

        layout.prop(scene, "blendermcp_use_hyper3d", text="Use Hyper3D Rodin 3D model generation")
        if scene.blendermcp_use_hyper3d:
            layout.prop(scene, "blendermcp_hyper3d_mode", text="Rodin Mode")
            layout.prop(scene, "blendermcp_hyper3d_api_key", text="API Key")
            layout.operator("blendermcp.set_hyper3d_free_trial_api_key", text="Set Free Trial API Key")

        layout.prop(scene, "blendermcp_use_sketchfab", text="Use assets from Sketchfab")
        if scene.blendermcp_use_sketchfab:
            layout.prop(scene, "blendermcp_sketchfab_api_key", text="API Key")

        layout.prop(scene, "blendermcp_use_hunyuan3d", text="Use Tencent Hunyuan 3D model generation")
        if scene.blendermcp_use_hunyuan3d:
            layout.prop(scene, "blendermcp_hunyuan3d_mode", text="Hunyuan3D Mode")
            if scene.blendermcp_hunyuan3d_mode == 'OFFICIAL_API':
                layout.prop(scene, "blendermcp_hunyuan3d_secret_id", text="SecretId")
                layout.prop(scene, "blendermcp_hunyuan3d_secret_key", text="SecretKey")
            if scene.blendermcp_hunyuan3d_mode == 'LOCAL_API':
                layout.prop(scene, "blendermcp_hunyuan3d_api_url", text="API URL")
                layout.prop(scene, "blendermcp_hunyuan3d_octree_resolution", text="Octree Resolution")
                layout.prop(scene, "blendermcp_hunyuan3d_num_inference_steps", text="Number of Inference Steps")
                layout.prop(scene, "blendermcp_hunyuan3d_guidance_scale", text="Guidance Scale")
                layout.prop(scene, "blendermcp_hunyuan3d_texture", text="Generate Texture")
        
        if not scene.blendermcp_server_running:
            layout.operator("blendermcp.start_server", text="Connect to MCP server")
        else:
            layout.operator("blendermcp.stop_server", text="Disconnect from MCP server")
            layout.label(text=f"Running on port {scene.blendermcp_port}")

# Operator to set Hyper3D API Key
class BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey(bpy.types.Operator):
    bl_idname = "blendermcp.set_hyper3d_free_trial_api_key"
    bl_label = "Set Free Trial API Key"

    def execute(self, context):
        context.scene.blendermcp_hyper3d_api_key = RODIN_FREE_TRIAL_KEY
        context.scene.blendermcp_hyper3d_mode = 'MAIN_SITE'
        self.report({'INFO'}, "API Key set successfully!")
        return {'FINISHED'}

# Operator to start the server
class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    bl_idname = "blendermcp.start_server"
    bl_label = "Connect to Claude"
    bl_description = "Start the BlenderMCP server to connect with Claude"

    def execute(self, context):
        scene = context.scene

        # Create a new server instance
        if not hasattr(bpy.types, "blendermcp_server") or not bpy.types.blendermcp_server:
            bpy.types.blendermcp_server = BlenderMCPServer(port=scene.blendermcp_port)

        # Start the server
        bpy.types.blendermcp_server.start()
        scene.blendermcp_server_running = True

        return {'FINISHED'}

# Operator to stop the server
class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop the connection to Claude"
    bl_description = "Stop the connection to Claude"

    def execute(self, context):
        scene = context.scene

        # Stop the server if it exists
        if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
            bpy.types.blendermcp_server.stop()
            del bpy.types.blendermcp_server

        scene.blendermcp_server_running = False

        return {'FINISHED'}

# Registration functions
def register():
    bpy.types.Scene.blendermcp_port = IntProperty(
        name="Port",
        description="Port for the BlenderMCP server",
        default=9876,
        min=1024,
        max=65535
    )

    bpy.types.Scene.blendermcp_server_running = bpy.props.BoolProperty(
        name="Server Running",
        default=False
    )

    bpy.types.Scene.blendermcp_use_polyhaven = bpy.props.BoolProperty(
        name="Use Poly Haven",
        description="Enable Poly Haven asset integration",
        default=False
    )

    bpy.types.Scene.blendermcp_use_hyper3d = bpy.props.BoolProperty(
        name="Use Hyper3D Rodin",
        description="Enable Hyper3D Rodin generatino integration",
        default=False
    )

    bpy.types.Scene.blendermcp_hyper3d_mode = bpy.props.EnumProperty(
        name="Rodin Mode",
        description="Choose the platform used to call Rodin APIs",
        items=[
            ("MAIN_SITE", "hyper3d.ai", "hyper3d.ai"),
            ("FAL_AI", "fal.ai", "fal.ai"),
        ],
        default="MAIN_SITE"
    )

    bpy.types.Scene.blendermcp_hyper3d_api_key = bpy.props.StringProperty(
        name="Hyper3D API Key",
        subtype="PASSWORD",
        description="API Key provided by Hyper3D",
        default=""
    )

    bpy.types.Scene.blendermcp_use_hunyuan3d = bpy.props.BoolProperty(
        name="Use Hunyuan 3D",
        description="Enable Hunyuan asset integration",
        default=False
    )

    bpy.types.Scene.blendermcp_hunyuan3d_mode = bpy.props.EnumProperty(
        name="Hunyuan3D Mode",
        description="Choose a local or official APIs",
        items=[
            ("LOCAL_API", "local api", "local api"),
            ("OFFICIAL_API", "official api", "official api"),
        ],
        default="LOCAL_API"
    )

    bpy.types.Scene.blendermcp_hunyuan3d_secret_id = bpy.props.StringProperty(
        name="Hunyuan 3D SecretId",
        description="SecretId provided by Hunyuan 3D",
        default=""
    )

    bpy.types.Scene.blendermcp_hunyuan3d_secret_key = bpy.props.StringProperty(
        name="Hunyuan 3D SecretKey",
        subtype="PASSWORD",
        description="SecretKey provided by Hunyuan 3D",
        default=""
    )

    bpy.types.Scene.blendermcp_hunyuan3d_api_url = bpy.props.StringProperty(
        name="API URL",
        description="URL of the Hunyuan 3D API service",
        default="http://localhost:8081"
    )

    bpy.types.Scene.blendermcp_hunyuan3d_octree_resolution = bpy.props.IntProperty(
        name="Octree Resolution",
        description="Octree resolution for the 3D generation",
        default=256,
        min=128,
        max=512,
    )

    bpy.types.Scene.blendermcp_hunyuan3d_num_inference_steps = bpy.props.IntProperty(
        name="Number of Inference Steps",
        description="Number of inference steps for the 3D generation",
        default=20,
        min=20,
        max=50,
    )

    bpy.types.Scene.blendermcp_hunyuan3d_guidance_scale = bpy.props.FloatProperty(
        name="Guidance Scale",
        description="Guidance scale for the 3D generation",
        default=5.5,
        min=1.0,
        max=10.0,
    )

    bpy.types.Scene.blendermcp_hunyuan3d_texture = bpy.props.BoolProperty(
        name="Generate Texture",
        description="Whether to generate texture for the 3D model",
        default=False,
    )
    
    bpy.types.Scene.blendermcp_use_sketchfab = bpy.props.BoolProperty(
        name="Use Sketchfab",
        description="Enable Sketchfab asset integration",
        default=False
    )

    bpy.types.Scene.blendermcp_sketchfab_api_key = bpy.props.StringProperty(
        name="Sketchfab API Key",
        subtype="PASSWORD",
        description="API Key provided by Sketchfab",
        default=os.environ.get("SKETCHFAB_API_KEY", "")
    )

    bpy.utils.register_class(BLENDERMCP_PT_Panel)
    bpy.utils.register_class(BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.register_class(BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(BLENDERMCP_OT_StopServer)

    print("BlenderMCP addon registered")

def unregister():
    # Stop the server if it's running
    if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
        bpy.types.blendermcp_server.stop()
        del bpy.types.blendermcp_server

    bpy.utils.unregister_class(BLENDERMCP_PT_Panel)
    bpy.utils.unregister_class(BLENDERMCP_OT_SetFreeTrialHyper3DAPIKey)
    bpy.utils.unregister_class(BLENDERMCP_OT_StartServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_StopServer)

    del bpy.types.Scene.blendermcp_port
    del bpy.types.Scene.blendermcp_server_running
    del bpy.types.Scene.blendermcp_use_polyhaven
    del bpy.types.Scene.blendermcp_use_hyper3d
    del bpy.types.Scene.blendermcp_hyper3d_mode
    del bpy.types.Scene.blendermcp_hyper3d_api_key
    del bpy.types.Scene.blendermcp_use_sketchfab
    del bpy.types.Scene.blendermcp_sketchfab_api_key
    del bpy.types.Scene.blendermcp_use_hunyuan3d
    del bpy.types.Scene.blendermcp_hunyuan3d_mode
    del bpy.types.Scene.blendermcp_hunyuan3d_secret_id
    del bpy.types.Scene.blendermcp_hunyuan3d_secret_key
    del bpy.types.Scene.blendermcp_hunyuan3d_api_url
    del bpy.types.Scene.blendermcp_hunyuan3d_octree_resolution
    del bpy.types.Scene.blendermcp_hunyuan3d_num_inference_steps
    del bpy.types.Scene.blendermcp_hunyuan3d_guidance_scale
    del bpy.types.Scene.blendermcp_hunyuan3d_texture

    print("BlenderMCP addon unregistered")

if __name__ == "__main__":
    register()
