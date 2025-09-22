// Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeMainApp();
});

function initializeMainApp() {
    // Initialize current time display
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File input handlers
    initializeFileInputs();

    // Form validation
    initializeFormValidation();
}

function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

function initializeFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const label = this.nextElementSibling;
                if (label && label.classList.contains('form-label')) {
                    label.textContent = file.name;
                }

                // Preview image files
                if (file.type.startsWith('image/')) {
                    previewImage(this, file);
                }
            }
        });
    });
}

function previewImage(input, file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        let preview = input.parentNode.querySelector('.image-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview mt-2';
            input.parentNode.appendChild(preview);
        }
        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">`;
    };
    reader.readAsDataURL(file);
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Utility functions
function showAlert(message, type = 'info', duration = 5000) {
    const alertsContainer = document.querySelector('.alerts-container') || document.querySelector('.container-fluid');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getAlertIcon(type)} me-2"></i>
            <div class="flex-grow-1">${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    if (alertsContainer.firstChild) {
        alertsContainer.insertBefore(alert, alertsContainer.firstChild);
    } else {
        alertsContainer.appendChild(alert);
    }

    if (duration > 0) {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);
    }
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'times-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function formatCurrency(amount, currency = '₹') {
    return `${currency}${formatNumber(amount, 2)}`;
}

function formatWeight(kg) {
    if (kg >= 1000) {
        return `${formatNumber(kg / 1000, 2)} tons`;
    }
    return `${formatNumber(kg, 2)} kg`;
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString();
}

// Loading states
function setLoadingState(element, isLoading = true) {
    if (isLoading) {
        element.classList.add('loading');
        element.disabled = true;
        if (element.tagName === 'BUTTON') {
            element.dataset.originalText = element.innerHTML;
            element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        }
    } else {
        element.classList.remove('loading');
        element.disabled = false;
        if (element.tagName === 'BUTTON' && element.dataset.originalText) {
            element.innerHTML = element.dataset.originalText;
            delete element.dataset.originalText;
        }
    }
}

// AJAX helper
function makeRequest(url, options = {}) {
    const defaults = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const config = Object.assign(defaults, options);

    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Table sorting
function initializeTableSorting() {
    const tables = document.querySelectorAll('table.sortable');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, header.dataset.sort));
        });
    });
}

function sortTable(table, column) {
    // Implementation for table sorting
    console.log('Sorting table by column:', column);
}

// Export functions for global use
window.showAlert = showAlert;
window.confirmAction = confirmAction;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatWeight = formatWeight;
window.formatDateTime = formatDateTime;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.setLoadingState = setLoadingState;
window.makeRequest = makeRequest;