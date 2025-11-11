/**
 * Study Hub WebSocket Client
 * Handles real-time updates for student study page
 */

class StudyHubWebSocket {
    constructor(userId, userType, classId) {
        this.userId = userId;
        this.userType = userType;
        this.classId = classId;
        this.socket = null;
        this.notificationPermission = null;
        
        this.init();
    }
    
    init() {
        // Request notification permission
        this.requestNotificationPermission();
        
        // Connect to WebSocket server
        this.connect();
    }
    
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
        
        // Handle school session created event
        this.socket.on('school_session_created', (data) => {
            console.log('School session created:', data);
            this.handleSchoolSessionCreated(data);
        });
    }
    
    joinRoom() {
        // Join the appropriate room based on user type
        this.socket.emit('join', {
            user_type: this.userType,
            user_id: this.userId
        });
    }
    
    async requestNotificationPermission() {
        // Check if browser supports notifications
        if (!('Notification' in window)) {
            console.log('This browser does not support notifications');
            return;
        }
        
        // Check current permission
        if (Notification.permission === 'granted') {
            this.notificationPermission = 'granted';
        } else if (Notification.permission !== 'denied') {
            // Request permission
            try {
                const permission = await Notification.requestPermission();
                this.notificationPermission = permission;
                localStorage.setItem('notificationPermission', permission);
            } catch (error) {
                console.error('Error requesting notification permission:', error);
            }
        } else {
            this.notificationPermission = 'denied';
        }
    }
    
    showBrowserNotification(title, body) {
        // Only show notification if:
        // 1. Permission is granted
        // 2. Page is not visible (user is on another tab or app)
        if (this.notificationPermission === 'granted' && document.hidden) {
            const notification = new Notification(title, {
                body: body,
                icon: '/static/images/logo.png',
                badge: '/static/images/logo.png',
                tag: 'school-session',
                requireInteraction: false
            });
            
            // Handle notification click - navigate to study page
            notification.onclick = () => {
                window.focus();
                notification.close();
            };
            
            // Auto-close after 10 seconds
            setTimeout(() => {
                notification.close();
            }, 10000);
        }
    }
    
    handleSchoolSessionCreated(data) {
        const { duration_minutes, start_time } = data;
        
        // Show browser notification
        const title = 'New Study Session Available';
        const body = `Your teacher has started a personalized study session for you. Click to join!`;
        this.showBrowserNotification(title, body);
        
        // Update the UI to show the join button
        this.updateUIForNewSession(data);
    }
    
    updateUIForNewSession(data) {
        // Reload the page to show the new session
        // This is the simplest approach and ensures all data is fresh
        window.location.reload();
    }
}

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Get user data from the page
    const userElement = document.querySelector('[data-user-id]');
    if (userElement) {
        const userId = parseInt(userElement.getAttribute('data-user-id'));
        const userType = userElement.getAttribute('data-user-type');
        const classId = userElement.getAttribute('data-class-id');
        
        console.log('Initializing WebSocket - User ID:', userId, 'User Type:', userType);
        
        // Normalize user type (handle variations like "student", "STUDENT", etc.)
        const normalizedUserType = userType ? userType.toUpperCase().replace(/\s+/g, '_') : '';
        
        if (userId && normalizedUserType === 'STUDENT') {
            window.studyHubWS = new StudyHubWebSocket(userId, 'STUDENT', classId);
            console.log('StudyHubWebSocket initialized');
        } else {
            console.log('WebSocket not initialized. Reason:', !userId ? 'No user ID' : !userType ? 'No user type' : `Not a student (got: ${normalizedUserType})`);
        }
    }
});

