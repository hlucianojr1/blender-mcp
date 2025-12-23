"""
Configuration for Blender MCP Server
Supports environment variables for sensitive data
"""

import os
from dataclasses import dataclass


@dataclass
class TelemetryConfig:
    """Configuration for telemetry system"""
    
    # Enable/disable telemetry (can be disabled via environment variables)
    enabled: bool = True
    
    # Supabase configuration (should be provided via environment variables)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # Privacy settings
    collect_prompts: bool = False  # Don't collect prompt text by default
    max_prompt_length: int = 500   # Maximum prompt length if collection is enabled
    
    # Rate limiting
    max_events_per_minute: int = 60


def create_telemetry_config() -> TelemetryConfig:
    """
    Create telemetry configuration from environment variables.
    
    Environment Variables:
    - BLENDER_MCP_SUPABASE_URL: Supabase project URL
    - BLENDER_MCP_SUPABASE_ANON_KEY: Supabase anonymous key
    - DISABLE_TELEMETRY: Set to 'true', '1', 'yes', or 'on' to disable telemetry
    - BLENDER_MCP_DISABLE_TELEMETRY: Alternative way to disable telemetry
    - MCP_DISABLE_TELEMETRY: Another alternative to disable telemetry
    """
    # Check if telemetry is disabled via environment variables
    disable_vars = [
        "DISABLE_TELEMETRY",
        "BLENDER_MCP_DISABLE_TELEMETRY",
        "MCP_DISABLE_TELEMETRY"
    ]
    
    enabled = True
    for var in disable_vars:
        if os.environ.get(var, "").lower() in ("true", "1", "yes", "on"):
            enabled = False
            break
    
    # Get Supabase configuration from environment
    supabase_url = os.environ.get("BLENDER_MCP_SUPABASE_URL", "")
    supabase_anon_key = os.environ.get("BLENDER_MCP_SUPABASE_ANON_KEY", "")
    
    # If credentials are missing, disable telemetry
    if enabled and (not supabase_url or not supabase_anon_key):
        enabled = False
    
    return TelemetryConfig(
        enabled=enabled,
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        collect_prompts=os.environ.get("BLENDER_MCP_COLLECT_PROMPTS", "").lower() in ("true", "1", "yes", "on"),
        max_prompt_length=int(os.environ.get("BLENDER_MCP_MAX_PROMPT_LENGTH", "500")),
    )


# Global configuration instance
telemetry_config = create_telemetry_config()
