import sys
import os
from datetime import datetime
import json

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from engines.panchanga.engine import PanchangaEngine

def test_parity():
    print("🧪 Running Zero Mutation Parity Test...")
    
    test_data = {
        "date": "2026-01-20",
        "time": "12:00",
        "location": "Bangalore, India",
        "lang": "EN"
    }

    # 1. Get output from Legacy app.py
    with app.test_client() as client:
        response = client.post('/api/panchanga', json=test_data)
        legacy_output = response.get_json()["data"]

    # 2. Get output from New PanchangaEngine
    engine = PanchangaEngine()
    new_output = engine.calculate_data(
        test_data["date"], 
        test_data["time"], 
        test_data["location"], 
        test_data["lang"]
    )

    # 3. Compare (excluding internal helper fields)
    fields_to_compare = [
        "input_datetime", "timezone", "address", "sunrise", "sunset", 
        "samvatsara", "saka_year", "masa", "paksha", "tithi", "vara", 
        "nakshatra", "yoga", "karana", "rashi", "lagna", "next_birthday"
    ]

    mismatches = []
    for field in fields_to_compare:
        legacy_val = legacy_output.get(field)
        new_val = new_output.get(field)
        if legacy_val != new_val:
            mismatches.append(f"Field '{field}':\n  Legacy: {legacy_val}\n  New:    {new_val}")

    if not mismatches:
        print("✅ SUCCESS: Outputs are 100% identical!")
        return True
    else:
        print("❌ FAILED: Mismatches detected!")
        for m in mismatches:
            print(m)
        return False

if __name__ == "__main__":
    if test_parity():
        sys.exit(0)
    else:
        sys.exit(1)
