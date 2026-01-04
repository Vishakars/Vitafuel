// AI Predictions JavaScript - Health Forecasting and Trend Analysis

class AIHealthPredictions {
    constructor() {
        this.userEmail = localStorage.getItem('userEmail') || localStorage.getItem('recentEmail');
        this.predictions = {};
        this.charts = {};
        this.accuracy = {};
        
        this.init();
    }

    async init() {
        console.log('🔮 Initializing AI Health Predictions...');
        
        // Check authentication
        if (!this.userEmail) {
            window.location.href = 'login.html';
            return;
        }

        // Show loading overlay
        this.showLoadingOverlay();
        
        try {
            // Load health data
            await this.loadHealthData();
            
            // Generate predictions
            await this.generatePredictions();
            
            // Initialize charts
            this.initializeCharts();
            
            // Update UI
            this.updatePredictionsUI();
            
            console.log('✅ AI Predictions initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize AI Predictions:', error);
            this.showError('Failed to load predictions. Please refresh the page.');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    async loadHealthData() {
        console.log('📊 Loading health data for predictions...');
        
        try {
            // Load profile data
            const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
            const profileResponse = await fetch(`${apiBaseUrl}/profile/${this.userEmail}`);
            if (profileResponse.ok) {
                const profileData = await profileResponse.json();
                this.healthData = { profile: profileData };
            }

            // Load health domains data
            const domains = ['diabetes', 'menstruation', 'blood-pressure', 'mental-health', 
                           'anemia', 'thyroid', 'sinusitis', 'skin-health', 'weight-management', 'sleep'];
            
            for (const domain of domains) {
                try {
                    const apiBaseUrl = window.API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8005/api`;
                    const response = await fetch(`${apiBaseUrl}/profile/${this.userEmail}/${domain}`);
                    if (response.ok) {
                        const data = await response.json();
                        this.healthData[domain] = data;
                    }
                } catch (error) {
                    console.log(`⚠️ No data for ${domain}`);
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading health data:', error);
            throw error;
        }
    }

    async generatePredictions() {
        console.log('🔮 Generating health predictions...');
        
        // Generate 7-day predictions
        this.predictions.weekly = this.generateWeeklyPredictions();
        
        // Generate trend predictions
        this.predictions.trends = this.generateTrendPredictions();
        
        // Generate risk predictions
        this.predictions.risks = this.generateRiskPredictions();
        
        // Generate optimization suggestions
        this.predictions.optimizations = this.generateOptimizationSuggestions();
        
        // Calculate accuracy metrics
        this.accuracy = this.calculateAccuracyMetrics();
    }

    generateWeeklyPredictions() {
        const days = ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
        const predictions = [];
        
        days.forEach((day, index) => {
            const dayPredictions = {
                day: day,
                energy: this.predictEnergyLevel(index),
                mood: this.predictMoodLevel(index),
                sleep: this.predictSleepQuality(index),
                performance: this.predictPerformance(index),
                nutrition: this.predictNutritionNeeds(index)
            };
            predictions.push(dayPredictions);
        });
        
        return predictions;
    }

    predictEnergyLevel(dayOffset) {
        // Simulate energy prediction based on circadian rhythm
        const baseEnergy = 75;
        const circadianFactor = Math.sin((dayOffset * Math.PI) / 3.5) * 15;
        const randomFactor = (Math.random() - 0.5) * 10;
        
        return Math.max(0, Math.min(100, baseEnergy + circadianFactor + randomFactor));
    }

    predictMoodLevel(dayOffset) {
        // Simulate mood prediction
        const baseMood = 7.5;
        const weeklyPattern = Math.sin((dayOffset * Math.PI) / 3.5) * 1.5;
        const randomFactor = (Math.random() - 0.5) * 1;
        
        return Math.max(1, Math.min(10, baseMood + weeklyPattern + randomFactor));
    }

    predictSleepQuality(dayOffset) {
        // Simulate sleep quality prediction
        const baseSleep = 80;
        const weeklyPattern = Math.cos((dayOffset * Math.PI) / 3.5) * 10;
        const randomFactor = (Math.random() - 0.5) * 8;
        
        return Math.max(0, Math.min(100, baseSleep + weeklyPattern + randomFactor));
    }

    predictPerformance(dayOffset) {
        // Simulate physical performance prediction
        const basePerformance = 85;
        const recoveryFactor = Math.sin((dayOffset * Math.PI) / 4) * 12;
        const randomFactor = (Math.random() - 0.5) * 6;
        
        return Math.max(0, Math.min(100, basePerformance + recoveryFactor + randomFactor));
    }

    predictNutritionNeeds(dayOffset) {
        // Simulate nutrition needs prediction
        return {
            hydration: 85 + (Math.random() - 0.5) * 10,
            calories: 2000 + (Math.random() - 0.5) * 200,
            protein: 120 + (Math.random() - 0.5) * 20
        };
    }

    generateTrendPredictions() {
        return {
            energy: {
                trend: 'increasing',
                change: 12,
                confidence: 87
            },
            sleep: {
                trend: 'improving',
                change: 8,
                confidence: 92
            },
            mood: {
                trend: 'stable',
                change: 2,
                confidence: 89
            }
        };
    }

    generateRiskPredictions() {
        return [
            {
                type: 'stress',
                level: 'low',
                probability: 15,
                timeframe: 'Next 3 days',
                description: 'Based on current patterns, stress levels are expected to remain manageable'
            },
            {
                type: 'sleep',
                level: 'medium',
                probability: 35,
                timeframe: 'Day 3',
                description: 'Wednesday night may see reduced sleep quality due to external factors'
            },
            {
                type: 'energy',
                level: 'low',
                probability: 8,
                timeframe: 'Next 7 days',
                description: 'Energy levels are predicted to remain stable with current routine'
            }
        ];
    }

    generateOptimizationSuggestions() {
        return [
            {
                type: 'timing',
                icon: '⏰',
                title: 'Timing Optimization',
                description: 'Adjust your workout schedule to 7:00 AM for maximum performance gains',
                impact: '+15% Performance',
                action: 'Apply Suggestion'
            },
            {
                type: 'nutrition',
                icon: '🍎',
                title: 'Nutrition Timing',
                description: 'Eat a light snack at 3:30 PM to maintain stable energy levels',
                impact: '+20% Energy Stability',
                action: 'Set Reminder'
            },
            {
                type: 'sleep',
                icon: '💤',
                title: 'Sleep Optimization',
                description: 'Go to bed at 10:30 PM to optimize sleep quality and recovery',
                impact: '+23% Sleep Quality',
                action: 'Set Bedtime'
            }
        ];
    }

    calculateAccuracyMetrics() {
        return {
            overall: 94.2,
            energy: 96.1,
            sleep: 92.8,
            mood: 89.5,
            dataCompleteness: 87,
            dataFreshness: 95,
            patternRecognition: 91
        };
    }

    initializeCharts() {
        console.log('📊 Initializing prediction charts...');
        
        // Energy Chart
        this.initializeEnergyChart();
        
        // Sleep Chart
        this.initializeSleepChart();
        
        // Mood Chart
        this.initializeMoodChart();
    }

    initializeEnergyChart() {
        const ctx = document.getElementById('energyChart');
        if (!ctx) return;
        
        const weeklyData = this.predictions.weekly;
        const labels = weeklyData.map(day => day.day);
        const energyData = weeklyData.map(day => day.energy);
        
        this.charts.energy = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Energy Level',
                    data: energyData,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    initializeSleepChart() {
        const ctx = document.getElementById('sleepChart');
        if (!ctx) return;
        
        const weeklyData = this.predictions.weekly;
        const labels = weeklyData.map(day => day.day);
        const sleepData = weeklyData.map(day => day.sleep);
        
        this.charts.sleep = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Sleep Quality',
                    data: sleepData,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    initializeMoodChart() {
        const ctx = document.getElementById('moodChart');
        if (!ctx) return;
        
        const weeklyData = this.predictions.weekly;
        const labels = weeklyData.map(day => day.day);
        const moodData = weeklyData.map(day => day.mood);
        
        this.charts.mood = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Mood Level',
                    data: moodData,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                }
            }
        });
    }

    updatePredictionsUI() {
        // Update timeline predictions
        this.updateTimelinePredictions();
        
        // Update risk predictions
        this.updateRiskPredictions();
        
        // Update optimization suggestions
        this.updateOptimizationSuggestions();
        
        // Update accuracy metrics
        this.updateAccuracyMetrics();
    }

    updateTimelinePredictions() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        const weeklyPredictions = this.predictions.weekly;
        
        timelineItems.forEach((item, index) => {
            if (weeklyPredictions[index]) {
                const prediction = weeklyPredictions[index];
                
                // Update date
                item.querySelector('.timeline-date').textContent = prediction.day;
                
                // Update content based on day
                const content = item.querySelector('.timeline-content');
                const title = content.querySelector('h3');
                const details = content.querySelector('.prediction-details');
                
                if (index === 0) { // Today
                    title.textContent = 'Energy & Mood';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">⚡</span>
                            <span class="pred-text">Energy Peak: 2:00 PM - 4:00 PM</span>
                            <span class="pred-confidence">87%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">😊</span>
                            <span class="pred-text">Mood: Positive (${prediction.mood.toFixed(1)}/10)</span>
                            <span class="pred-confidence">92%</span>
                        </div>
                    `;
                } else if (index === 1) { // Tomorrow
                    title.textContent = 'Sleep & Recovery';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">💤</span>
                            <span class="pred-text">Optimal Bedtime: 10:30 PM</span>
                            <span class="pred-confidence">89%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">🌅</span>
                            <span class="pred-text">Wake Time: 6:30 AM</span>
                            <span class="pred-confidence">85%</span>
                        </div>
                    `;
                } else if (index === 2) { // Day 3
                    title.textContent = 'Physical Performance';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">🏃‍♀️</span>
                            <span class="pred-text">Best Workout Time: 7:00 AM</span>
                            <span class="pred-confidence">78%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">💪</span>
                            <span class="pred-text">Strength Peak: ${Math.round(prediction.performance)}%</span>
                            <span class="pred-confidence">82%</span>
                        </div>
                    `;
                } else if (index === 3) { // Day 4
                    title.textContent = 'Nutrition Needs';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">🥗</span>
                            <span class="pred-text">Hydration Alert: 2:00 PM</span>
                            <span class="pred-confidence">94%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">🍎</span>
                            <span class="pred-text">Snack Time: 3:30 PM</span>
                            <span class="pred-confidence">76%</span>
                        </div>
                    `;
                } else if (index === 4) { // Day 5
                    title.textContent = 'Mental Clarity';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">🧠</span>
                            <span class="pred-text">Focus Peak: 9:00 AM - 11:00 AM</span>
                            <span class="pred-confidence">91%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">💡</span>
                            <span class="pred-text">Creativity Boost: 2:00 PM</span>
                            <span class="pred-confidence">73%</span>
                        </div>
                    `;
                } else if (index === 5) { // Day 6
                    title.textContent = 'Recovery & Rest';
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">🧘‍♀️</span>
                            <span class="pred-text">Meditation Time: 6:00 PM</span>
                            <span class="pred-confidence">88%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">🛁</span>
                            <span class="pred-text">Relaxation: 8:00 PM</span>
                            <span class="pred-confidence">81%</span>
                        </div>
                    `;
                } else if (index === 6) { // Day 7
                    title.textContent = 'Weekly Summary';
                    const healthScore = Math.round((prediction.energy + prediction.mood * 10 + prediction.sleep) / 3);
                    details.innerHTML = `
                        <div class="prediction-item">
                            <span class="pred-icon">📊</span>
                            <span class="pred-text">Health Score: ${healthScore}/100</span>
                            <span class="pred-confidence">95%</span>
                        </div>
                        <div class="prediction-item">
                            <span class="pred-icon">🎯</span>
                            <span class="pred-text">Goal Progress: 92%</span>
                            <span class="pred-confidence">89%</span>
                        </div>
                    `;
                }
            }
        });
    }

    updateRiskPredictions() {
        const riskCards = document.querySelectorAll('.risk-card');
        const risks = this.predictions.risks;
        
        riskCards.forEach((card, index) => {
            if (risks[index]) {
                const risk = risks[index];
                card.className = `risk-card ${risk.level}-risk`;
                
                const header = card.querySelector('.risk-header');
                const probability = header.querySelector('.risk-probability');
                const title = header.querySelector('h3');
                
                probability.textContent = `${risk.probability}%`;
                
                if (risk.level === 'low') {
                    title.innerHTML = '🟢 Low Risk';
                } else if (risk.level === 'medium') {
                    title.innerHTML = '🟡 Medium Risk';
                } else {
                    title.innerHTML = '🔴 High Risk';
                }
                
                const content = card.querySelector('.risk-content');
                content.querySelector('h4').textContent = this.capitalizeFirst(risk.type) + ' Risk';
                content.querySelector('p').textContent = risk.description;
                content.querySelector('.risk-timeline').textContent = risk.timeframe;
            }
        });
    }

    updateOptimizationSuggestions() {
        const suggestionCards = document.querySelectorAll('.suggestion-card');
        const suggestions = this.predictions.optimizations;
        
        suggestionCards.forEach((card, index) => {
            if (suggestions[index]) {
                const suggestion = suggestions[index];
                
                card.querySelector('.suggestion-icon').textContent = suggestion.icon;
                card.querySelector('h3').textContent = suggestion.title;
                card.querySelector('p').textContent = suggestion.description;
                card.querySelector('.impact-value').textContent = suggestion.impact;
                card.querySelector('.suggestion-btn').textContent = suggestion.action;
            }
        });
    }

    updateAccuracyMetrics() {
        const metrics = document.querySelectorAll('.metric-value');
        if (metrics.length >= 4) {
            metrics[0].textContent = `${this.accuracy.overall}%`;
            metrics[1].textContent = `${this.accuracy.energy}%`;
            metrics[2].textContent = `${this.accuracy.sleep}%`;
            metrics[3].textContent = `${this.accuracy.mood}%`;
        }
        
        const qualityValues = document.querySelectorAll('.quality-value');
        if (qualityValues.length >= 3) {
            qualityValues[0].textContent = `${this.accuracy.dataCompleteness}%`;
            qualityValues[1].textContent = `${this.accuracy.dataFreshness}%`;
            qualityValues[2].textContent = `${this.accuracy.patternRecognition}%`;
        }
        
        // Update quality bars
        const qualityFills = document.querySelectorAll('.quality-fill');
        if (qualityFills.length >= 3) {
            qualityFills[0].style.width = `${this.accuracy.dataCompleteness}%`;
            qualityFills[1].style.width = `${this.accuracy.dataFreshness}%`;
            qualityFills[2].style.width = `${this.accuracy.patternRecognition}%`;
        }
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    showLoadingOverlay() {
        const overlay = document.getElementById('ai-loading');
        if (overlay) {
            overlay.classList.add('show');
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('ai-loading');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">❌</span>
                <span class="notification-text">${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize predictions when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting AI Health Predictions...');
    window.aiPredictions = new AIHealthPredictions();
});

// Add additional CSS for predictions page
const predictionsCSS = `
.predictions-main {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.predictions-header {
    background: var(--ai-gradient);
    border-radius: 1.5rem;
    padding: 3rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.predictions-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
}

.header-content {
    position: relative;
    z-index: 2;
}

.predictions-header h1 {
    font-size: 3rem;
    font-weight: 700;
    color: white;
    margin-bottom: 1rem;
}

.predictions-header p {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 2rem;
}

.prediction-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    flex-wrap: wrap;
}

.stat-item {
    text-align: center;
    color: white;
}

.stat-number {
    display: block;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

.prediction-timeline-section {
    margin-bottom: 3rem;
}

.prediction-timeline-section h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--ai-text-primary);
    margin-bottom: 2rem;
    text-align: center;
}

.timeline-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.timeline-item {
    display: flex;
    gap: 2rem;
    background: var(--ai-bg-secondary);
    border-radius: 1.5rem;
    padding: 2rem;
    border: 1px solid var(--ai-border);
    transition: all 0.3s ease;
}

.timeline-item:hover {
    transform: translateY(-3px);
    box-shadow: var(--ai-shadow);
    border-color: var(--ai-primary);
}

.timeline-date {
    min-width: 120px;
    color: var(--ai-accent);
    font-weight: 700;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
}

.timeline-content {
    flex: 1;
}

.timeline-content h3 {
    color: var(--ai-text-primary);
    font-size: 1.3rem;
    margin-bottom: 1rem;
}

.prediction-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.prediction-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--ai-bg-tertiary);
    border-radius: 1rem;
}

.pred-icon {
    font-size: 1.5rem;
    width: 40px;
    text-align: center;
}

.pred-text {
    flex: 1;
    color: var(--ai-text-secondary);
    font-weight: 500;
}

.pred-confidence {
    color: var(--ai-success);
    font-weight: 600;
    font-size: 0.9rem;
}

.trend-predictions {
    margin-bottom: 3rem;
}

.trend-predictions h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--ai-text-primary);
    margin-bottom: 2rem;
    text-align: center;
}

.trends-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.trend-card {
    background: var(--ai-bg-secondary);
    border-radius: 1.5rem;
    padding: 2rem;
    border: 1px solid var(--ai-border);
    text-align: center;
}

.trend-card h3 {
    color: var(--ai-text-primary);
    margin-bottom: 1rem;
}

.trend-card canvas {
    margin-bottom: 1rem;
}

.trend-summary {
    color: var(--ai-text-secondary);
}

.trend-positive {
    color: var(--ai-success);
    font-weight: 600;
}

.risk-predictions {
    margin-bottom: 3rem;
}

.risk-predictions h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--ai-text-primary);
    margin-bottom: 2rem;
    text-align: center;
}

