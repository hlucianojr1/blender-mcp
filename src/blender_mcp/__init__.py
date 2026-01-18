"""Blender integration through the Model Context Protocol."""

__version__ = "0.1.0"

# Expose key classes and functions for easier imports
from .server import BlenderConnection, get_blender_connection

# Animation system exports
from .animation import (
    ANIMATION_PRESETS,
    ANIMATION_CATEGORIES,
    BONE_MAPPINGS,
    INTERPOLATION_TYPES,
    EASING_TYPES,
    get_preset_info,
    list_presets_by_category,
    get_bone_name,
    get_all_bone_mappings,
    suggest_animation,
    get_keyframe_data_for_blender,
    validate_armature_bones,
    get_animation_duration,
)
