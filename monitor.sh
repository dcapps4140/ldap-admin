#!/bin/bash

# TAK LDAP Admin Monitoring Script

echo "📊 TAK LDAP Admin Status Report"
echo "================================"
echo ""

# Service status
echo "🔧 Service Status:"
systemctl is-active ldap-admin && echo "  ✅ Application: Running" || echo "  ❌ Application: Stopped"
systemctl is-active nginx && echo "  ✅ Nginx: Running" || echo "  ❌ Nginx: Stopped"
systemctl is-active redis-server && echo "  ✅ Redis: Running" || echo "  ❌ Redis: Stopped"
echo ""

# Port status
echo "🌐 Port Status:"
netstat -tlnp | grep :443 > /dev/null && echo "  ✅ HTTPS (443): Open" || echo "  ❌ HTTPS (443): Closed"
netstat -tlnp | grep :8080 > /dev/null && echo "  ✅ App (8080): Open" || echo "  ❌ App (8080): Closed"
echo ""

# Disk usage
echo "💾 Disk Usage:"
df -h /var/www/ldap-admin | tail -1 | awk '{print "  📁 Application: " $5 " used"}'
df -h /var/log | tail -1 | awk '{print "  📋 Logs: " $5 " used"}'
echo ""

# Memory usage
echo "🧠 Memory Usage:"
free -h | grep Mem | awk '{print "  💾 RAM: " $3 "/" $2 " (" int($3/$2*100) "% used)"}'
echo ""

# Recent errors
echo "⚠️  Recent Errors (last 10):"
journalctl -u ldap-admin --since "1 hour ago" --no-pager -q | grep -i error | tail -10 || echo "  ✅ No recent errors"
echo ""

# SSL certificate status
echo "🔒 SSL Certificate:"
if [ -f "/etc/letsencrypt/live/your-domain.com/fullchain.pem" ]; then
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/your-domain.com/fullchain.pem | cut -d= -f2)
    echo "  📅 Expires: $EXPIRY"
else
    echo "  ❌ No SSL certificate found"
fi
echo ""

echo "📈 For detailed logs: journalctl -u ldap-admin -f"
