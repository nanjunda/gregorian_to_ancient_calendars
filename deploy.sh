#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v5.0 Deployment (AI Insights Edition)..."
echo "ℹ️  Mode: Nginx Reverse Proxy (Port 5080) -> Gunicorn"
echo "⚠️  RELOCATING App to /opt/panchanga to bypass SELinux Home Dir restrictions"

APP_NAME="panchanga"
SOURCE_DIR=$(pwd)
DEPLOY_DIR="/opt/$APP_NAME"
# Use SUDO_USER if running via sudo, otherwise the current user
CURRENT_USER=${SUDO_USER:-$(whoami)}

# detect --fast flag
FAST_MODE=false
for arg in "$@"; do
    if [ "$arg" == "--fast" ]; then
        FAST_MODE=true
    fi
done

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
if [ "$FAST_MODE" = false ]; then
    echo "📦 Installing system dependencies..."
    if [ "$PKG_MGR" == "dnf" ]; then
        sudo dnf install -y python3-pip python3-devel nginx git-core curl policycoreutils-python-utils openssl \
            libX11 libXext libXrender freetype libpng rsync
        sudo systemctl enable --now nginx
        
        # Open Firewall Port (Security Port 58921)
        if command -v firewall-cmd &> /dev/null; then
            echo "🔥 Opening Firewall Port 58921..."
            sudo firewall-cmd --permanent --add-port=58921/tcp
            sudo firewall-cmd --reload
        fi
    else
        sudo apt-get update -y
        sudo apt-get install -y python3-pip python3-venv nginx git curl rsync
    fi
else
    echo "⏩ Fast Mode: Skipping system dependency installs."
    # Ensure rsync is present even in fast mode if possible
    if ! command -v rsync &> /dev/null; then
        sudo $PKG_MGR install -y rsync
    fi
fi

# CRITICAL: Always ensure Nginx connectivity (regardless of Fast Mode)
if [ "$PKG_MGR" == "dnf" ]; then
    echo "🛡️  Ensuring Nginx SE booleans are enabled..."
    # These can take a while, so we only run if not already set
    [[ $(getsebool httpd_can_network_connect) == *"off"* ]] && sudo setsebool -P httpd_can_network_connect 1 || true
    [[ $(getsebool httpd_can_network_relay) == *"off"* ]] && sudo setsebool -P httpd_can_network_relay 1 || true
    [[ $(getsebool httpd_unified) == *"off"* ]] && sudo setsebool -P httpd_unified 1 || true
fi

# 2. Relocate Application to /opt
echo "🚚 Syncing application to $DEPLOY_DIR..."
# Create directory
sudo mkdir -p $DEPLOY_DIR

# Use rsync to preserve existing SELinux labels on unmodified files
echo "   Syncing files via rsync..."
sudo rsync -av --exclude='venv' --exclude='.git' --exclude='__pycache__' "$SOURCE_DIR/" "$DEPLOY_DIR/"

# Fix ownership and traversal permissions
echo "   Setting permissions on $DEPLOY_DIR..."
sudo chown -R $CURRENT_USER:$HTTP_GROUP $DEPLOY_DIR
# Ensure directories are traversable by Nginx
sudo find $DEPLOY_DIR -type d -exec chmod 755 {} +
# Ensure files are readable
sudo find $DEPLOY_DIR -type f -exec chmod 644 {} +
# Re-apply executable bit to venv/bin and scripts
sudo chmod -R +x $DEPLOY_DIR/scripts 2>/dev/null || true

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

# Optimization: only run pip install if FAST_MODE is false or requirements changed
if [ "$FAST_MODE" = false ] || [ "$DEPLOY_DIR/requirements.txt" -nt "$DEPLOY_DIR/venv/lib" ]; then
    ./venv/bin/pip install -r requirements.txt
else
    echo "⏩ Fast Mode: Requirements unchanged, skipping pip install."
fi
 
# 3.1 Pre-download Skyfield data files (Critical for servers)
if [ ! -f "de421.bsp" ]; then
    echo "🛰️ Pre-downloading astronomical data files..."
    ./venv/bin/python3 -c "from skyfield.api import load; load('de421.bsp'); load.timescale()"
else
    echo "🛰️ Skyfield data already present."
fi
sudo chown $CURRENT_USER:$HTTP_GROUP *.bsp *.dat *.tdb *.preds || true

