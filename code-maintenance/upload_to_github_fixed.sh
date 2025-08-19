#!/bin/bash

# Configuration
REPO_URL="https://github.com/dcapps4140/webui.git"
COMMIT_MESSAGE="Updated LDAP admin interface - working version with user/group management"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}TAK LDAP Admin - GitHub Upload Script${NC}"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "/var/www/ldap-admin/app.py" ]; then
    echo -e "${RED}Error: app.py not found. Make sure you're running this from the correct location.${NC}"
    exit 1
fi

# Navigate to the application directory
cd /var/www/ldap-admin

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    git branch -M main
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}Creating .gitignore...${NC}"
    cat > .gitignore << 'GITIGNORE_END'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# Environment variables
.env

# Logs
*.log
logs/

# Database
*.db
*.sqlite*

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Admin users file (contains sensitive data)
admin_users.json
GITIGNORE_END
fi

# Create a sample .env file for documentation
if [ ! -f ".env.example" ]; then
    echo -e "${YELLOW}Creating .env.example...${NC}"
    cat > .env.example << 'ENV_END'
# TAK LDAP Admin Configuration
SECRET_KEY=your_secret_key_here
LDAP_SERVER=ldaps://localhost:636
LDAP_BASE_DN=dc=tak,dc=local
LDAP_ADMIN_DN=cn=admin,dc=tak,dc=local
LDAP_ADMIN_PASSWORD=your_ldap_password_here
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
ENV_END
fi

# Create README
echo -e "${YELLOW}Creating/updating README.md...${NC}"
cat > README.md << 'README_END'
# TAK LDAP Admin Interface

A Flask-based web interface for managing LDAP users and groups for TAK Server.

## Features

- Dashboard with LDAP statistics
- User management (view, create, edit, delete)
- Group management (view, create, edit, delete)
- LDAP connection testing
- Secure authentication with rate limiting
- Responsive Bootstrap UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dcapps4140/webui.git
cd webui
Create virtual environment:
bash

python3 -m venv venv
source venv/bin/activate
Install dependencies:
bash

pip install -r requirements.txt
Configure environment:
bash

cp .env.example .env
# Edit .env with your LDAP settings
Run the application:
bash

python app.py
Configuration
Copy .env.example to .env and configure:

LDAP_SERVER: Your LDAP server URL
LDAP_BASE_DN: Base DN for LDAP searches
LDAP_ADMIN_DN: Admin DN for LDAP binding
LDAP_ADMIN_PASSWORD: Admin password for LDAP binding
Default Login
Username: admin
Password: admin123
License
MIT License
README_END

Generate requirements.txt
echo -e "${YELLOW}Generating requirements.txt...${NC}"
./venv/bin/pip freeze > requirements.txt

Check if remote origin exists and points to the right repo
if git remote get-url origin >/dev/null 2>&1; then
CURRENT_REMOTE=$(git remote get-url origin)
if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
echo -e "${YELLOW}Updating remote origin URL...${NC}"
git remote set-url origin $REPO_URL
fi
else
echo -e "${YELLOW}Adding remote origin...${NC}"
git remote add origin $REPO_URL
fi

Add all files
echo -e "${YELLOW}Adding files to git...${NC}"
git add .

Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "$COMMIT_MESSAGE"

Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push -u origin main

echo -e "${GREEN}Successfully uploaded to GitHub!${NC}"
echo "Repository URL: https://github.com/dcapps4140/webui"