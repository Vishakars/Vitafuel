// Common functionality for all health domains
class HealthDomainManager {
    constructor(domainName, currentUser) {
        this.domainName = domainName;
        this.currentUser = currentUser;
        this.data = [];
        this.charts = {};
        this.initialized = false;
    }

    async initialize() {
        if (!this.initialized) {
            this.data = await this.loadData();
            this.initialized = true;
        }
        return this.data;
    }

    // Data management
    async loadData() {
        // Try to load from API first
        try {
            const accessToken = localStorage.getItem('accessToken');
            if (accessToken && this.currentUser) {
                const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
                const response = await fetch(`${apiBaseUrl}/${this.domainName}/me`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                if (response.ok) {
                    const apiData = await response.json();
                    console.log(`✅ ${this.domainName} data loaded from API:`, apiData);
                    // Handle different response formats
                    if (Array.isArray(apiData)) {
                        return apiData;
                    } else if (apiData[this.domainName]) {
                        return apiData[this.domainName];
                    } else if (apiData.anemia) {
                        return apiData.anemia;
                    }
                    return apiData;
                } else {
                    console.warn(`⚠️ Failed to load ${this.domainName} from API:`, response.status);
                }
            }
        } catch (error) {
            console.warn(`⚠️ Error loading ${this.domainName} from API:`, error);
        }
        
        // Fallback to localStorage
        const stored = localStorage.getItem(`${this.currentUser}_${this.domainName}Data`);
        return stored ? JSON.parse(stored) : [];
    }

    async saveData() {
        // Save to localStorage
        localStorage.setItem(`${this.currentUser}_${this.domainName}Data`, JSON.stringify(this.data));
        
        // Also try to save to API
        try {
            const accessToken = localStorage.getItem('accessToken');
            if (accessToken && this.currentUser) {
                // For now, we'll save to localStorage and let individual pages handle API saves
                // This is because different domains have different data structures
                console.log(`💾 ${this.domainName} data saved to localStorage`);
            }
        } catch (error) {
            console.warn(`⚠️ Error saving ${this.domainName} to API:`, error);
        }
    }

    addEntry(entry) {
        entry.id = Date.now();
        entry.timestamp = new Date().toISOString();
        this.data.unshift(entry);
        this.saveData();
        return entry;
    }

    removeEntry(id) {
        this.data = this.data.filter(entry => entry.id !== id);
        this.saveData();
    }

    clearAllData() {
        if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
            this.data = [];
            this.saveData();
            return true;
        }
        return false;
    }

    // Chart management
    initializeChart(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (ctx && typeof Chart !== 'undefined') {
            this.charts[canvasId] = new Chart(ctx, config);
            return true;
        }
        return false;
    }

    updateChart(canvasId, newData) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].data = newData;
            this.charts[canvasId].update();
        }
    }

    // Utility functions
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatTime(date) {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    getTodayEntries() {
        const today = new Date().toISOString().split('T')[0];
        return this.data.filter(entry => 
            new Date(entry.timestamp).toISOString().split('T')[0] === today
        );
    }

    getLastNDays(n) {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - n);
        return this.data.filter(entry => 
            new Date(entry.timestamp) >= cutoff
        );
    }

    // Notification system
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Set background color based on type
        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            warning: '#ff9800',
            info: '#2196F3'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // Form validation
    validateForm(formData, requiredFields) {
        for (const field of requiredFields) {
            if (!formData[field] || formData[field].toString().trim() === '') {
                this.showNotification(`Please fill in the ${field} field`, 'error');
                return false;
            }
        }
        return true;
    }

    // Export functionality
    exportData(format = 'json') {
        const dataToExport = {
            domain: this.domainName,
            user: this.currentUser,
            exportDate: new Date().toISOString(),
            data: this.data
        };

        if (format === 'json') {
            const blob = new Blob([JSON.stringify(dataToExport, null, 2)], {
                type: 'application/json'
            });
            this.downloadFile(blob, `${this.domainName}_data.json`);
        } else if (format === 'csv') {
            const csv = this.convertToCSV(dataToExport.data);
            const blob = new Blob([csv], { type: 'text/csv' });
            this.downloadFile(blob, `${this.domainName}_data.csv`);
        }
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => 
                JSON.stringify(row[header] || '')
            ).join(','))
        ].join('\n');
        
        return csvContent;
    }

    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Reset functionality
    resetAll() {
        if (this.clearAllData()) {
            this.showNotification('All data has been cleared', 'success');
            // Trigger custom reset logic if needed
            if (typeof this.onReset === 'function') {
                this.onReset();
            }
        }
    }
}

// Common chart configurations
const ChartConfigs = {
    line: (data, labels, title, color = '#a15e32') => ({
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true },
                title: { display: true, text: title }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    }),

    bar: (data, labels, title, colors = ['#a15e32', '#d2996a', '#8b6c58']) => ({
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: { display: true, text: title }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    }),

    doughnut: (data, labels, title, colors = ['#a15e32', '#d2996a', '#8b6c58', '#7b5a3a']) => ({
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'bottom' },
                title: { display: true, text: title }
            }
        }
    })
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HealthDomainManager, ChartConfigs };
}
