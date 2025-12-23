"""
Color Grading System for Blender MCP
Provides cinematic color grading, LUTs, tone mapping, and color effects.
"""

from typing import Dict, List, Tuple, Optional, Any

# LUT (Look-Up Table) Presets - Cinematic color grading styles
LUT_PRESETS = {
    "cinematic_neutral": {
        "name": "Cinematic Neutral",
        "description": "Clean cinematic look with subtle contrast boost",
        "lift": (0.98, 0.98, 1.0),      # Shadows (slight cool)
        "gamma": (1.0, 1.0, 1.0),       # Midtones (neutral)
        "gain": (1.02, 1.0, 0.98),      # Highlights (slight warm)
        "saturation": 1.1,
        "contrast": 1.15,
        "brightness": 0.0,
        "color_temp": 0,  # Neutral
        "ideal_for": ["general", "professional", "commercial"],
    },
    
    "cinematic_warm": {
        "name": "Cinematic Warm",
        "description": "Warm, inviting look for sunset/golden hour scenes",
        "lift": (1.0, 0.95, 0.90),      # Warm shadows
        "gamma": (1.05, 1.0, 0.95),     # Warm midtones
        "gain": (1.10, 1.05, 0.95),     # Very warm highlights
        "saturation": 1.15,
        "contrast": 1.2,
        "brightness": 0.05,
        "color_temp": 500,  # Warm
        "ideal_for": ["sunset", "golden_hour", "warm", "cozy"],
    },
    
    "cinematic_cool": {
        "name": "Cinematic Cool",
        "description": "Cool, modern look for tech/sci-fi scenes",
        "lift": (0.90, 0.95, 1.05),     # Cool shadows
        "gamma": (0.95, 1.0, 1.05),     # Cool midtones
        "gain": (0.95, 1.0, 1.10),      # Cool highlights
        "saturation": 1.05,
        "contrast": 1.25,
        "brightness": -0.05,
        "color_temp": -300,  # Cool
        "ideal_for": ["tech", "modern", "sci-fi", "clinical"],
    },
    
    "teal_orange": {
        "name": "Teal & Orange",
        "description": "Hollywood blockbuster look (teal shadows, orange highlights)",
        "lift": (0.85, 0.95, 1.05),     # Teal shadows
        "gamma": (0.98, 1.0, 1.02),     # Neutral midtones
        "gain": (1.15, 1.05, 0.90),     # Orange highlights
        "saturation": 1.25,
        "contrast": 1.3,
        "brightness": 0.0,
        "color_temp": 200,
        "ideal_for": ["action", "blockbuster", "dramatic", "commercial"],
    },
    
    "film_noir": {
        "name": "Film Noir",
        "description": "Classic black and white high-contrast noir look",
        "lift": (0.85, 0.85, 0.85),     # Crushed blacks
        "gamma": (1.0, 1.0, 1.0),       # Neutral midtones
        "gain": (1.15, 1.15, 1.15),     # Bright highlights
        "saturation": 0.0,  # Black and white
        "contrast": 1.5,
        "brightness": 0.0,
        "color_temp": 0,
        "ideal_for": ["noir", "dramatic", "vintage", "mystery"],
    },
    
    "vintage_film": {
        "name": "Vintage Film",
        "description": "Faded film look with reduced contrast",
        "lift": (1.05, 1.0, 0.95),      # Lifted blacks (milky)
        "gamma": (1.0, 0.98, 0.95),     # Slight yellow cast
        "gain": (0.95, 0.95, 0.90),     # Reduced highlights
        "saturation": 0.8,
        "contrast": 0.85,
        "brightness": 0.1,
        "color_temp": 150,
        "ideal_for": ["vintage", "retro", "nostalgic", "faded"],
    },
    
    "vibrant_pop": {
        "name": "Vibrant Pop",
        "description": "High saturation, punchy colors for advertising",
        "lift": (0.95, 0.95, 0.95),
        "gamma": (1.0, 1.0, 1.0),
        "gain": (1.05, 1.05, 1.05),
        "saturation": 1.4,
        "contrast": 1.25,
        "brightness": 0.1,
        "color_temp": 0,
        "ideal_for": ["advertising", "product", "vibrant", "energetic"],
    },
    
    "muted_pastel": {
        "name": "Muted Pastel",
        "description": "Soft, desaturated pastel tones",
        "lift": (1.08, 1.05, 1.05),     # Very lifted shadows
        "gamma": (1.0, 1.0, 1.0),
        "gain": (0.92, 0.95, 0.95),     # Reduced highlights
        "saturation": 0.7,
        "contrast": 0.75,
        "brightness": 0.15,
        "color_temp": 50,
        "ideal_for": ["soft", "dreamy", "pastel", "gentle"],
    },
    
    "high_contrast_bw": {
        "name": "High Contrast B&W",
        "description": "Dramatic black and white with deep blacks",
        "lift": (0.75, 0.75, 0.75),     # Very crushed blacks
        "gamma": (0.95, 0.95, 0.95),    # Darkened midtones
        "gain": (1.20, 1.20, 1.20),     # Bright whites
        "saturation": 0.0,
        "contrast": 1.8,
        "brightness": -0.1,
        "color_temp": 0,
        "ideal_for": ["dramatic", "portrait", "architecture", "fine_art"],
    },
    
    "moody_dark": {
        "name": "Moody Dark",
        "description": "Dark, moody look for horror/thriller",
        "lift": (0.80, 0.82, 0.85),     # Dark shadows
        "gamma": (0.90, 0.92, 0.95),    # Dark midtones
        "gain": (1.0, 1.0, 1.05),       # Controlled highlights
        "saturation": 0.9,
        "contrast": 1.4,
        "brightness": -0.2,
        "color_temp": -200,
        "ideal_for": ["horror", "thriller", "dark", "moody"],
    },
}

