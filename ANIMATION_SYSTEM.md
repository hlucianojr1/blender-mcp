# Animation System for Blender MCP

## Overview

The Animation System provides comprehensive tools for creating character animations for third-person games. It supports standard game animations like idle, walk, run, jump, aim weapon, recoil, limp, death reactions, and more.

## Features

### Animation Presets

Pre-configured animations ready to apply to any rigged character:

| Preset | Category | Duration | Loop | Description |
|--------|----------|----------|------|-------------|
| `idle` | Locomotion | 60 frames | ✓ | Subtle breathing animation |
| `walk` | Locomotion | 30 frames | ✓ | Standard walking cycle |
| `run` | Locomotion | 20 frames | ✓ | Running locomotion cycle |
| `sprint` | Locomotion | 20 frames | ✓ | Maximum speed sprinting cycle |
| `crouch_idle` | Locomotion | 60 frames | ✓ | Crouched standing with subtle breathing |
| `crouch_walk` | Locomotion | 40 frames | ✓ | Crouched slow walking cycle |
| `jump` | Action | 45 frames | ✗ | Jump with takeoff and landing |
| `jump_start` | Locomotion | 10 frames | ✗ | Jump takeoff anticipation |
| `jump_loop` | Locomotion | 20 frames | ✓ | Mid-air floating loop |
| `jump_land` | Locomotion | 15 frames | ✗ | Landing impact and recovery |
| `crouch` | Action | 20 frames | ✗ | Transition to crouched position |
| `roll` | Action | 30 frames | ✗ | Combat dodge roll |
| `aim_weapon` | Combat | 15 frames | ✗ | Transition to weapon aiming pose |
| `aim_idle` | Combat | 60 frames | ✓ | Weapon aimed with subtle breathing |
| `recoil` | Combat | 10 frames | ✗ | Weapon recoil after shooting |
| `reload` | Combat | 60 frames | ✗ | Weapon reload sequence with mag swap |
| `cover_enter` | Combat | 20 frames | ✗ | Transition into cover position |
| `cover_idle` | Combat | 60 frames | ✓ | Crouched behind cover with subtle breathing |
| `cover_peek` | Combat | 30 frames | ✗ | Peek over/around cover to aim |
| `melee_attack` | Action | 25 frames | ✗ | Melee swing attack |
| `limp` | Status | 40 frames | ✓ | Injured walking animation |
| `death` | Status | 45 frames | ✗ | Death fall animation |
| `hit_react` | Status | 20 frames | ✗ | Hit reaction/flinch |
| `t_pose` | Utility | 1 frame | ✗ | Standard T-pose |
| `a_pose` | Utility | 1 frame | ✗ | Standard A-pose |

#### Frame Markers

Some presets include frame markers for syncing gameplay events:

| Preset | Marker | Frame | Description |
|--------|--------|-------|-------------|
| `reload` | `mag_out` | 18 | Magazine removed from weapon |
| `reload` | `mag_in` | 42 | New magazine inserted |
| `cover_peek` | `can_fire` | 15 | Frame when aiming is stable |
| `cover_peek` | `return_start` | 22 | Frame when returning to cover |

### Bone Mapping Support

Supports multiple bone naming conventions:

- **Mixamo** (default): Standard Mixamo rig naming (e.g., `mixamorig:Hips`)
- **Rigify**: Blender's Rigify addon naming (e.g., `spine`, `upper_arm.L`)
- **Generic**: Simple naming convention (e.g., `Hips`, `LeftArm`)

## MCP Tools Reference

### Preset Management

#### `list_animation_presets`
List all available animation presets.

```python
await list_animation_presets(ctx, category="locomotion")  # Filter by category
await list_animation_presets(ctx)  # List all presets
```

Categories: `locomotion`, `action`, `combat`, `status`, `utility`

#### `get_animation_preset_info`
Get detailed information about a preset including keyframe data.

```python
await get_animation_preset_info(ctx, preset_name="idle")
```

#### `suggest_animation_preset`
AI-powered animation suggestions based on description.

```python
await suggest_animation_preset(ctx, action_description="character walking slowly")
await suggest_animation_preset(ctx, action_description="player shooting rifle")
```

### Armature Management

#### `get_armature_info`
Get information about armatures in the scene.

