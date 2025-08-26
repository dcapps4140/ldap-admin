from flask import jsonify, jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, PasswordField, SelectField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length
import ldap3
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
import bcrypt
import redis
import logging
import os
from datetime import datetime, timedelta
import secrets
import json
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
from tak_server import TAKServerAPI
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['WTF_CSRF_TIME_LIMIT'] = 3600
# Initialize TAK Server API
tak_server_api = TAKServerAPI(
    app.config.get('TAK_SERVER_URL', 'https://opssmdtak.org'),
    app.config.get('TAK_ADMIN_USERNAME', 'admin'),
    app.config.get('TAK_ADMIN_PASSWORD', 'AdminPassword123!')
)

# Ensure directories exist
os.makedirs("static/enrollment_packages", exist_ok=True)
os.makedirs("static/certificates", exist_ok=True)


# Security configurations
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Redis for session storage
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
except:
    redis_client = None

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ldap-admin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# LDAP Configuration
LDAP_CONFIG = {
    'server': os.environ.get('LDAP_SERVER', 'ldap://localhost:389'),
    'base_dn': os.environ.get('LDAP_BASE_DN', 'dc=tak,dc=local'),
    'admin_dn': os.environ.get('LDAP_ADMIN_DN', 'cn=admin,dc=tak,dc=local'),
    'admin_password': os.environ.get('LDAP_ADMIN_PASSWORD', 'takserver123'),
    'users_ou': 'ou=users',
    'groups_ou': 'ou=groups'
}

