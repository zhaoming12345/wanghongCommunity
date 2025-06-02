document.addEventListener('DOMContentLoaded', function() {
    
    const textarea = document.getElementById('content');

    function adjustTextareaHeight() {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
    
    textarea.addEventListener('input', adjustTextareaHeight);

    adjustTextareaHeight();
});