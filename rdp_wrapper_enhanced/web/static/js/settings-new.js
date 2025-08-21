class SettingsManager {
    constructor() {
        this.settings = {};
        this.apiBase = '/api';
        this.init();
    }

    async init() {
        await this.loadSettings();
        this.bindEvents();
        this.setupTabs();
    }

    bindEvents() {
        // Form submissions
        document.getElementById('settings-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // Reset button
        document.getElementById('reset-settings').addEventListener('click', () => {
            this.resetSettings();
        });

        // Backup buttons
        document.getElementById('create-backup').addEventListener('click', () => {
            this.createBackup();
        });

        // Real-time validation
        this.setupValidation();
    }

    setupTabs() {
        const tabs = document.querySelectorAll('.tab-button');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Update active tab
        document.querySelectorAll('.tab-button').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show corresponding content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    async loadSettings() {
        try {
            const response = await fetch(`${this.apiBase}/settings`);
            const result = await response.json();
            
            if (result.success) {
                this.settings = result.data;
                this.populateForm();
                this.loadBackups();
            } else {
                this.showError('Failed to load settings: ' + result.error);
            }
        } catch (error) {
            this.showError('Error loading settings: ' + error.message);
        }
    }

    populateForm() {
        // General settings
        this.setCheckbox('auto-start', this.settings.general.autoStart);
        this.setSelect('log-level', this.settings.general.logLevel);
        this.setInput('max-sessions', this.settings.general.maxSessions);
        this.setInput('session-timeout', this.settings.general.sessionTimeout);

        // Security settings
        this.setCheckbox('enable-firewall', this.settings.security.enableFirewall);
        this.setCheckbox('enable-encryption', this.settings.security.enableEncryption);
        this.setCheckbox('require-auth', this.settings.security.requireAuthentication);
        this.setTextarea('allowed-ips', this.settings.security.allowedIPs.join('\n'));
        this.setTextarea('blocked-ips', this.settings.security.blockedIPs.join('\n'));

        // Performance settings
        this.setCheckbox('enable-compression', this.settings.performance.enableCompression);
        this.setCheckbox('enable-caching', this.settings.performance.enableCaching);
        this.setInput('max-bandwidth', this.settings.performance.maxBandwidth);
        this.setSelect('quality', this.settings.performance.quality);

        // Monitoring settings
        this.setCheckbox('enable-logging', this.settings.monitoring.enableLogging);
        this.setSelect('monitoring-log-level', this.settings.monitoring.logLevel);
        this.setCheckbox('enable-metrics', this.settings.monitoring.enableMetrics);
        this.setInput('alert-threshold', this.settings.monitoring.alertThreshold);

        // Registry settings
        this.setCheckbox('debug-mode', this.settings.registry.debugMode);
        this.setCheckbox('performance-logging', this.settings.registry.performanceLogging);
        this.setInput('custom-registry', this.settings.registry.customRegistry);
        this.setCheckbox('backup-enabled', this.settings.registry.backupEnabled);
    }

    collectFormData() {
        return {
            general: {
                autoStart: this.getCheckbox('auto-start'),
                logLevel: this.getSelect('log-level'),
                maxSessions: parseInt(this.getInput('max-sessions')),
                sessionTimeout: parseInt(this.getInput('session-timeout'))
            },
            security: {
                enableFirewall: this.getCheckbox('enable-firewall'),
                enableEncryption: this.getCheckbox('enable-encryption'),
                requireAuthentication: this.getCheckbox('require-auth'),
                allowedIPs: this.getTextarea('allowed-ips').split('\n').filter(ip => ip.trim()),
                blockedIPs: this.getTextarea('blocked-ips').split('\n').filter(ip => ip.trim())
            },
            performance: {
                enableCompression: this.getCheckbox('enable-compression'),
                enableCaching: this.getCheckbox('enable-caching'),
                maxBandwidth: parseInt(this.getInput('max-bandwidth')),
                quality: this.getSelect('quality')
            },
            monitoring: {
                enableLogging: this.getCheckbox('enable-logging'),
                logLevel: this.getSelect('monitoring-log-level'),
                enableMetrics: this.getCheckbox('enable-metrics'),
                alertThreshold: parseInt(this.getInput('alert-threshold'))
            },
            registry: {
                debugMode: this.getCheckbox('debug-mode'),
                performanceLogging: this.getCheckbox('performance-logging'),
                customRegistry: this.getInput('custom-registry'),
                backupEnabled: this.getCheckbox('backup-enabled')
            }
        };
    }

    async saveSettings() {
        const settings = this.collectFormData();
        
        try {
            const response = await fetch(`${this.apiBase}/settings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Settings saved successfully');
                this.settings = settings;
            } else {
                this.showError('Failed to save settings: ' + result.error);
            }
        } catch (error) {
            this.showError('Error saving settings: ' + error.message);
        }
    }

    async resetSettings() {
        if (!confirm('Are you sure you want to reset all settings to defaults?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/settings/reset`, {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Settings reset to defaults');
                await this.loadSettings();
            } else {
                this.showError('Failed to reset settings: ' + result.error);
            }
        } catch (error) {
            this.showError('Error resetting settings: ' + error.message);
        }
    }

    async createBackup() {
        try {
            const response = await fetch(`${this.apiBase}/settings/backup`, {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Backup created successfully');
                await this.loadBackups();
            } else {
                this.showError('Failed to create backup: ' + result.error);
            }
        } catch (error) {
            this.showError('Error creating backup: ' + error.message);
        }
    }

    async loadBackups() {
        try {
            const response = await fetch(`${this.apiBase}/settings/backups`);
            const result = await response.json();
            
            if (result.success) {
                this.displayBackups(result.data);
            }
        } catch (error) {
            console.error('Error loading backups:', error);
        }
    }

    displayBackups(backups) {
        const container = document.getElementById('backups-list');
        container.innerHTML = '';

        if (backups.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No backups available</p>';
            return;
        }

        backups.forEach(backup => {
            const div = document.createElement('div');
            div.className = 'backup-item';
            div.innerHTML = `
                <div class="backup-info">
                    <span class="backup-name">${backup.name}</span>
                    <span class="backup-date">${new Date(backup.date).toLocaleString()}</span>
                </div>
                <div class="backup-actions">
                    <button class="btn btn-sm btn-primary" onclick="settingsManager.restoreBackup('${backup.name}')">
                        Restore
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="settingsManager.deleteBackup('${backup.name}')">
                        Delete
                    </button>
                </div>
            `;
            container.appendChild(div);
        });
    }

    async restoreBackup(backupName) {
        if (!confirm(`Are you sure you want to restore from ${backupName}?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/settings/restore/${backupName}`, {
                method: 'POST'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Settings restored successfully');
                await this.loadSettings();
            } else {
                this.showError('Failed to restore backup: ' + result.error);
            }
        } catch (error) {
            this.showError('Error restoring backup: ' + error.message);
        }
    }

    async deleteBackup(backupName) {
        if (!confirm(`Are you sure you want to delete ${backupName}?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/settings/restore/${backupName}`, {
                method: 'DELETE'
            });

            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Backup deleted successfully');
                await this.loadBackups();
            } else {
                this.showError('Failed to delete backup: ' + result.error);
            }
        } catch (error) {
            this.showError('Error deleting backup: ' + error.message);
        }
    }

    setupValidation() {
        // Real-time validation for numeric inputs
        const numericInputs = document.querySelectorAll('input[type="number"]');
        numericInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                const min = parseInt(e.target.min) || 0;
                const max = parseInt(e.target.max) || 1000;
                
                if (value < min || value > max) {
                    e.target.classList.add('error');
                } else {
                    e.target.classList.remove('error');
                }
            });
        });

        // IP address validation
        const ipTextareas = document.querySelectorAll('textarea[data-type="ip"]');
        ipTextareas.forEach(textarea => {
            textarea.addEventListener('blur', (e) => {
                const ips = e.target.value.split('\n').filter(ip => ip.trim());
                const invalidIps = ips.filter(ip => !this.isValidIP(ip.trim()));
                
                if (invalidIps.length > 0) {
                    e.target.classList.add('error');
                    this.showError(`Invalid IP addresses: ${invalidIps.join(', ')}`);
                } else {
                    e.target.classList.remove('error');
                }
            });
        });
    }

    isValidIP(ip) {
        const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        const ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;
        
        return ipv4Regex.test(ip) || ipv6Regex.test(ip);
    }

    // Helper methods for form interaction
    getInput(id) {
        return document.getElementById(id).value;
    }

    setInput(id, value) {
        document.getElementById(id).value = value;
    }

    getCheckbox(id) {
        return document.getElementById(id).checked;
    }

    setCheckbox(id, value) {
        document.getElementById(id).checked = value;
    }

    getSelect(id) {
        return document.getElementById(id).value;
    }

    setSelect(id, value) {
        document.getElementById(id).value = value;
    }

    getTextarea(id) {
        return document.getElementById(id).value;
    }

    setTextarea(id, value) {
        document.getElementById(id).value = Array.isArray(value) ? value.join('\n') : value;
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});
