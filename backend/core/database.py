"""Setup database"""
from tornado.options import options
from tortoise import Tortoise

DEFAULT_CONFIG = {
    "apps": {
        "models": {
            "models": ["core.resources.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

SQLITE_CONFIG = {
    **DEFAULT_CONFIG,
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": "db.sqlite"},
        }
    },
}


POSTGRESQL_CONFIG = {
    **DEFAULT_CONFIG,
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": options.db_database,
                "host": options.db_host,
                "password": options.db_password,
                "port": options.db_port,
                "user": options.db_user,
            },
        }
    },
}


async def init_database() -> None:
    """Initialize database"""
    from core.config import TORTOISE_ORM

    await Tortoise.init(config=TORTOISE_ORM)

    await Tortoise.generate_schemas()
