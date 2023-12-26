from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "game" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "min_size" SMALLINT NOT NULL  DEFAULT 1,
    "max_size" SMALLINT NOT NULL  DEFAULT 1
) /* Game model */;
CREATE TABLE IF NOT EXISTS "player" (
    "date_joined" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(60) NOT NULL UNIQUE,
    "nickname" VARCHAR(60)  UNIQUE,
    "password" VARCHAR(120) NOT NULL
) /* Player model */;
CREATE TABLE IF NOT EXISTS "room" (
    "closed" TIMESTAMP,
    "created" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "size" SMALLINT NOT NULL  DEFAULT 1,
    "status" SMALLINT NOT NULL  DEFAULT 0,
    "admin_id" CHAR(36) NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE,
    "game_id" CHAR(36) NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE
) /* Room model */;
CREATE TABLE IF NOT EXISTS "gameturn" (
    "id" CHAR(36) NOT NULL  PRIMARY KEY,
    "data" JSON NOT NULL,
    "turn" SMALLINT NOT NULL  DEFAULT 0,
    "room_id" CHAR(36) NOT NULL REFERENCES "room" ("id") ON DELETE CASCADE
) /* Temporary model to store game state */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "room_player" (
    "room_id" CHAR(36) NOT NULL REFERENCES "room" ("id") ON DELETE CASCADE,
    "player_id" CHAR(36) NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
