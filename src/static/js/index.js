document.addEventListener('DOMContentLoaded', function() {
    const enterButton = document.getElementById('enterCommunity');
    
    enterButton.addEventListener('click', function(e) {
        window.location.href = '/forum';
    });
});