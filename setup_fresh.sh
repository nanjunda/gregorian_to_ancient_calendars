#!/bin/bash

# =================================================================
# Hindu Panchanga V5.3 - Oracle Linux 9 Fresh Install Orchestrator
# =================================================================

# Exit on any error
set -e

REPO_URL="https://github.com/nanjunda/gregorian_to_hindu_calendar.git"
INSTALL_DIR="panchanga_installer_v5.3"
APP_FOLDER="gregorian_to_hindu_calendar"

echo "🌌 Starting Fresh Installation of Hindu Panchanga Masterclass..."

# 1. Clean up old installer traces
if [ -d "$INSTALL_DIR" ]; then
    echo "🧹 Removing previous installation traces..."
    rm -rf "$INSTALL_DIR"
fi

# 2. Create and enter temporary staging dir
mkdir "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 3. Ensure Git is installed
echo "📦 Ensuring Git is present..."
sudo dnf install -y git-core

# 4. Clone the latest V5.3 Masterclass codebase
echo "🏎️  Cloning Cosmic Masterclass (V5.3)..."
git clone "$REPO_URL"

# 5. Execute the core deployment script
if [ ! -d "$APP_FOLDER" ]; then
    echo "❌ Error: Could not find $APP_FOLDER after clone."
    exit 1
fi

cd "$APP_FOLDER"
echo "🚀 Launching Deployment Engine in $(pwd)..."

# Ensure deploy script is executable and run using bash explicitly
chmod +x deploy.sh

# Pass the current environment's GOOGLE_API_KEY if it exists
if [ ! -z "$GOOGLE_API_KEY" ]; then
    sudo GOOGLE_API_KEY="$GOOGLE_API_KEY" bash ./deploy.sh
else
    sudo bash ./deploy.sh
fi

echo "================================================================="
echo "✅ SUCCESS! Hindu Panchanga Masterclass is now installed."
echo "🌍 Check your Public IP on port 58921."
echo "📘 The Student Guide is linked in the footer."
echo "================================================================="
