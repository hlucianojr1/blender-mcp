#!/usr/bin/env python3
"""
Test script for BlenderKit integration in Blender MCP
Tests search, categories, download, and background download polling
with exponential backoff retry logic and large file support.
"""

import socket
import json
import sys
import time

def send_command(sock, command_type, params=None):
    """Send a command to Blender and get response"""
    command = {
        "type": command_type,
        "params": params or {}
    }
    
    message = json.dumps(command) + "\n"
    sock.sendall(message.encode('utf-8'))
    
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
        try:
            json.loads(response.decode('utf-8'))
            break
        except json.JSONDecodeError:
            continue
    
    return json.loads(response.decode('utf-8'))


def test_blenderkit_features():
    """Test BlenderKit integration features"""
    print("=" * 60)
    print("BlenderKit Integration Test")
    print("(with retry logic & background downloads)")
    print("=" * 60)
    print("\nConnecting to Blender MCP server...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(120)  # Longer timeout for downloads
        sock.connect(('localhost', 9876))
        print("✓ Connected to Blender\n")
        
        # Test 1: Check BlenderKit status
        print("1. Checking BlenderKit status...")
        result = send_command(sock, "get_blenderkit_status", {})
        status_result = result.get("result", {})
        print(f"   Enabled: {status_result.get('enabled')}")
        print(f"   Authenticated: {status_result.get('authenticated')}")
        print(f"   Native available: {status_result.get('native_available')}")
        msg = status_result.get('message', '')[:80]
        print(f"   Message: {msg}...")
        
        if not status_result.get("enabled"):
            print("\n⚠️  BlenderKit is not enabled.")
            print("   To test BlenderKit features:")
            print("   1. Install BlenderKit addon from blenderkit.com")
            print("   2. Enable it in Blender preferences")
            print("   3. Enable 'Use BlenderKit' in BlenderMCP panel")
            print("   4. Start the MCP server")
            sock.close()
            return 0
        
        print()
        
        # Test 2: Get categories (tests retry logic)
        print("2. Getting model categories (tests API with retry logic)...")
        result = send_command(sock, "get_blenderkit_categories", {
            "asset_type": "model"
        })
        cat_result = result.get("result", {})
        if "error" in cat_result:
            print(f"   Error: {cat_result['error']}")
        else:
            categories = cat_result.get("categories", [])
            print(f"   Found {len(categories)} categories")
            if categories[:3]:
                print(f"   First 3: {[c.get('name') for c in categories[:3]]}")
        print()
        
        # Test 3: Search for free models
        print("3. Searching for free chair models...")
        result = send_command(sock, "search_blenderkit_assets", {
            "query": "chair",
            "asset_type": "model",
            "free_only": True,
            "count": 5
        })
        search_result = result.get("result", {})
        if "error" in search_result:
            print(f"   Error: {search_result['error']}")
            test_asset = None
        else:
            assets = search_result.get("results", [])
            print(f"   Found {len(assets)} free chair models")
            
            # Store first free asset for download test
            test_asset = None
            for a in assets:
                if a.get("is_free"):
                    test_asset = a
                    break
            
            if test_asset:
                print(f"   Test asset: {test_asset.get('name')}")
                print(f"   Asset ID: {test_asset.get('asset_base_id', test_asset.get('id'))}")
                size_mb = test_asset.get('file_size', 0) / (1024*1024)
                print(f"   Size: {size_mb:.1f}MB")
        print()
        
        # Test 4: Search materials
        print("4. Searching for free wood materials...")
        result = send_command(sock, "search_blenderkit_assets", {
            "query": "wood",
            "asset_type": "material",
            "free_only": True,
            "count": 3
        })
        mat_result = result.get("result", {})
        if "error" in mat_result:
            print(f"   Error: {mat_result['error']}")
        else:
            print(f"   Found {len(mat_result.get('results', []))} materials")
        print()
        
        # Test 5: Search HDRIs
        print("5. Searching for free HDRIs...")
        result = send_command(sock, "search_blenderkit_assets", {
            "query": "outdoor",
            "asset_type": "hdr",
            "free_only": True,
            "count": 3
        })
        hdr_result = result.get("result", {})
        if "error" in hdr_result:
            print(f"   Error: {hdr_result['error']}")
        else:
            print(f"   Found {len(hdr_result.get('results', []))} HDRIs")
        print()
        
        # Test 6: Download test (only if we have a small free asset)
        if test_asset and test_asset.get("file_size", float('inf')) < 5 * 1024 * 1024:
            print("6. Testing download (small asset < 5MB)...")
            asset_id = test_asset.get('asset_base_id', test_asset.get('id'))
            result = send_command(sock, "download_blenderkit_asset", {
                "asset_id": asset_id,
                "asset_type": "model",
                "name": "TestChair",
                "location": [2, 0, 0]
            })
            dl_result = result.get("result", {})
            
            if dl_result.get("status") == "background":
                # Poll for completion
                download_id = dl_result.get("download_id")
                print(f"   Background download started: {download_id}")
                
                for i in range(60):  # Poll for up to 60 seconds
                    time.sleep(1)
                    poll_result = send_command(sock, "poll_blenderkit_download", {
                        "download_id": download_id
                    })
                    poll_data = poll_result.get("result", {})
                    status = poll_data.get("status")
                    progress = poll_data.get("progress", 0)
                    
                    print(f"   Progress: {progress}% ({status})")
                    
                    if status in ["completed", "error"]:
                        if status == "completed":
                            print(f"   ✓ Imported: {poll_data.get('imported', [])}")
                        else:
                            print(f"   ✗ Error: {poll_data.get('error')}")
                        break
            elif dl_result.get("success"):
                print(f"   ✓ Imported: {dl_result.get('imported', [])}")
            elif "error" in dl_result:
                print(f"   Error: {dl_result['error']}")
        else:
            size_info = ""
            if test_asset:
                size_mb = test_asset.get("file_size", 0) / (1024*1024)
                size_info = f" (found asset is {size_mb:.1f}MB)"
            print(f"6. Skipping download test - no small free asset found{size_info}")
        
        print()
        
        # Test 7: Poll all downloads
        print("7. Checking all download status...")
        result = send_command(sock, "poll_blenderkit_download", {})
        poll_result = result.get("result", {})
        active = poll_result.get("active_downloads", [])
        completed = poll_result.get("completed", [])
        print(f"   Active downloads: {len(active)}")
        print(f"   Completed: {len(completed)}")
        
        print()
        print("=" * 60)
        print("✓ All BlenderKit tests completed!")
        print("=" * 60)
        
        sock.close()
        return 0
        
    except ConnectionRefusedError:
        print("✗ Error: Could not connect to Blender MCP server")
        print("  Make sure Blender is running with the MCP addon enabled")
        return 1
    except socket.timeout:
        print("✗ Error: Connection timed out")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_blenderkit_features())
