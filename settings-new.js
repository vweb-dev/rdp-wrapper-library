class AISettingsOptimizerUI {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.isMonitoring = false;
        this.currentRecommendations = null;
        this.init();
    }

    init() {
        this.createUI();
        this.bindEvents();
        this.startPerformanceMonitoring();
    }

    createUI() {
        const container = document.getElementById('ai-optimizer-container');
        if (!container) return;

        container.innerHTML = `
            <div class="ai-optimizer-panel">
                <h3>AI Settings Optimizer</h3>
                
                <div class="performance-section">
                    <h4>System Performance</h4>
                    <div class="performance-metrics">
                        <div class="metric">
                            <span class="label">CPU Usage:</span>
                            <span class="value" id="cpu-usage">--</span>
                        </div>
                        <div class="metric">
                            <span class="label">Memory Usage:</span>
                            <span class="value" id="memory-usage">--</span>
                        </div>
                        <div class="metric">
                            <span class="label">Network Latency:</span>
                            <span class="value" id="network-latency">--</span>
                        </div>
                    </div>
                </div>

                <div class="optimization-section">
                    <h4>AI Recommendations</h4>
                    <button id="get-recommendations" class="btn-primary">Get AI Recommendations</button>
                    <div id="recommendations-container" class="recommendations-container" style="display: none;">
                        <div id="recommendations-list"></div>
                        <button id="apply-recommendations" class="btn-success" style="display: none;">Apply Recommendations</button>
                    </div>
                </div>

                <div class="history-section">
                    <h4>Optimization History</h4>
                    <button id="view-history" class="btn-secondary">View History</button>
                    <div id="history-container" class="history-container" style="display: none;">
                        <div id="history-list"></div>
                    </div>
                </div>

                <div class="status-section">
                    <div id="status-message" class="status-message"></div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.getElementById('get-recommendations').addEventListener('click', () => this.getRecommendations());
        document.getElementById('apply-recommendations').addEventListener('click', () => this.applyRecommendations());
        document.getElementById('view-history').addEventListener('click', () => this.viewHistory());
    }

    async getRecommendations() {
        try {
            this.showStatus('Getting AI recommendations...', 'info');
            
            const currentSettings = this.getCurrentSettings();
            const response = await fetch(`${this.apiBase}/ai-optimize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ settings: currentSettings })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentRecommendations = data.recommendations;
                this.displayRecommendations(data.recommendations);
                this.showStatus('Recommendations received successfully', 'success');
            } else {
                this.showStatus('Failed to get recommendations: ' + data.error, 'error');
            }
        } catch (error) {
            this.showStatus('Error getting recommendations: ' + error.message, 'error');
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendations-container');
        const list = document.getElementById('recommendations-list');
        
        container.style.display = 'block';
        list.innerHTML = '';

        if (recommendations.recommendations && recommendations.recommendations.length > 0) {
            recommendations.recommendations.forEach(rec => {
                const item = document.createElement('div');
                item.className = 'recommendation-item';
                item.innerHTML = `
                    <div class="recommendation-header">
                        <span class="setting-name">${rec.setting}</span>
                        <span class="confidence">Confidence: ${rec.confidence}%</span>
                    </div>
                    <div class="recommendation-details">
                        <p><strong>Current:</strong> ${rec.current_value}</p>
                        <p><strong>Recommended:</strong> ${rec.recommended_value}</p>
                        <p><strong>Reason:</strong> ${rec.reason}</p>
                        <p><strong>Impact:</strong> ${rec.impact}</p>
                    </div>
                `;
                list.appendChild(item);
            });
            
            document.getElementById('apply-recommendations').style.display = 'inline-block';
        } else {
            list.innerHTML = '<p>No recommendations available at this time.</p>';
            document.getElementById('apply-recommendations').style.display = 'none';
        }
    }

    async applyRecommendations() {
        if (!this.currentRecommendations) {
            this.showStatus('No recommendations to apply', 'warning');
            return;
        }

        try {
            this.showStatus('Applying recommendations...', 'info');
            
            const response = await fetch(`${this.apiBase}/apply-recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recommendations: this.currentRecommendations })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showStatus('Recommendations applied successfully', 'success');
                this.currentRecommendations = null;
                document.getElementById('recommendations-container').style.display = 'none';
            } else {
                this.showStatus('Failed to apply recommendations: ' + data.message, 'error');
            }
        } catch (error) {
            this.showStatus('Error applying recommendations: ' + error.message, 'error');
        }
    }

    async viewHistory() {
        try {
            this.showStatus('Loading optimization history...', 'info');
            
            const response = await fetch(`${this.apiBase}/optimization-history`);
            const data = await response.json();
            
            if (data.success) {
                this.displayHistory(data.history);
            } else {
                this.showStatus('Failed to load history: ' + data.error, 'error');
            }
        } catch (error) {
            this.showStatus('Error loading history: ' + error.message, 'error');
        }
    }

    displayHistory(history) {
        const container = document.getElementById('history-container');
        const list = document.getElementById('history-list');
        
        container.style.display = 'block';
        list.innerHTML = '';

        if (history && history.length > 0) {
            history.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'history-item';
                itemDiv.innerHTML = `
                    <div class="history-header">
                        <span class="timestamp">${new Date(item.timestamp).toLocaleString()}</span>
                        <button class="rollback-btn" data-timestamp="${item.timestamp}">Rollback</button>
                    </div>
                    <div class="history-details">
                        <p><strong>Settings Changed:</strong> ${item.settings_changed}</p>
                        <p><strong>Performance Impact:</strong> ${item.performance_impact}</p>
                    </div>
                `;
                list.appendChild(itemDiv);
            });

            // Add rollback event listeners
            document.querySelectorAll('.rollback-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const timestamp = e.target.getAttribute('data-timestamp');
                    this.rollbackOptimization(timestamp);
                });
            });
        } else {
            list.innerHTML = '<p>No optimization history available.</p>';
        }
    }

    async rollbackOptimization(timestamp) {
        try {
            this.showStatus('Rolling back optimization...', 'info');
            
            const response = await fetch(`${this.apiBase}/rollback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ timestamp: timestamp })
            });

            const data = await response.json();
            
            if (data.success) {
                this.showStatus('Rollback completed successfully', 'success');
                document.getElementById('history-container').style.display = 'none';
            } else {
                this.showStatus('Rollback failed: ' + data.message, 'error');
            }
        } catch (error) {
            this.showStatus('Error during rollback: ' + error.message, 'error');
        }
    }

    async startPerformanceMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        
        const updateMetrics = async () => {
            try {
                const response = await fetch(`${this.apiBase}/performance-data`);
                const data = await response.json();
                
                if (data.success) {
                    this.updatePerformanceDisplay(data.data);
                }
            } catch (error) {
                console.error('Error updating performance metrics:', error);
            }
        };

        // Update every 30 seconds
        updateMetrics();
        setInterval(updateMetrics, 30000);
    }

    updatePerformanceDisplay(data) {
        document.getElementById('cpu-usage').textContent = `${data.cpu_usage}%`;
        document.getElementById('memory-usage').textContent = `${data.memory_usage}%`;
        document.getElementById('network-latency').textContent = `${data.network_latency}ms`;
    }

    getCurrentSettings() {
        // This would gather current settings from the RDP wrapper
        // For now, return a sample structure
        return {
            max_connections: 10,
            timeout: 30,
            buffer_size: 8192,
            compression: true,
            encryption_level: 'high'
        };
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.className = `status-message ${type}`;
        
        setTimeout(() => {
            statusEl.textContent = '';
            statusEl.className = 'status-message';
        }, 5000);
    }
}

// Initialize the AI Settings Optimizer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AISettingsOptimizerUI();
});
