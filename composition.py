"""
Composition System for Blender MCP (Addon-compatible version)
Simplified version for direct import in Blender addon.
"""

import math
from typing import Dict, List, Tuple, Optional, Any

# Import full composition module
try:
    from src.blender_mcp.composition import *
except ImportError:
    # Fallback: define everything inline if module not available
    pass

# Ensure all exports are available for addon
__all__ = [
    'COMPOSITION_RULES',
    'SHOT_TYPES', 
    'FRAMING_PRESETS',
    'COMPOSITION_PRESETS',
    'calculate_composition_score',
    'suggest_shot_type',
    'suggest_composition_rule',
    'calculate_camera_position',
    'get_framing_guide_data'
]
