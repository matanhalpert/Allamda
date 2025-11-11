/**
 * Dashboard Interactive Features
 * Handles calendar interactions, animations, and dynamic UI elements
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeAnimations();
    initializeStatsCounters();
});

/**
 * Initialize calendar event interactions
 */
function initializeCalendar() {
    const eventDots = document.querySelectorAll('.event-dot');
    const tooltip = document.getElementById('event-tooltip');
    
    eventDots.forEach(dot => {
        // Show tooltip on hover
        dot.addEventListener('mouseenter', function(e) {
            const title = this.getAttribute('data-event-title');
            const time = this.getAttribute('data-event-time');
            
            if (tooltip && title) {
                tooltip.querySelector('.tooltip-title').textContent = title;
                tooltip.querySelector('.tooltip-time').textContent = time;
                tooltip.style.display = 'block';
                
                // Position tooltip near the cursor
                updateTooltipPosition(e);
            }
        });
        
        // Update tooltip position on mouse move
        dot.addEventListener('mousemove', function(e) {
            updateTooltipPosition(e);
        });
        
        // Hide tooltip on mouse leave
        dot.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        });
        
        // Click event for event dots
        dot.addEventListener('click', function(e) {
            e.stopPropagation();
            const title = this.getAttribute('data-event-title');
            const time = this.getAttribute('data-event-time');
            showEventModal(title, time);
        });
    });
    
    // Calendar day click handlers
    const calendarDays = document.querySelectorAll('.calendar-day');
    calendarDays.forEach(day => {
        day.addEventListener('click', function() {
            const date = this.getAttribute('data-date');
            const events = this.querySelectorAll('.event-dot');
            
            if (events.length > 0) {
                highlightDay(this);
            }
        });
    });
}

/**
 * Update tooltip position relative to cursor
 */
function updateTooltipPosition(e) {
    const tooltip = document.getElementById('event-tooltip');
    if (!tooltip) return;
    
    const offsetX = 15;
    const offsetY = 15;
    
    let x = e.clientX + offsetX;
    let y = e.clientY + offsetY;
    
    // Prevent tooltip from going off-screen
    const tooltipRect = tooltip.getBoundingClientRect();
    const maxX = window.innerWidth - tooltipRect.width - 10;
    const maxY = window.innerHeight - tooltipRect.height - 10;
    
    if (x > maxX) x = e.clientX - tooltipRect.width - offsetX;
    if (y > maxY) y = e.clientY - tooltipRect.height - offsetY;
    
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
}

/**
 * Show event details in a simple alert (can be replaced with a modal)
 */
