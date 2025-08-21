"""
RDP Wrapper Enhanced - Connection and System Monitor
Monitors RDP connections, system resources, and security events
"""

import psutil
import time
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import socket
from pathlib import Path
import subprocess
import winreg
import os

class RDPMonitor:
    """Enhanced RDP connection and system monitor"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "rdp_monitor_config.json"
        self.logger = self._setup_logging()
        self.monitoring = False
        self.monitor_thread = None
        self.metrics = {
            'connections': [],
            'system_resources': {},
            'security_events': [],
            'performance_metrics': {}
        }
        self.config = self._load_config()
        self.alert_thresholds = self.config.get('alert_thresholds', {})
        self.connection_history = []
        self.active_sessions = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the monitor"""
        logger = logging.getLogger('RDPMonitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('rdp_monitor.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            'monitoring_interval': 5,
            'alert_thresholds': {
                'cpu_usage': 80,
                'memory_usage': 85,
                'disk_usage': 90,
                'failed_logins': 5,
                'concurrent_connections': 10
            },
            'log_retention_days': 30,
            'enable_performance_monitoring': True,
            'enable_security_monitoring': True,
            'enable_connection_logging': True
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            
        return default_config
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("RDP monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("RDP monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_system_resources()
                self._check_rdp_connections()
                self._check_security_events()
                self._update_performance_metrics()
                time.sleep(self.config['monitoring_interval'])
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    def _check_system_resources(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.metrics['system_resources'] = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # Check thresholds and generate alerts
            self._check_resource_alerts()
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
    
    def _check_resource_alerts(self):
        """Check if resource usage exceeds thresholds"""
        resources = self.metrics['system_resources']
        thresholds = self.alert_thresholds
        
        alerts = []
        
        if resources.get('cpu_usage', 0) > thresholds.get('cpu_usage', 80):
            alerts.append(f"High CPU usage: {resources['cpu_usage']}%")
            
        if resources.get('memory_usage', 0) > thresholds.get('memory_usage', 85):
            alerts.append(f"High memory usage: {resources['memory_usage']}%")
            
        if resources.get('disk_usage', 0) > thresholds.get('disk_usage', 90):
            alerts.append(f"High disk usage: {resources['disk_usage']}%")
            
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert}")
            self._log_security_event('resource_alert', alert)
    
    def _check_rdp_connections(self):
        """Check active RDP connections"""
        try:
            connections = self._get_rdp_connections()
            self.metrics['connections'] = connections
            
            # Track connection history
            for conn in connections:
                if conn['id'] not in self.active_sessions:
                    self.active_sessions[conn['id']] = conn
                    self._log_connection_event('connected', conn)
                elif conn['status'] == 'disconnected':
                    self._log_connection_event('disconnected', conn)
                    if conn['id'] in self.active_sessions:
                        del self.active_sessions[conn['id']]
            
            # Check concurrent connection limit
            active_count = len([c for c in connections if c['status'] == 'active'])
            if active_count > self.alert_thresholds.get('concurrent_connections', 10):
                self.logger.warning(f"High concurrent connections: {active_count}")
                
        except Exception as e:
            self.logger.error(f"Error checking RDP connections: {e}")
    
    def _get_rdp_connections(self) -> List[Dict]:
        """Get current RDP connections"""
        connections = []
        
        try:
            # Get terminal service sessions
            cmd = 'query session'
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        session_info = {
                            'id': parts[0],
                            'username': parts[1] if len(parts) > 1 else 'N/A',
                            'state': parts[2] if len(parts) > 2 else 'N/A',
                            'type': 'RDP',
                            'timestamp': datetime.now().isoformat()
                        }
                        connections.append(session_info)
                        
        except Exception as e:
            self.logger.error(f"Error getting RDP connections: {e}")
            
        return connections
    
    def _check_security_events(self):
        """Check for security-related events"""
        try:
            if not self.config.get('enable_security_monitoring'):
                return
                
            # Check Windows Security Log for RDP events
            events = self._get_security_events()
            self.metrics['security_events'] = events
            
            # Check for failed login attempts
            failed_logins = [e for e in events if e['event_type'] == 'failed_login']
            if len(failed_logins) > self.alert_thresholds.get('failed_logins', 5):
                self.logger.warning(f"High failed login attempts: {len(failed_logins)}")
                
        except Exception as e:
            self.logger.error(f"Error checking security events: {e}")
    
    def _get_security_events(self) -> List[Dict]:
        """Get security events from Windows Event Log"""
        events = []
        
        try:
            # Check for RDP-related events in Security log
            cmd = 'wevtutil qe Security /q:"*[System[EventID=4624 or EventID=4625]]" /f:text /c:50'
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse events (simplified parsing)
                lines = result.stdout.split('\n')
                event = {}
                for line in lines:
                    if 'Event ID:' in line:
                        event['event_id'] = line.split(':')[1].strip()
                    elif 'Account Name:' in line:
                        event['username'] = line.split(':')[1].strip()
                    elif 'Source Network Address:' in line:
                        event['source_ip'] = line.split(':')[1].strip()
                        
                    if event and 'event_id' in event:
                        event['event_type'] = 'successful_login' if event['event_id'] == '4624' else 'failed_login'
                        event['timestamp'] = datetime.now().isoformat()
                        events.append(event.copy())
                        event = {}
                        
        except Exception as e:
            self.logger.error(f"Error getting security events: {e}")
            
        return events
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        try:
            if not self.config.get('enable_performance_monitoring'):
                return
                
            # Get network statistics
            network_stats = psutil.net_io_counters()
            
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'rdp' in proc.info['name'].lower() or 'termsrv' in proc.info['name'].lower():
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.metrics['performance_metrics'] = {
                'timestamp': datetime.now().isoformat(),
                'network_bytes_sent': network_stats.bytes_sent,
                'network_bytes_recv': network_stats.bytes_recv,
                'rdp_processes': processes,
                'active_sessions_count': len(self.active_sessions)
            }
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    def _log_connection_event(self, event_type: str, connection: Dict):
        """Log connection events"""
        log_entry = {
            'event_type': event_type,
            'connection': connection,
            'timestamp': datetime.now().isoformat()
        }
        
        self.connection_history.append(log_entry)
        self.logger.info(f"Connection {event_type}: {connection}")
    
    def _log_security_event(self, event_type: str, details: str):
        """Log security events"""
        event = {
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.metrics['security_events'].append(event)
        self.logger.warning(f"Security event: {event_type} - {details}")
    
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        return {
            'monitoring_active': self.monitoring,
            'system_resources': self.metrics['system_resources'],
            'active_connections': len(self.active_sessions),
            'total_connections': len(self.connection_history),
            'security_events_count': len(self.metrics['security_events']),
            'uptime': time.time() - (getattr(self, 'start_time', time.time()))
        }
    
    def get_connection_report(self) -> Dict:
        """Get detailed connection report"""
        return {
            'active_sessions': list(self.active_sessions.values()),
            'connection_history': self.connection_history[-50:],  # Last 50
            'total_connections': len(self.connection_history),
            'unique_users': len(set(c.get('username') for c in self.connection_history))
        }
    
    def get_security_report(self) -> Dict:
        """Get security report"""
        security_events = self.metrics['security_events']
        
        failed_logins = [e for e in security_events if e['event_type'] == 'failed_login']
        successful_logins = [e for e in security_events if e['event_type'] == 'successful_login']
        
        return {
            'total_events': len(security_events),
            'failed_logins': len(failed_logins),
            'successful_logins': len(successful_logins),
            'recent_events': security_events[-20:],  # Last 20
            'unique_source_ips': len(set(e.get('source_ip') for e in security_events if 'source_ip' in e))
        }
    
    def save_metrics(self, filename: str = None):
        """Save current metrics to file"""
        try:
            filename = filename or f"rdp_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'metrics': self.metrics,
                    'config': self.config,
                    'status': self.get_status()
                }, f, indent=2, default=str)
                
            self.logger.info(f"Metrics saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            retention_days = self.config.get('log_retention_days', 30)
            cutoff_date = datetime.now().timestamp() - (retention_days * 24 * 3600)
            
            log_files = Path('.').glob('rdp_metrics_*.json')
            for log_file in log_files:
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Removed old log file: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up logs: {e}")

# Global monitor instance
monitor = RDPMonitor()

# Convenience functions
def start_monitoring():
    """Start the global monitor"""
    monitor.start_monitoring()

def stop_monitoring():
    """Stop the global monitor"""
    monitor.stop_monitoring()

def get_status():
    """Get monitor status"""
    return monitor.get_status()

def get_connection_report():
    """Get connection report"""
    return monitor.get_connection_report()

def get_security_report():
    """Get security report"""
    return monitor.get_security_report()

if __name__ == "__main__":
    # Test the monitor
    monitor.start_monitoring()
    time.sleep(10)
    monitor.stop_monitoring()
    
    print("Status:", monitor.get_status())
    print("Connections:", monitor.get_connection_report())
    print("Security:", monitor.get_security_report())
    
    monitor.save_metrics()
