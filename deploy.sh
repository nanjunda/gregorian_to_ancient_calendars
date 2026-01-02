#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v3.0 Deployment (Nginx Enabled)..."
echo "ℹ️  Mode: Nginx Reverse Proxy (Port 5080) -> Gunicorn (Internal 8000)"

APP_NAME="panchanga"
APP_PATH=$(pwd)
CURRENT_USER=$(whoami)

# Detect Package Manager
if command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    HTTP_GROUP="nginx"
    NGINX_CONF_DIR="/etc/nginx/conf.d"
    NGINX_LINK_DIR="" 
elif command -v apt-get &> /dev/null; then
    PKG_MGR="apt-get"
    HTTP_GROUP="www-data"
    NGINX_CONF_DIR="/etc/nginx/sites-available"
    NGINX_LINK_DIR="/etc/nginx/sites-enabled"
else
    echo "❌ Unsupported package manager. Please install manually."
    exit 1
fi

echo "📦 Detected package manager: $PKG_MGR"

# 1. Install dependencies
echo "📦 Installing system dependencies..."
if [ "$PKG_MGR" == "dnf" ]; then
    sudo dnf install -y python3-pip nginx git-core curl
    sudo systemctl enable --now nginx
    
    # Open firewall for Oracle Linux
    if command -v firewall-cmd &> /dev/null; then
        echo "🔥 Opening firewall port 5080..."
        sudo firewall-cmd --permanent --add-port=5080/tcp
        sudo firewall-cmd --reload
    fi
    
    # Allow Nginx to bind to custom port 5080 (SELinux)
    if command -v semanage &> /dev/null; then
        echo "🛡️ Configuring SELinux for port 5080..."
        sudo semanage port -a -t http_port_t -p tcp 5080 || true
    elif command -v setsebool &> /dev/null; then
        # Fallback: Allow Nginx to bind to any port if semanage is missing
        sudo setsebool -P httpd_run_stickshift 1 || true 
        sudo setsebool -P httpd_can_network_connect 1 || true
    fi
else
    sudo apt-get update -y
    sudo apt-get install -y python3-pip python3-venv nginx git curl
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "🏗️ Creating virtual environment..."
    python3 -m venv venv
fi

echo "🐍 Installing Python packages..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Configure systemd service
echo "⚙️ Configuring systemd service..."
sed -e "s|{{USER}}|$CURRENT_USER|g" \
    -e "s|{{GROUP}}|$HTTP_GROUP|g" \
    -e "s|{{APP_PATH}}|$APP_PATH|g" \
    panchanga.service.template | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# 4. Configure Nginx
echo "🌐 Configuring Nginx..."
PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")

sed -e "s|{{DOMAIN_OR_IP}}|$PUBLIC_IP|g" \
    -e "s|{{APP_PATH}}|$APP_PATH|g" \
    panchanga.nginx.template | sudo tee $NGINX_CONF_DIR/$APP_NAME.conf > /dev/null

if [ -n "$NGINX_LINK_DIR" ]; then
    sudo ln -sf $NGINX_CONF_DIR/$APP_NAME.conf $NGINX_LINK_DIR/
    sudo rm -f $NGINX_LINK_DIR/default
fi

sudo nginx -t && sudo systemctl restart nginx
# Fix permissions for Nginx access
echo "🔓 Fixing Nginx permissions..."
# Allow Nginx to traverse home directory (required if app is in /home/user)
chmod 711 /home/$CURRENT_USER

# Set group ownership
sudo chown -R $CURRENT_USER:$HTTP_GROUP $APP_PATH/static
sudo chmod -R 755 $APP_PATH/static

# Fix SELinux Context for Static Files (Critical for Oracle Linux)
if command -v chcon &> /dev/null; then
    echo "🛡️ applying SELinux context to static files..."
    sudo chcon -R -t httpd_sys_content_t $APP_PATH/static
    
    # CRITICAL: Allow Nginx to talk to Gunicorn on localhost:8000
    echo "🛡️ Enabling Nginx network connections..."
    sudo setsebool -P httpd_can_network_connect 1
    sudo setsebool -P httpd_can_network_relay 1 || true
    # Allow services to run in home directories
    sudo setsebool -P httpd_enable_homedirs 1 || true

    # Fix Gunicorn Execution from Systemd
    echo "🛡️ Fixing venv permissions and SELinux context..."
    chmod +x $APP_PATH/venv/bin/*
    sudo chcon -R -t bin_t $APP_PATH/venv
fi

echo "🎉 Deployment complete!"
echo "App should be accessible at: http://$PUBLIC_IP:5080"
