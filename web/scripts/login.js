class Login_page {
    get_data() {
        const username = document.getElementById('username')?.value || '';
        const password = document.getElementById('password')?.value || '';
        return { username, password };
    }

    async init_page() {
        console.log("Login_page.init_page started");
        
        const btn = document.getElementById('login-btn');
        if (!btn) {
            console.error("Кнопка login-btn не найдена");
            return;
        }
        
        btn.addEventListener('click', async () => {
            const data = this.get_data();
            console.log("Данные для входа:", data);
            
            if (!data.username || !data.password) {
                this.showError("Введите username и пароль");
                return;
            }
            
            // Блокируем кнопку
            btn.disabled = true;
            btn.textContent = "Вход...";
            
            try {
                const response = await eel.login(data.username, data.password)();
                console.log("Ответ от сервера:", response);
                
                // Проверяем, что ответ - объект, а не строка
                if (typeof response === 'object') {
                    if (response.status === "200" && response.success) {
                        console.log("Вход выполнен успешно");
                        await loadPage("main");
                    } else {
                        const errorMsg = response.error || "Ошибка входа";
                        this.showError(errorMsg);
                    }
                } else {
                    // Если пришла строка (HTML) - значит что-то пошло не так
                    console.error("Получен неожиданный ответ:", response);
                    this.showError("Ошибка сервера");
                }
            } catch (error) {
                console.error("Ошибка входа:", error);
                this.showError("Ошибка соединения с сервером");
            } finally {
                // Разблокируем кнопку
                btn.disabled = false;
                btn.textContent = "login in";
            }
        });
        
        // Обработка Enter
        const inputs = document.querySelectorAll('.entry');
        inputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    btn.click();
                }
            });
        });
    }
    
    showError(message) {
        let errorDiv = document.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            const authDiv = document.querySelector('.auth');
            if (authDiv) {
                authDiv.insertBefore(errorDiv, authDiv.firstChild);
            }
        }
        errorDiv.textContent = `⚠️ ${message}`;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 3000);
    }
}

