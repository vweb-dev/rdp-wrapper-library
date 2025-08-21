import json
from flask import Blueprint, request, jsonify
from .settings_ai_optimizer import AISettingsOptimizer
import os

ai_optimizer_bp = Blueprint('ai_optimizer', __name__, url_prefix='/api/ai-optimizer')

@ai_optimizer_bp.route('/analyze', methods=['POST'])
def analyze_system():
    """Analyze current system performance for RDP optimization"""
    try:
        optimizer = AISettingsOptimizer()
        analysis = optimizer.analyze_system_performance()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-powered optimization recommendations"""
    try:
        optimizer = AISettingsOptimizer()
        recommendations = optimizer.get_optimization_recommendations()
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/predict-impact', methods=['POST'])
def predict_impact():
    """Predict performance impact of proposed changes"""
    try:
        optimizer = AISettingsOptimizer()
        changes = request.json.get('changes', {})
        prediction = optimizer.predict_performance_impact(changes)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/apply-recommendations', methods=['POST'])
def apply_recommendations():
    """Apply selected AI recommendations"""
    try:
        optimizer = AISettingsOptimizer()
        recommendations = request.json.get('recommendations', [])
        results = optimizer.apply_recommendations(recommendations)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start continuous performance monitoring"""
    try:
        optimizer = AISettingsOptimizer()
        optimizer.start_monitoring()
        return jsonify({'status': 'monitoring_started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop continuous performance monitoring"""
    try:
        optimizer = AISettingsOptimizer()
        optimizer.stop_monitoring()
        return jsonify({'status': 'monitoring_stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_optimizer_bp.route('/monitoring/status', methods=['GET'])
def monitoring_status():
    """Get current monitoring status"""
    try:
        optimizer = AISettingsOptimizer()
        status = optimizer.get_monitoring_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
