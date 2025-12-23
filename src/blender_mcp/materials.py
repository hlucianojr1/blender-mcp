"""
Material System for Blender MCP
Provides PBR materials, procedural textures, and automatic material enhancement
"""

# PBR Material Presets
# Format: {material_name: {properties}}
MATERIAL_PRESETS = {
    # Metals
    "weathered_metal": {
        "type": "pbr",
        "base_color": (0.3, 0.3, 0.35, 1.0),
        "metallic": 0.9,
        "roughness": 0.6,
        "procedural": {
            "type": "noise",
            "scale": 15.0,
            "detail": 8.0,
            "roughness_variation": 0.3
        }
    },
    "brushed_metal": {
        "type": "pbr",
        "base_color": (0.7, 0.7, 0.72, 1.0),
        "metallic": 1.0,
        "roughness": 0.3,
        "procedural": {
            "type": "scratch",
            "scale": 100.0,
            "anisotropic": True
        }
    },
    "rusted_metal": {
        "type": "pbr",
        "base_color": (0.4, 0.25, 0.15, 1.0),
        "metallic": 0.7,
        "roughness": 0.8,
        "procedural": {
            "type": "rust",
            "scale": 10.0,
            "detail": 6.0
        }
    },
    "chrome": {
        "type": "pbr",
        "base_color": (0.95, 0.95, 0.95, 1.0),
        "metallic": 1.0,
        "roughness": 0.05
    },
    
    # Glass and Transparent
    "clear_glass": {
        "type": "glass",
        "base_color": (0.95, 0.95, 0.98, 1.0),
        "transmission": 1.0,
        "roughness": 0.0,
        "ior": 1.45
    },
    "frosted_glass": {
        "type": "glass",
        "base_color": (0.9, 0.9, 0.92, 1.0),
        "transmission": 0.95,
        "roughness": 0.3,
        "ior": 1.45,
        "procedural": {
            "type": "noise",
            "scale": 50.0,
            "roughness_variation": 0.2
        }
    },
    "tinted_glass": {
        "type": "glass",
        "base_color": (0.7, 0.85, 0.9, 1.0),
        "transmission": 0.9,
        "roughness": 0.05,
        "ior": 1.45
    },
    
    # Paint and Coatings
    "glossy_paint": {
        "type": "pbr",
        "base_color": (0.8, 0.1, 0.1, 1.0),
        "metallic": 0.0,
        "roughness": 0.2,
        "clearcoat": 0.5,
        "clearcoat_roughness": 0.1
    },
    "matte_paint": {
        "type": "pbr",
        "base_color": (0.6, 0.6, 0.65, 1.0),
        "metallic": 0.0,
        "roughness": 0.8
    },
    "weathered_paint": {
        "type": "pbr",
        "base_color": (0.2, 0.3, 0.4, 1.0),
        "metallic": 0.0,
        "roughness": 0.7,
        "procedural": {
            "type": "scratches_and_dirt",
            "scale": 20.0,
            "detail": 5.0,
            "roughness_variation": 0.4
        }
    },
    "car_paint": {
        "type": "pbr",
        "base_color": (0.1, 0.1, 0.8, 1.0),
        "metallic": 0.2,
        "roughness": 0.15,
        "clearcoat": 1.0,
        "clearcoat_roughness": 0.05
    },
    
    # Plastics
    "glossy_plastic": {
        "type": "pbr",
        "base_color": (0.9, 0.9, 0.9, 1.0),
        "metallic": 0.0,
        "roughness": 0.3,
        "specular": 0.5
    },
    "rubber": {
        "type": "pbr",
        "base_color": (0.1, 0.1, 0.1, 1.0),
        "metallic": 0.0,
        "roughness": 0.9,
        "procedural": {
            "type": "bump",
            "scale": 200.0
        }
    },
    
    # Wood
    "polished_wood": {
        "type": "pbr",
        "base_color": (0.4, 0.25, 0.15, 1.0),
        "metallic": 0.0,
        "roughness": 0.3,
        "procedural": {
            "type": "wood_grain",
            "scale": 5.0
        }
    },
    "rough_wood": {
        "type": "pbr",
        "base_color": (0.5, 0.35, 0.2, 1.0),
        "metallic": 0.0,
        "roughness": 0.8,
        "procedural": {
            "type": "wood_grain",
            "scale": 3.0,
            "detail": 8.0
        }
    },
    
    # Fabric
    "fabric": {
        "type": "pbr",
        "base_color": (0.6, 0.55, 0.5, 1.0),
        "metallic": 0.0,
        "roughness": 0.9,
        "procedural": {
            "type": "fabric_weave",
            "scale": 100.0
        }
    },
    
    # Stone and Concrete
    "concrete": {
        "type": "pbr",
        "base_color": (0.5, 0.5, 0.52, 1.0),
        "metallic": 0.0,
        "roughness": 0.9,
        "procedural": {
            "type": "concrete",
            "scale": 8.0,
            "detail": 4.0
        }
    },
    "stone": {
        "type": "pbr",
        "base_color": (0.4, 0.4, 0.42, 1.0),
        "metallic": 0.0,
        "roughness": 0.85,
        "procedural": {
            "type": "rock",
            "scale": 5.0,
            "detail": 6.0
        }
    },
    
    # Special Materials
    "emission": {
        "type": "emission",
        "base_color": (1.0, 0.9, 0.7, 1.0),
        "emission_strength": 5.0
    },
    "glow": {
        "type": "emission",
        "base_color": (0.9, 0.9, 1.0, 1.0),
        "emission_strength": 2.0
    }
}

