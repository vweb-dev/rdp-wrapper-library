// Settings Configuration JavaScript for RDP Wrapper Enhanced
function settingsData() {
    return {
        activeTab: 'general',
        settings: {
            general: {
                autoStart: true,
                logLevel: 'info',
                maxSessions: 10,
                sessionTimeout: 30
            },
            security: {
                firewall: true,
                ipWhitelist: '',
                maxAttempts: 3,
                lockoutDuration: 15
            },
            network: {
                port: 3389,
                adapter: 'all',
                bandwidthLimit: 0,
                compression: true
            },
            advanced: {
                debugMode: false,
                performanceLogging: false,
                customRegistry: '',
                backupEnabled: true
            }
        },
        
        async init() {
            await this.loadSettings();
        },
        
        async loadSettings() {
            try {
                const response = await fetch('/api/settings');
                const data = await response.json();
                if (data.success) {
                    this.settings = { ...this.settings, ...data.settings };
                }
            } catch (error) {
                console.error('Failed to load settings:', error);
            }
        },
        
        async saveGeneralSettings() {
            await this.saveSettings('general', this.settings.general);
        },
        
        async saveSecuritySettings() {
            await this.saveSettings('security', this.settings.security);
        },
        
        async saveNetworkSettings() {
            await this.saveSettings('network', this.settings.network);
        },
        
        async saveAdvancedSettings() {
            await this.saveSettings('advanced', this.settings.advanced);
        },
        
        async saveSettings(category, settings) {
            try {
                const response = await fetch(`/api/settings/${category}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(settings)
                });
                
                const result = await response.json();
                if (result.success) {
                    this.showNotification('Settings saved successfully', 'success');
                } else {
                    this.showNotification(result.message || 'Failed to save settings', 'error');
                }
            } catch (error) {
                console.error('Failed to save settings:', error);
                this.showNotification('Failed to save settings', 'error');
            }
        },
        
        showNotification(message, type) {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 p-4 rounded-md text-white z-50 ${
                type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        },
        
        validateIP(ip) {
            const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            return ipRegex.test(ip);
        },
        
        parseIPWhitelist() {
            return this.settings.security.ipWhitelist
                .split('\n')
                .map(ip => ip.trim())
                .filter(ip => ip && this.validateIP(ip));
        }
    };
}

// Initialize Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.data('settingsData', settingsData);
});
