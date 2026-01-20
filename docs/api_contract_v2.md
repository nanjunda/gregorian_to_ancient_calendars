# Ancient Calendars v2.0: JSON API Contract (Draft)

This document defines the stable interface between the Headless Logic Hub and any Presentation Client (Web, Mobile, etc.).

## Base URL: `/api/v2`

### POST `/api/v2/calculate`
Calculates calendar data for a specific moment and location.

**Request Body:**
```json
{
  "calendar": "panchanga",        // options: panchanga, mayan, chinese
  "date": "2026-01-19",
  "time": "18:30",
  "location": "Bangalore, India",
  "lang": "EN",
  "client_profile": {
    "form_factor": "mobile",      // options: desktop, mobile, watch
    "capabilities": ["audio", "webgl"]
  }
}
```

**Response Body:**
```json
{
  "status": "success",
  "metadata": {
    "civilization": "panchanga",
    "engine_version": "1.0",
    "timestamp_utc": "2026-01-19T13:00:00Z",
    "render_hints": ["zodiac_comparison", "moon_phase"]
  },
  "results": {
    "civilization_specific": {
       "samvatsara": "Anal",
       "masa": "Magha",
       "paksha": "Shukla",
       "tithi": "Dwitiya",
       "vara": "Somavara",
       "nakshatra": "Shravana",
       "yoga": "Vyatipata",
       "karana": "Bava"
    },
    "coordinates": {
       "rashi": { "name": "Makara", "code": "Cp" },
       "lagna": { "name": "Karkata", "code": "Cn" }
    },
    "astronomy": {
       "sunrise": "06:45:00",
       "sunset": "18:12:00",
       "moon_longitude": 284.5,
       "sun_longitude": 275.2,
       "angular_separation": 9.3
    }
  },
  "visuals": {
    "sky_shot_base64": "...",
    "solar_system_base64": "..."
  },
  "education": {
    "summary": "Today marks the alignment of...",
    "report_markdown": "# Cosmic Alignment Report...",
    "audio_summary_url": "..."
  }
}
```

## Guarantees:
1. **Stability**: Fields in `results.civilization_specific` will not change for a given calendar type.
2. **Extensibility**: Engines may add new fields to `astronomy` or `results` without breaking the structure.
3. **Headless**: No HTML strings should ever be returned in the `results` object.
