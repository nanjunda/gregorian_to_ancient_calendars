# Walkthrough: Remote Repository & Cloud Package

I have successfully set up the remote repository on your GitHub account and prepared the standalone installation package for your Linux VM.

## 1. Remote Repository Setup
The project is now hosted on GitHub:
- **URL**: [https://github.com/nanjunda/gregorian_to_hindu_calendar](https://github.com/nanjunda/gregorian_to_hindu_calendar)
- **Status**: Private Repository
- **Last Push**: Includes all v3.0 features (Multi-language, Nakshatra Padas) and Cloud Deployment artifacts.

## 2. Standalone Installation Package
I have created a compressed bundle for offline or direct transfer to a cloud VM:
- **File**: `panchanga_v3_install.tar.gz`
- **Location**: `/Users/nanjundasomayaji/dev/gregorian_to_hindu_calendar/panchanga_v3_install.tar.gz`

## 3. How to Install on Cloud VM (AWS/GCP/Oracle)
### Option A: Via Git (Recommended)
1. SSH into your VM.
2. Run:
```bash
git clone https://github.com/nanjunda/gregorian_to_hindu_calendar.git
cd gregorian_to_hindu_calendar
chmod +x deploy.sh
./deploy.sh
```

### Option B: Via Package (No-Git)
1. Transfer `panchanga_v3_install.tar.gz` to your VM (using `scp` or `sftp`).
2. Run:
```bash
tar -xzf panchanga_v3_install.tar.gz
cd gregorian_to_hindu_calendar
chmod +x deploy.sh
./deploy.sh
```

## Verification
The `deploy.sh` script has been updated to automatically install Python, Nginx, and Systemd services on any standard Ubuntu/Debian VM.
