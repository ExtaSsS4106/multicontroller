
    
    function RemoveClick(user_id, group_id) {

        
        fetch(`/group/${group_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                action: 'remove_user',
                user_id: user_id
            })
        })
        .then(response => {
            location.reload();
        });
    }

    function AddClick(user_id, group_id) {

        
        fetch(`/group/${group_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                action: 'add_user',
                user_id: user_id
            })
        })
        .then(response => {
            location.reload();
        });
    }

// ==================== ПОИСК ПОЛЬЗОВАТЕЛЕЙ (ЛОКАЛЬНЫЙ) ====================
function userSearchClick(groupId) {
    const query = document.getElementById('users_query').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.g-users .card');
    
    if (!query) {
        // Если поиск пустой - показываем все карточки
        cards.forEach(card => {
            card.style.display = 'flex';
        });
        return;
    }
    
    let foundCount = 0;
    cards.forEach(card => {
        const userName = card.querySelector('.c-text h2')?.innerText.toLowerCase() || '';
        
        if (userName.includes(query)) {
            card.style.display = 'flex';
            foundCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Показываем сообщение если ничего не найдено
    const container = document.querySelector('.g-users .content');
    let noResultsMsg = document.getElementById('no-users-results');
    
    if (foundCount === 0) {
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.id = 'no-users-results';
            noResultsMsg.className = 'no-results-message';
            noResultsMsg.innerHTML = '<h1>🔍 No users found</h1>';
            container.appendChild(noResultsMsg);
        }
    } else {
        if (noResultsMsg) noResultsMsg.remove();
    }
}

// ==================== ПОИСК ЗАМЕТОК (ЛОКАЛЬНЫЙ) ====================
function notesSearchClick(groupId) {
    const query = document.getElementById('notes_query').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.g-notes .card');
    
    if (!query) {
        // Если поиск пустой - показываем все карточки
        cards.forEach(card => {
            card.style.display = 'flex';
        });
        return;
    }
    
    let foundCount = 0;
    cards.forEach(card => {
        const title = card.querySelector('.c-text h2')?.innerText.toLowerCase() || '';
        const fileName = card.querySelector('.c-text h6')?.innerText.toLowerCase() || '';
        
        if (title.includes(query) || fileName.includes(query)) {
            card.style.display = 'flex';
            foundCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Показываем сообщение если ничего не найдено
    const container = document.querySelector('.g-notes .content');
    let noResultsMsg = document.getElementById('no-notes-results');
    
    if (foundCount === 0) {
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.id = 'no-notes-results';
            noResultsMsg.className = 'no-results-message';
            noResultsMsg.innerHTML = '<h1>📝 No notes found</h1>';
            container.appendChild(noResultsMsg);
        }
    } else {
        if (noResultsMsg) noResultsMsg.remove();
    }
}

// ==================== ПОИСК ПРИ ВВОДЕ ТЕКСТА (реалтайм) ====================
document.addEventListener('DOMContentLoaded', function() {
    // Поиск пользователей в реальном времени
    const usersInput = document.getElementById('users_query');
    if (usersInput) {
        usersInput.addEventListener('input', function() {
            const groupId = this.getAttribute('data-group-id') || '';
            userSearchClick(groupId);
        });
    }
    
    // Поиск заметок в реальном времени
    const notesInput = document.getElementById('notes_query');
    if (notesInput) {
        notesInput.addEventListener('input', function() {
            const groupId = this.getAttribute('data-group-id') || '';
            notesSearchClick(groupId);
        });
    }
});
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }