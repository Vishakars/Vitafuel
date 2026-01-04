// User Authentication and Data Isolation Utility
class UserAuth {
    constructor() {
        this.userEmail = null;
        this.accessToken = null;
        this.isAuthenticated = false;
        this.init();
    }

    init() {
        this.userEmail = localStorage.getItem('userEmail') || localStorage.getItem('recentEmail');
        this.accessToken = localStorage.getItem('accessToken');
        this.isAuthenticated = !!(this.userEmail && this.accessToken);
        
        // Validate authentication
        if (!this.isAuthenticated) {
            console.warn('User not authenticated - redirecting to login');
            this.redirectToLogin();
        }
    }

    // Get current user email (primary identifier)
    getCurrentUser() {
        if (!this.userEmail) {
            console.error('No user email found - user not authenticated');
            this.redirectToLogin();
            return null;
        }
        return this.userEmail;
    }

    // Get access token for API calls
    getAccessToken() {
        if (!this.accessToken) {
            console.warn('No access token found - API calls will fail');
            return null;
        }
        return this.accessToken;
    }

    // Check if user is authenticated
    isUserAuthenticated() {
        return this.isAuthenticated;
    }

    // Get user-specific localStorage key
    getUserKey(key) {
        const user = this.getCurrentUser();
        if (!user) return null;
        return `${user}_${key}`;
    }

    // Get user-specific data from localStorage
    getUserData(key, defaultValue = null) {
        const userKey = this.getUserKey(key);
        if (!userKey) return defaultValue;
        
        try {
            const data = localStorage.getItem(userKey);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error(`Error parsing user data for key ${key}:`, error);
            return defaultValue;
        }
    }

    // Set user-specific data in localStorage
    setUserData(key, data) {
        const userKey = this.getUserKey(key);
        if (!userKey) return false;
        
        try {
            localStorage.setItem(userKey, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error(`Error saving user data for key ${key}:`, error);
            return false;
        }
    }

    // Clear all user-specific data
    clearUserData() {
        const user = this.getCurrentUser();
        if (!user) return;

        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(`${user}_`)) {
                keysToRemove.push(key);
            }
        }

        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log(`Cleared ${keysToRemove.length} user-specific data entries`);
    }

    // Logout and clear all data
    logout() {
        // Clear authentication data
        localStorage.removeItem('userEmail');
        localStorage.removeItem('recentEmail');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('currentUser');
        
        // Clear user-specific data
        this.clearUserData();
        
        // Reset state
        this.userEmail = null;
        this.accessToken = null;
        this.isAuthenticated = false;
        
        // Redirect to login
        this.redirectToLogin();
    }

    // Redirect to login page
    redirectToLogin() {
        if (window.location.pathname !== '/login.html' && !window.location.pathname.includes('login.html')) {
            // Redirect to the correct server port
            window.location.href = 'login.html';
        }
    }

    // Validate user session
    async validateSession() {
        if (!this.isAuthenticated) {
            return false;
        }

        try {
            const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
            const response = await fetch(`${apiBaseUrl}/profile/me`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (response.ok) {
                return true;
            } else if (response.status === 401) {
                console.warn('Session expired - redirecting to login');
                this.logout();
                return false;
            } else {
                console.warn('Session validation failed:', response.status);
                return false;
            }
        } catch (error) {
            console.error('Error validating session:', error);
            return false;
        }
    }

    // Get user profile data
    async getUserProfile() {
        if (!this.isAuthenticated) {
            return null;
        }

        try {
            const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
            const response = await fetch(`${apiBaseUrl}/profile/me`, {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                console.error('Failed to fetch user profile:', response.status);
                return null;
            }
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return null;
        }
    }

    // Ensure data isolation - prevent cross-user data access
    ensureDataIsolation() {
        const currentUser = this.getCurrentUser();
        if (!currentUser) return;

        // Check for any localStorage keys that might be shared between users
        const suspiciousKeys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && !key.includes('_') && !this.isSystemKey(key)) {
                suspiciousKeys.push(key);
            }
        }

        if (suspiciousKeys.length > 0) {
            console.log('Found potentially shared data keys:', suspiciousKeys);
            console.log('These keys will be migrated to user-specific storage');
            
            // Migrate shared keys to user-specific keys
            const userEmail = localStorage.getItem('userEmail');
            if (userEmail) {
                const userPrefix = `vitafuel_${userEmail.replace('@', '_').replace('.', '_')}_`;
                suspiciousKeys.forEach(key => {
                    const value = localStorage.getItem(key);
                    const newKey = `${userPrefix}${key}`;
                    localStorage.setItem(newKey, value);
                    localStorage.removeItem(key);
                    console.log(`Migrated key: ${key} -> ${newKey}`);
                });
                console.log(`Migrated ${suspiciousKeys.length} keys to user-specific storage`);
            }
        }
    }

    // Check if a key is a system key (not user-specific)
    isSystemKey(key) {
        const systemKeys = [
            'accessToken',
            'userEmail',
            'recentEmail',
            'currentUser',
            'theme',
            'language',
            'lastLogin',
            'appVersion'
        ];
        return systemKeys.includes(key);
    }

    // Get user's first name for display
    getUserDisplayName() {
        const user = this.getCurrentUser();
        if (!user) return 'User';

        // Try to get from profile data
        const profileData = this.getUserData('profile');
        if (profileData && profileData.demographics) {
            const firstName = profileData.demographics.firstName;
            if (firstName) return firstName;
        }

        // Fallback to email username
        return user.split('@')[0];
    }

    // Get user's initials for profile circle
    getUserInitials() {
        const displayName = this.getUserDisplayName();
        return displayName.charAt(0).toUpperCase();
    }
}

// Create global instance
window.userAuth = new UserAuth();

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserAuth;
}
