# MultiController Backend

Бэкенд-сервер для системы MultiController, построенный на Django REST Framework. Обеспечивает JSON API с ролевой моделью доступа через JWT-токены в заголовке `Authorization`.

## 🚀 Технологический стек

- **Python** 3.10+
- **Django** 4.x
- **Django REST Framework** 3.14+
- **PostgreSQL** / **SQLite** (на выбор)




## 🔧 Быстрый старт

### 1️⃣ Клонирование репозитория

```bash
git clone https://github.com/your-repo/multicontroller.git
cd multicontroller/backend
```

### 2️⃣ Настройка виртуального окружения
```bash
# Создание виртуального окружения
python -m venv venv

# Активация
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4️⃣ Настройка базы данных
- Отредактируйте core/settings.py или используйте файл .env:
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'multicontroller_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5️⃣ Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```


https://docs.google.com/presentation/d/1ox6yopAaaB3IpwndWt3-A1UMEv-fyPAxzj__FvsX9rI/edit?usp=drivesdk


