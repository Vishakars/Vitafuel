// Enhanced 6-Step Registration Process JavaScript
// This file provides additional functionality for the multi-step registration form

document.addEventListener('DOMContentLoaded', function() {
    // Initialize particle trail animation
    createParticleTrail();
    
    // Setup slider value displays
    setupSliderDisplays();
    
    // Setup input animations
    setupInputAnimations();
    
    // Setup mouse trail effect
    setupMouseTrail();
});

function createParticleTrail() {
    const trail = document.getElementById('particleTrail');
    if (!trail) return;
    
    const particleCount = 20;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'trail-particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 4) + 's';
        trail.appendChild(particle);
    }
}

function setupSliderDisplays() {
    // Weekly goal slider
    const weeklyGoalSlider = document.getElementById('weeklyGoal');
    const weeklyGoalValue = document.getElementById('weeklyGoalValue');
    if (weeklyGoalSlider && weeklyGoalValue) {
        weeklyGoalSlider.addEventListener('input', function() {
            weeklyGoalValue.textContent = `${this.value} day${this.value > 1 ? 's' : ''}`;
        });
    }
    
    // Stress level slider
    const stressLevelSlider = document.getElementById('stressLevel');
    const stressLevelValue = document.getElementById('stressLevelValue');
    if (stressLevelSlider && stressLevelValue) {
        stressLevelSlider.addEventListener('input', function() {
            stressLevelValue.textContent = this.value;
        });
    }
}

function setupInputAnimations() {
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            createRippleEffect(this);
        });
    });
}

function createRippleEffect(element) {
    const ripple = document.createElement('div');
    const rect = element.getBoundingClientRect();
    ripple.style.position = 'absolute';
    ripple.style.left = rect.left + rect.width / 2 + 'px';
    ripple.style.top = rect.top + rect.height / 2 + 'px';
    ripple.style.width = '10px';
    ripple.style.height = '10px';
    ripple.style.background = 'rgba(140, 94, 42, 0.3)';
    ripple.style.borderRadius = '50%';
    ripple.style.transform = 'translate(-50%, -50%)';
    ripple.style.pointerEvents = 'none';
    ripple.style.zIndex = '1';
    document.body.appendChild(ripple);
    
    ripple.animate([
        { transform: 'translate(-50%, -50%) scale(0)', opacity: 1 },
        { transform: 'translate(-50%, -50%) scale(10)', opacity: 0 }
    ], { duration: 600, easing: 'ease-out' })
    .onfinish = () => ripple.remove();
}

function setupMouseTrail() {
    let mouseTrail = [];
    document.addEventListener('mousemove', (e) => {
        mouseTrail.push({ x: e.clientX, y: e.clientY, time: Date.now() });
        if (mouseTrail.length > 20) mouseTrail.shift();
        
        if (Math.random() < 0.1) {
            const trail = document.createElement('div');
            trail.style.position = 'fixed';
            trail.style.left = e.clientX + 'px';
            trail.style.top = e.clientY + 'px';
            trail.style.width = '3px';
            trail.style.height = '3px';
            trail.style.background = 'rgba(140, 94, 42, 0.6)';
            trail.style.borderRadius = '50%';
            trail.style.pointerEvents = 'none';
            trail.style.zIndex = '5';
            document.body.appendChild(trail);
            
            trail.animate([
                { opacity: 1, transform: 'scale(1)' },
                { opacity: 0, transform: 'scale(0)' }
            ], { duration: 500, easing: 'ease-out' })
            .onfinish = () => trail.remove();
        }
    });
}

function createSuccessParticles() {
    const colors = ['#4CAF50', '#45a049', '#66BB6A'];
    for (let i = 0; i < 15; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = Math.random() * 8 + 4 + 'px';
        particle.style.height = particle.style.width;
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.borderRadius = '50%';
        particle.style.left = '50%';
        particle.style.top = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '1000';
        document.body.appendChild(particle);
        
        const angle = (Math.PI * 2 * i) / 15;
        const velocity = Math.random() * 100 + 50;
        particle.animate([
            { transform: 'translate(-50%, -50%) scale(0)', opacity: 1 },
            { transform: `translate(calc(-50% + ${Math.cos(angle) * velocity}px), calc(-50% + ${Math.sin(angle) * velocity}px)) scale(1)`, opacity: 0 }
        ], { duration: 1000, easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' })
        .onfinish = () => particle.remove();
    }
}

// Export functions for use in the main registration flow
window.createSuccessParticles = createSuccessParticles;
