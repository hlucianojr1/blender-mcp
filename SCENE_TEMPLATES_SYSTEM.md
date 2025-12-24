# Scene Templates System

Professional pre-configured scene setups combining all enhancement systems for instant production-quality results.

## Overview

The Scene Templates System is the **FASTEST** way to transform a basic 3D scene into professional quality. Each template combines all 6 enhancement systems in one command:

1. **Geometry Enhancement** - Subdivision, beveling, smooth shading
2. **Material Setup** - PBR materials with appropriate settings
3. **Lighting Configuration** - HDRI + lighting rigs + atmosphere
4. **Composition Setup** - Camera framing + shot type + composition rules
5. **Color Grading** - Tone mapping + exposure + cinematic look
6. **Render Settings** - Quality, samples, resolution

**Quick Example:**
```python
# Transform basic model to professional product shot in ONE command
await apply_scene_template(ctx, "product_studio_pro", "my_product")
```

---

## Template Categories

### Product Photography (3 templates)
Professional product visualization for e-commerce, marketing, and advertising.

#### 1. product_studio_pro
**Clean studio product photography with white background**

- **Ideal for:** E-commerce, catalog, professional presentations
- **Geometry:** High detail with 2 subdivision levels, auto-smooth
- **Materials:** Aggressive auto-enhancement, glossy_plastic default
- **Lighting:** Studio HDRI + studio lighting rig
- **Composition:** Product hero shot, medium shot, rule of thirds, three-quarter angle
- **Color:** Product showcase grade (AgX tone mapping)
- **Render:** Production quality, 256 samples

**Use when:** You need clean, professional product shots for catalogs or online stores.

#### 2. product_lifestyle
**Natural lifestyle product shot with environmental context**

- **Ideal for:** Lifestyle marketing, social media, advertising
- **Geometry:** Smooth preset with 2 subdivision levels
- **Materials:** Standard auto-enhancement
- **Lighting:** Outdoor day HDRI + outdoor rig, haze atmosphere
- **Composition:** Product lifestyle preset, medium-wide shot, rule of thirds
- **Color:** Cinematic warm grade (Filmic, +0.2 exposure)
- **Render:** Production quality, 256 samples

**Use when:** Product needs to feel natural and contextual for lifestyle branding.

#### 3. product_hero_dramatic
**Dramatic hero shot with bold lighting and composition**

- **Ideal for:** Hero products, premium positioning, dramatic advertising
- **Geometry:** High detail with 3 subdivision levels + edge beveling
- **Materials:** Aggressive auto-enhancement
- **Lighting:** Sunset HDRI + dramatic rig, god rays atmosphere
- **Composition:** Product hero preset, closeup, golden ratio, low angle
- **Color:** Blockbuster grade (Filmic high contrast, +0.3 exposure)
- **Render:** Final quality, 512 samples

**Use when:** Product needs maximum visual impact for hero positioning.

---

### Portrait Photography (3 templates)
Professional character and portrait rendering.

#### 4. portrait_professional
**Classic professional portrait with balanced lighting**

- **Ideal for:** Professional headshots, business, corporate
- **Geometry:** Organic preset with 2 subdivision levels
- **Materials:** Standard auto-enhancement
- **Lighting:** Studio HDRI + three-point lighting rig
- **Composition:** Portrait pro preset, closeup, rule of thirds, front angle
- **Color:** Cinematic standard grade (Filmic)
- **Render:** Production quality, 256 samples

**Use when:** You need balanced, professional portrait photography.

#### 5. portrait_cinematic
**Cinematic portrait with dramatic lighting and mood**

- **Ideal for:** Cinematic shots, artistic portraits, dramatic mood
- **Geometry:** Organic preset with 3 subdivision levels
- **Materials:** Aggressive auto-enhancement
- **Lighting:** Sunset HDRI + dramatic rig, fog atmosphere
- **Composition:** Portrait cinematic preset, closeup, golden ratio, three-quarter angle
- **Color:** Moody portrait grade (Filmic high contrast, -0.2 exposure, 1.1 gamma)
- **Render:** Final quality, 512 samples

**Use when:** Portrait needs cinematic drama and artistic atmosphere.

#### 6. portrait_noir
**Classic black and white film noir portrait**

- **Ideal for:** Film noir style, black & white photography, vintage look
- **Geometry:** Smooth preset with 2 subdivision levels
- **Materials:** Standard auto-enhancement
- **Lighting:** Studio HDRI + dramatic rig (high contrast)
- **Composition:** Portrait pro preset, medium closeup, center composition, side angle
- **Color:** Noir classic grade (Filmic high contrast, -0.3 exposure, 0.9 gamma)
- **Render:** Production quality, 256 samples

