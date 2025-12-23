"""
Minimal lighting module for Blender addon import
"""

from src.blender_mcp.lighting import (
    HDRI_PRESETS,
    LIGHTING_RIGS,
    ATMOSPHERE_PRESETS,
    CAMERA_PRESETS,
    RENDER_PRESETS,
    SCENE_TYPE_LIGHTING,
    suggest_scene_lighting,
    calculate_camera_position
)

__all__ = [
    'HDRI_PRESETS',
    'LIGHTING_RIGS',
    'ATMOSPHERE_PRESETS',
    'CAMERA_PRESETS',
    'RENDER_PRESETS',
    'SCENE_TYPE_LIGHTING',
    'suggest_scene_lighting',
    'calculate_camera_position'
]
