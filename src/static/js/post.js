document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('title').addEventListener('input', function() {
        this.parentElement.querySelector('.char-count').textContent = 
            this.value.length + '/20';
    });

    document.getElementById('content').addEventListener('input', function() {
        this.parentElement.querySelector('.char-count').textContent = 
            this.value.length + '/2000';
    });

    document.querySelector('.post-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const content = document.getElementById('content').value;
        
        if (title.length < 4 || title.length > 20) {
            alert('标题长度必须在4-20字之间');
            return;
        }
        
        if (content.length === 0) {
            alert('内容不能为空');
            return;
        }

        this.submit();
    });
});
