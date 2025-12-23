"""
Lighting & Atmosphere System for Blender MCP
Provides cinematic lighting, HDRI environments, atmospheric effects, and camera setup
"""

# HDRI Environment Presets
HDRI_PRESETS = {
    "studio": {
        "description": "Neutral studio lighting with soft shadows",
        "recommended_hdris": ["studio_small_03", "photo_studio_01", "industrial_sunset"],
        "rotation": 0.0,
        "strength": 1.0,
        "background_strength": 0.0  # Don't show background
    },
    "outdoor_day": {
        "description": "Bright outdoor daylight",
        "recommended_hdris": ["kloppenheim_02", "venice_sunset", "syferfontein_18d"],
        "rotation": 0.0,
        "strength": 1.0,
        "background_strength": 1.0
    },
    "sunset": {
        "description": "Warm golden hour lighting",
        "recommended_hdris": ["venice_sunset", "artist_workshop", "kiara_1_dawn"],
        "rotation": 0.0,
        "strength": 0.8,
        "background_strength": 1.0
    },
    "night": {
        "description": "Night city or moonlight",
        "recommended_hdris": ["night_street", "moonlit_golf", "starmap_2020"],
        "rotation": 0.0,
        "strength": 0.3,
        "background_strength": 0.8
    },
    "overcast": {
        "description": "Soft overcast sky",
        "recommended_hdris": ["kloofendal_43d_clear", "cloudy_vondelpark", "kloppenheim_06"],
        "rotation": 0.0,
        "strength": 0.9,
        "background_strength": 1.0
    },
    "interior": {
        "description": "Interior ambient lighting",
        "recommended_hdris": ["leadenhall_market", "St_Peters_Square", "wooden_lounge"],
        "rotation": 0.0,
        "strength": 0.7,
        "background_strength": 0.0
    }
}

# Lighting Rig Configurations
LIGHTING_RIGS = {
    "three_point": {
        "description": "Classic 3-point lighting (key, fill, rim)",
        "lights": [
            {
                "type": "AREA",
                "name": "Key_Light",
                "energy": 500,
                "location": (4, -4, 5),
                "rotation": (0.785, 0, 0.785),  # 45° angles
                "size": 2.0,
                "color": (1.0, 0.95, 0.9)  # Slightly warm
            },
            {
                "type": "AREA",
                "name": "Fill_Light",
                "energy": 200,
                "location": (-4, -2, 3),
                "rotation": (0.785, 0, -0.785),
                "size": 3.0,
                "color": (0.9, 0.95, 1.0)  # Slightly cool
            },
            {
                "type": "AREA",
                "name": "Rim_Light",
                "energy": 300,
                "location": (-2, 4, 4),
                "rotation": (1.2, 0, 3.14),
                "size": 1.5,
                "color": (1.0, 1.0, 1.0)
            }
        ]
    },
    
    "studio": {
        "description": "Studio product photography lighting",
        "lights": [
            {
                "type": "AREA",
                "name": "Main_Light",
                "energy": 400,
                "location": (3, -3, 5),
                "rotation": (0.785, 0, 0.785),
                "size": 3.0,
                "color": (1.0, 1.0, 1.0)
            },
            {
                "type": "AREA",
                "name": "Side_Fill",
                "energy": 250,
                "location": (-3, -1, 4),
                "rotation": (0.785, 0, -0.785),
                "size": 2.5,
                "color": (1.0, 1.0, 1.0)
            },
            {
                "type": "AREA",
                "name": "Back_Light",
                "energy": 200,
                "location": (0, 3, 3),
                "rotation": (1.57, 0, 3.14),
                "size": 2.0,
                "color": (1.0, 1.0, 1.0)
            },
            {
                "type": "AREA",
                "name": "Top_Light",
                "energy": 150,
                "location": (0, 0, 6),
                "rotation": (0, 0, 0),
                "size": 4.0,
                "color": (1.0, 1.0, 1.0)
            }
        ]
    },
    
    "dramatic": {
        "description": "High contrast dramatic lighting",
        "lights": [
            {
                "type": "SPOT",
                "name": "Dramatic_Key",
                "energy": 1000,
                "location": (5, -5, 7),
                "rotation": (0.785, 0, 0.785),
                "spot_size": 0.785,  # 45 degrees
                "spot_blend": 0.15,
                "color": (1.0, 0.9, 0.8)  # Warm
            },
            {
                "type": "AREA",
                "name": "Subtle_Fill",
                "energy": 50,
                "location": (-3, -2, 2),
                "rotation": (0.785, 0, -0.785),
                "size": 2.0,
                "color": (0.8, 0.9, 1.0)  # Cool
            }
        ]
    },
    
    "outdoor": {
        "description": "Natural outdoor lighting simulation",
        "lights": [
            {
                "type": "SUN",
                "name": "Sun",
                "energy": 3.0,
                "location": (0, 0, 10),
                "rotation": (0.785, 0.524, 0),  # Angled sun
                "angle": 0.00918,  # Sun angular diameter
                "color": (1.0, 0.95, 0.9)
            },
            {
                "type": "AREA",
                "name": "Sky_Fill",
                "energy": 100,
                "location": (0, 0, 8),
                "rotation": (0, 0, 0),
                "size": 10.0,
                "color": (0.7, 0.85, 1.0)  # Sky blue
            }
        ]
    },
    
    "night": {
        "description": "Night scene with street lights",
        "lights": [
            {
                "type": "AREA",
                "name": "Street_Light_1",
                "energy": 400,
                "location": (3, 0, 5),
                "rotation": (1.2, 0, 0),
                "size": 1.0,
                "color": (1.0, 0.9, 0.7)  # Warm street light
            },
            {
                "type": "AREA",
                "name": "Street_Light_2",
                "energy": 350,
                "location": (-3, 0, 5),
                "rotation": (1.2, 0, 0),
                "size": 1.0,
                "color": (1.0, 0.9, 0.7)
            },
            {
                "type": "AREA",
                "name": "Moon_Fill",
                "energy": 50,
                "location": (0, -8, 10),
                "rotation": (0.785, 0, 0),
                "size": 5.0,
                "color": (0.7, 0.8, 1.0)  # Cool moonlight
            }
        ]
    }
}

