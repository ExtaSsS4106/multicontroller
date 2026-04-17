from functools import wraps
from tortoise import Tortoise

from .models import User

def with_db(func):
    """Декоратор - автоматически init и close"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        await Tortoise.init(
            db_url='sqlite://database.db',
            modules={'models': ['src.db.models']}
        )
        await Tortoise.generate_schemas()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            await Tortoise.close_connections()
    return wrapper


