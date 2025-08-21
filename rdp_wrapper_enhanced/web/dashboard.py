#!/usr/bin/env python3
"""
Enhanced RDP Wrapper Dashboard
Real-time monitoring dashboard for RDP connections and system resources
"""

import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import psutil
import socket
import win32evtlog
import win32con
import win32security
import win32net
import win32netcon

class EnhancedDashboard:
    def __init__(self, host='0.0.0.0', port=8080):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'rdp_enhanced_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.host = host
        self.port = port
        self.running = False
        
        # Enhanced monitoring data
        self.connection_history = []
        self.system_metrics = {}
        self.security_events = []
        self.user_sessions = {}
        
        self.setup_routes()
        self.setup_socketio()
        
    def setup_routes(self):
        """Setup web routes for the dashboard"""
        
        @self.app.route('/')
        def index():
            return render_template('dashboard.html')
            
        @self.app.route('/api/system-info')
        def system_info():
            """Get comprehensive system information"""
            return jsonify(self.get_system_info())
            
        @self.app.route('/api/connections')
        def connections():
            """Get active RDP connections"""
            return jsonify(self.get_active_connections())
            
        @self.app.route('/api/security-events')
        def security_events():
            """Get recent security events"""
            return jsonify(self.get_security_events())
            
        @self.app.route('/api/performance-metrics')
        def performance_metrics():
            """Get performance metrics"""
            return jsonify(self.get_performance_metrics())
            
    def setup_socketio(self):
        """Setup WebSocket for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected")
            self.start_monitoring()
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")
            
    def get_system_info(self):
        """Get comprehensive system information"""
        try:
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk Information
            disk_usage = psutil.disk_usage('C:\\')
            disk_io = psutil.disk_io_counters()
            
            # Network Information
            network_io = psutil.net_io_counters()
            
            # System Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None,
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': (disk_usage.used / disk_usage.total) * 100,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                },
                'uptime': str(uptime),
                'boot_time': boot_time.isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_active_connections(self):
        """Get active RDP connections with enhanced details"""
        connections = []
        try:
            # Get terminal services connections
            import win32ts
            server = win32ts.WTS_CURRENT_SERVER_HANDLE
            
            sessions = win32ts.WTSEnumerateSessions(server)
            for session in sessions:
                session_id = session['SessionId']
                session_info = win32ts.WTSQuerySessionInformation(server, session_id, win32ts.WTSUserName)
                client_name = win32ts.WTSQuerySessionInformation(server, session_id, win32ts.WTSClientName)
                client_ip = win32ts.WTSQuerySessionInformation(server, session_id, win32ts.WTSClientAddress)
                
                if session_info and session_info.strip():
                    connections.append({
                        'session_id': session_id,
                        'username': session_info,
                        'client_name': client_name or 'Unknown',
                        'client_ip': self.format_client_ip(client_ip),
                        'state': session['State'],
                        'connection_time': self.get_connection_time(session_id)
                    })
                    
        except Exception as e:
            connections.append({'error': str(e)})
            
        return connections
    
    def format_client_ip(self, client_address):
        """Format client IP address from WTSClientAddress"""
        if not client_address:
            return 'Unknown'
        try:
            # Convert bytes to IP string
            ip_bytes = client_address.Address
            if len(ip_bytes) >= 4:
                return f"{ip_bytes[0]}.{ip_bytes[1]}.{ip_bytes[2]}.{ip_bytes[3]}"
        except:
            return 'Unknown'
    
    def get_connection_time(self, session_id):
        """Get connection time for a session"""
        try:
            import win32ts
            server = win32ts.WTS_CURRENT_SERVER_HANDLE
            info = win32ts.WTSQuerySessionInformation(server, session_id, win32ts.WTSConnectTime)
            if info:
                return datetime.fromtimestamp(info).isoformat()
        except:
            return None
    
    def get_security_events(self):
        """Get recent security events from Windows Event Log"""
        events = []
        try:
            hand = win32evtlog.OpenEventLog(None, "Security")
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            events_list = win32evtlog.ReadEventLog(hand, flags, 0, 50)
            
            for event in events_list:
                if event.EventID in [4624, 4625, 4634, 4647, 4648]:  # RDP related events
                    events.append({
                        'event_id': event.EventID,
                        'time_generated': event.TimeGenerated.Format(),
                        'source': event.SourceName,
                        'event_type': event.EventType,
                        'message': str(event.StringInserts)
                    })
                    
            win32evtlog.CloseEventLog(hand)
        except Exception as e:
            events.append({'error': str(e)})
            
        return events
    
    def get_performance_metrics(self):
        """Get detailed performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_info(),
            'connections': len(self.get_active_connections()),
            'security_events': len(self.get_security_events())
        }
        return metrics
    
    def start_monitoring(self):
        """Start real-time monitoring and broadcasting"""
        if not self.running:
            self.running = True
            threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Update metrics
                self.system_metrics = self.get_system_info()
                connections = self.get_active_connections()
                
                # Emit updates via WebSocket
                self.socketio.emit('system_update', {
                    'system': self.system_metrics,
                    'connections': connections,
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def run(self):
        """Start the dashboard server"""
        print(f"Starting Enhanced RDP Dashboard on http://{self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=True)

if __name__ == '__main__':
    dashboard = EnhancedDashboard()
    dashboard.run()
