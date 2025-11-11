/**
 * ClassroomUI - Handles UI updates and toast notifications for classroom page
 */
class ClassroomUI {
    constructor() {
        // No initialization needed
    }

    /**
     * Update student row to show they joined the session
     * @param {Object} data - Student session data
     */
    handleStudentJoinedSession(data) {
        const { session_id, student_id, student_name, status, is_attendant, course_name } = data;
        
        // Find the row for this student in the active sessions table (updated selector)
        const table = document.querySelector('.sessions-table-modern tbody, .table-responsive table tbody');
        if (!table) {
            console.log('Active sessions table not found');
            return;
        }
        
        // Find the row by student name or session ID
        const rows = table.querySelectorAll('tr');
        let foundRow = null;
        
        rows.forEach(row => {
            const studentCell = row.querySelector('td:first-child, .student-name-cell');
            if (studentCell && studentCell.textContent.includes(student_name)) {
                foundRow = row;
            }
        });
        
        if (foundRow) {
            // Update the attendance badge
            const attendanceCell = foundRow.querySelector('td:nth-child(4)');
            if (attendanceCell) {
                attendanceCell.innerHTML = `
                    <span class="attendance-badge-modern present">
                        <i class="fas fa-check"></i>
                        <span>Present</span>
                    </span>
                `;
            }
            
            // Show a toast notification
            this.showToast(`${student_name} has joined the session`, 'success');
        } else {
            // Reload page if row not found (shouldn't happen, but just in case)
            console.log('Student row not found, reloading...');
            window.location.reload();
        }
    }
    
    /**
     * Update student row when session starts (PENDING -> ACTIVE)
     * @param {Object} data - Student session data
     */
    handleStudentStartedSession(data) {
        const { session_id, student_id, student_name, status, course_name } = data;
        
        // Find the row for this student in the active sessions table (updated selector)
        const table = document.querySelector('.sessions-table-modern tbody, .table-responsive table tbody');
        if (!table) {
            console.log('Active sessions table not found');
            return;
        }
        
        // Find the row by student name
        const rows = table.querySelectorAll('tr');
        let foundRow = null;
        
        rows.forEach(row => {
            const studentCell = row.querySelector('td:first-child, .student-name-cell');
            if (studentCell && studentCell.textContent.includes(student_name)) {
                foundRow = row;
            }
        });
        
        if (foundRow) {
            // Update the status badge from PENDING to ACTIVE
            const statusCell = foundRow.querySelector('td:nth-child(3)');
            if (statusCell) {
                statusCell.innerHTML = `
                    <span class="status-badge-modern status-active">
                        <i class="fas fa-play"></i>
                        <span>Active</span>
                    </span>
                `;
            }
            
            // Show a toast notification
            this.showToast(`${student_name} started their session`, 'success');
        }
    }
    
    /**
     * Handle session completed - remove row from table
     * @param {Object} data - Student session data
     */
    handleSessionCompleted(data) {
        const { session_id, student_id, student_name, difficulty_feedback, understanding_feedback } = data;
        
        // Show a toast notification
        this.showToast(`${student_name} has completed their session`, 'info');
        
        // Remove the row from active sessions table (updated selector)
        const table = document.querySelector('.sessions-table-modern tbody, .table-responsive table tbody');
        if (table) {
            const rows = table.querySelectorAll('tr');
            rows.forEach(row => {
                const studentCell = row.querySelector('td:first-child, .student-name-cell');
                if (studentCell && studentCell.textContent.includes(student_name)) {
                    // Fade out and remove
                    row.style.transition = 'opacity 0.5s';
                    row.style.opacity = '0';
                    setTimeout(() => {
                        row.remove();
                        
                        // If no more rows, optionally show a message or hide the section
                        const remainingRows = table.querySelectorAll('tr').length;
                        if (remainingRows === 0) {
                            const card = document.querySelector('.active-session-card, .card.shadow-sm.border-primary');
                            if (card) {
                                card.innerHTML = `
                                    <div class="text-center p-5">
                                        <div class="start-session-icon mx-auto mb-3">
                                            <i class="fas fa-check-circle"></i>
                                        </div>
                                        <h5 class="start-session-title">All sessions completed!</h5>
                                        <p class="start-session-description">Students have finished their study sessions.</p>
                                    </div>
                                `;
                            }
                        }
                    }, 500);
                }
            });
        }
    }
    
