# Hindu Panchanga Converter v4.2 (Interactive Education)

A high-precision tool to convert **any Gregorian event** into its traditional Vedic equivalent, featuring high-fidelity cosmic visualizations and interactive educational modules.

## Features
- **Version 4.2 (Interactive Education):**
    - **Interactive 3D Modules:** "Zodiac Stadium", "Precession Top", and "Lunar Nodes" allow students to explore cosmic mechanics.
    - **Hybrid Visualizations:** "Cosmic Alignment" (Heliocentric) and "Celestial Perspective" (Geocentric).
    - **Universal Event Support:** Generic engine designed for Birthdays, Festivals, or historical dates.
    - **Privacy First:** "Stealth Mode" generates base64 images, ensuring no user PII is stored on disk.
- **core Engine:**
    - **Vedic Recurrence:** Finds "Next Occurrence" for any event based on Masa, Paksha, and Tithi.
    - **iCal Export:** One-click download for the next 20 occurrences (.ics).
    - **Precision:** Uses `skyfield` and Lahiri Ayanamsha for sub-arcsecond accuracy.
- **Web UI:** Premium Glassmorphism interface with "Astronomical Insights" educational section.

## Installation & Deployment

### Local Development
1. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run:** `python3 app.py`

### Accessing the Application
Once the script finishes, it will print your public IP. You can access the application at:
`http://<your-vm-ip>:5080`

### Cloud Deployment (Native Linux VM)
Simply run the deployment script on your VM (Ubuntu/Debian recommended):
```bash
git clone https://github.com/nanjundasomayaji/gregorian_to_hindu_calendar.git
cd gregorian_to_hindu_calendar
chmod +x deploy.sh
./deploy.sh
```
The script will automatically:
1. Install Python, Nginx, and system dependencies.
2. Setup a virtual environment and install packages.
3. Configure Gunicorn to run as a systemd service.
4. Setup Nginx as a reverse proxy on port 80.

## Documentation
Refer to the `docs/` directory for detailed architecture and implementation plans.