**Use when:** You want classic black & white film noir aesthetic.

---

### Landscape/Environment (3 templates)
Wide environmental shots and scenic visualization.

#### 7. landscape_epic
**Epic wide landscape with dramatic sky and atmosphere**

- **Ideal for:** Epic vistas, cinematic environments, dramatic wide shots
- **Geometry:** Architectural preset with 1 subdivision level
- **Materials:** Standard auto-enhancement
- **Lighting:** Sunset HDRI + outdoor rig, god rays atmosphere
- **Composition:** Landscape epic preset, extreme wide, rule of thirds
- **Color:** Cinematic warm grade (Filmic high contrast, +0.3 exposure)
- **Render:** Final quality, 512 samples

**Use when:** You want maximum drama and epic scale for environments.

#### 8. landscape_classic
**Classic balanced landscape composition**

- **Ideal for:** Traditional photography, natural scenes, balanced composition
- **Geometry:** Smooth preset with 1 subdivision level
- **Materials:** Standard auto-enhancement
- **Lighting:** Outdoor day HDRI + outdoor rig, haze atmosphere
- **Composition:** Landscape classic preset, wide shot, golden ratio
- **Color:** Cinematic standard grade (AgX)
- **Render:** Production quality, 256 samples

**Use when:** You want classic, balanced landscape photography.

#### 9. landscape_moody
**Dark moody landscape with fog and low light**

- **Ideal for:** Moody atmospheres, mysterious scenes, dark environments
- **Geometry:** Smooth preset with 1 subdivision level
- **Materials:** Aggressive auto-enhancement
- **Lighting:** Night HDRI + night rig, heavy fog atmosphere
- **Composition:** Landscape classic preset, wide shot, rule of thirds
- **Color:** Moody portrait grade (Filmic high contrast, -0.5 exposure, 0.9 gamma)
- **Render:** Production quality, 256 samples

**Use when:** Scene needs dark, mysterious, atmospheric mood.

---

### Architecture Visualization (3 templates)
Professional architectural rendering and visualization.

#### 10. architecture_hero
**Dramatic architectural hero shot with strong composition**

- **Ideal for:** Hero shots, portfolio work, showcase projects
- **Geometry:** Architectural preset with 1 subdivision level
- **Materials:** Aggressive auto-enhancement
- **Lighting:** Sunset HDRI + dramatic rig, haze atmosphere
- **Composition:** Architecture hero preset, wide shot, golden ratio, low angle
- **Color:** Blockbuster grade (Filmic high contrast, +0.2 exposure)
- **Render:** Final quality, 512 samples

**Use when:** Building needs dramatic hero presentation for portfolio.

#### 11. architecture_technical
**Clean technical architectural visualization**

- **Ideal for:** Technical presentations, clean visuals, professional documentation
- **Geometry:** Architectural preset with 1 subdivision level
- **Materials:** Standard auto-enhancement
- **Lighting:** Outdoor day HDRI + outdoor rig
- **Composition:** Architecture hero preset, medium-wide, center composition, front angle
- **Color:** Product showcase grade (AgX)
- **Render:** Production quality, 256 samples

**Use when:** You need clean, technical architectural documentation.

#### 12. architecture_dramatic
**Dramatic night architecture with atmospheric lighting**

- **Ideal for:** Night shots, dramatic presentation, artistic visualization
- **Geometry:** Architectural preset with 1 subdivision level
- **Materials:** Aggressive auto-enhancement
- **Lighting:** Night HDRI + night rig, fog atmosphere
- **Composition:** Architecture dramatic preset, wide shot, diagonal rule, low angle
- **Color:** Sci-fi cool grade (Filmic high contrast, -0.3 exposure, 1.1 gamma)
- **Render:** Final quality, 512 samples

**Use when:** Building needs dramatic night presentation.

---

## API Reference

### 1. apply_scene_template()

Apply complete professional scene template.

```python
await apply_scene_template(
    ctx,
    template_key: str,
    target_object: str = None,  # Auto-detects if None
    auto_render: bool = False   # Render after applying
) -> str
```

**Parameters:**
- `template_key`: Template to apply (see categories above)
- `target_object`: Object to enhance (None = auto-detect main object)
- `auto_render`: Automatically render after applying template

**Returns:** Success message with applied steps

