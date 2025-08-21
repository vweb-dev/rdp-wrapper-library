"""
Configuration Manager for RDP Wrapper
Handles configuration backup, modification, and restoration
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any
import platform
import subprocess

class ConfigManager:
    def __init__(self):
        self.config_path = Path("rdp_wrapper_config.json")
        self.backup_dir = Path("rdp_wrapper_backups")
        
    def create_backup(self) -> bool:
        """Create backup of current RDP configuration"""
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            if platform.system() == "Windows":
                return self._backup_windows()
            else:
                return self._backup_linux()
                
        except Exception as e:
            print(f"Backup creation failed: {e}")
            return False
    
    def _backup_windows(self) -> bool:
        """Backup Windows RDP configuration"""
        try:
            # Backup RDP Wrapper files
            rdpwrap_path = Path("C:/Program Files/RDP Wrapper")
            if rdpwrap_path.exists():
                backup_path = self.backup_dir / f"rdpwrap_backup_{int(time.time())}"
                shutil.copytree(rdpwrap_path, backup_path)
                
            # Backup registry settings
            reg_backup = self.backup_dir / f"rdp_registry_{int(time.time())}.reg"
            subprocess.run([
                "reg", "export", 
                "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\TermService", 
                str(reg_backup)
            ], check=True)
            
            return True
            
        except Exception as e:
            print(f"Windows backup failed: {e}")
            return False
    
    def _backup_linux(self) -> bool:
        """Backup Linux xrdp configuration"""
        try:
            configs = ["/etc/xrdp/xrdp.ini", "/etc/xrdp/sesman.ini"]
            backup_time = int(time.time())
            
            for config in configs:
                config_path = Path(config)
                if config_path.exists():
                    backup_path = self.backup_dir / f"{config_path.name}_backup_{backup_time}"
                    shutil.copy2(config_path, backup_path)
                    
            return True
            
        except Exception as e:
            print(f"Linux backup failed: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Configuration save failed: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Configuration load failed: {e}")
            return {}
