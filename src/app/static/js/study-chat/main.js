/**
 * StudySessionChat - Main orchestrator that composes all chat module functionality
 * Manages the interactive chat interface for study sessions
 */
class StudySessionChat {
    constructor(sessionId, initialStatus) {
        this.sessionId = sessionId;
        this.sessionStatus = initialStatus;
        
        // Initialize sub-modules
        this.uiHelpers = new UIHelpers();
        this.audioPlayback = new AudioPlayback();
        this.fileAttachments = new FileAttachments();
        this.messaging = new Messaging(sessionId, this.uiHelpers, this.audioPlayback);
        this.sessionControls = new SessionControls(sessionId, initialStatus);
        this.voiceRecording = new VoiceRecording(sessionId, initialStatus);
        this.websocket = new ChatWebSocket(sessionId, this.sessionControls);
        
        this.init();
    }

    /**
     * Initialize the chat interface
     */
    init() {
        // Render all existing teacher messages with markdown
        this.uiHelpers.initExistingMessages();
        
        this.uiHelpers.scrollToBottom();
        
        // Initialize audio controls for existing teacher messages
        this.audioPlayback.initAudioControls();
        
        // Check if we need to fetch welcome message
        const container = document.getElementById('chat-container');
        const hasMessages = container.querySelector('.message:not(#typingIndicator .message)');
        
        if (!hasMessages && this.sessionStatus === 'active') {
            // Hide the placeholder immediately since we'll show the typing indicator
            const placeholder = document.getElementById('noMessagesPlaceholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }
            // Fetch welcome message asynchronously
            this.messaging.fetchWelcomeMessage();
        }
        
        // Enable Enter to send
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    /**
     * Handle file selection
     * @param {Event} event - File input change event
     */
    handleFileSelect(event) {
        this.fileAttachments.handleFileSelect(event);
    }

    /**
     * Send a message
     * @param {string} modality - Optional modality parameter
     */
    async sendMessage(modality = null) {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        // Allow sending if either message text exists OR files are attached
        if ((!message && this.fileAttachments.getFiles().length === 0) || this.sessionStatus !== 'active') return;
        
        // Check if message originated from voice (stored in dataset)
        if (!modality && input.dataset.modality) {
            modality = input.dataset.modality;
            delete input.dataset.modality; // Clear after use
        }
        
        // Disable inputs
        input.disabled = true;
        document.getElementById('sendButton').disabled = true;
        document.getElementById('attachButton').disabled = true;
        document.getElementById('cameraButton').disabled = true;
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) voiceButton.disabled = true;
        
        // Get files from file attachments module
        const files = this.fileAttachments.getFiles();
        
        // Clear message input and file attachments
        input.value = '';
        this.fileAttachments.clearFiles();
        
        // Send message via messaging module
        const result = await this.messaging.sendMessage(message, files, modality);
        
        // Re-enable inputs
        if (this.sessionStatus === 'active') {
            input.disabled = false;
            document.getElementById('sendButton').disabled = false;
            document.getElementById('attachButton').disabled = false;
            document.getElementById('cameraButton').disabled = false;
            const voiceButton = document.getElementById('voiceButton');
            if (voiceButton) voiceButton.disabled = false;
            input.focus();
        }
    }

    /**
     * Toggle voice recording
     */
    async toggleVoiceRecording() {
        await this.voiceRecording.toggleVoiceRecording();
    }

    /**
     * Stop voice recording
     */
    async stopVoiceRecording() {
        await this.voiceRecording.stopVoiceRecording();
    }

    /**
     * Cancel voice recording
     */
    cancelVoiceRecording() {
        this.voiceRecording.cancelVoiceRecording();
    }

    /**
     * Pause session
     */
    async pauseSession() {
        await this.sessionControls.pauseSession();
        this.sessionStatus = this.sessionControls.getSessionStatus();
        this.voiceRecording.updateSessionStatus(this.sessionStatus);
    }

    /**
     * Resume session
     */
    async resumeSession() {
        await this.sessionControls.resumeSession();
        this.sessionStatus = this.sessionControls.getSessionStatus();
        this.voiceRecording.updateSessionStatus(this.sessionStatus);
    }

    /**
     * End session
     */
    endSession() {
        this.sessionControls.endSession();
    }

    /**
     * Update UI to paused (called by WebSocket)
     */
    updateUIToPaused() {
        this.sessionControls.updateUIToPaused();
        this.sessionStatus = this.sessionControls.getSessionStatus();
        this.voiceRecording.updateSessionStatus(this.sessionStatus);
    }

    /**
     * Update UI to resumed (called by WebSocket)
     */
    updateUIToResumed() {
        this.sessionControls.updateUIToResumed();
        this.sessionStatus = this.sessionControls.getSessionStatus();
        this.voiceRecording.updateSessionStatus(this.sessionStatus);
    }
}

/**
 * Global function for file input onchange handler
 * @param {Event} event - File input change event
 */
function handleFileSelect(event) {
    if (window.chat) {
        window.chat.handleFileSelect(event);
    }
}