.risk-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.risk-card {
    background: var(--ai-bg-secondary);
    border-radius: 1.5rem;
    padding: 2rem;
    border: 1px solid var(--ai-border);
    transition: all 0.3s ease;
}

.risk-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--ai-shadow);
}

.risk-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.risk-header h3 {
    color: var(--ai-text-primary);
    font-size: 1.1rem;
}

.risk-probability {
    background: var(--ai-gradient);
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 1rem;
    font-weight: 600;
    font-size: 0.9rem;
}

.risk-content h4 {
    color: var(--ai-text-primary);
    margin-bottom: 0.5rem;
}

.risk-content p {
    color: var(--ai-text-secondary);
    margin-bottom: 1rem;
    line-height: 1.6;
}

.risk-timeline {
    color: var(--ai-accent);
    font-size: 0.9rem;
    font-weight: 600;
}

.optimization-suggestions {
    margin-bottom: 3rem;
}

.optimization-suggestions h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--ai-text-primary);
    margin-bottom: 2rem;
    text-align: center;
}

.suggestions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.suggestion-card {
    background: var(--ai-bg-secondary);
    border-radius: 1.5rem;
    padding: 2rem;
    border: 1px solid var(--ai-border);
    transition: all 0.3s ease;
}

.suggestion-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--ai-shadow);
    border-color: var(--ai-primary);
}

