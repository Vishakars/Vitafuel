// MongoDB Integration for Health Domains
class MongoDBIntegration {
    constructor() {
        this.baseURL = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
        this.accessToken = null;
        this.currentUser = null;
        this.init();
    }

    init() {
        // Wait for userAuth to be available
        if (window.userAuth) {
            this.accessToken = window.userAuth.getAccessToken();
            this.currentUser = window.userAuth.getCurrentUser();
        } else {
            // Fallback to direct localStorage access
            this.accessToken = localStorage.getItem('accessToken');
            this.currentUser = localStorage.getItem('userEmail') || localStorage.getItem('recentEmail');
        }
    }

    // Generic save function for any health domain
    async saveData(data, domain, endpoint = null) {
        console.log(`🔍 MongoDB saveData called for domain: ${domain}`);
        console.log(`🔍 Data to save:`, data);
        console.log(`🔍 Current user:`, this.currentUser);
        console.log(`🔍 Access token available:`, !!this.accessToken);
        
        if (!this.accessToken) {
            console.warn('No access token found, saving to localStorage only');
            return false;
        }

        const url = endpoint || `${this.baseURL}/${domain}/${this.currentUser}`;
        console.log(`🔍 API URL:`, url);
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify(data)
            });

            console.log(`🔍 Response status:`, response.status);
            console.log(`🔍 Response ok:`, response.ok);

            if (response.ok) {
                console.log(`✅ Data saved to MongoDB via ${domain}`);
                return true;
            } else {
                const errorText = await response.text();
                console.error(`❌ Failed to save to MongoDB: ${response.status} - ${errorText}`);
                return false;
            }
        } catch (error) {
            console.error('❌ Error saving to MongoDB:', error);
            return false;
        }
    }

    // Generic load function for any health domain
    async loadData(domain, endpoint = null) {
        if (!this.accessToken) {
            console.warn('No access token found, loading from localStorage only');
            return [];
        }

        const url = endpoint || `${this.baseURL}/${domain}/${this.currentUser}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Data loaded from MongoDB via ${domain}`);
                return data;
            } else {
                console.error(`❌ Failed to load from MongoDB: ${response.status}`);
                return [];
            }
        } catch (error) {
            console.error('❌ Error loading from MongoDB:', error);
            return [];
        }
    }

    // Update existing data
    async updateData(data, domain, entryId, endpoint = null) {
        if (!this.accessToken) {
            console.warn('No access token found, updating localStorage only');
            return false;
        }

        const url = endpoint || `${this.baseURL}/${domain}/${localStorage.getItem('userEmail')}/${entryId}`;
        
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.accessToken}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                console.log(`✅ Data updated in MongoDB via ${domain}`);
                return true;
            } else {
                console.error(`❌ Failed to update in MongoDB: ${response.status}`);
                return false;
            }
        } catch (error) {
            console.error('❌ Error updating in MongoDB:', error);
            return false;
        }
    }

    // Delete data
    async deleteData(domain, entryId, endpoint = null) {
        if (!this.accessToken) {
            console.warn('No access token found, deleting from localStorage only');
            return false;
        }

        const url = endpoint || `${this.baseURL}/${domain}/${localStorage.getItem('userEmail')}/${entryId}`;
        
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (response.ok) {
                console.log(`✅ Data deleted from MongoDB via ${domain}`);
                return true;
            } else {
                console.error(`❌ Failed to delete from MongoDB: ${response.status}`);
                return false;
            }
        } catch (error) {
            console.error('❌ Error deleting from MongoDB:', error);
            return false;
        }
    }

    // Sync localStorage with MongoDB
    async syncWithMongoDB(domain, localStorageKey, data = null) {
        // Load from localStorage if no data provided
        if (!data) {
            const stored = localStorage.getItem(localStorageKey);
            data = stored ? JSON.parse(stored) : [];
        }

        // Try to save to MongoDB
        const mongoSaved = await this.saveData(data, domain);
        
        if (mongoSaved) {
            console.log(`✅ ${domain} data synced to MongoDB`);
            return true;
        } else {
            console.log(`⚠️ ${domain} data remains in localStorage only`);
            return false;
        }
    }

    // Load from MongoDB with localStorage fallback
    async loadWithFallback(domain, localStorageKey) {
        // Try MongoDB first
        const mongoData = await this.loadData(domain);
        
        if (mongoData && mongoData.length > 0) {
            // Update localStorage with MongoDB data
            localStorage.setItem(localStorageKey, JSON.stringify(mongoData));
            return mongoData;
        }

        // Fallback to localStorage
        const stored = localStorage.getItem(localStorageKey);
        if (stored) {
            try {
                const data = JSON.parse(stored);
                console.log(`✅ ${domain} data loaded from localStorage fallback`);
                return data;
            } catch (e) {
                console.error(`❌ Failed to parse ${domain} data from localStorage:`, e);
                return [];
            }
        }

        return [];
    }

    // Health domain specific methods
    async saveDiabetesReading(reading) {
        return await this.saveData(reading, 'diabetes');
    }

    async loadDiabetesReadings() {
        return await this.loadWithFallback('diabetes', `diabetesData_${this.currentUser}`);
    }

    async saveSleepEntry(entry) {
        return await this.saveData(entry, 'sleep');
    }

    async loadSleepData() {
        return await this.loadWithFallback('sleep', `sleepData_${this.currentUser}`);
    }

    async saveBloodPressureReading(reading) {
        return await this.saveData(reading, 'bp');
    }

    async loadBloodPressureReadings() {
        return await this.loadWithFallback('bp', `bpData_${this.currentUser}`);
    }

    async saveMentalHealthEntry(entry) {
        return await this.saveData(entry, 'mental');
    }

    async loadMentalHealthData() {
        return await this.loadWithFallback('mental', `mentalHealthData_${this.currentUser}`);
    }

    async saveWeightEntry(entry) {
        return await this.saveData(entry, 'obesity');
    }

    async loadWeightData() {
        return await this.loadWithFallback('obesity', `weightData_${this.currentUser}`);
    }

    async saveThyroidReading(reading) {
        return await this.saveData(reading, 'thyroid');
    }

    async loadThyroidData() {
        return await this.loadWithFallback('thyroid', `thyroidData_${this.currentUser}`);
    }

    async saveAnemiaEntry(entry) {
        return await this.saveData(entry, 'anemia');
    }

    async loadAnemiaData() {
        return await this.loadWithFallback('anemia', `anemiaData_${this.currentUser}`);
    }

    async saveSkinHealthEntry(entry) {
        return await this.saveData(entry, 'skin');
    }

    async loadSkinHealthData() {
        return await this.loadWithFallback('skin', `skinHealthData_${this.currentUser}`);
    }

    async saveSinusitisEntry(entry) {
        return await this.saveData(entry, 'sinusitis');
    }

    async loadSinusitisData() {
        return await this.loadWithFallback('sinusitis', `sinusitisData_${this.currentUser}`);
    }

    async saveMenstruationEntry(entry) {
        return await this.saveData(entry, 'menstruation');
    }

    async loadMenstruationData() {
        return await this.loadWithFallback('menstruation', `menstruationData_${this.currentUser}`);
    }
}

// Create global instance
window.mongoDB = new MongoDBIntegration();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MongoDBIntegration;
}
