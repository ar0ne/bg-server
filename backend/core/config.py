"""
Config app
"""
import os

from tornado.options import define, options, parse_command_line, parse_config_file

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode", type=bool)
define("db_provider", default="sqlite", help="database provider", type=str)
define("db_host", default="127.0.0.1", help="database host", type=str)
define("db_port", default=5432, help="database port", type=int)
define("db_database", default="bg_server_db", help="database name", type=str)
define("db_user", default="", help="database user", type=str)
define("db_password", default="", help="database password", type=str)
define("JWT_SECRET", default="some-jwt-secret", help="JWT secret token", type=str)
define("JWT_ALGORITHM", default="HS256", help="JWT algorythm", type=str)
define("JWT_EXP_DELTA_SECONDS", default=3000, help="JWT expiration time in seconds", type=int)


ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE_PATH = os.path.join(ROOT_PATH, ".env")

STATIC_PATH = os.path.join(ROOT_PATH, "static")
TEMPLATE_PATH = os.path.join(ROOT_PATH, "templates")

parse_config_file(CONFIG_FILE_PATH)
parse_command_line()


from core.database import POSTGRESQL_CONFIG, SQLITE_CONFIG

TORTOISE_ORM = SQLITE_CONFIG
if options.db_provider == "postgres":
    TORTOISE_ORM = POSTGRESQL_CONFIG
