/**
 * ChatWebSocket - Manages WebSocket connection for real-time session updates
 */
class ChatWebSocket {
    constructor(sessionId, sessionControls) {
        this.sessionId = sessionId;
        this.sessionControls = sessionControls;
        this.socket = null;
        
        this.init();
    }

    /**
     * Initialize WebSocket connection
     */
    init() {
        // Connect to SocketIO server
        this.socket = io();
        
        // Get student ID from the page data
        const userElement = document.querySelector('[data-user-id]');
        if (userElement) {
            const userId = parseInt(userElement.getAttribute('data-user-id'));
            
            // Handle connection
            this.socket.on('connect', () => {
                console.log('Student connected to WebSocket server');
                
                // Join student's personal room
                this.socket.emit('join', {
                    user_type: 'STUDENT',
                    user_id: userId
                });
            });
            
            // Handle join confirmation
            this.socket.on('joined', (data) => {
                console.log('Student joined rooms:', data);
            });
            
            // Handle force pause event
            this.socket.on('force_pause', (data) => {
                console.log('Force pause received:', data);
                showMessage(data.message || 'Your class manager has paused your session', 'info');
                // Session already paused on backend, just update UI
                this.sessionControls.updateUIToPaused();
            });
            
            // Handle force resume event
            this.socket.on('force_resume', (data) => {
                console.log('Force resume received:', data);
                showMessage(data.message || 'Your class manager has resumed your session', 'info');
                // Session already resumed on backend, just update UI
                this.sessionControls.updateUIToResumed();
            });
            
            // Handle force stop event
            this.socket.on('force_stop', (data) => {
                console.log('Force stop received:', data);
                showMessage(data.message || 'Your class manager has ended your session. Please provide feedback', 'warning');
                
                // Redirect to feedback form after a short delay
                setTimeout(() => {
                    window.location.href = `/study/end/${this.sessionId}`;
                }, 2000);
            });
            
            // Handle errors
            this.socket.on('error', (data) => {
                console.error('WebSocket error:', data.message);
            });
        }
    }
}
