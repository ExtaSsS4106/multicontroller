function approve(request_id, note_id, user_id) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/requests/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            action: 'approved',
            request_id: request_id,
            note_id: note_id, 
            user_id: user_id
        })
    })
    .then(response => {
        location.reload();
    });
}
function cancel(request_id, note_id) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/requests/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            action: 'cancel',
            request_id: request_id,
            note_id: note_id
        })
    })
    .then(response => {
        location.reload();
    });
}


// ==================== ПОИСК ПОЛЬЗОВАТЕЛЕЙ (ЛОКАЛЬНЫЙ) ====================
function userSearchClick() {
    const query = document.getElementById('query').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.card');
    
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
    const container = document.querySelector('.content');
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



// ==================== ПОИСК ПРИ ВВОДЕ ТЕКСТА (реалтайм) ====================
document.addEventListener('DOMContentLoaded', function() {
    // Поиск пользователей в реальном времени
    const usersInput = document.getElementById('query');
    if (usersInput) {
        usersInput.addEventListener('input', function() {
            userSearchClick();
        });
    }
    

});