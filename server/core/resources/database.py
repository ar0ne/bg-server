"""Setup database"""
from tornado.options import options
from tortoise import Tortoise


async def init_database() -> None:
    """Initialize database"""

    db_settings = dict(
        provider=options.db_provider,
        user=options.db_user,
        password=options.db_password,
        host=options.db_host,
        port=options.db_port,
        database=options.db_database,
    )
    if options.db_provider == "sqlite":
        await Tortoise.init(
            db_url="sqlite://db.sqlite", modules={"models": ["core.resources.models"]}
        )
    elif options.db_provider == "postgres":
        await Tortoise.init(
            config={
                "connections": {
                    "default": {
                        "engine": "tortoise.backends.asyncpg",
                        "credentials": {
                            "database": db_settings["database"],
                            "host": db_settings["host"],
                            "password": db_settings["password"],
                            "port": db_settings["port"],
                            "user": db_settings["user"],
                        },
                    }
                },
                "apps": {
                    "models": {
                        "models": ["core.resources.models"],
                        "default_connection": "default",
                    }
                },
            },
        )

    # Generate the schema
    await Tortoise.generate_schemas()
