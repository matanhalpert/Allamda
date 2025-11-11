/**
 * StudyCourseForm - Manages the course and learning unit selection (Step 2)
 * Handles course selection, dynamic learning unit loading, and form validation
 */
class StudyCourseForm {
    constructor(preselectedUnits = []) {
        this.selectedUnits = [];
        this.courseSelect = null;
        this.unitsContainer = null;
        this.nextButton = null;
        this.preselectedUnits = preselectedUnits || [];
        this.init();
    }

    init() {
        // Get form elements
        this.courseSelect = document.getElementById('course_id');
        this.unitsContainer = document.getElementById('learning-units-container');
        this.nextButton = document.getElementById('nextButton');

        // Setup event listeners
        this.courseSelect.addEventListener('change', () => this.handleCourseChange());
        
        // Handle form submission
        document.getElementById('courseForm').addEventListener('submit', (e) => this.handleSubmit(e));
        
        // If course is already selected, load its units
        if (this.courseSelect.value) {
            this.handleCourseChange();
        }
    }

    handleCourseChange() {
        const courseId = this.courseSelect.value;
        
        if (!courseId) {
            this.unitsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Please select a course first to see available learning units.
                </div>
            `;
            this.selectedUnits = [];
            this.validateForm();
            return;
        }

        // Show loading
        this.unitsContainer.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading learning units...</p>
            </div>
        `;

        // Fetch learning units
        this.loadLearningUnits(courseId);
    }

    async loadLearningUnits(courseId) {
        try {
            const response = await fetch(`/study/get_learning_units/${courseId}`);
            const data = await response.json();
            
            if (data.error) {
                this.unitsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${data.error}
                    </div>
                `;
                this.selectedUnits = [];
                this.validateForm();
                return;
            }

            const units = data.learning_units;
            if (units.length === 0) {
                this.unitsContainer.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No learning units available for this course.
                    </div>
                `;
                this.selectedUnits = [];
                this.validateForm();
                return;
            }

            // Display units as checkboxes
            this.renderLearningUnits(units);
            
        } catch (error) {
            this.unitsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading learning units. Please try again.
                </div>
            `;
            this.selectedUnits = [];
            this.validateForm();
            console.error('Error:', error);
        }
    }

    renderLearningUnits(units) {
        let html = '<div class="border rounded p-3 learning-units-scrollable">';
        units.forEach(unit => {
            const unitId = `unit_${unit.name.replace(/\s/g, '_')}`;
            const isPreselected = this.preselectedUnits.includes(unit.name);
            html += `
                <div class="form-check mb-2">
                    <input class="form-check-input learning-unit-checkbox" type="checkbox" 
                           value="${unit.name}" id="${unitId}" ${isPreselected ? 'checked' : ''}>
                    <label class="form-check-label" for="${unitId}">
                        <strong>${unit.name}</strong>
                        ${unit.type ? `<span class="badge bg-secondary ms-2">${unit.type}</span>` : ''}
                        ${unit.description ? `<br><small class="text-muted">${unit.description}</small>` : ''}
                        ${unit.estimated_duration_minutes ? `<br><small class="text-info"><i class="fas fa-clock me-1"></i>~${unit.estimated_duration_minutes} min</small>` : ''}
                    </label>
                </div>
            `;
        });
        html += '</div>';
        
        this.unitsContainer.innerHTML = html;

        // Add event listeners to checkboxes
        document.querySelectorAll('.learning-unit-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.handleUnitSelection(checkbox));
        });

        // Initialize selected units from checkboxes
        this.selectedUnits = [];
        document.querySelectorAll('.learning-unit-checkbox:checked').forEach(checkbox => {
            this.selectedUnits.push(checkbox.value);
        });
        
        this.validateForm();
    }

    handleUnitSelection(checkbox) {
        if (checkbox.checked) {
            if (!this.selectedUnits.includes(checkbox.value)) {
                this.selectedUnits.push(checkbox.value);
            }
        } else {
            this.selectedUnits = this.selectedUnits.filter(u => u !== checkbox.value);
        }
        this.validateForm();
    }

    validateForm() {
        const isValid = 
            this.courseSelect.value !== '' &&
            this.selectedUnits.length > 0;
        
        this.nextButton.disabled = !isValid;
    }

    handleSubmit(event) {
        // If clicking back button, allow form submission
        if (event.submitter && event.submitter.name === 'back') {
            return;
        }
        
        // Remove any existing hidden inputs for learning units
        document.querySelectorAll('input[name="learning_units"]').forEach(input => input.remove());
        
        // Add selected units as hidden inputs
        const form = event.target;
        this.selectedUnits.forEach(unit => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'learning_units';
            input.value = unit;
            form.appendChild(input);
        });
    }
}

