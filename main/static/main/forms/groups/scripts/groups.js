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
            noResultsMsg.innerHTML = '<h1>🔍 No groups found</h1>';
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