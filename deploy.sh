#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Hindu Panchanga v3.0 Deployment..."

# 1. Update system
echo "📦 Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed."
else
    echo "✅ Docker is already installed."
fi

# 3. Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🏗️ Installing Docker Compose..."
    sudo apt-get install -y docker-compose
    echo "✅ Docker Compose installed."
else
    echo "✅ Docker Compose is already installed."
fi

# 4. Clone or update repository
if [ ! -d "gregorian_to_hindu_calendar" ]; then
    echo "📂 Cloning repository..."
    # Replace with the actual URL if needed, or assume it's already in the folder
    git clone https://github.com/nanjundasomayaji/gregorian_to_hindu_calendar.git
    cd gregorian_to_hindu_calendar
else
    echo "📂 Updating repository..."
    cd gregorian_to_hindu_calendar
    git pull
fi

# 5. Build and Run
echo "⚡ Building and starting containers..."
sudo docker-compose up --build -d

echo "🎉 Deployment complete! App is running on port 80."
echo "Wait a few seconds for the app to initialize."
