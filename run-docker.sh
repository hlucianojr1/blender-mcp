#!/bin/bash
# BlenderMCP Docker Build and Run Script
# Usage: ./run-docker.sh [command]
#   start   - Build and start the container (default)
#   stop    - Stop the container
#   restart - Restart the container
#   logs    - View container logs
#   status  - Check container status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker Desktop."
        exit 1
    fi
}

start_container() {
    log_info "Building and starting BlenderMCP container..."
    docker compose down 2>/dev/null || true
    docker compose up --build -d
    log_info "Container started successfully!"
    echo ""
    log_info "Make sure Blender is running with the addon enabled on port 9876"
    status_container
}

stop_container() {
    log_info "Stopping BlenderMCP container..."
    docker compose down
    log_info "Container stopped."
}

restart_container() {
    log_info "Restarting BlenderMCP container..."
    docker compose restart
    log_info "Container restarted."
    status_container
}

logs_container() {
    log_info "Showing container logs (Ctrl+C to exit)..."
    docker compose logs -f
}

status_container() {
    echo ""
    log_info "Container status:"
    docker compose ps
}

rebuild_container() {
    log_info "Rebuilding BlenderMCP container (no cache)..."
    docker compose down 2>/dev/null || true
    docker compose build --no-cache
    docker compose up -d
    log_info "Container rebuilt and started!"
    status_container
}

show_help() {
    echo "BlenderMCP Docker Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start    Build and start the container (default)"
    echo "  stop     Stop the container"
    echo "  restart  Restart the container"
    echo "  rebuild  Rebuild container without cache"
    echo "  logs     View container logs (follow mode)"
    echo "  status   Check container status"
    echo "  help     Show this help message"
    echo ""
}

# Main
check_docker

case "${1:-start}" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    rebuild)
        rebuild_container
        ;;
    logs)
        logs_container
        ;;
    status)
        status_container
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
