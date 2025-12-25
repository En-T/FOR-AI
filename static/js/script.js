// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();

    // Initialize delete confirmations
    initializeDeleteConfirmations();

    // Initialize AJAX handlers
    initializeAJAXHandlers();
});

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });

    // Validate individual fields on blur
    const inputs = document.querySelectorAll('input[data-required], select[data-required], textarea[data-required]');

    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });

        input.addEventListener('input', function() {
            // Clear error on input
            const errorEl = this.parentNode.querySelector('.form-error') ||
                           this.parentNode.parentNode.querySelector('.form-error');
            if (errorEl) {
                errorEl.remove();
                this.classList.remove('is-invalid');
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[data-required]');

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Additional validation for specific field types
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            isValid = false;
        }
    });

    const numberFields = form.querySelectorAll('input[type="number"]');
    numberFields.forEach(field => {
        if (field.value) {
            const min = parseFloat(field.min);
            const max = parseFloat(field.max);
            const value = parseFloat(field.value);

            if (!isNaN(min) && value < min) {
                showFieldError(field, `Value must be at least ${min}`);
                isValid = false;
            }

            if (!isNaN(max) && value > max) {
                showFieldError(field, `Value must be at most ${max}`);
                isValid = false;
            }
        }
    });

    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Check required
    if (field.hasAttribute('data-required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }

    // Check minlength
    if (isValid && field.hasAttribute('data-minlength')) {
        const minLength = parseInt(field.getAttribute('data-minlength'));
        if (value.length < minLength) {
            isValid = false;
            errorMessage = `Minimum length is ${minLength} characters`;
        }
    }

    // Check maxlength
    if (isValid && field.hasAttribute('data-maxlength')) {
        const maxLength = parseInt(field.getAttribute('data-maxlength'));
        if (value.length > maxLength) {
            isValid = false;
            errorMessage = `Maximum length is ${maxLength} characters`;
        }
    }

    // Check pattern
    if (isValid && field.hasAttribute('data-pattern')) {
        const pattern = new RegExp(field.getAttribute('data-pattern'));
        if (!pattern.test(value)) {
            isValid = false;
            errorMessage = field.getAttribute('data-pattern-error') || 'Invalid format';
        }
    }

    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }

    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);

    field.classList.add('is-invalid');

    const errorEl = document.createElement('div');
    errorEl.className = 'form-error';
    errorEl.textContent = message;

    // Insert after the field
    const parent = field.parentNode;
    parent.appendChild(errorEl);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');

    const parent = field.parentNode;
    const errorEl = parent.querySelector('.form-error');
    if (errorEl) {
        errorEl.remove();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Delete confirmations
function initializeDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('[data-delete-confirm]');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-delete-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Handle delete forms
    const deleteForms = document.querySelectorAll('form[data-delete-confirm]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = form.getAttribute('data-delete-confirm') || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// AJAX handlers
function initializeAJAXHandlers() {
    // Handle AJAX form submissions
    const ajaxForms = document.querySelectorAll('form[data-ajax-submit]');

    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';

            const formData = new FormData(form);
            const url = form.getAttribute('action') || window.location.href;
            const method = form.getAttribute('method') || 'POST';

            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message || 'Success!', 'success');
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    showMessage(data.error || 'An error occurred', 'error');
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) {
                                showFieldError(input, data.errors[field]);
                            }
                        });
                    }
                }
            })
            .catch(error => {
                showMessage('An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    });

    // Handle AJAX links
    const ajaxLinks = document.querySelectorAll('[data-ajax]');

    ajaxLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const url = this.getAttribute('href');
            const confirmMessage = this.getAttribute('data-confirm');

            if (confirmMessage && !confirm(confirmMessage)) {
                return;
            }

            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message || 'Success!', 'success');
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                    if (data.reload) {
                        window.location.reload();
                    }
                } else {
                    showMessage(data.error || 'An error occurred', 'error');
                }
            })
            .catch(error => {
                showMessage('An error occurred. Please try again.', 'error');
            });
        });
    });
}

// Show message
function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.messages');
    existingMessages.forEach(el => el.remove());

    const container = document.createElement('div');
    container.className = `messages message-${type}`;
    container.innerHTML = `<div class="message message-${type}">${message}</div>`;

    const mainContent = document.querySelector('.main-content') || document.body;
    mainContent.insertBefore(container, mainContent.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        container.remove();
    }, 5000);
}

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Student filter by class
function filterStudentsByClass() {
    const classSelect = document.getElementById('class-filter');
    if (classSelect) {
        classSelect.addEventListener('change', function() {
            const classId = this.value;
            const url = classId ? `/students/?class_id=${classId}` : '/students/';
            window.location.href = url;
        });
    }
}

// Bulk upload preview
function previewBulkUpload() {
    const textarea = document.getElementById('bulk-students');
    const preview = document.getElementById('preview');

    if (textarea && preview) {
        const lines = textarea.value.trim().split('\n').filter(line => line.trim());
        const count = lines.length;
        preview.textContent = `${count} student(s) will be added`;
    }
}

// Grade color highlighting
function highlightLowGrades() {
    const gradeInputs = document.querySelectorAll('.grade-input');

    gradeInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value >= 1 && value <= 2) {
                this.classList.add('grade-low');
            } else {
                this.classList.remove('grade-low');
            }
        });

        // Initialize on load
        const value = parseInt(input.value);
        if (value >= 1 && value <= 2) {
            input.classList.add('grade-low');
        }
    });
}

// Subgroup student selection
function initializeSubgroupSelection() {
    const checkboxes = document.querySelectorAll('.subgroup-student input[type="checkbox"]');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const studentId = this.value;
            const subgroupId = this.dataset.subgroup;

            // You can add AJAX here to save assignment in real-time
        });
    });
}

// Class selection handlers
function handleClassSelection() {
    const classSelect = document.getElementById('id_school_class');
    const subgroupSection = document.getElementById('subgroup-section');

    if (classSelect && subgroupSection) {
        classSelect.addEventListener('change', function() {
            if (this.value) {
                subgroupSection.style.display = 'block';
                // Load subgroups for selected class via AJAX
                loadSubgroups(this.value);
            } else {
                subgroupSection.style.display = 'none';
            }
        });
    }
}

function loadSubgroups(classId) {
    const subgroupSelect = document.getElementById('id_subgroup');

    fetch(`/api/subgroups/?class_id=${classId}`)
        .then(response => response.json())
        .then(data => {
            subgroupSelect.innerHTML = '<option value="">Select subgroup</option>';
            data.subgroups.forEach(subgroup => {
                const option = document.createElement('option');
                option.value = subgroup.id;
                option.textContent = `${subgroup.name} - ${subgroup.subject}`;
                subgroupSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading subgroups:', error);
        });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    highlightLowGrades();
    filterStudentsByClass();
    handleClassSelection();
    initializeSubgroupSelection();
});