    /**
     * Update student row when session is paused
     * @param {Object} data - Student session data
     */
    handleSessionPaused(data) {
        const { session_id, student_id, student_name, status, course_name } = data;
        
        // Find the row for this student in the active sessions table (updated selector)
        const table = document.querySelector('.sessions-table-modern tbody, .table-responsive table tbody');
        if (!table) {
            console.log('Active sessions table not found');
            return;
        }
        
        // Find the row by student name
        const rows = table.querySelectorAll('tr');
        let foundRow = null;
        
        rows.forEach(row => {
            const studentCell = row.querySelector('td:first-child, .student-name-cell');
            if (studentCell && studentCell.textContent.includes(student_name)) {
                foundRow = row;
            }
        });
        
        if (foundRow) {
            // Update the status badge to PAUSED
            const statusCell = foundRow.querySelector('td:nth-child(3)');
            if (statusCell) {
                statusCell.innerHTML = `
                    <span class="status-badge-modern status-paused">
                        <i class="fas fa-pause"></i>
                        <span>Paused</span>
                    </span>
                `;
            }
            
            // Show a toast notification
            this.showToast(`${student_name} has paused their session`, 'info');
        }
    }
    
    /**
     * Update student row when session is resumed
     * @param {Object} data - Student session data
     */
    handleSessionResumed(data) {
        const { session_id, student_id, student_name, status, course_name } = data;
        
        // Find the row for this student in the active sessions table (updated selector)
        const table = document.querySelector('.sessions-table-modern tbody, .table-responsive table tbody');
        if (!table) {
            console.log('Active sessions table not found');
            return;
        }
        
        // Find the row by student name
        const rows = table.querySelectorAll('tr');
        let foundRow = null;
        
        rows.forEach(row => {
            const studentCell = row.querySelector('td:first-child, .student-name-cell');
            if (studentCell && studentCell.textContent.includes(student_name)) {
                foundRow = row;
            }
        });
        
        if (foundRow) {
            // Update the status badge back to ACTIVE
            const statusCell = foundRow.querySelector('td:nth-child(3)');
            if (statusCell) {
                statusCell.innerHTML = `
                    <span class="status-badge-modern status-active">
                        <i class="fas fa-play"></i>
                        <span>Active</span>
                    </span>
                `;
            }
            
            // Show a toast notification
            this.showToast(`${student_name} has resumed their session`, 'success');
        }
    }
    
    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Type of notification (success, error, warning, info)
     */
    showToast(message, type = 'info') {
        // Create a simple toast notification
        const toastContainer = this.getOrCreateToastContainer();
        
        // Map type to Bootstrap alert class and icon
        const typeMap = {
            'success': { class: 'success', icon: 'check-circle' },
            'error': { class: 'danger', icon: 'exclamation-circle' },
            'warning': { class: 'warning', icon: 'exclamation-triangle' },
            'info': { class: 'info', icon: 'info-circle' }
        };
        
        const alertType = typeMap[type] || typeMap['info'];
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${alertType.class} alert-dismissible fade show`;
        toast.style.cssText = 'margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);';
        
        // Create icon element
        const icon = document.createElement('i');
        icon.className = `fas fa-${alertType.icon} me-2`;
        
        // Create text node for message (safe from XSS)
        const messageText = document.createTextNode(message);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        closeButton.setAttribute('aria-label', 'Close');
        
        // Append elements safely
        toast.appendChild(icon);
        toast.appendChild(messageText);
        toast.appendChild(closeButton);
        
        toastContainer.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    /**
     * Get or create toast container element
     * @returns {HTMLElement} Toast container
     */
    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; width: 350px;';
            document.body.appendChild(container);
        }
        return container;
    }
}

