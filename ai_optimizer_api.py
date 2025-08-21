from flask import Flask, request, jsonify
from settings_ai_optimizer import AISettingsOptimizer
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize AI optimizer
ai_optimizer = AISettingsOptimizer()

@app.route('/api/ai-optimize', methods=['POST'])
def optimize_settings():
    """Get AI-optimized settings recommendations"""
    try:
        data = request.get_json()
        current_settings = data.get('settings', {})
        
        # Get AI recommendations
        recommendations = ai_optimizer.get_recommendations(current_settings)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'timestamp': recommendations.get('timestamp')
        })
    except Exception as e:
        logging.error(f"AI optimization error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/performance-data', methods=['GET'])
def get_performance_data():
    """Get current system performance data"""
    try:
        performance_data = ai_optimizer.get_performance_data()
        return jsonify({
            'success': True,
            'data': performance_data
        })
    except Exception as e:
        logging.error(f"Performance data error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/apply-recommendations', methods=['POST'])
def apply_recommendations():
    """Apply AI recommendations to settings"""
    try:
        data = request.get_json()
        recommendations = data.get('recommendations', {})
        
        # Apply recommendations
        success = ai_optimizer.apply_recommendations(recommendations)
        
        return jsonify({
            'success': success,
            'message': 'Recommendations applied successfully' if success else 'Failed to apply recommendations'
        })
    except Exception as e:
        logging.error(f"Apply recommendations error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/optimization-history', methods=['GET'])
def get_optimization_history():
    """Get optimization history"""
    try:
        history = ai_optimizer.get_optimization_history()
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logging.error(f"History error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rollback', methods=['POST'])
def rollback_optimization():
    """Rollback to previous settings"""
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        
        success = ai_optimizer.rollback_to_previous(timestamp)
        
        return jsonify({
            'success': success,
            'message': 'Rollback successful' if success else 'Rollback failed'
        })
    except Exception as e:
        logging.error(f"Rollback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
