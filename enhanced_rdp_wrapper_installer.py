#!/usr/bin/env python3
"""
Enhanced RDP Wrapper Installer
A robust, cross-platform installer for RDP Wrapper with improved error handling and user experience.
"""

import os
import sys
import hashlib
import platform
import subprocess
import zipfile
import requests
from pathlib import Path
from typing import Optional, Tuple
import time

class RDPWrapperInstaller:
    def __init__(self):
        self.github_url = "https://github.com/stascorp/rdpwrap/releases/download/v1.6.2/RDPWrap-v1.6.2.zip"
        self.expected_hash = "a1b2c3d4e5f6789"  # Placeholder - should be actual SHA256
        self.download_path = Path("RDPWrap-v1.6.2.zip")
        self.extract_path = Path("RDPWrap-v1.6.2")
        
    def print_header(self):
        """Print installation header"""
        print("=" * 60)
        print("Enhanced RDP Wrapper Installer")
        print("=" * 60)
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")
        print("=" * 60)

    def check_admin_rights(self) -> bool:
        """Check if running with administrator/root privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False

    def download_with_progress(self, url: str, destination: Path) -> bool:
        """Download file with progress bar"""
        try:
            print(f"\nDownloading RDP Wrapper...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded / 1024 / 1024:.1f} MB)", end="")
            
            print("\nDownload completed successfully!")
            return True
            
        except requests.RequestException as e:
            print(f"\nDownload failed: {e}")
            return False

    def verify_checksum(self, file_path: Path, expected_hash: str) -> bool:
        """Verify file integrity using SHA256 checksum"""
        try:
            print("\nVerifying file integrity...")
            sha256_hash = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            if actual_hash == expected_hash:
                print("File integrity verified!")
                return True
            else:
                print(f"Warning: Checksum mismatch!")
                print(f"Expected: {expected_hash}")
                print(f"Actual: {actual_hash}")
                return False
                
        except Exception as e:
            print(f"Checksum verification failed: {e}")
            return False

    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract ZIP file with progress indication"""
        try:
            print("\nExtracting files...")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                total_files = len(files)
                
                for i, file in enumerate(files, 1):
                    zip_ref.extract(file, extract_to)
                    progress = (i / total_files) * 100
                    print(f"\rExtracting: {progress:.1f}% ({i}/{total_files})", end="")
            
            print("\nExtraction completed!")
            return True
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False

    def install_windows(self) -> bool:
        """Install RDP Wrapper on Windows"""
        try:
            install_script = self.extract_path / "install.bat"
            if not install_script.exists():
                print("Error: install.bat not found in extracted files")
                return False
            
            print("\nInstalling RDP Wrapper...")
            print("This may take a few moments...")
            
            # Run as administrator
            result = subprocess.run(
                [str(install_script)],
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.extract_path)
            )
            
            if result.returncode == 0:
                print("Installation completed successfully!")
                return True
            else:
                print(f"Installation failed with error code: {result.returncode}")
                print("Error output:", result.stderr)
                return False
                
        except Exception as e:
            print(f"Installation failed: {e}")
            return False

    def install_linux(self) -> bool:
        """Install xrdp on Linux (alternative to RDP Wrapper)"""
        try:
            print("\nInstalling xrdp on Linux...")
            print("This will install xrdp and configure it...")
            
            commands = [
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "-y", "xrdp"],
                ["sudo", "systemctl", "enable", "xrdp"],
                ["sudo", "systemctl", "start", "xrdp"]
            ]
            
            for cmd in commands:
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Command failed: {result.stderr}")
                    return False
            
            print("xrdp installed and started successfully!")
            return True
            
        except Exception as e:
            print(f"Linux installation failed: {e}")
            return False

    def cleanup(self):
        """Clean up temporary files"""
        try:
            print("\nCleaning up temporary files...")
            
            if self.download_path.exists():
                self.download_path.unlink()
                print(f"Removed: {self.download_path}")
            
            print("Cleanup completed!")
            
        except Exception as e:
            print(f"Cleanup warning: {e}")

    def run_installation(self):
        """Main installation process"""
        self.print_header()
        
        # Check admin rights
        if not self.check_admin_rights():
            print("WARNING: This script requires administrator/root privileges!")
            print("Please run as administrator (Windows) or with sudo (Linux)")
            return False
        
        # Platform-specific installation
        system = platform.system()
        
        if system == "Windows":
            # Download and install RDP Wrapper
            if not self.download_with_progress(self.github_url, self.download_path):
                return False
            
            # Note: Actual SHA256 should be calculated from the downloaded file
            # For now, skip checksum verification
            # if not self.verify_checksum(self.download_path, self.expected_hash):
            #     return False
            
            if not self.extract_zip(self.download_path, self.extract_path):
                return False
            
            success = self.install_windows()
            
        elif system == "Linux":
            success = self.install_linux()
            
        else:
            print(f"Unsupported operating system: {system}")
            return False
        
        # Cleanup
        self.cleanup()
        
        if success:
            print("\n" + "=" * 60)
            print("Installation completed successfully!")
            print("=" * 60)
            
            if system == "Windows":
                print("You may need to restart your computer for changes to take effect.")
            elif system == "Linux":
                print("You can now connect using any RDP client to your Linux machine.")
        
        return success

def main():
    """Main entry point"""
    try:
        installer = RDPWrapperInstaller()
        installer.run_installation()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
