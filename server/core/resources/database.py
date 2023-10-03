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
        # FIXME: fix for other db providers
        # await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["server.resources.models"]})
        await Tortoise.init(
            db_url="sqlite://db.sqlite", modules={"models": ["core.resources.models"]}
        )

    # Generate the schema
    await Tortoise.generate_schemas()

    # FIXME: remove it later
    # from server.resources.models import init_fake_data
    # await init_fake_data()