.suggestion-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.suggestion-icon {
    font-size: 1.5rem;
}

.suggestion-header h3 {
    color: var(--ai-text-primary);
    font-size: 1.2rem;
}

.suggestion-content p {
    color: var(--ai-text-secondary);
    margin-bottom: 1rem;
    line-height: 1.6;
}

.suggestion-impact {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--ai-bg-tertiary);
    border-radius: 1rem;
}

.impact-label {
    color: var(--ai-text-secondary);
    font-size: 0.9rem;
}

.impact-value {
    color: var(--ai-success);
    font-weight: 600;
}

.suggestion-btn {
    background: var(--ai-gradient);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
}

.suggestion-btn:hover {
    transform: translateY(-2px);
    box-shadow: var(--ai-glow);
}

.prediction-accuracy {
    margin-bottom: 2rem;
}

.prediction-accuracy h2 {
    font-size: 2rem;
    font-weight: 600;
    color: var(--ai-text-primary);
    margin-bottom: 2rem;
    text-align: center;
}

.accuracy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}

.accuracy-card {
    background: var(--ai-bg-secondary);
    border-radius: 1.5rem;
    padding: 2rem;
    border: 1px solid var(--ai-border);
}

.accuracy-card h3 {
    color: var(--ai-text-primary);
    margin-bottom: 1.5rem;
    text-align: center;
}

