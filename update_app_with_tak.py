#!/usr/bin/env python3
"""
Script to update app.py with TAK Server certificate management functionality.
Save this as update_app_with_tak.py and run it in the same directory as your app.py
"""

import os
import re
import shutil
from datetime import datetime

# First, create the tak_server.py file
tak_server_content = '''import requests
import json
import os
from flask import current_app
import base64
import subprocess

class TAKServerAPI:
    def __init__(self, base_url, admin_username, admin_password):
        self.base_url = base_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.session = requests.Session()
        self.session.auth = (admin_username, admin_password)
        self.session.verify = False  # For self-signed certs, set to True in production with proper certs
    
    def get_certificate_config(self):
        """Get certificate configuration from TAK Server"""
        url = f"{self.base_url}/Marti/api/tls/config"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.text
        else:
            current_app.logger.error(f"Failed to get certificate config: {response.status_code} {response.text}")
            return None
    
    def generate_enrollment_package(self, username):
        """Generate an enrollment package for a user"""
        # This would typically call the EnrollmentGenerator.jar utility
        # For now, we'll create a simplified version using Python
        
        # Create directory structure
        os.makedirs(f"temp/{username}/cert", exist_ok=True)
        
        # Get server hostname from base_url
        server_hostname = self.base_url.replace("https://", "").replace("http://", "").split(":")[0]
        
        # Create config.pref file
        config_pref = f"""<?xml version='1.0' encoding='ASCII' standalone='yes'?>
<preferences>
<preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">TAK Server</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">{server_hostname}:8089:ssl</entry>
    <entry key="caLocation0" class="class java.lang.String">cert/caCert.p12</entry>
    <entry key="caPassword0" class="class java.lang.String">atakatak</entry>
    <entry key="certificateAuthentication0" class="class java.lang.Boolean">true</entry>
    <entry key="useAuth0" class="class java.lang.Boolean">true</entry>
    <entry key="cacheCreds0" class="class java.lang.String">Cache credentials</entry>
</preference>
<preference version="1" name="com.atakmap.app_preferences">
    <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
    <entry key="network_quic_enabled" class="class java.lang.Boolean">true</entry>
    <entry key="apiSecureServerPort" class="class java.lang.String">8443</entry>
    <entry key="apiCertEnrollmentPort" class="class java.lang.String">8446</entry>
    <entry key="locationTeam" class="class java.lang.String">Blue</entry>
    <entry key="atakRoleType" class="class java.lang.String">Team Member</entry>
</preference>
</preferences>"""
        
        with open(f"temp/{username}/config.pref", "w") as f:
            f.write(config_pref)
        
        # Copy CA certificate - use subprocess to handle sudo if needed
        try:
            # Try to copy directly first
            shutil.copy("/opt/tak/certs/files/ca.pem", f"temp/{username}/cert/caCert.p12")
        except:
            # If that fails, try with sudo
            subprocess.run(["sudo", "cp", "/opt/tak/certs/files/ca.pem", f"temp/{username}/cert/caCert.p12"])
            subprocess.run(["sudo", "chmod", "644", f"temp/{username}/cert/caCert.p12"])
        
        # Create manifest
        manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="enrollment-{username}"/>
    <Parameter name="name" value="TAK Server Enrollment"/>
    <Parameter name="onReceiveDelete" value="true"/>
  </Configuration>
  <Contents>
    <Content ignore="false" zipEntry="config.pref"/>
    <Content ignore="false" zipEntry="cert/caCert.p12"/>
  </Contents>
</MissionPackageManifest>"""
        
        with open(f"temp/{username}/MANIFEST.xml", "w") as f:
            f.write(manifest)
        
        # Create zip file
        os.makedirs("static/enrollment_packages", exist_ok=True)
        subprocess.run(["zip", "-r", f"../../static/enrollment_packages/{username}.zip", "*"], cwd=f"temp/{username}")
        
        # Clean up
        shutil.rmtree(f"temp/{username}")
        
        return f"static/enrollment_packages/{username}.zip"
    
    def create_client_certificate(self, username):
        """Create a client certificate for a user using TAK Server's certificate tools"""
        os.makedirs("static/certificates", exist_ok=True)
        
        # Execute the makeCert.sh script
        subprocess.run(["sudo", "-u", "tak", "/opt/tak/certs/makeCert.sh", "client", username], cwd="/opt/tak/certs")
        
        # Create P12 file
        subprocess.run([
            "sudo", "openssl", "pkcs12", "-export", 
            "-in", f"/opt/tak/certs/files/{username}.pem", 
            "-inkey", f"/opt/tak/certs/files/{username}.key", 
            "-out", f"static/certificates/{username}.p12", 
            "-name", username, 
            "-passout", "pass:atakatak"
        ])
        
        # Set permissions
        subprocess.run(["sudo", "chmod", "644", f"static/certificates/{username}.p12"])
        
        return f"static/certificates/{username}.p12"
'''

