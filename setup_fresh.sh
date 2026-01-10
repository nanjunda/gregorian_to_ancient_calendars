#!/bin/bash

# =================================================================
# Hindu Panchanga V5.6 - Oracle Linux 9 Fresh Install Orchestrator
# =================================================================

# Exit on any error
set -e

REPO_URL="https://github.com/nanjunda/gregorian_to_hindu_calendar.git"
INSTALL_BASE="/tmp"
INSTALL_DIR="$INSTALL_BASE/panchanga_nuclear_v5.6"
APP_NAME="gregorian_to_hindu_calendar"
# Allow branch override, default to current feature branch for testing
BRANCH=${1:-"feature/v6.0-mobile-first"}

echo "🌌 Starting Fresh Installation of Hindu Panchanga..."
echo "🌿 Target Branch: $BRANCH"
echo "🔑 Debug: Environment API Key Length: ${#GOOGLE_API_KEY}"

# 1. Clean up old installer traces
if [ -d "$INSTALL_DIR" ]; then
    echo "🧹 Removing previous installation traces..."
    sudo rm -rf "$INSTALL_DIR"
fi

# 2. Create and enter temporary staging dir
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo "📂 Working in: $(pwd)"

# 3. Ensure Git is installed
echo "📦 Ensuring Git is present..."
if command -v dnf &> /dev/null; then
    sudo dnf install -y git-core
else
    sudo apt-get update && sudo apt-get install -y git
fi

# 4. Clone the specific branch
echo "🏎️  Cloning Codebase ($BRANCH)..."
git clone -b "$BRANCH" "$REPO_URL"

# 5. Execute the core deployment script
# Use absolute paths to avoid any "not found" ambiguities
DEPLOY_PATH="$INSTALL_DIR/$APP_NAME/deploy.sh"

if [ ! -f "$DEPLOY_PATH" ]; then
    echo "❌ Error: Could not find deploy.sh at $DEPLOY_PATH"
    exit 1
fi

echo "🚀 Launching Deployment Engine..."
echo "📍 Transitioning to: $INSTALL_DIR/$APP_NAME"
cd "$INSTALL_DIR/$APP_NAME"

# Ensure deploy script is executable
chmod +x deploy.sh

# Pass the current environment's GOOGLE_API_KEY if it exists
# 6. Handle Google API Key (Pre-flight)
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not found in environment."
    read -p "🔑 Please enter your Google Gemini API Key: " GOOGLE_API_KEY
    echo "✅ Key received."
else
    echo "✅ Found GOOGLE_API_KEY in environment."
fi

# Pass the key explicitly to the deployment script
echo "🚢 Handing off to deploy.sh..."
sudo GOOGLE_API_KEY="$GOOGLE_API_KEY" bash ./deploy.sh

echo "================================================================="
echo "✅ SUCCESS! Hindu Panchanga Masterclass V5.4 is now installed."
echo "🌍 Check your Public IP on port 58921."
echo "📘 The Student Guide is linked in the footer."
echo "================================================================="
