"""Setup database"""
from tornado.options import options
from tortoise import Tortoise


async def init_database() -> None:
    """Initialize database"""
    await Tortoise.init(config=options.TORTOISE_ORM)
