class UpdateNote {
    constructor() {
        this.selectedFile = null; // Свойство для хранения нового файла
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

        // Сохраняем выбранный файл и обновляем отображение
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.selectedFile = e.target.files[0];
                if (this.selectedFile) {
                    // Обновляем отображение имени файла
                    const fileTitle = document.getElementById('file-title');
                    if (fileTitle) {
                        fileTitle.textContent = this.selectedFile.name;
                    }
                    this.showMessage(`File selected: ${this.selectedFile.name}`, 'info');
                }
            });
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
            // Сначала обновляем заметку
            const response = await eel.update_note(title, description, noteId)();
            console.log('Update response:', response);
            
            if (response.status === 'success') {
                // Если есть выбранный новый файл, загружаем его
                if (this.selectedFile) {
                    this.showMessage('Uploading file...', 'info');
                    await this.uploadFile(this.selectedFile, noteId);
                }
                
                this.showMessage('Note updated successfully!', 'success');
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
        
        this.showMessage('Saving and pushing...', 'info');
        
        try {
            // Сначала обновляем заметку
            const response = await eel.update_note(title, description, noteId)();
            console.log('Update response:', response);
            
            if (response.status === 'success') {
                // Если есть выбранный новый файл, загружаем его
                if (this.selectedFile) {
                    this.showMessage('Uploading file...', 'info');
                    await this.uploadFile(this.selectedFile, noteId);
                }
                
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

    async uploadFile(file, noteId) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = e.target.result.split(',')[1];
                console.log('Uploading file:', file.name, 'for note ID:', noteId);
                
                try {
                    const response = await eel.upload_file(file.name, base64, noteId)();
                    if (response.status === 'success') {
                        this.showMessage('File uploaded!', 'success');
                        this.selectedFile = null;
                        resolve(true);
                    } else {
                        this.showMessage('Upload failed: ' + response.error, 'error');
                        reject(response.error);
                    }
                } catch (error) {
                    this.showMessage('Upload error: ' + error, 'error');
                    reject(error);
                }
            };
            reader.onerror = () => {
                reject('File read error');
            };
            reader.readAsDataURL(file);
        });
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

