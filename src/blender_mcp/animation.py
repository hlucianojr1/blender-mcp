"""
Animation System for Blender MCP

Provides presets and tools for creating 3D character animations,
focused on third-person game animations like jump, aim, recoil, limp, etc.

Supports:
- Keyframe animation with various interpolation types
- Armature/bone pose manipulation
- Action creation and management
- NLA (Non-Linear Animation) track/strip management
- Animation presets for common game character movements
"""

import math
from typing import Dict, List, Any, Optional, Tuple

# ============================================================================
# BONE NAMING CONVENTIONS
# ============================================================================
# Support multiple rigging conventions with mappings

BONE_MAPPINGS = {
    "mixamo": {
        "root": "mixamorig:Hips",
        "spine": "mixamorig:Spine",
        "spine1": "mixamorig:Spine1",
        "spine2": "mixamorig:Spine2",
        "neck": "mixamorig:Neck",
        "head": "mixamorig:Head",
        "shoulder_l": "mixamorig:LeftShoulder",
        "shoulder_r": "mixamorig:RightShoulder",
        "arm_upper_l": "mixamorig:LeftArm",
        "arm_upper_r": "mixamorig:RightArm",
        "arm_lower_l": "mixamorig:LeftForeArm",
        "arm_lower_r": "mixamorig:RightForeArm",
        "hand_l": "mixamorig:LeftHand",
        "hand_r": "mixamorig:RightHand",
        "leg_upper_l": "mixamorig:LeftUpLeg",
        "leg_upper_r": "mixamorig:RightUpLeg",
        "leg_lower_l": "mixamorig:LeftLeg",
        "leg_lower_r": "mixamorig:RightLeg",
        "foot_l": "mixamorig:LeftFoot",
        "foot_r": "mixamorig:RightFoot",
        "toe_l": "mixamorig:LeftToeBase",
        "toe_r": "mixamorig:RightToeBase",
    },
    "rigify": {
        "root": "root",
        "spine": "spine_fk.001",
        "spine1": "spine_fk.002",
        "spine2": "spine_fk.003",
        "neck": "neck",
        "head": "head",
        "shoulder_l": "shoulder.L",
        "shoulder_r": "shoulder.R",
        "arm_upper_l": "upper_arm_fk.L",
        "arm_upper_r": "upper_arm_fk.R",
        "arm_lower_l": "forearm_fk.L",
        "arm_lower_r": "forearm_fk.R",
        "hand_l": "hand_fk.L",
        "hand_r": "hand_fk.R",
        "leg_upper_l": "thigh_fk.L",
        "leg_upper_r": "thigh_fk.R",
        "leg_lower_l": "shin_fk.L",
        "leg_lower_r": "shin_fk.R",
        "foot_l": "foot_fk.L",
        "foot_r": "foot_fk.R",
        "toe_l": "toe.L",
        "toe_r": "toe.R",
    },
    "generic": {
        "root": "Hips",
        "spine": "Spine",
        "spine1": "Spine1",
        "spine2": "Spine2",
        "neck": "Neck",
        "head": "Head",
        "shoulder_l": "LeftShoulder",
        "shoulder_r": "RightShoulder",
        "arm_upper_l": "LeftArm",
        "arm_upper_r": "RightArm",
        "arm_lower_l": "LeftForeArm",
        "arm_lower_r": "RightForeArm",
        "hand_l": "LeftHand",
        "hand_r": "RightHand",
        "leg_upper_l": "LeftUpLeg",
        "leg_upper_r": "RightUpLeg",
        "leg_lower_l": "LeftLeg",
        "leg_lower_r": "RightLeg",
        "foot_l": "LeftFoot",
        "foot_r": "RightFoot",
        "toe_l": "LeftToeBase",
        "toe_r": "RightToeBase",
    },
}

# ============================================================================
# INTERPOLATION TYPES
# ============================================================================

INTERPOLATION_TYPES = {
    "constant": "CONSTANT",      # No interpolation, instant value change
    "linear": "LINEAR",          # Linear interpolation
    "bezier": "BEZIER",          # Smooth bezier curves (default)
    "sine": "SINE",              # Sine wave easing
    "quad": "QUAD",              # Quadratic easing
    "cubic": "CUBIC",            # Cubic easing
    "quart": "QUART",            # Quartic easing
    "quint": "QUINT",            # Quintic easing
    "expo": "EXPO",              # Exponential easing
    "circ": "CIRC",              # Circular easing
    "back": "BACK",              # Overshoot easing
    "bounce": "BOUNCE",          # Bouncing effect
    "elastic": "ELASTIC",        # Elastic/spring effect
}

EASING_TYPES = {
    "auto": "AUTO",
    "ease_in": "EASE_IN",
    "ease_out": "EASE_OUT",
    "ease_in_out": "EASE_IN_OUT",
}

