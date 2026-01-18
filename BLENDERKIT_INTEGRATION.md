# BlenderKit Integration Documentation

This document describes the BlenderKit integration features available in the Blender MCP server for discovering, searching, and downloading assets from BlenderKit.

## Overview

BlenderKit is a massive online library of 3D assets including models, materials, HDRIs, brushes, and scenes. This integration allows AI agents to search and download assets directly into Blender scenes.

### Requirements

- **BlenderKit addon** must be installed and enabled in Blender
- **BlenderKit account** with valid authentication (logged in via the addon)
- **"Use BlenderKit"** toggle enabled in the BlenderMCP panel

### Available Tools

| Tool | Description |
|------|-------------|
| `get_blenderkit_status` | Check if BlenderKit addon is installed and authenticated |
| `search_blenderkit_assets` | Search for assets with filters |
| `get_blenderkit_categories` | List available asset categories |
| `download_blenderkit_asset` | Download and import assets into Blender |
| `poll_blenderkit_download` | Check background download progress |

---

## Setup

### 1. Install BlenderKit Addon

1. Open Blender
2. Go to **Edit → Preferences → Add-ons**
3. Search for "BlenderKit"
4. Enable the addon
5. Log in to your BlenderKit account in the addon preferences

### 2. Enable BlenderKit in BlenderMCP

1. In Blender's 3D Viewport, find the **BlenderMCP** panel (usually in the sidebar, press `N`)
2. Enable the **"Use BlenderKit"** checkbox
3. Start the MCP server

---

## Tools Reference

### `get_blenderkit_status`

Check if BlenderKit integration is available and properly configured.

**Parameters:** None

**Returns:**
```json
{
  "enabled": true,
  "addon_installed": true,
  "authenticated": true,
  "api_key_available": true,
  "message": "BlenderKit integration is ready"
}
```

**Possible Status Messages:**
- `"BlenderKit integration is ready"` - Everything is configured correctly
- `"BlenderKit addon is not installed"` - Install the BlenderKit addon
- `"BlenderKit user is not authenticated"` - Log in to BlenderKit in addon preferences
- `"BlenderKit integration is disabled in MCP settings"` - Enable the toggle in BlenderMCP panel

---

### `search_blenderkit_assets`

Search for assets on BlenderKit with various filters.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | *required* | Search query (e.g., "wooden chair", "brick wall") |
| `asset_type` | string | "model" | Asset type to search for |
| `category` | string | None | Filter by category |
| `free_only` | bool | True | Only return free assets |
| `count` | int | 20 | Maximum number of results (1-100) |

**Asset Types:**

| Type | Description |
|------|-------------|
| `model` | 3D models (furniture, vehicles, characters, etc.) |
| `material` | PBR materials and textures |
| `hdr` | HDR environment maps for lighting |
| `brush` | Sculpting and painting brushes |
| `scene` | Complete scene setups |

**Example:**
```python
# Search for free wooden chairs
search_blenderkit_assets(
    query="wooden chair",
    asset_type="model",
    free_only=True,
    count=10
)

# Search for brick materials
search_blenderkit_assets(
    query="brick wall",
    asset_type="material",
    category="architecture"
)

# Search for outdoor HDRIs
search_blenderkit_assets(
    query="outdoor sunny",
    asset_type="hdr"
)
```

**Returns:**
```json
{
  "results": [
    {
      "id": "asset-uuid-here",
      "name": "Wooden Chair",
      "asset_type": "model",
      "author": "artist_name",
      "is_free": true,
      "thumbnail_url": "https://...",
      "description": "A rustic wooden chair...",
      "tags": ["wood", "furniture", "chair"],
      "download_count": 1234
    }
  ],
  "count": 10,
  "total": 150
}
```

---

### `get_blenderkit_categories`

Get available categories for a specific asset type.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asset_type` | string | "model" | Asset type to get categories for |

**Example:**
```python
# Get model categories
get_blenderkit_categories(asset_type="model")

# Get material categories
get_blenderkit_categories(asset_type="material")
```

**Returns:**
```json
{
  "asset_type": "model",
  "categories": [
    {"name": "furniture", "count": 5000},
    {"name": "architecture", "count": 3000},
    {"name": "vehicles", "count": 2000},
    {"name": "nature", "count": 4500}
  ]
}
```

---

### `download_blenderkit_asset`

Download and import an asset into the current Blender scene.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `asset_id` | string | *required* | Asset ID from search results |
| `location` | list[float] | [0, 0, 0] | World location to place the asset |
| `link` | bool | False | Link instead of append (for models) |

**Example:**
```python
# Download and place a model
download_blenderkit_asset(
    asset_id="abc123-uuid",
    location=[2.0, 0.0, 0.0]
)