```python
await get_armature_info(ctx)  # List all armatures
await get_armature_info(ctx, armature_name="Armature")  # Specific armature details
```

#### `get_armature_bones`
List bones with mapping validation.

```python
await get_armature_bones(ctx, armature_name="Armature", bone_mapping="mixamo")
```

### Timeline Control

#### `set_frame_range`
Set animation frame range.

```python
await set_frame_range(ctx, start_frame=1, end_frame=60)
```

#### `set_current_frame` / `get_current_frame`
Control timeline position.

```python
await set_current_frame(ctx, frame=30)
info = await get_current_frame(ctx)  # Returns frame info and FPS
```

### Keyframe Operations

#### `insert_keyframe`
Insert keyframe for a bone.

```python
await insert_keyframe(
    ctx,
    armature_name="Armature",
    bone_name="mixamorig:Hips",
    frame=10,
    rotation=[0, 15, 0],  # Euler degrees
    location=[0, 0, 0.1],
    interpolation="BEZIER"  # CONSTANT, LINEAR, BEZIER, etc.
)
```

#### `delete_keyframe`
Remove keyframe at specific frame.

```python
await delete_keyframe(ctx, armature_name="Armature", bone_name="mixamorig:Hips", frame=10)
```

### Preset Application

#### `apply_animation_preset`
**The fastest way to add professional animations!**

```python
await apply_animation_preset(
    ctx,
    preset_name="idle",
    armature_name="Armature",
    start_frame=1,
    bone_mapping="mixamo",  # Auto-detected if None
    action_name="my_idle_anim"  # Custom name (optional)
)
```

### Pose Control

#### `set_bone_pose`
Set bone pose without keyframing.

```python
await set_bone_pose(ctx, armature_name="Armature", bone_name="mixamorig:Head", rotation=[10, 0, 0])
```

#### `reset_bone_pose`
Reset bones to rest pose.

```python
await reset_bone_pose(ctx, armature_name="Armature")  # Reset all
await reset_bone_pose(ctx, armature_name="Armature", bone_name="mixamorig:Head")  # Reset one
```

### Action Management

#### `create_action`
Create a new action (animation clip).

```python
await create_action(ctx, action_name="walk_cycle", armature_name="Armature")
```

#### `list_actions`
List all actions in the scene.

```python
await list_actions(ctx)
await list_actions(ctx, armature_name="Armature")  # Filter by armature
```

#### `set_active_action`
Set which action is active on an armature.

```python
await set_active_action(ctx, armature_name="Armature", action_name="run_cycle")
```

#### `duplicate_action`
Duplicate an existing action.

```python
await duplicate_action(ctx, source_action="idle", new_name="idle_variant")
```

### NLA (Non-Linear Animation)

#### `create_nla_track`
Create NLA track for stacking animations.

```python
await create_nla_track(ctx, armature_name="Armature", track_name="combat_layer")
```

#### `push_action_to_nla`
Push action to NLA as a strip.

```python
await push_action_to_nla(
    ctx,
    armature_name="Armature",
    action_name="idle",
    track_name="base_layer",
    start_frame=1
)
```

### Playback & Export

#### `play_animation` / `stop_animation`
Control viewport playback.

```python
await play_animation(ctx, start_frame=1, end_frame=60, loop=True)
await stop_animation(ctx)
```

#### `export_animation_fbx`
Export for game engines (Unity, Unreal, Godot).

```python
await export_animation_fbx(
    ctx,
    filepath="/path/to/character_anims.fbx",
    armature_name="Armature",
    action_name="run_cycle",  # Specific action (optional)
    include_mesh=True
)
```

#### `export_animation_gltf`
Export to glTF/GLB for web engines (Three.js, Babylon.js) and game engines.

```python
await export_animation_gltf(
    ctx,
    filepath="/path/to/character_anims.glb",
    armature_name="Armature",
    action_name="run_cycle",  # Specific action (optional)
    include_mesh=True,
    export_format="GLB"  # GLB (binary) or GLTF_SEPARATE or GLTF_EMBEDDED
)
```

**glTF Export Formats:**

