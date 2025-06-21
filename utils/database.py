from enum import Enum, auto

class QueryType(Enum):
    FETCH_ONE = auto()
    FETCH_ALL = auto()
    COMMIT = auto()

import aiomysql, os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    """ Singleton class for managing MySQL connection pool. """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.pool = None
        self._initialized = True

    async def create_pool(self):
        """ Create the database connection pool. """
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host = os.getenv("DB_ENDPOINT"), port = 3306,
                user = os.getenv("DB_USERNAME"),
                password = os.getenv("DB_PASSWORD"),
                db = os.getenv("DB_NAME"),
                maxsize = 10
            )

    async def close_pool(self):
        """ Close the database connection pool. """
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def execute_query(self, query_type: QueryType, query: str, params = None):
        """ Execute a query based on the specified QueryType. """
        if self.pool is None:
            await self.create_pool()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                match query_type:
                    case QueryType.FETCH_ONE:
                        return await cursor.fetchone()
                    case QueryType.FETCH_ALL:
                        return await cursor.fetchall()
                    case QueryType.COMMIT:
                        await conn.commit()
                    case _:
                        raise ValueError(f"Unsupported QueryType: {query_type}")
