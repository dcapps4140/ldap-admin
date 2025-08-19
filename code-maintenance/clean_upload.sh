#!/bin/bash

REPO_URL="https://github.com/dcapps4140/webui.git"
COMMIT_MESSAGE="Updated LDAP admin interface - working version"

echo "TAK LDAP Admin - GitHub Upload Script"
echo "======================================"

cd /var/www/ldap-admin

# Fix Git ownership
sudo git config --global --add safe.directory /var/www/ldap-admin

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git branch -M main
fi

# Create .gitignore
cat > .gitignore << 'GITEND'
__pycache__/
*.py[cod]
venv/
.env
*.log
*.db
*.sqlite*
admin_users.json
GITEND

# Create .env.example
cat > .env.example << 'ENVEND'
SECRET_KEY=your_secret_key_here
LDAP_SERVER=ldaps://localhost:636
LDAP_BASE_DN=dc=tak,dc=local
LDAP_ADMIN_DN=cn=admin,dc=tak,dc=local
LDAP_ADMIN_PASSWORD=your_ldap_password_here
FLASK_ENV=production
ENVEND

# Create README
cat > README.md << 'READMEEND'
# TAK LDAP Admin Interface

Flask-based web interface for managing LDAP users and groups for TAK Server.

## Installation

1. Clone: `git clone https://github.com/dcapps4140/webui.git`
2. Setup: `cd webui && python3 -m venv venv && source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Configure: `cp .env.example .env` (edit with your settings)
5. Run: `python app.py`

## Default Login
- Username: admin
- Password: admin123
READMEEND

# Generate requirements
echo "Generating requirements.txt..."
./venv/bin/pip freeze > requirements.txt

# Setup remote
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "Adding remote origin..."
    git remote add origin $REPO_URL
fi

# Commit and push
echo "Adding files..."
git add .

echo "Committing..."
git commit -m "$COMMIT_MESSAGE"

echo "Pushing to GitHub..."
git push -u origin main

echo "Done! Repository: https://github.com/dcapps4140/webui"
EOF