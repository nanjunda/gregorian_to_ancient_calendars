# Gregorian to Ancient Calendars v1.0 (Constellation Hub)

A high-precision tool to convert **any Gregorian event** into its Traditional Panchanga equivalent, featuring high-fidelity cosmic visualizations, interactive educational modules, and an AI-powered "Astro-Tutor."

### Key Features (V6.0)
- **High-Precision Converter:** Handles events from 1900 to 2100 with location-aware precision.
- **Scientific Masterclass (AI):** Multi-phase technical deconstructions of orbital mechanics.
- **Universal Context:** Explains the "Great Drift" (Precession) and "Birthday Drift" (Lunar-Solar gap).
- **3D Celestial Modules:** Interactive Zodiac Comparison, Moon Phase Protractor, and Precession Wobble.
- **Interactive Engagement:** Maestro's Challenge (Quizzes) and Birthday Time-Machine (100-year drift).
- **iCal Integration:** Generate recurring Traditional dates for 20 years.
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
Simply run the bootstrap script on your VM (Oracle Linux 9 / RHEL recommended):
```bash
git clone https://github.com/nanjunda/gregorian_to_ancient_calendars.git
cd gregorian_to_ancient_calendars
sudo bash ./deploy.sh
```

### MAINTENANCE: Pulling Updates
To quickly update your live application to the latest version:
```bash
cd ~/gregorian_to_ancient_calendars
chmod +x update_app.sh
./update_app.sh
```
This "Hybrid Sync" workflow uses `rsync` to preserve SELinux labels and optimizes the update process to take less than 10 seconds.

## Documentation
Refer to the `docs/` directory for detailed architecture and implementation plans.