function showEventModal(title, time) {
    // For now, using a simple alert. Can be enhanced with a proper modal later.
    const message = `Event: ${title}\nTime: ${time}`;
    
    // Create a custom simple modal
    const existingModal = document.getElementById('simple-event-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'simple-event-modal';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        max-width: 400px;
        width: 90%;
        animation: modalFadeIn 0.3s ease-out;
    `;
    
    modal.innerHTML = `
        <h3 style="margin-top: 0; color: #4f46e5; font-size: 1.25rem;">
            <i class="fas fa-calendar-check"></i> Event Details
        </h3>
        <p style="margin: 1rem 0; color: #212529;"><strong>${title}</strong></p>
        <p style="margin: 0.5rem 0; color: #6b7280;"><i class="fas fa-clock"></i> ${time}</p>
        <button onclick="closeEventModal()" style="
            margin-top: 1.5rem;
            padding: 0.75rem 1.5rem;
            background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
        ">Close</button>
    `;
    
    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.id = 'modal-backdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
        animation: backdropFadeIn 0.3s ease-out;
    `;
    backdrop.onclick = closeEventModal;
    
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
    
    // Add animation styles if not exists
    if (!document.getElementById('modal-animations')) {
        const style = document.createElement('style');
        style.id = 'modal-animations';
        style.textContent = `
            @keyframes modalFadeIn {
                from {
                    opacity: 0;
                    transform: translate(-50%, -45%);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%);
                }
            }
            @keyframes backdropFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Close the event modal
 */
function closeEventModal() {
    const modal = document.getElementById('simple-event-modal');
    const backdrop = document.getElementById('modal-backdrop');
    
    if (modal) modal.remove();
    if (backdrop) backdrop.remove();
}

// Make closeEventModal global so it can be called from the button
window.closeEventModal = closeEventModal;

/**
 * Highlight a calendar day temporarily
 */
function highlightDay(dayElement) {
    // Remove previous highlights
    document.querySelectorAll('.calendar-day.highlighted').forEach(el => {
        el.classList.remove('highlighted');
    });
    
    // Add highlight to clicked day
    dayElement.classList.add('highlighted');
    
    // Add temporary highlight style if not exists
    if (!document.getElementById('highlight-style')) {
        const style = document.createElement('style');
        style.id = 'highlight-style';
        style.textContent = `
            .calendar-day.highlighted {
                animation: pulseHighlight 0.6s ease-out;
            }
            @keyframes pulseHighlight {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Initialize staggered animations for dashboard sections
 */
function initializeAnimations() {
    const sections = document.querySelectorAll('.dashboard-section');
    
    // Create intersection observer for animation on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

/**
 * Animate stat counters on page load
 */
function initializeStatsCounters() {
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach(stat => {
        const text = stat.textContent;
        const number = parseFloat(text);
        
        // Only animate if it's a number
        if (!isNaN(number)) {
            animateCounter(stat, 0, number, 1000);
        }
    });
}

/**
 * Animate a number counter from start to end
 */
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16); // 60 FPS
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        // Format the number (preserve decimals if original had them)
        const originalText = element.textContent;
        const hasDecimal = originalText.includes('.');
        const suffix = originalText.replace(/[\d.-]/g, '');
        
        if (hasDecimal) {
            element.textContent = current.toFixed(1) + suffix;
        } else {
            element.textContent = Math.floor(current) + suffix;
        }
    }, 16);
}

/**
 * Add smooth hover effects to action cards
 */
document.addEventListener('DOMContentLoaded', function() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.action-icon i');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
                icon.style.transition = 'transform 0.3s ease';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.action-icon i');
            if (icon) {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    });
});

/**
 * Add hover effects to course cards
 */
document.addEventListener('DOMContentLoaded', function() {
    const courseCards = document.querySelectorAll('.course-card');
    
    courseCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.course-icon i');
            if (icon) {
                icon.style.transform = 'rotate(10deg) scale(1.1)';
                icon.style.transition = 'transform 0.3s ease';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.course-icon i');
            if (icon) {
                icon.style.transform = 'rotate(0deg) scale(1)';
            }
        });
    });
});

/**
 * Add pulse animation to achievement icons
 */
document.addEventListener('DOMContentLoaded', function() {
    const achievementIcons = document.querySelectorAll('.achievement-icon');
    
    achievementIcons.forEach((icon, index) => {
        // Stagger the animation
        setTimeout(() => {
            icon.style.animation = 'achievementPulse 2s ease-in-out infinite';
        }, index * 200);
    });
    
    // Add animation style if not exists
    if (!document.getElementById('achievement-animation')) {
        const style = document.createElement('style');
        style.id = 'achievement-animation';
        style.textContent = `
            @keyframes achievementPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
        `;
        document.head.appendChild(style);
    }
});

/**
 * Welcome animation - slight delay for dramatic effect
 */
document.addEventListener('DOMContentLoaded', function() {
    const welcomeBanner = document.querySelector('.welcome-banner');
    if (welcomeBanner) {
        welcomeBanner.style.opacity = '0';
        welcomeBanner.style.transform = 'translateY(-30px)';
        
        setTimeout(() => {
            welcomeBanner.style.transition = 'all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            welcomeBanner.style.opacity = '1';
            welcomeBanner.style.transform = 'translateY(0)';
        }, 100);
    }
});

