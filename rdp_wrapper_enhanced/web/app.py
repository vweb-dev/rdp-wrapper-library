"""
Enhanced RDP Wrapper Web Application
Main Flask application for web-based RDP management
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from pathlib import Path

# Import our modules
from ..core.config import ConfigManager
from ..core.monitor import SessionMonitor
from ..core.security import SecurityManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rdp-wrapper-enhanced-2024')

# Initialize managers
config_manager = ConfigManager()
session_monitor = SessionMonitor()
security_manager = SecurityManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main dashboard page"""
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper auth)
        if username == 'admin' and password == 'rdp2024':
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    config = config_manager.load_config()
    sessions = session_monitor.get_active_sessions()
    system_info = session_monitor.get_system_info()
    
    return render_template('dashboard.html',
                         config=config,
                         sessions=sessions,
                         system_info=system_info,
                         username=session.get('username'))

@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    """Get current configuration"""
    return jsonify(config_manager.load_config())

@app.route('/api/config', methods=['POST'])
@login_required
def update_config():
    """Update configuration"""
    try:
        new_config = request.get_json()
        
        # Validate configuration
        validation = config_manager.validate_config(new_config)
        if not validation['valid']:
            return jsonify({'success': False, 'errors': validation['errors']}), 400
        
        # Save configuration
        if config_manager.save_config(new_config):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
            
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions')
@login_required
def get_sessions():
    """Get active RDP sessions"""
    return jsonify(session_monitor.get_active_sessions())

@app.route('/api/system-info')
@login_required
def get_system_info():
    """Get system information"""
    return jsonify(session_monitor.get_system_info())

@app.route('/api/security/scan', methods=['POST'])
@login_required
def security_scan():
    """Run security scan"""
    try:
        results = security_manager.run_security_scan()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Security scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/<session_id>/terminate', methods=['POST'])
@login_required
def terminate_session(session_id):
    """Terminate specific session"""
    try:
        success = session_monitor.terminate_session(session_id)
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    config = config_manager.load_config()
    return render_template('settings.html', config=config)

@app.route('/security')
@login_required
def security():
    """Security management page"""
    return render_template('security.html')

@app.route('/monitoring')
@login_required
def monitoring():
    """Monitoring page"""
    return render_template('monitoring.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
