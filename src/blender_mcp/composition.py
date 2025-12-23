"""
Composition System for Blender MCP
Provides intelligent camera framing and composition analysis using cinematography principles.
"""

import math
from typing import Dict, List, Tuple, Optional, Any

# Composition rules with their mathematical definitions
COMPOSITION_RULES = {
    "rule_of_thirds": {
        "name": "Rule of Thirds",
        "description": "Position subject at intersection of thirds grid",
        "grid_points": [
            (1/3, 1/3), (2/3, 1/3),  # Top intersections
            (1/3, 2/3), (2/3, 2/3),  # Bottom intersections
        ],
        "strength_lines": [(1/3, 0, 1/3, 1), (2/3, 0, 2/3, 1), (0, 1/3, 1, 1/3), (0, 2/3, 1, 2/3)],
        "ideal_for": ["portraits", "landscapes", "products", "general"],
        "headroom": 0.15,  # 15% from top
        "nose_room": 0.55,  # Subject at 55% horizontal
    },
    
    "golden_ratio": {
        "name": "Golden Ratio (Phi Grid)",
        "description": "Arrange elements using phi (1.618) proportions",
        "grid_points": [
            (0.382, 0.382), (0.618, 0.382),  # Phi intersections
            (0.382, 0.618), (0.618, 0.618),
        ],
        "strength_lines": [(0.382, 0, 0.382, 1), (0.618, 0, 0.618, 1), (0, 0.382, 1, 0.382), (0, 0.618, 1, 0.618)],
        "ideal_for": ["fine_art", "architecture", "nature"],
        "headroom": 0.12,
        "nose_room": 0.618,  # Golden ratio position
    },
    
    "center_composition": {
        "name": "Center Composition",
        "description": "Subject centered for symmetry and impact",
        "grid_points": [(0.5, 0.5)],
        "strength_lines": [(0.5, 0, 0.5, 1), (0, 0.5, 1, 0.5)],
        "ideal_for": ["symmetrical", "minimalist", "abstract", "patterns"],
        "headroom": 0.5,
        "nose_room": 0.5,
    },
    
    "diagonal": {
        "name": "Diagonal Composition",
        "description": "Dynamic energy along diagonal lines",
        "grid_points": [(0.25, 0.75), (0.75, 0.25)],
        "strength_lines": [(0, 1, 1, 0), (0, 0, 1, 1)],  # Two diagonals
        "ideal_for": ["action", "dynamic", "tension", "movement"],
        "headroom": 0.25,
        "nose_room": 0.65,
    },
    
    "frame_within_frame": {
        "name": "Frame Within Frame",
        "description": "Use environmental elements to frame subject",
        "grid_points": [(0.5, 0.5)],  # Subject centered in inner frame
        "strength_lines": [(0.15, 0.15, 0.85, 0.15), (0.85, 0.15, 0.85, 0.85), 
                          (0.85, 0.85, 0.15, 0.85), (0.15, 0.85, 0.15, 0.15)],  # Inner frame box
        "ideal_for": ["storytelling", "depth", "context"],
        "headroom": 0.35,
        "nose_room": 0.5,
    },
    
    "leading_lines": {
        "name": "Leading Lines",
        "description": "Guide viewer's eye to subject",
        "grid_points": [(0.618, 0.618)],  # Subject at terminus
        "strength_lines": [(0, 1, 0.618, 0.618), (0, 0, 0.618, 0.618), (1, 0, 0.618, 0.618)],  # Converging lines
        "ideal_for": ["depth", "perspective", "architecture", "roads"],
        "headroom": 0.2,
        "nose_room": 0.7,
    },
}

