#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v3.0 Native Deployment..."

APP_NAME="panchanga"
APP_PATH=$(pwd)
CURRENT_USER=$(whoami)

# Detect Package Manager
if command -v apt-get &> /dev/null; then
    PKG_MGR="apt-get"
    HTTP_GROUP="www-data"
    NGINX_CONF_DIR="/etc/nginx/sites-available"
    NGINX_LINK_DIR="/etc/nginx/sites-enabled"
elif command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    HTTP_GROUP="nginx"
    NGINX_CONF_DIR="/etc/nginx/conf.d"
    NGINX_LINK_DIR="" # RHEL usually reads directly from conf.d
else
    echo "❌ Unsupported package manager. Please install manually."
    exit 1
fi

echo "📦 Detected package manager: $PKG_MGR"

# 1. Install dependencies
echo "📦 Installing system dependencies..."
if [ "$PKG_MGR" == "apt-get" ]; then
    sudo apt-get update -y
    sudo apt-get install -y python3-pip python3-venv nginx git curl
else
    sudo dnf install -y python3-pip nginx git-core curl
    sudo systemctl enable --now nginx
    # Open firewall for Oracle Linux
    if command -v firewall-cmd &> /dev/null; then
        echo "🔥 Opening firewall port 5080..."
        sudo firewall-cmd --permanent --add-port=5080/tcp
        sudo firewall-cmd --reload
    fi
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

echo "🎉 Deployment complete!"
echo "App should be accessible at: http://$PUBLIC_IP:5080"
