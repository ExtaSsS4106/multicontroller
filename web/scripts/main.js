class Main_page {
    constructor() {
        console.log("Main_page constructor");
        this.initSearch();
    }
    
    updateUsersList(type, uid) {
        console.log("updateUsersList called:", type, uid);
        
        fetch(`/user-notes/${uid}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                type: type,
                user_id: uid
            })
        })
        .then(response => response.text())
        .then(html => {
            const container = document.getElementById('content-container');
            if (container) {
                container.innerHTML = html;
            } else {
                console.error("content-container not found");
            }
        })
        .catch(error => {
            console.error("Error in updateUsersList:", error);
        });
    }
    
    
    // ==================== ПОИСК ПОЛЬЗОВАТЕЛЕЙ (ЛОКАЛЬНЫЙ) ====================
    userSearchClick() {
        const query = document.getElementById('query')?.value.toLowerCase().trim() || '';
        const cards = document.querySelectorAll('.card');
        
        if (!query) {
            cards.forEach(card => {
                card.style.display = 'flex';
            });
            this.removeNoResultsMessage();
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
        
        if (foundCount === 0) {
            this.showNoResultsMessage();
        } else {
            this.removeNoResultsMessage();
        }
    }
    
    showNoResultsMessage() {
        let noResultsMsg = document.getElementById('no-users-results');
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.id = 'no-users-results';
            noResultsMsg.className = 'no-results-message';
            noResultsMsg.innerHTML = '<h1>🔍 No users found</h1>';
            const container = document.querySelector('.content');
            if (container) {
                container.appendChild(noResultsMsg);
            }
        }
    }
    
    removeNoResultsMessage() {
        const noResultsMsg = document.getElementById('no-users-results');
        if (noResultsMsg) {
            noResultsMsg.remove();
        }
    }
    
    // ==================== ПОИСК ПРИ ВВОДЕ ТЕКСТА ====================
    initSearch() {
        const usersInput = document.getElementById('query');
        if (usersInput) {
            usersInput.addEventListener('input', () => {
                this.userSearchClick();
            });
            console.log("Search initialized");
        } else {
            console.warn("Search input #query not found");
        }
    }
    
    initPage() {
        console.log("Main_page initPage");
        this.initSearch();
        
        // Инициализация кнопок
        const serverBtn = document.querySelector('[onclick*="updateUsersList(\'server\'"]');
        const groupsBtn = document.querySelector('[onclick*="updateUsersList(\'groups\'"]');
        
        if (serverBtn) {
            console.log("Server button found");
        }
        if (groupsBtn) {
            console.log("Groups button found");
        }
    }
}

// Глобальная функция для вызова из onclick
function updateUsersList(type, uid) {
    let mainPage = window.mainPage;
    if (window.mainPage) {
        window.mainPage.updateUsersList(type, uid);
    } else {
        console.error("Main_page not initialized");
    }
}

