from flask import Blueprint, request, jsonify
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

api = Blueprint('api', __name__)

# Configuration paths
CONFIG_DIR = Path("rdp_wrapper_enhanced/config")
CONFIG_FILE = CONFIG_DIR / "settings.json"
BACKUP_DIR = CONFIG_DIR / "backups"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def load_settings():
    """Load settings from JSON file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return get_default_settings()

def save_settings(settings):
    """Save settings to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def get_default_settings():
    """Get default settings configuration"""
    return {
        "general": {
            "autoStart": True,
            "logLevel": "info",
            "maxSessions": 10,
            "sessionTimeout": 30
        },
        "security": {
            "enableFirewall": True,
            "enableEncryption": True,
            "requireAuthentication": True,
            "allowedIPs": [],
            "blockedIPs": []
        },
        "performance": {
            "enableCompression": True,
            "enableCaching": True,
            "maxBandwidth": 100,
            "quality": "balanced"
        },
        "monitoring": {
            "enableLogging": True,
            "logLevel": "info",
            "enableMetrics": True,
            "alertThreshold": 80
        },
        "registry": {
            "debugMode": False,
            "performanceLogging": False,
            "customRegistry": "",
            "backupEnabled": True
        }
    }

def create_backup():
    """Create a backup of current settings"""
    if CONFIG_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"settings_backup_{timestamp}.json"
        shutil.copy2(CONFIG_FILE, backup_file)
        return str(backup_file)
    return None

def get_backups():
    """Get list of available backups"""
    if BACKUP_DIR.exists():
        backups = []
        for file in BACKUP_DIR.glob("settings_backup_*.json"):
            stat = file.stat()
            backups.append({
                "name": file.stem,
                "path": str(file),
                "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            })
        return sorted(backups, key=lambda x: x['date'], reverse=True)
    return []

@api.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    try:
        settings = load_settings()
        return jsonify({"success": True, "data": settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        new_settings = request.get_json()
        
        # Create backup before making changes
        if CONFIG_FILE.exists():
            create_backup()
        
        # Validate required fields
        required_sections = ["general", "security", "performance", "monitoring", "registry"]
        for section in required_sections:
            if section not in new_settings:
                return jsonify({
                    "success": False, 
                    "error": f"Missing required section: {section}"
                }), 400
        
        save_settings(new_settings)
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    try:
        create_backup()
        save_settings(get_default_settings())
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings/backup', methods=['POST'])
def backup_settings():
    """Create manual backup"""
    try:
        backup_path = create_backup()
        if backup_path:
            return jsonify({"success": True, "backup_path": backup_path})
        return jsonify({"success": False, "error": "No settings file to backup"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings/backups', methods=['GET'])
def list_backups():
    """List available backups"""
    try:
        backups = get_backups()
        return jsonify({"success": True, "data": backups})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings/restore/<backup_name>', methods=['POST'])
def restore_backup(backup_name):
    """Restore settings from backup"""
    try:
        backup_file = BACKUP_DIR / f"{backup_name}.json"
        if not backup_file.exists():
            return jsonify({"success": False, "error": "Backup not found"}), 404
        
        # Create current backup before restore
        create_backup()
        
        # Restore from backup
        shutil.copy2(backup_file, CONFIG_FILE)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/settings/restore/<backup_name>', methods=['DELETE'])
def delete_backup(backup_name):
    """Delete a backup"""
    try:
        backup_file = BACKUP_DIR / f"{backup_name}.json"
        if backup_file.exists():
            backup_file.unlink()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Backup not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
