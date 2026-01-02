# Version 3.0: Direct Cloud Deployment (Non-Docker)

The user wants to deploy the Hindu Panchanga Converter v3.0 directly on a cloud-based Linux VM (e.g., Ubuntu/Debian on AWS/GCP/OCI) without using Docker.

## Proposed Changes

### Deployment Script [UPDATE]
- **deploy.sh**: Modify to support a "native" installation.
    - Install system dependencies (Python, Nginx, Git).
    - Setup Python virtual environment.
    - Install package dependencies from `requirements.txt`.
    - Configure Gunicorn to run as a systemd service.
    - Configure Nginx as a reverse proxy.

### System Configuration [NEW]
- **panchanga.service**: A systemd unit file to manage the Gunicorn process.
- **panchanga.nginx**: An Nginx site configuration to handle incoming traffic on port 80.

### Documentation
- Update `README.md` to provide clear instructions for this native deployment method.

## Verification Plan

### Manual Verification
- Review the `deploy.sh` script logic for correctness on standard Ubuntu/Debian environments.
- Ensure the systemd and Nginx templates use relative/configurable paths where possible (or standardize on `/home/$USER/panchanga`).
