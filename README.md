# Gregorian to Ancient Calendars v2.0 (Headless Edition)

A high-precision tool to convert **any Gregorian event** into its Traditional Panchanga equivalent, featuring high-fidelity cosmic visualizations, interactive educational modules, and an AI-powered "Astro-Tutor."

### v2.0 Architectural Pillars
- **Headless Design:** Completely decoupled UI and Application Logic for multi-device support.
- **Framework Agnostic:** Core logic is independent of Flask, enabling deployment on generic servers (Apache/Nginx).
- **Multi-Civilization Hub:** Standardized engine interface to support Panchanga, Mayan, and Chinese calendars.
- **Scientific Masterclass (AI 2.0):** Configurable AI engines (OpenRouter default) for age-appropriate, science-only insights.
- **3D Celestial Modules:** Interactive visual units optimized for various device form factors.
- **iCal Precision:** Location-aware traditional date recurring calculation and export.

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