**Example:**
```python
# Apply product studio template to selected object
await apply_scene_template(ctx, "product_studio_pro")

# Apply portrait template to specific object
await apply_scene_template(ctx, "portrait_cinematic", "Character")

# Apply and render automatically
await apply_scene_template(ctx, "landscape_epic", auto_render=True)
```

---

### 2. list_scene_templates()

Browse all available scene templates.

```python
await list_scene_templates(
    ctx,
    category: str = "all"  # all, product, portrait, landscape, architecture
) -> str
```

**Parameters:**
- `category`: Filter by category

**Returns:** Formatted list of templates with descriptions

**Example:**
```python
# List all templates
await list_scene_templates(ctx)

# List only product templates
await list_scene_templates(ctx, "product")

# List architecture templates
await list_scene_templates(ctx, "architecture")
```

---

### 3. suggest_scene_template()

Get AI recommendation based on scene description.

```python
await suggest_scene_template(
    ctx,
    scene_description: str,
    object_type: str = None,    # product, character, building, environment
    style: str = None           # professional, dramatic, cinematic, clean
) -> str
```

**Parameters:**
- `scene_description`: Describe what you want to create
- `object_type`: Type of subject (optional)
- `style`: Desired style (optional)

**Returns:** Recommended template with explanation

**Examples:**
```python
# Get recommendation for e-commerce product
await suggest_scene_template(ctx, "professional product photo for e-commerce")
# Returns: product_studio_pro

# Get recommendation for dramatic architecture
await suggest_scene_template(ctx, "dramatic architectural night shot")
# Returns: architecture_dramatic

# Get recommendation with hints
await suggest_scene_template(
    ctx,
    "character portrait",
    object_type="character",
    style="cinematic"
)
# Returns: portrait_cinematic
```

---

### 4. customize_scene_template()

Create customized version of a template.

```python
await customize_scene_template(
    ctx,
    template_key: str,
    customizations: dict
) -> str
```

**Parameters:**
- `template_key`: Base template to customize
- `customizations`: Dict of settings to override

**Customizable Settings:**
- `geometry`: enhancement_preset, subdivision_levels, auto_smooth, edge_bevel
- `materials`: auto_enhance, aggressive, default_material
- `lighting`: hdri, lighting_rig, atmosphere, hdri_strength
- `composition`: preset, shot_type, composition_rule, camera_angle
- `color_grading`: preset, tone_mapping, exposure, gamma
- `render`: preset, samples

**Example:**
```python
# Customize product studio with sunset lighting
customizations = {
    "lighting": {
        "hdri": "sunset",
        "hdri_strength": 1.5
    },
    "color_grading": {
        "exposure": 0.3
    }
}
await customize_scene_template(ctx, "product_studio_pro", customizations)
```

---

## Workflows

### Quick Start Workflow

**Goal:** Transform basic model to professional quality in seconds

1. **Get Recommendation:**
   ```python
   await suggest_scene_template(ctx, "professional product shot")
   ```

2. **Apply Template:**
   ```python
   await apply_scene_template(ctx, "product_studio_pro", "MyProduct")
   ```

3. **Capture Result:**
   ```python
   await get_viewport_screenshot(ctx)
   ```

**Total Time:** < 10 seconds for production-quality results

---

### Browse and Select Workflow

**Goal:** Explore templates and choose manually

1. **Browse Category:**
   ```python
   await list_scene_templates(ctx, "product")
   ```

2. **Review Options:**
   - product_studio_pro - Clean white background
   - product_lifestyle - Natural environment
   - product_hero_dramatic - Bold dramatic lighting

3. **Select and Apply:**
   ```python
   await apply_scene_template(ctx, "product_lifestyle", "MyProduct")
   ```

---

### Customization Workflow

**Goal:** Start with template, then customize

1. **Start with Base Template:**
   ```python
   await apply_scene_template(ctx, "portrait_professional", "Character")
   ```

2. **Review Result:**
   ```python
   await get_viewport_screenshot(ctx)
   ```

3. **Customize if Needed:**
   ```python
   customizations = {
       "lighting": {"hdri": "sunset"},
       "color_grading": {"exposure": 0.2}
   }
   await customize_scene_template(ctx, "portrait_professional", customizations)
   ```

4. **Re-apply Customized:**
   ```python
   await apply_scene_template(ctx, "portrait_professional", "Character")
   ```

---

## Template Selection Guide

### By Use Case

**E-Commerce/Catalog:**
- `product_studio_pro` - Clean, professional, neutral

