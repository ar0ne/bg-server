from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
    INSERT INTO "game" (id, name, min_size, max_size)
        VALUES ('2eed8639-f3b7-461f-9a70-a046b6b71f40', 'Regicide', 1, 4), ('015c7cdd-0b93-4cfb-a984-cf52fd9d9ed3', 'TicTacToe', 2, 2);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
    DELETE FROM "game" WHERE "name" IN ('Regicide', 'TicTacToe');
    """
