// Camera functionality for file uploads

document.addEventListener('DOMContentLoaded', function() {
    initializeCameraContainers();
});

function initializeCameraContainers() {
    const cameraContainers = document.querySelectorAll('.camera-container');

    cameraContainers.forEach(container => {
        const inputName = container.dataset.cameraInput;
        const isMultiple = container.dataset.multiple === 'true';

        // Create hidden file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.name = inputName;
        fileInput.accept = 'image/*';
        fileInput.capture = 'camera';
        fileInput.style.display = 'none';
        if (isMultiple) {
            fileInput.multiple = true;
        }

        container.appendChild(fileInput);

        // Make container clickable
        container.style.cursor = 'pointer';
        container.style.border = '2px dashed #ccc';
        container.style.borderRadius = '8px';
        container.style.padding = '20px';
        container.style.textAlign = 'center';
        container.style.minHeight = '150px';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.justifyContent = 'center';
        container.style.alignItems = 'center';

        container.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            handleFileSelection(e, container);
        });
    });
}

function handleFileSelection(event, container) {
    const files = event.target.files;
    if (files.length === 0) return;

    // Clear previous preview
    const existingPreviews = container.querySelectorAll('.photo-preview');
    existingPreviews.forEach(preview => preview.remove());

    // Create preview for each file
    Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.className = 'photo-preview';
                preview.style.marginTop = '10px';

                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.maxWidth = '200px';
                img.style.maxHeight = '150px';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '4px';

                const fileName = document.createElement('small');
                fileName.textContent = file.name;
                fileName.style.display = 'block';
                fileName.style.marginTop = '5px';
                fileName.style.color = '#666';

                preview.appendChild(img);
                preview.appendChild(fileName);
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        }
    });

    // Update container appearance
    container.style.borderColor = '#28a745';
    container.style.backgroundColor = '#f8f9fa';
}