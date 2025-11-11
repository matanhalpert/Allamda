/**
 * AudioPlayback - Manages TTS audio playback controls for teacher messages
 */
class AudioPlayback {
    constructor() {
        this.currentAudio = null;
        this.currentMessageId = null;
        this.audioCache = new Map(); // Cache Audio elements
        this.progressUpdateInterval = null;
    }

    /**
     * Initialize audio controls for all existing teacher messages
     */
    initAudioControls() {
        document.querySelectorAll('.message-audio-controls').forEach(controls => {
            this.attachAudioControlListeners(controls);
        });
    }

    /**
     * Attach event listeners to audio control buttons
     * @param {HTMLElement} controlsElement - The audio controls container
     */
    attachAudioControlListeners(controlsElement) {
        const messageId = parseInt(controlsElement.dataset.messageId);
        
        const playBtn = controlsElement.querySelector('.play-btn');
        const pauseBtn = controlsElement.querySelector('.pause-btn');
        const stopBtn = controlsElement.querySelector('.stop-btn');
        const progressBar = controlsElement.querySelector('.audio-progress-bar');
        
        if (playBtn) {
            playBtn.addEventListener('click', () => this.playMessageAudio(messageId, controlsElement));
        }
        
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.pauseAudio());
        }
        
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopAudio());
        }
        
        if (progressBar) {
            progressBar.addEventListener('click', (e) => this.seekAudio(e, progressBar));
        }
    }

    /**
     * Play audio for a teacher message
     * @param {number} messageId - Message ID
     * @param {HTMLElement} controlsElement - Audio controls container
     */
    async playMessageAudio(messageId, controlsElement) {
        // If already playing this message, just resume
        if (this.currentMessageId === messageId && this.currentAudio && this.currentAudio.paused) {
            this.resumeAudio();
            return;
        }
        
        // Stop any currently playing audio
        if (this.currentAudio) {
            this.stopAudio();
        }
        
        try {
            // Show loading indicator
            this.togglePlayPauseButtons(controlsElement, 'loading');
            
            // Check cache first
            let audio = this.audioCache.get(messageId);
            
            if (!audio) {
                // Fetch audio from server
                const audioUrl = `/study/chat/message/${messageId}/audio`;
                audio = new Audio(audioUrl);
                this.audioCache.set(messageId, audio);
                
                // Set up audio event listeners
                audio.addEventListener('timeupdate', () => this.updateProgress(controlsElement));
                audio.addEventListener('ended', () => this.handleAudioEnded(controlsElement));
                audio.addEventListener('error', (e) => this.handleAudioError(e, messageId));
                
                // When audio can start playing, switch to pause button
                audio.addEventListener('playing', () => {
                    this.togglePlayPauseButtons(controlsElement, 'playing');
                }, { once: true });
            }
            
            this.currentAudio = audio;
            this.currentMessageId = messageId;
            
            // Update UI
            controlsElement.classList.add('playing');
            
            // Play audio
            await audio.play();
            
            // If cached, switch to pause immediately (no loading needed)
            if (audio.readyState >= 3) {
                this.togglePlayPauseButtons(controlsElement, 'playing');
            }
            
            // Start progress updates
            this.startProgressUpdates(controlsElement);
            
        } catch (error) {
            console.error('Error playing audio:', error);
            showMessage('Failed to play audio', 'error');
            controlsElement.classList.remove('playing');
            this.togglePlayPauseButtons(controlsElement, 'stopped');
        }
    }

    /**
     * Pause currently playing audio
     */
    pauseAudio() {
        if (this.currentAudio && !this.currentAudio.paused) {
            this.currentAudio.pause();
            
            const controlsElement = this.getCurrentControlsElement();
            if (controlsElement) {
                this.togglePlayPauseButtons(controlsElement, 'paused');
            }
            
            this.stopProgressUpdates();
        }
    }

    /**
     * Resume paused audio
     */
    resumeAudio() {
        if (this.currentAudio && this.currentAudio.paused) {
            this.currentAudio.play();
            
            const controlsElement = this.getCurrentControlsElement();
            if (controlsElement) {
                this.togglePlayPauseButtons(controlsElement, 'playing');
                this.startProgressUpdates(controlsElement);
            }
        }
    }

    /**
     * Stop currently playing audio
     */
    stopAudio() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
            
            const controlsElement = this.getCurrentControlsElement();
            if (controlsElement) {
                controlsElement.classList.remove('playing');
                this.togglePlayPauseButtons(controlsElement, 'stopped');
                this.updateProgress(controlsElement);
            }
            
            this.stopProgressUpdates();
            this.currentMessageId = null;
        }
    }

    /**
     * Seek to a position in the audio
     * @param {MouseEvent} event - Click event on progress bar
     * @param {HTMLElement} progressBar - Progress bar element
     */
    seekAudio(event, progressBar) {
        if (!this.currentAudio) return;
        
        const rect = progressBar.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const percentage = clickX / rect.width;
        
        this.currentAudio.currentTime = percentage * this.currentAudio.duration;
    }

    /**
     * Update progress bar display
     * @param {HTMLElement} controlsElement - Audio controls container
     */
    updateProgress(controlsElement) {
        if (!this.currentAudio || !controlsElement) return;
        
        const progressFill = controlsElement.querySelector('.audio-progress-fill');
        if (progressFill && this.currentAudio.duration) {
            const percentage = (this.currentAudio.currentTime / this.currentAudio.duration) * 100;
            progressFill.style.width = `${percentage}%`;
        }
    }

    /**
     * Start periodic progress updates
     * @param {HTMLElement} controlsElement - Audio controls container
     */
    startProgressUpdates(controlsElement) {
        this.stopProgressUpdates();
        this.progressUpdateInterval = setInterval(() => {
            this.updateProgress(controlsElement);
        }, 100);
    }

    /**
     * Stop periodic progress updates
     */
    stopProgressUpdates() {
        if (this.progressUpdateInterval) {
            clearInterval(this.progressUpdateInterval);
            this.progressUpdateInterval = null;
        }
    }

    /**
     * Handle audio playback ended
     * @param {HTMLElement} controlsElement - Audio controls container
     */
    handleAudioEnded(controlsElement) {
        controlsElement.classList.remove('playing');
        this.togglePlayPauseButtons(controlsElement, 'stopped');
        this.stopProgressUpdates();
        
        // Reset progress
        const progressFill = controlsElement.querySelector('.audio-progress-fill');
        if (progressFill) {
            progressFill.style.width = '0%';
        }
        
        this.currentMessageId = null;
    }

    /**
     * Handle audio playback error
     * @param {Event} error - Error event
     * @param {number} messageId - Message ID
     */
    handleAudioError(error, messageId) {
        console.error('Audio playback error:', error);
        showMessage('Failed to load audio. Please try again.', 'error');
        
        // Clean up
        const controlsElement = this.getCurrentControlsElement();
        if (controlsElement) {
            controlsElement.classList.remove('playing');
            this.togglePlayPauseButtons(controlsElement, 'stopped');
        }
        
        this.stopProgressUpdates();
        this.currentMessageId = null;
        
        // Remove from cache so it can be retried
        this.audioCache.delete(messageId);
    }

    /**
     * Toggle play/pause/loading buttons
     * @param {HTMLElement} controlsElement - Audio controls container
     * @param {string} state - Button state: 'loading', 'playing', 'paused', or 'stopped'
     */
    togglePlayPauseButtons(controlsElement, state) {
        const playBtn = controlsElement.querySelector('.play-btn');
        const loadingBtn = controlsElement.querySelector('.loading-btn');
        const pauseBtn = controlsElement.querySelector('.pause-btn');
        
        // Hide all buttons first
        playBtn.style.display = 'none';
        loadingBtn.style.display = 'none';
        pauseBtn.style.display = 'none';
        
        // Show appropriate button based on state
        if (state === 'loading') {
            loadingBtn.style.display = 'inline-flex';
        } else if (state === 'playing') {
            pauseBtn.style.display = 'inline-flex';
        } else {
            playBtn.style.display = 'inline-flex';
        }
    }

    /**
     * Get the controls element for the currently playing message
     * @returns {HTMLElement|null} Controls element or null
     */
    getCurrentControlsElement() {
        if (!this.currentMessageId) return null;
        return document.querySelector(`.message-audio-controls[data-message-id="${this.currentMessageId}"]`);
    }
}