# Tone Mapping Presets
TONE_MAPPING = {
    "filmic": {
        "name": "Filmic",
        "description": "Blender's Filmic color management (cinematic HDR)",
        "view_transform": "Filmic",
        "look": "Medium Contrast",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["general", "cinematic", "HDR", "realistic"],
    },
    
    "filmic_high_contrast": {
        "name": "Filmic High Contrast",
        "description": "Filmic with punchy contrast",
        "view_transform": "Filmic",
        "look": "High Contrast",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["dramatic", "commercial", "bold"],
    },
    
    "filmic_low_contrast": {
        "name": "Filmic Low Contrast",
        "description": "Filmic with softer contrast",
        "view_transform": "Filmic",
        "look": "Low Contrast",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["soft", "pastel", "gentle"],
    },
    
    "standard": {
        "name": "Standard (sRGB)",
        "description": "Standard sRGB display (no tone mapping)",
        "view_transform": "Standard",
        "look": "None",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["web", "standard", "no_grading"],
    },
    
    "agx": {
        "name": "AgX",
        "description": "AgX tone mapper (Blender 4.0+, highly recommended)",
        "view_transform": "AgX",
        "look": "None",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["modern", "accurate", "blender4+"],
    },
    
    "false_color": {
        "name": "False Color",
        "description": "Exposure visualization tool",
        "view_transform": "False Color",
        "look": "None",
        "exposure": 0.0,
        "gamma": 1.0,
        "ideal_for": ["technical", "debugging", "exposure_check"],
    },
}

