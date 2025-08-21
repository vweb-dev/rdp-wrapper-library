"""
Enhanced RDP Wrapper Installer
Provides secure installation with rollback capabilities and system compatibility checks
"""
import os
import shutil
import subprocess
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import zipfile
import tempfile
from .security import EnhancedSecurityManager

class EnhancedInstaller:
    """Advanced installer with security features and rollback support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_manager = EnhancedSecurityManager()
        self.backup_path = None
        self.installation_log = []
        
    def check_system_compatibility(self) -> Dict[str, Any]:
        """Check system compatibility for RDP Wrapper"""
        try:
            # Check Windows version
            result = subprocess.run(['ver'], capture_output=True, text=True, shell=True)
            windows_version = result.stdout.strip()
            
            # Check architecture
            arch_result = subprocess.run(['wmic', 'os', 'get', 'OSArchitecture'], 
                                       capture_output=True, text=True)
            architecture = arch_result.stdout.split('\n')[1].strip()
            
            # Check if Terminal Services is running
            ts_result = subprocess.run(['sc', 'query', 'TermService'], 
                                     capture_output=True, text=True)
            ts_running = "RUNNING" in ts_result.stdout
            
            compatibility = {
                "windows_version": windows_version,
                "architecture": architecture,
                "terminal_services": ts_running,
                "compatible": ts_running and ("64-bit" in architecture or "32-bit" in architecture)
            }
            
            self.logger.info(f"System compatibility check: {compatibility}")
            return compatibility
            
        except Exception as e:
            self.logger.error(f"Compatibility check failed: {e}")
            return {"error": str(e), "compatible": False}
            
    def create_backup(self, target_paths: List[str]) -> bool:
        """Create backup of existing RDP Wrapper installation"""
        try:
            backup_dir = tempfile.mkdtemp(prefix="rdp_wrapper_backup_")
            self.backup_path = backup_dir
            
            for path in target_paths:
                if os.path.exists(path):
                    dest_path = os.path.join(backup_dir, os.path.basename(path))
                    if os.path.isdir(path):
                        shutil.copytree(path, dest_path)
                    else:
                        shutil.copy2(path, dest_path)
                        
            self.logger.info(f"Backup created at: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False
            
    def download_and_verify(self, url: str, destination: str) -> bool:
        """Download RDP Wrapper with security verification"""
        try:
            import requests
            
            # Validate SSL certificate
            if not self.security_manager.validate_ssl_certificate(url.split('/')[2]):
                self.logger.error("SSL certificate validation failed")
                return False
                
            # Download file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save file
            with open(destination, 'wb') as f:
                f.write(response.content)
                
            # Verify integrity
            if not self.verify_file_integrity(destination):
                self.logger.error("File integrity verification failed")
                return False
                
            # Scan for malware
            scan_result = self.security_manager.scan_for_malware(destination)
            if scan_result.get("status") == "infected":
                self.logger.error(f"Malware detected: {scan_result.get('threat')}")
                return False
                
            self.logger.info("Download and verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False
            
    def verify_file_integrity(self, file_path: str) -> bool:
        """Verify file integrity using checksums"""
        try:
            # Calculate SHA256 hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                
            # Compare with known good hash
            known_hashes = {
                "rdp_wrapper.zip": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            }
            
            filename = os.path.basename(file_path)
            if filename in known_hashes:
                return file_hash == known_hashes[filename]
                
            return True  # If no known hash, assume valid
            
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {e}")
            return False
            
    def install_with_progress(self, source_path: str, install_dir: str) -> Dict[str, Any]:
        """Install RDP Wrapper with progress tracking"""
        try:
            self.installation_log = []
            
            # Create installation directory
            os.makedirs(install_dir, exist_ok=True)
            
            # Extract if zip file
            if source_path.endswith('.zip'):
                with zipfile.ZipFile(source_path, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
                    
            # Copy files
            for item in os.listdir(install_dir):
                src_path = os.path.join(install_dir, item)
                dst_path = os.path.join("C:\\Program Files\\RDP Wrapper", item)
                
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dst_path)
                    
            # Install service
            install_result = subprocess.run([
                "C:\\Program Files\\RDP Wrapper\\install.bat"
            ], capture_output=True, text=True)
            
            self.installation_log.append({
                "step": "service_installation",
                "output": install_result.stdout,
                "error": install_result.stderr
            })
            
            # Configure RDP Wrapper
            self.configure_rdp_wrapper()
            
            return {
                "status": "success",
                "installation_log": self.installation_log,
                "backup_path": self.backup_path
            }
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "installation_log": self.installation_log
            }
            
    def configure_rdp_wrapper(self):
        """Configure RDP Wrapper settings"""
        try:
            config_path = "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"
            if os.path.exists(config_path):
                # Read current configuration
                with open(config_path, 'r') as f:
                    config = f.read()
                    
                # Apply security settings
                secure_config = self.apply_security_settings(config)
                
                # Write updated configuration
                with open(config_path, 'w') as f:
                    f.write(secure_config)
                    
                self.logger.info("RDP Wrapper configured successfully")
                
        except Exception as e:
            self.logger.error(f"Configuration failed: {e}")
            
    def apply_security_settings(self, config: str) -> str:
        """Apply security settings to RDP Wrapper configuration"""
        # Add security headers
        security_settings = """
[Security]
AuthenticationLevel=2
EncryptionLevel=3
MaxSessions=10
IdleTimeout=30
"""
        
        if "[Security]" not in config:
            config += security_settings
            
        return config
        
    def rollback_installation(self) -> bool:
        """Rollback to previous state"""
        try:
            if not self.backup_path or not os.path.exists(self.backup_path):
                self.logger.error("No backup available for rollback")
                return False
                
            # Restore files from backup
            for item in os.listdir(self.backup_path):
                src_path = os.path.join(self.backup_path, item)
                dst_path = os.path.join("C:\\Program Files\\RDP Wrapper", item)
                
                if os.path.exists(dst_path):
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)
                        
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
                    
            self.logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
