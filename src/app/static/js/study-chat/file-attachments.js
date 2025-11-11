/**
 * FileAttachments - Manages file selection, validation, and preview display
 */
class FileAttachments {
    constructor() {
        this.selectedFiles = [];
        this.maxSize = 16 * 1024 * 1024; // 16MB
    }

    /**
     * Handle file input change event
     * @param {Event} event - File input change event
     */
    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        
        for (const file of files) {
            if (file.size > this.maxSize) {
                showMessage(`File ${file.name} is too large. Max 16MB`, 'error');
                return;
            }
        }
        
        this.selectedFiles = this.selectedFiles.concat(files);
        this.updateAttachmentPreview();
        event.target.value = ''; // Clear for reuse
    }

    /**
     * Update the attachment preview UI
     */
    updateAttachmentPreview() {
        const previewContainer = document.getElementById('attachmentPreview');
        const listContainer = document.getElementById('attachmentList');
        
        if (this.selectedFiles.length === 0) {
            previewContainer.style.display = 'none';
            return;
        }
        
        previewContainer.style.display = 'block';
        listContainer.innerHTML = '';
        
        this.selectedFiles.forEach((file, index) => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-secondary d-flex align-items-center gap-1';
            badge.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <button type="button" class="btn-close btn-close-white" 
                        style="font-size: 0.6rem;" 
                        onclick="chat.fileAttachments.removeFile(${index})"></button>
            `;
            listContainer.appendChild(badge);
        });
    }

    /**
     * Remove a file from the selected files list
     * @param {number} index - Index of file to remove
     */
    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateAttachmentPreview();
    }

    /**
     * Get selected files
     * @returns {Array} Array of selected files
     */
    getFiles() {
        return this.selectedFiles;
    }

    /**
     * Clear all selected files
     */
    clearFiles() {
        this.selectedFiles = [];
        this.updateAttachmentPreview();
    }
}