# Shot type definitions based on framing
SHOT_TYPES = {
    "extreme_closeup": {
        "name": "Extreme Close-Up (ECU)",
        "description": "Focus on small detail, fills frame",
        "frame_fill": 0.95,  # Object fills 95% of frame
        "distance_multiplier": 1.2,  # 1.2x object size
        "focal_length": 85,
        "dof_fstop": 1.8,  # Very shallow DOF
        "ideal_for": ["details", "emotions", "textures", "macro"],
        "composition_rule": "center_composition",
    },
    
    "closeup": {
        "name": "Close-Up (CU)",
        "description": "Subject fills frame with minimal background",
        "frame_fill": 0.75,  # 75% frame fill
        "distance_multiplier": 1.8,
        "focal_length": 85,
        "dof_fstop": 2.8,
        "ideal_for": ["portraits", "products", "expressions"],
        "composition_rule": "rule_of_thirds",
    },
    
    "medium_closeup": {
        "name": "Medium Close-Up (MCU)",
        "description": "Subject with some surrounding context",
        "frame_fill": 0.55,
        "distance_multiplier": 2.5,
        "focal_length": 50,
        "dof_fstop": 4.0,
        "ideal_for": ["interviews", "product_context", "interaction"],
        "composition_rule": "rule_of_thirds",
    },
    
    "medium_shot": {
        "name": "Medium Shot (MS)",
        "description": "Subject and environment equally important",
        "frame_fill": 0.4,
        "distance_multiplier": 3.5,
        "focal_length": 50,
        "dof_fstop": 5.6,
        "ideal_for": ["general", "balanced", "storytelling"],
        "composition_rule": "golden_ratio",
    },
    
    "medium_wide": {
        "name": "Medium Wide Shot (MWS)",
        "description": "Subject in environment, shows setting",
        "frame_fill": 0.25,
        "distance_multiplier": 5.0,
        "focal_length": 35,
        "dof_fstop": 8.0,
        "ideal_for": ["establishing", "context", "location"],
        "composition_rule": "rule_of_thirds",
    },
    
    "wide_shot": {
        "name": "Wide Shot (WS)",
        "description": "Full environment, subject is part of scene",
        "frame_fill": 0.15,
        "distance_multiplier": 7.0,
        "focal_length": 24,
        "dof_fstop": 11.0,
        "ideal_for": ["landscapes", "architecture", "establishing"],
        "composition_rule": "rule_of_thirds",
    },
    
    "extreme_wide": {
        "name": "Extreme Wide Shot (EWS)",
        "description": "Vast environment, subject small or distant",
        "frame_fill": 0.08,
        "distance_multiplier": 10.0,
        "focal_length": 14,
        "dof_fstop": 16.0,
        "ideal_for": ["epic", "scale", "isolation", "grandeur"],
        "composition_rule": "golden_ratio",
    },
}

# Framing guidelines for different subjects
FRAMING_PRESETS = {
    "portrait_standard": {
        "name": "Standard Portrait",
        "headroom": 0.12,  # 12% space above head
        "nose_room": 0.55,  # 55% horizontal (looking right)
        "composition_rule": "rule_of_thirds",
        "shot_type": "closeup",
        "angle_tilt": 0,  # No tilt
        "look_room_multiplier": 1.5,  # Extra space in look direction
    },
    
    "portrait_dramatic": {
        "name": "Dramatic Portrait",
        "headroom": 0.08,  # Tight headroom
        "nose_room": 0.65,  # Off-center
        "composition_rule": "golden_ratio",
        "shot_type": "closeup",
        "angle_tilt": 2,  # Slight dutch angle
        "look_room_multiplier": 2.0,  # More dramatic space
    },
    
    "product_hero": {
        "name": "Hero Product Shot",
        "headroom": 0.15,
        "nose_room": 0.5,  # Centered horizontally
        "composition_rule": "center_composition",
        "shot_type": "medium_closeup",
        "angle_tilt": 0,
        "look_room_multiplier": 1.0,
    },
    
    "product_lifestyle": {
        "name": "Lifestyle Product Shot",
        "headroom": 0.2,
        "nose_room": 0.618,  # Golden ratio
        "composition_rule": "golden_ratio",
        "shot_type": "medium_shot",
        "angle_tilt": 0,
        "look_room_multiplier": 1.0,
    },
    
    "architecture_standard": {
        "name": "Architecture Standard",
        "headroom": 0.1,
        "nose_room": 0.5,
        "composition_rule": "rule_of_thirds",
        "shot_type": "wide_shot",
        "angle_tilt": 0,
        "look_room_multiplier": 1.0,
    },
    
    "architecture_dynamic": {
        "name": "Architecture Dynamic",
        "headroom": 0.15,
        "nose_room": 0.618,
        "composition_rule": "diagonal",
        "shot_type": "medium_wide",
        "angle_tilt": 3,  # Dynamic tilt
        "look_room_multiplier": 1.2,
    },
}

