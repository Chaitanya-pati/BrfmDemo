// Live Camera Capture Functionality
class CameraCapture {
    constructor() {
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.capturedImages = [];
    }

    // Initialize camera for a specific input
    async initCamera(containerId, inputName, multiple = false) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Create camera interface
        const cameraHTML = `
            <div class="camera-interface">
                <div class="camera-preview-container mb-3">
                    <video id="video-${inputName}" class="camera-preview d-none" autoplay playsinline></video>
                    <canvas id="canvas-${inputName}" class="d-none"></canvas>
                </div>
                <div class="camera-controls text-center mb-3">
                    <button type="button" class="btn btn-primary me-2" onclick="startCamera('${inputName}')">
                        <i class="fas fa-camera me-1"></i>Start Camera
                    </button>
                    <button type="button" class="btn btn-success me-2 d-none" onclick="captureImage('${inputName}', ${multiple})">
                        <i class="fas fa-camera-retro me-1"></i>Capture Photo
                    </button>
                    <button type="button" class="btn btn-secondary me-2 d-none" onclick="stopCamera('${inputName}')">
                        <i class="fas fa-stop me-1"></i>Stop Camera
                    </button>
                    <button type="button" class="btn btn-warning me-2" onclick="selectFile('${inputName}', ${multiple})">
                        <i class="fas fa-upload me-1"></i>Upload File
                    </button>
                </div>
                <input type="file" id="file-${inputName}" name="${inputName}${multiple ? '[]' : ''}" 
                       accept="image/*,application/pdf,.doc,.docx" ${multiple ? 'multiple' : ''} class="d-none">
                <div id="preview-${inputName}" class="captured-images"></div>
            </div>
        `;
        container.innerHTML = cameraHTML;
    }

    // Start camera stream
    async startCamera(inputName) {
        try {
            const video = document.getElementById(`video-${inputName}`);
            const constraints = {
                video: {
                    facingMode: 'environment', // Use back camera on mobile
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            video.srcObject = this.stream;
            
            // Show/hide controls
            video.classList.remove('d-none');
            document.querySelector(`#video-${inputName}`).parentElement.parentElement
                .querySelector('button[onclick*="startCamera"]').classList.add('d-none');
            document.querySelector(`#video-${inputName}`).parentElement.parentElement
                .querySelector('button[onclick*="captureImage"]').classList.remove('d-none');
            document.querySelector(`#video-${inputName}`).parentElement.parentElement
                .querySelector('button[onclick*="stopCamera"]').classList.remove('d-none');
                
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Unable to access camera. Please check permissions or use file upload.');
        }
    }

    // Capture image from video stream
    captureImage(inputName, multiple = false) {
        const video = document.getElementById(`video-${inputName}`);
        const canvas = document.getElementById(`canvas-${inputName}`);
        const context = canvas.getContext('2d');
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to blob and create file
        canvas.toBlob((blob) => {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `captured_${inputName}_${timestamp}.jpg`;
            const file = new File([blob], filename, { type: 'image/jpeg' });
            
            // Add to captured images
            this.addCapturedImage(inputName, file, multiple);
            
        }, 'image/jpeg', 0.8);
    }

    // Add captured image to preview
    addCapturedImage(inputName, file, multiple) {
        const preview = document.getElementById(`preview-${inputName}`);
        const fileInput = document.getElementById(`file-${inputName}`);
        
        // Create preview element
        const imageDiv = document.createElement('div');
        imageDiv.className = 'captured-image-item d-inline-block m-2 position-relative';
        imageDiv.innerHTML = `
            <img src="${URL.createObjectURL(file)}" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
            <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                    onclick="removeCapturedImage(this, '${inputName}')">
                <i class="fas fa-times"></i>
            </button>
            <div class="text-center mt-1">
                <small class="text-muted">${file.name}</small>
            </div>
        `;
        
        if (multiple) {
            preview.appendChild(imageDiv);
            // Add to file input's files (this is tricky with regular inputs)
            this.updateFileInput(inputName, file, true);
        } else {
            preview.innerHTML = '';
            preview.appendChild(imageDiv);
            this.updateFileInput(inputName, file, false);
        }
    }

    // Update file input with captured files
    updateFileInput(inputName, file, multiple) {
        const fileInput = document.getElementById(`file-${inputName}`);
        
        if (multiple) {
            // For multiple files, we need to maintain an array
            if (!fileInput.files_array) {
                fileInput.files_array = [];
            }
            fileInput.files_array.push(file);
        } else {
            // For single file, replace
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
        }
    }

    // Stop camera stream
    stopCamera(inputName) {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        const video = document.getElementById(`video-${inputName}`);
        video.classList.add('d-none');
        video.srcObject = null;
        
        // Show/hide controls
        document.querySelector(`#video-${inputName}`).parentElement.parentElement
            .querySelector('button[onclick*="startCamera"]').classList.remove('d-none');
        document.querySelector(`#video-${inputName}`).parentElement.parentElement
            .querySelector('button[onclick*="captureImage"]').classList.add('d-none');
        document.querySelector(`#video-${inputName}`).parentElement.parentElement
            .querySelector('button[onclick*="stopCamera"]').classList.add('d-none');
    }

    // Select file from device
    selectFile(inputName, multiple) {
        const fileInput = document.getElementById(`file-${inputName}`);
        fileInput.click();
        
        fileInput.onchange = () => {
            const files = Array.from(fileInput.files);
            const preview = document.getElementById(`preview-${inputName}`);
            
            if (!multiple) {
                preview.innerHTML = '';
            }
            
            files.forEach(file => {
                if (file.type.startsWith('image/')) {
                    this.addFilePreview(inputName, file, multiple);
                } else {
                    this.addDocumentPreview(inputName, file, multiple);
                }
            });
        };
    }

    // Add file preview
    addFilePreview(inputName, file, multiple) {
        const preview = document.getElementById(`preview-${inputName}`);
        const imageDiv = document.createElement('div');
        imageDiv.className = 'captured-image-item d-inline-block m-2 position-relative';
        
        const reader = new FileReader();
        reader.onload = (e) => {
            imageDiv.innerHTML = `
                <img src="${e.target.result}" class="img-thumbnail" style="max-width: 150px; max-height: 150px;">
                <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                        onclick="removeCapturedImage(this, '${inputName}')">
                    <i class="fas fa-times"></i>
                </button>
                <div class="text-center mt-1">
                    <small class="text-muted">${file.name}</small>
                </div>
            `;
        };
        reader.readAsDataURL(file);
        
        preview.appendChild(imageDiv);
    }

    // Add document preview
    addDocumentPreview(inputName, file, multiple) {
        const preview = document.getElementById(`preview-${inputName}`);
        const docDiv = document.createElement('div');
        docDiv.className = 'captured-image-item d-inline-block m-2 position-relative';
        
        const fileIcon = this.getFileIcon(file.type);
        docDiv.innerHTML = `
            <div class="text-center p-3 border rounded" style="width: 150px; height: 150px; display: flex; flex-direction: column; justify-content: center;">
                <i class="${fileIcon} fa-3x text-primary mb-2"></i>
                <small class="text-muted">${file.name}</small>
            </div>
            <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle" 
                    onclick="removeCapturedImage(this, '${inputName}')">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        preview.appendChild(docDiv);
    }

    // Get file icon based on type
    getFileIcon(fileType) {
        if (fileType.includes('pdf')) return 'fas fa-file-pdf';
        if (fileType.includes('doc')) return 'fas fa-file-word';
        if (fileType.includes('image')) return 'fas fa-file-image';
        return 'fas fa-file';
    }

    // Remove captured image
    removeCapturedImage(button, inputName) {
        const imageItem = button.closest('.captured-image-item');
        imageItem.remove();
        
        // Update file input
        const fileInput = document.getElementById(`file-${inputName}`);
        if (fileInput.files_array) {
            // Remove from array logic would go here
            // This is complex with regular file inputs, might need form data handling
        }
    }
}

// Global camera instance
const cameraCapture = new CameraCapture();

// Global functions for onclick handlers
function startCamera(inputName) {
    cameraCapture.startCamera(inputName);
}

function captureImage(inputName, multiple) {
    cameraCapture.captureImage(inputName, multiple);
}

function stopCamera(inputName) {
    cameraCapture.stopCamera(inputName);
}

function selectFile(inputName, multiple) {
    cameraCapture.selectFile(inputName, multiple);
}

function removeCapturedImage(button, inputName) {
    cameraCapture.removeCapturedImage(button, inputName);
}

// Initialize cameras when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize camera containers
    document.querySelectorAll('[data-camera-input]').forEach(container => {
        const inputName = container.dataset.cameraInput;
        const multiple = container.dataset.multiple === 'true';
        cameraCapture.initCamera(container.id, inputName, multiple);
    });
});

// Form submission handler for multiple files
function handleFormSubmission(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    // Handle multiple file inputs with captured images
    document.querySelectorAll('input[type="file"]').forEach(input => {
        if (input.files_array && input.files_array.length > 0) {
            // Remove original files and add captured files
            formData.delete(input.name);
            input.files_array.forEach(file => {
                formData.append(input.name, file);
            });
        }
    });
    
    return formData;
}