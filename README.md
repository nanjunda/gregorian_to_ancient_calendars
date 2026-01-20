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
2. **Run:** `python3 gateway.py`

### Accessing the Application
Once the script finishes, it will print your public IP. You can access the application at:
`http://localhost:5080` (or your VM IP)

### Cloud Deployment (Native Linux VM)
Simply run the bootstrap script on your VM (Oracle Linux 9 / RHEL recommended):
```bash
git clone https://github.com/nanjunda/gregorian_to_ancient_calendars.git
cd gregorian_to_ancient_calendars
sudo bash ./deploy.sh
```

### MAINTAINING v2.0
To quickly refresh your live application:
```bash
sudo bash ./deploy.sh
```
The `deploy.sh` script is optimized to handle SELinux transitions and fresh environment setups for Oracle Linux 9.

## Documentation
Refer to the `docs/` directory for detailed architecture and implementation plans.