# Admin users configuration (move to database in production)
ADMIN_USERS = {
    'admin': {
        'password_hash': bcrypt.hashpw(b'admin123', bcrypt.gensalt()),
        'role': 'super_admin',
        'name': 'System Administrator'
    },
    'operator': {
        'password_hash': bcrypt.hashpw(b'operator123', bcrypt.gensalt()),
        'role': 'operator',
        'name': 'LDAP Operator'
    },
    'viewer': {
        'password_hash': bcrypt.hashpw(b'viewer123', bcrypt.gensalt()),
        'role': 'viewer',
        'name': 'Read Only User'
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username, role, name):
        self.id = username
        self.username = username
        self.role = role
        self.name = name
    
    def can_write(self):
        return self.role in ['super_admin', 'operator']
    
    def can_delete(self):
        return self.role == 'super_admin'
    
    def can_manage_groups(self):
        return self.role == 'super_admin'

@login_manager.user_loader
def load_user(username):
    if username in ADMIN_USERS:
        user_data = ADMIN_USERS[username]
        return User(username, user_data['role'], user_data['name'])
    return None

# Role-based access control decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('You do not have permission to access this resource.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# LDAP Helper Functions
def get_ldap_connection():
    """Get LDAP connection"""
    try:
        server = Server(LDAP_CONFIG['server'], get_info=ALL)
        conn = Connection(
            server,
            LDAP_CONFIG['admin_dn'],
            LDAP_CONFIG['admin_password'],
            auto_bind=True
        )
        return conn
    except Exception as e:
        logger.error(f"LDAP connection failed: {str(e)}")
        return None

def log_action(action, details=""):
    """Log user actions"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': current_user.username if current_user.is_authenticated else 'anonymous',
        'action': action,
        'details': details,
        'ip': request.remote_addr
    }
    logger.info(f"Action: {json.dumps(log_entry)}")

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', [DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=3, max=50)])
    first_name = StringField('First Name', [DataRequired(), Length(min=1, max=50)])
    last_name = StringField('Last Name', [DataRequired(), Length(min=1, max=50)])
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(), Length(min=6)])
    group = SelectField('Primary Group', choices=[
        ('users', 'Users'),
        ('operators', 'Operators'),
        ('admins', 'Administrators')
    ])

class GroupForm(FlaskForm):
    name = StringField('Group Name', [DataRequired(), Length(min=3, max=50)])
    description = TextAreaField('Description', [Length(max=200)])

# Routes
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower().strip()
        password = form.password.data.encode('utf-8')
        
        if username in ADMIN_USERS:
            stored_hash = ADMIN_USERS[username]['password_hash']
            if bcrypt.checkpw(password, stored_hash):
                user_data = ADMIN_USERS[username]
                user = User(username, user_data['role'], user_data['name'])
                login_user(user, remember=True)
                log_action('login_success')
                flash(f'Welcome back, {user.name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        
        log_action('login_failed', f'Username: {username}')
        flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    log_action('logout')
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    try:
        # Get statistics
        conn = get_ldap_connection()
        stats = {'users': 0, 'groups': 0, 'status': 'disconnected'}
        
        if conn:
            # Count users
            conn.search(
                f"{LDAP_CONFIG['users_ou']},{LDAP_CONFIG['base_dn']}",
                '(objectClass=inetOrgPerson)',
                SUBTREE
            )
            stats['users'] = len(conn.entries)
            
            # Count groups
            conn.search(
                f"{LDAP_CONFIG['groups_ou']},{LDAP_CONFIG['base_dn']}",
                '(objectClass=groupOfNames)',
                SUBTREE
            )
            stats['groups'] = len(conn.entries)
            stats['status'] = 'connected'
            conn.unbind()
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard data.', 'error')
        return render_template('dashboard.html', stats={'users': 0, 'groups': 0, 'status': 'error'})

@app.route('/users')
@login_required
def users():
    return render_template('users.html')

@app.route('/groups')
@login_required
def groups():
    return render_template('groups.html')

@app.route('/settings')
@role_required('super_admin')
def settings():
    return render_template('settings.html', ldap_config=LDAP_CONFIG)

# API Routes
@app.route('/api/users', methods=['GET'])
@login_required
@limiter.limit("20 per minute")
def api_get_users():
    try:
        conn = get_ldap_connection()
        if not conn:
            return jsonify({'error': 'LDAP connection failed'}), 500
        
        conn.search(
            f"{LDAP_CONFIG['users_ou']},{LDAP_CONFIG['base_dn']}",
            '(objectClass=inetOrgPerson)',
            SUBTREE,
            attributes=['cn', 'sn', 'givenName', 'mail', 'uid', 'displayName']
        )
        
        users = []
        for entry in conn.entries:
            user_data = {
                'username': str(entry.uid) if entry.uid else '',
                'first_name': str(entry.givenName) if entry.givenName else '',
                'last_name': str(entry.sn) if entry.sn else '',
                'email': str(entry.mail) if entry.mail else '',
		'groups': [str(group).split(',')[0].replace('cn=', '') for group in getattr(entry, 'memberOf', [])]
            }
            users.append(user_data)
        
        conn.unbind()
        log_action('list_users', f'Retrieved {len(users)} users')
        return jsonify(users)
        
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'error': 'Failed to retrieve users'}), 500

@app.route('/api/users', methods=['POST'])
@role_required('super_admin', 'operator')
@limiter.limit("10 per minute")
def api_add_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_ldap_connection()
        if not conn:
            return jsonify({'error': 'LDAP connection failed'}), 500
        
        username = data['username'].lower().strip()
        user_dn = f"uid={username},{LDAP_CONFIG['users_ou']},{LDAP_CONFIG['base_dn']}"
        
        # Check if user already exists
        if conn.search(user_dn, '(objectClass=*)'):
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user entry
        user_attrs = {
            'objectClass': ['inetOrgPerson', 'posixAccount'],
            'uid': username,
            'cn': f"{data['first_name']} {data['last_name']}",
            'sn': data['last_name'],
            'givenName': data['first_name'],
            'mail': data['email'],
            'userPassword': data['password'],  # LDAP will hash this
            'uidNumber': str(hash(username) % 10000 + 1000),
            'gidNumber': '1000',
            'homeDirectory': f'/home/{username}',
            'loginShell': '/bin/bash'
        }
        
        if conn.add(user_dn, attributes=user_attrs):
            log_action('add_user', f'Added user: {username}')
            return jsonify({'success': True, 'message': 'User added successfully'})
        else:
            return jsonify({'error': 'Failed to add user to LDAP'}), 500
            
    except Exception as e:
        logger.error(f"Error adding user: {str(e)}")
        return jsonify({'error': 'Failed to add user'}), 500
    finally:
        if 'conn' in locals():
            conn.unbind()

@app.route('/api/users/<username>', methods=['DELETE'])
@role_required('super_admin')
@limiter.limit("5 per minute")
def api_delete_user(username):
    try:
        conn = get_ldap_connection()
        if not conn:
            return jsonify({'error': 'LDAP connection failed'}), 500
        
        user_dn = f"uid={username},{LDAP_CONFIG['users_ou']},{LDAP_CONFIG['base_dn']}"
        
        if conn.delete(user_dn):
            log_action('delete_user', f'Deleted user: {username}')
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': 'Failed to delete user'}), 500
    finally:
        if 'conn' in locals():
            conn.unbind()

@app.route('/api/groups', methods=['GET'])
@login_required
@limiter.limit("20 per minute")
def api_get_groups():
    try:
        conn = get_ldap_connection()
        if not conn:
            return jsonify({'error': 'LDAP connection failed'}), 500
        
        conn.search(
            f"{LDAP_CONFIG['groups_ou']},{LDAP_CONFIG['base_dn']}",
            '(objectClass=groupOfNames)',
            SUBTREE,
            attributes=['cn', 'description', 'member']
        )
        
        groups = []
        for entry in conn.entries:
            group_data = {
                'name': str(entry.cn) if entry.cn else '',
                'description': str(entry.description) if entry.description else '',
                'member_count': len(entry.member) if entry.member else 0
            }
            groups.append(group_data)
        
        conn.unbind()
        log_action('list_groups', f'Retrieved {len(groups)} groups')
        return jsonify(groups)
        
    except Exception as e:
        logger.error(f"Error retrieving groups: {str(e)}")
        return jsonify({'error': 'Failed to retrieve groups'}), 500

@app.route('/api/test-connection', methods=['GET'])
@login_required
def api_test_connection():
    try:
        conn = get_ldap_connection()
        if conn:
            conn.unbind()
            log_action('test_connection', 'Connection successful')
            return jsonify({'success': True, 'message': 'LDAP connection successful'})
        else:
            return jsonify({'success': False, 'message': 'LDAP connection failed'})
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return jsonify({'success': False, 'message': f'Connection failed: {str(e)}'})

@app.route('/api/stats', methods=['GET'])
@login_required
def api_get_stats():
    try:
        conn = get_ldap_connection()
        stats = {'users': 0, 'groups': 0, 'status': 'disconnected'}
        
        if conn:
            # Count users
            conn.search(
                f"{LDAP_CONFIG['users_ou']},{LDAP_CONFIG['base_dn']}",
                '(objectClass=inetOrgPerson)',
                SUBTREE
            )
            stats['users'] = len(conn.entries)
            
            # Count groups
            conn.search(
                f"{LDAP_CONFIG['groups_ou']},{LDAP_CONFIG['base_dn']}",
                '(objectClass=groupOfNames)',
                SUBTREE
            )
            stats['groups'] = len(conn.entries)
            stats['status'] = 'connected'
            conn.unbind()
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'users': 0, 'groups': 0, 'status': 'error'})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('error.html', error_code=429, error_message="Rate limit exceeded"), 429

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

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
        
        msg.body = f"""
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
"""
        
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