# Color Effects Presets
COLOR_EFFECTS = {
    "vignette_subtle": {
        "name": "Subtle Vignette",
        "description": "Gentle darkening at edges",
        "vignette_strength": 0.3,
        "vignette_falloff": 2.0,
        "ideal_for": ["general", "subtle", "professional"],
    },
    
    "vignette_strong": {
        "name": "Strong Vignette",
        "description": "Dramatic edge darkening for focus",
        "vignette_strength": 0.6,
        "vignette_falloff": 1.5,
        "ideal_for": ["dramatic", "portrait", "focus"],
    },
    
    "film_grain_light": {
        "name": "Light Film Grain",
        "description": "Subtle grain for film texture",
        "grain_strength": 0.05,
        "grain_size": 1.0,
        "ideal_for": ["cinematic", "subtle", "texture"],
    },
    
    "film_grain_heavy": {
        "name": "Heavy Film Grain",
        "description": "Strong grain for vintage film look",
        "grain_strength": 0.15,
        "grain_size": 1.5,
        "ideal_for": ["vintage", "gritty", "retro"],
    },
    
    "chromatic_aberration": {
        "name": "Chromatic Aberration",
        "description": "Lens color fringing effect",
        "ca_strength": 0.003,
        "ideal_for": ["lens_simulation", "realistic", "subtle"],
    },
    
    "bloom_subtle": {
        "name": "Subtle Bloom",
        "description": "Gentle glow on bright areas",
        "bloom_threshold": 1.0,
        "bloom_intensity": 0.05,
        "bloom_radius": 6.5,
        "ideal_for": ["glow", "dreamy", "magical"],
    },
    
    "bloom_strong": {
        "name": "Strong Bloom",
        "description": "Dramatic glow effect",
        "bloom_threshold": 0.8,
        "bloom_intensity": 0.15,
        "bloom_radius": 8.0,
        "ideal_for": ["sci-fi", "magical", "dramatic"],
    },
    
    "lens_distortion": {
        "name": "Lens Distortion",
        "description": "Barrel/pincushion distortion",
        "distortion": 0.02,
        "dispersion": 0.01,
        "ideal_for": ["realistic", "lens_simulation"],
    },
}

# Complete color grade presets (LUT + effects combined)
COLOR_GRADE_PRESETS = {
    "cinematic_standard": {
        "name": "Cinematic Standard",
        "description": "Professional cinematic look with subtle enhancements",
        "lut": "cinematic_neutral",
        "tone_mapping": "filmic",
        "effects": ["vignette_subtle", "film_grain_light"],
        "ideal_for": ["general", "professional", "cinematic"],
    },
    
    "blockbuster": {
        "name": "Blockbuster",
        "description": "Hollywood action movie look",
        "lut": "teal_orange",
        "tone_mapping": "filmic_high_contrast",
        "effects": ["vignette_subtle", "bloom_subtle"],
        "ideal_for": ["action", "dramatic", "commercial"],
    },
    
    "product_showcase": {
        "name": "Product Showcase",
        "description": "Clean, vibrant look for product photography",
        "lut": "vibrant_pop",
        "tone_mapping": "filmic",
        "effects": ["vignette_subtle"],
        "ideal_for": ["product", "advertising", "commercial"],
    },
    
    "moody_portrait": {
        "name": "Moody Portrait",
        "description": "Dark, atmospheric portrait look",
        "lut": "moody_dark",
        "tone_mapping": "filmic_high_contrast",
        "effects": ["vignette_strong", "film_grain_light"],
        "ideal_for": ["portrait", "moody", "dramatic"],
    },
    
    "vintage_nostalgia": {
        "name": "Vintage Nostalgia",
        "description": "Retro faded film aesthetic",
        "lut": "vintage_film",
        "tone_mapping": "filmic_low_contrast",
        "effects": ["vignette_subtle", "film_grain_heavy"],
        "ideal_for": ["vintage", "retro", "nostalgic"],
    },
    
    "noir_classic": {
        "name": "Noir Classic",
        "description": "Classic film noir black and white",
        "lut": "film_noir",
        "tone_mapping": "filmic_high_contrast",
        "effects": ["vignette_strong", "film_grain_light"],
        "ideal_for": ["noir", "bw", "dramatic"],
    },
    
    "dreamy_pastel": {
        "name": "Dreamy Pastel",
        "description": "Soft, ethereal pastel look",
        "lut": "muted_pastel",
        "tone_mapping": "filmic_low_contrast",
        "effects": ["bloom_subtle"],
        "ideal_for": ["soft", "dreamy", "pastel"],
    },
    
    "sci_fi_cool": {
        "name": "Sci-Fi Cool",
        "description": "Cool futuristic tech aesthetic",
        "lut": "cinematic_cool",
        "tone_mapping": "filmic",
        "effects": ["bloom_strong", "chromatic_aberration"],
        "ideal_for": ["sci-fi", "tech", "futuristic"],
    },
}

