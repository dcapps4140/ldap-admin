import requests
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
