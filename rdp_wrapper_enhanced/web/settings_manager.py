"""
Enhanced Settings Configuration Management System
Provides advanced settings management with validation, backup, and real-time updates
"""

from flask import Blueprint, jsonify, request
from ..core.config import ConfigManager
from ..core.security import SecurityManager
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

settings_manager = Blueprint('settings_manager', __name__, url_prefix='/api/settings/v2')

# Enhanced configuration paths
CONFIG_DIR = Path("rdp_wrapper_enhanced/config")
ENHANCED_CONFIG_FILE = CONFIG_DIR / "enhanced_settings.json"
BACKUP_DIR = CONFIG_DIR / "enhanced_backups"
PROFILES_DIR = CONFIG_DIR / "profiles"

class SettingsManager:
    """Advanced settings management with validation and profiles"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.security = SecurityManager()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [CONFIG_DIR, BACKUP_DIR, PROFILES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_enhanced_settings(self):
        """Get enhanced settings with validation"""
        if ENHANCED_CONFIG_FILE.exists():
            try:
                with open(ENHANCED_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading enhanced settings: {e}")
        
        return self.get_default_enhanced_settings()
    
    def save_enhanced_settings(self, settings):
        """Save enhanced settings with validation"""
        try:
            # Validate settings structure
            validated = self.validate_settings(settings)
            
            # Create backup before saving
            self.create_backup()
            
            with open(ENHANCED_CONFIG_FILE, 'w') as f:
                json.dump(validated, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving enhanced settings: {e}")
            return False
    
    def validate_settings(self, settings):
        """Validate and normalize settings"""
        defaults = self.get_default_enhanced_settings()
        
        # Merge with defaults to ensure all required fields exist
        validated = defaults.copy()
        
        for section, values in settings.items():
            if section in validated:
                validated[section].update(values)
        
        return validated
    
    def get_default_enhanced_settings(self):
        """Get default enhanced settings configuration"""
        return {
            "general": {
                "autoStart": True,
                "logLevel": "info",
                "maxSessions": 10,
                "sessionTimeout": 30,
                "enableNotifications": True,
                "startupDelay": 5,
                "language": "en"
            },
            "security": {
                "enableFirewall": True,
                "enableEncryption": True,
                "requireAuthentication": True,
                "allowedIPs": [],
                "blockedIPs": [],
                "enable2FA": False,
                "sessionLockTimeout": 15,
                "maxLoginAttempts": 5,
                "lockoutDuration": 30
            },
            "performance": {
                "enableCompression": True,
                "enableCaching": True,
                "maxBandwidth": 100,
                "quality": "balanced",
                "frameRate": 30,
                "colorDepth": 24,
                "enableHardwareAcceleration": True,
                "memoryLimit": 512
            },
            "monitoring": {
                "enableLogging": True,
                "logLevel": "info",
                "enableMetrics": True,
                "alertThreshold": 80,
                "logRetention": 30,
                "enableHealthChecks": True,
                "healthCheckInterval": 60
            },
            "registry": {
                "debugMode": False,
                "performanceLogging": False,
                "customRegistry": "",
                "backupEnabled": True,
                "autoBackupInterval": 24,
                "maxBackups": 10
            },
            "network": {
                "port": 3389,
                "enableUPnP": False,
                "bindAddress": "0.0.0.0",
                "maxConnections": 100,
                "connectionTimeout": 30,
                "keepAlive": True
            },
            "display": {
                "defaultResolution": "1920x1080",
                "enableMultiMonitor": True,
                "enableAudio": True,
                "enableClipboard": True,
                "enableFileTransfer": True
            },
            "advanced": {
                "enableGPO": False,
                "enableLoggingToFile": True,
                "logFilePath": "logs/rdp_wrapper.log",
                "enableDebugConsole": False,
                "performanceCounters": False,
                "customParameters": {}
            }
        }
    
    def create_backup(self):
        """Create enhanced backup with metadata"""
        if ENHANCED_CONFIG_FILE.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = BACKUP_DIR / f"enhanced_settings_backup_{timestamp}.json"
            
            # Add metadata to backup
            with open(ENHANCED_CONFIG_FILE, 'r') as src:
                settings = json.load(src)
            
            settings['_metadata'] = {
                'backup_date': datetime.now().isoformat(),
                'version': '2.0',
                'source': 'enhanced_settings'
            }
            
            with open(backup_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            return str(backup_file)
        return None
    
    def get_backups(self):
        """Get enhanced backup list with metadata"""
        if BACKUP_DIR.exists():
            backups = []
            for file in BACKUP_DIR.glob("enhanced_settings_backup_*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    backups.append({
                        "name": file.stem,
                        "path": str(file),
                        "date": data.get('_metadata', {}).get('backup_date', ''),
                        "version": data.get('_metadata', {}).get('version', '1.0'),
                        "size": file.stat().st_size
                    })
                except Exception as e:
                    logger.error(f"Error reading backup {file}: {e}")
            
            return sorted(backups, key=lambda x: x['date'], reverse=True)
        return []
    
    def create_profile(self, name, settings):
        """Create a settings profile"""
        profile_file = PROFILES_DIR / f"{name}.json"
        
        profile_data = {
            'name': name,
            'created': datetime.now().isoformat(),
            'settings': settings
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        return str(profile_file)
    
    def get_profiles(self):
        """Get all available profiles"""
        if PROFILES_DIR.exists():
            profiles = []
            for file in PROFILES_DIR.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        profile = json.load(f)
                    
                    profiles.append({
                        'name': profile.get('name', file.stem),
                        'created': profile.get('created', ''),
                        'path': str(file)
                    })
                except Exception as e:
                    logger.error(f"Error reading profile {file}: {e}")
            
            return profiles
        return []
    
    def apply_profile(self, profile_name):
        """Apply a settings profile"""
        profile_file = PROFILES_DIR / f"{profile_name}.json"
        
        if not profile_file.exists():
            return False
        
        try:
            with open(profile_file, 'r') as f:
                profile = json.load(f)
            
            settings = profile.get('settings', {})
            return self.save_enhanced_settings(settings)
        except Exception as e:
            logger.error(f"Error applying profile {profile_name}: {e}")
            return False

# Initialize settings manager
settings_manager_instance = SettingsManager()

# API Routes
@settings_manager.route('/config', methods=['GET'])
def get_config():
    """Get current enhanced configuration"""
    try:
        settings = settings_manager_instance.get_enhanced_settings()
        return jsonify({
            "success": True,
            "data": settings,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/config', methods=['POST'])
def update_config():
    """Update enhanced configuration"""
    try:
        new_settings = request.get_json()
        
        if not new_settings:
            return jsonify({
                "success": False,
                "error": "No settings provided"
            }), 400
        
        if settings_manager_instance.save_enhanced_settings(new_settings):
            return jsonify({
                "success": True,
                "message": "Settings updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save settings"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/config/reset', methods=['POST'])
def reset_config():
    """Reset to default configuration"""
    try:
        settings_manager_instance.create_backup()
        settings_manager_instance.save_enhanced_settings(
            settings_manager_instance.get_default_enhanced_settings()
        )
        return jsonify({
            "success": True,
            "message": "Settings reset to defaults"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/backups', methods=['GET'])
def list_backups():
    """List available backups"""
    try:
        backups = settings_manager_instance.get_backups()
        return jsonify({
            "success": True,
            "data": backups
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/backups', methods=['POST'])
def create_backup():
    """Create manual backup"""
    try:
        backup_path = settings_manager_instance.create_backup()
        if backup_path:
            return jsonify({
                "success": True,
                "backup_path": backup_path
            })
        return jsonify({
            "success": False,
            "error": "No settings to backup"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/backups/<backup_name>/restore', methods=['POST'])
def restore_backup(backup_name):
    """Restore from backup"""
    try:
        backup_file = BACKUP_DIR / f"{backup_name}.json"
        if not backup_file.exists():
            return jsonify({
                "success": False,
                "error": "Backup not found"
            }), 404
        
        settings_manager_instance.create_backup()
        
        with open(backup_file, 'r') as f:
            settings = json.load(f)
        
        # Remove metadata if present
        if '_metadata' in settings:
            del settings['_metadata']
        
        settings_manager_instance.save_enhanced_settings(settings)
        
        return jsonify({
            "success": True,
            "message": "Settings restored from backup"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/profiles', methods=['GET'])
def list_profiles():
    """List available profiles"""
    try:
        profiles = settings_manager_instance.get_profiles()
        return jsonify({
            "success": True,
            "data": profiles
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/profiles', methods=['POST'])
def create_profile():
    """Create new profile"""
    try:
        data = request.get_json()
        name = data.get('name')
        settings = data.get('settings')
        
        if not name or not settings:
            return jsonify({
                "success": False,
                "error": "Name and settings required"
            }), 400
        
        profile_path = settings_manager_instance.create_profile(name, settings)
        return jsonify({
            "success": True,
            "profile_path": profile_path
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/profiles/<profile_name>/apply', methods=['POST'])
def apply_profile(profile_name):
    """Apply profile settings"""
    try:
        if settings_manager_instance.apply_profile(profile_name):
            return jsonify({
                "success": True,
                "message": f"Profile '{profile_name}' applied successfully"
            })
        return jsonify({
            "success": False,
            "error": "Failed to apply profile"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@settings_manager.route('/validate', methods=['POST'])
def validate_settings():
    """Validate settings configuration"""
    try:
        settings = request.get_json()
        validated = settings_manager_instance.validate_settings(settings)
        
        return jsonify({
            "success": True,
            "valid": True,
            "validated_settings": validated
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
