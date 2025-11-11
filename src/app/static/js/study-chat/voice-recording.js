/**
 * VoiceRecording - Manages voice recording, transcription, and recording UI
 */
class VoiceRecording {
    constructor(sessionId, sessionStatus) {
        this.sessionId = sessionId;
        this.sessionStatus = sessionStatus;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingStartTime = null;
        this.recordingTimer = null;
        this.maxRecordingDuration = 120; // 2 minutes in seconds
    }

    /**
     * Update session status (called from main class)
     * @param {string} status - New session status
     */
    updateSessionStatus(status) {
        this.sessionStatus = status;
    }

    /**
     * Toggle voice recording on/off
     */
    async toggleVoiceRecording() {
        if (this.isRecording) {
            await this.stopVoiceRecording();
        } else {
            await this.startVoiceRecording();
        }
    }

    /**
     * Start voice recording
     */
    async startVoiceRecording() {
        if (this.sessionStatus !== 'active') {
            showMessage('Cannot record while session is not active', 'warning');
            return;
        }

        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create MediaRecorder
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            // Handle data available event
            this.mediaRecorder.addEventListener('dataavailable', (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            });
            
            // Handle stop event
            this.mediaRecorder.addEventListener('stop', () => {
                // Stop all audio tracks
                stream.getTracks().forEach(track => track.stop());
            });
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordingStartTime = Date.now();
            
            // Show recording modal
            this.showRecordingModal();
            
            // Start timer update
            this.updateRecordingTimer();
            this.recordingTimer = setInterval(() => {
                this.updateRecordingTimer();
                
                // Auto-stop at max duration
                const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
                if (elapsed >= this.maxRecordingDuration) {
                    this.stopVoiceRecording();
                }
            }, 1000);
            
            // Update voice button appearance
            const voiceButton = document.getElementById('voiceButton');
            if (voiceButton) {
                voiceButton.classList.add('recording');
            }
            
        } catch (error) {
            console.error('Error starting voice recording:', error);
            if (error.name === 'NotAllowedError') {
                showMessage('Microphone access denied. Please allow microphone access to use voice mode.', 'error');
            } else {
                showMessage('Failed to start recording. Please check your microphone.', 'error');
            }
        }
    }

    /**
     * Stop voice recording and transcribe
     */
    async stopVoiceRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }

        // Stop recording
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Clear timer
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        // Hide recording modal
        this.hideRecordingModal();
        
        // Update voice button appearance
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.classList.remove('recording');
        }
        
        // Wait for all chunks to be collected
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Create audio blob
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        // Send to transcription endpoint
        await this.transcribeAudio(audioBlob);
    }

    /**
     * Cancel voice recording
     */
    cancelVoiceRecording() {
        if (!this.isRecording || !this.mediaRecorder) {
            return;
        }

        // Stop recording
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Clear timer
        if (this.recordingTimer) {
            clearInterval(this.recordingTimer);
            this.recordingTimer = null;
        }
        
        // Clear audio chunks
        this.audioChunks = [];
        
        // Hide recording modal
        this.hideRecordingModal();
        
        // Update voice button appearance
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.classList.remove('recording');
        }
        
        showMessage('Recording cancelled', 'info');
    }

    /**
     * Transcribe audio blob
     * @param {Blob} audioBlob - Audio blob to transcribe
     */
    async transcribeAudio(audioBlob) {
        // Show loading message
        const statusMsg = showMessage('Transcribing audio...', 'info');
        
        try {
            // Create FormData with audio file
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            
            // Send to transcription endpoint
            const response = await fetch(`/study/chat/${this.sessionId}/transcribe`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Populate message input with transcribed text
                const input = document.getElementById('messageInput');
                input.value = data.text;
                input.focus();
                
                // Store that this message originated from voice
                input.dataset.modality = 'speech_to_text';
                
                showMessage('Audio transcribed successfully', 'success');
            } else {
                showMessage(data.error || 'Failed to transcribe audio', 'error');
            }
        } catch (error) {
            console.error('Error transcribing audio:', error);
            showMessage('An error occurred during transcription', 'error');
        }
    }

    /**
     * Show recording modal
     */
    showRecordingModal() {
        const modal = document.getElementById('voiceRecordingModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    /**
     * Hide recording modal
     */
    hideRecordingModal() {
        const modal = document.getElementById('voiceRecordingModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    /**
     * Update recording timer display
     */
    updateRecordingTimer() {
        if (!this.recordingStartTime) return;
        
        const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        const timerDisplay = document.getElementById('recordingTimer');
        if (timerDisplay) {
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
}
