document.addEventListener('DOMContentLoaded', function() {
    const showReplyButton = document.getElementById('showReplyForm');
    const replyForm = document.getElementById('replyForm');
    const cancelReplyButton = document.getElementById('cancelReply');
    const replyToInfo = document.getElementById('replyToInfo');
    const replyError = document.getElementById('replyError');

    showReplyButton.addEventListener('click', function() {
        clearReplyTo();
        showReplyButton.style.display = 'none';
        replyForm.style.display = 'block';
        replyForm.querySelector('textarea').focus();
    });

    cancelReplyButton.addEventListener('click', function() {
        replyForm.style.display = 'none';
        showReplyButton.style.display = 'block';
        replyForm.querySelector('textarea').value = '';
        replyError.style.display = 'none';
        clearReplyTo();
    });

    replyForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const textarea = this.querySelector('textarea');
        const content = textarea.value.trim();
        const replyTo = document.getElementById('replyTo').value;
        
        if (!content) {
            showError('请输入回复内容');
            return;
        }

        const response = await fetch(window.location.pathname + '/reply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                reply_to: replyTo || null
            })
        });

        const result = await response.json();

        const replyList = document.querySelector('.reply-list');
        const newReply = document.createElement('div');
        newReply.className = 'reply-item';
        newReply.innerHTML = `
            <div class="reply-meta">
                <span class="author">${result.username}</span>
                ${result.titles ? 
                    `<div class="user-titles">
                        ${result.titles.split(',').map(title => 
                            `<span class="title-badge">${title}</span>`
                        ).join('')}
                    </div>` : ''}
                ${result.badges ? 
                    `<div class="user-badges">
                        ${result.badges.split(',').map(badge => 
                            `<span class="badge-item">${badge}</span>`
                        ).join('')}
                    </div>` : ''}
                <span class="time">${result.created_at}</span>
            </div>
            <div class="reply-content">${result.content}</div>
        `;

        replyList.appendChild(newReply);

        const replyCount = document.querySelector('.reply-count');
        replyCount.textContent = parseInt(replyCount.textContent) + 1;

        textarea.value = '';
        replyForm.style.display = 'none';
        showReplyButton.style.display = 'block';
        clearReplyTo();

        newReply.scrollIntoView({ behavior: 'smooth' });
    });
});

function showReplyForm(replyId, username) {
    const replyForm = document.getElementById('replyForm');
    const replyTo = document.getElementById('replyTo');
    const replyToInfo = document.getElementById('replyToInfo');
    const replyToUsername = document.getElementById('replyToUsername');
    const showReplyFormBtn = document.getElementById('showReplyForm');
    
    replyTo.value = replyId;
    replyToUsername.textContent = username;
    replyToInfo.style.display = 'block';
    replyForm.style.display = 'block';
    showReplyFormBtn.style.display = 'none';

    replyForm.scrollIntoView({ behavior: 'smooth' });
}

function clearReplyTo() {
    const replyTo = document.getElementById('replyTo');
    const replyToInfo = document.getElementById('replyToInfo');
    
    replyTo.value = '';
    replyToInfo.style.display = 'none';
}