# ============================================================================
# ANIMATION PRESETS FOR GAME CHARACTERS
# ============================================================================

ANIMATION_PRESETS: Dict[str, Dict[str, Any]] = {
    # ----- LOCOMOTION -----
    "idle": {
        "description": "Standing idle with subtle breathing motion",
        "category": "locomotion",
        "frame_range": (1, 60),
        "fps": 30,
        "loop": True,
        "root_motion": False,
        "keyframes": {
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (2, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "spine1": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (1, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "shoulder_l": [
                {"frame": 1, "rotation": (0, 0, 2), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, 2), "interpolation": "bezier"},
            ],
            "shoulder_r": [
                {"frame": 1, "rotation": (0, 0, -2), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, -2), "interpolation": "bezier"},
            ],
        },
    },
    
    "walk": {
        "description": "Basic walk cycle",
        "category": "locomotion",
        "frame_range": (1, 30),
        "fps": 30,
        "loop": True,
        "root_motion": True,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "interpolation": "linear"},
                {"frame": 30, "location": (0, 1.0, 0), "interpolation": "linear"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 23, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-30, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 23, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (30, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_l": [
                {"frame": 1, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 23, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (45, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 23, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (20, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-20, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (0, 3, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, -3, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 3, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "run": {
        "description": "Running cycle with forward momentum",
        "category": "locomotion",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": True,
        "root_motion": True,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "interpolation": "linear"},
                {"frame": 20, "location": (0, 2.5, 0), "interpolation": "linear"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (-50, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (50, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-50, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (50, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-50, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (50, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_l": [
                {"frame": 1, "rotation": (90, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (60, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (90, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (60, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (45, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-45, 0, 0), "interpolation": "bezier"},
            ],
            "arm_lower_l": [
                {"frame": 1, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-45, 0, 0), "interpolation": "bezier"},
            ],
            "arm_lower_r": [
                {"frame": 1, "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (-10, 5, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-10, -5, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-10, 5, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "sprint": {
        "description": "Maximum speed sprinting cycle",
        "category": "locomotion",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": True,
        "root_motion": True,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, 0, 0), "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "location": (0, 0.08, 0.15), "rotation": (8, -5, 0), "interpolation": "bezier"},
                {"frame": 10, "location": (0, 0, 0), "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "location": (0, 0.08, 0.15), "rotation": (8, 5, 0), "interpolation": "bezier"},
                {"frame": 20, "location": (0, 0, 0), "rotation": (5, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (15, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (60, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-15, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-30, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (60, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-15, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (60, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (60, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftArm": [
                {"frame": 1, "rotation": (45, 0, -25), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-35, 0, -25), "interpolation": "bezier"},
                {"frame": 20, "rotation": (45, 0, -25), "interpolation": "bezier"},
            ],
            "mixamorig:RightArm": [
                {"frame": 1, "rotation": (-35, 0, 25), "interpolation": "bezier"},
                {"frame": 10, "rotation": (45, 0, 25), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-35, 0, 25), "interpolation": "bezier"},
            ],
        },
    },
    
    "crouch_idle": {
        "description": "Crouched standing with subtle breathing",
        "category": "locomotion",
        "frame_range": (1, 60),
        "fps": 30,
        "loop": True,
        "root_motion": False,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, -0.4, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, -0.38, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "location": (0, -0.4, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (-15, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-13, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (-15, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (85, 0, 5), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (85, 0, -5), "interpolation": "bezier"},
            ],
            "mixamorig:LeftLeg": [
                {"frame": 1, "rotation": (-120, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightLeg": [
                {"frame": 1, "rotation": (-120, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "crouch_walk": {
        "description": "Crouched slow walking cycle",
        "category": "locomotion",
        "frame_range": (1, 40),
        "fps": 30,
        "loop": True,
        "root_motion": True,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, -0.4, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "location": (0, -0.38, 0.05), "rotation": (25, -3, 0), "interpolation": "bezier"},
                {"frame": 20, "location": (0, -0.4, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, -0.38, 0.05), "rotation": (25, 3, 0), "interpolation": "bezier"},
                {"frame": 40, "location": (0, -0.4, 0), "rotation": (25, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (-15, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (70, 0, 5), "interpolation": "bezier"},
                {"frame": 10, "rotation": (95, 0, 5), "interpolation": "bezier"},
                {"frame": 20, "rotation": (70, 0, 5), "interpolation": "bezier"},
                {"frame": 30, "rotation": (80, 0, 5), "interpolation": "bezier"},
                {"frame": 40, "rotation": (70, 0, 5), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (95, 0, -5), "interpolation": "bezier"},
                {"frame": 10, "rotation": (70, 0, -5), "interpolation": "bezier"},
                {"frame": 20, "rotation": (80, 0, -5), "interpolation": "bezier"},
                {"frame": 30, "rotation": (95, 0, -5), "interpolation": "bezier"},
                {"frame": 40, "rotation": (95, 0, -5), "interpolation": "bezier"},
            ],
        },
    },
    
    "jump_start": {
        "description": "Jump takeoff anticipation",
        "category": "locomotion",
        "frame_range": (1, 10),
        "fps": 30,
        "loop": False,
        "root_motion": True,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "location": (0, -0.15, 0), "rotation": (10, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "location": (0, 0.1, 0), "rotation": (-5, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-20, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-20, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftArm": [
                {"frame": 1, "rotation": (0, 0, -45), "interpolation": "bezier"},
                {"frame": 5, "rotation": (30, 0, -45), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-60, 0, -30), "interpolation": "bezier"},
            ],
            "mixamorig:RightArm": [
                {"frame": 1, "rotation": (0, 0, 45), "interpolation": "bezier"},
                {"frame": 5, "rotation": (30, 0, 45), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-60, 0, 30), "interpolation": "bezier"},
            ],
        },
    },
    
    "jump_loop": {
        "description": "Mid-air floating loop",
        "category": "locomotion",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": True,
        "root_motion": False,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, 0.1, 0), "rotation": (-5, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "location": (0, 0.12, 0), "rotation": (-3, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "location": (0, 0.1, 0), "rotation": (-5, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (-15, 0, 10), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-10, 0, 10), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-15, 0, 10), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (5, 0, -10), "interpolation": "bezier"},
                {"frame": 10, "rotation": (10, 0, -10), "interpolation": "bezier"},
                {"frame": 20, "rotation": (5, 0, -10), "interpolation": "bezier"},
            ],
            "mixamorig:LeftArm": [
                {"frame": 1, "rotation": (-45, 0, -60), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-40, 0, -65), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-45, 0, -60), "interpolation": "bezier"},
            ],
            "mixamorig:RightArm": [
                {"frame": 1, "rotation": (-45, 0, 60), "interpolation": "bezier"},
                {"frame": 10, "rotation": (-40, 0, 65), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-45, 0, 60), "interpolation": "bezier"},
            ],
        },
    },
    
    "jump_land": {
        "description": "Landing impact and recovery",
        "category": "locomotion",
        "frame_range": (1, 15),
        "fps": 30,
        "loop": False,
        "root_motion": True,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, 0.05, 0), "rotation": (-5, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "location": (0, -0.2, 0), "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpLeg": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (50, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpLeg": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (50, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftLeg": [
                {"frame": 1, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (-60, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightLeg": [
                {"frame": 1, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (-60, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    # ----- ACTIONS -----
    "jump": {
        "description": "Vertical jump with anticipation and landing",
        "category": "action",
        "frame_range": (1, 45),
        "fps": 30,
        "loop": False,
        "root_motion": True,
        "keyframes": {
            "root": [
                # Anticipation (crouch down)
                {"frame": 1, "location": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "location": (0, 0, -0.2), "interpolation": "bezier"},
                # Jump up
                {"frame": 15, "location": (0, 0, 1.5), "interpolation": "bezier", "easing": "ease_out"},
                # Peak
                {"frame": 25, "location": (0, 0, 1.8), "interpolation": "bezier"},
                # Fall
                {"frame": 35, "location": (0, 0, 0.2), "interpolation": "bezier", "easing": "ease_in"},
                # Land
                {"frame": 40, "location": (0, 0, -0.1), "interpolation": "bezier"},
                {"frame": 45, "location": (0, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (-60, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 35, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (-50, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (-60, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 35, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (-50, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 35, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (70, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 35, "rotation": (45, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (70, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-120, 0, -30), "interpolation": "bezier"},
                {"frame": 25, "rotation": (-90, 0, -20), "interpolation": "bezier"},
                {"frame": 35, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-120, 0, 30), "interpolation": "bezier"},
                {"frame": 25, "rotation": (-90, 0, 20), "interpolation": "bezier"},
                {"frame": 35, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-15, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 45, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "crouch": {
        "description": "Transition to crouching position",
        "category": "action",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "location": (0, 0, -0.5), "interpolation": "bezier"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-70, 0, 10), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-70, 0, -10), "interpolation": "bezier"},
            ],
            "leg_lower_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (100, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (100, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (25, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "roll": {
        "description": "Combat roll/dodge forward",
        "category": "action",
        "frame_range": (1, 30),
        "fps": 30,
        "loop": False,
        "root_motion": True,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "location": (0, 0.5, 0.3), "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "location": (0, 1.2, 0.5), "rotation": (-180, 0, 0), "interpolation": "bezier"},
                {"frame": 22, "location": (0, 1.8, 0.3), "rotation": (-270, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, 2.2, 0), "rotation": (-360, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-30, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 8, "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-30, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (0, 0, -60), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, -90), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, -30), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 60), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 90), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 30), "interpolation": "bezier"},
            ],
        },
    },
    
    # ----- COMBAT -----
    "aim_weapon": {
        "description": "Raise weapon to aiming position (rifle/pistol)",
        "category": "combat",
        "frame_range": (1, 15),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-5, -15, 0), "interpolation": "bezier"},
            ],
            "spine1": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-5, -10, 0), "interpolation": "bezier"},
            ],
            "shoulder_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, -20), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-70, 0, -45), "interpolation": "bezier"},
            ],
            "arm_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-45, 0, 0), "interpolation": "bezier"},
            ],
            "shoulder_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 30), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-60, 30, 45), "interpolation": "bezier"},
            ],
            "arm_lower_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "head": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, -10, 5), "interpolation": "bezier"},
            ],
        },
    },
    
    "recoil": {
        "description": "Weapon recoil after shooting",
        "category": "combat",
        "frame_range": (1, 10),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "spine": [
                {"frame": 1, "rotation": (-5, -15, 0), "interpolation": "bezier"},
                {"frame": 3, "rotation": (5, -15, 0), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 10, "rotation": (-5, -15, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (-70, 0, -45), "interpolation": "bezier"},
                {"frame": 3, "rotation": (-55, 5, -50), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 10, "rotation": (-70, 0, -45), "interpolation": "bezier"},
            ],
            "arm_lower_r": [
                {"frame": 1, "rotation": (-45, 0, 0), "interpolation": "bezier"},
                {"frame": 3, "rotation": (-35, 0, 0), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 10, "rotation": (-45, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (-60, 30, 45), "interpolation": "bezier"},
                {"frame": 3, "rotation": (-50, 25, 50), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 10, "rotation": (-60, 30, 45), "interpolation": "bezier"},
            ],
            "head": [
                {"frame": 1, "rotation": (0, -10, 5), "interpolation": "bezier"},
                {"frame": 3, "rotation": (5, -8, 3), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 10, "rotation": (0, -10, 5), "interpolation": "bezier"},
            ],
        },
    },
    
    "melee_attack": {
        "description": "Basic melee swing attack",
        "category": "combat",
        "frame_range": (1, 25),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (0, 30, 0), "interpolation": "bezier"},
                {"frame": 12, "rotation": (0, -45, 0), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (-90, 45, -30), "interpolation": "bezier"},
                {"frame": 12, "rotation": (-30, -60, -60), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_lower_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (-90, 0, 0), "interpolation": "bezier"},
                {"frame": 12, "rotation": (-30, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 12, "rotation": (-20, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "aim_idle": {
        "description": "Weapon aimed with subtle breathing",
        "category": "combat",
        "frame_range": (1, 60),
        "fps": 30,
        "loop": True,
        "root_motion": False,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 1), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (5, 15, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (6, 15, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (5, 15, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightShoulder": [
                {"frame": 1, "rotation": (0, 25, 10), "interpolation": "bezier"},
            ],
            "mixamorig:RightArm": [
                {"frame": 1, "rotation": (45, 0, 45), "interpolation": "bezier"},
            ],
            "mixamorig:RightForeArm": [
                {"frame": 1, "rotation": (0, 60, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftShoulder": [
                {"frame": 1, "rotation": (0, -15, -5), "interpolation": "bezier"},
            ],
            "mixamorig:LeftArm": [
                {"frame": 1, "rotation": (60, -20, -45), "interpolation": "bezier"},
            ],
            "mixamorig:LeftForeArm": [
                {"frame": 1, "rotation": (0, -80, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "reload": {
        "description": "Weapon reload sequence with mag swap",
        "category": "combat",
        "frame_range": (1, 60),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "frame_markers": {
            "mag_out": 18,      # 30% - magazine removed
            "mag_in": 42        # 70% - new magazine inserted
        },
        "keyframes": {
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (5, 15, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (10, 0, -5), "interpolation": "bezier"},
                {"frame": 45, "rotation": (10, 0, -5), "interpolation": "bezier"},
                {"frame": 60, "rotation": (5, 15, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightArm": [
                {"frame": 1, "rotation": (45, 0, 45), "interpolation": "bezier"},
                {"frame": 60, "rotation": (45, 0, 45), "interpolation": "bezier"},
            ],
            "mixamorig:LeftArm": [
                {"frame": 1, "rotation": (60, -20, -45), "interpolation": "bezier"},
                {"frame": 10, "rotation": (20, 30, -30), "interpolation": "bezier"},
                {"frame": 18, "rotation": (0, 60, -20), "interpolation": "bezier"},   # mag_out
                {"frame": 30, "rotation": (-20, 40, -10), "interpolation": "bezier"},
                {"frame": 42, "rotation": (0, 60, -20), "interpolation": "bezier"},   # mag_in
                {"frame": 50, "rotation": (40, -10, -40), "interpolation": "bezier"},
                {"frame": 60, "rotation": (60, -20, -45), "interpolation": "bezier"},
            ],
            "mixamorig:LeftForeArm": [
                {"frame": 1, "rotation": (0, -80, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (0, -100, 0), "interpolation": "bezier"},
                {"frame": 18, "rotation": (0, -120, 0), "interpolation": "bezier"},
                {"frame": 42, "rotation": (0, -120, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, -80, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Head": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (15, -20, 0), "interpolation": "bezier"},  # Look at mag
                {"frame": 45, "rotation": (15, -20, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "cover_enter": {
        "description": "Transition into cover position",
        "category": "combat",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "location": (0, -0.25, 0), "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "location": (0, -0.35, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-10, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpperLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (70, 0, 10), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (70, 0, -10), "interpolation": "bezier"},
            ],
            "mixamorig:LeftLowerLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightLowerLeg": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpperArm": [
                {"frame": 1, "rotation": (0, 0, -45), "interpolation": "bezier"},
                {"frame": 20, "rotation": (30, 20, -30), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperArm": [
                {"frame": 1, "rotation": (0, 0, 45), "interpolation": "bezier"},
                {"frame": 20, "rotation": (30, -20, 30), "interpolation": "bezier"},
            ],
        },
    },
    
    "cover_idle": {
        "description": "Crouched behind cover with subtle breathing",
        "category": "combat",
        "frame_range": (1, 60),
        "fps": 30,
        "loop": True,
        "root_motion": False,
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, -0.35, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, -0.33, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "location": (0, -0.35, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-8, 0, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (-10, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Head": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-10, 10, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (-10, -10, 0), "interpolation": "bezier"},
                {"frame": 60, "rotation": (-10, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpperLeg": [
                {"frame": 1, "rotation": (70, 0, 10), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperLeg": [
                {"frame": 1, "rotation": (70, 0, -10), "interpolation": "bezier"},
            ],
            "mixamorig:LeftLowerLeg": [
                {"frame": 1, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightLowerLeg": [
                {"frame": 1, "rotation": (-90, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperArm": [
                {"frame": 1, "rotation": (45, 0, 45), "interpolation": "bezier"},
            ],
            "mixamorig:RightLowerArm": [
                {"frame": 1, "rotation": (0, 60, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "cover_peek": {
        "description": "Peek over/around cover to aim",
        "category": "combat",
        "frame_range": (1, 30),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "frame_markers": {
            "can_fire": 15,      # Frame when aiming is stable
            "return_start": 22   # Frame when returning to cover
        },
        "keyframes": {
            "mixamorig:Hips": [
                {"frame": 1, "location": (0, -0.35, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "location": (0, -0.15, 0.05), "rotation": (10, 0, 0), "interpolation": "bezier"},
                {"frame": 22, "location": (0, -0.15, 0.05), "rotation": (10, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, -0.35, 0.1), "rotation": (20, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Spine": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (5, 15, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (5, 15, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-10, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:Head": [
                {"frame": 1, "rotation": (-10, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (-10, 0, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpperLeg": [
                {"frame": 1, "rotation": (70, 0, 10), "interpolation": "bezier"},
                {"frame": 15, "rotation": (45, 0, 5), "interpolation": "bezier"},
                {"frame": 30, "rotation": (70, 0, 10), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperLeg": [
                {"frame": 1, "rotation": (70, 0, -10), "interpolation": "bezier"},
                {"frame": 15, "rotation": (45, 0, -5), "interpolation": "bezier"},
                {"frame": 30, "rotation": (70, 0, -10), "interpolation": "bezier"},
            ],
            "mixamorig:RightUpperArm": [
                {"frame": 1, "rotation": (30, -20, 30), "interpolation": "bezier"},
                {"frame": 15, "rotation": (45, 0, 45), "interpolation": "bezier"},
                {"frame": 22, "rotation": (45, 0, 45), "interpolation": "bezier"},
                {"frame": 30, "rotation": (30, -20, 30), "interpolation": "bezier"},
            ],
            "mixamorig:RightLowerArm": [
                {"frame": 1, "rotation": (0, 30, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, 60, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (0, 60, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 30, 0), "interpolation": "bezier"},
            ],
            "mixamorig:LeftUpperArm": [
                {"frame": 1, "rotation": (30, 20, -30), "interpolation": "bezier"},
                {"frame": 15, "rotation": (60, -20, -45), "interpolation": "bezier"},
                {"frame": 22, "rotation": (60, -20, -45), "interpolation": "bezier"},
                {"frame": 30, "rotation": (30, 20, -30), "interpolation": "bezier"},
            ],
            "mixamorig:LeftLowerArm": [
                {"frame": 1, "rotation": (0, -30, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (0, -80, 0), "interpolation": "bezier"},
                {"frame": 22, "rotation": (0, -80, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, -30, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    # ----- STATUS EFFECTS -----
    "limp": {
        "description": "Injured walking limp on left leg",
        "category": "status",
        "frame_range": (1, 40),
        "fps": 30,
        "loop": True,
        "root_motion": True,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "interpolation": "linear"},
                {"frame": 10, "location": (0, 0.15, -0.05), "interpolation": "bezier"},
                {"frame": 20, "location": (0, 0.3, 0), "interpolation": "bezier"},
                {"frame": 30, "location": (0, 0.45, 0), "interpolation": "bezier"},
                {"frame": 40, "location": (0, 0.6, 0), "interpolation": "linear"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (-15, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (15, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (-15, 0, 0), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (-25, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (20, 0, 0), "interpolation": "bezier"},
            ],
            "leg_lower_l": [
                {"frame": 1, "rotation": (30, 0, 0), "interpolation": "bezier"},
                {"frame": 10, "rotation": (10, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (20, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (30, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (10, 5, 5), "interpolation": "bezier"},
                {"frame": 10, "rotation": (15, 0, 10), "interpolation": "bezier"},
                {"frame": 20, "rotation": (10, -5, 5), "interpolation": "bezier"},
                {"frame": 30, "rotation": (5, 0, 0), "interpolation": "bezier"},
                {"frame": 40, "rotation": (10, 5, 5), "interpolation": "bezier"},
            ],
            "shoulder_l": [
                {"frame": 1, "rotation": (0, 0, 10), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 5), "interpolation": "bezier"},
                {"frame": 40, "rotation": (0, 0, 10), "interpolation": "bezier"},
            ],
        },
    },
    
    "death": {
        "description": "Death fall animation",
        "category": "status",
        "frame_range": (1, 45),
        "fps": 30,
        "loop": False,
        "root_motion": True,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "location": (0, 0.2, 0.3), "rotation": (-20, 0, 15), "interpolation": "bezier"},
                {"frame": 30, "location": (0, 0.5, 0.1), "rotation": (-60, 0, 45), "interpolation": "bezier"},
                {"frame": 45, "location": (0, 0.8, 0), "rotation": (-90, 0, 90), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (20, 0, 10), "interpolation": "bezier"},
                {"frame": 30, "rotation": (30, 0, 20), "interpolation": "bezier"},
                {"frame": 45, "rotation": (15, 0, 10), "interpolation": "bezier"},
            ],
            "head": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 15, "rotation": (-30, 20, 0), "interpolation": "bezier"},
                {"frame": 30, "rotation": (20, 40, 20), "interpolation": "bezier"},
                {"frame": 45, "rotation": (30, 30, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, -90), "interpolation": "bezier"},
                {"frame": 45, "rotation": (30, 0, -120), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 45), "interpolation": "bezier"},
                {"frame": 45, "rotation": (-20, 0, 90), "interpolation": "bezier"},
            ],
            "leg_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (-20, 0, 20), "interpolation": "bezier"},
                {"frame": 45, "rotation": (10, 0, 30), "interpolation": "bezier"},
            ],
            "leg_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 25, "rotation": (-30, 0, -10), "interpolation": "bezier"},
                {"frame": 45, "rotation": (-15, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    "hit_react": {
        "description": "Reaction to being hit/damaged",
        "category": "status",
        "frame_range": (1, 20),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "root": [
                {"frame": 1, "location": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "location": (0, -0.1, 0), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 20, "location": (0, 0, 0), "interpolation": "bezier"},
            ],
            "spine": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (20, 0, 5), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 12, "rotation": (-5, 0, -2), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "head": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (15, 10, 5), "interpolation": "bezier", "easing": "ease_out"},
                {"frame": 12, "rotation": (-5, -5, 0), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_l": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (10, 0, 20), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
            "arm_upper_r": [
                {"frame": 1, "rotation": (0, 0, 0), "interpolation": "bezier"},
                {"frame": 5, "rotation": (10, 0, -20), "interpolation": "bezier"},
                {"frame": 20, "rotation": (0, 0, 0), "interpolation": "bezier"},
            ],
        },
    },
    
    # ----- UTILITY -----
    "t_pose": {
        "description": "Standard T-pose for rigging reference",
        "category": "utility",
        "frame_range": (1, 1),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "root": [{"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "constant"}],
            "spine": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "spine1": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "spine2": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "neck": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "head": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "shoulder_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "shoulder_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "arm_upper_l": [{"frame": 1, "rotation": (0, 0, -90), "interpolation": "constant"}],
            "arm_upper_r": [{"frame": 1, "rotation": (0, 0, 90), "interpolation": "constant"}],
            "arm_lower_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "arm_lower_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "hand_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "hand_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "leg_upper_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "leg_upper_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "leg_lower_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "leg_lower_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "foot_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "foot_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
        },
    },
    
    "a_pose": {
        "description": "A-pose for rigging reference (arms at 45 degrees)",
        "category": "utility",
        "frame_range": (1, 1),
        "fps": 30,
        "loop": False,
        "root_motion": False,
        "keyframes": {
            "root": [{"frame": 1, "location": (0, 0, 0), "rotation": (0, 0, 0), "interpolation": "constant"}],
            "spine": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "arm_upper_l": [{"frame": 1, "rotation": (0, 0, -45), "interpolation": "constant"}],
            "arm_upper_r": [{"frame": 1, "rotation": (0, 0, 45), "interpolation": "constant"}],
            "arm_lower_l": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "arm_lower_r": [{"frame": 1, "rotation": (0, 0, 0), "interpolation": "constant"}],
            "leg_upper_l": [{"frame": 1, "rotation": (0, 0, 5), "interpolation": "constant"}],
            "leg_upper_r": [{"frame": 1, "rotation": (0, 0, -5), "interpolation": "constant"}],
        },
    },
}

# ============================================================================
# ANIMATION CATEGORIES
# ============================================================================

ANIMATION_CATEGORIES = {
    "locomotion": {
        "description": "Movement animations (walk, run, idle, sprint, crouch, jump phases)",
        "presets": ["idle", "walk", "run", "sprint", "crouch_idle", "crouch_walk", "jump_start", "jump_loop", "jump_land"],
    },
    "action": {
        "description": "Action animations (jump, crouch, roll)",
        "presets": ["jump", "crouch", "roll"],
    },
    "combat": {
        "description": "Combat-related animations (aim, recoil, melee, reload, cover)",
        "presets": ["aim_weapon", "recoil", "melee_attack", "aim_idle", "reload", "cover_enter", "cover_idle", "cover_peek"],
    },
    "status": {
        "description": "Status effect animations (limp, death, hit)",
        "presets": ["limp", "death", "hit_react"],
    },
    "utility": {
        "description": "Utility poses (T-pose, A-pose)",
        "presets": ["t_pose", "a_pose"],
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_preset_info(preset_name: str) -> Optional[Dict[str, Any]]:
    """Get information about an animation preset."""
    return ANIMATION_PRESETS.get(preset_name)


def list_presets_by_category(category: Optional[str] = None) -> Dict[str, List[str]]:
    """List animation presets, optionally filtered by category."""
    if category and category in ANIMATION_CATEGORIES:
        return {category: ANIMATION_CATEGORIES[category]["presets"]}
    return {cat: info["presets"] for cat, info in ANIMATION_CATEGORIES.items()}


def get_bone_name(generic_name: str, convention: str = "mixamo") -> str:
    """Convert generic bone name to specific convention."""
    mapping = BONE_MAPPINGS.get(convention, BONE_MAPPINGS["generic"])
    return mapping.get(generic_name, generic_name)


def get_all_bone_mappings(convention: str = "mixamo") -> Dict[str, str]:
    """Get all bone name mappings for a convention."""
    return BONE_MAPPINGS.get(convention, BONE_MAPPINGS["generic"])


def suggest_animation(context: str) -> str:
    """
    Suggest an animation preset based on context description.
    
    Args:
        context: Description of what animation is needed
        
    Returns:
        Name of the suggested animation preset
    """
    context_lower = context.lower()
    
    # Locomotion
    if any(word in context_lower for word in ["idle", "standing", "still", "wait", "breathing"]):
        return "idle"
    if any(word in context_lower for word in ["walk", "walking", "stroll"]):
        return "walk"
    if any(word in context_lower for word in ["run", "running", "sprint", "jog"]):
        return "run"
    
    # Actions
    if any(word in context_lower for word in ["jump", "jumping", "leap", "hop"]):
        return "jump"
    if any(word in context_lower for word in ["crouch", "duck", "squat", "low"]):
        return "crouch"
    if any(word in context_lower for word in ["roll", "dodge", "evade", "tumble"]):
        return "roll"
    
    # Combat
    if any(word in context_lower for word in ["aim", "aiming", "target", "point", "sight"]):
        return "aim_weapon"
    if any(word in context_lower for word in ["recoil", "shoot", "fire", "kickback"]):
        return "recoil"
    if any(word in context_lower for word in ["melee", "swing", "slash", "punch", "attack"]):
        return "melee_attack"
    
    # Status
    if any(word in context_lower for word in ["limp", "injured", "hurt leg", "wounded"]):
        return "limp"
    if any(word in context_lower for word in ["death", "die", "dead", "fall", "collapse"]):
        return "death"
    if any(word in context_lower for word in ["hit", "damage", "hurt", "flinch", "react"]):
        return "hit_react"
    
    # Utility
    if any(word in context_lower for word in ["t-pose", "tpose", "t pose", "bind"]):
        return "t_pose"
    if any(word in context_lower for word in ["a-pose", "apose", "a pose"]):
        return "a_pose"
    
    # Default
    return "idle"


def degrees_to_radians(degrees: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Convert rotation from degrees to radians."""
    return tuple(math.radians(d) for d in degrees)


def get_keyframe_data_for_blender(
    preset_name: str,
    bone_convention: str = "mixamo"
) -> Optional[Dict[str, Any]]:
    """
    Get keyframe data formatted for Blender execution.
    
    Converts generic bone names to specific convention and
    rotation values to radians.
    
    Args:
        preset_name: Name of the animation preset
        bone_convention: Bone naming convention to use
        
    Returns:
        Dictionary with Blender-ready keyframe data
    """
    preset = ANIMATION_PRESETS.get(preset_name)
    if not preset:
        return None
    
    bone_mapping = BONE_MAPPINGS.get(bone_convention, BONE_MAPPINGS["generic"])
    blender_data = {
        "name": preset_name,
        "frame_range": preset["frame_range"],
        "fps": preset["fps"],
        "loop": preset["loop"],
        "root_motion": preset["root_motion"],
        "keyframes": {},
    }
    
    for generic_bone, keyframes in preset.get("keyframes", {}).items():
        actual_bone = bone_mapping.get(generic_bone, generic_bone)
        blender_keyframes = []
        
        for kf in keyframes:
            blender_kf = {
                "frame": kf["frame"],
                "interpolation": INTERPOLATION_TYPES.get(
                    kf.get("interpolation", "bezier"), "BEZIER"
                ),
            }
            
            if "easing" in kf:
                blender_kf["easing"] = EASING_TYPES.get(kf["easing"], "AUTO")
            
            if "location" in kf:
                blender_kf["location"] = kf["location"]
            
            if "rotation" in kf:
                blender_kf["rotation_euler"] = degrees_to_radians(kf["rotation"])
            
            if "scale" in kf:
                blender_kf["scale"] = kf["scale"]
            
            blender_keyframes.append(blender_kf)
        
        blender_data["keyframes"][actual_bone] = blender_keyframes
    
    return blender_data


def validate_armature_bones(
    armature_bones: List[str],
    preset_name: str,
    bone_convention: str = "mixamo"
) -> Dict[str, Any]:
    """
    Validate that armature has required bones for an animation preset.
    
    Args:
        armature_bones: List of bone names in the armature
        preset_name: Animation preset to validate against
        bone_convention: Bone naming convention used
        
    Returns:
        Dictionary with validation results
    """
    preset = ANIMATION_PRESETS.get(preset_name)
    if not preset:
        return {"valid": False, "error": f"Preset '{preset_name}' not found"}
    
    bone_mapping = BONE_MAPPINGS.get(bone_convention, BONE_MAPPINGS["generic"])
    required_bones = set()
    
    for generic_bone in preset.get("keyframes", {}).keys():
        actual_bone = bone_mapping.get(generic_bone, generic_bone)
        required_bones.add(actual_bone)
    
    armature_bones_set = set(armature_bones)
    missing_bones = required_bones - armature_bones_set
    found_bones = required_bones & armature_bones_set
    
    return {
        "valid": len(missing_bones) == 0,
        "required_bones": list(required_bones),
        "found_bones": list(found_bones),
        "missing_bones": list(missing_bones),
        "coverage": len(found_bones) / len(required_bones) if required_bones else 1.0,
    }


def get_animation_duration(preset_name: str, fps: int = 30) -> Optional[float]:
    """Get the duration of an animation preset in seconds."""
    preset = ANIMATION_PRESETS.get(preset_name)
    if not preset:
        return None
    
    frame_range = preset["frame_range"]
    total_frames = frame_range[1] - frame_range[0] + 1
    preset_fps = preset.get("fps", fps)
    
    return total_frames / preset_fps


# ============================================================================
# EXPORT LIST
# ============================================================================

__all__ = [
    # Constants
    "ANIMATION_PRESETS",
    "ANIMATION_CATEGORIES",
    "BONE_MAPPINGS",
    "INTERPOLATION_TYPES",
    "EASING_TYPES",
    # Functions
    "get_preset_info",
    "list_presets_by_category",
    "get_bone_name",
    "get_all_bone_mappings",
    "suggest_animation",
    "degrees_to_radians",
    "get_keyframe_data_for_blender",
    "validate_armature_bones",
    "get_animation_duration",
]
