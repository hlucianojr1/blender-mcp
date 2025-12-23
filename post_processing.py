"""
Post-processing presets for Blender MCP Addon
Minimal version for addon import
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
            "angle": 30.0
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
    "organic": ["character", "creature", "animal", "human", "body", "head", "face"],
    "high_detail": ["phone", "telephone", "booth", "vehicle", "car", "jewelry", "watch", "bottle"],
    "mechanical": ["robot", "machine", "engine", "gear", "weapon", "tool", "equipment"],
    "architectural": ["building", "wall", "floor", "door", "window", "column", "arch"],
}

def get_suggested_preset(object_name: str) -> str:
    """Suggest an enhancement preset based on object name keywords"""
    object_name_lower = object_name.lower()
    
    for preset_type, keywords in OBJECT_TYPE_PRESETS.items():
        for keyword in keywords:
            if keyword in object_name_lower:
                return preset_type
    
    return "smooth"  # Default preset

def analyze_mesh_quality(mesh_stats: dict) -> dict:
    """Analyze mesh quality and suggest improvements"""
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
