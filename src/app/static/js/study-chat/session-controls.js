/**
 * SessionControls - Manages session pause/resume/end and duration/countdown timers
 */
class SessionControls {
    constructor(sessionId, initialStatus) {
        this.sessionId = sessionId;
        this.sessionStatus = initialStatus;
        this.durationTimer = null;
        
        // Start duration timer
        this.startDurationTimer();
    }

    /**
     * Get current session status
     * @returns {string} Current session status
     */
    getSessionStatus() {
        return this.sessionStatus;
    }

    /**
     * Pause the session
     */
    async pauseSession() {
        const button = document.getElementById('pauseResumeButton');
        button.disabled = true;
        
        try {
            const response = await fetch(`/study/pause/${this.sessionId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.updateUIToPaused();
                showMessage('Session paused', 'info');
            } else {
                showMessage(data.error || 'Failed to pause session', 'error');
            }
        } catch (error) {
            showMessage('An error occurred', 'error');
            console.error('Error:', error);
        } finally {
            button.disabled = false;
        }
    }

    /**
     * Resume the session
     */
    async resumeSession() {
        const button = document.getElementById('pauseResumeButton');
        button.disabled = true;
        
        try {
            const response = await fetch(`/study/resume/${this.sessionId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.updateUIToResumed();
                showMessage('Session resumed', 'success');
            } else {
                showMessage(data.error || 'Failed to resume session', 'error');
            }
        } catch (error) {
            showMessage('An error occurred', 'error');
            console.error('Error:', error);
        } finally {
            button.disabled = false;
        }
    }
    
    /**
     * Update UI to paused state
     */
    updateUIToPaused() {
        // Update internal state
        this.sessionStatus = 'paused';
        this.updateSessionStatus('paused');
        
        // Update button to resume
        const button = document.getElementById('pauseResumeButton');
        if (button) {
            button.innerHTML = '<i class="fas fa-play me-1"></i>Resume';
            button.className = 'btn btn-success btn-sm';
            // Use global function to ensure main chat object is updated
            button.onclick = () => window.resumeSession();
            button.disabled = false;
        }
        
        // Disable message input
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const attachButton = document.getElementById('attachButton');
        const cameraButton = document.getElementById('cameraButton');
        const voiceButton = document.getElementById('voiceButton');
        
        if (messageInput) messageInput.disabled = true;
        if (sendButton) sendButton.disabled = true;
        if (attachButton) attachButton.disabled = true;
        if (cameraButton) cameraButton.disabled = true;
        if (voiceButton) voiceButton.disabled = true;
    }
    
    /**
     * Update UI to resumed/active state
     */
    updateUIToResumed() {
        // Update internal state
        this.sessionStatus = 'active';
        this.updateSessionStatus('active');
        
        // Update button to pause
        const button = document.getElementById('pauseResumeButton');
        if (button) {
            button.innerHTML = '<i class="fas fa-pause me-1"></i>Pause';
            button.className = 'btn btn-warning btn-sm';
            // Use global function to ensure main chat object is updated
            button.onclick = () => window.pauseSession();
            button.disabled = false;
        }
        
        // Enable message input
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const attachButton = document.getElementById('attachButton');
        const cameraButton = document.getElementById('cameraButton');
        const voiceButton = document.getElementById('voiceButton');
        
        if (messageInput) messageInput.disabled = false;
        if (sendButton) sendButton.disabled = false;
        if (attachButton) attachButton.disabled = false;
        if (cameraButton) cameraButton.disabled = false;
        if (voiceButton) voiceButton.disabled = false;
    }

    /**
     * Update session status badge
     * @param {string} status - Session status
     */
    updateSessionStatus(status) {
        const statusText = document.getElementById('statusText');
        const statusBadge = statusText.parentElement;
        
        statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        // Update badge color
        statusBadge.classList.remove('bg-success', 'bg-warning', 'bg-secondary');
        if (status === 'active') {
            statusBadge.classList.add('bg-success');
        } else if (status === 'paused') {
            statusBadge.classList.add('bg-warning', 'text-dark');
        } else {
            statusBadge.classList.add('bg-secondary');
        }
    }

    /**
     * End the session
     */
    endSession() {
        if (confirm('Are you sure you want to end this study session? You will be asked to provide feedback.')) {
            window.location.href = `/study/end/${this.sessionId}`;
        }
    }

    /**
     * Start duration timer (updates every minute)
     */
    startDurationTimer() {
        // Update duration every minute
        this.durationTimer = setInterval(() => {
            const durationEl = document.getElementById('duration');
            const currentMinutes = parseInt(durationEl.textContent);
            durationEl.textContent = `${currentMinutes + 1} min`;
        }, 60000);
    }
}

/**
 * SchoolSessionTimer - Countdown timer for school sessions with time limits
 */
class SchoolSessionTimer {
    constructor(sessionId, remainingSeconds) {
        this.sessionId = sessionId;
        this.remainingSeconds = remainingSeconds;
        this.timerInterval = null;
        this.displayElement = document.getElementById('countdown-display');
        
        if (!this.displayElement) {
            console.error('Countdown display element not found');
            return;
        }
        
        this.start();
    }
    
    /**
     * Update timer display
     */
    updateDisplay() {
        const minutes = Math.floor(this.remainingSeconds / 60);
        const seconds = this.remainingSeconds % 60;
        this.displayElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Change color when time is running out
        if (this.remainingSeconds <= 300) { // 5 minutes
            this.displayElement.classList.remove('text-warning');
            this.displayElement.classList.add('text-danger');
        } else if (this.remainingSeconds <= 600) { // 10 minutes
            this.displayElement.classList.add('text-warning');
        }
        
        // Auto-end session when timer reaches zero
        if (this.remainingSeconds <= 0) {
            this.stop();
            this.displayElement.textContent = '0:00';
            alert('Time is up! The session will now end.');
            // Redirect to end session page
            window.location.href = `/study/end/${this.sessionId}`;
        }
    }
    
    /**
     * Start the countdown timer
     */
    start() {
        // Initial display
        this.updateDisplay();
        
        // Update every second
        this.timerInterval = setInterval(() => {
            this.remainingSeconds--;
            this.updateDisplay();
        }, 1000);
    }
    
    /**
     * Stop the countdown timer
     */
    stop() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
}

/**
 * Initialize countdown timer if data is available
 */
function initializeSchoolSessionTimer() {
    const timerElement = document.getElementById('countdown-timer');
    if (timerElement && timerElement.dataset.remaining) {
        const sessionId = timerElement.dataset.sessionId;
        const remainingSeconds = parseInt(timerElement.dataset.remaining);
        window.schoolTimer = new SchoolSessionTimer(sessionId, remainingSeconds);
    }
}

