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

function updateJobProgress() {
    fetch('/api/job_progress')
        .then(response => response.json())
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
        .catch(error => console.error('Error updating job progress:', error));
}

function checkReminders() {
    fetch('/api/check_reminders')
        .then(response => response.json())
        .then(data => {
            if (data.reminders && data.reminders.length > 0) {
                data.reminders.forEach(reminder => {
                    showNotification(reminder.message, reminder.type || 'warning');
                });
            }
        })
        .catch(error => console.error('Error checking reminders:', error));
}

function initializeCountdowns() {
    const countdowns = document.querySelectorAll('.countdown');
    
    countdowns.forEach(countdown => {
        const endTime = new Date(countdown.dataset.endTime);
        updateCountdown(countdown, endTime);
        setInterval(() => updateCountdown(countdown, endTime), 1000);
    });
}

function updateCountdown(element, endTime) {
    const now = new Date();
    const distance = endTime - now;
    
    if (distance < 0) {
        element.innerHTML = "COMPLETED";
        element.classList.add('text-danger', 'fw-bold');
        return;
    }
    
    const hours = Math.floor(distance / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
    element.innerHTML = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Add warning styles when less than 30 minutes remaining
    if (distance < 30 * 60 * 1000) {
        element.classList.add('text-warning', 'fw-bold');
    }
    
    // Add danger styles when less than 10 minutes remaining
    if (distance < 10 * 60 * 1000) {
        element.classList.remove('text-warning');
        element.classList.add('text-danger', 'fw-bold');
    }
}

function initializeJobFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            filterJobs(filter);
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function filterJobs(status) {
    const rows = document.querySelectorAll('.job-row');
    
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

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        max-width: 350px;
        animation: slideIn 0.3s ease;
    `;
    
    notification.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 8 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.remove();
        }
    }, 8000);
}

// Production stage specific functions
function startJob(jobId, stage) {
    if (stage === 'transfer') {
        window.location.href = `/production_execution/transfer/${jobId}`;
    } else if (stage === 'cleaning_24h') {
        window.location.href = `/production_execution/cleaning_24h/${jobId}`;
    } else if (stage === 'cleaning_12h') {
        window.location.href = `/production_execution/cleaning_12h/${jobId}`;
    } else if (stage === 'grinding') {
        window.location.href = `/production_execution/grinding/${jobId}`;
    } else if (stage === 'packing') {
        window.location.href = `/production_execution/packing/${jobId}`;
    }
}

function startTransferProcess(jobId) {
    window.location.href = `/production_execution/transfer/${jobId}`;
}

function startCleaningProcess(jobId, processType) {
    if (processType === '24h') {
        window.location.href = `/production_execution/cleaning_24h/${jobId}`;
    } else if (processType === '12h') {
        window.location.href = `/production_execution/cleaning_12h/${jobId}`;
    }
}

function startGrindingProcess(jobId) {
    window.location.href = `/production_execution/grinding/${jobId}`;
}

function startPackingProcess(jobId) {
    window.location.href = `/production_execution/packing/${jobId}`;
}

// Machine cleaning functions
function recordMachineCleaning(machineId) {
    window.location.href = `/production_execution/machine_cleaning/${machineId}`;
}

function checkMachineStatus() {
    fetch('/api/machine_status')
        .then(response => response.json())
        .then(data => {
            data.machines.forEach(machine => {
                const statusElement = document.querySelector(`[data-machine-id="${machine.id}"] .machine-status`);
                if (statusElement) {
                    statusElement.className = `machine-status ${machine.status_class}`;
                }
            });
            
            // Show overdue cleaning notifications
            if (data.overdue_machines.length > 0) {
                data.overdue_machines.forEach(machine => {
                    showNotification(`Machine "${machine.name}" cleaning is overdue!`, 'danger');
                });
            }
        })
        .catch(error => console.error('Error checking machine status:', error));
}

// Job tracking and search functions
function searchOrderTracking() {
    const orderNumber = document.getElementById('searchOrderNumber').value;
    if (orderNumber) {
        window.location.href = `/order_tracking?order_number=${orderNumber}`;
    }
}

function exportJobReport(jobId) {
    window.open(`/production_execution/export_report/${jobId}`, '_blank');
}

// Missing functions that are called from the template
function startCleaning(jobId, type) {
    if (type === '24h') {
        window.location.href = `/production_execution/cleaning_24h/${jobId}`;
    } else if (type === '12h') {
        window.location.href = `/production_execution/cleaning_12h/${jobId}`;
    }
}

function viewJobDetails(jobId) {
    // Open job details in a modal or navigate to details page
    fetch(`/api/job_details/${jobId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showJobDetailsModal(data.job);
            } else {
                showNotification('Failed to load job details', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading job details:', error);
            showNotification('Error loading job details', 'error');
        });
}

function showJobDetailsModal(job) {
    // Create and show a modal with job details
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Job Details - ${job.job_number}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Order:</strong> ${job.order_number}</p>
                            <p><strong>Stage:</strong> ${job.stage}</p>
                            <p><strong>Status:</strong> <span class="badge bg-${job.status === 'completed' ? 'success' : job.status === 'in_progress' ? 'warning' : 'secondary'}">${job.status}</span></p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Started:</strong> ${job.started_at || 'Not started'}</p>
                            <p><strong>Started By:</strong> ${job.started_by || 'N/A'}</p>
                            <p><strong>Completed:</strong> ${job.completed_at || 'Not completed'}</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Remove modal from DOM when hidden
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// Quality control functions
function recordQualityCheck(processId, processType) {
    window.location.href = `/production_execution/quality_check/${processType}/${processId}`;
}

// Initialize machine status checking
setInterval(checkMachineStatus, 5 * 60 * 1000); // Check every 5 minutes

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .job-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .pipeline-stage {
        transition: background-color 0.3s ease;
    }
    
    .pipeline-stage:hover {
        background-color: rgba(255,255,255,0.2);
    }
`;
document.head.appendChild(style);