def calculate_composition_score(subject_position: Tuple[float, float], 
                                rule: str = "rule_of_thirds") -> Dict[str, Any]:
    """
    Calculate how well a subject position matches a composition rule.
    
    Args:
        subject_position: (x, y) position in normalized screen space (0-1)
        rule: Composition rule to evaluate against
        
    Returns:
        Dict with score (0-100) and analysis
    """
    if rule not in COMPOSITION_RULES:
        return {"score": 0, "error": f"Unknown rule: {rule}"}
    
    rule_data = COMPOSITION_RULES[rule]
    grid_points = rule_data["grid_points"]
    
    # Find closest grid point
    x, y = subject_position
    min_distance = float('inf')
    closest_point = None
    
    for gx, gy in grid_points:
        distance = math.sqrt((x - gx)**2 + (y - gy)**2)
        if distance < min_distance:
            min_distance = distance
            closest_point = (gx, gy)
    
    # Convert distance to score (0-100)
    # Perfect alignment (distance 0) = 100
    # Distance > 0.3 = 0
    max_distance = 0.3
    score = max(0, 100 * (1 - min_distance / max_distance))
    
    # Additional scoring factors
    edge_penalty = 0
    if x < 0.05 or x > 0.95 or y < 0.05 or y > 0.95:
        edge_penalty = 20  # Penalty for being too close to edges
    
    final_score = max(0, score - edge_penalty)
    
    return {
        "score": round(final_score, 1),
        "rule": rule_data["name"],
        "closest_point": closest_point,
        "distance": round(min_distance, 3),
        "recommendation": _get_score_recommendation(final_score),
        "adjustments": _suggest_adjustments(subject_position, closest_point) if final_score < 70 else None,
    }

def _get_score_recommendation(score: float) -> str:
    """Get text recommendation based on composition score."""
    if score >= 90:
        return "Excellent composition! Subject is well-positioned."
    elif score >= 70:
        return "Good composition. Minor adjustments could improve it."
    elif score >= 50:
        return "Acceptable composition. Consider repositioning for stronger impact."
    elif score >= 30:
        return "Weak composition. Subject should be repositioned."
    else:
        return "Poor composition. Major repositioning needed."

def _suggest_adjustments(current: Tuple[float, float], target: Tuple[float, float]) -> Dict[str, str]:
    """Suggest camera movements to improve composition."""
    cx, cy = current
    tx, ty = target
    
    suggestions = []
    
    # Horizontal adjustment
    h_diff = tx - cx
    if abs(h_diff) > 0.05:
        direction = "right" if h_diff > 0 else "left"
        amount = "significantly" if abs(h_diff) > 0.2 else "slightly"
        suggestions.append(f"Move camera {amount} to the {direction}")
    
    # Vertical adjustment
    v_diff = ty - cy
    if abs(v_diff) > 0.05:
        direction = "up" if v_diff > 0 else "down"
        amount = "significantly" if abs(v_diff) > 0.2 else "slightly"
        suggestions.append(f"Move camera {amount} {direction}")
    
    return {
        "horizontal_offset": round(h_diff, 3),
        "vertical_offset": round(v_diff, 3),
        "suggestions": suggestions if suggestions else ["Composition is well-aligned"],
    }