def suggest_color_grade(scene_description: str, lighting_type: str = None) -> str:
    """
    Suggest appropriate color grade based on scene description and lighting.
    
    Args:
        scene_description: Description of scene/mood (e.g., "dramatic portrait", "product shot")
        lighting_type: Optional lighting type (outdoor, indoor, studio, night, etc.)
        
    Returns:
        Recommended color grade preset key
    """
    desc_lower = scene_description.lower()
    
    # Keyword matching
    if any(word in desc_lower for word in ['product', 'commercial', 'advertising']):
        return "product_showcase"
    elif any(word in desc_lower for word in ['action', 'blockbuster', 'dramatic action']):
        return "blockbuster"
    elif any(word in desc_lower for word in ['noir', 'mystery', 'detective']):
        return "noir_classic"
    elif any(word in desc_lower for word in ['vintage', 'retro', 'old', 'nostalgic']):
        return "vintage_nostalgia"
    elif any(word in desc_lower for word in ['dreamy', 'soft', 'pastel', 'ethereal']):
        return "dreamy_pastel"
    elif any(word in desc_lower for word in ['sci-fi', 'tech', 'futuristic', 'cyberpunk']):
        return "sci_fi_cool"
    elif any(word in desc_lower for word in ['moody', 'dark', 'atmospheric']):
        return "moody_portrait"
    elif any(word in desc_lower for word in ['portrait', 'face', 'character']):
        return "moody_portrait" if "dark" in desc_lower or "moody" in desc_lower else "cinematic_standard"
    else:
        return "cinematic_standard"

def get_color_temperature_offset(kelvin: int) -> Tuple[float, float, float]:
    """
    Convert color temperature in Kelvin to RGB multipliers.
    
    Args:
        kelvin: Color temperature offset (-500 to +500, 0 = neutral)
        
    Returns:
        (r, g, b) multipliers
    """
    # Simplified color temperature conversion
    if kelvin == 0:
        return (1.0, 1.0, 1.0)
    
    # Warm (positive) - add red/orange, reduce blue
    if kelvin > 0:
        factor = min(kelvin / 500.0, 1.0)
        r = 1.0 + (factor * 0.15)
        g = 1.0 + (factor * 0.05)
        b = 1.0 - (factor * 0.10)
        return (r, g, b)
    
    # Cool (negative) - add blue, reduce red
    else:
        factor = min(abs(kelvin) / 500.0, 1.0)
        r = 1.0 - (factor * 0.10)
        g = 1.0
        b = 1.0 + (factor * 0.15)
        return (r, g, b)

