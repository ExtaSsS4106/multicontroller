class CreateNote {
    constructor() {
        this.selectedFile = null; // Свойство для хранения файла
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
                } else {
                    // Если файл не выбран, возвращаем placeholder
                    const fileTitle = document.getElementById('file-title');
                    if (fileTitle) {
                        fileTitle.textContent = 'No file selected';
                    }
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
    
    async saveNote() {
        const title = document.getElementById('note-title')?.innerText.trim() || '';
        const description = document.getElementById('note-description')?.innerText.trim() || '';
        
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
            // Сначала создаём заметку
            const response = await eel.create_or_update_local_note({"title": title, "description": description})();
            console.log('Response:', response);
            
            if (response.status === 'success') {
                // Если есть выбранный файл, загружаем его
                if (this.selectedFile && response.note && response.note.id) {
                    this.showMessage('Uploading file...', 'info');
                    await this.uploadLocalFile(this.selectedFile, response.note.id);
                }
                
                this.showMessage('Note created successfully!', 'success');
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
    
    async saveAndPush() {
        const title = document.getElementById('note-title')?.innerText.trim() || '';
        const description = document.getElementById('note-description')?.innerText.trim() || '';
        
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
            // Сначала создаём заметку
            const response = await eel.create_note(title, description)();

            console.log('Response:', response);
            
            if (response.status === 'success') {
                // Если есть выбранный файл, загружаем его
                if (this.selectedFile && response.note && response.note.id) {
                    this.showMessage('Uploading file...', 'info');
                    console.log('Note ID for upload:', response.note.id);
                    await this.uploadFile(this.selectedFile, response.note.id);
                }
                
                this.showMessage('Note created and pushed!', 'success');
                setTimeout(() => {
                    if (response.note && response.note.id) {
                        loadPage('server_note', response.note.id);
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

    async uploadLocalFile(file, noteId) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async (e) => {
                const base64 = e.target.result.split(',')[1];
                console.log('Uploading file:', file.name, 'for note ID:', noteId);
                
                try {
                    const response = await eel.local_save_file(file.name, base64, noteId)();
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
function saveNote() {
    if (window.createNotePage) {
        window.createNotePage.saveNote();
    }
}

function saveAndPush() {
    if (window.createNotePage) {
        window.createNotePage.saveAndPush();
    }
}