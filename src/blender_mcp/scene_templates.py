"""
Scene Templates System for Blender MCP
Provides complete pre-configured professional scenes combining all enhancement systems.
"""

from typing import Dict, List, Any, Optional

# Scene template definitions combining all 5 enhancement systems:
# 1. Geometry (post-processing)
# 2. Materials
# 3. Lighting & Atmosphere
# 4. Composition
# 5. Color Grading

# ==================== PRODUCT PHOTOGRAPHY TEMPLATES ====================

PRODUCT_TEMPLATES = {
    "product_studio_pro": {
        "name": "Product Studio Professional",
        "description": "Clean studio product photography with white background",
        "category": "product",
        "ideal_for": ["e-commerce", "catalog", "professional", "clean"],
        
        # Geometry settings
        "geometry": {
            "enhancement_preset": "high_detail",
            "subdivision_levels": 2,
            "auto_smooth": True,
        },
        
        # Material settings
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
            "default_material": "glossy_plastic",
        },
        
        # Lighting settings
        "lighting": {
            "hdri": "studio",
            "lighting_rig": "studio",
            "atmosphere": None,
            "hdri_strength": 1.0,
        },
        
        # Composition settings
        "composition": {
            "preset": "product_hero",
            "shot_type": "medium_shot",
            "composition_rule": "rule_of_thirds",
            "camera_angle": "three_quarter",
        },
        
        # Color grading settings
        "color_grading": {
            "preset": "product_showcase",
            "tone_mapping": "agx",
            "exposure": 0.0,
            "gamma": 1.0,
        },
        
        # Render settings
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
    
    "product_lifestyle": {
        "name": "Product Lifestyle",
        "description": "Natural lifestyle product shot with environmental context",
        "category": "product",
        "ideal_for": ["lifestyle", "social_media", "advertising", "contextual"],
        
        "geometry": {
            "enhancement_preset": "smooth",
            "subdivision_levels": 2,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "outdoor_day",
            "lighting_rig": "outdoor",
            "atmosphere": "haze",
            "hdri_strength": 1.2,
        },
        
        "composition": {
            "preset": "product_lifestyle",
            "shot_type": "medium_wide",
            "composition_rule": "rule_of_thirds",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "cinematic_warm",
            "tone_mapping": "filmic",
            "exposure": 0.2,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
    
    "product_hero_dramatic": {
        "name": "Product Hero Dramatic",
        "description": "Dramatic hero shot with bold lighting and composition",
        "category": "product",
        "ideal_for": ["hero", "dramatic", "premium", "advertising"],
        
        "geometry": {
            "enhancement_preset": "high_detail",
            "subdivision_levels": 3,
            "auto_smooth": True,
            "edge_bevel": 0.01,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
        },
        
        "lighting": {
            "hdri": "sunset",
            "lighting_rig": "dramatic",
            "atmosphere": "god_rays",
            "hdri_strength": 1.5,
        },
        
        "composition": {
            "preset": "product_hero",
            "shot_type": "closeup",
            "composition_rule": "golden_ratio",
            "camera_angle": "low",
        },
        
        "color_grading": {
            "preset": "blockbuster",
            "tone_mapping": "filmic_high_contrast",
            "exposure": 0.3,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "final",
            "samples": 512,
        },
    },
}

# ==================== PORTRAIT TEMPLATES ====================

PORTRAIT_TEMPLATES = {
    "portrait_professional": {
        "name": "Portrait Professional",
        "description": "Classic professional portrait with balanced lighting",
        "category": "portrait",
        "ideal_for": ["professional", "headshot", "business", "corporate"],
        
        "geometry": {
            "enhancement_preset": "organic",
            "subdivision_levels": 2,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "studio",
            "lighting_rig": "three_point",
            "atmosphere": None,
            "hdri_strength": 0.8,
        },
        
        "composition": {
            "preset": "portrait_pro",
            "shot_type": "closeup",
            "composition_rule": "rule_of_thirds",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "cinematic_standard",
            "tone_mapping": "filmic",
            "exposure": 0.0,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
    
    "portrait_cinematic": {
        "name": "Portrait Cinematic",
        "description": "Cinematic portrait with dramatic lighting and mood",
        "category": "portrait",
        "ideal_for": ["cinematic", "artistic", "dramatic", "moody"],
        
        "geometry": {
            "enhancement_preset": "organic",
            "subdivision_levels": 3,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
        },
        
        "lighting": {
            "hdri": "sunset",
            "lighting_rig": "dramatic",
            "atmosphere": "fog",
            "hdri_strength": 1.0,
        },
        
        "composition": {
            "preset": "portrait_cinematic",
            "shot_type": "closeup",
            "composition_rule": "golden_ratio",
            "camera_angle": "three_quarter",
        },
        
        "color_grading": {
            "preset": "moody_portrait",
            "tone_mapping": "filmic_high_contrast",
            "exposure": -0.2,
            "gamma": 1.1,
        },
        
        "render": {
            "preset": "final",
            "samples": 512,
        },
    },
    
    "portrait_noir": {
        "name": "Portrait Film Noir",
        "description": "Classic black and white film noir portrait",
        "category": "portrait",
        "ideal_for": ["noir", "black_white", "vintage", "dramatic"],
        
        "geometry": {
            "enhancement_preset": "smooth",
            "subdivision_levels": 2,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "studio",
            "lighting_rig": "dramatic",
            "atmosphere": None,
            "hdri_strength": 0.5,
        },
        
        "composition": {
            "preset": "portrait_pro",
            "shot_type": "medium_closeup",
            "composition_rule": "center_composition",
            "camera_angle": "side",
        },
        
        "color_grading": {
            "preset": "noir_classic",
            "tone_mapping": "filmic_high_contrast",
            "exposure": -0.3,
            "gamma": 0.9,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
}

# ==================== LANDSCAPE/ENVIRONMENT TEMPLATES ====================

LANDSCAPE_TEMPLATES = {
    "landscape_epic": {
        "name": "Landscape Epic",
        "description": "Epic wide landscape with dramatic sky and atmosphere",
        "category": "landscape",
        "ideal_for": ["epic", "environment", "wide", "cinematic"],
        
        "geometry": {
            "enhancement_preset": "architectural",
            "subdivision_levels": 1,
            "auto_smooth": False,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "sunset",
            "lighting_rig": "outdoor",
            "atmosphere": "god_rays",
            "hdri_strength": 1.5,
        },
        
        "composition": {
            "preset": "landscape_epic",
            "shot_type": "extreme_wide",
            "composition_rule": "rule_of_thirds",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "cinematic_warm",
            "tone_mapping": "filmic_high_contrast",
            "exposure": 0.3,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "final",
            "samples": 512,
        },
    },
    
    "landscape_classic": {
        "name": "Landscape Classic",
        "description": "Classic balanced landscape composition",
        "category": "landscape",
        "ideal_for": ["classic", "natural", "balanced", "photography"],
        
        "geometry": {
            "enhancement_preset": "smooth",
            "subdivision_levels": 1,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "outdoor_day",
            "lighting_rig": "outdoor",
            "atmosphere": "haze",
            "hdri_strength": 1.2,
        },
        
        "composition": {
            "preset": "landscape_classic",
            "shot_type": "wide_shot",
            "composition_rule": "golden_ratio",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "cinematic_standard",
            "tone_mapping": "agx",
            "exposure": 0.0,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
    
    "landscape_moody": {
        "name": "Landscape Moody",
        "description": "Dark moody landscape with fog and low light",
        "category": "landscape",
        "ideal_for": ["moody", "dark", "atmospheric", "mysterious"],
        
        "geometry": {
            "enhancement_preset": "smooth",
            "subdivision_levels": 1,
            "auto_smooth": True,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
        },
        
        "lighting": {
            "hdri": "night",
            "lighting_rig": "night",
            "atmosphere": "heavy_fog",
            "hdri_strength": 0.8,
        },
        
        "composition": {
            "preset": "landscape_classic",
            "shot_type": "wide_shot",
            "composition_rule": "rule_of_thirds",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "moody_portrait",
            "tone_mapping": "filmic_high_contrast",
            "exposure": -0.5,
            "gamma": 0.9,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
}

# ==================== ARCHITECTURE TEMPLATES ====================

ARCHITECTURE_TEMPLATES = {
    "architecture_hero": {
        "name": "Architecture Hero",
        "description": "Dramatic architectural hero shot with strong composition",
        "category": "architecture",
        "ideal_for": ["hero", "dramatic", "showcase", "portfolio"],
        
        "geometry": {
            "enhancement_preset": "architectural",
            "subdivision_levels": 1,
            "auto_smooth": False,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
        },
        
        "lighting": {
            "hdri": "sunset",
            "lighting_rig": "dramatic",
            "atmosphere": "haze",
            "hdri_strength": 1.3,
        },
        
        "composition": {
            "preset": "architecture_hero",
            "shot_type": "wide_shot",
            "composition_rule": "golden_ratio",
            "camera_angle": "low",
        },
        
        "color_grading": {
            "preset": "blockbuster",
            "tone_mapping": "filmic_high_contrast",
            "exposure": 0.2,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "final",
            "samples": 512,
        },
    },
    
    "architecture_technical": {
        "name": "Architecture Technical",
        "description": "Clean technical architectural visualization",
        "category": "architecture",
        "ideal_for": ["technical", "clean", "professional", "presentation"],
        
        "geometry": {
            "enhancement_preset": "architectural",
            "subdivision_levels": 1,
            "auto_smooth": False,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": False,
        },
        
        "lighting": {
            "hdri": "outdoor_day",
            "lighting_rig": "outdoor",
            "atmosphere": None,
            "hdri_strength": 1.0,
        },
        
        "composition": {
            "preset": "architecture_hero",
            "shot_type": "medium_wide",
            "composition_rule": "center_composition",
            "camera_angle": "front",
        },
        
        "color_grading": {
            "preset": "product_showcase",
            "tone_mapping": "agx",
            "exposure": 0.0,
            "gamma": 1.0,
        },
        
        "render": {
            "preset": "production",
            "samples": 256,
        },
    },
    
    "architecture_dramatic": {
        "name": "Architecture Dramatic Night",
        "description": "Dramatic night architecture with dramatic lighting",
        "category": "architecture",
        "ideal_for": ["night", "dramatic", "atmospheric", "artistic"],
        
        "geometry": {
            "enhancement_preset": "architectural",
            "subdivision_levels": 1,
            "auto_smooth": False,
        },
        
        "materials": {
            "auto_enhance": True,
            "aggressive": True,
        },
        
        "lighting": {
            "hdri": "night",
            "lighting_rig": "night",
            "atmosphere": "fog",
            "hdri_strength": 0.6,
        },
        
        "composition": {
            "preset": "architecture_dramatic",
            "shot_type": "wide_shot",
            "composition_rule": "diagonal",
            "camera_angle": "low",
        },
        
        "color_grading": {
            "preset": "sci_fi_cool",
            "tone_mapping": "filmic_high_contrast",
            "exposure": -0.3,
            "gamma": 1.1,
        },
        
        "render": {
            "preset": "final",
            "samples": 512,
        },
    },
}

# Combine all templates
SCENE_TEMPLATES = {}
SCENE_TEMPLATES.update(PRODUCT_TEMPLATES)
SCENE_TEMPLATES.update(PORTRAIT_TEMPLATES)
SCENE_TEMPLATES.update(LANDSCAPE_TEMPLATES)
SCENE_TEMPLATES.update(ARCHITECTURE_TEMPLATES)

def get_template_categories() -> List[str]:
    """Get list of all template categories"""
    categories = set()
    for template in SCENE_TEMPLATES.values():
        categories.add(template["category"])
    return sorted(list(categories))

def get_templates_by_category(category: str) -> Dict[str, Dict]:
    """Get all templates in a specific category"""
    return {
        key: template 
        for key, template in SCENE_TEMPLATES.items() 
        if template["category"] == category
    }

def suggest_template(
    scene_description: str,
    object_type: str = None,
    style: str = None
) -> str:
    """
    Suggest appropriate scene template based on description.
    
    Args:
        scene_description: Description of desired scene
        object_type: Type of object (product, character, building, environment)
        style: Desired style (professional, dramatic, cinematic, clean, etc.)
        
    Returns:
        Recommended template key
    """
    desc_lower = scene_description.lower()
    
    # Product templates
    if any(word in desc_lower for word in ['product', 'ecommerce', 'catalog', 'item']):
        if any(word in desc_lower for word in ['lifestyle', 'natural', 'contextual']):
            return "product_lifestyle"
        elif any(word in desc_lower for word in ['hero', 'dramatic', 'premium']):
            return "product_hero_dramatic"
        else:
            return "product_studio_pro"
    
    # Portrait templates
    elif any(word in desc_lower for word in ['portrait', 'character', 'person', 'face', 'headshot']):
        if any(word in desc_lower for word in ['noir', 'black and white', 'vintage']):
            return "portrait_noir"
        elif any(word in desc_lower for word in ['cinematic', 'dramatic', 'moody', 'artistic']):
            return "portrait_cinematic"
        else:
            return "portrait_professional"
    
    # Landscape templates
    elif any(word in desc_lower for word in ['landscape', 'environment', 'nature', 'outdoor scene']):
        if any(word in desc_lower for word in ['epic', 'wide', 'dramatic sky']):
            return "landscape_epic"
        elif any(word in desc_lower for word in ['moody', 'dark', 'fog', 'night']):
            return "landscape_moody"
        else:
            return "landscape_classic"
    
    # Architecture templates
    elif any(word in desc_lower for word in ['architecture', 'building', 'structure', 'interior']):
        if any(word in desc_lower for word in ['night', 'dramatic night']):
            return "architecture_dramatic"
        elif any(word in desc_lower for word in ['technical', 'clean', 'presentation']):
            return "architecture_technical"
        else:
            return "architecture_hero"
    
    # Default to product studio
    return "product_studio_pro"

def get_template_info(template_key: str) -> Dict[str, Any]:
    """Get detailed information about a specific template"""
    if template_key not in SCENE_TEMPLATES:
        return {"error": f"Template '{template_key}' not found"}
    
    template = SCENE_TEMPLATES[template_key]
    
    return {
        "name": template["name"],
        "description": template["description"],
        "category": template["category"],
        "ideal_for": template["ideal_for"],
        "settings": {
            "geometry": template["geometry"],
            "materials": template["materials"],
            "lighting": template["lighting"],
            "composition": template["composition"],
            "color_grading": template["color_grading"],
            "render": template["render"],
        }
    }

def customize_template(
    template_key: str,
    customizations: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a customized version of a template.
    
    Args:
        template_key: Base template to customize
        customizations: Dict of settings to override
        
    Returns:
        Customized template configuration
    """
    if template_key not in SCENE_TEMPLATES:
        return {"error": f"Template '{template_key}' not found"}
    
    # Deep copy template
    import copy
    custom_template = copy.deepcopy(SCENE_TEMPLATES[template_key])
    
    # Apply customizations
    for category, settings in customizations.items():
        if category in custom_template:
            if isinstance(settings, dict):
                custom_template[category].update(settings)
            else:
                custom_template[category] = settings
    
    return custom_template
