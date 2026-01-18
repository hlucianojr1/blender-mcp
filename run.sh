#!/bin/bash

# Blender MCP Server Startup Script
# This script runs the Blender Model Context Protocol server

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Blender MCP Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Check if dependencies are installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo -e "${RED}Warning: MCP package not found. Installing dependencies...${NC}"
    pip install -e .
fi

# Start the server
echo -e "${GREEN}Starting Blender MCP server...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

python3 main.py