# Link a model (doesn't embed data, references library file)
download_blenderkit_asset(
    asset_id="abc123-uuid",
    location=[0, 0, 0],
    link=True
)
```

**Returns (Immediate Download):**
```json
{
  "status": "completed",
  "asset_id": "abc123-uuid",
  "asset_name": "Wooden Chair",
  "object_name": "Wooden_Chair",
  "message": "Asset 'Wooden Chair' imported successfully"
}
```

**Returns (Background Download for Large Files):**
```json
{
  "status": "downloading",
  "download_id": "dl_abc123",
  "asset_id": "abc123-uuid",
  "message": "Large file detected. Download started in background. Use poll_blenderkit_download to check progress."
}
```

---

### `poll_blenderkit_download`

Check the progress of a background download.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `download_id` | string | *required* | Download ID from download_blenderkit_asset response |

**Example:**
```python
poll_blenderkit_download(download_id="dl_abc123")
```

**Returns (In Progress):**
```json
{
  "status": "downloading",
  "download_id": "dl_abc123",
  "progress": 65.5,
  "message": "Downloading... 65.5%"
}
```

**Returns (Completed):**
```json
{
  "status": "completed",
  "download_id": "dl_abc123",
  "asset_name": "Wooden Chair",
  "object_name": "Wooden_Chair",
  "message": "Download completed and asset imported"
}
```

**Returns (Failed):**
```json
{
  "status": "failed",
  "download_id": "dl_abc123",
  "error": "Network timeout"
}
```

---

## Workflows

### Workflow 1: Find and Add a 3D Model

```python
# 1. Check BlenderKit is ready
status = get_blenderkit_status()

# 2. Search for assets
results = search_blenderkit_assets(
    query="office desk",
    asset_type="model",
    free_only=True,
    count=5
)

# 3. Download the first result
asset = results["results"][0]
download_blenderkit_asset(
    asset_id=asset["id"],
    location=[0, 0, 0]
)
```

### Workflow 2: Apply a Material from BlenderKit

```python
# 1. Search for materials
results = search_blenderkit_assets(
    query="wood oak",
    asset_type="material",
    free_only=True
)

# 2. Download material (applies to selected object)
download_blenderkit_asset(
    asset_id=results["results"][0]["id"]
)
```

### Workflow 3: Set Up Lighting with HDRI

```python
# 1. Search for HDRIs
results = search_blenderkit_assets(
    query="studio lighting",
    asset_type="hdr",
    free_only=True
)

# 2. Download and apply HDRI
download_blenderkit_asset(
    asset_id=results["results"][0]["id"]
)
```

### Workflow 4: Handle Large Asset Downloads

```python
# 1. Start download
result = download_blenderkit_asset(
    asset_id="large-model-uuid",
    location=[0, 0, 0]
)

# 2. If background download started, poll for completion
if result["status"] == "downloading":
    download_id = result["download_id"]
    
    # Poll until complete
    while True:
        status = poll_blenderkit_download(download_id=download_id)
        if status["status"] == "completed":
            print(f"Asset imported: {status['object_name']}")
            break
        elif status["status"] == "failed":
            print(f"Download failed: {status['error']}")
            break
        # Wait before polling again
        time.sleep(2)
```

### Workflow 5: Browse Categories First

```python
# 1. Get available categories for models
categories = get_blenderkit_categories(asset_type="model")

# 2. Search within a specific category
results = search_blenderkit_assets(
    query="modern",
    asset_type="model",
    category="furniture",
    free_only=True
)
```

---

## Technical Details

### Rate Limiting & Retry Logic

The integration includes exponential backoff retry logic:
- **Max retries:** 5
- **Handles:** HTTP 429 (rate limit) and 5xx server errors
- **Respects:** `Retry-After` header when present
- **Backoff:** Exponential with jitter

### Background Downloads

Files larger than **10MB** are automatically downloaded in the background:
- Returns a `download_id` immediately
- Use `poll_blenderkit_download` to check progress
- Downloads continue even during other operations

### Authentication

Authentication is handled by the BlenderKit addon:
- API key is retrieved from addon preferences
- OAuth2 + PKCE flow (handled by addon)
- No separate authentication required in MCP

---

## Error Handling

All tools return error messages in the format:

```json
{"error": "Error description"}
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `"BlenderKit addon is not installed"` | Addon missing | Install BlenderKit addon in Blender preferences |
| `"BlenderKit user is not authenticated"` | Not logged in | Log in via BlenderKit addon preferences |
| `"BlenderKit integration is disabled"` | Toggle off | Enable "Use BlenderKit" in BlenderMCP panel |
| `"Asset not found"` | Invalid asset_id | Use asset_id from search results |
| `"Rate limited"` | Too many requests | Wait and retry (automatic with retry logic) |
| `"Download failed"` | Network/server issue | Check connection, retry later |

---

## Testing

Run the test script to verify BlenderKit features:

```bash
# Make sure Blender is running with MCP addon enabled
# Make sure BlenderKit addon is installed and logged in
# Make sure "Use BlenderKit" is enabled in BlenderMCP panel

python test_blenderkit_features.py
```

The test script verifies:
1. BlenderKit status check
2. Category listing
3. Asset search (models, materials, HDRIs)
4. Asset download
5. Background download polling

---

## Notes

- **Free assets by default:** `free_only=True` is the default to avoid unexpected purchases
- **Linked vs Appended:** Use `link=True` for library linking (smaller file size, but requires source file)
- **Asset placement:** Models are placed at the specified `location`; materials are applied to selected objects
- **HDRIs:** Automatically set up as world environment
- **Caching:** Downloaded assets are cached by BlenderKit addon for faster subsequent access
