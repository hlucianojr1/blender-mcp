#!/usr/bin/env python3
"""
Test script to verify connection to Blender MCP server.
This script tests both direct Blender connection and MCP server functionality.
"""

import socket
import json
import time
import sys
from typing import Dict, Any

# Configuration
BLENDER_HOST = "localhost"  # or "host.docker.internal" if testing from inside Docker
BLENDER_PORT = 9876
TIMEOUT = 5

def test_blender_direct_connection() -> bool:
    """Test direct socket connection to Blender addon."""
    print("🔌 Testing direct connection to Blender addon...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            result = sock.connect_ex((BLENDER_HOST, BLENDER_PORT))
            
            if result == 0:
                print(f"✅ Successfully connected to Blender at {BLENDER_HOST}:{BLENDER_PORT}")
                return True
            else:
                print(f"❌ Cannot connect to Blender at {BLENDER_HOST}:{BLENDER_PORT}")
                print("   Make sure Blender is running with the BlenderMCP addon enabled")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def send_test_command() -> bool:
    """Send a test command to Blender and verify response."""
    print("📤 Testing command execution...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((BLENDER_HOST, BLENDER_PORT))
            
            # Send a simple test command
            test_command = {
                "type": "get_scene_info",
                "params": {}
            }
            
            message = json.dumps(test_command).encode('utf-8')
            sock.sendall(message)
            
            # Receive response
            response_data = sock.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get("status") == "success":
                print("✅ Test command executed successfully!")
                print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
                return True
            else:
                print(f"❌ Command failed: {response}")
                return False
                
    except Exception as e:
        print(f"❌ Command execution error: {e}")
        return False

def test_mcp_server_process() -> bool:
    """Check if MCP server process is running."""
    print("🐳 Checking MCP server status...")
    
    import subprocess
    
    try:
        # Check if Docker container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=blender-mcp-server", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            if "Up" in status:
                print(f"✅ MCP Docker container is running: {status}")
                return True
            else:
                print(f"❌ MCP Docker container status: {status}")
                return False
        else:
            print("❌ MCP Docker container not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking Docker status: {e}")
        return False

def test_mcp_protocol() -> bool:
    """Test MCP protocol communication (if server is accessible)."""
    print("🔧 Testing MCP protocol...")
    
    try:
        # This would require MCP client library
        # For now, just check if we can import the server module
        import sys
        sys.path.append('src')
        
        try:
            from blender_mcp.server import BlenderConnection
            print("✅ MCP server module imports successfully")
            
            # Test connection creation
            conn = BlenderConnection(host=BLENDER_HOST, port=BLENDER_PORT)
            if conn.connect():
                print("✅ MCP BlenderConnection established")
                conn.disconnect()
                return True
            else:
                print("❌ MCP BlenderConnection failed")
                return False
                
        except ImportError as e:
            print(f"❌ Cannot import MCP server module: {e}")
            return False
            
    except Exception as e:
        print(f"❌ MCP protocol test error: {e}")
        return False

def main():
    """Run all connection tests."""
    print("🚀 BlenderMCP Connection Test Suite")
    print("=" * 50)
    
    tests = [
        ("Docker Container Status", test_mcp_server_process),
        ("Direct Blender Connection", test_blender_direct_connection),
        ("Command Execution", send_test_command),
        ("MCP Protocol", test_mcp_protocol),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Connection is working properly.")
        return 0
    else:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        if not results.get("Docker Container Status", True):
            print("• Start Docker container: docker compose up")
        if not results.get("Direct Blender Connection", True):
            print("• Open Blender and install the BlenderMCP addon")
            print("• Enable the addon and click 'Connect to Claude'")
        if not results.get("Command Execution", True):
            print("• Check Blender console for error messages")
            print("• Verify addon is properly loaded and running")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())