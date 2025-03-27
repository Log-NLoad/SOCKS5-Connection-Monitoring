#!/bin/bash
set -e

REPO_URL="https://github.com/Log-NLoad/SOCKS5-Connection-Monitoring.git"
PROJECT_DIR="/socks_monitor"
CRON_USER="root"
CONFIG_FILE="$PROJECT_DIR/config.json"

install_package() {
    if ! command -v "$1" &> /dev/null; then
        echo "📦 Installing $1..."
        sudo apt update -y && sudo apt install -y "$1" || { echo "❌ Failed to install $1"; exit 1; }
    fi
}

install_package git
install_package python3
install_package python3-pip
install_package python3.8-venv
install_package cron
install_package jq

if [ -d "$PROJECT_DIR" ]; then
    echo "🚨 Directory $PROJECT_DIR exists! Pulling latest changes..."
    cd "$PROJECT_DIR" && git pull
else
    echo "⬇️ Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
python3 -m venv venv
$PROJECT_DIR/venv/bin/pip install --upgrade pip
$PROJECT_DIR/venv/bin/pip install -r requirements.txt

echo "Please enter your SOCKS5 proxy details:"
declare -a PROXIES
while true; do
    read -p "Proxy server (e.g., 192.168.1.1): " PROXY_SERVER
    while true; do
        read -p "Proxy port: " PROXY_PORT
        if [[ "$PROXY_PORT" =~ ^[0-9]+$ ]]; then break; else echo "❌ Invalid port!"; fi
    done
    read -p "Proxy username: " PROXY_USERNAME
    read -p "Proxy password: " PROXY_PASSWORD

    PROXIES+=("{\"server\": \"$PROXY_SERVER\", \"port\": $PROXY_PORT, \"username\": \"$PROXY_USERNAME\", \"password\": \"$PROXY_PASSWORD\"}")

    read -p "Add another proxy? (y/n): " ADD_ANOTHER
    [[ "$ADD_ANOTHER" =~ ^[Yy]$ ]] || break
done

echo "Please enter your email details:"
read -p "SMTP host (e.g., smtp.gmail.com): " SMTP_HOST
while true; do
    read -p "SMTP port (e.g., 587): " SMTP_PORT
    if [[ "$SMTP_PORT" =~ ^[0-9]+$ ]]; then break; else echo "❌ Invalid SMTP port!"; fi
done
read -p "Sender email: " SENDER_EMAIL
read -p "Sender app-password: " SENDER_PASSWORD
read -p "Recipient email: " RECIPIENT_EMAIL


echo "⚙️ Generating config.json..."
jq -n \
    --argjson proxies "[$(IFS=','; echo "${PROXIES[*]}")]" \
    --arg smtphost "$SMTP_HOST" \
    --arg smtpport "$SMTP_PORT" \
    --arg senderemail "$SENDER_EMAIL" \
    --arg senderpassword "$SENDER_PASSWORD" \
    --arg recipientemail "$RECIPIENT_EMAIL" \
    '{
        proxies: $proxies,
        smtp_host: $smtphost,
        smtp_port: ($smtpport | tonumber),
        sender_email: $senderemail,
        sender_password: $senderpassword,
        recipient_email: $recipientemail,
        email_subject: "Connection is DOWN!!!",
        email_body: "The SOCKS5 proxy connection is down. Please check your servers and connections."
    }' > "$CONFIG_FILE" || { echo "❌ Failed to generate config.json"; exit 1; }

sudo chown "$CRON_USER":"$CRON_USER" "$CONFIG_FILE"


echo "⏰ Setting up cron job for user: $CRON_USER"
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /socks_monitor && /socks_monitor/venv/bin/python3 /socks_monitor/monitor.py > /dev/null 2>&1") | sudo -u "$CRON_USER" crontab -

echo "✅ SOCKS5 monitor setup complete!"