# Material suggestions based on object name keywords
OBJECT_TYPE_MATERIALS = {
    # Glass objects
    "window": "frosted_glass",
    "glass": "clear_glass",
    "lens": "clear_glass",
    "screen": "clear_glass",
    
    # Metal objects
    "metal": "brushed_metal",
    "steel": "brushed_metal",
    "iron": "weathered_metal",
    "chrome": "chrome",
    "aluminum": "brushed_metal",
    "brass": "chrome",
    "copper": "rusted_metal",
    "gold": "chrome",
    "silver": "chrome",
    
    # Paint
    "car": "car_paint",
    "vehicle": "car_paint",
    "door": "weathered_paint",
    "wall": "matte_paint",
    "panel": "glossy_paint",
    
    # Plastic
    "plastic": "glossy_plastic",
    "button": "glossy_plastic",
    "case": "glossy_plastic",
    
    # Wood
    "wood": "polished_wood",
    "table": "polished_wood",
    "chair": "polished_wood",
    "floor": "polished_wood",
    "plank": "rough_wood",
    
    # Fabric
    "fabric": "fabric",
    "cloth": "fabric",
    "curtain": "fabric",
    "carpet": "fabric",
    
    # Stone/Concrete
    "concrete": "concrete",
    "cement": "concrete",
    "stone": "stone",
    "rock": "stone",
    "brick": "concrete",
    
    # Rubber
    "rubber": "rubber",
    "tire": "rubber",
    "seal": "rubber",
    
    # Light/Glow
    "light": "emission",
    "lamp": "emission",
    "bulb": "emission",
    "neon": "glow",
    "led": "glow"
}

# Procedural texture generation templates
PROCEDURAL_SHADERS = {
    "noise": """
def create_noise_shader(material, scale=15.0, detail=8.0, roughness_variation=0.3):
    # Add noise texture for variation
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Find or create Principled BSDF
    bsdf = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf = node
            break
    
    if not bsdf:
        return
    
    # Create noise texture
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = detail
    noise.location = (-400, 0)
    
    # Create color ramp for variation
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (-200, 0)
    
    # Link noise to color ramp to roughness
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Fac'], bsdf.inputs['Roughness'])
""",
    
    "scratches_and_dirt": """
def create_scratches_shader(material, scale=20.0, detail=5.0, roughness_variation=0.4):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    bsdf = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf = node
            break
    
    if not bsdf:
        return
    
    # Scratch noise
    scratch_noise = nodes.new('ShaderNodeTexNoise')
    scratch_noise.inputs['Scale'].default_value = scale
    scratch_noise.inputs['Detail'].default_value = detail
    scratch_noise.location = (-600, 0)
    
    # Dirt noise
    dirt_noise = nodes.new('ShaderNodeTexNoise')
    dirt_noise.inputs['Scale'].default_value = scale * 0.5
    dirt_noise.location = (-600, -200)
    
    # Mix scratches and dirt
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.5
    mix.location = (-400, -100)
    
    # Color ramp for contrast
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    color_ramp.location = (-200, -100)
    
    # Connect
    links.new(scratch_noise.outputs['Fac'], mix.inputs['Color1'])
    links.new(dirt_noise.outputs['Fac'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Fac'], bsdf.inputs['Roughness'])
    
    # Bump for surface detail
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.3
    bump.location = (-200, -300)
    links.new(color_ramp.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
""",
    
    "wood_grain": """
def create_wood_grain_shader(material, scale=5.0, detail=8.0):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    bsdf = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            bsdf = node
            break
    
    if not bsdf:
        return
    
    # Wave texture for grain
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
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.3
    mix.location = (-400, -100)
    
    # Color ramp
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (-200, -100)
    
    # Connect
    links.new(wave.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Fac'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Bump
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.1
    bump.location = (-200, -300)
    links.new(color_ramp.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
"""
}

def get_suggested_material(object_name: str) -> str:
    """
    Suggest a material based on object name keywords
    
    Args:
        object_name: Name of the object
        
    Returns:
        Suggested material preset name, or 'matte_paint' as default
    """
    object_name_lower = object_name.lower()
    
    for keyword, material in OBJECT_TYPE_MATERIALS.items():
        if keyword in object_name_lower:
            return material
    
    return "matte_paint"  # Default material

def list_available_materials() -> list:
    """
    List all available material presets
    
    Returns:
        List of material preset names
    """
    return list(MATERIAL_PRESETS.keys())

def get_material_info(material_name: str) -> dict:
    """
    Get information about a material preset
    
    Args:
        material_name: Name of the material preset
        
    Returns:
        Material properties dictionary, or None if not found
    """
    return MATERIAL_PRESETS.get(material_name)
