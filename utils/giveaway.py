from utils.database import DatabaseManager, QueryType

class GiveawayManager:
    """ Manages database operations for giveaways. """
    _db = DatabaseManager()

    @classmethod
    async def create_giveaway(cls, message_id: int, data: dict):
        """ Create a new giveaway and its entry table. """
        await cls._db.execute_query(QueryType.COMMIT,
            f"CREATE TABLE g{message_id} ( id BIGINT PRIMARY KEY, user_name TEXT );"
        )
        columns = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        await cls._db.execute_query(QueryType.COMMIT,
            f"INSERT INTO giveaways ({columns}) VALUES ({values});", tuple(data.values())
        )

    @classmethod
    async def get_active_giveaways(cls):
        """ Fetch all active giveaways. """
        return await cls._db.execute_query(QueryType.FETCH_ALL,
            "SELECT * FROM giveaways WHERE active = 1;"
        )

    @classmethod
    async def get_all_entries(cls, giveaway_id: int) -> list:
        """ Fetch all entries for a specific giveaway. """
        rows = await cls._db.execute_query(QueryType.FETCH_ALL,
            f"SELECT id FROM g{giveaway_id};"
        )
        return [row["id"] for row in rows]

    @classmethod
    async def add_entry(cls, giveaway_id: int, data: dict):
        """ Add an entry to a giveaway. """
        columns = ", ".join(data.keys())
        values = ", ".join(["%s"] * len(data))
        await cls._db.execute_query(QueryType.COMMIT,
            f"INSERT INTO g{giveaway_id} ({columns}) VALUES ({values});", tuple(data.values())
        )
        await cls._db.execute_query(QueryType.COMMIT,
            f"UPDATE giveaways SET entries = (SELECT COUNT(*) FROM g{giveaway_id}) WHERE id = %s;", (giveaway_id)
        )

    @classmethod
    async def remove_entry(cls, giveaway_id: int, user_id: int):
        """ Remove an entry from a giveaway. """
        await cls._db.execute_query(QueryType.COMMIT,
            f"DELETE FROM g{giveaway_id} WHERE id = %s;", (user_id)
        )
        await cls._db.execute_query(QueryType.COMMIT,
            f"UPDATE giveaways SET entries = (SELECT COUNT(*) FROM g{giveaway_id}) WHERE id = %s;", (giveaway_id)
        )

    @classmethod
    async def select_winners(cls, giveaway_id: int, limit: int) -> list:
        """ Select random winners from the entries. """
        rows = await cls._db.execute_query(QueryType.FETCH_ALL,
            f"SELECT id FROM g{giveaway_id} ORDER BY RAND() LIMIT {limit};"
        )
        if not rows:
            return ["None"]
        for row in rows:
            await cls._db.execute_query(QueryType.COMMIT,
                f"DELETE FROM g{giveaway_id} WHERE id = %s;", (row["id"])
            )
        return [row["id"] for row in rows]

    @classmethod
    async def mark_as_completed(cls, giveaway_id: int):
        """ Mark a giveaway as completed. """
        await cls._db.execute_query(QueryType.COMMIT,
            f"UPDATE giveaways SET active = 0 WHERE id = %s;", (giveaway_id)
        )

    @classmethod
    async def delete_giveaway(cls, giveaway_id: int):
        """ Drop the entry table for a giveaway. """
        await cls._db.execute_query(QueryType.COMMIT,
            f"DROP TABLE IF EXISTS g{giveaway_id};"
        )
