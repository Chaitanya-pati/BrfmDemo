// Camera functionality for file uploads

let currentStream = null;
let currentCamera = null;

function initializeCamera(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    if (!input || !preview) {
        console.error('Camera initialization failed: elements not found');
        return;
    }
    
    // Create camera controls
    const controls = createCameraControls(inputId);
    input.parentNode.insertBefore(controls, input.nextSibling);
}

function createCameraControls(inputId) {
    const controls = document.createElement('div');
    controls.className = 'camera-controls mt-2';
    controls.innerHTML = `
        <div class="d-flex gap-2 mb-2">
            <button type="button" class="btn btn-outline-primary btn-sm" onclick="startCamera('${inputId}')">
                <i class="fas fa-camera me-1"></i>Start Camera
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="stopCamera('${inputId}')" disabled>
                <i class="fas fa-stop me-1"></i>Stop Camera
            </button>
            <button type="button" class="btn btn-outline-success btn-sm" onclick="capturePhoto('${inputId}')" disabled>
                <i class="fas fa-camera-retro me-1"></i>Capture
            </button>
        </div>
        <video id="${inputId}_video" class="camera-preview" style="display: none; max-width: 100%; height: 200px; background: #000;" autoplay muted playsinline></video>
        <canvas id="${inputId}_canvas" style="display: none;"></canvas>
        <div id="${inputId}_photo_preview" class="photo-preview"></div>
    `;
    return controls;
}

async function startCamera(inputId) {
    try {
        const video = document.getElementById(inputId + '_video');
        const startBtn = document.querySelector(`button[onclick="startCamera('${inputId}')"]`);
        const stopBtn = document.querySelector(`button[onclick="stopCamera('${inputId}')"]`);
        const captureBtn = document.querySelector(`button[onclick="capturePhoto('${inputId}')"]`);
        
        if (!video) {
            throw new Error('Video element not found');
        }
        
        // Stop any existing stream
        if (currentStream) {
            stopCamera(inputId);
        }
        
        // Request camera access
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment' // Use rear camera if available
            },
            audio: false
        };
        
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = currentStream;
        video.style.display = 'block';
        
        // Update button states
        startBtn.disabled = true;
        stopBtn.disabled = false;
        captureBtn.disabled = false;
        
        currentCamera = inputId;
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        let errorMessage = 'Failed to access camera. ';
        
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera access and try again.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else if (error.name === 'NotSupportedError') {
            errorMessage += 'Camera is not supported in this browser.';
        } else {
            errorMessage += error.message;
        }
        
        showAlert(errorMessage, 'danger');
    }
}

function stopCamera(inputId) {
    try {
        const video = document.getElementById(inputId + '_video');
        const startBtn = document.querySelector(`button[onclick="startCamera('${inputId}')"]`);
        const stopBtn = document.querySelector(`button[onclick="stopCamera('${inputId}')"]`);
        const captureBtn = document.querySelector(`button[onclick="capturePhoto('${inputId}')"]`);
        
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
            currentStream = null;
        }
        
        if (video) {
            video.style.display = 'none';
            video.srcObject = null;
        }
        
        // Update button states
        if (startBtn) startBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        if (captureBtn) captureBtn.disabled = true;
        
        currentCamera = null;
        
    } catch (error) {
        console.error('Error stopping camera:', error);
    }
}

function capturePhoto(inputId) {
    try {
        const video = document.getElementById(inputId + '_video');
        const canvas = document.getElementById(inputId + '_canvas');
        const preview = document.getElementById(inputId + '_photo_preview');
        const fileInput = document.getElementById(inputId);
        
        if (!video || !canvas || !video.videoWidth) {
            throw new Error('Camera not ready');
        }
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to blob
        canvas.toBlob(function(blob) {
            if (!blob) {
                throw new Error('Failed to capture photo');
            }
            
            // Create file from blob
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `capture_${timestamp}.jpg`;
            const file = new File([blob], filename, { type: 'image/jpeg' });
            
            // Create FileList object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            // Show preview
            const imageUrl = URL.createObjectURL(blob);
            preview.innerHTML = `
                <div class="captured-photo">
                    <img src="${imageUrl}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                    <div class="mt-1">
                        <small class="text-success"><i class="fas fa-check me-1"></i>Photo captured: ${filename}</small>
                    </div>
                </div>
            `;
            
            // Trigger change event
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Stop camera after capture
            stopCamera(inputId);
            
            showAlert('Photo captured successfully!', 'success');
            
        }, 'image/jpeg', 0.8);
        
    } catch (error) {
        console.error('Error capturing photo:', error);
        showAlert('Failed to capture photo: ' + error.message, 'danger');
    }
}

// Check if camera is supported
function isCameraSupported() {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

// Initialize camera controls on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!isCameraSupported()) {
        console.warn('Camera not supported in this browser');
        return;
    }
    
    // Auto-initialize camera controls for file inputs with camera class
    const cameraInputs = document.querySelectorAll('input[type="file"].camera-enabled');
    cameraInputs.forEach(input => {
        const previewId = input.id + '_preview';
        initializeCamera(input.id, previewId);
    });
});

// Cleanup when page unloads
window.addEventListener('beforeunload', function() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }
});

// Export functions for global use
window.initializeCamera = initializeCamera;
window.startCamera = startCamera;
window.stopCamera = stopCamera;
window.capturePhoto = capturePhoto;
window.isCameraSupported = isCameraSupported;