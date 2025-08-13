/**
 * Main JavaScript file for Wheat Processing Management System
 * Handles common functionality across all pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Handle file uploads
    initializeFileUploads();
    
    // Auto-refresh for real-time updates
    initializeAutoRefresh();
    
    // Navigation active state
    setActiveNavigation();
    
    // Confirmation dialogs
    initializeConfirmations();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    let isValid = true;
    const value = field.value.trim();
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        isValid = false;
    }
    // Email validation
    else if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        isValid = false;
    }
    // Phone validation
    else if (field.type === 'tel' && value && !isValidPhone(value)) {
        showFieldError(field, 'Please enter a valid phone number');
        isValid = false;
    }
    // Number validation
    else if (field.type === 'number' && value) {
        const min = parseFloat(field.min);
        const max = parseFloat(field.max);
        const val = parseFloat(value);
        
        if (!isNaN(min) && val < min) {
            showFieldError(field, `Value must be at least ${min}`);
            isValid = false;
        } else if (!isNaN(max) && val > max) {
            showFieldError(field, `Value must be no more than ${max}`);
            isValid = false;
        }
    }
    
    if (isValid) {
        clearFieldError(field);
    }
    
    return isValid;
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Email validation
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Phone validation
 */
function isValidPhone(phone) {
    // Remove all non-digit characters
    const cleaned = phone.replace(/\D/g, '');
    // Check if it's 10-15 digits
    return cleaned.length >= 10 && cleaned.length <= 15;
}

/**
 * Initialize file upload handling
 */
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            validateFileUpload(this);
            previewFile(this);
        });
    });
}

/**
 * Validate file upload
 */
function validateFileUpload(input) {
    const file = input.files[0];
    if (!file) return true;
    
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    
    if (file.size > maxSize) {
        showFieldError(input, 'File size must be less than 16MB');
        input.value = '';
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        showFieldError(input, 'Only JPEG, PNG, GIF images and PDF files are allowed');
        input.value = '';
        return false;
    }
    
    clearFieldError(input);
    return true;
}

/**
 * Preview uploaded file
 */
function previewFile(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Remove existing preview
    const existingPreview = input.parentNode.querySelector('.file-preview');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.createElement('div');
            preview.className = 'file-preview mt-2';
            preview.innerHTML = `
                <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                <p class="small text-muted mt-1">${file.name} (${formatFileSize(file.size)})</p>
            `;
            input.parentNode.appendChild(preview);
        };
        reader.readAsDataURL(file);
    } else {
        const preview = document.createElement('div');
        preview.className = 'file-preview mt-2';
        preview.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-file-pdf"></i> ${file.name} (${formatFileSize(file.size)})
            </div>
        `;
        input.parentNode.appendChild(preview);
    }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Initialize auto-refresh for specific pages
 */
function initializeAutoRefresh() {
    // Only auto-refresh on dashboard and monitoring pages
    const autoRefreshPages = ['/', '/reports', '/cleaning_management'];
    const currentPath = window.location.pathname;
    
    if (autoRefreshPages.includes(currentPath)) {
        // Refresh every 5 minutes
        setInterval(function() {
            // Only refresh if page is visible
            if (!document.hidden) {
                const statusElements = document.querySelectorAll('[data-auto-refresh]');
                statusElements.forEach(element => {
                    refreshElement(element);
                });
            }
        }, 300000); // 5 minutes
    }
}

/**
 * Refresh specific element content
 */
function refreshElement(element) {
    const url = element.dataset.refreshUrl;
    if (url) {
        fetch(url)
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
            })
            .catch(error => {
                console.error('Error refreshing element:', error);
            });
    }
}

/**
 * Set active navigation state
 */
function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Initialize confirmation dialogs
 */
function initializeConfirmations() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Show loading state for forms
 */
function showLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    }
}

/**
 * Hide loading state for forms
 */
function hideLoading(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
    }
}

/**
 * Format numbers for display
 */
function formatNumber(number, decimals = 1) {
    return parseFloat(number).toFixed(decimals);
}

/**
 * Format weight for display
 */
function formatWeight(weightInKg) {
    if (weightInKg >= 1000) {
        return formatNumber(weightInKg / 1000, 1) + ' tons';
    } else {
        return formatNumber(weightInKg, 1) + ' kg';
    }
}

/**
 * Calculate percentage
 */
function calculatePercentage(value, total) {
    if (total === 0) return 0;
    return (value / total) * 100;
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, duration);
}

/**
 * Utility function to get current date in YYYY-MM-DD format
 */
function getCurrentDate() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Utility function to get current time in HH:MM format
 */
function getCurrentTime() {
    return new Date().toTimeString().slice(0, 5);
}

/**
 * Local storage helpers
 */
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    }
};

/**
 * Export utilities for use in other scripts
 */
window.WheatProcessing = {
    validateField,
    validateForm,
    showFieldError,
    clearFieldError,
    isValidEmail,
    isValidPhone,
    validateFileUpload,
    formatFileSize,
    formatNumber,
    formatWeight,
    calculatePercentage,
    debounce,
    showNotification,
    getCurrentDate,
    getCurrentTime,
    Storage
};
