#!/bin/bash

# Function to check and install packages
install_if_missing() {
    if ! dpkg -l | grep -q ""; then
        echo "Installing ..."
        sudo apt-get update
        sudo apt-get install -y ""
    fi
}

# Ask if virtual environment is preferred
read -p "Do you want to use a virtual environment? (y/n): " use_venv

# Create and activate virtual environment if requested
if [[ "" =~ ^(yes|y)$ ]]; then
    python3 -m venv venv
    source venv/bin/activate
fi

# Install requirements
pip install -r requirements.txt

# Gather information for .env file
read -p "Enter AGENT_API_KEY: " AGENT_API_KEY
read -p "Enter allowed IPs (e.g., 192.168.1.1): " ALLOWED_IPS
read -p "Enter log file path (default: ./agent_shell.log): " LOG_FILE
LOG_FILE=/var/log/agent_shell.log

# Write to .env file
cat <<EOL > .env
AGENT_API_KEY=xB6xaXnh9z3sG6d3G7p2ZX2wWHTs1zkQosxjU3FZ7do
ALLOWED_IPS=127.0.0.1,178.79.141.115,81.137.195.253
LOG_FILE=/var/log/agent_shell.log
