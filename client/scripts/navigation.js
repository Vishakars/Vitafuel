// Shared navigation functionality for all pages
// This script provides consistent navigation across all pages

(function configureApiBase() {
    if (window.__vitafuelApiConfigured) {
        return;
    }

    const explicitOrigin = window.__VITAFUEL_API_ORIGIN;
    const storedOrigin = localStorage.getItem('vitafuel_api_origin');
    const derivedOrigin = deriveDefaultOrigin();

    const apiOrigin = sanitizeOrigin(explicitOrigin || storedOrigin || derivedOrigin);
    window.API_BASE_ORIGIN = apiOrigin;
    window.API_BASE_URL = `${apiOrigin}/api`;
    window.__vitafuelApiConfigured = true;

    const legacyHosts = [
        'http://127.0.0.1:8005',
        'https://127.0.0.1:8005',
        'http://localhost:8005',
        'https://localhost:8005'
    ];

    const originalFetch = window.fetch.bind(window);
    window.fetch = function(resource, options) {
        let rewrittenResource = resource;

        if (typeof resource === 'string') {
            rewrittenResource = rewriteUrl(resource);
        } else if (resource instanceof Request) {
            const rewrittenUrl = rewriteUrl(resource.url);
            if (rewrittenUrl !== resource.url) {
                rewrittenResource = new Request(rewrittenUrl, resource);
            }
        }

        return originalFetch(rewrittenResource, options);
    };

    function rewriteUrl(url) {
        if (!url) return url;

        if (url.startsWith('/api/')) {
            return `${apiOrigin}${url}`;
        }

        if (url.startsWith('api/')) {
            return `${apiOrigin}/${url.replace(/^api\//, '')}`;
        }

        for (const legacy of legacyHosts) {
            if (url.startsWith(legacy)) {
                return url.replace(legacy, apiOrigin);
            }
        }

        return url;
    }

    function deriveDefaultOrigin() {
        if (window.location.port && window.location.port !== '3000') {
            return window.location.origin;
        }
        return `${window.location.protocol}//${window.location.hostname}:8005`;
    }

    function sanitizeOrigin(origin) {
        if (!origin) return deriveDefaultOrigin();
        return origin.replace(/\/+$/, '');
    }
})();

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation for all pages
    initializeNavigation();
});

function initializeNavigation() {
    // Get current user info
    const currentUser = localStorage.getItem('userEmail');
    const accessToken = localStorage.getItem('accessToken');
    
    // Redirect to login if not authenticated (except for login/register pages)
    const currentPage = window.location.pathname.split('/').pop();
    const publicPages = ['login.html', 'register.html', 'register1.html', 'index.html'];
    
    if (!currentUser && !publicPages.includes(currentPage)) {
        window.location.href = 'login.html';
        return;
    }
    
    // Update profile circle with user's name
    updateProfileCircle();
    
    // Set active navigation link
    setActiveNavLink();
}

async function updateProfileCircle() {
    const profileCircle = document.getElementById("user-profile");
    if (!profileCircle) return;
    
    const currentUser = localStorage.getItem('userEmail');
    const savedAvatar = localStorage.getItem('userAvatar');
    
    try {
        if (currentUser) {
            // If we have a saved avatar, display it
            if (savedAvatar) {
                profileCircle.style.backgroundImage = `url(${savedAvatar})`;
                profileCircle.style.backgroundSize = 'cover';
                profileCircle.textContent = ''; // Clear initials when showing avatar
                return;
            }
            
            // Fall back to initials if no avatar
            const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
            const response = await fetch(`${apiBaseUrl}/profile/${currentUser}`);
            if (response.ok) {
                const data = await response.json();
                const name = data.profile?.demographics?.firstName || data.email;
                profileCircle.textContent = name.charAt(0).toUpperCase();
                profileCircle.title = name;
            }
        }
    } catch (error) {
        console.log('Could not fetch profile, using fallback');
        const emailUsername = currentUser.split('@')[0];
        profileCircle.textContent = emailUsername[0].toUpperCase();
        profileCircle.title = emailUsername;
    }

    
    // Add click handler for profile dropdown
    const profileDropdown = document.getElementById("profileDropdown");
    if (profileDropdown) {
        profileCircle.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            profileDropdown.classList.toggle("show");
        });
        
        // Hide dropdown when clicking outside
        window.addEventListener("click", function (e) {
            if (!profileCircle.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove("show");
            }
        });
    }
}

function setActiveNavLink() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}

// Logout functionality
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

// Make logout function globally available
window.logout = logout;
