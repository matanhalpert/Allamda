/**
 * StudyFeedbackForm - Manages the study session feedback form
 * Handles slider updates and form validation
 */
class StudyFeedbackForm {
    constructor() {
        this.difficultySlider = null;
        this.difficultyValue = null;
        this.understandingSlider = null;
        this.understandingValue = null;
        this.feedbackForm = null;
        this.init();
    }

    init() {
        // Get form elements
        this.difficultySlider = document.getElementById('difficulty_feedback');
        this.difficultyValue = document.getElementById('difficultyValue');
        this.understandingSlider = document.getElementById('understanding_feedback');
        this.understandingValue = document.getElementById('understandingValue');
        this.feedbackForm = document.getElementById('feedbackForm');

        // Setup slider event listeners
        this.difficultySlider.addEventListener('input', () => {
            this.updateSliderValue(this.difficultySlider, this.difficultyValue);
        });
        
        this.understandingSlider.addEventListener('input', () => {
            this.updateSliderValue(this.understandingSlider, this.understandingValue);
        });

        // Handle form submission
        this.feedbackForm.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    updateSliderValue(slider, display) {
        display.textContent = slider.value;
    }

    handleSubmit(event) {
        // Check if an emotional state radio button is selected
        const emotionalState = document.querySelector('input[name="emotional_state_after"]:checked');
        
        if (!emotionalState) {
            event.preventDefault();
            showMessage('Please select your emotional state', 'warning');
            return false;
        }
        
        // Show loading state
        const submitBtn = this.feedbackForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    }
}

