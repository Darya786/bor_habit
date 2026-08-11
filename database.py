import aiosqlite

async def init_db():
    async with aiosqlite.connect("habits.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                habit_name TEXT
            )
        """)
        await db.commit()

async def add_habit(user_id: int, habit_name: str):
    async with aiosqlite.connect("habits.db") as db:
        await db.execute(
            "INSERT INTO habits (user_id, habit_name) VALUES (?, ?)",
            (user_id, habit_name)
        )
        await db.commit()

async def get_habits(user_id: int):
    async with aiosqlite.connect("habits.db") as db:
        async with db.execute("SELECT id, habit_name FROM habits WHERE user_id = ?", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return rows 

async def delete_habit(habit_id: int, user_id: int):
    async with aiosqlite.connect("habits.db") as db:
        await db.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
        await db.commit()