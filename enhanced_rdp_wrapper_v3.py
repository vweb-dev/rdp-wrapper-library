#!/usr/bin/env python3
"""
Enhanced RDP Wrapper Installer v3.0
Advanced Security & Configuration Management
Powered by VWEB.DEV
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
from tkinter import ttk, messagebox, filedialog
import json
import platform
import winreg
from pathlib import Path
import socket
import time
import hashlib
import base64
from datetime import datetime
import configparser
import traceback
import tempfile
import psutil
import win32security
import win32api
import win32con

class EnhancedRDPWrapperInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced RDP Wrapper Installer v3.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configuration
        self.config = self.load_config()
        self.is_dark_mode = self.config.get('theme', 'light') == 'dark'
        
        # Security settings
        self.verified_sources = [
            "https://github.com/stascorp/rdpwrap",
            "https://raw.githubusercontent.com/rdpwrap/rdpwrap"
        ]
        
        # Setup
        self.setup_logging()
        self.setup_ui()
        self.check_system_compatibility()
        
    def load_config(self):
        """Load user configuration"""
        config_path = Path.home() / ".rdp_wrapper_config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {
            'theme': 'light',
            'auto_backup': True,
            'verify_signatures': True,
            'check_updates': True
        }
        
    def save_config(self):
        """Save user configuration"""
        config_path = Path.home() / ".rdp_wrapper_config.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.log_error(f"Failed to save config: {e}")
            
    def setup_logging(self):
        """Setup advanced logging system"""
        log_dir = Path.home() / "RDPWrapper_Logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"rdp_wrapper_{timestamp}.log"
        
        # Create logger
        import logging
        self.logger = logging.getLogger('RDPWrapper')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def setup_ui(self):
        """Create modern, responsive UI"""
        self.setup_styles()
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
    def setup_styles(self):
        """Setup modern theme styles"""
        self.style = ttk.Style()
        
        # Color schemes
        self.colors = {
            'light': {
                'bg': '#ffffff',
                'fg': '#333333',
                'accent': '#007acc',
                'secondary': '#f0f0f0',
                'border': '#e0e0e0',
                'text': '#2d3748',
                'success': '#38a169',
                'warning': '#d69e2e',
                'error': '#e53e3e'
            },
            'dark': {
                'bg': '#1a1a1a',
                'fg': '#e0e0e0',
                'accent': '#00bcd4',
                'secondary': '#2d2d2d',
                'border': '#404040',
                'text': '#e0e0e0',
                'success': '#4ade80',
                'warning': '#fbbf24',
                'error': '#f87171'
            }
        }
        
        self.current_colors = self.colors['dark' if self.is_dark_mode else 'light']
        
        # Configure styles
        self.root.configure(bg=self.current_colors['bg'])
        
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Log", command=self.export_log)
        file_menu.add_command(label="Import Config", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Network Test", command=self.test_network)
        tools_menu.add_command(label="System Scan", command=self.system_scan)
        tools_menu.add_command(label="Registry Backup", command=self.backup_registry)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(
            label="Dark Mode", 
            variable=tk.BooleanVar(value=self.is_dark_mode),
            command=self.toggle_theme
        )
        settings_menu.add_checkbutton(
            label="Auto Backup",
            variable=tk.BooleanVar(value=self.config.get('auto_backup', True)),
            command=lambda: self.config.update({'auto_backup': not self.config.get('auto_backup', True)})
        )
        
    def create_header(self):
        """Create enhanced header with system info"""
        header = tk.Frame(self.root, bg=self.current_colors['secondary'])
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Title
        title_frame = tk.Frame(header, bg=self.current_colors['secondary'])
        title_frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(
            title_frame, 
            text="Enhanced RDP Wrapper Installer v3.0",
            font=("Segoe UI", 20, "bold"),
            fg=self.current_colors['accent'],
            bg=self.current_colors['secondary']
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Advanced Security & Configuration Management",
            font=("Segoe UI", 11),
            fg=self.current_colors['text'],
            bg=self.current_colors['secondary']
        )
        subtitle.pack()
        
        # System info bar
        info_bar = tk.Frame(header, bg=self.current_colors['bg'], relief=tk.RAISED, bd=1)
        info_bar.pack(fill=tk.X, pady=5, padx=5)
        
        self.system_labels = {}
        info_items = [
            ("OS", self.get_os_info()),
            ("Admin", "Checking..."),
            ("Network", "Checking..."),
            ("RDP Status", "Checking...")
        ]
        
        for i, (label, value) in enumerate(info_items):
            frame = tk.Frame(info_bar, bg=self.current_colors['bg'])
            frame.pack(side=tk.LEFT, padx=10, pady=5)
            
            tk.Label(
                frame,
                text=f"{label}:",
                font=("Segoe UI", 9, "bold"),
                fg=self.current_colors['accent'],
                bg=self.current_colors['bg']
            ).pack(side=tk.LEFT)
            
            self.system_labels[label.lower()] = tk.Label(
                frame,
                text=value,
                font=("Segoe UI", 9),
                fg=self.current_colors['text'],
                bg=self.current_colors['bg']
            )
            self.system_labels[label.lower()].pack(side=tk.LEFT, padx=(5, 0))
            
    def create_main_content(self):
        """Create main content area with tabs"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard()
        
        # Configuration tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.create_config_panel()
        
        # Advanced tab
        self.advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_frame, text="Advanced")
        self.create_advanced_panel()
        
    def create_dashboard(self):
        """Create dashboard with status and actions"""
        # Left panel - Status
        left_frame = tk.Frame(self.dashboard_frame, bg=self.current_colors['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Status section
        status_group = tk.LabelFrame(
            left_frame,
            text="System Status",
            font=("Segoe UI", 11, "bold"),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        status_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.status_text = tk.Text(
            status_group,
            height=15,
            width=50,
            font=("Consolas", 9),
            bg=self.current_colors['secondary'],
            fg=self.current_colors['text'],
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress section
        progress_frame = tk.Frame(left_frame, bg=self.current_colors['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        self.progress_label.pack()
        
        # Right panel - Actions
        right_frame = tk.Frame(self.dashboard_frame, bg=self.current_colors['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Action buttons
        actions_group = tk.LabelFrame(
            right_frame,
            text="Quick Actions",
            font=("Segoe UI", 11, "bold"),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        actions_group.pack(fill=tk.Y, expand=True)
        
        actions = [
            ("Install RDP Wrapper", self.install_rdp_wrapper, "success"),
            ("Uninstall", self.uninstall_rdp_wrapper, "error"),
            ("Check Status", self.check_status, "accent"),
            ("Update", self.update_rdp_wrapper, "warning"),
            ("Backup Config", self.backup_config, "accent"),
            ("Restore Config", self.restore_config, "accent")
        ]
        
        for text, command, color in actions:
            btn = tk.Button(
                actions_group,
                text=text,
                command=command,
                bg=self.current_colors[color],
                fg="white",
                font=("Segoe UI", 10),
                width=20,
                cursor="hand2"
            )
            btn.pack(pady=5, padx=10)
            
    def create_config_panel(self):
        """Create configuration management panel"""
        config_frame = tk.Frame(self.config_frame, bg=self.current_colors['bg'])
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuration editor
        editor_frame = tk.LabelFrame(
            config_frame,
            text="RDP Wrapper Configuration",
            font=("Segoe UI", 11, "bold"),
            bg=self.current_colors['bg'],
            fg=self.current_colors['text']
        )
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text editor for config
        self.config_text = tk.Text(
            editor_frame,
            height=20,
            width=80,
            font=("Consolas", 10),
            bg=self.current_colors['secondary'],
            fg=self.current_colors['text']
        )
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load current config
        self.load_current_config()
        
        # Buttons
        btn_frame = tk.Frame(editor_frame, bg=self.current_colors['bg'])
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            btn_frame,
            text="Load Current",
            command=self.load_current_config,
            bg=self.current_colors['accent'],
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Save Config",
            command=self.save_config_file,
            bg=self.current_colors['success'],
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Apply Changes",
            command=self.apply_config,
            bg=self.current_colors['warning'],
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
    def create_advanced_panel(self):
        """Create advanced tools panel"""
        advanced_frame = tk.Frame(self.advanced_frame, bg=self.current_colors['bg'])
        advanced_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tools grid
        tools = [
            ("Network Test", self.test_network, "Test network connectivity"),
            ("Registry Scan", self.scan_registry, "Scan registry for RDP settings"),
            ("Service Manager", self.manage_services, "Manage RDP services"),
            ("Port Checker", self.check_ports, "Check RDP port availability"),
            ("Firewall Rules", self.manage_firewall, "Configure Windows Firewall"),
            ("System Restore", self.create_restore_point, "Create system restore point")
        ]
        
        for i, (title, command, desc) in enumerate(tools):
            row = i // 2
            col = i % 2
            
            tool_frame = tk.LabelFrame(
                advanced_frame,
                text=title,
                font=("Segoe UI", 10, "bold"),
                bg=self.current_colors['bg'],
                fg=self.current_colors['text']
            )
            tool_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            tk.Label(
                tool_frame,
                text=desc,
                font=("Segoe UI", 9),
                bg=self.current_colors['bg'],
                fg=self.current_colors['text'],
                wraplength=200
            ).pack(pady=5)
            
            tk.Button(
                tool_frame,
                text="Run",
                command=command,
                bg=self.current_colors['accent'],
                fg="white",
                width=15
            ).pack(pady=5)
            
        # Configure grid
        advanced_frame.grid_columnconfigure(0, weight=1)
        advanced_frame.grid_columnconfigure(1, weight=1)
        
    def create_footer(self):
        """Create footer with status bar"""
        footer = tk.Frame(self.root, bg=self.current_colors['secondary'])
        footer.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        # Status bar
        self.status_bar = tk.Label(
            footer,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.current_colors['secondary'],
            fg=self.current_colors['text']
        )
        self.status_bar.pack(side=tk.LEFT, padx=10)
        
        # Version info
        version_label = tk.Label(
            footer,
            text="v3.0 Enhanced",
            font=("Segoe UI", 9),
            bg=self.current_colors['secondary'],
            fg=self.current_colors['text']
        )
        version_label.pack(side=tk.RIGHT, padx=10)
        
    def get_os_info(self):
        """Get detailed OS information"""
        try:
            win_info = platform.win32_ver()
            return f"Windows {win_info[0]} {win_info[2]}"
        except:
            return "Unknown"
            
    def check_system_compatibility(self):
        """Enhanced system compatibility check"""
        try:
            # Check admin rights
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            self.system_labels['admin'].config(
                text="Yes" if is_admin else "No",
                fg=self.current_colors['success'] if is_admin else self.current_colors['error']
            )
            
            # Check network
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                self.system_labels['network'].config(
                    text="Connected",
                    fg=self.current_colors['success']
                )
            except:
                self.system_labels['network'].config(
                    text="No Internet",
                    fg=self.current_colors['error']
                )
                
            # Check RDP status
            self.check_rdp_status()
            
        except Exception as e:
            self.log_error(f"System check error: {e}")
            
    def check_rdp_status(self):
        """Check current RDP wrapper status"""
        try:
            # Check if RDP Wrapper is installed
            rdp_path = Path("C:\\Program Files\\RDP Wrapper")
            if rdp_path.exists():
                self.system_labels['rdp status'].config(
                    text="Installed",
                    fg=self.current_colors['success']
                )
            else:
                self.system_labels['rdp status'].config(
                    text="Not Installed",
                    fg=self.current_colors['warning']
                )
        except:
            self.system_labels['rdp status'].config(text="Unknown")
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.config['theme'] = 'dark' if self.is_dark_mode else 'light'
        self.save_config()
        
        # Update UI
        self.current_colors = self.colors['dark' if self.is_dark_mode else 'light']
        self.setup_ui()
        
    def log_status(self, message, level="INFO"):
        """Enhanced logging with levels"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.config(state=tk.NORMAL)
        
        # Color coding
        color_tags = {
            "ERROR": self.current_colors['error'],
            "WARNING": self.current_colors['warning'],
            "SUCCESS": self.current_colors['success'],
            "INFO": self.current_colors['text']
        }
        
        tag_name = f"color_{level}"
        self.status_text.tag_configure(tag_name, foreground=color_tags.get(level, self.current_colors['text']))
        
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n", tag_name)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # Also log to file
        self.logger.log(getattr(logging, level, logging.INFO), message)
        
    def log_error(self, message):
        """Log error with traceback"""
        self.log_status(message, "ERROR")
        self.logger.error(message, exc_info=True)
        
    def update_progress(self, value, message=""):
        """Update progress bar and label"""
        self.progress['value'] = value
        if message:
            self.progress_label.config(text=message)
            self.status_bar.config(text=message)
        self.root.update()
        
    def verify_download(self, file_path, expected_hash):
        """Verify downloaded file integrity"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            actual_hash = sha256_hash.hexdigest()
            return actual_hash == expected_hash
        except Exception as e:
            self.log_error(f"Hash verification failed: {e}")
            return False
            
    def download_file(self, url, filename, expected_hash=None):
        """Enhanced download with verification"""
        try:
            self.log_status(f"📥 Downloading: {filename}")
            
            # Verify URL
            if not any(source in url for source in self.verified_sources):
                self.log_status("⚠️ Warning: Downloading from unverified source", "WARNING")
                
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
                            
            # Verify if hash provided
            if expected_hash and not self.verify_download(filename, expected_hash):
                self.log_status("❌ Download verification failed", "ERROR")
                return False
                
            self.log_status(f"✅ Downloaded: {filename}", "SUCCESS")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_status(f"❌ Download failed: {str(e)}", "ERROR")
            return False
            
    def get_latest_release_info(self):
        """Get latest release information with security checks"""
        try:
            api_url = "https://api.github.com/repos/stascorp/rdpwrap/releases/latest"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Find zip asset
            zip_asset = None
            for asset in data.get('assets', []):
                if asset['name'].endswith('.zip'):
                    zip_asset = asset
                    break
                    
            if not zip_asset:
                return None
                
            return {
                'version': data['tag_name'],
                'download_url': zip_asset['browser_download_url'],
                'size': zip_asset['size'],
                'published': data['published_at']
            }
            
        except Exception as e:
            self.log_error(f"Failed to get release info: {e}")
            return None
            
    def install_rdp_wrapper(self):
        """Enhanced installation with security checks"""
        if not self.check_admin_rights():
            messagebox.showerror("Admin Required", "Please run as administrator")
            return
            
        try:
            self.update_progress(0, "Starting installation...")
            
            # Create restore point
            if self.config.get('auto_backup', True):
                self.create_restore_point()
                
            # Get latest release
            release_info = self.get_latest_release_info()
            if not release_info:
                self.log_status("❌ Failed to get release information", "ERROR")
                return
                
            # Download
            zip_path = "rdp_wrapper_latest.zip"
            if not self.download_file(release_info['download_url'], zip_path):
                return
                
            # Extract
            self.update_progress(60, "Extracting files...")
            extract_dir = "rdp_wrapper_temp"
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Install
            self.update_progress(80, "Installing RDP Wrapper...")
            installer_path = Path(extract_dir) / "install.bat"
            if installer_path.exists():
                result = subprocess.run(
                    [str(installer_path)],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0:
                    self.log_status("✅ RDP Wrapper installed successfully", "SUCCESS")
                else:
                    self.log_status(f"❌ Installation failed: {result.stderr}", "ERROR")
                    
            # Cleanup
            self.update_progress(100, "Cleaning up...")
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
                
            self.check_rdp_status()
            
        except Exception as e:
            self.log_error(f"Installation error: {e}")
            
    def uninstall_rdp_wrapper(self):
        """Enhanced uninstallation with cleanup"""
        if not messagebox.askyesno("Confirm", "Are you sure you want to uninstall RDP Wrapper?"):
            return
            
        try:
            self.update_progress(0, "Starting uninstallation...")
            
            # Find uninstaller
            uninstall_paths = [
                "C:\\Program Files\\RDP Wrapper\\uninstall.bat",
                "C:\\Program Files (x86)\\RDP Wrapper\\uninstall.bat"
            ]
            
            uninstalled = False
            for path in uninstall_paths:
                if os.path.exists(path):
                    result = subprocess.run(
                        [path],
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                    
                    if result.returncode == 0:
                        self.log_status("✅ RDP Wrapper uninstalled successfully", "SUCCESS")
                        uninstalled = True
                        break
                        
            if not uninstalled:
                # Manual cleanup
                self.log_status("Performing manual cleanup...")
                self.cleanup_rdp_wrapper()
                
            self.check_rdp_status()
            
        except Exception as e:
            self.log_error(f"Uninstallation error: {e}")
            
    def cleanup_rdp_wrapper(self):
        """Manual cleanup of RDP Wrapper files"""
        try:
            paths_to_remove = [
                "C:\\Program Files\\RDP Wrapper",
                "C:\\Program Files (x86)\\RDP Wrapper"
            ]
            
            for path in paths_to_remove:
                if os.path.exists(path):
                    shutil.rmtree(path)
                    self.log_status(f"Removed: {path}")
                    
        except Exception as e:
            self.log_error(f"Cleanup error: {e}")
            
    def check_status(self):
        """Enhanced status check"""
        try:
            self.log_status("🔍 Checking RDP Wrapper status...")
            
            # Check service status
            try:
                result = subprocess.run(
                    ["sc", "query", "TermService"],
                    capture_output=True,
                    text=True
                )
                
                if "RUNNING" in result.stdout:
                    self.log_status("✅ Terminal Services: Running", "SUCCESS")
                else:
                    self.log_status("⚠️ Terminal Services: Not running", "WARNING")
                    
            except Exception as e:
                self.log_error(f"Service check error: {e}")
                
            # Check configuration
            config_path = "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"
            if os.path.exists(config_path):
                self.log_status("✅ Configuration file found", "SUCCESS")
                
                # Parse configuration
                try:
                    config = configparser.ConfigParser()
                    config.read(config_path)
                    
                    if config.has_section('Main'):
                        self.log_status(f"📋 Version: {config.get('Main', 'version', fallback='Unknown')}")
                        
                except Exception as e:
                    self.log_error(f"Config parse error: {e}")
            else:
                self.log_status("❌ Configuration file not found", "ERROR")
                
            self.check_rdp_status()
            
        except Exception as e:
            self.log_error(f"Status check error: {e}")
            
    def update_rdp_wrapper(self):
        """Update RDP Wrapper to latest version"""
        self.log_status("🔄 Checking for updates...")
        self.install_rdp_wrapper()
        
    def backup_config(self):
        """Enhanced configuration backup"""
        try:
            backup_dir = Path.home() / "RDPWrapper_Backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"rdp_wrapper_backup_{timestamp}"
            backup_path.mkdir()
            
            # Backup configuration
            config_path = "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"
            if os.path.exists(config_path):
                shutil.copy2(config_path, backup_path / "rdpwrap.ini")
                
            # Backup registry
            self.backup_registry_to_file(backup_path / "registry_backup.reg")
            
            self.log_status(f"✅ Backup created: {backup_path}", "SUCCESS")
            
        except Exception as e:
            self.log_error(f"Backup error: {e}")
            
    def restore_config(self):
        """Restore configuration from backup"""
        try:
            backup_dir = Path.home() / "RDPWrapper_Backups"
            if not backup_dir.exists():
                messagebox.showerror("Error", "No backups found")
                return
                
            # List backups
            backups = list(backup_dir.glob("rdp_wrapper_backup_*"))
            if not backups:
                messagebox.showerror("Error", "No backups found")
                return
                
            # Show selection dialog
            backup_list = [b.name for b in sorted(backups, reverse=True)]
            selected = self.show_selection_dialog("Select backup to restore", backup_list)
            
            if selected:
                backup_path = backup_dir / selected
                
                # Restore configuration
                config_backup = backup_path / "rdpwrap.ini"
                if config_backup.exists():
                    shutil.copy2(config_backup, "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini")
                    
                # Restore registry
                reg_backup = backup_path / "registry_backup.reg"
                if reg_backup.exists():
                    subprocess.run(["reg", "import", str(reg_backup)], shell=True)
                    
                self.log_status(f"✅ Restored from: {selected}", "SUCCESS")
                
        except Exception as e:
            self.log_error(f"Restore error: {e}")
            
    def load_current_config(self):
        """Load current RDP wrapper configuration"""
        try:
            config_path = "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                    self.config_text.delete(1.0, tk.END)
                    self.config_text.insert(1.0, content)
            else:
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(1.0, "# RDP Wrapper configuration file not found")
                
        except Exception as e:
            self.log_error(f"Config load error: {e}")
            
    def save_config_file(self):
        """Save configuration file"""
        try:
            config_path = "C:\\Program Files\\RDP Wrapper\\rdpwrap.ini"
            content = self.config_text.get(1.0, tk.END)
            
            if messagebox.askyesno("Confirm", "Save configuration changes?"):
                with open(config_path, 'w') as f:
                    f.write(content)
                self.log_status("✅ Configuration saved", "SUCCESS")
                
        except Exception as e:
            self.log_error(f"Config save error: {e}")
            
    def apply_config(self):
        """Apply configuration changes"""
        try:
            self.save_config_file()
            
            # Restart terminal services
            subprocess.run(["net", "stop", "TermService"], shell=True)
            time.sleep(2)
            subprocess.run(["net", "start", "TermService"], shell=True)
            
            self.log_status("✅ Configuration applied", "SUCCESS")
            
        except Exception as e:
            self.log_error(f"Apply config error: {e}")
            
    def test_network(self):
        """Test network connectivity"""
        try:
            self.log_status("🌐 Testing network connectivity...")
            
            # Test DNS resolution
            try:
                socket.gethostbyname("github.com")
                self.log_status("✅ DNS resolution: OK", "SUCCESS")
            except:
                self.log_status("❌ DNS resolution: Failed", "ERROR")
                
            # Test HTTP connectivity
            try:
                response = requests.get("https://github.com", timeout=5)
                if response.status_code == 200:
                    self.log_status("✅ HTTP connectivity: OK", "SUCCESS")
                else:
                    self.log_status(f"⚠️ HTTP status: {response.status_code}", "WARNING")
            except:
                self.log_status("❌ HTTP connectivity: Failed", "ERROR")
                
        except Exception as e:
            self.log_error(f"Network test error: {e}")
            
    def scan_registry(self):
        """Scan registry for RDP-related settings"""
        try:
            self.log_status("🔍 Scanning registry for RDP settings...")
            
            keys_to_check = [
                r"SYSTEM\CurrentControlSet\Control\Terminal Server",
                r"SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp",
                r"SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
            ]
            
            for key_path in keys_to_check:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
                        self.log_status(f"📋 Found: {key_path}")
                        
                        # List values
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                self.log_status(f"  {name}: {value}")
                                i += 1
                            except OSError:
                                break
                                
                except Exception as e:
                    self.log_status(f"⚠️ Cannot access: {key_path}", "WARNING")
                    
        except Exception as e:
            self.log_error(f"Registry scan error: {e}")
            
    def manage_services(self):
        """Manage Windows services"""
        try:
            self.log_status("🔧 Managing Windows services...")
            
            # Get service status
            services = ["TermService", "SessionEnv", "RemoteRegistry"]
            
            for service in services:
                try:
                    result = subprocess.run(
                        ["sc", "query", service],
                        capture_output=True,
                        text=True
                    )
                    
                    if "RUNNING" in result.stdout:
                        self.log_status(f"✅ {service}: Running", "SUCCESS")
                    elif "STOPPED" in result.stdout:
                        self.log_status(f"⚠️ {service}: Stopped", "WARNING")
                    else:
                        self.log_status(f"❓ {service}: Unknown state", "WARNING")
                        
                except Exception as e:
                    self.log_error(f"Service check error for {service}: {e}")
                    
        except Exception as e:
            self.log_error(f"Service management error: {e}")
            
    def check_ports(self):
        """Check RDP port availability"""
        try:
            self.log_status("🔌 Checking RDP port availability...")
            
            # Check if port 3389 is in use
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 3389))
            sock.close()
            
            if result == 0:
                self.log_status("✅ Port 3389: In use (RDP active)", "SUCCESS")
            else:
                self.log_status("⚠️ Port 3389: Not in use", "WARNING")
                
        except Exception as e:
            self.log_error(f"Port check error: {e}")
            
    def manage_firewall(self):
        """Configure Windows Firewall for RDP"""
        try:
            self.log_status("🛡️ Configuring Windows Firewall...")
            
            # Check current rules
            result = subprocess.run(
                ["net