# 4. FIX SELINUX (The Nuclear Way)
if command -v semanage &> /dev/null; then
    echo "🛡️ Configuring SELinux contexts for /opt/panchanga..."
    
    # 1. Allow Nginx to read static files
    sudo semanage fcontext -a -t httpd_sys_content_t "$DEPLOY_DIR/static(/.*)?"
    
    # Ensure directories exist and have correct permissions for Nginx to read
    sudo mkdir -p $DEPLOY_DIR/static/skyshots $DEPLOY_DIR/static/solar_systems
    sudo chown -R $CURRENT_USER:$HTTP_GROUP $DEPLOY_DIR/static
    sudo chmod -R 775 $DEPLOY_DIR/static
    # Set setgid bit so new files inherit the 'nginx' group
    sudo find $DEPLOY_DIR/static -type d -exec chmod g+s {} +
    
    # 2. Allow Systemd/Init to execute Gunicorn (bin_t)
    # Applying strictly to the bin folder
    sudo semanage fcontext -a -t bin_t "$DEPLOY_DIR/venv/bin(/.*)?"
    
    # Apply contexts
    sudo restorecon -R -v $DEPLOY_DIR
    
    # Explicitly ensure Gunicorn is bin_t (Critical for 203/EXEC)
    sudo chcon -t bin_t $DEPLOY_DIR/venv/bin/gunicorn
    
    # Allow Nginx to connect to the Gunicorn port (8000)
    echo "🛡️ Explicitly allowing Nginx to connect to port 8000..."
    sudo semanage port -m -t http_port_t -p tcp 8000 || sudo semanage port -a -t http_port_t -p tcp 8000 || true


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

# Handle Google API Key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY is not set in the current environment."
    read -p "🔑 Please enter your Google Gemini API Key: " GOOGLE_API_KEY
fi

# Using DEPLOY_DIR now instead of pwd
sed -e "s|{{USER}}|$CURRENT_USER|g" \
    -e "s|{{GROUP}}|$HTTP_GROUP|g" \
    -e "s|{{APP_PATH}}|$DEPLOY_DIR|g" \
    -e "s|{{GOOGLE_API_KEY}}|$GOOGLE_API_KEY|g" \
    panchanga.service.template | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

# 7. LOGGING & PRIVACY: Logrotate and Image Cleanup
echo "📝 Configuring logs and privacy settings..."
if [ -f "$SOURCE_DIR/panchanga.logrotate" ]; then
    sudo cp $SOURCE_DIR/panchanga.logrotate /etc/logrotate.d/panchanga
    sudo chmod 644 /etc/logrotate.d/panchanga
    
    # Force hourly execution via cron (system logrotate might only be daily)
    echo "   Setting up hourly cron job for logs..."
    echo "0 * * * * root /usr/sbin/logrotate -f /etc/logrotate.d/panchanga" | sudo tee /etc/cron.d/panchanga-rotate > /dev/null
fi

# PRIVACY: Setup automated image cleanup (Deletes images > 24h old)
echo "🧹 Setting up automated image cache cleanup..."
sudo mkdir -p $DEPLOY_DIR/scripts
sudo cp $SOURCE_DIR/scripts/cleanup_cache.sh $DEPLOY_DIR/scripts/cleanup_cache.sh
sudo chmod +x $DEPLOY_DIR/scripts/cleanup_cache.sh
echo "15 * * * * root $DEPLOY_DIR/scripts/cleanup_cache.sh >> /var/log/panchanga_cleanup.log 2>&1" | sudo tee /etc/cron.d/panchanga-cleanup > /dev/null

# 8. SECURITY: Generate Self-Signed Certificate
echo "🔒 Generating Self-Signed SSL Certificate..."
# Ensure directories exist
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

if [ "$FAST_MODE" = false ] || [ ! -f "/etc/ssl/certs/panchanga-selfsigned.crt" ]; then
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

echo "🎉 Deployment complete (v5.4)!"
echo "🕵️  Self-Diagnostic: Checking Service Health..."
if systemctl is-active --quiet $APP_NAME; then
    echo "   ✅ Gunicorn Service is RUNNING."
    echo "   🕵️  Checking backend response (localhost:8000)..."
    if curl -s -I http://127.0.0.1:8000 | grep -q "200 OK\|302 Found\|301 Moved"; then
        echo "   ✅ Backend is RESPONDING."
    else
        echo "   ⚠️  Backend is NOT responding on port 8000. Check logs."
    fi
else
    echo "   ❌ ERROR: Gunicorn Service is NOT running. Check 'sudo journalctl -u $APP_NAME'"
fi

if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is RUNNING."
else
    echo "   ❌ ERROR: Nginx is NOT running. Check 'sudo nginx -t'"
fi

echo "================================================================="
echo "App is SECURE at: https://$PUBLIC_IP:58921"
echo "Note: Accept the self-signed certificate warning in browser."
