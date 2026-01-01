# Hindu Panchanga Converter v3.0

A high-precision tool to convert Gregorian calendar dates into traditional Hindu Panchanga elements.

## Features
- **Version 3.0 (New):**
    - **Multi-language Support:** English (EN), Kannada (KN), and Sanskrit (SA).
    - **Nakshatra Padas:** Detailed calculation of the 4 padas for each Nakshatra.
    - **Cloud Deployment:** Ready-to-use Docker and `deploy.sh` for Linux VMs.
- **Version 2.0:**
    - **Vedic Recurrence:** Generate calendar events that recur based on Masa, Paksha, and Tithi.
    - **iCal Export:** Download a 20-year `.ics` file.
- **Web UI:** Modern Glassmorphism interface.
- **High Precision:** Uses `skyfield` (DE440/DE421) and Lahiri Ayanamsha.

## Installation & Deployment

### Local Development
1. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run:** `python3 app.py`

### Cloud Deployment (Linux VM)
Simply run the deployment script:
```bash
curl -sSL https://raw.githubusercontent.com/nanjundasomayaji/gregorian_to_hindu_calendar/main/deploy.sh | bash
```
Or manually using Docker:
```bash
docker-compose up --build -d
```

## Documentation
Refer to the `docs/` directory for detailed architecture and implementation plans.
