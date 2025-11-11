/**
 * Messaging - Handles sending and receiving messages, displaying them in the UI
 */
class Messaging {
    constructor(sessionId, uiHelpers, audioPlayback) {
        this.sessionId = sessionId;
        this.uiHelpers = uiHelpers;
        this.audioPlayback = audioPlayback;
    }

    /**
     * Send a message to the server
     * @param {string} message - Message text
     * @param {Array} files - Array of File objects
     * @param {string} modality - Optional modality (e.g., 'speech_to_text')
     * @returns {Promise} Promise that resolves when message is sent
     */
    async sendMessage(message, files, modality = null) {
        // Create FormData for file upload
        const formData = new FormData();
        formData.append('message', message);
        
        // Add modality if provided
        if (modality) {
            formData.append('modality', modality);
        }
        
        // Add files
        files.forEach(file => {
            formData.append('attachments', file);
        });
        
        // Show student message immediately (optimistically without attachments)
        this.addMessageToChat(message || '[Sending file...]', true, null, []);
        
        // Show typing indicator
        document.getElementById('typingIndicator').style.display = 'block';
        this.uiHelpers.scrollToBottom();
        
        try {
            const response = await fetch(`/study/chat/${this.sessionId}/message`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            document.getElementById('typingIndicator').style.display = 'none';
            
            if (response.ok) {
                // Update the last student message with attachments if present
                if (data.student_message && data.student_message.attachments && data.student_message.attachments.length > 0) {
                    // Remove the temporary student message
                    const container = document.getElementById('chat-container');
                    const messages = container.querySelectorAll('.message.student');
                    const lastStudentMessage = messages[messages.length - 1];
                    if (lastStudentMessage) {
                        lastStudentMessage.remove();
                    }
                    
                    // Re-add with attachments
                    this.addMessageToChat(message || '[File attachment]', true, null, data.student_message.attachments);
                }
                
                // Add teacher response to chat
                this.addMessageToChat(data.content, false, data.timestamp, [], data.id);
                
                return { success: true };
            } else {
                showMessage(data.error || 'Failed to send message', 'error');
                return { success: false, error: data.error };
            }
        } catch (error) {
            document.getElementById('typingIndicator').style.display = 'none';
            showMessage('An error occurred. Please try again.', 'error');
            console.error('Error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Fetch welcome message from server
     */
    async fetchWelcomeMessage() {
        // Show typing indicator
        document.getElementById('typingIndicator').style.display = 'block';
        this.uiHelpers.scrollToBottom();
        
        try {
            const response = await fetch(`/study/chat/${this.sessionId}/welcome`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            document.getElementById('typingIndicator').style.display = 'none';
            
            if (response.ok) {
                // Add welcome message to chat
                this.addMessageToChat(data.content, false, data.timestamp, [], data.id);
            } else {
                console.error('Failed to fetch welcome message:', data.error);
                // Continue without welcome message - student can start conversation
            }
        } catch (error) {
            document.getElementById('typingIndicator').style.display = 'none';
            console.error('Error fetching welcome message:', error);
            // Continue without welcome message
        }
    }

    /**
     * Add a message to the chat UI
     * @param {string} content - Message content
     * @param {boolean} isStudent - Whether message is from student
     * @param {string} timestamp - Message timestamp
     * @param {Array} attachments - Array of attachment objects
     * @param {number} messageId - Message ID (for teacher messages with audio)
     */
    addMessageToChat(content, isStudent, timestamp = null, attachments = [], messageId = null) {
        const container = document.getElementById('chat-container');
        
        // Remove "no messages" placeholder if exists
        const placeholder = document.getElementById('noMessagesPlaceholder');
        if (placeholder) placeholder.remove();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isStudent ? 'student' : 'teacher'}`;
        
        const timeStr = timestamp || new Date().toLocaleString();
        
        // Process content based on sender
        let messageContent;
        if (isStudent) {
            // Escape HTML for student messages
            messageContent = this.uiHelpers.escapeHtml(content);
        } else {
            // Render markdown for teacher messages
            messageContent = this.uiHelpers.renderMarkdown(content);
        }
        
        // Build attachment HTML if present
        let attachmentHtml = '';
        if (isStudent && attachments && attachments.length > 0) {
            attachmentHtml = '<div class="message-attachments mt-2">';
            attachments.forEach(att => {
                if (att.file_type === 'image') {
                    attachmentHtml += `
                        <div class="attachment-image">
                            <a href="${att.url}" target="_blank">
                                <img src="${att.url}" alt="Attached image" />
                            </a>
                        </div>
                    `;
                } else {
                    const filename = att.url.split('/').pop().split('_').slice(1).join('_');
                    attachmentHtml += `
                        <a href="${att.url}" target="_blank" class="attachment-file">
                            <i class="fas fa-paperclip me-1"></i>${filename}
                        </a>
                    `;
                }
            });
            attachmentHtml += '</div>';
        }
        
        // Build footer HTML (timestamp + audio controls for teacher messages)
        let footerHtml = '';
        if (isStudent) {
            footerHtml = `<div class="message-time">${timeStr}</div>`;
        } else if (messageId) {
            footerHtml = `
                <div class="message-footer">
                    <div class="message-time">
                        ${timeStr}
                    </div>
                    <div class="message-audio-controls" data-message-id="${messageId}">
                        <button class="audio-control-btn play-btn" title="Play audio">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="audio-control-btn loading-btn" style="display: none;" title="Loading...">
                            <i class="fas fa-spinner fa-spin"></i>
                        </button>
                        <button class="audio-control-btn pause-btn" style="display: none;" title="Pause audio">
                            <i class="fas fa-pause"></i>
                        </button>
                        <button class="audio-control-btn stop-btn" title="Stop audio">
                            <i class="fas fa-stop"></i>
                        </button>
                        <div class="audio-progress-bar">
                            <div class="audio-progress-fill"></div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div>
                <div class="message-label">
                    ${isStudent ? '<i class="fas fa-user me-1"></i>You' : '<i class="fas fa-chalkboard-teacher me-1"></i>Teacher'}
                </div>
                <div class="message-bubble ${isStudent ? '' : 'markdown-content'}">
                    ${messageContent}
                    ${attachmentHtml}
                </div>
                ${footerHtml}
            </div>
        `;
        
        // Insert before typing indicator
        const typingIndicator = document.getElementById('typingIndicator');
        container.insertBefore(messageDiv, typingIndicator);
        
        // Attach audio control listeners for teacher messages
        if (!isStudent && messageId) {
            const controlsElement = messageDiv.querySelector('.message-audio-controls');
            if (controlsElement) {
                this.audioPlayback.attachAudioControlListeners(controlsElement);
            }
        }
        
        this.uiHelpers.scrollToBottom();
    }
}
