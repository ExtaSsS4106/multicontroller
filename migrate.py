from src.db.db import with_db
import asyncio
from tortoise import Tortoise

@with_db
async def main():
    await Tortoise.generate_schemas()
    

if __name__ == "__main__":
    asyncio.run(main())