#!/bin/bash

# TAK LDAP Admin Installation Script
# Run as root or with sudo

set -e

echo "🚀 Starting TAK LDAP Admin Installation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root or with sudo"
   exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx redis-server \
    python3-ldap libldap2-dev libsasl2-dev libssl-dev \
    certbot python3-certbot-nginx ufw fail2ban

# Create application directory
print_status "Creating application directory..."
mkdir -p /var/www/ldap-admin
cd /var/www/ldap-admin

# Set permissions
chown -R www-data:www-data /var/www/ldap-admin
chmod -R 755 /var/www/ldap-admin

# Create Python virtual environment
print_status "Creating Python virtual environment..."
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install --upgrade pip

# Install Python packages
print_status "Installing Python packages..."
sudo -u www-data ./venv/bin/pip install flask flask-login flask-wtf flask-limiter \
    python-ldap redis gunicorn python-dotenv

# Generate secret key
print_status "Generating secret key..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Update .env file with generated secret key
sed -i "s/your-secret-key-here-change-this-in-production/$SECRET_KEY/" .env

# Enable and start Redis
print_status "Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# Configure fail2ban
print_status "Configuring fail2ban..."
tee /etc/fail2ban/jail.local > /dev/null << 'FAIL2BAN_EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/ldap-admin-error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/ldap-admin-error.log
maxretry = 10

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
FAIL2BAN_EOF

systemctl enable fail2ban
systemctl start fail2ban

# Enable and start the application service
print_status "Enabling application service..."
systemctl daemon-reload
systemctl enable ldap-admin

# Configure Nginx
print_status "Configuring Nginx..."
ln -sf /etc/nginx/sites-available/ldap-admin /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Enable and start Nginx
systemctl enable nginx
systemctl restart nginx

# Start the application
print_status "Starting application..."
systemctl start ldap-admin

# Create admin user setup script
tee /var/www/ldap-admin/setup_admin.py > /dev/null << 'ADMIN_EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/var/www/ldap-admin')

from werkzeug.security import generate_password_hash
import json

def create_admin_user():
    print("Creating admin user configuration...")
    
    # This would typically be stored in a database
    # For now, we'll create a simple JSON file
    admin_users = {
        "admin": {
            "password_hash": generate_password_hash("admin123"),
            "role": "super_admin",
            "email": "admin@localhost"
        },
        "operator": {
            "password_hash": generate_password_hash("operator123"),
            "role": "operator",
            "email": "operator@localhost"
        },
        "viewer": {
            "password_hash": generate_password_hash("viewer123"),
            "role": "viewer",
            "email": "viewer@localhost"
        }
    }
    
    with open('/var/www/ldap-admin/admin_users.json', 'w') as f:
        json.dump(admin_users, f, indent=2)
    
    os.chmod('/var/www/ldap-admin/admin_users.json', 0o600)
    os.chown('/var/www/ldap-admin/admin_users.json', 
             os.stat('/var/www/ldap-admin').st_uid,
             os.stat('/var/www/ldap-admin').st_gid)
    
    print("Admin users created:")
    print("  Username: admin, Password: admin123 (Super Admin)")
    print("  Username: operator, Password: operator123 (Operator)")
    print("  Username: viewer, Password: viewer123 (Viewer)")
    print("\n⚠️  IMPORTANT: Change these default passwords immediately!")

if __name__ == "__main__":
    create_admin_user()
ADMIN_EOF

chmod +x /var/www/ldap-admin/setup_admin.py
sudo -u www-data python3 /var/www/ldap-admin/setup_admin.py

print_success "Installation completed!"
print_warning "Next steps:"
echo "1. Update LDAP configuration in /var/www/ldap-admin/.env"
echo "2. Replace 'your-domain.com' in /etc/nginx/sites-available/ldap-admin"
echo "3. Obtain SSL certificate: certbot --nginx -d your-domain.com"
echo "4. Change default admin passwords"
echo "5. Test the application: systemctl status ldap-admin"
echo ""
echo "Default admin credentials:"
echo "  Username: admin, Password: admin123"
echo "  Username: operator, Password: operator123"
echo "  Username: viewer, Password: viewer123"
echo ""
print_warning "🔒 SECURITY: Change default passwords immediately!"
print_success "Access your application at: https://your-domain.com"