with open("tak_server.py", "w") as f:
    f.write(tak_server_content)
print("Created tak_server.py")

# Create the certificate management template
os.makedirs("templates", exist_ok=True)
user_cert_template = '''{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>Certificate Management for {{ username }}</h1>
    
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h3>Enrollment Package</h3>
                </div>
                <div class="card-body">
                    <p>Enrollment packages allow users to request their own certificates using their LDAP credentials.</p>
                    
                    {% if has_enrollment %}
                        <a href="{{ url_for('download_enrollment', username=username) }}" class="btn btn-primary">
                            <i class="fas fa-download"></i> Download Enrollment Package
                        </a>
                        <div class="mt-2">
                            <form method="post" action="{{ url_for('email_enrollment', username=username) }}">
                                <button type="submit" class="btn btn-info">
                                    <i class="fas fa-envelope"></i> Email Enrollment Package
                                </button>
                            </form>
                        </div>
                    {% else %}
                        <form method="post">
                            <input type="hidden" name="action" value="generate_enrollment">
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-plus"></i> Generate Enrollment Package
                            </button>
                        </form>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h3>Client Certificate</h3>
                </div>
                <div class="card-body">
                    <p>Client certificates allow direct access to TAK Server without enrollment.</p>
                    
                    {% if has_certificate %}
                        <a href="{{ url_for('download_certificate', username=username) }}" class="btn btn-primary">
                            <i class="fas fa-download"></i> Download Certificate
                        </a>
                        <p class="mt-2"><small>Certificate password: atakatak</small></p>
                    {% else %}
                        <form method="post">
                            <input type="hidden" name="action" value="create_certificate">
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-plus"></i> Create Certificate
                            </button>
                        </form>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <div class="mt-4">
        <a href="{{ url_for('user_detail', username=username) }}" class="btn btn-secondary">
            <i class="fas fa-arrow-left"></i> Back to User Details
        </a>
    </div>
</div>
{% endblock %}
'''

with open("templates/user_certificate.html", "w") as f:
    f.write(user_cert_template)
print("Created templates/user_certificate.html")

