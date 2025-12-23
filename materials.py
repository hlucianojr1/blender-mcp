"""
Material presets and suggestions for Blender MCP Addon
This is a minimal version for the addon to import
"""

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

# PBR Material Presets
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

def get_suggested_material(object_name: str) -> str:
    """Suggest a material based on object name keywords"""
    object_name_lower = object_name.lower()
    
    for keyword, material in OBJECT_TYPE_MATERIALS.items():
        if keyword in object_name_lower:
            return material
    
    return "matte_paint"  # Default material
