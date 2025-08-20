// Production Execution JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeProductionExecution();
});

function initializeProductionExecution() {
    // Initialize progress tracking
    updateJobProgress();
    
    // Initialize countdown timers
    initializeCountdowns();
    
    // Initialize job filtering
    initializeJobFilters();
    
    // Start auto-refresh for active jobs
    setInterval(updateJobProgress, 30000); // Update every 30 seconds
    setInterval(checkReminders, 60000); // Check reminders every minute
}

function filterJobs(status) {
    const rows = document.querySelectorAll('.job-row');
    const buttons = document.querySelectorAll('.btn-group .btn');
    
    // Update button states
    buttons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Filter rows
    rows.forEach(row => {
        if (status === 'all') {
            row.style.display = '';
        } else {
            if (row.dataset.status === status) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

function updateJobProgress() {
    fetch('/api/job_progress')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            data.forEach(job => {
                const progressBar = document.querySelector(`[data-job-id="${job.id}"]`);
                if (progressBar) {
                    progressBar.style.width = job.progress + '%';
                    const progressText = progressBar.closest('td').querySelector('small');
                    if (progressText) {
                        progressText.textContent = job.progress + '%';
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error updating job progress:', error);
            if (typeof showNotification === 'function') {
                showNotification('Error updating job progress', 'error');
            }
        });
}

function checkReminders() {
    fetch('/api/check_reminders')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.new_reminders > 0) {
                showNotification(`You have ${data.new_reminders} new reminders!`, 'warning');
            }
        })
        .catch(error => {
            console.error('Error checking reminders:', error);
        });
}

function initializeCountdowns() {
    const countdowns = document.querySelectorAll('.countdown');
    
    countdowns.forEach(countdown => {
        const endTime = new Date(countdown.dataset.endTime);
        updateCountdown(countdown, endTime);
        
        // Update every minute
        setInterval(() => updateCountdown(countdown, endTime), 60000);
    });
}

function updateCountdown(element, endTime) {
    const now = new Date();
    const timeLeft = endTime - now;
    
    if (timeLeft <= 0) {
        element.textContent = 'Completed';
        element.classList.remove('warning', 'danger');
        return;
    }
    
    const hours = Math.floor(timeLeft / (1000 * 60 * 60));
    const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    
    element.textContent = `${hours}h ${minutes}m`;
    
    // Color coding based on time remaining
    if (timeLeft <= 30 * 60 * 1000) { // 30 minutes
        element.classList.add('danger');
        element.classList.remove('warning');
    } else if (timeLeft <= 60 * 60 * 1000) { // 1 hour
        element.classList.add('warning');
        element.classList.remove('danger');
    }
}

function initializeJobFilters() {
    const filterButtons = document.querySelectorAll('.btn-group .btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            filterJobs(filter);
        });
    });
}

function startJob(jobId) {
    if (!confirm('Are you sure you want to start this job?')) {
        return;
    }
    
    fetch('/api/start_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred starting the job', 'error');
    });
}

function pauseJob(jobId) {
    if (!confirm('Are you sure you want to pause this job?')) {
        return;
    }
    
    fetch('/api/pause_job', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred pausing the job', 'error');
    });
}

function viewJobDetails(jobId) {
    fetch(`/api/production_job/${jobId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(job => {
            // Populate job details modal
            const modal = document.getElementById('jobDetailsModal');
            if (modal) {
                modal.querySelector('.modal-title').textContent = `Job ${job.job_number}`;
                modal.querySelector('#jobOrderNumber').textContent = job.order_number;
                modal.querySelector('#jobStage').textContent = job.stage.replace('_', ' ');
                modal.querySelector('#jobStatus').textContent = job.status.replace('_', ' ');
                modal.querySelector('#jobProgress').style.width = job.progress + '%';
                modal.querySelector('#jobProgressText').textContent = job.progress + '%';
                
                // Timeline
                const timeline = modal.querySelector('#jobTimeline');
                timeline.innerHTML = '';
                
                if (job.timeline && job.timeline.length > 0) {
                    job.timeline.forEach(event => {
                        const timelineItem = document.createElement('div');
                        timelineItem.className = 'timeline-item';
                        timelineItem.innerHTML = `
                            <div class="d-flex justify-content-between">
                                <strong>${event.stage}</strong>
                                <small class="text-muted">${new Date(event.time).toLocaleString()}</small>
                            </div>
                            <small class="text-muted">By: ${event.operator}</small>
                            ${event.quantity ? `<small class="text-info">Quantity: ${event.quantity}</small>` : ''}
                        `;
                        timeline.appendChild(timelineItem);
                    });
                } else {
                    timeline.innerHTML = '<p class="text-muted">No timeline events yet.</p>';
                }
                
                new bootstrap.Modal(modal).show();
            }
        })
        .catch(error => {
            console.error('Error fetching job details:', error);
            showNotification('Error loading job details', 'error');
        });
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Make showNotification globally available
window.showNotification = showNotification;

// File upload preview
function previewFile(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);
    
    if (file && preview) {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" class="file-preview img-thumbnail">`;
            };
            reader.readAsDataURL(file);
        } else {
            preview.innerHTML = `<div class="alert alert-info">File selected: ${file.name}</div>`;
        }
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Auto-save form data
function enableAutoSave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        });
    });
    
    // Restore saved data
    const savedData = localStorage.getItem(`form_${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && !input.value) {
                input.value = data[key];
            }
        });
    }
}

// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
});