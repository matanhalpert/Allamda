/**
 * UIHelpers - Handles markdown rendering, HTML escaping, and DOM utilities
 */
class UIHelpers {
    constructor() {
        // No initialization needed
    }

    /**
     * Render markdown to HTML with sanitization
     * @param {string} content - Raw markdown text
     * @returns {string} Sanitized HTML
     */
    renderMarkdown(content) {
        // Parse markdown to HTML
        const rawHtml = marked.parse(content);
        // Sanitize HTML to prevent XSS
        const cleanHtml = DOMPurify.sanitize(rawHtml);
        return cleanHtml;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Scroll chat container to bottom
     */
    scrollToBottom() {
        const container = document.getElementById('chat-container');
        container.scrollTop = container.scrollHeight;
    }

    /**
     * Initialize markdown rendering for all existing messages
     */
    initExistingMessages() {
        document.querySelectorAll('.markdown-content').forEach((bubble) => {
            const rawContent = bubble.querySelector('.markdown-raw');
            const renderedContent = bubble.querySelector('.markdown-rendered');
            if (rawContent && renderedContent) {
                const markdownText = rawContent.textContent;
                renderedContent.innerHTML = this.renderMarkdown(markdownText);
            }
        });
    }
}
