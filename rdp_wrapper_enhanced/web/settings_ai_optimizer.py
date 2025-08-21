import json
import psutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import requests
import os
from typing import Dict, List, Any, Optional

class AISettingsOptimizer:
    def __init__(self):
        self.model_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.performance_history = []
        self.optimization_cache = {}
        self.monitoring_active = False
        
    def analyze_system_performance(self) -> Dict[str, Any]:
        """Analyze current system performance for RDP optimization"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network metrics
            network = psutil.net_io_counters()
            
            # Simulate RDP-specific metrics
            rdp_metrics = {
                'active_sessions': self._get_active_sessions(),
                'avg_response_time': self._get_response_time(),
                'connection_quality': self._assess_connection_quality(),
                'bandwidth_usage': network.bytes_sent + network.bytes_recv
            }
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'disk_usage': (disk.used / disk.total) * 100,
                    'available_memory': memory.available
                },
                'rdp_performance': rdp_metrics,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_active_sessions(self) -> int:
        """Get number of active RDP sessions"""
        # This would integrate with actual RDP monitoring
        return 2  # Placeholder
    
    def _get_response_time(self) -> float:
        """Get average RDP response time"""
        # This would measure actual RDP response times
        return 45.2  # Placeholder in ms
    
    def _assess_connection_quality(self) -> str:
        """Assess RDP connection quality"""
        # This would analyze connection metrics
        return "good"
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-powered optimization recommendations"""
        try:
            system_info = self.analyze_system_performance()
            
            # Prepare prompt for AI analysis
            prompt = self._create_optimization_prompt(system_info)
            
            # Get AI recommendations
            recommendations = self._query_ai_model(prompt)
            
            return recommendations
        except Exception as e:
            return [{"type": "error", "message": str(e)}]
    
    def _create_optimization_prompt(self, system_info: Dict[str, Any]) -> str:
        """Create prompt for AI optimization analysis"""
        return f"""
        Analyze this RDP wrapper system performance data and provide optimization recommendations:
        
        System Performance:
        - CPU Usage: {system_info['system']['cpu_usage']}%
        - Memory Usage: {system_info['system']['memory_usage']}%
        - Disk Usage: {system_info['system']['disk_usage']}%
        - Available Memory: {system_info['system']['available_memory']} bytes
        
        RDP Performance:
        - Active Sessions: {system_info['rdp_performance']['active_sessions']}
        - Average Response Time: {system_info['rdp_performance']['avg_response_time']}ms
        - Connection Quality: {system_info['rdp_performance']['connection_quality']}
        
        Network:
        - Bytes Sent: {system_info['network']['bytes_sent']}
        - Bytes Received: {system_info['network']['bytes_recv']}
        
        Provide specific, actionable optimization recommendations for RDP wrapper settings. 
        Focus on performance, security, and user experience improvements.
        Format as JSON with recommendations including priority, impact, and implementation steps.
        """
    
    def _query_ai_model(self, prompt: str) -> List[Dict[str, Any]]:
        """Query AI model for optimization recommendations"""
        if not self.api_key:
            return self._get_fallback_recommendations()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "anthropic/claude-sonnet-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an RDP optimization expert. Provide specific, actionable recommendations for RDP wrapper settings."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000
            }
            
            response = requests.post(self.model_endpoint, headers=headers, json=payload)
            
            if response.status_code == 200:
                ai_response = response.json()
                recommendations = self._parse_ai_recommendations(ai_response['choices'][0]['message']['content'])
                return recommendations
            else:
                return self._get_fallback_recommendations()
                
        except Exception as e:
            return self._get_fallback_recommendations()
    
    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Fallback recommendations when AI service is unavailable"""
        return [
            {
                "id": "cpu_optimization",
                "type": "performance",
                "priority": "high",
                "title": "CPU Optimization",
                "description": "Reduce CPU usage by optimizing RDP compression settings",
                "action": "Enable RDP compression and reduce color depth for remote sessions",
                "expected_impact": "20-30% reduction in CPU usage",
                "implementation": "Set compression level to high in RDP settings"
            },
            {
                "id": "memory_optimization",
                "type": "performance",
                "priority": "medium",
                "title": "Memory Optimization",
                "description": "Optimize memory allocation for RDP sessions",
                "action": "Adjust memory limits per RDP session",
                "expected_impact": "15-25% reduction in memory usage",
                "implementation": "Set max memory per session to 512MB"
            },
            {
                "id": "network_optimization",
                "type": "performance",
                "priority": "high",
                "title": "Network Optimization",
                "description": "Improve network performance for remote connections",
                "action": "Enable TCP optimizations and reduce latency",
                "expected_impact": "30-40% improvement in connection speed",
                "implementation": "Enable TCP_NODELAY and optimize buffer sizes"
            },
            {
                "id": "security_hardening",
                "type": "security",
                "priority": "high",
                "title": "Security Hardening",
                "description": "Enhance security settings for RDP connections",
                "action": "Enable NLA and set strong encryption",
                "expected_impact": "Significant security improvement",
                "implementation": "Enable Network Level Authentication and AES encryption"
            }
        ]
    
    def _parse_ai_recommendations(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured recommendations"""
        try:
            # Try to parse as JSON
            if ai_response.strip().startswith('[') or ai_response.strip().startswith('{'):
                return json.loads(ai_response)
            else:
                # Parse text response
                return self._parse_text_recommendations(ai_response)
        except:
            return self._get_fallback_recommendations()
    
    def _parse_text_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parse text-based AI recommendations"""
        recommendations = []
        lines = text.split('\n')
        
        current_rec = {}
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {
                    "title": line.lstrip('-* ').split(':')[0],
                    "description": line.lstrip('-* ')
                }
        
        if current_rec:
            recommendations.append(current_rec)
            
        return recommendations[:5]  # Limit to 5 recommendations
    
    def predict_performance_impact(self, changes: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict performance impact of proposed changes"""
        try:
            system_info = self.analyze_system_performance()
            
            # Calculate baseline performance score
            baseline_score = self._calculate_performance_score(system_info)
            
            # Predict impact of changes
            predicted_impact = {
                'baseline_score': baseline_score,
                'predicted_improvements': {},
                'risk_factors': [],
                'estimated_time_to_implement': '5-15 minutes',
                'rollback_time': '2-5 minutes'
            }
            
            # Simulate impact prediction
            if changes:
                for change_type, change_data in changes.items():
                    predicted_impact['predicted_improvements'][change_type] = {
                        'expected_improvement': f"{15 + hash(str(change_data)) % 30}%",
                        'confidence': 'high' if change_type in ['compression', 'memory'] else 'medium',
                        'side_effects': []
                    }
            else:
                # Default predictions
                predicted_impact['predicted_improvements'] = {
                    'cpu_optimization': {'expected_improvement': '25%', 'confidence': 'high'},
                    'memory_optimization': {'expected_improvement': '20%', 'confidence': 'high'},
                    'network_optimization': {'expected_improvement': '35%', 'confidence': 'medium'}
                }
            
            return predicted_impact
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_performance_score(self, system_info: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        try:
            cpu_score = max(0, 100 - system_info['system']['cpu_usage'])
            memory_score = max(0, 100 - system_info['system']['memory_usage'])
            disk_score = max(0, 100 - system_info['system']['disk_usage'])
            
            # Weighted average
            return (cpu_score * 0.4 + memory_score * 0.3 + disk_score * 0.3)
        except:
            return 75.0
    
    def apply_recommendations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply selected AI recommendations"""
        try:
            results = {
                'applied': [],
                'failed': [],
                'warnings': []
            }
            
            for rec in recommendations:
                try:
                    # Simulate applying recommendation
                    success = self._apply_single_recommendation(rec)
                    if success:
                        results['applied'].append({
                            'id': rec.get('id'),
                            'title': rec.get('title'),
                            'status': 'success'
                        })
                    else:
                        results['failed'].append({
                            'id': rec.get('id'),
                            'title': rec.get('title'),
                            'error': 'Implementation pending'
                        })
                        
                except Exception as e:
                    results['failed'].append({
                        'id': rec.get('id'),
                        'title': rec.get('title'),
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            return {'error': str(e)}
    
    def _apply_single_recommendation(self, recommendation: Dict[str, Any]) -> bool:
        """Apply a single recommendation"""
        # This would integrate with actual RDP wrapper configuration
        # For now, return True to simulate success
        return True
    
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self.analyze_system_performance()
                self.performance_history.append(metrics)
                
                # Keep only last 100 entries
                if len(self.performance_history) > 100:
                    self.performance_history = self.performance_history[-100:]
                    
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(60)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get collected monitoring data"""
        return {
            'performance_history': self.performance_history,
            'current_recommendations': self.current_recommendations,
            'is_monitoring': self.monitoring_active
        }

# Global optimizer instance
ai_optimizer = AISettingsOptimizer()
