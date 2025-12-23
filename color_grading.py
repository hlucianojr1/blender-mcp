"""
Addon-compatible wrapper for color grading system.
Imports from src.blender_mcp.color_grading for use in Blender addon.
"""

from src.blender_mcp.color_grading import (
    LUT_PRESETS,
    TONE_MAPPING,
    COLOR_EFFECTS,
    COLOR_GRADE_PRESETS,
    suggest_color_grade,
    get_color_temperature_offset,
    generate_compositor_nodes
)
