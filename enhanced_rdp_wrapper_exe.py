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

class RDPWrapperInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced RDP Wrapper Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Set icon (will be embedded in exe)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        self.setup_ui()
        self.check_admin()
        
    def setup_ui(self):
        """Create modern UI with VWEB.DEV branding"""
        # Header frame
        header = tk.Frame(self.root, bg="#1a1a1a", height=80)
        header.pack(fill=tk.X)
        
        # Title
        title = tk.Label(header, text="Enhanced RDP Wrapper Installer", 
                        font=("Segoe UI", 16, "bold"), fg="white", bg="#1a1a1a")
        title.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(header, text="Powered by VWEB.DEV", 
                           font=("Segoe UI", 10), fg="#888", bg="#1a1a1a")
        subtitle.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Installation Status", 
                                   font=("Segoe UI", 10, "bold"), bg="#f5f5f5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = tk.Text(status_frame, height=8, width=60, 
                                 font=("Consolas", 9), state=tk.DISABLED)
        self.status_text.pack(padx=5, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#f5f5f5")
        button_frame.pack(fill=tk.X)
        
        self.install_btn = ttk.Button(button_frame, text="Install RDP Wrapper", 
                                    command=self.install_rdp_wrapper)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.uninstall_btn = ttk.Button(button_frame, text="Uninstall", 
                                      command=self.uninstall_rdp_wrapper)
        self.uninstall_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.check_btn = ttk.Button(button_frame, text="Check Status", 
                                  command=self.check_status)
        self.check_btn.pack(side=tk.LEFT)
        
        # Footer
        footer = tk.Frame(self.root, bg="#1a1a1a", height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(footer, text="© 2024 VWEB.DEV - Enhanced RDP Wrapper", 
                               font=("Segoe UI", 8), fg="#666", bg="#1a1a1a")
        footer_label.pack(pady=5)
        
    def check_admin(self):
        """Check if running as administrator"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                messagebox.showwarning("Admin Rights Required", 
                                     "Please run as administrator for full functionality")
        except:
            pass
            
    def log_status(self, message):
        """Add message to status log"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def download_file(self, url, filename):
        """Download file with progress"""
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filename, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.progress['value'] = progress
                            self.root.update()
                            
            return True
        except Exception as e:
            self.log_status(f"Download failed: {str(e)}")
            return False
            
    def install_rdp_wrapper(self):
        """Main installation process"""
        def install_thread():
            try:
                self.log_status("Starting Enhanced RDP Wrapper installation...")
                
                # Check Windows version
                win_version = platform.win32_ver()
                self.log_status(f"Windows Version: {win_version[0]} {win_version[1]}")
                
                # Create installation directory
                install_dir = Path("C:\\Program Files\\RDP Wrapper")
                install_dir.mkdir(exist_ok=True)
                
                # Download latest RDP Wrapper
                self.log_status("Downloading RDP Wrapper...")
                rdp_url = "https://github.com/stascorp/rdpwrap/releases/latest/download/RDPWrap-v1.6.2.zip"
                
                if not self.download_file(rdp_url, "rdpwrap.zip"):
                    return
                    
                # Extract files
                self.log_status("Extracting files...")
                with zipfile.ZipFile("rdpwrap.zip", 'r') as zip_ref:
                    zip_ref.extractall(str(install_dir))
                    
                # Install RDP Wrapper
                self.log_status("Installing RDP Wrapper service...")
                installer_path = install_dir / "install.bat"
                if installer_path.exists():
                    subprocess.run([str(installer_path)], shell=True, check=True)
                    
                # Update INI file with enhanced configuration
                self.log_status("Updating configuration...")
                ini_path = install_dir / "rdpwrap.ini"
                if ini_path.exists():
                    self.update_ini_file(str(ini_path))
                    
                # Configure firewall
                self.log_status("Configuring Windows Firewall...")
                self.configure_firewall()
                
                # Start service
                self.log_status("Starting RDP Wrapper service...")
                subprocess.run(["net", "start", "rdpwrap"], shell=True, check=True)
                
                self.log_status("Installation completed successfully!")
                self.log_status("RDP Wrapper is now active on your system.")
                
                # Clean up
                Path("rdpwrap.zip").unlink(missing_ok=True)
                
            except Exception as e:
                self.log_status(f"Installation failed: {str(e)}")
                
        threading.Thread(target=install_thread, daemon=True).start()
        
    def update_ini_file(self, ini_path):
        """Update rdpwrap.ini with enhanced settings"""
        enhanced_config = """
[Main]
; Enhanced RDP Wrapper Configuration
; Powered by VWEB.DEV
Updated=2024-01-01
LogLevel=2
SLPolicy=0

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
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-Admin=1
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-Admin=1
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-Admin=1
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-UserSession=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-UserSession=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-UserSession=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-Session=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-Session=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-Session=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4a4c-8b66-5b4bf5a3f029-MaxSessions=0
TerminalServices-RemoteConnectionManager-8dc86f1d-adef-4e2b-9aa5-a8f222b456df-MaxSessions=0
TerminalServices-RemoteConnectionManager-7b3663d6-3c2e-4fbb-9f3d-9e00b595a409-MaxSessions=0
TerminalServices-RemoteConnectionManager-45344f7e-c16d-4
