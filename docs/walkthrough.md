# Walkthrough: Nginx-Enabled Cloud Deployment (Branch: feature/nginx-enable)

This branch enables **Nginx** as a reverse proxy for enhanced security and static file performance.

## Deployment Workflow

```mermaid
graph TD
    User["User Browser (Port 5080)"] -->|HTTP Request| Nginx["Nginx (Reverse Proxy)"]
    
    subgraph "Cloud VM (Oracle Linux 9)"
        Nginx -->|Proxy Pass| Socket["TCP Socket (127.0.0.1:8000)"]
        Socket -->|WSGI Protocol| Gunicorn["Gunicorn (App Server)"]
        Gunicorn -->|Python Code| Flask["Flask Application"]
        Flask -->|Calculations| Ephemeris["Astronomical Data (de421.bsp)"]
        
        Nginx -->|Static Serving| Static["Static Assets (/static)"]
    end
    
    Static -.->|CSS/JS/Images| User
    Flask -.->|HTML/JSON Response| User
```

## How it works
1. **Nginx** listens on public port **5080**.
2. It serves static files (CSS/JS) directly for speed.
3. It forwards app requests to **Gunicorn** on internal port `8000`.

## Installation
Run these commands on your VM:
```bash
git fetch origin
git checkout feature/nginx-enable
git pull origin feature/nginx-enable
chmod +x deploy.sh
./deploy.sh
```
