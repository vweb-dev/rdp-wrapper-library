#!/usr/bin/env python3
"""
Enhanced RDP Wrapper Installer
Powered by VWEB.DEV
Standalone Windows Executable
"""

import os
import sys
import subprocess
import requests
import zipfile
import shutil
import ctypes
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
import platform
import winreg
from pathlib import Path
import socket
import time

class RDPWrapperInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced RDP Wrapper Installer")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Set icon (will be embedded in exe)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        self.setup_ui()
        self.check_admin()
        self.check_windows_version()
        
    def setup_ui(self):
        """Create modern UI with VWEB.DEV branding"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header frame
        header = tk.Frame(self.root, bg="#1a1a1a", height=100)
        header.pack(fill=tk.X)
        
        # Title
        title = tk.Label(header, text="Enhanced RDP Wrapper Installer", 
                        font=("Segoe UI", 18, "bold"), fg="white", bg="#1a1a1a")
        title.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(header, text="Powered by VWEB.DEV - Advanced RDP Configuration", 
                           font=("Segoe UI", 11), fg="#888", bg="#1a1a1a")
        subtitle.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # System info frame
        info_frame = tk.LabelFrame(main_frame, text="System Information", 
                                 font=("Segoe UI", 10, "bold"), bg="#f8f9fa")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.system_label = tk.Label(info_frame, text="Checking system...", 
                                   font=("Segoe UI", 9), bg="#f8f9fa")
        self.system_label.pack(pady=5)
        
        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Installation Status", 
                                   font=("Segoe UI", 10, "bold"), bg="#f8f9fa")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.status_text = tk.Text(status_frame, height=12, width=70, 
                                 font=("Consolas", 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Progress label
        self.progress_label = tk.Label(main_frame, text="Ready", 
                                     font=("Segoe UI", 9), bg="#f8f9fa")
        self.progress_label.pack()
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#f8f9fa")
        button_frame.pack(fill=tk.X, pady=10)
        
        button_style = {"width": 15, "font": ("Segoe UI", 10)}
        
        self.install_btn = ttk.Button(button_frame, text="Install", 
                                    command=self.install_rdp_wrapper, **button_style)
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.uninstall_btn = ttk.Button(button_frame, text="Uninstall", 
                                      command=self.uninstall_rdp_wrapper, **button_style)
        self.uninstall_btn.pack(side=tk.LEFT, padx=5)
        
        self.check_btn = ttk.Button(button_frame, text="Check Status", 
                                  command=self.check_status, **button_style)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.backup_btn = ttk.Button(button_frame, text="Backup", 
                                   command=self.backup_config, **button_style)
        self.backup_btn.pack(side=tk.LEFT, padx=5)
        
        self.restore_btn = ttk.Button(button_frame, text="Restore", 
                                    command=self.restore_config, **button_style)
        self.restore_btn.pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer = tk.Frame(self.root, bg="#1a1a1a", height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(footer, text="© 2024 VWEB.DEV - Enhanced RDP Wrapper v2.0", 
                               font=("Segoe UI", 9), fg="#666", bg="#1a1a1a")
        footer_label.pack(pady=5)
        
    def check_admin(self):
        """Check if running as administrator"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                self.log_status("⚠️ Warning: Not running as administrator. Some features may not work.")
            return is_admin
        except:
            return False
            
    def check_windows_version(self):
        """Check Windows version compatibility"""
        try:
            win_version = platform.win32_ver()
            version_info = f"Windows {win_version[0]} {win_version[1]}"
            
            # Check compatibility
            supported_versions = ['10', '11', '8.1', '8', '7']
            is_supported = any(ver in win_version[0] for ver in supported_versions)
            
            status = "✅ Supported" if is_supported else "⚠️ May not be fully supported"
            self.system_label.config(text=f"{version_info} - {status}")
            
            return is_supported
        except Exception as e:
            self.system_label.config(text=f"Error checking version: {str(e)}")
            return False
            
    def log_status(self, message):
        """Add message to status log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def update_progress(self, value, message=""):
        """Update progress bar and label"""
        self.progress['value'] = value
        if message:
            self.progress_label.config(text=message)
        self.root.update()
        
    def download_file(self, url, filename):
        """Download file with progress and error handling"""
        try:
            self.log_status(f"📥 Downloading: {filename}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.update_progress(progress, f"Downloading... {progress:.1f}%")
                            
            self.log_status(f"✅ Downloaded: {filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_status(f"❌ Download failed: {str(e)}")
            return False
            
    def get_latest_release_url(self):
        """Get the latest RDP Wrapper release URL"""
        try:
            api_url = "https://api.github.com/repos/stascorp/rdpwrap/releases/latest"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            for asset in data.get('assets', []):
                if asset['name'].endswith('.zip'):
                    return asset['browser_download_url']
                    
            return "https://github.com/stascorp/rdpwrap/releases/download/v1.6.2/RDPWrap-v1.6.2.zip"
        except:
            return "https://github.com/stascorp/rdpwrap/releases/download/v1.6.2/RDPWrap-v1.6.2.zip"
            
    def configure_firewall(self):
        """Configure Windows Firewall for RDP"""
        try:
            self.log_status("🔧 Configuring Windows Firewall...")
            
            # Allow RDP through firewall
            commands = [
                'netsh advfirewall firewall add rule name="RDP Wrapper" dir=in action=allow protocol=TCP localport=3389',
                'netsh advfirewall firewall add rule name="RDP Wrapper" dir=out action=allow protocol=TCP localport=3389'
            ]
            
            for cmd in commands:
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                
            self.log_status("✅ Firewall configured for RDP")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_status(f"⚠️ Firewall configuration failed: {str(e)}")
            return False
            
    def backup_config(self):
        """Backup current RDP Wrapper configuration"""
        try:
            self.log_status("💾 Creating backup...")
            
            backup_dir = Path.home() / "Documents" / "RDPWrapperBackup"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"rdpwrap_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Backup files
            install_dir = Path("C:\\Program Files\\RDP Wrapper")
            if install_dir.exists():
                for file in ["rdpwrap.ini", "rdpwrap.dll"]:
                    src = install_dir / file
                    if src.exists():
                        shutil.copy2(src, backup_path / file)
                        
            self.log_status(f"✅ Backup created: {backup_path}")
            messagebox.showinfo("Backup Complete", f"Configuration backed up to:\n{backup_path}")
            
        except Exception as e:
            self.log_status(f"❌ Backup failed: {str(e)}")
            messagebox.showerror("Backup Failed", str(e))
            
    def restore_config(self):
        """Restore RDP Wrapper configuration from backup"""
        try:
            backup_dir = Path.home() / "Documents" / "RDPWrapperBackup"
            if not backup_dir.exists():
                messagebox.showwarning("No Backup", "No backup found!")
                return
                
            # Find latest backup
            backups = list(backup_dir.glob("rdpwrap_backup_*"))
            if not backups:
                messagebox.showwarning("No Backup", "No backup found!")
                return
                
            latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
            
            # Restore files
            install_dir = Path("C:\\Program Files\\RDP Wrapper")
            if install_dir.exists():
                for file in ["rdpwrap.ini", "rdpwrap.dll"]:
                    src = latest_backup / file
                    if src.exists():
                        shutil.copy2(src, install_dir / file)
                        
            self.log_status(f"✅ Configuration restored from: {latest_backup}")
            messagebox.showinfo("Restore Complete", "Configuration restored successfully!")
            
        except Exception as e:
            self.log_status(f"❌ Restore failed: {str(e)}")
            messagebox.showerror("Restore Failed", str(e))
            
    def update_ini_file(self, ini_path):
        """Update rdpwrap.ini with enhanced configuration"""
        try:
            enhanced_config = """[Main]
