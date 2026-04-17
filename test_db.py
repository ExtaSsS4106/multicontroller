import asyncio
from src.db.users import create_user, get_all_users, get_user, delete_user

async def main():
    # Создаём
    await create_user("Алиса")
    await create_user("Боб")
    await create_user("Карл")
    
    # Получаем всех
    users = await get_all_users()
    print("\nВсе пользователи:")
    for u in users:
        print(f"  {u.id}. {u.name}")
    
    # Получаем одного
    user = await get_user(1)
    print(f"\nПользователь с ID=1: {user.name}")
    
    # Удаляем
    await delete_user(2)
    
    # Проверяем после удаления
    users = await get_all_users()
    print("\nПосле удаления:")
    for u in users:
        print(f"  {u.id}. {u.name}")

if __name__ == "__main__":
    asyncio.run(main())