# Atmospheric Effects Presets
ATMOSPHERE_PRESETS = {
    "fog": {
        "description": "Volumetric fog for depth and atmosphere",
        "volumetric": True,
        "density": 0.05,
        "anisotropy": 0.1,
        "color": (0.8, 0.85, 0.9),
        "absorption_color": (0.9, 0.9, 0.9)
    },
    
    "heavy_fog": {
        "description": "Dense fog for moody scenes",
        "volumetric": True,
        "density": 0.15,
        "anisotropy": 0.2,
        "color": (0.7, 0.75, 0.8),
        "absorption_color": (0.85, 0.85, 0.85)
    },
    
    "god_rays": {
        "description": "Light shafts through atmosphere",
        "volumetric": True,
        "density": 0.03,
        "anisotropy": 0.5,  # Higher for visible light shafts
        "color": (1.0, 0.95, 0.9),
        "absorption_color": (0.95, 0.95, 0.95)
    },
    
    "haze": {
        "description": "Subtle atmospheric haze",
        "volumetric": True,
        "density": 0.01,
        "anisotropy": 0.05,
        "color": (0.9, 0.92, 0.95),
        "absorption_color": (0.98, 0.98, 0.98)
    },
    
    "none": {
        "description": "Clear atmosphere",
        "volumetric": False
    }
}

# Camera Presets
CAMERA_PRESETS = {
    "portrait": {
        "description": "Portrait focal length (85mm equivalent)",
        "focal_length": 85,
        "sensor_width": 36,
        "dof_enabled": True,
        "f_stop": 2.8
    },
    
    "wide": {
        "description": "Wide angle (24mm equivalent)",
        "focal_length": 24,
        "sensor_width": 36,
        "dof_enabled": False,
        "f_stop": 8.0
    },
    
    "normal": {
        "description": "Normal view (50mm equivalent)",
        "focal_length": 50,
        "sensor_width": 36,
        "dof_enabled": True,
        "f_stop": 5.6
    },
    
    "telephoto": {
        "description": "Telephoto (135mm equivalent)",
        "focal_length": 135,
        "sensor_width": 36,
        "dof_enabled": True,
        "f_stop": 2.0
    },
    
    "architectural": {
        "description": "Architectural (35mm, no distortion)",
        "focal_length": 35,
        "sensor_width": 36,
        "dof_enabled": False,
        "f_stop": 11.0
    }
}