Updated=2024-01-01
LogLevel=2
SLPolicy=0
SLPolicyOffset=0

[SLPolicy]
TerminalServices-RemoteConnectionManager-AllowRemoteConnections=1
TerminalServices-RemoteConnectionManager-AllowMultipleSessions=1
TerminalServices-RemoteConnectionManager-AllowAppServerMode=1
TerminalServices-RemoteConnectionManager-AllowMultimon=1
TerminalServices-RemoteConnectionManager-MaxUserSessions=0
TerminalServices-RemoteConnectionManager-ce0ad219-4670-4f8f-92df-08d0c7f847b6-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=2
TerminalServices-RDP-7-Advanced-Compression-Allowed=1
TerminalServices-RDP-7-Advanced-Compression-Allowed-Admin=1
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-LocalOnly=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-LocalOnly=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-LocalOnly=0
TerminalServices-RemoteConnectionManager-42b2631e-1f93-4b5b-8c55-5f56024b4d4e-MaxSessions=0
TerminalServices-RemoteConnectionManager-42b2631e-1f93-4b5b-8c55-5f56024b4d4e-LocalOnly=0
"""
            
            with open(ini_path, 'w') as f:
                f.write(enhanced_config)
                
            self.log_status("✅ Configuration updated with enhanced settings")
            
        except Exception as e:
            self.log_status(f"❌ Configuration update failed: {str(e)}")
            
    def install_rdp_wrapper(self):
        """Main installation process"""
        def install_thread():
            try:
                self.update_progress(0, "Starting installation...")
                self.log_status("🚀 Starting Enhanced RDP Wrapper installation...")
                
                # Check if already installed
                install_dir = Path("C:\\Program Files\\RDP Wrapper")
                if install_dir.exists():
                    result = messagebox.askyesno("Already Installed", 
                                               "RDP Wrapper appears to be already installed. Reinstall?")
                    if not result:
                        return
                
                # Get download URL
                download_url = self.get_latest_release_url()
                self.log_status(f"📥 Download URL: {download_url}")
                
                # Download
                self.update_progress(10, "Downloading RDP Wrapper...")
                if not self.download_file(download_url, "rdpwrap.zip"):
                    return
                
                # Create installation directory
                self.update_progress(30, "Preparing installation...")
                install_dir.mkdir(parents=True, exist_ok=True)
                
                # Extract files
                self.update_progress(50, "Extracting files...")
                with zipfile.ZipFile("rdpwrap.zip", 'r') as zip_ref:
                    zip_ref.extractall(str(install_dir))
                
                # Install service
                self.update_progress(70, "Installing service...")
                installer_path = install_dir / "install.bat"
                if installer_path.exists():
                    subprocess.run([str(installer_path)], shell=True, check=True)
                
                # Update configuration
                self.update_progress(80, "Updating configuration...")
                ini_path = install_dir / "rdpwrap.ini"
                if ini_path.exists():
                    self.update_ini_file(str(ini_path))
                
                # Configure firewall
                self.update_progress(90, "Configuring firewall...")
                self.configure_firewall()
                
                # Final checks
                self.update_progress(100, "Installation complete!")
                self.log_status("✅ Installation completed successfully!")
                self.log_status("🎉 RDP Wrapper is now active on your system!")
                
                # Clean up
                Path("rdpwrap.zip").unlink(missing_ok=True)
                
                messagebox.showinfo("Success", "Enhanced RDP Wrapper installed successfully!")
                
            except Exception as e:
                self.update_progress(0, "Installation failed")
                self.log_status(f"❌ Installation failed: {str(e)}")
                messagebox.showerror("Installation Failed", str(e))
                
        threading.Thread(target=install_thread, daemon=True).start()
        
    def uninstall_rdp_wrapper(self):
        """Uninstall RDP Wrapper"""
        def uninstall_thread():
            try:
                self.log_status("🗑️ Starting uninstallation...")
                
                install_dir = Path("C:\\Program Files\\RDP Wrapper")
                uninstaller_path = install_dir / "uninstall.bat"
                
                if uninstaller_path.exists():
                    subprocess.run([str(uninstaller_path)], shell=True, check=True)
                    self.log_status("✅ Service uninstalled")
                else:
                    self.log_status("⚠️ Uninstaller not found")
                
                # Clean up files
                if install_dir.exists():
                    shutil.rmtree(install_dir)
                    self.log_status("✅ Files removed")
                
                messagebox.showinfo("Uninstall Complete", "RDP Wrapper has been uninstalled")
                
            except Exception as e:
                self.log_status(f"❌ Uninstall failed: {str(e)}")
                messagebox.showerror("Uninstall Failed", str(e))
                
        threading.Thread(target=uninstall_thread, daemon=True).start()
        
    def check_status(self):
        """Check RDP Wrapper status"""
        def check_thread():
            try:
                self.log_status("🔍 Checking RDP Wrapper status...")
                
                # Check service status
                result = subprocess.run(["sc", "query", "rdpwrap"], 
                                      capture_output=True, text=True, shell=True)
                
                if "RUNNING" in result.stdout:
                    self.log_status("✅ RDP Wrapper service is running")
                elif "STOPPED" in result.stdout:
                    self.log_status("⚠️ RDP Wrapper service is stopped")
                else:
                    self.log_status("❌ RDP Wrapper service not found")
                
                # Check RDP port
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('127.0.0.1', 3389))
                    sock.close()
                    
                    if result == 0:
                        self.log_status("✅ RDP port 3389 is open")
                    else:
                        self.log_status("⚠️ RDP port 3389 is closed")
                except:
                    self.log_status("❌ Cannot check RDP port")
                
                self.log_status("🔍 Status check complete")
                
            except Exception as e:
                self.log_status(f"❌ Status check failed: {str(e)}")
                
        threading.Thread(target=check_thread, daemon=True).start()
        
    def run(self):
        """Start the application"""
        self.log_status("🎯 Enhanced RDP Wrapper Installer started")
        self.log_status("📋 Ready to install RDP Wrapper")
        self.root.mainloop()

if __name__ == "__main__":
    # Ensure we're on Windows
    if platform.system() != "Windows":
        print("This installer only works on Windows")
        sys.exit(1)
        
    app = RDPWrapperInstaller()
    app.run()
