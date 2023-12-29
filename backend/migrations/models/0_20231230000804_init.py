from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "game" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "min_size" SMALLINT NOT NULL  DEFAULT 1,
    "max_size" SMALLINT NOT NULL  DEFAULT 1
);
COMMENT ON TABLE "game" IS 'Game model';
CREATE TABLE IF NOT EXISTS "player" (
    "date_joined" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(60) NOT NULL UNIQUE,
    "nickname" VARCHAR(60)  UNIQUE,
    "password" VARCHAR(120) NOT NULL
);
COMMENT ON TABLE "player" IS 'Player model';
CREATE TABLE IF NOT EXISTS "room" (
    "closed" TIMESTAMPTZ,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "id" UUID NOT NULL  PRIMARY KEY,
    "size" SMALLINT NOT NULL  DEFAULT 1,
    "status" SMALLINT NOT NULL  DEFAULT 0,
    "admin_id" UUID NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE,
    "game_id" UUID NOT NULL REFERENCES "game" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "room" IS 'Room model';
CREATE TABLE IF NOT EXISTS "gameturn" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "data" JSONB NOT NULL,
    "turn" SMALLINT NOT NULL  DEFAULT 0,
    "room_id" UUID NOT NULL REFERENCES "room" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "gameturn" IS 'Temporary model to store game state';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "room_player" (
    "room_id" UUID NOT NULL REFERENCES "room" ("id") ON DELETE CASCADE,
    "player_id" UUID NOT NULL REFERENCES "player" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