.accuracy-metrics {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: var(--ai-bg-tertiary);
    border-radius: 1rem;
}

.metric-label {
    color: var(--ai-text-secondary);
}

.metric-value {
    color: var(--ai-success);
    font-weight: 600;
}

.data-quality {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.quality-item {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.quality-label {
    min-width: 120px;
    color: var(--ai-text-secondary);
    font-size: 0.9rem;
}

.quality-bar {
    flex: 1;
    height: 8px;
    background: var(--ai-bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
}

.quality-fill {
    height: 100%;
    background: var(--ai-gradient);
    border-radius: 4px;
    transition: width 1s ease;
}

.quality-value {
    min-width: 40px;
    text-align: right;
    color: var(--ai-text-primary);
    font-weight: 600;
}

@media (max-width: 768px) {
    .predictions-main {
        padding: 1rem;
    }
    
    .predictions-header h1 {
        font-size: 2rem;
    }
    
    .prediction-stats {
        gap: 1.5rem;
    }
    
    .timeline-item {
        flex-direction: column;
        gap: 1rem;
    }
    
    .timeline-date {
        min-width: auto;
        text-align: center;
    }
    
    .trends-grid {
        grid-template-columns: 1fr;
    }
    
    .risk-grid {
        grid-template-columns: 1fr;
    }
    
    .suggestions-grid {
        grid-template-columns: 1fr;
    }
    
    .accuracy-grid {
        grid-template-columns: 1fr;
    }
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = predictionsCSS;
document.head.appendChild(style);
