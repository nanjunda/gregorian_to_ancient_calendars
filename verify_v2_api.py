import sys
import os
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.getcwd())

from app import app

def verify_v2_contract():
    print("🧪 Verifying API v2.0 Headless Contract...")
    
    test_data = {
        "calendar": "panchanga",
        "date": "2026-05-20",
        "time": "10:00",
        "location": "New York, USA",
        "lang": "EN"
    }

    with app.test_client() as client:
        print("  - Calling /api/v2/calculate...")
        resp = client.post('/api/v2/calculate', json=test_data)
        if resp.status_code != 200:
            print(f"  ❌ Failed: Status Code {resp.status_code}")
            return False
        
        data = resp.get_json()
        
        # Verify Structure
        required_keys = ["status", "metadata", "results", "education"]
        for key in required_keys:
            if key not in data:
                print(f"  ❌ Missing required key: {key}")
                return False
        
        # Verify Metadata
        if data["metadata"]["civilization"] != "panchanga":
            print(f"  ❌ Incorrect civilization in metadata: {data['metadata']['civilization']}")
            return False
            
        # Verify Results
        civ_data = data["results"]["civilization_specific"]
        if "tithi" not in civ_data or "nakshatra" not in civ_data:
            print(f"  ❌ Missing core panchanga data in results")
            return False
            
        print("  ✅ v2.0 Calculation API Contract Verified!")
        return True

if __name__ == "__main__":
    if verify_v2_contract():
        sys.exit(0)
    else:
        sys.exit(1)
