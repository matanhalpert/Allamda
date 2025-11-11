/**
 * ClassroomControls - Handles bulk control actions (force pause/resume/stop)
 */
class ClassroomControls {
    constructor(ui) {
        this.ui = ui;
    }

    /**
     * Force pause all active sessions
     */
    async forcePauseAll() {
        if (!confirm('Are you sure you want to pause all active sessions? Students will be notified.')) {
            return;
        }
        
        try {
            const response = await fetch('/classroom/force_pause', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                let message = result.message || `Paused ${result.count} session(s)`;
                if (result.errors && result.errors.length > 0) {
                    message += ` (${result.errors.length} failed)`;
                    console.warn('Pause errors:', result.errors);
                }
                this.ui.showToast(message, result.errors && result.errors.length > 0 ? 'warning' : 'success');
                // UI will update via websocket events (session_paused)
            } else {
                this.ui.showToast(result.error || 'Failed to pause sessions', 'error');
            }
        } catch (error) {
            console.error('Error pausing sessions:', error);
            this.ui.showToast('An error occurred while pausing sessions', 'error');
        }
    }
    
    /**
     * Force resume all paused sessions
     */
    async forceResumeAll() {
        if (!confirm('Are you sure you want to resume all paused sessions? Students will be notified.')) {
            return;
        }
        
        try {
            const response = await fetch('/classroom/force_resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                let message = result.message || `Resumed ${result.count} session(s)`;
                if (result.errors && result.errors.length > 0) {
                    message += ` (${result.errors.length} failed)`;
                    console.warn('Resume errors:', result.errors);
                }
                this.ui.showToast(message, result.errors && result.errors.length > 0 ? 'warning' : 'success');
                // UI will update via websocket events (session_resumed)
            } else {
                this.ui.showToast(result.error || 'Failed to resume sessions', 'error');
            }
        } catch (error) {
            console.error('Error resuming sessions:', error);
            this.ui.showToast('An error occurred while resuming sessions', 'error');
        }
    }
    
    /**
     * Force stop all sessions (active and paused)
     */
    async forceStopAll() {
        if (!confirm('Are you sure you want to stop all sessions? Students will be redirected to provide feedback. This action affects all active and paused sessions.')) {
            return;
        }
        
        try {
            const response = await fetch('/classroom/force_stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                let message = result.message || `Stopped ${result.count} session(s)`;
                if (result.errors && result.errors.length > 0) {
                    message += ` (${result.errors.length} failed)`;
                    console.warn('Stop errors:', result.errors);
                }
                this.ui.showToast(message, result.errors && result.errors.length > 0 ? 'warning' : 'success');
                // Students are being redirected to feedback - sessions will be removed when completed
            } else {
                this.ui.showToast(result.error || 'Failed to stop sessions', 'error');
            }
        } catch (error) {
            console.error('Error stopping sessions:', error);
            this.ui.showToast('An error occurred while stopping sessions', 'error');
        }
    }
}