def generate_compositor_nodes(
    lut_preset: str = None,
    tone_mapping: str = None,
    effects: List[str] = None
) -> Dict[str, Any]:
    """
    Generate compositor node configuration for color grading.
    
    Args:
        lut_preset: LUT preset key
        tone_mapping: Tone mapping preset key
        effects: List of effect preset keys
        
    Returns:
        Dict with node configuration data
    """
    nodes_config = {
        "use_nodes": True,
        "nodes": [],
        "links": []
    }
    
    # Base nodes: Render Layers -> Composite
    nodes_config["nodes"].append({
        "type": "CompositorNodeRLayers",
        "name": "Render Layers",
        "location": (0, 0)
    })
    
    current_x = 200
    current_node = "Render Layers"
    
    # Add LUT (Color Balance) if specified
    if lut_preset and lut_preset in LUT_PRESETS:
        lut = LUT_PRESETS[lut_preset]
        nodes_config["nodes"].append({
            "type": "CompositorNodeColorBalance",
            "name": f"LUT_{lut_preset}",
            "location": (current_x, 0),
            "lift": lut["lift"],
            "gamma": lut["gamma"],
            "gain": lut["gain"],
        })
        nodes_config["links"].append({
            "from_node": current_node,
            "from_socket": "Image",
            "to_node": f"LUT_{lut_preset}",
            "to_socket": "Image"
        })
        current_node = f"LUT_{lut_preset}"
        current_x += 200
        
        # Add Hue/Saturation for saturation control
        nodes_config["nodes"].append({
            "type": "CompositorNodeHueSat",
            "name": f"Saturation_{lut_preset}",
            "location": (current_x, 0),
            "saturation": lut["saturation"],
        })
        nodes_config["links"].append({
            "from_node": current_node,
            "from_socket": "Image",
            "to_node": f"Saturation_{lut_preset}",
            "to_socket": "Image"
        })
        current_node = f"Saturation_{lut_preset}"
        current_x += 200
        
        # Add Bright/Contrast
        nodes_config["nodes"].append({
            "type": "CompositorNodeBrightContrast",
            "name": f"Contrast_{lut_preset}",
            "location": (current_x, 0),
            "bright": lut["brightness"],
            "contrast": lut["contrast"] - 1.0,  # Blender uses offset from 0
        })
        nodes_config["links"].append({
            "from_node": current_node,
            "from_socket": "Image",
            "to_node": f"Contrast_{lut_preset}",
            "to_socket": "Image"
        })
        current_node = f"Contrast_{lut_preset}"
        current_x += 200
    
    # Add effects if specified
    if effects:
        for effect_key in effects:
            if effect_key in COLOR_EFFECTS:
                effect = COLOR_EFFECTS[effect_key]
                
                # Vignette
                if "vignette" in effect_key:
                    nodes_config["nodes"].append({
                        "type": "CompositorNodeLensdist",
                        "name": f"Vignette_{effect_key}",
                        "location": (current_x, -200),
                        "use_jitter": True,
                        "use_fit": True,
                    })
                    # Note: Vignette implemented via ellipse mask in actual code
                
                # Film Grain
                elif "grain" in effect_key:
                    nodes_config["nodes"].append({
                        "type": "CompositorNodeMixRGB",
                        "name": f"Grain_{effect_key}",
                        "location": (current_x, 0),
                        "blend_type": "OVERLAY",
                        "fac": effect["grain_strength"],
                    })
                
                # Bloom/Glare
                elif "bloom" in effect_key:
                    nodes_config["nodes"].append({
                        "type": "CompositorNodeGlare",
                        "name": f"Bloom_{effect_key}",
                        "location": (current_x, 0),
                        "glare_type": "FOG_GLOW",
                        "quality": "HIGH",
                        "threshold": effect.get("bloom_threshold", 1.0),
                        "size": int(effect.get("bloom_radius", 6.5)),
                        "mix": effect.get("bloom_intensity", 0.1) * -1,  # Negative for additive
                    })
                    nodes_config["links"].append({
                        "from_node": current_node,
                        "from_socket": "Image",
                        "to_node": f"Bloom_{effect_key}",
                        "to_socket": "Image"
                    })
                    current_node = f"Bloom_{effect_key}"
                    current_x += 200
    
    # Final composite node
    nodes_config["nodes"].append({
        "type": "CompositorNodeComposite",
        "name": "Composite",
        "location": (current_x, 0)
    })
    nodes_config["links"].append({
        "from_node": current_node,
        "from_socket": "Image",
        "to_node": "Composite",
        "to_socket": "Image"
    })
    
    return nodes_config
