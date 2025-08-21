"""
Enhanced RDP Wrapper Configuration Management
Handles configuration files, settings, and environment variables
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages RDP Wrapper configuration and settings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path("C:\\ProgramData\\RDP Wrapper Enhanced")
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}")
            
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "security": {
                "enable_encryption": True,
                "require_authentication": True,
                "max_sessions": 10,
                "idle_timeout": 30,
                "block_external_connections": False,
                "allowed_users": [],
                "blocked_users": []
            },
            "performance": {
                "enable_compression": True,
                "max_color_depth": 32,
                "enable_font_smoothing": True,
                "enable_desktop_composition": True
            },
            "logging": {
                "level": "INFO",
                "max_file_size": "10MB",
                "max_files": 5,
                "log_connections": True,
                "log_failures": True
            },
            "updates": {
                "auto_check": True,
                "auto_install": False,
                "check_interval": 86400  # 24 hours
            },
            "network": {
                "port": 3389,
                "bind_address": "0.0.0.0",
                "enable_ipv6": False
            }
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Merge with defaults
                default_config = self.get_default_config()
                return self.merge_configs(default_config, config)
            else:
                # Create default config
                config = self.get_default_config()
                self.save_config(config)
                return config
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self.get_default_config()
            
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
            
    def merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults"""
        merged = default.copy()
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
        
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get specific setting value"""
        config = self.load_config()
        return config.get(section, {}).get(key, default)
        
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """Set specific setting value"""
        config = self.load_config()
        if section not in config:
            config[section] = {}
        config[section][key] = value
        return self.save_config(config)
        
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration values"""
        errors = []
        
        # Validate security settings
        security = config.get("security", {})
        if security.get("max_sessions", 0) < 1 or security.get("max_sessions", 0) > 100:
            errors.append("max_sessions must be between 1 and 100")
            
        if security.get("idle_timeout", 0) < 1 or security.get("idle_timeout", 0) > 1440:
            errors.append("idle_timeout must be between 1 and 1440 minutes")
            
        # Validate network settings
        network = config.get("network", {})
        port = network.get("port", 3389)
        if port < 1 or port > 65535:
            errors.append("port must be between 1 and 65535")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
