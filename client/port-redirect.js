/**
 * Port Redirect Script
 * Automatically redirects users from wrong ports to the correct port
 */

(function() {
    'use strict';
    
    // Correct ports configuration
    const CORRECT_FRONTEND_PORT = '3000';
    const CORRECT_BACKEND_PORT = '8005';
    const CORRECT_URL = `http://127.0.0.1:${CORRECT_FRONTEND_PORT}`;
    
    // Wrong ports that should be redirected
    const WRONG_PORTS = ['5502', '8004', '8000', '5050'];
    
    function checkAndRedirect() {
        const currentPort = window.location.port;
        const currentHost = window.location.hostname;
        
        // Only redirect if we're on localhost/127.0.0.1 and using a wrong port
        if ((currentHost === 'localhost' || currentHost === '127.0.0.1') && 
            WRONG_PORTS.includes(currentPort)) {
            
            console.warn(`⚠️ Wrong port detected: ${currentPort}. Redirecting to correct port: ${CORRECT_FRONTEND_PORT}`);
            
            // Show user-friendly message
            const message = `You're accessing VitaFuel from the wrong port (${currentPort}).\n\nRedirecting to the correct URL for the best experience...`;
            
            if (confirm(message)) {
                // Redirect to correct URL
                const currentPath = window.location.pathname;
                const newUrl = `${CORRECT_URL}${currentPath}`;
                window.location.href = newUrl;
            } else {
                // User chose not to redirect, show warning
                alert('⚠️ You may experience errors with data saving.\n\nFor the best experience, please use:\n' + CORRECT_URL);
            }
        }
    }
    
    // Check on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAndRedirect);
    } else {
        checkAndRedirect();
    }
    
    // Also check when the page becomes visible (in case of tab switching)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            checkAndRedirect();
        }
    });
    
    // Add a global function to manually check port
    window.checkVitaFuelPort = function() {
        const currentPort = window.location.port;
        const isCorrectPort = currentPort === CORRECT_FRONTEND_PORT;
        
        if (!isCorrectPort) {
            console.warn(`Current port: ${currentPort}, Correct port: ${CORRECT_FRONTEND_PORT}`);
            return false;
        }
        
        console.log('✅ Using correct port:', currentPort);
        return true;
    };
    
    // Add port status indicator to console
    console.log('🔍 VitaFuel Port Checker loaded');
    console.log(`Current URL: ${window.location.href}`);
    console.log(`Current Port: ${window.location.port}`);
    console.log(`Correct Port: ${CORRECT_FRONTEND_PORT}`);
    
    if (window.location.port === CORRECT_FRONTEND_PORT) {
        console.log('✅ Using correct port!');
    } else {
        console.warn('⚠️ Using wrong port - may cause issues');
    }
    
})();
