#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Gregorian to Ancient Calendars v1.0 Deployment..."
echo "ℹ️  Mode: Nginx Reverse Proxy (Port 5080) -> Gunicorn"
echo "⚠️  RELOCATING App to /opt/ancient_calendars for SELinux stability"

APP_NAME="ancient_calendars"
SOURCE_DIR=$(pwd)
DEPLOY_DIR="/opt/$APP_NAME"
CURRENT_USER=${SUDO_USER:-$(whoami)}

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

# 1. Install system dependencies
echo "📦 Installing system dependencies..."
if [ "$PKG_MGR" == "dnf" ]; then
    sudo dnf install -y python3-pip python3-devel nginx git-core curl policycoreutils-python-utils openssl \
        libX11 libXext libXrender freetype libpng rsync
    sudo systemctl enable --now nginx
    
    # Allow Nginx network connect (Critical for 502 fix)
    echo "🛡️ Enabling Nginx network connections..."
    sudo setsebool -P httpd_can_network_connect 1
    sudo setsebool -P httpd_can_network_relay 1 || true
    sudo setsebool -P httpd_unified 1 || true

    # Open Firewall Port (Security Port 58921)
    if command -v firewall-cmd &> /dev/null; then
        echo "🔥 Opening Firewall Port 58921..."
        sudo firewall-cmd --permanent --add-port=58921/tcp
        sudo firewall-cmd --reload
    fi
    
    # Explicitly whitelist port 8000 for SELinux
    echo "🛡️ Whitelisting port 8000 for backend..."
    sudo semanage port -m -t http_port_t -p tcp 8000 || sudo semanage port -a -t http_port_t -p tcp 8000 || true
else
    sudo apt-get install -y python3-pip python3-venv nginx git curl rsync openssl
fi

# 1.5 Generate Self-Signed SSL Certificate (required for Nginx)
echo "🔐 Generating Self-Signed SSL Certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/ancient_calendars-selfsigned.key \
    -out /etc/ssl/certs/ancient_calendars-selfsigned.crt \
    -subj "/C=IN/ST=Karnataka/L=Bangalore/O=AstroTutor/OU=Education/CN=ancient_calendars.local"

# 2. Relocate Application to /opt
echo "🚚 Moving application to $DEPLOY_DIR..."
sudo mkdir -p $DEPLOY_DIR
# Use rsync for clean copy
sudo rsync -av --exclude='venv' --exclude='.git' --exclude='__pycache__' "$SOURCE_DIR/" "$DEPLOY_DIR/"

# 3. Handle Google API Key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY is not set."
    read -p "🔑 Please enter your Google Gemini API Key: " GOOGLE_API_KEY
fi

# 4. Setup Virtual Environment (Always Fresh)
cd $DEPLOY_DIR
echo "🗑️  Clearing old virtual environment..."
sudo rm -rf venv

echo "🏗️  Creating fresh virtual environment..."
sudo /usr/bin/python3 -m venv venv

echo "🐍 Installing Python packages..."
# We use sudo -u $CURRENT_USER to ensure the venv belongs to the real user
sudo -u $CURRENT_USER ./venv/bin/pip install --upgrade pip
sudo -u $CURRENT_USER ./venv/bin/pip install -r requirements.txt

# 5. Pre-launch Syntax Check (v5.6.1)
echo "🔍 Validating code integrity..."
if ! sudo -u $CURRENT_USER ./venv/bin/python3 -m py_compile $DEPLOY_DIR/app.py $DEPLOY_DIR/utils/ai_engine.py; then
    echo "❌ CRITICAL ERROR: Syntax error detected in the code!"
    echo "   Check the output above for the specific line number."
    exit 1
fi
echo "🛰️  Pre-downloading astronomical data files..."
sudo -u $CURRENT_USER ./venv/bin/python3 -c "from skyfield.api import load; load('de421.bsp'); load.timescale()"

# 6. FIX PERMISSIONS (Layered Strategy)
echo "🔒 Applying Layered Permission Strategy..."
# Phase 1: Reset all to standard readable
sudo chown -R $CURRENT_USER:$HTTP_GROUP $DEPLOY_DIR
sudo find $DEPLOY_DIR -type d -exec chmod 755 {} +
sudo find $DEPLOY_DIR -type f -exec chmod 644 {} +

# Phase 2: RESTORE Execution exactly where needed
echo "⚡ Restoring execution bits to binaries..."
sudo chmod +x $DEPLOY_DIR/venv/bin/*
sudo chmod -R +x $DEPLOY_DIR/scripts 2>/dev/null || true

# 7. FIX SELINUX (The Nuclear Way)
if command -v semanage &> /dev/null; then
    echo "🛡️  Configuring SELinux labels..."
    sudo semanage fcontext -a -t httpd_sys_content_t "$DEPLOY_DIR/static(/.*)?"
    sudo semanage fcontext -a -t bin_t "$DEPLOY_DIR/venv/bin(/.*)?"
    sudo restorecon -R -v $DEPLOY_DIR
    sudo chcon -t bin_t $DEPLOY_DIR/venv/bin/gunicorn || true
    
    # Application Whitelisting (Oracle Linux 9)
    if systemctl is-active --quiet fapolicyd; then
        echo "🛑 Disabling fapolicyd to allow custom binaries..."
        sudo systemctl stop fapolicyd
        sudo systemctl disable fapolicyd
    fi
fi

# 8. Configure systemd service
echo "⚙️  Configuring systemd service..."
sed -e "s|{{USER}}|$CURRENT_USER|g" \
    -e "s|{{GROUP}}|$HTTP_GROUP|g" \
    -e "s|{{APP_PATH}}|$DEPLOY_DIR|g" \
    -e "s|{{GOOGLE_API_KEY}}|$GOOGLE_API_KEY|g" \
    $DEPLOY_DIR/ancient_calendars.service.template | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# 9. Configure Nginx
echo "🌐 Configuring Nginx..."
PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
sed -e "s|{{DOMAIN_OR_IP}}|$PUBLIC_IP|g" \
    -e "s|{{APP_PATH}}|$DEPLOY_DIR|g" \
    $DEPLOY_DIR/ancient_calendars.nginx.template | sudo tee $NGINX_CONF_DIR/$APP_NAME.conf > /dev/null

if [ -n "$NGINX_LINK_DIR" ]; then
    sudo ln -sf $NGINX_CONF_DIR/$APP_NAME.conf $NGINX_LINK_DIR/
fi
sudo nginx -t && sudo systemctl restart nginx

# 10. Self-Diagnostic
echo "================================================================="
echo "🕵️  Self-Diagnostic: Checking Service Health..."
sleep 5
if systemctl is-active --quiet $APP_NAME; then
    echo "   ✅ Gunicorn Service is RUNNING."
    if curl -s -I http://127.0.0.1:8000 | grep -q "200 OK\|302 Found\|301 Moved"; then
        echo "   ✅ Backend is RESPONDING."
    else
        echo "   ⚠️  Backend is NOT responding. Check logs: journalctl -u $APP_NAME"
    fi
else
    echo "   ❌ ERROR: Gunicorn failed to start."
fi

if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is RUNNING."
else
    echo "   ❌ ERROR: Nginx failed to start."
fi
echo "================================================================="
echo "🎉 SUCCESS! Access at: https://$PUBLIC_IP:58921"