# Render Quality Presets
RENDER_PRESETS = {
    "draft": {
        "description": "Fast preview render",
        "engine": "BLENDER_EEVEE",
        "samples": 64,
        "resolution_percentage": 50,
        "use_denoising": True
    },
    
    "preview": {
        "description": "Quick quality check",
        "engine": "CYCLES",
        "samples": 128,
        "resolution_percentage": 75,
        "use_denoising": True
    },
    
    "production": {
        "description": "High quality for final output",
        "engine": "CYCLES",
        "samples": 512,
        "resolution_percentage": 100,
        "use_denoising": True
    },
    
    "final": {
        "description": "Maximum quality",
        "engine": "CYCLES",
        "samples": 2048,
        "resolution_percentage": 100,
        "use_denoising": False
    }
}

# Scene lighting suggestions based on object/scene type
SCENE_TYPE_LIGHTING = {
    "outdoor": {
        "hdri": "outdoor_day",
        "lighting_rig": "outdoor",
        "atmosphere": "haze",
        "camera": "normal"
    },
    "studio": {
        "hdri": "studio",
        "lighting_rig": "studio",
        "atmosphere": "none",
        "camera": "portrait"
    },
    "product": {
        "hdri": "studio",
        "lighting_rig": "studio",
        "atmosphere": "none",
        "camera": "normal"
    },
    "dramatic": {
        "hdri": "sunset",
        "lighting_rig": "dramatic",
        "atmosphere": "god_rays",
        "camera": "portrait"
    },
    "night": {
        "hdri": "night",
        "lighting_rig": "night",
        "atmosphere": "fog",
        "camera": "normal"
    },
    "interior": {
        "hdri": "interior",
        "lighting_rig": "three_point",
        "atmosphere": "haze",
        "camera": "wide"
    }
}

def suggest_scene_lighting(scene_description: str) -> dict:
    """
    Suggest lighting setup based on scene description
    
    Args:
        scene_description: Description of the scene or object
        
    Returns:
        Dictionary with suggested hdri, lighting_rig, atmosphere, camera
    """
    desc_lower = scene_description.lower()
    
    # Check for keywords
    if any(word in desc_lower for word in ["outdoor", "street", "city", "park"]):
        return SCENE_TYPE_LIGHTING["outdoor"]
    elif any(word in desc_lower for word in ["night", "evening", "dark"]):
        return SCENE_TYPE_LIGHTING["night"]
    elif any(word in desc_lower for word in ["studio", "product", "commercial"]):
        return SCENE_TYPE_LIGHTING["product"]
    elif any(word in desc_lower for word in ["dramatic", "cinematic", "moody"]):
        return SCENE_TYPE_LIGHTING["dramatic"]
    elif any(word in desc_lower for word in ["interior", "room", "indoor"]):
        return SCENE_TYPE_LIGHTING["interior"]
    else:
        # Default to outdoor
        return SCENE_TYPE_LIGHTING["outdoor"]

def calculate_camera_position(object_bounds: list, camera_type: str = "normal") -> dict:
    """
    Calculate optimal camera position based on object bounding box
    
    Args:
        object_bounds: [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        camera_type: Type of shot (front, threequarter, side, top)
        
    Returns:
        Dictionary with location and rotation
    """
    if not object_bounds or len(object_bounds) != 2:
        # Default position
        return {
            "location": (7.5, -7.5, 5.5),
            "rotation": (63.0, 0.0, 45.0)
        }
    
    min_corner = object_bounds[0]
    max_corner = object_bounds[1]
    
    # Calculate object center and size
    center = [
        (min_corner[0] + max_corner[0]) / 2,
        (min_corner[1] + max_corner[1]) / 2,
        (min_corner[2] + max_corner[2]) / 2
    ]
    
    size = [
        max_corner[0] - min_corner[0],
        max_corner[1] - min_corner[1],
        max_corner[2] - min_corner[2]
    ]
    
    max_size = max(size)
    distance = max_size * 2.5  # Distance multiplier
    
    if camera_type == "front":
        location = [center[0], center[1] - distance, center[2] + max_size * 0.3]
        rotation = [75.0, 0.0, 0.0]
    elif camera_type == "side":
        location = [center[0] + distance, center[1], center[2] + max_size * 0.3]
        rotation = [75.0, 0.0, 90.0]
    elif camera_type == "top":
        location = [center[0], center[1], center[2] + distance]
        rotation = [0.0, 0.0, 0.0]
    else:  # three_quarter (default)
        location = [
            center[0] + distance * 0.7,
            center[1] - distance * 0.7,
            center[2] + max_size * 0.6
        ]
        rotation = [63.0, 0.0, 45.0]
    
    return {
        "location": location,
        "rotation": rotation,
        "target": center
    }
