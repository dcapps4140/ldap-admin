#!/bin/bash

# TAK LDAP Admin Update Script

set -e

echo "🔄 Updating TAK LDAP Admin..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

cd /var/www/ldap-admin

# Backup current installation
print_status "Creating backup..."
tar -czf "/tmp/ldap-admin-backup-$(date +%Y%m%d-%H%M%S).tar.gz" \
    --exclude='venv' --exclude='__pycache__' .

# Stop the service
print_status "Stopping service..."
systemctl stop ldap-admin

# Update Python packages
print_status "Updating Python packages..."
sudo -u www-data ./venv/bin/pip install --upgrade pip
sudo -u www-data ./venv/bin/pip install --upgrade flask flask-login flask-wtf \
    flask-limiter python-ldap redis gunicorn python-dotenv

# Restart services
print_status "Restarting services..."
systemctl start ldap-admin
systemctl reload nginx

# Check status
sleep 5
if systemctl is-active --quiet ldap-admin; then
    print_success "Update completed successfully!"
else
    echo "❌ Service failed to start. Check logs: journalctl -u ldap-admin"
    exit 1
fi
