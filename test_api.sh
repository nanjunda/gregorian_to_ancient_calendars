#!/bin/bash
# test_api.sh - Helper script to verify Ancient Calendars v2.1 API

echo "------------------------------------------------"
echo "Ancient Calendars v2.1 - Backend API Test Suite"
echo "------------------------------------------------"

# 1. Test Mayan Calculation
echo -e "\n[1] Testing Mayan Calculation (2026-01-20)..."
curl -s -X POST http://127.0.0.1:5080/api/v2/calculate \
-H "Content-Type: application/json" \
-d '{
  "calendar": "mayan",
  "date": "2026-01-20",
  "time": "12:00",
  "location": "London, UK"
}' | python3 -m json.tool

# 2. Test Mayan iCal (Recurrence Engine)
echo -e "\n[2] Testing Mayan iCal Generation (Ancient Birthdays)..."
curl -s -X POST http://127.0.0.1:5080/api/generate-ical \
-H "Content-Type: application/json" \
-d '{
  "calendar": "mayan",
  "date": "2026-01-20",
  "time": "12:00",
  "location": "London, UK"
}' --output my_mayan_test.ics

if [ -f "my_mayan_test.ics" ]; then
    echo "✅ iCal generated successfully: my_mayan_test.ics"
else
    echo "❌ iCal generation failed."
fi

# 3. Test Zero Mutation (Hindu Panchanga)
echo -e "\n[3] Verifying Zero Mutation (Hindu Panchanga)..."
curl -s -X POST http://127.0.0.1:5080/api/v2/calculate \
-H "Content-Type: application/json" \
-d '{
  "calendar": "panchanga",
  "date": "2026-01-20",
  "time": "12:00",
  "location": "London, UK"
}' | python3 -m json.tool

echo -e "\n------------------------------------------------"
echo "Verification Complete."
