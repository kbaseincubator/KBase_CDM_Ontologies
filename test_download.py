#!/usr/bin/env python3
"""Simple test script to debug ontology downloads."""

import os
import sys
import requests

def test_download():
    """Test downloading a single ontology."""
    test_url = "http://purl.obolibrary.org/obo/bfo.owl"
    print(f"Testing download from: {test_url}")
    
    try:
        # Test basic connectivity
        print("1. Testing basic connectivity...")
        response = requests.head(test_url, timeout=10, allow_redirects=True)
        print(f"   Status code: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        # Test actual download
        print("\n2. Testing actual download...")
        response = requests.get(test_url, timeout=30, allow_redirects=True)
        print(f"   Status code: {response.status_code}")
        print(f"   Content length: {len(response.content)} bytes")
        print(f"   Content type: {response.headers.get('content-type', 'unknown')}")
        
        # Save to test file
        test_file = "test_bfo.owl"
        with open(test_file, 'wb') as f:
            f.write(response.content)
        print(f"\n3. Successfully saved to {test_file}")
        print(f"   File size: {os.path.getsize(test_file)} bytes")
        
        # Clean up
        os.remove(test_file)
        print("\n✅ Download test successful!")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Ontology Download Test ===\n")
    success = test_download()
    sys.exit(0 if success else 1)