| Format | Extension | Description | Best For |
|--------|-----------|-------------|----------|
| `GLB` | .glb | Binary, single file | Web deployment, Three.js, Babylon.js |
| `GLTF_SEPARATE` | .gltf + .bin | Separate JSON + binary | Debugging, manual editing |
| `GLTF_EMBEDDED` | .gltf | Single JSON with embedded data | Simple sharing |

## Workflow Examples

### Quick Start: Apply Preset Animation

```python
# 1. List armatures
info = await get_armature_info(ctx)

# 2. Apply idle animation
await apply_animation_preset(ctx, "idle", "Armature")

# 3. Preview
await play_animation(ctx)
```

### Create Custom Animation

```python
# 1. Create new action
await create_action(ctx, "custom_nod", "Armature")

# 2. Set frame range
await set_frame_range(ctx, 1, 30)

# 3. Add keyframes
await insert_keyframe(ctx, "Armature", "mixamorig:Head", 1, rotation=[0, 0, 0])
await insert_keyframe(ctx, "Armature", "mixamorig:Head", 15, rotation=[15, 0, 0])
await insert_keyframe(ctx, "Armature", "mixamorig:Head", 30, rotation=[0, 0, 0])

# 4. Preview
await play_animation(ctx)
```

### Layer Multiple Animations with NLA

```python
# Apply base idle
await apply_animation_preset(ctx, "idle", "Armature", action_name="base_idle")

# Push to NLA
await push_action_to_nla(ctx, "Armature", "base_idle", "base_layer", 1)

# Apply aim on top
await apply_animation_preset(ctx, "aim_weapon", "Armature", action_name="aim_overlay")
await push_action_to_nla(ctx, "Armature", "aim_overlay", "upper_body_layer", 1)
```

### Export for Game Engine

```python
# Create animations
await apply_animation_preset(ctx, "idle", "Armature", action_name="idle")
await apply_animation_preset(ctx, "walk", "Armature", action_name="walk")
await apply_animation_preset(ctx, "run", "Armature", action_name="run")

# Export to FBX (Unity, Unreal)
await export_animation_fbx(ctx, "/game/assets/character.fbx", "Armature", include_mesh=True)

# Or export to glTF/GLB (Three.js, Babylon.js, Godot, web)
await export_animation_gltf(ctx, "/game/assets/character.glb", "Armature", include_mesh=True)
```

## Interpolation Types

Available interpolation modes for keyframes:

| Type | Description |
|------|-------------|
| `CONSTANT` | No interpolation, instant change |
| `LINEAR` | Linear interpolation |
| `BEZIER` | Smooth Bezier curves (default) |
| `SINE` | Sinusoidal ease |
| `QUAD` | Quadratic ease |
| `CUBIC` | Cubic ease |
| `QUART` | Quartic ease |
| `QUINT` | Quintic ease |
| `EXPO` | Exponential ease |
| `CIRC` | Circular ease |
| `BACK` | Overshoot ease |
| `BOUNCE` | Bounce effect |
| `ELASTIC` | Elastic spring effect |

## Best Practices

1. **Check bone mapping first**: Use `get_armature_bones()` to verify bone names before applying presets.

2. **Use presets for quick results**: Animation presets provide professional-quality animations instantly.

3. **Layer with NLA**: Use NLA tracks to combine animations (e.g., idle + aim_weapon).

4. **Export per-action for games**: Many game engines prefer separate FBX files per animation.

5. **Match FPS**: Ensure Blender's FPS matches your game engine (typically 30 or 60).

6. **Choose the right export format**:
   - **FBX**: Unity, Unreal Engine (industry standard)
   - **GLB**: Web (Three.js, Babylon.js), Godot, lightweight deployment
   - **GLTF_SEPARATE**: When you need to inspect/edit animation data

## Troubleshooting

### "Bone not found"
- Use `get_armature_bones()` to see actual bone names
- Try different `bone_mapping` values: `mixamo`, `rigify`, `generic`

### Animation not playing
- Check frame range with `get_current_frame()`
- Ensure armature has an action assigned
- Try `set_active_action()` to assign action

### Export issues
- Ensure armature is selected
- Check action is assigned before export
- Verify filepath has `.fbx` or `.glb`/`.gltf` extension
- For glTF: use `GLB` for single binary file, `GLTF_SEPARATE` for separate files
