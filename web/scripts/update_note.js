class UpdateNote {
    constructor() {
        this.init();
    }
    
    init() {
        // Инициализация плейсхолдеров
        const titleEl = document.getElementById('note-title');
        const descEl = document.getElementById('note-description');
        
        if (titleEl) {
            titleEl.addEventListener('focus', () => this.onFocus(titleEl, 'Enter title...'));
            titleEl.addEventListener('blur', () => this.onBlur(titleEl, 'Enter title...'));
        }
        
        if (descEl) {
            descEl.addEventListener('focus', () => this.onFocus(descEl, 'Enter description...'));
            descEl.addEventListener('blur', () => this.onBlur(descEl, 'Enter description...'));
        }
    }
    
    onFocus(element, placeholder) {
        if (element.innerText === placeholder) {
            element.innerText = '';
        }
    }
    
    onBlur(element, placeholder) {
        if (element.innerText.trim() === '') {
            element.innerText = placeholder;
        }
    }
    
    async updateNote() {
        const title = document.getElementById('note-title')?.innerText.trim() || '';
        const description = document.getElementById('note-description')?.innerText.trim() || '';
        const noteId = document.querySelector('.content')?.getAttribute('data-note-id');

        if (!title || title === 'Enter title...') {
            this.showMessage('Please enter a title', 'error');
            return;
        }
        
        if (!description || description === 'Enter description...') {
            this.showMessage('Please enter a description', 'error');
            return;
        }
        
        this.showMessage('Saving...', 'info');
        
        try {
            const response = await eel.update_note(title, description, noteId)();
            console.log('Response:', response);
            
            if (response.status === 'success') {
                this.showMessage('Note updated successfully!', 'success');
                setTimeout(() => {
                    // Используем loadPage вместо window.location
                    if (response.note && response.note.id) {
                        loadPage('note', response.note.id);
                    } else {
                        loadPage('main');
                    }
                }, 1500);
            } else {
                this.showMessage('Error: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error saving note:', error);
            this.showMessage('Error saving note: ' + error, 'error');
        }
    }
    
    async updateNoteAndPush() {
        const title = document.getElementById('note-title')?.innerText.trim() || '';
        const description = document.getElementById('note-description')?.innerText.trim() || '';
        const noteId = document.querySelector('.content')?.getAttribute('data-note-id');
        if (!title || title === 'Enter title...') {
            this.showMessage('Please enter a title', 'error');
            return;
        }
        
        if (!description || description === 'Enter description...') {
            this.showMessage('Please enter a description', 'error');
            return;
        }
        
        this.showMessage('Creating and pushing...', 'info');
        
        try {
            const response = await eel.update_note(title, description, noteId)();
            console.log('Response:', response);
            
            if (response.status === 'success') {
                this.showMessage('Note updated and pushed!', 'success');
                setTimeout(() => {
                    if (response.note && response.note.id) {
                        loadPage('note', response.note.id);
                    } else {
                        loadPage('main');
                    }
                }, 1500);
            } else {
                this.showMessage('Error: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('Error: ' + error, 'error');
        }
    }
    
    showMessage(msg, type) {
        const messageDiv = document.getElementById('message');
        if (!messageDiv) return;
        
        messageDiv.textContent = msg;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
        
        if (type !== 'info') {
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 3000);
        }
    }
}

// Глобальные функции для вызова из onclick
function updateNote() {
    if (window.updateNotePage) {
        window.updateNotePage.updateNote();
    }
}

function updateNoteAndPush() {
    if (window.updateNotePage) {
        window.updateNotePage.updateNoteAndPush();
    }
}