**Social Media/Marketing:**
- `product_lifestyle` - Natural, contextual, engaging

**Hero/Premium Products:**
- `product_hero_dramatic` - Bold, impactful, premium

**Professional Headshots:**
- `portrait_professional` - Balanced, clean, corporate

**Artistic/Cinematic:**
- `portrait_cinematic` - Dramatic, moody, artistic

**Black & White/Vintage:**
- `portrait_noir` - Classic film noir aesthetic

**Epic Environments:**
- `landscape_epic` - Wide, dramatic, cinematic

**Natural Landscapes:**
- `landscape_classic` - Balanced, traditional, clean

**Mysterious/Moody:**
- `landscape_moody` - Dark, foggy, atmospheric

**Architecture Portfolio:**
- `architecture_hero` - Dramatic, golden hour

**Technical Documentation:**
- `architecture_technical` - Clean, neutral, accurate

**Night Visualization:**
- `architecture_dramatic` - Night, dramatic, atmospheric

---

### By Lighting Style

**Studio Lighting:**
- product_studio_pro
- portrait_professional
- portrait_noir

**Outdoor Day:**
- product_lifestyle
- landscape_classic
- architecture_technical

**Golden Hour/Sunset:**
- product_hero_dramatic
- portrait_cinematic
- landscape_epic
- architecture_hero

**Night:**
- landscape_moody
- architecture_dramatic

---

### By Mood/Tone

**Clean & Professional:**
- product_studio_pro
- portrait_professional
- architecture_technical

**Warm & Inviting:**
- product_lifestyle
- landscape_classic

**Dramatic & Bold:**
- product_hero_dramatic
- portrait_cinematic
- landscape_epic
- architecture_hero

**Moody & Mysterious:**
- portrait_noir
- landscape_moody
- architecture_dramatic

---

## Technical Details

### Template Structure

Each template contains:

```python
{
    "name": "Human-readable name",
    "description": "What this template does",
    "category": "product|portrait|landscape|architecture",
    "ideal_for": ["use case 1", "use case 2"],
    
    "geometry": {
        "enhancement_preset": "smooth|high_detail|mechanical|organic|architectural",
        "subdivision_levels": 1-3,
        "auto_smooth": True|False,
        "edge_bevel": 0.01  # Optional
    },
    
    "materials": {
        "auto_enhance": True|False,
        "aggressive": True|False,
        "default_material": "material_preset_key"  # Optional
    },
    
    "lighting": {
        "hdri": "studio|outdoor_day|sunset|night",
        "lighting_rig": "studio|three_point|dramatic|outdoor|night",
        "atmosphere": None|"haze"|"fog"|"heavy_fog"|"god_rays",
        "hdri_strength": 0.5-2.0
    },
    
    "composition": {
        "preset": "composition_preset_key",
        "shot_type": "extreme_wide|wide|medium_wide|medium|medium_closeup|closeup",
        "composition_rule": "rule_of_thirds|golden_ratio|center|diagonal|leading_lines|symmetry",
        "camera_angle": "front|three_quarter|side|low|high"
    },
    
    "color_grading": {
        "preset": "color_grade_preset_key",
        "tone_mapping": "filmic|filmic_high_contrast|agx|standard",
        "exposure": -1.0 to +1.0,
        "gamma": 0.8 to 1.5
    },
    
    "render": {
        "preset": "preview|production|final",
        "samples": 64-512
    }
}
```

---

### Application Pipeline

When you call `apply_scene_template()`, it executes:

1. **Target Detection** - Auto-detect main object if not specified
2. **Geometry Enhancement** - Apply subdivision, beveling, smooth shading
3. **Material Setup** - Auto-enhance or apply preset materials
4. **Lighting Configuration** - Setup HDRI, lighting rigs, atmosphere
5. **Composition** - Position and frame camera with rules
6. **Color Grading** - Apply tone mapping and color adjustments
7. **Render Settings** - Configure quality and samples
8. **Optional Render** - Render if auto_render=True

Total execution time: 2-5 seconds for complete transformation

---

## Tips & Best Practices

### When to Use Templates

**✓ Use Templates When:**
- You want professional results immediately
- Scene fits standard photography style
- Working with common subject types
- Time is critical
- Learning the enhancement pipeline

**✗ Avoid Templates When:**
- Highly custom requirements
- Non-standard scenes
- Experimenting with unique styles
- Need granular control over every setting

---

### Template Modification

