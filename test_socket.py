#!/usr/bin/env python3
"""
Simple socket test to verify Docker container can reach Blender.
This tests the basic networking between Docker and host.
"""

import socket
import time

def test_socket_connection():
    """Test raw socket connection to Blender from different perspectives."""
    
    hosts_to_test = [
        ("localhost", "From VS Code to local Blender"),
        ("host.docker.internal", "From Docker to host Blender (macOS/Windows)"),
        ("172.17.0.1", "From Docker to host Blender (Linux default)"),
    ]
    
    port = 9876
    
    print("🔌 Socket Connection Test")
    print("=" * 40)
    
    for host, description in hosts_to_test:
        print(f"\n📡 Testing {description}")
        print(f"   Target: {host}:{port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            
            start_time = time.time()
            result = sock.connect_ex((host, port))
            end_time = time.time()
            
            if result == 0:
                print(f"   ✅ Connected successfully ({int((end_time - start_time) * 1000)}ms)")
                sock.close()
            else:
                print(f"   ❌ Connection failed (error code: {result})")
                
        except socket.gaierror as e:
            print(f"   ❌ DNS/Host resolution failed: {e}")
        except Exception as e:
            print(f"   ❌ Socket error: {e}")
        finally:
            try:
                sock.close()
            except:
                pass

def test_port_availability():
    """Test if the port is available on the host."""
    print(f"\n🚪 Port Availability Test")
    print("=" * 40)
    
    try:
        # Test if we can bind to the port (means it's free)
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_sock.bind(('localhost', 9876))
        test_sock.close()
        print("   ⚠️  Port 9876 is available (Blender addon not running)")
    except OSError:
        print("   ✅ Port 9876 is in use (likely Blender addon)")

if __name__ == "__main__":
    test_socket_connection()
    test_port_availability()
    
    print(f"\n💡 Next Steps:")
    print("   1. Ensure Blender is running")
    print("   2. Install and enable BlenderMCP addon")
    print("   3. Click 'Connect to Claude' in Blender")
    print("   4. Run the full test: python test_connection.py")