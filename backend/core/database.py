"""Setup database"""
from tortoise import Tortoise

from core.config import TORTOISE_ORM


async def init_database() -> None:
    """Initialize database"""
    await Tortoise.init(config=TORTOISE_ORM)
