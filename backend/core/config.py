"""
Config app
"""
import os

from aiocache import caches
from tornado.options import define, options, parse_command_line, parse_config_file

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode", type=bool)
define("db_host", default="127.0.0.1", help="database host", type=str)
define("db_port", default=5432, help="database port", type=int)
define("db_database", default="bg_server_db", help="database name", type=str)
define("db_user", default="", help="database user", type=str)
define("db_password", default="", help="database password", type=str)
define("redis_host", default="127.0.0.1", help="Redis cache host endpoint", type=str)
define("redis_port", default=6379, help="Redis cache port", type=int)
define("JWT_SECRET", default="some-jwt-secret", help="JWT secret token", type=str)
define("JWT_ALGORITHM", default="HS256", help="JWT algorythm", type=str)
define("JWT_EXP_DELTA_SECONDS", default=3000, help="JWT expiration time in seconds", type=int)
define("TORTOISE_ORM", help="Tortoise ORM configuration", type=dict)


ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE_PATH = os.path.join(ROOT_PATH, ".env")

STATIC_PATH = os.path.join(ROOT_PATH, "static")
TEMPLATE_PATH = os.path.join(ROOT_PATH, "templates")

parse_config_file(CONFIG_FILE_PATH)
parse_command_line()

"""
If you want to use SQLite, you could use following config. *Note*: After that you need to remove existing
migrations and regenerate them for SQLite with aerich.

TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["core.resources.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": "db.sqlite"},
        }
    },
}
"""

TORTOISE_ORM = {
    "apps": {
        "models": {
            "models": ["core.resources.models", "aerich.models"],
            "default_connection": "default",
        }
    },
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


CACHE_CONFIG = {
    "default": {
        "cache": "aiocache.RedisCache",
        "endpoint": options.redis_host,
        "port": options.redis_port,
        "timeout": 5,
        "serializer": {"class": "aiocache.serializers.PickleSerializer"},
        "plugins": [
            {"class": "aiocache.plugins.HitMissRatioPlugin"},
            {"class": "aiocache.plugins.TimingPlugin"},
        ],
    }
}

caches.set_config(CACHE_CONFIG)