def suggest_shot_type(object_bounds: Dict[str, float], 
                     purpose: str = "general") -> str:
    """
    Suggest appropriate shot type based on object characteristics.
    
    Args:
        object_bounds: Dict with 'width', 'height', 'depth' of object
        purpose: Purpose of shot ('detail', 'general', 'establishing', 'product', 'portrait')
        
    Returns:
        Recommended shot type key
    """
    # Calculate object size (use diagonal)
    size = math.sqrt(object_bounds['width']**2 + 
                    object_bounds['height']**2 + 
                    object_bounds['depth']**2)
    
    # Map purpose to shot types
    purpose_map = {
        "detail": ["extreme_closeup", "closeup"],
        "macro": ["extreme_closeup"],
        "portrait": ["closeup", "medium_closeup"],
        "product": ["closeup", "medium_closeup", "medium_shot"],
        "general": ["medium_shot", "medium_wide"],
        "context": ["medium_wide", "wide_shot"],
        "establishing": ["wide_shot", "extreme_wide"],
        "landscape": ["wide_shot", "extreme_wide"],
        "epic": ["extreme_wide"],
    }
    
    # Get appropriate shot types for purpose
    candidates = purpose_map.get(purpose, ["medium_shot"])
    
    # For very small objects, prefer closer shots
    if size < 1.0:
        return "extreme_closeup" if "extreme_closeup" in candidates else candidates[0]
    elif size < 2.0:
        return "closeup" if "closeup" in candidates else candidates[0]
    else:
        return candidates[0]

def suggest_composition_rule(object_type: str, 
                            scene_context: str = "neutral") -> str:
    """
    Suggest appropriate composition rule based on object type and scene.
    
    Args:
        object_type: Type of object ('portrait', 'product', 'architecture', etc.)
        scene_context: Scene context ('symmetrical', 'dynamic', 'minimal', etc.)
        
    Returns:
        Recommended composition rule key
    """
    # Context-based suggestions
    if scene_context == "symmetrical" or scene_context == "minimal":
        return "center_composition"
    elif scene_context == "dynamic" or scene_context == "action":
        return "diagonal"
    elif scene_context == "depth" or scene_context == "perspective":
        return "leading_lines"
    
    # Object-based suggestions
    object_map = {
        "portrait": "rule_of_thirds",
        "face": "rule_of_thirds",
        "product": "golden_ratio",
        "architecture": "rule_of_thirds",
        "landscape": "rule_of_thirds",
        "nature": "golden_ratio",
        "abstract": "center_composition",
        "symmetrical": "center_composition",
        "pattern": "center_composition",
    }
    
    return object_map.get(object_type.lower(), "rule_of_thirds")

def calculate_camera_position(object_center: Tuple[float, float, float],
                              object_bounds: Dict[str, float],
                              shot_type: str,
                              composition_rule: str,
                              camera_angle: Tuple[float, float] = (15, 45)) -> Dict[str, Any]:
    """
    Calculate optimal camera position for composition.
    
    Args:
        object_center: (x, y, z) world position of object center
        object_bounds: Dict with 'width', 'height', 'depth'
        shot_type: Desired shot type key
        composition_rule: Composition rule to apply
        camera_angle: (elevation, azimuth) in degrees
        
    Returns:
        Dict with camera position, rotation, and settings
    """
    if shot_type not in SHOT_TYPES:
        shot_type = "medium_shot"
    
    shot_data = SHOT_TYPES[shot_type]
    rule_data = COMPOSITION_RULES.get(composition_rule, COMPOSITION_RULES["rule_of_thirds"])
    
    # Calculate distance based on shot type and object size
    object_size = max(object_bounds['width'], object_bounds['height'], object_bounds['depth'])
    distance = object_size * shot_data['distance_multiplier']
    
    # Convert camera angle to radians
    elevation_rad = math.radians(camera_angle[0])
    azimuth_rad = math.radians(camera_angle[1])
    
    # Calculate camera position in spherical coordinates
    ox, oy, oz = object_center
    
    camera_x = ox + distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
    camera_y = oy + distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
    camera_z = oz + distance * math.sin(elevation_rad)
    
    # Adjust for composition rule (offset camera to position subject at grid point)
    # Use the first grid point of the rule
    grid_point = rule_data['grid_points'][0]
    
    # Horizontal offset based on grid point
    h_offset = (grid_point[0] - 0.5) * object_size * 0.3
    camera_x += h_offset * math.sin(azimuth_rad)
    camera_y -= h_offset * math.cos(azimuth_rad)
    
    # Vertical offset based on headroom
    v_offset = (rule_data['headroom'] - 0.5) * object_size * 0.5
    camera_z += v_offset
    
    return {
        "position": (round(camera_x, 3), round(camera_y, 3), round(camera_z, 3)),
        "target": object_center,
        "focal_length": shot_data['focal_length'],
        "fstop": shot_data['dof_fstop'],
        "shot_type": shot_data['name'],
        "composition_rule": rule_data['name'],
        "distance": round(distance, 3),
        "frame_fill": shot_data['frame_fill'],
    }

