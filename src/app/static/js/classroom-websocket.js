/**
 * ClassroomWebSocket - Manages WebSocket connection and real-time updates for classroom page
 */
class ClassroomWebSocket {
    constructor(userId, userType) {
        this.userId = userId;
        this.userType = userType;
        this.socket = null;
        
        // Initialize sub-modules
        this.ui = new ClassroomUI();
        this.controls = new ClassroomControls(this.ui);
        
        this.init();
    }
    
    /**
     * Initialize WebSocket connection
     */
    init() {
        this.connect();
    }
    
    /**
     * Connect to WebSocket server
     */
    connect() {
        // Connect to SocketIO server
        this.socket = io();
        
        // Handle connection
        this.socket.on('connect', () => {
            console.log('Connected to WebSocket server');
            this.joinRoom();
        });
        
        // Handle disconnection
        this.socket.on('disconnect', () => {
            console.log('Disconnected from WebSocket server');
        });
        
        // Handle reconnection
        this.socket.on('reconnect', () => {
            console.log('Reconnected to WebSocket server');
            this.joinRoom();
        });
        
        // Handle join confirmation
        this.socket.on('joined', (data) => {
            console.log('Joined room:', data.room);
        });
        
        // Handle errors
        this.socket.on('error', (data) => {
            console.error('WebSocket error:', data.message);
        });
        
        // Handle student joined session event
        this.socket.on('student_joined_session', (data) => {
            console.log('Student joined session:', data);
            this.ui.handleStudentJoinedSession(data);
        });
        
        // Handle student started session event (PENDING -> ACTIVE)
        this.socket.on('student_started_session', (data) => {
            console.log('Student started session:', data);
            this.ui.handleStudentStartedSession(data);
        });
        
        // Handle session completed event
        this.socket.on('session_completed', (data) => {
            console.log('Session completed:', data);
            this.ui.handleSessionCompleted(data);
        });
        
        // Handle session paused event
        this.socket.on('session_paused', (data) => {
            console.log('Session paused:', data);
            this.ui.handleSessionPaused(data);
        });
        
        // Handle session resumed event
        this.socket.on('session_resumed', (data) => {
            console.log('Session resumed:', data);
            this.ui.handleSessionResumed(data);
        });
    }
    
    /**
     * Join the manager's personal room
     */
    joinRoom() {
        this.socket.emit('join', {
            user_type: this.userType,
            user_id: this.userId
        });
    }
    
    /**
     * Force pause all sessions (delegates to controls module)
     */
    async forcePauseAll() {
        await this.controls.forcePauseAll();
    }
    
    /**
     * Force resume all sessions (delegates to controls module)
     */
    async forceResumeAll() {
        await this.controls.forceResumeAll();
    }
    
    /**
     * Force stop all sessions (delegates to controls module)
     */
    async forceStopAll() {
        await this.controls.forceStopAll();
    }
}

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Get user data from the page
    const userElement = document.querySelector('[data-user-id]');
    if (userElement) {
        const userId = parseInt(userElement.getAttribute('data-user-id'));
        const userType = userElement.getAttribute('data-user-type');
        
        console.log('Initializing WebSocket - User ID:', userId, 'User Type:', userType);
        
        // Normalize user type (handle both "class manager" and "CLASS_MANAGER" or "class_manager")
        const normalizedUserType = userType ? userType.toUpperCase().replace(/\s+/g, '_') : '';
        
        if (userId && normalizedUserType === 'CLASS_MANAGER') {
            window.classroomWS = new ClassroomWebSocket(userId, 'CLASS_MANAGER');
            console.log('ClassroomWebSocket initialized');
        } else {
            console.log('WebSocket not initialized. Reason:', !userId ? 'No user ID' : !userType ? 'No user type' : `Not a class manager (got: ${normalizedUserType})`);
        }
    }
});

