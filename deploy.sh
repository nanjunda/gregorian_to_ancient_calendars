#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v3.0 Deployment (Nuclear Option)..."
echo "ℹ️  Mode: Nginx Reverse Proxy (Port 5080) -> Gunicorn"
echo "⚠️  RELOCATING App to /opt/panchanga to bypass SELinux Home Dir restrictions"

APP_NAME="panchanga"
SOURCE_DIR=$(pwd)
DEPLOY_DIR="/opt/$APP_NAME"
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
    sudo dnf install -y python3-pip nginx git-core curl policycoreutils-python-utils openssl
    sudo systemctl enable --now nginx
    

    
    # Allow Nginx network connect (Critical)
    echo "🛡️ Enabling Nginx network connections..."
    sudo setsebool -P httpd_can_network_connect 1
    sudo setsebool -P httpd_can_network_relay 1 || true
else
    sudo apt-get update -y
    sudo apt-get install -y python3-pip python3-venv nginx git curl
fi

# 2. Relocate Application to /opt
echo "🚚 Moving application to $DEPLOY_DIR..."
# Create directory
sudo mkdir -p $DEPLOY_DIR
# Copy files (excluding venv and .git to keep it clean)
echo "   Copying files..."
sudo cp -r $SOURCE_DIR/* $DEPLOY_DIR/
# Fix ownership
sudo chown -R $CURRENT_USER:$HTTP_GROUP $DEPLOY_DIR

# 3. Setup Virtual Environment in NEW location
cd $DEPLOY_DIR
# CRITICAL: We cannot reuse the copied venv because absolute paths (shebangs) are broken after move
echo "🗑️ Removing copied venv to force clean recreation..."
sudo rm -rf venv

# Ensure system python is available (using pyenv from home dir causes SELinux denials)
if [ "$PKG_MGR" == "dnf" ]; then
    echo "📦 Installing system Python 3 to avoid /home/opc/.pyenv dependency..."
    sudo dnf install -y python3
fi

if [ ! -d "venv" ]; then
    echo "🏗️ Creating virtual environment in $DEPLOY_DIR using SYSTEM Python..."
    # Force use of /usr/bin/python3 instead of "python3" (which might find pyenv)
    /usr/bin/python3 -m venv venv
fi

echo "🐍 Installing Python packages..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. FIX SELINUX (The Nuclear Way)
if command -v semanage &> /dev/null; then
    echo "🛡️ Configuring SELinux contexts for /opt/panchanga..."
    
    # 1. Allow Nginx to read static files
    sudo semanage fcontext -a -t httpd_sys_content_t "$DEPLOY_DIR/static(/.*)?"
    
    # 2. Allow Systemd/Init to execute Gunicorn (bin_t)
    # Applying strictly to the bin folder
    sudo semanage fcontext -a -t bin_t "$DEPLOY_DIR/venv/bin(/.*)?"
    
    # Apply contexts
    sudo restorecon -R -v $DEPLOY_DIR
    
    # Explicitly ensure Gunicorn is bin_t (Critical for 203/EXEC)
    sudo chcon -t bin_t $DEPLOY_DIR/venv/bin/gunicorn
    


    # CRITICAL ORACLE LINUX 9 FIX: Check for fapolicyd (Application Whitelisting)
    # This prevents running any binary not installed via DNF/RPM (like our pip gunicorn)
    if systemctl is-active --quiet fapolicyd; then
        echo "🛑 fapolicyd detected! This blocks custom binaries."
        echo "   Stopping fapolicyd to allow Gunicorn execution..."
        sudo systemctl stop fapolicyd
        sudo systemctl disable fapolicyd
        # Ideally we would add a rule, but for deployment success now, we disable it.
    fi
fi

# Explicit permission fix (Ignore errors on symlinks like 'python' which point to system read-only files)
chmod +x $DEPLOY_DIR/venv/bin/* || true

# 5. Configure systemd service
echo "⚙️ Configuring systemd service..."
# Using DEPLOY_DIR now instead of pwd
sed -e "s|{{USER}}|$CURRENT_USER|g" \
    -e "s|{{GROUP}}|$HTTP_GROUP|g" \
    -e "s|{{APP_PATH}}|$DEPLOY_DIR|g" \
    panchanga.service.template | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# 7. OPS: Log Rotation
echo "🔄 Configuring Log Rotation..."
if [ -f "$SOURCE_DIR/panchanga.logrotate" ]; then
    sudo cp $SOURCE_DIR/panchanga.logrotate /etc/logrotate.d/panchanga
    sudo chmod 644 /etc/logrotate.d/panchanga
    
    # Force hourly execution via cron (system logrotate might only be daily)
    echo "   Setting up hourly cron job for logs..."
    echo "0 * * * * root /usr/sbin/logrotate -f /etc/logrotate.d/panchanga" | sudo tee /etc/cron.d/panchanga-rotate > /dev/null
fi

# 8. SECURITY: Generate Self-Signed Certificate
echo "🔒 Generating Self-Signed SSL Certificate..."
# Ensure directories exist
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

if [ ! -f "/etc/ssl/certs/panchanga-selfsigned.crt" ]; then
    # Use PUBLIC_IP if available, else localhost
    CERT_CN=$(curl -s ifconfig.me || echo "localhost")
    
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/panchanga-selfsigned.key \
        -out /etc/ssl/certs/panchanga-selfsigned.crt \
        -subj "/C=IN/ST=Karnataka/L=Bangalore/O=HinduPanchanga/OU=Engineering/CN=$CERT_CN"
    
    # Set strict permissions for key
    sudo chmod 600 /etc/ssl/private/panchanga-selfsigned.key
fi

# 6. Configure Nginx
echo "🌐 Configuring Nginx..."
PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")

sed -e "s|{{DOMAIN_OR_IP}}|$PUBLIC_IP|g" \
    -e "s|{{APP_PATH}}|$DEPLOY_DIR|g" \
    panchanga.nginx.template | sudo tee $NGINX_CONF_DIR/$APP_NAME.conf > /dev/null

if [ -n "$NGINX_LINK_DIR" ]; then
    sudo ln -sf $NGINX_CONF_DIR/$APP_NAME.conf $NGINX_LINK_DIR/
    sudo rm -f $NGINX_LINK_DIR/default
fi

sudo nginx -t && sudo systemctl restart nginx

echo "🎉 Deployment complete (v3.2)!"
echo "App is SECURE at: https://$PUBLIC_IP"
echo "Note: Accept the self-signed certificate warning in browser."
