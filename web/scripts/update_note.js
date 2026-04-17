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
        let title = document.getElementById('note-title')?.innerText.trim() || '';
        let description = document.getElementById('note-description')?.innerText.trim() || '';
        let noteId = document.querySelector('.content')?.getAttribute('data-note-id');
        let localNoteId = document.querySelector('.content')?.getAttribute('data-note-local-id');
        console.log('Note ID:', noteId, 'Local Note ID:', localNoteId);
            // ✅ Преобразуем в число
        if (noteId && noteId !== 'None' && noteId !== 'null') {
            noteId = parseInt(noteId);
        } else {
            noteId = null;
        }
        
        if (localNoteId && localNoteId !== 'None' && localNoteId !== 'null') {
            localNoteId = parseInt(localNoteId);
        } else {
            localNoteId = null;
        }
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
            const response = await eel.create_or_update_local_note({"title": title, "description": description, "note_id": localNoteId, "server_id": noteId})();
            console.log('Update response:', response);
            
            if (response.status === 'success') {
                // Если есть выбранный новый файл, загружаем его
                if (this.selectedFile) {
                    this.showMessage('Uploading file...', 'info');
                    await this.uploadLocalFile(this.selectedFile, localNoteId);
                }
                
                this.showMessage('Note updated successfully!', 'success');
                setTimeout(() => {
                    if (response.note && response.note.id) {
                        loadPage('local_note', localNoteId);
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
        let title = document.getElementById('note-title')?.innerText.trim() || '';
        let description = document.getElementById('note-description')?.innerText.trim() || '';
        let noteId = document.querySelector('.content')?.getAttribute('data-note-id');
        let localNoteId = document.querySelector('.content')?.getAttribute('data-note-local-id');
        // ✅ Преобразуем в число
        if (noteId && noteId !== 'None' && noteId !== 'null') {
            noteId = parseInt(noteId);
        } else {
            noteId = null;
        }
        
        if (localNoteId && localNoteId !== 'None' && localNoteId !== 'null') {
            localNoteId = parseInt(localNoteId);
        } else {
            localNoteId = null;
        }
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
            console.log('Local update response:', localResponse);

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

    async uploadLocalFile(file, localNoteId) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = e.target.result.split(',')[1];
                console.log('Uploading file:', file.name, 'for note ID:', localNoteId);
                
                try {
                    const response = await eel.local_save_file(file.name, base64, localNoteId)();
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

    async deleteNote() {
        let noteId = document.querySelector('.content')?.getAttribute('data-note-id');
        let type = document.querySelector('.content')?.getAttribute('data-type');
        if (noteId && noteId !== 'None' && noteId !== 'null') {
            noteId = parseInt(noteId);
        } else {
            this.showMessage('Note ID not found', 'error');
            return;
        }
        
        if (!confirm('Are you sure you want to delete this note?')) {
            return;
        }
        
        this.showMessage('Deleting...', 'info');
        
        try {
            const response = await eel.delete_note(noteId, type)();
            if (response.status === 'success') {
                this.showMessage('Note deleted!', 'success');
                setTimeout(() => loadPage('main'), 1500);
            } else {
                this.showMessage('Error: ' + (response.error || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Error deleting note:', error);
            this.showMessage('Error deleting note: ' + error, 'error');
        }
    }
}
function deleteNote() {
    if (window.updateNotePage) {
        window.updateNotePage.deleteNote();
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