# Now update app.py
# First, make a backup
if os.path.exists("app.py"):
    backup_name = f"app.py.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy("app.py", backup_name)
    print(f"Created backup of app.py as {backup_name}")

    with open("app.py", "r") as f:
        app_content = f.read()

    # Add imports
    import_pattern = r"from flask import .*?\n"
    if re.search(import_pattern, app_content):
        new_imports = "from flask import Flask, render_template, request, redirect, url_for, flash, send_file\n"
        app_content = re.sub(import_pattern, new_imports, app_content)
    
    # Add TAK Server API import
    if "from tak_server import TAKServerAPI" not in app_content:
        import_section_end = app_content.find("app = Flask")
        if import_section_end > 0:
            app_content = app_content[:import_section_end] + "from tak_server import TAKServerAPI\nimport os\n\n" + app_content[import_section_end:]
    
    # Add TAK Server API initialization
    tak_api_init = """
# Initialize TAK Server API
tak_server_api = TAKServerAPI(
    app.config.get('TAK_SERVER_URL', 'https://opssmdtak.org'),
    app.config.get('TAK_ADMIN_USERNAME', 'admin'),
    app.config.get('TAK_ADMIN_PASSWORD', 'AdminPassword123!')
)

# Ensure directories exist
os.makedirs("static/enrollment_packages", exist_ok=True)
os.makedirs("static/certificates", exist_ok=True)
"""
    
    app_init_pattern = r"app = Flask\(__name__\).*?\n"
    if re.search(app_init_pattern, app_content):
        app_config_end = re.search(app_init_pattern, app_content).end()
        # Find the end of app configuration section
        next_section = app_content.find("\n\n", app_config_end)
        if next_section > 0:
            app_content = app_content[:next_section] + tak_api_init + app_content[next_section:]
    
    # Add certificate routes
    certificate_routes = """
@app.route('/users/<username>/certificate', methods=['GET', 'POST'])
@login_required
def user_certificate(username):
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate_enrollment':
            # Generate enrollment package
            package_path = tak_server_api.generate_enrollment_package(username)
            flash(f"Enrollment package generated for {username}", "success")
            return redirect(url_for('user_certificate', username=username))
        
        elif action == 'create_certificate':
            # Create client certificate
            cert_path = tak_server_api.create_client_certificate(username)
            flash(f"Certificate created for {username}", "success")
            return redirect(url_for('user_certificate', username=username))
    
    # Check if enrollment package exists
    enrollment_package = f"static/enrollment_packages/{username}.zip"
    has_enrollment = os.path.exists(enrollment_package)
    
    # Check if certificate exists
    certificate = f"static/certificates/{username}.p12"
    has_certificate = os.path.exists(certificate)
    
    return render_template(
        'user_certificate.html',
        username=username,
        has_enrollment=has_enrollment,
        has_certificate=has_certificate
    )

@app.route('/users/<username>/download/enrollment')
@login_required
def download_enrollment(username):
    enrollment_package = f"static/enrollment_packages/{username}.zip"
    if os.path.exists(enrollment_package):
        return send_file(enrollment_package, as_attachment=True, download_name=f"{username}_enrollment.zip")
    else:
        flash("Enrollment package not found", "error")
        return redirect(url_for('user_certificate', username=username))

@app.route('/users/<username>/download/certificate')
@login_required
def download_certificate(username):
    certificate = f"static/certificates/{username}.p12"
    if os.path.exists(certificate):
        return send_file(certificate, as_attachment=True, download_name=f"{username}_certificate.p12")
    else:
        flash("Certificate not found", "error")
        return redirect(url_for('user_certificate', username=username))

@app.route('/users/<username>/email_enrollment', methods=['POST'])
@login_required
def email_enrollment(username):
    # Get user email from LDAP
    user = ldap_manager.get_user_by_username(username)
    user_email = user.get('mail', [''])[0] if user else None
    
    if not user_email:
        flash("User email not found", "error")
        return redirect(url_for('user_certificate', username=username))
    
    # Check if enrollment package exists
    enrollment_package = f"static/enrollment_packages/{username}.zip"
    if not os.path.exists(enrollment_package):
        # Generate enrollment package if it doesn't exist
        tak_server_api.generate_enrollment_package(username)
    
    # Send email - this requires Flask-Mail to be configured
    try:
        from flask_mail import Message
        msg = Message(
            "Your TAK Server Enrollment Package",
            sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@example.com'),
            recipients=[user_email]
        )
        
        msg.body = f\"\"\"
Hello {username},

Your TAK Server account has been created. Please follow these steps to access the system:

1. Download the attached enrollment package
2. Import it into your TAK client (ATAK/WinTAK)
3. When prompted, enter your LDAP credentials:
   - Username: {username}
   - Password: (your LDAP password)

If you have any questions, please contact support.

Regards,
TAK Server Admin Team
\"\"\"
        
        with app.open_resource(enrollment_package) as fp:
            msg.attach(
                f"{username}_enrollment.zip",
                "application/zip",
                fp.read()
            )
        
        mail.send(msg)
        flash(f"Enrollment package sent to {user_email}", "success")
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")
        flash(f"Failed to send email: {str(e)}", "error")
    
    return redirect(url_for('user_certificate', username=username))
"""
    
    # Add the routes at the end of the file
    app_content += certificate_routes
    
    # Write the updated content back to app.py
    with open("app.py", "w") as f:
        f.write(app_content)
    
    print("Updated app.py with TAK Server certificate management functionality")
    
    # Create a patch for user_detail.html
    user_detail_patch = """
<!-- Add this to your user_detail.html template -->
<!-- Find a suitable location, like near other action buttons -->
<a href="{{ url_for('user_certificate', username=username) }}" class="btn btn-info">
    <i class="fas fa-certificate"></i> Manage Certificates
</a>
"""
    
    print("\nAdd this to your user_detail.html template:")
    print(user_detail_patch)
    
    # Create a .env update suggestion
    env_update = """
# Add these to your .env file
TAK_SERVER_URL=https://opssmdtak.org
TAK_ADMIN_USERNAME=admin
TAK_ADMIN_PASSWORD=AdminPassword123!

# For email functionality
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@example.com
"""
    
    print("\nAdd these to your .env file (adjust values as needed):")
    print(env_update)
    
    # Create requirements update suggestion
    requirements_update = """
# Add these to your requirements.txt file if not already present
flask-mail==0.9.1
"""
    
    print("\nAdd these to your requirements.txt file if not already present:")
    print(requirements_update)
    
else:
    print("Error: app.py not found in the current directory")
