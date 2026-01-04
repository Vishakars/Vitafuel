// client/scripts/dashboard.js

document.addEventListener('DOMContentLoaded', () => {

// --- 1. CONFIGURATION & DOM REFERENCES ---
const deriveApiBase = () => {
    if (window.API_BASE_URL) return window.API_BASE_URL;
    if (window.location.port && window.location.port !== '3000') {
        return `${window.location.origin}/api`;
    }
    return `${window.location.protocol}//${window.location.hostname}:8005/api`;
};

const API_BASE_URL = deriveApiBase();
const API_ORIGIN = window.API_BASE_ORIGIN || API_BASE_URL.replace(/\/api$/, '');
const SERVER_URL = API_ORIGIN;
const userEmail = localStorage.getItem('userEmail');
const accessToken = localStorage.getItem('accessToken');

// --- 2. AUTHENTICATION ---
if (!accessToken || !userEmail) {
    alert('Authentication failed. Please log in.');
    window.location.href = 'login.html';
    return;
}

console.log(`User ${userEmail} is authenticated. Fetching data...`);

// --- 3. DATA FETCHING ---
const fetchDashboardData = async () => {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
    };

    try {
        const [profileResponse, healthResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/profile/${userEmail}`, { headers }),
            fetch(`${API_BASE_URL}/health/${userEmail}`, { headers })
        ]);

        if (!profileResponse.ok || !healthResponse.ok) {
            throw new Error('Your session may have expired or the server is unavailable.');
        }

        const profileData = await profileResponse.json();
        const healthData = await healthResponse.json();

        console.log("✅ PROFILE DATA FROM SERVER:", profileData);
        console.log("✅ HEALTH DATA FROM SERVER:", healthData);

        populateUI(profileData, healthData);
        window.__latestProfileData = profileData;

    } catch (error) {
        console.error('❌ Error fetching dashboard data:', error);
        alert('Could not load your dashboard. ' + error.message);
    }
};

// --- 4. UI POPULATION ---
const populateUI = (profile, health) => {
    if (!profile || !profile.profile) {
        console.error("Profile data is missing or malformed.");
        return;
    }

    const { profile: userProfile } = profile;
    const { demographics } = userProfile;

    const welcomeEl = document.getElementById('welcome-message');
    if (welcomeEl && demographics?.fullName) {
        welcomeEl.textContent = `Welcome, ${demographics.fullName.split(' ')[0]}!`;
    }

    console.log("✅ UI has been populated with the latest data.");
};


// --- 6. LOGOUT ---
const logoutLink = document.querySelector('a[href*="logout"]');
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.clear();
        alert('You have been successfully logged out.');
        window.location.href = 'login.html';
    });
}

// --- INITIALIZE ---
fetchDashboardData();

});