**Start with Closest Match:**
1. Use `suggest_scene_template()` to find closest
2. Apply template
3. Customize specific aspects if needed

**Common Customizations:**
- Lighting HDRI (change time of day)
- Exposure (adjust brightness)
- Camera angle (change viewpoint)
- Samples (balance quality vs speed)

**Example:**
```python
# Start with portrait professional
await apply_scene_template(ctx, "portrait_professional", "Character")

# Too dark? Increase exposure
custom = {"color_grading": {"exposure": 0.3}}
await customize_scene_template(ctx, "portrait_professional", custom)
```

---

### Performance Optimization

**Preview Mode:**
```python
# Use lower samples for quick previews
custom = {"render": {"samples": 64}}
await customize_scene_template(ctx, "product_studio_pro", custom)
```

**Production Mode:**
```python
# Use higher samples for final output
custom = {"render": {"samples": 512}}
await customize_scene_template(ctx, "architecture_hero", custom)
```

**Selective Enhancement:**
- Templates enhance target object only
- Other objects unaffected (efficient)
- Camera and lighting applied globally

---

## Troubleshooting

### Template Not Found

**Error:** `Template 'xyz' not found`

**Solution:**
```python
# List available templates
await list_scene_templates(ctx)

# Use exact key name
await apply_scene_template(ctx, "product_studio_pro")  # Correct
await apply_scene_template(ctx, "product studio")       # Wrong
```

---

### No Objects in Scene

**Error:** `No mesh objects found in scene`

**Solution:**
```python
# Import or create object first
await generate_hyper3d_model_via_text(ctx, "coffee mug")

# Then apply template
await apply_scene_template(ctx, "product_studio_pro", "generated_mug")
```

---

### Results Not as Expected

**Issue:** Template results don't match preview

**Solutions:**

1. **Check Object Scale:**
   ```python
   # Template assumes reasonable object size
   # Ensure object is 1-10 units in size
   ```

2. **Verify Materials:**
   ```python
   # Some templates work better with specific materials
   # Try different template or manual material setup
   ```

3. **Adjust Exposure:**
   ```python
   # Too dark/bright?
   custom = {"color_grading": {"exposure": 0.3}}
   await customize_scene_template(ctx, template_key, custom)
   ```

4. **Change HDRI:**
   ```python
   # Wrong lighting mood?
   custom = {"lighting": {"hdri": "sunset"}}
   await customize_scene_template(ctx, template_key, custom)
   ```

---

## Integration with Other Systems

Scene templates work seamlessly with other enhancement tools:

### After Template Application

You can still use individual enhancement tools:

```python
# Apply template first
await apply_scene_template(ctx, "product_studio_pro", "MyProduct")

# Then adjust specific aspects
await apply_composition_rule(ctx, "diagonal")  # Change composition
await setup_tone_mapping(ctx, "filmic_high_contrast")  # Adjust color
await configure_render_settings(ctx, "final")  # Increase quality
```

### Before Template Application

Generate or import assets first:

```python
# Generate AI model
await generate_hyper3d_model_via_text(ctx, "wooden chair")

# Import from Sketchfab
await download_sketchfab_model(ctx, "model_uid")

# Then apply template
await apply_scene_template(ctx, "product_lifestyle", "chair")
```

---

## Summary

Scene Templates provide the **FASTEST path** from basic 3D model to production-quality render:

**12 Professional Templates:**
- 3 Product Photography
- 3 Portrait Photography
- 3 Landscape/Environment
- 3 Architecture Visualization

**One Command:**
```python
await apply_scene_template(ctx, "template_key", "object_name")
```

**Complete Enhancement:**
- Geometry (subdivision, beveling)
- Materials (PBR auto-enhancement)
- Lighting (HDRI + rigs + atmosphere)
- Composition (camera + framing + rules)
- Color Grading (tone mapping + exposure)
- Render Settings (quality + samples)

**Instant Results:**
- 2-5 seconds application time
- Production quality output
- Fully customizable
- Works with all asset sources

**For more details:**
- See [MATERIAL_SYSTEM.md](MATERIAL_SYSTEM.md) for materials
- See [LIGHTING_SYSTEM.md](LIGHTING_SYSTEM.md) for lighting
- See [COMPOSITION_SYSTEM.md](COMPOSITION_SYSTEM.md) for composition
- See [COLOR_GRADING_SYSTEM.md](COLOR_GRADING_SYSTEM.md) for color grading
- See [POST_PROCESSING.md](POST_PROCESSING.md) for geometry
- See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for all tools
