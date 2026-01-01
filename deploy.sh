#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v3.0 Native Deployment..."

APP_NAME="panchanga"
APP_PATH=$(pwd)
CURRENT_USER=$(whoami)

# 1. Update system and install dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git curl

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
    -e "s|{{APP_PATH}}|$APP_PATH|g" \
    panchanga.service.template | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# 4. Configure Nginx
echo "🌐 Configuring Nginx..."
# Use localhost or server IP if no domain provided
PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")

sed -e "s|{{DOMAIN_OR_IP}}|$PUBLIC_IP|g" \
    -e "s|{{APP_PATH}}|$APP_PATH|g" \
    panchanga.nginx.template | sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null

sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "🎉 Deployment complete!"
echo "App should be accessible at: http://$PUBLIC_IP"