def get_framing_guide_data(composition_rule: str, 
                          resolution: Tuple[int, int] = (1920, 1080)) -> Dict[str, Any]:
    """
    Get data for drawing composition guide overlays.
    
    Args:
        composition_rule: Rule to visualize
        resolution: Render resolution (width, height)
        
    Returns:
        Dict with line coordinates and labels for overlay
    """
    if composition_rule not in COMPOSITION_RULES:
        return {"error": f"Unknown rule: {composition_rule}"}
    
    rule_data = COMPOSITION_RULES[composition_rule]
    width, height = resolution
    
    # Convert normalized coordinates to pixel coordinates
    lines = []
    for line in rule_data['strength_lines']:
        x1 = int(line[0] * width)
        y1 = int(line[1] * height)
        x2 = int(line[2] * width)
        y2 = int(line[3] * height)
        lines.append({'start': (x1, y1), 'end': (x2, y2)})
    
    points = []
    for point in rule_data['grid_points']:
        x = int(point[0] * width)
        y = int(point[1] * height)
        points.append({'position': (x, y), 'is_power_point': True})
    
    return {
        "rule_name": rule_data['name'],
        "description": rule_data['description'],
        "lines": lines,
        "points": points,
        "resolution": resolution,
    }

# Preset combinations for quick setup
COMPOSITION_PRESETS = {
    "portrait_pro": {
        "name": "Professional Portrait",
        "composition_rule": "rule_of_thirds",
        "shot_type": "closeup",
        "camera_angle": (10, 45),
        "framing": "portrait_standard",
    },
    
    "portrait_cinematic": {
        "name": "Cinematic Portrait",
        "composition_rule": "golden_ratio",
        "shot_type": "medium_closeup",
        "camera_angle": (5, 30),
        "framing": "portrait_dramatic",
    },
    
    "product_hero": {
        "name": "Hero Product Shot",
        "composition_rule": "center_composition",
        "shot_type": "closeup",
        "camera_angle": (20, 45),
        "framing": "product_hero",
    },
    
    "product_lifestyle": {
        "name": "Lifestyle Product",
        "composition_rule": "golden_ratio",
        "shot_type": "medium_shot",
        "camera_angle": (15, 60),
        "framing": "product_lifestyle",
    },
    
    "architecture_hero": {
        "name": "Architecture Hero",
        "composition_rule": "rule_of_thirds",
        "shot_type": "wide_shot",
        "camera_angle": (10, 30),
        "framing": "architecture_standard",
    },
    
    "architecture_dramatic": {
        "name": "Dramatic Architecture",
        "composition_rule": "diagonal",
        "shot_type": "medium_wide",
        "camera_angle": (25, 45),
        "framing": "architecture_dynamic",
    },
    
    "landscape_classic": {
        "name": "Classic Landscape",
        "composition_rule": "rule_of_thirds",
        "shot_type": "wide_shot",
        "camera_angle": (5, 0),
        "framing": "architecture_standard",
    },
    
    "landscape_epic": {
        "name": "Epic Landscape",
        "composition_rule": "golden_ratio",
        "shot_type": "extreme_wide",
        "camera_angle": (15, 0),
        "framing": "architecture_standard",
    },
}
