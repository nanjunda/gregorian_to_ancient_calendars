import sys
import os
from datetime import datetime
import json
import traceback

# Add project root to path
sys.path.append(os.getcwd())

from app import app
from engines.panchanga.engine import PanchangaEngine

TEST_SCENARIOS = [
    # 1. Standard Case
    {"date": "2026-01-20", "time": "12:00", "location": "Bangalore, India", "lang": "EN", "desc": "Standard Bangalore"},
    
    # 2. Languages
    {"date": "2026-01-20", "time": "18:30", "location": "Bangalore, India", "lang": "KN", "desc": "Kannada Language Support"},
    {"date": "2026-01-20", "time": "09:00", "location": "Bangalore, India", "lang": "SA", "desc": "Sanskrit Language Support"},
    
    # 3. DST Transitions (NYC Spring Forward/Fall Back)
    {"date": "2026-03-08", "time": "02:30", "location": "New York, USA", "lang": "EN", "desc": "NYC DST Start Transition"},
    {"date": "2026-11-01", "time": "01:30", "location": "New York, USA", "lang": "EN", "desc": "NYC DST End Transition"},
    
    # 4. Leap Year
    {"date": "2024-02-29", "time": "12:00", "location": "London, UK", "lang": "EN", "desc": "Leap Year Entry"},
    
    # 5. Extreme Latitudes (Polar effects on sunrise/sunset)
    {"date": "2026-06-21", "time": "12:00", "location": "Reykjavik, Iceland", "desc": "Summer Solstice (High Lat)"},
    {"date": "2026-12-21", "time": "12:00", "location": "Ushuaia, Argentina", "desc": "Winter Solstice (Southern Hem)"},
    
    # 6. Year Boundaries
    {"date": "2025-12-31", "time": "23:59", "location": "Tokyo, Japan", "desc": "NYE Boundary Case"},
    {"date": "2026-01-01", "time": "00:01", "location": "San Francisco, USA", "desc": "New Year Boundary Case"},
]

def run_stress_test():
    print(f"🚀 Starting Exhaustive Parity Stress Test ({len(TEST_SCENARIOS)} scenarios)...")
    engine = PanchangaEngine()
    client = app.test_client()
    
    total_mismatches = 0
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        desc = scenario.get("desc", f"Scenario {i}")
        print(f"\n[{i}/{len(TEST_SCENARIOS)}] Testing: {desc}...")
        
        try:
            # 1. Legacy Run
            resp = client.post('/api/panchanga', json=scenario)
            if resp.status_code != 200:
                print(f"  ❌ Legacy Route Failed: {resp.status_code}")
                total_mismatches += 1
                continue
            legacy_data = resp.get_json()["data"]

            # 2. Modular Run
            new_data = engine.calculate_data(
                scenario["date"], 
                scenario["time"], 
                scenario["location"], 
                scenario.get("lang", "EN")
            )

            # 3. Compare Core Fields
            fields = [
                "input_datetime", "timezone", "address", "samvatsara", 
                "masa", "paksha", "tithi", "vara", "nakshatra", "yoga", 
                "karana", "rashi", "lagna", "next_birthday"
            ]
            
            case_mismatches = []
            for f in fields:
                l_v = legacy_data.get(f)
                n_v = new_data.get(f)
                if l_v != n_v:
                    case_mismatches.append(f"{f}: '{l_v}' != '{n_v}'")
            
            if not case_mismatches:
                print("  ✅ 100% Identical")
            else:
                print("  ❌ MISMATCH FOUND:")
                for m in case_mismatches:
                    print(f"    - {m}")
                total_mismatches += 1
                
        except Exception as e:
            print(f"  🔥 CRASH in test: {str(e)}")
            traceback.print_exc()
            total_mismatches += 1

    print("\n" + "="*40)
    if total_mismatches == 0:
        print("🎉 ALL STRESS TESTS PASSED! Zero Mutation Confirmed.")
        return True
    else:
        print(f"🚫 FAILED: {total_mismatches} scenarios had discrepancies.")
        return False

if __name__ == "__main__":
    success = run_stress_test()
    sys.exit(0 if success else 1)
