#!/bin/bash

# TAK LDAP Admin Backup Script

BACKUP_DIR="/var/backups/ldap-admin"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ldap-admin-$DATE.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🗄️  Creating backup..."

# Create backup
cd /var/www
tar -czf $BACKUP_FILE \
    --exclude='ldap-admin/venv' \
    --exclude='ldap-admin/__pycache__' \
    --exclude='ldap-admin/*.pyc' \
    ldap-admin/

# Set permissions
chmod 600 $BACKUP_FILE
chown root:root $BACKUP_FILE

echo "✅ Backup created: $BACKUP_FILE"

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "ldap-admin-*.tar.gz" -mtime +30 -delete

echo "🧹 Old backups cleaned"
