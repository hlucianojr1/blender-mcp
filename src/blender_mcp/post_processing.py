"""
Post-Processing Pipeline for Blender MCP
Enhances geometry quality of AI-generated and imported models
"""

# Enhancement strategies based on object analysis
ENHANCEMENT_PRESETS = {
    "smooth": {
        "subdivision": {
            "enabled": True,
            "levels": 2,
            "render_levels": 3,
            "adaptive": True,
            "use_creases": True
        },
        "edge_split": {
            "enabled": True,
            "angle": 30.0  # degrees
        },
        "shade_smooth": True,
        "auto_smooth": {
            "enabled": True,
            "angle": 30.0
        }
    },
    
    "high_detail": {
        "subdivision": {
            "enabled": True,
            "levels": 3,
            "render_levels": 4,
            "adaptive": True,
            "use_creases": True
        },
        "edge_split": {
            "enabled": True,
            "angle": 20.0
        },
        "shade_smooth": True,
        "auto_smooth": {
            "enabled": True,
            "angle": 20.0
        },
        "bevel": {
            "enabled": True,
            "width": 0.01,
            "segments": 2
        }
    },
    
    "mechanical": {
        "subdivision": {
            "enabled": False
        },
        "edge_split": {
            "enabled": True,
            "angle": 45.0
        },
        "bevel": {
            "enabled": True,
            "width": 0.02,
            "segments": 3,
            "only_vertices": False
        },
        "shade_smooth": True,
        "auto_smooth": {
            "enabled": True,
            "angle": 45.0
        }
    },
    
    "organic": {
        "subdivision": {
            "enabled": True,
            "levels": 2,
            "render_levels": 3,
            "adaptive": False,
            "use_creases": False
        },
        "remesh": {
            "enabled": True,
            "mode": "SMOOTH",
            "octree_depth": 6
        },
        "shade_smooth": True,
        "auto_smooth": {
            "enabled": False
        }
    },
    
    "architectural": {
        "subdivision": {
            "enabled": True,
            "levels": 1,
            "render_levels": 2,
            "adaptive": True,
            "use_creases": True
        },
        "edge_split": {
            "enabled": True,
            "angle": 30.0
        },
        "bevel": {
            "enabled": True,
            "width": 0.005,
            "segments": 2
        },
        "shade_smooth": False
    }
}

# Object type detection keywords
OBJECT_TYPE_PRESETS = {
    # Smooth organic objects
    "organic": ["character", "creature", "animal", "human", "body", "head", "face"],
    
    # High detail props
    "high_detail": ["phone", "telephone", "booth", "vehicle", "car", "jewelry", "watch", "bottle"],
    
    # Mechanical/hard surface
    "mechanical": ["robot", "machine", "engine", "gear", "weapon", "tool", "equipment"],
    
    # Architectural elements
    "architectural": ["building", "wall", "floor", "door", "window", "column", "arch"],
}

def get_suggested_preset(object_name: str) -> str:
    """
    Suggest an enhancement preset based on object name keywords
    
    Args:
        object_name: Name of the object
        
    Returns:
        Suggested preset name, or 'smooth' as default
    """
    object_name_lower = object_name.lower()
    
    for preset_type, keywords in OBJECT_TYPE_PRESETS.items():
        for keyword in keywords:
            if keyword in object_name_lower:
                return preset_type
    
    return "smooth"  # Default preset

def list_available_presets() -> list:
    """
    List all available enhancement presets
    
    Returns:
        List of preset names
    """
    return list(ENHANCEMENT_PRESETS.keys())

def get_preset_info(preset_name: str) -> dict:
    """
    Get information about an enhancement preset
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        Preset configuration dictionary, or None if not found
    """
    return ENHANCEMENT_PRESETS.get(preset_name)

# Normal map baking configurations
NORMAL_MAP_PRESETS = {
    "low_detail": {
        "samples": 16,
        "distance": 0.1,
        "resolution": 1024
    },
    "medium_detail": {
        "samples": 32,
        "distance": 0.05,
        "resolution": 2048
    },
    "high_detail": {
        "samples": 64,
        "distance": 0.02,
        "resolution": 4096
    }
}

def calculate_optimal_subdivision_levels(poly_count: int) -> dict:
    """
    Calculate optimal subdivision levels based on polygon count
    
    Args:
        poly_count: Current polygon count of the mesh
        
    Returns:
        Dictionary with viewport_levels and render_levels
    """
    if poly_count < 1000:
        # Very low poly - can afford more subdivision
        return {"viewport_levels": 3, "render_levels": 4}
    elif poly_count < 5000:
        # Low poly
        return {"viewport_levels": 2, "render_levels": 3}
    elif poly_count < 20000:
        # Medium poly
        return {"viewport_levels": 1, "render_levels": 2}
    else:
        # High poly - minimal subdivision
        return {"viewport_levels": 0, "render_levels": 1}

def analyze_mesh_quality(mesh_stats: dict) -> dict:
    """
    Analyze mesh quality and suggest improvements
    
    Args:
        mesh_stats: Dictionary with mesh statistics (vertex_count, face_count, etc.)
        
    Returns:
        Analysis results with suggested improvements
    """
    suggestions = []
    priority = "low"
    
    vertex_count = mesh_stats.get("vertex_count", 0)
    face_count = mesh_stats.get("face_count", 0)
    
    # Check if mesh is too simple
    if face_count < 500:
        suggestions.append("Very low polygon count - consider subdivision")
        priority = "high"
    elif face_count < 2000:
        suggestions.append("Low polygon count - subdivision recommended")
        priority = "medium"
    
    # Check for non-manifold geometry
    if mesh_stats.get("non_manifold", False):
        suggestions.append("Non-manifold geometry detected - may cause issues")
        priority = "high"
    
    # Check for loose geometry
    if mesh_stats.get("loose_verts", 0) > 0:
        suggestions.append(f"{mesh_stats['loose_verts']} loose vertices detected")
    
    # Check face types
    tris = mesh_stats.get("triangles", 0)
    quads = mesh_stats.get("quads", 0)
    ngons = mesh_stats.get("ngons", 0)
    
    if ngons > face_count * 0.1:
        suggestions.append("High ngon count - may affect subdivision")
    
    return {
        "priority": priority,
        "suggestions": suggestions,
        "recommended_preset": "high_detail" if face_count < 1000 else "smooth"
    }
