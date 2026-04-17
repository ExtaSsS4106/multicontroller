from .models import User
from .db import with_db

@with_db
async def create_user(name: str):
    """Создание пользователя"""
    user = await User.create(name=name)
    print(f"Создан: {user.name}")
    return user

@with_db
async def get_all_users():
    """Получение всех пользователей"""
    users = await User.all()
    return users

@with_db
async def get_user(user_id: int):
    """Получение одного пользователя"""
    user = await User.get(id=user_id)
    return user

@with_db
async def delete_user(user_id: int):
    """Удаление пользователя"""
    await User.filter(id=user_id).delete()
    print(f"Удалён пользователь {user_id}")