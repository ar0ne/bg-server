"""Setup database"""
from tornado.options import options, parse_config_file
from tortoise import Tortoise

if "port" not in options:
    from core.config import load_env_variables

    load_env_variables()


SQLITE_CONFIG = {
    "connections": {
        "default": {"engine": "tortoise.backends.sqlite", "credentials": {"file_path": "db.sqlite"}}
    },
    "apps": {
        "models": {
            "models": ["core.resources.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


POSTGRESQL_CONFIG = {
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
    "apps": {
        "models": {
            "models": ["core.resources.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


TORTOISE_ORM = SQLITE_CONFIG
if options.db_provider == "postgres":
    TORTOISE_ORM = POSTGRESQL_CONFIG


async def init_database() -> None:
    """Initialize database"""

    await Tortoise.init(config=TORTOISE_ORM)

    # Generate the schema
    await Tortoise.generate_schemas()
