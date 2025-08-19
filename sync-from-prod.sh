#!/bin/bash
echo "Syncing from production..."
sudo cp -r /var/www/ldap-admin/* ~/projects/ldap-admin/
sudo chown -R dcapps:dcapps ~/projects/ldap-admin/
echo "Sync complete!"
